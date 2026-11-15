# B0 Evaluation Report

Split: dev (selected subset, NOT full-split or hidden-test EX)
Questions: 400
EX: **236/400 (59.00%)**

## Accuracy by difficulty

| Difficulty | Correct | Total | EX |
|---|---:|---:|---:|
| challenging | 42 | 83 | 50.60% |
| moderate | 107 | 200 | 53.50% |
| simple | 87 | 117 | 74.36% |

## Inference and SQL execution

| Metric | Total | Mean | P50 | P95 | Observed |
|---|---:|---:|---:|---:|---:|
| tool_calls | 1946.00 | 4.87 | 5.00 | 8.00 | 400 |
| model_calls | 1897.00 | 4.74 | 4.00 | 7.00 | 400 |
| sql_calls | 578.00 | 1.45 | 1.00 | 3.00 | 400 |
| sql_success_calls | 574.00 | 1.44 | 1.00 | 3.00 | 400 |
| sql_error_calls | 4.00 | 0.01 | 0.00 | 0.00 | 400 |
| sql_truncated_calls | 56.00 | 0.14 | 0.00 | 1.00 | 400 |
| input_tokens | 5910910.00 | 14777.27 | 13373.50 | 24535.00 | 400 |
| output_tokens | 97351.00 | 243.38 | 221.00 | 436.00 | 400 |
| total_tokens | 6008261.00 | 15020.65 | 13573.50 | 24946.00 | 400 |
| cached_input_tokens | 3773440.00 | 9433.60 | 8192.00 | 14336.00 | 400 |
| reasoning_tokens | 0.00 | 0.00 | 0.00 | 0.00 | 400 |
| input_tokens_observed_calls | 1897.00 | 4.74 | 4.00 | 7.00 | 400 |
| output_tokens_observed_calls | 1897.00 | 4.74 | 4.00 | 7.00 | 400 |
| total_tokens_observed_calls | 1897.00 | 4.74 | 4.00 | 7.00 | 400 |
| cached_input_tokens_observed_calls | 1897.00 | 4.74 | 4.00 | 7.00 | 400 |
| reasoning_tokens_observed_calls | 1897.00 | 4.74 | 4.00 | 7.00 | 400 |
| latency_ms | 6735446.00 | 16838.62 | 14904.50 | 29335.00 | 400 |
| sql_execution_ms | 19398.87 | 48.50 | 2.04 | 145.68 | 400 |
| gold_sql_execution_ms | 549609.08 | 1374.02 | 2.46 | 154.38 | 400 |
| agent_sql_execution_ms | 30628.75 | 76.96 | 3.00 | 244.07 | 398 |
| sql_tool_success_rate | 0.9930795847750865 | — | — | — | — |
| final_sql_generation_rate | 1.0 | — | — | — | — |
| final_sql_execution_rate | 1.0 | — | — | — | — |

## Per-question scores

| Question | Difficulty | EX | Status | Model turns | Tool calls | Agent SQL calls | Inference ms |
|---|---|---:|---|---:|---:|---:|---:|
| 5 | simple | 1 | correct | 5 | 4 | 1 | 16013.0 |
| 11 | simple | 1 | correct | 5 | 4 | 1 | 17858.0 |
| 12 | moderate | 1 | correct | 5 | 4 | 1 | 18404.0 |
| 17 | simple | 0 | incorrect_result | 5 | 4 | 1 | 17753.0 |
| 24 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 12604.0 |
| 26 | moderate | 0 | incorrect_result | 5 | 5 | 2 | 20221.0 |
| 27 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 15174.0 |
| 28 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 19869.0 |
| 31 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 14078.0 |
| 32 | moderate | 0 | incorrect_result | 9 | 8 | 4 | 28915.0 |
| 36 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 12936.0 |
| 37 | moderate | 0 | incorrect_result | 5 | 5 | 2 | 16929.0 |
| 40 | moderate | 1 | correct | 4 | 4 | 1 | 16487.0 |
| 45 | moderate | 1 | correct | 4 | 5 | 1 | 15392.0 |
| 46 | simple | 0 | incorrect_result | 6 | 5 | 1 | 18224.0 |
| 47 | moderate | 1 | correct | 4 | 3 | 1 | 12944.0 |
| 48 | moderate | 1 | correct | 5 | 4 | 2 | 20263.0 |
| 50 | simple | 0 | incorrect_result | 5 | 5 | 2 | 16819.0 |
| 62 | challenging | 1 | correct | 5 | 6 | 3 | 17922.0 |
| 72 | moderate | 0 | incorrect_result | 6 | 6 | 2 | 21981.0 |
| 77 | moderate | 1 | correct | 4 | 4 | 1 | 15688.0 |
| 82 | simple | 0 | incorrect_result | 6 | 5 | 3 | 17751.0 |
| 85 | moderate | 1 | correct | 4 | 4 | 1 | 14810.0 |
| 87 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 13532.0 |
| 89 | moderate | 0 | incorrect_result | 17 | 16 | 10 | 56865.0 |
| 93 | moderate | 1 | correct | 7 | 6 | 3 | 22472.0 |
| 94 | challenging | 0 | incorrect_result | 9 | 10 | 5 | 38454.0 |
| 95 | moderate | 0 | incorrect_result | 8 | 10 | 5 | 26917.0 |
| 99 | moderate | 1 | correct | 4 | 4 | 1 | 14245.0 |
| 100 | moderate | 1 | correct | 5 | 8 | 3 | 18869.0 |
| 112 | simple | 1 | correct | 4 | 7 | 1 | 14785.0 |
| 116 | challenging | 1 | correct | 6 | 9 | 3 | 22554.0 |
| 117 | moderate | 1 | correct | 4 | 3 | 1 | 13597.0 |
| 118 | moderate | 0 | incorrect_result | 5 | 4 | 2 | 14037.0 |
| 125 | challenging | 0 | incorrect_result | 7 | 8 | 2 | 20329.0 |
| 128 | moderate | 0 | incorrect_result | 4 | 6 | 1 | 14176.0 |
| 129 | moderate | 0 | incorrect_result | 4 | 6 | 1 | 15759.0 |
| 136 | moderate | 0 | incorrect_result | 6 | 6 | 3 | 22668.0 |
| 137 | moderate | 1 | correct | 4 | 5 | 1 | 15679.0 |
| 138 | moderate | 1 | correct | 5 | 5 | 2 | 15417.0 |
| 145 | moderate | 0 | incorrect_result | 4 | 7 | 1 | 16260.0 |
| 149 | challenging | 1 | correct | 4 | 4 | 0 | 12884.0 |
| 152 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 13602.0 |
| 159 | simple | 0 | incorrect_result | 4 | 5 | 1 | 11989.0 |
| 168 | moderate | 0 | incorrect_result | 5 | 7 | 2 | 18645.0 |
| 169 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 18820.0 |
| 173 | challenging | 0 | incorrect_result | 5 | 6 | 3 | 15101.0 |
| 192 | moderate | 0 | incorrect_result | 8 | 8 | 4 | 24634.0 |
| 194 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 16902.0 |
| 195 | simple | 1 | correct | 4 | 4 | 1 | 11385.0 |
| 197 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 12480.0 |
| 198 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 13667.0 |
| 206 | challenging | 1 | correct | 4 | 5 | 1 | 14008.0 |
| 207 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 12899.0 |
| 208 | moderate | 1 | correct | 5 | 4 | 1 | 15189.0 |
| 212 | challenging | 1 | correct | 4 | 5 | 1 | 13876.0 |
| 213 | moderate | 1 | correct | 5 | 4 | 1 | 18987.0 |
| 215 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 12334.0 |
| 219 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 13169.0 |
| 226 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 11602.0 |
| 227 | simple | 0 | incorrect_result | 4 | 3 | 1 | 13752.0 |
| 228 | moderate | 1 | correct | 4 | 3 | 1 | 11311.0 |
| 231 | challenging | 0 | incorrect_result | 6 | 6 | 2 | 19619.0 |
| 232 | moderate | 1 | correct | 4 | 5 | 1 | 14173.0 |
| 234 | moderate | 0 | incorrect_result | 5 | 5 | 1 | 14839.0 |
| 236 | moderate | 1 | correct | 5 | 7 | 2 | 17224.0 |
| 239 | simple | 1 | correct | 4 | 5 | 1 | 13476.0 |
| 240 | challenging | 1 | correct | 4 | 6 | 1 | 10858.0 |
| 243 | moderate | 1 | correct | 5 | 5 | 1 | 16791.0 |
| 244 | moderate | 0 | incorrect_result | 6 | 6 | 3 | 26762.0 |
| 245 | moderate | 1 | correct | 5 | 5 | 1 | 17741.0 |
| 247 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 11346.0 |
| 248 | simple | 1 | correct | 5 | 6 | 1 | 17576.0 |
| 249 | challenging | 1 | correct | 5 | 5 | 1 | 15950.0 |
| 253 | challenging | 1 | correct | 5 | 5 | 1 | 14929.0 |
| 260 | moderate | 0 | incorrect_result | 4 | 6 | 1 | 13940.0 |
| 263 | challenging | 1 | correct | 4 | 5 | 1 | 12638.0 |
| 268 | challenging | 1 | correct | 6 | 5 | 1 | 16800.0 |
| 273 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 12947.0 |
| 282 | challenging | 1 | correct | 4 | 4 | 1 | 11898.0 |
| 327 | moderate | 1 | correct | 4 | 6 | 1 | 13995.0 |
| 340 | simple | 0 | incorrect_result | 4 | 3 | 1 | 10316.0 |
| 345 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 14070.0 |
| 346 | moderate | 1 | correct | 5 | 4 | 1 | 14124.0 |
| 349 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 15188.0 |
| 352 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 13918.0 |
| 356 | simple | 1 | correct | 4 | 3 | 1 | 11946.0 |
| 358 | simple | 1 | correct | 4 | 3 | 1 | 10579.0 |
| 366 | simple | 0 | incorrect_result | 5 | 4 | 2 | 14598.0 |
| 368 | simple | 1 | correct | 4 | 3 | 1 | 11819.0 |
| 371 | challenging | 0 | incorrect_result | 7 | 6 | 1 | 20859.0 |
| 379 | simple | 1 | correct | 4 | 3 | 1 | 10401.0 |
| 383 | simple | 0 | incorrect_result | 5 | 4 | 1 | 16358.0 |
| 397 | moderate | 1 | correct | 4 | 3 | 1 | 10308.0 |
| 402 | moderate | 0 | incorrect_result | 6 | 5 | 3 | 21824.0 |
| 405 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 15769.0 |
| 407 | moderate | 1 | correct | 5 | 4 | 1 | 14685.0 |
| 408 | moderate | 0 | incorrect_result | 4 | 3 | 1 | 11581.0 |
| 409 | moderate | 1 | correct | 6 | 5 | 1 | 16995.0 |
| 412 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 13784.0 |
| 414 | simple | 1 | correct | 5 | 4 | 1 | 14702.0 |
| 415 | challenging | 1 | correct | 7 | 6 | 3 | 23115.0 |
| 416 | challenging | 1 | correct | 5 | 4 | 1 | 15129.0 |
| 422 | simple | 1 | correct | 5 | 4 | 1 | 13465.0 |
| 427 | moderate | 1 | correct | 5 | 4 | 1 | 13430.0 |
| 440 | simple | 1 | correct | 6 | 5 | 2 | 19905.0 |
| 462 | moderate | 1 | correct | 5 | 6 | 2 | 16790.0 |
| 465 | moderate | 0 | incorrect_result | 6 | 5 | 2 | 18333.0 |
| 466 | moderate | 1 | correct | 6 | 5 | 1 | 17953.0 |
| 468 | moderate | 1 | correct | 4 | 4 | 1 | 14913.0 |
| 469 | moderate | 0 | incorrect_result | 6 | 5 | 2 | 19437.0 |
| 472 | moderate | 1 | correct | 5 | 4 | 1 | 14107.0 |
| 473 | moderate | 0 | incorrect_result | 6 | 5 | 2 | 19300.0 |
| 477 | challenging | 1 | correct | 4 | 3 | 1 | 10881.0 |
| 480 | moderate | 1 | correct | 5 | 4 | 2 | 18697.0 |
| 484 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 16300.0 |
| 486 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 16433.0 |
| 487 | challenging | 1 | correct | 5 | 4 | 1 | 14872.0 |
| 518 | moderate | 1 | correct | 5 | 4 | 1 | 18406.0 |
| 522 | moderate | 1 | correct | 5 | 6 | 2 | 17706.0 |
| 529 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 15204.0 |
| 530 | moderate | 0 | incorrect_result | 8 | 8 | 5 | 29722.0 |
| 532 | simple | 1 | correct | 4 | 3 | 1 | 11008.0 |
| 533 | simple | 0 | incorrect_result | 4 | 3 | 1 | 11020.0 |
| 537 | simple | 1 | correct | 5 | 4 | 1 | 12723.0 |
| 539 | simple | 1 | correct | 4 | 4 | 1 | 11613.0 |
| 547 | simple | 1 | correct | 5 | 4 | 1 | 15124.0 |
| 549 | simple | 1 | correct | 5 | 4 | 1 | 13603.0 |
| 555 | simple | 1 | correct | 5 | 4 | 1 | 18247.0 |
| 557 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 15210.0 |
| 563 | moderate | 1 | correct | 5 | 5 | 2 | 18765.0 |
| 565 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 13721.0 |
| 567 | simple | 1 | correct | 5 | 4 | 1 | 13887.0 |
| 568 | simple | 1 | correct | 4 | 4 | 1 | 12491.0 |
| 571 | moderate | 1 | correct | 4 | 4 | 1 | 13001.0 |
| 572 | moderate | 1 | correct | 4 | 3 | 1 | 10342.0 |
| 576 | simple | 1 | correct | 4 | 4 | 1 | 13711.0 |
| 578 | moderate | 1 | correct | 4 | 4 | 1 | 11526.0 |
| 581 | moderate | 1 | correct | 7 | 6 | 3 | 21715.0 |
| 584 | moderate | 0 | incorrect_result | 6 | 5 | 1 | 17652.0 |
| 586 | challenging | 0 | incorrect_result | 5 | 6 | 1 | 14913.0 |
| 587 | moderate | 0 | incorrect_result | 6 | 6 | 2 | 18546.0 |
| 592 | simple | 1 | correct | 4 | 3 | 1 | 10769.0 |
| 595 | moderate | 0 | incorrect_result | 5 | 6 | 2 | 24181.0 |
| 598 | challenging | 0 | incorrect_result | 6 | 5 | 3 | 18015.0 |
| 604 | moderate | 1 | correct | 6 | 5 | 2 | 18656.0 |
| 629 | simple | 1 | correct | 4 | 3 | 1 | 13210.0 |
| 633 | moderate | 1 | correct | 5 | 4 | 1 | 13969.0 |
| 634 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 18683.0 |
| 665 | moderate | 1 | correct | 5 | 4 | 1 | 20398.0 |
| 672 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 15409.0 |
| 678 | simple | 1 | correct | 4 | 4 | 1 | 20717.0 |
| 682 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 14598.0 |
| 683 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 12519.0 |
| 687 | simple | 1 | correct | 5 | 4 | 1 | 12738.0 |
| 694 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 16171.0 |
| 701 | challenging | 1 | correct | 4 | 4 | 1 | 13940.0 |
| 704 | simple | 1 | correct | 4 | 3 | 1 | 17667.0 |
| 705 | simple | 1 | correct | 4 | 4 | 1 | 11800.0 |
| 710 | simple | 0 | incorrect_result | 5 | 4 | 1 | 12842.0 |
| 716 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 14735.0 |
| 717 | simple | 1 | correct | 4 | 5 | 1 | 11633.0 |
| 719 | moderate | 1 | correct | 4 | 5 | 1 | 13052.0 |
| 723 | moderate | 1 | correct | 4 | 6 | 1 | 16762.0 |
| 724 | challenging | 1 | correct | 4 | 4 | 1 | 16464.0 |
| 726 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 13028.0 |
| 728 | moderate | 0 | incorrect_result | 4 | 7 | 1 | 14666.0 |
| 730 | challenging | 1 | correct | 4 | 6 | 1 | 15471.0 |
| 732 | moderate | 1 | correct | 4 | 6 | 1 | 14867.0 |
| 733 | moderate | 1 | correct | 4 | 5 | 1 | 13165.0 |
| 736 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 14888.0 |
| 737 | simple | 1 | correct | 4 | 4 | 1 | 10858.0 |
| 738 | simple | 1 | correct | 4 | 5 | 1 | 12206.0 |
| 739 | moderate | 1 | correct | 4 | 5 | 1 | 16037.0 |
| 743 | challenging | 1 | correct | 4 | 5 | 1 | 13838.0 |
| 747 | simple | 1 | correct | 4 | 3 | 1 | 11110.0 |
| 750 | simple | 1 | correct | 4 | 4 | 1 | 11426.0 |
| 758 | moderate | 1 | correct | 6 | 7 | 3 | 20493.0 |
| 760 | challenging | 1 | correct | 5 | 4 | 1 | 80105.0 |
| 761 | moderate | 1 | correct | 5 | 4 | 1 | 13489.0 |
| 764 | simple | 1 | correct | 5 | 4 | 1 | 14421.0 |
| 765 | simple | 1 | correct | 5 | 4 | 1 | 76157.0 |
| 766 | moderate | 0 | incorrect_result | 6 | 7 | 3 | 20682.0 |
| 769 | challenging | 1 | correct | 10 | 12 | 7 | 42105.0 |
| 772 | challenging | 0 | incorrect_result | 4 | 6 | 1 | 14511.0 |
| 773 | challenging | 1 | correct | 4 | 5 | 1 | 11864.0 |
| 775 | challenging | 1 | correct | 4 | 5 | 1 | 15404.0 |
| 779 | simple | 1 | correct | 4 | 5 | 1 | 12144.0 |
| 782 | moderate | 1 | correct | 4 | 4 | 1 | 11879.0 |
| 786 | moderate | 1 | correct | 6 | 5 | 1 | 19419.0 |
| 790 | moderate | 1 | correct | 4 | 3 | 1 | 11351.0 |
| 791 | simple | 0 | incorrect_result | 3 | 3 | 1 | 11981.0 |
| 792 | simple | 1 | correct | 6 | 5 | 1 | 23888.0 |
| 794 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 13626.0 |
| 796 | moderate | 1 | correct | 4 | 5 | 1 | 13533.0 |
| 797 | moderate | 1 | correct | 5 | 4 | 1 | 15359.0 |
| 798 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 13502.0 |
| 800 | moderate | 1 | correct | 4 | 3 | 1 | 12206.0 |
| 806 | simple | 1 | correct | 4 | 4 | 1 | 11712.0 |
| 819 | challenging | 1 | correct | 4 | 4 | 1 | 14348.0 |
| 822 | moderate | 1 | correct | 4 | 5 | 1 | 13418.0 |
| 825 | moderate | 1 | correct | 4 | 6 | 1 | 16332.0 |
| 829 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 14630.0 |
| 846 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 15026.0 |
| 847 | simple | 0 | incorrect_result | 4 | 4 | 1 | 12596.0 |
| 850 | simple | 1 | correct | 4 | 4 | 1 | 13437.0 |
| 854 | simple | 1 | correct | 4 | 4 | 1 | 11983.0 |
| 857 | simple | 1 | correct | 4 | 4 | 1 | 12626.0 |
| 861 | simple | 0 | incorrect_result | 4 | 4 | 1 | 11619.0 |
| 862 | simple | 1 | correct | 4 | 4 | 1 | 12881.0 |
| 865 | moderate | 1 | correct | 4 | 4 | 1 | 14337.0 |
| 866 | moderate | 1 | correct | 4 | 4 | 1 | 13321.0 |
| 868 | simple | 1 | correct | 4 | 4 | 1 | 12580.0 |
| 869 | moderate | 1 | correct | 4 | 4 | 1 | 13796.0 |
| 872 | simple | 1 | correct | 4 | 4 | 1 | 12620.0 |
| 875 | simple | 1 | correct | 4 | 4 | 1 | 15314.0 |
| 877 | moderate | 1 | correct | 4 | 4 | 1 | 12840.0 |
| 880 | challenging | 1 | correct | 5 | 4 | 2 | 15846.0 |
| 884 | moderate | 1 | correct | 4 | 3 | 1 | 11941.0 |
| 892 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 13723.0 |
| 894 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 12465.0 |
| 896 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 16521.0 |
| 897 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 17134.0 |
| 902 | simple | 0 | incorrect_result | 4 | 5 | 1 | 14667.0 |
| 904 | moderate | 1 | correct | 5 | 6 | 2 | 26265.0 |
| 906 | moderate | 0 | incorrect_result | 4 | 6 | 1 | 15772.0 |
| 909 | moderate | 1 | correct | 5 | 4 | 1 | 15289.0 |
| 910 | simple | 1 | correct | 4 | 3 | 1 | 10784.0 |
| 912 | simple | 1 | correct | 4 | 3 | 1 | 11435.0 |
| 915 | simple | 1 | correct | 4 | 3 | 1 | 11183.0 |
| 928 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 16680.0 |
| 930 | simple | 0 | incorrect_result | 6 | 7 | 3 | 29335.0 |
| 931 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 12407.0 |
| 933 | moderate | 1 | correct | 4 | 5 | 1 | 12511.0 |
| 937 | simple | 0 | incorrect_result | 4 | 5 | 1 | 13208.0 |
| 940 | moderate | 1 | correct | 5 | 6 | 2 | 17746.0 |
| 944 | challenging | 0 | incorrect_result | 17 | 18 | 14 | 59256.0 |
| 948 | simple | 0 | incorrect_result | 4 | 4 | 1 | 13057.0 |
| 950 | simple | 0 | incorrect_result | 4 | 4 | 1 | 14039.0 |
| 951 | simple | 0 | incorrect_result | 4 | 4 | 1 | 12622.0 |
| 954 | challenging | 1 | correct | 4 | 5 | 1 | 14167.0 |
| 960 | moderate | 1 | correct | 4 | 4 | 1 | 15171.0 |
| 962 | challenging | 1 | correct | 4 | 5 | 1 | 15323.0 |
| 963 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 17083.0 |
| 964 | simple | 1 | correct | 4 | 3 | 1 | 11256.0 |
| 967 | simple | 1 | correct | 5 | 4 | 2 | 17163.0 |
| 971 | simple | 1 | correct | 4 | 4 | 2 | 11514.0 |
| 977 | simple | 1 | correct | 4 | 3 | 1 | 19082.0 |
| 981 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 19607.0 |
| 988 | challenging | 0 | incorrect_result | 5 | 5 | 2 | 16062.0 |
| 989 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 13210.0 |
| 990 | challenging | 1 | correct | 5 | 6 | 2 | 24378.0 |
| 994 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 16768.0 |
| 1003 | moderate | 1 | correct | 4 | 6 | 1 | 17190.0 |
| 1011 | challenging | 0 | incorrect_result | 5 | 7 | 2 | 30994.0 |
| 1014 | challenging | 0 | incorrect_result | 7 | 9 | 3 | 33697.0 |
| 1025 | moderate | 1 | correct | 4 | 4 | 1 | 13173.0 |
| 1028 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 17193.0 |
| 1029 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 14327.0 |
| 1030 | moderate | 1 | correct | 4 | 4 | 1 | 15107.0 |
| 1031 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 15107.0 |
| 1032 | moderate | 1 | correct | 5 | 4 | 1 | 14776.0 |
| 1035 | simple | 1 | correct | 4 | 3 | 1 | 11610.0 |
| 1036 | challenging | 1 | correct | 5 | 6 | 3 | 18426.0 |
| 1037 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 28129.0 |
| 1040 | moderate | 1 | correct | 5 | 4 | 1 | 16849.0 |
| 1042 | challenging | 1 | correct | 4 | 4 | 1 | 15561.0 |
| 1044 | simple | 1 | correct | 3 | 2 | 0 | 8129.0 |
| 1048 | simple | 1 | correct | 4 | 4 | 1 | 13994.0 |
| 1057 | moderate | 1 | correct | 4 | 5 | 1 | 12327.0 |
| 1058 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 17683.0 |
| 1068 | moderate | 1 | correct | 4 | 4 | 1 | 17510.0 |
| 1078 | simple | 0 | incorrect_result | 4 | 3 | 1 | 13714.0 |
| 1079 | simple | 1 | correct | 4 | 3 | 1 | 11820.0 |
| 1080 | moderate | 0 | incorrect_result | 4 | 3 | 1 | 11970.0 |
| 1084 | challenging | 1 | correct | 5 | 4 | 1 | 15097.0 |
| 1091 | moderate | 1 | correct | 4 | 4 | 1 | 12202.0 |
| 1092 | simple | 0 | incorrect_result | 4 | 4 | 1 | 13155.0 |
| 1094 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 21549.0 |
| 1096 | moderate | 1 | correct | 5 | 4 | 1 | 16974.0 |
| 1098 | moderate | 1 | correct | 5 | 4 | 1 | 14896.0 |
| 1102 | moderate | 1 | correct | 5 | 4 | 1 | 14334.0 |
| 1105 | moderate | 1 | correct | 5 | 4 | 1 | 17584.0 |
| 1107 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 21361.0 |
| 1113 | moderate | 1 | correct | 4 | 4 | 1 | 12206.0 |
| 1114 | challenging | 1 | correct | 5 | 4 | 1 | 16610.0 |
| 1115 | challenging | 1 | correct | 5 | 5 | 2 | 19094.0 |
| 1116 | simple | 1 | correct | 4 | 3 | 1 | 13389.0 |
| 1122 | simple | 1 | correct | 5 | 4 | 1 | 16564.0 |
| 1124 | moderate | 1 | correct | 4 | 4 | 1 | 16906.0 |
| 1134 | simple | 1 | correct | 4 | 3 | 1 | 10787.0 |
| 1135 | moderate | 0 | incorrect_result | 6 | 5 | 2 | 15925.0 |
| 1136 | moderate | 0 | incorrect_result | 4 | 3 | 1 | 11677.0 |
| 1141 | moderate | 1 | correct | 5 | 4 | 2 | 16455.0 |
| 1144 | simple | 0 | incorrect_result | 6 | 5 | 2 | 20402.0 |
| 1145 | simple | 0 | incorrect_result | 5 | 4 | 1 | 15556.0 |
| 1148 | moderate | 0 | incorrect_result | 5 | 4 | 1 | 19378.0 |
| 1149 | moderate | 0 | incorrect_result | 5 | 4 | 2 | 20434.0 |
| 1152 | moderate | 1 | correct | 4 | 5 | 1 | 15257.0 |
| 1153 | simple | 1 | correct | 4 | 6 | 2 | 18261.0 |
| 1155 | simple | 1 | correct | 4 | 4 | 1 | 13021.0 |
| 1156 | moderate | 1 | correct | 4 | 5 | 1 | 17161.0 |
| 1157 | simple | 1 | correct | 4 | 5 | 1 | 13751.0 |
| 1162 | moderate | 1 | correct | 4 | 5 | 1 | 10684.0 |
| 1166 | simple | 0 | incorrect_result | 5 | 6 | 2 | 20870.0 |
| 1168 | challenging | 0 | incorrect_result | 6 | 7 | 3 | 20066.0 |
| 1169 | challenging | 1 | correct | 4 | 5 | 1 | 17930.0 |
| 1171 | challenging | 0 | incorrect_result | 5 | 4 | 1 | 18892.0 |
| 1175 | moderate | 1 | correct | 9 | 10 | 6 | 31612.0 |
| 1185 | challenging | 1 | correct | 5 | 6 | 2 | 22581.0 |
| 1187 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 13668.0 |
| 1189 | challenging | 1 | correct | 4 | 5 | 1 | 12740.0 |
| 1192 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 11780.0 |
| 1198 | simple | 1 | correct | 4 | 5 | 1 | 11088.0 |
| 1201 | moderate | 1 | correct | 4 | 3 | 1 | 13163.0 |
| 1205 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 14695.0 |
| 1208 | moderate | 1 | correct | 4 | 5 | 1 | 14299.0 |
| 1209 | moderate | 1 | correct | 4 | 5 | 1 | 24616.0 |
| 1225 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 12810.0 |
| 1227 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 12959.0 |
| 1229 | moderate | 1 | correct | 4 | 5 | 1 | 12937.0 |
| 1231 | challenging | 1 | correct | 4 | 5 | 1 | 13965.0 |
| 1232 | challenging | 1 | correct | 4 | 5 | 1 | 16322.0 |
| 1235 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 14243.0 |
| 1238 | moderate | 1 | correct | 4 | 5 | 1 | 13876.0 |
| 1242 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 13779.0 |
| 1243 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 16723.0 |
| 1247 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 16326.0 |
| 1251 | simple | 0 | incorrect_result | 4 | 5 | 1 | 13441.0 |
| 1252 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 16495.0 |
| 1254 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 15677.0 |
| 1255 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 14564.0 |
| 1265 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 13497.0 |
| 1267 | moderate | 0 | incorrect_result | 9 | 8 | 4 | 47316.0 |
| 1270 | challenging | 1 | correct | 4 | 5 | 1 | 14986.0 |
| 1275 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 13154.0 |
| 1281 | moderate | 1 | correct | 4 | 5 | 1 | 11436.0 |
| 1302 | challenging | 0 | incorrect_result | 4 | 5 | 1 | 15830.0 |
| 1312 | simple | 1 | correct | 4 | 4 | 1 | 13361.0 |
| 1322 | moderate | 0 | incorrect_result | 5 | 5 | 1 | 30096.0 |
| 1323 | moderate | 1 | correct | 5 | 5 | 2 | 16957.0 |
| 1331 | simple | 1 | correct | 4 | 4 | 1 | 12814.0 |
| 1334 | simple | 1 | correct | 5 | 6 | 1 | 15885.0 |
| 1338 | moderate | 0 | incorrect_result | 8 | 8 | 4 | 28383.0 |
| 1339 | challenging | 1 | correct | 4 | 5 | 1 | 14045.0 |
| 1344 | simple | 1 | correct | 4 | 3 | 1 | 12230.0 |
| 1346 | simple | 1 | correct | 4 | 3 | 1 | 13274.0 |
| 1350 | moderate | 1 | correct | 7 | 7 | 3 | 21879.0 |
| 1351 | simple | 1 | correct | 4 | 4 | 1 | 13256.0 |
| 1356 | simple | 1 | correct | 4 | 4 | 1 | 11841.0 |
| 1357 | simple | 1 | correct | 4 | 4 | 1 | 12161.0 |
| 1361 | simple | 1 | correct | 4 | 3 | 1 | 9748.0 |
| 1362 | simple | 1 | correct | 4 | 3 | 1 | 10444.0 |
| 1368 | simple | 1 | correct | 5 | 4 | 1 | 13889.0 |
| 1376 | moderate | 1 | correct | 4 | 5 | 1 | 15198.0 |
| 1378 | simple | 1 | correct | 4 | 3 | 1 | 8797.0 |
| 1381 | moderate | 0 | incorrect_result | 4 | 4 | 1 | 14773.0 |
| 1387 | moderate | 0 | incorrect_result | 8 | 11 | 4 | 34432.0 |
| 1389 | simple | 0 | incorrect_result | 6 | 5 | 1 | 18236.0 |
| 1390 | moderate | 1 | correct | 6 | 6 | 2 | 21024.0 |
| 1394 | simple | 1 | correct | 5 | 4 | 1 | 16683.0 |
| 1398 | moderate | 1 | correct | 5 | 6 | 1 | 16234.0 |
| 1399 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 14468.0 |
| 1401 | moderate | 1 | correct | 5 | 5 | 1 | 19208.0 |
| 1403 | moderate | 1 | correct | 4 | 5 | 1 | 13544.0 |
| 1404 | moderate | 0 | incorrect_result | 7 | 7 | 3 | 23922.0 |
| 1405 | moderate | 1 | correct | 4 | 4 | 1 | 16247.0 |
| 1409 | simple | 1 | correct | 4 | 3 | 1 | 10640.0 |
| 1411 | simple | 1 | correct | 5 | 4 | 1 | 13075.0 |
| 1422 | simple | 0 | incorrect_result | 4 | 3 | 1 | 9646.0 |
| 1426 | moderate | 1 | correct | 4 | 4 | 1 | 11410.0 |
| 1427 | moderate | 0 | incorrect_result | 4 | 5 | 1 | 13164.0 |
| 1435 | moderate | 1 | correct | 4 | 3 | 1 | 12752.0 |
| 1457 | challenging | 1 | correct | 4 | 4 | 1 | 14364.0 |
| 1460 | challenging | 0 | incorrect_result | 4 | 4 | 1 | 11500.0 |
| 1464 | challenging | 1 | correct | 7 | 6 | 3 | 53855.0 |
| 1471 | simple | 1 | correct | 4 | 3 | 1 | 14891.0 |
| 1472 | moderate | 1 | correct | 5 | 7 | 2 | 16680.0 |
| 1473 | moderate | 1 | correct | 4 | 5 | 1 | 15316.0 |
| 1479 | moderate | 1 | correct | 6 | 9 | 4 | 23117.0 |
| 1480 | moderate | 1 | correct | 6 | 8 | 3 | 20398.0 |
| 1481 | challenging | 0 | incorrect_result | 6 | 10 | 3 | 35064.0 |
| 1482 | challenging | 0 | incorrect_result | 5 | 7 | 3 | 24292.0 |
| 1486 | simple | 0 | incorrect_result | 5 | 5 | 2 | 36638.0 |
| 1490 | moderate | 0 | incorrect_result | 9 | 9 | 5 | 39969.0 |
| 1493 | simple | 1 | correct | 4 | 6 | 1 | 24826.0 |
| 1498 | simple | 1 | correct | 5 | 5 | 2 | 18817.0 |
| 1500 | simple | 1 | correct | 6 | 7 | 3 | 18475.0 |
| 1501 | moderate | 0 | incorrect_result | 7 | 8 | 4 | 21522.0 |
| 1507 | simple | 1 | correct | 4 | 4 | 1 | 12478.0 |
| 1509 | moderate | 1 | correct | 4 | 4 | 1 | 16342.0 |
| 1514 | simple | 1 | correct | 5 | 5 | 2 | 16378.0 |
| 1515 | simple | 1 | correct | 4 | 4 | 1 | 12730.0 |
| 1521 | moderate | 1 | correct | 4 | 4 | 1 | 14532.0 |
| 1524 | simple | 1 | correct | 13 | 14 | 6 | 39784.0 |
| 1525 | simple | 0 | incorrect_result | 5 | 5 | 2 | 18186.0 |
| 1526 | challenging | 0 | incorrect_result | 8 | 9 | 5 | 29450.0 |
| 1528 | simple | 1 | correct | 6 | 7 | 2 | 21588.0 |
| 1529 | moderate | 0 | incorrect_result | 6 | 8 | 3 | 32645.0 |
| 1533 | moderate | 0 | incorrect_result | 4 | 6 | 1 | 17780.0 |

Times are milliseconds. Model turns represent observable main-agent model calls.
Cached input tokens are part of input tokens; reasoning tokens are part of output tokens.
Optional usage fields may be partial: compare *_observed_calls with model_calls.
Thinking/effort values are reported only when a provider supplies them.
Nested subagent activity may be unobserved. n/a does not mean zero.
Agent SQL tool success is not equivalent to final SQL EX.
Gold SQL is validated separately before any predicted SQL scoring.
