# Reproduction and provenance

Run commands from the Group Project directory. The archived inference used source commit `465bde31b67c6fb01d9ffbba7fec665a23d63a01`; the restoration helper was added later to make the completed restoration reproducible. Existing predictions and scores are frozen. New inference consumes provider quota and may produce different SQL.

## Dataset and descriptions

Install the pinned Mini-Dev 2026 SQLite dataset following [dataset versions](../../docs/bird-dataset-versions.md). Preserve the existing manifest, annotations and database hashes. The description helper accepts an already-downloaded official package and the pinned official schema; it never extracts databases or annotations from the package.

Official sources:

- [BIRD Mini-Dev repository](https://github.com/bird-bench/mini_dev).
- [Complete package linked by that repository](https://drive.google.com/file/d/13VLWIwpw5E3d5DUkMvzw7hvHE67a4XkG/view).
- [Pinned official SQLite baseline schema](https://huggingface.co/datasets/birdsql/bird_mini_dev/resolve/5b256b5a9c17478f06ed6912612e9a14d17065c8/baseline_inference/schemas/sqlite.json).

Expected SHA-256 values for this experiment:

```text
aeb211c0e39010bbdae3838bb5e8bd27dc446ed77495b1709f85ccc9bf67f2be  official-mini-dev.zip
5176e324a72e80a8a37a12285596d123e0ba6c310dceaa9f13a1e413ee88ff5b  official-sqlite-schema.json
```

After downloading those files into an ignored local download directory, check their hashes before restoring:

```bash
uv run python -m scr.datasets.restore_bird_descriptions \
  --dataset-root data/bird/mini-dev-2026 \
  --archive data/bird/_downloads/official-mini-dev.zip \
  --official-schema data/bird/_downloads/official-sqlite-schema.json \
  --report data/bird/_downloads/new-restoration-audit.json
```

Use a new report filename. This command refuses existing destination CSVs. On an already restored dataset, add `--verify-existing` and use another new report filename; verification compares the expected bytes and does not rewrite the descriptions. Both modes check the CSV tables/columns and preserve existing dataset files. The only permitted release adaptations are the documented constructors row removal and schema-only element supplement. Other mismatches fail before CSV writes.

## Fresh full inference

Use unused selection, experiment and run IDs. This example uses a fresh `metadata-discovery-v2-descriptions-reproduction` prefix; change it if those IDs already exist. Do not run `--resume` against the archived experiment.

```bash
uv run python -m scr.cli.run_bird_b0_eval prepare \
  --dataset-root data/bird/mini-dev-2026 --total-questions 500 \
  --dev-ratio 0.8 --seed 42 --selection-id metadata-discovery-v2-descriptions-reproduction

uv run python -m scr.cli.run_bird_metadata_eval infer \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id metadata-discovery-v2-descriptions-reproduction --workflow metadata-discovery-v2 \
  --experiment-id metadata-discovery-v2-descriptions-reproduction \
  --split dev --run-id metadata-discovery-v2-descriptions-reproduction-dev \
  --provider chatgpt-siwc --model gpt-6-luna \
  --reasoning-effort none --prompt-variant generalized-v1 --preview-rows 20

uv run python -m scr.cli.run_bird_metadata_eval infer \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id metadata-discovery-v2-descriptions-reproduction --workflow metadata-discovery-v2 \
  --experiment-id metadata-discovery-v2-descriptions-reproduction \
  --split test --run-id metadata-discovery-v2-descriptions-reproduction-test \
  --provider chatgpt-siwc --model gpt-6-luna \
  --reasoning-effort none --prompt-variant generalized-v1 --preview-rows 20
```

Use the existing authorized SIWC sign-in. No API-provider fallback is intended. Dev must finish before Test. The archived experiment manifest records the exact source configuration and prompt/code hashes. Preserve the 120/200/80 global budgets and 20/40 per-attempt A1 model/tool limits when comparing runs. The new selection ID changes provenance hashes, so the original manifest is a reference, not a file to replace the newly generated manifest.

Score each new run with `scr.cli.run_bird_metadata_eval score`, supplying the same selection, dataset root, workflow, split and matching run ID. Its default timeout for this experiment is 300 seconds. Generate the viewer with the corresponding `visualize` command.

## Offline rescoring of this archive

Use a fresh output location and matching dataset. These commands do not invoke a model or change archived scores:

```bash
uv run python -m scr.cli.evaluate_bird \
  --variant MetadataDiscoveryV2 --split dev \
  --dataset-root data/bird/mini-dev-2026 \
  --predictions evaluation-results/metadata-discovery-v2-descriptions-20261111/dev/predictions.jsonl \
  --output-dir results/metadata-discovery-v2-descriptions-rescore --run-id dev \
  --timeout-seconds 300

uv run python -m scr.cli.evaluate_bird \
  --variant MetadataDiscoveryV2 --split test \
  --dataset-root data/bird/mini-dev-2026 \
  --predictions evaluation-results/metadata-discovery-v2-descriptions-20261111/test/predictions.jsonl \
  --output-dir results/metadata-discovery-v2-descriptions-rescore --run-id test \
  --timeout-seconds 300
```

The original runner passed all explicit split IDs, causing the scorer's generic “SMOKE SUBSET ONLY” log label. Independent ID/count checks establish complete 400/100 coverage. Omitting `--question-ids` above selects the full requested split.

## Local traces and export recovery

The raw trace and HTML paths/hashes are in `provenance/local-artifacts.json`. The original Dev trace is about 58 MiB, exceeding the viewer's default 50 MiB input cap. Its successful export used the existing `scr.tracing.viewer.write_html` with a process-local `MAX_TRACE_BYTES = 100 * 1024 * 1024`, bounded to these verified local inputs; source code and raw traces were unchanged. Both HTML explorers were opened in Chromium, with all 400/100 questions present. Database labels were then filled from the matching predictions through the existing renderer because the original trace records omit top-level database IDs.

The Codex daemon restarted during Dev; the original inference process survived and was adopted without rerunning questions. Two failed SQL-generation questions remain failures, without post-score replacements. Transient failed streams may have unreported usage. SIWC monetary costs are unavailable.

## Knowledge and offline analysis

The final 572 notes/indexes and operation history are retained for audit. Test started with the exact Dev completion snapshot and could add/update notes. This is continual same-database knowledge reuse. Notes, the operation log, scores and failure analysis must not be injected into a new supposedly fresh Dev run. All reference-SQL research is evaluator-only; the full local SQL-review inventory includes gold SQL and is deliberately absent from Git.

The metrics and review are frozen outputs. Sixteen mismatch cases received direct SQL/question review; all 160 failures are indexed, but the remaining mismatches are not claimed to have proven semantic root causes. No automatic SQL-difference flag is a verified fix. See the performance report for observed-call accounting, historical-comparison caveats and resource tradeoffs.
