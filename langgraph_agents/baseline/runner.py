"""Execute frozen BIRD selections with LangGraph B0, retaining B0 report semantics."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from time import perf_counter

from scr.baselines import bird_b0 as b0
from scr.baselines.common import DEFAULT_MODELS, build_model, redact_credentials
from scr.baselines.sqlite_readonly import DEFAULT_SQL_TIMEOUT_SECONDS
from scr.cli import run_bird_b0_eval as original_cli

from langgraph_agents.baseline.graph import GRAPH_VERSION, build_graph

VARIANT = "LangGraphB0"


def run_question(graph, question, *, run_id: str, config_snapshot: dict):
    """Return one report and graph transitions without extra model/SQL calls."""
    graph_events = []
    output = {}
    started = perf_counter()
    try:
        for update in graph.stream(
            {"agent_input": question, "run_id": run_id, "config_snapshot": config_snapshot},
            config={"recursion_limit": 25}, stream_mode="updates",
        ):
            for node_name, values in update.items():
                if not isinstance(values, dict):
                    continue
                output.update(values)
                graph_events.append({
                    "seq": len(graph_events) + 1, "kind": "graph_node_complete",
                    "node": node_name,
                    "observed_at_ms": round((perf_counter() - started) * 1000, 3),
                })
        if "report" not in output:
            raise RuntimeError("LangGraph finished without B0 report")
    except Exception as exc:
        output["report"] = {
            "final_sql": None, "model_calls": 0, "tool_calls": 0,
            "sql_calls": 0, "input_tokens": None, "output_tokens": None,
            "usage_observed": False, "seconds": None, "graph_completed": False,
            "stop_reason": type(exc).__name__,
            "error": redact_credentials(f"{type(exc).__name__}: {exc}"),
        }
        output["final_sql"] = None
        output["status"] = "missing_final_sql"
        graph_events.append({
            "seq": len(graph_events) + 1, "kind": "graph_error",
            "error": output["report"]["error"],
            "observed_at_ms": round((perf_counter() - started) * 1000, 3),
        })
    return output, graph_events


def _model_for_args(args):
    provider = args.provider
    if provider not in DEFAULT_MODELS:
        raise ValueError("Unsupported provider")
    if args.reasoning_effort is not None and provider != "chatgpt-siwc":
        raise ValueError("--reasoning-effort currently requires --provider chatgpt-siwc")
    model_name = args.model or (b0.MODEL if provider == "nvidia" else DEFAULT_MODELS[provider])
    if not model_name:
        raise ValueError(f"--model is required for provider {provider!r}")
    if provider == "nvidia" and not os.environ.get("NVIDIA_API_KEY"):
        raise ValueError("NVIDIA_API_KEY required for NVIDIA B0; no fallback")
    if provider == "chatgpt-siwc":
        from scr.baselines.siwc_auth import CREDS, read_json
        if not read_json(CREDS):
            raise ValueError("Sign in first: uv run python -m scr.baselines.siwc_auth")
    # Preserve the same optional-provider parameter handling as original B0 CLI.
    model = None
    if provider != "nvidia" or model_name != b0.MODEL:
        model = build_model(
            model_name, provider=provider,
            temperature=None if provider in ("openai", "chatgpt-siwc") else b0.TEMPERATURE,
            top_p=b0.TOP_P if provider == "nvidia" else None,
            max_tokens=b0.MAX_OUTPUT_TOKENS, timeout=b0.REQUEST_TIMEOUT,
            **({"reasoning_effort": args.reasoning_effort}
               if args.reasoning_effort is not None else {}),
        )
    return model_name, model


def infer(args) -> int:
    # Same immutable selection and dataset-manifest checks as the reference B0 CLI.
    folder, dataset, selected = original_cli._selection(args)
    system_sha = sha256(b0.system_prompt_for_variant(args.prompt_variant).encode()).hexdigest()
    model_name, model = _model_for_args(args)  # authentication preflight before files
    run_dir = folder / VARIANT / args.split / args.run_id
    if run_dir.exists() or run_dir.is_symlink():
        raise ValueError(f"Refusing to overwrite run: {run_dir}")
    run_dir.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    config = {
        "model": model_name, "provider": args.provider,
        "prompt_variant": args.prompt_variant,
        "requested_reasoning_effort": args.reasoning_effort,
        "max_model_calls": b0.MAX_MODEL_CALLS,
        "max_total_tool_calls": b0.MAX_TOTAL_TOOL_CALLS,
        "max_sql_executions": b0.MAX_SQL_EXECUTIONS,
    }
    graph = build_graph(
        database_path=dataset.get_database_path,
        model=model, model_name=model_name,
        prompt_variant=args.prompt_variant, preview_rows=args.preview_rows,
    )
    missing = 0
    with (run_dir / "predictions.jsonl").open("w", encoding="utf-8") as predictions, \
         (run_dir / "traces.jsonl").open("w", encoding="utf-8") as traces:
        for question in selected:
            output, graph_events = run_question(graph, question, run_id=args.run_id, config_snapshot=config)
            report = output["report"]
            report["model"] = model_name
            sql = output.get("final_sql") if report.get("graph_completed") else None
            missing += int(sql is None)
            original_cli._jsonl_write(predictions, {
                "question_id": question["question_id"], "db_id": question["db_id"],
                "predicted_sql": sql, "provider": args.provider, "model": model_name,
                "requested_reasoning_effort": args.reasoning_effort,
                "tool_calls": report.get("tool_calls"),
                "input_tokens": report.get("input_tokens") if report.get("usage_observed") else None,
                "output_tokens": report.get("output_tokens") if report.get("usage_observed") else None,
                "total_tokens": report.get("total_tokens"),
                "cached_input_tokens": report.get("cached_input_tokens"),
                "reasoning_tokens": report.get("reasoning_tokens"),
                "reasoning_effort": report.get("reasoning_effort"),
                "thinking_level": report.get("thinking_level"),
                "reasoning_mode": report.get("reasoning_mode"),
                "input_tokens_observed_calls": report.get("input_tokens_observed_calls"),
                "output_tokens_observed_calls": report.get("output_tokens_observed_calls"),
                "total_tokens_observed_calls": report.get("total_tokens_observed_calls"),
                "cached_input_tokens_observed_calls": report.get("cached_input_tokens_observed_calls"),
                "reasoning_tokens_observed_calls": report.get("reasoning_tokens_observed_calls"),
                "latency_ms": round(report["seconds"] * 1000, 3)
                if report.get("seconds") is not None else None,
                "model_calls": report.get("model_calls"), "sql_calls": report.get("sql_calls"),
                "sql_success_calls": report.get("sql_success_calls"),
                "sql_error_calls": report.get("sql_error_calls"),
                "sql_truncated_calls": report.get("sql_truncated_calls"),
                "agent_sql_execution_ms": report.get("agent_sql_execution_ms")
                if report.get("sql_execution_observed") else None,
                "cost_usd": None,
            })
            original_cli._jsonl_write(traces, {
                "question_id": question["question_id"],
                "question": question.get("question"), "evidence": question.get("evidence"),
                "report": report, "events": output.get("events", []),
                "structured_events": output.get("structured_events", []),
                "graph_events": graph_events,
            })
            print(f"Q{question['question_id']}: "
                  f"{'final_sql_ready' if sql else report.get('stop_reason', 'failed')}", flush=True)
    original_cli._dump(run_dir / "inference_manifest.json", {
        "completed": True, "agent_variant": VARIANT, "outer_graph_version": GRAPH_VERSION,
        "question_ids": [q["question_id"] for q in selected],
        "prediction_sha256": sha256((run_dir / "predictions.jsonl").read_bytes()).hexdigest(),
        "selection_sha256": sha256((folder / "selection_manifest.json").read_bytes()).hexdigest(),
        "dataset_manifest": dataset.manifest,
        "preview_rows": args.preview_rows,
        "agent_sql_timeout_seconds": DEFAULT_SQL_TIMEOUT_SECONDS,
        "output_format_version": b0.OUTPUT_FORMAT_VERSION,
        "parser_revision": "accept-inline-opening-delimiter-v1",
        "trace_schema_version": 1,
        "selection_id": args.selection_id, "split": args.split, "run_id": args.run_id,
        "created_utc": started, "model": model_name, "provider": args.provider,
        "prompt_variant": args.prompt_variant, "system_prompt_sha256": system_sha,
        "requested_reasoning_effort": args.reasoning_effort,
        "temperature": None if args.provider in ("openai", "chatgpt-siwc") else b0.TEMPERATURE,
        "top_p": b0.TOP_P if args.provider == "nvidia" else None,
        "request_timeout_seconds": b0.REQUEST_TIMEOUT,
        "max_output_tokens": None if args.provider == "chatgpt-siwc" else b0.MAX_OUTPUT_TOKENS,
        "max_context_tokens": b0.MAX_CONTEXT_TOKENS if args.provider == "nvidia" else None,
        "context_budget_enforced": False,
        "max_model_calls": b0.MAX_MODEL_CALLS,
        "max_total_tool_calls": b0.MAX_TOTAL_TOOL_CALLS,
        "max_sql_executions": b0.MAX_SQL_EXECUTIONS,
        "recursion_limit": b0.RECURSION_LIMIT,
        "expected_questions": len(selected), "missing_final_sql": missing,
        "usage_schema_version": 2,
        "note": "Usage values remain optional and only reflect provider-observed data; "
                "cached input tokens are included in input tokens; cost unknown.",
    })
    print(f"Saved {len(selected)} predictions ({missing} missing SQL) to {run_dir}", flush=True)
    return 0
