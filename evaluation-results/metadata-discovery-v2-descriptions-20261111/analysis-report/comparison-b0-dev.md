# BIRD — Control vs Metadata Agent

Control scores: `evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/dev/scores/per_question.jsonl`
Metadata scores: `scr/evaluation/result/metadata-discovery-v2-resource-full-20261111/MetadataDiscoveryV2/dev/metadata-discovery-v2-descriptions-dev-20261111/scores/per_question.jsonl`

## Execution accuracy (EX)

| Variant | Correct | EX |
| --- | ---: | ---: |
| Control | 255/400 | 63.75% |
| Metadata | 272/400 | 68.00% |

**EX change:** +4.25% (+17 questions).
**Fixed:** 71; **regressed:** 54.

## Accuracy by difficulty and database

| Group | Control EX | Metadata EX |
| --- | ---: | ---: |
| database:california_schools | 26/40 (65.0%) | 21/40 (52.5%) |
| database:card_games | 34/55 (61.8%) | 38/55 (69.1%) |
| database:codebase_community | 15/25 (60.0%) | 14/25 (56.0%) |
| database:debit_card_specializing | 8/11 (72.7%) | 5/11 (45.5%) |
| database:european_football_2 | 15/25 (60.0%) | 18/25 (72.0%) |
| database:financial | 19/37 (51.4%) | 24/37 (64.9%) |
| database:formula_1 | 33/44 (75.0%) | 38/44 (86.4%) |
| database:student_club | 23/30 (76.7%) | 22/30 (73.3%) |
| database:superhero | 19/40 (47.5%) | 29/40 (72.5%) |
| database:thrombosis_prediction | 45/68 (66.2%) | 46/68 (67.6%) |
| database:toxicology | 18/25 (72.0%) | 17/25 (68.0%) |
| difficulty:challenging | 230/369 (62.3%) | 251/369 (68.0%) |
| difficulty:moderate | 20/24 (83.3%) | 16/24 (66.7%) |
| difficulty:simple | 5/7 (71.4%) | 5/7 (71.4%) |

## Efficiency (observed records only)

| Measure | Control mean (observed) | Metadata mean (observed) |
| --- | ---: | ---: |
| tool_calls | 7.27 (n=400) | 43.76 (n=400) |
| model_calls | 6.04 (n=400) | 28.56 (n=400) |
| sql_calls | 3.33 (n=400) | 8.59 (n=400) |
| input_tokens | 25240.15 (n=400) | 229082.04 (n=400) |
| output_tokens | 462.82 (n=400) | 3970.96 (n=400) |
| cached_input_tokens | 13734.40 (n=400) | 74799.68 (n=400) |
| reasoning_tokens | 0.00 (n=400) | 0.00 (n=400) |
| latency_ms | 23572.10 (n=400) | 145131.80 (n=400) |

## Changed questions

**Corrected IDs:** 5, 12, 19, 21, 62, 65, 78, 79, 80, 81, 84, 92, 98, 102, 103, 105, 108, 128, 136, 139, 173, 174, 189, 194, 206, 212, 214, 222, 230, 235, 238, 251, 255, 259, 272, 277, 279, 286, 295, 306, 328, 345, 348, 350, 355, 356, 357, 360, 363, 366, 368, 370, 371, 374, 379, 380, 381, 398, 421, 439, 441, 445, 448, 458, 459, 466, 467, 480, 481, 486, 494

**Regressed IDs:** 8, 13, 16, 17, 18, 20, 26, 42, 44, 70, 71, 85, 93, 95, 106, 109, 112, 115, 124, 127, 133, 138, 152, 156, 162, 199, 203, 213, 270, 292, 312, 320, 322, 324, 332, 336, 339, 344, 347, 354, 384, 409, 411, 422, 425, 431, 432, 446, 447, 473, 483, 488, 489, 496

## Interpretation guardrails

- Both runs must use the same question IDs, source dataset and model settings. This script validates IDs/db/difficulty but cannot independently verify external model configuration.
- Metadata Test performance depends on question order and knowledge accumulated earlier in the same experiment. This is continual same-database reuse, not a frozen holdout.
- Token/latency means exclude missing values; inspect observed-call counts for partial data.
- Inspect trace and metadata-operation logs before attributing any EX gain to particular notes.
