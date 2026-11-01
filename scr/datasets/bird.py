"""Original BIRD Mini-Dev (SQLite) access for KORA agents.

Agent-facing functions deliberately omit reference SQL. Evaluation-only references
are handled by a separate class and must never be passed to an agent or prompt.
"""

from __future__ import annotations

import csv
from contextlib import contextmanager
import hashlib
import json
from itertools import islice
import random
import sqlite3
from collections import defaultdict
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "data" / "bird" / "original-mini-dev"
EXPECTED_QUESTIONS = 500
EXPECTED_DATABASES = 11
DIFFICULTIES = {"simple", "moderate", "challenging"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_annotations(path: Path, *, expected_count: int = EXPECTED_QUESTIONS,
                     expected_databases: int = EXPECTED_DATABASES) -> list[dict]:
    """Validate original SQLite annotations; fail closed on V2 or malformed input."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != expected_count:
        raise ValueError(f"Expected {expected_count} original Mini-Dev questions, got {len(data) if isinstance(data, list) else 'non-list'}")
    required = {"question_id", "db_id", "question", "evidence", "SQL", "difficulty"}
    ids, db_ids = set(), set()
    for row in data:
        if not isinstance(row, dict) or not required.issubset(row):
            raise ValueError("Original Mini-Dev record missing required fields")
        qid = row["question_id"]
        if not isinstance(qid, int) or isinstance(qid, bool) or qid in ids:
            raise ValueError(f"Duplicate/invalid question_id: {qid!r}")
        ids.add(qid)
        dbid = row["db_id"]
        if not isinstance(dbid, str) or not dbid or "/" in dbid or "\\" in dbid or dbid in {".", ".."}:
            raise ValueError(f"Invalid database ID: {dbid!r}")
        db_ids.add(dbid)
        if not isinstance(row["question"], str) or not row["question"].strip():
            raise ValueError(f"Empty question {qid}")
        if not isinstance(row["evidence"], str):
            raise ValueError(f"Invalid evidence {qid}")
        if not isinstance(row["SQL"], str) or not row["SQL"].strip():
            raise ValueError(f"Empty reference SQL {qid}")
        if row["difficulty"] not in DIFFICULTIES:
            raise ValueError(f"Unexpected difficulty for {qid}: {row['difficulty']!r}")
    if len(db_ids) != expected_databases:
        raise ValueError(f"Expected {expected_databases} databases, got {len(db_ids)}")
    return data


def make_split(rows: list[dict], seed: int = 42, test_size: int = 100,
               *, heldout: int | None = None) -> dict[str, list[int]]:
    """Deterministic 80/20 question-level split, stratified by (db_id, difficulty).

    'heldout' is an optional legacy keyword; both spellings select the same IDs.
    """
    if heldout is not None:
        if test_size != 100:
            raise ValueError("Specify test_size or legacy heldout, not both")
        test_size = heldout
    if not 0 < test_size < len(rows):
        raise ValueError("test_size must be smaller than dataset size")
    groups = defaultdict(list)
    for row in rows:
        groups[(row["db_id"], row["difficulty"])].append(row["question_id"])
    ordered = sorted(groups)
    target = {key: len(groups[key]) * test_size / len(rows) for key in ordered}
    counts = {key: int(target[key]) for key in ordered}
    missing = test_size - sum(counts.values())
    rng = random.Random(seed)
    tie_break = {key: rng.random() for key in ordered}
    priority = sorted(ordered, key=lambda k: (-(target[k] - counts[k]), tie_break[k], k))
    for key in priority[:missing]:
        counts[key] += 1
    test_ids = []
    for key in ordered:
        ids = sorted(groups[key])
        random.Random(f"bird-{seed}-{key[0]}-{key[1]}").shuffle(ids)
        test_ids.extend(ids[:counts[key]])
    selected = set(test_ids)
    return {"dev": sorted(row["question_id"] for row in rows if row["question_id"] not in selected),
            "test": sorted(test_ids)}


@contextmanager
def read_only_connection(db: Path):
    if not Path(db).is_file():
        raise FileNotFoundError(f"SQLite file missing: {db}")
    conn = sqlite3.connect(Path(db).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        conn.execute("PRAGMA query_only=ON")
        yield conn
    finally:
        conn.close()


class BirdDataset:
    """Public agent-facing dataset reader: no reference SQL in returned rows."""

    def __init__(self, root: Path = DEFAULT_ROOT):
        self.root = Path(root).resolve()
        manifest_file = self.root / "dataset_manifest.json"
        self.manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        if self.manifest.get("dataset") != "bird-mini-dev-original-sqlite":
            raise ValueError("Manifest does not describe original BIRD Mini-Dev SQLite")
        self.annotations_path = self.root / "annotations.json"
        if sha256_file(self.annotations_path) != self.manifest["annotations_sha256"]:
            raise ValueError("Dataset annotations changed since setup")
        self._rows = read_annotations(self.annotations_path)
        self._by_id = {row["question_id"]: row for row in self._rows}
        raw_split = self.manifest["split"]
        if set(raw_split) not in ({"dev", "test"}, {"dev", "heldout"}):
            raise ValueError("Split manifest must use dev/test or legacy dev/heldout")
        self._split = {"dev": raw_split["dev"],
                       "test": raw_split["test"] if "test" in raw_split else raw_split["heldout"]}
        ids = set(self._by_id)
        if (set(self._split["dev"]) | set(self._split["test"])) != ids or set(self._split["dev"]) & set(self._split["test"]):
            raise ValueError("Split manifest does not match annotations")
        if len(self._split["dev"]) != 400 or len(self._split["test"]) != 100:
            raise ValueError("Split must contain 400 development and 100 local-test questions")
        if self._split != make_split(self._rows, seed=self.manifest["split_seed"]):
            raise ValueError("Split manifest was not generated deterministically")
        self._dbs = self.manifest["databases"]
        if set(self._dbs) != {r["db_id"] for r in self._rows}:
            raise ValueError("Database inventory and questions disagree")

    @staticmethod
    def _public(row: dict) -> dict:
        return {key: row[key] for key in ("question_id", "db_id", "question", "evidence", "difficulty")}

    def load_questions(self) -> list[dict]:
        return [self._public(r) for r in self._rows]

    def get_agent_input(self, question_id: int) -> dict:
        return self._public(self._by_id[question_id])

    def get_split(self, split_name: str) -> list[dict]:
        if split_name == "heldout":  # Backward compatibility for saved experiments.
            split_name = "test"
        if split_name not in ("dev", "test"):
            raise ValueError("Use split_name='dev' or 'test'")
        return [self.get_agent_input(qid) for qid in self._split[split_name]]

    def get_database_path(self, db_id: str) -> Path:
        if db_id not in self._dbs:
            raise KeyError(f"Unknown BIRD database: {db_id}")
        relative = Path(self._dbs[db_id]["path"])
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root) or not path.is_file():
            raise ValueError(f"Unsafe/missing database path for {db_id}")
        return path

    def get_schema(self, db_id: str) -> dict:
        db = self.get_database_path(db_id)
        with read_only_connection(db) as conn:
            names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            schema = {}
            for name in names:
                quoted = '"' + name.replace('"', '""') + '"'
                schema[name] = {
                    "columns": [{"name": r[1], "type": r[2], "not_null": bool(r[3]), "primary_key_order": r[5]}
                                for r in conn.execute(f"PRAGMA table_info({quoted})")],
                    "foreign_keys": [{"table": r[2], "from": r[3], "to": r[4], "id": r[0]}
                                     for r in conn.execute(f"PRAGMA foreign_key_list({quoted})")],
                }
            return schema

    def get_descriptions(self, db_id: str, max_rows_per_file: int = 2000) -> dict[str, list[dict]]:
        db = self.get_database_path(db_id)
        folder = db.parent / "database_description"
        if not folder.is_dir():
            folder = db.parent.parent / "database_description"
        if not folder.is_dir():
            return {}
        out = {}
        for file in sorted(folder.glob("*.csv")):
            with file.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
                reader = csv.DictReader(handle)
                out[file.name] = list(islice(reader, max_rows_per_file))
        return out


class BirdEvaluationReferences:
    """Evaluation-only access; never construct or share this object in an agent runtime."""

    def __init__(self, root: Path = DEFAULT_ROOT):
        self._dataset = BirdDataset(root)
        self._reference = {r["question_id"]: r["SQL"] for r in self._dataset._rows}

    def get_reference_sql(self, question_id: int) -> str:
        return self._reference[question_id]
