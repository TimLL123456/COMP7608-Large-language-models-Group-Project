# B0 Baseline Performance & Failure Analysis

> **Current setting (10 November 2026):** B0 now uses 40 model calls, 40 total tool calls and 40 SQL executions for both prompt variants; the current requested evaluation runs only `generalized-v1`. The earlier Mini-Dev 2026 B0 configuration metadata also lists 40/40/40. Historical execution limits and scores below remain as originally recorded; this note does not regenerate predictions or convert the archive into a matched control.


> **Study date:** 2026-11-08　|　**Variant:** B0 / `gpt-6-luna` / `chatgpt-siwc` / requested reasoning effort `none`  
> **Evaluation:** Original BIRD Mini-Dev SQLite; fixed local 400-development / 100-test split. **Diagnosis and improvement selection focus on development data.**  
> **Status:** Read-only analysis of an archived run and proposals for future experiments; no prediction, score, agent, or model outputs were modified.

This report distinguishes **verified measurements**, **case observations grounded in traces**, **hypotheses to test**, and **limitations**. Execution Accuracy (EX) measures agreement with reference query results, not the rate of SQL statements that execute successfully.

## Contents

- [0. Executive Summary](#executive-summary)
- [1. Evaluation Setup](#evaluation-setup)
- [2. Overall Performance](#overall-performance)
- [3. Database Performance](#database-performance)
- [4. SQL & Agent Trace Analysis](#trace-analysis)
- [5. Failure Root Cause Taxonomy](#root-causes)
- [6. Representative Case Studies](#case-studies)
- [7. Improvement Recommendations](#recommendations)
- [8. Controlled Experiment Plan](#experiment-plan)
- [9. Limitations & Reproducibility](#limitations)

<a id="executive-summary"></a>
## 0. Executive Summary

| Metric | Verified value | Interpretation |
| --- | ---: | --- |
| All-question EX | **299/500 = 59.8%** | Dev 59.0%; local Test 63.0% |
| Development failures | **164/400** | Moderate 93; Challenging 41; Simple 30 |
| Moderate + Challenging share of Dev failures | **134/164 = 81.7%** | Prioritize these difficulty groups for deep investigation |
| Final SQL execution success | **500/500** | All 201 EX failures were result mismatches |
| Dev failures with exactly one SQL call | **113/164 = 68.9%** | Motivates semantic review, **not** forced retries |
| Dev final SQL text differs from all previously executed SQL, after normalization | **201/400**, including **99/164 failures** | Textual difference is **not** semantic difference or proven cause |
| Existing retrospective Dev projection diagnostic | **17 matching cases** | Opportunity hypothesis using reference outputs, **not** a realized +4.25 percentage-point gain |

**Primary conclusion:** Prioritize **question/column semantics, aggregation and Top-K logic, output specification, and final SQL verification**, rather than increasing call ceilings. The smallest first intervention is an opt-in **output/semantic checklist**. Evaluate **final SQL verification** separately; independently ablate stronger reasoning effort, query planning, and schema/value grounding. Do not assume knowledge graphs or model routing will help without measured evidence.

**Investigation allocation:** Use the 400 development questions. Briefly inspect systematic Simple failures and regressions; review Moderate and Challenging cases in depth. Select database slices by both **failure rate and absolute number of failures**.

<a id="evaluation-setup"></a>
## 1. Evaluation Setup

| Setting | Archived run |
| --- | --- |
| Provider / Model | `chatgpt-siwc` / `gpt-6-luna` |
| Requested reasoning effort | `none`; observable response metadata retained in predictions/traces |
| Dataset | Original BIRD Mini-Dev SQLite, 500 questions across 11 databases (not Mini-Dev V2) |
| Local split | 400 Dev / 100 Test, seed 42; every question inferred afresh |
| Per-question ceilings | 40 model calls, 40 total tool calls, 20 SQL executions; recursion limit 200 |
| Model request timeout | 300 seconds per model request |
| Scoring timeout | 600 seconds per reference/predicted SQL statement |
| Agent SQL tool timeout | The archived run used 5 seconds; current code/documentation describes a longer default. Match or disclose this in future comparisons |
| Run timestamps | 2026-11-08 03:59:35–06:32:14 UTC (approximately 2 h 33 min) |

**EX definition:** The evaluator compares **sets of complete result tuples** from predicted and reference SQL. Row order and duplicate rows do not determine EX, while the number/position of columns and their values do. An executable SQL query is not necessarily semantically correct. Gold SQL and reference results remain evaluator-only and must not be fed to the evaluated agent.

Raw scorer files label the data `is_full_split: false` / selected subset because explicit question IDs were passed. Membership checking confirms all 400 local Dev and 100 local Test IDs were covered; the export summary sets `covers_full_local_split: true`. **These are not official BIRD hidden-test scores.** The Dev 59% vs Test 63% difference represents different question populations, not a before/after improvement.

<a id="overall-performance"></a>
## 2. Overall Performance

### 2.1 Split results

| Split | Correct | Total | EX | Failed |
| --- | ---: | ---: | ---: | ---: |
| Development | 236 | 400 | **59.0%** | 164 |
| Local Test | 63 | 100 | **63.0%** | 37 |
| **Overall** | **299** | **500** | **59.8%** | **201** |

Inference and scoring completed for every question; no final prediction was missing and all final queries executed successfully. All 201 failed EX judgments were `incorrect_result`, suggesting that **semantic correctness rather than SQL executability** is the principal bottleneck.

### 2.2 Development accuracy by difficulty

| Difficulty | Correct / Total | EX | Failures | Share of Dev failures |
| --- | ---: | ---: | ---: | ---: |
| Simple | 87/117 | **74.4%** | 30 | 18.3% |
| Moderate | 107/200 | **53.5%** | 93 | 56.7% |
| Challenging | 42/83 | **50.6%** | 41 | 25.0% |
| **Total** | **236/400** | **59.0%** | **164** | **100%** |

Moderate and Challenging contribute 134 of 164 development failures (**81.7%**). Put most trace-review effort into those groups, but still inspect the 30 Simple failures for systematic errors and regression risks.

<a id="database-performance"></a>
## 3. Database Performance

### 3.1 Full Development Database × Difficulty matrix

Cells are “correct/total (EX)”. Rows are ordered by **absolute number of failures**, which complements the ranking by low EX.

| Database | Failed | Overall Dev EX | Simple | Moderate | Challenging |
| --- | ---: | ---: | --- | --- | --- |
| `formula_1` | **24** | 29/53 (54.7%) | 14/22 (63.6%) | 11/21 (52.4%) | 4/10 (40.0%) |
| `thrombosis_prediction` | **21** | 20/41 (48.8%) | 4/6 (66.7%) | 10/22 (45.5%) | 6/13 (46.2%) |
| `card_games` | **18** | 23/41 (56.1%) | 7/10 (70.0%) | 12/26 (46.2%) | 4/5 (80.0%) |
| `financial` | **16** | 9/25 (36.0%) | 1/2 (50.0%) | 6/17 (35.3%) | 2/6 (33.3%) |
| `codebase_community` | **15** | 24/39 (61.5%) | 15/17 (88.2%) | 8/18 (44.4%) | 1/4 (25.0%) |
| `european_football_2` | **15** | 26/41 (63.4%) | 7/11 (63.6%) | 14/20 (70.0%) | 5/10 (50.0%) |
| `california_schools` | **14** | 10/24 (41.7%) | 2/6 (33.3%) | 7/14 (50.0%) | 1/4 (25.0%) |
| `toxicology` | **13** | 19/32 (59.4%) | 3/4 (75.0%) | 8/14 (57.1%) | 8/14 (57.1%) |
| `student_club` | **10** | 28/38 (73.7%) | 15/17 (88.2%) | 10/17 (58.8%) | 3/4 (75.0%) |
| `debit_card_specializing` | **9** | 15/24 (62.5%) | 9/11 (81.8%) | 6/10 (60.0%) | 0/3 (0.0%) |
| `superhero` | **9** | 33/42 (78.6%) | 10/11 (90.9%) | 15/21 (71.4%) | 8/10 (80.0%) |

**Two prioritization axes:** (a) Lowest EX: `financial` and `california_schools`. (b) Most failures to potentially recover: `formula_1`, `thrombosis_prediction`, and `card_games`. Looking only at failure rate overlooks how many questions each database contributes.

### 3.2 Difficulty-mix-adjusted descriptive comparison

For each database, multiply its count of Simple, Moderate, and Challenging questions by the overall Dev EX of each difficulty (87/117, 107/200, 42/83), respectively. This yields a difficulty-mix-based expected EX—not a controlled causal estimate or significance test.

| Database | Observed Dev EX | Expected from difficulty mix (approx.) | Gap |
| --- | ---: | ---: | ---: |
| `financial` | 36% | 54% | **−18 pp** |
| `california_schools` | 42% | 58% | **−17 pp** |
| `formula_1` | 55% | 62% | −7 pp |
| `thrombosis_prediction` | 49% | 56% | −7 pp |
| `student_club` | 74% | 63% | +11 pp |
| `superhero` | 79% | 58% | +20 pp |

The weak `financial` and `california_schools` results cannot be explained solely by their difficulty mix. However, schema size, question composition, value distributions, and sampling variation remain confounders. Some cells include only 2–6 questions; always preserve the denominator. “Database type” here means **domain and schema/query characteristics**, not SQL engine; all 11 databases are SQLite.

### 3.3 Follow-up database questions

Characterize table/column counts, foreign-key completeness, join depth, ambiguous names, unusual value/date encodings, aggregation operators, and requested output grain. Cross these features with database and difficulty before deciding whether a knowledge graph or richer metadata is likely to address the observed weaknesses.

<a id="trace-analysis"></a>
## 4. SQL & Agent Trace Analysis

### 4.1 Development final SQL feature slices

Features are detected by simple textual patterns in the **predicted final SQL**, not necessarily required by the question. Categories overlap, so rates must not be summed.

| SQL feature | Correct / predicted queries with feature | EX | Failed |
| --- | ---: | ---: | ---: |
| JOIN | 170/296 | 57.4% | 126 |
| Subquery (`(SELECT`) | 37/90 | 41.1% | 53 |
| DISTINCT (any use) | 62/107 | 57.9% | 45 |
| ORDER BY | 44/80 | 55.0% | 36 |
| GROUP BY | 23/57 | 40.4% | 34 |
| CASE | 28/58 | 48.3% | 30 |
| LIMIT | 27/55 | 49.1% | 28 |
| COUNT(DISTINCT …) | 16/43 | 37.2% | 27 |
| CTE (starts with WITH) | 3/16 | 18.8% | 13 |

**Observation:** Predicted queries using subqueries, grouping, distinct counting, and CTEs have lower observed EX; they are good **candidates for manual review**. Difficulty and SQL structure are confounded, so this does not show that a syntax feature *causes* failures. Validate the necessary operations against the question, reference SQL, and trace.

### 4.2 Observed agent behavior across 400 Dev traces

| Measured signal | Result | Interpretation |
| --- | ---: | --- |
| Failed questions with exactly one SQL call | 113/164 (68.9%) | Investigate whether first-run semantic validation was missing |
| Failed questions with two or more SQL calls | 51/164 | Extra calls are not proof of correctness |
| Final SQL text differs from every executed SQL text after normalization | 201/400 (50.3%) | Can reflect harmless aliases or equivalent rewrites |
| Such textual differences among failed questions | 99/164 (60.4%) | Verification hypothesis, **not** 99 proven causes |
| At least one SQL execution returned zero rows | 24/400; 13 failed | An empty result need not be wrong |
| At least one truncated SQL tool preview (trace-level per question) | 51/400; 23 failed | Not equivalent to a scorer truncation |
| No `inspect_table` call | 0/400 | Every question inspected at least one table |

Text comparison extracts `execute_sql` argument strings and `report.final_sql`, removes whitespace/comments, lowercases, and strips terminal semicolons. **It is neither AST-based nor a semantic equivalence check.** A mismatch means “no previously executed SQL has the same normalized text,” not necessarily that a meaningful query change was never tested. Tool output usually previews at most 20 rows.

### 4.3 Efficiency: secondary, not the current optimization target

Metrics below cover all 500 questions; P95 uses the nearest-rank convention.

| Metric | Mean | Median | P95 | Maximum |
| --- | ---: | ---: | ---: | ---: |
| Model calls | 4.78 | 4.00 | 7.00 | 18 |
| Tool calls | 4.90 | 5.00 | 8.00 | 19 |
| SQL calls | 1.47 | 1.00 | 3.00 | 14 |
| Total tokens | 15,298.74 | 13,573.50 | 26,514 | 81,685 |
| Latency (ms) | 17,093.78 | 15,022 | 29,722 | 80,105 |

There were 736 SQL tool calls and 6 SQL tool errors affecting 5 questions. Sixty-six questions had at least one truncated SQL preview; tool previews do not cap formal scoring. The maximum observed 18 model calls is below the ceiling of 40, so **budget exhaustion is not a demonstrated bottleneck**. Failed cases averaged 5.04 model calls, 16,889 tokens and 18.35 seconds; successful cases averaged 4.60 calls, 14,229 tokens and 16.25 seconds. This association does not imply that extra calls cause failures. Monetary cost is unknown, not zero.

<a id="root-causes"></a>
## 5. Failure Root Cause Taxonomy

Use the following taxonomy to annotate **all 164 Dev failures** in future work; only some cases have sufficient reviewed evidence today. **This is not an exhaustive, mutually exclusive count of causes across all 164 cases.** Multiple causes can be recorded, with an `uncertain` or `reference-review` status where appropriate.

| Category | Diagnostic question | Reviewed example / status |
| --- | --- | --- |
| Schema / Column Mapping | Wrong entity, column, join key? | Q89, Q861: observed differences |
| Value / Evidence Interpretation | Incorrect value code or evidence mapping? | Q231: label encoding not verified |
| Join / Row Duplication | Join path or many-to-many multiplication? | Q197: reference SQL also disputed |
| Aggregation / Granularity | GROUP BY, distinct count, denominator? | Q17, Q1322 |
| Ranking / Top-K | LIMIT, ordering, rank column, ties? | Q846, Q726, Q728 |
| Date / Filter Logic | Timestamp/date boundaries, ABS, predicates? | Q533, Q82, Q1338 |
| Output Specification | Wrong column count/order, full name representation? | Q1486, Q1381; 17 projection matches |
| Final SQL Verification | Is the final query meaningfully different from the verified result? | Q82, Q1322: concrete trace examples |
| Reference / Annotation Ambiguity | Question, evidence, and gold disagree? | Q345, Q197, Q1322: manual adjudication needed |

### 5.1 Preserved retrospective projection audit

The previous report documents a read-only diagnostic that re-executed predicted and reference SQL for 164 Dev failures under a **separate 1-second-per-query** limit and **100,000-row cap**. It completed 160 cases; Q192, Q530, Q595 and Q1014 timed out. Of the 160 completed, 44 produced different column counts; 17 matched the reference result after selecting/reordering existing predicted result columns:

`Q32, Q87, Q125, Q231, Q345, Q402, Q634, Q798, Q829, Q981, Q989, Q1078, Q1145, Q1192, Q1338, Q1486, Q1533`.

These comprise Simple **3**, Moderate **8**, and Challenging **6** cases. The 17/400 cases equate to a retrospective **4.25-percentage-point opportunity indicator**, **not** a deployable selection rule or demonstrated EX improvement. Matching on one database instance does not prove general SQL equivalence; the 44 column-count mismatches include both missing and extra columns. No original EX score was changed.

<a id="case-studies"></a>
## 6. Representative Case Studies

The cases below use [Dev traces](../dev/traces.jsonl.gz), [Dev per-question scores](../dev/scores/per_question.jsonl), and the preserved reference-output audit. Distinguish the **trace observation** from the **candidate diagnosis**; some reference answers still require review.

### 6.1 Simple — Q82: absolute-longitude predicate error

- **Question/evidence:** Find `GSoffered` for the school with the largest **absolute** longitude.
- **Trace:** The first `Longitude = MAX(ABS(Longitude))` query returned no rows. A later `ORDER BY ABS(Longitude) DESC` inspection found the candidate school and `GSoffered = 'K-8'`. The final SQL still compared the **raw negative Longitude** directly to the positive `MAX(ABS(Longitude))`.
- **Observation:** The agent obtained a useful result during investigation but retained the wrong comparison in its final query.
- **Hypothesis to test:** Explicit predicate semantics and rerunning the final SQL would catch this case.

### 6.2 Simple — Q17 / Q861: rank and entity ownership

- **Q17 (California Schools):** Grouped by Charter Number and averaged writing scores; omitted the explicit rank expected by the reference. The intended row grain and rank representation need to be checked.
- **Q861 (Formula 1):** Selected `qualifying.number` whereas the reference uses `drivers.number`. Similar names refer to different entities.
- **Potential remedy:** Output-grain/rank requirements and grounded column ownership.

### 6.3 Moderate — Q89: Financial field semantics

Question: How many East Bohemia accounts selected issuance after transaction? Evidence references `'POPLATEK PO OBRATU'`. The agent repeatedly queried `order.k_symbol` and `trans`-related fields, finally filtering on `order.k_symbol` and obtaining zero. The preserved reference comparison maps the target to `account.frequency`. The trace also shows a nonexistent-column error and an attempt to execute multiple statements.

**Likely weakness:** Similar business concepts in different tables are hard to disambiguate from DDL alone; extra SQL attempts did not repair the field mapping. **Experiment:** Field definitions, candidate values, and evidence-based schema grounding.

### 6.4 Moderate — Q846: Formula 1 Top-K semantics

Evidence specifies **five drivers** eliminated in the first qualifying period. The agent used `q1 = (SELECT MAX(q1) …)` and its tool result contained only one driver.

**Potential remedy:** A planner should record `expected cardinality = 5`, ordering, LIMIT, and tie handling, then verify the observed result count.

### 6.5 Moderate — Q1322: tested count versus final grouping

Question: Of the events attended by more than ten club members, how many are meetings? The trace includes a tested nested-query version that first selects qualifying events then returns a single `COUNT(*) = 4`. The final SQL instead used `GROUP BY e.event_id HAVING COUNT(...) > 10` without a subsequent execution; this can return one row per qualifying event rather than a scalar total.

**Potential remedy:** Rerun final SQL and check output grain. **Important caveat:** The existing report also questions the Gold SQL for this item; do not treat the reference interpretation as fully adjudicated.

### 6.6 Moderate — Q1338 / Q1486: dates and extra output fields

- **Q1338 (Student Club):** Initial `event_date = '2019-10-08'` returned nothing. Data inspection showed a timestamp, so the agent changed to `LIKE '2019-10-08%'`. The final query fixed the date predicate but included an extra `expense_description` column relative to the reference output.
- **Q1486 (Debit Card):** The trace correctly calculated a CZK-vs-EUR SME count difference of **23505**. The final query additionally returned a Yes/No field. The Yes/No answer is arguably natural given the wording, but differs from the reference result structure. This is an **output-contract/reference-alignment question**, not necessarily a mathematical error.

### 6.7 Challenging — Q28 / Q36 / Q231 / Q1192

- **Q28 (California Schools):** Requires calculating an average enrollment difference first, then filtering schools above it. This is a suitable multi-stage aggregation/planning review; available evidence does not isolate one definitive root cause.
- **Q36 (California Schools):** Evidence says a school can have up to three administrators. The trace retrieved multiple administrator-name fields, but final SQL returned only the first; inspect answer completeness.
- **Q231 (Toxicology):** The trace observed `molecule.label = '-'`; final SQL compared `label` with `'carcinogenic'` without verifying the encoding. Value grounding is a plausible issue.
- **Q1192 (Thrombosis):** Selected `Patient.*`. The retrospective projection audit found a subset of its result columns matching the reference. Output-grain checks may help, subject to question semantics.

### 6.8 Other preserved findings and reference concerns

- **Q533:** Prior gold comparison indicates extracting the date before comparison; direct timestamp comparison risks incorrect boundary semantics.
- **Q726 / Q728:** Sorted output omits an explicit rank column expected by the reference.
- **Q1381:** Concatenated full name into one field; reference returned separate `first_name` and `last_name` fields.
- **Q345:** Question/evidence/reference differ in `type` versus `types` interpretation.
- **Q197:** The reference atom/bond join may multiply atom counts; not confirmed as an annotation error.
- **Q1322:** The reference grouping/counting design itself warrants review.

**Policy:** Retain original Gold SQL, predictions, and official local EX. Flag disputed cases `reference-review` for adjudication rather than treating them as confirmed annotation errors.

<a id="recommendations"></a>
## 7. Improvement Recommendations

| Priority | Proposed intervention | Evidence motivating the hypothesis | Controlled check |
| --- | --- | --- | --- |
| **P0** | **Output / Semantic Checklist** | 17 projection-match cases; rank, grain, extra/missing output fields | Opt-in prompt-only paired comparison; corrections and regressions |
| **P0** | **Final SQL Verification** (separate variant) | Q82 and Q1322; 99 failed cases with normalized final-SQL textual differences | Selective final query execution and semantic/result-shape checks; do not assume every string difference is an error |
| **P1** | Schema / Value Grounding | Q89, Q861, Q231 field/value interpretation | Establish repeated failure mechanism before adding metadata or value tools |
| **P1** | Explicit Query Planner | Q846, Q28; lower EX among grouping/Top-K/subquery patterns | Compare planner vs non-planner under matched model/budget |
| **P1** | Reasoning Effort Ablation | Archived B0 requested `none` | Keep the original prompt, test a **supported and verifiable** higher effort |
| **P2** | Knowledge Graph / Adaptive Routing | No established primary bottleneck yet | Defer until schema/join or model-choice failure prevalence is demonstrated |

Do **not** blindly raise model/tool ceilings, remove columns from all outputs, add ranks universally, or force all questions to retry SQL. Make all checks respect the question-specific output contract and SQL safety boundaries.

<a id="experiment-plan"></a>
## 8. Controlled Experiment Plan (Accuracy First)

### 8.1 First round: separate checklist and reasoning effort

| Variant | Prompt / controller | Reasoning effort | Goal |
| --- | --- | --- | --- |
| **B0** | Original | `none` | Archived control |
| **E1** | Output / Semantic Checklist | `none` | Isolate checklist effect |
| **E2** | Original | Higher supported level (e.g. `medium`) | Isolate effort effect |
| **E3** | Same as E1 | Same as E2 | Test combined effect |

Do not silently mix planning, grounding, and final verification into E1: that would confound attribution. A second round can evaluate opt-in final SQL verification, planner, and grounding variants according to the results and further manual case classification.

### 8.2 Evaluation contract and success criteria

1. Use **identical Dev question IDs** for paired runs and comparable dataset, evidence policy, model/provider, scoring code, SQL safety restrictions, call limits, and timeouts. Disclose every deviation, give each new run its own ID, and preserve the archived B0.
2. Compare `EX`, `corrected_count` (B0 wrong → variant right), `regressed_count` (B0 right → variant wrong), their difference, difficulty/database slices, and paired uncertainty. Report qualitative corrected and regressed cases.
3. Treat tokens, tool calls, and latency as **secondary** outcomes for now. Retain complete observable usage metadata. Record both requested and response-reported reasoning settings; do not attribute effects to an unverified effort level.
4. Smoke-test a small **development** subset, then freeze the variant and evaluate on full development. Consider a fresh B0 repeat to estimate hosted-model variability if feasible.
5. Evaluate on the local test only after variant selection. The existing local-test baseline has already been viewed, so **do not tune on its individual failures**, and disclose this exposure.
6. Do not promise a particular target EX or +4.25 pp. Include regressions, uncertainty, and additional compute in the decision.

<a id="limitations"></a>
## 9. Limitations & Reproducibility

### 9.1 Evidence quality and limitations

- **Verified metrics:** archived 500/400 score rows, model/tool-call counts, database/difficulty summaries, and observable trace events.
- **Exploratory trace signals:** normalized-text final SQL matching, SQL regex patterns, empty SQL results, and tool-preview truncation. These are not SQL semantic equivalence or causal attribution.
- **Retrospective gold-based diagnostic:** the prior 160/164 completed projection audit used a 1-second-per-query limit and local reference results. No standalone reproducible script was saved. Its timeout differs from the 600-second formal scorer, so its coverage must be disclosed.
- **Incomplete root-cause labeling:** selected cases do not quantify causes across all 164 Dev failures; candidate diagnoses are not a fully annotated taxonomy.
- **Small cells and confounding:** some database/difficulty cells have only a few questions; SQL features overlap and correlate with question difficulty.
- **Usage coverage:** cached input tokens are included in input tokens; reasoning tokens in output tokens. Usage may be incomplete for unobserved or nested calls. Hidden reasoning text is unavailable; cost is unknown.
- **Run variability:** a hosted model slug is not an immutable weights snapshot; results may vary with model changes, sampling, environment, or caching. Pin run/configuration/provenance.
- **Score integrity:** reference disputes do not authorize changing Gold, predictions, archived scores, or official local EX.

### 9.2 Archived data and reproduction entry points

| Evidence | Source |
| --- | --- |
| Run overview | [README](../README.md), [Combined summary](../summary.json), [Configuration](../configuration.json) |
| Provenance | [Dataset manifest](../dataset_manifest.json), [Provenance](../provenance.json), [Environment](../environment.json) |
| Development | [Per-question scores](../dev/scores/per_question.jsonl), [Predictions](../dev/predictions.jsonl), [Compressed traces](../dev/traces.jsonl.gz) |
| Local test | [Per-question scores](../test/scores/per_question.jsonl), [Predictions](../test/predictions.jsonl) |
| Procedure and integrity | [Reproduction guide](../reproduce.md), [Checksums](../checksums.sha256) |

**Recalculation:** Join by `question_id` and preserve `split`. Group per-question `ex` by `split`, `difficulty`, and `db_id`; EX is correct count divided by question count. SQL-feature summaries use predicted-SQL text patterns and permit overlapping categories. Trace comparisons rely on observable `execute_sql` inputs and `report.final_sql`. P95 uses nearest-rank index `ceil(0.95 × n) - 1` in zero-based indexing.

**Scope of this document update:** Integrated prior and newly observed evidence into the bilingual report. **No new model inference, rescoring, independent gold-based audit, or agent-code changes** were performed.
