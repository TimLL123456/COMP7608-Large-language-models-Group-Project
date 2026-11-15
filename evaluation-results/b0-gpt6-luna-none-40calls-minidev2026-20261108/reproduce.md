# Reproduce dataset, split and scoring

Run from the Group Project directory containing pyproject.toml, using its project environment (`uv sync --frozen`).

```bash
uv run python -m scr.datasets.setup_bird --release latest --revision 5b256b5a9c17478f06ed6912612e9a14d17065c8
uv run python -m scr.datasets.setup_bird --release latest --verify-only
(cd evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108 && sha256sum -c checksums.sha256)
```

Compare the installed dataset manifest with the exported dataset_manifest.json, including annotation and database hashes. Initial download depends on upstream availability. Raw databases are not included in this archive.

Reuse dev.jsonl, test.jsonl and selection_manifest.json to preserve exact membership; do not resample. Inputs omit reference SQL. Gold answers remain evaluator-only.

Rescore the saved predictions without model calls:

```bash
uv run python -m scr.cli.evaluate_bird --variant B0 --split dev --dataset-root data/bird/mini-dev-2026 --predictions evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/dev/predictions.jsonl --output-dir results/reproduced-minidev2026 --run-id dev --timeout-seconds 600
uv run python -m scr.cli.evaluate_bird --variant B0 --split test --dataset-root data/bird/mini-dev-2026 --predictions evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/test/predictions.jsonl --output-dir results/reproduced-minidev2026 --run-id test --timeout-seconds 600
```

Expected scores: dev 235/400; test 59/100; overall 294/500. Use fresh output directories. Match evaluator/runtime versions when investigating differences. New inference is not required and need not reproduce identical predictions. See README.md for historical per-case budgets.
