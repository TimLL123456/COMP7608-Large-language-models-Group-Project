# B0 Evaluation Report

Split: test (selected subset, NOT full-split or hidden-test EX)
Questions: 100
EX: **59/100 (59.00%)**

## Accuracy by difficulty

| Difficulty | Correct | Total | EX |
|---|---:|---:|---:|
| challenging | 54 | 91 | 59.34% |
| moderate | 5 | 8 | 62.50% |
| simple | 0 | 1 | 0.00% |

## Inference and SQL execution

| Metric | Total | Mean | P50 | P95 | Observed |
|---|---:|---:|---:|---:|---:|
| tool_calls | 678.00 | 6.78 | 6.00 | 13.00 | 100 |
| model_calls | 587.00 | 5.87 | 5.00 | 11.00 | 100 |
| sql_calls | 280.00 | 2.80 | 2.00 | 8.00 | 100 |
| sql_success_calls | 275.00 | 2.75 | 2.00 | 8.00 | 100 |
| sql_error_calls | 5.00 | 0.05 | 0.00 | 0.00 | 100 |
| sql_truncated_calls | 29.00 | 0.29 | 0.00 | 2.00 | 100 |
| input_tokens | 2200441.00 | 22004.41 | 16792.50 | 52239.00 | 100 |
| output_tokens | 46151.00 | 461.51 | 407.50 | 1008.00 | 100 |
| total_tokens | 2246592.00 | 22465.92 | 17208.50 | 53400.00 | 100 |
| cached_input_tokens | 1136768.00 | 11367.68 | 9792.00 | 23936.00 | 100 |
| reasoning_tokens | 0.00 | 0.00 | 0.00 | 0.00 | 100 |
| input_tokens_observed_calls | 587.00 | 5.87 | 5.00 | 11.00 | 100 |
| output_tokens_observed_calls | 587.00 | 5.87 | 5.00 | 11.00 | 100 |
| total_tokens_observed_calls | 587.00 | 5.87 | 5.00 | 11.00 | 100 |
| cached_input_tokens_observed_calls | 587.00 | 5.87 | 5.00 | 11.00 | 100 |
| reasoning_tokens_observed_calls | 587.00 | 5.87 | 5.00 | 11.00 | 100 |
| latency_ms | 3271796.00 | 32717.96 | 20755.50 | 50530.00 | 100 |
| sql_execution_ms | 26539.09 | 265.39 | 4.07 | 389.99 | 100 |
| gold_sql_execution_ms | 31316.01 | 313.16 | 4.61 | 578.55 | 100 |
| agent_sql_execution_ms | 943473.51 | 9434.74 | 17.83 | 3638.89 | 100 |
| sql_tool_success_rate | 0.9821428571428571 | — | — | — | — |
| final_sql_generation_rate | 1.0 | — | — | — | — |
| final_sql_execution_rate | 0.99 | — | — | — | — |

## Per-question scores

| Question | Difficulty | EX | Status | Model turns | Tool calls | Agent SQL calls | Inference ms |
|---|---|---:|---|---:|---:|---:|---:|
| 0 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 12666.0 |
| 15 | challenging | 1 | correct | 9 | 10 | 6 | 30381.0 |
| 22 | challenging | 1 | correct | 5 | 4 | 2 | 16349.0 |
| 30 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 17244.0 |
| 32 | challenging | 0 | incorrect_result | 9 | 10 | 6 | 50530.0 |
| 35 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 28569.0 |
| 40 | challenging | 1 | correct | 10 | 11 | 7 | 52936.0 |
| 43 | challenging | 1 | correct | 7 | 8 | 4 | 25532.0 |
| 46 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 16535.0 |
| 49 | simple | 0 | incorrect_result | 14 | 13 | 11 | 42173.0 |
| 58 | challenging | 0 | incorrect_result | 6 | 5 | 2 | 320586.0 |
| 59 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 13486.0 |
| 60 | challenging | 1 | correct | 5 | 4 | 1 | 16996.0 |
| 63 | challenging | 1 | correct | 6 | 5 | 3 | 19814.0 |
| 73 | challenging | 0 | sql_error | 9 | 10 | 6 | 41624.0 |
| 76 | challenging | 0 | incorrect_result | 4 | 3 | 1 | 12602.0 |
| 87 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 16389.0 |
| 91 | challenging | 1 | correct | 5 | 5 | 1 | 14885.0 |
| 97 | challenging | 1 | correct | 13 | 14 | 10 | 45511.0 |
| 107 | challenging | 0 | incorrect_result | 10 | 11 | 7 | 347251.0 |
| 111 | challenging | 1 | correct | 4 | 3 | 1 | 15242.0 |
| 113 | challenging | 1 | correct | 5 | 6 | 2 | 17117.0 |
| 117 | challenging | 1 | correct | 11 | 10 | 7 | 39342.0 |
| 119 | moderate | 1 | correct | 4 | 4 | 1 | 26298.0 |
| 132 | challenging | 1 | correct | 4 | 5 | 1 | 20510.0 |
| 135 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 20283.0 |
| 137 | challenging | 1 | correct | 6 | 5 | 3 | 24409.0 |
| 141 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15116.0 |
| 144 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 14897.0 |
| 149 | challenging | 1 | correct | 6 | 9 | 5 | 33719.0 |
| 159 | challenging | 1 | correct | 8 | 11 | 5 | 25722.0 |
| 160 | challenging | 1 | correct | 6 | 7 | 3 | 29973.0 |
| 167 | challenging | 1 | correct | 5 | 4 | 1 | 18777.0 |
| 168 | challenging | 1 | correct | 5 | 5 | 2 | 20245.0 |
| 170 | moderate | 1 | correct | 4 | 3 | 1 | 13306.0 |
| 185 | challenging | 1 | correct | 4 | 4 | 1 | 15829.0 |
| 187 | challenging | 0 | incorrect_result | 4 | 7 | 1 | 33838.0 |
| 193 | challenging | 1 | correct | 7 | 7 | 4 | 333071.0 |
| 204 | challenging | 0 | incorrect_result | 5 | 6 | 1 | 24886.0 |
| 207 | challenging | 1 | correct | 6 | 10 | 5 | 23870.0 |
| 208 | challenging | 1 | correct | 6 | 8 | 3 | 27058.0 |
| 209 | challenging | 1 | correct | 5 | 8 | 2 | 22461.0 |
| 211 | challenging | 0 | incorrect_result | 5 | 8 | 3 | 22365.0 |
| 218 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 20149.0 |
| 221 | challenging | 1 | correct | 7 | 9 | 4 | 28092.0 |
| 233 | challenging | 1 | correct | 8 | 13 | 6 | 40168.0 |
| 239 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 19780.0 |
| 244 | challenging | 1 | correct | 4 | 5 | 1 | 19292.0 |
| 249 | challenging | 1 | correct | 4 | 5 | 1 | 23390.0 |
| 252 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 18166.0 |
| 253 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 15376.0 |
| 254 | challenging | 1 | correct | 4 | 5 | 1 | 15300.0 |
| 256 | challenging | 1 | correct | 4 | 5 | 1 | 16563.0 |
| 262 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 14310.0 |
| 264 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 14685.0 |
| 284 | challenging | 1 | correct | 6 | 7 | 3 | 25542.0 |
| 289 | challenging | 1 | correct | 5 | 6 | 2 | 19816.0 |
| 293 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 12126.0 |
| 298 | challenging | 1 | correct | 5 | 5 | 2 | 21533.0 |
| 299 | moderate | 1 | correct | 5 | 6 | 2 | 21613.0 |
| 303 | challenging | 0 | incorrect_result | 7 | 7 | 4 | 30829.0 |
| 304 | challenging | 1 | correct | 4 | 6 | 1 | 19070.0 |
| 307 | challenging | 1 | correct | 6 | 8 | 3 | 24872.0 |
| 317 | challenging | 1 | correct | 5 | 6 | 2 | 18845.0 |
| 326 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 23077.0 |
| 338 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 14112.0 |
| 343 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 19699.0 |
| 346 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 12535.0 |
| 349 | challenging | 0 | incorrect_result | 11 | 14 | 8 | 47881.0 |
| 353 | challenging | 0 | incorrect_result | 13 | 18 | 10 | 47226.0 |
| 362 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 20121.0 |
| 369 | challenging | 0 | incorrect_result | 5 | 8 | 2 | 22889.0 |
| 372 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 17230.0 |
| 373 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 24172.0 |
| 375 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 13471.0 |
| 382 | challenging | 1 | correct | 5 | 5 | 2 | 19869.0 |
| 385 | challenging | 1 | correct | 8 | 8 | 3 | 30759.0 |
| 386 | challenging | 1 | correct | 5 | 5 | 1 | 16117.0 |
| 387 | challenging | 1 | correct | 5 | 6 | 2 | 18940.0 |
| 388 | moderate | 1 | correct | 5 | 6 | 2 | 17354.0 |
| 396 | challenging | 1 | correct | 6 | 7 | 3 | 27695.0 |
| 399 | challenging | 1 | correct | 5 | 6 | 2 | 18120.0 |
| 403 | challenging | 1 | correct | 4 | 4 | 1 | 18371.0 |
| 404 | challenging | 0 | incorrect_result | 14 | 15 | 11 | 53564.0 |
| 414 | challenging | 1 | correct | 7 | 8 | 4 | 31630.0 |
| 419 | challenging | 1 | correct | 7 | 8 | 4 | 26703.0 |
| 436 | challenging | 1 | correct | 10 | 12 | 8 | 33015.0 |
| 449 | challenging | 1 | correct | 8 | 9 | 5 | 28209.0 |
| 451 | challenging | 1 | correct | 4 | 5 | 1 | 12801.0 |
| 452 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 25351.0 |
| 455 | challenging | 1 | correct | 4 | 5 | 1 | 12985.0 |
| 456 | challenging | 0 | incorrect_result | 6 | 6 | 3 | 25881.0 |
| 463 | challenging | 1 | correct | 6 | 7 | 3 | 22755.0 |
| 474 | moderate | 1 | correct | 6 | 8 | 2 | 21001.0 |
| 475 | challenging | 1 | correct | 5 | 6 | 1 | 22459.0 |
| 479 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 19417.0 |
| 484 | challenging | 1 | correct | 7 | 8 | 3 | 25572.0 |
| 490 | challenging | 1 | correct | 4 | 7 | 1 | 17966.0 |
| 493 | challenging | 1 | correct | 6 | 8 | 3 | 23732.0 |
| 495 | challenging | 1 | correct | 5 | 7 | 2 | 19207.0 |

Times are milliseconds. Model turns represent observable main-agent model calls.
Cached input tokens are part of input tokens; reasoning tokens are part of output tokens.
Optional usage fields may be partial: compare *_observed_calls with model_calls.
Thinking/effort values are reported only when a provider supplies them.
Nested subagent activity may be unobserved. n/a does not mean zero.
Agent SQL tool success is not equivalent to final SQL EX.
Gold SQL is validated separately before any predicted SQL scoring.
