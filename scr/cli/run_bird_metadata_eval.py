"""Independent Metadata Agent BIRD runner, sharing B0 dataset/SQL/scorer contracts.

Prepare selections with the existing B0 'prepare' command. This runner owns
Metadata agent inference, scoring, and trace rendering only.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path

from scr.baselines import bird_b0 as b0
from scr.baselines.common import DEFAULT_MODELS, build_model, redact_credentials
from scr.baselines.sqlite_readonly import ReadOnlySqlite, DEFAULT_SQL_TIMEOUT_SECONDS
from scr.cli import run_bird_b0_eval as base_cli
from scr.datasets.bird import DEFAULT_ROOT
from scr.agents import metadata_agent as agent
from scr.metadata.engine import MetadataEngine
from scr.metadata.resume import audit_partial_run


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def _append_json(stream, data: dict) -> None:
    stream.write(json.dumps(data, ensure_ascii=False, allow_nan=False) + "\n")
    stream.flush()


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _snapshot(experiment_dir: Path) -> str:
    """Deterministic checksum of all note files and indexes, excluding logs."""
    base = experiment_dir / "knowledge"
    digest = sha256()
    for path in sorted(base.rglob("*")):
        if path.is_file():
            digest.update(str(path.relative_to(base)).encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _configure_model(args):
    if args.reasoning_effort is not None and args.provider != "chatgpt-siwc":
        raise ValueError("--reasoning-effort requires --provider chatgpt-siwc")
    model_name = args.model or (b0.MODEL if args.provider == "nvidia"
                                else DEFAULT_MODELS[args.provider])
    if not model_name:
        raise ValueError(f"--model required for {args.provider}")
    if args.provider == "chatgpt-siwc":
        from scr.baselines.siwc_auth import CREDS, read_json
        if not read_json(CREDS):
            raise ValueError("Sign in using scr.baselines.siwc_auth")
    if args.provider == "nvidia" and not os.environ.get("NVIDIA_API_KEY"):
        raise ValueError("NVIDIA_API_KEY required")
    if args.provider == "nvidia" and model_name == b0.MODEL:
        return model_name, None  # Retain the existing NVIDIA model construction.
    return model_name, build_model(
        model_name, provider=args.provider,
        temperature=None if args.provider in ("openai", "chatgpt-siwc") else b0.TEMPERATURE,
        top_p=b0.TOP_P if args.provider == "nvidia" else None,
        max_tokens=b0.MAX_OUTPUT_TOKENS, timeout=b0.REQUEST_TIMEOUT,
        **({"reasoning_effort": args.reasoning_effort}
           if args.reasoning_effort is not None else {}),
    )


def _experiment_settings(args, dataset, model_name: str) -> dict:
    settings = {
        "experiment_id": args.experiment_id,
        "selection_id": args.selection_id,
        "dataset_manifest": dataset.manifest,
        "provider": args.provider,
        "model": model_name,
        "prompt_variant": args.prompt_variant,
        "system_prompt_sha256": sha256(
            agent.system_prompt_for_variant(args.prompt_variant).encode("utf-8")
        ).hexdigest(),
        "requested_reasoning_effort": args.reasoning_effort,
        "preview_rows": args.preview_rows,
        "max_model_calls": b0.MAX_MODEL_CALLS,
        "max_total_tool_calls": b0.MAX_TOTAL_TOOL_CALLS,
        "max_sql_executions": b0.MAX_SQL_EXECUTIONS,
    }
    if args.workflow == "metadata-discovery-v2":
        from scr.agents import metadata_discovery_v2
        from scr.metadata.engine import MAX_DISCOVERY_V2_CONTEXT_CHARS
        settings["workflow"] = args.workflow
        settings["definition_schema_version"] = "table-column-v1"
        settings.update({
            "max_model_calls": metadata_discovery_v2.GLOBAL_MAX_MODEL_CALLS,
            "max_total_tool_calls": metadata_discovery_v2.GLOBAL_MAX_TOTAL_TOOL_CALLS,
            "max_sql_executions": metadata_discovery_v2.GLOBAL_MAX_SQL_EXECUTIONS,
            "max_a1_attempts": metadata_discovery_v2.MAX_A1_ATTEMPTS,
            "max_a1_model_calls_per_attempt": metadata_discovery_v2.A1_MODELS_PER_ATTEMPT,
            "max_a1_tool_calls_per_attempt": metadata_discovery_v2.A1_TOOLS_PER_ATTEMPT,
            "max_a1_sql_calls_per_attempt": metadata_discovery_v2.A1_SQL_PER_ATTEMPT,
            "c1_reserved_model_calls": metadata_discovery_v2.C1_RESERVED_MODEL_CALLS,
            "c1_reserved_tool_calls": metadata_discovery_v2.C1_RESERVED_TOOL_CALLS,
            "c1_reserved_sql_calls": metadata_discovery_v2.C1_RESERVED_SQL_CALLS,
            "metadata_context_chars_per_question": MAX_DISCOVERY_V2_CONTEXT_CHARS,
        })
        settings["workflow_code_sha256"] = sha256(
            Path(metadata_discovery_v2.__file__).read_bytes()).hexdigest()
        settings["discovery_agent_code_sha256"] = sha256(
            Path(agent.__file__).read_bytes()).hexdigest()
        settings["system_prompt_sha256"] = sha256((
            agent.DISCOVERY_PROMPT +
            b0.system_prompt_for_variant(args.prompt_variant) +
            "A1-B1-C1-metadata-discovery-v2"
        ).encode("utf-8")).hexdigest()
    return settings


def _variant(args) -> str:
    return "MetadataDiscoveryV2" if args.workflow == "metadata-discovery-v2" else "Metadata"


def infer(args) -> int:
    folder, dataset, questions = base_cli._selection(args)
    model_name, model = _configure_model(args)
    selected_manifest = _hash(folder / "selection_manifest.json")
    variant = _variant(args)
    experiment_dir = folder / variant / "experiments" / args.experiment_id
    experiment_file = experiment_dir / "experiment_manifest.json"
    run_dir = folder / variant / args.split / args.run_id
    expected = _experiment_settings(args, dataset, model_name)
    expected["selection_sha256"] = selected_manifest

    completed_ids, failures, corrections = [], 0, []
    if args.resume:
        if not run_dir.is_dir() or not experiment_file.is_file():
            raise ValueError("Resume requires an existing partial run and experiment")
        settings = json.loads(experiment_file.read_text(encoding="utf-8"))
        if any(settings.get(k) != v for k, v in expected.items()):
            raise ValueError("Experiment configuration changed; refusing resume")
        if settings.get(f"{args.split}_completed"):
            raise ValueError("This split already completed")
        if args.split == "test" and not settings.get("dev_completed"):
            raise ValueError("Test requires completed Dev inference")
        known_run = settings.get(f"{args.split}_run_id")
        if known_run is not None and known_run != args.run_id:
            raise ValueError("Different run ID already owns this experiment's split")
        dev_ids = set()
        if args.split == "test":
            dev_rows = [
                json.loads(line) for line in
                (folder / "dev.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            dev_ids = {r["question_id"] for r in dev_rows}
        completed_ids, failures, corrections = audit_partial_run(
            folder, experiment_dir, run_dir, questions, split=args.split,
            provider=args.provider, model_name=model_name, previous_dev_ids=dev_ids)
        if corrections:
            corrections_path = run_dir / "trace_model_corrections.jsonl"
            correction_text = "".join(
                json.dumps(row, ensure_ascii=False) + "\n" for row in corrections
            )
            if corrections_path.exists():
                if corrections_path.read_text(encoding="utf-8") != correction_text:
                    raise ValueError("Existing model-label correction audit differs")
            else:
                # Add an audit sidecar; NEVER rewrite historical trace records.
                with corrections_path.open("x", encoding="utf-8") as audit_file:
                    audit_file.write(correction_text)
        print(f"Safe resume verified: {len(completed_ids)} completed questions; "
              f"continuing at position {len(completed_ids) + 1}", flush=True)
    else:
        if run_dir.exists():
            raise ValueError(f"Refusing to overwrite inference run: {run_dir}")
        if args.split == "dev":
            if experiment_dir.exists():
                raise ValueError("Experiment already exists; use a fresh experiment ID")
            experiment_dir.mkdir(parents=True)
            settings = {**expected, "created_utc": datetime.now(timezone.utc).isoformat(),
                        "dev_completed": False, "test_completed": False}
        else:
            if not experiment_file.is_file():
                raise ValueError("Run Dev first with this experiment ID")
            settings = json.loads(experiment_file.read_text(encoding="utf-8"))
            if any(settings.get(k) != v for k, v in expected.items()):
                raise ValueError("Test configuration differs from Dev experiment")
            if not settings.get("dev_completed") or settings.get("test_completed"):
                raise ValueError("Dev inference must be completed and Test not repeated")
        settings[f"{args.split}_run_id"] = args.run_id
        settings[f"{args.split}_started_utc"] = datetime.now(timezone.utc).isoformat()
        settings[f"{args.split}_knowledge_sha256_before"] = _snapshot(experiment_dir)
        _write_json(experiment_file, settings)
        run_dir.mkdir(parents=True)

    # Legacy partial Dev runs have no initial hash recorded, but begin empty.
    # Legacy partial Test runs began with the last completed Dev knowledge hash.
    initial_default = (sha256(b"").hexdigest() if args.split == "dev"
                       else settings.get("dev_knowledge_sha256", _snapshot(experiment_dir)))
    before = settings.get(f"{args.split}_knowledge_sha256_before", initial_default)
    started = settings.get(f"{args.split}_started_utc") or datetime.now(timezone.utc).isoformat()
    question_ids = list(completed_ids)
    file_mode = "a" if args.resume else "w"
    with (run_dir / "predictions.jsonl").open(file_mode, encoding="utf-8") as predictions, \
         (run_dir / "traces.jsonl").open(file_mode, encoding="utf-8") as traces:
        for question in questions[len(completed_ids):]:
            qid, db_id = question["question_id"], question["db_id"]
            question_ids.append(qid)
            messages, events = [], []
            try:
                sql_store = ReadOnlySqlite(
                    dataset.get_database_path(db_id), max_rows=args.preview_rows)
                notes = MetadataEngine(
                    experiment_dir, db_id, qid, schema=dataset.get_schema(db_id),
                    descriptions=dataset.get_descriptions(db_id),
                    definition_mode=(args.workflow == "metadata-discovery-v2"),
                )
                if args.workflow == "metadata-discovery-v2":
                    from scr.agents.metadata_discovery_v2 import build_workflow
                    active = build_workflow(
                        sql_store, notes, model, model_name,
                        prompt_variant=args.prompt_variant,
                    )
                    result = active.run_one(
                        question,
                        log=lambda message: messages.append(
                            redact_credentials(str(message))),
                        trace_events=events,
                    )
                else:
                    active = agent.make_agent(
                        sql_store, notes, model=model,
                        prompt_variant=args.prompt_variant,
                    )
                    result = agent.run_one(
                        question, active,
                        log=lambda message: messages.append(
                            redact_credentials(str(message))),
                        trace_events=events,
                    )
            except Exception as exc:
                result = {
                    "final_sql": None, "graph_completed": False, "model_calls": 0,
                    "tool_calls": 0, "sql_calls": 0, "usage_observed": False,
                    "seconds": None, "stop_reason": type(exc).__name__,
                    "error": redact_credentials(f"{type(exc).__name__}: {exc}"),
                }
            # b0.run_one() defaults to B0's NVIDIA constant in its report.
            # The real provider/model was selected in _configure_model above.
            result["model"] = model_name
            final_sql = result.get("final_sql") if result.get("graph_completed") else None
            failures += int(final_sql is None)
            row = {
                "question_id": qid, "db_id": db_id,
                "predicted_sql": final_sql, "provider": args.provider,
                "model": model_name, "requested_reasoning_effort": args.reasoning_effort,
                "cost_usd": None,
                "latency_ms": round(result["seconds"] * 1000, 3)
                              if result.get("seconds") is not None else None,
            }
            for key in (
                "tool_calls", "model_calls", "sql_calls", "sql_success_calls",
                "sql_error_calls", "sql_truncated_calls", "agent_sql_execution_ms",
                "total_tokens", "cached_input_tokens", "reasoning_tokens",
                "reasoning_effort", "thinking_level", "reasoning_mode",
                "input_tokens_observed_calls", "output_tokens_observed_calls",
                "total_tokens_observed_calls", "cached_input_tokens_observed_calls",
                "reasoning_tokens_observed_calls",
                "a1_attempts", "b1_evaluations",
            ):
                row[key] = result.get(key)
            row["input_tokens"] = (result.get("input_tokens")
                                   if result.get("usage_observed") else None)
            row["output_tokens"] = (result.get("output_tokens")
                                    if result.get("usage_observed") else None)
            _append_json(predictions, row)
            _append_json(traces, {
                "question_id": qid, "question": question.get("question"),
                "evidence": question.get("evidence"), "report": result,
                "events": messages, "structured_events": events,
            })
            print(f"Q{qid}: {'final_sql_ready' if final_sql else result.get('stop_reason')}",
                  flush=True)
    output_manifest = {
        **expected, "agent_variant": variant, "run_id": args.run_id,
        "split": args.split, "created_utc": started,
        "question_ids": question_ids, "expected_questions": len(questions),
        "completed": True, "missing_final_sql": failures,
        "prediction_sha256": _hash(run_dir / "predictions.jsonl"),
        "selection_sha256": selected_manifest,
        "knowledge_sha256_before": before,
        "knowledge_sha256_after": _snapshot(experiment_dir),
        "output_format_version": b0.OUTPUT_FORMAT_VERSION,
        "agent_sql_timeout_seconds": DEFAULT_SQL_TIMEOUT_SECONDS,
        "trace_schema_version": 1, "usage_schema_version": 2,
        "resumed_from_questions": len(completed_ids),
        "historical_trace_model_corrections": len(corrections),
        "knowledge_policy": "continual same-database notes; Dev and Test share writable store",
        **({"workflow": "metadata-discovery-v2", "definition_schema_version": "table-column-v1"}
           if args.workflow == "metadata-discovery-v2" else {}),
    }
    _write_json(run_dir / "inference_manifest.json", output_manifest)
    settings[f"{args.split}_completed"] = True
    settings[f"{args.split}_run_id"] = args.run_id
    settings[f"{args.split}_knowledge_sha256"] = output_manifest["knowledge_sha256_after"]
    _write_json(experiment_file, settings)
    print(f"{variant} {args.split}: {len(questions)} predictions; {failures} missing SQL")
    return 0


def score(args) -> int:
    from scr.cli.evaluate_bird import run as evaluate
    from scr.evaluation.bird import load_predictions, validate_predictions
    folder, dataset, selected = base_cli._selection(args)
    variant = _variant(args)
    run_dir = folder / variant / args.split / args.run_id
    manifest_path, predictions_path = (run_dir / "inference_manifest.json",
                                       run_dir / "predictions.jsonl")
    if not manifest_path.is_file() or not predictions_path.is_file():
        raise ValueError("Metadata inference predictions/manifest required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    predictions = load_predictions(predictions_path)
    validate_predictions(predictions, selected)
    required = {
        "agent_variant": variant, "completed": True,
        "run_id": args.run_id, "split": args.split,
        "selection_id": args.selection_id,
        "selection_sha256": _hash(folder / "selection_manifest.json"),
        "dataset_manifest": dataset.manifest,
        "question_ids": [row["question_id"] for row in selected],
        "expected_questions": len(selected),
        "prediction_sha256": _hash(predictions_path),
    }
    if len(predictions) != len(selected) or any(manifest.get(k) != v
                                                for k, v in required.items()):
        raise ValueError("Incomplete or mismatched Metadata inference")
    if any(row.get("model") != manifest["model"] or
           row.get("provider") != manifest["provider"] for row in predictions):
        raise ValueError("Predictions do not match inference provider/model")
    if (run_dir / "scores").exists():
        raise ValueError("Metadata scores already exist")
    outcome = evaluate([
        "--variant", variant, "--split", args.split,
        "--predictions", str(predictions_path),
        "--dataset-root", str(args.dataset_root),
        "--output-dir", str(run_dir), "--run-id", "scores",
        "--question-ids", ",".join(str(q["question_id"]) for q in selected),
        "--timeout-seconds", str(args.timeout_seconds),
    ])
    if outcome == 0:
        summary = json.loads((run_dir / "scores" / "summary.json").read_text(encoding="utf-8"))
        (run_dir / "scores" / "report.md").write_text(
            f"# {variant} Agent — {args.split} results\n\n"
            f"EX: **{summary['correct']}/{summary['total']} ({summary['ex']:.2%})**\n\n"
            "This is a local same-database continual-knowledge evaluation; "
            "not an official hidden test.\n",
            encoding="utf-8")
    return outcome


def visualize(args) -> int:
    from scr.tracing.viewer import write_html
    directory = args.result_root / args.selection_id / _variant(args) / args.split
    paths = [directory / rid for rid in args.run_id]
    output = args.output or (paths[0] / "trace-explorer.html" if len(paths) == 1
                             else directory / "trace-explorer-combined.html")
    print("Trace Explorer:", write_html(paths, output))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Independent KORA Metadata Agent evaluation")
    sub = root.add_subparsers(dest="action", required=True)
    for action in ("infer", "score", "visualize"):
        cmd = sub.add_parser(action)
        cmd.add_argument("--selection-id", required=True)
        cmd.add_argument("--dataset-root", type=Path, default=DEFAULT_ROOT)
        cmd.add_argument("--result-root", type=Path, default=base_cli.DEFAULT_RESULT_ROOT)
        cmd.add_argument("--split", required=True, choices=("dev", "test"))
        cmd.add_argument("--workflow", choices=("v1", "metadata-discovery-v2"), default="v1",
                         help="v1 remains unchanged; metadata-discovery-v2 uses A1/B1/C1 and a separate store")
        cmd.add_argument("--run-id", required=True,
                         nargs="+" if action == "visualize" else None)
        if action == "infer":
            cmd.add_argument("--experiment-id", required=True)
            cmd.add_argument("--resume", action="store_true",
                             help="Audit and append to a partial run without rerunning completed questions")
            cmd.add_argument("--prompt-variant", default="generalized-v1",
                             choices=b0.PROMPT_VARIANTS)
            cmd.add_argument("--provider", default="nvidia", choices=DEFAULT_MODELS)
            cmd.add_argument("--model")
            cmd.add_argument("--reasoning-effort",
                             choices=("none", "low", "medium", "high", "xhigh", "max"))
            cmd.add_argument("--preview-rows", type=int, default=20)
        elif action == "score":
            cmd.add_argument("--timeout-seconds", type=float,
                             default=DEFAULT_SQL_TIMEOUT_SECONDS)
        else:
            cmd.add_argument("--output", type=Path)
    return root


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    for name in ("selection_id", "experiment_id", "run_id"):
        value = getattr(args, name, None)
        if value is not None:
            for item in value if isinstance(value, list) else [value]:
                if not base_cli.SAFE_ID.fullmatch(item):
                    raise ValueError(f"Unsafe {name}: {item!r}")
    if args.action == "infer" and not 1 <= args.preview_rows <= 200:
        raise ValueError("--preview-rows must be 1..200")
    if args.action == "score" and args.timeout_seconds <= 0:
        raise ValueError("--timeout-seconds must be positive")
    return {"infer": infer, "score": score, "visualize": visualize}[args.action](args)


if __name__ == "__main__":
    raise SystemExit(main())
