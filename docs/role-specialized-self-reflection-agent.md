# Role-Specialized Self-Reflection Agent — KORA Final Experiment

**Status (16 November 2026):** A complete **500-question local BIRD Mini-Dev 2026 EX evaluation** is archived ([full report and provenance](../evaluation-results/role-specialized-luna-terra-full-20261116/README.md)). The implementation also supports parallel shard/merge and explicit in-place resume. It reuses the B0 SQL generator, read-only SQLite adapter, Rubric Reviewer and independent EX scorer; the historical B0, SelfReflection and RubricSelfReflection variants remain unchanged.

## Research question

Can a lightweight model responsible for database investigation and SQL
generation be made more accurate/cost-efficient by a stronger rubric-based
reviewer and a bounded feedback loop, compared with a lightweight-only
generator and strong-only generator?

This is **role specialization**, not difficulty-based model routing.

## Completed local evaluation — 16 November 2026

The archived run used **Luna (`gpt-6-luna`) for investigation and SQL generation** and **Terra (`gpt-6.1-terra`) for requirement extraction, SQL review and feedback**. The Python coordinator selected the final eligible SQL. Both models used `chatgpt-siwc`, provider-default reasoning effort, `generalized-v1` and the recorded default budgets. It ran as **one sequential shard**, not the optional two-terminal parallel mode shown later in this guide.

| Frozen local split | EX-correct | Total | Execution Accuracy |
| --- | ---: | ---: | ---: |
| Development | 321 | 400 | 80.25% |
| Local Test | 80 | 100 | 80.00% |
| **Overall (local)** | **401** | **500** | **80.20%** |

Of 500 questions, **498** produced a non-missing final SQL. Final reviewer statuses were **PASS 391**, **UNCERTAIN 95**, **FAIL 12** and **ERROR 2**. These are reviewer decisions, **not** independent EX labels: an executable or reviewer-PASS SQL can still return the wrong result. The archived retained records report **6,497 model calls**, **6,345 tool calls**, **3,194 SQL calls** and **23,439,080 total tokens**; they exclude overwritten/unsaved interrupted work, and no billing cost is established.

**Recovery and limitations:** The original inference stopped after 109 saved records due to SIWC usage limits. The recovery kept positions 1–107 unchanged, replaced positions 108–109 (question IDs 131, 133) and completed the remaining questions under the same run ID. The archive documents **two source revisions** and saved backup/provenance; it is not an uninterrupted single-revision experiment. Q466 (Dev) and Q73 (local Test) had no eligible final SQL. The 400/100 split is **not** the official BIRD hidden Test, and the run does not isolate a causal improvement or establish cost savings over lightweight-only / strong-only controls. See the [archived experiment report](../evaluation-results/role-specialized-luna-terra-full-20261116/README.md) and [`performance-summary.json`](../evaluation-results/role-specialized-luna-terra-full-20261116/performance-summary.json) for exact details.

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

Start from the root of the [public KORA repository](../README.md), install dependencies with `uv sync`, and follow the [dataset setup guide](bird-setup.md). Downloaded SQLite databases and credentials are not included in Git.

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

## Luna + Terra: optional two-terminal sharded inference (not the archived run mode)

The role-specialized runner defaults to **chatgpt-siwc** for both roles.
When these providers are used, the default generator model ID is
`gpt-6-luna`; the **archived evaluation** used reviewer ID `gpt-6.1-terra`.
Model availability can differ by account and environment, so verify the available IDs before starting a new run.
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
the cloned public repository root; replace
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

Each fresh shard writes to a distinct directory (the backed-up, explicitly authorized in-place resume path below is an exception to immutability):
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

### Resume or replace records in the SAME run ID

A shard can now be resumed in place from an explicit **1-based position
within that shard**, rather than the BIRD question ID. Stop any worker using
this shard first. For example, if shard 1 saved 109 records and positions
108–109 have reviewer failures, preserve 1–107 and re-run 108–250:

```bash
uv run python -m scr.agents.role_specialized.cli infer \
  --selection-id final-roles-v1 --split all --run-id luna-terra-v1 \
  --shard-index 1 --shard-count 2 \
  --generator-provider chatgpt-siwc --generator-model gpt-6-luna \
  --reviewer-provider chatgpt-siwc --reviewer-model <ACCOUNT_TERRA_SLUG> \
  --prompt-variant generalized-v1 \
  --start-position 108 --replace-existing
```

Include all original reasoning-effort and budget flags if they were
customized. The command validates the immutable selection order, all readable
existing record IDs, generator/reviewer identities, and any saved configuration
or completed manifest, then copies the **original** three JSONL files and
existing metadata under `resume_backups/<UTC timestamp>/`. Positions before
108 retain their original raw bytes. Positions 108 onward are discarded and
recomputed in the original shard directory; the run ID is unchanged. The
resumption is recorded in `resume_history.jsonl` and the final manifest.
A fresh inference automatically saves `inference_config.json` before work
begins, enabling configuration verification after an interruption.

Legacy interrupted shards created before this feature may have no saved
configuration; their recorded identities and selection can be checked but
their original prompt and budgets cannot be independently proven. Preserve
the full command settings from the original run. Inference aborts without
committing a question when a reviewer-provider error or observed usage-limit
error occurs. Re-run from that same position after quota is available.

**Safety:** `--start-position` and `--replace-existing` must be supplied
together. Without them, an existing run is still protected. Never resume a
shard while an old-process worker is still writing; modern workers hold a
per-run OS file lock, automatically released if the process exits or
crashes. A scored or already-merged shard cannot be
replaced in place because it would invalidate published results. A resume
may leave the run incomplete if interrupted again; the same explicit
position can be used again. After completion, run `merge` as usual.

Merging checks model/prompt/budget and file hashes as before. A source
revision mismatch is accepted only when a shard has recorded in-place
resume history; the merged manifest lists every observed source revision,
so mixed-code provenance stays visible. Provider concurrency/rate limits
may prevent a 2x throughput improvement.

## Offline validation

```bash
python -m unittest tests.test_role_specialized
python -m unittest tests.test_rubric_reviewer tests.test_rubric_self_reflection
python -m compileall -q scr/agents/role_specialized
```

The documented 500-question run is now complete and archived; these commands are **offline regression checks**, not a new live inference or a rerun of the benchmark. The original evaluation archive records 41 initial and 22 recovery offline tests plus a passing `compileall` check; a documentation update does not rerun them. New inference still requires model access, database files and quota. Prefer fresh run IDs; use explicit guarded resume only for eligible unscored/unmerged shards, and never overwrite scored or published results.
