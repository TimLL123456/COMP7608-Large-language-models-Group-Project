"""LangGraph role-specialized inference, scoring, sharding and comparison.

The generator and reviewer always have separately configured provider/model/effort.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from scr.baselines import bird_b0 as b0
from scr.baselines.common import DEFAULT_MODELS, build_model, redact_credentials
from scr.baselines.sqlite_readonly import ReadOnlySqlite, DEFAULT_SQL_TIMEOUT_SECONDS
from scr.cli import run_bird_b0_eval as base_cli
from scr.datasets.bird import DEFAULT_ROOT
from scr.agents.rubric_self_reflection.cli import _revision
from scr.agents.rubric_self_reflection.reviewer import (
    RubricReviewer, REVIEW_PROMPT, PROMPT_VERSION,
)
from langgraph_agents.role_specialized.coordinator import LangGraphRoleSpecializedAgent as RoleSpecializedSelfReflectionAgent
from langgraph_agents.role_specialized.graph import GRAPH_VERSION
from scr.agents.role_specialized.sharding import (inference_lock, load_resume_history, merge_shards,
                       prepare_in_place_resume, shard_dir, shard_slice)

VARIANT = "LangGraphRoleSpecializedSelfReflection"


def _sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2,
                                    allow_nan=False) + "\n", encoding="utf-8")


def _append(file, data):
    file.write(json.dumps(data, ensure_ascii=False, default=str,
                          allow_nan=False) + "\n")
    file.flush()


def _run_dir(args):
    root = args.result_root / args.selection_id / VARIANT / args.split / args.run_id
    if getattr(args, "action", None) == "infer" and args.split == "all":
        return shard_dir(root, args.shard_index, args.shard_count)
    return root


def _selected(args):
    """Use the original validated Dev/Test selection; all means Dev then Test."""
    if args.split != "all":
        return base_cli._selection(args)
    dev_args = argparse.Namespace(**{**vars(args), "split": "dev"})
    test_args = argparse.Namespace(**{**vars(args), "split": "test"})
    folder, dataset, dev = base_cli._selection(dev_args)
    test_folder, test_dataset, test = base_cli._selection(test_args)
    if test_folder != folder or test_dataset.manifest != dataset.manifest:
        raise ValueError("Dev and Test selections must share a dataset")
    if len({q["question_id"] for q in dev + test}) != len(dev) + len(test):
        raise ValueError("Overlapping Dev/Test selection IDs")
    return folder, dataset, dev + test


def _validate_role_slugs(generator_provider, generator_name, reviewer_provider, reviewer_name):
    """Only check account-advertised SIWC model IDs, never silently substitute."""
    roles = {name for provider, name in (
        (generator_provider, generator_name), (reviewer_provider, reviewer_name)
    ) if provider == "chatgpt-siwc"}
    if not roles:
        return
    from scr.baselines.chatgpt_siwc import list_available_models
    advertised = {row["slug"] for row in list_available_models()}
    unknown = sorted(roles - advertised)
    if unknown:
        raise ValueError(
            "SIWC account does not advertise these model slugs: " + ", ".join(unknown) +
            ". Run langgraph_agents.role_specialized.cli models to see exact available slugs; "
            "set --generator-model / --reviewer-model explicitly."
        )


def _role_model(provider, model_name, effort):
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Unknown provider: {provider}")
    if effort is not None and provider != "chatgpt-siwc":
        raise ValueError("Reasoning effort currently requires chatgpt-siwc")
    name = model_name or DEFAULT_MODELS[provider]
    if not name:
        raise ValueError(f"Explicit model required for {provider}")
    if provider == "chatgpt-siwc":
        from scr.baselines.siwc_auth import CREDS, read_json
        if not read_json(CREDS):
            raise ValueError("Authenticate chatgpt-siwc before inference")
    options = {
        "provider": provider,
        "temperature": None if provider in ("openai", "chatgpt-siwc") else b0.TEMPERATURE,
        "top_p": b0.TOP_P if provider == "nvidia" else None,
        "max_tokens": b0.MAX_OUTPUT_TOKENS,
        "timeout": b0.REQUEST_TIMEOUT,
        **({"reasoning_effort": effort} if effort is not None else {}),
    }
    return name, build_model(name, **options)



def _transient_provider_failure(result: dict) -> bool:
    """Do not checkpoint quota/provider failures as completed questions."""
    def limited(value):
        message = str(value or "").lower()
        return any(token in message for token in (
            "usage limit", "usage_limit", "quota", "rate limit", "rate_limit",
            "too many requests", "429",
        ))
    if limited((result.get("report") or {}).get("error")):
        return True
    if limited((result.get("extraction") or {}).get("error")):
        return True
    if any(report.get("stop_reason") == "review_provider_error"
           for report in result.get("review_reports", [])):
        return True
    for attempt in result.get("attempts", []):
        report = attempt.get("b0_report") or {}
        review = attempt.get("review") or {}
        if limited(report.get("error")) or limited(review.get("error")) or (
            review.get("stop_reason") == "review_provider_error"
        ):
            return True
    return False


def infer(args):
    folder, dataset, selection = _selected(args)
    selected, shard_info = (
        shard_slice(selection, args.shard_index, args.shard_count)
        if args.split == "all" else (selection, {})
    )
    b0.system_prompt_for_variant(args.prompt_variant)
    generator_id = args.generator_model or (
        "gpt-6-luna" if args.generator_provider == "chatgpt-siwc" else None)
    reviewer_id = args.reviewer_model or (
        "gpt-6.1-terra" if args.reviewer_provider == "chatgpt-siwc" else None)
    if args.check_models:
        _validate_role_slugs(args.generator_provider, generator_id,
                             args.reviewer_provider, reviewer_id)
    generator_name, generator = _role_model(
        args.generator_provider, generator_id, args.generator_reasoning_effort)
    reviewer_name, reviewer_model = _role_model(
        args.reviewer_provider, reviewer_id, args.reviewer_reasoning_effort)
    run_dir = _run_dir(args)
    resume = args.start_position is not None
    if resume:
        if not args.replace_existing or not run_dir.is_dir() or run_dir.is_symlink():
            raise ValueError("Resume requires --replace-existing and an existing run")
    else:
        if run_dir.exists() or run_dir.is_symlink():
            raise ValueError(f"Refusing to overwrite experiment: {run_dir}")
        run_dir.mkdir(parents=True)
        (run_dir / "reviews").mkdir()
    config = {
        "agent_variant": VARIANT, "outer_graph_version": GRAPH_VERSION,
        "selection_id": args.selection_id,
        "split": args.split, "run_id": args.run_id,
        "dataset_manifest": dataset.manifest,
        "selection_sha256": _sha(folder / "selection_manifest.json"),
        "question_ids": [q["question_id"] for q in selected],
        "expected_questions": len(selected), **shard_info,
        "generator_provider": args.generator_provider, "generator_model": generator_name,
        "generator_reasoning_effort": args.generator_reasoning_effort,
        "reviewer_provider": args.reviewer_provider, "reviewer_model": reviewer_name,
        "reviewer_reasoning_effort": args.reviewer_reasoning_effort,
        "prompt_variant": args.prompt_variant,
        "b0_prompt_sha256": sha256(b0.system_prompt_for_variant(
            args.prompt_variant).encode("utf-8")).hexdigest(),
        "reviewer_prompt_version": PROMPT_VERSION,
        "reviewer_prompt_sha256": _sha(REVIEW_PROMPT),
        "max_attempts": args.max_attempts,
        "max_review_model_calls": args.max_review_model_calls,
        "max_inspections": args.max_inspections,
        "max_total_model_calls": args.max_total_model_calls,
        "max_total_tool_calls": args.max_total_tool_calls,
        "max_total_sql_calls": args.max_total_sql_calls,
        "preview_rows": args.preview_rows, "source_revision": _revision(),
        "output_format_version": b0.OUTPUT_FORMAT_VERSION,
        "note": "No gold data is available to the generator or reviewer. "
                "Strong model never generates or refines SQL.",
    }
    with inference_lock(run_dir):
        reviewer = RubricReviewer(
            reviewer_model, max_model_calls=args.max_review_model_calls,
            max_inspections=args.max_inspections)
        coordinator = RoleSpecializedSelfReflectionAgent(
            reviewer, generator_model=generator, prompt_variant=args.prompt_variant,
            max_attempts=args.max_attempts,
            max_total_model_calls=args.max_total_model_calls,
            max_total_tool_calls=args.max_total_tool_calls,
            max_total_sql_calls=args.max_total_sql_calls,
        )
        if resume:
            resume_info = prepare_in_place_resume(
                run_dir=run_dir, selected=selected,
                start_position=args.start_position, config=config,
            )
            created = resume_info["created_utc"]
            missing = resume_info["missing"]
            print(f"Resuming {run_dir} from position {args.start_position}; "
                  f"backup: {resume_info['backup_directory']}", flush=True)
        else:
            created = datetime.now(timezone.utc).isoformat()
            missing = 0
            _write_json(run_dir / "inference_config.json", {**config, "created_utc": created})
        start_position = args.start_position or 1
        mode = "a" if resume else "x"
        with (run_dir / "predictions.jsonl").open(mode, encoding="utf-8") as predictions, \
             (run_dir / "traces.jsonl").open(mode, encoding="utf-8") as traces, \
             (run_dir / "reviews" / "review_reports.jsonl").open(mode, encoding="utf-8") as reports:
            for position, question in enumerate(selected[start_position - 1:], start_position):
                try:
                    store = ReadOnlySqlite(dataset.get_database_path(question["db_id"]),
                                           max_rows=args.preview_rows)
                    result = coordinator.run(question, store)
                    report, sql = result["report"], result["final_sql"]
                except Exception as exc:
                    sql = None
                    report = {
                        "question_id": question["question_id"], "db_id": question["db_id"],
                        "graph_completed": False, "output_status": "missing",
                        "review_status": "ERROR", "stop_reason": "coordinator_error",
                        "error": redact_credentials(f"{type(exc).__name__}: {exc}")[:500],
                    }
                    result = {"report": report, "extraction": {}, "attempts": [],
                              "structured_events": [], "review_reports": [],
                              "generator_usage": {}, "reviewer_usage": {}}
                if _transient_provider_failure(result):
                    raise RuntimeError(
                        f"Provider usage limit/error at shard position {position}; "
                        "result not saved. Retry this position with --replace-existing."
                    )
                missing += int(sql is None)
                report["model"] = generator_name
                report["reviewer_model"] = reviewer_name
                # B0's reused run_one() can contain a historical constant model label.
                # Normalize each nested attempt to its actual configured generator.
                for attempt in result["attempts"]:
                    attempt_report = attempt.get("b0_report")
                    if isinstance(attempt_report, dict):
                        attempt_report["model"] = generator_name
                        attempt_report["provider"] = args.generator_provider
                        attempt_report["reasoning_effort"] = args.generator_reasoning_effort
                prediction = {
                    "question_id": question["question_id"], "db_id": question["db_id"],
                    "predicted_sql": sql, "provider": args.generator_provider,
                    "model": generator_name,
                    "reasoning_effort": args.generator_reasoning_effort,
                    "reviewer_provider": args.reviewer_provider, "reviewer_model": reviewer_name,
                    "reviewer_reasoning_effort": args.reviewer_reasoning_effort,
                    "cost_usd": None,
                    "output_status": report.get("output_status"),
                    "review_status": report.get("review_status"),
                    "latency_ms": (round(report["seconds"] * 1000, 3)
                                   if report.get("seconds") is not None else None),
                }
                for key in ("model_calls", "tool_calls", "sql_calls", "input_tokens",
                            "output_tokens", "total_tokens", "cached_input_tokens",
                            "reasoning_tokens"):
                    prediction[key] = report.get(key)
                _append(predictions, prediction)
                _append(traces, {
                    "question_id": question["question_id"],
                    "question": question["question"], "evidence": question.get("evidence"),
                    "generator": {"provider": args.generator_provider, "model": generator_name,
                                  "reasoning_effort": args.generator_reasoning_effort},
                    "reviewer": {"provider": args.reviewer_provider, "model": reviewer_name,
                                 "reasoning_effort": args.reviewer_reasoning_effort},
                    **result,
                })
                _append(reports, {
                    "question_id": question["question_id"],
                    "extraction": result["extraction"],
                    "review_reports": result["review_reports"],
                    "final_sql": sql, "output_status": report.get("output_status"),
                    "generator_usage": result["generator_usage"],
                    "reviewer_usage": result["reviewer_usage"],
                })
                print(f"Q{question['question_id']}: {report.get('output_status')} "
                      f"({report.get('stop_reason')})", flush=True)
        manifest = {
            **config, "completed": True, "created_utc": created,
            "missing_final_sql": missing,
            "prediction_sha256": _sha(run_dir / "predictions.jsonl"),
            "trace_sha256": _sha(run_dir / "traces.jsonl"),
            "review_reports_sha256": _sha(run_dir / "reviews" / "review_reports.jsonl"),
            "resume_history": load_resume_history(run_dir),
        }
        # Publish the completed manifest only after all three streams are finished.
        staging_manifest = run_dir / ".inference_manifest.json.tmp"
        _write_json(staging_manifest, manifest)
        staging_manifest.replace(run_dir / "inference_manifest.json")
        print(f"{VARIANT}: {len(selected)} questions; {missing} missing SQL: {run_dir}")
        return 0


def merge(args):
    if args.split != "all":
        raise ValueError("Sharded 500-question merging requires --split all")
    folder, dataset, _ = _selected(args)
    selections = {}
    for split in ("dev", "test"):
        original = argparse.Namespace(**{**vars(args), "split": split})
        _, _, selections[split] = base_cli._selection(original)
    base = _run_dir(args)
    target = {split: args.result_root / args.selection_id / VARIANT / split / args.run_id
              for split in ("dev", "test")}
    summary = merge_shards(
        folder=folder, run_root=base, split_dirs=target,
        selections=selections, dataset_manifest=dataset.manifest,
        shard_count=args.shard_count, variant=VARIANT, run_id=args.run_id,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("Score separately with --split dev and --split test; do not leak Test labels into tuning.")
    return 0


def models(args):
    from scr.baselines.chatgpt_siwc import list_available_models
    for entry in list_available_models():
        print(f"{entry['slug']} — {entry['name']}")
    return 0


def _verified_run(args):
    from scr.evaluation.bird import load_predictions, validate_predictions
    folder, dataset, selected = base_cli._selection(args)
    run_dir = _run_dir(args)
    manifest_path, pred_path = (run_dir / "inference_manifest.json",
                                run_dir / "predictions.jsonl")
    if not manifest_path.is_file() or not pred_path.is_file():
        raise ValueError("Missing inference artifacts")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    predictions = load_predictions(pred_path)
    validate_predictions(predictions, selected)
    required = {
        "agent_variant": VARIANT, "completed": True,
        "selection_id": args.selection_id, "split": args.split, "run_id": args.run_id,
        "dataset_manifest": dataset.manifest,
        "selection_sha256": _sha(folder / "selection_manifest.json"),
        "question_ids": [q["question_id"] for q in selected],
        "expected_questions": len(selected), "prediction_sha256": _sha(pred_path),
        "trace_sha256": _sha(run_dir / "traces.jsonl"),
        "review_reports_sha256": _sha(run_dir / "reviews" / "review_reports.jsonl"),
    }
    if len(predictions) != len(selected) or any(manifest.get(k) != v
                                                for k, v in required.items()):
        raise ValueError("Experiment manifest/hash mismatch")
    if any(p.get("model") != manifest.get("generator_model") or
           p.get("provider") != manifest.get("generator_provider") or
           p.get("reviewer_model") != manifest.get("reviewer_model") or
           p.get("reviewer_provider") != manifest.get("reviewer_provider")
           for p in predictions):
        raise ValueError("Model identities do not match manifest")
    return run_dir, manifest, predictions, selected


def score(args):
    from scr.cli.evaluate_bird import run as evaluate
    run_dir, _, _, selected = _verified_run(args)
    if (run_dir / "scores").exists():
        raise ValueError("Refusing to overwrite existing scores")
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
    control_dir = (args.result_root / args.selection_id / args.control_variant /
                   args.split / args.control_run_id)
    for path in (run_dir / "scores" / "per_question.jsonl",
                 control_dir / "scores" / "per_question.jsonl"):
        if not path.is_file():
            raise ValueError(f"Missing independently scored run: {path}")
    control = json.loads((control_dir / "inference_manifest.json").read_text(encoding="utf-8"))
    for key in ("dataset_manifest", "selection_sha256", "question_ids"):
        if control.get(key) != manifest.get(key):
            raise ValueError(f"Control selection differs in {key}")
    def load(path):
        return {x["question_id"]: x for x in (
            json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip())}
    control_rows = load(control_dir / "scores" / "per_question.jsonl")
    candidate_rows = load(run_dir / "scores" / "per_question.jsonl")
    expected = {q["question_id"] for q in selected}
    if set(control_rows) != expected or set(candidate_rows) != expected:
        raise ValueError("Scored question IDs mismatch")
    fixed = sorted(q for q in expected if not control_rows[q]["ex"]
                   and candidate_rows[q]["ex"])
    regressed = sorted(q for q in expected if control_rows[q]["ex"]
                       and not candidate_rows[q]["ex"])
    before = sum(control_rows[q]["ex"] for q in expected)
    after = sum(candidate_rows[q]["ex"] for q in expected)
    mean = lambda rows, field: (
        sum(row[field] for row in rows.values() if row.get(field) is not None) /
        sum(row.get(field) is not None for row in rows.values())
        if any(row.get(field) is not None for row in rows.values()) else None)
    summary = {
        "control_variant": args.control_variant,
        "control_run_id": args.control_run_id,
        "experiment_variant": VARIANT, "experiment_run_id": args.run_id,
        "questions": len(expected),
        "control_correct": before, "experiment_correct": after,
        "delta_ex_percentage_points": (after-before) / len(expected) * 100,
        "fixed_ids": fixed, "regressed_ids": regressed,
        "control_mean_input_tokens": mean(control_rows, "input_tokens"),
        "experiment_mean_input_tokens": mean(candidate_rows, "input_tokens"),
        "control_mean_latency_ms": mean(control_rows, "latency_ms"),
        "experiment_mean_latency_ms": mean(candidate_rows, "latency_ms"),
        "note": "Model assignments and call budgets may differ; interpret accuracy/cost "
                "comparisons accordingly. No price is imputed without observed billing.",
    }
    output = run_dir / f"comparison_{args.control_variant.lower()}_{args.control_run_id}.json"
    if output.exists():
        raise ValueError(f"Refusing to overwrite comparison: {output}")
    _write_json(output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def visualize(args):
    from scr.tracing.viewer import write_html
    run_dir = _run_dir(args)
    output = args.output or run_dir / "trace-explorer.html"
    print("Trace Explorer:", write_html([run_dir], output))
    return 0


def parser():
    result = argparse.ArgumentParser(description="LangGraph role-specialized KORA Text-to-SQL experiment")
    sub = result.add_subparsers(dest="action", required=True)
    sub.add_parser("models", help="List account-advertised ChatGPT SIWC model slugs")
    for action in ("infer", "merge", "score", "compare", "visualize"):
        cmd = sub.add_parser(action)
        cmd.add_argument("--selection-id", required=True)
        cmd.add_argument("--dataset-root", type=Path, default=DEFAULT_ROOT)
        cmd.add_argument("--result-root", type=Path, default=base_cli.DEFAULT_RESULT_ROOT)
        cmd.add_argument("--split", choices=("all",) if action == "merge"
                         else ("dev", "test", "all") if action in ("infer", "visualize")
                         else ("dev", "test"), required=True)
        cmd.add_argument("--run-id", required=True)
        if action == "infer":
            cmd.add_argument("--generator-provider", choices=DEFAULT_MODELS, default="chatgpt-siwc")
            cmd.add_argument("--generator-model")
            cmd.add_argument("--generator-reasoning-effort",
                             choices=("none", "low", "medium", "high", "xhigh", "max"))
            cmd.add_argument("--reviewer-provider", choices=DEFAULT_MODELS, default="chatgpt-siwc")
            cmd.add_argument("--reviewer-model")
            cmd.add_argument("--check-models", action="store_true",
                             help="Preflight check against your SIWC account's advertised model slugs")
            cmd.add_argument("--shard-index", type=int, default=1,
                             help="1-based worker index, e.g. 1 or 2")
            cmd.add_argument("--shard-count", type=int, default=1,
                             help="Number of disjoint terminal workers")
            cmd.add_argument("--start-position", type=int,
                             help="1-based question position within this shard to rerun")
            cmd.add_argument("--replace-existing", action="store_true",
                             help="Back up and replace records at/after --start-position")
            cmd.add_argument("--reviewer-reasoning-effort",
                             choices=("none", "low", "medium", "high", "xhigh", "max"))
            cmd.add_argument("--prompt-variant", choices=b0.PROMPT_VARIANTS,
                             default="generalized-v1")
            cmd.add_argument("--preview-rows", type=int, default=20)
            cmd.add_argument("--max-attempts", type=int, default=3)
            cmd.add_argument("--max-review-model-calls", type=int, default=40)
            cmd.add_argument("--max-inspections", type=int, default=39)
            cmd.add_argument("--max-total-model-calls", type=int, default=240)
            cmd.add_argument("--max-total-tool-calls", type=int, default=240)
            cmd.add_argument("--max-total-sql-calls", type=int, default=240)
        elif action == "merge":
            cmd.add_argument("--shard-count", type=int, required=True)
        elif action == "score":
            cmd.add_argument("--timeout-seconds", type=float,
                             default=DEFAULT_SQL_TIMEOUT_SECONDS)
        elif action == "compare":
            cmd.add_argument("--control-variant",
                             choices=("B0", "LangGraphB0", "SelfReflection", "RubricSelfReflection",
                                      "RoleSpecializedSelfReflection"),
                             default="B0")
            cmd.add_argument("--control-run-id", required=True)
        else:
            cmd.add_argument("--output", type=Path)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    for key in ("selection_id", "run_id", "control_run_id"):
        value = getattr(args, key, None)
        if value is not None and not base_cli.SAFE_ID.fullmatch(value):
            raise ValueError(f"Unsafe {key}: {value!r}")
    if args.action == "infer":
        if args.replace_existing != (args.start_position is not None):
            raise ValueError("--start-position and --replace-existing must be used together")
        if args.start_position is not None and args.start_position < 1:
            raise ValueError("--start-position must be at least 1")
        if args.split != "all" and (args.shard_index != 1 or args.shard_count != 1):
            raise ValueError("Sharded inference currently requires --split all")
        if not 1 <= args.shard_count <= 999 or not 1 <= args.shard_index <= args.shard_count:
            raise ValueError("Invalid shard index/count")
        if not 1 <= args.preview_rows <= 200 or not 1 <= args.max_attempts <= 10:
            raise ValueError("Invalid preview / attempt budget")
        if not 1 <= args.max_review_model_calls <= 40 or not 0 <= args.max_inspections <= 39:
            raise ValueError("Invalid review budget")
        if min(args.max_total_model_calls, args.max_total_tool_calls,
               args.max_total_sql_calls) < 1:
            raise ValueError("Invalid global budget")
    elif args.action == "merge" and not 1 <= args.shard_count <= 999:
        raise ValueError("Invalid shard count")
    elif args.action == "score" and args.timeout_seconds <= 0:
        raise ValueError("Invalid scoring timeout")
    return {"infer": infer, "merge": merge, "score": score,
            "compare": compare, "visualize": visualize,
            "models": models}[args.action](args)


if __name__ == "__main__":
    raise SystemExit(main())
