# KORA Developer Guide — Current Agent Framework

**Updated: 15 November 2026.** This guide describes available implementations, their interfaces and how to develop reproducible experiments. The older B1–B4 design proposal is archived in the [historical developer guide](history/agent-development-pre-current-only-20261115.md).

## Shared foundations

All current agents reuse the project's BIRD dataset/selection logic, read-only SQLite execution adapter and independent execution-accuracy (EX) scorer. The Python source package is named `scr/`, **not** `src/`.

| Component | Source | Responsibility |
| --- | --- | --- |
| BIRD data loader | [datasets/bird.py](../scr/datasets/bird.py) | Pinned question/evidence input, schema and database paths |
| B0 SQL agent | [baselines/bird_b0.py](../scr/baselines/bird_b0.py) | Inspect schemas, produce SQL and record observations |
| SQL safety | [baselines/sqlite_readonly.py](../scr/baselines/sqlite_readonly.py) | Bound SQL execution to read-only SQLite |
| EX scoring | [evaluation/bird.py](../scr/evaluation/bird.py) | Score saved predictions using evaluator-only gold references |
| B0 CLI | [run_bird_b0_eval.py](../scr/cli/run_bird_b0_eval.py) | Prepare, infer, score and visualize |
| Metadata v1 | [metadata_agent.py](../scr/agents/metadata_agent.py) | Reuse scoped metadata notes |
| MetadataDiscoveryV2 | [metadata_discovery_v2.py](../scr/agents/metadata_discovery_v2.py) | A1 discovery → B1 sufficiency → C1 SQL |
| Self Reflection | [self_reflection_agent.py](../scr/agents/self_reflection_agent.py) | Independent SQL reviewer and bounded B0 retry |
| Rubric Self Reflection | [rubric_self_reflection/](../scr/agents/rubric_self_reflection/) | Atomic requirements, evidence checks and final SQL refinement |
| Role-Specialized Self Reflection | [role_specialized/](../scr/agents/role_specialized/) | Separate generator/reviewer models; parallel shards and merge |

## Run and test

From the Group repository root:

~~~bash
uv sync
uv run python -m unittest discover -s tests -t . -v
uv run python -m scr.cli.run_bird_b0_eval --help
uv run python -m scr.cli.run_bird_metadata_eval --help
uv run python -m scr.cli.run_bird_self_reflection_eval --help
uv run python -m scr.agents.rubric_self_reflection.cli --help
uv run python -m scr.agents.role_specialized.cli --help
~~~

First install [Mini-Dev 2026](bird-setup.md), then follow the [B0 example](bird-b0.md#mini-dev-2026-current-workflow). Run a small uniquely named Dev selection before a complete 500-question experiment. Individual agent usage is documented in [MetadataDiscoveryV2](metadata-discovery-v2.md), [Self Reflection](self-reflection-agent.md), [Rubric Self Reflection](rubric-self-reflection-agent.md) and [Role-Specialized Self Reflection](role-specialized-self-reflection-agent.md).

## Evaluation contract

- Freeze dataset revision, selected question IDs, model/provider, prompt, budgets, inference settings, retry policy and experiment IDs. Prefer distinct immutable run IDs.
- Keep gold SQL and reference outputs **out of inference input, agent-visible files and prompts**. Only offline scoring may load them.
- Record the produced final SQL, including missing SQL, read-only execution errors, attempts, reviewer decisions, observable model/tool calls, tokens and latency. Missing usage must not be reported as zero.
- EX is based on result-set agreement, not SQL compilation alone and not a provisional reviewer PASS.
- Compare per-question cases, corrected/regressed SQL and resource use. Declare non-matched budgets or model differences; do not label them causal ablations.
- Preserve historical results and checksum manifests. Never edit an existing experiment to adjust its score.

## Current boundaries

Available agent modules and local benchmarks do **not** establish a completed interactive app, unseen-database generalization or official hidden-Test performance. Role-specialized full EX performance remains pending. The B1–B4 legacy roadmap describes older hypothetical architecture tracks, not implemented claims: see [historical design](history/agent-development-pre-current-only-20261115.md), [earlier planning](history/progress-planning-pre-current-only-20261115.md), and [original proposal](../proposal/).

No developer should commit API keys, credential caches or downloaded dataset binaries to the public repository.
