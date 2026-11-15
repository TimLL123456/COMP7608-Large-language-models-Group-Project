"""SQL-first orchestration for the independent RubricSelfReflection variant."""
from __future__ import annotations

import json
import time

from scr.baselines import bird_b0 as b0
from scr.baselines.common import redact_credentials
from .reviewer import RubricReviewer, TOKEN_KEYS, _usage, add_usage
from .finalizer import refine_sql


class RubricSelfReflectionAgent:
    """Run unchanged B0; review all atomic requirements; refine once if needed."""

    def __init__(self, reviewer: RubricReviewer, *, model=None, finalizer_model=None,
                 prompt_variant="baseline", max_attempts=3,
                 max_total_model_calls=240, max_total_tool_calls=240,
                 max_total_sql_calls=240):
        if not 1 <= max_attempts <= 10 or min(max_total_model_calls,
                max_total_tool_calls, max_total_sql_calls) < 1:
            raise ValueError("Invalid coordinator budget")
        b0.system_prompt_for_variant(prompt_variant)
        self.reviewer = reviewer
        self.model = model
        self.finalizer_model = finalizer_model or reviewer.model
        self.prompt_variant = prompt_variant
        self.max_attempts = max_attempts
        self.limits = {"model_calls": max_total_model_calls,
                       "tool_calls": max_total_tool_calls, "sql_calls": max_total_sql_calls}

    def _available(self, totals, *, model=0, tool=0, sql=0, reserve_final=True):
        reserve = int(reserve_final)
        return (totals["model_calls"] + model + reserve <= self.limits["model_calls"] and
                totals["tool_calls"] + tool + reserve <= self.limits["tool_calls"] and
                totals["sql_calls"] + sql + reserve <= self.limits["sql_calls"])

    @staticmethod
    def _retry_question(original, previous_sql, feedback):
        updated = dict(original)
        updated["evidence"] = ((original.get("evidence") or "") +
            "\n\n[REVIEW DIAGNOSTIC CONTEXT — not new user requirements]"
            "\nOriginal question above has priority. Recheck the existing SQL using"
            " the evidence-backed diagnostic; preserve correct logic."
            "\nPrevious candidate:\n" + previous_sql[:6000] +
            "\nConfirmed reviewer findings:\n" + feedback[:5000] +
            "\n[/REVIEW DIAGNOSTIC CONTEXT]")
        return updated

    def _b0_generate(self, question, store) -> dict:
        """Reserve B0 call/tool/SQL slot for output even when investigation fails."""
        from langchain_core.messages import HumanMessage, SystemMessage

        events = []
        try:
            kwargs = {"prompt_variant": self.prompt_variant,
                      "model_call_limit": b0.MAX_MODEL_CALLS - 1,
                      "tool_call_limit": b0.MAX_TOTAL_TOOL_CALLS - 1,
                      "sql_call_limit": b0.MAX_SQL_EXECUTIONS - 1}
            if self.model is not None:
                kwargs["model"] = self.model
            agent = b0.make_agent(store, **kwargs)
            report = b0.run_one(question, agent, log=lambda _message: None, trace_events=events)
        except Exception as exc:
            report = {"final_sql": None, "graph_completed": False,
                      "model_calls": 0, "tool_calls": 0, "sql_calls": 0,
                      "stop_reason": "b0_error", "error": redact_credentials(str(exc))[:400]}
        sql = report.get("final_sql") if report.get("graph_completed") else None
        completion = {"triggered": not bool(sql), "status": "not_needed" if sql else "missing",
                      "error": None, "model_calls": 0, "tool_calls": 0, "sql_calls": 0}
        if not sql:
            draft = report.get("final_sql_observed")
            # The 40th B0 model call was reserved for output finalization.
            if self.finalizer_model is not None and (report.get("model_calls") or 0) < b0.MAX_MODEL_CALLS:
                completion["model_calls"] = 1
                report["model_calls"] = (report.get("model_calls") or 0) + 1
                observations = [{"kind": e.get("kind"), "name": e.get("name"),
                                 "content": str(e.get("output") or e.get("content") or "")[:900]}
                                for e in events if e.get("kind") in ("tool_result", "model")][-25:]
                try:
                    context = {"question": question.get("question"), "evidence": question.get("evidence"),
                               "observed_draft_sql": draft, "observations": observations}
                    reply = self.finalizer_model.invoke([
                        SystemMessage(content=b0.system_prompt_for_variant(self.prompt_variant) +
                            "\nFINALIZATION ONLY: No new tools. Return exactly one safe read-only "
                            'SQL in the format Final SQL Query:\n"""\nSELECT ...;\n"""'),
                        HumanMessage(content=json.dumps(context, ensure_ascii=False, default=str)[:20_000]),
                    ])
                    metrics = b0._observed_model_metadata(reply)
                    for key in TOKEN_KEYS:
                        if metrics.get(key) is not None:
                            report[key] = (report.get(key) or 0) + metrics[key]
                    draft = b0.extract_final_sql(getattr(reply, "content", None)) or draft
                except Exception as exc:
                    completion["error"] = redact_credentials(f"{type(exc).__name__}: {exc}")[:400]
            if draft and (report.get("tool_calls") or 0) < b0.MAX_TOTAL_TOOL_CALLS and (
                    report.get("sql_calls") or 0) < b0.MAX_SQL_EXECUTIONS:
                completion["tool_calls"] = 1
                completion["sql_calls"] = 1
                report["tool_calls"] = (report.get("tool_calls") or 0) + 1
                report["sql_calls"] = (report.get("sql_calls") or 0) + 1
                try:
                    check = store.execute(draft)
                    if "error" not in check:
                        sql = draft
                        completion["status"] = "executable"
                    else:
                        completion["error"] = str(check["error"])[:600]
                except Exception as exc:
                    completion["error"] = redact_credentials(str(exc))[:500]
        report["finalization"] = completion
        if sql:
            report["final_sql"] = sql
        return {"report": report, "candidate_sql": sql, "events": events,
                "completion": completion}

    def run(self, question: dict, store) -> dict:
        started = time.monotonic()
        totals, b0_usage, reviewer_usage, refinement_usage = (_usage(), _usage(), _usage(), _usage())
        attempts, candidates, structured_events = [], [], []
        def emit(kind, **details):
            structured_events.append({"seq": len(structured_events)+1, "kind": kind, **details})

        extracted = {"status": "ERROR", "requirements": [], "error": "not_started", **_usage()}
        # First reserve one full B0 run and the final refinement if possible.
        if self._available(totals, model=b0.MAX_MODEL_CALLS + 2,
                           tool=b0.MAX_TOTAL_TOOL_CALLS, sql=b0.MAX_SQL_EXECUTIONS):
            extracted = self.reviewer.extract(question, max_calls=2)
            add_usage(totals, extracted)
            add_usage(reviewer_usage, extracted)
        emit("requirements_extracted", status=extracted["status"],
             requirements=extracted["requirements"], error=extracted.get("error"))
        feedback, previous_sql = "", ""
        seen_sql = set()
        stop_reason = "not_started"
        for number in range(1, self.max_attempts + 1):
            if not self._available(totals, model=b0.MAX_MODEL_CALLS,
                                   tool=b0.MAX_TOTAL_TOOL_CALLS, sql=b0.MAX_SQL_EXECUTIONS):
                stop_reason = "global_budget_before_b0"
                break
            request = question if number == 1 else self._retry_question(question, previous_sql, feedback)
            generated = self._b0_generate(request, store)
            add_usage(totals, generated["report"])
            add_usage(b0_usage, generated["report"])
            sql = generated["candidate_sql"]
            attempt = {"attempt": number, "candidate_sql": sql,
                       "b0_report": generated["report"], "b0_events": generated["events"],
                       "review": None}
            attempts.append(attempt)
            emit("b0_attempt", attempt=number, candidate_sql=sql,
                 b0_status=generated["report"].get("stop_reason"),
                 finalization=generated["completion"])
            if not sql:
                stop_reason = "b0_no_executable_sql"
                break
            if sql.strip() in seen_sql:
                stop_reason = "no_progress_repeated_sql"
                break
            seen_sql.add(sql.strip())
            if extracted["status"] != "PASS":
                # Preserve B0 candidate, but do not misclassify a non-review as PASS.
                if self._available(totals, tool=1, sql=1):
                    totals["tool_calls"] += 1
                    totals["sql_calls"] += 1
                    check = store.execute(sql)
                    if "error" not in check:
                        candidates.append({"sql": sql, "status": "ERROR", "review": {}, "attempt": number})
                stop_reason = "requirements_extraction_error"
                break
            max_model = min(self.reviewer.max_model_calls,
                            self.limits["model_calls"] - totals["model_calls"] - 1)
            max_tool = min(self.reviewer.max_inspections + 1,
                           self.limits["tool_calls"] - totals["tool_calls"] - 1)
            max_sql = self.limits["sql_calls"] - totals["sql_calls"] - 1
            if min(max_model, max_tool, max_sql) < 1:
                if self._available(totals, tool=1, sql=1):
                    totals["tool_calls"] += 1
                    totals["sql_calls"] += 1
                    check = store.execute(sql)
                    if "error" not in check:
                        candidates.append({"sql": sql, "status": "UNCERTAIN", "review": {}, "attempt": number})
                stop_reason = "global_budget_before_review"
                break
            review = self.reviewer.review(question, sql, store, extracted["requirements"],
                                          previous_feedback=feedback, max_model_calls=max_model,
                                          max_inspections=min(self.reviewer.max_inspections,
                                                              max_tool - 1, max_sql - 1))
            attempt["review"] = review
            add_usage(totals, review)
            add_usage(reviewer_usage, review)
            emit("rubric_review", attempt=number, status=review["status"],
                 requirements=review.get("requirements", []), coverage=review.get("coverage", {}),
                 issues=review.get("issues", []), stop_reason=review.get("stop_reason"))
            if review.get("candidate_safe"):
                candidates.append({"sql": sql, "status": review["status"], "review": review,
                                   "attempt": number})
            if review["status"] == "PASS":
                stop_reason = "rubric_pass"
                break
            if review["status"] == "FAIL" and review.get("feedback") and number < self.max_attempts:
                # Read-only store rejects unsafe final SQL. Retry from original question.
                previous_sql, feedback = sql, review["feedback"]
                stop_reason = "retry_feedback"
                continue
            stop_reason = review.get("stop_reason") or "review_not_pass"
            break
        rank = {"PASS": 0, "UNCERTAIN": 1, "FAIL": 2, "ERROR": 3}
        best = min(candidates, key=lambda x: (rank[x["status"]], -x["attempt"])) if candidates else None
        selected = best["sql"] if best else None
        selected_review = best["review"] if best else {}
        final_status = best["status"] if best else "unverified"
        refinement = {"triggered": False, "status": "not_needed", **_usage()}
        # Reviewer ERROR alone is not justification for speculative refinement.
        material_unmet = bool(best and any(r.get("material") and r.get("status") in ("FAIL", "UNCERTAIN")
                                           for r in selected_review.get("requirements", [])))
        material_unmet |= bool(best and selected_review.get("coverage", {}).get("status") in ("GAP", "UNCERTAIN"))
        # Permit repairing an invalid final SQL when no safe candidate exists; the
        # execution error is evidence, but this raw SQL is NEVER an output fallback.
        refinement_input = selected
        if not best:
            failed = next((a for a in reversed(attempts) if a.get("candidate_sql") and
                           (a.get("review") or {}).get("status") == "FAIL"), None)
            if failed:
                material_unmet = True
                refinement_input = failed["candidate_sql"]
                selected_review = failed["review"]
        if material_unmet and final_status != "PASS" and refinement_input:
            observations = []
            for attempt in attempts:
                for e in attempt["b0_events"]:
                    if e.get("kind") == "tool_result":
                        observations.append({"kind": "b0_tool", "name": e.get("name"),
                                             "content": str(e.get("output", ""))[:1000]})
                for e in (attempt.get("review") or {}).get("inspection_log", []):
                    observations.append({"kind": "review_inspection",
                                         "content": json.dumps(e, ensure_ascii=False, default=str)[:1200]})
            refinement = refine_sql(self.finalizer_model, question, refinement_input, selected_review,
                                    observations, store,
                                    allow_model=self._available(totals, model=1, reserve_final=False),
                                    allow_execution=self._available(totals, tool=1, sql=1, reserve_final=False))
            add_usage(totals, refinement)
            add_usage(refinement_usage, refinement)
            emit("sql_refinement", status=refinement["status"],
                 sql=refinement.get("sql"), error=refinement.get("error"))
            if refinement["status"] == "executable":
                selected = refinement["sql"]
                final_status = "UNCERTAIN"  # Refinement execution is not reviewer PASS.
                stop_reason = "refined_sql_executable_unverified"
        output_status = ("missing" if selected is None else
                         "verified" if final_status == "PASS" else
                         "generated_known_issues" if final_status == "FAIL" else
                         "generated_unverified")
        report = {"question_id": question["question_id"], "db_id": question["db_id"],
                  "final_sql": selected, "graph_completed": selected is not None,
                  "review_status": final_status, "output_status": output_status,
                  "stop_reason": stop_reason, "attempt_count": len(attempts),
                  "refinement_status": refinement["status"], "finalization_triggered": bool(
                      refinement["triggered"] or any(a["b0_report"]["finalization"]["triggered"]
                                                   for a in attempts)),
                  "seconds": round(time.monotonic()-started, 3), **totals}
        emit("final_validation", status=output_status, sql=selected, reason=stop_reason)
        return {"report": report, "attempts": attempts, "extraction": extracted,
                "structured_events": structured_events, "final_sql": selected,
                "review_status": final_status, "stop_reason": stop_reason,
                "refinement": refinement, "b0_usage": b0_usage,
                "reviewer_usage": reviewer_usage, "refinement_usage": refinement_usage}
