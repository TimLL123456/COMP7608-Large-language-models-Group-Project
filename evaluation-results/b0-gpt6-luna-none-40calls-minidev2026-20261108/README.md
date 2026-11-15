# Luna B0 — Mini-Dev 2026

Execution accuracy: **294/500 (58.8%)**. Dev: 235/400; local test: 59/100. These are complete local splits, not the official hidden test.

This archive freezes the sampled agent inputs, dataset identity, inference traces, predictions and scoring outputs. Download the raw dataset using the pinned command in [reproduce.md](reproduce.md).

Recorded settings are 40 model calls, 40 total tool calls and 40 SQL calls, with Luna effort `none`. Historical execution differs: 498 cases used a 20 SQL-call limit; dev Q421 and test Q107 were replaced by reruns with a 40 SQL-call limit. Configuration and inference manifests preserve execution history. Metadata alignment did not rerun other cases. This is a mixed-budget result.

Checksums cover the published run files only; local logs, backups and analysis artifacts are excluded.
