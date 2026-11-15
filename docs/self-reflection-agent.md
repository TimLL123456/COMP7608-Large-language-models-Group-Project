# Self Reflection Agent — Current SQL-First Workflow

**Variant:** `SelfReflection` · **Implemented and evaluated:** 13 November 2026

**Latest result:** [350/500 (70.00%) local strict EX](../evaluation-results/self-reflection-full-20261113/README.md) on BIRD Mini-Dev 2026 (Dev 280/400; local Test 70/100). Final SQL was produced for **498/500** questions. This is not the official hidden BIRD Test.

## Architecture

~~~text
Question / Evidence
  → B0 schema and data investigation → candidate SQL
  → Independent SQL Reflection Reviewer
      PASS → accept executable candidate (provisional)
      FAIL with actionable evidence → retry fresh B0 within budget
      UNCERTAIN / ERROR / exhausted → keep best eligible executable SQL
  → Final SQL + decision/report/trace
~~~

The original B0 agent is reused rather than rewritten. The Reviewer checks read-only execution and material requirements such as output schema, filters, metric calculation, grain, temporal logic, relationships/joins and value semantics. Its PASS/FAIL/UNCERTAIN/ERROR verdict is **not** an independent EX score. An unresolved concern does not automatically suppress a safe, executable candidate; unsafe or non-executable SQL must not be returned as a usable answer.

The workflow supports up to **three B0 attempts** and bounded model/inspection calls for independent reviews. Actual limits, retry conditions and observed usage are recorded in run manifests. See the [archived full-run methods, traces and limitations](../evaluation-results/self-reflection-full-20261113/README.md).

## Run the agent

Install [BIRD Mini-Dev 2026](bird-setup.md) and prepare a uniquely named selection using the [B0 CLI](bird-b0.md#mini-dev-2026-current-workflow). With provider credentials configured, run from the project root:

~~~bash
uv run python -m scr.cli.run_bird_self_reflection_eval infer \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id YOUR_SELECTION --split dev --run-id reflection-dev-001 \
  --provider chatgpt-siwc --model gpt-6-luna \
  --reasoning-effort none --prompt-variant generalized-v1

uv run python -m scr.cli.run_bird_self_reflection_eval score \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id YOUR_SELECTION --split dev --run-id reflection-dev-001

uv run python -m scr.cli.run_bird_self_reflection_eval visualize \
  --selection-id YOUR_SELECTION --split dev --run-id reflection-dev-001
~~~

Use unused run IDs and the same frozen dataset, selection, provider, prompt and configuration for Dev/Test. Inference can consume provider quota. Scoring uses evaluator-only gold SQL and does not call the model.

## Outputs

The run writes predictions, manifests, traces and independent reviewer reports under the selection's `SelfReflection` result path, followed by `scores/` after scoring. Keep archived experimental results immutable; create a new run to repeat an experiment.

## Historical research

Earlier V1.1 design, original reviewer rubric, implementation notes and before-benchmark claims are preserved in the [dated Self Reflection design snapshot](history/self-reflection-agent-pre-current-only-20261115.md). The authoritative completed run and methodology remain in the [13 November experiment archive](../evaluation-results/self-reflection-full-20261113/README.md).
