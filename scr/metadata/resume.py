"""Conservative, non-destructive preflight for resuming partial Metadata inference.

No model calls or modification occurs during validation. A partial run is
resumable only if predictions/traces are an exact question prefix and all
metadata writes are attributable to completed questions. No guessed rollback.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from scr.baselines import bird_b0 as b0


_NOTE_ID = re.compile(r"n_[0-9a-f]{24}\Z")


def _read_jsonl(path: Path, *, required: bool = False) -> list[dict]:
    if not path.is_file():
        if required:
            raise ValueError(f"Missing partial-run artifact: {path.name}")
        return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"{path.name}: blank/unfinished row {line_no}")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}: truncated/invalid JSON row {line_no}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path.name}: invalid record at row {line_no}")
        rows.append(row)
    return rows


def _audit_knowledge(experiment_dir: Path, permitted_questions: set[int]) -> None:
    """Correlate note revisions to successful, question-scoped write events."""
    history = _read_jsonl(experiment_dir / "knowledge_operations.jsonl")
    revisions: dict[tuple[str, str], int] = {}
    for event in history:
        if type(event.get("question_id")) is not int or event["question_id"] not in permitted_questions:
            raise ValueError(
                "Uncommitted question has metadata activity: cannot safely resume "
                "without a matching state snapshot")
        if event.get("action") in ("create", "update") and event.get("status") == "ok":
            db, note_id, revision = (event.get("db_id"), event.get("note_id"),
                                     event.get("revision"))
            if not isinstance(db, str) or not isinstance(note_id, str):
                raise ValueError("Invalid metadata write event")
            key = (db, note_id)
            next_revision = revisions.get(key, 0) + 1
            if revision != next_revision:
                raise ValueError("Metadata write/revision history is inconsistent")
            revisions[key] = next_revision

    knowledge = experiment_dir / "knowledge"
    observed: dict[tuple[str, str], int] = {}
    if not knowledge.exists():
        if revisions:
            raise ValueError("Knowledge files missing despite successful write events")
        return
    if knowledge.is_symlink():
        raise ValueError("Knowledge directory cannot be a symlink")
    for path in knowledge.rglob("*"):
        if path.is_symlink():
            raise ValueError("Knowledge store contains a symlink")
        if not path.is_file():
            continue
        relative = path.relative_to(knowledge)
        parts = relative.parts
        if len(parts) == 2 and parts[1] == "index.json":
            index = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(index, dict):
                raise ValueError("Invalid note index")
            db = parts[0]
            for note_id, entry in index.items():
                if not _NOTE_ID.fullmatch(note_id) or not isinstance(entry, dict):
                    raise ValueError("Malformed metadata note index")
                if entry.get("note_id") != note_id:
                    raise ValueError("Metadata note identity does not match index")
                content_path = knowledge / db / "notes" / f"{note_id}.md"
                if not content_path.is_file() or content_path.is_symlink():
                    raise ValueError("Indexed note is missing or unsafe")
                content = content_path.read_text(encoding="utf-8")
                if sha256(content.encode("utf-8")).hexdigest() != entry.get("sha256"):
                    raise ValueError("Knowledge note content differs from its index")
                revision = entry.get("revision")
                if type(revision) is not int or revision < 1:
                    raise ValueError("Invalid note revision")
                observed[(db, note_id)] = revision
        elif len(parts) == 3 and parts[1] == "notes" and (
                parts[2].startswith("n_") and parts[2].endswith(".md")):
            continue
        else:
            raise ValueError(f"Unexpected knowledge file: {relative}")
    if observed != revisions:
        raise ValueError("Knowledge store cannot be reconciled to completed write history")
    # Reject orphaned notes even if the index and event history agree.
    for path in knowledge.rglob("*.md"):
        db, folder, filename = path.relative_to(knowledge).parts
        if folder != "notes" or (db, filename[:-3]) not in observed:
            raise ValueError("Unindexed note in knowledge directory")


def audit_partial_run(folder: Path, experiment_dir: Path, run_dir: Path,
                      questions: list[dict], *, split: str, provider: str,
                      model_name: str, previous_dev_ids: set[int]) -> tuple[list[int], int, list[dict]]:
    """Return completed prefix IDs, existing missing-SQL count, and label corrections.

    Raises ValueError rather than modifying or guessing about incomplete state.
    This also supports legacy partial runs created before --resume existed.
    """
    if (run_dir / "inference_manifest.json").exists():
        raise ValueError("Inference already completed; refusing to resume")
    predictions = _read_jsonl(run_dir / "predictions.jsonl", required=True)
    traces = _read_jsonl(run_dir / "traces.jsonl", required=True)
    if len(predictions) != len(traces) or len(predictions) > len(questions):
        raise ValueError("Predictions/traces count mismatch or excess records")
    expected = questions[:len(predictions)]
    corrections = []
    for row, trace, question in zip(predictions, traces, expected):
        qid, db = question["question_id"], question["db_id"]
        if (row.get("question_id") != qid or row.get("db_id") != db or
                trace.get("question_id") != qid or row.get("provider") != provider or
                row.get("model") != model_name):
            raise ValueError("Existing predictions/traces do not match question order, DB or model")
        report = trace.get("report")
        if not isinstance(report, dict):
            raise ValueError("Missing trace report")
        recorded = report.get("model")
        # Historical B0 runner constant was incorrectly copied into Metadata traces.
        if recorded not in (None, model_name):
            if recorded != b0.MODEL:
                raise ValueError(f"Unexpected trace model label for Q{qid}: {recorded}")
            corrections.append({
                "question_id": qid, "recorded_trace_model": recorded,
                "configured_model": model_name,
                "reason": "Historical B0 run_one() default label; original trace retained",
            })
        sql = row.get("predicted_sql")
        if sql is not None and not isinstance(sql, str):
            raise ValueError("Invalid saved prediction SQL")
        if report.get("final_sql") != sql:
            raise ValueError(f"Prediction and trace SQL disagree for Q{qid}")
        if bool(report.get("graph_completed")) is False and sql is not None:
            raise ValueError(f"Prediction Q{qid} has SQL despite incomplete graph")
    allowed = set(previous_dev_ids if split == "test" else ()) | {
        q["question_id"] for q in expected
    }
    _audit_knowledge(experiment_dir, allowed)
    return ([q["question_id"] for q in expected],
            sum(row.get("predicted_sql") is None for row in predictions),
            corrections)
