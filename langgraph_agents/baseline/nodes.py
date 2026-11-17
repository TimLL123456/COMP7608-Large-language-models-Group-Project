"""Three deterministic graph boundaries; only run_b0 invokes the original agent."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scr.baselines import bird_b0 as b0
from scr.baselines.common import redact_credentials
from scr.baselines.sqlite_readonly import ReadOnlySqlite


def prepare_input(state: dict[str, Any]) -> dict[str, Any]:
    question = state.get("agent_input")
    if not isinstance(question, dict):
        raise ValueError("Missing BIRD agent input")
    if type(question.get("question_id")) is not int:
        raise ValueError("Invalid question_id")
    db_id = question.get("db_id")
    if not isinstance(db_id, str) or not db_id or db_id in {".", ".."} or "/" in db_id or "\\" in db_id:
        raise ValueError("Invalid db_id")
    if not isinstance(question.get("question"), str) or not question["question"].strip():
        raise ValueError("Missing question")
    if "SQL" in question:
        raise ValueError("Reference SQL is not permitted in the agent input")
    return {"question_id": question["question_id"], "db_id": db_id, "status": "prepared"}


def make_run_b0_node(
    *, database_path: Callable[[str], Any], model: Any, model_name: str,
    prompt_variant: str, preview_rows: int,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def run_b0(state: dict[str, Any]) -> dict[str, Any]:
        question = state["agent_input"]
        events: list[str] = []
        structured_events: list[dict[str, Any]] = []
        try:
            store = ReadOnlySqlite(database_path(question["db_id"]), max_rows=preview_rows)
            # Preserve legacy call shape when the baseline prompt is selected.
            if prompt_variant == "baseline":
                agent = b0.make_agent(store, model=model)
            else:
                agent = b0.make_agent(store, model=model, prompt_variant=prompt_variant)
            report = b0.run_one(
                question, agent,
                log=lambda message: events.append(redact_credentials(str(message))),
                trace_events=structured_events,
            )
            report["model"] = model_name
        except Exception as exc:
            report = {
                "final_sql": None, "model_calls": 0, "tool_calls": 0,
                "sql_calls": 0, "input_tokens": None, "output_tokens": None,
                "usage_observed": False, "seconds": None, "graph_completed": False,
                "stop_reason": type(exc).__name__,
                "error": redact_credentials(f"{type(exc).__name__}: {exc}"),
                "model": model_name,
            }
        return {
            "candidate_sql": report.get("final_sql"),
            "report": report,
            "events": events,
            "structured_events": structured_events,
            "status": "generated" if report.get("graph_completed") else "incomplete",
            "stop_reason": report.get("stop_reason"),
        }

    return run_b0


def collect_output(state: dict[str, Any]) -> dict[str, Any]:
    report = state["report"]
    sql = report.get("final_sql") if report.get("graph_completed") else None
    return {
        "final_sql": sql,
        "status": "final_sql_ready" if sql else "missing_final_sql",
        "stop_reason": report.get("stop_reason"),
    }
