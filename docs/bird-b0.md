# KORA-05 — B0 Text-to-SQL Beginner Tutorial

**Goal:** Run the existing B0 agent from a small sample to a scored result, then inspect its trace.

**Workflow:** Dataset → **Prepare** → **Infer** → **Score** → **Visualize (optional)**.

**Beginner terms:** *Dataset* means questions and SQLite databases; *inference* means the LLM generating SQL; *gold SQL* is evaluator-only reference SQL; *EX* means execution accuracy (exactly matching result sets). Successfully executed SQL can still have EX=0.

> **Run from the cloned group-repository root** where `pyproject.toml` is located. Complete [BIRD setup](bird-setup.md) first.

## 1. First-time checks — Required

**Why:** Ensure the project dependencies and dataset are available.

```powershell
Test-Path .\pyproject.toml       # Expected: True
uv sync
uv run python -m scr.datasets.setup_bird --verify-only
```

**Expected:** Dataset verification reports `PASS`, 500 questions and 11 SQLite databases. If data is missing, run [dataset setup](bird-setup.md) first; `--verify-only` does not download data.

To run NVIDIA inference, set the key in **your local PowerShell session**:

```powershell
$secureKey = Read-Host "NVIDIA API key" -AsSecureString
$env:NVIDIA_API_KEY = [System.Net.NetworkCredential]::new("", $secureKey).Password
Remove-Variable secureKey
```

**Security:** Never commit API keys, downloaded database files or raw traces. Running inference may use API credits. `prepare`, `score` and `visualize` do **not** make NVIDIA model calls.

**Provider note:** The current B0 inference CLI uses NVIDIA. Other providers exist in the shared model factory but **do not imply** a `--provider` flag on this CLI.

## 2. Prepare sample questions — Required

**What:** Choose a repeatable sample. **Why:** Start small before expensive inference.

```powershell
uv run python -m scr.cli.run_bird_b0_eval prepare `
  --total-questions 5 `
  --dev-ratio 0.8 `
  --seed 42 `
  --selection-id sample-001
```

**Expected:** `dev=4, test=1`; files appear under:

```text
scr/evaluation/result/sample-001/
├── dev.jsonl
├── test.jsonl
└── selection_manifest.json
```

| Parameter | Meaning | First-trial value |
| --- | --- | --- |
| `--total-questions` | Total sample size | `5` |
| `--dev-ratio` | Share sampled from the existing dev pool | `0.8` |
| `--seed` | Repeatable sampling | `42` |
| `--selection-id` | Name of the saved sample | `sample-001` |
| `--difficulty-ratio` | Difficulty weighting | **Optional**; default `auto` |

Sampling never reads or sends gold SQL to the agent. The underlying fixed dataset split stays **400 dev / 100 local test**. A five-question sample is just a **smoke test**, not a benchmark accuracy claim.

## 3. Run B0 inference — Required

**What:** Let the agent inspect schemas, call read-only SQL tools and generate an answer. **Why:** Create predictions that can be independently scored.

```powershell
uv run python -m scr.cli.run_bird_b0_eval infer `
  --selection-id sample-001 `
  --split dev `
  --run-id run-001 `
  --preview-rows 20
```

**Expected:** One prediction and one trace record per selected **dev** question (4 in this example), saved as:

```text
scr/evaluation/result/sample-001/B0/dev/run-001/
├── predictions.jsonl
├── traces.jsonl
└── inference_manifest.json
```

| Parameter | Meaning |
| --- | --- |
| `--selection-id` | The saved selection from Step 2 |
| `--split dev` | Development questions; `test` is for later frozen evaluation |
| `--run-id` | A **new** run folder; existing runs cannot be overwritten |
| `--preview-rows 20` | Number of SQLite rows the **agent** may preview (1–200); not the EX scoring limit |

**Current B0:** NVIDIA `nvidia/nemotron-3.5-super-vl-120b-a12b`, 300-second timeout **per model API request**, 16,384 maximum completion tokens, and a **documented but not enforced** 262,144-token hosted context budget. The agent permits up to 20 model calls, 20 tool calls, 20 SQL executions and LangGraph recursion limit 100. A single question can take more than five minutes because the timeout is **per request**. Deep Agents retains its normal context management.

An API timeout produces `predicted_sql: null`, not proof the model generated incorrect SQL. `inference_manifest.json` records the settings for later comparisons.

### Final answer format — Advanced reference

B0 requires a single `SELECT` / `WITH` SQL query between delimiters:

```text
Final SQL Query:
"""
SELECT ...;
"""
```

The agent can explore tables and retry read-only SQL, but only a valid completed final answer is saved as a prediction. Gold SQL never enters the prompt.

## 4. Score the predictions — Required for EX evaluation

**What:** Run the saved SQL against reference result sets. **Why:** Measure **Execution Accuracy (EX)**, not just whether SQL executed.

```powershell
uv run python -m scr.cli.run_bird_b0_eval score `
  --selection-id sample-001 `
  --split dev `
  --run-id run-001
```

**Expected:** New files under:

```text
scr/evaluation/result/sample-001/B0/dev/run-001/scores/
├── report.md            # Start here: readable result summary
├── summary.json         # Overall/per-difficulty metrics
├── per_question.csv     # Investigate individual questions
├── per_question.jsonl
└── run_manifest.json
```

**How to read:** `EX=1` means the predicted SQL produced the correct result set; `EX=0` means wrong/missing/failed SQL. A successful intermediate tool call or executable final SQL **does not guarantee EX=1**. Missing results stay in the denominator.

This is a custom **local Mini-Dev** evaluation, not the official BIRD hidden leaderboard. Learn more in [EX scoring, examples and fairness](bird-evaluation.md).

## 5. Visualize the agent trace — Optional

**What:** Build a self-contained HTML graph from saved traces. **Why:** Diagnose why a question succeeded, failed or timed out.

```powershell
uv run python -m scr.cli.run_bird_b0_eval visualize `
  --selection-id sample-001 `
  --split dev `
  --run-id run-001
```

**Expected:** `scr/evaluation/result/sample-001/B0/dev/run-001/trace-explorer.html`. Open it in Chrome or Edge. It does not call NVIDIA or run SQL.

**Main controls:** Select a question; expand model/tool nodes; switch **Readable / Raw** for each result; resize nodes; set top-level width (default 1000px); pan/zoom and Go to end; search errors. SQL output appears as tables when structured data is present.

### Live Refresh — Optional (advanced)

**When:** You want to monitor new JSON/JSONL trace files or runs without reopening the browser.

```powershell
uv run python -m scr.cli.run_bird_b0_eval serve `
  --selection-id sample-001 `
  --split dev `
  --port 8765
```

Open `http://127.0.0.1:8765`. **Refresh** rescans on demand and **Auto refresh** checks every five seconds. The local service is **read-only** and binds to `127.0.0.1`. A standalone static HTML snapshot cannot auto-discover newly written files.

## 6. Optional debugging and advanced options

**Single-question debugging (Optional):** Set `QUESTION_ID` in `scr/baselines/bird_b0.py` and run:

```powershell
uv run python scr/baselines/bird_b0.py
```

**Different sample weights (Optional):** Pass `--difficulty-ratio 5:3:2` to `prepare`. The default is `auto`; very small samples may omit difficulty levels.

**Explicit difficulty counts (Advanced):** Use the `--dev-simple`, `--dev-moderate`, `--dev-challenging` and matching `--test-...` flags **instead of** `--total-questions`. Do not mix the two selection modes.

**Replace an unused selection (Optional):** `prepare --force` works only if that selection contains exactly `dev.jsonl`, `test.jsonl` and `selection_manifest.json` with no runs, extra files or symlinks. A selection with inference results is protected; use a **new selection ID**.

**Multiple static runs (Optional):** `visualize --run-id run-001 run-002` makes a combined HTML, or use `--output` to select a filename.

**Inspect failures:** Use `traces.jsonl` for model/tool errors, `predictions.jsonl` for SQL or `null`, `per_question.csv` for EX status, and `report.md` for the summary. Do not mistake a transport `ReadTimeout` for SQL reasoning failure.

| Problem | First action |
| --- | --- |
| `No pyproject.toml found` | Use the project root, not `scr/cli/` |
| `NVIDIA_API_KEY required` | Set the key in your local session (Step 1) |
| `Unknown selection` | Run `prepare` first, using the same selection ID |
| Run already exists | Use a **new** `--run-id` |
| `ReadTimeout` | Inspect the trace; the configured 300 seconds is **per model request** |
| `Invalid final answer` | Inspect the model's final message and expected SQL delimiters |
| `Gold SQL preflight failed` | Check dataset integrity; do **not** count the evaluation as a valid model score |

**For B1–B4 developers:** Read [Framework reuse guide](agent-development.md). Do not duplicate the loader, read-only SQL adapter or shared evaluator. Keep the same question IDs and evaluator when comparing agents.

**Boundaries:** Inference/traces can include database content. The official EX scorer uses separate, bounded read-only SQL execution; it is not the same as the agent's `--preview-rows`. Use the local `test` split only after finalizing settings on `dev`.
