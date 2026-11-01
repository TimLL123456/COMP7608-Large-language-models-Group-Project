# KORA-03 — BIRD Execution Accuracy (EX) Guide

> **Beginner scoring policy:** This is original BIRD Mini-Dev with a *local* 400-dev/100-test split, not the hidden leaderboard. Strict EX compares executed result sets with no numeric tolerance. Prior 16/16 *selected-case* official scorer parity is not full parity. Extra safety/timeout/row limits can make edge cases differ. Keep disputed gold semantics and numeric gaps as **separate diagnostics**; do not change gold SQL or EX.

**Goal:** Understand how KORA checks whether generated Text-to-SQL answers are correct. The evaluator reads **saved predictions**; it does **not** call an LLM.

**Normal B0 workflow:** Follow [Prepare → Infer → Score](bird-b0.md). You **do not need** to run the low-level evaluator separately.

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

For B1–B4, reuse the **same evaluator, dataset split and question IDs** to make comparisons fair. See the [agent development guide](agent-development.md).

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
- SQL is executed **read-only** (SQLite authorizer), with default scorer timeout **30 seconds** and maximum **100,000 result rows**. This is **different** from the agent's `infer --preview-rows`.
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

For dataset versions and installation, see [KORA-02](bird-setup.md). For commands and trace viewing, see [KORA-05 B0](bird-b0.md).
