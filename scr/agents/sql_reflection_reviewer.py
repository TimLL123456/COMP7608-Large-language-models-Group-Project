"""Independent, bounded and evidence-aware reviewer for *final* B0 SQL."""
from __future__ import annotations

from contextlib import closing
from hashlib import sha256
import json
import re
from pathlib import Path
import time

from scr.baselines import bird_b0 as b0
from scr.baselines.common import redact_credentials

PROMPT_FILE = Path(__file__).with_name("prompts") / "sql_reflection_v1.txt"
PROMPT_VERSION = "sql-reflection-v2.0"
CRITERIA = frozenset({
    "requirement_coverage", "table_column_selection", "join_relationship",
    "aggregation_logic", "filtering_logic", "data_granularity",
    "value_semantics", "temporal_logic", "output_requirements",
    "execution_result_consistency",
})
REQUIREMENT_STATUSES = frozenset({"PASS", "FAIL", "UNCERTAIN", "N/A"})
REVIEW_STATUSES = frozenset({"PASS", "FAIL", "UNCERTAIN"})
TOKEN_KEYS = ("input_tokens", "output_tokens", "total_tokens",
              "cached_input_tokens", "reasoning_tokens")

# Only the reviewer requests constrained output. B0 model calls are untouched.
def _object(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


REVIEW_SCHEMA = _object({
    "status": {"type": "string", "enum": sorted(REVIEW_STATUSES)},
    "requirements": {"type": "array", "items": _object({
        "name": {"type": "string"}, "expected": {"type": "string"},
        "observed": {"type": "string"},
        "status": {"type": "string", "enum": sorted(REQUIREMENT_STATUSES)},
        "evidence": {"type": "string"},
    })},
    "issues": {"type": "array", "items": _object({
        "category": {"type": "string", "enum": sorted(CRITERIA)},
        "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
        "description": {"type": "string"}, "evidence": {"type": "string"},
        "suggested_action": {"type": "string"},
    })},
    "feedback": {"type": "string"},
    "needs_more_evidence": {"type": "boolean"},
    "inspection_requests": {"type": "array", "items": _object({
        "kind": {"type": "string",
                 "enum": ["list_tables", "inspect_table", "execute_sql"]},
        "reason": {"type": "string"}, "table": {"type": "string"},
        "sql": {"type": "string"},
    })},
})


def _redact_diagnostic(value):
    """Bound persisted diagnostics; never retain raw authorization credentials."""
    text = redact_credentials(str(value))
    text = re.sub(r'(?i)(bearer\s+)[^\s"\x27]+', r'\1[REDACTED]', text)
    text = re.sub(r"\bsk-[A-Za-z0-9_-]{12,}\b", "[REDACTED]", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{8,}\b",
                  "[REDACTED]", text)
    return text[:900] if len(text) <= 900 else text[:450] + " … [truncated] … " + text[-450:]


def _response_diagnostic(reply, attempt, failure):
    try:
        raw = _model_text(reply)
    except (TypeError, ValueError):
        raw = f"<{type(reply).__name__} non-text response>"
    return {
        "call": attempt, "kind": "invalid_response",
        "error_type": type(failure).__name__,
        "error": _redact_diagnostic(failure)[:400],
        "response_chars": len(raw),
        "response_sha256": sha256(raw.encode("utf-8", errors="replace")).hexdigest(),
        "response_excerpt": _redact_diagnostic(raw),
    }


def _model_text(message):
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content
                       if isinstance(part, dict) and part.get("type") in ("text", "output_text"))
    raise ValueError("Reviewer response is not text")


def _parse_decision(message):
    if isinstance(message, dict):
        if len(json.dumps(message, ensure_ascii=False, default=str)) > 32000:
            raise ValueError("Reviewer response too long")
        decision = message
    else:
        text = _model_text(message).strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) < 3 or not lines[-1].strip() == "```":
                raise ValueError("Malformed fenced reviewer response")
            text = "\n".join(lines[1:-1])
        if len(text) > 32000:
            raise ValueError("Reviewer response too long")
        # Do not strip a valid prefix and silently discard trailing content.
        decision = json.loads(text)
    if not isinstance(decision, dict) or decision.get("status") not in REVIEW_STATUSES:
        raise ValueError("Invalid reviewer status")
    requirements, issues = decision.get("requirements"), decision.get("issues")
    if not isinstance(requirements, list) or not isinstance(issues, list) or len(requirements) > 30 or len(issues) > 15:
        raise ValueError("Invalid reviewer requirement/issue lists")
    for item in requirements:
        if not isinstance(item, dict) or item.get("status") not in REQUIREMENT_STATUSES:
            raise ValueError("Invalid per-requirement status")
        if not all(isinstance(item.get(key), str) for key in ("name", "expected", "observed", "evidence")):
            raise ValueError("Incomplete reviewer requirement")
    for item in issues:
        if not isinstance(item, dict) or item.get("category") not in CRITERIA:
            raise ValueError("Invalid reviewer issue category")
        if item.get("severity") not in ("critical", "major", "minor"):
            raise ValueError("Invalid issue severity")
        if not all(isinstance(item.get(key), str) and item[key].strip()
                   for key in ("description", "evidence", "suggested_action")):
            raise ValueError("FAIL issues need description, evidence and suggested action")
    if not isinstance(decision.get("feedback"), str) or len(decision["feedback"]) > 5000:
        raise ValueError("Invalid reviewer feedback")
    if type(decision.get("needs_more_evidence")) is not bool:
        raise ValueError("Invalid evidence flag")
    requests = decision.get("inspection_requests", [])
    if not isinstance(requests, list) or len(requests) > 2:
        raise ValueError("Invalid inspection requests")
    for req in requests:
        if not isinstance(req, dict) or req.get("kind") not in ("list_tables", "inspect_table", "execute_sql"):
            raise ValueError("Invalid inspection request kind")
        if not isinstance(req.get("reason"), str) or not req["reason"].strip():
            raise ValueError("Inspection request needs a specific reason")
        key = "table" if req["kind"] == "inspect_table" else "sql" if req["kind"] == "execute_sql" else None
        if key and (not isinstance(req.get(key), str) or not req[key].strip()):
            raise ValueError("Inspection request missing table/sql")
    if decision["status"] == "FAIL":
        if not issues or not decision["feedback"].strip():
            raise ValueError("Evidence-backed FAIL requires issues and feedback")
    elif issues:
        raise ValueError("Only FAIL can contain confirmed issues")
    if decision["status"] == "PASS":
        checked = [item for item in requirements if item["status"] == "PASS"]
        if (not checked or any(item["status"] in ("FAIL", "UNCERTAIN")
                               for item in requirements)
                or any(not all(item[key].strip() for key in
                               ("name", "expected", "observed", "evidence"))
                       for item in checked)):
            raise ValueError("PASS lacks substantive supported coverage")
        if decision["needs_more_evidence"] or requests:
            raise ValueError("PASS cannot request more evidence")
    if decision["status"] == "UNCERTAIN" and any(item["status"] == "FAIL" for item in requirements):
        raise ValueError("A confirmed material mismatch must produce FAIL")
    if decision["status"] != "UNCERTAIN" and (decision["needs_more_evidence"] or requests):
        raise ValueError("Only UNCERTAIN can request more evidence")
    return decision


class SQLReflectionReviewer:
    """Independent multi-round reviewer; reserves one model call for final judgment."""

    def __init__(self, model, *, max_model_calls=40, max_inspections=39):
        if model is None or not 1 <= max_model_calls <= 40 or not 0 <= max_inspections <= 39:
            raise ValueError("Invalid reviewer model/budget")
        self.model = model
        self.max_model_calls = max_model_calls
        self.max_inspections = max_inspections
        self.prompt = PROMPT_FILE.read_text(encoding="utf-8")
        self.structured_model = None
        self.structured_disabled = False  # Remember preview incompatibility across questions.
        kind = getattr(model, "_llm_type", None)
        if kind == "chatgpt-siwc":
            # SIWC adapter forwards this only on the independent reviewer call.
            self.structured_model = model.bind(text_format={
                "type": "json_schema", "name": "sql_reflection_review",
                "strict": True, "schema": REVIEW_SCHEMA,
            })
        elif kind in ("openai-chat", "openai"):
            # Preserve the raw message for usage accounting and diagnostics.
            self.structured_model = model.with_structured_output(
                REVIEW_SCHEMA, method="json_schema", strict=True, include_raw=True)

    @staticmethod
    def _inspect(store, request):
        kind = request["kind"]
        if kind == "list_tables":
            return store.list_tables()
        if kind == "inspect_table":
            return store.inspect_table(request["table"][:200])
        return store.execute(request["sql"])

    def review(self, question: dict, sql: str, store, *, previous_feedback=None) -> dict:
        """Never reads evaluation references; all DB access uses the B0 read-only store."""
        from langchain_core.messages import HumanMessage, SystemMessage

        started = time.perf_counter()
        review = {
            "status": "ERROR", "requirements": [], "issues": [], "feedback": "",
            "needs_more_evidence": False, "inspection_requests": [],
            "inspection_log": [], "execution": None, "candidate_safe": False,
            "stop_reason": None, "model_calls": 0, "tool_calls": 0, "sql_calls": 0,
            "usage_observed": False, **{key: None for key in TOKEN_KEYS},
            **{key + "_observed_calls": 0 for key in TOKEN_KEYS},
            "latency_ms": None, "response_diagnostics": [],
            "finalization_triggered": False, "finalization_reason": None,
        }
        try:
            if not isinstance(sql, str) or not sql.strip():
                raise ValueError("No candidate SQL to review")
            # The actual final submitted SQL gets its own read-only compilation/execution gate.
            execution = store.execute(sql)
            review["execution"] = execution
            review["tool_calls"] += 1
            review["sql_calls"] += 1
            if "error" in execution:
                error = str(execution["error"])
                uncertain = any(term in error.lower() for term in (
                    "interrupted", "timeout", "locked", "busy", "unavailable"))
                unsafe = any(term in error.lower() for term in (
                    "not authorized", "only select", "not allowed", "multiple statements"))
                review.update(
                    status="UNCERTAIN" if uncertain else "FAIL",
                    candidate_safe=False,
                    stop_reason="execution_inconclusive" if uncertain else "final_sql_execution_error",
                    issues=[] if uncertain else [{
                        "category": "execution_result_consistency", "severity": "critical",
                        "description": "The exact final SQL failed the read-only execution check.",
                        "evidence": error[:1000],
                        "suggested_action": "Recheck SQL syntax, source identifiers, aliases and safety restrictions.",
                    }],
                    feedback="" if uncertain else "Correct the exact final SQL execution error: " + error[:1000],
                )
                if unsafe:
                    review["stop_reason"] = "unsafe_final_sql"
                return review
            review["candidate_safe"] = True
            evidence_log = []
            repair = None
            force_final = self.max_inspections == 0
            active_model = (self.structured_model if not self.structured_disabled
                            and self.structured_model is not None else self.model)
            for attempt in range(self.max_model_calls):
                finalizing = force_final or attempt + 1 == self.max_model_calls
                if finalizing:
                    review["finalization_triggered"] = True
                    review["finalization_reason"] = ("review_tool_budget_exhausted"
                        if force_final else "review_model_budget_exhausted")
                context = {
                    "question": question.get("question"), "evidence": question.get("evidence"),
                    "candidate_sql": sql,
                    "observed_execution": execution,
                    "previous_feedback": previous_feedback or "",
                    "inspection_observations": evidence_log[-12:],
                    "prior_inspection_count": len(evidence_log),
                    "remaining_inspections": (0 if finalizing else
                                              self.max_inspections - len(evidence_log)),
                    "review_finalization": finalizing,
                    "requested_format": "JSON",
                }
                if repair is not None:
                    context["response_repair"] = repair
                review["model_calls"] += 1  # attempted calls, including failures
                try:
                    raw_reply = active_model.invoke([
                        SystemMessage(content=self.prompt + (
                            "\nFINALIZATION MODE: No more inspection requests. Decide PASS "
                            "only with supported evidence, FAIL only for confirmed defects; "
                            "otherwise UNCERTAIN. Preserve all uncertainty." if finalizing else "")),
                        HumanMessage(content=json.dumps(context, ensure_ascii=False, default=str)),
                    ])
                except Exception as exc:
                    review["response_diagnostics"].append({
                        "call": attempt + 1, "kind": "provider_error",
                        "error_type": type(exc).__name__,
                        "error": _redact_diagnostic(exc),
                    })
                    # A preview provider may reject strict response formatting.
                    # The fallback is another charged call, never an extra budget.
                    status_code = getattr(getattr(exc, "response", None), "status_code", None)
                    if active_model is not self.model and status_code in (400, 422):
                        self.structured_disabled = True
                        if attempt + 1 < self.max_model_calls:
                            active_model = self.model
                            repair = {"reason": "The provider rejected constrained output. "
                                        "Return one complete JSON decision with the original evidence."}
                            continue
                    review["stop_reason"] = "review_provider_error"
                    break

                reply = (raw_reply.get("raw") if isinstance(raw_reply, dict)
                         and "raw" in raw_reply else raw_reply)
                candidate = (raw_reply.get("parsed") if isinstance(raw_reply, dict)
                             and "parsed" in raw_reply
                             and raw_reply.get("parsing_error") is None
                             and raw_reply.get("parsed") is not None else reply)
                observed = b0._observed_model_metadata(reply)
                for key in TOKEN_KEYS:
                    value = observed.get(key)
                    if value is not None:
                        review[key] = (review[key] or 0) + value
                        review[key + "_observed_calls"] += 1
                        review["usage_observed"] = True
                try:
                    if (isinstance(raw_reply, dict)
                            and raw_reply.get("parsing_error") is not None):
                        raise ValueError("Structured output parser rejected response: "
                                         + str(raw_reply["parsing_error"])[:300])
                    decision = _parse_decision(candidate)
                except (ValueError, TypeError) as exc:
                    diagnostic = _response_diagnostic(reply, attempt + 1, exc)
                    review["response_diagnostics"].append(diagnostic)
                    review.update(status="ERROR", requirements=[], issues=[], feedback="",
                                  needs_more_evidence=False, inspection_requests=[])
                    if attempt + 1 >= self.max_model_calls:
                        review["stop_reason"] = "review_response_retry_exhausted"
                        break
                    # Use the same question and evidence; never accept or silently
                    # coerce a previous invalid decision into a PASS.
                    repair = {
                        "reason": "The previous reviewer response was invalid. "
                                  "Re-evaluate the original question and SQL; emit one "
                                  "complete, internally consistent JSON decision.",
                        "validation_error": diagnostic["error"],
                        "rejected_response_excerpt": diagnostic["response_excerpt"][:600],
                    }
                    continue

                review["response_diagnostics"].append({
                    "call": attempt + 1, "kind": "valid_decision",
                    "status": decision["status"],
                })
                review.update({k: decision.get(k) for k in (
                    "status", "requirements", "issues", "feedback",
                    "needs_more_evidence", "inspection_requests")})
                if finalizing:
                    review["stop_reason"] = (review["finalization_reason"]
                                              if decision["status"] == "UNCERTAIN"
                                              else "review_complete")
                    break
                if decision["status"] != "UNCERTAIN" or not decision["needs_more_evidence"]:
                    review["stop_reason"] = "review_complete"
                    break
                requests = decision["inspection_requests"]
                if not requests or len(evidence_log) >= self.max_inspections:
                    force_final = True
                    continue
                repair = None
                for request in requests[:self.max_inspections - len(evidence_log)]:
                    review["tool_calls"] += 1
                    review["sql_calls"] += int(request["kind"] == "execute_sql")
                    try:
                        observed_result = self._inspect(store, request)
                    except Exception as exc:
                        observed_result = {"error": redact_credentials(f"{type(exc).__name__}: {exc}")}
                    log = {"kind": request["kind"], "reason": request["reason"][:500],
                           "request": {key: val[:2000] if isinstance(val, str) else val
                                       for key, val in request.items()},
                           "observation": observed_result}
                    evidence_log.append(log)
                    review["inspection_log"].append(log)
                if len(evidence_log) >= self.max_inspections:
                    force_final = True
            else:
                review["stop_reason"] = "review_model_budget_exhausted"
        except Exception as exc:
            review.update(status="ERROR", issues=[], feedback="", requirements=[],
                          needs_more_evidence=False, inspection_requests=[],
                          stop_reason=_redact_diagnostic(f"{type(exc).__name__}: {exc}"))
        finally:
            review["latency_ms"] = round((time.perf_counter() - started) * 1000, 3)
        return review
