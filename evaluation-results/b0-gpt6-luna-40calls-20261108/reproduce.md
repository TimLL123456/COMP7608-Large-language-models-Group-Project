# Reproduce the saved evaluation

> **Current setting (10 November 2026):** B0 now uses 40 model calls, 40 total tool calls and 40 SQL executions for both prompt variants; the current requested evaluation runs only `generalized-v1`. The earlier Mini-Dev 2026 B0 configuration metadata also lists 40/40/40. Historical execution limits and scores below remain as originally recorded; this note does not regenerate predictions or convert the archive into a matched control.


Run commands from the Group Project directory containing `pyproject.toml`. Use the repository commit containing this export. The exported environment used Python 3.14.10 and SQLite 3.53.1; see `environment.json` for all installed packages and source hashes.

## 1. Restore dependencies

```bash
uv sync --frozen --python 3.14.10
```

This downloads dependencies if needed. SQLite ships with the selected Python runtime; check its version against the recorded environment when investigating differences.

## 2. Verify the export

```bash
(cd evaluation-results/b0-gpt6-luna-40calls-20261108 && sha256sum -c checksums.sha256)
```

The checksums cover every exported file except the checksum list itself. Trace archives are deterministic gzip files (mtime zero); `gzip -dc dev/traces.jsonl.gz` reads a trace without modifying it.

## 3. Download and verify the dataset

```bash
uv run python -m scr.datasets.setup_bird
uv run python -m scr.datasets.setup_bird --verify-only
```

The installer uses pinned Hugging Face annotations and the official Google Drive SQLite archive. See `dataset_manifest.json` for exact annotation revision, question IDs, archive/database hashes, and split. Compare installed annotation and database hashes with the exported manifest before scoring; a successful verification against a newly generated local manifest alone does not prove equality with this run. The original archive is approximately 800 MB, and extraction uses approximately 3.3 GB. Network access is needed for initial downloads; subsequently scoring is offline. Manual-download alternatives are documented in `docs/bird-setup.md`.

## 4. Rescore saved predictions (no model calls or sign-in)

```bash
uv run python -m scr.cli.evaluate_bird --variant B0 --split dev --predictions evaluation-results/b0-gpt6-luna-40calls-20261108/dev/predictions.jsonl --output-dir results/reproduced-40calls --run-id dev --timeout-seconds 600
uv run python -m scr.cli.evaluate_bird --variant B0 --split test --predictions evaluation-results/b0-gpt6-luna-40calls-20261108/test/predictions.jsonl --output-dir results/reproduced-40calls --run-id test --timeout-seconds 600
```

These commands use the complete fixed split and the default 100,000-row result cap. Expected results: dev 236/400, test 63/100, overall 299/500. Compare per-question `question_id`, `predicted_sql`, `ex`, and `status`; elapsed times need not match. Outputs go to Git-ignored `results/`; use another output directory if it already exists. A reference-query timeout invalidates the evaluation; do not silently exclude questions or report a partial score as full accuracy.

## 5. Optional: rerun inference

This requires a valid local ChatGPT sign-in, can consume account usage, and can generate different predictions. Authentication is deliberately absent from the export. After explicitly choosing to run new inference, sign in using `uv run python -m scr.baselines.siwc_auth` if necessary and verify available models using `uv run python -m scr.baselines.chatgpt_siwc`.

Confirm `scr/baselines/bird_b0.py` uses 40 model calls, 40 total tool calls, 20 SQL executions, and recursion 200. Then run:

```bash
uv run python -m scr.cli.run_bird_b0_eval prepare --total-questions 500 --dev-ratio 0.8 --seed 42 --selection-id reproduce-full-500-40calls
uv run python -m scr.cli.run_bird_b0_eval infer --selection-id reproduce-full-500-40calls --split dev --run-id gpt6-luna-none-40calls --provider chatgpt-siwc --model gpt-6-luna --reasoning-effort none
uv run python -m scr.cli.run_bird_b0_eval infer --selection-id reproduce-full-500-40calls --split test --run-id gpt6-luna-none-40calls --provider chatgpt-siwc --model gpt-6-luna --reasoning-effort none
uv run python -m scr.cli.run_bird_b0_eval score --selection-id reproduce-full-500-40calls --split dev --run-id gpt6-luna-none-40calls --timeout-seconds 600
uv run python -m scr.cli.run_bird_b0_eval score --selection-id reproduce-full-500-40calls --split test --run-id gpt6-luna-none-40calls --timeout-seconds 600
```

Keep inference sequential when sharing a rotating ChatGPT refresh token. These commands produce a separate new result and do not overwrite this committed export. The fixed split is reused; changing limits does not resample it.
