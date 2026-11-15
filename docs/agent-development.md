# KORA Developer Guide — B0, Research Agents and Historical B1–B4 Roadmap

**Audience:** COMP7608 teammates inspecting current agents and developing the historical B1–B4 proposals.

**Goal:** Reuse one dataset, SQL safety layer and evaluator, so improvements can be compared fairly with B0.

> **Current status (15 November 2026):** The group repository includes B0, Metadata v1, **MetadataDiscoveryV2**, Self Reflection, Rubric Self Reflection and Role-Specialized Self Reflection. The historical B1–B4 roadmap below describes proposed integration work.


## Implemented research variants and saved evaluations

| Variant | Code / guide | Latest archived local Mini-Dev 2026 EX |
| --- | --- | --- |
| B0 generalized-v1 | [B0 CLI](../scr/cli/run_bird_b0_eval.py) | [319/500 (63.80%)](../evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/README.md) |
| Metadata v1 | [Metadata guide](metadata-agent.md) | No completed result claimed here |
| MetadataDiscoveryV2 | [A1/B1/C1 guide](metadata-discovery-v2.md) | [340/500 (68.00%)](../evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) |
| Self Reflection | [Reviewer + SQL-first guide](self-reflection-agent.md) | [350/500 (70.00%)](../evaluation-results/self-reflection-full-20261113/README.md) |
| Rubric Self Reflection | [Atomic-rubric guide](rubric-self-reflection-agent.md) | [326/500 (65.20%)](../evaluation-results/rubric-self-reflection-full-20261115/README.md) |
| Role-Specialized Self Reflection | [Luna/Terra roles and parallel shards](role-specialized-self-reflection-agent.md) | Full benchmark pending |

These are distinct experiments, not proof that the originally planned B1–B4 components have all been delivered. Comparisons must state dataset, model, budgets, retries and compute differences.

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

## 4. Historical B1–B4 proposed directions

| Agent | What to build | Keep shared |
| --- | --- | --- |
| **B0 — existing baseline** | Tool-using SQL generation and repair | Dataset/SQL safety/scorer |
| **B1 — Knowledge Graph** | Schema relationship graph and bounded join-path exploration | Same question IDs, evaluator and safe SQL |
| **B2 — Query Planner** | Explicit plan of tables, joins, filters and subgoals before SQL | Same benchmark/evaluator and model budget |
| **B3 — Model Router** | Choose model based on observable task features and a stated budget | Same tasks, metrics; report model choices and costs |
| **B4 — Integrated** | Combine B1/B2/B3 with independently selectable features | Same reference B0 and controlled comparisons |

**Start with the smallest change from B0.** Avoid duplicating datasets or scoring just to add an agent feature. Record new tool calls, planner decisions, graph paths or routing choices in the trace.

A common `Agent` class, plugin framework or web UI is **not required** to complete the first controlled comparison.

### Standalone Self Reflection Agent (implemented and benchmarked)

The independent [Self Reflection Agent](self-reflection-agent.md) wraps B0 with a SQL Reflection Reviewer, PASS / FAIL / UNCERTAIN decisions and a bounded B0 feedback loop. Its [13 November full 500-question evaluation](../evaluation-results/self-reflection-full-20261113/README.md) reached **350/500 (70.00%)** local strict EX. The document retains the original V1.1 design history; this implementation is distinct from **MetadataDiscoveryV2** and the legacy B1–B4 roadmap.

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

## 7. Contributing to the group repository

Run setup and tests from the repository root. Open a pull request with the validation results and describe any changes to experiment inputs or outputs. Review new files for credentials, local paths and unreviewed runtime traces. Preserve the existing experiment archives and their manifests.

**Never publish** credentials or downloaded BIRD reference answers/databases. Retain original dataset download instructions and citation/provenance. Confirm teammate ownership and whether fixed S0/S1 baselines remain required by the submitted proposal before changing the group roadmap.

Further reading: [BIRD setup](bird-setup.md), [B0 tutorial](bird-b0.md), [EX scoring](bird-evaluation.md), and [progress plan](../progress-planning.md).
