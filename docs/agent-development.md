# KORA Developer Guide — Reusing B0 for B1–B4

**Audience:** COMP7608 teammates developing B1 Knowledge Graph, B2 Query Planner, B3 Model Router and B4 integration.

**Goal:** Reuse one dataset, SQL safety layer and evaluator, so improvements can be compared fairly with B0.

> **Current status:** B0, the dataset loader, EX scorer, and trace viewer are now included in this public group repository. B1–B4, an interactive app, and full reliability tests remain planned; this guide does not claim they run.

## 1. Run and understand B0 first — Required

From the root folder containing `pyproject.toml`:

1. Install and verify the [original BIRD dataset](bird-setup.md).
2. Follow [B0: Prepare → Infer → Score](bird-b0.md) using **five sample questions**.
3. **Optional:** Generate a [Trace Explorer](bird-b0.md#5-visualize-the-agent-trace--optional) HTML and inspect model/tool decisions.
4. Check `report.md` and `per_question.csv` before changing the agent.

**Why:** This provides a baseline run and known input/output files, not merely a test that an agent starts.

## 2. Existing framework: where to find things

| Module | Responsibility | Reuse recommendation |
| --- | --- | --- |
| `scr/datasets/setup_bird.py` | Download and verify pinned dataset | Use for installation; **do not create a second downloader** |
| `scr/datasets/bird.py` | Read questions, schema, splits and database locations | Reuse `BirdDataset` |
| `scr/baselines/common.py` | Create supported LLM providers; trace shared runtime | Reuse provider selection; no silent model fallback |
| `scr/baselines/sqlite_readonly.py` | Execute safe, bounded read-only SQL | Reuse, don't add unguarded SQL execution |
| `scr/baselines/bird_b0.py` | Build and run B0 Deep Agent | Study `make_agent()`, `run_one()` and prompt/output contract |
| `scr/cli/run_bird_b0_eval.py` | Sample questions, run B0, score and visualize | Use as a reference; **not currently a universal B0–B4 infer CLI** |
| `scr/cli/evaluate_bird.py` and `scr/evaluation/bird.py` | Independent EX evaluator | Reuse for all variants |
| `scr/tracing/` | Convert saved B0 traces to local HTML | Adapt only after agreeing a common trace schema |
| `tests/` | Offline regression fixtures | Extend with tests for your added feature |

**Important:** The project uses the package directory name **`scr/`** (not `src/`). Run commands from the project root so Python resolves `scr`.

## 3. Shared input and output contracts

### Input (agent-visible)

A BIRD question provides its actual ID, database ID, natural-language question and evidence. Example access:

```python
from scr.datasets.bird import BirdDataset

dataset = BirdDataset()
record = dataset.get_split("dev")[0]
agent_input = dataset.get_agent_input(record["question_id"])
db_path = dataset.get_database_path(agent_input["db_id"])

assert "SQL" not in agent_input  # Gold reference must not reach the agent
```

**Do not use** `BirdEvaluationReferences` inside an agent; gold SQL is only for independent scoring. The default dev/test split contains 400/100 question IDs, not the official hidden BIRD test.

### Output (for evaluation)

Save **one JSONL prediction per selected question**, with the real IDs:

```json
{"question_id": 2000, "db_id": "demo_0", "predicted_sql": "SELECT COUNT(*) FROM records", "model_calls": 3, "tool_calls": 5, "latency_ms": 1200}
```

That record is an **illustration**, not a real Mini-Dev question. Set `predicted_sql` to `null` when no final SQL was produced; do not invent SQL after failures. Optional observed fields include tokens, timing, tool calls, model/provider and SQL successes/errors. Missing metrics should be `null`, not 0.

For accuracy scoring, follow [manual prediction scoring — Advanced](bird-evaluation.md#4-manual-prediction-scoring--advanced--optional). B0's `prepare/infer/score` path already creates compatible prediction files and manifests; B1–B4 will need their own reproducible inference integration until a shared runner is implemented.

## 4. Where each agent differs

| Agent | What to build | Keep shared |
| --- | --- | --- |
| **B0 — existing baseline** | Tool-using SQL generation and repair | Dataset/SQL safety/scorer |
| **B1 — Knowledge Graph** | Schema relationship graph and bounded join-path exploration | Same question IDs, evaluator and safe SQL |
| **B2 — Query Planner** | Explicit plan of tables, joins, filters and subgoals before SQL | Same benchmark/evaluator and model budget |
| **B3 — Model Router** | Choose model based on observable task features and a stated budget | Same tasks, metrics; report model choices and costs |
| **B4 — Integrated** | Combine B1/B2/B3 with independently selectable features | Same reference B0 and controlled comparisons |

**Start with the smallest change from B0.** Avoid duplicating datasets or scoring just to add an agent feature. Record new tool calls, planner decisions, graph paths or routing choices in the trace.

A common `Agent` class, plugin framework or web UI is **not required** to complete the first controlled comparison.

## 5. Reproducible experiment checklist

- Freeze the same **`selection_manifest.json` / question IDs and database version** for each variant. Start on `dev`; use local `test` only after selecting settings.
- Keep inference conditions comparable: model, temperature, top-p, output tokens, per-request timeout, model/tool limits and retry policy. If a variant intentionally uses different models, report the difference.
- Preserve read-only SQLite tools and the final SQL contract. Log failures as failures; an HTTP timeout is not proof of incorrect SQL reasoning.
- Run the **same EX evaluator** on prediction JSONL from each variant. EX is correctness of the final result set, **not** successful query execution.
- Save a manifest recording variant, prompt/config version, run ID, selected IDs, date, model, limits and result hashes. **Do not edit an existing run.**
- Compare per-question results and difficulty breakdown, tool/model calls, latency and (when known) costs. Separate synthetic fixture results from BIRD results.

## 6. Offline tests and development workflow

```powershell
# From the project root
uv sync
uv run python -m unittest discover -s tests -t . -v
```

Use small synthetic SQLite fixtures in tests to check new joins/plans/routing without hosted APIs. This does **not** replace real BIRD EX or prove that an NVIDIA request works.

**Suggested development sequence:** implement feature → test safety on fixtures → run a small frozen dev selection → inspect traces → score with the shared evaluator → compare to B0 → document evidence.

## 7. How to contribute

From this repository root, follow [BIRD setup](bird-setup.md) and [B0 walkthrough](bird-b0.md), then run `uv run python -X utf8 -m unittest discover -s tests -t . -v`. Python package folder: `scr/`, **not** `src/`.

**Suggested workflow:** Work on a feature branch → make a focused change → add relevant tests → run offline tests → run the same frozen development sample as B0 → inspect traces, strict EX, measured tokens and latency → open a Pull Request describing results and limitations. Keep model, prompt, budget and dataset settings matched when comparing agent improvements.

Never commit API keys, downloaded BIRD databases/annotations/gold references, or raw model traces. `tests/fixtures/demo_schema.sql` is an **offline SQL safety test fixture** and is neither BIRD nor a completed KORA-17 application demo dataset.

B1–B4 enhancements and KORA-14–17 interactive application remain future work. See [progress planning](../progress-planning.md).
