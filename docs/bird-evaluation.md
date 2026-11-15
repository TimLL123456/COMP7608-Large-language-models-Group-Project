# KORA — Execution Accuracy (EX) Evaluation

The current independent scorer evaluates **saved final SQL predictions** against reference SQL outputs on the *same* SQLite database. It makes **no model calls**. Use the [Mini-Dev 2026 setup](bird-setup.md) and [B0 Prepare → Infer → Score workflow](bird-b0.md#mini-dev-2026-current-workflow).

## What EX measures

~~~text
Question / Evidence → Agent → Final SQL → SQLite result ─┐
                                                          ├→ Compare result sets → 1 or 0
Reference SQL (evaluator-only) → SQLite result ──────────┘
~~~

EX compares complete result sets. The current evaluator compares row tuples as sets; **column order matters**, while result-row order and duplicate rows do not. Missing SQL, unsafe SQL, execution errors and timeouts score 0. Invalid Gold SQL/execution invalidates evaluation rather than becoming an ordinary model error.

A successful SQL execution or reviewer PASS **does not** imply an EX-correct answer.

## Score an existing B0 run

~~~bash
uv run python -m scr.cli.run_bird_b0_eval score \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id YOUR_SELECTION --split dev \
  --run-id YOUR_RUN_ID
~~~

Read the created `scores/report.md`, per-question scores and manifest. The agent's own inputs must never contain Gold SQL or reference result rows. New independent generators must emit prediction records and matching dataset provenance; consult the [historical full evaluation guide](history/bird-evaluation-pre-current-only-20261115.md) for advanced custom-prediction examples.

## Interpreting research results

All completed KORA 500-question agent evaluations currently reported in the [Group README](../README.md#latest-research-results) use the **local** 400/100 Mini-Dev 2026 split, not official hidden Test. Different provider/model budgets, retry policies and restored metadata can confound cross-variant EX comparisons. Report SQL output rate, database/difficulty variation, corrected/regressed cases, tokens, latency, budgets and failure types separately.

For complete scoring methods, caveats, historical experiments and downstream research, follow the [archived evaluation guide](history/bird-evaluation-pre-current-only-20261115.md) and [experiment archive index](history/README.md).
