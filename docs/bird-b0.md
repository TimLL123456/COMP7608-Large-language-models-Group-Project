# B0 Text-to-SQL — Current Run and Evaluation Guide

Use **BIRD Mini-Dev 2026** for new experiments. The baseline generates read-only SQLite SQL through its tools; an independent scorer computes execution accuracy (EX). Historical runs and legacy dataset commands are linked under [Historical Research](history/README.md).

## Mini-Dev 2026: current workflow

Run from the cloned Group Project root. Follow the [setup guide](bird-setup.md) first:

~~~bash
uv sync
uv run python -m scr.datasets.setup_bird --release latest --revision 5b256b5a9c17478f06ed6912612e9a14d17065c8
uv run python -m scr.datasets.setup_bird --release latest --verify-only
uv run python -m scr.cli.run_bird_b0_eval prepare \
  --dataset-root data/bird/mini-dev-2026 \
  --total-questions 5 --dev-ratio 0.8 --seed 42 \
  --selection-id minidev2026-smoke-001
~~~

Preparation creates a small selection of four local Dev questions and one local Test question. It is a smoke test, **not** full-dataset model performance evidence.

## 1. First-time checks — Required

Choose an available model/provider and authenticate locally. The B0 default provider is NVIDIA and requires its credential. Alternatively, authorize ChatGPT SIWC explicitly:

~~~bash
uv run python -m scr.baselines.siwc_auth
uv run python -m scr.baselines.chatgpt_siwc
~~~

Use the exact model slug available to your signed-in account. Provider availability and reasoning-effort options vary.

## 2. Prepare sample questions — Required

The `prepare` command in the current workflow above builds a reproducible frozen selection. Use unique selection IDs and matching dataset paths for all subsequent commands. Reference SQL stays in the evaluator, never in the agent prompt.

## 3. Run B0 inference — Required

This example uses the previously tested ChatGPT SIWC model slug, subject to current account availability:

~~~bash
uv run python -m scr.cli.run_bird_b0_eval infer \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id minidev2026-smoke-001 --split dev \
  --run-id b0-smoke-001 \
  --provider chatgpt-siwc --model gpt-6-luna \
  --reasoning-effort none --prompt-variant generalized-v1 \
  --preview-rows 20
~~~

Inference generates predictions and trace files and consumes provider usage. For each new experiment, use a new run ID. Preserve model configuration, prompt variant and resource budgets in the output manifest.

## 4. Score the predictions — Required for EX evaluation

~~~bash
uv run python -m scr.cli.run_bird_b0_eval score \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id minidev2026-smoke-001 --split dev \
  --run-id b0-smoke-001
~~~

Scoring reads existing predicted SQL and independent Gold SQL results, not a model API. Read the saved `scores/report.md`, `per_question.csv` and manifest. See [execution-accuracy definitions and safeguards](bird-evaluation.md).

## 5. Visualize the agent trace — Optional

~~~bash
uv run python -m scr.cli.run_bird_b0_eval visualize \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id minidev2026-smoke-001 --split dev \
  --run-id b0-smoke-001
~~~

The trace viewer helps inspect questions, SQL generation, read-only tool calls and errors. Tracing does not replace EX evaluation.

## Optional: Other model providers

B0 supports explicitly selected providers such as NVIDIA, Ollama, Gemini, DeepSeek and experimental ChatGPT SIWC, depending on the configured environment. Set provider-specific authentication locally and pass supported `--provider` and `--model` arguments. Do not silently substitute a provider or assume a particular login grants every model.

## Latest completed full B0 benchmark

The completed **B0 generalized-v1** run achieved [319/500 (63.80%) local EX](../evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/README.md) on Mini-Dev 2026. The archived report documents its exact 40/40/40 limits and retry provenance. It is not a controlled, matched-budget comparison to other agent variants.

For past original-release commands and earlier baseline configurations, follow the [previous complete B0 guide](history/bird-b0-pre-current-only-20261115.md); older experiment data remains unchanged.
