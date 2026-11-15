# B0 Evaluation Report

Split: dev (selected subset, NOT full-split or hidden-test EX)
Questions: 400
EX: **235/400 (58.75%)**

## Accuracy by difficulty

| Difficulty | Correct | Total | EX |
|---|---:|---:|---:|
| challenging | 213 | 369 | 57.72% |
| moderate | 17 | 24 | 70.83% |
| simple | 5 | 7 | 71.43% |

## Inference and SQL execution

| Metric | Total | Mean | P50 | P95 | Observed |
|---|---:|---:|---:|---:|---:|
| tool_calls | 2549.00 | 6.37 | 6.00 | 11.00 | 400 |
| model_calls | 2255.00 | 5.64 | 5.00 | 10.00 | 400 |
| sql_calls | 1021.00 | 2.55 | 2.00 | 7.00 | 400 |
| sql_success_calls | 1008.00 | 2.52 | 2.00 | 7.00 | 400 |
| sql_error_calls | 13.00 | 0.03 | 0.00 | 0.00 | 400 |
| sql_truncated_calls | 118.00 | 0.29 | 0.00 | 2.00 | 400 |
| input_tokens | 8286371.00 | 20715.93 | 16772.50 | 48119.00 | 400 |
| output_tokens | 173370.00 | 433.43 | 370.00 | 921.00 | 400 |
| total_tokens | 8459741.00 | 21149.35 | 17143.50 | 48859.00 | 400 |
| cached_input_tokens | 4419328.00 | 11048.32 | 9856.00 | 21760.00 | 400 |
| reasoning_tokens | 0.00 | 0.00 | 0.00 | 0.00 | 400 |
| input_tokens_observed_calls | 2255.00 | 5.64 | 5.00 | 10.00 | 400 |
| output_tokens_observed_calls | 2255.00 | 5.64 | 5.00 | 10.00 | 400 |
| total_tokens_observed_calls | 2255.00 | 5.64 | 5.00 | 10.00 | 400 |
| cached_input_tokens_observed_calls | 2255.00 | 5.64 | 5.00 | 10.00 | 400 |
| reasoning_tokens_observed_calls | 2255.00 | 5.64 | 5.00 | 10.00 | 400 |
| latency_ms | 8775741.00 | 21939.35 | 18785.00 | 41687.00 | 400 |
| sql_execution_ms | 211861.82 | 529.65 | 4.45 | 558.25 | 400 |
| gold_sql_execution_ms | 36633.23 | 91.58 | 5.01 | 458.05 | 400 |
| agent_sql_execution_ms | 216710.38 | 543.13 | 10.71 | 719.93 | 399 |
| sql_tool_success_rate | 0.9872673849167483 | — | — | — | — |
| final_sql_generation_rate | 1.0 | — | — | — | — |
| final_sql_execution_rate | 0.995 | — | — | — | — |

## Per-question scores

| Question | Difficulty | EX | Status | Model turns | Tool calls | Agent SQL calls | Inference ms |
|---|---|---:|---|---:|---:|---:|---:|
| 1 | challenging | 1 | correct | 5 | 5 | 2 | 26798.0 |
| 2 | moderate | 0 | incorrect_result | 7 | 6 | 3 | 23524.0 |
| 3 | moderate | 1 | correct | 4 | 3 | 1 | 12375.0 |
| 4 | simple | 0 | incorrect_result | 4 | 4 | 1 | 13526.0 |
| 5 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 11946.0 |
| 6 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 11605.0 |
| 7 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 12678.0 |
| 8 | challenging | 1 | correct | 9 | 8 | 6 | 39004.0 |
| 9 | challenging | 1 | correct | 7 | 7 | 4 | 39072.0 |
| 10 | challenging | 1 | correct | 6 | 6 | 3 | 22536.0 |
| 11 | challenging | 1 | correct | 6 | 6 | 3 | 25590.0 |
| 12 | challenging | 1 | correct | 9 | 10 | 6 | 37936.0 |
| 13 | challenging | 1 | correct | 7 | 7 | 4 | 25019.0 |
| 14 | challenging | 1 | correct | 7 | 6 | 3 | 21858.0 |
| 16 | challenging | 1 | correct | 6 | 6 | 3 | 23283.0 |
| 17 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 12674.0 |
| 18 | challenging | 1 | correct | 7 | 7 | 4 | 26107.0 |
| 19 | challenging | 0 | incorrect_result | 5 | 4 | 2 | 18359.0 |
| 20 | challenging | 1 | correct | 9 | 10 | 6 | 52996.0 |
| 21 | challenging | 0 | incorrect_result | 11 | 11 | 8 | 44452.0 |
| 23 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 22240.0 |
| 24 | challenging | 0 | incorrect_result | 7 | 6 | 4 | 23563.0 |
| 25 | challenging | 1 | correct | 6 | 7 | 3 | 21529.0 |
| 26 | challenging | 0 | incorrect_result | 5 | 7 | 3 | 28438.0 |
| 27 | challenging | 1 | correct | 6 | 7 | 3 | 26855.0 |
| 28 | challenging | 0 | incorrect_result | 12 | 13 | 9 | 61408.0 |
| 29 | challenging | 0 | incorrect_result | 9 | 9 | 6 | 35598.0 |
| 31 | challenging | 1 | correct | 5 | 5 | 1 | 18786.0 |
| 33 | challenging | 0 | incorrect_result | 12 | 12 | 9 | 47681.0 |
| 34 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 13311.0 |
| 36 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 25656.0 |
| 37 | challenging | 1 | correct | 8 | 11 | 7 | 36727.0 |
| 38 | challenging | 1 | correct | 5 | 6 | 2 | 29318.0 |
| 39 | challenging | 1 | correct | 6 | 6 | 4 | 22079.0 |
| 41 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 18280.0 |
| 42 | challenging | 1 | correct | 4 | 4 | 1 | 13838.0 |
| 44 | challenging | 0 | incorrect_result | 23 | 23 | 20 | 83484.0 |
| 45 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 14127.0 |
| 47 | challenging | 1 | correct | 7 | 7 | 4 | 22847.0 |
| 48 | challenging | 1 | correct | 11 | 13 | 9 | 45948.0 |
| 50 | moderate | 1 | correct | 5 | 4 | 1 | 16739.0 |
| 51 | moderate | 1 | correct | 7 | 6 | 3 | 19448.0 |
| 52 | simple | 0 | incorrect_result | 4 | 3 | 1 | 9608.0 |
| 53 | challenging | 1 | correct | 7 | 6 | 3 | 25396.0 |
| 54 | simple | 1 | correct | 5 | 4 | 2 | 12932.0 |
| 55 | simple | 1 | correct | 5 | 5 | 2 | 75851.0 |
| 56 | moderate | 1 | correct | 4 | 4 | 1 | 12218.0 |
| 57 | challenging | 1 | correct | 5 | 4 | 1 | 17650.0 |
| 61 | moderate | 1 | correct | 7 | 6 | 3 | 22426.0 |
| 62 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 19593.0 |
| 64 | challenging | 1 | correct | 4 | 3 | 1 | 11149.0 |
| 65 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 15679.0 |
| 66 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 24293.0 |
| 67 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 15142.0 |
| 68 | challenging | 1 | correct | 4 | 3 | 1 | 13801.0 |
| 69 | challenging | 0 | incorrect_result | 4 | 3 | 1 | 13643.0 |
| 70 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 18209.0 |
| 71 | challenging | 1 | correct | 5 | 4 | 1 | 20478.0 |
| 72 | challenging | 0 | incorrect_result | 4 | 3 | 1 | 11711.0 |
| 74 | challenging | 1 | correct | 6 | 5 | 3 | 16926.0 |
| 75 | challenging | 1 | correct | 10 | 11 | 7 | 35401.0 |
| 77 | challenging | 1 | correct | 5 | 4 | 2 | 17944.0 |
| 78 | challenging | 0 | incorrect_result | 15 | 15 | 12 | 58992.0 |
| 79 | challenging | 0 | incorrect_result | 9 | 10 | 6 | 64955.0 |
| 80 | challenging | 0 | incorrect_result | 5 | 4 | 2 | 13931.0 |
| 81 | challenging | 1 | correct | 6 | 5 | 3 | 19577.0 |
| 82 | challenging | 0 | incorrect_result | 6 | 5 | 3 | 17857.0 |
| 83 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 12010.0 |
| 84 | challenging | 0 | incorrect_result | 5 | 4 | 2 | 15092.0 |
| 85 | challenging | 1 | correct | 6 | 5 | 2 | 22434.0 |
| 86 | challenging | 0 | incorrect_result | 10 | 9 | 7 | 36169.0 |
| 88 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 23715.0 |
| 89 | challenging | 1 | correct | 6 | 5 | 2 | 17414.0 |
| 90 | challenging | 0 | incorrect_result | 4 | 3 | 1 | 14179.0 |
| 92 | challenging | 1 | correct | 4 | 3 | 1 | 12772.0 |
| 93 | challenging | 1 | correct | 5 | 4 | 1 | 19789.0 |
| 94 | challenging | 1 | correct | 7 | 7 | 4 | 27178.0 |
| 95 | challenging | 1 | correct | 9 | 10 | 6 | 54085.0 |
| 96 | challenging | 0 | incorrect_result | 7 | 6 | 4 | 21437.0 |
| 98 | challenging | 1 | correct | 7 | 6 | 3 | 23113.0 |
| 99 | challenging | 1 | correct | 6 | 6 | 3 | 22944.0 |
| 100 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 19514.0 |
| 101 | challenging | 1 | correct | 5 | 5 | 2 | 17093.0 |
| 102 | challenging | 1 | correct | 11 | 10 | 7 | 39474.0 |
| 103 | challenging | 1 | correct | 4 | 4 | 1 | 14620.0 |
| 104 | challenging | 1 | correct | 8 | 7 | 5 | 25157.0 |
| 105 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 14611.0 |
| 106 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 28283.0 |
| 108 | challenging | 1 | correct | 5 | 7 | 2 | 23917.0 |
| 109 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 14345.0 |
| 110 | challenging | 1 | correct | 6 | 5 | 2 | 22030.0 |
| 112 | challenging | 1 | correct | 4 | 4 | 1 | 13224.0 |
| 114 | challenging | 1 | correct | 5 | 4 | 1 | 15187.0 |
| 115 | challenging | 0 | incorrect_result | 11 | 10 | 6 | 41174.0 |
| 116 | challenging | 1 | correct | 5 | 4 | 1 | 14397.0 |
| 118 | moderate | 1 | correct | 4 | 5 | 1 | 15123.0 |
| 120 | challenging | 0 | incorrect_result | 4 | 3 | 1 | 15978.0 |
| 121 | challenging | 1 | correct | 5 | 5 | 1 | 15826.0 |
| 122 | moderate | 1 | correct | 4 | 4 | 1 | 12451.0 |
| 123 | moderate | 1 | correct | 5 | 4 | 1 | 13032.0 |
| 124 | moderate | 1 | correct | 4 | 5 | 1 | 14353.0 |
| 125 | challenging | 1 | correct | 4 | 4 | 1 | 16090.0 |
| 126 | simple | 1 | correct | 5 | 4 | 1 | 15099.0 |
| 127 | challenging | 1 | correct | 4 | 4 | 1 | 12928.0 |
| 128 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 14124.0 |
| 129 | challenging | 1 | correct | 4 | 4 | 1 | 16800.0 |
| 130 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 16613.0 |
| 131 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 17419.0 |
| 133 | challenging | 1 | correct | 4 | 5 | 1 | 12289.0 |
| 134 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 13717.0 |
| 136 | challenging | 1 | correct | 4 | 4 | 1 | 18152.0 |
| 138 | challenging | 1 | correct | 7 | 7 | 4 | 28264.0 |
| 139 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 12142.0 |
| 140 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 16681.0 |
| 142 | challenging | 0 | incorrect_result | 4 | 3 | 1 | 10280.0 |
| 143 | challenging | 1 | correct | 4 | 4 | 1 | 14146.0 |
| 145 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 20485.0 |
| 146 | challenging | 1 | correct | 4 | 4 | 1 | 17253.0 |
| 147 | challenging | 1 | correct | 4 | 4 | 1 | 13888.0 |
| 148 | challenging | 1 | correct | 7 | 8 | 4 | 25670.0 |
| 150 | challenging | 1 | correct | 6 | 7 | 3 | 26233.0 |
| 151 | challenging | 1 | correct | 8 | 9 | 5 | 27589.0 |
| 152 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 17916.0 |
| 153 | challenging | 0 | incorrect_result | 5 | 7 | 3 | 18183.0 |
| 154 | challenging | 1 | correct | 6 | 7 | 3 | 20387.0 |
| 155 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15568.0 |
| 156 | challenging | 1 | correct | 7 | 9 | 4 | 23709.0 |
| 157 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 22654.0 |
| 158 | challenging | 1 | correct | 5 | 6 | 2 | 19636.0 |
| 161 | challenging | 1 | correct | 5 | 7 | 2 | 20321.0 |
| 162 | challenging | 0 | incorrect_result | 5 | 12 | 7 | 19508.0 |
| 163 | challenging | 1 | correct | 4 | 5 | 1 | 16038.0 |
| 164 | challenging | 1 | correct | 5 | 5 | 2 | 19551.0 |
| 165 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 14694.0 |
| 166 | challenging | 1 | correct | 4 | 5 | 1 | 12931.0 |
| 169 | challenging | 1 | correct | 5 | 5 | 2 | 23826.0 |
| 171 | moderate | 1 | correct | 4 | 4 | 1 | 128998.0 |
| 172 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 12065.0 |
| 173 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 17224.0 |
| 174 | challenging | 1 | correct | 4 | 5 | 1 | 35610.0 |
| 175 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15306.0 |
| 176 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 22179.0 |
| 177 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 19789.0 |
| 178 | challenging | 1 | correct | 5 | 4 | 1 | 17262.0 |
| 179 | challenging | 1 | correct | 4 | 4 | 1 | 35889.0 |
| 180 | challenging | 1 | correct | 5 | 7 | 2 | 17006.0 |
| 181 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 20842.0 |
| 182 | challenging | 1 | correct | 4 | 4 | 1 | 24398.0 |
| 183 | challenging | 1 | correct | 4 | 7 | 1 | 29995.0 |
| 184 | challenging | 1 | correct | 5 | 6 | 1 | 32227.0 |
| 186 | challenging | 1 | correct | 4 | 4 | 1 | 14246.0 |
| 188 | challenging | 1 | correct | 4 | 4 | 1 | 16485.0 |
| 189 | challenging | 0 | incorrect_result | 4 | 3 | 1 | 14951.0 |
| 190 | challenging | 1 | correct | 4 | 4 | 1 | 21401.0 |
| 191 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 14477.0 |
| 192 | challenging | 1 | correct | 5 | 6 | 2 | 21130.0 |
| 194 | challenging | 1 | correct | 8 | 10 | 5 | 24817.0 |
| 195 | simple | 1 | correct | 4 | 6 | 1 | 15090.0 |
| 196 | challenging | 1 | correct | 6 | 6 | 3 | 21003.0 |
| 197 | challenging | 1 | correct | 5 | 8 | 4 | 23267.0 |
| 198 | moderate | 1 | correct | 6 | 6 | 3 | 19612.0 |
| 199 | challenging | 1 | correct | 5 | 7 | 2 | 15831.0 |
| 200 | challenging | 1 | correct | 5 | 6 | 2 | 21825.0 |
| 201 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 19040.0 |
| 202 | challenging | 1 | correct | 5 | 5 | 2 | 14743.0 |
| 203 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 16328.0 |
| 205 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 18788.0 |
| 206 | challenging | 1 | correct | 5 | 5 | 1 | 17325.0 |
| 210 | challenging | 1 | correct | 4 | 5 | 1 | 16235.0 |
| 212 | challenging | 1 | correct | 6 | 10 | 3 | 25815.0 |
| 213 | challenging | 0 | incorrect_result | 4 | 8 | 1 | 25101.0 |
| 214 | challenging | 0 | incorrect_result | 8 | 11 | 5 | 41687.0 |
| 215 | challenging | 1 | correct | 6 | 7 | 3 | 23526.0 |
| 216 | challenging | 0 | incorrect_result | 5 | 9 | 2 | 23356.0 |
| 217 | challenging | 0 | incorrect_result | 10 | 11 | 7 | 42581.0 |
| 219 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 29365.0 |
| 220 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 18177.0 |
| 222 | challenging | 0 | incorrect_result | 7 | 11 | 4 | 45440.0 |
| 223 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 22903.0 |
| 224 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 26112.0 |
| 225 | challenging | 1 | correct | 6 | 10 | 3 | 32799.0 |
| 226 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 19680.0 |
| 227 | challenging | 0 | incorrect_result | 10 | 12 | 7 | 31411.0 |
| 228 | challenging | 0 | incorrect_result | 5 | 6 | 1 | 14812.0 |
| 229 | challenging | 1 | correct | 6 | 7 | 3 | 21939.0 |
| 230 | challenging | 0 | incorrect_result | 8 | 14 | 7 | 46166.0 |
| 231 | challenging | 0 | incorrect_result | 7 | 8 | 3 | 26757.0 |
| 232 | challenging | 1 | correct | 7 | 7 | 4 | 25704.0 |
| 234 | challenging | 1 | correct | 12 | 17 | 9 | 61218.0 |
| 235 | challenging | 0 | incorrect_result | 5 | 8 | 1 | 20645.0 |
| 236 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 21855.0 |
| 237 | challenging | 1 | correct | 5 | 5 | 2 | 15498.0 |
| 238 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 18784.0 |
| 240 | challenging | 1 | correct | 5 | 6 | 2 | 21529.0 |
| 241 | challenging | 1 | correct | 4 | 5 | 1 | 14355.0 |
| 242 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 16275.0 |
| 243 | challenging | 1 | correct | 7 | 7 | 4 | 20450.0 |
| 245 | challenging | 0 | incorrect_result | 8 | 8 | 5 | 28814.0 |
| 246 | challenging | 1 | correct | 4 | 5 | 1 | 15602.0 |
| 247 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 18421.0 |
| 248 | challenging | 1 | correct | 4 | 6 | 1 | 15107.0 |
| 250 | challenging | 1 | correct | 5 | 6 | 2 | 20165.0 |
| 251 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 16518.0 |
| 255 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 14884.0 |
| 257 | challenging | 1 | correct | 5 | 7 | 2 | 18174.0 |
| 258 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 19040.0 |
| 259 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 18442.0 |
| 260 | challenging | 1 | correct | 7 | 8 | 4 | 26312.0 |
| 261 | challenging | 1 | correct | 4 | 5 | 1 | 16705.0 |
| 263 | challenging | 1 | correct | 4 | 5 | 1 | 17434.0 |
| 265 | challenging | 1 | correct | 4 | 4 | 1 | 16079.0 |
| 266 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 14262.0 |
| 267 | challenging | 1 | correct | 8 | 11 | 5 | 33889.0 |
| 268 | challenging | 1 | correct | 4 | 5 | 1 | 14167.0 |
| 269 | challenging | 1 | correct | 5 | 6 | 2 | 25796.0 |
| 270 | challenging | 1 | correct | 4 | 5 | 1 | 15177.0 |
| 271 | challenging | 1 | correct | 4 | 5 | 1 | 14460.0 |
| 272 | challenging | 1 | correct | 4 | 6 | 1 | 20360.0 |
| 273 | challenging | 1 | correct | 4 | 4 | 1 | 15259.0 |
| 274 | challenging | 1 | correct | 5 | 5 | 2 | 20688.0 |
| 275 | challenging | 1 | correct | 5 | 5 | 2 | 15644.0 |
| 276 | challenging | 1 | correct | 6 | 8 | 3 | 22773.0 |
| 277 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15241.0 |
| 278 | challenging | 1 | correct | 4 | 6 | 1 | 17588.0 |
| 279 | challenging | 1 | correct | 4 | 5 | 1 | 22534.0 |
| 280 | challenging | 1 | correct | 5 | 7 | 2 | 17278.0 |
| 281 | challenging | 1 | correct | 5 | 7 | 2 | 18390.0 |
| 282 | challenging | 1 | correct | 4 | 5 | 1 | 15093.0 |
| 283 | challenging | 1 | correct | 5 | 6 | 2 | 22043.0 |
| 285 | challenging | 1 | correct | 6 | 7 | 3 | 26395.0 |
| 286 | challenging | 1 | correct | 6 | 7 | 3 | 20961.0 |
| 287 | challenging | 1 | correct | 4 | 5 | 1 | 12609.0 |
| 288 | challenging | 1 | correct | 4 | 6 | 1 | 15410.0 |
| 290 | challenging | 0 | incorrect_result | 7 | 7 | 4 | 24608.0 |
| 291 | challenging | 1 | correct | 4 | 4 | 1 | 15618.0 |
| 292 | challenging | 1 | correct | 4 | 5 | 1 | 13247.0 |
| 294 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 23251.0 |
| 295 | challenging | 1 | correct | 6 | 7 | 2 | 20511.0 |
| 296 | moderate | 1 | correct | 10 | 11 | 6 | 33424.0 |
| 297 | simple | 1 | correct | 4 | 4 | 1 | 12327.0 |
| 300 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 12671.0 |
| 301 | challenging | 1 | correct | 4 | 4 | 1 | 12175.0 |
| 302 | challenging | 1 | correct | 7 | 9 | 6 | 30115.0 |
| 305 | challenging | 1 | correct | 7 | 12 | 6 | 28673.0 |
| 306 | challenging | 1 | correct | 5 | 6 | 2 | 21676.0 |
| 308 | challenging | 1 | correct | 5 | 5 | 1 | 18173.0 |
| 309 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 20197.0 |
| 310 | challenging | 1 | correct | 4 | 4 | 1 | 12474.0 |
| 311 | challenging | 1 | correct | 4 | 6 | 1 | 16755.0 |
| 312 | challenging | 1 | correct | 4 | 4 | 1 | 13397.0 |
| 313 | challenging | 1 | correct | 6 | 5 | 1 | 18591.0 |
| 314 | challenging | 1 | correct | 7 | 8 | 4 | 26042.0 |
| 315 | challenging | 1 | correct | 9 | 10 | 5 | 36042.0 |
| 316 | challenging | 1 | correct | 4 | 4 | 1 | 14717.0 |
| 318 | challenging | 1 | correct | 6 | 6 | 3 | 18244.0 |
| 319 | challenging | 1 | correct | 4 | 5 | 1 | 12213.0 |
| 320 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 14671.0 |
| 321 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 13417.0 |
| 322 | challenging | 1 | correct | 4 | 5 | 1 | 18197.0 |
| 323 | challenging | 1 | correct | 4 | 5 | 1 | 12471.0 |
| 324 | challenging | 1 | correct | 7 | 8 | 3 | 31360.0 |
| 325 | challenging | 0 | sql_error | 4 | 5 | 1 | 15454.0 |
| 327 | challenging | 0 | sql_error | 6 | 9 | 3 | 24285.0 |
| 328 | challenging | 1 | correct | 4 | 5 | 1 | 14186.0 |
| 329 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 12115.0 |
| 330 | challenging | 1 | correct | 5 | 5 | 2 | 25491.0 |
| 331 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 11875.0 |
| 332 | moderate | 0 | incorrect_result | 8 | 10 | 3 | 25430.0 |
| 333 | challenging | 1 | correct | 4 | 6 | 1 | 13666.0 |
| 334 | challenging | 1 | correct | 4 | 5 | 1 | 14207.0 |
| 335 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 13096.0 |
| 336 | moderate | 1 | correct | 11 | 11 | 8 | 39981.0 |
| 337 | challenging | 1 | correct | 5 | 4 | 1 | 14482.0 |
| 339 | challenging | 0 | incorrect_result | 4 | 7 | 1 | 15951.0 |
| 340 | challenging | 1 | correct | 5 | 8 | 2 | 17241.0 |
| 341 | challenging | 1 | correct | 4 | 5 | 1 | 15413.0 |
| 342 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 20268.0 |
| 344 | challenging | 1 | correct | 5 | 6 | 2 | 23065.0 |
| 345 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 14394.0 |
| 347 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 25061.0 |
| 348 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 20850.0 |
| 350 | challenging | 0 | incorrect_result | 8 | 8 | 4 | 26748.0 |
| 351 | challenging | 1 | correct | 4 | 5 | 1 | 13489.0 |
| 352 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 13650.0 |
| 354 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 18036.0 |
| 355 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 19138.0 |
| 356 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 12090.0 |
| 357 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 17935.0 |
| 358 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 13190.0 |
| 359 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 13920.0 |
| 360 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 15111.0 |
| 361 | challenging | 1 | correct | 5 | 6 | 2 | 16134.0 |
| 363 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15808.0 |
| 364 | challenging | 1 | correct | 7 | 10 | 4 | 26466.0 |
| 365 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 15151.0 |
| 366 | challenging | 0 | incorrect_result | 5 | 5 | 1 | 16266.0 |
| 367 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 17486.0 |
| 368 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 14800.0 |
| 370 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 12672.0 |
| 371 | challenging | 0 | incorrect_result | 6 | 9 | 3 | 20366.0 |
| 374 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 14552.0 |
| 376 | challenging | 1 | correct | 8 | 10 | 6 | 32570.0 |
| 377 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15581.0 |
| 378 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 17240.0 |
| 379 | challenging | 0 | incorrect_result | 4 | 7 | 1 | 14961.0 |
| 380 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 25138.0 |
| 381 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 13412.0 |
| 383 | moderate | 1 | correct | 4 | 5 | 1 | 14362.0 |
| 384 | moderate | 1 | correct | 4 | 5 | 1 | 16356.0 |
| 389 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 18155.0 |
| 390 | challenging | 1 | correct | 9 | 10 | 6 | 29010.0 |
| 391 | challenging | 1 | correct | 5 | 6 | 2 | 19228.0 |
| 392 | challenging | 1 | correct | 11 | 12 | 8 | 38751.0 |
| 393 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 26511.0 |
| 394 | challenging | 1 | correct | 8 | 9 | 5 | 24664.0 |
| 395 | challenging | 1 | correct | 4 | 5 | 1 | 15717.0 |
| 397 | challenging | 1 | correct | 4 | 5 | 1 | 11318.0 |
| 398 | challenging | 0 | incorrect_result | 12 | 13 | 9 | 37999.0 |
| 400 | challenging | 0 | incorrect_result | 10 | 10 | 6 | 36685.0 |
| 401 | challenging | 1 | correct | 7 | 8 | 4 | 22179.0 |
| 402 | challenging | 1 | correct | 7 | 8 | 4 | 21256.0 |
| 405 | challenging | 1 | correct | 6 | 7 | 3 | 17965.0 |
| 406 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 20109.0 |
| 407 | challenging | 1 | correct | 5 | 6 | 2 | 16655.0 |
| 408 | challenging | 1 | correct | 6 | 7 | 3 | 17731.0 |
| 409 | challenging | 1 | correct | 7 | 8 | 4 | 21750.0 |
| 410 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 16653.0 |
| 411 | challenging | 0 | incorrect_result | 8 | 9 | 5 | 25267.0 |
| 412 | challenging | 0 | incorrect_result | 16 | 16 | 12 | 50105.0 |
| 413 | challenging | 1 | correct | 4 | 5 | 1 | 13335.0 |
| 415 | challenging | 1 | correct | 4 | 5 | 1 | 13004.0 |
| 416 | challenging | 1 | correct | 3 | 3 | 0 | 10065.0 |
| 417 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 17267.0 |
| 418 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 21334.0 |
| 420 | challenging | 0 | incorrect_result | 8 | 9 | 5 | 34790.0 |
| 421 | challenging | 1 | correct | 16 | 17 | 13 | 57312.0 |
| 422 | challenging | 1 | correct | 4 | 4 | 1 | 16262.0 |
| 423 | challenging | 0 | incorrect_result | 6 | 5 | 3 | 19149.0 |
| 424 | challenging | 1 | correct | 5 | 6 | 2 | 14801.0 |
| 425 | challenging | 1 | correct | 4 | 5 | 1 | 12771.0 |
| 426 | challenging | 1 | correct | 6 | 7 | 3 | 17406.0 |
| 427 | challenging | 1 | correct | 7 | 8 | 5 | 21220.0 |
| 428 | challenging | 1 | correct | 5 | 6 | 2 | 20743.0 |
| 429 | challenging | 1 | correct | 4 | 5 | 1 | 17015.0 |
| 430 | challenging | 0 | incorrect_result | 11 | 12 | 8 | 38471.0 |
| 431 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 19434.0 |
| 432 | challenging | 1 | correct | 4 | 5 | 1 | 15825.0 |
| 433 | challenging | 1 | correct | 8 | 9 | 5 | 28330.0 |
| 434 | challenging | 1 | correct | 5 | 6 | 2 | 16332.0 |
| 435 | challenging | 1 | correct | 5 | 6 | 2 | 20859.0 |
| 437 | challenging | 1 | correct | 4 | 5 | 1 | 12705.0 |
| 438 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 21123.0 |
| 439 | challenging | 0 | incorrect_result | 10 | 11 | 7 | 35238.0 |
| 440 | challenging | 1 | correct | 7 | 8 | 4 | 28816.0 |
| 441 | challenging | 1 | correct | 12 | 13 | 9 | 42797.0 |
| 442 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 21450.0 |
| 443 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15514.0 |
| 444 | challenging | 1 | correct | 7 | 8 | 4 | 26819.0 |
| 445 | challenging | 1 | correct | 7 | 8 | 4 | 23819.0 |
| 446 | challenging | 1 | correct | 6 | 7 | 3 | 18601.0 |
| 447 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 18013.0 |
| 448 | challenging | 1 | correct | 15 | 16 | 12 | 54214.0 |
| 450 | challenging | 1 | correct | 4 | 4 | 1 | 12499.0 |
| 453 | challenging | 1 | correct | 6 | 7 | 3 | 21582.0 |
| 454 | challenging | 1 | correct | 5 | 6 | 2 | 14629.0 |
| 457 | challenging | 1 | correct | 4 | 5 | 1 | 15505.0 |
| 458 | challenging | 1 | correct | 4 | 4 | 1 | 17965.0 |
| 459 | challenging | 1 | correct | 6 | 7 | 3 | 18292.0 |
| 460 | challenging | 1 | correct | 5 | 5 | 2 | 14374.0 |
| 461 | challenging | 1 | correct | 6 | 7 | 3 | 21019.0 |
| 462 | challenging | 1 | correct | 4 | 5 | 1 | 21478.0 |
| 464 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 22998.0 |
| 465 | challenging | 1 | correct | 6 | 7 | 3 | 21636.0 |
| 466 | challenging | 1 | correct | 5 | 6 | 2 | 20481.0 |
| 467 | challenging | 1 | correct | 4 | 5 | 1 | 17223.0 |
| 468 | moderate | 1 | correct | 6 | 8 | 3 | 22170.0 |
| 469 | challenging | 1 | correct | 5 | 5 | 2 | 15295.0 |
| 470 | challenging | 1 | correct | 4 | 5 | 1 | 11687.0 |
| 471 | challenging | 1 | correct | 10 | 11 | 5 | 31854.0 |
| 472 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 14240.0 |
| 473 | challenging | 1 | correct | 4 | 4 | 1 | 13238.0 |
| 476 | moderate | 1 | correct | 6 | 8 | 3 | 17214.0 |
| 477 | challenging | 1 | correct | 6 | 8 | 3 | 21530.0 |
| 478 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 23661.0 |
| 480 | challenging | 0 | incorrect_result | 7 | 9 | 3 | 27826.0 |
| 481 | challenging | 0 | incorrect_result | 6 | 9 | 3 | 27482.0 |
| 482 | challenging | 1 | correct | 6 | 7 | 3 | 20444.0 |
| 483 | challenging | 0 | incorrect_result | 7 | 10 | 4 | 25913.0 |
| 485 | challenging | 1 | correct | 5 | 8 | 2 | 18805.0 |
| 486 | challenging | 1 | correct | 4 | 7 | 1 | 16463.0 |
| 487 | challenging | 0 | incorrect_result | 5 | 9 | 4 | 17005.0 |
| 488 | challenging | 0 | incorrect_result | 6 | 5 | 1 | 17229.0 |
| 489 | challenging | 1 | correct | 6 | 7 | 3 | 22098.0 |
| 491 | challenging | 1 | correct | 8 | 12 | 6 | 35794.0 |
| 492 | challenging | 0 | incorrect_result | 9 | 11 | 5 | 30180.0 |
| 494 | challenging | 0 | incorrect_result | 11 | 14 | 8 | 34578.0 |
| 496 | challenging | 1 | correct | 8 | 11 | 5 | 28559.0 |
| 497 | challenging | 0 | incorrect_result | 7 | 9 | 3 | 57207.0 |
| 498 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 17343.0 |
| 499 | challenging | 0 | incorrect_result | 8 | 10 | 4 | 26765.0 |

Times are milliseconds. Model turns represent observable main-agent model calls.
Cached input tokens are part of input tokens; reasoning tokens are part of output tokens.
Optional usage fields may be partial: compare *_observed_calls with model_calls.
Thinking/effort values are reported only when a provider supplies them.
Nested subagent activity may be unobserved. n/a does not mean zero.
Agent SQL tool success is not equivalent to final SQL EX.
Gold SQL is validated separately before any predicted SQL scoring.
