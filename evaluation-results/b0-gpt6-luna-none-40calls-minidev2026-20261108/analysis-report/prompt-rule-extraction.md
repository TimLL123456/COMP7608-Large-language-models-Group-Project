# KORA B0 — Failure-to-rule extraction for generalized-v1

> 2026-11-09 · Evidence source: frozen BIRD Mini-Dev 2026 Development (400), pinned annotation revision `5b256b5a9c17478f06ed6912612e9a14d17065c8`.
> Baseline: GPT-6 Luna, requested reasoning `none`, **235/400 Dev EX (58.75%)**. Configured limits are 40 model / 40 total tool / 40 SQL calls; preserved execution history includes original 20-SQL cases and two 40-SQL reruns; this document is a **prompt design input, not a validated performance uplift**.

## Purpose and leakage boundary

Extract repeated mistakes from the [165-case failure inventory](failure-inventory.csv) and synthesize general rules transferable across databases. **Only the eight generalized instructions in** [generalized-v1.txt](../../../scr/baselines/prompts/generalized-v1.txt) **may reach model prompts**. This research document, failure cases, case IDs, score labels, Gold SQL and fixes are **offline/evaluator-only**, and must not be included in the Agent's retriever, workspace tools, prompt, test-time context, or demo index.

All 165 failures were compared at the Question/Gold/Agent SQL level: 153 have a provisional single primary label; 12 remain unresolved. The labels are candidate hypotheses, not independent counterfactual SQLite-verified causes; individual cases may have several errors.

## R1–R8 rule mapping (primary candidate only)

| Rule | Failure group | Count | Core instruction | Over-generalization guardrail |
| --- | --- | ---: | --- | --- |
| R1 | Value semantics | 49 | Interpret NULL, zero, blanks, sentinel strings, encoded numeric, numeric-vs-text ordering and validity with respect to question and field domain. | Do not add a global >0 / NOT NULL predicate; zero can be real. |
| R2 | Metric source and grain | 22 | Locate source-of-truth measure; verify numerator, denominator, unit scale, declared calculation and data granularity. | Do not assume an existing percent or a row COUNT matches a requested measure. |
| R3 | Aggregation population | 21 | Define the counted entity and weighting of AVG/SUM; watch one-to-many joins, DISTINCT, pre-aggregation, and whether zero-member groups stay in scope. | DISTINCT is not a universal fix; preserve legitimate repeated transactions/events. |
| R4 | Filter alignment | 19 | Ground each inclusion/exclusion in question or evidence; check restrictive extra filters introduced during data exploration. | Do not copy Gold predicates verbatim or invent domain filters. |
| R5 | Temporal semantics | 11 | Distinguish event, record, first/last, valid-as-of and ranking-after-filter; preserve timestamp boundaries. | Latest overall is not necessarily latest qualifying; but do not always select latest-valid. |
| R6 | Relationships | 7 | Inspect entity keys, many-to-many cardinality, optional entities and transitive relationship requirements. | Joining more tables can multiply counts or silently drop unmatched groups. |
| R7 | Output contract | 22 | Honor requested number/order/shape of columns and rows, scalar-vs-grouped, ordering, ties and numeric representation. | Never add a tie-breaking LIMIT 1 unless explicitly required. |
| R8 | Final SQL consistency | 2 | Preserve tested semantics through final edits; ensure a single SQLite-compatible SELECT/WITH statement. | Execution success does not imply correct result; avoid hardcoded precomputed answers. |
| ? | Unresolved / reference QA | 12 | Keep unresolved without claiming a verified cause. | Gold/reference annotation may require checking; no new rule inferred. |

Rule counts represent **label frequency among failed Dev questions**, not number of guaranteed recoverable cases. Do not interpret them as additive expected uplift.

## Evidence examples: mechanism, not answer

| Rule | Evidence case IDs (offline only) | Generalizable problem |
| --- | --- | --- |
| R1 | Q345, Q352, Q69, Q393 | Unknown measurements/sentinel codes and numeric-vs-text representation require domain-aware checks. |
| R2 | Q6, Q7, Q79, Q115, Q217 | Stored percentages, set sizes, crime figures and other metrics are not interchangeable with approximations. |
| R3 | Q67, Q88, Q131, Q172, Q223, Q236 | Averages and counts must operate at the intended entity grain, not multiplied join rows. |
| R4 | Q33, Q153, Q226, Q439 | An unsupported restriction may remove qualified observations; SQL exploration should not rewrite user intent. |
| R5 | Q176, Q228, Q231, Q443 | As-of, opened-before and latest-valid distinctions determine which rows qualify. |
| R6 | Q354, Q487, Q494 | Relationships may be transitive or multi-ended; joins and EXISTS clauses must follow specified entity links. |
| R7 | Q203, Q220, Q290, Q406, Q420 | Expected scalar columns, data types, row count, ordering and tied entities are part of correctness. |
| R8 | Q33, Q354, Q325, Q327 | Validated SQL can regress after revision; syntax or alias errors should be caught selectively. |

## Complete 165-case candidate mapping

The following QIDs are an **offline research index only**, never runtime instructions. Detailed evidence is retained in the [inventory](failure-inventory.csv) and archived [case studies](case-studies.md). Each case appears once here under its primary *candidate* group.

### R1 — Value semantics (49)

Q5, Q26, Q52, Q62, Q69, Q70, Q72, Q80, Q83, Q84, Q86, Q90, Q96, Q105, Q139, Q140, Q175, Q177, Q189, Q191, Q294, Q309, Q331, Q345, Q347, Q348, Q350, Q352, Q355, Q356, Q357, Q359, Q360, Q363, Q366, Q367, Q368, Q370, Q371, Q374, Q378, Q380, Q381, Q389, Q393, Q400, Q418, Q423, Q472

### R2 — Metric source and grain (22)

Q6, Q7, Q19, Q24, Q28, Q29, Q65, Q66, Q79, Q100, Q106, Q115, Q142, Q145, Q162, Q216, Q217, Q222, Q320, Q321, Q329, Q498

### R3 — Aggregation population (21)

Q67, Q82, Q88, Q109, Q120, Q128, Q131, Q134, Q172, Q205, Q219, Q223, Q230, Q235, Q236, Q238, Q258, Q266, Q379, Q411, Q481

### R4 — Filter alignment (19)

Q4, Q17, Q21, Q23, Q33, Q34, Q41, Q78, Q153, Q181, Q214, Q226, Q332, Q398, Q410, Q412, Q430, Q431, Q439

### R5 — Temporal semantics (11)

Q130, Q176, Q224, Q228, Q231, Q251, Q255, Q277, Q443, Q447, Q464

### R6 — Relationships (7)

Q152, Q227, Q354, Q480, Q487, Q488, Q494

### R7 — Output contract (22)

Q2, Q36, Q44, Q45, Q157, Q165, Q203, Q213, Q220, Q247, Q259, Q290, Q300, Q335, Q342, Q365, Q406, Q420, Q442, Q478, Q483, Q499

### R8 — Final SQL consistency (2)

Q325, Q327

### ? — Unresolved / reference QA (12)

Q155, Q173, Q201, Q242, Q245, Q339, Q358, Q377, Q417, Q438, Q492, Q497


## Current evaluation plan — 10 November 2026

- **Scope:** run only B0 with `--prompt-variant generalized-v1`; no new original-baseline inference and no pilot.
- **Limits:** 40 model calls, 40 total tool calls and 40 SQL executions per question for B0. SQL executions count toward the shared total-tool budget. Keep recursion limit 200, preview rows 20 and SQL timeout 300 seconds.
- **Frozen selection:** all 500 Mini-Dev 2026 questions, original 400 Dev / 100 local Test membership, seed 42, `--difficulty-ratio auto`.
- **Two runs:** Dev 400 then Test 100, provider `chatgpt-siwc`, model `gpt-6-luna`, requested reasoning effort `none`. Keep `generalized-v1.txt` unchanged, save separate predictions/traces/manifests and independently score each split.
- **Outputs:** Dev/Test/overall EX, database and query-category analysis, observed tokens, model/tool/SQL calls, latency and failure investigation. Retain all failures in denominators.
- **Historical comparison:** the previous Mini-Dev 2026 B0 configuration metadata lists 40/40/40 after alignment. Preserve `execution_budget_history`, which records original 20-SQL cases and two 40-SQL reruns. Do not rewrite those runtime facts or present historical results as a new matched control. Corrected/regressed historical transitions, if reported, are descriptive; prompt-only causal attribution and individual-rule effects are unproven.
- **Leakage boundary:** only the versioned R1–R8 addendum reaches the agent; this document, Gold SQL and case studies remain offline/evaluator-only.
- **Local Test:** previously reviewed; not an untouched external hidden set. Do not retune the frozen prompt on either split.

## Status

This document captures an **evidence-based hypothesis and test plan**. A separate inference run, fresh SQLite scoring and post-run comparison are required before saying generalized-v1 improves accuracy. Do not commit credentials, downloaded BIRD databases, raw run results or traces into the source repository.
