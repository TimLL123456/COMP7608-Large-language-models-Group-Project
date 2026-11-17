# KORA LangGraph Agents — parity-first migration

An **explicit outer LangGraph `StateGraph`** that wraps the original KORA Deep Agents B0 generator. Original agent scripts under `scr/`, prompts, read-only SQLite tools, B0 per-run budgets, and scoring semantics remain intact. This new folder is **not** a new SQL reasoning algorithm or a claim of improved BIRD EX accuracy.

## Runtime defaults (new CLI only)

| Setting | LangGraph B0 default |
| --- | --- |
| Provider | `chatgpt-siwc` |
| Model | `gpt-6-luna` |
| Reasoning effort | `none` |
| Prompt | `generalized-v1` (same prompt as historical Luna benchmark; original `baseline` available via flag) |
| Model/tool/SQL limit | 40/40/40, as existing B0 |
| Request/SQL timeout | 300 seconds each, as existing B0 |
| Preview rows | 20 |

The existing B0 CLI **still defaults to NVIDIA**. No model is silently substituted. SIWC auth must already exist: `uv run python -m scr.baselines.siwc_auth`. Provider/model availability is account dependent. Inference consumes model quota.

## Architecture

```text
START → prepare_input → run_b0 (existing Deep Agent) → collect_output → END
```

Three graph nodes have actual execution semantics. The original B0 model/tool loop runs **inside** `run_b0`, not as independently resumable outer graph nodes. The wrapper adds **no** new model calls, reviewer calls, SQL checks, retries or forced answers. It collects graph node-completion events separately from original B0 structured tool/model traces. Optional LangGraph checkpointing is supported by `build_graph(checkpointer=...)`, but replaying an interrupted `run_b0` node may repeat external model calls; no exactly-once guarantee.

## Installation and commands

From project root (folder containing `pyproject.toml`):

```bash
uv sync
uv run python -m scr.datasets.setup_bird --release latest --revision 5b256b5a9c17478f06ed6912612e9a14d17065c8
uv run python -m scr.datasets.setup_bird --release latest --verify-only

uv run python -m langgraph_agents.baseline.cli prepare \\
  --dataset-root data/bird/mini-dev-2026 \\
  --selection-id langgraph-b0-smoke --total-questions 5 \\
  --dev-ratio 0.8 --seed 42

uv run python -m langgraph_agents.baseline.cli infer \\
  --dataset-root data/bird/mini-dev-2026 \\
  --selection-id langgraph-b0-smoke --split dev \\
  --run-id lg-b0-001

uv run python -m langgraph_agents.baseline.cli score \\
  --dataset-root data/bird/mini-dev-2026 \\
  --selection-id langgraph-b0-smoke --split dev \\
  --run-id lg-b0-001

uv run python -m langgraph_agents.baseline.cli visualize \\
  --selection-id langgraph-b0-smoke --split dev --run-id lg-b0-001
```

Use a **new** selection/run ID for each experiment. `--result-root` and `--dataset-root` accept overrides; the original selection logic preserves its Dev/Test frozen split. The CLI defaults to the historical Luna **generalized-v1** prompt (not guaranteed identical stochastic SQL outputs); use `--prompt-variant baseline` to opt into the original B0 system prompt. To run the old NVIDIA default explicitly, use `--provider nvidia`, with original NVIDIA credentials and model behavior.

## Output path

```text
scr/evaluation/result/<selection_id>/
  selection_manifest.json
  dev.jsonl
  test.jsonl
  LangGraphB0/<dev-or-test>/<run_id>/
    predictions.jsonl
    traces.jsonl                    # original B0 structured_events + graph_events
    inference_manifest.json
    scores/                        # created by score only
      summary.json
      per_question.jsonl
      per_question.csv
      run_manifest.json
      report.md
    trace-explorer.html             # optional visualize
```

The scorer uses the original BIRD EX evaluator; reference SQL is never included in the agent input. The `LangGraphB0` variant is added to the evaluator's allowlist without changing how EX is computed. Historical `B0/` output directories are not overwritten. The default result tree is ignored by Git.

## Validation and limits

Run `uv run --with pytest python -m pytest -q langgraph_agents/tests tests/`; this may fetch pytest when not already installed. The new tests cover graph node transitions, no gold SQL leakage, output eligibility, provider defaults, manifests, scorer tag and read-only SQLite safety. Full 500-question inference is not part of the smoke phase. Report live provider authentication errors as blocked, never fall back to another model.

Public source: https://github.com/TimLL123456/COMP7608-Large-language-models-Group-Project
Design and progress: https://app.notion.com/p/41bce09ce40c810093b4cbc2ca55fc0b

## Role-Specialized Self-Reflection — second LangGraph variant

A second independent variant lives in langgraph_agents/role_specialized/ and implements five actual LangGraph nodes: prepare_input, generate_sql, review_sql, route_decision and finalize_sql. The reviewer decision has a real conditional feedback edge to the generator, subject to the original budgets and safe SQL rules.

The generator remains Luna (gpt-6-luna), the rubric reviewer Terra (gpt-6.1-terra), both using chatgpt-siwc with **provider-default reasoning effort**, and generalized-v1 prompt. This differs from the separate LangGraph B0-only CLI's explicit default reasoning effort none. Legacy role code, prompts, shard/merge/resume behavior, independent EX scoring and its 500-question archive are unchanged.

    uv run python -m langgraph_agents.role_specialized.cli models
    uv run python -m langgraph_agents.role_specialized.cli infer \
      --selection-id final-roles-v1 --split dev --run-id lg-roles-dev
    uv run python -m langgraph_agents.role_specialized.cli score \
      --selection-id final-roles-v1 --split dev --run-id lg-roles-dev
    uv run python -m langgraph_agents.role_specialized.cli visualize \
      --selection-id final-roles-v1 --split dev --run-id lg-roles-dev

New variant: LangGraphRoleSpecializedSelfReflection, with independent output directories. See [full architecture, validation and recovery guidance](../docs/langgraph-role-specialized.md). The archived legacy 500-question benchmark does **not** establish new LangGraph EX accuracy.
