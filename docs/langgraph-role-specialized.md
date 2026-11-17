# LangGraph Role-Specialized Self-Reflection Agent

**Status:** Implemented in the separate langgraph_agents/role_specialized/ package. This is an orchestration migration, not a new benchmark result. The 16 November 2026 archived 500-question Luna/Terra evaluation describes the **legacy** agent, not this graph.

## Architecture

This agent preserves the original SQL generator (Luna), evidence-grounded Rubric Reviewer (Terra) and safe-final-SQL policy, exposing five actual LangGraph nodes:

    START -> prepare_input -> generate_sql (Luna B0)
                              |             |
                              | candidate   | no SQL / duplicate / exhausted
                              v             v
                         review_sql      finalize_sql -> END
                         (Terra)            ^
                              |              |
                         route_decision -----+
                              |
                     actionable feedback + budget
                              |
                              +----> generate_sql (new B0 attempt)

The B0 model/tool loop still runs inside generate_sql. Its individual tool calls are not independently checkpointable graph nodes. Requirements are extracted once, after the first candidate, then reused. Review receives bounded actual B0 tool observations, never reference SQL. Terra does not create or edit SQL; failures or material uncertainty may send feedback to a new Luna B0 attempt.

Five graph nodes: prepare_input, generate_sql, review_sql, route_decision, finalize_sql. A reviewer PASS gives a reviewer-verified result, not an independent BIRD EX label. Unverified or known-issue candidates may be returned only if safe read-only execution succeeds. No guessing when every candidate is unsafe or absent.

## Parity defaults

| Setting | Value |
| --- | --- |
| Generator / reviewer | chatgpt-siwc: gpt-6-luna / gpt-6.1-terra |
| Both reasoning efforts | Provider default (None), unlike LangGraph B0 CLI default none |
| B0 system prompt | generalized-v1 |
| Attempts | 3 |
| Per B0 model/tool/SQL ceilings | 40 / 40 / 40, with finalization reserve |
| Per-review model calls / inspections | 40 / 39 |
| Global model/tool/SQL budgets | 240 / 240 / 240 |
| Model request / SQL timeout | 300 seconds each |
| SQLite preview | 20 rows |

No model substitutions occur if the requested model is unavailable. SIWC authentication, credentials and dataset files must be installed separately. The legacy Role Agent code, prompts and archived results remain unchanged.

## Quick start

From the repository root, after provisioning the BIRD Mini-Dev dataset:

    uv sync --frozen

    # Create a 5-question frozen selection if none is available.
    uv run python -m langgraph_agents.baseline.cli prepare \
      --dataset-root data/bird/mini-dev-2026 \
      --selection-id lg-roles-smoke --total-questions 5 --dev-ratio 0.8 --seed 42

    # Confirm the exact available SIWC model names.
    uv run python -m langgraph_agents.role_specialized.cli models

    uv run python -m langgraph_agents.role_specialized.cli infer \
      --dataset-root data/bird/mini-dev-2026 \
      --selection-id lg-roles-smoke --split dev --run-id lg-role-001 \
      --generator-provider chatgpt-siwc --generator-model gpt-6-luna \
      --reviewer-provider chatgpt-siwc --reviewer-model gpt-6.1-terra \
      --prompt-variant generalized-v1 --check-models

    uv run python -m langgraph_agents.role_specialized.cli score \
      --dataset-root data/bird/mini-dev-2026 \
      --selection-id lg-roles-smoke --split dev --run-id lg-role-001

    uv run python -m langgraph_agents.role_specialized.cli visualize \
      --selection-id lg-roles-smoke --split dev --run-id lg-role-001

Compare with a separately scored original Role Agent, B0, LangGraphB0, SelfReflection or RubricSelfReflection via the compare command. Comparisons require matching frozen question IDs, dataset manifest and selection checksum. Do not interpret differing accuracy as a causal LangGraph effect: stochastic model calls and budgets may differ.

## Two workers and safe recovery

For the *same* frozen 500-question selection, terminal 1 processes positions 1–250, terminal 2 processes positions 251–500. Keep all settings, prompt versions and source revisions identical between workers.

    # Terminal 1
    uv run python -m langgraph_agents.role_specialized.cli infer \
      --selection-id final-roles-v1 --split all --run-id lg-role-500 \
      --shard-index 1 --shard-count 2

    # Terminal 2
    uv run python -m langgraph_agents.role_specialized.cli infer \
      --selection-id final-roles-v1 --split all --run-id lg-role-500 \
      --shard-index 2 --shard-count 2

    # After both finish
    uv run python -m langgraph_agents.role_specialized.cli merge \
      --selection-id final-roles-v1 --split all --run-id lg-role-500 \
      --shard-count 2

The new CLI reuses the original shard slicing, per-run OS file locks, checked configuration and guarded merge. To resume an unscored, unmerged shard, stop its worker and rerun with the same arguments plus --start-position N --replace-existing. The backup and resume-history mechanisms protect saved records. Never overwrite scored or merged runs.

## Output and trace contracts

New results are isolated under:

    scr/evaluation/result/<selection-id>/
      LangGraphRoleSpecializedSelfReflection/<split>/<run-id>/
        inference_config.json
        predictions.jsonl
        traces.jsonl
        reviews/review_reports.jsonl
        inference_manifest.json
        scores/                   # after scoring
        trace-explorer.html       # after visualization

Every manifest records generator/reviewer identity, reasoning effort, prompt versions/hashes, budgets, graph version, selection checksum, source revision, artifact checksums and resume history. Each question trace preserves the attempt reports, individual review findings, feedback and **actual ordered graph_events**. Provider usage is observed rather than imputed; absent billing data does not establish cost.

Only the independent scorer may read gold SQL or reference results. A LangGraph checkpointer can be added to the graph builder, but replaying a model-invoking node may call external services again; the CLI's durable per-question JSONL and guarded recovery are the supported experiment recovery contract.

## Validation

    uv run --frozen --with pytest python -m pytest -q langgraph_agents/tests
    uv run --frozen --with pytest python -m pytest -q langgraph_agents/tests tests/
    uv run --frozen python -m compileall -q langgraph_agents/role_specialized

The tests compare old and new agent decisions deterministically for PASS, FAIL, UNCERTAIN, ERROR, duplicate SQL, invalid SQL, extraction errors and budget exhaustion. They do not make provider calls. A live inference/evaluation requires valid SIWC access, BIRD database files and quota.
