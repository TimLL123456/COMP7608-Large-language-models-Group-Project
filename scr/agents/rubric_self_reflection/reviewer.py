"""Independent rubric-first SQL reviewer; read-only inspections and bounded calls."""
from __future__ import annotations

import json
from pathlib import Path
import time

from scr.baselines import bird_b0 as b0
from .rubric import model_json, parse_requirements, parse_review

ROOT = Path(__file__).resolve().parent
REVIEW_PROMPT = ROOT / "prompts" / "reviewer_v1.txt"
PROMPT_VERSION = "rubric-review-v1"
TOKEN_KEYS = ("input_tokens", "output_tokens", "total_tokens", "cached_input_tokens", "reasoning_tokens")


def _usage() -> dict:
    return {"model_calls": 0, "tool_calls": 0, "sql_calls": 0,
            **{key: None for key in TOKEN_KEYS}}


def add_usage(total: dict, increment: dict) -> None:
    for key in ("model_calls", "tool_calls", "sql_calls", *TOKEN_KEYS):
        val = increment.get(key)
        if val is not None:
            total[key] = (total.get(key) or 0) + val


def _model_call(model, prompt: str, data: dict, usage: dict):
    from langchain_core.messages import SystemMessage, HumanMessage
    usage["model_calls"] += 1  # Count provider failures too.
    reply = model.invoke([SystemMessage(content=prompt), HumanMessage(
        content=json.dumps(data, ensure_ascii=False, default=str))])
    observed = b0._observed_model_metadata(reply)
    for key in TOKEN_KEYS:
        value = observed.get(key)
        if value is not None:
            usage[key] = (usage[key] or 0) + value
    return model_json(reply)


def _inspection(store, req: dict):
    if req["kind"] == "list_tables":
        return store.list_tables()
    if req["kind"] == "inspect_table":
        return store.inspect_table(req["table"][:200])
    return store.execute(req["sql"])


class RubricReviewer:
    def __init__(self, model, *, max_model_calls: int = 40, max_inspections: int = 39):
        if model is None or not 1 <= max_model_calls <= 40 or not 0 <= max_inspections <= 39:
            raise ValueError("Invalid rubric reviewer configuration")
        self.model = model
        self.max_model_calls = max_model_calls
        self.max_inspections = max_inspections
        self.prompt = REVIEW_PROMPT.read_text(encoding="utf-8")

    def extract(self, question: dict, *, max_calls: int = 2) -> dict:
        """Extract a single stable checklist before any candidate SQL is seen."""
        result = {"status": "ERROR", "requirements": [], "error": None,
                  "stop_reason": "extraction_error", **_usage()}
        max_calls = min(max_calls, self.max_model_calls)
        error = None
        for attempt in range(max_calls):
            try:
                raw = _model_call(self.model, self.prompt,
                                  {"stage": "EXTRACTION", "question": question.get("question"),
                                   "evidence": question.get("evidence"),
                                   "repair": error or ""}, result)
                requirements = parse_requirements(raw, question)
                result.update(status="PASS", requirements=requirements, stop_reason="complete", error=None)
                return result
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"[:400]
                result["error"] = error
                # Provider/infrastructure errors should not be retried endlessly.
                if not isinstance(exc, (ValueError, TypeError, json.JSONDecodeError)):
                    break
        return result

    def review(self, question: dict, sql: str, store, requirements: list[dict], *,
               previous_feedback: str = "", max_model_calls: int | None = None,
               max_inspections: int | None = None) -> dict:
        """Evaluate exact submitted candidate against all stable requirement IDs."""
        started = time.monotonic()
        cap = min(self.max_model_calls, max_model_calls if max_model_calls is not None else self.max_model_calls)
        inspections = min(self.max_inspections, max_inspections if max_inspections is not None else self.max_inspections)
        if cap < 0 or inspections < 0:
            raise ValueError("Negative review budget")
        result = {"status": "ERROR", "requirements": [], "coverage": {}, "issues": [],
                  "feedback": "", "inspection_log": [], "execution": None,
                  "candidate_safe": False, "stop_reason": "review_error",
                  "finalization_triggered": False, "latency_ms": None, **_usage()}
        try:
            if not requirements or not isinstance(sql, str) or not sql.strip():
                result["stop_reason"] = "missing_candidate_or_requirements"
                return result
            execution = store.execute(sql)
            result["execution"] = execution
            result["tool_calls"] += 1
            result["sql_calls"] += 1
            if "error" in execution:
                error = str(execution["error"])
                inconclusive = any(s in error.lower() for s in ("timeout", "interrupted", "locked", "busy"))
                result.update(status="UNCERTAIN" if inconclusive else "FAIL",
                              stop_reason="execution_inconclusive" if inconclusive else "sql_execution_error",
                              issues=[] if inconclusive else [{
                                  "requirement_id": "execution_gate",
                                  "description": "Candidate SQL failed exact read-only execution",
                                  "evidence": error[:1000],
                                  "suggested_action": "Check identifiers, syntax and read-only constraints",
                              }],
                              feedback="" if inconclusive else "Fix SQL execution error: " + error[:1000])
                return result
            result["candidate_safe"] = True
            if cap == 0:
                result.update(status="UNCERTAIN", stop_reason="review_model_budget_exhausted")
                return result
            evidence_log = []
            prior_error = ""
            force_final = inspections == 0
            for index in range(cap):
                finalizing = force_final or index + 1 == cap
                if finalizing:
                    result["finalization_triggered"] = True
                context = {
                    "stage": "REVIEW", "question": question.get("question"),
                    "evidence": question.get("evidence"),
                    "requirements": requirements, "candidate_sql": sql,
                    "initial_execution": execution, "inspection_observations": evidence_log[-12:],
                    "previous_feedback": previous_feedback,
                    "review_finalization": finalizing,
                    "remaining_inspections": 0 if finalizing else inspections - len(evidence_log),
                    "repair": prior_error,
                }
                try:
                    raw = _model_call(self.model, self.prompt, context, result)
                    decision = parse_review(raw, requirements, finalizing=finalizing)
                except Exception as exc:
                    prior_error = f"{type(exc).__name__}: {exc}"[:400]
                    result["stop_reason"] = "review_invalid_response"
                    if not isinstance(exc, (ValueError, TypeError, json.JSONDecodeError)):
                        result["stop_reason"] = "review_provider_error"
                        break
                    continue
                result.update({k: decision[k] for k in (
                    "status", "requirements", "coverage", "issues", "feedback")})
                if finalizing or decision["status"] != "UNCERTAIN" or not decision["needs_more_evidence"]:
                    result["stop_reason"] = ("review_complete" if decision["status"] != "UNCERTAIN" else
                                             "review_budget_or_evidence_exhausted" if finalizing else "review_uncertain")
                    break
                requests = decision["inspection_requests"]
                if not requests:
                    result["stop_reason"] = "review_uncertain"
                    break
                for req in requests[:inspections - len(evidence_log)]:
                    result["tool_calls"] += 1
                    result["sql_calls"] += int(req["kind"] == "execute_sql")
                    try:
                        observed = _inspection(store, req)
                    except Exception as exc:
                        observed = {"error": f"{type(exc).__name__}: {exc}"[:500]}
                    entry = {"request": req, "observation": observed}
                    result["inspection_log"].append(entry)
                    evidence_log.append(entry)
                if len(evidence_log) >= inspections:
                    force_final = True
            else:
                if result["status"] == "ERROR" and result["stop_reason"] == "review_error":
                    result["stop_reason"] = "review_model_budget_exhausted"
        except Exception as exc:
            result.update(status="ERROR", stop_reason=f"{type(exc).__name__}: {exc}"[:300])
        finally:
            result["latency_ms"] = round((time.monotonic() - started) * 1000, 3)
        return result
