# Self Reflection Agent — full Mini-Dev 2026 experiment

**350/500 correct (70.00% execution accuracy)**: Dev 280/400, local held-out Test 70/100. SQL was generated for 498/500 questions.

- [Performance report](performance-report.md): accuracy by split, difficulty and database; reviewer decisions versus independent scores; resources and limitations.
- [Failure inventory](analysis-report/failure-inventory.csv): all 150 incorrect or missing answers.
- [Configuration](configuration.json), [selection manifest](selection_manifest.json), [reproduction instructions](reproduce.md).
- [Dev results](dev/scores/summary.json) and [Test results](test/scores/summary.json).
- [Archive receipt](provenance/archive-receipt.json) and [validation](provenance/validation.json).

## Preserved artifacts

`inputs/` contains the exact 400 Dev and 100 Test agent-facing records (without reference SQL), dataset manifest, database description CSVs, and versioned prompt text. Each split contains original predictions, inference manifest, reviewer decisions, independent scores, gzip-compressed complete raw traces and HTML explorer. Gzip decompression restores the original bytes. `provenance/` contains original run logs, preflight tests, original controller, source and dataset receipts, and a compact snapshot of the exact evaluated source/dependencies/tests (`source-cbb8ea4.tar.gz`). SQLite databases and the downloaded dataset package remain local, matching the prior experiment archive convention; obtain the pinned dataset to rescore.

Inference used source `cbb8ea4`, provider `chatgpt-siwc`, model `gpt-6-luna`, reasoning `none`, and prompt `generalized-v1`. This is a local Mini-Dev result, not an official hidden-test result. The known preflight test failure is disclosed in the report. No code or predictions were changed during archiving.

The course project was moved after inference. Original manifests preserve the old paths as provenance; use the current project root for commands. Run `sha256sum --check checksums.sha256` inside this archive to verify its contents.
