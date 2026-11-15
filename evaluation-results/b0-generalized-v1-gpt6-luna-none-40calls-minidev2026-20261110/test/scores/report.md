# B0 Evaluation Report

Split: test (selected subset, NOT full-split or hidden-test EX)
Questions: 100
EX: **64/100 (64.00%)**

## Accuracy by difficulty

| Difficulty | Correct | Total | EX |
|---|---:|---:|---:|
| challenging | 59 | 91 | 64.84% |
| moderate | 4 | 8 | 50.00% |
| simple | 1 | 1 | 100.00% |

## Inference and SQL execution

| Metric | Total | Mean | P50 | P95 | Observed |
|---|---:|---:|---:|---:|---:|
| tool_calls | 769.00 | 7.69 | 7.00 | 13.00 | 100 |
| model_calls | 625.00 | 6.25 | 6.00 | 10.00 | 100 |
| sql_calls | 359.00 | 3.59 | 3.00 | 7.00 | 100 |
| sql_success_calls | 349.00 | 3.49 | 3.00 | 7.00 | 100 |
| sql_error_calls | 9.00 | 0.09 | 0.00 | 1.00 | 100 |
| sql_truncated_calls | 41.00 | 0.41 | 0.00 | 2.00 | 100 |
| input_tokens | 2699083.00 | 26990.83 | 20507.00 | 52634.00 | 100 |
| output_tokens | 48052.00 | 480.52 | 386.00 | 1005.00 | 100 |
| total_tokens | 2747135.00 | 27471.35 | 20887.00 | 53301.00 | 100 |
| cached_input_tokens | 1229440.00 | 12294.40 | 10624.00 | 19840.00 | 100 |
| reasoning_tokens | 0.00 | 0.00 | 0.00 | 0.00 | 100 |
| input_tokens_observed_calls | 625.00 | 6.25 | 6.00 | 10.00 | 100 |
| output_tokens_observed_calls | 625.00 | 6.25 | 6.00 | 10.00 | 100 |
| total_tokens_observed_calls | 625.00 | 6.25 | 6.00 | 10.00 | 100 |
| cached_input_tokens_observed_calls | 625.00 | 6.25 | 6.00 | 10.00 | 100 |
| reasoning_tokens_observed_calls | 625.00 | 6.25 | 6.00 | 10.00 | 100 |
| latency_ms | 3170702.00 | 31707.02 | 23871.50 | 58521.00 | 100 |
| sql_execution_ms | 15756.81 | 159.16 | 3.94 | 341.00 | 99 |
| gold_sql_execution_ms | 30220.91 | 302.21 | 6.10 | 526.04 | 100 |
| agent_sql_execution_ms | 620029.16 | 6200.29 | 11.90 | 1147.76 | 100 |
| sql_tool_success_rate | 0.9721448467966574 | — | — | — | — |
| final_sql_generation_rate | 0.99 | — | — | — | — |
| final_sql_execution_rate | 1.0 | — | — | — | — |

## Per-question scores

| Question | Difficulty | EX | Status | Model turns | Tool calls | Agent SQL calls | Inference ms |
|---|---|---:|---|---:|---:|---:|---:|
| 0 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 15962.0 |
| 15 | challenging | 1 | correct | 9 | 10 | 6 | 30885.0 |
| 22 | challenging | 1 | correct | 6 | 5 | 3 | 16784.0 |
| 30 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 13530.0 |
| 32 | challenging | 1 | correct | 11 | 13 | 9 | 45697.0 |
| 35 | challenging | 1 | correct | 6 | 7 | 3 | 24293.0 |
| 40 | challenging | 1 | correct | 22 | 23 | 19 | 91043.0 |
| 43 | challenging | 1 | correct | 7 | 9 | 4 | 27083.0 |
| 46 | challenging | 0 | incorrect_result | 6 | 6 | 3 | 16652.0 |
| 49 | simple | 1 | correct | 5 | 6 | 2 | 17084.0 |
| 58 | challenging | 1 | correct | 8 | 7 | 3 | 324386.0 |
| 59 | moderate | 0 | incorrect_result | 6 | 5 | 2 | 16282.0 |
| 60 | challenging | 1 | correct | 4 | 3 | 1 | 23200.0 |
| 63 | challenging | 1 | correct | 5 | 6 | 2 | 15798.0 |
| 73 | challenging | 1 | correct | 4 | 4 | 1 | 18361.0 |
| 76 | challenging | 0 | incorrect_result | 5 | 4 | 2 | 18851.0 |
| 87 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 10216.0 |
| 91 | challenging | 1 | correct | 5 | 6 | 2 | 15544.0 |
| 97 | challenging | 1 | correct | 8 | 10 | 7 | 26183.0 |
| 107 | challenging | 1 | correct | 7 | 8 | 4 | 26962.0 |
| 111 | challenging | 1 | correct | 5 | 4 | 2 | 13471.0 |
| 113 | challenging | 1 | correct | 9 | 11 | 6 | 29506.0 |
| 117 | challenging | 0 | incorrect_result | 7 | 7 | 4 | 24380.0 |
| 119 | moderate | 1 | correct | 4 | 4 | 1 | 12201.0 |
| 132 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 32478.0 |
| 135 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 19977.0 |
| 137 | challenging | 0 | incorrect_result | 6 | 5 | 3 | 19723.0 |
| 141 | challenging | 1 | correct | 6 | 6 | 3 | 19572.0 |
| 144 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 14613.0 |
| 149 | challenging | 1 | correct | 6 | 8 | 4 | 28667.0 |
| 159 | challenging | 1 | correct | 10 | 13 | 6 | 31252.0 |
| 160 | challenging | 1 | correct | 5 | 8 | 4 | 19799.0 |
| 167 | challenging | 1 | correct | 4 | 4 | 1 | 16581.0 |
| 168 | challenging | 1 | correct | 4 | 4 | 1 | 14181.0 |
| 170 | moderate | 1 | correct | 4 | 4 | 1 | 11494.0 |
| 185 | challenging | 1 | correct | 4 | 4 | 1 | 13419.0 |
| 187 | challenging | 0 | incorrect_result | 4 | 7 | 1 | 29376.0 |
| 193 | challenging | 1 | correct | 7 | 7 | 4 | 329228.0 |
| 204 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 22103.0 |
| 207 | challenging | 1 | correct | 7 | 11 | 6 | 26934.0 |
| 208 | challenging | 1 | correct | 5 | 9 | 4 | 20549.0 |
| 209 | challenging | 1 | correct | 5 | 11 | 5 | 24162.0 |
| 211 | challenging | 1 | correct | 7 | 11 | 6 | 30270.0 |
| 218 | challenging | 0 | incorrect_result | 7 | 9 | 4 | 30775.0 |
| 221 | challenging | 1 | correct | 8 | 10 | 5 | 39693.0 |
| 233 | challenging | 1 | correct | 12 | 18 | 10 | 68506.0 |
| 239 | challenging | 0 | incorrect_result | 10 | 13 | 7 | 46991.0 |
| 244 | challenging | 1 | correct | 4 | 5 | 1 | 22226.0 |
| 249 | challenging | 1 | correct | 4 | 4 | 1 | 15868.0 |
| 252 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 22565.0 |
| 253 | challenging | 1 | correct | 4 | 5 | 1 | 20989.0 |
| 254 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 22009.0 |
| 256 | challenging | 1 | correct | 4 | 5 | 1 | 19638.0 |
| 262 | challenging | 1 | correct | 4 | 4 | 1 | 13063.0 |
| 264 | challenging | 1 | correct | 5 | 5 | 2 | 20514.0 |
| 284 | challenging | 1 | correct | 6 | 7 | 3 | 24946.0 |
| 289 | challenging | 1 | correct | 6 | 7 | 3 | 25443.0 |
| 293 | challenging | 1 | correct | 4 | 5 | 1 | 14994.0 |
| 298 | challenging | 1 | correct | 5 | 5 | 2 | 20853.0 |
| 299 | moderate | 1 | correct | 6 | 10 | 6 | 31287.0 |
| 303 | challenging | 0 | incorrect_result | 9 | 9 | 6 | 35660.0 |
| 304 | challenging | 1 | correct | 5 | 8 | 3 | 23890.0 |
| 307 | challenging | 0 | incorrect_result | 6 | 7 | 2 | 20323.0 |
| 317 | challenging | 1 | correct | 6 | 7 | 3 | 27001.0 |
| 326 | challenging | 0 | incorrect_result | 5 | 6 | 3 | 24450.0 |
| 338 | moderate | 0 | incorrect_result | 6 | 7 | 3 | 26593.0 |
| 343 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 23853.0 |
| 346 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 13591.0 |
| 349 | challenging | 0 | incorrect_result | 5 | 9 | 3 | 27200.0 |
| 353 | challenging | 0 | incorrect_result | 14 | 22 | 14 | 58521.0 |
| 362 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 25432.0 |
| 369 | challenging | 0 | incorrect_result | 5 | 11 | 5 | 25702.0 |
| 372 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 15171.0 |
| 373 | challenging | 0 | incorrect_result | 8 | 10 | 5 | 30729.0 |
| 375 | challenging | 1 | correct | 6 | 6 | 3 | 22715.0 |
| 382 | challenging | 1 | correct | 4 | 5 | 1 | 14855.0 |
| 385 | challenging | 1 | correct | 4 | 5 | 1 | 16155.0 |
| 386 | challenging | 1 | correct | 6 | 8 | 4 | 28403.0 |
| 387 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 22404.0 |
| 388 | moderate | 1 | correct | 5 | 6 | 2 | 19378.0 |
| 396 | challenging | 1 | correct | 6 | 8 | 4 | 24884.0 |
| 399 | challenging | 1 | correct | 7 | 8 | 4 | 26127.0 |
| 403 | challenging | 1 | correct | 4 | 4 | 1 | 15909.0 |
| 404 | challenging | 0 | missing_sql | 29 | 41 | 37 | 136899.0 |
| 414 | challenging | 1 | correct | 9 | 10 | 6 | 36473.0 |
| 419 | challenging | 1 | correct | 5 | 6 | 2 | 26440.0 |
| 436 | challenging | 1 | correct | 7 | 8 | 4 | 24544.0 |
| 449 | challenging | 1 | correct | 6 | 7 | 3 | 32079.0 |
| 451 | challenging | 1 | correct | 5 | 6 | 2 | 16087.0 |
| 452 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 28268.0 |
| 455 | challenging | 1 | correct | 5 | 6 | 2 | 23812.0 |
| 456 | challenging | 0 | incorrect_result | 6 | 6 | 3 | 23229.0 |
| 463 | challenging | 1 | correct | 4 | 5 | 1 | 16118.0 |
| 474 | moderate | 0 | incorrect_result | 6 | 7 | 1 | 25800.0 |
| 475 | challenging | 1 | correct | 7 | 9 | 2 | 29217.0 |
| 479 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 26582.0 |
| 484 | challenging | 1 | correct | 5 | 10 | 4 | 24796.0 |
| 490 | challenging | 1 | correct | 5 | 8 | 2 | 25485.0 |
| 493 | challenging | 0 | incorrect_result | 6 | 9 | 4 | 24546.0 |
| 495 | challenging | 1 | correct | 6 | 9 | 3 | 22289.0 |

Times are milliseconds. Model turns represent observable main-agent model calls.
Cached input tokens are part of input tokens; reasoning tokens are part of output tokens.
Optional usage fields may be partial: compare *_observed_calls with model_calls.
Thinking/effort values are reported only when a provider supplies them.
Nested subagent activity may be unobserved. n/a does not mean zero.
Agent SQL tool success is not equivalent to final SQL EX.
Gold SQL is validated separately before any predicted SQL scoring.
