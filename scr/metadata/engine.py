"""Small, run-scoped, database-isolated Markdown metadata knowledge store.

No gold SQL or evaluator imports belong in this module. Each instance is bound by
the runner to one question and active database; tools cannot switch namespaces.
"""
from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile
import threading


SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
NOTE_TYPES = {"database", "table", "column", "metric", "concept"}
TABLE_HEADINGS = ("Business Summary", "Business Use Cases", "Data Granularity", "Data Scope & Exclusions")
COLUMN_HEADINGS = ("Business Meaning", "Business Usage", "Value Meaning", "Calculation Meaning")
MAX_NOTE_CHARS = 1500
MAX_SUMMARY_CHARS = 160
MAX_KEYWORDS = 8
MAX_CONTEXT_CHARS = 6000  # Historical v1.
MAX_DISCOVERY_V2_CONTEXT_CHARS = 20000
BANNED = re.compile(r"(?i)(gold[_ -]?sql|reference[_ -]?sql|final sql query|question[_ -]?id|expected answer)")
WORDS = re.compile(r"[a-z0-9]+")
_LOCK_REGISTRY_GUARD = threading.Lock()
_EVENT_LOCK = threading.Lock()
_DB_LOCKS = {}


def _db_lock(directory: Path):
    with _LOCK_REGISTRY_GUARD:
        return _DB_LOCKS.setdefault(str(directory), threading.RLock())



def _atomic_text(path: Path, text: str) -> None:
    """Write a complete file, never a partially written document."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".metadata-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _serialize(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


class MetadataEngine:
    """One question's view of a persistent experiment's active database notes."""

    def __init__(self, experiment_root: Path, db_id: str, question_id: int,
                 schema: dict, descriptions: dict | None = None,
                 definition_mode: bool = False):
        if not isinstance(db_id, str) or not SAFE_ID.fullmatch(db_id):
            raise ValueError("Invalid database ID")
        if type(question_id) is not int or not isinstance(schema, dict):
            raise ValueError("A question ID and trusted database schema are required")
        self.experiment_root = Path(experiment_root).resolve()
        if self.experiment_root.is_symlink():
            raise ValueError("Knowledge root must not be a symlink")
        self.db_id = db_id
        self.question_id = question_id
        self.schema = schema
        self.descriptions = descriptions or {}
        self.definition_mode = bool(definition_mode)
        self.directory = self.experiment_root / "knowledge" / db_id
        self.index_path = self.directory / "index.json"
        self.events_path = self.experiment_root / "knowledge_operations.jsonl"
        self.loaded_chars = 0
        self.max_context_chars = (MAX_DISCOVERY_V2_CONTEXT_CHARS if self.definition_mode
                                  else MAX_CONTEXT_CHARS)
        self._loaded_revisions = {}
        self.directory.mkdir(parents=True, exist_ok=True)
        self._write_mutex = _db_lock(self.directory)

    def _index(self) -> dict:
        if not self.index_path.exists():
            return {}
        value = json.loads(self.index_path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("Invalid metadata index")
        return value

    def _event(self, action: str, status: str, **fields) -> None:
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"question_id": self.question_id, "db_id": self.db_id,
                   "action": action, "status": status, **fields}
        with _EVENT_LOCK:
            with self.events_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _validate_consistency(self, index: dict) -> None:
        """Detect orphaned notes or mismatched hashes before further writes."""
        notes_dir = self.directory / "notes"
        paths = {p.stem: p for p in notes_dir.glob("*.md")} if notes_dir.exists() else {}
        if set(paths) != set(index):
            raise ValueError("Knowledge notes/index inconsistent; recovery required")
        for note_id, entry in index.items():
            path = paths[note_id]
            if path.is_symlink() or not isinstance(entry, dict):
                raise ValueError("Unsafe note/index entry")
            if sha256(path.read_bytes()).hexdigest() != entry.get("sha256"):
                raise ValueError("Note hash differs from index; recovery required")

    @contextmanager
    def _transaction(self):
        # In-process serialization plus cross-process fail-closed write marker.
        with self._write_mutex:
            marker = self.directory / ".write-lock"
            try:
                marker.mkdir()
            except FileExistsError as exc:
                raise ValueError(
                    "Active or interrupted metadata writer; inspect store before reuse"
                ) from exc
            try:
                self._validate_consistency(self._index())
                yield
            finally:
                marker.rmdir()

    def summaries_for(self, note_ids: list[str]) -> list[dict]:
        """Recover saved-note handoffs without loading full Markdown."""
        with self._write_mutex:
            index = self._index()
            result = []
            for note_id in dict.fromkeys(note_ids):
                entry = index.get(note_id)
                if entry is not None:
                    result.append({
                        "note_id": note_id, "summary": entry["summary"],
                        "table_name": entry["table_name"],
                        "source_refs": entry["source_refs"],
                        "revision": entry["revision"], "status": entry["status"],
                    })
            return result

    @staticmethod
    def _identity(note_type: str, table_name: str, concept_id: str) -> str:
        key = json.dumps([note_type, table_name, concept_id], ensure_ascii=False)
        return "n_" + sha256(key.encode("utf-8")).hexdigest()[:24]

    def _path(self, note_id: str) -> Path:
        if not re.fullmatch(r"n_[0-9a-f]{24}", note_id):
            raise ValueError("Invalid note ID")
        path = self.directory / "notes" / f"{note_id}.md"
        if path.is_symlink():
            raise ValueError("Refusing note symlink")
        return path

    def _table(self, table_name: str) -> str:
        if not isinstance(table_name, str) or len(table_name) > 200:
            raise ValueError("Invalid table name")
        if table_name and table_name not in self.schema:
            raise ValueError("Table not present in active database schema")
        return table_name

    def search(self, query: str, table_name: str = "") -> dict:
        try:
            if not isinstance(query, str) or not query.strip() or len(query) > 240:
                raise ValueError("Search query must contain 1-240 characters")
            table_name = self._table(table_name)
            terms = set(WORDS.findall(query.lower()))
            matches = []
            with self._write_mutex:
                entries = list(self._index().values())
            for entry in entries:
                if table_name and entry["table_name"] not in ("", table_name):
                    continue
                fields = [entry["title"], entry["summary"], entry["concept_id"],
                          *entry["keywords"], entry["table_name"]]
                text = " ".join(fields).lower()
                tokens = set(WORDS.findall(text))
                overlap = len(terms & tokens)
                if not overlap:
                    continue
                exact = query.lower().strip() in text
                matches.append((int(exact), overlap, entry["note_id"],
                                {key: entry[key] for key in
                                 ("note_id", "note_type", "table_name", "concept_id",
                                  "title", "summary", "keywords", "revision", "status")}))
            matches.sort(key=lambda item: (-item[0], -item[1], item[2]))
            candidates = [row[3] for row in matches[:5]]
            # Official database-description snippets are hints, not stored facts.
            hints = []
            for filename, rows in self.descriptions.items():
                for idx, row in enumerate(rows):
                    text = " ".join(str(v) for v in row.values())
                    if terms & set(WORDS.findall(text.lower())):
                        hints.append({"source": f"description:{filename}:{idx + 1}",
                                      "excerpt": text[:240]})
                    if len(hints) >= 3:
                        break
                if len(hints) >= 3:
                    break
            result = {"candidates": candidates, "description_hints": hints}
            self._event("search", "ok", query=query[:160], table_name=table_name,
                        candidates=len(candidates), descriptions=len(hints))
            return result
        except (ValueError, KeyError, TypeError) as exc:
            self._event("search", "error", reason=str(exc))
            return {"error": str(exc)}

    def read(self, note_id: str) -> dict:
        try:
            with self._write_mutex:
                entry = self._index().get(note_id)
                if entry is None:
                    raise ValueError("Unknown note in active database")
                content = self._path(note_id).read_text(encoding="utf-8")
                if sha256(content.encode("utf-8")).hexdigest() != entry["sha256"]:
                    raise ValueError("Note content does not match indexed revision")
                cached = (self.definition_mode and
                          self._loaded_revisions.get(note_id) == entry["revision"])
                if not cached:
                    if self.loaded_chars + len(content) > self.max_context_chars:
                        raise ValueError("Per-question metadata context budget exceeded")
                    self.loaded_chars += len(content)
                    if self.definition_mode:
                        self._loaded_revisions[note_id] = entry["revision"]
                result = {"note_id": note_id, "revision": entry["revision"],
                          "table_name": entry["table_name"], "status": entry["status"],
                          "source_refs": entry["source_refs"], "content": content,
                          "cached": bool(cached)}
            self._event("read", "ok", note_id=note_id,
                        revision=entry["revision"], cached=bool(cached))
            return result
        except (ValueError, KeyError, OSError, TypeError) as exc:
            self._event("read", "error", note_id=str(note_id)[:60], reason=str(exc))
            return {"error": str(exc)}

    def record_decision(self, *, attempt: int, action: str, reason: str,
                        note_ids: list[str] | None = None) -> None:
        """Record the actual A1 decision, including deliberately skipped writes."""
        allowed = {"created", "updated", "reused", "no_note",
                   "insufficient_evidence", "decision_missing", "decision_inconsistent"}
        if type(attempt) is not int or attempt < 1 or attempt > 3 or action not in allowed:
            raise ValueError("Invalid knowledge decision")
        if not isinstance(reason, str) or len(reason) > 400:
            raise ValueError("Invalid knowledge decision reason")
        ids = note_ids or []
        if not isinstance(ids, list) or len(ids) > 5 or any(
            not isinstance(item, str) or not re.fullmatch(r"n_[0-9a-f]{24}", item)
            for item in ids
        ):
            raise ValueError("Invalid note IDs in knowledge decision")
        self._event("decision", "ok", attempt=attempt, decision=action,
                    reason=reason, note_ids=ids)

    def _validate_definition(self, note_type: str, table_name: str,
                             concept_id: str, body: str) -> None:
        """Require the user's eight-part table/column framework for v2 notes."""
        if note_type not in ("table", "column"):
            raise ValueError("v2 only stores table and column definitions")
        if note_type == "table" and concept_id != "table_definition":
            raise ValueError("v2 table note concept ID must be table_definition")
        if note_type == "column":
            columns = {c.get("name") for c in self.schema.get(table_name, {}).get("columns", [])}
            if concept_id not in columns:
                raise ValueError("Column definition must use exact schema column name")
        expected = TABLE_HEADINGS if note_type == "table" else COLUMN_HEADINGS
        sections = re.split(r"(?m)^## ([^\n]+)\s*$", body.strip())
        # The body must have exactly the four named headings, in this order.
        headings = tuple(part.strip() for part in sections[1::2])
        if headings != expected or any(not value.strip() for value in sections[2::2]):
            raise ValueError("Definition must contain four nonempty framework sections, in order")

    def _validated(self, note_type: str, table_name: str, concept_id: str,
                   title: str, summary: str, keywords: str, body: str,
                   source_refs: str) -> tuple[str, dict]:
        if note_type not in NOTE_TYPES:
            raise ValueError("Unknown note type")
        table_name = self._table(table_name)
        if note_type in ("table", "column") and not table_name:
            raise ValueError("Table and column notes require a table scope")
        if not isinstance(concept_id, str) or not concept_id or len(concept_id) > 200:
            raise ValueError("Invalid concept identifier")
        if not (self.definition_mode and note_type == "column") and not SAFE_ID.fullmatch(concept_id):
            raise ValueError("Invalid concept identifier")
        if not isinstance(title, str) or not title.strip() or len(title) > 100:
            raise ValueError("Title must be 1-100 characters")
        if not isinstance(summary, str) or not summary.strip() or len(summary) > MAX_SUMMARY_CHARS:
            raise ValueError("Summary must be 1-160 characters")
        if not isinstance(keywords, str) or not isinstance(body, str) or not isinstance(source_refs, str):
            raise ValueError("Keywords, body and sources must be strings")
        terms = list(dict.fromkeys(s.strip().lower() for s in keywords.split(",") if s.strip()))
        refs = list(dict.fromkeys(s.strip() for s in source_refs.split(";") if s.strip()))
        if len(terms) > MAX_KEYWORDS or any(len(s) > 50 for s in terms):
            raise ValueError("Maximum eight keywords of up to 50 characters")
        if not 1 <= len(refs) <= 6 or any(
            not r.startswith(("schema:", "description:", "values:")) or len(r) > 180 for r in refs
        ):
            raise ValueError("1-6 provenance references required (schema:/description:/values:)")
        if BANNED.search(body + " " + summary):
            raise ValueError("Question answers, gold SQL and reference SQL are not metadata")
        if self.definition_mode:
            self._validate_definition(note_type, table_name, concept_id, body)
        content = (f"# {title.strip()}\n\nType: {note_type}\n"
                   f"Table: {table_name or '(database-wide)'}\n"
                   f"Scope: {concept_id}\nSummary: {summary.strip()}\n"
                   f"Keywords: {', '.join(terms)}\nStatus: provisional\n"
                   f"Sources: {'; '.join(refs)}\n\n{body.strip()}\n")
        if len(content) > MAX_NOTE_CHARS:
            raise ValueError(f"Metadata note exceeds {MAX_NOTE_CHARS} characters")
        note_id = self._identity(note_type, table_name, concept_id)
        entry = {"note_id": note_id, "note_type": note_type, "table_name": table_name,
                 "concept_id": concept_id, "title": title.strip(),
                 "summary": summary.strip(), "keywords": terms,
                 "source_refs": refs, "status": "provisional",
                 "revision": 0, "sha256": sha256(content.encode("utf-8")).hexdigest()}
        return content, entry

    def create(self, note_type: str, table_name: str, concept_id: str, title: str,
               summary: str, keywords: str, body: str, source_refs: str) -> dict:
        try:
            with self._transaction():
                content, entry = self._validated(note_type, table_name, concept_id,
                                                  title, summary, keywords, body, source_refs)
                note_id = entry["note_id"]
                index = self._index()
                if note_id in index or self._path(note_id).exists():
                    raise ValueError("Note already exists; read and update instead")
                entry["revision"] = 1
                _atomic_text(self._path(note_id), content)
                index[note_id] = entry
                _atomic_text(self.index_path, _serialize(index))
                self._event("create", "ok", note_id=note_id, revision=1)
                return {"note_id": note_id, "revision": 1, "created": True}
        except (ValueError, OSError, TypeError, KeyError) as exc:
            self._event("create", "error", reason=str(exc))
            return {"error": str(exc)}

    def update(self, note_id: str, expected_revision: int, title: str,
               summary: str, keywords: str, body: str, source_refs: str) -> dict:
        try:
            with self._transaction():
                index = self._index()
                old = index.get(note_id)
                if old is None:
                    raise ValueError("Unknown note; create it first")
                if type(expected_revision) is not int or old["revision"] != expected_revision:
                    raise ValueError("Stale note revision; reread before updating")
                content, entry = self._validated(
                    old["note_type"], old["table_name"], old["concept_id"],
                    title, summary, keywords, body, source_refs)
                if note_id != entry["note_id"]:
                    raise ValueError("Note identity cannot change")
                current = self._path(note_id).read_text(encoding="utf-8")
                if sha256(current.encode("utf-8")).hexdigest() != old["sha256"]:
                    raise ValueError("Existing note changed without index update")
                entry["revision"] = expected_revision + 1
                _atomic_text(self._path(note_id), content)
                index[note_id] = entry
                _atomic_text(self.index_path, _serialize(index))
                self._event("update", "ok", note_id=note_id, revision=entry["revision"])
                return {"note_id": note_id, "revision": entry["revision"], "updated": True}
        except (ValueError, OSError, TypeError, KeyError) as exc:
            self._event("update", "error", note_id=str(note_id)[:60], reason=str(exc))
            return {"error": str(exc)}
