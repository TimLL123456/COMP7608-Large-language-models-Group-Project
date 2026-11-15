# Inspect and reproduce the experiment

## Inspect without model calls

From this archive, run `sha256sum --check checksums.sha256`. Decompress `dev/traces.jsonl.gz` or `test/traces.jsonl.gz` with `gzip -dk`. Decompress `trace-explorer.html.gz` and open the resulting HTML locally to inspect the saved trace viewer. These operations do not call a model. Independent scoring outputs are already in each split’s `scores/` directory.

## Reproduce inference or scoring

Use source commit `cbb8ea4ada492ceb7970692f571b4e36a34b8227` and its pinned project dependencies. A snapshot of its `scr/`, tests, dependency files and self-reflection design document is included in `provenance/source-cbb8ea4.tar.gz`; extract it into a separate directory to inspect the exact evaluated implementation. The source project then lived at `2026-2027/Sem1/COMP7608 - Large language models/Group Project`. It now lives at `2026-2027/Sem1/COMP7608 - Large language models/COMP7608 - Large language models - Group Project`.

Restore the exact Mini-Dev 2026 dataset matching `inputs/dataset_manifest.json`; SQLite database files are not in this archive. Supply provider authentication through the project’s existing sign-in mechanism, never committed secrets. Create a NEW results root, copy `selection_manifest.json` into its `sr-full-20261113/` folder and copy `inputs/dev.jsonl` and `inputs/test.jsonl` beside it.

From the source project root, replace DATASET and RESULTS with those absolute directories and run for each split (`dev`, then `test`):

```bash
python -m scr.cli.run_bird_self_reflection_eval infer   --dataset-root DATASET --result-root RESULTS   --selection-id sr-full-20261113 --split dev --run-id sr-luna-none-sqlfirst-001   --provider chatgpt-siwc --model gpt-6-luna --reasoning-effort none   --prompt-variant generalized-v1   --max-attempts 3 --max-review-model-calls 40 --max-inspections 39   --max-total-model-calls 240 --max-total-tool-calls 240 --max-total-sql-calls 240

python -m scr.cli.run_bird_self_reflection_eval score   --dataset-root DATASET --result-root RESULTS   --selection-id sr-full-20261113 --split dev --run-id sr-luna-none-sqlfirst-001

python -m scr.cli.run_bird_self_reflection_eval visualize   --dataset-root DATASET --result-root RESULTS   --selection-id sr-full-20261113 --split dev --run-id sr-luna-none-sqlfirst-001
```

To rescore existing predictions without inference, reconstruct that layout from the archive’s selection files and split run folders; omit their existing `scores/` directories because the scorer refuses overwrites. Copy the saved predictions and inference manifests unchanged. Scoring loads reference SQL offline. Original raw traces and HTML are optional for scoring.

The original local controller is retained for audit, not as a portable entry point: it contains historic absolute paths. New inference can differ because of model/service nondeterminism. The archived result also has a known forced-finalization preflight test failure; inspect `provenance/logs/tests.txt` before treating this revision as fully validated.
