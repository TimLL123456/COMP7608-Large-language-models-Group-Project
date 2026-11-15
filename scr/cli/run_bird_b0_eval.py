"""B0 difficulty-sampled Mini-Dev evaluation: prepare, infer, score.

Run: uv run python -m scr.cli.run_bird_b0_eval {prepare,infer,score} --help
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile

from scr.baselines.sqlite_readonly import DEFAULT_SQL_TIMEOUT_SECONDS
from scr.datasets.bird import BirdDataset, DEFAULT_ROOT
from scr.baselines.common import DEFAULT_MODELS, build_model
from scr.evaluation.bird_sampling import LEVELS, difficulty_counts, select_questions, allocate_ratios

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULT_ROOT = PROJECT_ROOT / "scr" / "evaluation" / "result"
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")


def _dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def _jsonl_write(file, row) -> None:
    file.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    file.flush()


def _selection(args):
    folder = args.result_root / args.selection_id
    manifest_path = folder / "selection_manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"Unknown selection: {folder}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dataset = BirdDataset(args.dataset_root)
    if manifest["dataset_manifest"] != dataset.manifest:
        raise ValueError("Dataset manifest changed since sampling")
    selected = [json.loads(line) for line in (folder / f"{args.split}.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if [row["question_id"] for row in selected] != manifest["question_ids"][args.split]:
        raise ValueError("Selected IDs do not match manifest")
    allowed = {row["question_id"] for row in dataset.get_split(args.split)}
    for row in selected:
        if row["question_id"] not in allowed or row != dataset.get_agent_input(row["question_id"]):
            raise ValueError("Out-of-split or modified question")
    if not selected:
        raise ValueError(f"No questions selected for {args.split}")
    return folder, dataset, selected


def prepare(args) -> int:
    dataset = BirdDataset(args.dataset_root)
    folder = args.result_root / args.selection_id
    if folder.is_symlink():
        raise ValueError("Refusing to overwrite symlinked selection")
    if folder.exists():
        if not args.force:
            raise ValueError(f"Refusing to overwrite selection: {folder} (use prepare --force for an unused selection)")
        if not folder.is_dir():
            raise ValueError("Selection path is not a directory")
        expected_files = {"dev.jsonl", "test.jsonl", "selection_manifest.json"}
        children = list(folder.iterdir())
        if {item.name for item in children} != expected_files or any(not item.is_file() or item.is_symlink() for item in children):
            raise ValueError("Refusing --force: selection has runs, unexpected files or unsafe entries; use a new --selection-id")
        old = json.loads((folder / "selection_manifest.json").read_text(encoding="utf-8"))
        if old.get("selection_id") != args.selection_id:
            raise ValueError("Existing selection manifest ID does not match folder")
    chosen = {}
    counts = {}
    explicit = any(getattr(args, f"{s}_{lv}") is not None for s in ("dev", "test") for lv in LEVELS)
    if args.total_questions is not None:
        if explicit:
            raise ValueError("Ratio and explicit counts cannot be combined")
        configured = allocate_ratios(args.total_questions, args.dev_ratio, args.difficulty_ratio, dataset)
    else:
        configured = {s: {lv: getattr(args, f"{s}_{lv}") or 0 for lv in LEVELS} for s in ("dev", "test")}
    for split in ("dev", "test"):
        requested = configured[split]
        rows = select_questions(dataset, split, requested, args.seed)
        chosen[split], counts[split] = rows, difficulty_counts(rows)
    if not chosen["dev"] and not chosen["test"]:
        raise ValueError("Choose at least one question")
    args.result_root.mkdir(parents=True, exist_ok=True)
    # Stage the complete selection before touching the previous one.
    with tempfile.TemporaryDirectory(prefix=f".{args.selection_id}-staging-", dir=args.result_root) as temporary:
        staging_root = Path(temporary)
        staged = staging_root / "new"
        staged.mkdir()
        for split, rows in chosen.items():
            with (staged / f"{split}.jsonl").open("w", encoding="utf-8") as out:
                for row in rows:
                    _jsonl_write(out, row)
        _dump(staged / "selection_manifest.json", {
            "selection_id": args.selection_id, "seed": args.seed,
            "dataset_manifest": dataset.manifest,
            "question_ids": {split: [row["question_id"] for row in rows] for split, rows in chosen.items()},
            "difficulty_counts": counts,
            "note": "test is local Mini-Dev held-out, NOT the official BIRD hidden test; gold SQL excluded",
        })
        if folder.exists():
            # Refuse if another process has added runs since preflight.
            children = list(folder.iterdir())
            if {item.name for item in children} != {"dev.jsonl", "test.jsonl", "selection_manifest.json"} or any(item.is_symlink() for item in children):
                raise ValueError("Selection changed during --force; refusing replacement")
            backup = staging_root / "backup"
            folder.rename(backup)
            try:
                staged.rename(folder)
            except OSError:
                backup.rename(folder)
                raise
        else:
            staged.rename(folder)
    print(f"Selection {folder}: dev={len(chosen['dev'])}, test={len(chosen['test'])}")
    return 0


def infer(args) -> int:
    from scr.baselines import bird_b0 as b0
    from scr.baselines.common import redact_credentials
    from scr.baselines.sqlite_readonly import ReadOnlySqlite

    folder, dataset, selected = _selection(args)
    provider = args.provider
    reasoning_effort = args.reasoning_effort
    prompt_variant = args.prompt_variant
    # Preflight versioned instructions before opening an immutable run directory.
    system_prompt_sha256 = sha256(b0.system_prompt_for_variant(prompt_variant).encode("utf-8")).hexdigest()
    if reasoning_effort is not None and provider != "chatgpt-siwc":
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
    # Preserve the original default NVIDIA call path for backward compatibility.
    model = None
    if provider != "nvidia" or model_name != b0.MODEL:
        model = build_model(
            model_name, provider=provider,
            temperature=None if provider in ("openai", "chatgpt-siwc") else b0.TEMPERATURE,
            top_p=b0.TOP_P if provider == "nvidia" else None,
            max_tokens=b0.MAX_OUTPUT_TOKENS, timeout=b0.REQUEST_TIMEOUT,
            **({"reasoning_effort": reasoning_effort} if reasoning_effort is not None else {}),
        )
    run_dir = folder / "B0" / args.split / args.run_id
    if run_dir.exists():
        raise ValueError(f"Refusing to overwrite run: {run_dir}")
    run_dir.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    failures = 0
    with (run_dir / "predictions.jsonl").open("w", encoding="utf-8") as preds, \
         (run_dir / "traces.jsonl").open("w", encoding="utf-8") as traces:
        for question in selected:
            events = []
            structured_events = []
            try:
                store = ReadOnlySqlite(dataset.get_database_path(question["db_id"]), max_rows=args.preview_rows)
                if prompt_variant == "baseline":
                    # Retain the historical call shape for all legacy users/tests.
                    agent = b0.make_agent(store) if model is None else b0.make_agent(store, model=model)
                else:
                    agent = (b0.make_agent(store, prompt_variant=prompt_variant) if model is None
                             else b0.make_agent(store, model=model, prompt_variant=prompt_variant))
                report = b0.run_one(
                    question, agent, log=lambda msg: events.append(redact_credentials(str(msg))),
                    trace_events=structured_events,
                )
                report["model"] = model_name
            except Exception as exc:
                report = {
                    "final_sql": None, "model_calls": 0, "tool_calls": 0,
                    "sql_calls": 0, "input_tokens": None, "output_tokens": None,
                    "usage_observed": False, "seconds": None, "graph_completed": False,
                    "stop_reason": type(exc).__name__,
                    "error": redact_credentials(f"{type(exc).__name__}: {exc}"),
                }
            sql = report.get("final_sql") if report.get("graph_completed") else None
            failures += int(sql is None)
            _jsonl_write(preds, {
                "question_id": question["question_id"], "db_id": question["db_id"],
                "predicted_sql": sql, "provider": provider, "model": model_name,
                "requested_reasoning_effort": reasoning_effort,
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
                "latency_ms": round(report["seconds"] * 1000, 3) if report.get("seconds") is not None else None,
                "model_calls": report.get("model_calls"), "sql_calls": report.get("sql_calls"),
                "sql_success_calls": report.get("sql_success_calls"),
                "sql_error_calls": report.get("sql_error_calls"),
                "sql_truncated_calls": report.get("sql_truncated_calls"),
                "agent_sql_execution_ms": report.get("agent_sql_execution_ms") if report.get("sql_execution_observed") else None,
                "cost_usd": None,
            })
            _jsonl_write(traces, {"question_id": question["question_id"],
                                  "question": question.get("question"), "evidence": question.get("evidence"),
                                  "report": report, "events": events,
                                  "structured_events": structured_events})
            print(f"Q{question['question_id']}: {'final_sql_ready' if sql else report.get('stop_reason', 'failed')}", flush=True)
    _dump(run_dir / "inference_manifest.json", {
        "completed": True, "question_ids": [q["question_id"] for q in selected],
        "prediction_sha256": sha256((run_dir / "predictions.jsonl").read_bytes()).hexdigest(),
        "selection_sha256": sha256((folder / "selection_manifest.json").read_bytes()).hexdigest(),
        "dataset_manifest": dataset.manifest,
        "preview_rows": args.preview_rows,
        "agent_sql_timeout_seconds": DEFAULT_SQL_TIMEOUT_SECONDS,
        "output_format_version": b0.OUTPUT_FORMAT_VERSION,
        "parser_revision": "accept-inline-opening-delimiter-v1",
        "trace_schema_version": 1,
        "selection_id": args.selection_id, "split": args.split, "run_id": args.run_id,
        "created_utc": started, "model": model_name, "provider": provider,
        "prompt_variant": prompt_variant, "system_prompt_sha256": system_prompt_sha256,
        "requested_reasoning_effort": reasoning_effort,
        "temperature": None if provider in ("openai", "chatgpt-siwc") else b0.TEMPERATURE,
        "top_p": b0.TOP_P if provider == "nvidia" else None,
        "request_timeout_seconds": b0.REQUEST_TIMEOUT,
        "max_output_tokens": None if provider == "chatgpt-siwc" else b0.MAX_OUTPUT_TOKENS,
        "max_context_tokens": b0.MAX_CONTEXT_TOKENS if provider == "nvidia" else None,
        "context_budget_enforced": False,
        "max_model_calls": b0.MAX_MODEL_CALLS, "max_total_tool_calls": b0.MAX_TOTAL_TOOL_CALLS,
        "max_sql_executions": b0.MAX_SQL_EXECUTIONS, "recursion_limit": b0.RECURSION_LIMIT,
        "expected_questions": len(selected), "missing_final_sql": failures,
        "usage_schema_version": 2,
        "note": (
            "Optional token details and reasoning settings are stored only when returned. "
            "Their *_observed_calls may be smaller than model_calls; sums can be partial. "
            "Cached input tokens are included in input tokens, and reasoning tokens in "
            "output tokens. Nested subagent usage may be unobserved; cost unknown."
        ),
    })
    print(f"Saved {len(selected)} predictions ({failures} missing SQL) to {run_dir}")
    return 0


def score(args) -> int:
    from scr.cli.evaluate_bird import run as evaluate
    folder, dataset, selected = _selection(args)
    run_dir = folder / "B0" / args.split / args.run_id
    predictions = run_dir / "predictions.jsonl"
    manifest_file = run_dir / "inference_manifest.json"
    if not predictions.is_file() or not manifest_file.is_file():
        raise ValueError(f"Run predictions and manifest required: {run_dir}")
    from hashlib import sha256
    from scr.evaluation.bird import load_predictions, validate_predictions
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    records = load_predictions(predictions)
    validate_predictions(records, selected)
    from scr.baselines import bird_b0 as b0
    expected = {"completed": True, "selection_id": args.selection_id, "split": args.split,
                "run_id": args.run_id, "expected_questions": len(selected),
                "question_ids": [q["question_id"] for q in selected],
                "prediction_sha256": sha256(predictions.read_bytes()).hexdigest(),
                "selection_sha256": sha256((folder / "selection_manifest.json").read_bytes()).hexdigest(),
                "dataset_manifest": dataset.manifest,
                "output_format_version": b0.OUTPUT_FORMAT_VERSION,
                }
    if any(manifest.get(k) != v for k, v in expected.items()) or len(records) != len(selected):
        raise ValueError("Incomplete or mismatched inference manifest/predictions")
    if manifest.get("provider") not in DEFAULT_MODELS:
        raise ValueError("Inference manifest has an unsupported provider")
    if not isinstance(manifest.get("model"), str) or not manifest["model"]:
        raise ValueError("Inference manifest missing model")
    if any(row.get("provider") != manifest["provider"] or row.get("model") != manifest["model"] for row in records):
        raise ValueError("Incomplete or mismatched inference manifest/predictions")
    if (run_dir / "scores").exists():
        raise ValueError(f"Scores already exist: {run_dir / 'scores'}")
    outcome = evaluate([
        "--variant", "B0", "--split", args.split,
        "--predictions", str(predictions), "--dataset-root", str(args.dataset_root),
        "--output-dir", str(run_dir), "--run-id", "scores",
        "--question-ids", ",".join(str(row["question_id"]) for row in selected),
        "--timeout-seconds", str(args.timeout_seconds),
    ])
    if outcome == 0:
        scores = run_dir / "scores"
        summary_file = scores / "summary.json"
        if not summary_file.is_file():
            raise ValueError("Scoring succeeded without summary.json")
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        performance = summary.get("performance", {})
        lines = [
            "# B0 Evaluation Report", "",
            f"Split: {args.split} (selected subset, NOT full-split or hidden-test EX)",
            f"Questions: {summary['total']}",
            f"EX: **{summary['correct']}/{summary['total']} ({summary['ex']:.2%})**", "",
            "## Accuracy by difficulty", "",
            "| Difficulty | Correct | Total | EX |", "|---|---:|---:|---:|",
        ]
        for level, stats in sorted(summary["by_difficulty"].items()):
            lines.append(f"| {level} | {stats['correct']} | {stats['total']} | {stats['ex']:.2%} |")
        lines.extend(["", "## Inference and SQL execution", "",
                      "| Metric | Total | Mean | P50 | P95 | Observed |",
                      "|---|---:|---:|---:|---:|---:|"])
        for key, stat in performance.items():
            if isinstance(stat, dict):
                def display(field):
                    value = stat.get(field)
                    return f"{value:.2f}" if isinstance(value, (int, float)) else "n/a"
                lines.append(f"| {key} | {display('total')} | {display('mean')} | {display('p50')} | {display('p95')} | {stat.get('observed', 0)} |")
            else:
                lines.append(f"| {key} | {stat} | — | — | — | — |")
        per_question = scores / "per_question.jsonl"
        if not per_question.is_file():
            raise ValueError("Scoring succeeded without per_question.jsonl")
        lines.extend(["", "## Per-question scores", "",
                      "| Question | Difficulty | EX | Status | Model turns | Tool calls | Agent SQL calls | Inference ms |",
                      "|---|---|---:|---|---:|---:|---:|---:|"])
        for line in per_question.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            def label(key):
                return str(row[key]) if row.get(key) is not None else "n/a"
            lines.append(
                f"| {row['question_id']} | {row['difficulty']} | {row['ex']} | {row['status']} | "
                f"{label('model_calls')} | {label('tool_calls')} | {label('sql_calls')} | {label('latency_ms')} |"
            )
        lines.extend(["", "Times are milliseconds. Model turns represent observable main-agent model calls.",
                      "Cached input tokens are part of input tokens; reasoning tokens are part of output tokens.",
                      "Optional usage fields may be partial: compare *_observed_calls with model_calls.",
                      "Thinking/effort values are reported only when a provider supplies them.",
                      "Nested subagent activity may be unobserved. n/a does not mean zero.",
                      "Agent SQL tool success is not equivalent to final SQL EX.",
                      "Gold SQL is validated separately before any predicted SQL scoring."])
        (scores / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return outcome


def visualize(args) -> int:
    """Render selected saved runs as an offline HTML graph; never run agents or SQL."""
    from scr.tracing.viewer import write_html
    base = args.result_root / args.selection_id / "B0" / args.split
    paths = [base / name for name in args.run_id]
    output = args.output or (paths[0] / "trace-explorer.html" if len(paths) == 1
                             else base / "trace-explorer-combined.html")
    result = write_html(paths, output)
    print(f"Trace Explorer: {result}")
    return 0


def serve(args) -> int:
    """Serve a live-refreshing local read-only Trace Explorer."""
    from scr.tracing.server import serve_trace_explorer
    base = args.result_root / args.selection_id / "B0" / args.split
    serve_trace_explorer(base, port=args.port, run_ids=args.run_id)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="B0 difficulty-sampled original Mini-Dev evaluation")
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("prepare", "infer", "score", "visualize", "serve"):
        command = sub.add_parser(action)
        command.add_argument("--selection-id", required=True)
        command.add_argument("--dataset-root", type=Path, default=DEFAULT_ROOT)
        command.add_argument("--result-root", type=Path, default=DEFAULT_RESULT_ROOT)
        if action == "prepare":
            command.add_argument("--seed", type=int, default=42)
            command.add_argument("--force", action="store_true",
                                 help="Replace an unused selection only; refuse if any run or unknown file exists")
            command.add_argument("--total-questions", type=int)
            command.add_argument("--dev-ratio", type=float, default=0.8)
            command.add_argument("--difficulty-ratio", default="auto")
            for split in ("dev", "test"):
                for level in LEVELS:
                    command.add_argument(f"--{split}-{level}", type=int)
        else:
            command.add_argument("--split", required=True, choices=("dev", "test"))
            if action == "serve":
                command.add_argument("--run-id", nargs="+", help="Optional run IDs; default: discover all")
                command.add_argument("--port", type=int, default=8765)
            else:
                command.add_argument("--run-id", required=True,
                                     nargs="+" if action == "visualize" else None)
            if action == "score":
                command.add_argument("--timeout-seconds", type=float, default=DEFAULT_SQL_TIMEOUT_SECONDS,
                                     help="Per-query timeout for reference and predicted SQL")
            if action == "visualize":
                command.add_argument("--output", type=Path)
            if action == "infer":
                command.add_argument("--prompt-variant", choices=("baseline", "generalized-v1"),
                                     default="baseline", help="Versioned system instructions; baseline is unchanged")
                command.add_argument("--reasoning-effort", choices=("none", "low", "medium", "high", "xhigh", "max"),
                                     help="Explicit SIWC effort; omitted preserves provider default")
                command.add_argument("--preview-rows", type=int, default=20)
                command.add_argument("--provider", choices=DEFAULT_MODELS, default="nvidia")
                command.add_argument("--model", help="Provider-specific model ID; required for OpenAI and ChatGPT SIWC")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    for label in ("selection_id", "run_id"):
        value = getattr(args, label, None)
        if value is not None and any(not SAFE_ID.fullmatch(item) for item in
                                     (value if isinstance(value, list) else [value])):
            parser.error(f"--{label.replace('_', '-')} must be 1-80 path-safe characters")
    if args.action == "infer" and not 1 <= args.preview_rows <= 200:
        parser.error("--preview-rows must be 1..200")
    try:
        return {"prepare": prepare, "infer": infer, "score": score, "visualize": visualize, "serve": serve}[args.action](args)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
