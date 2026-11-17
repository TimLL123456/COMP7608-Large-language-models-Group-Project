"""Independent BIRD SelfReflection runner; does not modify or wrap B0 CLI runs.

Prepare selections with: python -m scr.cli.run_bird_b0_eval prepare ...
This runner supports infer, score, compare and visualize.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

from langgraph_agents.self_reflection.graph import LangGraphSelfReflectionAgent as SelfReflectionAgent
from scr.agents.sql_reflection_reviewer import SQLReflectionReviewer, PROMPT_FILE, PROMPT_VERSION
from scr.baselines import bird_b0 as b0
from scr.baselines.common import DEFAULT_MODELS, build_model, redact_credentials
from scr.baselines.sqlite_readonly import ReadOnlySqlite, DEFAULT_SQL_TIMEOUT_SECONDS
from scr.cli import run_bird_b0_eval as base_cli
from scr.datasets.bird import DEFAULT_ROOT

VARIANT = "LangGraphSelfReflection"


def _sha(path: Path):
    return sha256(path.read_bytes()).hexdigest()


def _write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False,
                                    allow_nan=False) + "\n", encoding="utf-8")


def _append(file, value):
    file.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
    file.flush()


def _run_dir(args):
    return args.result_root / args.selection_id / VARIANT / args.split / args.run_id


def _configure_model(args):
    if args.reasoning_effort is not None and args.provider != "chatgpt-siwc":
        raise ValueError("--reasoning-effort requires --provider chatgpt-siwc")
    name = args.model or (b0.MODEL if args.provider == "nvidia"
                          else DEFAULT_MODELS[args.provider])
    if not name:
        raise ValueError(f"--model required for provider {args.provider}")
    if args.provider == "nvidia" and not os.environ.get("NVIDIA_API_KEY"):
        raise ValueError("NVIDIA_API_KEY required; no implicit fallback")
    if args.provider == "chatgpt-siwc":
        from scr.baselines.siwc_auth import CREDS, read_json
        if not read_json(CREDS):
            raise ValueError("Sign in using scr.baselines.siwc_auth first")
    options = dict(
        provider=args.provider,
        temperature=None if args.provider in ("openai", "chatgpt-siwc") else b0.TEMPERATURE,
        top_p=b0.TOP_P if args.provider == "nvidia" else None,
        max_tokens=b0.MAX_OUTPUT_TOKENS, timeout=b0.REQUEST_TIMEOUT,
    )
    if args.reasoning_effort is not None:
        options["reasoning_effort"] = args.reasoning_effort
    reviewer_model = build_model(name, **options)
    # Keep original B0 NVIDIA default construction exactly as in the historical runner.
    b0_model = None if (args.provider == "nvidia" and name == b0.MODEL) else reviewer_model
    return name, b0_model, reviewer_model


def _source_revision():
    try:
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                capture_output=True, text=True, timeout=2, check=True)
        return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def infer(args):
    folder, dataset, selected = base_cli._selection(args)
    b0.system_prompt_for_variant(args.prompt_variant)
    model_name, b0_model, reviewer_model = _configure_model(args)
    run_dir = _run_dir(args)
    if run_dir.exists() or run_dir.is_symlink():
        raise ValueError(f"Refusing to overwrite: {run_dir}")
    reviewer = SQLReflectionReviewer(reviewer_model,
                                    max_model_calls=args.max_review_model_calls,
                                    max_inspections=args.max_inspections)
    coordinator = SelfReflectionAgent(
        reviewer, model=b0_model, finalizer_model=reviewer_model,
        prompt_variant=args.prompt_variant,
        max_attempts=args.max_attempts,
        max_total_model_calls=args.max_total_model_calls,
        max_total_tool_calls=args.max_total_tool_calls,
        max_total_sql_calls=args.max_total_sql_calls,
    )
    run_dir.mkdir(parents=True)
    (run_dir / "reviews").mkdir()
    created = datetime.now(timezone.utc).isoformat()
    missing = 0
    with (run_dir / "predictions.jsonl").open("x", encoding="utf-8") as predictions, \
         (run_dir / "traces.jsonl").open("x", encoding="utf-8") as traces, \
         (run_dir / "reviews" / "reflection_decisions.jsonl").open("x", encoding="utf-8") as decisions:
        for question in selected:
            try:
                store = ReadOnlySqlite(dataset.get_database_path(question["db_id"]),
                                       max_rows=args.preview_rows)
                result = coordinator.run(question, store)
                report = result["report"]
                sql = result["final_sql"]
            except Exception as exc:
                report = dict(final_sql=None, graph_completed=False,
                              model_calls=0, tool_calls=0, sql_calls=0,
                              stop_reason=type(exc).__name__, review_status="ERROR",
                              error=redact_credentials(f"{type(exc).__name__}: {exc}"))
                sql = None
                result = dict(report=report, attempts=[], structured_events=[],
                              b0_usage={}, reviewer_usage={}, review_status="ERROR",
                              stop_reason=report["stop_reason"])
            missing += int(sql is None)
            report["model"] = model_name
            row = {
                "question_id": question["question_id"], "db_id": question["db_id"],
                "predicted_sql": sql, "provider": args.provider, "model": model_name,
                "model_calls": report.get("model_calls"),
                "tool_calls": report.get("tool_calls"), "sql_calls": report.get("sql_calls"),
                "latency_ms": round(report["seconds"] * 1000, 3)
                if report.get("seconds") is not None else None,
                "cost_usd": None,
                "output_status": report.get("output_status"),
                "review_status": report.get("review_status"),
            }
            for key in ("input_tokens", "output_tokens", "total_tokens",
                        "cached_input_tokens", "reasoning_tokens"):
                row[key] = report.get(key)
            row["reasoning_effort"] = args.reasoning_effort
            _append(predictions, row)
            _append(traces, {
                "question_id": question["question_id"], "question": question.get("question"),
                "evidence": question.get("evidence"), "report": report,
                "structured_events": result["structured_events"],
                "graph_events": result.get("graph_events", []),
                "attempts": result["attempts"],
            })
            _append(decisions, {
                "question_id": question["question_id"],
                "review_status": result["review_status"], "stop_reason": result["stop_reason"],
                "output_status": report.get("output_status"),
                "finalization_triggered": report.get("finalization_triggered"),
                "b0_usage": result["b0_usage"], "reviewer_usage": result["reviewer_usage"],
                "decisions": [{"attempt": attempt["attempt"],
                               "candidate_sql": attempt["candidate_sql"],
                               "review": attempt["review"]}
                              for attempt in result["attempts"]],
            })
            print(f"Q{question['question_id']}: {result['review_status']} "
                  f"({result['stop_reason']})", flush=True)
    _write_json(run_dir / "inference_manifest.json", {
        "agent_variant": VARIANT, "completed": True,
        "outer_graph_version": "self_reflection-v1",
        "selection_id": args.selection_id, "split": args.split, "run_id": args.run_id,
        "created_utc": created, "dataset_manifest": dataset.manifest,
        "selection_sha256": _sha(folder / "selection_manifest.json"),
        "question_ids": [q["question_id"] for q in selected],
        "expected_questions": len(selected), "missing_final_sql": missing,
        "prediction_sha256": _sha(run_dir / "predictions.jsonl"),
        "trace_sha256": _sha(run_dir / "traces.jsonl"),
        "review_decisions_sha256": _sha(run_dir / "reviews" / "reflection_decisions.jsonl"),
        "provider": args.provider, "model": model_name,
        "requested_reasoning_effort": args.reasoning_effort,
        "prompt_variant": args.prompt_variant,
        "b0_prompt_sha256": sha256(b0.system_prompt_for_variant(
            args.prompt_variant).encode("utf-8")).hexdigest(),
        "reviewer_prompt_version": PROMPT_VERSION, "reviewer_prompt_sha256": _sha(PROMPT_FILE),
        "source_revision": _source_revision(),
        "max_attempts": args.max_attempts,
        "max_review_model_calls": args.max_review_model_calls,
        "max_inspections": args.max_inspections,
        "max_total_model_calls": args.max_total_model_calls,
        "max_total_tool_calls": args.max_total_tool_calls,
        "max_total_sql_calls": args.max_total_sql_calls,
        "b0_max_model_calls_per_attempt": b0.MAX_MODEL_CALLS,
        "b0_investigation_model_calls": b0.MAX_MODEL_CALLS - 1,
        "b0_investigation_tool_calls": b0.MAX_TOTAL_TOOL_CALLS - 1,
        "reserved_b0_finalization_model_calls": 1,
        "reserved_review_finalization_model_calls": 1,
        "b0_max_tool_calls_per_attempt": b0.MAX_TOTAL_TOOL_CALLS,
        "b0_max_sql_calls_per_attempt": b0.MAX_SQL_EXECUTIONS,
        "preview_rows": args.preview_rows,
        "output_format_version": b0.OUTPUT_FORMAT_VERSION,
        "trace_schema_version": 1,
        "note": "All usage is observed only; incomplete nested/provider failures may be undercounted. "
                "Gold references are offline evaluator only. Reviewer PASS is provisional. "
                "Standalone B0 defaults are unchanged; this workflow reserves finalization "
                "capacity. SQL output and review PASS are separate outcomes.",
    })
    print(f"{VARIANT}: {len(selected)} predictions, {missing} missing SQL: {run_dir}")
    return 0


def _verified_run(args):
    from scr.evaluation.bird import load_predictions, validate_predictions
    folder, dataset, selected = base_cli._selection(args)
    run_dir = _run_dir(args)
    pred_path = run_dir / "predictions.jsonl"
    manifest_path = run_dir / "inference_manifest.json"
    if not pred_path.is_file() or not manifest_path.is_file():
        raise ValueError(f"Missing predictions or inference manifest: {run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    predictions = load_predictions(pred_path)
    validate_predictions(predictions, selected)
    required = {
        "agent_variant": VARIANT, "completed": True,
        "selection_id": args.selection_id, "run_id": args.run_id,
        "split": args.split, "dataset_manifest": dataset.manifest,
        "question_ids": [q["question_id"] for q in selected],
        "expected_questions": len(selected),
        "selection_sha256": _sha(folder / "selection_manifest.json"),
        "prediction_sha256": _sha(pred_path),
    }
    if len(predictions) != len(selected) or any(manifest.get(k) != v for k, v in required.items()):
        raise ValueError("Invalid SelfReflection inference provenance")
    for field in ("provider", "model"):
        if not manifest.get(field) or any(row.get(field) != manifest[field] for row in predictions):
            raise ValueError(f"Prediction {field} does not match inference manifest")
    return run_dir, manifest, predictions, selected


def score(args):
    from scr.cli.evaluate_bird import run as evaluate
    run_dir, _manifest, _predictions, selected = _verified_run(args)
    if (run_dir / "scores").exists():
        raise ValueError("Refusing to overwrite existing scores")
    result = evaluate([
        "--variant", VARIANT, "--split", args.split,
        "--predictions", str(run_dir / "predictions.jsonl"),
        "--dataset-root", str(args.dataset_root),
        "--output-dir", str(run_dir), "--run-id", "scores",
        "--question-ids", ",".join(str(q["question_id"]) for q in selected),
        "--timeout-seconds", str(args.timeout_seconds),
    ])
    if result == 0:
        summary = json.loads((run_dir / "scores" / "summary.json").read_text(encoding="utf-8"))
        (run_dir / "scores" / "report.md").write_text(
            f"# {VARIANT} — independent EX scoring\n\n"
            f"Split: {args.split}; selected questions: {summary['total']}\n\n"
            f"EX: **{summary['correct']}/{summary['total']} ({summary['ex']:.2%})**\n\n"
            "These are local BIRD Mini-Dev scores, not an official hidden-test result. "
            "Reviewer PASS is not the EX label.\n", encoding="utf-8")
    return result


def compare(args):
    run_dir, manifest, _, questions = _verified_run(args)
    baseline_dir = (args.result_root / args.selection_id / "B0" / args.split
                    / args.baseline_run_id)
    if not (baseline_dir / "scores" / "per_question.jsonl").is_file():
        raise ValueError("Scored B0 baseline run required for compare")
    if not (run_dir / "scores" / "per_question.jsonl").is_file():
        raise ValueError("Score SelfReflection first")
    baseline_manifest_path = baseline_dir / "inference_manifest.json"
    if not baseline_manifest_path.is_file():
        raise ValueError("B0 inference manifest required")
    control = json.loads(baseline_manifest_path.read_text(encoding="utf-8"))
    for key in ("dataset_manifest", "selection_sha256", "question_ids", "provider", "model",
                "prompt_variant", "requested_reasoning_effort"):
        expected = (manifest["b0_prompt_sha256"] if key == "b0_prompt_sha256" else
                    manifest.get(key))
        if control.get(key) != expected:
            raise ValueError(f"Cannot compare runs with different {key}")
    if control.get("system_prompt_sha256") != manifest.get("b0_prompt_sha256"):
        raise ValueError("Baseline prompt hash differs")
    def load(path):
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()]
        return {r["question_id"]: r for r in rows}
    base = load(baseline_dir / "scores" / "per_question.jsonl")
    variant = load(run_dir / "scores" / "per_question.jsonl")
    ids = {q["question_id"] for q in questions}
    if set(base) != ids or set(variant) != ids:
        raise ValueError("Paired scores do not cover the same selected questions")
    fixed = sorted(qid for qid in ids if not base[qid]["ex"] and variant[qid]["ex"])
    regressed = sorted(qid for qid in ids if base[qid]["ex"] and not variant[qid]["ex"])
    b0_correct = sum(bool(base[qid]["ex"]) for qid in ids)
    new_correct = sum(bool(variant[qid]["ex"]) for qid in ids)
    report = ("# B0 vs SelfReflection — Paired EX Comparison\n\n"
              f"Dataset: {args.selection_id}; split: {args.split}; total: {len(ids)}\n\n"
              f"B0: **{b0_correct}/{len(ids)}**; SelfReflection: **{new_correct}/{len(ids)}**; "
              f"delta **{(new_correct-b0_correct)/len(ids)*100:+.2f} percentage points**.\n\n"
              f"Corrected: **{len(fixed)}**; regressed: **{len(regressed)}**.\n\n"
              "**Interpretation:** The reflection workflow has additional computation; "
              "this is not a matched-compute causal result.\n\n"
              f"Corrected question IDs: {fixed}\n\nRegressed question IDs: {regressed}\n")
    output = run_dir / "comparison_report.md"
    if output.exists():
        raise ValueError("Comparison report exists; refusing overwrite")
    output.write_text(report, encoding="utf-8")
    print(report)
    return 0


def visualize(args):
    from scr.tracing.viewer import write_html
    path = _run_dir(args)
    output = args.output or path / "trace-explorer.html"
    print("Trace Explorer:", write_html([path], output))
    return 0


def parser():
    result = argparse.ArgumentParser(description="LangGraphSelfReflection evaluation")
    sub = result.add_subparsers(dest="action", required=True)
    for name in ("infer", "score", "compare", "visualize"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--selection-id", required=True)
        cmd.add_argument("--dataset-root", type=Path, default=DEFAULT_ROOT)
        cmd.add_argument("--result-root", type=Path, default=base_cli.DEFAULT_RESULT_ROOT)
        cmd.add_argument("--split", required=True, choices=("dev", "test"))
        cmd.add_argument("--run-id", required=True)
        if name == "infer":
            cmd.add_argument("--provider", choices=DEFAULT_MODELS, default="nvidia")
            cmd.add_argument("--model")
            cmd.add_argument("--reasoning-effort", choices=(
                "none", "low", "medium", "high", "xhigh", "max"))
            cmd.add_argument("--prompt-variant", choices=b0.PROMPT_VARIANTS, default="baseline")
            cmd.add_argument("--preview-rows", type=int, default=20)
            cmd.add_argument("--max-attempts", type=int, default=3)
            cmd.add_argument("--max-review-model-calls", type=int, default=40)
            cmd.add_argument("--max-inspections", type=int, default=39)
            cmd.add_argument("--max-total-model-calls", type=int, default=240)
            cmd.add_argument("--max-total-tool-calls", type=int, default=240)
            cmd.add_argument("--max-total-sql-calls", type=int, default=240)
        elif name == "score":
            cmd.add_argument("--timeout-seconds", type=float, default=DEFAULT_SQL_TIMEOUT_SECONDS)
        elif name == "compare":
            cmd.add_argument("--baseline-run-id", required=True)
        elif name == "visualize":
            cmd.add_argument("--output", type=Path)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    for key in ("selection_id", "run_id", "baseline_run_id"):
        value = getattr(args, key, None)
        if value is not None and not base_cli.SAFE_ID.fullmatch(value):
            raise ValueError(f"Unsafe {key}: {value!r}")
    if args.action == "infer":
        if not 1 <= args.preview_rows <= 200 or not 1 <= args.max_attempts <= 10:
            raise ValueError("Invalid preview/attempt budget")
        if not 1 <= args.max_review_model_calls <= 40 or not 0 <= args.max_inspections <= 39:
            raise ValueError("Invalid reviewer budget")
        if min(args.max_total_model_calls, args.max_total_tool_calls,
               args.max_total_sql_calls) < 1:
            raise ValueError("Global budgets must be positive")
    if args.action == "score" and args.timeout_seconds <= 0:
        raise ValueError("Scoring timeout must be positive")
    return {"infer": infer, "score": score, "compare": compare,
            "visualize": visualize}[args.action](args)


if __name__ == "__main__":
    raise SystemExit(main())
