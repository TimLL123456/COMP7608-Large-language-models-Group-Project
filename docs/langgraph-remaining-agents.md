# LangGraph migration: remaining KORA agents

**Scope:** four independent LangGraph variants; original source in scr/agents/ and scr/cli/ is unchanged. This is an orchestration migration, not evidence of higher SQL execution accuracy (EX).

| Agent | Module | Routing | Historical behavior retained |
| --- | --- | --- | --- |
| Self Reflection | langgraph_agents.self_reflection | prepare → B0 → reviewer → decision → retry/final SQL | SQL-first, bounded FAIL retries, B0 finalization, safe SQL selection |
| Rubric Self Reflection | langgraph_agents.rubric_self_reflection | prepare → requirements → B0 → rubric review → feedback/refinement → final | Original requirements-first order, reviewer and optional evidence-based SQL refinement |
| Metadata V1 | langgraph_agents.metadata_v1 | prepare → original metadata-enabled Deep Agent → collect | Original four note tools, knowledge engine, defaults, Dev/Test knowledge reuse and recovery |
| MetadataDiscoveryV2 | langgraph_agents.metadata_discovery_v2 | original compiled A1 → B1 → A1/C1 graph | Reuse the existing StateGraph, all limits, note definitions and fallback rules |

B0 (LangGraphB0) and Role-Specialized (LangGraphRoleSpecializedSelfReflection) are independently maintained and unchanged.

## Meaning of LangGraph integration

Self Reflection and Rubric use real LangGraph StateGraph nodes and a bounded conditional retry edge. Their original Deep Agents B0 model/tool loops execute inside the SQL generator node; the migration does not pretend an individual model/tool call is independently checkpointable.

Metadata V1 wraps the existing Deep Agent with three actual outer graph nodes. Its metadata search, read, create and update tools are unchanged. MetadataDiscoveryV2 already used LangGraph internally in scr/agents/metadata_discovery_v2.py; its new CLI exposes that same compiled A1/B1/C1 graph under the consolidated package without duplicating its implementation.

Node transitions are persisted as observed graph events and rendered in the Trace Explorer. SQL, review and metadata evidence remain untrusted until validated. LangGraph checkpoint replay may repeat provider calls: there is no exactly-once guarantee.

## Model and prompt defaults

The new Self Reflection and Rubric CLIs intentionally preserve the original NVIDIA default provider and baseline prompt. Metadata V1 and MetadataDiscoveryV2 retain the NVIDIA and generalized-v1 defaults. No Luna/Terra substitution is implicit. To run with SIWC, specify chatgpt-siwc and the exact model name. Both reasoning-effort defaults and explicit overrides retain the historical semantics. Reviewer and generator use the same configured model in these variants; only the separate Role-Specialized Agent configures independent role models.

The original model/tool/SQL limits, reviewer call budgets, finalization and SQLite read-only safety remain intact.

## Commands

All commands run from the repository root after the dataset has been provisioned and a frozen selection created with the original B0 prepare command.

    uv sync --frozen

    # Self Reflection
    uv run python -m langgraph_agents.self_reflection.cli infer \
      --selection-id YOUR_SELECTION --split dev --run-id lg-self-001 \
      --provider chatgpt-siwc --model gpt-6-luna \
      --reasoning-effort none --prompt-variant generalized-v1
    uv run python -m langgraph_agents.self_reflection.cli score \
      --selection-id YOUR_SELECTION --split dev --run-id lg-self-001

    # Rubric Self Reflection
    uv run python -m langgraph_agents.rubric_self_reflection.cli infer \
      --selection-id YOUR_SELECTION --split dev --run-id lg-rubric-001 \
      --provider chatgpt-siwc --model gpt-6-luna \
      --reasoning-effort none --prompt-variant generalized-v1
    uv run python -m langgraph_agents.rubric_self_reflection.cli score \
      --selection-id YOUR_SELECTION --split dev --run-id lg-rubric-001

    # Metadata V1 (Dev creates a new, isolated notes store)
    uv run python -m langgraph_agents.metadata_v1.cli infer \
      --selection-id YOUR_SELECTION --split dev --run-id lg-meta-dev-001 \
      --experiment-id lg-meta-exp-001 --provider chatgpt-siwc \
      --model gpt-6-luna --reasoning-effort none --prompt-variant generalized-v1

    # Metadata V1 Test continues the SAME experiment after Dev completes
    uv run python -m langgraph_agents.metadata_v1.cli infer \
      --selection-id YOUR_SELECTION --split test --run-id lg-meta-test-001 \
      --experiment-id lg-meta-exp-001 --provider chatgpt-siwc \
      --model gpt-6-luna --reasoning-effort none --prompt-variant generalized-v1

    # MetadataDiscoveryV2 — an independent table/column knowledge experiment
    uv run python -m langgraph_agents.metadata_discovery_v2.cli infer \
      --selection-id YOUR_SELECTION --split dev --run-id lg-discovery-dev-001 \
      --experiment-id lg-discovery-exp-001 --provider chatgpt-siwc \
      --model gpt-6-luna --reasoning-effort none --prompt-variant generalized-v1
    uv run python -m langgraph_agents.metadata_discovery_v2.cli score \
      --selection-id YOUR_SELECTION --split dev --run-id lg-discovery-dev-001

Each CLI also offers visualize. Both Reflection CLIs retain compare; both Metadata CLIs retain the existing infer, score, visualize and audited --resume semantics. Run and experiment IDs must be unique. Do not copy old experiments into the new variant namespace.

## Result directory and safety contracts

Independent variants:

    scr/evaluation/result/<selection-id>/
      LangGraphSelfReflection/<split>/<run-id>/
      LangGraphRubricSelfReflection/<split>/<run-id>/
      LangGraphMetadata/<split>/<run-id>/
      LangGraphMetadataDiscoveryV2/<split>/<run-id>/

The output files retain the original variant's predictions, review/rubric decisions, traces, immutable manifest, optional scores and Trace Explorer. The metadata experiment's knowledge files and experiment manifest live under that new variant's experiments/<experiment-id>/ path.

Reference SQL remains scorer-only, never part of agent prompts, graph states or notes. Independent EX scoring uses the existing SQLite scorer and its strict manifest checks. Historical results from the old variants do not prove new LangGraph EX parity or cost differences.

## Validation

    uv run --frozen python -m compileall -q langgraph_agents
    uv run --frozen --with pytest python -m pytest -q langgraph_agents/tests
    uv run --frozen --with pytest python -m pytest -q langgraph_agents/tests tests/

The offline suite covers retry routing, SQL eligibility, prompt/settings parity, rubric stage order, output provenance, independent scoring, trace visualization, and metadata Dev/Test store isolation. Live model tests require SIWC authentication and quota and a local BIRD SQLite dataset. Existing legacy failures should be reported separately; do not misattribute them to migration.

## Executed VPS smoke checks (17 November 2026)

All four variants completed a **real** SIWC Luna (gpt-6-luna, reasoning effort none), BIRD Mini-Dev Dev **question 52** inference, persisted final SQL, passed the scorer's provenance checks, and generated an HTML Trace Explorer. The Self/Rubric one-question smoke limited B0 attempts to one (the normal CLI default remains three); the metadata variants used their normal budget settings.

| New variant | Observed graph path | Model/tool/SQL calls | Final SQL | Independent EX |
| --- | --- | --- | --- | --- |
| LangGraphSelfReflection | prepare → generator → review → decision → final | 6 / 4 / 2 | Present, reviewer FAIL | 0/1 |
| LangGraphRubricSelfReflection | prepare → requirements → generator → review → decision → refinement → final | 7 / 5 / 3 | Present, review UNCERTAIN | 1/1 |
| LangGraphMetadata | prepare → metadata-enabled agent → collect | 5 / 4 / 1 | Present | 0/1 |
| LangGraphMetadataDiscoveryV2 | A1 → B1 → C1 | 12 / 14 / 3 | Present | 0/1 |

This only proves the routes and scorer run for one question. Reviewer status and independent EX are not interchangeable. Do not treat 1/1 or 0/1 as the agent's generalization performance, or as parity with the historical full 500-question experiments. Live outputs remain under a separate, Git-ignored local selection named lg-remaining-smoke-20261117; no SQL gold or credentials are committed.
