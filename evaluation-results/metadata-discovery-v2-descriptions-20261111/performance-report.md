# Metadata Discovery V2 with restored BIRD descriptions — performance report

Execution status: COMPLETE. Dev precedes Test; Test shares the writable knowledge accumulated in Dev. Scores are execution accuracy (EX), comparing result sets using the existing evaluator.


The complete run scores **340/500 EX (68.00%)**: **272/400 Dev** and **68/100 Test**. Of 160 failures, 154 are result mismatches, four are final SQL compilation errors, and two have no SQL after provider overload. Compared with historical generalized-v1 B0, the net difference is +21 correct answers (+4.20 percentage points), with 89 gains and 68 regressions. This required 9.11 times the observed input tokens and 5.86 times the recorded inference time. Description restoration, larger budgets and workflow fixes are confounded; their separate effects are not established.

## Execution and preservation

Project: {project root}. Git HEAD and origin/main were verified at 465bde31b67c6fb01d9ffbba7fec665a23d63a01. The working tree was clean before execution. Existing passing dependency/offline-test logs were reviewed rather than repeating cleanup or the complete suite. No agent code, evaluator logic, databases, gold SQL, annotations or pre-existing dataset manifests were modified. Existing provider authentication was used without manual credential changes; provider-managed token refresh was not independently audited. No commit or push was made.

Experiment metadata-discovery-v2-descriptions-20261111 uses the prepared metadata-discovery-v2-resource-full-20261111 selection, fresh metadata-discovery-v2-descriptions-dev-20261111 and metadata-discovery-v2-descriptions-test-20261111 runs, workflow metadata-discovery-v2, chatgpt-siwc / gpt-6-luna / reasoning none / generalized-v1. Global model/tool/SQL caps: 120/200/80; A1 per-attempt model/tool caps: 20/40, SQL cap 20; at most 3 attempts; metadata context 20,000 characters; preview 20 rows. Prior interrupted experiments and logs were preserved. Inference receives public question/evidence fields, schema/descriptions and read-only database tools; gold references are used only in the offline scorer and post-run analysis.

## Description restoration

Official source: https://github.com/bird-bench/mini_dev, its linked complete package https://drive.google.com/file/d/13VLWIwpw5E3d5DUkMvzw7hvHE67a4XkG/view. Archive SHA-256: aeb211c0e39010bbdae3838bb5e8bd27dc446ed77495b1709f85ccc9bf67f2be. The archive was downloaded fresh; only description CSVs were installed. Every installed table/column is checked against SQLite and BirdDataset.get_descriptions(). All 16 pre-existing dataset files retain their recorded SHA-256 hashes, including all 11 databases; the existing dataset verifier passes.

The official legacy package has two version mismatches: constructors.csv lists a nonexistent formula_1.constructors.wins column, so that row was excluded; toxicology.element is absent, so an element.csv containing its two column names and SQLite types was generated from the pinned official 2026 baseline schema, corroborated against SQLite. The official schema supplies no semantic descriptions for those columns, and none were invented. Raw package bytes, the pinned schema and the exact adaptation audit are retained. This is 75 official CSVs (74 unchanged, one filtered) plus one schema-only supplement, covering all 76 tables.

## Overall accuracy

| Split | Predictions | Scored | EX | Missing SQL |
| --- | --- | --- | --- | --- |
| dev | 400 | 400 | 272/400 (68.00%) | 2/400 (0.50%) |
| test | 100 | 100 | 68/100 (68.00%) | 0/100 (0.00%) |
| overall | 500 | 500 | 340/500 (68.00%) | 2/500 (0.40%) |

## Accuracy by difficulty and database

| Split | Group | EX |
| --- | --- | --- |
| dev | difficulty:challenging | 251/369 (68.02%) |
| dev | difficulty:moderate | 16/24 (66.67%) |
| dev | difficulty:simple | 5/7 (71.43%) |
| dev | db_id:california_schools | 21/40 (52.50%) |
| dev | db_id:card_games | 38/55 (69.09%) |
| dev | db_id:codebase_community | 14/25 (56.00%) |
| dev | db_id:debit_card_specializing | 5/11 (45.45%) |
| dev | db_id:european_football_2 | 18/25 (72.00%) |
| dev | db_id:financial | 24/37 (64.86%) |
| dev | db_id:formula_1 | 38/44 (86.36%) |
| dev | db_id:student_club | 22/30 (73.33%) |
| dev | db_id:superhero | 29/40 (72.50%) |
| dev | db_id:thrombosis_prediction | 46/68 (67.65%) |
| dev | db_id:toxicology | 17/25 (68.00%) |
| test | difficulty:challenging | 62/91 (68.13%) |
| test | difficulty:moderate | 5/8 (62.50%) |
| test | difficulty:simple | 1/1 (100.00%) |
| test | db_id:california_schools | 5/9 (55.56%) |
| test | db_id:card_games | 10/14 (71.43%) |
| test | db_id:codebase_community | 4/6 (66.67%) |
| test | db_id:debit_card_specializing | 3/3 (100.00%) |
| test | db_id:european_football_2 | 4/6 (66.67%) |
| test | db_id:financial | 5/9 (55.56%) |
| test | db_id:formula_1 | 7/11 (63.64%) |
| test | db_id:student_club | 4/7 (57.14%) |
| test | db_id:superhero | 6/10 (60.00%) |
| test | db_id:thrombosis_prediction | 14/18 (77.78%) |
| test | db_id:toxicology | 6/7 (85.71%) |
| overall | difficulty:challenging | 313/460 (68.04%) |
| overall | difficulty:moderate | 21/32 (65.62%) |
| overall | difficulty:simple | 6/8 (75.00%) |
| overall | db_id:california_schools | 26/49 (53.06%) |
| overall | db_id:card_games | 48/69 (69.57%) |
| overall | db_id:codebase_community | 18/31 (58.06%) |
| overall | db_id:debit_card_specializing | 8/14 (57.14%) |
| overall | db_id:european_football_2 | 22/31 (70.97%) |
| overall | db_id:financial | 29/46 (63.04%) |
| overall | db_id:formula_1 | 45/55 (81.82%) |
| overall | db_id:student_club | 26/37 (70.27%) |
| overall | db_id:superhero | 35/50 (70.00%) |
| overall | db_id:thrombosis_prediction | 60/86 (69.77%) |
| overall | db_id:toxicology | 23/32 (71.88%) |

Difficulty labels come directly from the pinned 2026 annotations: 8 simple, 32 moderate and 460 challenging across the complete dataset. Small strata are unstable; labels and IDs differ from Original Mini-Dev.

## Failures and execution errors

| Split | Status | Count | Rate |
| --- | --- | --- | --- |
| dev | correct | 272 | 68.00% |
| dev | incorrect_result | 123 | 30.75% |
| dev | missing_sql | 2 | 0.50% |
| dev | sql_error | 3 | 0.75% |
| test | correct | 68 | 68.00% |
| test | incorrect_result | 31 | 31.00% |
| test | sql_error | 1 | 1.00% |
| overall | correct | 340 | 68.00% |
| overall | incorrect_result | 154 | 30.80% |
| overall | missing_sql | 2 | 0.40% |
| overall | sql_error | 4 | 0.80% |

Final prediction execution errors/timeouts are evaluator outcomes; exploratory SQL errors may occur on ultimately correct questions. They are reported separately. The failure inventory covers every failed question. Result mismatches can reflect joins, filters, grouping, projection, arithmetic, NULL handling or ordering; EX alone does not establish which. The local evaluator-only inventory adds predicted/gold SQL and structural differences for review. Such differences are hypotheses, since equivalent SQL can use different structures.

Trace-grounded failure categories: {'result_mismatch': 154, 'missing_SQL:RuntimeError': 2, 'execution:sql_error': 4}. Exploratory SQL error calls: 77. Questions with exploratory SQL errors: 57.

## A1 discovery, B1 sufficiency and C1 fallback

| A1 attempts | Questions | Final SQL | EX |
| --- | --- | --- | --- |
| 1 | 183 | 183 | 136/183 (74.32%) |
| 2 | 77 | 76 | 56/77 (72.73%) |
| 3 | 240 | 239 | 148/240 (61.67%) |

A1 knowledge decisions: {'created': 266, 'updated': 722, 'reused': 50, 'decision_missing': 13, 'decision_inconsistent': 1, 'no_note': 5}. B1 sufficiency decisions: {'False': 780, 'True': 276}. Exact missing facts and B1 reasons are retained in b1-missing-information.json. Discovery quality is assessed through decision validity, recovered schema evidence, durable note operations, unresolved facts and downstream outcomes; structural note validity is not a semantic correctness audit.

| C1 route | Questions | Final SQL | EX |
| --- | --- | --- | --- |
| Fallback after insufficient/failed B1 | 224 | 223 | 137/224 (61.16%) |
| Sufficient B1 / other | 276 | 275 | 203/276 (73.55%) |

Fallback success means scored EX, not merely producing SQL. Repeated attempts and fallback groups are selected by difficulty encountered during inference; their outcomes do not measure the causal effect of retries.

## Knowledge creation, reuse and integrity

Operation counts: {'search:ok': 4714, 'create:error': 960, 'create:ok': 572, 'read:ok': 6245, 'update:ok': 1246, 'decision:ok': 1057, 'update:error': 108, 'read:error': 76, 'search:error': 4}. Decisions and operation counts differ: bootstrap reads, failed operations and repeated actions can occur in one attempt.

Final notes: 572. Types: {'column': 498, 'table': 74}. First created in Dev/Test: {'dev': 543, 'test': 29}. Notes read by other questions: 457. Distinct cross-question note/reader pairs: 3220. Reuse means an observed successful read; it does not prove an accuracy contribution.

Index audit: [{'database': 'california_schools', 'indexed': 69, 'files': 69, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'card_games', 'indexed': 83, 'files': 83, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'codebase_community', 'indexed': 58, 'files': 58, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'debit_card_specializing', 'indexed': 21, 'files': 21, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'european_football_2', 'indexed': 59, 'files': 59, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'financial', 'indexed': 52, 'files': 52, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'formula_1', 'indexed': 80, 'files': 80, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'student_club', 'indexed': 43, 'files': 43, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'superhero', 'indexed': 39, 'files': 39, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'thrombosis_prediction', 'indexed': 53, 'files': 53, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}, {'database': 'toxicology', 'indexed': 15, 'files': 15, 'orphaned': [], 'missing_files': [], 'hash_mismatches': [], 'write_marker': False}]. Indexed hashes are checked against content, on-disk notes against index IDs, and leftover writer markers are reported. Required heading checks pass for 572/572 notes; source references present for 572/572. Notes explicitly marking uncertainty: 454. These are format/provenance checks, not proof of business truth.

Metadata errors: {'1-6 provenance references required (schema:/description:/values:)': 64, 'Note already exists; read and update instead': 890, 'Summary must be 1-160 characters': 79, 'Unknown note in active database': 69, 'Metadata note exceeds 1500 characters': 12, 'Unknown note; create it first': 8, 'Table not present in active database schema': 4, 'Per-question metadata context budget exceeded': 7, 'Column definition must use exact schema column name': 9, 'Stale note revision; reread before updating': 2, 'Definition must contain four nonempty framework sections, in order': 2, 'Question answers, gold SQL and reference SQL are not metadata': 2}. Node errors: {'ModelCallLimitExceededError: Model call limits exceeded: run limit (20/20)': 50, 'RuntimeError: SIWC stream failed: error (server_is_overloaded)': 3, 'ToolCallLimitExceededError: Tool call limit reached: run limit exceeded (41/40 calls).': 15, 'ToolCallLimitExceededError: Tool call limit reached: run limit exceeded (43/40 calls).': 2, 'ToolCallLimitExceededError: Tool call limit reached: run limit exceeded (42/40 calls).': 2, 'RuntimeError: SIWC stream failed: error (server_error)': 1, 'ToolCallLimitExceededError: Tool call limit reached: run limit exceeded (45/40 calls).': 1, 'B1: RuntimeError: SIWC stream failed: error (invalid_prompt)': 1}. See metrics.json for tool names and node counts. Metadata-budget rejections and model/tool limit exceptions are individual failures unless they establish a critical systemic issue.

## Resources, latency and cost

| Split | Measure | N | Total | Mean | Median | p95 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | model_calls | 400 | 11425 | 28.562 | 27.5 | 52.0 | 68 |
| dev | tool_calls | 400 | 17502 | 43.755 | 39.0 | 89.0 | 130 |
| dev | sql_calls | 400 | 3434 | 8.585 | 7.0 | 21.0 | 38 |
| dev | input_tokens | 400 | 91632815 | 229082.038 | 194936.0 | 540406.95 | 1044027 |
| dev | output_tokens | 400 | 1588384 | 3970.96 | 3716.0 | 7618.45 | 11107 |
| dev | cached_input_tokens | 400 | 29919872 | 74799.68 | 64896.0 | 173721.6 | 358272 |
| dev | reasoning_tokens | 400 | 0 | 0 | 0.0 | 0.0 | 0 |
| dev | seconds | 400 | 58052.721 | 145.132 | 134.276 | 290.464 | 505.515 |
| test | model_calls | 100 | 2997 | 29.97 | 29.0 | 51.05 | 65 |
| test | tool_calls | 100 | 4654 | 46.54 | 42.0 | 99.05 | 132 |
| test | sql_calls | 100 | 848 | 8.48 | 8.0 | 18.05 | 21 |
| test | input_tokens | 100 | 24955453 | 249554.53 | 222502.0 | 558757.1 | 931358 |
| test | output_tokens | 100 | 408937 | 4089.37 | 4198.5 | 7489.15 | 8642 |
| test | cached_input_tokens | 100 | 7952256 | 79522.56 | 70848.0 | 164249.6 | 310784 |
| test | reasoning_tokens | 100 | 0 | 0 | 0.0 | 0.0 | 0 |
| test | seconds | 100 | 15812.105 | 158.121 | 151.883 | 275.194 | 770.951 |
| overall | model_calls | 500 | 14422 | 28.844 | 28.0 | 52.0 | 68 |
| overall | tool_calls | 500 | 22156 | 44.312 | 40.0 | 89.05 | 132 |
| overall | sql_calls | 500 | 4282 | 8.564 | 7.0 | 20.0 | 38 |
| overall | input_tokens | 500 | 116588268 | 233176.536 | 198530.0 | 541845.5 | 1044027 |
| overall | output_tokens | 500 | 1997321 | 3994.642 | 3748.0 | 7606.35 | 11107 |
| overall | cached_input_tokens | 500 | 37872128 | 75744.256 | 65792.0 | 172480.0 | 358272 |
| overall | reasoning_tokens | 500 | 0 | 0 | 0.0 | 0.0 | 0 |
| overall | seconds | 500 | 73864.826 | 147.73 | 137.094 | 283.123 | 770.951 |

| Measure | Observed questions | Total | Mean |
| --- | --- | --- | --- |
| input_tokens | 500 | 116588268 | 233176.536 |
| output_tokens | 500 | 1997321 | 3994.642 |
| total_tokens | 500 | 118585589 | 237171.178 |
| cached_input_tokens | 500 | 37872128 | 75744.256 |
| reasoning_tokens | 500 | 0 | 0 |
| model_calls | 500 | 14422 | 28.844 |
| tool_calls | 500 | 22156 | 44.312 |
| sql_calls | 500 | 4282 | 8.564 |
| seconds | 500 | 73864.826 | 147.729652 |

| Node | Visits | Model calls | Tool calls | SQL calls | Seconds |
| --- | --- | --- | --- | --- | --- |
| a1 | 1057 | 10906 | 19180 | 2966 | 58495.214 |
| b1 | 1056 | 1057 | 0 | 0 | 4493.046013341751 |
| c1 | 500 | 2459 | 2976 | 1316 | 10795.652 |

| Split | Token field | Observed calls | Model calls |
| --- | --- | --- | --- |
| dev | input_tokens | 11424 | 11425 |
| dev | output_tokens | 11424 | 11425 |
| dev | cached_input_tokens | 11424 | 11425 |
| dev | reasoning_tokens | 11424 | 11425 |
| test | input_tokens | 2997 | 2997 |
| test | output_tokens | 2997 | 2997 |
| test | cached_input_tokens | 2997 | 2997 |
| test | reasoning_tokens | 2997 | 2997 |
| overall | input_tokens | 14421 | 14422 |
| overall | output_tokens | 14421 | 14422 |
| overall | cached_input_tokens | 14421 | 14422 |
| overall | reasoning_tokens | 14421 | 14422 |

Cached input tokens are included in input totals; reasoning tokens are included in output totals. Do not add them again. Observed-question counts are shown; incomplete calls can have missing usage. B1 counts include failed invocations, whereas A1/C1 counters depend on observed AI messages; tool observer counts may include attempted/rejected middleware calls, and metadata logs additionally include bootstrap operations. Question latency totals are sequential inference time, distinct from scorer/rendering wall time. SIWC returns no billed dollar amount; actual costs and cost per correct answer are unavailable. API list prices were not substituted for SIWC billing.

## Historical comparisons and attribution

| Historical run | EX | Matched question coverage | Fixed / regressed |
| --- | --- | --- | --- |
| Metadata v1 | Unavailable | False | Unavailable |
| generalized-v1 B0 | 319/500 (63.80%) | True | 89 / 68 |

Generalized B0 previously scored 319/500 (63.80%); earlier B0 scored 294/500 (58.80%; Dev 235/400, Test 59/100). Original Mini-Dev 299/500 (59.80%) is a different dataset version and cannot be compared as a matched control. Historical Metadata v1 report gives 326/500 (65.20%; Dev 261/400, Test 65/100), but available source artifacts determine whether an actual paired comparison is possible.

Previous Metadata Discovery V2 was stopped after 46 Dev predictions, 44 missing SQL (95.65%), with 124 A1 tool-limit errors and 411 metadata-budget read errors. It used 8 A1 model calls / 10 tools per attempt and lacked the current handoff recovery, C1 fallback, read caching and write serialization fixes. Its EX was never scored. The later resource-budget experiment was interrupted before any completed prediction. Both are incomplete runs; neither provides full Dev/Test EX.

This run changes description availability, resource budgets and workflow reliability relative to that earlier Metadata Discovery V2. Any coverage or EX difference is descriptive. Restored descriptions and increased budgets cannot be assigned separate causal effects without matched ablations at fixed code, model, selection, order and knowledge policy. Test also uses knowledge learned during Dev and remains writable, so it measures continual same-database reuse, not an untouched official hidden test.

## Root causes and recommended improvements

1. Use actual node errors and knowledge operations to distinguish failed discovery handoff, invalid B1 output, context/tool ceilings and final SQL failures. The accompanying inventories identify the affected questions and retain evidence rather than treating every result mismatch as a proven semantic cause.
2. Target invalid note creation and duplicate writes using the observed error counts; require A1 to use tool-returned provenance IDs and revise existing definitions when appropriate. Audit semantic usefulness rather than maximizing note count.
3. Review the mismatch inventory against the question, evidence, actual database and evaluator reference before changing agent logic. Structural flags support triage, not automatic fixes or claims that gold is wrong.
4. Run controlled description-on/off and budget-low/high ablations with fixed current code and fresh stores for each cell. Keep the existing full baseline unchanged; report paired gains/regressions and resource cost alongside EX. This is the experiment needed to distinguish descriptions from resources.
5. Preserve C1 fallback, cached note reads and serialized index writes; use the integrity audit to detect any remaining storage issues. If limit errors persist, reserve a structured final A1 handoff and make remaining budgets visible.


## Concrete failure review and follow-up

All 160 failures are indexed. The following 16 result mismatches were selected for a direct question/evidence/predicted/reference SQL review across databases; they are not a random sample or an exhaustive semantic categorization of all 154 mismatches. Differences below are verified in the saved SQL. Except for compiler diagnostics and the already-scored constant answer, no corrective SQL counterfactual was evaluated.

| Question | Verified difference category | Finding |
| --- | --- | --- |
| 8 | output coverage | Only AdmEmail1 is returned; the request and reference unify all three administrator email fields. |
| 15 | row scope | The reference constrains SAT rows to rtype=S; the prediction omits this row-type condition. The text difference is verified; no single-change counterfactual was scored. |
| 40 | unsupported cohort restriction | The prediction adds School Type=High Schools (Public), narrowing a request covering regular non-charter schools; it also differs in code matching and FRPM share derivation. |
| 70 | value semantics | The prediction fixes frameVersion=future and returns that label; the reference computes the maximum numeric frame-version year. |
| 91 | unsupported cohort restriction | The prediction adds rarity=common even though the requested printing population is determined by pauper legality and paper availability. |
| 115 | wrong output measure | The prediction returns totalSetSize as the third column rather than the count of official translation languages. |
| 162 | ungrounded constant answer | The final prediction is SELECT 0 instead of deriving the requested count from customers and yearmonth. The stored EX confirms the constant is wrong. |
| 193 | temporal snapshot | The prediction uses only player-attribute rows dated July 12; the question explicitly requires all players with their latest ratings in force on that date. |
| 221 | unsupported cohort restriction | The prediction narrows withdrawal operations and standing orders to selected operations and SIPO; neither restriction appears in the request/reference. |
| 249 | table choice and result grain | The prediction orders results.fastestLapTime rows and takes 20 rows; the reference uses lapTimes, aggregates each driver minimum, and selects 20 drivers. |
| 304 | distinctness across groups | Summing distinct attendees per event can count a member repeatedly across multiple events of the same type; the reference counts distinct members per event type. |
| 344 | entity confusion | Strength attribute membership is used to identify heroes instead of membership in the Super Strength superpower. |
| 384 | age boundary | The prediction uses a 51-year cutoff; the reference uses Birthday < 1976-10-09 for older than 50 on the stated date. |
| 411 | patient versus visit grain | The prediction divides examination-row counts; the reference divides distinct patient counts. |
| 431 | extra output column | The prediction adds a total-patients column and returns three columns; the request/reference require two laboratory-related counts. |
| 483 | benchmark output representation | The prediction labels bond types single/double/triple while the reference returns encoded bond symbols. This is a strict EX representation mismatch; the wording permits a semantic ambiguity and is not proof that the plain-English labels are useless. |

These cases show recurring output-contract errors, unsupported extra filters, temporal cohort errors and incorrect counting grain. Restored descriptions can explain columns and encoded values, but they do not guarantee that C1 obeys the requested population, time scope, grouping or projection. No claim is made that a particular note caused these errors.

Four final SQL statements fail SQLite compilation:

| Question | SQLite compiler error | Final SQL present in observed execute_sql arguments |
| --- | --- | --- |
| 66 | no such column: t.translation | False |
| 201 | unrecognized token: "1997.0_total" | False |
| 219 | 1st ORDER BY term does not match any column in the result set | False |
| 73 | 1st ORDER BY term does not match any column in the result set | False |

Q66 references t.translation after its derived table projected only setCode; Q201 has unquoted numeric-leading aliases and invalid numeric identifier tokens; Q219 orders a compound SELECT by an expression not projected as an output column; Q73 references releaseDate outside the projected compound-result columns. A final read-only EXPLAIN gate on the exact returned SQL would catch these syntax/name-resolution defects. This recommendation has not been implemented and its net EX effect has not been measured.

Primary actionable changes supported by the review: (1) check the requested output columns and units before finalizing; (2) reject unrequested cohort restrictions unless grounded in the question; (3) explicitly track entity/counting grain and whether distinctness spans the whole requested group; (4) distinguish as-of snapshots from same-day updates; (5) compile the exact final SQL; (6) add bounded retry/backoff for transient provider overload, preserving attempts and usage. These would require a separate reviewed code change and evaluation; this run remains unchanged.

## Resource tradeoff against generalized-v1 B0

| Measure | B0 total (n) | Metadata Discovery V2 total (n) | Ratio |
| --- | --- | --- | --- |
| model_calls | 3043 (500) | 14422 (500) | 4.739 |
| tool_calls | 3677 (500) | 22156 (500) | 6.026 |
| sql_calls | 1689 (500) | 4282 (500) | 2.535 |
| input_tokens | 12795143 (500) | 116588268 (500) | 9.112 |
| output_tokens | 233182 (500) | 1997321 (500) | 8.566 |
| cached_input_tokens | 6723200 (500) | 37872128 (500) | 5.633 |
| reasoning_tokens | 0 (500) | 0 (500) | n/a |
| latency_ms | 12599540.0 (500) | 73864826.0 (500) | 5.863 |

Against the matched historical generalized-v1 B0, EX rises by 21/500 = 4.20 percentage points, with 89 corrected questions and 68 regressions. The comparison is historical rather than randomized; resource and workflow changes are confounded. Separate per-split paired reports are comparison-b0-dev.md and comparison-b0-test.md. The earlier 58.8% B0 differs by +9.2 percentage points; historical Metadata v1 at 65.2% differs by +2.8 points, without available per-question v1 artifacts for a new paired audit.

## Completion checks and export recovery

All 500 prediction IDs and 500 matching traces were checked against their exact ordered selections, with 400 Dev/100 Test scores. The scorer prints SMOKE SUBSET ONLY because this runner passes explicit question IDs; exact set/count validation confirms these are the complete splits. This is a misleading generic log label, not evidence of sampling.

The standard Dev Trace Explorer export hit its default 50 MiB input cap (Dev trace approximately 58 MiB). export_traces.py called the same viewer.write_html with a process-local, bounded 100 MiB cap for these verified local files. Both complete HTML explorers were generated. Original traces and repository code remain unchanged; the initial failed export log and successful recovery log are retained. The Test export used the same bounded process configuration.

Deep Agents also emits built-in filesystem tools such as grep, read_file and edit_file. The inspected installed create_deep_agent implementation defaults to StateBackend(), an agent-state virtual filesystem; the project passes no host filesystem backend or gold files. These calls are accounted for in tool counts and do not establish access to host gold SQL. No gold was supplied to inference.

Reported model calls count observed A1/C1 AI messages plus B1 invocations. Provider failures before an AI-message observer event can be absent from A1/C1 counts. Token totals are observed usage and therefore lower bounds for any unreported failed calls; B1 has one invocation with no usage. The per-call coverage ratio alone does not recover usage for those failed streams. Costs remain unavailable.

Additional evidence: sql-error-diagnostics.json, b0-resource-comparison.json, comparison-b0-dev.md, comparison-b0-test.md, trace-export-recovery.log, export_traces.py and execution-status.json.


## Final validation and practical interpretation

The complete 400/100 selections, trace alignment, prediction checksums, empty Dev starting hash, exact Dev-to-Test knowledge continuity, final knowledge snapshot, all original dataset hashes and the clean Git working tree pass independent final checks. The retained earlier environment logs show 159 offline tests passed (two skipped) and successful locked dependency synchronization; they were not rerun for this restoration-only change.

All 572 note files match their indexes and hashes. The store has table definitions for 74 of 76 schema tables (97.37%) and column definitions for 498 of 800 columns (62.25%). Coverage is a count of defined objects, not a measure of correctness or completeness of meaning. A1 consumes about 79.2% of recorded question time. Duplicate creates were rejected 890 times; this is a prominent avoidable source of discovery work, although its individual accuracy impact was not measured. Of 1,057 discovery decisions, 13 were missing and one inconsistent; 240/500 questions used all three attempts. There were 50 local model-limit and 20 local tool-limit exceptions, but no question report exceeded the global 120/200/80 model/tool/SQL ceilings (observed maxima 68/132/38). Metadata-context read rejection occurred seven times. The older partial Metadata Discovery V2 counts use a different run length and code/budget setting, so raw error totals are not matched rates.

C1 was reached for all 500 questions. The 224 fallback questions yielded 137 correct results (61.16%); the 276 questions with a sufficient B1 decision yielded 203 correct results (73.55%). This supports retaining a route to SQL generation when B1 is uncertain, but does not measure a causal fallback benefit. The main remaining accuracy problem is semantic/result correctness rather than absence of SQL: final SQL coverage is 498/500 (99.60%), with 154 runnable result mismatches.

Both HTML explorers were opened in headless Chromium. The rendered question selectors contain all 400 Dev and 100 Test questions, and the initial graphs and resource metadata render. Database labels were populated from the matching saved predictions in the exported HTML using the existing renderer, because original trace records omit the top-level database ID. Neither the traces nor agent code were changed. Browser diagnostics include unavailable GPU warnings; DOM loading and question-count checks succeeded. See explorer-validation.json. Interactive behavior beyond the initial rendering/selector population was not exhaustively tested.

Reported inference time totals 73,864.826 seconds (20.52 hours), excluding scoring, analysis and export. Observed usage is 116,588,268 input tokens, 1,997,321 output tokens, 37,872,128 cached input tokens (a subset of input), and zero observed reasoning tokens. Missing failed-stream usage prevents treating these as guaranteed billed totals. SIWC monetary cost is unavailable.



## Portable archive

See [README](README.md), [reproduction instructions](reproduce.md), [analysis](analysis-report/), [provenance](provenance/), and [knowledge](knowledge/). Raw traces, HTML explorers, databases, source archive and the gold SQL review column remain local. Their original locations and hashes are recorded in [local-artifacts.json](provenance/local-artifacts.json). The root checksums.sha256 verifies every archived file. The original report and source files remain unchanged.
