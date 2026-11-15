# KORA-05 — B0 Text-to-SQL Beginner Tutorial

> **Dataset update — 8 November 2026:** Use **Mini-Dev 2026** for new harness experiments. The original Mini-Dev instructions and archived 59.8% EX remain historical reproduction evidence. See [dataset versions and migration](bird-dataset-versions.md) for the Docker-free download command, changed IDs, and fresh evaluation workflow. Full Dev 20251106 is a separate optional benchmark.

**Goal:** Run the existing B0 agent from a small sample to a scored result, then inspect its trace.

**Workflow:** Dataset → **Prepare** → **Infer** → **Score** → **Visualize (optional)**.

> **Run from the project root** (the directory containing `pyproject.toml`). This tutorial assumes [BIRD setup](bird-setup.md) has passed.

## Mini-Dev 2026: current workflow

Run these commands from the project root on Linux or Windows. Python downloads the dataset without Docker:

```bash
uv sync
uv run python -m scr.datasets.setup_bird --release latest
uv run python -m scr.datasets.setup_bird --release latest --verify-only
uv run python -m scr.cli.run_bird_b0_eval prepare --dataset-root data/bird/mini-dev-2026 --total-questions 5 --dev-ratio 0.8 --seed 42 --selection-id minidev2026-smoke
```

Expect setup `PASS` (500 questions, 11 databases, local 400/100 split), then preparation `dev=4, test=1`. Preparation and verification make no model calls.

Configure your provider using the authentication instructions below before inference. This example uses the existing NVIDIA default and requires `NVIDIA_API_KEY`; inference consumes provider usage. Other provider examples below remain applicable: keep the new dataset root and selection ID when adapting them.

```bash
uv run python -m scr.cli.run_bird_b0_eval infer --dataset-root data/bird/mini-dev-2026 --selection-id minidev2026-smoke --split dev --run-id minidev2026-nvidia-001 --preview-rows 20
uv run python -m scr.cli.run_bird_b0_eval score --dataset-root data/bird/mini-dev-2026 --selection-id minidev2026-smoke --split dev --run-id minidev2026-nvidia-001
uv run python -m scr.cli.run_bird_b0_eval visualize --dataset-root data/bird/mini-dev-2026 --selection-id minidev2026-smoke --split dev --run-id minidev2026-nvidia-001
```

Inference writes four dev prediction/trace records under `scr/evaluation/result/minidev2026-smoke/B0/dev/minidev2026-nvidia-001/`. Scoring writes `scores/report.md`, per-question scores and provenance. Visualization writes `trace-explorer.html`. Scoring and visualization make no model calls. No particular accuracy is promised; five questions are only a smoke sample.

Use fresh selection/run IDs if these already exist. Never reuse original-dataset predictions or selections. Every evaluation command needs the explicit dataset root: its default still selects original Mini-Dev. See [manual 2026 prediction provenance](bird-evaluation.md#mini-dev-2026-independent-predictions) for independent B1–B4 generators.

## Archived B0 generalized-v1 evaluation — Mini-Dev 2026 (10 November 2026)

The archived 10 November B0 run evaluated **only `--prompt-variant generalized-v1`** on all 500 questions (400 Development / 100 local Test), scoring [319/500 (63.80%)](../evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/README.md). It did not rerun the original baseline prompt. Later independent MetadataDiscoveryV2, Self Reflection and Rubric Self Reflection studies are documented separately; this section is a historical B0 procedure, not a restriction on current experiments. The default `baseline` prompt remains available for historical reproduction.

The generalized prompt appends the frozen [R1–R8 addendum](../scr/baselines/prompts/generalized-v1.txt) to B0's original instructions. The [rule extraction](../evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/analysis-report/prompt-rule-extraction.md) is offline research only; do not expose its cases or Gold SQL to the runtime agent.

**Current B0 limits for either prompt variant: 40 model calls, 40 total tool calls, and 40 SQL executions per question.** SQL calls consume the shared 40-tool budget; these are not 40 additional SQL calls. Keep recursion limit 200, SQL timeout 300 seconds, preview rows 20, provider `chatgpt-siwc`, model `gpt-6-luna`, requested reasoning effort `none`, and seed 42. Do not tune the prompt during evaluation.

```powershell
# From the Group Project root after dataset verification and SIWC login.
uv run python -m scr.cli.run_bird_b0_eval prepare `
  --dataset-root data/bird/mini-dev-2026 `
  --total-questions 500 --dev-ratio 0.8 --difficulty-ratio auto --seed 42 `
  --selection-id generalized-v1-full500-40calls

# Two scored runs; 500 question inferences in total. No baseline inference.
foreach ($split in @("dev", "test")) {
  uv run python -m scr.cli.run_bird_b0_eval infer `
    --dataset-root data/bird/mini-dev-2026 --selection-id generalized-v1-full500-40calls `
    --split $split --run-id b0-generalized-v1-40calls `
    --provider chatgpt-siwc --model gpt-6-luna --reasoning-effort none `
    --prompt-variant generalized-v1 --preview-rows 20
  if ($LASTEXITCODE -ne 0) { throw "Generalized-v1 inference failed for $split" }
  uv run python -m scr.cli.run_bird_b0_eval score `
    --dataset-root data/bird/mini-dev-2026 --selection-id generalized-v1-full500-40calls `
    --split $split --run-id b0-generalized-v1-40calls
  if ($LASTEXITCODE -ne 0) { throw "Generalized-v1 scoring failed for $split" }
}
```

Check `selection_manifest.json`: all 500 unique official IDs must retain the original 400/100 split. Use fresh selection/run IDs and preserve historical files. Record `prompt_variant`, `system_prompt_sha256` and all three 40-call budgets in inference manifests. Failed questions remain in their split's denominator.

Report EX, per-database and query-category performance, observed tokens, model/tool/SQL calls, latency and failures for Dev, local Test and overall. Archived B0 scores may be shown as **descriptive historical comparisons**, not as a fresh matched prompt-only control. The previous Mini-Dev 2026 archive's configured limits are listed as 40/40/40 after a metadata alignment; its retained execution history records 20 SQL executions for 498 original cases and 40 for the two rerun cases. A documentation update does not regenerate those predictions. Preserve that history and any timeout differences when interpreting changes.

Local Test has already informed prior project discussion, so it is not an untouched hidden test. This evaluation is not an ablation of individual R1–R8 rules and cannot establish their separate causal effects.

## Original Mini-Dev reproduction and provider reference

The numbered walkthrough below retains the original dataset defaults and examples. Its bare commands do not select Mini-Dev 2026. For new experiments use the current workflow above; reuse the provider/authentication reference below as needed.

## 1. First-time checks — Required

**Why:** Ensure the project dependencies and dataset are available.

```powershell
Test-Path .\pyproject.toml       # Expected: True
uv sync
uv run python -m scr.datasets.setup_bird --verify-only
```

**Expected:** Dataset verification reports `PASS`, 500 questions and 11 SQLite databases.

To run NVIDIA inference, set the key in **your local PowerShell session**:

```powershell
$secureKey = Read-Host "NVIDIA API key" -AsSecureString
$env:NVIDIA_API_KEY = [System.Net.NetworkCredential]::new("", $secureKey).Password
Remove-Variable secureKey
```

**Security:** Never commit API keys, downloaded database files or raw traces. Running inference may use API credits. `prepare`, `score` and `visualize` do **not** make NVIDIA model calls.

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

**Current B0:** NVIDIA `nvidia/nemotron-3.5-super-vl-120b-a12b`, 300-second timeout **per model API request**, 16,384 maximum completion tokens, and a **documented but not enforced** 262,144-token hosted context budget. The agent permits up to 40 model calls, 40 tool calls, 40 SQL executions and LangGraph recursion limit 200. A single question can take more than five minutes because the timeout is **per request**. Deep Agents retains its normal context management.

The shared SQL execution default is **300 seconds (5 minutes) per query**,
for both agent read-only SQL tools and offline scoring of reference/predicted SQL.
The model API timeout above is a separate timer. `score --timeout-seconds 600`
overrides scoring only. New inference manifests record `agent_sql_timeout_seconds`.
The saved 8 November 40-call evaluation used the earlier 5-second agent SQL-tool
limit and explicitly selected 600-second scoring; its exported records remain unchanged.

An API timeout produces `predicted_sql: null`, not proof the model generated incorrect SQL. `inference_manifest.json` records the settings for later comparisons.

### Optional: Other model providers

The default `infer` command above still uses NVIDIA and the existing B0
settings. Add `--provider` and `--model` to opt into another model. Keep
the **same selection ID** for comparisons but use a **new run ID** per run.
`prepare`, `score`, and `visualize` remain provider-independent.

**OpenAI API** (separate API billing and key, NOT ChatGPT OAuth):

```powershell
$secureKey = Read-Host "OpenAI API key" -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new("", $secureKey).Password
Remove-Variable secureKey
uv run python -m scr.cli.run_bird_b0_eval infer `
  --selection-id sample-001 --split dev --run-id openai-001 `
  --provider openai --model YOUR_OPENAI_API_MODEL
```

**ChatGPT plan sign-in (experimental, single local account):**

```powershell
# Run once in the same desktop environment as the browser login:
uv run python -m scr.baselines.siwc_auth
# List the signed-in account's available model slugs:
uv run python -m scr.baselines.chatgpt_siwc
uv run python -m scr.cli.run_bird_b0_eval infer `
  --selection-id sample-001 --split dev --run-id siwc-001 `
  --provider chatgpt-siwc --model YOUR_LISTED_CHATGPT_MODEL
```

The OAuth adapter reuses the credential directory from
[`custom-harness`](https://github.com/TimLL123456/custom-harness):
`~/.config/siwc-harness-demo/`. Do not commit, copy, or log these tokens.
The loopback browser login is not suitable for a browser on a separate computer
or a shared multi-user VPS. Do not run concurrent copies with the same rotating
refresh token. If you lose eligibility or permission, inference fails explicitly
without switching to paid API calls. The Sign in with ChatGPT preview permits
eligible client-side function tools but rejects request parameters such as
`temperature`, `top_p`, and `max_output_tokens`. The adapter intentionally
omits those parameters. Availability and tool behavior require a live account test.
See [OpenAI SIWC preview limits](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).

**Other configured factories:** `--provider ollama|gemini|deepseek|nvidia`;
the existing local Ollama or API credentials are required. Use a provider's
actual supported model ID where needed.

**Evaluation fairness:** Use identical sampled question IDs and the same SQL
safety/scoring code. Report model, provider, observed tokens/tool calls, latency,
time-outs and any parameter differences. The NVIDIA hosted context budget is
not the context budget for OpenAI or SIWC. SIWC may not report costs: record them
as unknown rather than zero. Do not claim comparable sampling parameters
where the endpoint forbids them.

### Optional: Token usage and reported thinking metadata

The B0 runner records only fields actually available in each model response;
missing or invalid optional fields become `null` and do **not** fail inference.
This works for SIWC and other providers through LangChain's normalized usage
metadata where supported. For SIWC, `infer --reasoning-effort none` explicitly
requests the lowest GPT-6 Luna effort. Omit the flag to retain provider defaults.
The inference manifest records `requested_reasoning_effort` separately from
response-reported effort; acceptance does not prove the provider honored it.

| Observed field | Meaning | Saved where |
| --- | --- | --- |
| `input_tokens`, `output_tokens`, `total_tokens` | Token counts if available | `predictions.jsonl`, `traces.jsonl`, scoring |
| `cached_input_tokens` | Input tokens read from prompt cache, if reported | Same |
| `reasoning_tokens` | Output tokens used for reasoning, if reported | Same |
| `reasoning_effort`, `thinking_level`, `reasoning_mode` | Response-reported settings only, not inferred defaults | Prediction record and per-model-call trace |
| `*_observed_calls` | Count of model calls providing that metric | Prediction and scoring |

**Caution:** Cached input tokens are a **subset** of input tokens; reasoning
tokens are a **subset** of output tokens. Do not add them to those totals again.
A numeric aggregate with `*_observed_calls < model_calls` may be incomplete,
because some calls did not report the detail. A `null` value means unobserved,
not zero. Two different reported efforts in one question are kept separately
in `traces.jsonl` and `report.reasoning_efforts`; the question-level
`reasoning_effort` is then `null` to avoid claiming a single setting.
Nested subagent usage can still be missed by the current top-level tracing.

Each `structured_events` Model node retains observed usage and effort metadata;
the Trace Explorer displays it if available. No hidden chain-of-thought text is
exposed or stored. Pre-existing run artifacts are not rewritten.

From the project root, after inference, inspect observed per-question values:

```powershell
Get-Content "scr/evaluation/result/sample-001/B0/dev/siwc-001/predictions.jsonl" |
  ConvertFrom-Json |
  Select-Object question_id, input_tokens, cached_input_tokens, output_tokens, reasoning_tokens, total_tokens, reasoning_effort, thinking_level, model_calls
```

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
