# KORA — COMP7608B Group Project

**Group 9 · 2026–2027 Semester 1** · Research status: **15 November 2026**

KORA investigates evidence-driven **Text-to-SQL**: agents inspect SQLite database schemas, generate read-only SQL and evaluate the resulting answers against the BIRD benchmark. This is the shared, standalone project repository. The core research implementation is available; a complete interactive multi-turn application has not been verified.

## Latest research results

The following are **local BIRD Mini-Dev 2026** results (400 development + 100 local test questions across 11 databases), **not the official hidden BIRD test**.

| Implementation | Local execution accuracy (EX) | Reference |
| --- | ---: | --- |
| B0 with generalized-v1 prompt | **319/500 (63.80%)** | [Full evaluation](evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/README.md) |
| **MetadataDiscoveryV2** (A1/B1/C1) | **340/500 (68.00%)** | [Workflow](docs/metadata-discovery-v2.md) · [Evaluation](evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) |
| Self Reflection Agent | **350/500 (70.00%)** | [Workflow](docs/self-reflection-agent.md) · [Evaluation](evaluation-results/self-reflection-full-20261113/README.md) |
| Rubric Self Reflection | **326/500 (65.20%)** | [Workflow](docs/rubric-self-reflection-agent.md) · [Evaluation](evaluation-results/rubric-self-reflection-full-20261115/README.md) |
| Role-Specialized Self Reflection | **Full benchmark pending** | [Luna/Terra role and parallel inference guide](docs/role-specialized-self-reflection-agent.md) |

These evaluations have **different budgets, retries and experimental conditions**; their EX differences do not establish causal architectural improvements. SQL execution accuracy is distinct from reviewer PASS and from an end-to-end application evaluation. Experiment READMEs record provenance and limitations.

## Quick start

Requirements: Python and [uv](https://docs.astral.sh/uv/). Run from this repository root, which contains `pyproject.toml`.

~~~bash
git clone https://github.com/TimLL123456/COMP7608-Large-language-models-Group-Project.git
cd COMP7608-Large-language-models-Group-Project
uv sync
uv run python -m scr.datasets.setup_bird --release latest --revision 5b256b5a9c17478f06ed6912612e9a14d17065c8
uv run python -m scr.datasets.setup_bird --release latest --verify-only
uv run python -m unittest discover -s tests -t . -v
~~~

The BIRD dataset is downloaded separately into the ignored `data/bird/mini-dev-2026/` directory; it is not bundled. For a small model evaluation, follow [Prepare → Infer → Score → Visualize](docs/bird-b0.md#mini-dev-2026-current-workflow). Inference requires provider authentication and can use model quota; setup, offline tests and scoring do not call models.

## Available agents and documentation

| Task | Current guide |
| --- | --- |
| Install and verify the BIRD dataset | [BIRD setup](docs/bird-setup.md) |
| Run the baseline agent | [B0 tutorial](docs/bird-b0.md) |
| Understand execution accuracy | [EX scoring](docs/bird-evaluation.md) |
| Explore reusable metadata notes (v1) | [Metadata v1](docs/metadata-agent.md) |
| Run A1/B1/C1 knowledge discovery | [MetadataDiscoveryV2](docs/metadata-discovery-v2.md) |
| Review and regenerate SQL | [Self Reflection](docs/self-reflection-agent.md) |
| Check atomic requirements and refine SQL | [Rubric Self Reflection](docs/rubric-self-reflection-agent.md) |
| Run role-specialized generation/review in parallel shards | [Role-Specialized Self Reflection](docs/role-specialized-self-reflection-agent.md) |
| Extend or evaluate an agent | [Developer guide](docs/agent-development.md) |
| Current priorities and unverified work | [Current progress](progress-planning.md) |

## Repository structure

- [`scr/`](scr/) — B0, agent variants, dataset handling, evaluation, CLI and trace helpers
- [`tests/`](tests/) — offline regression tests
- [`evaluation-results/`](evaluation-results/) — six preserved research experiment archives, predictions, scores and reports
- [`docs/`](docs/) — current workflows and technical guides
- [`research/`](research/) — supporting research
- [`agent-study/`](agent-study/) — tutorials and notebooks
- [`proposal/`](proposal/) and [`guidelines/`](guidelines/) — original project materials
- [`docs/history/`](docs/history/README.md) — superseded documentation snapshots

## Earlier research and provenance

The **original Mini-Dev B0** [299/500 study](evaluation-results/b0-gpt6-luna-40calls-20261108/README.md), earlier **Mini-Dev 2026 B0** [294/500 study](evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/README.md) and all other experiment evidence remain preserved. For older architecture drafts, planning milestones and prior documentation, use the [Historical Research Index](docs/history/README.md). Original proposals are under [proposal/](proposal/).

Never commit API tokens, login credentials or downloaded BIRD databases; use a local environment and the safe [`.env.example`](.env.example) reference.
