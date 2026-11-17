"""Graph nodes preserving the legacy RoleSpecialized coordinator's decisions."""
from __future__ import annotations

import time
from typing import Any

from langgraph_agents.baseline.nodes import prepare_input as validate_bird_input
from scr.agents.rubric_self_reflection.reviewer import _usage, add_usage
from scr.baselines import bird_b0 as b0
from scr.baselines.common import redact_credentials


def _emit(events: list[dict], kind: str, **fields) -> list[dict]:
    return [*events, {"seq": len(events) + 1, "kind": kind, **fields}]


class RoleNodes:
    def __init__(self, coordinator, store):
        self.coordinator = coordinator
        self.store = store

    def prepare_input(self, state: dict[str, Any]) -> dict:
        # Shared B0 input boundary excludes gold SQL and unsafe db identifiers.
        validate_bird_input({"agent_input": state["question"]})
        return {
            "attempt_number": 0,
            "attempts": [], "candidates": [], "seen_sql": [],
            "review_reports": [], "structured_events": [],
            "totals": _usage(), "generator_usage": _usage(), "reviewer_usage": _usage(),
            "requirements": None, "review": None,
            "extraction": {"status": "not_started", "requirements": [], **_usage()},
            "feedback": "", "previous_sql": "",
            "stop_reason": "not_started", "next_action": "review",
        }

    def generate_sql(self, state: dict[str, Any]) -> dict:
        totals = dict(state["totals"])
        if not self.coordinator._available(
            totals, model=b0.MAX_MODEL_CALLS, tool=b0.MAX_TOTAL_TOOL_CALLS,
            sql=b0.MAX_SQL_EXECUTIONS, reserve_final=False
        ):
            return {"stop_reason": "global_budget_before_generator",
                    "next_action": "finalize"}

        attempt_number = state["attempt_number"] + 1
        question = state["question"] if attempt_number == 1 else (
            self.coordinator._retry_question(
                state["question"], state["previous_sql"], state["feedback"]
            )
        )
        generated = self.coordinator._b0_generate(question, self.store)
        add_usage(totals, generated["report"])
        generator_usage = dict(state["generator_usage"])
        add_usage(generator_usage, generated["report"])
        sql = generated["candidate_sql"]
        attempt = {
            "attempt": attempt_number, "candidate_sql": sql,
            "b0_report": generated["report"], "b0_events": generated["events"],
            "review": None, "review_report": None,
        }
        events = _emit(
            state["structured_events"], "generator_attempt",
            attempt=attempt_number, candidate_sql=sql,
            completion=generated["completion"],
        )
        update = {
            "totals": totals, "generator_usage": generator_usage,
            "attempt_number": attempt_number,
            "attempts": [*state["attempts"], attempt],
            "generated": generated,
            "structured_events": events,
        }
        if not sql:
            update.update(stop_reason="generator_no_sql", next_action="finalize")
        elif sql.strip() in state["seen_sql"]:
            update.update(stop_reason="no_progress_repeated_sql", next_action="finalize")
        else:
            update.update(seen_sql=[*state["seen_sql"], sql.strip()],
                          next_action="review")
        return update

    def _retain_fallback(
        self, state: dict[str, Any], sql: str, status: str
    ) -> dict[str, Any]:
        """Only preserve an unreviewed SQL if read-only execution succeeds."""
        totals = dict(state["totals"])
        candidates = list(state["candidates"])
        events = list(state["structured_events"])
        if self.coordinator._available(totals, tool=1, sql=1, reserve_final=False):
            totals["tool_calls"] += 1
            totals["sql_calls"] += 1
            try:
                observation = self.store.execute(sql)
                if isinstance(observation, dict) and "error" not in observation:
                    candidates.append({
                        "sql": sql, "status": status, "attempt": state["attempt_number"],
                    })
            except Exception as exc:
                events = _emit(
                    events, "fallback_check_error",
                    error=redact_credentials(str(exc))[:300],
                )
        return {"totals": totals, "candidates": candidates,
                "structured_events": events}

    def review_sql(self, state: dict[str, Any]) -> dict:
        question = state["question"]
        generated = state["generated"]
        sql = generated["candidate_sql"]
        totals = dict(state["totals"])
        reviewer_usage = dict(state["reviewer_usage"])
        events = list(state["structured_events"])
        requirements = state["requirements"]
        extraction = state["extraction"]

        if requirements is None:
            remaining = self.coordinator.limits["model_calls"] - totals["model_calls"]
            if remaining > 0:
                extraction = self.coordinator.reviewer.extract(
                    question, max_calls=min(2, remaining)
                )
                add_usage(totals, extraction)
                add_usage(reviewer_usage, extraction)
            else:
                extraction = {"status": "ERROR", "requirements": [],
                              "error": "model_budget_exhausted", **_usage()}
            events = _emit(
                events, "requirements_extracted",
                status=extraction["status"],
                requirements=extraction.get("requirements", []),
                error=extraction.get("error"),
            )
            if extraction["status"] != "PASS":
                fallback = self._retain_fallback(
                    {**state, "totals": totals, "structured_events": events},
                    sql, "ERROR",
                )
                return {
                    **fallback, "extraction": extraction, "reviewer_usage": reviewer_usage,
                    "stop_reason": "requirements_extraction_error", "review": None,
                }
            requirements = extraction["requirements"]

        remaining_model = self.coordinator.limits["model_calls"] - totals["model_calls"]
        remaining_tool = self.coordinator.limits["tool_calls"] - totals["tool_calls"]
        remaining_sql = self.coordinator.limits["sql_calls"] - totals["sql_calls"]
        if min(remaining_model, remaining_tool, remaining_sql) < 1:
            fallback = self._retain_fallback(
                {**state, "totals": totals, "structured_events": events},
                sql, "UNCERTAIN",
            )
            return {
                **fallback, "requirements": requirements, "extraction": extraction,
                "reviewer_usage": reviewer_usage,
                "stop_reason": "global_budget_before_review", "review": None,
            }

        review = self.coordinator.reviewer.review(
            self.coordinator._investigation_context(question, generated["events"]),
            sql, self.store, requirements, previous_feedback=state["feedback"],
            max_model_calls=min(self.coordinator.reviewer.max_model_calls, remaining_model),
            max_inspections=min(
                self.coordinator.reviewer.max_inspections,
                remaining_tool - 1, remaining_sql - 1,
            ),
        )
        add_usage(totals, review)
        add_usage(reviewer_usage, review)
        report = self.coordinator._review_report(state["attempt_number"], review)
        attempts = list(state["attempts"])
        attempts[-1] = {**attempts[-1], "review": review, "review_report": report}
        events = _emit(
            events, "review_report", attempt=state["attempt_number"],
            status=review["status"], overall_decision=report["overall_decision"],
            findings=report["criteria_findings"], feedback=report["regeneration_feedback"],
        )
        candidates = list(state["candidates"])
        if review.get("candidate_safe"):
            candidates.append({
                "sql": sql, "status": review["status"],
                "attempt": state["attempt_number"],
            })
        return {
            "review": review, "requirements": requirements, "extraction": extraction,
            "totals": totals, "reviewer_usage": reviewer_usage,
            "attempts": attempts, "candidates": candidates,
            "review_reports": [*state["review_reports"], report],
            "structured_events": events,
        }

    def route_decision(self, state: dict[str, Any]) -> dict:
        review = state.get("review")
        if review is None:
            # Extraction failure or budget gate has already provided the stop reason.
            return {"next_action": "finalize"}
        if review["status"] == "PASS" and review.get("candidate_safe"):
            return {"stop_reason": "reviewer_pass", "next_action": "finalize"}
        next_feedback = self.coordinator._actionable_feedback(review)
        if next_feedback and state["attempt_number"] < self.coordinator.max_attempts:
            return {
                "previous_sql": state["generated"]["candidate_sql"],
                "feedback": next_feedback,
                "stop_reason": "retry_from_review_report",
                "next_action": "retry",
            }
        return {
            "stop_reason": review.get("stop_reason") or "review_not_pass",
            "next_action": "finalize",
        }

    def finalize_sql(self, state: dict[str, Any]) -> dict:
        rank = {"PASS": 0, "UNCERTAIN": 1, "FAIL": 2, "ERROR": 3}
        candidates = state["candidates"]
        best = min(
            candidates, key=lambda candidate: (
                rank.get(candidate["status"], 4), -candidate["attempt"]
            ),
        ) if candidates else None
        sql = best["sql"] if best else None
        final_status = best["status"] if best else "ERROR"
        output_status = (
            "missing" if sql is None else
            "verified" if final_status == "PASS" else
            "generated_known_issues" if final_status == "FAIL" else
            "generated_unverified"
        )
        report = {
            "question_id": state["question"]["question_id"],
            "db_id": state["question"]["db_id"],
            "final_sql": sql, "graph_completed": sql is not None,
            "review_status": final_status, "output_status": output_status,
            "stop_reason": state["stop_reason"],
            "attempt_count": len(state["attempts"]),
            "review_report_count": len(state["review_reports"]),
            "seconds": round(time.monotonic() - state["started_at"], 3),
            **state["totals"],
        }
        return {
            "report": report, "final_sql": sql, "review_status": final_status,
            "structured_events": _emit(
                state["structured_events"], "final_sql",
                status=output_status, sql=sql,
                selected_attempt=best["attempt"] if best else None,
            ),
        }
