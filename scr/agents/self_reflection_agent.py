"""SQL-first Self Reflection workflow with bounded finalization and review."""
from __future__ import annotations

import json
import re
import time

from scr.baselines import bird_b0 as b0
from scr.baselines.common import redact_credentials

USAGE_KEYS = ("input_tokens", "output_tokens", "total_tokens",
              "cached_input_tokens", "reasoning_tokens")


def _compact_sql(sql):
    """Normalize SQL formatting, preserving quoted values and SQL comments.

    In particular, SQLite string comparison can distinguish 'a' from 'A',
    and internal whitespace in literals is meaningful.
    """
    tokens = []
    i = 0
    while i < len(sql):
        char = sql[i]
        if char in ("'", '"', "`", "["):
            close = "]" if char == "[" else char
            start = i
            i += 1
            while i < len(sql):
                if sql[i] == close:
                    i += 1
                    if i < len(sql) and sql[i] == close and close != "]":
                        i += 1  # Doubled quote escaping.
                        continue
                    break
                i += 1
            tokens.append(sql[start:i])  # Never change quoted content.
        elif sql.startswith("--", i):
            end = sql.find("\n", i)
            if end < 0:
                end = len(sql)
            tokens.append(sql[i:end])
            i = end
        elif sql.startswith("/*", i):
            end = sql.find("*/", i + 2)
            end = len(sql) if end < 0 else end + 2
            tokens.append(sql[i:end])
            i = end
        elif char.isspace():
            while i < len(sql) and sql[i].isspace():
                i += 1
            tokens.append(" ")
        else:
            tokens.append(char.lower())
            i += 1
    return "".join(tokens).strip()


def _retry_input(original: dict, sql: str, feedback: str) -> dict:
    """B0.make_prompt consumes question/evidence only, not an extra feedback key."""
    cloned = dict(original)
    cloned["evidence"] = (
        (original.get("evidence") or "") +
        "\n\n[REFLECTION FEEDBACK — diagnostic context, not user requirements]"
        "\nThe original question above remains unchanged. Reassess your previous"
        " final query using the verified diagnostic observations below."
        "\nPrevious final SQL:\n" + sql[:6000] +
        "\nReviewer diagnostic feedback:\n" + feedback[:5000] +
        "\n[/REFLECTION FEEDBACK]"
    )
    return cloned


class SelfReflectionAgent:
    """Bounded coordinator; separate from the existing B0 implementation."""

    def __init__(self, reviewer, *, model=None, prompt_variant="baseline",
                 finalizer_model=None, max_attempts=3, max_total_model_calls=240,
                 max_total_tool_calls=240, max_total_sql_calls=240):
        if not 1 <= max_attempts <= 10 or min(max_total_model_calls,
                max_total_tool_calls, max_total_sql_calls) < 1:
            raise ValueError("Invalid Self Reflection budget")
        self.reviewer = reviewer
        self.model = model
        self.finalizer_model = finalizer_model
        self.prompt_variant = prompt_variant
        self.max_attempts = max_attempts
        self.max_total_model_calls = max_total_model_calls
        self.max_total_tool_calls = max_total_tool_calls
        self.max_total_sql_calls = max_total_sql_calls
        b0.system_prompt_for_variant(prompt_variant)  # validate preflight

    @staticmethod
    def _take_b0_usage(report, total):
        total["model_calls"] += report.get("model_calls") or 0
        total["tool_calls"] += report.get("tool_calls") or 0
        total["sql_calls"] += report.get("sql_calls") or 0
        for key in USAGE_KEYS:
            value = report.get(key)
            if value is not None:
                total[key] = (total[key] or 0) + value

    @staticmethod
    def _take_review_usage(review, total):
        for key in ("model_calls", "tool_calls", "sql_calls", *USAGE_KEYS):
            value = review.get(key)
            if value is not None:
                total[key] = (total[key] or 0) + value

    def _can_start_b0(self, total):
        """Reserve B0 investigation and one possible finalizer call/check."""
        return (total["model_calls"] + b0.MAX_MODEL_CALLS <= self.max_total_model_calls
                and total["tool_calls"] + b0.MAX_TOTAL_TOOL_CALLS <= self.max_total_tool_calls
                and total["sql_calls"] + b0.MAX_SQL_EXECUTIONS <= self.max_total_sql_calls)

    def _can_start_review(self, total):
        return (total["model_calls"] + self.reviewer.max_model_calls <= self.max_total_model_calls
                and total["tool_calls"] + 1 + self.reviewer.max_inspections <= self.max_total_tool_calls
                and total["sql_calls"] + 1 + self.reviewer.max_inspections <= self.max_total_sql_calls)

    def _finalize_b0(self, question, store, report, events):
        """No further investigation. Reuse the evidence and the last SQL draft."""
        from langchain_core.messages import HumanMessage, SystemMessage

        final = {"triggered": True, "reason": report.get("stop_reason"),
                 "model_calls": 0, "tool_calls": 0, "sql_calls": 0,
                 "status": "missing", "error": None}
        sql = report.get("final_sql_observed")
        if (self.finalizer_model is not None
                and (report.get("model_calls") or 0) < b0.MAX_MODEL_CALLS):
            observations = []
            for event in events:
                if event.get("kind") in ("tool_result", "model"):
                    observations.append({
                        "kind": event.get("kind"), "name": event.get("name"),
                        "status": event.get("status"),
                        "content": str(event.get("output") or event.get("content") or "")[:1400],
                    })
            context = {
                "question": question.get("question"), "evidence": question.get("evidence"),
                "observed_draft_sql": sql,
                "prior_observations": observations[-30:],
                "instruction": "No more tool calls. Return the single best supported SQL.",
            }
            try:
                report["model_calls"] = (report.get("model_calls") or 0) + 1
                final["model_calls"] = 1
                reply = self.finalizer_model.invoke([
                    SystemMessage(content=(
                        b0.system_prompt_for_variant(self.prompt_variant) +
                        "\nFINALIZATION ONLY: You have no database tools. Use only the "
                        "provided question, evidence and observations; do not invent "
                        "schema facts. Return exactly one safe read-only SQL as "
                        'Final SQL Query:\n"""\nSELECT ...;\n"""'
                    )),
                    HumanMessage(content=json.dumps(context, ensure_ascii=False, default=str)[:24000]),
                ])
                observed = b0._observed_model_metadata(reply)
                for key in USAGE_KEYS:
                    if observed.get(key) is not None:
                        report[key] = (report.get(key) or 0) + observed[key]
                sql = b0.extract_final_sql(getattr(reply, "content", None)) or sql
            except Exception as exc:
                final["error"] = redact_credentials(f"{type(exc).__name__}: {exc}")[:600]
        if sql:
            # Reserve one of B0's 40 tool and SQL calls for this validation.
            if ((report.get("tool_calls") or 0) < b0.MAX_TOTAL_TOOL_CALLS
                    and (report.get("sql_calls") or 0) < b0.MAX_SQL_EXECUTIONS):
                report["tool_calls"] = (report.get("tool_calls") or 0) + 1
                report["sql_calls"] = (report.get("sql_calls") or 0) + 1
                final["tool_calls"], final["sql_calls"] = 1, 1
                try:
                    execution = store.execute(sql)
                    if "error" not in execution:
                        final["status"] = "executable"
                        report["finalization"] = final
                        return sql
                    final["error"] = str(execution["error"])[:600]
                except Exception as exc:
                    final["error"] = redact_credentials(f"{type(exc).__name__}: {exc}")[:600]
            else:
                final["error"] = "No SQL execution budget remains"
        report["finalization"] = final
        return None

    def run(self, question: dict, store) -> dict:
        started = time.perf_counter()
        attempts, structured_events = [], []
        totals = {
            "model_calls": 0, "tool_calls": 0, "sql_calls": 0,
            **{key: None for key in USAGE_KEYS},
        }
        b0_totals = dict(totals)
        reviewer_totals = dict(totals)
        seen_sql, prior_sql, feedback = set(), None, None
        candidates = []
        final_sql = None
        review_status = "unverified"
        stop_reason = "max_attempts"

        def add_event(kind, **data):
            structured_events.append({"seq": len(structured_events) + 1,
                                      "kind": kind, **data})

        for attempt_no in range(1, self.max_attempts + 1):
            if not self._can_start_b0(totals):
                stop_reason = "global_budget_before_b0"
                break
            current_question = (question if attempt_no == 1
                                else _retry_input(question, prior_sql, feedback))
            b0_events, logs = [], []
            try:
                kwargs = {"prompt_variant": self.prompt_variant,
                          "model_call_limit": b0.MAX_MODEL_CALLS - 1,
                          "tool_call_limit": b0.MAX_TOTAL_TOOL_CALLS - 1,
                          "sql_call_limit": b0.MAX_SQL_EXECUTIONS - 1}
                if self.model is not None:
                    kwargs["model"] = self.model
                agent = b0.make_agent(store, **kwargs)
                report = b0.run_one(
                    current_question, agent, log=lambda line: logs.append(
                        redact_credentials(str(line))[:1500]), trace_events=b0_events)
            except Exception as exc:
                report = {
                    "final_sql": None, "graph_completed": False,
                    "model_calls": 0, "tool_calls": 0, "sql_calls": 0,
                    "stop_reason": type(exc).__name__,
                    "error": redact_credentials(f"{type(exc).__name__}: {exc}"),
                }
            if not (report.get("graph_completed") and report.get("final_sql")):
                finalized = self._finalize_b0(current_question, store, report, b0_events)
                if finalized is not None:
                    report["final_sql"] = finalized
                    report["graph_completed"] = True
                    report["stop_reason"] = "b0_forced_sql_finalization"
                add_event("sql_finalization", attempt=attempt_no,
                          status=report.get("finalization", {}).get("status"),
                          reason=report.get("finalization", {}).get("reason"),
                          sql=finalized)
            self._take_b0_usage(report, totals)
            self._take_b0_usage(report, b0_totals)
            for event in b0_events:
                event = dict(event)
                event.pop("seq", None)
                event["attempt"] = attempt_no
                if event.get("kind") == "model":
                    event["model_call"] = (sum(a["b0_report"].get("model_calls") or 0
                                               for a in attempts) + (event.get("model_call") or 0))
                add_event(event.pop("kind"), **event)
            sql = report.get("final_sql") if report.get("graph_completed") else None
            item = {"attempt": attempt_no, "b0_report": report, "b0_events": b0_events,
                    "review": None, "candidate_sql": sql}
            attempts.append(item)
            if not sql:
                stop_reason = "b0_" + str(report.get("stop_reason") or "no_final_sql")
                break
            normalized = _compact_sql(sql)
            if normalized in seen_sql:
                stop_reason = "no_progress_repeated_sql"
                break
            seen_sql.add(normalized)
            if not self._can_start_review(totals):
                if report.get("finalization", {}).get("status") == "executable":
                    candidates.append({"sql": sql, "status": "UNCERTAIN",
                                       "attempt": attempt_no})
                stop_reason = "global_budget_before_review"
                break
            review = self.reviewer.review(question, sql, store, previous_feedback=feedback)
            item["review"] = review
            self._take_review_usage(review, totals)
            self._take_review_usage(review, reviewer_totals)
            rid = f"review-{attempt_no}"
            add_event("tool_call", attempt=attempt_no, name="reflection_review",
                      tool_call_id=rid, args={"candidate_sql": sql[:6000]})
            add_event("tool_result", attempt=attempt_no, name="reflection_review",
                      tool_call_id=rid, status=review.get("status"),
                      output=json.dumps({"status": review.get("status"),
                          "issues": review.get("issues", [])[:5],
                          "feedback": review.get("feedback", "")[:3000],
                          "stop_reason": review.get("stop_reason")}, ensure_ascii=False)[:6000],
                      execution_ms=review.get("latency_ms"))
            review_status = review.get("status", "ERROR")
            if review.get("candidate_safe"):
                candidates.append({"sql": sql, "status": review_status,
                                   "attempt": attempt_no})
            if review_status == "PASS":
                final_sql, stop_reason = sql, "final_sql_ready"
                break
            if review_status == "FAIL":
                if attempt_no >= self.max_attempts:
                    stop_reason = ("unsafe_final_sql" if review.get("stop_reason") == "unsafe_final_sql"
                                   else "max_attempts")
                    break
                feedback = review.get("feedback") or ""
                if not feedback.strip():
                    stop_reason = "missing_review_feedback"
                    break
                prior_sql = sql
                continue
            review_reason = review.get("stop_reason")
            budget_reasons = {"review_model_budget_exhausted",
                              "review_tool_budget_exhausted",
                              "review_response_retry_exhausted"}
            stop_reason = (review_reason if review_status == "UNCERTAIN"
                           and review_reason in budget_reasons else
                           "review_uncertain" if review_status == "UNCERTAIN" else "review_error")
            break

        if final_sql is None and candidates:
            order = {"PASS": 0, "UNCERTAIN": 1, "FAIL": 2, "ERROR": 3}
            best = min(candidates, key=lambda c: (order.get(c["status"], 4), -c["attempt"]))
            final_sql = best["sql"]
            review_status = best["status"]
        output_status = ("missing" if final_sql is None else
                         "verified" if review_status == "PASS" else
                         "generated_known_issues" if review_status == "FAIL" else
                         "generated_unverified")
        if final_sql is None and stop_reason == "max_attempts" and not attempts:
            stop_reason = "not_started"
        add_event("final_validation", status=output_status,
                  sql=final_sql, reason=stop_reason)
        report = {
            "question_id": question["question_id"], "db_id": question["db_id"],
            "final_sql": final_sql, "graph_completed": final_sql is not None,
            "output_status": output_status,
            "review_status": review_status, "stop_reason": stop_reason,
            "finalization_triggered": any(bool(a["b0_report"].get("finalization", {}).get("triggered"))
                                          or bool((a.get("review") or {}).get("finalization_triggered"))
                                          for a in attempts),
            "model_calls": totals["model_calls"], "tool_calls": totals["tool_calls"],
            "sql_calls": totals["sql_calls"],
            **{key: totals[key] for key in USAGE_KEYS},
            "seconds": round(time.perf_counter() - started, 3),
            "attempt_count": len(attempts),
        }
        return {"report": report, "attempts": attempts,
                "structured_events": structured_events,
                "b0_usage": b0_totals, "reviewer_usage": reviewer_totals,
                "final_sql": final_sql, "review_status": review_status,
                "stop_reason": stop_reason}
