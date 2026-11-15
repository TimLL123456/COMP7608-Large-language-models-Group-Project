# B0 generalized-v1 — Mini-Dev 2026, 40/40/40

| Split | Correct | Total | EX |
|---|---:|---:|---:|
| Dev | 255 | 400 | 63.75% |
| Local Test | 64 | 100 | 64.00% |
| Overall | 319 | 500 | 63.80% |

Only generalized-v1 was inferred. Provider chatgpt-siwc, model gpt-6-luna, requested effort none, 40 model / 40 shared total tool / 40 SQL limits, preview20, seed42. Q60 was rerun once after HTTP504 and replaced only after valid error-free completion, independently of EX; original failed prediction is preserved in q60-retry-audit. No other predictions were replaced.

Read the [Traditional Chinese report](analysis-report/report-zh-HK.md), [181-case RCA](analysis-report/failure-case-review.md), [107 historical transitions](analysis-report/historical-case-review.md), and [500-row analysis CSV](analysis-report/question-analysis-500.csv). Historical B0 had mixed recorded SQL budgets and different scoring timeout: the +5pp difference is descriptive, not a matched prompt-only causal result.

This archive includes compact predictions, manifests, independent scores, reviewed SQL diagnostics and reports. Gold SQL in analysis files is offline/evaluator-only and must never enter runtime prompts. Raw traces, local HTML viewers, datasets, credentials and backups remain local. See [reproduction and local traces](reproduce.md).
