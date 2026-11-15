# KORA Metadata Agent — Implementation & Experiment Guide

**Status (Metadata v1):** Implemented; no completed v1 benchmark improvement is claimed in this guide. The separate **MetadataDiscoveryV2** A1/B1/C1 workflow reached [340/500 (68.00%) local EX](../evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) on Mini-Dev 2026. Do not attribute that result to Metadata v1.  
**Scope:** Same-Database Generalization (continual knowledge reuse), not unseen-database evaluation.  
**Code:** `scr/agents/metadata_agent.py`, `scr/metadata/engine.py`, `scr/cli/run_bird_metadata_eval.py`.

## 1. What this does

Metadata Agent is a **separate** KORA Text-to-SQL agent. It retains the existing read-only SQLite tools and B0's output parser, token/trace accounting and execution limits, but adds four note tools:

- `search_metadata_notes(query, table_name="")` — query scoped index summaries and bounded official description hints.
- `read_metadata_note(note_id)` — read one full scoped Markdown note.
- `create_metadata_note(note_type, table_name, concept_id, title, summary, keywords, body, source_refs)` — create a concise reusable note.
- `update_metadata_note(note_id, expected_revision, title, summary, keywords, body, source_refs)` — update with revision checking.

The engine hard-limits Markdown notes to **1,500 characters**, index summaries to **160**, keywords to **8**, search results to **5**, and per-question full-note reading to approximately **6,000 characters**. Notes live inside the named experiment's private result folder.

The engine identifies notes by **database + table + note type + concept ID**, not by keyword alone. Every note is marked provisional by default; source pointers are recorded but not independently certified as true business definitions. The agent must use table/schema/data investigation to ground meaning.

Example conceptual difference: the string “gross sales” in two distinct tables does not automatically mean the same formula or exclusions. Search can show both candidates within the same database, but the agent must verify scope before reuse.

## 2. Prepare data and install dependencies

Work from the `Group Project` directory (the one containing `pyproject.toml`), with BIRD Mini-Dev 2026 already installed:

```powershell
uv sync
uv run python -m unittest discover -s tests -t . -v
```

Run a focused offline check before any API calls:

```powershell
uv run python -m unittest tests.test_metadata_engine tests.test_metadata_agent -v
```

The original B0 `prepare` command remains the **shared selection creator**, not an instruction to run B0 inference. It creates immutable Dev/Test question lists **without exposing Gold SQL**:

```powershell
uv run python -m scr.cli.run_bird_b0_eval prepare `
  --dataset-root data/bird/mini-dev-2026 `
  --total-questions 500 --dev-ratio 0.8 --seed 42 `
  --selection-id metadata-full-001
```

Adjust `--dataset-root` to the actual installed dataset. The full selection uses the existing project's 400/100 deterministic split. For a cheap **smoke test**, make a *different* selection with `--total-questions 5` and unique IDs.

## 3. Inference: Dev and Test share one experiment store

**Default example below:** original NVIDIA B0 model and `generalized-v1` prompt. Configure `NVIDIA_API_KEY` locally, or choose a supported provider/model with required local credentials. **No API key is stored in results.**

Dev: starts one **new empty store**, and creates/updates notes across its questions:

```powershell
uv run python -m scr.cli.run_bird_metadata_eval infer `
  --selection-id metadata-full-001 `
  --dataset-root data/bird/mini-dev-2026 `
  --split dev --run-id metadata-dev-001 `
  --experiment-id metadata-001 `
  --prompt-variant generalized-v1
```

Test: reuses **the same writable store** and can continue updating it; no reset between splits:

```powershell
uv run python -m scr.cli.run_bird_metadata_eval infer `
  --selection-id metadata-full-001 `
  --dataset-root data/bird/mini-dev-2026 `
  --split test --run-id metadata-test-001 `
  --experiment-id metadata-001 `
  --prompt-variant generalized-v1
```

The same experiment ID must also have **matching model, provider, prompt, dataset selection, SQL preview limit and budgets**. Each new experiment ID starts empty; existing experiment IDs cannot be silently reset or overwritten. This v1 runner requires Dev to complete before Test begins, but **does not add any new scoring gate**.

**Important:** Partial/incomplete inference can leave an experiment folder for investigation. Do not delete/reuse it accidentally; start a fresh experiment ID for a fresh run. The v1 runner does not support resuming a half-finished split automatically.

### Supported providers

The Metadata CLI reuses the same model factory and `--provider`/`--model`/`--reasoning-effort` options as B0. Example SIWC:

```powershell
uv run python -m scr.cli.run_bird_metadata_eval infer `
  --selection-id metadata-full-001 `
  --dataset-root data/bird/mini-dev-2026 `
  --split dev --run-id metadata-dev-siwc `
  --experiment-id metadata-siwc-001 `
  --provider chatgpt-siwc --model YOUR_MODEL `
  --reasoning-effort high
```

Model availability and valid effort settings depend on your configured provider. Do not mix provider/model settings between Dev and Test of the same experiment.

## 3A. Safely resume a partially completed inference run

**Use only after stopping any currently running inference process.** Do not
start two writers for the same experiment at the same time.

If a prior Dev or Test `infer` stopped after writing several complete
predictions, you can attempt to continue the **same run** without repeating
those questions. Use the same dataset selection, exact run ID, experiment ID,
provider, model, prompt, reasoning settings and preview-row setting, but add
`--resume`:

```powershell
uv run python -m scr.cli.run_bird_metadata_eval infer `
  --selection-id metadata-full-001 `
  --dataset-root data/bird/mini-dev-2026 `
  --split dev --run-id metadata-dev-001 `
  --experiment-id metadata-001 `
  --prompt-variant generalized-v1 `
  --provider chatgpt-siwc --model YOUR_EXISTING_MODEL `
  --resume
```

The command **refuses** to resume unless every saved prediction and trace is
valid JSON, forms the exact completed-prefix of the selected question order,
matches the expected database/provider/model, and is consistent with note
create/update revision events and on-disk note hashes. Any metadata tool
activity from a not-yet-completed question is treated as evidence that note
state might have changed; the command **stops instead of inventing a
rollback**. It will not overwrite completed predictions or traces.

For older partial runs created before `--resume` existed, this strict audit
can accept a clean prefix even without checkpoint files. If the audit rejects
the old run, preserve it and start a **new experiment ID**; there is no
automatic repair or destructive reset of the old knowledge store. A successful
resume is recorded as `resumed_from_questions` in the final inference
manifest.

### Historical model-label correction (non-destructive)

The original Metadata Runner reused B0's `run_one()` and inherited its
hardcoded NVIDIA model value **inside `traces.jsonl.report.model`**, even
when the configured provider/model in `predictions.jsonl` was different.
New records now set `report.model` to the configured model name. Previously
saved traces are **not rewritten**. On successful resume, mismatches matching
this known historical default are documented in the additive audit file:

```text
Metadata/<split>/<run-id>/trace_model_corrections.jsonl
```

The configured model is taken from the selected CLI/provider configuration,
not inferred from the old trace label. This fixes report consistency; it does
not independently prove which model the provider executed. Verify API/provider
response metadata if model provenance is disputed. Existing inference results,
SQL, and the scorer are unchanged.

## 4. Outputs and trace inspection

```text
scr/evaluation/result/<selection-id>/
  B0/                             # historical control; unchanged
  Metadata/
    dev/<run-id>/
      predictions.jsonl
      traces.jsonl
      inference_manifest.json
    test/<run-id>/
      predictions.jsonl
      traces.jsonl
      inference_manifest.json
    experiments/<experiment-id>/
      experiment_manifest.json
      knowledge_operations.jsonl  # question-id + db + operation/result
      knowledge/<db-id>/
        index.json
        notes/<note-id>.md
```

Per-run inference manifests record knowledge checksums **before and after** the run. Metadata operations are logged without copying the full note content. Traces use the same B0 `structured_events` format and show metadata tool calls/results.

View a run with the existing offline trace renderer (no model request):

```powershell
uv run python -m scr.cli.run_bird_metadata_eval visualize `
  --selection-id metadata-full-001 --split dev --run-id metadata-dev-001
```

## 5. Independent scoring (operator controlled)

Metadata Inference does **not** import `BirdEvaluationReferences` or score SQL. Only the existing evaluator sees Gold SQL, after predictions are saved.

```powershell
uv run python -m scr.cli.run_bird_metadata_eval score `
  --selection-id metadata-full-001 `
  --dataset-root data/bird/mini-dev-2026 `
  --split dev --run-id metadata-dev-001

uv run python -m scr.cli.run_bird_metadata_eval score `
  --selection-id metadata-full-001 `
  --dataset-root data/bird/mini-dev-2026 `
  --split test --run-id metadata-test-001
```

Scoring uses the same SQL execution accuracy (EX) algorithm, with evaluation variant label `Metadata`. The wrapper verifies prediction IDs, model, manifest and checksum before invoking the evaluator. **You choose when to score; this runner does not demand Dev+Test both finish first.**

## 6. Controlled B0 / generalized-v1 comparison

Use the existing B0 runner on the **same selection**, ideally with `--prompt-variant generalized-v1` and the **same provider, exact model, reasoning effort, max token budget, timeout and sampling settings**. The Metadata Agent adds metadata tools/instructions; it keeps the original model/tool-call ceilings, so extra tools count against the same total budget.

The historical generalized-v1 result may have different configurations. If settings are different, do **not** attribute EX changes solely to metadata.

After running scores for both variants:

```powershell
uv run python -m scr.cli.compare_metadata_runs `
  --control-scores scr/evaluation/result/metadata-full-001/B0/test/CONTROL_RUN/scores/per_question.jsonl `
  --metadata-scores scr/evaluation/result/metadata-full-001/Metadata/test/metadata-test-001/scores/per_question.jsonl `
  --output scr/evaluation/result/metadata-full-001/metadata-comparison.md
```

The comparison validates matching question IDs, database IDs, and difficulty labels. Report:

- Total EX and by-database/by-difficulty EX, fixed and regressed question IDs.
- Tokens (including cached/reasoning where actually observed), model/SQL/total tool calls and latency.
- Knowledge searches, note reads/creates/updates, revision conflicts, rejected writes, and cross-question reuse from `knowledge_operations.jsonl`.

Inspect traces before claiming a particular note caused an improvement. This design evaluates **order-dependent continual same-database knowledge reuse**, not a frozen independent-test benchmark or cross-database generalization.

## 7. Known limitations and safeguards

- Notes are **provisional** even when they carry source references. The engine checks reference syntax, but does not semantically verify every natural-language claim; investigate and report hallucinated notes.
- Retrieval is deterministic lexical matching; it can miss synonyms/indirect relationships.
- The store uses local sequential file writes, intended for one experiment runner process. Parallel writers are **not supported** in v1.
- The strict resume audit intentionally refuses runs if partial-question metadata activity or inconsistent note revisions make recovery unsafe; it never silently rolls back knowledge.
- The engine stores a short index and Markdown per note. If a process is terminated between separate filesystem replacements, an incomplete transaction may require manual inspection. Never silently reuse a corrupted experiment.
- Word/keyword scopes are not intrinsically semantic; correctness depends on agent investigation. Similar keywords in different databases/tables are **never merged automatically**.
- Test performance is order-dependent, because knowledge created during Test remains available to later Test questions. Freeze question order and report this caveat.
- Local Mini-Dev Test questions are not an unseen official BIRD hidden-test set, and some have been reviewed during project development.
- No automatic full 500-question model evaluation should be claimed until actual credentials, dataset and completed result manifests are available.

## Metadata Discovery V2

See [Metadata Discovery V2](metadata-discovery-v2.md) for the independent A1/B1/C1 workflow, evaluation, configuration and metadata definitions.
