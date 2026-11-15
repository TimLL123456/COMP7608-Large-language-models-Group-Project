# BIRD dataset versions and migration

Decision recorded 8 November 2026: use **Mini-Dev 2026 SQLite** for new harness comparisons. Preserve original Mini-Dev for historical reproduction. Full Dev 20251106 is optional future broader validation; this installer does not support it.

| Release | Purpose | Identity |
| --- | --- | --- |
| Original Mini-Dev | Reproduce archived B0: 299/500 = 59.8% EX | 500 questions, revision `f65faf4ae3b638c1fa6df1d3370c8d92c8366301` |
| Mini-Dev 2026 | Fresh baseline and controlled harness comparisons | 500 questions, IDs 0–499; reviewed revision `5b256b5a9c17478f06ed6912612e9a14d17065c8` |
| Full Dev 20251106 | Optional separate 1,534-question study | Separate dataset; not interchangeable with Mini-Dev |

## Install and run

The downloader uses Python and HTTPS only. Docker, a database server and root access are not required. It downloads the official SQLite seed layers directly from the public image registry, verifies SHA-256 digests and extracts database files without executing image code. Allow space for compressed layers plus extracted databases.

```powershell
# Resolve current annotations to a recorded immutable commit
uv run python -m scr.datasets.setup_bird --release latest
# Reproduce the reviewed annotation revision
uv run python -m scr.datasets.setup_bird --release latest --revision 5b256b5a9c17478f06ed6912612e9a14d17065c8
uv run python -m scr.datasets.setup_bird --release latest --verify-only
```

Latest installs separately in `data/bird/mini-dev-2026/`. Original remains in `data/bird/original-mini-dev/`. No-argument setup still selects original so archived reproduction commands remain valid. `--release original` makes this explicit. Existing installations are verified, never overwritten; choose a separate `--root` to install another revision. `--verify-only` is offline. Original manual ZIP/annotation installation remains supported; current installation requires network access to resolve image digests, even when database layers are cached. Current manual annotations are format-checked but marked unverified against Hugging Face.

The current database route uses the official per-database `3036197201/bird-mini-dev-sqlite` reviewed-release images, resolved to digests. Only the final seed database layer is downloaded; shared operating-system layers are skipped. Image indexes, platform manifests, configs and layer bytes are checked against their digests. A layout with layers after the seed fails rather than silently ignoring possible changes. It does not assume the legacy Google Drive ZIP is equivalent. Source annotation bytes, normalized annotations, image/platform/layer digests and database hashes are recorded. Verified compressed layers are cached under `data/bird/_downloads/image-layers/`. Rerunning after an interrupted installation reuses valid layers; a failed or corrupt download is not accepted. A future upstream layout/tag change fails explicitly and requires a reviewed installer update.

All new evaluation commands need `--dataset-root data/bird/mini-dev-2026`; otherwise they still use original Mini-Dev. For example:

```powershell
uv run python -m scr.cli.run_bird_b0_eval prepare --dataset-root data/bird/mini-dev-2026 --total-questions 500 --dev-ratio 0.8 --seed 42 --selection-id minidev2026-full
```

Use the same dataset root on `infer` and `score`, a new run ID, and your explicitly chosen model/provider. Current scoring requires the runner's matching `inference_manifest.json` beside predictions. Do not copy old manifests to make old predictions pass. The new deterministic 400/100 split is local, not an official hidden test or an unseen-database split. IDs and difficulty labels changed: do not reuse the old selection. Earlier exposure to related questions also limits claims of an untouched holdout.

## Questions and reference answers

The official SQLite JSONL contains `question_id`, `db_id`, `question`, `evidence`, `SQL`, and `difficulty` for all 500 records. Gold `SQL` is the reference answer, not a model prediction. Expected result rows are obtained by executing Gold SQL against matching databases. Keep reference SQL and result rows evaluator-only; agent input omits SQL. Do not expose reference files through agent filesystem tools.

## Fair harness comparisons

Run a fresh B0 baseline on 2026 inputs, then each variant using the same frozen dataset, model, evidence policy, tool permissions and budgets. Track EX, tokens, latency and model/tool/SQL calls. A difference from the old 59.8% is not evidence of harness improvement because the dataset changed. Report suspected annotation defects separately without silently removing failures or changing official references. Successful Gold execution alone does not prove semantic correctness.

## Watchlist correction

Version matters: the installed original Mini-Dev annotations match the official pinned bytes (SHA-256 `88ceb0710163cae46a256ecea8f0a8c98286599530b60587fda5c3cfe57d45d2`). In that release Q1526 really uses `Price = 1513.12` despite asking for 634.8; Q1322 groups by event and returns one distinct event count per group. Earlier checks against full Dev gave different SQL and must not be applied to Mini-Dev. Q587 contains `'<humor>'` in both Evidence and SQL, not an empty string. Other original Watchlist entries need version-specific semantic and database review; they are not 15 confirmed wrong answers. Current IDs 0–499 must not be matched numerically to original IDs.

## Validation status

Validated on the Linux server on 8 November 2026:

- **61 focused BIRD tests passed**, covering legacy behavior, release separation, JSONL, prediction provenance, registry digest rejection, verified-cache reuse and unsupported image layouts.
- The real pinned Mini-Dev 2026 installation completed with **PASS**: 500 questions, 11 SQLite databases, and a separate deterministic local 400/100 split.
- An independent `--verify-only` run passed, including database SHA-256 checks. Docker and root privileges were not used.
- All **500 Gold SQL queries compiled** with SQLite `EXPLAIN`; one representative Gold query per database (**11/11**) executed successfully with a five-second limit and no result truncation. This is not full Gold execution coverage or proof of semantic correctness.
- The original dataset and archived B0 results were preserved. No new model inference or model accuracy result is claimed.

To check an installed copy on Linux:

```bash
cd COMP7608-Large-language-models-Group-Project
uv run python -m scr.datasets.setup_bird --release latest
uv run python -m scr.datasets.setup_bird --release latest --verify-only
```

Both commands should print `"status": "PASS"` for the installed release. Initial downloads require HTTPS access to Hugging Face, Docker Hub and registry/CDN endpoints. Public registry rate limits or network outages can still cause download failures; rerun to reuse verified layers.

## Official sources

- [Mini-Dev 2026 release and database image links](https://huggingface.co/datasets/birdsql/bird_mini_dev/blob/5b256b5a9c17478f06ed6912612e9a14d17065c8/README.md)
- [SQLite questions and Gold SQL](https://huggingface.co/datasets/birdsql/bird_mini_dev/resolve/5b256b5a9c17478f06ed6912612e9a14d17065c8/data/mini_dev_sqlite.jsonl)
- [Full Dev 20251106](https://huggingface.co/datasets/birdsql/bird_sql_dev_20251106)


## Restoring description CSVs for Mini-Dev 2026

The reviewed SQLite seed-image installation can contain the 11 databases without description CSVs. The full Metadata Discovery V2 experiment on 11 November 2026 restored them from the complete package linked by the official Mini-Dev repository. See [the experiment reproduction instructions](../evaluation-results/metadata-discovery-v2-descriptions-20261111/reproduce.md) for pinned sources, hashes and commands.

Use `python -m scr.datasets.restore_bird_descriptions --help` through `uv run` for the local archive-based helper. It validates all table/column coverage before proposing CSV writes, uses exclusive file creation, refuses existing destination files, and checks that existing dataset hashes are unchanged. `--verify-existing` checks an already restored installation without rewriting it. The helper reads only CSV members; it does not extract the package's databases, annotations or gold SQL.

The official legacy package differs from the installed 2026 schemas in two documented places: `formula_1/constructors.csv` includes a nonexistent `wins` column, whose row is removed; `toxicology.element` is absent, so its two column names/types are supplied from the pinned official 2026 SQLite baseline schema. That supplement contains no invented semantic descriptions. Other schema mismatches fail. Raw downloads and installed dataset files remain ignored and are not committed.
