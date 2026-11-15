> **Completed Metadata Discovery V2 evaluation with restored descriptions:** 340/500 EX (68.00%): Dev 272/400, local Test 68/100. Historical generalized-v1 B0 comparison is +4.20 percentage points with 9.11× observed input tokens and 5.86× inference time; descriptions and resource-budget effects are not separately established. [Results, evidence and reproduction](../../evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md).

# KORA — COMP7608B Group Project


## Research status — 15 November 2026

**This repository is the canonical shared home for the KORA group project.** Use [BIRD Mini-Dev 2026](bird-dataset-versions-pre-current-only-20261115.md) for current studies (400 local Dev / 100 local Test, not the official hidden test).

| Research variant | Completed local strict EX | Implementation and results |
| --- | ---: | --- |
| B0 generalized-v1 | **319/500 (63.80%)** | [B0 CLI](../../scr/cli/run_bird_b0_eval.py) · [evaluation](../../evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/README.md) |
| [Metadata v1](../../scr/agents/metadata_agent.py) | No archived full run | Original metadata workflow |
| **MetadataDiscoveryV2** | **340/500 (68.00%)** | [A1/B1/C1 design and commands](../metadata-discovery-v2.md) · [implementation](../../scr/agents/metadata_discovery_v2.py) · `--workflow metadata-discovery-v2` · [evaluation](../../evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) |
| Self Reflection Agent | **350/500 (70.00%)** | [agent guide](self-reflection-agent-pre-current-only-20261115.md) · [evaluation](../../evaluation-results/self-reflection-full-20261113/README.md) |
| Rubric Self Reflection | **326/500 (65.20%)** | [agent guide](../rubric-self-reflection-agent.md) · [evaluation](../../evaluation-results/rubric-self-reflection-full-20261115/README.md) |
| Role-Specialized Self Reflection | **Not yet benchmarked** | [Luna/Terra roles and two-shard parallel workflow](../role-specialized-self-reflection-agent.md) |

The six preserved [experiment archives](../../evaluation-results) also include two historical B0 runs: [**299/500 (59.8%)** on the original Mini-Dev](../../evaluation-results/b0-gpt6-luna-40calls-20261108/README.md) and [**294/500 (58.8%)** on Mini-Dev 2026](../../evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/README.md) with mixed recorded SQL-call budgets. **These experiments do not all share the same compute budget, retry policy, dataset version or execution context; differences in EX are descriptive rather than causal claims.** Some runs include repaired transport/DNS failures; read each archive's provenance. Metadata v1 remains distinct from MetadataDiscoveryV2. The interactive KORA application, reliability scenarios and final integration are not established by these offline SQL benchmarks.

Current implementations are under [`scr/`](../../scr), regression tests under [`tests/`](../../tests), and methods/reproducibility in [developer docs](agent-development-pre-current-only-20261115.md). Historical November 3 v4.4 material is retained below as a dated snapshot.

> **Completed generalized-v1 evaluation:** 319/500 EX (63.80%), with full RCA and performance review: [results and report](../../evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/README.md). Historical comparison is descriptive; see budget and retry caveats.


> **Archived B0 evaluation (10 November 2026):** Ran only `generalized-v1` on all 500 Mini-Dev 2026 questions (400 Dev / 100 local Test), with **40 model calls / 40 total tool calls / 40 SQL executions**. SQL executions share the total-tool budget. No new original-baseline inference is requested. Previous Mini-Dev 2026 B0 configuration metadata also lists 40/40/40; its preserved execution history still documents the original 20-SQL cases and two 40-SQL reruns. Historical scores are descriptive comparisons, not a newly matched control. See [B0 workflow](bird-b0-pre-current-only-20261115.md).

> **Dataset update — 8 November 2026:** Use **Mini-Dev 2026** for new harness experiments. The original Mini-Dev instructions and archived 59.8% EX remain historical reproduction evidence. See [dataset versions and migration](bird-dataset-versions-pre-current-only-20261115.md) for the Docker-free download command, changed IDs, and fresh evaluation workflow. Full Dev 20251106 is a separate optional benchmark.

**Group 9 · 2026–2027 Semester 1** · Research status updated 15 November 2026; v4.4 snapshot dated 3 November 2026

KORA is a Text-to-SQL research project with multiple implemented agent variants and preserved local BIRD Mini-Dev 2026 evaluations. The B0 Deep Agent and read-only SQLite/evaluation utilities remain reusable. The historical B1–B4 roadmap does not by itself describe all current experiments; the interactive API/UI and end-to-end demo remain separate planned work.

**Start with the tutorials.** You do not need to read the long research plan before running your first B0 test.


## Historical B0 evaluation archive — BIRD Mini-Dev 2026 (9 November 2026)

The archived Luna B0 run on **Mini-Dev 2026** scored **294/500 = 58.8% execution accuracy** (Development 235/400; local Test 59/100). This historical B0 analysis used matching pinned official Gold SQL, scores, and observable agent traces to investigate failure patterns by **database, query category, table/column semantics, SQL grain, and agent tool behavior**. It proposed E1–E5 follow-up experiments at that time; later independently archived agent experiments are listed in the current status table above. This historical analysis was not itself a fresh model inference. The follow-up RCA now compares **all 165 Development failures** against matching pinned 2026 Gold/final Agent SQL: **153 provisional candidate categories and 12 unresolved**, with no fresh database re-execution.

| Read | Purpose |
| --- | --- |
| **[繁體中文完整分析](../../evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/analysis-report/baseline-analysis-zh-HK.md)** | Updated 12-section report with 165-failure RCA breakdown, trace findings, evidence tiers and next experiments |
| **[English analysis](../../evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/analysis-report/baseline-analysis-en.md)** | Equivalent updated English RCA and baseline findings for project collaboration |
| **[Gold vs Agent SQL case studies](../../evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/analysis-report/case-studies.md)** | 114 documented SQL/trace case studies (97 original + 17 added); offline research only |
| **[165 Development failures — CSV](../../evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/analysis-report/failure-inventory.csv)** | All 165 Dev failures reviewed with candidate primary cause, per-case evidence, review basis and counterfactual status |

**Dataset/version and reproducibility:** These reports apply only to the [Mini-Dev 2026 frozen run](../../evaluation-results/b0-gpt6-luna-none-40calls-minidev2026-20261108/reproduce.md), not the [historical Original Mini-Dev baseline](../../evaluation-results/b0-gpt6-luna-40calls-20261108/analysis-report/baseline-analysis-zh-CN.md). Gold SQL excerpts are **offline research/evaluator-only**; exclude the analysis files from agent prompts or retrieval corpora. The frozen run README, prediction/trace/score files and `checksums.sha256` remain untouched to preserve checksum verification. RCA categories are **not verified fixes**; Gold-derived research material must not be ingested by the agent.

## Start here — beginner workflow

| Read in this order | What you will learn |
| --- | --- |
| **[1. Install BIRD dataset](bird-setup-pre-current-only-20261115.md)** | Download and verify Mini-Dev 2026 without Docker |
| **[2. Run B0: Prepare → Infer → Score → Visualize](bird-b0-pre-current-only-20261115.md)** | Execute a small agent test, inspect predictions and create a trace graph |
| **[3. Understand EX accuracy](bird-evaluation-pre-current-only-20261115.md)** | Compare the final SQL result to gold reference results |
| **[4. Extend B0 to B1–B4](agent-development-pre-current-only-20261115.md)** | Find shared modules and experiment contracts (developers) |
| **[5. Roadmap and tickets](progress-planning-pre-current-only-20261115.md)** | Current status, acceptance criteria, milestones and unresolved scope decisions |

> **Required** instructions come first in each tutorial. Manual downloads, custom sampling, low-level scoring and live visualization are marked **Optional** or **Advanced**.

## Additional B0 providers (API key and ChatGPT sign-in)

B0 inference now supports `--provider` and `--model` while keeping the original
NVIDIA default. The existing Ollama, Gemini and DeepSeek model factory is reusable
from B0; OpenAI Responses API accepts `OPENAI_API_KEY`. The experimental
`chatgpt-siwc` provider uses a locally authorized ChatGPT account, NOT an API
key or an automatic fallback. It depends on available model permissions and may
have different tool/sampling capabilities. Sign in explicitly:

```powershell
uv run python -m scr.baselines.siwc_auth
uv run python -m scr.baselines.chatgpt_siwc  # list visible model slugs
```

For usage examples and provider-specific evaluation caveats, see
[the B0 tutorial](bird-b0-pre-current-only-20261115.md#optional-other-model-providers).

## Original Mini-Dev Quick Start — Windows PowerShell

For new Mini-Dev 2026 experiments on Linux or Windows, use the [current setup tutorial](bird-setup-pre-current-only-20261115.md). The commands below retain the original dataset workflow for historical reproduction.

Clone the repository and run the setup commands from its root. Install [BIRD Mini-Dev 2026](bird-setup-pre-current-only-20261115.md) and configure [model authentication](bird-b0-pre-current-only-20261115.md#3-run-b0-inference--required) before inference.

```powershell
git clone https://github.com/TimLL123456/COMP7608-Large-language-models-Group-Project.git
cd COMP7608-Large-language-models-Group-Project
uv sync
uv run python -m scr.datasets.setup_bird
uv run python -m scr.datasets.setup_bird --verify-only
```

**When working from the separate public group repository root, skip `Set-Location`.** Expected dataset result: `PASS`, 500 questions, 11 databases, 400 dev / 100 local-test questions.

Set `NVIDIA_API_KEY` in your local terminal before `infer` (secure instructions in [B0 tutorial](bird-b0-pre-current-only-20261115.md#1-first-time-checks--required)). Inference requires a network connection and may consume model credits.

```powershell
# Small repeatable smoke sample: 4 dev questions, 1 local-test question
uv run python -m scr.cli.run_bird_b0_eval prepare --total-questions 5 --dev-ratio 0.8 --seed 42 --selection-id sample-001

# Calls NVIDIA to generate SQL and traces for the 4 sampled dev questions
uv run python -m scr.cli.run_bird_b0_eval infer --selection-id sample-001 --split dev --run-id run-001 --preview-rows 20

# Scores saved SQL offline; does not call NVIDIA
uv run python -m scr.cli.run_bird_b0_eval score --selection-id sample-001 --split dev --run-id run-001

# Optional: create an offline trace-explorer.html
uv run python -m scr.cli.run_bird_b0_eval visualize --selection-id sample-001 --split dev --run-id run-001
```

**Read your results:** `scr/evaluation/result/sample-001/B0/dev/run-001/scores/report.md`. Inspect `per_question.csv` for EX 0/1, and `traces.jsonl` for model/tool errors. This **five-question selection is a smoke test**, not full BIRD benchmark evidence. Use a **new `--run-id`** for each new inference run.

## v4.4 progress snapshot — 3 November 2026

**Done:** KORA-02 dataset setup and KORA-03 independent EX scorer. **In Progress:** KORA-05 B0 and KORA-10 failure diagnosis. **To Do (P0):** KORA-17 demo data, KORA-14 controller, KORA-15 UI, KORA-16 end-to-end reliability, KORA-11 report/source ZIP and KORA-12 demo. Active P0 tasks are now tracked in [Notion](https://app.notion.com/p/ae1642e8bb734b7183a470de01fb99b2); older BENCH-03 research is Done and the broader BENCH-04 remains Backlog. The four-question smoke EX of 25% is not a representative benchmark, and all TC-I/TC-R scenarios remain unexecuted.

## Historical implementation snapshot — 3 November 2026

| Component | State |
| --- | --- |
| Dataset loader and setup (KORA-02) | Implemented; previous Windows validation reported original 500/11 and fixed 400/100 |
| Independent EX evaluator (KORA-03) | Implemented; prior 16/16 selected-case upstream parity checks, **not full parity** |
| B0 Text-to-SQL (KORA-05) | Implemented; 1 Nov four-dev-question smoke generated 4/4 final SQL and strict EX 1/4 (25%); a representative scored benchmark and current full Windows regression **not yet verified** |
| B1 Knowledge Graph / B2 Planner / B3 Router / B4 Integration | **Planned**; see [developer guide](agent-development-pre-current-only-20261115.md) |
| Backend/frontend, synthetic demo | **Planned**, not built |
| Document RAG | **Optional P2** prototype; not part of required BIRD EX |

**Historical v4.4 B0 configuration:** Nemotron 3.5 Super VL; **300 seconds per NVIDIA model request**, **16,384 output tokens**, documented **262,144-token hosted context budget** (not directly enforced by the client). See [B0 parameters](bird-b0-pre-current-only-20261115.md#3-run-b0-inference--required). Context, API availability and large output limits can affect latency.

**Important research decision:** The original submitted [Group 9 proposal](../../proposal/KORA/KORA_Group9_Proposal.pdf) includes S0/S1; both private and public v4.4 **working roadmaps** now use **B0 as the sole active baseline** with evidence-gated B1–B4. This is not a revision to the submitted proposal; team/teaching-team alignment and truthful final-report disclosure remain important.

## Where to find source and research files

| Directory | Purpose |
| --- | --- |
| `scr/datasets/` | Dataset installer and question/schema loader |
| `scr/baselines/` | B0 agent, provider factory and safe SQLite adapter |
| `scr/cli/` | B0 prepare/infer/score/visualize/serve and independent EX scoring |
| `scr/evaluation/` | Shared EX evaluator and sampled result locations |
| `scr/tracing/` | Offline/live read-only execution graph |
| `tests/` | Offline regression tests |
| `docs/` | Canonical beginner tutorials and framework guide |
| `progress-planning.md` | Detailed tickets, roadmap and validation evidence |
| `guidelines/`, `research/`, `proposal/` | Course material, historical studies and submitted proposal |

Offline regression checks (do not replace real-dataset verification):

```powershell
uv run python -m unittest discover -s tests -t . -v
```

## Sharing boundaries

Review new files for credentials, local configuration, downloaded data and unreviewed traces before opening a pull request. See the [developer guide](agent-development-pre-current-only-20261115.md).

Never commit API keys, original BIRD database archives, gold SQL/reference datasets, or unreviewed inference traces. Earlier unit/smoke tests and selected-case scorer parity are **not** model benchmark accuracy.

<details>
<summary><strong>Historical progress log (Optional — dated records)</strong></summary>

| Date | Progress |
| --- | --- |
| 2026-10-04 | Organized dataset research covering 34 resources across 11 domains; established the project documentation structure; included the original guideline and requirements summary. Topic, dataset and baseline remain undecided. |
| 2026-10-04 | Checked reference answer availability across all 34 resources; recorded public answer/solution formats, split restrictions and outcome-based task references. Updated the research links. Topic, dataset and baseline remain undecided. |
| 2026-10-05 | Added a BrowseComp-Plus deep dive covering the fixed-corpus design, dataset schema, worked cases, failure modes and a concrete retriever-vs-agent evaluation direction. |
| 2026-10-05 | Added a HotpotQA deep dive covering multi-hop question types, worked comparison and bridge cases, distractor/fullwiki settings, supporting-fact evaluation and an iterative retrieval experiment direction. |
| 2026-10-05 | Added a MuSiQue deep dive covering connected 2–4 hop construction, a worked decomposition example, MuSiQue-Ans/Full evaluation, leakage controls and a decomposition-plus-iterative-retrieval experiment direction. |
| 2026-10-05 | Added a ToolSandbox deep dive covering stateful tool execution, world-state dependencies, milestone/minefield scoring, the official messaging example and a prerequisite-checking experiment direction. |
| 2026-10-05 | Added a BIRD-SQL / BIRD Mini-Dev deep dive covering the original 500-example setting, dataset fields, a worked SQL case, schema/value inspection, execution-feedback repair, evaluation metrics and an ablation-based SQL-agent experiment direction. |
| 2026-10-06 | Saved concise BIRD Mini-Dev and MuSiQue proposal drafts with text workflow charts for team review. The final topic has not been selected. |
| 2026-10-06 | Added two-page PDF versions of the BIRD Mini-Dev and MuSiQue proposal drafts, preserving their text workflow charts. Linked both PDFs from the file index. |
| 2026-10-10 (HKT) | Submitted KORA proposal PDF was added to GitHub (commit `a11d199`); the chosen benchmark is original BIRD Mini-Dev. |
| 2026-10-25 | Aligned documentation with the final proposal and marked earlier topic research/drafts as historical; no files removed or relocated. |
| 2026-10-28 | Prepared `progress-planning.md` for Group 9 review; updated the README to reflect existing prototype scaffolds and the proposed combined S0/S1 fixed baseline. No new model runs, tickets or application code changes. |
| 2026-10-28 | Updated planning to v3.1 and documented [public group repository](https://github.com/TimLL123456/COMP7608-Large-language-models-Group-Project) as canonical source; added SQL-only API/UI, optional progress-gated RAG and KORA-17 synthetic demo fixtures. Documentation-only, no code migration or scoring. |
| 2026-10-29 | HKU-only B0–B4 research-plan revision: retired KORA-04, revised RQs, metrics, diagrams and dependencies, and preserved KORA-02 dataset details. Submitted proposal and public group planning remain unchanged. Historical entries above describe earlier plans. |
| 2026-10-29 | Cleaned the HKU-only planning ticket list, added the detailed KORA-03 evaluation-harness execution plan, and removed the obsolete toy SQL evaluator and its test/documentation references. No BIRD harness implementation or scores claimed. |
| 2026-10-29 | Merged explicit multi-provider planning into KORA-05 and updated KORA-08's dependency, preserving SQL/RAG provider usage and existing model-factory tests. Documentation-only; no external repo or code modifications. |
| 2026-10-29 | KORA-02 implemented original SQLite Mini-Dev setup/loader, pinned HF annotation source, metadata/splits, ZIP safety, 11 passing synthetic-fixture tests and a PowerShell tutorial. Real official dataset validation still pending because download access was unavailable. |

</details>
