# KORA — COMP7608B Group Project

**Group 9 · 2026–2027 Semester 1** · **Research status verified: 16 November 2026**

KORA is a research project investigating evidence-driven **Text-to-SQL**: AI agents explore SQLite database metadata, generate read-only SQL, and evaluate the results with an independent execution-accuracy (EX) scorer. This is the **shared public Group Project repository**. The standalone research agents, their tests, and experiment archives live in this repository; an end-to-end interactive KORA application is not yet verified.

## Latest research results

These are the most recent **completed local BIRD Mini-Dev 2026** evaluations for each variant. The dataset has 500 questions across 11 SQLite databases, split into 400 local Development and 100 local Test questions. These results are **not official hidden BIRD Test** scores.

| Research implementation | Latest local EX | Details |
| --- | ---: | --- |
| B0 generalized-v1 | **319/500 (63.80%)** | [Experiment and limitations](evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/README.md) |
| **MetadataDiscoveryV2** (A1/B1/C1) | **340/500 (68.00%)** | [Agent guide](docs/metadata-discovery-v2.md) · [Evaluation](evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) |
| **Self Reflection Agent** | **350/500 (70.00%)** | [Agent guide](docs/self-reflection-agent.md) · [Evaluation](evaluation-results/self-reflection-full-20261113/README.md) |
| **Rubric Self Reflection** | **326/500 (65.20%)** | [Agent guide](docs/rubric-self-reflection-agent.md) · [Evaluation](evaluation-results/rubric-self-reflection-full-20261115/README.md) |
| **Role-Specialized Self Reflection** | **401/500 (80.20%)** | [Agent guide](docs/role-specialized-self-reflection-agent.md) · [Full local evaluation](evaluation-results/role-specialized-luna-terra-full-20261116/README.md) |

**Latest completed run (16 November 2026):** Luna (`gpt-6-luna`) investigated and generated SQL, while Terra (`gpt-6.1-terra`) extracted requirements and reviewed candidates. A single sequential 500-question run achieved **321/400 (80.25%) local Dev EX**, **80/100 (80.00%) local Test EX**, and **498/500 non-missing final SQL**. An interrupted run was resumed in place; its preserved 107-record prefix and mixed source revisions are documented in the [evaluation report](evaluation-results/role-specialized-luna-terra-full-20261116/README.md). This benchmark was **not** a two-terminal parallel run.

**Interpretation:** This is the highest **observed local EX** among the archived variants, not an official hidden BIRD Test result. Reviewer PASS is not the same as independent EX correctness. Experimental budgets, model assignments, description availability and retries differ; the raw percentages do **not** isolate a causal benefit of role specialization or prove cost savings. See the linked reports for reproducibility, resources and failure cases.

## Current agents overview

KORA currently has **six implemented agent variants**. They share the BIRD dataset utilities, read-only SQLite execution and independent execution-accuracy (EX) scoring. The workflows below are simplified; their full configurations and limitations are documented in the linked guides.

| Agent | What it is | Simplified workflow | Problem it aims to address |
| --- | --- | --- | --- |
| **[B0 — Baseline Agent](docs/bird-b0.md)** | The foundational Text-to-SQL agent: investigates database schemas and values, then generates SQL. | Question → Inspect schema/data → Generate and check SQL → Final SQL | Establish a reproducible starting point for SQL generation and evaluating later approaches. |
| **[Metadata Agent V1](docs/metadata-agent.md)** | Extends B0 with scoped, reusable table/column knowledge notes. | Question → Search notes → Investigate missing context → Create/update notes → Generate SQL | Repeated schema exploration and missing reusable business meanings; no completed full V1 benchmark is claimed. |
| **[MetadataDiscoveryV2](docs/metadata-discovery-v2.md)** | A staged metadata-first workflow with explicit evidence sufficiency evaluation. | **A1** Discover/reuse metadata → **B1** Check sufficiency → Return to A1 if needed → **C1** Generate SQL (or stop when exhausted) | Generating SQL before enough evidence is available about tables, columns, values, filters or granularity. |
| **[Self Reflection Agent](docs/self-reflection-agent.md)** | Adds an independent reviewer and bounded retries to B0 while prioritizing safe SQL output. | B0 generates SQL → Reviewer checks evidence and execution → Retry B0 on actionable FAIL → Select eligible final SQL | Unchecked mistakes in candidate SQL and unnecessarily losing executable output when review remains uncertain. |
| **[Rubric Self Reflection](docs/rubric-self-reflection-agent.md)** | Breaks the question into atomic requirements and checks each against SQL evidence. | B0 SQL → Extract requirements → Criterion-by-criterion review → Retry/refine when justified → Checked final SQL | Missed output fields, filters, metric logic, grain, joins and temporal requirements that broad reviews may overlook. |
| **[Role-Specialized Self Reflection](docs/role-specialized-self-reflection-agent.md)** | Assigns SQL investigation/generation to a lightweight model and rubric review to a stronger model. | Lightweight generator → Strong reviewer → Feedback to generator within budget → Safe SQL + review report | Tests model role specialization with a bounded evidence-based review loop. **A complete local 500-question EX evaluation is recorded; isolated benefit and cost efficiency are not established.** |

**Research boundary:** These are distinct implementations, not six stages of one finished application. They aim to address the problems above, but their existence alone does not prove improvement. Compare documented local EX results and compute/retry differences in the [latest research results](#latest-research-results). The complete interactive multi-turn application has not been verified.

### LangGraph B0 orchestration (experimental)

A separate [LangGraph B0 implementation](langgraph_agents/README.md) wraps the existing Deep Agents B0 in an explicit `StateGraph` and supports `prepare → infer → score` with independent `LangGraphB0` result directories. Its new CLI defaults to ChatGPT SIWC / `gpt-6-luna` / reasoning effort `none` / `generalized-v1` prompt; the original B0 CLI and agent remain unchanged. This is a framework migration, **not** a seventh SQL algorithm or evidence of higher EX accuracy.

## Current quick start

Use **BIRD Mini-Dev 2026** for new evaluations. Clone the public repository and run these commands from its root (the directory containing `pyproject.toml`). Requires Python and [uv](https://docs.astral.sh/uv/).

~~~bash
git clone https://github.com/TimLL123456/COMP7608-Large-language-models-Group-Project.git
cd COMP7608-Large-language-models-Group-Project
uv sync
uv run python -m scr.datasets.setup_bird --release latest --revision 5b256b5a9c17478f06ed6912612e9a14d17065c8
uv run python -m scr.datasets.setup_bird --release latest --verify-only
~~~

Follow the [current BIRD setup instructions](docs/bird-setup.md) and [Prepare → Infer → Score → Visualize guide](docs/bird-b0.md#mini-dev-2026-current-workflow) to run a new evaluation. Inference may require provider authentication and model quota. Dataset downloads are kept outside Git.

## Documentation and source

| Goal | Current resource |
| --- | --- |
| Dataset installation and version | [Setup](docs/bird-setup.md) · [Dataset standard](docs/bird-dataset-versions.md) |
| Run and evaluate B0 | [B0 workflow](docs/bird-b0.md) · [EX scoring](docs/bird-evaluation.md) |
| Develop or compare agents | [Developer guide](docs/agent-development.md) |
| Metadata v1 (distinct from V2) | [Metadata v1](docs/metadata-agent.md) |
| Current research progress | [Progress and next steps](progress-planning.md) |
| Code and regression tests | [`scr/`](scr/) · [`tests/`](tests/) |
| Research reports | [`evaluation-results/`](evaluation-results/) · [`research/`](research/) |

## Repository structure

- [`scr/`](scr/) — agent implementations, dataset loader, CLI, read-only SQL and EX evaluator
- [`tests/`](tests/) — offline regression tests
- [`evaluation-results/`](evaluation-results/) — seven historical and current experiment archives
- [`docs/`](docs/) — current documentation and historic snapshots
- [`agent-study/`](agent-study/), [`research/`](research/), [`proposal/`](proposal/) — tutorials, background research and original proposals

## Historical research

For **earlier B0 evaluations, original-dataset reproduction instructions, previous plans and superseded agent designs**, see the [Historical Research Index](docs/history/README.md). Full historical documents and experimental evidence remain available through those links rather than being repeated here. Keep provider keys and local database downloads outside the repository; [`.env.example`](.env.example) contains safe configuration placeholders.

### LangGraph role-specialized agent

The second [LangGraph Role-Specialized Self-Reflection implementation](langgraph_agents/README.md#role-specialized-self-reflection--second-langgraph-variant) adds explicit generator/reviewer/decision graph nodes with bounded retries. The original Luna/Terra agent and archived evaluation remain unchanged. See [setup, commands, output and limitations](docs/langgraph-role-specialized.md).

### Remaining LangGraph agent variants

The [LangGraph migration guide](docs/langgraph-remaining-agents.md) covers independent graph versions of **Self Reflection**, **Rubric Self Reflection**, **Metadata V1**, and **MetadataDiscoveryV2**. The last reuses the existing A1/B1/C1 StateGraph rather than rewriting it. The six original agents and their historical results are preserved; the new LangGraph variants need independent EX scoring before accuracy comparisons.
