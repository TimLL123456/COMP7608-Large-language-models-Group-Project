"""Restore schema-checked description CSVs without replacing existing dataset files.

Download the official Mini-Dev complete package separately. This command reads
only CSV members; it never extracts databases or annotations from that archive.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

from .bird import BirdDataset, sha256_file


def _csv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def plan_descriptions(dataset, archive: Path, official_schema: Path) -> tuple[dict, dict]:
    """Validate the entire input before returning any proposed CSV writes."""
    planned, audit = {}, {}
    official = json.loads(Path(official_schema).read_text(encoding="utf-8"))
    with zipfile.ZipFile(archive) as source:
        for db_id in sorted(dataset.manifest["databases"]):
            schema = dataset.get_schema(db_id)
            folder = dataset.get_database_path(db_id).parent / "database_description"
            if folder.is_symlink():
                raise ValueError(f"Symlinked description directory: {folder}")
            tables = set()
            files = []
            for member in source.infolist():
                name = member.filename
                if ("__MACOSX" in name.split("/") or
                        f"/{db_id}/database_description/" not in name or
                        not name.endswith(".csv")):
                    continue
                filename = Path(name).name
                matching = [t for t in schema if t.casefold() == filename[:-4].casefold()]
                if len(matching) != 1 or matching[0] in tables:
                    raise ValueError(f"Unknown or duplicate description table: {db_id}/{name}")
                table = matching[0]
                tables.add(table)
                raw = source.read(member)
                reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig", errors="replace")))
                rows = list(reader)
                fields = reader.fieldnames or []
                key = next((k for k in fields if k.strip().lower() == "original_column_name"), None)
                if not rows or key is None or any(not isinstance(r.get(key), str) for r in rows):
                    raise ValueError(f"Missing column descriptions: {db_id}/{filename}")
                actual = {c["name"].strip().casefold() for c in schema[table]["columns"]}
                names = [r[key].strip().casefold() for r in rows]
                if len(names) != len(set(names)) or "" in names:
                    raise ValueError(f"Duplicate or empty column: {db_id}/{filename}")
                extra = set(names) - actual
                missing = actual - set(names)
                adaptation = None
                if extra == {"wins"} and db_id == "formula_1" and table == "constructors":
                    raw = _csv_bytes(fields, [r for r in rows if r[key].strip().casefold() != "wins"])
                    extra = set()
                    adaptation = "Removed nonexistent constructors.wins row"
                if missing or extra:
                    raise ValueError(f"Column mismatch: {db_id}/{filename}; missing={sorted(missing)}, extra={sorted(extra)}")
                planned[folder / filename] = raw
                files.append({"file": filename, "member": name,
                              "source_sha256": hashlib.sha256(source.read(member)).hexdigest(),
                              "installed_sha256": hashlib.sha256(raw).hexdigest(),
                              "adaptation": adaptation})
            missing_tables = set(schema) - tables
            if missing_tables == {"element"} and db_id == "toxicology":
                text = official.get(db_id, "")
                # The reviewed official 2026 schema has names/types, no semantics.
                marker = "CREATE TABLE `element` ("
                if marker not in text:
                    raise ValueError("Official schema is missing toxicology.element")
                block = text.split(marker, 1)[1].split(");", 1)[0]
                columns = schema["element"]["columns"]
                if {c["name"] for c in columns} != {"element_id", "element_name"}:
                    raise ValueError("Unexpected toxicology.element columns")
                if any(f"`{c['name']}` {c['type']}" not in block for c in columns):
                    raise ValueError("Official element schema disagrees with SQLite")
                fields = ["original_column_name", "column_name", "column_description", "data_format", "value_description"]
                raw = _csv_bytes(fields, [dict(zip(fields, [c["name"], c["name"], "", c["type"], ""])) for c in columns])
                planned[folder / "element.csv"] = raw
                files.append({"file": "element.csv", "installed_sha256": hashlib.sha256(raw).hexdigest(),
                              "adaptation": "Schema-only supplement; no invented semantic descriptions"})
                missing_tables = set()
            if missing_tables:
                raise ValueError(f"Missing tables for {db_id}: {sorted(missing_tables)}")
            audit[db_id] = files
    return planned, audit


def restore_descriptions(dataset, archive: Path, official_schema: Path, *, verify_existing=False) -> dict:
    """Restore only new CSVs, or verify an already restored installation."""
    planned, audit = plan_descriptions(dataset, archive, official_schema)
    # Check all destinations before writing any CSV. Exclusive creation also
    # prevents overwriting a file created by another process after this check.
    for path, raw in planned.items():
        if path.is_symlink():
            raise ValueError(f"Symlinked description file: {path}")
        if verify_existing:
            if not path.is_file() or path.read_bytes() != raw:
                raise ValueError(f"Installed description differs: {path}")
        elif path.exists():
            raise FileExistsError(f"Refusing to overwrite: {path}")
    original = {p: sha256_file(p) for p in dataset.root.rglob("*") if p.is_file()}
    if not verify_existing:
        for path, raw in planned.items():
            path.parent.mkdir(exist_ok=True)
            with path.open("xb") as stream:
                stream.write(raw)
    if any(sha256_file(p) != digest for p, digest in original.items()):
        raise ValueError("An existing dataset file changed during restoration")
    return {"status": "PASS", "mode": "verify" if verify_existing else "restore",
            "archive_sha256": sha256_file(archive),
            "official_schema_sha256": sha256_file(official_schema),
            "existing_files_unchanged": len(original), "csv_files": len(planned),
            "databases": audit}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--official-schema", type=Path, required=True)
    parser.add_argument("--verify-existing", action="store_true")
    parser.add_argument("--report", type=Path, help="New audit file; never replaces an existing report")
    args = parser.parse_args(argv)
    if args.report is not None and args.report.exists():
        parser.error("Report already exists; choose a new path")
    result = restore_descriptions(BirdDataset(args.dataset_root), args.archive,
                                  args.official_schema, verify_existing=args.verify_existing)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.report is not None:
        with args.report.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    print(json.dumps({k: v for k, v in result.items() if k != "databases"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
