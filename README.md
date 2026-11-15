# KORA — COMP7608B Group Project

**Group 9 · 2026–2027 Semester 1** · **Research status verified: 15 November 2026**

KORA is a research project investigating evidence-driven **Text-to-SQL**: AI agents explore SQLite database metadata, generate read-only SQL, and evaluate the results with an independent execution-accuracy (EX) scorer. This is the **shared public Group Project repository**. The standalone research agents, their tests, and experiment archives live in this repository; an end-to-end interactive KORA application is not yet verified.

## Latest research results

These are the most recent **completed local BIRD Mini-Dev 2026** evaluations for each variant. The dataset has 500 questions across 11 SQLite databases, split into 400 local Development and 100 local Test questions. These results are **not official hidden BIRD Test** scores.

| Research implementation | Latest local EX | Details |
| --- | ---: | --- |
| B0 generalized-v1 | **319/500 (63.80%)** | [Experiment and limitations](evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/README.md) |
| **MetadataDiscoveryV2** (A1/B1/C1) | **340/500 (68.00%)** | [Agent guide](docs/metadata-discovery-v2.md) · [Evaluation](evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) |
| **Self Reflection Agent** | **350/500 (70.00%)** | [Agent guide](docs/self-reflection-agent.md) · [Evaluation](evaluation-results/self-reflection-full-20261113/README.md) |
| **Rubric Self Reflection** | **326/500 (65.20%)** | [Agent guide](docs/rubric-self-reflection-agent.md) · [Evaluation](evaluation-results/rubric-self-reflection-full-20261115/README.md) |
| **Role-Specialized Self Reflection** | **Full benchmark pending** | [Generator/reviewer roles and parallel shards](docs/role-specialized-self-reflection-agent.md) |

**Interpretation:** Experimental budgets, description availability, retry policies and model execution conditions differ. Raw EX differences do **not** demonstrate isolated causal improvements. See each experiment report for reproducibility, resources, failures and limitations.

## Current architecture and implementation

The implementations reuse shared BIRD data handling, a **read-only SQLite execution layer**, a baseline SQL agent and independent EX scoring.

- **B0:** Schema investigation, SQL generation and bounded repair.
- **MetadataDiscoveryV2:** A1 metadata discovery → B1 evidence-sufficiency check → C1 SQL generation.
- **Self Reflection:** Independent SQL review with evidence-backed feedback and bounded B0 retries.
- **Rubric Self Reflection:** Atomic requirement checking and guarded final SQL refinement.
- **Role-Specialized Self Reflection:** Separate generation/review model roles, including two-terminal sharded inference and merging. Full benchmark evidence is not yet available.

The experimental agent implementations do **not** establish that a complete interactive, multi-turn KORA application has been delivered.

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
- [`evaluation-results/`](evaluation-results/) — all six historical and current experiment archives
- [`docs/`](docs/) — current documentation and historic snapshots
- [`agent-study/`](agent-study/), [`research/`](research/), [`proposal/`](proposal/) — tutorials, background research and original proposals

## Historical research

For **earlier B0 evaluations, original-dataset reproduction instructions, previous plans and superseded agent designs**, see the [Historical Research Index](docs/history/README.md). Full historical documents and experimental evidence remain available through those links rather than being repeated here. Keep provider keys and local database downloads outside the repository; [`.env.example`](.env.example) contains safe configuration placeholders.
