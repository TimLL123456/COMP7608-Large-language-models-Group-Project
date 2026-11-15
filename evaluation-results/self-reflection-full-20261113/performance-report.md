# Self Reflection Agent — full Mini-Dev performance report

The agent achieved **350/500 correct results (70.00% execution accuracy)**. It returned SQL for 498 questions; 148 returned a different result from the reference and two had no final SQL.

| Split | Correct | Questions | EX |
| --- | ---: | ---: | ---: |
| Dev | 280 | 400 | 70.00% |
| Local held-out Test | 70 | 100 | 70.00% |
| Overall | 350 | 500 | 70.00% |

## Configuration and scope

Inference source: `cbb8ea4ada492ceb7970692f571b4e36a34b8227`. Provider: `chatgpt-siwc`; model: `gpt-6-luna`; reasoning effort: `none`; B0 prompt: `generalized-v1`. The SQL-first workflow allows three B0 attempts, 40 reviewer model calls and 39 inspections per candidate, and 240 aggregate model/tool/SQL calls. See each inference manifest for reservations and exact limits.

These are the complete 500 questions of the local BIRD Mini-Dev 2026 dataset, with its fixed 400/100 split. They are not an official hidden-test result. Reference SQL was used only by the offline scorer. Description CSVs are preserved as dataset provenance; their presence does not establish that a reviewer could access them through its tools.

## Accuracy by difficulty

| Difficulty | Correct | Questions | EX |
| --- | ---: | ---: | ---: |
| challenging | 319 | 460 | 69.35% |
| moderate | 23 | 32 | 71.88% |
| simple | 8 | 8 | 100.00% |

## Accuracy by database

| Database | Correct | Questions | EX |
| --- | ---: | ---: | ---: |
| california_schools | 35 | 49 | 71.43% |
| card_games | 47 | 69 | 68.12% |
| codebase_community | 24 | 31 | 77.42% |
| debit_card_specializing | 11 | 14 | 78.57% |
| european_football_2 | 24 | 31 | 77.42% |
| financial | 28 | 46 | 60.87% |
| formula_1 | 44 | 55 | 80.00% |
| student_club | 27 | 37 | 72.97% |
| superhero | 25 | 50 | 50.00% |
| thrombosis_prediction | 61 | 86 | 70.93% |
| toxicology | 24 | 32 | 75.00% |

## Reviewer decisions and independent scoring

Reviewer PASS is a provisional decision, not the execution accuracy label. FAIL can still retain a SQL prediction. The following table joins final reviewer outcomes to independently scored answers.

| Reviewer outcome | Correct | Incorrect result | Missing SQL |
| --- | ---: | ---: | ---: |
| ERROR | 4 | 0 | 0 |
| FAIL | 12 | 16 | 0 |
| PASS | 264 | 93 | 0 |
| UNCERTAIN | 70 | 39 | 1 |
| unverified | 0 | 0 | 1 |

The [failure inventory](analysis-report/failure-inventory.csv) includes every independently incorrect or missing answer. It does not claim a semantic root cause for every failure. Full structured reviewer diagnoses are saved in each split’s `reviews/` directory.

## Resources and latency

The run recorded 6,711 model calls, 8,209 tool calls and 4,278 SQL calls. Observed tokens: 26,977,682 input and 1,884,806 output (28,862,488 total). Provider billing cost was not measured. Cached input tokens are included in reported input usage, not additional tokens.

Recorded question inference time totals 18.92 hours; mean 136.2 seconds and median 61.3 seconds. The sequential controller completed in about 19 hours, including scoring and visualization. Slowest question: Q199, 24.90 minutes. See [the ten slowest questions](analysis-report/slowest-questions.json). Nested/provider failures may leave usage undercounted.

## Validation and limitations

Preflight ran 198 tests: 195 passed, two skipped, and `test_forced_sql_finalization_generates_executable_sql` failed. The evaluated source was not patched; the complete test output is preserved.

Archive validation checks all 500 distinct question IDs, split counts, source revision, original prediction/trace/review hashes, and gzip round-trip integrity. SQL generation is 498/500; strict EX is 350/500. Original manifests and controller retain historic absolute paths. The nested B0 report hard-codes its NVIDIA default model label even when the CLI injects another model; this run’s CLI configuration and outer manifests identify `gpt-6-luna` as the selected model.

No new model inference was performed during packaging. No matched-compute or causal improvement claim is made.
