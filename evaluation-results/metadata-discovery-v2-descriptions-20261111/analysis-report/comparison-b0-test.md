# BIRD — Control vs Metadata Agent

Control scores: `evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/test/scores/per_question.jsonl`
Metadata scores: `scr/evaluation/result/metadata-discovery-v2-resource-full-20261111/MetadataDiscoveryV2/test/metadata-discovery-v2-descriptions-test-20261111/scores/per_question.jsonl`

## Execution accuracy (EX)

| Variant | Correct | EX |
| --- | ---: | ---: |
| Control | 64/100 | 64.00% |
| Metadata | 68/100 | 68.00% |

**EX change:** +4.00% (+4 questions).
**Fixed:** 18; **regressed:** 14.

## Accuracy by difficulty and database

| Group | Control EX | Metadata EX |
| --- | ---: | ---: |
| database:california_schools | 6/9 (66.7%) | 5/9 (55.6%) |
| database:card_games | 10/14 (71.4%) | 10/14 (71.4%) |
| database:codebase_community | 2/6 (33.3%) | 4/6 (66.7%) |
| database:debit_card_specializing | 3/3 (100.0%) | 3/3 (100.0%) |
| database:european_football_2 | 5/6 (83.3%) | 4/6 (66.7%) |
| database:financial | 6/9 (66.7%) | 5/9 (55.6%) |
| database:formula_1 | 9/11 (81.8%) | 7/11 (63.6%) |
| database:student_club | 4/7 (57.1%) | 4/7 (57.1%) |
| database:superhero | 1/10 (10.0%) | 6/10 (60.0%) |
| database:thrombosis_prediction | 14/18 (77.8%) | 14/18 (77.8%) |
| database:toxicology | 4/7 (57.1%) | 6/7 (85.7%) |
| difficulty:challenging | 59/91 (64.8%) | 62/91 (68.1%) |
| difficulty:moderate | 4/8 (50.0%) | 5/8 (62.5%) |
| difficulty:simple | 1/1 (100.0%) | 1/1 (100.0%) |

## Efficiency (observed records only)

| Measure | Control mean (observed) | Metadata mean (observed) |
| --- | ---: | ---: |
| tool_calls | 7.69 (n=100) | 46.54 (n=100) |
| model_calls | 6.25 (n=100) | 29.97 (n=100) |
| sql_calls | 3.59 (n=100) | 8.48 (n=100) |
| input_tokens | 26990.83 (n=100) | 249554.53 (n=100) |
| output_tokens | 480.52 (n=100) | 4089.37 (n=100) |
| cached_input_tokens | 12294.40 (n=100) | 79522.56 (n=100) |
| reasoning_tokens | 0.00 (n=100) | 0.00 (n=100) |
| latency_ms | 31707.02 (n=100) | 158121.05 (n=100) |

## Changed questions

**Corrected IDs:** 30, 59, 76, 132, 137, 144, 218, 307, 326, 338, 343, 349, 362, 369, 387, 456, 474, 493

**Regressed IDs:** 15, 40, 73, 91, 141, 193, 211, 221, 249, 256, 299, 304, 388, 396

## Interpretation guardrails

- Both runs must use the same question IDs, source dataset and model settings. This script validates IDs/db/difficulty but cannot independently verify external model configuration.
- Metadata Test performance depends on question order and knowledge accumulated earlier in the same experiment. This is continual same-database reuse, not a frozen holdout.
- Token/latency means exclude missing values; inspect observed-call counts for partial data.
- Inspect trace and metadata-operation logs before attributing any EX gain to particular notes.
