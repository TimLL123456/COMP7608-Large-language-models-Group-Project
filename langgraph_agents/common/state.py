"""Baseline graph state; never checkpoint credentials, models, or SQLite handles."""
from __future__ import annotations

from typing import Any, TypedDict


class BaselineState(TypedDict, total=False):
    agent_input: dict[str, Any]
    run_id: str
    question_id: int
    db_id: str
    config_snapshot: dict[str, Any]
    candidate_sql: str | None
    final_sql: str | None
    report: dict[str, Any]
    events: list[str]
    structured_events: list[dict[str, Any]]
    status: str
    stop_reason: str | None
