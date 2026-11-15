# BIRD Mini-Dev 2026 — Current Setup Guide

**Dataset:** BIRD Mini-Dev 2026 (500 questions, 11 SQLite databases; local Dev 400 / local Test 100). This local split is **not** the official hidden BIRD Test. Use this release for new KORA research and evaluation.

## 1. Install dependencies — Required

From the root of the cloned [Group Project repository](../README.md), where `pyproject.toml` is located:

~~~bash
uv sync
~~~

Use Python and [uv](https://docs.astral.sh/uv/). No Docker runtime or root access is required for the supported SQLite download workflow.

## 2. Install the pinned dataset — Required

~~~bash
uv run python -m scr.datasets.setup_bird --release latest --revision 5b256b5a9c17478f06ed6912612e9a14d17065c8
~~~

The installer downloads and verifies the official SQLite dataset and question annotations via HTTPS. The dataset lives under `data/bird/mini-dev-2026/` by default and is ignored by Git. Preserve enough disk space for downloads plus extracted database files.

For verification without re-downloading:

~~~bash
uv run python -m scr.datasets.setup_bird --release latest --verify-only
~~~

Expect a PASS with 500 questions, 11 databases and the local 400/100 split. Stop and investigate if hashes, database integrity or dataset provenance do not match.

## 3. Prepare a reproducible selection — Required

~~~bash
uv run python -m scr.cli.run_bird_b0_eval prepare \
  --dataset-root data/bird/mini-dev-2026 \
  --total-questions 5 --dev-ratio 0.8 --seed 42 \
  --selection-id minidev2026-smoke-001
~~~

A five-question selection creates **four local Dev questions and one local Test question**; it is only a smoke test, not a representative performance study. Always pass the same `--dataset-root`, `--selection-id` and release to inference and scoring. Use fresh selection IDs if the destination already exists.

Next: [Run B0 → Score → Visualize](bird-b0.md#mini-dev-2026-current-workflow).

## Provider authentication

Model inference uses your selected provider and may consume paid quota; dataset setup and offline scoring do not. For ChatGPT SIWC, explicitly authorize the client locally and inspect available slugs:

~~~bash
uv run python -m scr.baselines.siwc_auth
uv run python -m scr.baselines.chatgpt_siwc
~~~

For other supported providers, supply credentials securely through local environment variables. Never commit tokens or a real `.env` file. See [B0 provider reference](bird-b0.md#optional-other-model-providers).

## Troubleshooting

- **Version mismatch:** do not reuse selections or prediction manifests created for original Mini-Dev; use the explicit 2026 dataset root.
- **Network/rate-limit error:** retry verification or installation; only hash-verified cached layers are reusable.
- **Existing installation mismatch:** do not overwrite official dataset files silently; inspect the recorded hashes and provenance.
- **Missing optional column descriptions:** some studies additionally restore official description CSVs. Follow the [MetadataDiscoveryV2 experiment reproduction instructions](../evaluation-results/metadata-discovery-v2-descriptions-20261111/reproduce.md) rather than assuming description availability.
- **Cannot reach a model provider:** verify authentication separately. Setup and offline evaluator tests do not require a model API call.

For the original Mini-Dev installer, extra reproducibility detail and old setup paths, see the [dated setup snapshot](history/bird-setup-pre-current-only-20261115.md) and [dataset-version history](history/bird-dataset-versions-pre-current-only-20261115.md).
