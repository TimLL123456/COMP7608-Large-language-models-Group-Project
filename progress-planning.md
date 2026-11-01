# KORA — Progress Planning & Development Tickets

**COMP7608B Large Language Models | Group 9 | 2026–2027 Semester 1**  
**Version:** v4.3 — B0 Initial Evaluation & Delivery Roadmap (shared group edition) | **Updated:** 1 November 2026  
**Status:** **KORA-02 Done** (BIRD dataset), **KORA-03 Done** (EX evaluator with 16/16 selected-case upstream parity), **KORA-05 In Progress** (B0 implemented; 1 Nov four-dev-question smoke scored **EX 1/4 = 25%**), and **KORA-10 Stage A In Progress** (initial failure diagnosis). This small sample is **not** a representative/full-split benchmark. Interactive app, B0–B4 controlled comparisons and eight TC-I/TC-R application scenarios remain pending. Tickets are planning labels, not confirmed issue records.

> **Working group plan:** **B0 is the sole active baseline**. B1/B2/B3 are optional evidence-selected improvements; B4 is conditional integration. The earlier submitted proposal includes fixed S0/S1 metrics; posting this roadmap does **not** revise it. Confirm scope changes with the team and disclose them in the final report.

> **Public repository scope:** This repo contains B0, original BIRD loader and evaluator, tracing, focused tests and tutorials. Submitted proposal materials, separate learning/RAG experiments, downloaded BIRD reference data and raw traces have **not** been migrated.

## How to use this document

**New team member?** Start with [dataset setup](docs/bird-setup.md) → [B0 Prepare/Infer/Score/Visualize](docs/bird-b0.md) → [EX explanation](docs/bird-evaluation.md). For B1–B4 implementation, use [framework reuse guide](docs/agent-development.md).

**This roadmap lists tickets, dependencies and evidence**, not duplicate installation instructions. For step-by-step commands use `docs/`. Publishing a working plan does not imply the submitted proposal has been changed or the teaching team has approved a scope revision.

## 1. Project Overview — User-facing Autonomous Agent

**Intended users:** Data analysts and business users, consistent with the submitted KORA proposal. The deliverable is a **working autonomous Text-to-SQL application**, not just standalone benchmark scripts. Users ask questions without needing to know tables, column names or joins.

**Target workflow:** Request → agent chooses schema/data tools → runs safe read-only SQL → receives actual rows/errors → decides whether to inspect/revise/retry within a budget → returns an understandable answer and rows, clarification or safe stop. Multi-turn changed conditions must be handled in the **application**; the current B0 single-question CLI is not evidence that this works yet.

**Required user scenarios:**
1. Ordinary: “Show the top five products by revenue” → grounded SQL, rows and visible tool decisions.
2. Changed condition: “Only include October orders” → correctly revise the previous request in the same session or seek clarification.
3. Failure: invalid/missing column → observe error, optionally inspect and repair within limits or stop safely.
4. Provider failure: NVIDIA timeout/unavailable → bounded retry or safe stop with explicit user feedback; do not claim unsuccessful inference is a reasoning error.

**B0 is the only baseline.** B1 (KG), B2 (planner), B3 (router) and B4 (integrated) are **P1 research improvements**, compared with B0 only when implemented and tested. No additional baseline agent is planned. Document RAG remains P2 optional. The core **P0** path is B0 → usable application → reliability/evaluation → report/ZIP/live demo.

**Research questions:** Does graph-guided evidence exploration, explicit planning or adaptive routing improve B0 execution accuracy (EX), error recovery, inference cost or latency when the same question IDs, evidence and scoring rules are used? Compare only real outputs and report negative/inconclusive cases.

**Guideline delivery boundary:** A complete autonomous application, meaningful decisions, tool use, feedback-dependent next steps and safe stop/clarification are required. The final report must discuss actual users, planned/delivered scope, design/state/prompts, **at least two tested failures**, relevant non-functional measurements, fair evaluation, contributions and attribution. Notebook-only operation, component-only benchmarks and unverified demo claims do not suffice; multiple agents, RLHF and fine-tuning are not mandatory.

**Dataset separation:** The original 500-question / 11-SQLite BIRD Mini-Dev remains for research EX, with a fixed 400-dev / 100-local-test question split (not BIRD's official hidden test). Use separate deterministic fictional SQLite data for real user interactions, changed requests and failure demos. Never mix benchmark EX with synthetic demonstration scores.


### Development Objective and Evidence-based Improvement Gate

**User problem:** Help data analysts and business users explore an approved relational database and answer natural-language questions without writing SQL. The initial deliverable is a **read-only SQLite Text-to-SQL application** that can inspect schemas, execute bounded SQL, explain actual results, remember relevant session context, handle changed conditions and clarify or stop on unsupported requests. This is **not** a general-purpose assistant; the exact supported database, permitted operations and limitations must be visible to users and the live-demo team.

**Delivery strategy:** **B0 → diagnose actual weaknesses → choose relevant proposal improvements → validate improvements → deliver the interactive agent**. Application work and B0 diagnostics proceed in parallel, so B1/B2/B3/B4 cannot block the minimum application or final submission.

**Evidence-to-improvement gate:** Use the frozen original BIRD Mini-Dev development selection and the existing KORA-03 scorer to establish B0 EX, then manually review unsuccessful cases and agent/tool traces. Classify schema discovery, join path, logical/aggregation/filter, SQL execution and recovery, correct execution with wrong result, and model/service errors **separately**. Document a hypothesis and expected benefit before choosing B1 (KG), B2 (planner) or B3 (router). A framework difference alone is **not** a project improvement.

**Improvement priority:** Start with the changes most likely to address observed, repeated B0 weaknesses; keep proposed KG, planner and router work tied to the submitted proposal, but allow justified reprioritization or non-integration if the measured benefit is weak. Report the decision and unfinished scope transparently, and follow the course procedure for material objective changes.

**Outcome evidence:** The final report must connect (1) a real user-facing capability, (2) observed baseline problems, (3) a tested integrated improvement or defensible component comparison, and (4) measured limitations. BIRD EX and separate interactive-functional test results have different denominators and must never be merged.

### Interactive and Reliability Test Coverage

**Course-related acceptance:** Demonstrate at least **two distinct observed failure situations** (detection → bounded recovery or safe stopping → user feedback, including repeated-action risks) and support genuine **in-scope follow-up questions and changed conditions** in the live application. These are distinct evidence requirements, not optional extensions to a single-turn BIRD EX score.

**Planned test suite (not yet implemented or run):** `TC-R01–R04` cover Reliability & Recovery; `TC-I01–I04` cover Interactive & Multi-turn. **Five P0 scenarios** are `R01`, `R02`, `I01`, `I02` and `I03`; **three P1 scenarios** are `R03`, `R04` and `I04`. P1 indicates additional dedicated test-case coverage, **not permission to omit underlying P0 SQL read-only protection, bounded execution or safe clarification**. The case definitions, evidence and pass rules are maintained in KORA-16 (with KORA-17 fixtures and KORA-10 evaluation).

**Test isolation:** Use separate, manually verified synthetic/fictional database cases for session and recovery behavior; preserve original BIRD Mini-Dev EX and evaluator-only gold SQL unchanged. Keep prepared tests separate from a further **unseen-question rehearsal** within the declared read-only SQL domain.
## 2. Current Repository Status (1 November 2026)

| Component | Verified repository evidence | Status / remaining work |
| --- | --- | --- |
| Final proposal | Group 9 proposal (not included here) and submitted PDF | Submitted; scope frozen for planning |
| SQL baseline | [scr/baselines/bird_b0.py](scr/baselines/bird_b0.py) | **Current B0:** NVIDIA Nemotron 3.5 Super VL / Deep Agents and three read-only SQLite tools; Q1409 single-question inference and 1 Nov four-dev-question B0 scored smoke (1/4 strict EX); interactive app pending |
| Optional Document RAG (P2) | Excluded from this Text-to-SQL code migration | Independent prototype remains separate; no integrated RAG system is claimed |
| Shared utilities | [scr/baselines/common.py](scr/baselines/common.py) | Explicit Ollama/Gemini/DeepSeek/NVIDIA factory and partial trace preservation; shared default stays Ollama |
| BIRD dataset setup / loader | [scr/datasets/setup_bird.py](scr/datasets/setup_bird.py), [scr/datasets/bird.py](scr/datasets/bird.py) | **KORA-02 Done:** local original SQLite Mini-Dev installation verified (500 questions, 11 DBs, pinned HF source, 400/100 split); read-only schema/SELECT smoke checks passed on all 11 real databases; 11/11 KORA-02 unit tests passed |
| SQL evaluation | [scr/evaluation/bird.py](scr/evaluation/bird.py), [scr/cli/evaluate_bird.py](scr/cli/evaluate_bird.py) | **KORA-03 Done:** 10/10 scorer tests, 8/8 gold self-check, 7/8 negative control and 16/16 matched selected-case upstream scorer parity; full-split model EX pending |
| B0 inference and sampled evaluation | [scr/baselines/bird_b0.py](scr/baselines/bird_b0.py), [scr/cli/run_bird_b0_eval.py](scr/cli/run_bird_b0_eval.py), [docs/bird-b0.md](docs/bird-b0.md) | **KORA-05 In Progress:** Prepare / Infer / Score / Visualize implemented; 4/4 dev final SQL and 1/4 strict EX on 1 Nov. Latest full Windows regression and larger frozen sample remain pending |
| Automated regression tests | [tests/](tests/) | Historical 41/41 Windows run occurred before later B0/v2 changes. Current expanded suite: execution and exact test count not verified in Windows |
| BIRD official benchmark verification | research/bird-sql.md (not included here), [docs/bird-evaluation.md](docs/bird-evaluation.md) | Original published databases verified locally; pinned upstream EX scorer matched on 16/16 selected comparison cases. Broader parity checks and representative/full-split model evaluation remain pending; a separate 4-question B0 dev smoke scored 1/4 strict EX |
| Graph, planner, router, full KORA | Final proposal only | Not implemented |
| SQL application and interface | KORA-14–16 **P0** | Not yet verified as an end-to-end user application; ordinary/changed/failure requests must be tested |
| Synthetic demo/test data generator | KORA-17 **P0** | Deterministic ordinary/changed/failure fixtures remain pending. Existing tiny SQL unit-test fixtures are **not** the complete KORA-17 interactive demo dataset |
| Dedicated group development repo | [Public group repo](https://github.com/TimLL123456/COMP7608-Large-language-models-Group-Project) | Now includes B0 framework, tests, tutorials and this plan; interactive app and B1–B4 remain planned |

**Repository boundaries:** B0, loader, evaluator, trace viewer and test file links now refer to files in this public repo. Learning experiments and optional RAG were not copied; backend/frontend and KORA-17 full interactive fixtures remain planned.

### Offline test coverage and verification boundary

**Historical Windows unit tests:** Runs at different earlier revisions passed 21/21, 35/35 and 41/41 tests on 29 October. The latest B0/evaluation code has **not** had a verified full Windows regression; these counts are not evidence that the current suite passes.

~~~powershell
# Run from Group Project/ after uv sync
uv run python -m unittest discover -s tests -t . -p "test_bird*.py" -v
uv run python -m unittest discover -s tests -t . -v
~~~

These are offline fixtures/mocks and cannot establish BIRD real-dataset EX or paid model/tool compatibility. A real Mini-Dev dataset verification and selected-case upstream parity checks are documented separately below.

### Real BIRD Mini-Dev Validation Evidence (Windows, 29 October 2026)

The following results are **observed in the user's Windows PowerShell execution log**, not inferred from synthetic tests. The generated output directory and validation helper script are **local-only** and have not been committed to HKU or the public group repository.

| Check | Observed evidence | Result |
| --- | --- | --- |
| Local original Mini-Dev setup and verify-only | 500 questions; 11 SQLite DBs; 400 dev / 100 held-out; `source_verification=pinned_hf_download` | **PASS** |
| Annotation SHA-256 | `88ceb0710163cae46a256ecea8f0a8c98286599530b60587fda5c3cfe57d45d2` | Recorded |
| Full offline unit tests | 35/35, including 21 BIRD tests and 14 model/SQL-safety/RAG tests | **PASS** |
| Real schema, description CSV and read-only SELECT checks | 11/11 real DBs, each with discoverable tables and description CSVs | **PASS** |
| Evaluator gold SQL self-check (diagnostic, **not model predictions**) | 8/8 on real dev questions | Expected 100% |
| Deliberately broken prediction negative control | 7/8 on same real dev cases | Expected 87.50% |
| Pinned upstream scorer vs KORA EX comparison | 16/16 matched paired results from the two 8-case diagnostic conditions | **Selected-case parity PASS** |

Pinned upstream evaluator commit: `abd11b6db92a1c9f809b32f7564c7c71b34d67f0`; official scorer implementation: `evaluation/evaluation_ex.py`, `evaluation/evaluation_utils.py`. The comparison checks the **selected cases only** and is not proof of complete 500-question parity, every edge case, or benchmark accuracy. The command's setup `PASS` shows verified local installation and pinned-source metadata; it does **not independently prove a fresh network download occurred during that invocation**, since setup can reuse an existing verified installation.

**Reproduction:** Follow the maintained [dataset setup](docs/bird-setup.md) and [EX scoring guide](docs/bird-evaluation.md). The extra upstream parity helper was **local-only and untracked**, not a bundled command.

Observed locally generated results: `results/bird/real-validation/20261029T083507Z-8104/` (`gold_selfcheck/`, `negative_control/`, parity diagnostics). Gold/reference SQL is used **only in offline scorer self-checks**, never in B0 agent prompts, generation, routing, or reported model accuracy. These diagnostic results must not be described as BIRD leaderboard scores. The user-reported local results and command line are evidence; the output artifacts have not been independently inspected in this repository.

**Phase 1 foundation:** KORA-02/03 are **Done**. The B0 agent now has one small scored dev smoke; broad parity, representative benchmark, ablation and interactive tests remain separate work under KORA-05/10/14–17.

### Initial B0 Development Evaluation — 1 November 2026 (Smoke Only)

**Run:** User-reported Windows B0 CLI, `--selection-id smoke-nov01-001 --split dev --run-id run-001`, with sampling `--seed 42`. Five questions selected (**4 dev, 1 local test**); **only the four dev questions** were inferred and scored. Local result files/traces were reported, not independently inspected from this GitHub document. This is **not** a representative sample, the full 400-question dev split or the official hidden BIRD test.

| Metric | Observed four-question dev result |
| --- | --- |
| Final SQL generated | **4/4** |
| Strict BIRD-style Execution Accuracy (EX) | **1/4 (25%)** |
| Agent SQL tool calls / successes | **9/9**; SQL execution success is **not** answer correctness |
| Observed model / tool calls | **19 / 21** |
| Input / output tokens | **94,021 / 6,103**; nested usage may be incomplete |
| Observed total inference latency | **61.307 seconds** summed across four questions, ~**15.3 s/question** |
| API cost | **Unknown** (`cost_usd=null`) |

| Question / difficulty | EX | Early diagnosis |
| --- | --- | --- |
| **Q440** / simple, `card_games` | **1** | Predicted SQL result matches reference |
| **Q672** / moderate, `codebase_community` | **0** | **14 unique users** vs gold **19 user–post rows**: aggregation unit differs; natural-language ambiguity requires human review |
| **Q963** / moderate, `formula_1` | **0** | **9 unique French drivers** vs gold **23,295 qualifying lap rows**. Controlled filtering comparison: milliseconds **23,292 lap rows**, gold time-string filter **23,295**, **9 distinct drivers** under both filters. The primary mismatch is counting grain |
| **Q1037** / challenging, `european_football_2` | **0** | Predicted **24.59%** vs gold **24.56690504416995%**. Different join key, latest historical-record selection and rounding; not a proven floating-point-only scorer bug |

**Accuracy integrity:** Preserve strict EX, including for disputed wording/annotations. A prior **16/16 selected-case upstream EX parity** check is diagnostic scorer validation, *not* a model benchmark and not complete 500-question parity. Treat semantic ambiguity and numeric differences as separate **manual review notes**, not altered official gold answers or extra EX points.

**Next (KORA-05 / KORA-10 Stage A):** Isolate Q1037 join key, latest-row selection and rounding one at a time; manually inspect Q672/Q963 count units; inspect the full recorded traces; then evaluate a larger **frozen dev selection** spanning database/difficulty within model budgets. Count root causes before choosing targeted B0 changes or B1/B2/B3 improvements. Do not tune on the local-test split. **All eight TC-I/TC-R scenarios remain not run.**

## 3. Architecture — Complete Application First

~~~mermaid
flowchart TD
    U[Analyst / business user] --> UI[Interactive SQL application]
    UI --> API[Backend or application controller]
    API --> B0[B0 autonomous Text-to-SQL agent]
    B0 --> TOOLS[Read-only SQL / schema tools]
    TOOLS --> DB[(Approved SQLite database)]
    TOOLS --> OBS[Observed rows and errors]
    OBS --> B0
    B0 --> DEC{Final answer / clarify / safe stop}
    DEC --> UI
    FIX[Seeded synthetic demo data] --> DB
    DATA[Original BIRD Mini-Dev] --> EVAL[Independent EX scorer]
    B0 -. "saved benchmark predictions" .-> EVAL
    B1[B1 KG / P1] -. "optional enhancement" .-> B0
    B2[B2 Planner / P1] -.-> B0
    B3[B3 Router / P1] -.-> B0
    B4[B4 Integration / P1] -.-> B0
~~~

**Meaningful autonomy:** A real observation must influence a subsequent tool, revision or stopping decision; preserve actual model/tool traces rather than invented reasoning. Stop on exhausted budgets or unsupported requests. Never expose evaluator gold SQL, secrets or unrestricted database access.

**Technology TBC:** A small FastAPI + React/Vite app is possible, but a simpler Streamlit/equivalent interface is acceptable if it runs independently of notebooks and supports real in-scope inputs, changed follow-ups and visible recovery. Avoid unnecessary architecture.

**Shared user response:** question, session/request ID where applicable, safe SQL/rows or clarification/error, observed tool actions, completion status, latency and available usage. Keep credentials server-side; enforce row/time/step budgets and read-only SQL.

**Agent variants:** B0 is the only baseline. B1 adds graph paths, B2 plans, B3 routes models, B4 integrates independently validated features. These are not dependencies of the minimum application or final submission.

**Independent evaluation:** BIRD EX runs from saved SQL predictions and evaluator-only gold; synthetic functional cases use expected fixture results. Do not conflate them.


**Improvement decision gate:** The four-question dev smoke exposed aggregation/temporal SQL discrepancies but is insufficient to justify a large B1/B2/B3 implementation. Expand frozen dev diagnostics and inspect traces before choosing research enhancements; do not delay the minimum working application.

## 4. Roadmap & Milestones — Delivery-first Priorities

| Priority / workstream | Tickets | Exit criteria |
| --- | --- | --- |
| Done — benchmark foundation | KORA-02/03 | Original BIRD local verification and selected-case EX parity already recorded |
| **P0 — B0 agent MVP** | KORA-05 | Actual tool-dependent agent trace, safe SQL result/stop; fresh offline and live validation |
| **P0 — early B0 diagnostics (started)** | KORA-05 + KORA-10 (Stage A) | Small scored dev smoke and early SQL-difference review recorded; broader frozen sample, trace-backed counts and improvement decision still required |
| **P0 — fictional demo data** | KORA-17 | Deterministic SQLite fixture, human-verified multi-turn reference results and controlled failure-injection fixtures for the eight scenario IDs |
| **P0 — runnable application** | KORA-14/15/16 | Launch from README; ordinary, changed and failure requests; TC-I01/I02/I03 and TC-R01/R02 application evidence |
| **P0 — evaluation** | KORA-10 (Stages A–C) | Early B0 diagnosis; tested targeted improvements where feasible; separately report BIRD EX, TC-I01–I04 interaction and TC-R01–R04 recovery results, with measured latency/cost/safety |
| **P0 — delivery** | KORA-11/12 | Final report PDF, source ZIP/AI-use records, two-minute pitch and interactive live demo |
| P1 — evidence-selected improvements | KORA-06/07/08 | Prioritize KG/planner/router only against documented B0 failure hypotheses; measure effects relative to B0 where implemented |
| P1 — integration | KORA-09 | B4 only when validated; **not a P0 dependency** |
| P2 — optional RAG | KORA-13 | Only if SQL delivery is on track |

**Critical path:** (KORA-05 → KORA-10 Stage A diagnosis) in parallel with (KORA-05 + KORA-17 → KORA-14/15/16 application); then KORA-10 Stages B/C and KORA-11/12 delivery. Evidence-selected P1 work may proceed alongside the app but must not hold it up. **B0 evaluation starts before B4**, with a representative frozen dev sample and documented budget; final evaluation must measure the actually delivered application.

**Confirmed COMP7608B Final Project Student Guideline dates:**
- **Final submission:** **25 November 2026, 23:59 Hong Kong time (UTC+8)**.
- **Live demo:** **1 December or 8 December 2026** during regular class time. Assignment is announced after submission; reserve both dates and every member must attend the assigned session.
- **Weights:** Proposal 20%, report + code 50%, presentation + demo 30%.

**Suggested internal targets (team targets, NOT course deadlines):**

| Date | Expected readiness |
| --- | --- |
| **5 Nov** | B0 diagnostic sample and root-cause table, improvement shortlist, seeded synthetic fixtures, ownership and stack decision |
| **12 Nov** | Runnable B0 SQL-only app and manually verified TC-I01/I02/I03 conversation fixtures; basic session continuity functioning |
| **18 Nov** | B0 EX and applicable improvement comparisons; run five P0 TC-I/TC-R cases with actual/clearly labeled injected traces, optional P1 cases and NFR measures |
| **22 Nov** | Report draft, contribution records, AI prompt inventory, live-demo rehearsal |
| **24 Nov** | Freeze, fresh-clone README test and PDF/ZIP verification |
| **25 Nov** | Submit PDF and ZIP by 23:59 HKT |

**Fallback:** If B1–B4 are incomplete, disclose that fact and finish the B0 application, evaluation, reliability, packaging and demo rather than blocking submission.

## 5. Proposed Tickets

The IDs below are **planning labels only**, not confirmed Notion/GitHub ticket records. Unless stated otherwise: **status = Not Started**; group owner and delivery date = **TBD**. Existing examples/scripts are explicitly identified and must not be confused with complete tasks.

### KORA-02 — BIRD Mini-Dev Dataset Setup & Loader

- **Priority / phase:** P0 / Phase 1
- **Status / dependencies: Done (29 Oct 2026).** The existing local original SQLite Mini-Dev installation passed setup + verify-only (500 questions, 11 databases, 400/100 split, pinned HF metadata). All 11 real SQLite databases passed schema/CSV/read-only SELECT smoke checks. **11/11 KORA-02 offline tests passed**, included within 21 BIRD and 35 total tests. No dependency. Reuse previous BENCH research as background.
- **Objective:** Build a reproducible SQLite loader for the **2025-updated original BIRD Mini-Dev**, using **pinned Hugging Face original SQLite annotations** (revision `f65faf4ae3b638c1fa6df1d3370c8d92c8366301`) and the official Google Drive database complete package (file ID `13VLWIwpw5E3d5DUkMvzw7hvHE67a4XkG`). Exclude Mini-Dev V2. Google Drive contents remain hash-recorded rather than revision-pinned; local compatibility has now been checked against 11 real databases, with archive/database checksums recorded in the local manifest.

**Implementation summary (how-to and recovery commands live in [dataset setup](docs/bird-setup.md))**

1. Use the pinned **original SQLite** Mini-Dev annotations and official database ZIP, not V2. Record the actual archive and SQLite SHA-256 hashes; Drive IDs alone do not pin file contents.
2. Install with `scr/datasets/setup_bird.py`; verify 500 unique questions, 11 valid databases, readable SQLite schemas/description CSVs and safe extraction. **Optional:** `--archive` and `--annotations` for network/offline fallback, with manual annotation provenance clearly flagged.
3. Expose `BirdDataset`'s question, schema, description and database-path APIs to agents while keeping gold SQL evaluator-only. This is a code convention, **not** OS-level isolation.
4. Preserve the deterministic **seed-42 400 dev / 100 local-test** split stratified by database/difficulty. Real IDs, no overlap. The test questions may share database schemas with dev.
5. Retain fixture safety tests, real 11-DB read-only SQL checks and provenance manifest. **Not verified:** fresh download retries/throttling and a complete live manual-download fallback run.

**Beginner verification:** `uv run python -m scr.datasets.setup_bird --verify-only` from the project root. See the tutorial for prerequisites, exact expected output and optional troubleshooting.

**Implemented files (11/11 KORA-02 unit tests and real 11-database smoke checks passed)**

| File | Responsibility |
| --- | --- |
| `scr/datasets/setup_bird.py` | Pinned HF SQLite annotations, Google Drive database download, safe/idempotent extraction, provenance, `--archive` / `--annotations` / `--verify-only` CLI |
| `scr/datasets/bird.py` | Question-to-database mapping, SQLite schema/CSV descriptions, split access and evaluator-only gold references |
| `tests/test_bird_setup.py` | Offline download/extraction logic and failure/idempotency fixtures |
| `tests/test_bird_loader.py` | Question, database, metadata, split and gold-isolation checks |
| `docs/bird-setup.md` | Windows/uv usage, sources, versions, local layout, integrity checks and manual fallback |
| `data/bird/original-mini-dev/dataset_manifest.json` | Generated local provenance and database inventory (not committed as benchmark data) |

**Commands:** Follow [KORA-02 beginner dataset setup](docs/bird-setup.md). Keep the standard download and `--verify-only` as the recommended first-run path. Manual `--archive`/`--annotations` commands are **Optional** and not prerequisites.

**Acceptance criteria**

- [x] One command sets up/reuses a verified local original SQLite installation and `--verify-only` passes on real data; manual-archive behavior has synthetic test coverage, **not a verified live manual-archive run**.
- [x] ZIP safety, partial extraction refusal, idempotent reruns and manual-archive behavior pass **synthetic offline tests**. Actual Google Drive failure/retry behavior remains unverified.
- [x] Exactly 500 questions and 11 distinct database IDs validated on installed original Mini-Dev; loader verifies unique IDs and source annotations are marked pinned HF.
- [x] All 11 real `db_id` values resolve to readable SQLite files; table/schema and description CSV inspection succeeded.
- [x] Read-only SELECT smoke checks passed on all 11 real databases; SQL write-denial behavior passed the existing offline safety tests.
- [x] Fixed seed-42, disjoint 400/100 question-ID split passed both deterministic offline tests and real installed Mini-Dev verification (not unseen databases or an official hidden split).
- [x] Agent-facing inputs exclude reference SQL and answer results in **offline tests**; evaluation-only references use a distinct class, not a filesystem security boundary.
- [x] Local annotation/archive/SQLite checksum manifest and `/data/bird/` Git exclusion implemented; real verification checked installed SQLite hashes and annotation SHA-256 `88ceb0710163cae46a256ecea8f0a8c98286599530b60587fda5c3cfe57d45d2`. Archive checksum is recorded locally, not asserted against a separately published official hash.
- [x] Real Windows setup/verify commands, 11-DB smoke results, pinned annotation checksum and scope limitations are recorded in **Section 2**; existing `docs/bird-setup.md` remains the general tutorial (local-only helper script and results were not committed).

- **Implementation and real-data evidence (29 Oct 2026):** `scr/datasets/{setup_bird.py,bird.py}`, `tests/{test_bird_setup.py,test_bird_loader.py}` and `docs/bird-setup.md` are in this shared group repo. The Windows run reported setup and verify-only `PASS` for 500/11/400/100, 11/11 real DB SELECT checks, the pinned annotation hash and 11/11 KORA-02 tests (included in 21 BIRD / 35 overall). Actual network download/retry behavior is not established by the log. The separate **KORA-03** validation performed real-data SQL scoring diagnostics.
- **Output:** BIRD SQLite loader/setup, 11 real DB schema/SELECT checks, pinned annotation revision and local integrity manifest, deterministic split and reproducible Windows commands. **Next:** KORA-05 consumes agent-safe questions/schema; optional download-fallback QA remains separate.
- **Boundary:** KORA-02 prepares data and safe read-only access; official Execution Accuracy scoring, result-set comparison and benchmark reporting remain **KORA-03**. No agent benchmark results are claimed at this stage.

### KORA-03 — Study BIRD Evaluation and Build a Shared Harness

- **Priority / phase:** P0 / Phase 1
- **Status / dependencies: Done (29 Oct 2026).** EX harness/CLI implemented; 10/10 evaluator unit tests, 8/8 gold self-check, 7/8 negative control and **16/16 selected-case upstream EX parity** reported. Depends on KORA-02. This is not full-set parity; **a later B0 four-question dev smoke scored 1/4 strict EX**, while representative/full-split experiments belong to KORA-05/10.
- **Objective:** Build **one reproducible, official-compatible SQL evaluation harness** for B0–B4. Score final agent SQL separately from inference, avoid gold-answer leakage, and report comparable accuracy, failures and resource usage. The retired toy SQL evaluator is not a benchmark implementation.

**Implementation summary (see [EX tutorial](docs/bird-evaluation.md) for commands and worked examples)**

1. Pin original SQLite Mini-Dev and the upstream EX implementation. Compare **executed result sets** (not SQL text); row order and duplicate rows do not matter, but tuple/column order does.
2. Validate every real `question_id` and `db_id`. Reference SQL stays in the scorer. Preflight all selected gold SQL before scoring; if a gold query fails, **the evaluation run is invalid**.
3. Score saved final predictions read-only with explicit failure categories, timeout and row cap; missing/no-SQL predictions count 0 without shrinking the denominator. Keep the scorer independent of inference.
4. Export per-question JSONL/CSV, overall/difficulty EX, observed efficiency metrics and a reproducible run manifest. Missing observed usage is `null`, not 0.
5. Test safety and parity on synthetic fixtures and representative real BIRD data. The **16/16 selected-case parity** reported on 29 Oct is not full-dataset validation. Wider edge-case checks remain optional future QA.

**Advanced / Optional:** Low-level `scr/cli/evaluate_bird.py` is for manual prediction files and future B1–B4; B0 users should use `scr.cli.run_bird_b0_eval score`. Soft F1/R-VES are optional later metrics. The local 400/100 split is not BIRD's official hidden test.

**Implemented files and responsibilities (selected-case upstream EX parity validated; separate small B0 dev smoke now scored)**

| File | Responsibility |
| --- | --- |
| `scr/evaluation/bird.py` | Read-only, bounded, official-compatible EX scorer/adapter and prediction alignment |
| `scr/cli/evaluate_bird.py` | Common B0–B4 evaluation CLI and per-question/aggregate reporting |
| `tests/test_bird_evaluator.py` | Local EX-equivalence, row-order, empty/duplicate results, invalid IDs, SQL error/timeout, missing predictions and CLI-report tests; **separate local-only helper matched pinned upstream scorer on 16/16 selected comparisons** |
| `docs/bird-evaluation.md` | Upstream evaluator version, input format, scoring choices, safe invocation, reproducible commands and caveats |
| `results/bird/<variant>/<run_id>/` | Generated prediction/score JSON, CSV summaries, trace metadata and run manifest (not source-controlled) |

**Acceptance criteria**

- [x] EX semantics matched the pinned official SQLite Mini-Dev evaluator on **16/16 selected diagnostic comparisons**; the pinned scorer commit and local dataset provenance/split are recorded. Complete parity across 500 questions is not implied.
- [x] Synthetic fixtures cover 0/1 EX, duplicates/reordered rows and empty/wrong results; additionally real-database gold/negative controls matched the official scorer on 16/16 selected comparisons. **Broader edge-case parity, including independent column-order stress cases, remains future QA rather than a claim of exhaustive coverage.**
- [x] Loader question-ID-to-database mapping and gold reference isolation pass synthetic tests; all 11 published Mini-Dev databases were also verified as readable on Windows.
- [x] Synthetic tests confirm expected scored-record counts: **missing/no-SQL/timeout cases keep their places in the denominator**, while duplicate/unknown/wrong-DB prediction records are rejected before scoring.
- [x] Shared CLI accepts B0–B4 variants and exports saved-prediction results (synthetic CLI coverage exercised B0 and B4); actual predictions for all five models/variants remain KORA-05–10 work.
- [x] Read-only evaluation, timeouts/row caps and error categories passed offline tests; real-data selected-case upstream comparisons passed 16/16. Safety-limit divergence on untested complex queries is an explicitly documented future QA risk.
- [x] JSONL/CSV per-question records plus JSON summary and run manifest are generated in synthetic CLI tests, including EX, coverage, difficulty, status and observed usage fields; unobserved usage remains null.
- [x] Reproducible scorer offline tests passed on Windows (29 Oct 2026); the later small B0 dev result is **not** an official BIRD hidden-test score.

**Implementation and validation evidence (29 October 2026):** This group repository contains `scr/evaluation/bird.py`, `scr/cli/evaluate_bird.py`, `tests/test_bird_evaluator.py`, and `docs/bird-evaluation.md`. User Windows logs show 10/10 KORA-03 evaluator tests (21/21 BIRD; 35/35 full suite), 8/8 real gold-SQL self-check, expected 7/8 real negative control, and **16/16 selected-case parity matches** against upstream `abd11b6db92a1c9f809b32f7564c7c71b34d67f0`. The self-check/negative control **are diagnostic reference-based tests, not model inference**. Full-split B0–B4 EX is not yet measured.

- **Boundary:** KORA-03 covers **evaluation**, not SQL generation, KG exploration, routing or a general web application. KORA-02 owns dataset setup; B0–B4 agents deliver saved predictions; KORA-10 owns comparative analysis/ablations.
- **Output:** Pinned EX protocol, evaluation adapter, reusable B0–B4 CLI, focused tests, reproducibility guide and auditable result schema.

### KORA-05 — B0 Agentic Text-to-SQL & Multi-Provider Foundation

- **Priority / phase:** **P0 / Core autonomous agent**.
- **Status:** **In Progress.** B0 Deep Agent and sampled `prepare → infer → score → visualize` pipeline implemented; 1 Nov four-question dev smoke generated **4/4 final SQL** and scored **1/4 strict EX**. Latest full Windows tests and larger batch remain unverified.
- **Entry points:** `scr/baselines/bird_b0.py` (single-question debugging, prior Q1409) and `scr/cli/run_bird_b0_eval.py` (sampled workflow). Tutorial: [B0 walkthrough](docs/bird-b0.md). S0/S1 is not an active separate baseline.
- **Model:** NVIDIA `nvidia/nemotron-3.5-super-vl-120b-a12b`; temperature 1.0, top-p 0.95, max output 16,384 tokens, 300-second timeout **per API request**, declared 262,144 context-token budget (**not client-enforced**).
- **Agent/tools:** Deep Agents; `list_tables`, `inspect_table`, `execute_sql` on read-only SQLite; model/tool/SQL limits **20/20/20**, LangGraph recursion limit **100**. Default middleware/subagents remain enabled; nested token usage may not be fully observed.
- **Safety:** BIRD gold SQL stays evaluator-only; preserve actual tool observations and errors, valid final SQL only after confirmed graph completion and honest unknown usage/cost.
- **Retired history:** Old filesystem-middleware failures and Nemotron 3 Ultra experiments are not current B0 performance evidence.
- **Next:** Rerun current offline tests, use a larger frozen dev sample, investigate Q672/Q963/Q1037 and independently validate the user-facing application.
- **Guideline tasks:** Demonstrate real inspect/execute/revise/stop decisions using actual tool observations; preserve response content or explicit safe errors, bounded model/tool/SQL budgets, timeout categories and usable app interfaces. Do not present a single-question CLI as a finished interactive application.
- **Acceptance criteria:** A representative in-scope natural-language request returns genuinely executed read-only rows or a clear stop/clarification; a trace shows tool feedback influencing the next action; invalid SQL can be repaired or stopped within limits. KORA-16 verifies changed-request continuity. Store prompt/model/run settings and actual usage; do not count provider outages as proof of bad SQL reasoning.
- **Benchmark gate:** Establish measured development EX and frozen comparable configurations before assessing B1/B2/B3/B4.

> **Research gate (KORA-06–09):** P1 extensions may proceed in parallel but cannot delay the runnable B0 app, required recovery tests, final PDF/ZIP or live demo. Compare only integrated, actually validated features against B0; unfinished features remain transparently marked incomplete.


**KORA-05 — Early B0 diagnostic gate (started; completion pending)**

1. **Small scored dev smoke completed (1 Nov, 4 dev questions).** Rerun latest project tests, then freeze a **larger dev selection** (e.g. 30 spread across databases and difficulty, budget permitting) with the existing prepare/infer/score flow. The larger run is pending.
2. Store the selected question IDs, split, model/provider/version, prompt/config, seed (if supported), tool limits, run timestamps, inference traces, saved final SQL and actual usage. Keep BIRD gold SQL **out of model prompts and agent tools**.
3. Score **actual model-generated final SQL** using KORA-03 and preserve failures in the denominator. Separate successful SQL execution from correct result-set EX and from completed user-facing answers.
4. Manually review failed predictions and a representative sample of successful predictions, using reference results **only offline**. Use categories: schema/table/column choice, join error, filtering/aggregation/subquery logic, syntax/execution error, SQL executes but wrong result, timeout/provider error, budget exhaustion, missing SQL and uncertain diagnosis. Record evidence, counts, examples and possible root causes without assuming one root cause per case.
5. Produce a concise **diagnostic decision table**: failure type → observed count/trace IDs → hypothesis → candidate B1/B2/B3 or simpler B0 fix → expected measure → priority. Reserve the held-out local-test set for later evaluation; do not optimize from it.

**Gate status:** A genuine scored dev smoke is **done**. A representative trace-backed root-cause breakdown and justified improvement selection are **not**. Do not present this 25% smoke EX as general model accuracy.

### KORA-06 — B1 Knowledge Graph and Join-path Exploration

- **Priority / phase:** P1 / Phase 3
- **Objective:** Test whether bounded graph-guided relationship exploration helps multi-table queries.
- **Tasks:** Build a lightweight table-column graph from verified schema/FKs; add traceable term/evidence links while clearly separating inferred from verified relations; expose `explore_relationships()` to return bounded k-hop candidate join paths; capture graph traversal traces and path coverage diagnostics.
- **Acceptance criteria:** Demonstrate correct direct and intermediate join paths on known cases; compare **B1 versus B0** using equivalent underlying structural metadata and budget controls; report EX and added work.
- **Dependencies:** KORA-05.
- **Output:** Graph builder, traversal tool, tests and comparison configuration.


**v4.1 selection rule:** Start B1 only if B0 diagnostics reveal recurrent wrong joins, missed intermediate relationships or schema-linking failures. State the expected improvement (e.g. join-path correctness or BIRD EX on multi-table cases), then compare the tested integrated B1 with B0 under the same question IDs, underlying schema access, evaluator and documented budgets. Avoid claiming benefit based on graph construction alone.

### KORA-07 — B2 Explicit Query Planner

- **Priority / phase:** P1 / Phase 3
- **Objective:** Test whether a structured plan improves complex SQL construction.
- **Tasks:** Produce explicit subgoals, tables, join steps, filters, aggregation and expected output before SQL generation; validate plan schema and handle impossible/partial plans; execute through the existing safe SQL adapter; log plans, revisions and errors.
- **Acceptance criteria:** Structured plans are inspectable on representative complex questions; **B2 versus B0** comparison isolates planner behavior under a fixed model and documented budgets.
- **Dependencies:** KORA-05.
- **Output:** Planner module, plan examples, tests and ablation configuration.


**v4.1 selection rule:** Start B2 if actual B0 traces reveal decomposition, filter, aggregation or multi-step SQL-planning failures. Inspect whether structured planning corrects these errors without excessive tool calls or latency. Evaluate the integrated query path, not just standalone plan quality; compare with B0 under recorded matched conditions.

### KORA-08 — B3 Adaptive Model Router

- **Priority / phase:** P1 / Phase 3
- **Objective:** Study the accuracy–cost trade-off of normal/strong model selection.
- **Tasks:** Reuse KORA-05's existing `common.py` explicit-provider factory (do not build a duplicate adapter); verify normal/strong model access, capabilities, quotas and costs (including any potential HKU API); define observable inference-time routing features (context complexity, plan difficulty, tool failures), thresholds and escalation budget; log model choices, tokens, latency and cost. Compare normal-only, strong-only and routed conditions under matched tools/retry limits, with no silent paid fallback.
- **Acceptance criteria:** Normal-only, strong-only and routed conditions run with the **same tools and retry ceiling**; thresholds are chosen without peeking at scored gold outcomes; EX, strong-model fraction and cost comparisons are available.
- **Dependencies:** KORA-05 (including the provider foundation); confirmed stronger-model access or a documented alternative.
- **Output:** Routing policy, model-access notes, tests and experiment configurations.


**v4.1 selection rule:** Start B3 when real outcomes suggest a model-capability/cost/latency trade-off or an escalation need that a router could address. Provider outages belong in reliability testing and do **not** alone establish that accuracy-based routing will help. Establish provider access and equivalent task/tool settings before reporting comparative benefits.

### KORA-09 — B4 Full KORA Integration

- **Priority / phase:** P1 / Phase 3
- **Objective:** Combine adaptive control, KG exploration, query planning and model routing without losing independent ablations.
- **Tasks:** Integrate B1/B2/B3 behind selectable configuration flags; maintain structured state, bounded execution and consistent tool safety; handle component failures and fallbacks; test end-to-end representative BIRD questions.
- **Acceptance criteria:** B4 can run the same questions/evaluator as B0; graph/planner/router can be enabled independently; complete traces and safe failure behavior are documented.
- **Dependencies:** KORA-06, KORA-07, KORA-08.
- **Output:** Integrated B4 variant and reproducible run configuration.


**v4.1 integration gate:** B4 is activated only if there are individually evaluated B1/B2/B3 improvements to integrate **and** the working app, reliability tests and submission package are on schedule. Report single-component ablations and costs; do not treat a planned B4 as the delivery baseline.

### KORA-10 — B0 Evaluation, Reliability and Controlled Improvements

- **Priority:** **P0, start as soon as B0 can be measured**; B1–B4 are not prerequisites.
- **Objective:** Test the complete user-oriented B0 system in addition to the independent BIRD EX benchmark.
- **Tasks:** (1) Freeze BIRD dev IDs and model/settings, run and score final B0 SQL with the existing KORA-03 evaluator; record exact sample coverage and usage. (2) Compare synthetic ordinary/changed/ambiguous user requests to reference results. (3) Test **failure A:** invalid column/syntax → detect → schema reinspection and bounded repair, or safe stop; capture user feedback and trace. (4) Test **failure B:** NVIDIA API timeout/unavailable → identify provider failure, bounded retry or safe stop, visible message; no invented answer or unannounced paid fallback. (5) Measure latency (P50/P95 where meaningful), completions/recovery, calls, tokens and verifiable cost, privacy/read-only checks and repeated external-action risks. (6) Compare B0 to any completed B1/B2/B3/B4 feature or feasible B0 component ablation with matched conditions; disclose any comparison that cannot be completed.
- **Acceptance criteria:** An actual scored B0 run, ordinary and changed-request evidence, **at least two distinct failure cases** with true/clearly identified injected traces and bounded recovery/stop, relevant non-functional results with assumptions and real limitations. End-to-end application results are separated from BIRD EX and synthetic fixtures are never presented as official benchmark scores.
- **Dependencies:** B0 + KORA-02/03 for EX; KORA-14–17 for full application tests. Do not wait for B4.
- **Output:** Per-question data, summary charts, traces, NFR and reliability evidence, component comparison where available, explicit limits and incomplete cases.


**KORA-10 — Evaluation stages and evidence (current)**

- **Stage A — early B0 diagnosis (P0; In Progress):** Four dev questions scored on 1 Nov (**EX 1/4**) and early SQL-difference review started (Section 2). Next inspect complete traces, broaden fixed dev coverage, quantify failure categories and document a justified P1 decision. Do not wait for KORA-14–16.
- **Stage B — controlled improvement analysis (P1; only for integrated changes actually completed):** On matched frozen question IDs and gold-isolated scoring, compare B0 with B1/B2/B3 or meaningful B0 ablations. Track EX, error-category shifts, coverage, latency, token/model/tool calls, and observable costs. Log settings, limitations, variability and regressions. Do not imply that every proposed enhancement must be built.
- **Stage C — interactive application evaluation (P0):** Execute KORA-16's **TC-I01–I04 / TC-R01–R04** against KORA-17's **separate, human-verified** fixture suite. Assess in-scope fresh inputs, condition changes, references, sustained context and ambiguity; capture **two distinct** real or explicitly injected failures with bounded recovery/stop and meaningful user feedback. Include a separate teammate-driven unseen-question rehearsal. Never use synthetic outcomes as BIRD EX.
- **Required report separation:** Track A = **original BIRD Mini-Dev EX** on final saved predictions; Track B = **custom application functional/reliability evaluation** with its own case count and expected outputs. Never present synthetic, ChatGPT-generated or BIRD-derived follow-up cases as official BIRD benchmark scores.

**Failure evidence:** SQL/schema errors must show detection, any schema reinspection and a **bounded** regeneration/re-execution or a safe stop; provider failures must show classification, retry/stop and honest user feedback. Test prohibited writes, empty results, exhausted budgets and state errors where feasible. No automatic claim of recovery when the SQL executes but returns the wrong result.

**Acceptance:** An actual scored B0 diagnostic run, a documented enhancement choice, a runnable application's ordinary/changed/failure results, **at least two distinct failure tests**, and fair comparison evidence for any implemented improvement. Unknown service usage stays `null`/unknown; report P50/P95 only when supported by sufficient observations.

**KORA-10 — Reporting and metric ownership (Stage C, not run):**

| Metric | Definition / interpretation |
| --- | --- |
| Interactive scenario correctness | Number of TC-I cases matching their **human-verified expected results or required clarification** / TC-I cases actually run; also report full planned coverage (4) and P0 coverage (3) |
| Failure detection | Correctly classified injected or observed failures / failure cases executed; keep SQL/schema and provider failure categories distinct |
| Recovery success | Failed requests subsequently completed with verified correct results **within configured limits** / recovery-attempted requests; a safe stop is **not** recovered |
| Safe-stop correctness | Cases where limits/unavailability prohibit safe completion and the system stops with correct user-visible status / applicable stop cases |
| Retry and tool budget compliance | Cases respecting configured retry/model/tool/SQL/time budgets / cases executed; preserve actual counters and limits |
| Efficiency and repeated-action risk | Measured end-to-end latency, calls, tokens, known costs and SQL execution counts; read-only/side-effect checks and repeated-call behavior |

**Evidence contract for each executed scenario:** `test_case_id`, `test_type`, `priority`, `environment/model/version`, `fixture_version/seed`, `session_id`, `conversation_turns`, `expected_intent`, `expected_sql_or_result_or_status`, `actual_sql`, `actual_result/status`, `tool_trace_ref`, `injection_type` (none/SQL/provider/budget), `retry_count`, `budget_limits`, `latency/usage`, `human_review` and `status` (Not Run/Pass/Fail/Blocked). Preserve a clear failed test record instead of removing it from the denominator. Missing observable measurements are unknown, **never assumed zero**. Reports show sample size and distinguish simulated provider faults from naturally encountered failures.

**Stage ownership:** KORA-16 executes application tests, KORA-17 defines fixtures and expected outcomes, and KORA-10 validates results. **Stage A has initial B0 evidence; Stage B comparisons and all Stage C application scenarios remain not run.**
### KORA-11 — Final Report, Runnable Code, AI Use and Submission Package

- **Priority:** **P0 / submission by 25 November 2026, 23:59 HKT**.
- **Report PDF tasks:** State user needs, initial proposal, planned/delivered/unfinished work and material changes; explain agent workflow, decisions, model/version, prompts, tools, data and state using observed traces; evaluate **at least two** failure/recovery situations; show operating assumptions, measured latency/cost/privacy/workload and trade-offs; give representative, challenging and failure evaluation with EX/fair comparison, variability and limitations. Attribute libraries/data/reused work, disclose mocks and list **each member's contributions**. Check the separately published report/code rubric.
- **Runnable submission ZIP:** Include **complete source snapshot** (GitHub link is not a substitute), non-notebook app entry point, tested README with setup/run/evaluation commands, dependency versions, model settings, data/service and paid/hardware requirements, prompts/config, ordinary/changed/failure sample inputs, evaluation scripts/results, success/failure traces, source version, and any required data or access instructions. Keep credentials and sensitive data out.
- **AI-use declaration:** Name AI tools/models, how they helped and include project-related prompts where used. Redact credentials and personal details; declare missing records; AI outputs are not required.
- **Submission formatting:** PDF and ZIP must identify **Group 9, project title and member names** (report and README). Report claims must match actual tested behavior.
- **Acceptance:** Verify submitted ZIP in a clean environment using README and no notebooks; test normal/changed/failure inputs; inspect PDF/ZIP contents and AI-use inventory; disclose unavailable live dependencies and any mocks.
- **Dependencies:** KORA-05/10/16 evidence for final results; report and packaging preparation start earlier. No B4 requirement.
- **Output:** PDF, complete runnable ZIP, reproducibility checklist, prompt/AI declaration, contribution table and source version.

### KORA-12 — Live Presentation, Pitch and Demo

- **Priority:** **P0**. Demo on **1 December or 8 December 2026**; assignment announced after final submission. Every student attends the assigned session (non-attendance receives zero presentation marks).
- **Tasks:** Prepare a **two-minute pitch**: intended users/problem, main agent workflow/decisions, delivered features, one real evaluation result and live-demo preview. Rehearse real in-scope unprepared questions, changed follow-ups, tool decisions and bounded failure recovery. Confirm model/service credentials and data availability, show genuine SQL rows and safe errors, and prepare Q&A on architecture, costs, limitations, team work and AI-assisted implementation. Backup traces are useful, but **recordings do not replace the live demo**.
- **Acceptance:** A teammate launches the exact submitted app and handles an ordinary query, a changed condition and a failure safely and interactively; all members can explain their code and contributions. Rehearse ahead of deadline; keep both dates available.
- **Dependencies:** B0 + KORA-14–17 and preliminary KORA-10 results. B4 is not needed.
- **Output:** Pitch, interactive demo runbook, contingency plan, Q&A notes, attendance coordination.

### KORA-13 — Optional Document RAG Agent (Progress-dependent)

- **Priority / phase:** **P2 / Backlog / Optional**, outside committed BIRD evaluation.
- **Activation gate:** Group may start this only **after** the core SQL agent, BIRD evaluator and essential SQL-only application integration are progressing satisfactorily, with time available for a meaningful independent test. If not activated, leaving it incomplete does not block the SQL MVP or demo.
- **Objective:** Reuse the existing document-RAG prototype as a distinct tool-using agent capable of evidence-based answers.
- **Tasks:** Reuse the private HKU `scr/baselines/rag.py` design if/when reviewed for migration; ingest approved example documents; chunk, embed and retrieve passages; support bounded iterative `search_documents` decisions, citations and abstention on unsupported questions; evaluate on an independent document QA set; record actual tool traces and latency.
- **Acceptance criteria:** If activated, a separately runnable RAG agent returns relevant cited passages, handles missing information, and produces independent QA/grounding diagnostics; its results are **not included in BIRD EX**.
- **Dependencies:** Stable SQL MVP and SQL-only app progress; explicit team go/no-go; optional contract with KORA-14/15.
- **Output:** Optional RAG agent, sample documents, independent evaluation, documentation. The browser **hides/disables RAG mode** until it is verified.

### KORA-14 — SQL Application Backend / Controller

- **Priority:** **P0 / complete runnable system**.
- **Objective:** Connect real B0 reasoning and read-only SQLite data to a user-facing interface.
- **Tasks:** Define the question, optional session/previous-request context, answer/SQL/rows, observed tools, errors/clarification and metadata contract. Build a small secure execution service/controller using FastAPI or an equally suitable integrated solution (framework **TBC**). Validate input and approved source; enforce read-only SQL, time/step/row budgets, explicit retry/stop and secret-safe logging. Handle provider outages without silent fallbacks.
- **Acceptance:** Ordinary in-scope requests run actual B0 and yield results or clear safe stops; invalid requests get informative responses; no RAG or paid fallback dependency; documented entry point and tests.
- **Dependencies:** KORA-05 and KORA-17; response contract can be prepared early.
- **Output:** Controller/API, input-output contract, startup command, tests.


**v4.2 controller contract:** Request includes user question, approved database ID and session ID/context; response includes resolved intent or clarification, safe SQL (if generated), executed rows, state update, observed tool actions, status (success/clarification/recovered/safe-stop), error category and measurable latency/usage. Do not blindly concatenate old SQL: revised filters and referenced result sets must be resolved from conversation context or clarified. Persist **only** the session state needed for follow-ups; prohibit access to arbitrary databases/paths. This contract should support genuinely new in-scope requests, not a fixed demo-question menu.

**v4.2 session and recovery criteria (KORA-14):** Expose a stable session identifier, active approved database, resolved request context (filters/grouping/ordering/limit and referenced entity IDs where valid), and a fresh-request/session reset path. Apply changed conditions without unintentionally dropping retained constraints; ask for clarification when references are ambiguous. Return actual SQL/error and accurate completion/recovered/safe-stop status. Cap SQL/time/tool/model budgets even when a provider or nested tool fails; no silent paid model fallback or unsafe repeated writes. Test requests at the controller level before UI integration.
### KORA-15 — Interactive Text-to-SQL Interface

- **Priority:** **P0 / complete runnable system**.
- **Objective:** Allow analysts/business users to ask questions, update conditions and inspect genuine results/actions.
- **Tasks:** Choose React/Vite, Streamlit or an equivalent simple non-notebook UI (**TBC**). Include ordinary questions, session/changed-condition requests, result tables, safe feedback/clarification and genuine model/tool trace, with available latency/usage. Hide unavailable B1–B4 and optional RAG features.
- **Acceptance:** User can change a condition and obtain correctly updated rows or a justified clarification; failures remain visible; no private paths or credentials exposed.
- **Dependencies:** KORA-14 contract and KORA-17 fixtures; frontend prototype may proceed in parallel.
- **Output:** Runnable interface, local start instructions and UI tests.


**v4.2 UI acceptance:** In a single session, a user can ask a new in-scope question, change a condition (e.g. “Only October”), and ask a context-dependent follow-up (e.g. “Which of those sold the most?”). The visible result must match verified fixture rows or an explicit clarification; the interface must not silently drop context, invent rows or hide provider/SQL failure feedback. Demonstrate tool-observed agent decisions and disclose the database/operation scope.

**v4.2 interactive UI criteria (KORA-15):** Demonstrate in one session: `TC-I01` changed filter, `TC-I02` reference to an entity returned previously and `TC-I03` a sequence of accumulating filters, sort and limit. Render the current interpretation, genuine rows/status or clarification and failure feedback without hard-coding prepared input strings. In the same supported scope, allow a teammate to enter unprepared queries and follow-ups. `TC-I04` adds explicit ambiguous-reference clarification coverage.
### KORA-16 — End-to-End Integration, Reliability and NFR Tests

- **Priority:** **P0 / core guideline gate**.
- **Objective:** Validate user → UI → controller → autonomous B0 → SQLite → answer, including changed conditions and safe failure handling.
- **Tasks:** (1) Test ordinary known-answer question and expected rows. (2) Test a changed request after a first answer in the same session or the planned clarification behavior. (3) Test invalid SQL/column → bounded repair or stop, with recorded observation and feedback. (4) Test API timeout/provider error → bounded retry or safe stop; preserve failure category. (5) Check empty results, invalid inputs, prohibited writes, exhausted budgets and safe repeated actions. (6) Measure latency, completion/recovery and available usage/cost/privacy checks. (7) Fresh-clone/unzip README launch, **without a notebook**, and success/failure trace capture.
- **Acceptance:** Genuine application normal and changed user flows, **two distinct failure cases**, observed decisions and useful user feedback; SQL-only mode works without RAG; documented fresh-run evidence and limitations.
- **Dependencies:** KORA-05, KORA-14/15 and KORA-17. Feeds KORA-10/11/12.
- **Output:** E2E tests, actual and labeled injected failure traces, NFR table, deployment/demo checklist.


**v4.2 KORA-16 formal Test Case Matrix — design only (all cases Not Run).** These are **scenario templates**; the KORA-17 fixture owner must finalize data and execute reference SQL to determine exact expected rows before a test can be run/scored.

**A. Reliability & Recovery** (failure tests; at least **R01 and R02** must have independently recorded results)

| Test ID | Priority | Controlled scenario / injection | Pass criteria |
| --- | --- | --- | --- |
| **TC-R01 — SQL Execution Error** | **P0** | On an approved SELECT task, the SQL execution tool receives an invalid reference such as `revenue_amount` and reports `no such column` (inject at the tool boundary if needed) | Recognize real error observation; reinspect actual schema when appropriate; correct and re-execute within configured limit **or** safely stop; record attempts, final verified rows/status and user feedback |
| **TC-R02 — Model API Timeout** | **P0** | Inject a deterministic NVIDIA/provider timeout or unavailable response at the model adapter | Classify as provider error; obey bounded retry/timeout policy; recover only if an actual result returns, otherwise clear safe stop; never invent SQL/rows or silently switch to paid provider |
| **TC-R03 — Unsafe SQL Operation** | **P1** | Request `DELETE FROM orders` on a throwaway synthetic database | SQL safety layer rejects write/unsafe operation; DB state unchanged; user sees read-only limitation; no execution/retry of prohibited write |
| **TC-R04 — Retry / Tool Budget Exhaustion** | **P1** | Repeated SQL errors or repeated tool calls until configured ceiling is reached | Terminate within explicit model/tool/SQL/retry/time budgets; report safe stop and actual counters; no runaway loop or repeated side effects |

**B. Interactive & Multi-turn** (use a **single session** across all turns inside each scenario; do not reset context between those turns)

| Test ID | Priority | Conversation / input | Pass criteria |
| --- | --- | --- | --- |
| **TC-I01 — Changed Conditions** | **P0** | Turn 1: “Show the top 5 products by revenue in 2026.” → Turn 2: “Only include October.” | Keep revenue/top 5/year and change the date filter to **October 2026**; new actual rows match manually verified reference, not merely plausible SQL |
| **TC-I02 — Contextual Follow-up** | **P0** | Turn 1: “Which customer spent the most in 2026?” → Turn 2: “How many orders did that customer place?” | Resolve `that customer` to the prior answer's customer ID, maintain 2026 unless explicitly changed, and return correct manually verified order count |
| **TC-I03 — Multi-turn Context Updates** | **P0** | Turn 1: “Show revenue by product category in 2026.” → Turn 2: “Only include October.” → Turn 3: “Sort by revenue descending.” → Turn 4: “Show only the top 3.” | Final executed query/output retains category grouping, **October 2026**, descending revenue and top 3 together; expected results match fixture |
| **TC-I04 — Ambiguous Follow-up** | **P1** | Turn 1: “Compare sales for Product A and Product B.” → Turn 2: “Show its monthly revenue.” | Ask which product `its` refers to **without guessing or executing an unsupported assumed reference**; retain enough context to continue after clarification |

**Execution order and evidence:** (1) KORA-17 fixture and manual reference-result verification; (2) focused controller/agent integration tests, with **deterministic fault injection** where needed; (3) genuine UI → controller → agent → database end-to-end runs of the **five P0 cases**, plus P1 when time allows; (4) a separate **unseen-question** interactive rehearsal with unprepared but in-scope questions, follow-ups and changed conditions. Capture actual tool traces/SQL/rows/user messages and distinguish tool-fault simulation from natural model mistakes. SQL error repair passes only with correct observable result or documented safe stop—not SQL compilation alone.

**Acceptance gate:** At least the five P0 scenarios executed and recorded as **Pass/Fail/Blocked**, with goal of **Pass** against their detailed checks; **both R01 and R02 are distinct failure investigations** with detection, bounded recovery/stop and user feedback. Failing or blocked tests remain reported and require limitation discussion; they are not silently marked Done. R03/R04/I04 are P1 **dedicated test scenarios**, but safe read-only SQL, limits and clarification in the real application remain P0 behavior. No code feature, scenario or test is claimed implemented by this planning document.

### KORA-17 — Synthetic Relational Demo and Test Data

- **Priority / phase:** **P0 / Foundation** (parallel to KORA-02/03).
- **Objective:** Generate **deterministic fictional data** for development, automated testing and classroom demo, distinct from original BIRD benchmark data.
- **Tasks:** Design a small fictional retail database with `customers`, `products`, `orders`, `order_items` (and justified additional tables); define PK/FK constraints, realistic prices/dates and cross-table records; implement an idempotent generator/reset script with a fixed random seed and documented row counts; provide human-readable data dictionary and a question-to-reference-SQL / expected-result fixture set. Include **ordinary queries, changed-condition follow-up pairs and failure inputs**, plus joins, ranking, aggregation, empty results and invalid columns; label simulated outages separately. Avoid real customer data or credentials.
- **Acceptance criteria:** A teammate can deterministically generate/reset the database, reproduce expected ordinary and changed-request rows and test two failure conditions; PK/FK integrity passes automatic checks; both SQL unit tests and UI demos can use it. **Synthetic results must never be reported as official BIRD EX.**
- **Dependencies:** None for initial generation; used by KORA-05 and KORA-14–16.
- **Output:** Synthetic schema, generator/reset script, seed, documented fixture questions, expected results, validation tests and demo walkthrough.



**No KORA-01 ticket**: scope was already established by the submitted proposal. There is **no standalone shared-runtime ticket**; reuse `common.py` where useful. Existing BENCH studies can inform KORA-02/03 but are not automatically new tickets.


**v4.2 KORA-17 fixture design and manual verification:** Build deterministic fictional SQLite data with customers/products/orders/order_items, documented date and amount definitions (including **2026 and October 2026** records) and stable customer/product identities to support `TC-I01/I02/I03/I04`. Execute reference SQL **independently** to verify each expected result and updated-context interpretation; human reviewer signs off on turn-level intent and final rows, including ordering/ties and empty results. Include at least two changed-condition pairs and one four-turn session; preserve a fresh-session reset scenario.

For `TC-R01/R02/R04`, describe controlled injection setup (invalid SQL response, provider timeout, budget exhaustion), expected policy branch, maximum retries/timeouts and reset procedure **without** requiring a real paid API outage; `TC-R03` uses a disposable test DB and verifies its checksum/contents remain unchanged. Injected errors must be labeled and repeated-action checks must include SQL executions and provider calls.

Maintain a deterministic case manifest: `test_case_id`, dataset schema/version/checksum/seed, session ID and ordered user turns, reference SQL (evaluator/test-only), expected intent/rows/status, injection setup, configured budgets, source, reviewer and review result. Suggested ChatGPT paraphrases are **proposals**, not automatically gold; a teammate verifies them before freezing the fixture. Separate all interactive data/cases from original BIRD EX, including BIRD-derived follow-ups, and never reveal reference SQL to the agent. All eight scenarios are **planned**, not implemented/passed.

## 6. Evaluation Protocol, Reliability and Non-functional Requirements

| Measure / test | Evidence and metric |
| --- | --- |
| **B0 diagnostic root causes** | Trace-backed counts/examples of wrong schema, joins, filters/aggregation, invalid SQL, successful execution with incorrect results, provider errors, safe stops and unclassified cases; prioritize fixes using observed evidence |
| **BIRD Execution Accuracy (EX)** | Correct final query result sets / frozen question count, using KORA-03 evaluator; missing/failed SQL counts 0 |
| **B0 baseline quality** | EX, coverage, model/tool calls, error categories, SQL generation/execution rate |
| **Changed-request correctness** | TC-I01/I03: retained and updated conditions plus independently verified rows in the same session | 
| **Contextual follow-up correctness** | TC-I02: resolve prior entity ID/date scope; count matches verified reference query | 
| **Ambiguity handling** | TC-I04: clarify ambiguous reference instead of assuming user intent |
| **Failure 1: SQL/schema error** | TC-R01: detect bad SQL, inspect/revise or stop within budget; record trace and user message |
| **Failure 2: API timeout** | TC-R02: classify provider error, limit retry or stop; record honest status and user message |
| **Unsafe SQL and repeated actions** | TC-R03/R04: reject writes, DB unchanged; track repeated model/tool/SQL calls and safe termination |
| **Agentic decisions** | Real tool-selection, observation-dependent revision/stopping traces; do not invent hidden thoughts |
| **Fair improvement comparison** | B0 versus actually tested B1/B2/B3/B4 or feasible B0 component ablation with matched tasks/budgets |
| **Efficiency** | Input/output tokens if available, latency, SQL runtime, model/tool calls and documented cost assumptions |
| **Reliability** | Detection/recovery/safe-stop counts, retry-budget compliance, observed timeout/exhaustion and repeated-action safety; report tested denominator |

**Two distinct evaluation tracks:** (A) original BIRD Mini-Dev fixed-ID benchmark using KORA-03 execution accuracy; (B) separate human-verified interactive/synthetic suite scored for follow-up intent, actual answer/result correctness, clarification, bounded repair/stop and user feedback. Use explicit numerators/denominators for each metric, report case provenance and never combine A and B into one EX. For both tracks, an executable SQL query can still be incorrect.

**Root-cause mapping:** Incorrect joins/relationship selection → consider B1; decomposition, grouping or filter mistakes → consider B2; verified accuracy–cost/provider-capability gaps → consider B3; SQL error recovery, context maintenance and safe stopping → prioritize B0/app reliability without requiring B1–B4. Treat these as hypotheses, not automatic diagnoses.


**Application test pass rules (Stage C, not run):** A scenario is **Pass** only if the observed behavior matches its manually reviewed oracle (correct result or required clarification/safe stop) and applicable safety/limit checks. **Fail** means executed but contrary to expected behavior, **Blocked** means execution could not complete for documented external/setup reasons, and **Not Run** means never attempted. Preserve all four statuses and denominator definitions in KORA-10. A valid SELECT or a polished answer without matching observed results does **not** establish correctness. Report P0 5/5 coverage separately from P1 3/3 coverage; never infer completion from this document.

**Required coverage:** ordinary, challenging/multi-table, changed follow-up, SQL/schema failure and provider failure. SQL-only live/demo fixture is separate from BIRD benchmark EX; mock failure injection must be labeled.

**Non-functional requirement evidence:**

| Area | Observable checks |
| --- | --- |
| Latency | E2E duration, individual request latency if observable, P50/P95 where sample permits and timeouts |
| Cost/workload | Tokens, model calls, credits/cost only if verifiable; service/network/compute assumptions |
| Reliability | Completion and recovery rates, bounded tool/time/SQL retries, safe stopping and risk from repeated external actions |
| Privacy/security | Read-only SQLite, credential secrecy, safe source access, trace privacy and row limits |
| Reproducibility | Python/dependency/model versions, prompts/settings, dataset checksum, IDs/seed, run IDs and startup commands |

**Fairness:** Freeze model, prompt, evidence, BIRD question IDs, dataset/evaluator and budgets for paired comparisons. Use development questions to debug, local test after decisions are frozen; local test is not BIRD's hidden leaderboard. Record run variance; LLM judging, if used, requires explicit criteria and a human cross-check. Missing metrics remain unknown/**null**, not invented zero. Successful SQL execution ≠ EX correctness.

**Validation boundary:** 16/16 selected-case upstream parity is evaluator QA, **not model performance**. A four-dev-question B0 smoke now scored 1/4 strict EX, but representative B0 EX, recovery traces and interactive-app outcomes remain pending. Gold SQL stays evaluator-only.

## 7. Dependencies and Parallel Work

~~~mermaid
flowchart LR
    K02[KORA-02 Dataset Done] --> K03[KORA-03 EX Done]
    K03 --> K05[KORA-05 B0]
    K05 --> K10A[KORA-10 Stage A Diagnose B0]
    K10A -. "Evidence-based P1 choice" .-> K06[KORA-06 B1 KG]
    K10A -.-> K07[KORA-07 B2 Planner]
    K10A -.-> K08[KORA-08 B3 Router]
    K06 -.-> K09[KORA-09 B4 Conditional]
    K07 -.-> K09
    K08 -.-> K09
    K17[KORA-17 Verified fixtures] --> K14[KORA-14 Controller]
    K05 --> K14
    K14 --> K15[KORA-15 Interactive UI]
    K15 --> K16[KORA-16 App E2E Tests]
    K17 --> K16
    K10A --> K10BC[KORA-10 Stage B/C Evaluation]
    K16 --> K10BC
    K09 -. "Only if tested" .-> K10BC
    K10BC --> K11[KORA-11 Final PDF and ZIP]
    K16 --> K11
    K11 --> K12[KORA-12 Live Demo]
~~~

**P0 parallel paths:** **Diagnostics:** KORA-02/03 (done) → KORA-05 → KORA-10 Stage A (frozen B0 EX, trace-backed error analysis, improvement selection). **Application:** KORA-05 + KORA-17 → KORA-14/15 → KORA-16 (free-input, follow-up and reliability tests). **Evidence and submission:** KORA-10 Stages B/C → KORA-11/12. Draft the report and prepare the demo while engineering continues.

**P1 decision point:** Begin B1/B2/B3 from the proposal only when Stage A supports a measurable hypothesis and P0 delivery is protected. B4 depends on completed, validated components, never on the mere existence of a proposal. KORA-10 Stage A **does not depend on KORA-16**, preventing circular scheduling; Stage C does.

**Stop/go rule:** If enhancements are too costly, underperform B0 or risk the final deadline, freeze the SQL-only B0 app and finish interactive testing, two failure cases, honest benchmark results and packaging. List incomplete improvements in the report instead of claiming them integrated.

## 8. Risks and Submission Checklist

| Concern | Plan / required validation |
| --- | --- |
| Application not yet delivered | Prioritize interactive launch and **TC-I01/I02/I03** (changed constraints, contextual follow-ups, multi-turn state); rehearse additional unseen in-scope questions |
| B0 benchmark incomplete | Four-question B0 dev smoke EX 1/4 is available; broaden frozen dev coverage and trace review. Neither 25% smoke EX nor 16/16 scorer parity is representative model accuracy |
| Recovery unverified | Run **TC-R01/R02** as two distinct failure cases with detection, bounded retries/stopping, observed traces, user feedback and explicit injection labels |
| Latency/service availability | Measure actual latency/tokens/credits and disclose NVIDIA or local-model availability and operating assumptions |
| Proposal continuity | Keep original submission unchanged; final report must compare planned and delivered features and document changes |
| Team ownership | Assign members and backups across B0, app, evaluation, report, packaging and demo; record each contribution |
| Research enhancements | Keep B1–B4 P1 and report only tested integrations; optional RAG is P2 |
| Privacy and data | No credentials, personal data, raw sensitive traces, BIRD gold SQL or large DB archives in public packages |
| Group repository | Private HKU source/docs are not automatically in public repo; separate code migration and reproduction verification |
| Rubric | Obtain and check published final report/code rubric in addition to two-page Student Guideline |

**Confirmed submission:** **25 November 2026, 23:59 HKT**. Submit **both** final report PDF and **ZIP with complete runnable source snapshot** (a GitHub URL alone is insufficient). Group number, title and all member names in the PDF and README.

### Required final deliverables

- [ ] **Report PDF:** users, proposal continuity, delivered vs unfinished, decisions/tools/state/prompts/model, two observed failures/recovery, measurable NFRs, fair evaluation/results, limits, attribution and contributions.
- [ ] **Source ZIP:** independent non-notebook entry point and README; dependencies, model settings, setup/run/evaluation, credentials instructions, service/hardware/paid needs, sample ordinary/changed/failure inputs, actual evaluation results and success/failure traces, source version/snapshot.
- [ ] **AI-use records:** declaration of tools/models and their assistance, project prompts, missing-record disclosure and redaction of private/secret content.
- [ ] **Reproduction:** install from clean archive, start app via README, test ordinary/changed/error input, validate model/runtime access or clearly label mocks.
- [ ] **Scenario evidence:** Record executed P0 TC-R01/R02 and TC-I01/I02/I03 with expected vs actual outputs, error/decision traces, user feedback, budgets and reviewer sign-off; separately disclose P1 TC-R03/R04/I04 status and any blocked/failed cases.
- [ ] **Demo:** **1 December or 8 December 2026**, all members attend assigned session; two-minute pitch, live in-scope free inputs, follow-ups/changed conditions, actual tool decisions and recovery, Q&A. Recordings are not a substitute.
- [ ] **Team rehearsal and package verification:** validate PDF and ZIP, member credits, prompt logs and demo credentials before submission.

### Team execution decisions

1. Assign P0 owners for KORA-05, KORA-10 Stage A diagnosis, KORA-10/11/12 delivery and KORA-14–17; treat B1–B4 as evidence-selected P1 experiments.
2. Choose simplest robust non-notebook interface and ensure it handles user changes, errors and safe stops.
3. Run a frozen B0 dev diagnostic sample first, categorize observed failures and select B1/B2/B3 improvements only against explicit hypotheses. Compare only tested, integrated improvements and preserve all failed/negative evidence in the final report.
4. Prepare report/ZIP/AI-use inventory early, and test README in a fresh environment.
5. Keep both demo days available; publish to public group repo only through a separately reviewed migration.

## 9. References

- [Group README](README.md), [B0 beginner tutorial](docs/bird-b0.md), [Developer guide](docs/agent-development.md)
- [BIRD setup](docs/bird-setup.md), [Execution Accuracy guide](docs/bird-evaluation.md), [B0 code](scr/baselines/bird_b0.py)
- [Original BIRD Mini-Dev](https://github.com/bird-bench/mini_dev) and [pinned official scorer](https://github.com/bird-bench/mini_dev/blob/abd11b6db92a1c9f809b32f7564c7c71b34d67f0/evaluation/evaluation_ex.py)
- Proposal and course guideline documents are maintained separately, not included in this code-only public migration.

---

**Document state (1 November 2026):** Shared group edition of HKU v4.3 B0-first delivery roadmap. KORA-02/03 foundation complete; KORA-05 and KORA-10 Stage A have a **four-dev-question scored smoke (EX 1/4)** and early error diagnosis. Current Windows suite, representative benchmark, P1 comparisons, working interactive app and all TC-I/TC-R scenario executions remain pending. See canonical tutorials for commands.

**Maintenance:** Keep only essential earlier validation and proposal differences as provenance. Prioritize frozen B0 diagnostics, interactive SQL app, reliability scenarios and submission; public group repo migration is reflected in this edition.
