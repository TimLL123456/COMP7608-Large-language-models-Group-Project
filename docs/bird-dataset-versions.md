# BIRD Dataset Version — Current Standard

**Current KORA default for new experiments:** BIRD **Mini-Dev 2026 SQLite**, pinned annotation revision `5b256b5a9c17478f06ed6912612e9a14d17065c8`.

- Questions: **500** across **11** SQLite databases.
- Deterministic project split: **400 local Dev / 100 local Test**. Neither split is the official hidden BIRD test.
- Dataset root for all new CLI operations: `data/bird/mini-dev-2026`.
- Evaluation input: question, evidence and schema; reference Gold SQL is evaluator-only.

## Install and verify

~~~bash
uv run python -m scr.datasets.setup_bird --release latest --revision 5b256b5a9c17478f06ed6912612e9a14d17065c8
uv run python -m scr.datasets.setup_bird --release latest --verify-only
~~~

Follow the [current setup guide](bird-setup.md) and [B0 evaluation guide](bird-b0.md#mini-dev-2026-current-workflow). If preparing a run manually, always pass `--dataset-root data/bird/mini-dev-2026` to prepare, infer and score; defaults may refer to original Mini-Dev.

## Version and evidence boundaries

The earlier **original Mini-Dev** contains a distinct annotation revision and question IDs and is retained exclusively for historical reproduction. Do not reuse its predictions, selections or scores for a 2026 experiment. A newer or broader BIRD Dev set is a separate study, not interchangeable with Mini-Dev 2026.

The [original B0 archive](../evaluation-results/b0-gpt6-luna-40calls-20261108/README.md) and [earlier 2026 B0 archive](../evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/README.md) remain available for historical analysis. The [detailed dataset-version investigation](history/bird-dataset-versions-pre-current-only-20261115.md) preserves previous watchlist corrections, download provenance and legacy instructions.

## Restored metadata descriptions

The [MetadataDiscoveryV2 experiment](../evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) used officially restored table/column descriptions; consult its [reproduction guide](../evaluation-results/metadata-discovery-v2-descriptions-20261111/reproduce.md) for an exact restoration procedure and integrity checks. Do not assume all local SQLite dataset installs include those CSVs.

Official source: [BIRD Mini-Dev 2026 release](https://huggingface.co/datasets/birdsql/bird_mini_dev/blob/5b256b5a9c17478f06ed6912612e9a14d17065c8/README.md).
