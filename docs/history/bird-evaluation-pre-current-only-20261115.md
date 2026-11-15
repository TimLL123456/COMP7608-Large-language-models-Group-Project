# KORA-03 — BIRD Execution Accuracy (EX) Guide

> **Dataset update — 8 November 2026:** Use **Mini-Dev 2026** for new harness experiments. The original Mini-Dev instructions and archived 59.8% EX remain historical reproduction evidence. See [dataset versions and migration](bird-dataset-versions-pre-current-only-20261115.md) for the Docker-free download command, changed IDs, and fresh evaluation workflow. Full Dev 20251106 is a separate optional benchmark.

**Goal:** Understand how KORA checks whether generated Text-to-SQL answers are correct. The evaluator reads **saved predictions**; it does **not** call an LLM.

**Normal B0 workflow:** Follow [Prepare → Infer → Score](bird-b0-pre-current-only-20261115.md). You **do not need** to run the low-level evaluator separately.

## Mini-Dev 2026: B0 scoring

The B0 runner saves its full `inference_manifest.json` automatically. Use the [current 2026 walkthrough](bird-b0-pre-current-only-20261115.md#mini-dev-2026-current-workflow), passing `--dataset-root data/bird/mini-dev-2026` to prepare, infer and score. The original examples below retain their old defaults.

## Mini-Dev 2026: independent predictions

For independent B1–B4 generators, the scorer additionally requires `inference_manifest.json` beside `predictions.jsonl`, with a `dataset_manifest` equal to the installed dataset manifest. Record it when starting generation against that dataset; it is not a way to relabel old predictions. B0 has a richer manifest and should continue using its runner rather than this minimal example.

Illustrative Python integration for a new independent B1 run (paths are examples):

```python
import json
from pathlib import Path
from scr.datasets.bird import BirdDataset

bird = BirdDataset("data/bird/mini-dev-2026")
output = Path("results/minidev2026/B1/run-001")
output.mkdir(parents=True, exist_ok=False)  # refuse to reuse a run
with (output / "inference_manifest.json").open("x", encoding="utf-8") as stream:
    json.dump({"dataset_manifest": bird.manifest}, stream, indent=2)
# Your generator now uses bird.get_split("dev") / bird.get_agent_input(qid),
# and writes predictions.jsonl in this output directory.
# Each line needs question_id, db_id and predicted_sql (string or null).
# Never pass Gold SQL/reference files to the model.
```

After your generator has produced the predictions, score them without model calls:

```bash
uv run python -m scr.cli.evaluate_bird --dataset-root data/bird/mini-dev-2026 --variant B1 --split dev --predictions results/minidev2026/B1/run-001/predictions.jsonl --output-dir results/minidev2026/B1/scores --run-id run-001
```

The example does not generate predictions itself. Use a new output directory for each run. For B2–B4 substitute the variant and paths. Missing/wrong dataset provenance is rejected before scoring. Missing individual predictions score zero; use `--question-ids` for an explicitly labelled smoke subset. Do not attach a new manifest to predictions generated for another release.

## Original-release examples and shared EX rules

The remaining command examples retain original Mini-Dev defaults. The EX definition and safety rules apply to both supported releases; manual 2026 scoring additionally requires the provenance described above.

## 1. What is EX?

**Execution Accuracy (EX)** compares the **result returned by your SQL** with the result returned by the reference (gold) SQL on the *same SQLite database*.

```text
Question → Agent final SQL → SQLite result ──┐
                                              ├─ Compare results → EX = 1 or 0
             Gold SQL → SQLite result ────────┘
```

| Example (illustrative, not real BIRD questions) | Gold result | Predicted result | EX |
| --- | --- | --- | ---: |
| Q1 | `[(100,)]` | `[(100,)]` | 1 |
| Q2 | `[(200,)]` | `[(150,)]` | 0 |
| Q3 | `[(300,)]` | SQL error | 0 |

**Example score:** 1 correct / 3 questions = **33.33% EX**.

- Row order and duplicate rows are ignored: complete result tuples are compared as **sets**.
- Column/tuple order **still matters**; two empty result sets match.
- Wrong SQL, missing final SQL, unsafe statements, errors or timeouts score **0**.
- **Reference SQL preflight:** The evaluator first checks every selected gold SQL. If any gold query fails, the **entire evaluation is invalid**, not a model EX score.

**Important:** A valid `SELECT` statement or a successful SQL tool call is not necessarily the correct answer.

## 2. Run B0 evaluation — Required for a B0 benchmark

**What:** Compare the predictions saved by `infer` against reference outputs.

```powershell
uv run python -m scr.cli.run_bird_b0_eval score `
  --selection-id sample-001 `
  --split dev `
  --run-id run-001
```

**Expected:**

```text
scr/evaluation/result/sample-001/B0/dev/run-001/scores/
├── report.md               # Read this first
├── summary.json            # Overall EX and breakdown by difficulty
├── per_question.csv        # Investigate individual questions
├── per_question.jsonl
└── run_manifest.json       # Scorer configuration and provenance
```

**Read `report.md` first.** Use `per_question.csv` to identify which questions returned incorrect, missing or timed-out SQL. Use `traces.jsonl` from the inference run to investigate why.

For B1–B4, reuse the **same evaluator, dataset split and question IDs** to make comparisons fair. See the [agent development guide](agent-development-pre-current-only-20261115.md).

## 3. Which metrics matter?

| Metric | Meaning |
| --- | --- |
| **EX** | Did final SQL return the correct result? **Primary accuracy metric** |
| Final SQL generation rate | How often the agent produced a valid final SQL statement |
| Final SQL execution rate | How often generated final SQL ran successfully (not necessarily correctly) |
| Agent SQL tool success rate | How often intermediate `execute_sql` tool calls succeeded |
| Efficiency | Observed tokens, model/tool calls, latency and SQL execution time |
| Coverage | How many intended questions received prediction records |

**Example:** An API `ReadTimeout` can lead to missing final SQL and EX=0 in an end-to-end benchmark; report timeout counts separately so the team can distinguish service reliability from SQL reasoning quality.

Token usage can be unavailable (e.g., in nested subagent activity). Use `null` / `n/a`, **not zero**, for missing observations. Latency and execution timings in outputs are recorded in **milliseconds**.

## 4. Manual prediction scoring — Advanced / Optional

**When:** You're building B1/B2/B3/B4 or want to score your own saved prediction JSONL without the B0 `infer` wrapper.

The independent scorer accepts one JSON object per line with real `question_id`, matching `db_id` and `predicted_sql` (a SQL string or `null`).

```json
{"question_id": 2000, "db_id": "demo_0", "predicted_sql": "SELECT COUNT(*) FROM records"}
```

This is **format illustration only**. The IDs are not an actual BIRD record; use IDs and databases from your installed split.

```powershell
uv run python scr/cli/evaluate_bird.py --help

# Example: use your own JSONL with actual dev IDs
uv run python scr/cli/evaluate_bird.py `
  --variant B1 `
  --split dev `
  --predictions results/predictions/b1.jsonl `
  --output-dir results/bird/B1 `
  --run-id b1-dev-001
```

`results/predictions/b1.jsonl` is an **example path**, not an included file. A small-subset run should set `--question-ids` to an explicit comma-separated list of genuine IDs and is labeled not full split. Scorer options `--timeout-seconds` and `--max-result-rows` control SQL execution limits.

The **low-level** scorer allows missing predictions and marks them EX=0; the **B0 wrapper** requires complete prediction records (including explicit `null` results), validated manifests and hashes before scoring. Do not run both interfaces for the same B0 experiment.

## 5. Reproducible comparisons and safety

**Before comparing B0–B4:** Keep the annotation/database version, dev/test membership, question IDs, evidence policy, evaluator settings and SQL safety the same. Record changes to models, prompts, tool limits, tokens, and timeouts in each experiment manifest. Tune only on `dev` and freeze choices before using local `test`.

- This project's **original BIRD Mini-Dev** has 500 questions and 11 SQLite databases, split locally into 400 dev and 100 test questions. Local `test` is **not** BIRD's official hidden leaderboard test and may share database schemas with dev.
- SQL is executed **read-only** (SQLite authorizer), with default scorer timeout **300 seconds (5 minutes)** and maximum **100,000 result rows**. This is **different** from the agent's `infer --preview-rows`.
- Gold references are used **only by the evaluator**, never sent to an agent, router, planner or repair tool. This is a **code convention**, not an operating-system security boundary.
- The scorer validates question IDs and database IDs. Its output also includes full-difficulty EX, per-question status, available token/tool metrics and scorer provenance.
- The reported **16/16 matched selected-case** upstream EX comparisons are diagnostic evidence, **not** verified full-dataset parity or a B0 model accuracy score.
- Soft F1 and R-VES are **optional future metrics**; they are not required for a first EX run.

### Provenance and reference — Advanced

- `dataset_manifest.json`: pinned sources, SQLite file hashes, fixed 400/100 split.
- `selection_manifest.json`: selected question IDs and seed.
- `inference_manifest.json`: prediction checksum, model/settings, run identity.
- `run_manifest.json`: scorer version, SQL limits, input source and evaluated IDs.
- [Pinned BIRD upstream EX reference (commit abd11b6)](https://github.com/bird-bench/mini_dev/blob/abd11b6db92a1c9f809b32f7564c7c71b34d67f0/evaluation/evaluation_ex.py). It pairs its submission/gold SQL positionally; our adapter validates question IDs first. Extra SQLite time/row limits may affect strict upstream parity.

For dataset versions and installation, see [KORA-02](bird-setup-pre-current-only-20261115.md). For commands and trace viewing, see [KORA-05 B0](bird-b0-pre-current-only-20261115.md).
