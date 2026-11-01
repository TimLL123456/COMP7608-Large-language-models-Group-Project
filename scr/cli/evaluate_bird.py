"""Score saved KORA SQL predictions on the original BIRD Mini-Dev SQLite data.

Run from the Group Project directory: uv run python scr/cli/evaluate_bird.py --help
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

# Direct script invocation from the project root (no editable package required).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scr.datasets.bird import BirdDataset, BirdEvaluationReferences, DEFAULT_ROOT  # noqa: E402
from scr.evaluation.bird import (USAGE_FIELDS, VARIANTS, evaluate_predictions,
                                 load_predictions)  # noqa: E402


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate saved B0-B4 SQL with original BIRD Mini-Dev EX")
    parser.add_argument("--variant", required=True, choices=sorted(VARIANTS))
    parser.add_argument("--split", required=True, choices=("dev", "test", "heldout"),
                        help="dev/test; heldout is a deprecated alias for test")
    parser.add_argument("--predictions", required=True, type=Path, help="JSONL with question_id, db_id and predicted_sql")
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", help="Explicit path-safe run name (otherwise UTC timestamp)")
    parser.add_argument("--question-ids", help="Optional comma-separated smoke-test IDs; output is not full-split EX")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--max-result-rows", type=int, default=100_000)
    args = parser.parse_args(argv)
    dataset = BirdDataset(args.dataset_root)
    args.split = "test" if args.split == "heldout" else args.split
    questions = dataset.get_split(args.split)
    if args.question_ids is not None:
        try:
            ids = [int(x.strip()) for x in args.question_ids.split(",")]
        except ValueError as exc:
            parser.error(f"Invalid --question-ids: {exc}")
        if not ids or len(ids) != len(set(ids)):
            parser.error("--question-ids must contain unique IDs")
        wanted = set(ids)
        questions = [q for q in questions if q["question_id"] in wanted]
        if len(questions) != len(wanted):
            parser.error("--question-ids includes an ID outside the selected split")
    if args.timeout_seconds <= 0 or args.max_result_rows < 1:
        parser.error("Timeout and maximum result rows must be positive")
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}", run_id):
        parser.error("--run-id must be 1-80 path-safe characters")
    records, summary = evaluate_predictions(
        dataset, BirdEvaluationReferences(args.dataset_root), questions,
        load_predictions(args.predictions), variant=args.variant,
        timeout_seconds=args.timeout_seconds, max_result_rows=args.max_result_rows)
    summary.update({"split": args.split, "is_full_split": args.question_ids is None})
    destination = args.output_dir / run_id
    if destination.exists():
        parser.error(f"Output directory already exists: {destination}")
    destination.mkdir(parents=True)
    with (destination / "per_question.jsonl").open("w", encoding="utf-8") as stream:
        for row in records:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    fields = ["question_id", "db_id", "difficulty", "variant", "predicted_sql", "ex", "status", "sql_execution_ms", "gold_sql_execution_ms", *USAGE_FIELDS]
    with (destination / "per_question.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    (destination / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    manifest = {
        "run_id": run_id, "created_utc": datetime.now(timezone.utc).isoformat(),
        "variant": args.variant, "split": args.split, "is_full_split": args.question_ids is None,
        "question_ids": [item["question_id"] for item in questions],
        "dataset_root": str(dataset.root), "dataset_manifest": dataset.manifest,
        "predictions_file": str(args.predictions.resolve()),
        "timeout_seconds": args.timeout_seconds, "max_result_rows": args.max_result_rows,
        "scoring": "original Mini-Dev SQLite EX: set(row-tuples) equality",
        "upstream_repository": "bird-bench/mini_dev",
        "upstream_evaluator_commit": "abd11b6db92a1c9f809b32f7564c7c71b34d67f0",
        "scorer_version": "kora03-v1",
        "note": "Not an official hidden-test leaderboard score; source dataset is public Mini-Dev.",
    }
    (destination / "run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(f"{args.variant} {args.split}: {summary['correct']}/{summary['total']} EX={summary['ex']:.2%}")
    print(f"Results: {destination}")
    if args.question_ids is not None:
        print("SMOKE SUBSET ONLY: not comparable to a full split")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
