# Rubric Self Reflection Agent — independent V1

**Status (15 November 2026):** Implemented and evaluated on BIRD Mini-Dev 2026. **Variant:** `RubricSelfReflection`. The [full-run archive](../../evaluation-results/rubric-self-reflection-full-20261115/README.md) reports **326/500 (65.20%) local strict EX** (Dev 255/400; Test 71/100).

This standalone KORA Text-to-SQL variant adds **atomic requirement extraction**, **SQL-evidence mapping**, a **criterion-by-criterion review gate**, bounded full-B0 retry, and **post-review final SQL refinement**. It is deliberately separate from the existing `SelfReflection` variant, whose B0, coordinator, reviewer, prompts, CLI, tests and archived results must remain unchanged.


## Completed benchmark and limitations

On the [15 November 2026 local 500-question evaluation](../../evaluation-results/rubric-self-reflection-full-20261115/README.md), 326 final SQL results matched reference execution (65.20% EX). The prior Self Reflection archive recorded 350/500 (70.00%); paired comparison recorded **38 corrected and 62 regressed** cases. This is not a matched-compute causal comparison. Twenty-four Dev questions with DNS failures were rerun under the unchanged setup and are documented in retry provenance. Reviewer PASS remains a separate provisional assessment; all 500 final SQL queries executed in the offline scorer.


## Why this experiment

The historical 2026-11-13 `SelfReflection` BIRD Mini-Dev 2026 study achieved 350/500 (70.0% strict EX) with 498/500 SQL outputs. Its reviewer PASS category included 93 independently EX-incorrect results (not necessarily all confirmed semantic errors). The new variant tests whether a requirement-complete, evidence-grounded review can reduce such outcomes without harming the SQL-first output rate or introducing excessive UNCERTAIN results.

## Workflow

```text
Question + Evidence
  -> unchanged B0 investigation and Candidate SQL
  -> atomic requirements extracted once per question, without candidate SQL
  -> rubric reviewer: map every R01..Rn to SQL and bounded evidence
  -> decision (PASS, FAIL, UNCERTAIN, ERROR)
       PASS -> accept candidate
       FAIL + budget -> fresh full B0 with diagnostic feedback -> review again
       UNCERTAIN/ERROR -> preserve safe executable candidate
  -> if material FAIL/UNCERTAIN remains: one evidence-only refinement attempt
  -> strictly read-only SQL execution check; fallback if invalid
  -> best eligible SQL and explicit output status
```

Nine review dimensions: **output**, **filter**, **metric**, **grain**, **time**, **source_join**, **value_semantics**, **presentation**, and **execution**. Each atomic requirement has a stable ID, expected behavior, verbatim user/evidence quote, category and materiality. A review must provide one grounded PASS/FAIL/UNCERTAIN/N/A assessment per ID and assess overall question coverage. A material requirement cannot be N/A. The validator rejects partial, contradictory or ungrounded PASS decisions. The final assessment is provisional and distinct from offline EX correctness.

The reviewer alone does not write SQL. It can request at most two targeted read-only inspections per model round, bounded by a total per-review inspection cap. New SQL is produced only by unchanged B0 or the distinct **final refinement** stage. Refinement uses *existing* question, candidate, checks and tool observations; no additional schema/value investigation. It never converts a mere successful SQL execution into a reviewer PASS.

## Files

- `scr/agents/rubric_self_reflection/rubric.py` — requirement schemas, JSON parsing and coverage/verdict validation.
- `reviewer.py` — extraction, exact SQL execution, targeted evidence checks and decisions.
- `coordinator.py` — unchanged B0 orchestration, retry, budget and candidate selection.
- `finalizer.py` — one-shot SQL refinement with read-only validation and safe fallback.
- `prompts/` — versioned reviewer and refinement prompts.
- `cli.py` — independently runnable infer, score, compare and visualize workflow.
- `tests/test_rubric_*.py` — synthetic reviewer, SQL and coordinator regression tests.

No existing `SelfReflection` code is imported by this variant; it uses B0 and reusable dataset/evaluator/SQLite utilities.

## Budget defaults

| Resource | Default maximum |
| --- | ---: |
| B0 attempts | 3 |
| B0 per-attempt model, tool and SQL calls | 40 each, with finalization slots reserved |
| Reviewer model calls per attempt | 40 |
| Reviewer per-candidate inspection calls | 39 |
| Global model, tool and SQL calls | 240 each |
| Post-review refinement | 1 model call + 1 SQL check reserved; 0 new investigations |

Global limits override nominal per-attempt ceilings and can reduce or skip late reviews/retries. Provider calls that fail still consume model-call budget; partial usage metadata is reported as observed, never fabricated. Avoid assuming these caps guarantee SQL output.

## Running

Create a pinned Mini-Dev 2026 selection with the existing B0 preparation CLI and environment. Run from the group-project root:

```bash
uv run python -m scr.agents.rubric_self_reflection.cli infer \
  --selection-id YOUR_SELECTION --split dev --run-id rubric-v1-dev \
  --provider chatgpt-siwc --model gpt-6-luna \
  --reasoning-effort none --prompt-variant generalized-v1

uv run python -m scr.agents.rubric_self_reflection.cli score \
  --selection-id YOUR_SELECTION --split dev --run-id rubric-v1-dev

uv run python -m scr.agents.rubric_self_reflection.cli compare \
  --selection-id YOUR_SELECTION --split dev --run-id rubric-v1-dev \
  --baseline-variant SelfReflection --baseline-run-id EXISTING_SELF_REFLECTION_RUN

uv run python -m scr.agents.rubric_self_reflection.cli visualize \
  --selection-id YOUR_SELECTION --split dev --run-id rubric-v1-dev
```

`--baseline-variant B0` is also supported when selection/model/prompt hashes match. By design `compare` refuses mismatched datasets, selections, providers or prompts. Infer refuses to overwrite an existing result directory. `score` reads reference SQL **only** in the independent offline evaluator; no inference component accesses gold references. Run the Test split separately, only after fixing the design using Dev evidence.

## Outputs and research evaluation

Files live at `<result-root>/<selection-id>/RubricSelfReflection/<dev|test>/<run-id>/` and include `predictions.jsonl`, `traces.jsonl`, `reviews/rubric_decisions.jsonl`, `inference_manifest.json`, followed by independent `scores/` and optional comparison report. Each record retains original candidate SQL, rubric decisions, known uncertainty, evidence inspections, post-review refinement, usage and final SQL. Main output statuses:

- `verified`: Reviewer PASS on the actual accepted candidate (provisional).
- `generated_unverified`: executable candidate/refinement, not Reviewer PASS.
- `generated_known_issues`: safe candidate retained despite diagnosed material issue.
- `missing`: no known safe/executable SQL.

Compare strict EX, SQL output rate, PASS-but-EX-incorrect outcomes, correct SQL reviewed as UNCERTAIN/FAIL, corrected/regressed cases, calls, tokens and latency. Compute differs across variants; raw EX differences are not causal proof.

## References

- [Design draft in Notion](https://app.notion.com/p/417ce09ce40c81b583ecd968ace93587)
- [Historical Self Reflection design](https://app.notion.com/p/415ce09ce40c81f9b308e898d523f161)
- [Full Self Reflection evaluation (2026-11-13)](https://app.notion.com/p/417ce09ce40c8128b72ff8fb6b474375)
