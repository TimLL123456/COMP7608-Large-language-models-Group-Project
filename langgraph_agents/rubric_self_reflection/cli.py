"""Independent BIRD Mini-Dev runner for RubricSelfReflection.

Usage: python -m scr.agents.rubric_self_reflection.cli {infer,score,compare,visualize}
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

from scr.baselines import bird_b0 as b0
from scr.baselines.common import DEFAULT_MODELS, build_model, redact_credentials
from scr.baselines.sqlite_readonly import ReadOnlySqlite, DEFAULT_SQL_TIMEOUT_SECONDS
from scr.cli import run_bird_b0_eval as base_cli
from scr.datasets.bird import DEFAULT_ROOT
from langgraph_agents.rubric_self_reflection.graph import LangGraphRubricSelfReflectionAgent as RubricSelfReflectionAgent
from scr.agents.rubric_self_reflection.reviewer import RubricReviewer, REVIEW_PROMPT, PROMPT_VERSION
from scr.agents.rubric_self_reflection.finalizer import FINAL_PROMPT, FINAL_PROMPT_VERSION

VARIANT = "LangGraphRubricSelfReflection"


def _sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False,
                                    allow_nan=False) + "\n", encoding="utf-8")


def _append(file, value):
    file.write(json.dumps(value, ensure_ascii=False, default=str, allow_nan=False) + "\n")
    file.flush()


def _run_dir(args):
    return args.result_root / args.selection_id / VARIANT / args.split / args.run_id


def _configure_model(args):
    if args.reasoning_effort is not None and args.provider != "chatgpt-siwc":
        raise ValueError("--reasoning-effort requires chatgpt-siwc")
    name = args.model or (b0.MODEL if args.provider == "nvidia" else DEFAULT_MODELS[args.provider])
    if not name:
        raise ValueError("--model is required")
    if args.provider == "nvidia" and not os.environ.get("NVIDIA_API_KEY"):
        raise ValueError("NVIDIA_API_KEY required")
    if args.provider == "chatgpt-siwc":
        from scr.baselines.siwc_auth import CREDS, read_json
        if not read_json(CREDS):
            raise ValueError("Sign in using scr.baselines.siwc_auth first")
    options = {"provider": args.provider,
               "temperature": None if args.provider in ("openai", "chatgpt-siwc") else b0.TEMPERATURE,
               "top_p": b0.TOP_P if args.provider == "nvidia" else None,
               "max_tokens": b0.MAX_OUTPUT_TOKENS, "timeout": b0.REQUEST_TIMEOUT}
    if args.reasoning_effort is not None:
        options["reasoning_effort"] = args.reasoning_effort
    model = build_model(name, **options)
    b0_model = None if args.provider == "nvidia" and name == b0.MODEL else model
    return name, b0_model, model


def _revision():
    try:
        run = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, check=True, timeout=3,
                             cwd=Path(__file__).resolve().parents[3])
        return run.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def infer(args):
    folder, dataset, selected = base_cli._selection(args)
    b0.system_prompt_for_variant(args.prompt_variant)
    model_name, b0_model, reviewer_model = _configure_model(args)
    run_dir = _run_dir(args)
    if run_dir.exists() or run_dir.is_symlink():
        raise ValueError(f"Refusing to overwrite existing run: {run_dir}")
    reviewer = RubricReviewer(reviewer_model,
                            max_model_calls=args.max_review_model_calls,
                            max_inspections=args.max_inspections)
    coordinator = RubricSelfReflectionAgent(
        reviewer, model=b0_model, finalizer_model=reviewer_model,
        prompt_variant=args.prompt_variant, max_attempts=args.max_attempts,
        max_total_model_calls=args.max_total_model_calls,
        max_total_tool_calls=args.max_total_tool_calls,
        max_total_sql_calls=args.max_total_sql_calls)
    run_dir.mkdir(parents=True)
    (run_dir / "reviews").mkdir()
    missing = 0
    created = datetime.now(timezone.utc).isoformat()
    with (run_dir / "predictions.jsonl").open("x", encoding="utf-8") as predictions, \
         (run_dir / "traces.jsonl").open("x", encoding="utf-8") as traces, \
         (run_dir / "reviews" / "rubric_decisions.jsonl").open("x", encoding="utf-8") as decisions:
        for question in selected:
            try:
                store = ReadOnlySqlite(dataset.get_database_path(question["db_id"]),
                                       max_rows=args.preview_rows)
                result = coordinator.run(question, store)
                report, sql = result["report"], result["final_sql"]
            except Exception as exc:
                sql = None
                report = {"question_id": question["question_id"], "db_id": question["db_id"],
                          "graph_completed": False, "output_status": "missing", "review_status": "ERROR",
                          "stop_reason": type(exc).__name__,
                          "error": redact_credentials(f"{type(exc).__name__}: {exc}")[:500]}
                result = {"report": report, "extraction": {}, "attempts": [], "refinement": {},
                          "structured_events": [], "b0_usage": {}, "reviewer_usage": {},
                          "refinement_usage": {}, "review_status": "ERROR",
                          "stop_reason": report["stop_reason"]}
            missing += int(sql is None)
            report["model"] = model_name
            prediction = {"question_id": question["question_id"], "db_id": question["db_id"],
                          "predicted_sql": sql, "provider": args.provider, "model": model_name,
                          "reasoning_effort": args.reasoning_effort, "cost_usd": None,
                          "output_status": report.get("output_status"),
                          "review_status": report.get("review_status"),
                          "latency_ms": round(report["seconds"] * 1000, 3)
                          if report.get("seconds") is not None else None}
            for key in ("model_calls", "tool_calls", "sql_calls", "input_tokens", "output_tokens",
                        "total_tokens", "cached_input_tokens", "reasoning_tokens"):
                prediction[key] = report.get(key)
            _append(predictions, prediction)
            _append(traces, {"question_id": question["question_id"],
                             "question": question.get("question"), "evidence": question.get("evidence"),
                             "report": report, "structured_events": result["structured_events"],
                "graph_events": result.get("graph_events", []),
                             "extraction": result["extraction"], "attempts": result["attempts"],
                             "refinement": result["refinement"]})
            _append(decisions, {"question_id": question["question_id"],
                                "extraction": result["extraction"],
                                "attempts": [{"attempt": a["attempt"],
                                              "candidate_sql": a["candidate_sql"],
                                              "review": a["review"]} for a in result["attempts"]],
                                "refinement": result["refinement"],
                                "final_sql": sql, "review_status": result["review_status"],
                                "stop_reason": result["stop_reason"],
                                "b0_usage": result["b0_usage"],
                                "reviewer_usage": result["reviewer_usage"],
                                "refinement_usage": result["refinement_usage"]})
            print(f"Q{question['question_id']}: {result['review_status']} "
                  f"({result['stop_reason']})", flush=True)
    _write_json(run_dir / "inference_manifest.json", {
        "agent_variant": VARIANT, "completed": True,
        "outer_graph_version": "rubric_self_reflection-v1",
        "selection_id": args.selection_id, "split": args.split, "run_id": args.run_id,
        "created_utc": created, "dataset_manifest": dataset.manifest,
        "selection_sha256": _sha(folder / "selection_manifest.json"),
        "question_ids": [q["question_id"] for q in selected],
        "expected_questions": len(selected), "missing_final_sql": missing,
        "prediction_sha256": _sha(run_dir / "predictions.jsonl"),
        "trace_sha256": _sha(run_dir / "traces.jsonl"),
        "review_decisions_sha256": _sha(run_dir / "reviews" / "rubric_decisions.jsonl"),
        "provider": args.provider, "model": model_name,
        "requested_reasoning_effort": args.reasoning_effort,
        "prompt_variant": args.prompt_variant,
        "b0_prompt_sha256": sha256(b0.system_prompt_for_variant(
            args.prompt_variant).encode("utf-8")).hexdigest(),
        "reviewer_prompt_version": PROMPT_VERSION,
        "reviewer_prompt_sha256": _sha(REVIEW_PROMPT),
        "refinement_prompt_version": FINAL_PROMPT_VERSION,
        "refinement_prompt_sha256": _sha(FINAL_PROMPT),
        "source_revision": _revision(), "max_attempts": args.max_attempts,
        "max_review_model_calls": args.max_review_model_calls,
        "max_inspections": args.max_inspections,
        "max_total_model_calls": args.max_total_model_calls,
        "max_total_tool_calls": args.max_total_tool_calls,
        "max_total_sql_calls": args.max_total_sql_calls,
        "preview_rows": args.preview_rows,
        "output_format_version": b0.OUTPUT_FORMAT_VERSION,
        "trace_schema_version": 1,
        "note": "Gold references are offline scorer only; reviewer PASS is provisional. "
                "RubricSelfReflection runs independently of unchanged B0 and SelfReflection.",
    })
    print(f"{VARIANT}: {len(selected)} questions, {missing} missing SQL: {run_dir}")
    return 0


def _verified_run(args):
    from scr.evaluation.bird import load_predictions, validate_predictions
    folder, dataset, selected = base_cli._selection(args)
    run_dir = _run_dir(args)
    pred_path = run_dir / "predictions.jsonl"
    manifest_path = run_dir / "inference_manifest.json"
    if not pred_path.is_file() or not manifest_path.is_file():
        raise ValueError("Missing predictions or inference manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    predictions = load_predictions(pred_path)
    validate_predictions(predictions, selected)
    expected = {"agent_variant": VARIANT, "completed": True,
                "selection_id": args.selection_id, "split": args.split, "run_id": args.run_id,
                "dataset_manifest": dataset.manifest,
                "selection_sha256": _sha(folder / "selection_manifest.json"),
                "question_ids": [q["question_id"] for q in selected],
                "expected_questions": len(selected), "prediction_sha256": _sha(pred_path)}
    if len(predictions) != len(selected) or any(manifest.get(k) != v for k,v in expected.items()):
        raise ValueError("Invalid RubricSelfReflection experiment provenance")
    if any(p.get("provider") != manifest.get("provider") or p.get("model") != manifest.get("model")
           for p in predictions):
        raise ValueError("Predictions model/provider do not match manifest")
    return run_dir, manifest, predictions, selected


def score(args):
    from scr.cli.evaluate_bird import run as evaluate
    run_dir, _, _, selected = _verified_run(args)
    if (run_dir / "scores").exists():
        raise ValueError("Refusing to overwrite scores")
    return evaluate([
        "--variant", VARIANT, "--split", args.split,
        "--predictions", str(run_dir / "predictions.jsonl"),
        "--dataset-root", str(args.dataset_root),
        "--output-dir", str(run_dir), "--run-id", "scores",
        "--question-ids", ",".join(str(q["question_id"]) for q in selected),
        "--timeout-seconds", str(args.timeout_seconds),
    ])


def compare(args):
    run_dir, manifest, _, selected = _verified_run(args)
    baseline_dir = (args.result_root / args.selection_id / args.baseline_variant /
                    args.split / args.baseline_run_id)
    if not (baseline_dir / "scores" / "per_question.jsonl").is_file() or not (
            run_dir / "scores" / "per_question.jsonl").is_file():
        raise ValueError("Both runs must be independently scored first")
    control = json.loads((baseline_dir / "inference_manifest.json").read_text(encoding="utf-8"))
    for key in ("dataset_manifest", "selection_sha256", "question_ids", "provider",
                "model", "prompt_variant", "requested_reasoning_effort"):
        if control.get(key) != manifest.get(key):
            raise ValueError(f"Comparison mismatch in {key}")
    control_prompt = control.get("b0_prompt_sha256") if args.baseline_variant == "SelfReflection" else control.get("system_prompt_sha256")
    if control_prompt != manifest.get("b0_prompt_sha256"):
        raise ValueError("B0 prompt hash mismatch")
    def load(path):
        return {r["question_id"]: r for r in (json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip())}
    first = load(baseline_dir / "scores" / "per_question.jsonl")
    second = load(run_dir / "scores" / "per_question.jsonl")
    ids = {q["question_id"] for q in selected}
    if set(first) != ids or set(second) != ids:
        raise ValueError("Question lists differ")
    fixed = sorted(q for q in ids if not first[q]["ex"] and second[q]["ex"])
    regressed = sorted(q for q in ids if first[q]["ex"] and not second[q]["ex"])
    base_correct = sum(bool(first[q]["ex"]) for q in ids)
    new_correct = sum(bool(second[q]["ex"]) for q in ids)
    report = (f"# {args.baseline_variant} vs {VARIANT} — Paired EX\n\n"
              f"Baseline {base_correct}/{len(ids)}; rubric {new_correct}/{len(ids)}; "
              f"delta {(new_correct-base_correct)/len(ids)*100:+.2f} percentage points.\n\n"
              f"Corrected {len(fixed)}: {fixed}\n\nRegressed {len(regressed)}: {regressed}\n\n"
              "Compute may differ; this is not a matched-compute causal comparison.\n")
    output = run_dir / f"comparison_{args.baseline_variant.lower()}.md"
    output.write_text(report, encoding="utf-8", errors="strict") if not output.exists() else (
        _raise_existing(output))
    print(report)
    return 0


def _raise_existing(path):
    raise ValueError(f"Refusing to overwrite: {path}")


def visualize(args):
    from scr.tracing.viewer import write_html
    path = _run_dir(args)
    output = args.output or path / "trace-explorer.html"
    print("Trace Explorer:", write_html([path], output))
    return 0


def parser():
    result = argparse.ArgumentParser(description="LangGraphRubricSelfReflection evaluation")
    sub = result.add_subparsers(dest="action", required=True)
    for action in ("infer", "score", "compare", "visualize"):
        cmd = sub.add_parser(action)
        cmd.add_argument("--selection-id", required=True)
        cmd.add_argument("--dataset-root", type=Path, default=DEFAULT_ROOT)
        cmd.add_argument("--result-root", type=Path, default=base_cli.DEFAULT_RESULT_ROOT)
        cmd.add_argument("--split", required=True, choices=("dev", "test"))
        cmd.add_argument("--run-id", required=True)
        if action == "infer":
            cmd.add_argument("--provider", choices=DEFAULT_MODELS, default="nvidia")
            cmd.add_argument("--model")
            cmd.add_argument("--reasoning-effort", choices=("none", "low", "medium", "high", "xhigh", "max"))
            cmd.add_argument("--prompt-variant", choices=b0.PROMPT_VARIANTS, default="baseline")
            cmd.add_argument("--preview-rows", type=int, default=20)
            cmd.add_argument("--max-attempts", type=int, default=3)
            cmd.add_argument("--max-review-model-calls", type=int, default=40)
            cmd.add_argument("--max-inspections", type=int, default=39)
            cmd.add_argument("--max-total-model-calls", type=int, default=240)
            cmd.add_argument("--max-total-tool-calls", type=int, default=240)
            cmd.add_argument("--max-total-sql-calls", type=int, default=240)
        elif action == "score":
            cmd.add_argument("--timeout-seconds", type=float, default=DEFAULT_SQL_TIMEOUT_SECONDS)
        elif action == "compare":
            cmd.add_argument("--baseline-variant", choices=("B0", "SelfReflection"), default="SelfReflection")
            cmd.add_argument("--baseline-run-id", required=True)
        else:
            cmd.add_argument("--output", type=Path)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    for key in ("selection_id", "run_id", "baseline_run_id"):
        val = getattr(args, key, None)
        if val is not None and not base_cli.SAFE_ID.fullmatch(val):
            raise ValueError(f"Unsafe {key}: {val!r}")
    if args.action == "infer":
        if not 1 <= args.preview_rows <= 200 or not 1 <= args.max_attempts <= 10:
            raise ValueError("Invalid preview/attempt budget")
        if not 1 <= args.max_review_model_calls <= 40 or not 0 <= args.max_inspections <= 39:
            raise ValueError("Invalid reviewer budget")
        if min(args.max_total_model_calls, args.max_total_tool_calls,
               args.max_total_sql_calls) < 1:
            raise ValueError("Invalid global budget")
    elif args.action == "score" and args.timeout_seconds <= 0:
        raise ValueError("Invalid scoring timeout")
    return {"infer": infer, "score": score, "compare": compare, "visualize": visualize}[args.action](args)


if __name__ == "__main__":
    raise SystemExit(main())
