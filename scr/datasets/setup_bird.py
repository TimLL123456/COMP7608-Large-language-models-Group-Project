"""Reproducible setup for original and current BIRD Mini-Dev SQLite databases.

Use `python -m scr.datasets.setup_bird --help`. No API keys or gold SQL are
passed to agents. Dataset archives and generated manifests stay under data/bird/.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from .bird import (DEFAULT_ROOT, EXPECTED_DATABASES, EXPECTED_QUESTIONS,
                   BirdDataset, make_split, read_annotations, read_only_connection, sha256_file)

HF_REPO = "birdsql/bird_mini_dev"
HF_REVISION = "f65faf4ae3b638c1fa6df1d3370c8d92c8366301"
HF_FILE = "data/mini_dev_sqlite-00000-of-00001.json"
DRIVE_FILE_ID = "13VLWIwpw5E3d5DUkMvzw7hvHE67a4XkG"
MAX_UNCOMPRESSED_BYTES = 40 * 1024**3


def safe_extract_zip(archive: Path, destination: Path) -> None:
    """Reject ZIP slip, symlinks, special entries, oversized and duplicate names."""
    destination = Path(destination)
    seen = set()
    with zipfile.ZipFile(archive) as source:
        infos = source.infolist()
        total = sum(i.file_size for i in infos)
        if total > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("ZIP exceeds allowed extracted size")
        if source.testzip() is not None:
            raise ValueError("ZIP CRC check failed")
        for item in infos:
            raw = item.filename.replace("\\", "/")
            path = PurePosixPath(raw)
            unix_mode = (item.external_attr >> 16) & 0xFFFF
            if (not raw or path.is_absolute() or ".." in path.parts or
                    any(":" in part for part in path.parts) or raw.startswith("//") or "\x00" in raw):
                raise ValueError(f"Unsafe ZIP member: {item.filename!r}")
            if stat.S_IFMT(unix_mode) in (stat.S_IFLNK, stat.S_IFCHR, stat.S_IFBLK,
                                         stat.S_IFIFO, stat.S_IFSOCK):
                raise ValueError(f"Unsupported ZIP member: {item.filename!r}")
            rel = str(path).casefold()
            if rel in seen:
                raise ValueError(f"Duplicate ZIP member: {item.filename!r}")
            seen.add(rel)
        destination.mkdir(parents=True, exist_ok=True)
        for item in infos:
            target = destination.joinpath(*PurePosixPath(item.filename.replace("\\", "/")).parts)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.open(item) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst, 1024 * 1024)


def fetch_annotations(path: Path | None = None, *, release: str = "original", revision: str | None = None) -> tuple[Path, str]:
    """Download official SQLite annotations at a resolved commit, or use manual input."""
    if path:
        path = Path(path).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return path, "manual-annotations-verify-against-pinned-source"
    try:
        from huggingface_hub import hf_hub_download, HfApi
    except ImportError as exc:
        raise RuntimeError("Install dependencies with 'uv sync' to use Hugging Face downloads") from exc
    try:
        resolved = HfApi().dataset_info(HF_REPO, revision=revision or "main").sha if release == "latest" else HF_REVISION
        result = hf_hub_download(repo_id=HF_REPO, repo_type="dataset",
                                 revision=resolved, filename="data/mini_dev_sqlite.jsonl" if release == "latest" else HF_FILE)
    except Exception as exc:
        raise RuntimeError("Hugging Face annotations unavailable; check the release/revision or pass --annotations PATH") from exc
    return Path(result), resolved


def fetch_archive(destination: Path, manual: Path | None = None) -> Path:
    if manual is not None:
        source = Path(manual).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        return source
    try:
        import gdown
    except ImportError as exc:
        raise RuntimeError("Install dependencies with 'uv sync' to download the official ZIP") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = gdown.download(id=DRIVE_FILE_ID, output=str(destination), quiet=False, resume=True)
    except Exception as exc:
        raise RuntimeError("Google Drive download failed; use --archive PATH for a manually downloaded official ZIP") from exc
    if not result or not destination.is_file():
        raise RuntimeError("Google Drive download missing or unavailable; use --archive PATH")
    return destination


def locate_databases(extracted: Path, db_ids: set[str]) -> dict[str, Path]:
    """Find each expected SQLite file without assuming one archive root folder."""
    candidates = list(Path(extracted).rglob("*.sqlite"))
    found = {}
    for db_id in sorted(db_ids):
        matches = [p for p in candidates if p.name == f"{db_id}.sqlite" and p.parent.name == db_id]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one SQLite file for {db_id}, found {len(matches)}")
        with read_only_connection(matches[0]) as conn:
            if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError(f"SQLite quick_check failed for {db_id}")
            if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' LIMIT 1").fetchone():
                raise ValueError(f"SQLite database has no tables: {db_id}")
        found[db_id] = matches[0]
    return found


def verify(root: Path = DEFAULT_ROOT, *, hashes: bool = True) -> dict:
    dataset = BirdDataset(root)
    if "source_annotations_file" in dataset.manifest:
        source = dataset.root / dataset.manifest["source_annotations_file"]
        if not source.resolve().is_relative_to(dataset.root) or sha256_file(source) != dataset.manifest["source_annotations_sha256"]:
            raise ValueError("Source annotation checksum mismatch")
    if hashes:
        for dbid, item in dataset.manifest["databases"].items():
            if sha256_file(dataset.get_database_path(dbid)) != item["sha256"]:
                raise ValueError(f"Database checksum mismatch: {dbid}")
    for dbid in dataset.manifest["databases"]:
        if not dataset.get_schema(dbid):
            raise ValueError(f"No tables for {dbid}")
    difficulty_distribution = {
        name: {level: Counter(row["difficulty"] for row in dataset.get_split(name))[level]
               for level in ("simple", "moderate", "challenging")}
        for name in ("dev", "test")
    }
    return {"questions": len(dataset.load_questions()), "databases": len(dataset.manifest["databases"]),
            "dev": len(dataset.get_split("dev")), "test": len(dataset.get_split("test")),
            "difficulty_distribution": difficulty_distribution,
            "annotations_sha256": dataset.manifest["annotations_sha256"],
            "source_verification": dataset.manifest["source_verification"], "status": "PASS"}


def setup(root: Path = DEFAULT_ROOT, *, archive: Path | None = None,
          annotations: Path | None = None, force: bool = False,
          release: str = "original", revision: str | None = None) -> dict:
    if release not in {"original", "latest"}:
        raise ValueError("Unknown release")
    if revision and release != "latest":
        raise ValueError("--revision requires --release latest")
    root = Path(root).resolve()
    if root.exists() and not force:
        installed = BirdDataset(root).manifest
        expected = "bird-mini-dev-2026-sqlite" if release == "latest" else "bird-mini-dev-original-sqlite"
        if installed["dataset"] != expected or (revision and installed["annotations_source_revision"] != revision):
            raise ValueError("Installed release/revision differs; use a separate --root")
        return verify(root)
    if root.exists() and force:
        raise ValueError("Refusing to overwrite dataset in place; move/delete the existing dataset after backing it up")
    root.parent.mkdir(parents=True, exist_ok=True)
    source_json, source_revision = fetch_annotations(annotations, release=release, revision=revision)
    rows = read_annotations(source_json)
    if release == "latest" and {r["question_id"] for r in rows} != set(range(500)):
        raise ValueError("Latest Mini-Dev requires IDs 0–499")
    split = make_split(rows)
    if release == "latest" and archive:
        raise ValueError("Latest release uses official database images, not the legacy archive")
    archive_path = fetch_archive(root.parent / "_downloads" / "original-mini-dev.zip", archive) if release == "original" else None
    with tempfile.TemporaryDirectory(prefix="bird-setup-", dir=root.parent) as tmp:
        staging = Path(tmp) / "original-mini-dev"
        package = staging / "package"
        images = {}
        if release == "latest":
            from .bird_images import fetch_databases
            images = fetch_databases(package, {row["db_id"] for row in rows})
        else:
            safe_extract_zip(archive_path, package)
        dbs = locate_databases(package, {row["db_id"] for row in rows})
        staging.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_json, staging / ("annotations.source.jsonl" if source_json.suffix == ".jsonl" else "annotations.source.json"))
        (staging / "annotations.json").write_text(json.dumps(rows, ensure_ascii=False) + "\n", encoding="utf-8")
        if release == "original":
            shutil.copyfile(source_json, staging / "annotations.json")
        inventory = {db_id: {"path": path.relative_to(staging).as_posix(), "sha256": sha256_file(path)}
                     for db_id, path in sorted(dbs.items())}
        manifest = {
            "dataset": "bird-mini-dev-2026-sqlite" if release == "latest" else "bird-mini-dev-original-sqlite", "source": HF_REPO,
            "database_images": images, "source_annotations_sha256": sha256_file(source_json),
            "source_annotations_file": "annotations.source.jsonl" if source_json.suffix == ".jsonl" else "annotations.source.json",
            "hf_revision_expected": source_revision if release == "latest" else HF_REVISION, "annotations_source_revision": source_revision,
            "hf_annotations_file": "data/mini_dev_sqlite.jsonl" if release == "latest" else HF_FILE,
            "drive_file_id": DRIVE_FILE_ID if archive_path else None,
            "archive_filename": archive_path.name if archive_path else None,
            "archive_sha256": sha256_file(archive_path) if archive_path else None,
            "annotations_sha256": sha256_file(staging / "annotations.json"),
            "question_count": EXPECTED_QUESTIONS, "database_count": EXPECTED_DATABASES,
            "sql_dialect": "SQLite", "split_seed": 42, "split": split,
            "databases": inventory,
            "source_verification": ("pinned_hf_download" if annotations is None else
                                    "manual_annotation_unverified_against_hf"),
        }
        (staging / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        verify(staging)
        staging.rename(root)
    return verify(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Setup original or current 500-question BIRD Mini-Dev SQLite")
    parser.add_argument("--release", choices=("original", "latest"), default="original")
    parser.add_argument("--revision", help="Hugging Face commit for current Mini-Dev layout")
    parser.add_argument("--root", type=Path, default=None, help="Local dataset directory")
    parser.add_argument("--archive", type=Path, help="Official Google Drive complete-package ZIP, already downloaded")
    parser.add_argument("--annotations", type=Path, help="SQLite JSON/JSONL for manual setup; provenance marked unverified")
    parser.add_argument("--verify-only", action="store_true", help="Check installed dataset without network")
    args = parser.parse_args(argv)
    if args.verify_only and (args.archive or args.annotations):
        parser.error("--verify-only cannot be combined with --archive or --annotations")
    args.root = args.root or (DEFAULT_ROOT if args.release == "original" else DEFAULT_ROOT.parent / "mini-dev-2026")
    try:
        if args.verify_only:
            installed = BirdDataset(args.root).manifest
            expected = "bird-mini-dev-2026-sqlite" if args.release == "latest" else "bird-mini-dev-original-sqlite"
            if installed["dataset"] != expected or (args.revision and installed["annotations_source_revision"] != args.revision):
                raise ValueError("Installed release/revision differs from requested verification")
        result = verify(args.root) if args.verify_only else setup(args.root, archive=args.archive, annotations=args.annotations, release=args.release, revision=args.revision)
    except (ValueError, FileNotFoundError, RuntimeError, zipfile.BadZipFile, OSError) as exc:
        parser.exit(1, f"BIRD setup/verification failed: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
