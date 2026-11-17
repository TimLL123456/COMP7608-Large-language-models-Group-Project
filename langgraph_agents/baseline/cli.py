"""B0 parity-first LangGraph prepare/infer/score/visualize commands."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from scr.baselines import bird_b0 as b0
from scr.baselines.common import DEFAULT_MODELS
from scr.baselines.sqlite_readonly import DEFAULT_SQL_TIMEOUT_SECONDS
from scr.cli import run_bird_b0_eval as original
from scr.datasets.bird import DEFAULT_ROOT
from scr.evaluation.bird import load_predictions, validate_predictions
from langgraph_agents.baseline.runner import VARIANT, infer


def score(args) -> int:
    from scr.cli.evaluate_bird import run as evaluate

    folder, dataset, selected = original._selection(args)
    run_dir = folder / VARIANT / args.split / args.run_id
    predictions = run_dir / "predictions.jsonl"
    manifest_path = run_dir / "inference_manifest.json"
    if not predictions.is_file() or not manifest_path.is_file():
        raise ValueError(f"Run predictions and manifest required: {run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = load_predictions(predictions)
    validate_predictions(records, selected)
    expected = {
        "completed": True, "agent_variant": VARIANT,
        "selection_id": args.selection_id, "split": args.split, "run_id": args.run_id,
        "expected_questions": len(selected),
        "question_ids": [q["question_id"] for q in selected],
        "prediction_sha256": sha256(predictions.read_bytes()).hexdigest(),
        "selection_sha256": sha256((folder / "selection_manifest.json").read_bytes()).hexdigest(),
        "dataset_manifest": dataset.manifest,
        "output_format_version": b0.OUTPUT_FORMAT_VERSION,
    }
    if any(manifest.get(k) != v for k, v in expected.items()):
        raise ValueError("Incomplete or mismatched inference manifest/predictions")
    if manifest.get("provider") not in DEFAULT_MODELS or not manifest.get("model"):
        raise ValueError("Unsupported or missing provider/model")
    if any(row.get("provider") != manifest["provider"] or row.get("model") != manifest["model"]
           for row in records):
        raise ValueError("Incomplete or mismatched prediction provider/model")
    if (run_dir / "scores").exists():
        raise ValueError(f"Scores already exist: {run_dir / 'scores'}")
    outcome = evaluate([
        "--variant", VARIANT, "--split", args.split,
        "--predictions", str(predictions), "--dataset-root", str(args.dataset_root),
        "--output-dir", str(run_dir), "--run-id", "scores",
        "--question-ids", ",".join(str(row["question_id"]) for row in selected),
        "--timeout-seconds", str(args.timeout_seconds),
    ])
    if outcome != 0:
        return outcome
    score_dir = run_dir / "scores"
    summary = json.loads((score_dir / "summary.json").read_text(encoding="utf-8"))
    lines = [
        "# LangGraph B0 Evaluation Report", "",
        f"Split: {args.split} (selected subset; NOT official hidden-test EX)",
        f"Questions: {summary['total']}",
        f"EX: **{summary['correct']}/{summary['total']} ({summary['ex']:.2%})**", "",
        "## Accuracy by difficulty", "",
        "| Difficulty | Correct | Total | EX |", "|---|---:|---:|---:|",
    ]
    for difficulty, stat in sorted(summary["by_difficulty"].items()):
        lines.append(f"| {difficulty} | {stat['correct']} | {stat['total']} | {stat['ex']:.2%} |")
    lines += ["", "## Inference and SQL execution", "",
              "| Metric | Total | Mean | P50 | P95 | Observed |",
              "|---|---:|---:|---:|---:|---:|"]
    for key, stat in summary.get("performance", {}).items():
        if not isinstance(stat, dict):
            lines.append(f"| {key} | {stat} | — | — | — | — |")
            continue
        def label(field):
            value = stat.get(field)
            return f"{value:.2f}" if isinstance(value, (int, float)) else "n/a"
        lines.append(f"| {key} | {label('total')} | {label('mean')} | "
                     f"{label('p50')} | {label('p95')} | {stat.get('observed', 0)} |")
    lines += ["", "## Per-question scores", "",
              "| Question | Difficulty | EX | Status | Model turns | Tool calls | SQL calls | Inference ms |",
              "|---|---|---:|---|---:|---:|---:|---:|"]
    for line in (score_dir / "per_question.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        def show(key):
            return str(row[key]) if row.get(key) is not None else "n/a"
        lines.append(f"| {row['question_id']} | {row['difficulty']} | {row['ex']} | "
                     f"{row['status']} | {show('model_calls')} | {show('tool_calls')} | "
                     f"{show('sql_calls')} | {show('latency_ms')} |")
    lines += ["", "Usage fields may be partial; unavailable does not mean zero.",
              "Agent SQL execution success does not guarantee final SQL EX.",
              "Reference SQL is available only to the independent scorer."]
    (score_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Evaluation report: {score_dir / 'report.md'}")
    return 0


def visualize(args) -> int:
    from scr.tracing.viewer import write_html
    base = args.result_root / args.selection_id / VARIANT / args.split
    paths = [base / run_id for run_id in args.run_id]
    target = args.output or (paths[0] / "trace-explorer.html" if len(paths) == 1
                             else base / "trace-explorer-combined.html")
    write_html(paths, target)
    print(f"Trace Explorer: {target}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="LangGraph B0 baseline — prepare, infer, score, visualize")
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("prepare", "infer", "score", "visualize"):
        command = sub.add_parser(action)
        command.add_argument("--selection-id", required=True)
        command.add_argument("--dataset-root", type=Path, default=DEFAULT_ROOT)
        command.add_argument("--result-root", type=Path, default=original.DEFAULT_RESULT_ROOT)
        if action == "prepare":
            command.add_argument("--seed", type=int, default=42)
            command.add_argument("--force", action="store_true")
            command.add_argument("--total-questions", type=int)
            command.add_argument("--dev-ratio", type=float, default=0.8)
            command.add_argument("--difficulty-ratio", default="auto")
            for split in ("dev", "test"):
                for level in original.LEVELS:
                    command.add_argument(f"--{split}-{level}", type=int)
            continue
        command.add_argument("--split", required=True, choices=("dev", "test"))
        command.add_argument("--run-id", required=True, nargs="+" if action == "visualize" else None)
        if action == "infer":
            command.add_argument("--prompt-variant", choices=b0.PROMPT_VARIANTS, default="baseline")
            command.add_argument("--reasoning-effort",
                                 choices=("none", "low", "medium", "high", "xhigh", "max"),
                                 default=None)
            command.add_argument("--preview-rows", type=int, default=20)
            command.add_argument("--provider", choices=DEFAULT_MODELS, default="chatgpt-siwc")
            command.add_argument("--model", default=None)
        elif action == "score":
            command.add_argument("--timeout-seconds", type=float, default=DEFAULT_SQL_TIMEOUT_SECONDS)
        elif action == "visualize":
            command.add_argument("--output", type=Path)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    for label in ("selection_id", "run_id"):
        value = getattr(args, label, None)
        if value is not None and any(not original.SAFE_ID.fullmatch(item)
                                     for item in (value if isinstance(value, list) else [value])):
            parser.error(f"--{label.replace('_', '-')} must be 1-80 path-safe characters")
    if args.action == "infer":
        if not 1 <= args.preview_rows <= 200:
            parser.error("--preview-rows must be 1..200")
        if args.provider == "chatgpt-siwc":
            args.model = args.model or "gpt-6-luna"
            args.reasoning_effort = args.reasoning_effort if args.reasoning_effort is not None else "none"
    try:
        return {"prepare": original.prepare, "infer": infer,
                "score": score, "visualize": visualize}[args.action](args)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
