"""BIRD original SQLite Mini-Dev execution accuracy (EX) evaluator.

Official EX compares sets of complete result tuples; SQL text, result row order
and duplicate result rows do not determine correctness. Reference SQL is used
only by this offline scorer and is never included in prediction exports.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import math
import sqlite3
import time
from typing import Any

from scr.datasets.bird import BirdDataset, BirdEvaluationReferences, read_only_connection

VARIANTS = {"B0", "B1", "B2", "B3", "B4"}
USAGE_FIELDS = ("provider", "model", "tool_calls", "input_tokens", "output_tokens", "latency_ms", "cost_usd", "model_calls", "sql_calls", "sql_success_calls", "sql_error_calls", "sql_truncated_calls", "agent_sql_execution_ms")
DENIED_ACTIONS = {
    getattr(sqlite3, name)
    for name in (
        "SQLITE_ATTACH", "SQLITE_DETACH", "SQLITE_PRAGMA", "SQLITE_INSERT",
        "SQLITE_UPDATE", "SQLITE_DELETE", "SQLITE_TRANSACTION", "SQLITE_SAVEPOINT",
        "SQLITE_CREATE_TABLE", "SQLITE_CREATE_INDEX", "SQLITE_CREATE_VIEW",
        "SQLITE_CREATE_TRIGGER", "SQLITE_CREATE_VTABLE", "SQLITE_DROP_TABLE",
        "SQLITE_DROP_INDEX", "SQLITE_DROP_VIEW", "SQLITE_DROP_TRIGGER",
        "SQLITE_DROP_VTABLE", "SQLITE_ALTER_TABLE", "SQLITE_REINDEX",
        "SQLITE_ANALYZE",
    )
    if hasattr(sqlite3, name)
}


def load_predictions(path: Path) -> list[dict[str, Any]]:
    """Read one explicitly keyed prediction object per JSONL line."""
    predictions = []
    with Path(path).open(encoding="utf-8-sig") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {number}: {exc.msg}") from exc
            if not isinstance(entry, dict):
                raise ValueError(f"Prediction line {number} must be an object")
            predictions.append(entry)
    return predictions


def validate_predictions(predictions: list[dict[str, Any]], questions: list[dict]) -> dict[int, dict]:
    """Reject extra/duplicate/wrong-DB records; missing IDs are scored as zero."""
    expected = {row["question_id"]: row for row in questions}
    seen: dict[int, dict] = {}
    for index, item in enumerate(predictions, 1):
        if not isinstance(item, dict):
            raise ValueError(f"Prediction {index} must be an object")
        qid = item.get("question_id")
        if type(qid) is not int or qid not in expected:
            raise ValueError(f"Unknown or out-of-split question_id: {qid!r}")
        if qid in seen:
            raise ValueError(f"Duplicate question_id: {qid}")
        if item.get("db_id") != expected[qid]["db_id"]:
            raise ValueError(f"Incorrect db_id for question_id {qid}")
        sql = item.get("predicted_sql")
        if sql is not None and not isinstance(sql, str):
            raise ValueError(f"predicted_sql for question_id {qid} must be a string or null")
        for field in USAGE_FIELDS:
            value = item.get(field)
            if value is None:
                continue
            if field in ("model", "provider"):
                if not isinstance(value, str):
                    raise ValueError(f"{field} for question_id {qid} must be a string")
            elif type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{field} for question_id {qid} must be a nonnegative finite number")
        seen[qid] = item
    return seen


def execute_bounded_sql(db_path: Path, sql: str, *, timeout_seconds: float = 30.0,
                        max_result_rows: int = 100_000) -> tuple[str, list[tuple] | None, float]:
    """Read-only SQLite query with VM-level time and fetched-row limits.

    A blocked/over-limit query is an explicit failure, not a silently truncated
    result eligible for a correct EX score. Does not enable SQLite extensions.
    """
    if not isinstance(sql, str) or not sql.strip():
        return "missing_sql", None, 0.0
    if timeout_seconds <= 0 or max_result_rows < 1:
        raise ValueError("timeout_seconds and max_result_rows must be positive")
    started = time.monotonic()
    deadline = started + timeout_seconds
    interrupted = False
    try:
        with read_only_connection(db_path) as conn:
            def authorize(action, arg1, arg2, database, source):
                if action in DENIED_ACTIONS:
                    return sqlite3.SQLITE_DENY
                if action == sqlite3.SQLITE_FUNCTION and arg2 == "load_extension":
                    return sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK

            def progress():
                nonlocal interrupted
                if time.monotonic() >= deadline:
                    interrupted = True
                    return 1
                return 0

            conn.set_authorizer(authorize)
            conn.set_progress_handler(progress, 1000)
            cursor = conn.execute(sql)  # SQLite rejects multiple statements.
            if cursor.description is None:
                return "unsafe_sql", None, (time.monotonic() - started) * 1000
            rows = cursor.fetchmany(max_result_rows + 1)
            duration = (time.monotonic() - started) * 1000
            if interrupted or time.monotonic() >= deadline:
                return "timeout", None, duration
            if len(rows) > max_result_rows:
                return "result_limit", None, duration
            return "ok", rows, duration
    except sqlite3.Error as exc:
        duration = (time.monotonic() - started) * 1000
        if interrupted or "interrupted" in str(exc).lower():
            return "timeout", None, duration
        if "not authorized" in str(exc).lower() or "readonly" in str(exc).lower() or "read-only" in str(exc).lower():
            return "unsafe_sql", None, duration
        return "sql_error", None, duration


def evaluate_predictions(dataset: BirdDataset, references: BirdEvaluationReferences,
                         questions: list[dict], predictions: list[dict], *, variant: str,
                         timeout_seconds: float = 30.0,
                         max_result_rows: int = 100_000) -> tuple[list[dict], dict]:
    """Score a declared question set. Missing predictions stay in denominator."""
    if variant not in VARIANTS:
        raise ValueError(f"Unknown variant {variant!r}; choose B0 to B4")
    if not questions:
        raise ValueError("Question set must not be empty")
    if timeout_seconds <= 0 or max_result_rows < 1:
        raise ValueError("timeout_seconds and max_result_rows must be positive")
    matched = validate_predictions(predictions, questions)
    gold_results = {}
    for q in questions:
        qid = q["question_id"]
        status, rows, gold_elapsed = execute_bounded_sql(dataset.get_database_path(q["db_id"]),
            references.get_reference_sql(qid), timeout_seconds=timeout_seconds,
            max_result_rows=max_result_rows)
        if status != "ok":
            raise RuntimeError(f"Reference SQL failed for question_id {qid}: {status}; evaluation invalid")
        gold_results[qid] = (rows, round(gold_elapsed, 3))
    records = []
    for question in questions:
        qid, dbid = question["question_id"], question["db_id"]
        prediction = matched.get(qid, {})
        sql = prediction.get("predicted_sql")
        record = {
            "question_id": qid, "db_id": dbid, "difficulty": question["difficulty"],
            "variant": variant, "predicted_sql": sql, "ex": 0,
            "status": "missing_prediction" if qid not in matched else "missing_sql",
            "sql_execution_ms": None, "gold_sql_execution_ms": gold_results[qid][1],
        }
        record.update({key: prediction.get(key) for key in USAGE_FIELDS})
        if isinstance(sql, str) and sql.strip():
            database = dataset.get_database_path(dbid)
            predicted_status, predicted_rows, elapsed = execute_bounded_sql(
                database, sql, timeout_seconds=timeout_seconds, max_result_rows=max_result_rows)
            record["sql_execution_ms"] = round(elapsed, 3)
            record["status"] = predicted_status
            if predicted_status == "ok":
                record["ex"] = int(set(predicted_rows) == set(gold_results[qid][0]))
                record["status"] = "correct" if record["ex"] else "incorrect_result"
        records.append(record)
    overall = sum(item["ex"] for item in records)
    counts = Counter(item["status"] for item in records)
    difficulties = {}
    for difficulty in sorted(set(row["difficulty"] for row in records)):
        subset = [row for row in records if row["difficulty"] == difficulty]
        correct = sum(row["ex"] for row in subset)
        difficulties[difficulty] = {"correct": correct, "total": len(subset), "ex": correct / len(subset)}
    summary = {
        "variant": variant, "correct": overall, "total": len(records),
        "ex": overall / len(records), "predictions_supplied": len(matched),
        "missing_predictions": len(records) - len(matched),
        "status_counts": dict(sorted(counts.items())), "by_difficulty": difficulties,
    }
    for field in ("tool_calls", "input_tokens", "output_tokens", "latency_ms", "cost_usd"):
        observed = [row[field] for row in records if row.get(field) is not None]
        summary[f"mean_{field}"] = sum(observed) / len(observed) if observed else None
        summary[f"observed_{field}"] = len(observed)
    from statistics import median
    performance = {}
    for field in ("tool_calls", "model_calls", "sql_calls", "sql_success_calls",
                  "sql_error_calls", "sql_truncated_calls", "input_tokens",
                  "output_tokens", "latency_ms", "sql_execution_ms",
                  "gold_sql_execution_ms", "agent_sql_execution_ms"):
        vals = sorted(row[field] for row in records if type(row.get(field)) in (int, float))
        performance[field] = {"observed": len(vals),
            "total": sum(vals) if vals else None,
            "mean": sum(vals)/len(vals) if vals else None,
            "p50": median(vals) if vals else None,
            "p95": vals[max(0, math.ceil(.95*len(vals))-1)] if vals else None}
    attempts = performance["sql_calls"]["total"]
    succeeded = performance["sql_success_calls"]["total"]
    performance["sql_tool_success_rate"] = succeeded/attempts if attempts and succeeded is not None else None
    generated = sum(bool(row.get("predicted_sql")) for row in records)
    executed = sum(row["status"] in ("correct", "incorrect_result") for row in records)
    performance["final_sql_generation_rate"] = generated/len(records)
    performance["final_sql_execution_rate"] = executed/generated if generated else None
    summary["performance"] = performance
    return records, summary
