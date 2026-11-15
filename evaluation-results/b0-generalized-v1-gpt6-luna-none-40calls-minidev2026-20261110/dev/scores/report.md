# B0 Evaluation Report

Split: dev (selected subset, NOT full-split or hidden-test EX)
Questions: 400
EX: **255/400 (63.75%)**

## Accuracy by difficulty

| Difficulty | Correct | Total | EX |
|---|---:|---:|---:|
| challenging | 230 | 369 | 62.33% |
| moderate | 20 | 24 | 83.33% |
| simple | 5 | 7 | 71.43% |

## Inference and SQL execution

| Metric | Total | Mean | P50 | P95 | Observed |
|---|---:|---:|---:|---:|---:|
| tool_calls | 2908.00 | 7.27 | 7.00 | 13.00 | 400 |
| model_calls | 2418.00 | 6.04 | 5.00 | 11.00 | 400 |
| sql_calls | 1330.00 | 3.33 | 3.00 | 8.00 | 400 |
| sql_success_calls | 1292.00 | 3.23 | 3.00 | 8.00 | 400 |
| sql_error_calls | 38.00 | 0.10 | 0.00 | 1.00 | 400 |
| sql_truncated_calls | 144.00 | 0.36 | 0.00 | 2.00 | 400 |
| input_tokens | 10096060.00 | 25240.15 | 20966.00 | 50903.00 | 400 |
| output_tokens | 185130.00 | 462.82 | 390.50 | 1027.00 | 400 |
| total_tokens | 10281190.00 | 25702.97 | 21484.00 | 51933.00 | 400 |
| cached_input_tokens | 5493760.00 | 13734.40 | 12032.00 | 25728.00 | 400 |
| reasoning_tokens | 0.00 | 0.00 | 0.00 | 0.00 | 400 |
| input_tokens_observed_calls | 2418.00 | 6.04 | 5.00 | 11.00 | 400 |
| output_tokens_observed_calls | 2418.00 | 6.04 | 5.00 | 11.00 | 400 |
| total_tokens_observed_calls | 2418.00 | 6.04 | 5.00 | 11.00 | 400 |
| cached_input_tokens_observed_calls | 2418.00 | 6.04 | 5.00 | 11.00 | 400 |
| reasoning_tokens_observed_calls | 2418.00 | 6.04 | 5.00 | 11.00 | 400 |
| latency_ms | 9428838.00 | 23572.10 | 19814.00 | 41719.00 | 400 |
| sql_execution_ms | 151056.70 | 378.59 | 4.97 | 328.54 | 399 |
| gold_sql_execution_ms | 54462.72 | 136.16 | 5.00 | 626.89 | 400 |
| agent_sql_execution_ms | 535774.65 | 1339.44 | 12.33 | 794.09 | 400 |
| sql_tool_success_rate | 0.9714285714285714 | — | — | — | — |
| final_sql_generation_rate | 0.9975 | — | — | — | — |
| final_sql_execution_rate | 0.9949874686716792 | — | — | — | — |

## Per-question scores

| Question | Difficulty | EX | Status | Model turns | Tool calls | Agent SQL calls | Inference ms |
|---|---|---:|---|---:|---:|---:|---:|
| 1 | challenging | 1 | correct | 8 | 10 | 6 | 32833.0 |
| 2 | moderate | 0 | incorrect_result | 7 | 7 | 4 | 22789.0 |
| 3 | moderate | 1 | correct | 5 | 4 | 2 | 15652.0 |
| 4 | simple | 0 | incorrect_result | 4 | 4 | 1 | 12747.0 |
| 5 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 17590.0 |
| 6 | moderate | 0 | incorrect_result | 7 | 8 | 5 | 25923.0 |
| 7 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 13337.0 |
| 8 | challenging | 1 | correct | 7 | 8 | 4 | 29924.0 |
| 9 | challenging | 1 | correct | 7 | 8 | 4 | 25622.0 |
| 10 | challenging | 1 | correct | 6 | 6 | 3 | 20996.0 |
| 11 | challenging | 0 | incorrect_result | 8 | 9 | 5 | 31563.0 |
| 12 | challenging | 0 | incorrect_result | 6 | 9 | 6 | 26974.0 |
| 13 | challenging | 1 | correct | 7 | 8 | 5 | 27208.0 |
| 14 | challenging | 1 | correct | 9 | 9 | 6 | 37871.0 |
| 16 | challenging | 1 | correct | 6 | 7 | 4 | 22264.0 |
| 17 | challenging | 1 | correct | 6 | 6 | 3 | 19928.0 |
| 18 | challenging | 1 | correct | 5 | 5 | 2 | 20947.0 |
| 19 | challenging | 0 | incorrect_result | 5 | 4 | 2 | 19239.0 |
| 20 | challenging | 1 | correct | 11 | 11 | 8 | 64251.0 |
| 21 | challenging | 0 | incorrect_result | 9 | 9 | 6 | 29898.0 |
| 23 | challenging | 1 | correct | 6 | 7 | 3 | 24353.0 |
| 24 | challenging | 0 | incorrect_result | 7 | 7 | 5 | 26413.0 |
| 25 | challenging | 1 | correct | 6 | 7 | 3 | 22969.0 |
| 26 | challenging | 1 | correct | 9 | 10 | 6 | 40844.0 |
| 27 | challenging | 1 | correct | 7 | 8 | 4 | 31663.0 |
| 28 | challenging | 0 | incorrect_result | 7 | 10 | 6 | 29164.0 |
| 29 | challenging | 1 | correct | 7 | 7 | 4 | 25123.0 |
| 31 | challenging | 1 | correct | 5 | 6 | 3 | 17547.0 |
| 33 | challenging | 1 | correct | 7 | 8 | 4 | 24825.0 |
| 34 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 14056.0 |
| 36 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 30268.0 |
| 37 | challenging | 1 | correct | 9 | 15 | 11 | 37466.0 |
| 38 | challenging | 1 | correct | 6 | 7 | 3 | 29564.0 |
| 39 | challenging | 1 | correct | 6 | 5 | 3 | 18543.0 |
| 41 | challenging | 1 | correct | 6 | 6 | 3 | 24749.0 |
| 42 | challenging | 1 | correct | 6 | 7 | 3 | 41709.0 |
| 44 | challenging | 1 | correct | 6 | 7 | 4 | 20849.0 |
| 45 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15090.0 |
| 47 | challenging | 1 | correct | 6 | 7 | 4 | 24018.0 |
| 48 | challenging | 1 | correct | 8 | 9 | 5 | 28797.0 |
| 50 | moderate | 1 | correct | 4 | 4 | 1 | 16213.0 |
| 51 | moderate | 1 | correct | 7 | 6 | 3 | 21345.0 |
| 52 | simple | 0 | incorrect_result | 4 | 3 | 1 | 10388.0 |
| 53 | challenging | 1 | correct | 6 | 7 | 3 | 21626.0 |
| 54 | simple | 1 | correct | 5 | 5 | 2 | 14807.0 |
| 55 | simple | 1 | correct | 5 | 6 | 2 | 15572.0 |
| 56 | moderate | 1 | correct | 5 | 5 | 2 | 17619.0 |
| 57 | challenging | 1 | correct | 5 | 4 | 1 | 15166.0 |
| 61 | moderate | 1 | correct | 9 | 11 | 7 | 31489.0 |
| 62 | challenging | 0 | incorrect_result | 5 | 8 | 4 | 19473.0 |
| 64 | challenging | 1 | correct | 8 | 7 | 4 | 24755.0 |
| 65 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 14142.0 |
| 66 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 24654.0 |
| 67 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 13339.0 |
| 68 | challenging | 1 | correct | 4 | 3 | 1 | 16699.0 |
| 69 | challenging | 0 | incorrect_result | 5 | 4 | 2 | 15867.0 |
| 70 | challenging | 1 | correct | 6 | 6 | 3 | 22781.0 |
| 71 | challenging | 1 | correct | 5 | 4 | 1 | 14804.0 |
| 72 | challenging | 1 | correct | 6 | 5 | 3 | 20386.0 |
| 74 | challenging | 1 | correct | 6 | 6 | 3 | 17589.0 |
| 75 | challenging | 1 | correct | 11 | 12 | 8 | 34355.0 |
| 77 | challenging | 1 | correct | 6 | 5 | 3 | 33535.0 |
| 78 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 18992.0 |
| 79 | challenging | 0 | incorrect_result | 9 | 10 | 6 | 34001.0 |
| 80 | challenging | 0 | incorrect_result | 6 | 5 | 3 | 22785.0 |
| 81 | challenging | 0 | incorrect_result | 8 | 7 | 5 | 29567.0 |
| 82 | challenging | 0 | incorrect_result | 6 | 5 | 3 | 16955.0 |
| 83 | challenging | 1 | correct | 8 | 9 | 6 | 25149.0 |
| 84 | challenging | 0 | incorrect_result | 9 | 8 | 6 | 26405.0 |
| 85 | challenging | 1 | correct | 5 | 5 | 2 | 20582.0 |
| 86 | challenging | 0 | incorrect_result | 10 | 11 | 7 | 43472.0 |
| 88 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 23014.0 |
| 89 | challenging | 1 | correct | 5 | 5 | 2 | 21735.0 |
| 90 | challenging | 1 | correct | 7 | 6 | 3 | 26004.0 |
| 92 | challenging | 0 | incorrect_result | 4 | 3 | 1 | 14124.0 |
| 93 | challenging | 1 | correct | 7 | 6 | 3 | 22714.0 |
| 94 | challenging | 1 | correct | 6 | 7 | 3 | 25025.0 |
| 95 | challenging | 1 | correct | 12 | 11 | 8 | 48051.0 |
| 96 | challenging | 0 | incorrect_result | 5 | 4 | 2 | 16934.0 |
| 98 | challenging | 0 | incorrect_result | 9 | 9 | 6 | 33406.0 |
| 99 | challenging | 1 | correct | 5 | 5 | 2 | 18842.0 |
| 100 | challenging | 1 | correct | 6 | 8 | 3 | 26353.0 |
| 101 | challenging | 1 | correct | 5 | 5 | 2 | 17686.0 |
| 102 | challenging | 0 | incorrect_result | 7 | 7 | 4 | 25203.0 |
| 103 | challenging | 0 | incorrect_result | 8 | 7 | 4 | 26636.0 |
| 104 | challenging | 1 | correct | 6 | 5 | 3 | 19151.0 |
| 105 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 18467.0 |
| 106 | challenging | 1 | correct | 5 | 6 | 2 | 17212.0 |
| 108 | challenging | 0 | incorrect_result | 6 | 8 | 3 | 22101.0 |
| 109 | challenging | 1 | correct | 8 | 9 | 5 | 37743.0 |
| 110 | challenging | 1 | correct | 8 | 7 | 4 | 28633.0 |
| 112 | challenging | 1 | correct | 4 | 4 | 1 | 13899.0 |
| 114 | challenging | 1 | correct | 7 | 6 | 3 | 26006.0 |
| 115 | challenging | 1 | correct | 13 | 14 | 10 | 52826.0 |
| 116 | challenging | 1 | correct | 4 | 5 | 1 | 13237.0 |
| 118 | moderate | 1 | correct | 4 | 5 | 1 | 12406.0 |
| 120 | challenging | 0 | incorrect_result | 6 | 5 | 3 | 21182.0 |
| 121 | challenging | 1 | correct | 6 | 7 | 3 | 20549.0 |
| 122 | moderate | 1 | correct | 5 | 7 | 3 | 18251.0 |
| 123 | moderate | 1 | correct | 4 | 5 | 1 | 12289.0 |
| 124 | moderate | 1 | correct | 5 | 6 | 2 | 18443.0 |
| 125 | challenging | 1 | correct | 4 | 4 | 1 | 14563.0 |
| 126 | simple | 1 | correct | 5 | 5 | 2 | 318708.0 |
| 127 | challenging | 1 | correct | 4 | 4 | 1 | 11798.0 |
| 128 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 15732.0 |
| 129 | challenging | 1 | correct | 4 | 4 | 1 | 17406.0 |
| 130 | challenging | 0 | incorrect_result | 5 | 6 | 3 | 20829.0 |
| 131 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 11607.0 |
| 133 | challenging | 1 | correct | 4 | 5 | 1 | 13336.0 |
| 134 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 16811.0 |
| 136 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 17425.0 |
| 138 | challenging | 1 | correct | 5 | 5 | 3 | 17404.0 |
| 139 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 11586.0 |
| 140 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 12310.0 |
| 142 | challenging | 0 | incorrect_result | 4 | 3 | 1 | 10620.0 |
| 143 | challenging | 1 | correct | 4 | 4 | 1 | 13204.0 |
| 145 | challenging | 0 | incorrect_result | 10 | 11 | 7 | 39833.0 |
| 146 | challenging | 1 | correct | 7 | 7 | 4 | 25303.0 |
| 147 | challenging | 1 | correct | 4 | 4 | 1 | 14988.0 |
| 148 | challenging | 1 | correct | 8 | 9 | 5 | 28476.0 |
| 150 | challenging | 1 | correct | 7 | 9 | 4 | 30022.0 |
| 151 | challenging | 1 | correct | 6 | 9 | 4 | 23703.0 |
| 152 | challenging | 1 | correct | 4 | 8 | 3 | 15318.0 |
| 153 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 25393.0 |
| 154 | challenging | 1 | correct | 5 | 8 | 4 | 18356.0 |
| 155 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 23120.0 |
| 156 | challenging | 1 | correct | 8 | 11 | 6 | 29000.0 |
| 157 | challenging | 0 | incorrect_result | 6 | 10 | 6 | 23016.0 |
| 158 | challenging | 1 | correct | 7 | 9 | 5 | 25821.0 |
| 161 | challenging | 1 | correct | 6 | 7 | 3 | 18690.0 |
| 162 | challenging | 1 | correct | 7 | 16 | 11 | 26767.0 |
| 163 | challenging | 1 | correct | 5 | 6 | 2 | 20260.0 |
| 164 | challenging | 1 | correct | 6 | 7 | 3 | 20042.0 |
| 165 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 14757.0 |
| 166 | challenging | 1 | correct | 4 | 4 | 1 | 11414.0 |
| 169 | challenging | 1 | correct | 4 | 4 | 1 | 14993.0 |
| 171 | moderate | 1 | correct | 5 | 4 | 1 | 210454.0 |
| 172 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15437.0 |
| 173 | challenging | 0 | incorrect_result | 6 | 5 | 2 | 17098.0 |
| 174 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 96735.0 |
| 175 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 13999.0 |
| 176 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 18759.0 |
| 177 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15462.0 |
| 178 | challenging | 1 | correct | 7 | 6 | 3 | 26773.0 |
| 179 | challenging | 1 | correct | 4 | 4 | 1 | 36097.0 |
| 180 | challenging | 1 | correct | 8 | 9 | 5 | 28395.0 |
| 181 | challenging | 1 | correct | 5 | 6 | 2 | 27325.0 |
| 182 | challenging | 1 | correct | 4 | 5 | 1 | 20481.0 |
| 183 | challenging | 1 | correct | 4 | 6 | 1 | 32619.0 |
| 184 | challenging | 1 | correct | 14 | 16 | 11 | 82336.0 |
| 186 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 16227.0 |
| 188 | challenging | 1 | correct | 4 | 3 | 1 | 13946.0 |
| 189 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 16704.0 |
| 190 | challenging | 1 | correct | 4 | 4 | 1 | 38793.0 |
| 191 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 10798.0 |
| 192 | challenging | 1 | correct | 5 | 6 | 2 | 18820.0 |
| 194 | challenging | 0 | incorrect_result | 10 | 12 | 7 | 34134.0 |
| 195 | simple | 1 | correct | 4 | 6 | 1 | 14605.0 |
| 196 | challenging | 1 | correct | 8 | 9 | 5 | 26456.0 |
| 197 | challenging | 1 | correct | 5 | 6 | 2 | 16578.0 |
| 198 | moderate | 1 | correct | 6 | 7 | 3 | 20397.0 |
| 199 | challenging | 1 | correct | 6 | 8 | 3 | 22142.0 |
| 200 | challenging | 1 | correct | 7 | 8 | 3 | 20053.0 |
| 201 | challenging | 0 | incorrect_result | 5 | 8 | 3 | 20953.0 |
| 202 | challenging | 1 | correct | 4 | 7 | 3 | 14977.0 |
| 203 | challenging | 1 | correct | 6 | 6 | 3 | 21082.0 |
| 205 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 22901.0 |
| 206 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 21318.0 |
| 210 | challenging | 1 | correct | 4 | 6 | 1 | 16387.0 |
| 212 | challenging | 0 | incorrect_result | 5 | 11 | 4 | 24636.0 |
| 213 | challenging | 1 | correct | 6 | 16 | 8 | 33171.0 |
| 214 | challenging | 0 | incorrect_result | 10 | 13 | 7 | 45473.0 |
| 215 | challenging | 1 | correct | 6 | 7 | 3 | 21895.0 |
| 216 | challenging | 0 | incorrect_result | 8 | 12 | 5 | 30941.0 |
| 217 | challenging | 0 | incorrect_result | 19 | 21 | 15 | 69695.0 |
| 219 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 30672.0 |
| 220 | challenging | 0 | incorrect_result | 5 | 8 | 4 | 23726.0 |
| 222 | challenging | 0 | incorrect_result | 6 | 12 | 5 | 30915.0 |
| 223 | challenging | 1 | correct | 5 | 6 | 2 | 17389.0 |
| 224 | challenging | 1 | correct | 7 | 13 | 6 | 30746.0 |
| 225 | challenging | 1 | correct | 6 | 10 | 3 | 26424.0 |
| 226 | challenging | 0 | incorrect_result | 5 | 7 | 3 | 17847.0 |
| 227 | challenging | 0 | incorrect_result | 12 | 14 | 9 | 38725.0 |
| 228 | challenging | 0 | incorrect_result | 5 | 6 | 1 | 15919.0 |
| 229 | challenging | 1 | correct | 6 | 10 | 5 | 33975.0 |
| 230 | challenging | 0 | incorrect_result | 6 | 10 | 3 | 48019.0 |
| 231 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 23231.0 |
| 232 | challenging | 1 | correct | 6 | 8 | 3 | 22693.0 |
| 234 | challenging | 1 | correct | 7 | 12 | 4 | 34719.0 |
| 235 | challenging | 0 | incorrect_result | 6 | 9 | 2 | 23791.0 |
| 236 | challenging | 1 | correct | 8 | 10 | 4 | 28502.0 |
| 237 | challenging | 1 | correct | 7 | 8 | 4 | 18788.0 |
| 238 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 19772.0 |
| 240 | challenging | 1 | correct | 5 | 5 | 2 | 18034.0 |
| 241 | challenging | 1 | correct | 4 | 5 | 1 | 14264.0 |
| 242 | moderate | 1 | correct | 4 | 5 | 1 | 15652.0 |
| 243 | challenging | 1 | correct | 5 | 7 | 2 | 20646.0 |
| 245 | challenging | 0 | incorrect_result | 8 | 8 | 5 | 28167.0 |
| 246 | challenging | 1 | correct | 4 | 5 | 1 | 13559.0 |
| 247 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 15016.0 |
| 248 | challenging | 1 | correct | 4 | 6 | 1 | 13049.0 |
| 250 | challenging | 1 | correct | 6 | 7 | 3 | 22812.0 |
| 251 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 15545.0 |
| 255 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 74209.0 |
| 257 | challenging | 1 | correct | 4 | 5 | 1 | 18423.0 |
| 258 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 15732.0 |
| 259 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 18588.0 |
| 260 | challenging | 1 | correct | 4 | 5 | 1 | 12756.0 |
| 261 | challenging | 1 | correct | 4 | 5 | 1 | 12649.0 |
| 263 | challenging | 1 | correct | 5 | 6 | 2 | 16791.0 |
| 265 | challenging | 1 | correct | 5 | 6 | 2 | 17619.0 |
| 266 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 15649.0 |
| 267 | challenging | 1 | correct | 11 | 14 | 8 | 42120.0 |
| 268 | challenging | 1 | correct | 5 | 6 | 3 | 22288.0 |
| 269 | challenging | 1 | correct | 5 | 6 | 2 | 20486.0 |
| 270 | challenging | 1 | correct | 5 | 7 | 2 | 17819.0 |
| 271 | challenging | 1 | correct | 5 | 6 | 2 | 17039.0 |
| 272 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 17446.0 |
| 273 | challenging | 1 | correct | 4 | 4 | 1 | 12661.0 |
| 274 | challenging | 1 | correct | 5 | 5 | 2 | 18353.0 |
| 275 | challenging | 1 | correct | 5 | 5 | 2 | 14669.0 |
| 276 | challenging | 1 | correct | 18 | 20 | 15 | 62942.0 |
| 277 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 16623.0 |
| 278 | challenging | 1 | correct | 5 | 7 | 2 | 19856.0 |
| 279 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 19437.0 |
| 280 | challenging | 1 | correct | 5 | 6 | 2 | 18094.0 |
| 281 | challenging | 1 | correct | 5 | 8 | 2 | 34597.0 |
| 282 | challenging | 1 | correct | 5 | 6 | 2 | 18145.0 |
| 283 | challenging | 1 | correct | 5 | 6 | 2 | 16914.0 |
| 285 | challenging | 1 | correct | 4 | 5 | 1 | 14839.0 |
| 286 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 25596.0 |
| 287 | challenging | 1 | correct | 4 | 5 | 1 | 11670.0 |
| 288 | challenging | 1 | correct | 5 | 7 | 2 | 17344.0 |
| 290 | challenging | 1 | correct | 8 | 8 | 5 | 36172.0 |
| 291 | challenging | 1 | correct | 4 | 5 | 1 | 14405.0 |
| 292 | challenging | 1 | correct | 6 | 8 | 4 | 24040.0 |
| 294 | challenging | 1 | correct | 6 | 7 | 3 | 20795.0 |
| 295 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 17717.0 |
| 296 | moderate | 1 | correct | 14 | 15 | 10 | 40923.0 |
| 297 | simple | 1 | correct | 4 | 3 | 1 | 10181.0 |
| 300 | moderate | 1 | correct | 4 | 5 | 1 | 13983.0 |
| 301 | challenging | 1 | correct | 4 | 4 | 1 | 11943.0 |
| 302 | challenging | 1 | correct | 7 | 9 | 6 | 30738.0 |
| 305 | challenging | 1 | correct | 7 | 13 | 7 | 26719.0 |
| 306 | challenging | 0 | incorrect_result | 5 | 7 | 3 | 21110.0 |
| 308 | challenging | 1 | correct | 5 | 5 | 2 | 15043.0 |
| 309 | challenging | 1 | correct | 6 | 7 | 3 | 18608.0 |
| 310 | challenging | 1 | correct | 5 | 6 | 2 | 14138.0 |
| 311 | challenging | 1 | correct | 4 | 6 | 1 | 14985.0 |
| 312 | challenging | 1 | correct | 4 | 4 | 1 | 11828.0 |
| 313 | challenging | 0 | incorrect_result | 8 | 9 | 5 | 28829.0 |
| 314 | challenging | 0 | incorrect_result | 8 | 11 | 7 | 28127.0 |
| 315 | challenging | 1 | correct | 8 | 10 | 4 | 33279.0 |
| 316 | challenging | 1 | correct | 6 | 6 | 3 | 20896.0 |
| 318 | challenging | 1 | correct | 5 | 7 | 3 | 18581.0 |
| 319 | challenging | 1 | correct | 4 | 5 | 1 | 11134.0 |
| 320 | challenging | 1 | correct | 4 | 4 | 1 | 14176.0 |
| 321 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 12754.0 |
| 322 | challenging | 1 | correct | 5 | 6 | 2 | 18123.0 |
| 323 | challenging | 1 | correct | 8 | 9 | 5 | 23531.0 |
| 324 | challenging | 1 | correct | 11 | 12 | 8 | 40020.0 |
| 325 | challenging | 1 | correct | 4 | 5 | 1 | 14596.0 |
| 327 | challenging | 1 | correct | 8 | 12 | 7 | 28426.0 |
| 328 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 13053.0 |
| 329 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 12172.0 |
| 330 | challenging | 1 | correct | 11 | 11 | 7 | 45751.0 |
| 331 | challenging | 1 | correct | 7 | 7 | 4 | 18885.0 |
| 332 | moderate | 1 | correct | 5 | 10 | 4 | 18669.0 |
| 333 | challenging | 1 | correct | 4 | 8 | 3 | 15680.0 |
| 334 | challenging | 1 | correct | 5 | 6 | 2 | 18332.0 |
| 335 | challenging | 1 | correct | 4 | 4 | 1 | 12192.0 |
| 336 | moderate | 1 | correct | 6 | 8 | 3 | 17518.0 |
| 337 | challenging | 1 | correct | 5 | 5 | 2 | 16670.0 |
| 339 | challenging | 1 | correct | 6 | 10 | 4 | 21694.0 |
| 340 | challenging | 1 | correct | 7 | 9 | 4 | 21644.0 |
| 341 | challenging | 1 | correct | 5 | 7 | 3 | 17694.0 |
| 342 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 12743.0 |
| 344 | challenging | 1 | correct | 6 | 7 | 3 | 20781.0 |
| 345 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 11323.0 |
| 347 | challenging | 1 | correct | 7 | 9 | 4 | 24542.0 |
| 348 | challenging | 0 | incorrect_result | 5 | 8 | 4 | 19696.0 |
| 350 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 27161.0 |
| 351 | challenging | 1 | correct | 4 | 5 | 1 | 14994.0 |
| 352 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 14359.0 |
| 354 | challenging | 1 | correct | 5 | 6 | 2 | 18542.0 |
| 355 | challenging | 0 | incorrect_result | 5 | 8 | 4 | 19251.0 |
| 356 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 14202.0 |
| 357 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 24747.0 |
| 358 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 9739.0 |
| 359 | challenging | 1 | correct | 4 | 5 | 1 | 12021.0 |
| 360 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 15201.0 |
| 361 | challenging | 1 | correct | 6 | 7 | 3 | 20201.0 |
| 363 | challenging | 0 | incorrect_result | 6 | 5 | 2 | 13918.0 |
| 364 | challenging | 1 | correct | 8 | 11 | 5 | 24038.0 |
| 365 | challenging | 0 | incorrect_result | 5 | 8 | 3 | 17715.0 |
| 366 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 13758.0 |
| 367 | challenging | 1 | correct | 10 | 10 | 5 | 26839.0 |
| 368 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 17602.0 |
| 370 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 17128.0 |
| 371 | challenging | 0 | incorrect_result | 5 | 7 | 3 | 15537.0 |
| 374 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 19712.0 |
| 376 | challenging | 1 | correct | 6 | 7 | 3 | 19873.0 |
| 377 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 13980.0 |
| 378 | challenging | 1 | correct | 6 | 10 | 5 | 23774.0 |
| 379 | challenging | 0 | incorrect_result | 6 | 11 | 5 | 22044.0 |
| 380 | challenging | 0 | incorrect_result | 5 | 7 | 3 | 16438.0 |
| 381 | challenging | 0 | incorrect_result | 5 | 7 | 3 | 15967.0 |
| 383 | moderate | 1 | correct | 5 | 6 | 2 | 14835.0 |
| 384 | moderate | 1 | correct | 4 | 5 | 1 | 12769.0 |
| 389 | challenging | 1 | correct | 7 | 8 | 4 | 19915.0 |
| 390 | challenging | 1 | correct | 7 | 8 | 4 | 19438.0 |
| 391 | challenging | 1 | correct | 7 | 8 | 4 | 22947.0 |
| 392 | challenging | 0 | incorrect_result | 7 | 11 | 7 | 24027.0 |
| 393 | challenging | 0 | incorrect_result | 7 | 9 | 5 | 26698.0 |
| 394 | challenging | 1 | correct | 6 | 7 | 3 | 18524.0 |
| 395 | challenging | 1 | correct | 4 | 5 | 1 | 13761.0 |
| 397 | challenging | 1 | correct | 7 | 9 | 5 | 20781.0 |
| 398 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 16054.0 |
| 400 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 26777.0 |
| 401 | challenging | 1 | correct | 7 | 8 | 4 | 20408.0 |
| 402 | challenging | 1 | correct | 6 | 7 | 3 | 16968.0 |
| 405 | challenging | 1 | correct | 6 | 9 | 5 | 19028.0 |
| 406 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 15308.0 |
| 407 | challenging | 0 | incorrect_result | 13 | 19 | 15 | 46073.0 |
| 408 | challenging | 1 | correct | 6 | 7 | 3 | 18805.0 |
| 409 | challenging | 1 | correct | 5 | 6 | 3 | 15365.0 |
| 410 | challenging | 1 | correct | 8 | 9 | 5 | 24240.0 |
| 411 | challenging | 1 | correct | 8 | 9 | 5 | 24169.0 |
| 412 | challenging | 0 | incorrect_result | 13 | 19 | 15 | 48153.0 |
| 413 | challenging | 1 | correct | 4 | 5 | 1 | 13974.0 |
| 415 | challenging | 1 | correct | 6 | 7 | 3 | 18740.0 |
| 416 | challenging | 1 | correct | 4 | 4 | 1 | 14997.0 |
| 417 | challenging | 1 | correct | 5 | 8 | 3 | 20021.0 |
| 418 | challenging | 0 | incorrect_result | 7 | 8 | 4 | 27376.0 |
| 420 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 18537.0 |
| 421 | challenging | 0 | incorrect_result | 18 | 19 | 15 | 56898.0 |
| 422 | challenging | 1 | correct | 5 | 7 | 3 | 16838.0 |
| 423 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 20974.0 |
| 424 | challenging | 1 | correct | 7 | 8 | 4 | 21067.0 |
| 425 | challenging | 1 | correct | 5 | 6 | 2 | 13990.0 |
| 426 | challenging | 1 | correct | 6 | 7 | 3 | 17309.0 |
| 427 | challenging | 1 | correct | 6 | 6 | 3 | 21044.0 |
| 428 | challenging | 1 | correct | 6 | 7 | 3 | 19202.0 |
| 429 | challenging | 1 | correct | 5 | 6 | 2 | 17154.0 |
| 430 | challenging | 0 | incorrect_result | 13 | 14 | 10 | 37100.0 |
| 431 | challenging | 1 | correct | 5 | 6 | 2 | 15230.0 |
| 432 | challenging | 1 | correct | 5 | 6 | 2 | 14242.0 |
| 433 | challenging | 1 | correct | 8 | 9 | 5 | 25266.0 |
| 434 | challenging | 1 | correct | 5 | 5 | 2 | 14206.0 |
| 435 | challenging | 1 | correct | 6 | 7 | 3 | 20447.0 |
| 437 | challenging | 1 | correct | 6 | 7 | 3 | 16883.0 |
| 438 | challenging | 1 | correct | 5 | 6 | 2 | 16121.0 |
| 439 | challenging | 0 | incorrect_result | 15 | 16 | 12 | 44880.0 |
| 440 | challenging | 1 | correct | 8 | 11 | 7 | 31397.0 |
| 441 | challenging | 0 | sql_error | 6 | 8 | 4 | 22363.0 |
| 442 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 23147.0 |
| 443 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 13289.0 |
| 444 | challenging | 1 | correct | 5 | 8 | 4 | 22325.0 |
| 445 | challenging | 0 | incorrect_result | 11 | 14 | 10 | 38319.0 |
| 446 | challenging | 1 | correct | 8 | 9 | 5 | 23354.0 |
| 447 | challenging | 1 | correct | 13 | 14 | 10 | 40812.0 |
| 448 | challenging | 0 | incorrect_result | 6 | 9 | 5 | 20756.0 |
| 450 | challenging | 1 | correct | 4 | 4 | 1 | 12562.0 |
| 453 | challenging | 1 | correct | 5 | 6 | 2 | 14641.0 |
| 454 | challenging | 1 | correct | 6 | 7 | 3 | 18731.0 |
| 457 | challenging | 1 | correct | 7 | 8 | 4 | 24534.0 |
| 458 | challenging | 0 | incorrect_result | 6 | 6 | 3 | 17813.0 |
| 459 | challenging | 0 | incorrect_result | 5 | 7 | 3 | 15450.0 |
| 460 | challenging | 1 | correct | 5 | 6 | 3 | 13906.0 |
| 461 | challenging | 1 | correct | 6 | 7 | 3 | 15998.0 |
| 462 | challenging | 1 | correct | 7 | 8 | 4 | 24853.0 |
| 464 | challenging | 0 | incorrect_result | 5 | 6 | 2 | 17608.0 |
| 465 | challenging | 1 | correct | 6 | 9 | 5 | 20938.0 |
| 466 | challenging | 0 | missing_sql | 7 | 8 | 4 | 23310.0 |
| 467 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 23266.0 |
| 468 | moderate | 1 | correct | 6 | 8 | 3 | 17313.0 |
| 469 | challenging | 1 | correct | 5 | 6 | 2 | 14595.0 |
| 470 | challenging | 1 | correct | 4 | 5 | 1 | 12143.0 |
| 471 | challenging | 1 | correct | 9 | 16 | 11 | 35353.0 |
| 472 | challenging | 1 | correct | 5 | 7 | 3 | 20924.0 |
| 473 | challenging | 1 | correct | 4 | 4 | 1 | 13875.0 |
| 476 | moderate | 1 | correct | 5 | 9 | 4 | 15956.0 |
| 477 | challenging | 1 | correct | 5 | 7 | 2 | 17081.0 |
| 478 | challenging | 1 | correct | 4 | 7 | 3 | 11499.0 |
| 480 | challenging | 0 | incorrect_result | 6 | 10 | 3 | 19926.0 |
| 481 | challenging | 0 | incorrect_result | 5 | 10 | 4 | 20974.0 |
| 482 | challenging | 1 | correct | 5 | 6 | 2 | 14408.0 |
| 483 | challenging | 1 | correct | 8 | 13 | 7 | 27374.0 |
| 485 | challenging | 1 | correct | 5 | 9 | 3 | 16048.0 |
| 486 | challenging | 0 | incorrect_result | 7 | 9 | 3 | 21290.0 |
| 487 | challenging | 1 | correct | 5 | 7 | 1 | 17550.0 |
| 488 | challenging | 1 | correct | 5 | 7 | 1 | 15095.0 |
| 489 | challenging | 1 | correct | 5 | 7 | 2 | 17969.0 |
| 491 | challenging | 1 | correct | 11 | 15 | 9 | 47628.0 |
| 492 | challenging | 1 | correct | 9 | 11 | 5 | 26278.0 |
| 494 | challenging | 0 | sql_error | 13 | 17 | 11 | 41719.0 |
| 496 | challenging | 1 | correct | 4 | 6 | 1 | 12882.0 |
| 497 | challenging | 0 | incorrect_result | 8 | 12 | 6 | 26428.0 |
| 498 | challenging | 0 | incorrect_result | 8 | 10 | 3 | 24522.0 |
| 499 | challenging | 0 | incorrect_result | 5 | 8 | 2 | 19703.0 |

Times are milliseconds. Model turns represent observable main-agent model calls.
Cached input tokens are part of input tokens; reasoning tokens are part of output tokens.
Optional usage fields may be partial: compare *_observed_calls with model_calls.
Thinking/effort values are reported only when a provider supplies them.
Nested subagent activity may be unobserved. n/a does not mean zero.
Agent SQL tool success is not equivalent to final SQL EX.
Gold SQL is validated separately before any predicted SQL scoring.
