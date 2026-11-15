"""Compare already-scored B0/generalized-v1 and Metadata Agent BIRD runs.

Read-only: no model calls, no rescoring, no mutation of original results.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import mean


MEASURES = ("tool_calls", "model_calls", "sql_calls", "input_tokens",
            "output_tokens", "cached_input_tokens", "reasoning_tokens", "latency_ms")


def _load(path: Path) -> dict[int, dict]:
    records = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        qid = row["question_id"]
        if qid in records:
            raise ValueError(f"Duplicate question ID {qid} in {path}")
        records[qid] = row
    if not records:
        raise ValueError(f"No rows in {path}")
    return records


def _format_ratio(correct: int, total: int) -> str:
    return f"{correct}/{total} ({correct / total:.1%})" if total else "n/a"


def compare(control: Path, candidate: Path, output: Path) -> str:
    a, b = _load(control), _load(candidate)
    if set(a) != set(b):
        raise ValueError("Control and Metadata must contain identical question IDs")
    for qid in a:
        if a[qid]["db_id"] != b[qid]["db_id"] or a[qid]["difficulty"] != b[qid]["difficulty"]:
            raise ValueError(f"Question {qid} has mismatched database/difficulty")
    ids = sorted(a)
    ca = sum(int(a[i]["ex"]) for i in ids)
    cb = sum(int(b[i]["ex"]) for i in ids)
    gain = [i for i in ids if not a[i]["ex"] and b[i]["ex"]]
    regress = [i for i in ids if a[i]["ex"] and not b[i]["ex"]]
    lines = [
        "# BIRD — Control vs Metadata Agent",
        "",
        f"Control scores: \u0060{control}\u0060",
        f"Metadata scores: \u0060{candidate}\u0060",
        "",
        "## Execution accuracy (EX)",
        "",
        "| Variant | Correct | EX |",
        "| --- | ---: | ---: |",
        f"| Control | {ca}/{len(ids)} | {ca / len(ids):.2%} |",
        f"| Metadata | {cb}/{len(ids)} | {cb / len(ids):.2%} |",
        "",
        f"**EX change:** {(cb - ca) / len(ids):+.2%} ({cb-ca:+d} questions).",
        f"**Fixed:** {len(gain)}; **regressed:** {len(regress)}.",
        "",
        "## Accuracy by difficulty and database",
        "",
        "| Group | Control EX | Metadata EX |",
        "| --- | ---: | ---: |",
    ]
    groups = defaultdict(list)
    for i in ids:
        groups["difficulty:" + a[i]["difficulty"]].append(i)
        groups["database:" + a[i]["db_id"]].append(i)
    for name, group in sorted(groups.items()):
        x = sum(int(a[i]["ex"]) for i in group)
        y = sum(int(b[i]["ex"]) for i in group)
        lines.append(f"| {name} | {_format_ratio(x, len(group))} | {_format_ratio(y, len(group))} |")
    lines.extend([
        "", "## Efficiency (observed records only)", "",
        "| Measure | Control mean (observed) | Metadata mean (observed) |",
        "| --- | ---: | ---: |",
    ])
    for key in MEASURES:
        x = [a[i].get(key) for i in ids if type(a[i].get(key)) in (int, float)]
        y = [b[i].get(key) for i in ids if type(b[i].get(key)) in (int, float)]
        left = f"{mean(x):.2f} (n={len(x)})" if x else "n/a"
        right = f"{mean(y):.2f} (n={len(y)})" if y else "n/a"
        lines.append(f"| {key} | {left} | {right} |")
    lines.extend([
        "", "## Changed questions", "",
        f"**Corrected IDs:** {', '.join(map(str, gain)) or '(none)'}",
        "",
        f"**Regressed IDs:** {', '.join(map(str, regress)) or '(none)'}",
        "",
        "## Interpretation guardrails", "",
        "- Both runs must use the same question IDs, source dataset and model settings. "
        "This script validates IDs/db/difficulty but cannot independently verify external model configuration.",
        "- Metadata Test performance depends on question order and knowledge accumulated earlier "
        "in the same experiment. This is continual same-database reuse, not a frozen holdout.",
        "- Token/latency means exclude missing values; inspect observed-call counts for partial data.",
        "- Inspect trace and metadata-operation logs before attributing any EX gain to particular notes.",
        "",
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return str(output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-scores", type=Path, required=True,
                        help="Control scores/per_question.jsonl")
    parser.add_argument("--metadata-scores", type=Path, required=True,
                        help="Metadata scores/per_question.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    print(compare(args.control_scores, args.metadata_scores, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
