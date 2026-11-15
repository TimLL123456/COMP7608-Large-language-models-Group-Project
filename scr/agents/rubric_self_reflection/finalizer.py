"""One-shot post-review final SQL improvement using existing evidence only."""
from __future__ import annotations

import json
from pathlib import Path

from scr.baselines import bird_b0 as b0
from .reviewer import _usage, TOKEN_KEYS

FINAL_PROMPT = Path(__file__).resolve().parent / "prompts" / "final_refinement_v1.txt"
FINAL_PROMPT_VERSION = "rubric-refinement-v1"


def refine_sql(model, question: dict, sql: str, review: dict, observations: list,
               store, *, allow_model: bool, allow_execution: bool) -> dict:
    """Do not return SQL unless read-only store execution verifies it can run."""
    result = {"triggered": True, "status": "not_run", "sql": None, "error": None,
              "execution": None, **_usage()}
    if not allow_model or not allow_execution:
        result["status"] = "budget_exhausted"
        return result
    from langchain_core.messages import HumanMessage, SystemMessage
    context = {"question": question.get("question"), "evidence": question.get("evidence"),
               "current_sql": sql, "review": {k: review.get(k) for k in (
                   "status", "requirements", "coverage", "issues", "feedback")},
               "prior_observations": observations[-20:]}
    result["model_calls"] += 1
    try:
        reply = model.invoke([
            SystemMessage(content=FINAL_PROMPT.read_text(encoding="utf-8")),
            HumanMessage(content=json.dumps(context, ensure_ascii=False, default=str)[:28_000]),
        ])
        observed = b0._observed_model_metadata(reply)
        for key in TOKEN_KEYS:
            value = observed.get(key)
            if value is not None:
                result[key] = (result[key] or 0) + value
        candidate = b0.extract_final_sql(getattr(reply, "content", None))
        if not candidate:
            result.update(status="invalid_format", error="No single final SELECT query parsed")
            return result
        result["tool_calls"] += 1
        result["sql_calls"] += 1
        execution = store.execute(candidate)
        result["execution"] = execution
        if "error" in execution:
            result.update(status="invalid_execution", error=str(execution["error"])[:800])
            return result
        result.update(status="executable", sql=candidate)
    except Exception as exc:
        result.update(status="error", error=f"{type(exc).__name__}: {exc}"[:400])
    return result
