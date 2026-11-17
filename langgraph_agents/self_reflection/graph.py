"""Explicit LangGraph version of the legacy SQL-first SelfReflection coordinator.

The original agent supplies the identical generator, finalizer, reviewer and
budget functions. Only the outer orchestration is expressed as graph nodes.
"""
from __future__ import annotations

import time
from typing import Any, TypedDict

from langgraph.graph import START, END, StateGraph

from langgraph_agents.baseline.nodes import prepare_input as validate_input
from scr.agents.self_reflection_agent import (
    SelfReflectionAgent, _retry_input, _compact_sql, USAGE_KEYS,
)
from scr.baselines import bird_b0 as b0
from scr.baselines.common import redact_credentials


class ReflectionState(TypedDict, total=False):
    question: dict[str, Any]
    started_at: float
    attempts: list[dict]
    structured_events: list[dict]
    totals: dict
    b0_totals: dict
    reviewer_totals: dict
    seen_sql: list[str]
    candidates: list[dict]
    previous_sql: str | None
    feedback: str | None
    final_sql: str | None
    review_status: str
    stop_reason: str
    next_action: str
    current_sql: str | None
    current_report: dict
    report: dict


def _emit(events, kind, **details):
    return [*events, {"seq": len(events) + 1, "kind": kind, **details}]


def _usage():
    return {"model_calls": 0, "tool_calls": 0, "sql_calls": 0,
            **{key: None for key in USAGE_KEYS}}


def build_graph(coordinator: SelfReflectionAgent, store, checkpointer=None):
    def prepare_input(state):
        validate_input({"agent_input": state["question"]})
        return {
            "attempts": [], "structured_events": [],
            "totals": _usage(), "b0_totals": _usage(), "reviewer_totals": _usage(),
            "seen_sql": [], "candidates": [], "previous_sql": None,
            "feedback": None, "final_sql": None, "review_status": "unverified",
            "stop_reason": "max_attempts", "next_action": "generate",
        }

    def generate(state):
        totals, events = dict(state["totals"]), list(state["structured_events"])
        if not coordinator._can_start_b0(totals):
            return {"stop_reason": "global_budget_before_b0", "next_action": "finalize"}
        attempt_no = len(state["attempts"]) + 1
        current = (state["question"] if attempt_no == 1 else
                   _retry_input(state["question"], state["previous_sql"], state["feedback"]))
        b0_events, logs = [], []
        try:
            kwargs = {"prompt_variant": coordinator.prompt_variant,
                      "model_call_limit": b0.MAX_MODEL_CALLS - 1,
                      "tool_call_limit": b0.MAX_TOTAL_TOOL_CALLS - 1,
                      "sql_call_limit": b0.MAX_SQL_EXECUTIONS - 1}
            if coordinator.model is not None:
                kwargs["model"] = coordinator.model
            agent = b0.make_agent(store, **kwargs)
            report = b0.run_one(
                current, agent, log=lambda line: logs.append(
                    redact_credentials(str(line))[:1500]), trace_events=b0_events)
        except Exception as exc:
            report = {
                "final_sql": None, "graph_completed": False,
                "model_calls": 0, "tool_calls": 0, "sql_calls": 0,
                "stop_reason": type(exc).__name__,
                "error": redact_credentials(f"{type(exc).__name__}: {exc}"),
            }
        if not (report.get("graph_completed") and report.get("final_sql")):
            finalized = coordinator._finalize_b0(current, store, report, b0_events)
            if finalized is not None:
                report["final_sql"] = finalized
                report["graph_completed"] = True
                report["stop_reason"] = "b0_forced_sql_finalization"
            events = _emit(events, "sql_finalization", attempt=attempt_no,
                           status=report.get("finalization", {}).get("status"),
                           reason=report.get("finalization", {}).get("reason"),
                           sql=finalized)
        b0_totals = dict(state["b0_totals"])
        coordinator._take_b0_usage(report, totals)
        coordinator._take_b0_usage(report, b0_totals)
        for event in b0_events:
            event = dict(event)
            event.pop("seq", None)
            event["attempt"] = attempt_no
            if event.get("kind") == "model":
                event["model_call"] = (sum(a["b0_report"].get("model_calls") or 0
                                           for a in state["attempts"]) +
                                       (event.get("model_call") or 0))
            events = _emit(events, event.pop("kind"), **event)
        sql = report.get("final_sql") if report.get("graph_completed") else None
        attempts = [*state["attempts"], {
            "attempt": attempt_no, "b0_report": report, "b0_events": b0_events,
            "review": None, "candidate_sql": sql,
        }]
        update = {"totals": totals, "b0_totals": b0_totals,
                  "structured_events": events, "attempts": attempts,
                  "current_sql": sql, "current_report": report}
        if not sql:
            update.update(stop_reason="b0_" + str(report.get("stop_reason") or "no_final_sql"),
                          next_action="finalize")
        elif _compact_sql(sql) in state["seen_sql"]:
            update.update(stop_reason="no_progress_repeated_sql", next_action="finalize")
        else:
            update.update(seen_sql=[*state["seen_sql"], _compact_sql(sql)],
                          next_action="review")
        return update

    def review_sql(state):
        totals = dict(state["totals"])
        sql = state["current_sql"]
        if not coordinator._can_start_review(totals):
            candidates = list(state["candidates"])
            if state["current_report"].get("finalization", {}).get("status") == "executable":
                candidates.append({"sql": sql, "status": "UNCERTAIN",
                                   "attempt": len(state["attempts"])})
            return {
                "candidates": candidates, "stop_reason": "global_budget_before_review",
                "review_status": "unverified", "next_action": "finalize",
            }
        review = coordinator.reviewer.review(
            state["question"], sql, store, previous_feedback=state["feedback"])
        attempts = list(state["attempts"])
        attempts[-1] = {**attempts[-1], "review": review}
        reviewer_totals = dict(state["reviewer_totals"])
        coordinator._take_review_usage(review, totals)
        coordinator._take_review_usage(review, reviewer_totals)
        number = len(attempts)
        rid = f"review-{number}"
        events = _emit(state["structured_events"], "tool_call", attempt=number,
                       name="reflection_review", tool_call_id=rid,
                       args={"candidate_sql": sql[:6000]})
        import json
        events = _emit(events, "tool_result", attempt=number, name="reflection_review",
                       tool_call_id=rid, status=review.get("status"),
                       output=json.dumps({
                           "status": review.get("status"),
                           "issues": review.get("issues", [])[:5],
                           "feedback": review.get("feedback", "")[:3000],
                           "stop_reason": review.get("stop_reason"),
                       }, ensure_ascii=False)[:6000],
                       execution_ms=review.get("latency_ms"))
        candidates = list(state["candidates"])
        status = review.get("status", "ERROR")
        if review.get("candidate_safe"):
            candidates.append({"sql": sql, "status": status, "attempt": number})
        return {"attempts": attempts, "totals": totals, "reviewer_totals": reviewer_totals,
                "structured_events": events, "candidates": candidates,
                "review_status": status, "next_action": "route"}

    def route(state):
        review = state["attempts"][-1]["review"]
        status = state["review_status"]
        if status == "PASS":
            return {"final_sql": state["current_sql"],
                    "stop_reason": "final_sql_ready", "next_action": "finalize"}
        if status == "FAIL":
            if len(state["attempts"]) >= coordinator.max_attempts:
                reason = ("unsafe_final_sql" if review.get("stop_reason") == "unsafe_final_sql"
                          else "max_attempts")
                return {"stop_reason": reason, "next_action": "finalize"}
            feedback = review.get("feedback") or ""
            if not feedback.strip():
                return {"stop_reason": "missing_review_feedback",
                        "next_action": "finalize"}
            return {
                "previous_sql": state["current_sql"], "feedback": feedback,
                "next_action": "retry",
            }
        reason = review.get("stop_reason")
        reasons = {"review_model_budget_exhausted", "review_tool_budget_exhausted",
                   "review_response_retry_exhausted"}
        return {"stop_reason": (reason if status == "UNCERTAIN" and reason in reasons else
                                "review_uncertain" if status == "UNCERTAIN" else "review_error"),
                "next_action": "finalize"}

    def finalize(state):
        sql, status = state.get("final_sql"), state["review_status"]
        if sql is None and state["candidates"]:
            order = {"PASS": 0, "UNCERTAIN": 1, "FAIL": 2, "ERROR": 3}
            best = min(state["candidates"],
                       key=lambda c: (order.get(c["status"], 4), -c["attempt"]))
            sql, status = best["sql"], best["status"]
        output_status = ("missing" if sql is None else
                         "verified" if status == "PASS" else
                         "generated_known_issues" if status == "FAIL" else
                         "generated_unverified")
        reason = state["stop_reason"]
        if sql is None and reason == "max_attempts" and not state["attempts"]:
            reason = "not_started"
        events = _emit(state["structured_events"], "final_validation",
                       status=output_status, sql=sql, reason=reason)
        totals = state["totals"]
        report = {
            "question_id": state["question"]["question_id"],
            "db_id": state["question"]["db_id"],
            "final_sql": sql, "graph_completed": sql is not None,
            "output_status": output_status, "review_status": status,
            "stop_reason": reason,
            "finalization_triggered": any(
                bool(a["b0_report"].get("finalization", {}).get("triggered"))
                or bool((a.get("review") or {}).get("finalization_triggered"))
                for a in state["attempts"]),
            "model_calls": totals["model_calls"],
            "tool_calls": totals["tool_calls"],
            "sql_calls": totals["sql_calls"],
            **{key: totals[key] for key in USAGE_KEYS},
            "seconds": round(time.perf_counter() - state["started_at"], 3),
            "attempt_count": len(state["attempts"]),
        }
        return {"report": report, "structured_events": events, "final_sql": sql,
                "review_status": status, "stop_reason": reason}

    graph = StateGraph(ReflectionState)
    graph.add_node("prepare_input", prepare_input)
    graph.add_node("generate_sql", generate)
    graph.add_node("review_sql", review_sql)
    graph.add_node("route_decision", route)
    graph.add_node("finalize_sql", finalize)
    graph.add_edge(START, "prepare_input")
    graph.add_edge("prepare_input", "generate_sql")
    graph.add_conditional_edges(
        "generate_sql", lambda state: state["next_action"],
        {"review": "review_sql", "finalize": "finalize_sql"})
    graph.add_conditional_edges(
        "review_sql", lambda state: state["next_action"],
        {"route": "route_decision", "finalize": "finalize_sql"})
    graph.add_conditional_edges(
        "route_decision", lambda state: state["next_action"],
        {"retry": "generate_sql", "finalize": "finalize_sql"})
    graph.add_edge("finalize_sql", END)
    return graph.compile(checkpointer=checkpointer)


class LangGraphSelfReflectionAgent(SelfReflectionAgent):
    """Drop-in replacement; node completion metadata is extra, not inferred."""

    def run(self, question: dict, store) -> dict:
        graph = build_graph(self, store)
        from langgraph_agents.role_specialized.runner import run_question
        state, graph_events = run_question(graph, question)
        return {
            "report": state["report"], "attempts": state["attempts"],
            "structured_events": state["structured_events"],
            "b0_usage": state["b0_totals"], "reviewer_usage": state["reviewer_totals"],
            "final_sql": state["final_sql"], "review_status": state["review_status"],
            "stop_reason": state["stop_reason"], "graph_events": graph_events,
        }
