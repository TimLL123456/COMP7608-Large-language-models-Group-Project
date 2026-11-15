# B0: GPT-6 Luna, 40-call evaluation

> **Current setting (10 November 2026):** B0 now uses 40 model calls, 40 total tool calls and 40 SQL executions for both prompt variants; the current requested evaluation runs only `generalized-v1`. The earlier Mini-Dev 2026 B0 configuration metadata also lists 40/40/40. Historical execution limits and scores below remain as originally recorded; this note does not regenerate predictions or convert the archive into a matched control.


All 500 questions were inferred afresh using the same configuration. These are the final results of the replacement run, not the earlier mixed-budget run.

| Split | Correct | Questions | Execution accuracy |
| --- | ---: | ---: | ---: |
| Dev | 236 | 400 | 59.0% |
| Test | 63 | 100 | 63.0% |
| Overall | 299 | 500 | 59.8% |

## Configuration and scope

- Provider: existing single-user ChatGPT sign-in (`chatgpt-siwc`); model: `gpt-6-luna`.
- Requested reasoning effort: `none`. Response-reported settings are retained in predictions and traces.
- Per-question budgets: 40 model calls, 40 total tool calls, 20 SQL executions; graph recursion limit 200.
- Model request timeout: 300 seconds per request; SQL scoring timeout: 600 seconds per reference or predicted query.
- Original BIRD Mini-Dev SQLite: 500 questions, 11 databases, fixed local 400-dev/100-test split, seed 42. This is not the official hidden BIRD benchmark.
- Inference and scoring completed successfully for every question. The limit is a maximum, not an observed call count.
- Run started 2026-11-08 03:59:35 UTC and completed 06:32:14 UTC (approximately 2 hours 33 minutes).

## Files for analysis

`dev/` and `test/` contain the original prediction JSONL, inference manifest, compressed full traces, and all five scoring files: per-question CSV/JSONL, summary JSON, Markdown report, and scoring manifest. Join predictions, scores, and traces using `question_id`; retain the split when combining data. Predictions include model/tool calls, SQL call outcomes, latency in milliseconds, token counts, and reported reasoning settings. Traces contain question/evidence text and observed model/tool events; they can include SQL and database row previews.

Missing optional metrics remain null; cost is unknown, not zero. Cached tokens are included in input tokens, and reasoning tokens are included in output tokens. Usage can be partial when not every call reports it, and nested subagent usage may be unobserved. Traces contain observable events and metadata, not hidden reasoning text.

`summary.json` is the combined export summary. `configuration.json`, `environment.json`, and `provenance.json` identify configuration, runtime/dependency versions, source hashes, and the source run. The matching harness source and `uv.lock` are committed alongside this directory. `dataset_manifest.json` records pinned sources, split membership, and dataset checksums; dataset binaries and downloaded annotations are intentionally excluded from Git.

## Raw scorer labeling limitation

The original runner passes explicit question IDs even when selecting the whole local split. Consequently the raw score summaries/manifests say `is_full_split: false`, and reports say "selected subset". Those raw files are preserved byte-for-byte. Membership verification confirms that all 400 dev and all 100 test IDs were scored. The combined summary records this as `covers_full_local_split: true`. This does not imply an official hidden-test result.

## Reproduction

See [reproduce.md](reproduce.md) for dependency setup, dataset download/verification, offline rescoring, and an optional new inference run. Saved-prediction scoring can be reproduced without model authentication. New model outputs and timings may differ due to hosted-model changes, sampling, hardware, and cache state; the model slug is not an immutable model-weight snapshot.

The export contains no dataset ZIP, SQLite database files, downloaded reference-annotation file, credentials, virtual environment, or temporary job logs. Full traces are compressed to keep Git storage small. Verify the export using `sha256sum -c checksums.sha256` from this directory.
