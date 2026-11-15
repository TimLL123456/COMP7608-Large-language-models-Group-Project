# Role-Specialized Self-Reflection Agent — KORA Final Experiment

**Status (15 November 2026):** Implementation and parallel shard/merge CLI are available; full Mini-Dev 2026 EX evaluation is **not yet verified**. Reuses the
existing B0 Text-to-SQL generator, read-only SQLite adapter, Rubric Reviewer,
and Mini-Dev 2026 strict EX scorer. The historical B0, SelfReflection and
RubricSelfReflection agents remain unchanged.

## Research question

Can a lightweight model responsible for database investigation and SQL
generation be made more accurate/cost-efficient by a stronger rubric-based
reviewer and a bounded feedback loop, compared with a lightweight-only
generator and strong-only generator?

This is **role specialization**, not difficulty-based model routing.

## Workflow (three main nodes)

```text
User Question
     |
Lightweight Generator (B0 investigation + SQL generation)
     | candidate SQL + observed investigation evidence
Strong Rubric Reviewer (atomic requirements, evidence-backed checks)
     |-- PASS ---> safe Final SQL + archived Review Report
     |-- NOT PASS + actionable feedback + budget
     |               |
     +---------------+----> retry full lightweight B0
     |
     +-- exhausted/no progress ---> best safe SQL (unverified)
```

The strong reviewer does **not** generate SQL. Even B0's forced finalization
uses the lightweight generator. The reviewer first extracts requirements after
the first SQL candidate; requirements are grounded in the original authorized
question/evidence, and subsequent reviews also receive bounded B0 tool-result
observations. Reviewer checklist includes output, filter, metric, grain, time,
source/join, value semantics, presentation and execution.

**Every completed review** emits an attempt-specific report (including PASS)
with `criteria_findings`, `review_status`, `overall_decision`,
`coverage`, `issues`, `regeneration_feedback`, observed execution, and
inspection trace. A PASS is archived and ends the loop. Confirmed FAIL or
material UNCERTAIN can produce actionable feedback for a bounded new B0 run.
ERROR is not treated as confirmed semantic FAIL. If the budget is exhausted,
only an SQL confirmed executable by the read-only adapter may be returned,
labeled `generated_unverified` or `generated_known_issues` (not verified).
An erroring or unsafe SQL is never an eligible final fallback.

## Running on the existing BIRD Mini-Dev 2026 selection

Prepare a deterministic selection once using
`python -m scr.cli.run_bird_b0_eval prepare` with your
`--dataset-root`, `--selection-id`, `--total-questions 500` and
`--dev-ratio 0.8`. Reuse the same selection for all variants. Do not
inspect the local held-out test answers when tuning.

Example model IDs below are **configuration examples, not verified model
rankings**. Choose provider credentials and models supported by your runtime.

```bash
# E0: lightweight-only B0, and E1: strong-only B0.
python -m scr.cli.run_bird_b0_eval infer \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id final-roles-v1 --split dev --run-id e0-light \
  --provider nvidia --model deepseek-ai/deepseek-v4.1-flash \
  --prompt-variant generalized-v1

python -m scr.cli.run_bird_b0_eval infer \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id final-roles-v1 --split dev --run-id e1-strong \
  --provider nvidia --model nvidia/nemotron-3-ultra-550b-a55b \
  --prompt-variant generalized-v1

# E2: lightweight generation + stronger independent rubric review.
python -m scr.agents.role_specialized.cli infer \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id final-roles-v1 --split dev --run-id e2-roles \
  --generator-provider nvidia --generator-model deepseek-ai/deepseek-v4.1-flash \
  --reviewer-provider nvidia --reviewer-model nvidia/nemotron-3-ultra-550b-a55b \
  --prompt-variant generalized-v1 \
  --max-attempts 3 --max-review-model-calls 40 \
  --max-inspections 39 --max-total-model-calls 240 \
  --max-total-tool-calls 240 --max-total-sql-calls 240

python -m scr.agents.role_specialized.cli score \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id final-roles-v1 --split dev --run-id e2-roles

python -m scr.agents.role_specialized.cli compare \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id final-roles-v1 --split dev --run-id e2-roles \
  --control-variant B0 --control-run-id e0-light

python -m scr.agents.role_specialized.cli visualize \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id final-roles-v1 --split dev --run-id e2-roles
```

Score E0 and E1 separately using the existing B0 score CLI, then compare
their scored results to E2. Repeat with `--split test` only after Dev choices
are frozen.

Each E2 run saves `predictions.jsonl`, `traces.jsonl`,
`reviews/review_reports.jsonl`, and `inference_manifest.json` in an
isolated run directory under
`<result-root>/<selection-id>/RoleSpecializedSelfReflection/<split>/<run-id>`.
The manifest records both roles, provider and model settings, prompt hashes,
call budgets and file checksums. Compare requires the same dataset,
question IDs and selection checksum; it **intentionally permits different
models**, because model allocation is the experiment.

Reported costs are `null` unless genuinely observed. EX is calculated
only by the offline scorer; gold SQL/results are excluded from inference.
Track reviewer false PASS, missed defects, per-question repairs/regressions,
calls, tokens, latency and SQL coverage. Differing compute budgets mean that
EX differences alone are **not** causal evidence of superior architecture.

## Luna + Terra: two-terminal sharded 500-question inference

The role-specialized runner defaults to **chatgpt-siwc** for both roles.
When these providers are used, the default generator model ID is
`gpt-6-luna`, and the provisional reviewer ID is `gpt-6.1-terra`.
**The Terra slug has not been confirmed for your specific account.**
List the authenticated account's available model names first:

```bash
uv run python -m scr.agents.role_specialized.cli models
```

Use the exact Terra slug printed by the command with `--reviewer-model`
on **both** workers, rather than assuming an alias. The optional
`--check-models` flag fails early if a chosen slug is not advertised.
Do not auto-substitute another model. Reasoning effort defaults to the
provider default; explicitly use `--generator-reasoning-effort` and
`--reviewer-reasoning-effort` when comparing fixed effort configurations.

The existing Mini-Dev 2026 selection already contains **400 local Dev
questions plus 100 local Test questions**. The new `--split all`
means the frozen, validated **Dev order followed by Test order**.
Shard positions are 1-based positions in this selection, **not**
BIRD `question_id` values. For two shards over a 500-row selection,
positions 1–250 and 251–500 are disjoint and cover all 500.

Start these commands **simultaneously in two separate terminals**, from
the existing Group Project working directory; replace
`<ACCOUNT_TERRA_SLUG>` with the checked model ID:

**Terminal 1 — positions 1–250**
```bash
uv run python -m scr.agents.role_specialized.cli infer \
  --selection-id final-roles-v1 --split all --run-id luna-terra-v1 \
  --shard-index 1 --shard-count 2 \
  --generator-provider chatgpt-siwc --generator-model gpt-6-luna \
  --reviewer-provider chatgpt-siwc --reviewer-model <ACCOUNT_TERRA_SLUG> \
  --prompt-variant generalized-v1 --check-models
```

**Terminal 2 — positions 251–500**
```bash
uv run python -m scr.agents.role_specialized.cli infer \
  --selection-id final-roles-v1 --split all --run-id luna-terra-v1 \
  --shard-index 2 --shard-count 2 \
  --generator-provider chatgpt-siwc --generator-model gpt-6-luna \
  --reviewer-provider chatgpt-siwc --reviewer-model <ACCOUNT_TERRA_SLUG> \
  --prompt-variant generalized-v1 --check-models
```

Each shard writes to a distinct, immutable directory:
`<result-root>/final-roles-v1/RoleSpecializedSelfReflection/all/luna-terra-v1/shards/shard-01-of-02`
and `shard-02-of-02`. No two processes ever write the same JSONL
files. The SIWC OAuth refresh-token path is guarded by an interprocess
file lock; provider calls remain independently concurrent. Both
workers must use the **same repository commit, dataset, selection,
model IDs/efforts, prompts and budgets**.

Once both workers finish, combine safely:

```bash
uv run python -m scr.agents.role_specialized.cli merge \
  --selection-id final-roles-v1 --split all --run-id luna-terra-v1 \
  --shard-count 2
```

Merge refuses missing shards, changed hashes, mismatched model/prompt
configuration, duplicate/missing/reordered question IDs, and existing
merged output. It writes the **500-question aggregate** under
`.../all/luna-terra-v1/` and derived, separately scoreable Dev/Test
artifacts under `.../dev/luna-terra-v1/` and
`.../test/luna-terra-v1/`.

Use the **existing scorer**, once per original local split:

```bash
uv run python -m scr.agents.role_specialized.cli score \
  --selection-id final-roles-v1 --split dev --run-id luna-terra-v1
uv run python -m scr.agents.role_specialized.cli score \
  --selection-id final-roles-v1 --split test --run-id luna-terra-v1
```

These commands reuse the default dataset/result root; add matching
`--dataset-root` and `--result-root` flags if your local dataset
uses custom locations. The scoring output is split-aware; **there is
no single 500-question official BIRD hidden-Test score**. If this is a
research evaluation, freeze all configuration decisions before
examining the local Test answers or tuning on the Test outcomes.

A run is not automatically resumable: retry with a fresh
`--run-id` after any failed shard. Provider concurrency/rate limits
may prevent a 2x throughput improvement.

## Offline validation

```bash
python -m unittest tests.test_role_specialized
python -m unittest tests.test_rubric_reviewer tests.test_rubric_self_reflection
python -m compileall -q scr/agents/role_specialized
```

This change does not perform live inference or a full 500-question benchmark;
those operations require the selected models, credentials, database files,
and provider quota. Use independent fresh run IDs and never overwrite old runs.
