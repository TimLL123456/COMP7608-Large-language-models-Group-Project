# Rubric Self Reflection — Current Agent Guide

**Variant:** `RubricSelfReflection` · **Evaluated 15 November 2026**

**Latest completed local BIRD Mini-Dev 2026 benchmark:** [326/500 (65.20%) strict EX](../evaluation-results/rubric-self-reflection-full-20261115/README.md) (Dev 255/400; local Test 71/100). All 500 final SQL outputs executed in the offline scorer. This is not the official hidden Test, and the archived 24 Dev DNS-related retries mean the result is not a strictly single-pass run.

## Workflow

~~~text
Question and authorized evidence
  → Unchanged B0 investigation → candidate SQL
  → Extract atomic requirements for output/filter/metric/grain/time/joins/values/etc.
  → Reviewer assesses each requirement against SQL and bounded inspections
       PASS → provisional accept
       FAIL + budget → new complete B0 attempt with diagnostic feedback
       UNCERTAIN / ERROR → preserve evidence and eligible SQL
  → Evidence-only final SQL refinement (when applicable)
  → Read-only execution check → final SQL and review report
~~~

Every material requirement needs an evidence-backed verdict; an overall reviewer PASS is **not** independently scored correctness. An executable but unverified candidate may be retained, never presented as verified. Invalid or unsafe SQL is not an eligible fallback. SQL output and evaluation scores are distinct.

The implementation is in [rubric_self_reflection/](../scr/agents/rubric_self_reflection/); its prompt and stage budgets are versioned. The [full experiment archive](../evaluation-results/rubric-self-reflection-full-20261115/README.md) documents exact budgets, retries, resources, paired correctness changes and limitations; no matched-compute causal improvement is claimed.

## Run

First install [Mini-Dev 2026](bird-setup.md) and prepare a unique selection through [B0](bird-b0.md#mini-dev-2026-current-workflow). Then run:

~~~bash
uv run python -m scr.agents.rubric_self_reflection.cli infer \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id YOUR_SELECTION --split dev --run-id rubric-dev-001 \
  --provider chatgpt-siwc --model gpt-6-luna \
  --reasoning-effort none --prompt-variant generalized-v1

uv run python -m scr.agents.rubric_self_reflection.cli score \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id YOUR_SELECTION --split dev --run-id rubric-dev-001

uv run python -m scr.agents.rubric_self_reflection.cli visualize \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id YOUR_SELECTION --split dev --run-id rubric-dev-001
~~~

Scoring uses evaluator-only reference SQL and does not call a model. Do not overwrite previous experiment IDs.

## Current output and reporting contract

Final statuses include provisional reviewer-verified SQL, `generated_unverified`, `generated_known_issues` and `missing`. Saved outputs include predictions, manifests, evidence/rubric reports, traces and independently scored results. Use the [Developer Guide](agent-development.md) for evaluation and safety conventions.

For the original design, hypothesis and baseline comparisons, follow the [historical Rubric Self Reflection guide](history/rubric-self-reflection-agent-pre-current-only-20261115.md), the [Self Reflection archived study](../evaluation-results/self-reflection-full-20261113/README.md), and the [complete rubric benchmark report](../evaluation-results/rubric-self-reflection-full-20261115/README.md).
