# B0 Evaluation Report

Split: test (selected subset, NOT full-split or hidden-test EX)
Questions: 100
EX: **63/100 (63.00%)**

## Accuracy by difficulty

| Difficulty | Correct | Total | EX |
|---|---:|---:|---:|
| challenging | 8 | 19 | 42.11% |
| moderate | 32 | 50 | 64.00% |
| simple | 23 | 31 | 74.19% |

## Inference and SQL execution

| Metric | Total | Mean | P50 | P95 | Observed |
|---|---:|---:|---:|---:|---:|
| tool_calls | 505.00 | 5.05 | 4.50 | 9.00 | 100 |
| model_calls | 492.00 | 4.92 | 4.00 | 8.00 | 100 |
| sql_calls | 158.00 | 1.58 | 1.00 | 5.00 | 100 |
| sql_success_calls | 156.00 | 1.56 | 1.00 | 5.00 | 100 |
| sql_error_calls | 2.00 | 0.02 | 0.00 | 0.00 | 100 |
| sql_truncated_calls | 21.00 | 0.21 | 0.00 | 1.00 | 100 |
| input_tokens | 1616075.00 | 16160.75 | 13340.50 | 36425.00 | 100 |
| output_tokens | 25035.00 | 250.35 | 219.00 | 476.00 | 100 |
| total_tokens | 1641110.00 | 16411.10 | 13562.00 | 37002.00 | 100 |
| cached_input_tokens | 1010944.00 | 10109.44 | 8192.00 | 18304.00 | 100 |
| reasoning_tokens | 0.00 | 0.00 | 0.00 | 0.00 | 100 |
| input_tokens_observed_calls | 492.00 | 4.92 | 4.00 | 8.00 | 100 |
| output_tokens_observed_calls | 492.00 | 4.92 | 4.00 | 8.00 | 100 |
| total_tokens_observed_calls | 492.00 | 4.92 | 4.00 | 8.00 | 100 |
| cached_input_tokens_observed_calls | 492.00 | 4.92 | 4.00 | 8.00 | 100 |
| reasoning_tokens_observed_calls | 492.00 | 4.92 | 4.00 | 8.00 | 100 |
| latency_ms | 1811443.00 | 18114.43 | 15674.00 | 31429.00 | 100 |
| sql_execution_ms | 18696.99 | 186.97 | 2.09 | 128.95 | 100 |
| gold_sql_execution_ms | 2807.02 | 28.07 | 2.20 | 145.11 | 100 |
| agent_sql_execution_ms | 20994.13 | 212.06 | 4.26 | 1533.90 | 99 |
| sql_tool_success_rate | 0.9873417721518988 | — | — | — | — |
| final_sql_generation_rate | 1.0 | — | — | — | — |
| final_sql_execution_rate | 1.0 | — | — | — | — |

## Per-question scores

| Question | Difficulty | EX | Status | Model turns | Tool calls | Agent SQL calls | Inference ms |
|---|---|---:|---|---:|---:|---:|---:|
| 23 | moderate | 1 | correct | 5 | 5 | 2 | 16943.0 |
| 25 | moderate | 0 | incorrect_result | 6 | 7 | 3 | 21505.0 |
| 39 | simple | 1 | correct | 4 | 5 | 1 | 17852.0 |
| 41 | simple | 0 | incorrect_result | 5 | 5 | 1 | 17380.0 |
| 79 | moderate | 1 | correct | 4 | 3 | 1 | 11690.0 |
| 83 | challenging | 0 | incorrect_result | 8 | 7 | 4 | 30514.0 |
| 92 | simple | 1 | correct | 3 | 4 | 0 | 8884.0 |
| 98 | moderate | 1 | correct | 9 | 9 | 6 | 33650.0 |
| 115 | challenging | 0 | incorrect_result | 6 | 6 | 2 | 20284.0 |
| 119 | moderate | 1 | correct | 8 | 9 | 5 | 27568.0 |
| 120 | moderate | 0 | incorrect_result | 10 | 12 | 5 | 37946.0 |
| 186 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 15708.0 |
| 189 | moderate | 0 | incorrect_result | 8 | 10 | 5 | 31429.0 |
| 200 | simple | 1 | correct | 4 | 5 | 1 | 13270.0 |
| 201 | moderate | 1 | correct | 4 | 4 | 1 | 14828.0 |
| 218 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 13766.0 |
| 220 | challenging | 1 | correct | 5 | 6 | 1 | 15575.0 |
| 230 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 16355.0 |
| 242 | moderate | 1 | correct | 4 | 5 | 1 | 12532.0 |
| 255 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 13896.0 |
| 281 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 14231.0 |
| 341 | simple | 0 | incorrect_result | 5 | 4 | 2 | 15215.0 |
| 344 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 21124.0 |
| 347 | moderate | 0 | incorrect_result | 5 | 6 | 3 | 21423.0 |
| 377 | simple | 1 | correct | 4 | 3 | 1 | 14442.0 |
| 391 | moderate | 1 | correct | 6 | 5 | 2 | 22519.0 |
| 424 | simple | 0 | incorrect_result | 4 | 3 | 1 | 12150.0 |
| 459 | moderate | 1 | correct | 6 | 5 | 3 | 20119.0 |
| 474 | moderate | 1 | correct | 5 | 4 | 1 | 17467.0 |
| 479 | moderate | 1 | correct | 5 | 4 | 1 | 22050.0 |
| 483 | moderate | 0 | incorrect_result | 8 | 9 | 3 | 29260.0 |
| 528 | challenging | 0 | incorrect_result | 5 | 5 | 1 | 21920.0 |
| 531 | simple | 1 | correct | 4 | 3 | 1 | 12681.0 |
| 544 | moderate | 1 | correct | 4 | 4 | 1 | 15819.0 |
| 573 | simple | 1 | correct | 4 | 3 | 1 | 11776.0 |
| 637 | moderate | 0 | incorrect_result | 6 | 7 | 3 | 28302.0 |
| 639 | challenging | 0 | incorrect_result | 10 | 11 | 6 | 36753.0 |
| 640 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 14469.0 |
| 669 | simple | 1 | correct | 5 | 4 | 1 | 17352.0 |
| 671 | simple | 1 | correct | 4 | 4 | 1 | 13201.0 |
| 685 | moderate | 0 | incorrect_result | 6 | 6 | 3 | 21624.0 |
| 707 | moderate | 1 | correct | 4 | 4 | 1 | 14600.0 |
| 740 | moderate | 1 | correct | 5 | 6 | 1 | 18375.0 |
| 744 | challenging | 1 | correct | 4 | 4 | 1 | 14128.0 |
| 745 | simple | 1 | correct | 4 | 3 | 1 | 9439.0 |
| 751 | moderate | 0 | incorrect_result | 4 | 6 | 1 | 18512.0 |
| 753 | moderate | 1 | correct | 4 | 4 | 1 | 11858.0 |
| 781 | simple | 1 | correct | 4 | 4 | 1 | 13395.0 |
| 785 | simple | 1 | correct | 5 | 4 | 1 | 14953.0 |
| 788 | challenging | 1 | correct | 4 | 5 | 1 | 15018.0 |
| 801 | moderate | 1 | correct | 5 | 5 | 2 | 16563.0 |
| 824 | moderate | 1 | correct | 4 | 5 | 1 | 13655.0 |
| 859 | simple | 1 | correct | 4 | 4 | 1 | 14510.0 |
| 879 | moderate | 1 | correct | 5 | 4 | 1 | 17637.0 |
| 881 | moderate | 0 | incorrect_result | 5 | 5 | 2 | 18969.0 |
| 895 | moderate | 1 | correct | 4 | 5 | 1 | 16480.0 |
| 898 | simple | 0 | incorrect_result | 4 | 3 | 1 | 14084.0 |
| 901 | simple | 1 | correct | 4 | 4 | 1 | 12822.0 |
| 945 | simple | 1 | correct | 4 | 3 | 1 | 10809.0 |
| 955 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 16054.0 |
| 959 | simple | 1 | correct | 4 | 7 | 1 | 14648.0 |
| 972 | moderate | 1 | correct | 4 | 4 | 1 | 13774.0 |
| 978 | simple | 0 | incorrect_result | 5 | 4 | 1 | 17276.0 |
| 1001 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 14712.0 |
| 1002 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 17774.0 |
| 1039 | simple | 1 | correct | 5 | 5 | 1 | 16794.0 |
| 1076 | challenging | 1 | correct | 4 | 4 | 1 | 13037.0 |
| 1088 | moderate | 1 | correct | 5 | 4 | 1 | 14441.0 |
| 1103 | moderate | 1 | correct | 4 | 3 | 1 | 12934.0 |
| 1110 | moderate | 1 | correct | 8 | 7 | 3 | 29604.0 |
| 1130 | moderate | 1 | correct | 5 | 4 | 1 | 20793.0 |
| 1133 | simple | 1 | correct | 4 | 3 | 1 | 11414.0 |
| 1139 | challenging | 1 | correct | 4 | 4 | 1 | 19184.0 |
| 1146 | moderate | 1 | correct | 5 | 4 | 1 | 18675.0 |
| 1147 | simple | 1 | correct | 5 | 4 | 1 | 14537.0 |
| 1150 | moderate | 1 | correct | 4 | 3 | 1 | 71504.0 |
| 1164 | moderate | 1 | correct | 4 | 4 | 1 | 12953.0 |
| 1179 | moderate | 0 | incorrect_result | 5 | 6 | 2 | 16248.0 |
| 1195 | moderate | 1 | correct | 4 | 5 | 1 | 13651.0 |
| 1220 | simple | 1 | correct | 4 | 5 | 1 | 11879.0 |
| 1239 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 15006.0 |
| 1241 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 12984.0 |
| 1256 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 16574.0 |
| 1257 | challenging | 1 | correct | 4 | 5 | 1 | 15640.0 |
| 1317 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 14381.0 |
| 1340 | moderate | 1 | correct | 18 | 19 | 11 | 58975.0 |
| 1352 | moderate | 1 | correct | 4 | 4 | 1 | 12992.0 |
| 1359 | challenging | 1 | correct | 4 | 4 | 1 | 15551.0 |
| 1371 | simple | 1 | correct | 5 | 4 | 1 | 20373.0 |
| 1375 | moderate | 1 | correct | 4 | 4 | 1 | 13721.0 |
| 1380 | simple | 1 | correct | 5 | 4 | 1 | 16058.0 |
| 1392 | simple | 0 | incorrect_result | 4 | 3 | 1 | 17283.0 |
| 1410 | simple | 0 | incorrect_result | 4 | 4 | 1 | 17336.0 |
| 1432 | moderate | 1 | correct | 4 | 4 | 1 | 12696.0 |
| 1476 | challenging | 1 | correct | 5 | 7 | 2 | 16069.0 |
| 1483 | simple | 1 | correct | 4 | 4 | 1 | 13257.0 |
| 1484 | simple | 1 | correct | 5 | 4 | 2 | 18372.0 |
| 1505 | simple | 0 | incorrect_result | 6 | 5 | 1 | 21591.0 |
| 1506 | moderate | 1 | correct | 4 | 5 | 1 | 14968.0 |
| 1531 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 14451.0 |

Times are milliseconds. Model turns represent observable main-agent model calls.
Cached input tokens are part of input tokens; reasoning tokens are part of output tokens.
Optional usage fields may be partial: compare *_observed_calls with model_calls.
Thinking/effort values are reported only when a provider supplies them.
Nested subagent activity may be unobserved. n/a does not mean zero.
Agent SQL tool success is not equivalent to final SQL EX.
Gold SQL is validated separately before any predicted SQL scoring.
