# KORA-02 — BIRD Mini-Dev Dataset Setup

> **Dataset update — 8 November 2026:** Use **Mini-Dev 2026** for new harness experiments. The original Mini-Dev instructions and archived 59.8% EX remain historical reproduction evidence. See [dataset versions and migration](bird-dataset-versions-pre-current-only-20261115.md) for the Docker-free download command, changed IDs, and fresh evaluation workflow. Full Dev 20251106 is a separate optional benchmark.

**Goal:** Install and verify **Mini-Dev 2026 SQLite**: 500 questions and 11 databases. Python downloads the files directly over HTTPS; Docker and administrator/root privileges are not required. Original Mini-Dev remains available for historical reproduction. The local 400 dev / 100 test split is **not** BIRD's official hidden test.

> **Start here:** Steps 1–3 are the normal first-time setup. Steps marked **Optional** are for troubleshooting or developers.

## 1. Install dependencies — Required

**What:** Prepare Python and the project libraries. **Why:** The downloader and database loader need them.

Open PowerShell or a Linux terminal in the **project root** (the folder containing `pyproject.toml`).

Clone the group repository in PowerShell or a Linux terminal.

```sh
git clone https://github.com/TimLL123456/COMP7608-Large-language-models-Group-Project.git
cd COMP7608-Large-language-models-Group-Project
uv sync
```

On Windows, you can verify the checkout and tool versions in PowerShell.

```powershell
Test-Path .\pyproject.toml      # Expected: True
python --version                # Python 3.11–3.14
uv --version                    # Install uv if missing: https://docs.astral.sh/uv/
uv sync
```

**Expected:** Dependencies install without errors. Run the following commands from this same project root.

## 2. Download and install BIRD — Required

**What:** Download current question annotations and verified SQLite database seed layers directly over HTTPS. The resolved annotation commit and image/layer/database hashes are recorded for reproducibility. Container software is not required.

```powershell
uv run python -m scr.datasets.setup_bird --release latest
```

**Expected:** JSON output containing `"status": "PASS"`, `"questions": 500`, `"databases": 11`, `"dev": 400`, and `"test": 100`. The command may take time because the database files are large. Verified compressed layers are cached for retries.

The installer validates files, creates the fixed split (seed 42) and saves data under:

```text
data/bird/mini-dev-2026/
├── annotations.source.jsonl  # original downloaded question/reference records
├── annotations.json
├── dataset_manifest.json
└── package/                 # extracted SQLite databases and descriptions
```

**Do not commit** downloaded datasets, gold SQL or archives. `data/bird/` is Git-ignored. Re-running setup with an existing installation verifies it instead of downloading it again.

## 3. Verify your installation — Required

**What:** Check the downloaded dataset without using the network. **Why:** Catch missing or modified files before running the agent.

```powershell
uv run python -m scr.datasets.setup_bird --release latest --verify-only
```

**Expected:** `"status": "PASS"` with 500 questions, 11 databases, 400 dev and 100 local-test questions.

The check covers file hashes, database schemas, annotations and saved split membership. It **does not run an LLM or calculate SQL accuracy**.

**Next:** Follow [Mini-Dev 2026: Prepare → Infer → Score → Visualize](bird-b0-pre-current-only-20261115.md#mini-dev-2026-current-workflow), using `--dataset-root data/bird/mini-dev-2026` on every prepare/infer/score command. Those command defaults still select the original dataset. Use fresh selection/run IDs; never reuse old predictions because question IDs and annotations changed.

Example preparation (no model calls):

```bash
uv run python -m scr.cli.run_bird_b0_eval prepare --dataset-root data/bird/mini-dev-2026 --total-questions 5 --dev-ratio 0.8 --seed 42 --selection-id minidev2026-smoke
```

For a fixed reviewed annotation commit, append `--revision 5b256b5a9c17478f06ed6912612e9a14d17065c8` to initial setup. Existing installations are verified, not refreshed in place; use a separate `--root` for another revision.

## Original Mini-Dev reproduction — Optional

No-argument setup continues to select the original release for compatibility. The explicit route is:

```bash
uv run python -m scr.datasets.setup_bird --release original
uv run python -m scr.datasets.setup_bird --release original --verify-only
```

This installs/verifies `data/bird/original-mini-dev/`. The manual ZIP instructions below apply only to this original release, not Mini-Dev 2026.

## 4. Original release: manual archive fallback — Optional

**When:** The normal download cannot fetch the official database ZIP, or Google Drive has throttled access.

Download the complete ZIP from the [official archive](https://drive.google.com/file/d/13VLWIwpw5E3d5DUkMvzw7hvHE67a4XkG/view), then run:

```powershell
uv run python -m scr.datasets.setup_bird --archive "D:\Downloads\mini_dev_complete.zip"
```

The annotations still download automatically from the pinned Hugging Face version. **Skip this section if Step 2 passed.**

### Fully offline setup — Optional

**When:** Both the database ZIP and annotation JSON are already downloaded.

```powershell
uv run python -m scr.datasets.setup_bird `
  --archive "D:\Downloads\mini_dev_complete.zip" `
  --annotations "D:\Downloads\mini_dev_sqlite-00000-of-00001.json"
```

Use the original SQLite annotation file from the pinned revision below. Manual annotations receive the provenance label `manual_annotation_unverified_against_hf`. Their format is validated, but the installer cannot prove they match the official pinned bytes while offline.

**Important:** Back up a damaged existing `data/bird/original-mini-dev/` installation before moving or replacing it. The installer will not overwrite an installed dataset in place.

## 5. Explore the current loader — Optional (developers)

**Why:** Understand how B0–B4 retrieve questions and schemas without exposing the gold SQL to the agent.

```python
from scr.datasets.bird import BirdDataset

bird = BirdDataset("data/bird/mini-dev-2026")
questions = bird.load_questions()
print(len(questions))                            # 500
print(len(bird.get_split("dev")))                 # 400
print(len(bird.get_split("test")))                # 100

qid = questions[0]["question_id"]                # Use real ID, never list position
agent_input = bird.get_agent_input(qid)
print(agent_input["question"])
assert "SQL" not in agent_input                  # Reference SQL stays evaluator-only

print(bird.get_schema(agent_input["db_id"]))
print(bird.get_database_path(agent_input["db_id"]))
```

The deterministic local split groups questions by database and difficulty, then assigns **100 test and 400 dev questions** with seed 42. The two sets can contain questions from the same SQLite database. `test` is **not** an unseen-database or official hidden-test split. Do not tune your agent on local-test results.

Gold-reference isolation is a **code convention**, not a filesystem security boundary: do not grant the model unrestricted access to evaluation reference files.

## 6. Troubleshooting and tests — Optional

| Problem | Action |
| --- | --- |
| `No pyproject.toml found` | Move to the project root; verify `Test-Path .\pyproject.toml` returns `True` |
| Missing `gdown` / `huggingface_hub` | Run `uv sync` |
| Original-release ZIP blocked or throttled | Use the original-release manual archive fallback above |
| Wrong question count or unexpected schema | Confirm release and dataset root; both supported releases have 500 questions but different annotations and IDs |
| Docker permission error | Update to the latest PR branch: current downloads do not use Docker |
| HTTPS or registry rate-limit error | Wait as directed by the service, then rerun; verified layers are reused |
| Failed hash or SQLite integrity check | Back up the dataset, restore from trusted sources, and verify again |
| Python tests import wrong `tests` package | Use `uv run python -m unittest discover -s tests -t . -v` |

```powershell
# Offline unit tests — do not replace the real-data verification in Step 3
uv run python -m unittest discover -s tests -t . -p "test_bird*.py" -v
```

### Original release provenance — Advanced

For current 2026 sources and validation, see [dataset versions and migration](bird-dataset-versions-pre-current-only-20261115.md). The following references describe the original release.

- [Official BIRD Mini-Dev annotations](https://huggingface.co/datasets/birdsql/bird_mini_dev), pinned revision `f65faf4ae3b638c1fa6df1d3370c8d92c8366301`; file `data/mini_dev_sqlite-00000-of-00001.json`.
- [Official complete database archive](https://drive.google.com/file/d/13VLWIwpw5E3d5DUkMvzw7hvHE67a4XkG/view). The Drive file ID does **not** provide a content-addressed version.
- [Upstream Mini-Dev project](https://github.com/bird-bench/mini_dev). Mini-Dev V2 is a different release and is excluded.
- `dataset_manifest.json` stores the archive/annotation/database SHA-256 hashes, source verification status, seed and split membership. Keep that provenance for reproducible evaluations.
- Historical `heldout` split names are supported when reading old data; new commands use `dev` and `test`.
- `setup_bird` installs the entire dataset. B0's `prepare --force` only replaces an **unused sampled selection**, never the dataset.

**Responsibility:** KORA-02 owns dataset setup. KORA-03 owns scoring; KORA-05 owns agent inference. A successful unit test does not establish that the real dataset download or final EX scoring succeeded.
