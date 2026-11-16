"""Deterministic, immutable sharded inference artifacts for KORA role specialization."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
import shutil
from pathlib import Path
import tempfile


ARTIFACTS = ("predictions.jsonl", "traces.jsonl", "reviews/review_reports.jsonl")
CONSISTENCY_KEYS = (
    "agent_variant", "dataset_manifest", "selection_sha256", "selection_id",
    "split", "run_id", "selection_size", "shard_count", "generator_provider",
    "generator_model", "generator_reasoning_effort", "reviewer_provider",
    "reviewer_model", "reviewer_reasoning_effort", "prompt_variant",
    "b0_prompt_sha256", "reviewer_prompt_version", "reviewer_prompt_sha256",
    "max_attempts", "max_review_model_calls", "max_inspections",
    "max_total_model_calls", "max_total_tool_calls", "max_total_sql_calls",
    "preview_rows", "source_revision", "output_format_version",
)


def sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def shard_slice(selected: list[dict], index: int, count: int):
    """1-based contiguous selection positions, NOT BIRD question IDs."""
    if type(index) is not int or type(count) is not int or not 1 <= count <= len(selected) or not 1 <= index <= count:
        raise ValueError("Shard index/count must identify a nonempty part of the selection")
    size = (len(selected) + count - 1) // count
    start = (index - 1) * size
    end = min(start + size, len(selected))
    if start >= end:
        raise ValueError("Empty shard")
    return selected[start:end], {"shard_index": index, "shard_count": count,
                                 "position_start": start + 1, "position_end": end,
                                 "selection_size": len(selected)}


def shard_dir(root: Path, index: int, count: int) -> Path:
    return root / "shards" / f"shard-{index:02d}-of-{count:02d}"


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise ValueError(f"Missing shard artifact: {path}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Non-object JSONL entry in {path}")
            rows.append(row)
    return rows


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2,
                               allow_nan=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")



@contextmanager
def inference_lock(run_dir: Path):
    """Cross-platform nonblocking run lock, released even after a process crash."""
    lock = run_dir / ".inference.lock"
    fd = os.open(lock, os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(fd, "r+b") as handle:
        if os.name == "nt":
            import msvcrt
            if not handle.read(1):
                handle.seek(0)
                handle.write(b"0")
                handle.flush()
            try:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ValueError(f"Another worker is writing this run: {lock}") from exc
        else:
            import fcntl
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ValueError(f"Another worker is writing this run: {lock}") from exc
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _resume_rows(path: Path, protected: int) -> tuple[list[dict], bytes]:
    """Accept an interrupted last JSONL write only when it will be discarded."""
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing or unsafe resume artifact: {path}")
    lines = path.read_bytes().splitlines(keepends=True)
    rows = []
    for pos, raw in enumerate(lines):
        try:
            row = json.loads(raw)
            if not isinstance(row, dict):
                raise ValueError("JSONL entry is not an object")
        except (ValueError, UnicodeError) as exc:
            if pos == len(lines) - 1 and len(rows) >= protected:
                break
            raise ValueError(f"Invalid protected JSONL entry {pos + 1}: {path}") from exc
        rows.append(row)
    if len(rows) < protected:
        raise ValueError(f"Not enough existing records to preserve: {path}")
    if protected and not lines[protected - 1].endswith(b"\n"):
        raise ValueError(f"Unterminated protected JSONL entry: {path}")
    return rows, b"".join(lines[:protected])


def _verify_resume_identity(rows: dict, selected: list[dict], config: dict) -> None:
    """All readable records must belong to this exact shard and model pair."""
    for filename, entries in rows.items():
        if len(entries) > len(selected):
            raise ValueError(f"Too many records in {filename}")
        for pos, row in enumerate(entries):
            question = selected[pos]
            if row.get("question_id") != question["question_id"]:
                raise ValueError(f"Question ID/order mismatch at position {pos + 1}: {filename}")
            if filename == "predictions.jsonl":
                expected = {
                    "db_id": question["db_id"],
                    "provider": config["generator_provider"],
                    "model": config["generator_model"],
                    "reasoning_effort": config["generator_reasoning_effort"],
                    "reviewer_provider": config["reviewer_provider"],
                    "reviewer_model": config["reviewer_model"],
                    "reviewer_reasoning_effort": config["reviewer_reasoning_effort"],
                }
                if any(row.get(k) != v for k, v in expected.items()):
                    raise ValueError(f"Model/database mismatch at position {pos + 1}")
            if filename == "traces.jsonl":
                for role in ("generator", "reviewer"):
                    identity = row.get(role)
                    if not isinstance(identity, dict):
                        raise ValueError(f"Missing {role} identity at position {pos + 1}")
                    expected = {
                        "provider": config[f"{role}_provider"],
                        "model": config[f"{role}_model"],
                        "reasoning_effort": config[f"{role}_reasoning_effort"],
                    }
                    if any(identity.get(k) != v for k, v in expected.items()):
                        raise ValueError(f"Trace model mismatch at position {pos + 1}")
                if row.get("question") != question.get("question") or (
                    row.get("evidence") != question.get("evidence")
                ):
                    raise ValueError(f"Question content mismatch at position {pos + 1}")


def prepare_in_place_resume(*, run_dir: Path, selected: list[dict],
                            start_position: int, config: dict) -> dict:
    """Back up all existing files, then keep exactly the requested prefix.

    No shard is created and no existing record before start_position is changed.
    Only use while holding inference_lock.
    """
    if type(start_position) is not int or not 1 <= start_position <= len(selected):
        raise ValueError("Invalid --start-position for this shard")
    if not run_dir.is_dir() or run_dir.is_symlink():
        raise ValueError(f"Existing run directory required: {run_dir}")
    if (run_dir / "scores").exists() or (run_dir.parent.parent / "inference_manifest.json").exists():
        raise ValueError("Cannot replace a scored or already merged shard")
    protected = start_position - 1
    current = {}
    for name in ("inference_config.json", "inference_manifest.json"):
        path = run_dir / name
        if path.exists():
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"Unsafe metadata file: {path}")
            current[name] = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(current[name], dict):
                raise ValueError(f"Invalid metadata file: {path}")
    for old in current.values():
        for key in CONSISTENCY_KEYS:
            if key != "source_revision" and key in old and old[key] != config.get(key):
                raise ValueError(f"Resume configuration mismatch: {key}")
        for key in ("question_ids", "expected_questions", "shard_index",
                    "position_start", "position_end"):
            if key in old and old[key] != config.get(key):
                raise ValueError(f"Resume selection mismatch: {key}")
        if old.get("merge_complete"):
            raise ValueError("Cannot resume an already merged run")
    rows, prefixes = {}, {}
    for name in ARTIFACTS:
        rows[name], prefixes[name] = _resume_rows(run_dir / name, protected)
    _verify_resume_identity(rows, selected, config)
    counts = {name: len(rows[name]) for name in ARTIFACTS}
    # A prior crash during suffix truncation may leave unequal file lengths.
    # All preserved rows have been validated; the suffix will be discarded.
    completed = current.get("inference_manifest.json")
    if completed:
        if not completed.get("completed"):
            raise ValueError("Malformed completed-run manifest")
        checksums = ("prediction_sha256", "trace_sha256", "review_reports_sha256")
        if any(completed.get(k) != sha(run_dir / name)
               for name, k in zip(ARTIFACTS, checksums)):
            raise ValueError("Existing completed-run checksum mismatch")
        if any(count != len(selected) for count in counts.values()):
            raise ValueError("Completed manifest has incomplete records")

    backups = run_dir / "resume_backups"
    backups.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = backups / stamp
    backup.mkdir()
    for name in (*ARTIFACTS, *current.keys()):
        dest = backup / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(run_dir / name, dest)
        if sha(dest) != sha(run_dir / name):
            raise ValueError(f"Backup verification failed: {name}")

    # Old manifest must not claim completion while replacement is in progress.
    (run_dir / "inference_manifest.json").unlink(missing_ok=True)
    for name in ARTIFACTS:
        path = run_dir / name
        temp = path.with_name(f".{path.name}.resume-tmp")
        with temp.open("wb") as stream:
            stream.write(prefixes[name])
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    created = (current.get("inference_config.json", {}).get("created_utc")
               or (completed or {}).get("created_utc")
               or datetime.now(timezone.utc).isoformat())
    config_path = run_dir / "inference_config.json"
    if not config_path.exists():
        _write_json(config_path, {**config, "created_utc": created})
    history_path = run_dir / "resume_history.jsonl"
    entry = {
        "resumed_utc": datetime.now(timezone.utc).isoformat(),
        "start_position": start_position, "replaced_from_position": start_position,
        "previous_record_counts": counts,
        "backup_directory": str(backup),
        "previous_source_revision": (completed or {}).get("source_revision"),
        "source_revision": config.get("source_revision"),
        "legacy_configuration_unverified": not bool(current),
    }
    with history_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return {
        "created_utc": created,
        "missing": sum(row.get("predicted_sql") is None
                       for row in rows["predictions.jsonl"][:protected]),
        "backup_directory": str(backup),
    }


def load_resume_history(run_dir: Path) -> list[dict]:
    path = run_dir / "resume_history.jsonl"
    return _read_jsonl(path) if path.exists() else []


def merge_shards(*, folder: Path, run_root: Path, split_dirs: dict[str, Path],
                 selections: dict[str, list[dict]], dataset_manifest: dict,
                 shard_count: int, variant: str, run_id: str) -> dict:
    """Verify every immutable shard before publishing combined and per-split outputs.

    No gold/reference SQL is read; only validated public question IDs are used.
    """
    if not 1 <= shard_count <= 999:
        raise ValueError("Invalid shard count")
    all_questions = selections["dev"] + selections["test"]
    expected_ids = [q["question_id"] for q in all_questions]
    if len(expected_ids) != len(set(expected_ids)):
        raise ValueError("Duplicate question IDs in selected dataset")
    if shard_count > len(expected_ids):
        raise ValueError("More shards than questions")
    if not run_root.is_dir():
        raise ValueError(f"Missing run root: {run_root}")
    for split, target in split_dirs.items():
        if split not in ("dev", "test") or target.exists() or target.is_symlink():
            raise ValueError(f"Refusing to overwrite target split: {target}")
    if any((run_root / name).exists() or (run_root / name).is_symlink()
           for name in (*ARTIFACTS, "inference_manifest.json")):
        raise ValueError("Merged output already exists: refusing to overwrite")
    selection_hash = sha(folder / "selection_manifest.json")
    manifests = []
    records = {name: [] for name in ARTIFACTS}
    for index in range(1, shard_count + 1):
        subdir = shard_dir(run_root, index, shard_count)
        manifest_file = subdir / "inference_manifest.json"
        if not manifest_file.is_file():
            raise ValueError(f"Missing completed shard {index}")
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        selected, info = shard_slice(all_questions, index, shard_count)
        ids = [q["question_id"] for q in selected]
        required = {
            "completed": True, "agent_variant": variant, "split": "all",
            "run_id": run_id, "selection_id": folder.name,
            "selection_sha256": selection_hash,
            "dataset_manifest": dataset_manifest, "expected_questions": len(ids),
            "question_ids": ids, **info,
        }
        if any(manifest.get(k) != value for k, value in required.items()):
            raise ValueError(f"Shard {index} metadata or question range mismatch")
        if manifests:
            differences = [k for k in CONSISTENCY_KEYS
                           if manifest.get(k) != manifests[0].get(k)]
            if differences and not (
                differences == ["source_revision"] and
                (manifest.get("resume_history") or manifests[0].get("resume_history"))
            ):
                raise ValueError(f"Shard {index} model/prompt/budget/revision mismatch: "
                                 + ", ".join(differences))
        for filename, digest_name in zip(
            ARTIFACTS, ("prediction_sha256", "trace_sha256", "review_reports_sha256")
        ):
            path = subdir / filename
            if sha(path) != manifest.get(digest_name):
                raise ValueError(f"Shard {index} checksum mismatch: {filename}")
            part = _read_jsonl(path)
            if [record.get("question_id") for record in part] != ids:
                raise ValueError(f"Shard {index} missing/reordered/duplicate IDs: {filename}")
            records[filename].extend(part)
        for row in records["predictions.jsonl"][-len(ids):]:
            if (row.get("provider") != manifest.get("generator_provider") or
                row.get("model") != manifest.get("generator_model") or
                row.get("reviewer_provider") != manifest.get("reviewer_provider") or
                row.get("reviewer_model") != manifest.get("reviewer_model")):
                raise ValueError(f"Shard {index} prediction model mismatch")
        manifests.append(manifest)
    if any([x["question_id"] for x in records[filename]] != expected_ids
           for filename in ARTIFACTS):
        raise ValueError("Merged question coverage mismatch")

    selected_id_sets = {split: {q["question_id"] for q in questions}
                        for split, questions in selections.items()}
    with tempfile.TemporaryDirectory(prefix=".merge-staging-", dir=run_root) as stage:
        staging = Path(stage)
        staged = {"all": staging / "all", **{split: staging / split
                                               for split in ("dev", "test")}}
        for split, directory in staged.items():
            if split == "all":
                parts = records
                questions = all_questions
            else:
                members = selected_id_sets[split]
                parts = {name: [row for row in records[name]
                                if row["question_id"] in members]
                         for name in ARTIFACTS}
                questions = selections[split]
            ids = [q["question_id"] for q in questions]
            if any([r["question_id"] for r in parts[name]] != ids for name in ARTIFACTS):
                raise ValueError(f"Merged {split} question order mismatch")
            for filename, rows in parts.items():
                _write_jsonl(directory / filename, rows)
            original = manifests[0]
            new_manifest = {k: v for k, v in original.items()
                            if k not in ("shard_index", "shard_count", "position_start", "position_end")}
            new_manifest.update({
                "split": split, "completed": True, "question_ids": ids,
                "expected_questions": len(ids), "selection_size": len(ids),
                "missing_final_sql": sum(row.get("predicted_sql") is None
                                         for row in parts["predictions.jsonl"]),
                "prediction_sha256": sha(directory / "predictions.jsonl"),
                "trace_sha256": sha(directory / "traces.jsonl"),
                "review_reports_sha256": sha(directory / "reviews/review_reports.jsonl"),
                "merged_from_shards": [str(shard_dir(run_root, i, shard_count))
                                       for i in range(1, shard_count + 1)],
                "merge_complete": True,
                "source_revisions": sorted({str(m.get("source_revision"))
                                             for m in manifests}),
            })
            _write_json(directory / "inference_manifest.json", new_manifest)
        # All validation/staging happens before any publication. Never replace
        # existing runs, even if another process creates one after preflight.
        published = []
        try:
            for split in ("dev", "test"):
                target = split_dirs[split]
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() or target.is_symlink():
                    raise ValueError(f"Target appeared during merge: {target}")
                os.rename(staged[split], target)
                published.append(target)
            for filename in (*ARTIFACTS, "inference_manifest.json"):
                target = run_root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() or target.is_symlink():
                    raise ValueError(f"Merged artifact appeared during merge: {target}")
                os.rename(staged["all"] / filename, target)
                published.append(target)
        except Exception:
            for target in reversed(published):
                if target.is_dir():
                    import shutil
                    shutil.rmtree(target)
                else:
                    target.unlink(missing_ok=True)
            raise
    return {"question_count": len(expected_ids),
            "dev_count": len(selections["dev"]),
            "test_count": len(selections["test"]),
            "shard_count": shard_count,
            "merged_root": str(run_root)}
