"""Serializable per-question graph state. Models and SQLite handles stay in closures."""
from __future__ import annotations

from typing import Any, TypedDict


class RoleState(TypedDict, total=False):
    question: dict[str, Any]
    started_at: float
    attempt_number: int
    attempts: list[dict[str, Any]]
    generated: dict[str, Any]
    requirements: list[dict[str, Any]] | None
    extraction: dict[str, Any]
    review: dict[str, Any] | None
    review_reports: list[dict[str, Any]]
    candidates: list[dict[str, Any]]
    seen_sql: list[str]
    totals: dict[str, Any]
    generator_usage: dict[str, Any]
    reviewer_usage: dict[str, Any]
    structured_events: list[dict[str, Any]]
    previous_sql: str
    feedback: str
    next_action: str
    stop_reason: str
    report: dict[str, Any]
    final_sql: str | None
    review_status: str
