"""RubricSelfReflection's exact stages as explicit LangGraph transitions.

The original B0 generator, rubric extractor/reviewer, and final SQL refiner
are invoked unchanged; the new graph owns the orchestration and evidence
selection policy, with independent result directories.
"""
from __future__ import annotations

import json
import time
from typing import Any, TypedDict

from langgraph.graph import START, END, StateGraph

from langgraph_agents.baseline.nodes import prepare_input as validate_input
from langgraph_agents.role_specialized.runner import run_question
from scr.agents.rubric_self_reflection import coordinator as legacy
from scr.agents.rubric_self_reflection.reviewer import _usage, add_usage
from scr.baselines import bird_b0 as b0


class RubricState(TypedDict, total=False):
    question: dict[str, Any]
    started_at: float
    totals: dict
    b0_usage: dict
    reviewer_usage: dict
    refinement_usage: dict
    attempts: list[dict]
    candidates: list[dict]
    structured_events: list[dict]
    extracted: dict
    seen_sql: list[str]
    previous_sql: str
    feedback: str
    current_sql: str | None
    stop_reason: str
    next_action: str
    refinement: dict
    final_sql: str | None
    review_status: str
    report: dict


def _emit(events, kind, **details):
    return [*events, {"seq": len(events) + 1, "kind": kind, **details}]


def build_graph(coordinator: legacy.RubricSelfReflectionAgent, store, checkpointer=None):
    def prepare_input(state):
        validate_input({"agent_input": state["question"]})
        return {"totals": _usage(), "b0_usage": _usage(),
                "reviewer_usage": _usage(), "refinement_usage": _usage(),
                "attempts": [], "candidates": [], "structured_events": [],
                "seen_sql": [], "previous_sql": "", "feedback": "",
                "stop_reason": "not_started", "next_action": "generate"}

    def extract_requirements(state):
        totals, reviewer_usage = dict(state["totals"]), dict(state["reviewer_usage"])
        extracted = {"status": "ERROR", "requirements": [],
                     "error": "not_started", **_usage()}
        if coordinator._available(totals, model=b0.MAX_MODEL_CALLS + 2,
                                  tool=b0.MAX_TOTAL_TOOL_CALLS,
                                  sql=b0.MAX_SQL_EXECUTIONS):
            extracted = coordinator.reviewer.extract(state["question"], max_calls=2)
            add_usage(totals, extracted)
            add_usage(reviewer_usage, extracted)
        events = _emit(state["structured_events"], "requirements_extracted",
                       status=extracted["status"], requirements=extracted["requirements"],
                       error=extracted.get("error"))
        return {"extracted": extracted, "totals": totals,
                "reviewer_usage": reviewer_usage, "structured_events": events}

    def generate_sql(state):
        totals = dict(state["totals"])
        if not coordinator._available(totals, model=b0.MAX_MODEL_CALLS,
                                      tool=b0.MAX_TOTAL_TOOL_CALLS,
                                      sql=b0.MAX_SQL_EXECUTIONS):
            return {"stop_reason": "global_budget_before_b0", "next_action": "refine"}
        number = len(state["attempts"]) + 1
        request = (state["question"] if number == 1 else
                   coordinator._retry_question(
                       state["question"], state["previous_sql"], state["feedback"]))
        generated = coordinator._b0_generate(request, store)
        b0_usage = dict(state["b0_usage"])
        add_usage(totals, generated["report"])
        add_usage(b0_usage, generated["report"])
        sql = generated["candidate_sql"]
        attempt = {"attempt": number, "candidate_sql": sql,
                   "b0_report": generated["report"], "b0_events": generated["events"],
                   "review": None}
        events = _emit(state["structured_events"], "b0_attempt", attempt=number,
                       candidate_sql=sql,
                       b0_status=generated["report"].get("stop_reason"),
                       finalization=generated["completion"])
        update = {"totals": totals, "b0_usage": b0_usage,
                  "attempts": [*state["attempts"], attempt],
                  "current_sql": sql, "structured_events": events}
        if not sql:
            update.update(stop_reason="b0_no_executable_sql", next_action="refine")
        elif sql.strip() in state["seen_sql"]:
            update.update(stop_reason="no_progress_repeated_sql", next_action="refine")
        else:
            update.update(seen_sql=[*state["seen_sql"], sql.strip()],
                          next_action="review")
        return update

    def review_sql(state):
        sql, number = state["current_sql"], len(state["attempts"])
        extracted = state["extracted"]
        totals = dict(state["totals"])
        candidates = list(state["candidates"])
        if extracted["status"] != "PASS":
            if coordinator._available(totals, tool=1, sql=1):
                totals["tool_calls"] += 1
                totals["sql_calls"] += 1
                check = store.execute(sql)
                if "error" not in check:
                    candidates.append({"sql": sql, "status": "ERROR", "review": {},
                                       "attempt": number})
            return {"totals": totals, "candidates": candidates,
                    "stop_reason": "requirements_extraction_error",
                    "next_action": "refine"}
        max_model = min(coordinator.reviewer.max_model_calls,
                        coordinator.limits["model_calls"] - totals["model_calls"] - 1)
        max_tool = min(coordinator.reviewer.max_inspections + 1,
                       coordinator.limits["tool_calls"] - totals["tool_calls"] - 1)
        max_sql = coordinator.limits["sql_calls"] - totals["sql_calls"] - 1
        if min(max_model, max_tool, max_sql) < 1:
            if coordinator._available(totals, tool=1, sql=1):
                totals["tool_calls"] += 1
                totals["sql_calls"] += 1
                check = store.execute(sql)
                if "error" not in check:
                    candidates.append({"sql": sql, "status": "UNCERTAIN",
                                       "review": {}, "attempt": number})
            return {"totals": totals, "candidates": candidates,
                    "stop_reason": "global_budget_before_review",
                    "next_action": "refine"}
        review = coordinator.reviewer.review(
            state["question"], sql, store, extracted["requirements"],
            previous_feedback=state["feedback"], max_model_calls=max_model,
            max_inspections=min(coordinator.reviewer.max_inspections,
                                max_tool - 1, max_sql - 1))
        attempts = list(state["attempts"])
        attempts[-1] = {**attempts[-1], "review": review}
        reviewer_usage = dict(state["reviewer_usage"])
        add_usage(totals, review)
        add_usage(reviewer_usage, review)
        events = _emit(state["structured_events"], "rubric_review", attempt=number,
                       status=review["status"],
                       requirements=review.get("requirements", []),
                       coverage=review.get("coverage", {}),
                       issues=review.get("issues", []),
                       stop_reason=review.get("stop_reason"))
        if review.get("candidate_safe"):
            candidates.append({"sql": sql, "status": review["status"],
                               "review": review, "attempt": number})
        return {"attempts": attempts, "totals": totals,
                "reviewer_usage": reviewer_usage, "candidates": candidates,
                "structured_events": events, "next_action": "route"}

    def route_decision(state):
        review = state["attempts"][-1]["review"]
        number = len(state["attempts"])
        if review["status"] == "PASS":
            return {"stop_reason": "rubric_pass", "next_action": "refine"}
        if review["status"] == "FAIL" and review.get("feedback") and number < coordinator.max_attempts:
            return {"previous_sql": state["current_sql"], "feedback": review["feedback"],
                    "stop_reason": "retry_feedback", "next_action": "retry"}
        return {"stop_reason": review.get("stop_reason") or "review_not_pass",
                "next_action": "refine"}

    def refine_sql(state):
        candidates = state["candidates"]
        rank = {"PASS": 0, "UNCERTAIN": 1, "FAIL": 2, "ERROR": 3}
        best = min(candidates, key=lambda x: (rank[x["status"]], -x["attempt"])) if candidates else None
        selected = best["sql"] if best else None
        selected_review = best["review"] if best else {}
        final_status = best["status"] if best else "unverified"
        refinement = {"triggered": False, "status": "not_needed", **_usage()}
        material_unmet = bool(best and any(
            r.get("material") and r.get("status") in ("FAIL", "UNCERTAIN")
            for r in selected_review.get("requirements", [])))
        material_unmet |= bool(best and selected_review.get("coverage", {}).get("status")
                              in ("GAP", "UNCERTAIN"))
        refinement_input = selected
        if not best:
            failed = next((a for a in reversed(state["attempts"])
                           if a.get("candidate_sql") and
                           (a.get("review") or {}).get("status") == "FAIL"), None)
            if failed:
                material_unmet = True
                refinement_input = failed["candidate_sql"]
                selected_review = failed["review"]
        totals = dict(state["totals"])
        refinement_usage = dict(state["refinement_usage"])
        events = list(state["structured_events"])
        stop_reason = state["stop_reason"]
        if material_unmet and final_status != "PASS" and refinement_input:
            observations = []
            for attempt in state["attempts"]:
                for event in attempt["b0_events"]:
                    if event.get("kind") == "tool_result":
                        observations.append({"kind": "b0_tool", "name": event.get("name"),
                                             "content": str(event.get("output", ""))[:1000]})
                for event in (attempt.get("review") or {}).get("inspection_log", []):
                    observations.append({
                        "kind": "review_inspection",
                        "content": json.dumps(event, ensure_ascii=False, default=str)[:1200],
                    })
            refinement = legacy.refine_sql(
                coordinator.finalizer_model, state["question"],
                refinement_input, selected_review, observations, store,
                allow_model=coordinator._available(
                    totals, model=1, reserve_final=False),
                allow_execution=coordinator._available(
                    totals, tool=1, sql=1, reserve_final=False))
            add_usage(totals, refinement)
            add_usage(refinement_usage, refinement)
            events = _emit(events, "sql_refinement", status=refinement["status"],
                           sql=refinement.get("sql"), error=refinement.get("error"))
            if refinement["status"] == "executable":
                selected = refinement["sql"]
                final_status = "UNCERTAIN"
                stop_reason = "refined_sql_executable_unverified"
        return {
            "final_sql": selected, "review_status": final_status,
            "refinement": refinement, "totals": totals,
            "refinement_usage": refinement_usage,
            "structured_events": events, "stop_reason": stop_reason,
        }

    def finalize_sql(state):
        selected, status = state["final_sql"], state["review_status"]
        output_status = ("missing" if selected is None else
                         "verified" if status == "PASS" else
                         "generated_known_issues" if status == "FAIL" else
                         "generated_unverified")
        refinement = state["refinement"]
        report = {
            "question_id": state["question"]["question_id"],
            "db_id": state["question"]["db_id"], "final_sql": selected,
            "graph_completed": selected is not None,
            "review_status": status, "output_status": output_status,
            "stop_reason": state["stop_reason"],
            "attempt_count": len(state["attempts"]),
            "refinement_status": refinement["status"],
            "finalization_triggered": bool(
                refinement["triggered"] or any(
                    a["b0_report"]["finalization"]["triggered"]
                    for a in state["attempts"])),
            "seconds": round(time.monotonic() - state["started_at"], 3),
            **state["totals"],
        }
        return {"report": report,
                "structured_events": _emit(
                    state["structured_events"], "final_validation",
                    status=output_status, sql=selected, reason=state["stop_reason"])}

    graph = StateGraph(RubricState)
    graph.add_node("prepare_input", prepare_input)
    graph.add_node("extract_requirements", extract_requirements)
    graph.add_node("generate_sql", generate_sql)
    graph.add_node("review_sql", review_sql)
    graph.add_node("route_decision", route_decision)
    graph.add_node("refine_sql", refine_sql)
    graph.add_node("finalize_sql", finalize_sql)
    graph.add_edge(START, "prepare_input")
    graph.add_edge("prepare_input", "extract_requirements")
    graph.add_edge("extract_requirements", "generate_sql")
    graph.add_conditional_edges(
        "generate_sql", lambda state: state["next_action"],
        {"review": "review_sql", "refine": "refine_sql"})
    graph.add_conditional_edges(
        "review_sql", lambda state: state["next_action"],
        {"route": "route_decision", "refine": "refine_sql"})
    graph.add_conditional_edges(
        "route_decision", lambda state: state["next_action"],
        {"retry": "generate_sql", "refine": "refine_sql"})
    graph.add_edge("refine_sql", "finalize_sql")
    graph.add_edge("finalize_sql", END)
    return graph.compile(checkpointer=checkpointer)


class LangGraphRubricSelfReflectionAgent(legacy.RubricSelfReflectionAgent):
    def run(self, question: dict, store) -> dict:
        graph = build_graph(self, store)
        state, graph_events = run_question(graph, question)
        return {
            "report": state["report"], "attempts": state["attempts"],
            "extraction": state["extracted"],
            "structured_events": state["structured_events"],
            "final_sql": state["final_sql"],
            "review_status": state["review_status"],
            "stop_reason": state["stop_reason"],
            "refinement": state["refinement"], "b0_usage": state["b0_usage"],
            "reviewer_usage": state["reviewer_usage"],
            "refinement_usage": state["refinement_usage"],
            "graph_events": graph_events,
        }
