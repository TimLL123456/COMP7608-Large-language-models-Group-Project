# KORA B0 — BIRD Mini-Dev 2026 Baseline Performance and Failure Analysis

> **Analysis date:** 2026-11-09 · **Run:** B0, `chatgpt-siwc`, `gpt-6-luna`, requested reasoning effort `none`  
> **Dataset:** BIRD Mini-Dev 2026 SQLite, pinned annotation revision `5b256b5a9c17478f06ed6912612e9a14d17065c8`  
> **Scope:** Frozen local Development 400 / Local Test 100. Diagnostic prioritization and improvement design use Development.  
> **Status:** Retrospective, read-only analysis; no fresh inference, SQLite rescoring, or exhaustive independently verified causal labeling.

**Execution Accuracy (EX)** compares the result of the submitted final SQL with the reference result. It is not simply the proportion of syntactically executable SQL. This report combines the archived scores, predictions, structured traces, official questions/evidence, and matching-release Gold SQL to identify failure mechanisms and propose controlled tests. Gold SQL is strictly evaluation-only and must never be exposed to an agent prompt or retrieval tool.

## Contents
- [0. Executive Summary](#summary)
- [1. Data Provenance and Integrity](#integrity)
- [2. Overall Performance and Difficulty](#overall)
- [3. Database-Level Analysis](#databases)
- [4. Query Categories and Gold SQL Features](#categories)
- [5. Tables, Columns and Data Grain](#tables)
- [6. Observable Inference Traces](#traces)
- [7. Root-Cause Candidate Taxonomy](#causes)
- [8. Detailed Failure Cases](#cases)
- [9. Prioritized Improvements](#priorities)
- [10. Controlled Experiments](#experiments)
- [11. Limitations and Reference QA](#limitations)
- [12. Source Links](#sources)

<a id="summary"></a>
## 0. Executive Summary

| Finding | Result | Interpretation |
| --- | --- | --- |
| Overall EX | **294/500 = 58.80%** | Local Development + Local Test, not official hidden test |
| Development | **235/400 = 58.75%** | **165 failures** (163 incorrect result + 2 final SQL error) |
| Local Test | **59/100 = 59.00%** | 41 failures (40 incorrect result + 1 final SQL error) |
| Final result mismatch | **203/206 total failures** | The central challenge is SQL semantics rather than syntax |
| Worst Development database | `superhero`: **11/40 = 27.5%** | 29 failures |
| Repeated superhero numeric sentinel pattern | **15/29 superhero failures** | Gold requires positive measurement; agent omits matching `>0` predicate |
| Final SQL not text-matched to a tested SQL (Development) | **325/400** | Includes 197 correct and 128 failed; text mismatch is **not** causal evidence |
| Failed cases without complete inspection of Gold-referenced physical tables | **9/165**, approximate | Seeing the right table is different from understanding its values |

**Main recommendation:** Start with small, targeted experiments addressing **value semantics and metric grain** before increasing reasoning effort, SQL-call budget, or architecture complexity. The strongest concentrated candidate is a cluster of 15 `superhero` failures involving `height_cm`/`weight_kg` validity. This follow-up also reviews all 165 Development failures: 153 receive a provisional single primary category and 12 remain unresolved. **This is not a confirmed 15-case improvement**: causal repair requires paired re-execution, and some cases may have additional errors.

### Update: Complete provisional review of 165 Development failures (2026-11-09)
All **500/500** archived question/evidence/database/difficulty tuples (400 Development + 100 local Test) matched the same pinned 2026 official annotations. The original 97 SQL-comparison/reference-QA cases are preserved; **68 additional Development failures** were compared against their matching official Gold and final Agent SQL. All 165 now have a provisional primary-cause decision or explicit unresolved status in the [failure inventory](failure-inventory.csv): **153 candidates, 12 unresolved**.
| Provisional primary cause | Cases | Share of 165 failures |
| --- | ---: | ---: |
| Value semantics / encoded values | 49 | 29.7% |
| Output contract / representation | 22 | 13.3% |
| Measure source / grain | 22 | 13.3% |
| Aggregation / population | 21 | 12.7% |
| Missing / unsupported filters | 19 | 11.5% |
| Unresolved / comparison needed | 12 | 7.3% |
| Temporal logic | 11 | 6.7% |
| Entity relationships / joins | 7 | 4.2% |
| SQL dialect / validation | 2 | 1.2% |
Each case is counted **once** here for prioritization, but a query may contain multiple defects. These are descriptive, evidence-based **candidate** labels—not a counterfactually verified, exclusive causal census. Do not interpret counts as guaranteed fixes or accuracy uplift. Keep Gold-derived materials out of agent runtime, retrieval corpora and benchmark prompts.

<a id="integrity"></a>
## 1. Data Provenance and Integrity

Verified across pinned official and local records:

| Check | Result |
| --- | --- |
| Official annotations | 500 IDs (0–499), unique; Gold SQL available at fixed revision |
| Agent-facing question/evidence/database/difficulty | Exact match to corresponding official records; 0 differences |
| Scores and traces | 400 Development, 100 Local Test; all 500 scored and trace-backed |
| Final SQL | Present for all questions |
| Local scoring status | Development: 235 correct, 163 incorrect result, 2 SQL errors; Test: 59, 40, 1 |
| Fresh execution in this research | **Not performed**; scoring uses frozen evaluator outputs |

**Critical execution-budget caveat:** The exported `configuration.json` currently says `max_sql_executions=40`, but its `execution_budget_history` shows **498 questions were executed under an actual 20-SQL-call limit**. Only rerun Development Q421 and Test Q107 used 40. Model/total-tool caps are documented as 40, request timeout 300 seconds, scorer timeout 600 seconds. This is a **mixed-budget archive**, not a uniform 40-SQL-call study.

The historical Original Mini-Dev baseline scored **299/500 (59.8%)**, whereas this *different* Mini-Dev 2026 release scored 294/500. Treating the 1 percentage-point numerical difference as a controlled regression would be invalid: annotations, question IDs and difficulty labels changed.

<a id="overall"></a>
## 2. Overall Performance and Difficulty

| Split | Correct | Total | Failures | EX |
| --- | ---: | ---: | ---: | ---: |
| Development | 235 | 400 | **165** | **58.75%** |
| Local Test | 59 | 100 | 41 | 59.00% |
| **Total** | **294** | **500** | **206** | **58.80%** |

| Difficulty, overall | Correct / total | EX | Failures |
| --- | ---: | ---: | ---: |
| Challenging | 267/460 | 58.04% | 193 |
| Moderate | 22/32 | 68.75% | 10 |
| Simple | 5/8 | 62.50% | 3 |

Development specifically: Challenging **213/369**, Moderate **17/24**, Simple **5/7**. The release is **92% Challenging**, so merely emphasizing difficult questions adds little discrimination; Simple/Moderate are too small for strong inference. Prefer database, task semantics, required query features and trace-based strata.

<a id="databases"></a>
## 3. Database-Level Analysis (Development only)

| Database | Correct / total | EX | Failures |
| --- | ---: | ---: | ---: |
| `superhero` | 11/40 | 27.5% | 29 |
| `card_games` | 32/55 | 58.2% | 23 |
| `financial` | 17/37 | 45.9% | 20 |
| `thrombosis_prediction` | 48/68 | 70.6% | 20 |
| `california_schools` | 21/40 | 52.5% | 19 |
| `toxicology` | 13/25 | 52.0% | 12 |
| `formula_1` | 33/44 | 75.0% | 11 |
| `codebase_community` | 16/25 | 64.0% | 9 |
| `european_football_2` | 16/25 | 64.0% | 9 |
| `student_club` | 22/30 | 73.3% | 8 |
| `debit_card_specializing` | 6/11 | 54.5% | 5 |

The top five databases by *absolute* Development failure count—superhero, card_games, financial, thrombosis_prediction and california_schools—contain **111/165 = 67.3%** of all failures.

Even among Challenging tasks, `superhero` performs **10/38 = 26.3%** versus `formula_1` at **33/43 = 76.7%**. `list_tables` traces show approximately 10 and 13 tables, respectively. Thus table count by itself does not explain the gap. More plausible hypotheses include **field/value conventions, choice of measure, temporal semantics and multiplicity of entity relationships**; none should be asserted causal without a controlled follow-up.

### Provisional primary-cause patterns by database
| Database | Development failures | Most frequent candidate categories |
| --- | ---: | --- |
| `superhero` | 29 | Value semantics 20; entity/join 1 |
| `card_games` | 23 | Value semantics 12; metric/grain 6 |
| `financial` | 20 | Aggregation/population 7; metric/grain 3; temporal 3 |
| `thrombosis_prediction` | 20 | Filter 6; value semantics 5 |
| `california_schools` | 19 | Filter 7; metric/grain 6 |
| `toxicology` | 12 | Entity/join 4; output contract 3 |
| `formula_1` | 11 | Output contract 3; temporal 3 |
| `codebase_community` | 9 | Aggregation/population 4 |
| `european_football_2` | 9 | Value semantics 4 |
| `student_club` | 8 | Metric/grain 3; final SQL errors 2 |
| `debit_card_specializing` | 5 | Scattered across categories; no dominant single pattern |
This is descriptive, not a causal ranking of databases. Differences in question mix, values and schema conventions remain uncontrolled.

<a id="categories"></a>
## 4. Query Categories and Gold SQL Features

The categories below are **overlapping exploratory labels**: natural-language labels are keyword heuristics, SQL features use the required *Gold* SQL (not solely predicted SQL). Because a question can appear in multiple rows, counts must not be summed, and associations do not establish causes.

| Category/feature | Development n | Failures | EX |
| --- | ---: | ---: | ---: |
| NL: Average / mean / median | 114 | 59 | 48.2% |
| NL: Count / number | 230 | 111 | 51.7% |
| NL: Ranking / Top-K / extrema | 192 | 78 | 59.4% |
| NL: Temporal / date | 190 | 72 | 62.1% |
| NL: Conditional / negation | 183 | 77 | 57.9% |
| NL: Rate / percentage / ratio | 56 | 23 | 58.9% |
| Gold: GROUP BY | 145 | 68 | 53.1% |
| Gold: LIMIT | 44 | 22 | 50.0% |
| Gold: CASE | 88 | 43 | 51.1% |
| Gold: COUNT(DISTINCT) | 108 | 46 | 57.4% |
| Gold: CTE | 118 | 50 | 57.6% |
| Gold: Subquery | 247 | 105 | 57.5% |
| Gold: LEFT JOIN | 68 | 24 | 64.7% |

Mean/average cases have **59 failures out of 114 (48.2% EX)**; count-related questions **111 failures out of 230 (51.7% EX)**. The problem is often *which values and rows to aggregate*: denominator, NULL/zero validity, deduplication, join amplification, and whether a question expects one row or one row per entity.

Syntactically different SQL can be semantically equivalent: CTE versus subquery, JOIN versus EXISTS, and varying aliases are not automatic errors. The structural breakdown is useful for case selection, not a per-feature causal attribution.

<a id="tables"></a>
## 5. Tables, Columns, and Data Grain

| Gold-referenced physical table (Development) | Correct / relevant | Failed |
| --- | ---: | ---: |
| `superhero.superhero` | 10/38 | 28 |
| `financial.district` | 13/30 | 17 |
| `financial.account` | 12/29 | 17 |
| `card_games.cards` | 29/44 | 15 |
| `california_schools.frpm` | 10/24 | 14 |
| `toxicology.atom` | 10/22 | 12 |
| `toxicology.connected` | 3/13 | 10 |
| `card_games.set_translations` | 3/12 | 9 |

These are overlapping *Gold table reference* counts, not independent table-caused failures.

A heuristic comparison of the physical tables referenced in Gold SQL against each agent's `inspect_table` events found that **156/165 failed Development cases had inspected the required physical tables**, while **9/165** lacked at least one inspection. This is an approximation (regex-based FROM/JOIN parsing cannot perfectly distinguish CTE aliases and complex quoted identifiers). It does, however, caution against focusing solely on more schema-inspection calls.

Illustrative field/grain traps:

- `superhero.weight_kg`, `height_cm`: unknown values can be encoded as 0 as well as NULL.
- `card_games.sets.totalSetSize` versus `cards` rows: full set size is not the same measure as observed rows of printings.
- `financial.district.A16`: a stored crime count for 1996; not a count of bank transactions.
- `student_club.expense_description`: comma-delimited purchases require item-level expansion.
- `toxicology.connected`: atom–bond–molecule relationships demand correct pairwise join and distinct bond grain.
- `thrombosis_prediction.Laboratory`: "latest valid measurement" versus "latest laboratory record."

<a id="traces"></a>
## 6. Observable Inference Traces

| Structured event or call, all 500 | Count |
| --- | ---: |
| Model events | **2,842** |
| Tool calls and matching results | **3,227 + 3,227** |
| `list_tables` / `inspect_table` | 504 / 1,417 |
| `execute_sql` / `grep` | **1,301** / 5 |
| SQL tool-call errors | 18 |
| Final-validation events | 500 |

These are observable **model messages, tool arguments, SQL rows/errors, and final submissions**, not a hidden chain-of-thought transcript. Requested reasoning effort was `none`; observed reasoning token metadata is 0. It is not valid to infer the model's full internal reasoning process.

**Development efficiency:** 1,021 SQL calls (mean 2.55), 2,549 tool calls (mean 6.37), 2,255 model calls (mean 5.64). Mean input tokens 20,715.93, output tokens 433.43, total tokens 21,149.35, cached input tokens 11,048.32, wall latency approximately 21.94 seconds. Cached input is *part of* input tokens, not additional tokens; `cost_usd=null` means unobserved, **not zero cost**.

| SQL executions per Development case | Cases | Correct | EX |
| --- | ---: | ---: | ---: |
| 1 | 177 | 98 | 55.4% |
| 2–3 | 137 | 86 | 62.8% |
| 4–6 | 61 | 41 | 67.2% |
| 7+ | 25 | 10 | 40.0% |

Correct cases averaged ~2.51 SQL calls; failures ~2.61. Cases with many attempts may be inherently more difficult; this is not evidence that tool calls cause failures or that budget increases would fix them.

**Final SQL vs prior execution, normalized text comparison:** Development correct **38 matched / 197 unmatched**, Development failures **37 matched / 128 unmatched**. Therefore **128/165 = 77.6%** failed cases *did not text-match* a prior executed SQL, but **197/235 = 83.8%** correct cases also did not. Do not equate text mismatch with a semantic difference, a lack of all testing, or 128 recoverable cases. Selective checking of high-risk changes (extra filters, granularity drift, SQL dialect) is a more defensible experiment.

### New trace findings: post-execution decision regression
- **Q33 (`california_schools`):** The agent calculated 572/12 ≈ 47.67, then introduced an unsupported `SOCType LIKE '%(Public)%'` predicate, reduced the count to 519 and finalized `SELECT 519.0 / 12` (43.25). This is observable exploration-induced predicate drift.
- **Q354 (`superhero`):** An executed query considered heroes sharing **any** power with a Cryokinesis holder and returned 9.1; final SQL narrowed this to sharing Cryokinesis itself. This is a candidate executed-to-final semantic regression.
- **Q203 (`financial`):** A SQL tool result represented population as the text `"1204953"`; Gold casts A4 to INTEGER. A type/output mismatch is plausible but unconfirmed without actual scorer/result comparison.
- **Q497 (`toxicology`):** Gold examines `connected.atom_id` while the agent examines both bond endpoints. Add to the reference-QA watchlist, without claiming the official annotation is wrong.
Structured traces expose model/tool events, not hidden chain-of-thought. A final SQL text mismatch alone is **not evidence of semantic regression**: 197 correct Development cases also lack an exact normalized text match.

<a id="causes"></a>
## 7. Root-Cause Candidate Taxonomy

| Mechanism | Evidence | Representative questions | Status |
| --- | --- | --- | --- |
| Sentinel / encoded numeric values | Gold `weight_kg > 0` or `height_cm > 0`; agent lacks matching predicate | Q345, Q348, Q350, Q363, Q371, Q374, Q380 | Strong repeated candidate, no repair rerun |
| Wrong metric source / grain | `sets.totalSetSize` vs card rows; `district.A16` vs transactions | Q65, Q79, Q162, Q217, Q320, Q321 | Clear SQL differences |
| Denominator / aggregation population | Averaging comments vs users; LEFT vs INNER join | Q128, Q379, Q411, Q481 | Substantive semantic mismatches |
| Extra or missing filter | Unexpected Good/Thrombosis restriction; missing Admission | Q332, Q398, Q412, Q430 | Observable predicate drift |
| Temporal semantics | latest non-null measure; as-of-date balance | Q224, Q251, Q443, Q447 | Evidence-based hypotheses |
| Output contract | wrong columns, extra labels, row/column grain | Q2, Q157, Q165, Q335, Q365 | Visible shape mismatch |
| Final SQL dialect/syntax | `>= ALL` unsupported by SQLite; undefined `item` column | Q325, Q327 | Two scored Development SQL errors |
| Annotation/reference watchlist | Question may differ subtly from Gold interpretation | Q235, Q255, Q325 | QA candidates, not confirmed defects |

**High-impact concentration:** In the 29 failed Development `superhero` questions, **15** share a Gold positive-measurement predicate omitted from the agent's final query: **Q345, 348, 350, 355, 356, 357, 360, 363, 366, 367, 368, 370, 371, 374, 380**. These are **51.7%** of superhero failures and **9.1%** of all Development failures. No targeted zero-value profiling query was visible in those traces. Q381 Gold also explicitly treats unknown weight as 0 or NULL, reinforcing the domain-specific value convention.

If all 15 were independently corrected with **zero regressions**, the mathematical maximum attributable gain on 400 Development questions would be **+15/400 = +3.75 percentage points** (58.75% → 62.50%). This is an *upper-bound thought experiment*, **not measured uplift**; other differences may coexist in those SQL statements.

<a id="cases"></a>
## 8. Detailed Failure Cases

**Q345, superhero — unknown weight:** Gold uses `s.weight_kg > 0`; agent uses `s.weight_kg IS NOT NULL`. The trace shows `list_tables → inspect_table(superhero) → inspect_table(colour) → execute_sql`, returning **967.6** before finalizing the same SQL. The query executes, but may include zero-weight sentinel values. This motivates value profiling.

**Q33, california_schools — exploration-induced filter drift:** The agent first found **572** schools and calculated **572/12 = 47.6667**, consistent with the Gold filter logic. It then added an unsupported `SOCType LIKE '%(Public)%'` condition, reduced the count to **519**, and finally emitted `SELECT 519.0 / 12;` = **43.25**. More exploration is not guaranteed to improve alignment; every new filter should be justified by question/evidence.

**Q65/Q79, card_games — wrong measure:** Gold uses `sets.totalSetSize` for complete set size; agent counts `cards` rows. In Q65, it also groups by set where a single total is required. Fix both metric source and output grain.

**Q217, financial — wrong column meaning:** Gold reads `district.A16` (1996 crimes). The agent calculates `COUNT(trans.trans_id)`, i.e. bank transactions, rather than crimes. Schema listings alone do not provide adequate business semantics.

**Q379, superhero — denominator shifted by JOIN:** Gold retains heroes with unknown alignment in the denominator via `LEFT JOIN`; agent uses `INNER JOIN` and may exclude them. The planner should explicitly define numerator and denominator populations.

**Q443/Q447, thrombosis_prediction — latest valid measurement:** Gold chooses the latest **non-null IgG/RNP** test; agent chooses the latest laboratory record regardless of whether that field was measured. Candidate: latest-valid-row planning.

**Q325/Q327, student_club — final SQL errors:** SQLite does not support Q325's `>= ALL (...)`; Q327's final SQL refers to an `item` column not present in its scope. A narrow final SQL execution/syntax check addresses these errors, but not the other 163 Development incorrect-result cases.

See [Case Studies](case-studies.md) for side-by-side Gold/agent SQL and observable trace evidence, and [Failure Inventory](failure-inventory.csv) for every failed Development question and investigation status.

### Additional cross-category cases (newly reviewed)
- **Q6/Q7, California Schools:** Stored eligibility percentages used instead of count/enrollment × 100 derived according to the question evidence.
- **Q67/Q88, Card Games:** Printing-level ruling rows counted instead of distinct ruling content for a named card.
- **Q115, Card Games:** `sets.totalSetSize` is not equivalent to `COUNT(cards)`; added LIMIT 1 may lose ties.
- **Q131/Q223/Q236:** Row-level joins weight user/district measures by post, account or loan multiplicity.
- **Q172, European Football:** Appearance-weighted player height instead of distinct-player height.
- **Q406/Q420, Thrombosis:** Grouped two-row output instead of two scalar count columns.
- **Q497, Toxicology:** Possible reference/semantics issue about connected bond endpoints; keep unresolved.
Full SQL and observable trace notes for representative new cases appear in the [case-study appendix](case-studies.md).

<a id="priorities"></a>
## 9. Prioritized Improvements

| Priority | Candidate | Expected target / caveat |
| --- | --- | --- |
| **P0 / E1** | Prompt-only Value/Semantic Grounding | NULL vs 0, enums, encoded values; may overfit if tailored to known benchmark cases |
| **P0 / E2** | Query Contract / Granularity checklist | Population, numerator/denominator, measure source, tie logic, result columns/rows |
| **P1 / E3** | On-demand Column Value Profiling | Query data values and sentinel distributions; extra tool/latency cost |
| **P1** | Aggregation and Temporal planning | Per-entity distinct grain, latest valid, as-of balance, exact boundary |
| **P1 / E4** | Selective Final SQL verification | Dialect and unjustified final edits; syntax validity does not establish EX |
| **P2 / E5** | Reasoning effort ablation | Measure whether higher effort improves accuracy enough to justify cost |
| **P2** | Complex architecture/routing | Defer until controlled experiments identify a clear use case |

Do **not** presume B1–B4 are implemented. E1–E5 denote *proposed, independent experiments*, not renamed B1–B4 milestones or measured upgrades.

<a id="experiments"></a>
## 10. Controlled Experiment Design

Establish uniform **dataset revision, Development membership, provider/model, schema and evidence policy, tools, execution budgets, timeouts, evaluator and prompts**. Because the archived B0 mixed execution budgets, consider first obtaining a uniform-budget B0 comparator or explicitly controlling/reporting that confound.

| Comparison | Only intervention | Target cases / controls |
| --- | --- | --- |
| E1 vs B0 | Value semantics checklist | Sentinel 15, non-sentinel controls |
| E2 vs B0 | Query contract checklist | Q2, Q65, Q79, Q128, Q320, Q365 |
| E3 vs E1/B0 | On-demand value inspection tool | Distinguish reminder effects from actual data grounding |
| E4 vs B0 | Selective final SQL check | Q33, Q325, Q327 and regression cases |
| E5 vs B0 | Higher reasoning effort only | Full paired Development accuracy, tokens, latency |

Primary statistic on the same N questions:

`ΔEX = (newly_correct - regressed) / N`

Report total EX plus *corrected and regressed IDs*, per-database and category splits, SQL/model/tool calls, total/cached tokens, latency, and suitable paired uncertainty. Choose improvements using Development, then treat the already-exposed Local Test as a **one-time descriptive confirmation**, not an untouched external hidden holdout. Do not tune repeatedly against it or claim it is an official hidden-test result.

### Controlled test matrix informed by new case review
| Intervention | Target cases | Guardrails |
| --- | --- | --- |
| E1 Semantic Grounding | Q345/348/363, Q347/352, Q69/90 | Keep valid zeros and NULL semantics; do not globally drop 0 |
| E2 Query Contract | Q6/7, Q67/88, Q115, Q131/172/223/236, Q406/420 | Verify metric origin, entity grain, denominator, output columns; monitor regressions |
| E3 On-demand Value Profile | Q309, Q393/418/423, Q352 | Compare with prompt-only E1 and measure additional tool calls |
| E4 Selective Final Verification | Q33/354/325/327 | Focus on high-risk final edits and dialect; verify net corrected minus regressed |
| E5 Reasoning Effort | Fixed 400 Development members | Hold provider, dataset version and budgets constant; track tokens/latency |
Primary paired measure: `ΔEX = (newly_correct - regressed) / 400`. First establish a consistently budgeted baseline because the archive mixes 20- and 40-SQL-call histories. **None of these interventions were run in this documentation update.**

<a id="limitations"></a>
## 11. Limitations and Reference QA

1. **All 165 Development failures were compared at the Question/Gold/Agent SQL level (97 previously, 68 newly), but this is not a causal census.** There are 153 provisional primary candidates and 12 unresolved cases; cases may have multiple defects. Inventory separates review basis, per-case evidence and missing counterfactual verification.
2. **No fresh SQL re-execution:** The archived EX comes from the frozen scorer; the study compares Gold and predicted queries and observable traces, without rerunning each candidate repair. Structurally different SQL can sometimes be result-equivalent on the actual SQLite data.
3. **Heuristic feature extraction:** Natural-language categories are keyword-based. Table identification and final SQL matching are textual, not complete SQL AST parsing or semantic equivalence.
4. **Reference QA candidates, *not confirmed annotation defects*:** Q235 (question specifies bank+account identity; Gold `COUNT(DISTINCT t.account)`), Q255 (question asks for all tied fastest drivers; Gold `LIMIT 1`), Q325 (question names Sep 2019–May 2020; Gold has no explicit date filter), Q497 (Gold considers only one bond endpoint, while the Agent examines both). The actual data may make alternative interpretations equivalent; do not change official scores/Gold.
5. **Small samples/confounding:** Only 8 overall Simple and 32 Moderate questions; database and query-feature strata overlap and vary in complexity. Association is not causation.
6. **Observability:** Available trace is not the model's hidden reasoning. `cost_usd=null` is missing cost data. Cached input is included in input tokens.
7. **Gold contamination control:** Case studies quote official Gold SQL for offline research only. Exclude these documents and inventory's Gold-derived metadata from agent retrieval/indexing, evaluation prompts, or production demo evidence sources.

**Follow-up review (9 Nov 2026):** The [Case Studies](case-studies.md) preserve the previous 97 cases and add 17 representative entries (114 in total); all remaining 51 also receive provisional SQL-difference reviews in the [165-case inventory](failure-inventory.csv). Reviewed does **not** mean counterfactually validated.

<a id="sources"></a>
## 12. Source Links and Reproduction

- [Archived run README](../README.md) · [Configuration](../configuration.json) · [Manifest](../dataset_manifest.json) · [Reproduction steps](../reproduce.md) · [Checksum manifest](../checksums.sha256)
- Development: [Per-question scores](../dev/scores/per_question.jsonl) · [Predictions](../dev/predictions.jsonl) · [Traces](../dev/traces.jsonl)
- Local Test: [Per-question scores](../test/scores/per_question.jsonl) · [Predictions](../test/predictions.jsonl) · [Traces](../test/traces.jsonl)
- Official pinned [Mini-Dev 2026 annotated Question/Evidence/Gold SQL](https://huggingface.co/datasets/birdsql/bird_mini_dev/blob/5b256b5a9c17478f06ed6912612e9a14d17065c8/data/mini_dev_sqlite.jsonl) · [Version and leakage guidance](../../../docs/bird-dataset-versions.md)
- [Traditional Chinese report](baseline-analysis-zh-HK.md) · [Case studies](case-studies.md) · [All 165 Development failures](failure-inventory.csv)
- Historical-only [Original Mini-Dev report](../../b0-gpt6-luna-40calls-20261108/analysis-report/baseline-analysis-en.md), **not directly comparable to this release**.

**Preservation note:** The run's `checksums.sha256` includes its own `README.md`. To preserve archival verification, this report is added under a separate `analysis-report/` folder and linked from the *Group Project* root README; the run README, checksums, scores, traces, and predictions are unchanged.
