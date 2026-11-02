# KORA — COMP7608B Group 9 Text-to-SQL Agent

**HKU MSc Computer Science · Large Language Models · Semester 1, 2026–2027**

> **Start here:** This repository contains a working B0 Text-to-SQL agent, the original BIRD Mini-Dev loader, strict EX evaluator, trace viewer, offline tests and beginner tutorials. The interactive application (follow-up questions, session context and reliable user-facing recovery) is **planned, not finished**.

## 1. Project goal — what does KORA solve?

Data analysts and business users often know what they want to ask but do not know the database schema or how to write SQL. **KORA** aims to turn natural-language questions into safe read-only SQL by exploring the schema, executing SQL tools, observing real database results/errors and deciding whether to fix the query or stop safely.

**Current executable path:** BIRD question → B0 Deep Agent → schema/SQL tools → SQLite → final SQL → **independent EX scoring**. This existing command-line benchmark pipeline is not yet the final live interactive app.

## 2. Progress and what is next (3 November 2026 · v4.4)

| Workstream | Status | Evidence / next step |
| --- | --- | --- |
| KORA-02 · Original BIRD Mini-Dev data | **Done** | 500 questions, 11 SQLite databases, local 400-dev/100-test split previously verified |
| KORA-03 · Execution Accuracy scorer | **Done** | Selected-case upstream scorer parity **16/16**, not comprehensive parity |
| KORA-05 · B0 Text-to-SQL agent | **In progress** | Implemented; initial 4-dev-question smoke: **4/4 final SQL, 1/4 strict EX = 25%** |
| KORA-10 · Evaluation and diagnostics | **In progress** | Analyze Q672/Q963 aggregation and Q1037 join/temporal discrepancies; expand frozen dev sample |
| KORA-06–09 · B1–B4 improvements | **Planned / conditional** | KG, explicit planner, router and optional integration based on measured B0 weaknesses |
| KORA-14–17 · Working agent application | **Planned, P0** | Backend/controller, interactive UI, reliability tests and independent fictional demo data |
| KORA-11–12 · Submission and demo | **Planned** | Final report, runnable source ZIP, pitch and live demo |

**Important:** 25% EX is only **1 of 4 development questions**, not a representative model accuracy estimate; this was a user-reported local smoke run. Successful SQL execution is not the same as a correct answer. The earlier submitted proposal included fixed S0/S1 metrics; the **B0-only baseline working plan** does not modify the submitted proposal and requires team agreement and honest final-report disclosure. A latest full Windows regression and larger frozen dev run remain pending.

**3 November tracking update:** Eight active P0 KORA tasks (05, 10, 11, 12, 14–17) now have private Notion execution records. KORA-02/03 completion remains documented in the shared roadmap. The prior BENCH-03 BIRD research ticket is Done; broader BENCH-04 three-dataset planning is still Backlog. The public repo already contains B0 code/tests/docs; private-only proposals, RAG work and raw benchmarks remain excluded.

## 3. Quick Start — Windows PowerShell

**Prerequisites:** Git, Python **3.11–3.14**, [uv](https://docs.astral.sh/uv/getting-started/installation/) and network access to download the original BIRD dataset. A private NVIDIA API key is needed only for hosted **Infer**. All commands below run from the repository root containing `pyproject.toml`.

### Step 1 — Clone and install project dependencies

**Why:** Obtain the scripts, then install Python packages into a managed local environment.

```powershell
git clone https://github.com/TimLL123456/COMP7608-Large-language-models-Group-Project.git
cd COMP7608-Large-language-models-Group-Project
python --version
uv --version
uv sync
```

**Expected:** Python and uv report versions, and `uv sync` completes without errors. See the detailed [dataset setup tutorial](docs/bird-setup.md) for installation help.

### Step 2 — Run offline unit tests

**Why:** Check the code and small synthetic fixtures without using an API key or downloading BIRD.

```powershell
uv run python -X utf8 -m unittest discover -s tests -t . -v
```

**Expected:** Tests pass; JavaScript-specific trace-viewer tests may be skipped if Node.js is unavailable. These tests do **not** demonstrate real BIRD accuracy or live NVIDIA availability.

### Step 3 — Install and verify original BIRD Mini-Dev

**Why:** The agent needs the actual benchmark questions and 11 SQLite databases. The dataset is downloaded separately, never stored in this GitHub repo.

```powershell
uv run python -m scr.datasets.setup_bird
uv run python -m scr.datasets.setup_bird --verify-only
```

**Expected:** A `PASS` result with **500 questions, 11 databases, 400 dev and 100 local test questions**. This is original **Mini-Dev**, not Mini-Dev V2. Our 100 local-test questions are **not** BIRD's official hidden test.

### Step 4 — Prepare a five-question smoke sample

**Why:** Choose a small repeatable set before making model calls.

```powershell
uv run python -m scr.cli.run_bird_b0_eval prepare `
  --total-questions 5 `
  --dev-ratio 0.8 `
  --seed 42 `
  --selection-id sample-001
```

**Expected:** `dev=4` and `test=1`. `--seed` makes the question *selection* repeatable, not the model's generated SQL. `prepare` makes no NVIDIA API calls.

### Step 5 — Generate SQL using B0 (hosted inference)

**Why:** The agent inspects relevant tables and executes safe SQL tools before producing a final candidate.

**First:** Set `NVIDIA_API_KEY` securely in your own PowerShell session using [Step 1 of the B0 tutorial](docs/bird-b0.md#1-first-time-checks--required). Inference requires internet access and may incur provider charges. Do not put real keys into `.env.example` or Git.

```powershell
uv run python -m scr.cli.run_bird_b0_eval infer `
  --selection-id sample-001 `
  --split dev `
  --run-id run-001
```

**Expected:** `predictions.jsonl`, `traces.jsonl` and `inference_manifest.json` under `scr/evaluation/result/sample-001/B0/dev/run-001/`. A transport timeout may generate `predicted_sql: null`; it is not automatically a SQL reasoning failure.

### Step 6 — Score results without calling an LLM

**Why:** Compare saved final SQL's executed rows with reference SQL's rows. **EX=1** indicates exact result-set equality; **EX=0** indicates mismatch, failure or missing final SQL.

```powershell
uv run python -m scr.cli.run_bird_b0_eval score `
  --selection-id sample-001 `
  --split dev `
  --run-id run-001
```

**Expected:** Check `scr/evaluation/result/sample-001/B0/dev/run-001/scores/report.md` for the summary, `per_question.csv` for each error, and `summary.json` for metrics.

### Step 7 — Visualize the agent trace (optional)

**Why:** See the actual model/tool sequence and diagnose why the generated SQL succeeded, failed or timed out.

```powershell
uv run python -m scr.cli.run_bird_b0_eval visualize `
  --selection-id sample-001 `
  --split dev `
  --run-id run-001
```

**Expected:** Open `scr/evaluation/result/sample-001/B0/dev/run-001/trace-explorer.html` in Edge or Chrome. No additional NVIDIA call is made. Use a fresh run ID next time rather than overwriting the saved run.

## 4. Documentation — where to start

| Tutorial | Audience / what you will learn |
| --- | --- |
| [BIRD dataset setup](docs/bird-setup.md) | Beginners: environment prerequisites, downloading and verifying databases, troubleshooting |
| [B0 step-by-step tutorial](docs/bird-b0.md) | Beginners: `prepare`, `infer`, `score`, `visualize`, key parameters and expected files |
| [BIRD Evaluation / EX](docs/bird-evaluation.md) | All team members: official-style strict EX, gold SQL, diagnostic limitations and fair comparisons |
| [Agent development](docs/agent-development.md) | Contributors: extend B0 toward B1 KG, B2 planner and B3 router; reuse the shared evaluator |
| [Progress planning v4.4](progress-planning.md) | Team: current statuses, dependencies, proposed tickets, milestones and acceptance criteria |

## 5. Source code map

```text
scr/baselines/      B0 agent, explicit-provider model factory and read-only SQL
scr/datasets/       Original BIRD dataset setup, loader and local split
scr/evaluation/     Strict EX evaluation and deterministic question sampling
scr/cli/            Prepare / Infer / Score / Visualize and independent scorer CLI
scr/tracing/        Trace graph, HTML viewer and local refresh server
tests/              Offline regression tests and tests/fixtures/demo_schema.sql
docs/               Beginner setup, evaluation and development documentation
```

**Small database clarification:** `tests/fixtures/demo_schema.sql` contains simple fictional customers/orders used only to check SQL safety. It is **not** original BIRD Mini-Dev, gold reference data or the planned KORA-17 application/demo fixture set.

## 6. Team contribution and safety

Start by running the existing offline tests, reading [agent development](docs/agent-development.md) and checking [remaining tickets](progress-planning.md). Create a feature branch; keep agent improvements small and testable; use the same question IDs and evaluation conditions when comparing them with B0; open a Pull Request containing commands run, observed results and limitations.

**Never commit:** API credentials, real `.env` files, downloaded BIRD SQLite databases/annotations, evaluator-only reference answers, raw traces or private data. `.env.example` contains variable **names**, not credentials, and is **not auto-loaded**. The B0 evaluation CLI currently uses NVIDIA `nvidia/nemotron-3.5-super-vl-120b-a12b`; optional Ollama/Gemini/DeepSeek support in `common.py` is not a `--provider` flag of this CLI.

**Planned delivery:** The working roadmap lists final report PDF + runnable code ZIP submission on **25 November 2026 at 23:59 HKT**, followed by a live demo on **1 or 8 December** (session assignment pending). Consult official course announcements for authoritative requirements.
