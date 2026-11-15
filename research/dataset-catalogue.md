# Agentic System Datasets and Evaluation Environments: Organized by Domain

> **Historical research note (2026-10-25):** This 34-benchmark catalogue was prepared before final topic selection. Group 9 has selected **KORA** on the **original BIRD Mini-Dev** for its Text-to-SQL evaluation. This file is retained as earlier topic-selection research; see the [submitted KORA proposal](../proposal/KORA/KORA_Group9_Proposal.pdf).

Compiled: 2026-10-04 (Hong Kong Time)

**Reference answer availability:** See the [dedicated check of all 34 resources](dataset-answer-availability.md) for public answers/solutions, answer formats, split restrictions and tasks evaluated through outcomes rather than standard written answers. The check covers official documentation and visible samples, not a full per-record completeness audit.

This catalogue supports topic selection and comparison. It contains 34 resources across 11 categories. Each entry includes official sources, data and uses, an agent that could be built, evaluation methods, access conditions and a possible improvement experiment.

The research used Exa for 15 search batches, inspecting 105 candidate results (103 after simple URL deduplication), followed by checks against author websites, GitHub repositories, Hugging Face dataset cards and original papers. Results can include multiple URLs for the same resource or secondary sources; this catalogue prioritizes authors and official sources. Environments were not installed, complete datasets were not downloaded, gated approval was not obtained, and benchmarks were not run.

**Data descriptions, published scoring methods and access conditions come from the sources. Agent ideas, improvement experiments and starting difficulty are research suggestions in this catalogue, not official conclusions.** Starting difficulty concerns data preparation, environments and engineering costs, not the intrinsic difficulty of the research question.

## How to read this catalogue: datasets and benchmarks

| Type | What it provides | Implications for agent evaluation |
| --- | --- | --- |
| Static dataset with reference answers | Questions, documents/data and answers; sometimes evidence or code | Supports objective result comparison; retrieval, tools and agent workflows usually need to be built |
| Tasks with executable evaluation code | Task inputs, tests, validators or rubrics | Measures whether code/answers meet requirements; development feedback must remain separate from final evaluation |
| Interactive environment | Simulated APIs, websites, VMs, initial states and tasks | Evaluates whether actions actually completed the task; setup and reset costs are higher |
| Raw data without task annotations | Documents, CSVs, products or other data | Supports applications, but questions, gold answers, scoring and held-out tasks must be created separately; it is not a complete agent benchmark |

Most tasks/documents in this catalogue are in English. A Chinese interface can be built separately; translating official test questions into Chinese should be treated as a separate experimental setting rather than directly compared with the original leaderboard.

## Category index

| Category | Resources | Main capabilities |
| --- | ---: | --- |
| 1. Databases, SQL and data analysis | 6 | Querying, cross-source integration, Python analysis and ML experiments |
| 2. Knowledge retrieval, RAG and research QA | 4 | Evidence retrieval, multi-hop reasoning and research search |
| 3. APIs, tool selection and tool calling | 3 | Tool selection, parameters, dependencies and clarification |
| 4. Customer service, CRM and cross-app workflows | 3 | Business policies, multi-turn dialogue and cross-app workflows |
| 5. Software development and repair | 2 | Code generation, localization and bug repair |
| 6. Browser and desktop operation | 3 | UI navigation, state verification and desktop operation |
| 7. Financial reports and numerical reasoning | 3 | Financial-report retrieval, numbers and units |
| 8. Documents, contracts and clause understanding | 3 | Document image reading, clause extraction and proposition verification |
| 9. Scientific literature and research workflows | 3 | Scientific claim verification, literature QA and paper replication |
| 10. Long-term memory and personal assistants | 1 | Cross-session memory, information updates and temporal reasoning |
| 11. Planning, shopping and simulated actions | 3 | Constrained planning, product selection and action prerequisites |

## 1. Databases, SQL and data analysis

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [BIRD Mini-Dev (original 500-question setting)](https://github.com/bird-bench/mini_dev) | Natural-language questions, database contents and schemas, supplementary evidence and reference SQL; useful for evaluating joins and understanding database values. | SQL analysis and repair agent: inspect the schema → generate SQL → execute it → inspect errors or results → repair. | Compare execution results with reference results; also report SQL execution success, Soft F1 and cost. Successful execution does not necessarily mean a correct answer. | Low–medium |
| [Spider 2.0](https://spider2-sql.github.io/) | Enterprise databases, metadata, documentation and complex analysis requests. Settings cover BigQuery, Snowflake and SQLite; the DBT setting covers project-level SQL workflows. | Enterprise data analysis agent: read documentation and the project → identify tables and columns → execute multiple SQL steps → produce a result table. | Compare outputs using the official evaluator for the selected setting. Some settings require CSV output rather than an SQL string. | High |
| [Data Agent Benchmark (DAB)](https://github.com/ucbepic/DataAgentBench) | 12 datasets and 54 queries involving PostgreSQL, MongoDB, SQLite and DuckDB; includes cross-database integration, inconsistent join keys, unstructured text and domain knowledge. | Cross-source analysis agent: locate data → align entities and keys → integrate sources → calculate an answer. | Use each query's validator. The official aggregation stratifies pass@1 by dataset and requires repeated trials. | Medium–high |
| [InfiAgent-DABench](https://github.com/InfiAgent/InfiAgent/tree/main/examples/DA-Agent) | CSV files, analysis questions, answers and required output formats; useful for evaluating statistics, data processing and analytical reasoning. | CSV/Python analysis agent: read files → write pandas code → execute → repair → answer. | Automatically score closed-form answers and formats. The original workflow may use an LLM to reformat answers; keep the scoring workflow consistent. | Low–medium |
| [DS-1000](https://github.com/xlang-ai/DS-1000) | 1,000 Python data-science programming tasks covering pandas, NumPy, SciPy, scikit-learn, Matplotlib, PyTorch and TensorFlow. | Data-science code repair agent: generate code → execute visible examples or self-created checks → read errors → repair. | Use official execution/string tests and report pass rates by library rather than only an overall average. | Low–medium |
| [MLAgentBench](https://github.com/snap-stanford/MLAgentBench) | 13 types of ML engineering tasks in which agents read/write files, train models, analyze metrics and iteratively improve results. | ML experiment agent: select a method → modify training code → run experiments → compare validation results → choose the next experiment. | Use official task evaluators for model performance and success. The original framework defines success through improvement over a baseline; also report time and cost. | High |

### 1. BIRD Mini-Dev (original 500-question setting)

- **Where to find it:** [BIRD authors' GitHub; Hugging Face birdsql/bird_mini_dev](https://github.com/bird-bench/mini_dev).
- **Detailed note:** [BIRD-SQL / BIRD Mini-Dev introduction and agent evaluation notes](bird-sql.md).
- **Resource type:** Dataset with reference answers, databases and evaluation code.
- **Data and uses:** Natural-language questions, database contents and schemas, supplementary evidence and reference SQL; useful for evaluating joins and understanding database values.
- **Agent to build:** SQL analysis and repair agent: inspect the schema → generate SQL → execute it → inspect errors or results → repair.
- **How to evaluate:** Compare execution results with reference results; also report SQL execution success, Soft F1 and cost. Successful execution does not necessarily mean a correct answer.
- **Access and setup:** The official repository and dataset download links are public; the SQLite setting is easier to start with.
- **Possible improvement experiment:** With the same model and budget, compare one-shot generation, repair using error messages, and schema/value inspection.
- **Main limitations:** The original 500 questions are a development subset. Further development/held-out splits are custom splits, not the official test set. The repository also contains V2/LiveSQLBench material; pin the questions, databases, dialect and commit.

### 2. Spider 2.0

- **Where to find it:** [Spider 2.0 official website; xlang-ai/Spider2](https://spider2-sql.github.io/).
- **Resource type:** Enterprise SQL workflow benchmark and data environment.
- **Data and uses:** Enterprise databases, metadata, documentation and complex analysis requests. Settings cover BigQuery, Snowflake and SQLite; the DBT setting covers project-level SQL workflows.
- **Agent to build:** Enterprise data analysis agent: read documentation and the project → identify tables and columns → execute multiple SQL steps → produce a result table.
- **How to evaluate:** Compare outputs using the official evaluator for the selected setting. Some settings require CSV output rather than an SQL string.
- **Access and setup:** The website provides settings and downloads. BigQuery/Snowflake require accounts, access and quotas; the DBT setting can use DuckDB.
- **Possible improvement experiment:** Compare providing the entire schema up front with retrieving metadata on demand; study long-context and multi-step execution costs.
- **Main limitations:** Spider2-Lite, Snow and DBT use different tasks and environments; do not combine their scores. Clearly identify any setting using the officially released oracle tables.

### 3. Data Agent Benchmark (DAB)

- **Where to find it:** [UC Berkeley EPIC Data Lab and Hasura; official GitHub/website](https://github.com/ucbepic/DataAgentBench).
- **Resource type:** Multi-database dataset with task validators.
- **Data and uses:** 12 datasets and 54 queries involving PostgreSQL, MongoDB, SQLite and DuckDB; includes cross-database integration, inconsistent join keys, unstructured text and domain knowledge.
- **Agent to build:** Cross-source analysis agent: locate data → align entities and keys → integrate sources → calculate an answer.
- **How to evaluate:** Use each query's validator. The official aggregation stratifies pass@1 by dataset and requires repeated trials.
- **Access and setup:** Public GitHub repository, downloader and data manifest; configure the DBMS required by the selected data.
- **Possible improvement experiment:** Test whether join-key checks or text normalization before querying improve cross-database tasks.
- **Main limitations:** DAB is distinct from InfiAgent-DABench. There are relatively few tasks, so repeat runs and report per-task results. Pin validator versions and hint settings.

### 4. InfiAgent-DABench

- **Where to find it:** [InfiAgent authors' GitHub; ICML 2024 paper](https://github.com/InfiAgent/InfiAgent/tree/main/examples/DA-Agent).
- **Resource type:** CSV question-answering data and an agent execution/evaluation framework.
- **Data and uses:** CSV files, analysis questions, answers and required output formats; useful for evaluating statistics, data processing and analytical reasoning.
- **Agent to build:** CSV/Python analysis agent: read files → write pandas code → execute → repair → answer.
- **How to evaluate:** Automatically score closed-form answers and formats. The original workflow may use an LLM to reformat answers; keep the scoring workflow consistent.
- **Access and setup:** Public examples/DA-Agent, data and author releases; confirm official test availability for the selected version.
- **Possible improvement experiment:** Compare one-shot code generation, execution-error repair and statistical sanity checks.
- **Main limitations:** Question/CSV counts differ between papers, websites and releases. Verify the actual downloaded version. CSV tasks evaluate analysis correctness, not the quality of a complete open-ended report.

### 5. DS-1000

- **Where to find it:** [DS-1000 authors' GitHub; Hugging Face xlangai/DS-1000](https://github.com/xlang-ai/DS-1000).
- **Resource type:** Programming tasks with execution/string tests.
- **Data and uses:** 1,000 Python data-science programming tasks covering pandas, NumPy, SciPy, scikit-learn, Matplotlib, PyTorch and TensorFlow.
- **Agent to build:** Data-science code repair agent: generate code → execute visible examples or self-created checks → read errors → repair.
- **How to evaluate:** Use official execution/string tests and report pass rates by library rather than only an overall average.
- **Access and setup:** Public JSONL/Hugging Face data and official testing code; pin dependency versions.
- **Possible improvement experiment:** Identify how the benefits of execution feedback differ by library or error category.
- **Main limitations:** This is a local code-generation benchmark, not a complete multi-step business analysis benchmark. Do not expose official evaluation tests or gold solutions as agent repair feedback.

### 6. MLAgentBench

- **Where to find it:** [Stanford authors' GitHub; ICML 2024 paper](https://github.com/snap-stanford/MLAgentBench).
- **Resource type:** ML experiment tasks, data and execution environments.
- **Data and uses:** 13 types of ML engineering tasks in which agents read/write files, train models, analyze metrics and iteratively improve results.
- **Agent to build:** ML experiment agent: select a method → modify training code → run experiments → compare validation results → choose the next experiment.
- **How to evaluate:** Use official task evaluators for model performance and success. The original framework defines success through improvement over a baseline; also report time and cost.
- **Access and setup:** Public code; some datasets require a Kaggle account and acceptance of competition terms, and some tasks need GPUs.
- **Possible improvement experiment:** Under a fixed experiment count/training budget, compare random search, a simple fixed strategy and a results-driven agent.
- **Main limitations:** Separate agent decision costs, training costs and hardware differences. Do not repeatedly select models using the final test set.

## 2. Knowledge retrieval, RAG and research QA

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [HotpotQA](https://hotpotqa.github.io/) | Multi-hop questions, answers and supporting facts. The distractor setting provides 10 article passages per question; fullwiki also provides a retrieval corpus. | Evidence-seeking agent: decompose the question → retrieve information → assess evidence completeness → search again → answer with citations. | Answer EM/F1, supporting-fact EM/F1 and joint scores distinguish correct answers from incorrect citations. | Low–medium |
| [MuSiQue](https://github.com/StonyBrookNLP/musique) | Multi-hop questions composed from dependent single-hop questions. Ans and Full settings are available; Full includes unanswerable cases. | Multi-step knowledge reasoning agent: use the previous answer to search for the next step; stop or abstain when evidence is missing. | Answer F1 and support F1; evaluate answerability/abstention according to the selected setting. | Medium |
| [BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus) | Research questions from BrowseComp paired with approximately 100,000 fixed documents and retrieval relevance annotations, enabling reproducible deep-search experiments. | Deep research agent: repeatedly generate queries → search the fixed corpus → synthesize evidence → verify the final answer. | Use the official answer scoring workflow; additionally measure document Recall/nDCG, query count and cost. Retrieval metrics are not final task success. | Medium–high |
| [GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) | Questions requiring search, calculation, file reading or multimodal understanding, divided into three levels by tool and reasoning difficulty. | Research/general assistant agent: select search, Python, document or image tools as needed to solve the question. | Use the official final-answer matching rules; also record tool success, elapsed time and cost. | Medium–high |

### 7. HotpotQA

- **Where to find it:** [HotpotQA official website; hotpotqa/hotpot](https://hotpotqa.github.io/).
- **Detailed note:** [HotpotQA introduction and evaluation notes](hotpotqa.md).
- **Resource type:** Wikipedia question answering with sentence-level evidence annotations.
- **Data and uses:** Multi-hop questions, answers and supporting facts. The distractor setting provides 10 article passages per question; fullwiki also provides a retrieval corpus.
- **Agent to build:** Evidence-seeking agent: decompose the question → retrieve information → assess evidence completeness → search again → answer with citations.
- **How to evaluate:** Answer EM/F1, supporting-fact EM/F1 and joint scores distinguish correct answers from incorrect citations.
- **Access and setup:** Official train/dev data, Wikipedia corpus and scoring code.
- **Possible improvement experiment:** Compare single retrieval, iterative retrieval and evidence-completeness checks; report distractor and fullwiki separately.
- **Main limitations:** Widely used public benchmarks may be contaminated. Distractor scores do not establish open-web search capability. Putting every supplied article in one prompt may not require an agent.

### 8. MuSiQue

- **Where to find it:** [MuSiQue authors' GitHub; TACL 2022 paper](https://github.com/StonyBrookNLP/musique).
- **Detailed note:** [MuSiQue introduction and evaluation notes](musique.md).
- **Resource type:** Two- to four-hop questions with supporting-paragraph annotations.
- **Data and uses:** Multi-hop questions composed from dependent single-hop questions. Ans and Full settings are available; Full includes unanswerable cases.
- **Agent to build:** Multi-step knowledge reasoning agent: use the previous answer to search for the next step; stop or abstain when evidence is missing.
- **How to evaluate:** Answer F1 and support F1; evaluate answerability/abstention according to the selected setting.
- **Access and setup:** Official download scripts and evaluator are public.
- **Possible improvement experiment:** Study where question decomposition, stepwise search and completeness verification help, by hop count or question type.
- **Main limitations:** Avoid training or tuning prompts with seed single-hop questions corresponding to dev/test examples. Do not mix Ans and Full scores.

### 9. BrowseComp-Plus

- **Where to find it:** [BrowseComp-Plus authors' GitHub; Tevatron data release](https://github.com/texttron/BrowseComp-Plus).
- **Detailed note:** [BrowseComp-Plus introduction and evaluation notes](browsecomp-plus.md).
- **Resource type:** Research questions, a fixed document corpus and relevance judgments.
- **Data and uses:** Research questions from BrowseComp paired with approximately 100,000 fixed documents and retrieval relevance annotations, enabling reproducible deep-search experiments.
- **Agent to build:** Deep research agent: repeatedly generate queries → search the fixed corpus → synthesize evidence → verify the final answer.
- **How to evaluate:** Use the official answer scoring workflow; additionally measure document Recall/nDCG, query count and cost. Retrieval metrics are not final task success.
- **Access and setup:** Public code, a script for obtaining obfuscated questions and the corpus; downloads may require a Hugging Face token.
- **Possible improvement experiment:** Fix the corpus, retriever and model; vary only the search stopping policy or evidence checking.
- **Main limitations:** Fixed-corpus search is not equivalent to live-web BrowseComp. Indexing, storage and retrieval services add setup work.

### 10. GAIA

- **Where to find it:** [GAIA authors' official Hugging Face dataset card](https://huggingface.co/datasets/gaia-benchmark/GAIA).
- **Resource type:** General knowledge tasks requiring tools, with attachments for some tasks.
- **Data and uses:** Questions requiring search, calculation, file reading or multimodal understanding, divided into three levels by tool and reasoning difficulty.
- **Agent to build:** Research/general assistant agent: select search, Python, document or image tools as needed to solve the question.
- **How to evaluate:** Use the official final-answer matching rules; also record tool success, elapsed time and cost.
- **Access and setup:** Gated dataset requiring acceptance of terms. Validation includes answers; test answers and some metadata are private.
- **Possible improvement experiment:** Compare fixed tool workflows with dynamic tool selection. Analyze errors by level and divide answer-visible validation tasks into development and held-out tasks.
- **Main limitations:** Do not call validation the official test set. Live-web content changes, so record sources, access times and page versions. Official terms prohibit public redistribution of crawlable questions.

## 3. APIs, tool selection and tool calling

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html) | Tool definitions, user requests, parameters and multi-turn tasks, including relevant/irrelevant tools and broader agentic evaluation. Select categories for the chosen version. | Tool routing and calling agent: decide whether a tool is needed → choose a tool → populate parameters → handle multi-turn dependencies. | Use official category-specific AST, execution or multi-turn state scoring. Do not describe every category as measuring actual tool execution success. | Low–medium |
| [API-Bank](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/api-bank) | Executable simulated tools, tool-use dialogues and API call annotations, with planning, retrieving and calling task levels. | API workflow assistant: understand the request → find tools → combine APIs → respond to the user. | Use the official evaluator to check API calls and results. Report dialogue output quality separately from workflow scoring. | Low–medium |
| [ToolSandbox](https://github.com/apple/ToolSandbox) | Tool state, implicit prerequisites, multi-turn dialogue and intermediate/final milestones; useful for studying missing information and dependencies between tools. | Assistant that clarifies and verifies state: check prerequisites → ask the user when necessary → call tools → verify the result. | Score intermediate and final milestones along the trajectory; also measure invalid tool calls and clarification costs. | Medium |

### 11. BFCL

- **Where to find it:** [UC Berkeley Gorilla official leaderboard; gorilla repository](https://gorilla.cs.berkeley.edu/leaderboard.html).
- **Resource type:** Function-calling data with category-specific evaluation code.
- **Data and uses:** Tool definitions, user requests, parameters and multi-turn tasks, including relevant/irrelevant tools and broader agentic evaluation. Select categories for the chosen version.
- **Agent to build:** Tool routing and calling agent: decide whether a tool is needed → choose a tool → populate parameters → handle multi-turn dependencies.
- **How to evaluate:** Use official category-specific AST, execution or multi-turn state scoring. Do not describe every category as measuring actual tool execution success.
- **Access and setup:** Official code/data and bfcl-eval. The website described V4 at the research date; pin the version and categories.
- **Possible improvement experiment:** Test whether tool-description retrieval, parameter validation or clarification of missing information reduces incorrect calls.
- **Main limitations:** Simple function-call scores do not establish long-workflow success. Correct syntax and parameters do not guarantee a correct business outcome.

### 12. API-Bank

- **Where to find it:** [AlibabaResearch authors' GitHub; EMNLP 2023 paper](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/api-bank).
- **Resource type:** Simulated APIs, dialogue data and an evaluator.
- **Data and uses:** Executable simulated tools, tool-use dialogues and API call annotations, with planning, retrieving and calling task levels.
- **Agent to build:** API workflow assistant: understand the request → find tools → combine APIs → respond to the user.
- **How to evaluate:** Use the official evaluator to check API calls and results. Report dialogue output quality separately from workflow scoring.
- **Access and setup:** Public simulated tools, initial databases, dialogue samples and evaluator.
- **Possible improvement experiment:** Compare exposing all tool specifications with on-demand tool lookup; analyze tool, parameter and ordering errors.
- **Main limitations:** Training and evaluation resources differ in scale. Do not treat the larger training API count as the number of runnable evaluation tools.

### 13. ToolSandbox

- **Where to find it:** [Apple official GitHub; authors' paper](https://github.com/apple/ToolSandbox).
- **Detailed note:** [ToolSandbox introduction and evaluation notes](toolsandbox.md).
- **Resource type:** Stateful tool environment, user simulator and milestone evaluation.
- **Data and uses:** Tool state, implicit prerequisites, multi-turn dialogue and intermediate/final milestones; useful for studying missing information and dependencies between tools.
- **Agent to build:** Assistant that clarifies and verifies state: check prerequisites → ask the user when necessary → call tools → verify the result.
- **How to evaluate:** Score intermediate and final milestones along the trajectory; also measure invalid tool calls and clarification costs.
- **Access and setup:** Public environment; both the user simulator and agent may require model APIs.
- **Possible improvement experiment:** Compare standard ReAct, explicit prerequisite checking and clarification of missing information.
- **Main limitations:** Fix the user simulator model, seed and environment version. Do not attribute all simulator instability to differences in agent capability.

## 4. Customer service, CRM and cross-app workflows

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [τ-bench family (τ²/τ³)](https://github.com/sierra-research/tau2-bench) | Customer-service tasks in airline, retail and telecom domains, with policies, databases, tools and multi-turn interaction. Newer versions add settings such as voice/knowledge. | Policy-aware customer-service agent: clarify → inspect policies and data → refund/change orders/troubleshoot → explain and verify outcomes. | Use each task's reward_basis to check final database state, required communications and other criteria; repeat runs for reliability. Audit trajectories separately for complete policy compliance. | Medium |
| [CRMArena-Pro](https://github.com/SalesforceAIResearch/CRMArena) | B2B/B2C sales, customer-service and quotation workflow tasks, including multi-turn interaction, roles/personas and confidentiality awareness evaluation. | Enterprise CRM agent: analyze trends, identify recurring issues, route cases/leads, and check quotations and business stages. | Use official task answer/action-result evaluators for success; report confidentiality and multi-turn performance separately. | Medium–high |
| [AppWorld](https://appworld.dev/) | Simulated data and cross-app tasks for everyday apps such as email, shopping, music and payments; provides 457 APIs and controllable initial states. | Cross-app personal assistant: read data → write code or call APIs → coordinate apps → verify changes. | Official state/execution tests assess task completion and unintended changes; report success and collateral damage. | Medium–high |

### 14. τ-bench family (τ²/τ³)

- **Where to find it:** [Sierra Research official GitHub; docs/evaluation.md](https://github.com/sierra-research/tau2-bench).
- **Resource type:** Business policies, simulated APIs/users, tasks and scoring.
- **Data and uses:** Customer-service tasks in airline, retail and telecom domains, with policies, databases, tools and multi-turn interaction. Newer versions add settings such as voice/knowledge.
- **Agent to build:** Policy-aware customer-service agent: clarify → inspect policies and data → refund/change orders/troubleshoot → explain and verify outcomes.
- **How to evaluate:** Use each task's reward_basis to check final database state, required communications and other criteria; repeat runs for reliability. Audit trajectories separately for complete policy compliance.
- **Access and setup:** Public code and simulated data. Text settings avoid voice setup; agent and simulator models are required.
- **Possible improvement experiment:** Compare pre-action policy checks and post-action verification; report outcome success and policy violations separately.
- **Main limitations:** The tau2-bench repository carried τ³ updates and grading fixes at the research date. Pin the release/commit, domain, split and simulator. Passing final-state checks does not prove every policy step was compliant.

### 15. CRMArena-Pro

- **Where to find it:** [Salesforce AI Research official GitHub; Salesforce/CRMArenaPro](https://github.com/SalesforceAIResearch/CRMArena).
- **Resource type:** Synthetic CRM data, professional tasks and a Salesforce test environment.
- **Data and uses:** B2B/B2C sales, customer-service and quotation workflow tasks, including multi-turn interaction, roles/personas and confidentiality awareness evaluation.
- **Agent to build:** Enterprise CRM agent: analyze trends, identify recurring issues, route cases/leads, and check quotations and business stages.
- **How to evaluate:** Use official task answer/action-result evaluators for success; report confidentiality and multi-turn performance separately.
- **Access and setup:** Authors' data is public on Hugging Face; the official workflow involves a Salesforce org/API. GitHub states public GUI access has closed and requires a separate application.
- **Possible improvement experiment:** Test whether retrieving business policies on demand improves case routing or handling of sensitive data.
- **Main limitations:** These are simulated/synthetic enterprise data, not the company's CRM. Downloading data does not grant immediate access to every operational environment; keep evaluation modes separate.

### 16. AppWorld

- **Where to find it:** [AppWorld official website; StonyBrookNLP/appworld](https://appworld.dev/).
- **Resource type:** Nine simulated apps, APIs, tasks and state/execution tests.
- **Data and uses:** Simulated data and cross-app tasks for everyday apps such as email, shopping, music and payments; provides 457 APIs and controllable initial states.
- **Agent to build:** Cross-app personal assistant: read data → write code or call APIs → coordinate apps → verify changes.
- **How to evaluate:** Official state/execution tests assess task completion and unintended changes; report success and collateral damage.
- **Access and setup:** Public package, data and API explorer. test_normal/test_challenge provide evaluation code; preserve development restrictions.
- **Possible improvement experiment:** Compare individual API calls with programmatic batch operations, or add final-state verification.
- **Main limitations:** Simulated apps do not connect to real Amazon, banks or email. Keep evaluation code, reference solutions and task setup internals out of the agent's inputs.

## 5. Software development and repair

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [SWE-bench Verified](https://www.swebench.com/verified) | 500 human-verified issue tasks. Inputs are issue descriptions and the repository at the relevant state; outputs are repair patches. | Repository bug-repair agent: locate files → modify code → run available tests → check regressions → submit a patch. | Resolved rate from the official Docker harness, checking tests that need to be fixed and tests that must remain passing. | High |
| [BigCodeBench](https://github.com/bigcode-project/bigcodebench) | 1,140 Python tasks with multiple libraries and complex instructions; includes Complete/Instruct and Hard settings. | Small code implementation/repair agent: understand requirements → look up library usage → execute visible checks → repair. | Use official unit tests; report pass@1 or a clearly defined pass@k. | Low–medium |

### 17. SWE-bench Verified

- **Where to find it:** [SWE-bench official website; SWE-bench/SWE-bench](https://www.swebench.com/verified).
- **Resource type:** Real GitHub issues, repository states and a test harness.
- **Data and uses:** 500 human-verified issue tasks. Inputs are issue descriptions and the repository at the relevant state; outputs are repair patches.
- **Agent to build:** Repository bug-repair agent: locate files → modify code → run available tests → check regressions → submit a patch.
- **How to evaluate:** Resolved rate from the official Docker harness, checking tests that need to be fixed and tests that must remain passing.
- **Access and setup:** Public tasks and Docker evaluator; launch execution environments for the repositories.
- **Possible improvement experiment:** Compare one improvement at a time, such as direct localization, retrieval-based localization, execution feedback or review; fix rollout/cost budgets.
- **Main limitations:** Do not expose official test_patch, gold patches or evaluation answers as repair feedback. Passing task tests does not establish that every production bug is fixed.

### 18. BigCodeBench

- **Where to find it:** [BigCode authors' GitHub; official paper arXiv:2406.15877](https://github.com/bigcode-project/bigcodebench).
- **Resource type:** Function-level programming requirements with unit tests.
- **Data and uses:** 1,140 Python tasks with multiple libraries and complex instructions; includes Complete/Instruct and Hard settings.
- **Agent to build:** Small code implementation/repair agent: understand requirements → look up library usage → execute visible checks → repair.
- **How to evaluate:** Use official unit tests; report pass@1 or a clearly defined pass@k.
- **Access and setup:** Public data and evaluation package. The original main repository was marked archived when researched; verify dependencies and pin versions.
- **Possible improvement experiment:** Compare one-shot generation with autonomous debugging under equal generation/execution budgets.
- **Main limitations:** Function-level code scores do not establish repository-level agent success. Keep evaluation tests held out; do not use hidden-test failures to guide the agent directly.

## 6. Browser and desktop operation

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [WebArena](https://github.com/web-arena-x/webarena) | Interactive shopping, forum and GitLab-style websites with text tasks; the environment supplies initial website states. | Browser workflow agent: locate pages → fill forms/perform actions → check page or backend state. | The official harness checks task outcomes or environment state; an agent's final claim of completion is insufficient. | High |
| [WorkArena](https://github.com/ServiceNow/WorkArena) | Enterprise knowledge-work tasks such as forms, search, lists, sorting and navigation, plus more complex combined workflows. | Internal enterprise operations agent: locate records → execute forms/workflows → confirm platform results. | Task validators check actual outcomes; also report steps and time. | High |
| [OSWorld/OSWorld-Verified](https://github.com/xlang-ai/OSWorld) | Multi-step browser, LibreOffice, file and desktop app tasks, with initial machine states and final checks. | Computer-use agent: inspect screenshots/available UI information → click and type → verify file or app results. | Task-specific execution/state evaluators; track success, steps, time and environment failures. | Very high |

### 19. WebArena

- **Where to find it:** [WebArena official GitHub; webarena.dev](https://github.com/web-arena-x/webarena).
- **Resource type:** Self-hosted website environments, tasks and state-based scoring.
- **Data and uses:** Interactive shopping, forum and GitLab-style websites with text tasks; the environment supplies initial website states.
- **Agent to build:** Browser workflow agent: locate pages → fill forms/perform actions → check page or backend state.
- **How to evaluate:** The official harness checks task outcomes or environment state; an agent's final claim of completion is insufficient.
- **Access and setup:** Public Docker/deployment resources and tasks; set up websites and a browser environment.
- **Possible improvement experiment:** Compare DOM-only input, adding screenshots and explicit outcome verification.
- **Main limitations:** Reset behavior, service availability and evaluator versions affect scores. Label ServiceNow's WebArena-Verified separately from the original setting.

### 20. WorkArena

- **Where to find it:** [ServiceNow official GitHub; WorkArena/BrowserGym](https://github.com/ServiceNow/WorkArena).
- **Resource type:** ServiceNow operation tasks, platform instances and validators.
- **Data and uses:** Enterprise knowledge-work tasks such as forms, search, lists, sorting and navigation, plus more complex combined workflows.
- **Agent to build:** Internal enterprise operations agent: locate records → execute forms/workflows → confirm platform results.
- **How to evaluate:** Task validators check actual outcomes; also report steps and time.
- **Access and setup:** Apply for gated ServiceNow/WorkArena-Instances, await approval and install BrowserGym/Playwright.
- **Possible improvement experiment:** Compare a generic browser agent with one using task-navigation memory or form verification.
- **Main limitations:** Keep L1 and WorkArena++ settings separate. A platform instance is required; downloading task JSON alone does not make the benchmark runnable.

### 21. OSWorld/OSWorld-Verified

- **Where to find it:** [OSWorld authors' GitHub; os-world.github.io](https://github.com/xlang-ai/OSWorld).
- **Resource type:** VM desktop environments, task configurations and execution evaluation.
- **Data and uses:** Multi-step browser, LibreOffice, file and desktop app tasks, with initial machine states and final checks.
- **Agent to build:** Computer-use agent: inspect screenshots/available UI information → click and type → verify file or app results.
- **How to evaluate:** Task-specific execution/state evaluators; track success, steps, time and environment failures.
- **Access and setup:** Public code with VM/cloud support; a Verified update was released in 2025.
- **Possible improvement experiment:** Study before/after action verification or failure recovery with a fixed VM and step budget.
- **Main limitations:** Requires VMs, resets and multimodal operation. OS, image resolution, Verified version and interaction mode affect comparisons.

## 7. Financial reports and numerical reasoning

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [FinQA](https://github.com/czyssrs/FinQA) | Numerical financial-report questions with reference calculation programs, such as ratios, growth rates and differences; includes supporting facts and execution answers. | Financial-report calculation agent: find numbers and periods → write a calculation program/use a calculator → verify units → cite an answer. | Execution accuracy and program accuracy. Explain alignment if using a different program representation. | Low–medium |
| [TAT-QA](https://github.com/NExTplusplus/TAT-QA) | 16,552 questions from 2,757 hybrid financial-report contexts; includes numerical, single/multiple span, comparison and sorting questions. | Joint table-and-text analysis agent: identify answer locations → combine table/text → calculate → check scale. | Official EM/F1 with rules for numbers, spans and scale; report results by question type. | Low–medium |
| [FinanceBench (public sample)](https://github.com/patronus-ai/financebench) | 150 public annotated financial-report questions with evidence, justifications and document metadata; useful for studying document retrieval and hallucinations. | Financial-report research agent: retrieve company documents → extract evidence → calculate if necessary → answer with sources. | Assess correctness and evidence against gold answers/evidence. Free-text answers need explicit human rules or a fixed judge; the original study included human review. | Medium |

### 22. FinQA

- **Where to find it:** [FinQA authors' GitHub; EMNLP 2021 paper](https://github.com/czyssrs/FinQA).
- **Resource type:** Financial report text/tables, answers, reasoning programs and evidence.
- **Data and uses:** Numerical financial-report questions with reference calculation programs, such as ratios, growth rates and differences; includes supporting facts and execution answers.
- **Agent to build:** Financial-report calculation agent: find numbers and periods → write a calculation program/use a calculator → verify units → cite an answer.
- **How to evaluate:** Execution accuracy and program accuracy. Explain alignment if using a different program representation.
- **Access and setup:** Public data and evaluation scripts. Public test includes answers; private test lacks gold references.
- **Possible improvement experiment:** Compare text-only reasoning with evidence extraction, a calculator and unit verification.
- **Main limitations:** This is not stock-price or trading-strategy data and cannot evaluate investment returns. Distinguish supplied-context tasks from retrieval over complete reports.

### 23. TAT-QA

- **Where to find it:** [TAT-QA official GitHub/website; ACL 2021 paper](https://github.com/NExTplusplus/TAT-QA).
- **Resource type:** Tables, associated text and QA annotations.
- **Data and uses:** 16,552 questions from 2,757 hybrid financial-report contexts; includes numerical, single/multiple span, comparison and sorting questions.
- **Agent to build:** Joint table-and-text analysis agent: identify answer locations → combine table/text → calculate → check scale.
- **How to evaluate:** Official EM/F1 with rules for numbers, spans and scale; report results by question type.
- **Access and setup:** Public data; authors released test ground truth in 2024.
- **Possible improvement experiment:** Study strategies for selecting a table tool, text retrieval or calculator according to the question.
- **Main limitations:** The original setting supplies hybrid context. Adding full-PDF retrieval or OCR creates an additional setting with separately defined evaluation.

### 24. FinanceBench (public sample)

- **Where to find it:** [Patronus AI official GitHub; FinanceBench authors' paper](https://github.com/patronus-ai/financebench).
- **Resource type:** Financial-report QA with reference answers, evidence and explanations.
- **Data and uses:** 150 public annotated financial-report questions with evidence, justifications and document metadata; useful for studying document retrieval and hallucinations.
- **Agent to build:** Financial-report research agent: retrieve company documents → extract evidence → calculate if necessary → answer with sources.
- **How to evaluate:** Assess correctness and evidence against gold answers/evidence. Free-text answers need explicit human rules or a fixed judge; the original study included human review.
- **Access and setup:** GitHub provides the 150-question sample and document information. Do not assume the paper's full 10,231-question collection is publicly downloadable.
- **Possible improvement experiment:** Compare RAG, long-context input and an iterative agent with evidence checks under equal costs.
- **Main limitations:** 150 questions is a small sample. Do not draw strong conclusions solely from an LLM judge; manually spot-check and report per-task results. This is not trading backtest data.

## 8. Documents, contracts and clause understanding

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [DocVQA (original Single Document setting)](https://www.docvqa.org/datasets/docvqa) | Approximately 50,000 questions and 12,000 document images; answers are generally text spans within an image. | Document reading agent: choose OCR/visual reading → locate the answer region → cross-check → answer. | The original task uses ANLS to measure similarity to reference text. Check metrics separately for other DocVQA years/subtasks. | Medium |
| [CUAD](https://www.atticusprojectai.org/cuad) | 510 commercial contracts with over 13,000 labels supervised by legal professionals; useful for evaluating extraction of specified clauses. | Contract clause assistant: search by clause type → extract text and locations → check for missed exceptions. | Clause/span extraction precision, recall and F1, or official QA scores. Additional risk ratings require new gold labels. | Low–medium |
| [ContractNLI](https://stanfordnlp.github.io/contract-nli/) | 607 NDAs with 17 fixed propositions labeled Entailment, Contradiction or NotMentioned, plus supporting/refuting evidence. | Contract QA and verification agent: retrieve clauses → compare the proposition → inspect exceptions/negation → classify and cite. | Proposition classification and evidence-span identification; report official evaluator components separately. | Low–medium |

### 25. DocVQA (original Single Document setting)

- **Where to find it:** [DocVQA official website; RRC official challenge/task pages](https://www.docvqa.org/datasets/docvqa).
- **Resource type:** Document images, questions and extractive answers.
- **Data and uses:** Approximately 50,000 questions and 12,000 document images; answers are generally text spans within an image.
- **Agent to build:** Document reading agent: choose OCR/visual reading → locate the answer region → cross-check → answer.
- **How to evaluate:** The original task uses ANLS to measure similarity to reference text. Check metrics separately for other DocVQA years/subtasks.
- **Access and setup:** Obtain data from the RRC challenge Download page; check portal account and usage conditions.
- **Possible improvement experiment:** Compare a direct vision model, OCR plus a text model, and cross-verification between vision and OCR.
- **Main limitations:** Primarily measures reading answers in documents, not long workflows or arbitrary report summarization. Keep 2026 competition data separate from the original 2020 setting.

### 26. CUAD

- **Where to find it:** [The Atticus Project official website and authors' data release](https://www.atticusprojectai.org/cuad).
- **Resource type:** Legal contracts with annotations for 41 clause/span categories.
- **Data and uses:** 510 commercial contracts with over 13,000 labels supervised by legal professionals; useful for evaluating extraction of specified clauses.
- **Agent to build:** Contract clause assistant: search by clause type → extract text and locations → check for missed exceptions.
- **How to evaluate:** Clause/span extraction precision, recall and F1, or official QA scores. Additional risk ratings require new gold labels.
- **Access and setup:** Official GitHub/Hugging Face download entry points; CC BY 4.0.
- **Possible improvement experiment:** Compare fixed-chunk retrieval with clause-specific retrieval and merging across chunks.
- **Main limitations:** Annotations concern clause extraction, not complete legal compliance or risk assessment. Original scores do not establish reliable legal advice.

### 27. ContractNLI

- **Where to find it:** [Stanford authors' official website and data](https://stanfordnlp.github.io/contract-nli/).
- **Resource type:** NDA contracts, three-way proposition labels and evidence spans.
- **Data and uses:** 607 NDAs with 17 fixed propositions labeled Entailment, Contradiction or NotMentioned, plus supporting/refuting evidence.
- **Agent to build:** Contract QA and verification agent: retrieve clauses → compare the proposition → inspect exceptions/negation → classify and cite.
- **How to evaluate:** Proposition classification and evidence-span identification; report official evaluator components separately.
- **Access and setup:** Public JSON, document text, spans and annotation formats.
- **Possible improvement experiment:** Test whether explicit checks for exceptions and negation reduce misclassification.
- **Main limitations:** Primarily NDA documents with fixed hypotheses; results do not generalize automatically to arbitrary contracts or legal questions.

## 9. Scientific literature and research workflows

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [SciFact](https://github.com/allenai/scifact) | Scientific claims, paper abstracts and supporting/refuting evidence sentences; useful for evidence retrieval and claim verification. | Scientific fact-checking agent: find abstracts → inspect evidence → support/refute/report insufficient evidence → cite. | Official abstract-level and sentence-level precision, recall and F1, including labels and rationales. | Low–medium |
| [BioASQ (Task b)](https://bioasq.org/) | Biomedical literature retrieval and QA, including yes/no, factoid/list exact answers and paragraph-style ideal answers; use according to the challenge year/task. | Biomedical literature research assistant: search corpora such as PubMed → collect evidence → answer and write a grounded summary. | Year/task-specific retrieval and exact-answer metrics; ideal answers involve automatic summarization metrics and expert human assessment. | Medium–high |
| [PaperBench](https://github.com/openai/frontier-evals/tree/main/project/paperbench) | Requires understanding ICML 2024 papers, implementing code and running experiments; each paper has a replication rubric decomposed into subtasks. | Paper replication agent: read methods → design an implementation → write code → run experiments → debug and produce reproducible results. | Execute submitted code in a fresh environment and grade replication against the rubric; the framework includes an LLM judge and JudgeEval. | Very high |

### 28. SciFact

- **Where to find it:** [AllenAI official GitHub; doc/evaluation.md](https://github.com/allenai/scifact).
- **Resource type:** Scientific claims, an abstract corpus and label/rationale annotations.
- **Data and uses:** Scientific claims, paper abstracts and supporting/refuting evidence sentences; useful for evidence retrieval and claim verification.
- **Agent to build:** Scientific fact-checking agent: find abstracts → inspect evidence → support/refute/report insufficient evidence → cite.
- **How to evaluate:** Official abstract-level and sentence-level precision, recall and F1, including labels and rationales.
- **Access and setup:** Public data and scripts; train/dev include annotations. Official test label access/scoring depends on the current challenge procedure.
- **Possible improvement experiment:** Compare direct judgment, retrieval plus judgment and additional counter-evidence search.
- **Main limitations:** Labels are grounded in the abstract corpus, not necessarily current scientific consensus. Failure to find evidence does not prove a claim false.

### 29. BioASQ (Task b)

- **Where to find it:** [BioASQ official challenge and data portal](https://bioasq.org/).
- **Resource type:** Biomedical expert questions, articles/snippets and exact/ideal answers.
- **Data and uses:** Biomedical literature retrieval and QA, including yes/no, factoid/list exact answers and paragraph-style ideal answers; use according to the challenge year/task.
- **Agent to build:** Biomedical literature research assistant: search corpora such as PubMed → collect evidence → answer and write a grounded summary.
- **How to evaluate:** Year/task-specific retrieval and exact-answer metrics; ideal answers involve automatic summarization metrics and expert human assessment.
- **Access and setup:** Official annual releases; some access/participation requires registration. Full text/corpora follow the conditions of their sources.
- **Possible improvement experiment:** Compare one retrieval with multiple-query synthesis; evaluate retrieved evidence, exact answers and summaries separately.
- **Main limitations:** Exact and ideal answers have different scoring. EM alone cannot evaluate every question type; results establish literature QA performance only.

### 30. PaperBench

- **Where to find it:** [OpenAI official GitHub; ICML 2025 authors' paper](https://github.com/openai/frontier-evals/tree/main/project/paperbench).
- **Resource type:** 20 ML papers, author-collaborated rubrics and replication/grading infrastructure.
- **Data and uses:** Requires understanding ICML 2024 papers, implementing code and running experiments; each paper has a replication rubric decomposed into subtasks.
- **Agent to build:** Paper replication agent: read methods → design an implementation → write code → run experiments → debug and produce reproducible results.
- **How to evaluate:** Execute submitted code in a fresh environment and grade replication against the rubric; the framework includes an LLM judge and JudgeEval.
- **Access and setup:** Public code and Git-LFS data; replication may require GPUs, external data/models, API keys and multiple containers.
- **Possible improvement experiment:** Study experiment-result tracking, staged verification or failure recovery within a clearly limited compute budget.
- **Main limitations:** High runtime and compute costs usually make this unsuitable for a first low-budget project. Evaluate judge errors; this is not equivalent to purely deterministic unit tests.

## 10. Long-term memory and personal assistants

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [LongMemEval (original/cleaned setting)](https://github.com/xiaowu0162/LongMemEval) | 500 questions testing information extraction, cross-session reasoning, knowledge updates, temporal reasoning and abstention. | Long-term memory assistant: store updateable information → retrieve history → resolve old/new information → answer or abstain. | The official QA evaluator uses a judge. Additional retrieval, update, latency and storage/token cost metrics can be defined separately. | Low–medium |

### 31. LongMemEval (original/cleaned setting)

- **Where to find it:** [LongMemEval authors' official GitHub; longmemeval-cleaned](https://github.com/xiaowu0162/LongMemEval).
- **Resource type:** Timestamped cross-session conversations, questions and reference answers.
- **Data and uses:** 500 questions testing information extraction, cross-session reasoning, knowledge updates, temporal reasoning and abstention.
- **Agent to build:** Long-term memory assistant: store updateable information → retrieve history → resolve old/new information → answer or abstain.
- **How to evaluate:** The official QA evaluator uses a judge. Additional retrieval, update, latency and storage/token cost metrics can be defined separately.
- **Access and setup:** Public cleaned data and evaluation-only requirements.
- **Possible improvement experiment:** Compare full history, summary memory, vector retrieval and memory with timestamps/update rules.
- **Main limitations:** Fix the cleaned version, history length and judge. Original historical-conversation QA does not establish full interactive agent task success. V2 was available in 2026 with web/enterprise trajectories and should be treated as a separate setting.

## 11. Planning, shopping and simulated actions

| Resource and official source | Data / uses | Agent to build | Evaluation | Starting difficulty |
| --- | --- | --- | --- | --- |
| [TravelPlanner](https://github.com/OSU-NLP-Group/TravelPlanner) | Transport, accommodation, dining and attraction data with budget/schedule constraints; supports data lookup plus planning and sole-planning. | Travel planning agent: look up options → build an itinerary → verify budget/feasibility → revise. | Official constraints and final-pass metrics check environment, commonsense and hard constraints. | Medium |
| [WebShop](https://github.com/princeton-nlp/WebShop) | Real product text and user constraints; agents search, inspect products, choose attributes and purchase in a simulated store. | Shopping agent: convert needs into queries → compare products → verify price/specifications → select. | Official reward/success based on selected products/attributes and target constraints; also analyze search cost. | Medium |
| [ALFWorld (text environment)](https://github.com/alfworld/alfworld) | Household tasks involving object search, movement, placement, cleaning and heating with action prerequisites; the text setting supports abstract multi-step planning. | Planning and failure-recovery agent: inspect state → plan actions → execute → replan when blocked. | Task completion, step counts and invalid actions; distinguish seen/unseen tasks and text/visual settings. | Low–medium (text setting) |

### 32. TravelPlanner

- **Where to find it:** [OSU NLP official GitHub; ICML 2024 paper](https://github.com/OSU-NLP-Group/TravelPlanner).
- **Resource type:** Travel databases, requests/constraints and a planning evaluator.
- **Data and uses:** Transport, accommodation, dining and attraction data with budget/schedule constraints; supports data lookup plus planning and sole-planning.
- **Agent to build:** Travel planning agent: look up options → build an itinerary → verify budget/feasibility → revise.
- **How to evaluate:** Official constraints and final-pass metrics check environment, commonsense and hard constraints.
- **Access and setup:** Public databases, tools and evaluation code.
- **Possible improvement experiment:** Compare one-shot generation with a constraint checker and iterative repair, holding tool/model budgets constant.
- **Main limitations:** Fixed benchmark data is not live travel pricing or bookable inventory. Keep sole-planning and two-stage modes separate.

### 33. WebShop

- **Where to find it:** [Princeton NLP official GitHub; NeurIPS 2022 paper](https://github.com/princeton-nlp/WebShop).
- **Resource type:** Product data, shopping instructions and a simulated store.
- **Data and uses:** Real product text and user constraints; agents search, inspect products, choose attributes and purchase in a simulated store.
- **Agent to build:** Shopping agent: convert needs into queries → compare products → verify price/specifications → select.
- **How to evaluate:** Official reward/success based on selected products/attributes and target constraints; also analyze search cost.
- **Access and setup:** Public environment and data; small/all setups are available, but require product indexes and dependencies.
- **Possible improvement experiment:** Test whether checking each required attribute before purchase reduces similar-but-noncompliant selections.
- **Main limitations:** Operates only in a simulated store. Built-in reward approximates preference satisfaction and does not establish real user satisfaction.

### 34. ALFWorld (text environment)

- **Where to find it:** [ALFWorld authors' official GitHub; ICLR 2021 paper](https://github.com/alfworld/alfworld).
- **Resource type:** Text/embodied simulation environments with goals and state feedback.
- **Data and uses:** Household tasks involving object search, movement, placement, cleaning and heating with action prerequisites; the text setting supports abstract multi-step planning.
- **Agent to build:** Planning and failure-recovery agent: inspect state → plan actions → execute → replan when blocked.
- **How to evaluate:** Task completion, step counts and invalid actions; distinguish seen/unseen tasks and text/visual settings.
- **Access and setup:** Public Python package and game/PDDL data; the text setting does not require the full visual THOR environment.
- **Possible improvement experiment:** Compare ReAct, explicit subgoals and replanning with recorded failure reasons.
- **Main limitations:** An abstract simulation; text results do not establish physical robot capability. Clearly distinguish settings with admissible commands from baselines without them.

## Directions to compare first

These were possible research directions during topic selection. The chosen KORA project uses original BIRD Mini-Dev for knowledge-guided Text-to-SQL; the remaining options are historical comparisons.

| Research question | Resources to consider | Direct improvement experiments |
| --- | --- | --- |
| Can an agent analyze CSVs/tables reliably? | InfiAgent-DABench, FinQA, TAT-QA | Execution feedback, calculator, number/unit checks |
| Can it retrieve information and provide complete evidence? | HotpotQA, MuSiQue, SciFact | Question decomposition, iterative retrieval, counter-evidence/missing-evidence checks |
| Can it choose tools and complete multi-step tasks? | BFCL, API-Bank, ToolSandbox | Tool retrieval, parameter checks, prerequisites and clarification |
| Can it handle enterprise data and policies? | Data Agent Benchmark, CRMArena-Pro, τ-bench family | Cross-source key alignment, policy retrieval, outcome verification |
| Can it remember current information and avoid outdated data? | LongMemEval | Timestamps, memory updates, retrieval versus summaries |
| Can it generate plans satisfying multiple constraints? | TravelPlanner, ALFWorld | Constraint checker, subgoals, failure recovery |
| Can it actually modify code, websites or desktops? | SWE-bench Verified, WebArena, OSWorld | Localization, execution/state feedback; allow more environment engineering time |

## A useful evaluation structure

1. Pin the dataset version, split, databases/corpus, tools, model, evaluator and judge.
2. Establish a simple baseline on development tasks; compare one-shot answering/generation with an agent using the same model.
3. Analyze error categories and add one targeted improvement.
4. Compare on held-out tasks that were not used to tune prompts or workflows; include a baseline with the same cost/time budget.
5. Report correctness, per-task cost, latency, tool calls and repeated-run reliability. For small samples, include per-task results and uncertainty.
6. Record user simulator, LLM judge and environment failures separately. Fix the LLM judge and manually spot-check judgments.

For resources with gold answers only in dev/validation, create development and held-out subsets and explicitly describe the latter as a custom held-out set. Grouping by database, document/contract, conversation history or question family can reduce near-duplicate leakage compared with a fully random question split; the appropriate split depends on the research objective.

**Evaluation isolation:** Agents may use permitted tools, examples and development feedback, while the scoring workflow retains final-evaluation gold answers, reference SQL, gold patches, hidden tests and evaluator internals. Do not repeatedly tune prompts on the final held-out set and then present the same tasks as unseen evidence.

## Common metrics

| Metric | Meaning and limitations |
| --- | --- |
| EM (Exact Match) | Exact agreement after the benchmark's normalization; rules differ between benchmarks |
| F1 | Harmonic mean of precision and recall; answer-token, evidence and extracted-span F1 are different measures |
| Execution accuracy | Whether execution results meet the reference criteria, not merely whether SQL/code runs without errors |
| pass@1 | Success in one attempt; aggregation and repeated-trial definitions depend on the benchmark |
| pass@k | Estimated probability that at least one of multiple candidates succeeds; extra attempts generally increase cost |
| τ-bench pass^k | Reliability across repeated attempts that all succeed, unlike pass@k's at-least-one-success interpretation |
| State-based evaluation | Checks the system state after actions; useful for action agents, but validators may miss side effects |
| LLM-as-judge | Model-based scoring under a rubric; supports free text but has bias and instability, requiring fixed rules and human spot-checks |
| ANLS | Document-QA text similarity based on normalized edit distance; here it refers to the original DocVQA setting |

## Important access, version and scoring checks

- **BIRD Mini-Dev:** The starting setting here is the original 500 questions. The same repository has newer material; do not combine versions, dialects or tasks as one setting.
- **InfiAgent-DABench:** Data counts differ across the original paper, official proceedings, website and repository. Verify question IDs, CSV counts and annotations against the actual release files before experiments.
- **GAIA:** Gating and redistribution restrictions apply. Distinguish validation gold answers from the official test's private answers.
- **FinanceBench:** The public sample contains 150 questions; the paper describes a full collection of 10,231. This catalogue does not assume the full collection is public.
- **τ-bench:** The official tau2-bench repository carried τ³ updates and grading fixes when researched. Use the chosen release/commit and task evaluator; a matching final database does not establish compliance at every policy step.
- **WorkArena:** Official access requires a ServiceNow instance application. A dataset download is not the full environment.
- **CRMArena-Pro:** API and GUI access are separate routes. Official documentation says GUI access is no longer public and requires an application. No org was logged into or tested in this research.
- **BigCodeBench:** The original main repository was marked archived when checked. Data and papers remain references; package setup was not verified.
- **DocVQA:** This catalogue covers the original Single Document 2020 task. The 2026 document reasoning competition uses separate data and scoring.
- **LongMemEval:** Original/cleaned conversation data and new V2 trajectory data are different settings. Official author V2 dataset page: [xiaowu0162/longmemeval-v2](https://huggingface.co/datasets/xiaowu0162/longmemeval-v2).
- **PaperBench:** Formal replication involves fresh execution environments, GPUs and rubric/judge grading, with greater engineering cost than ordinary QA data.

## Additional official methodology sources checked

- [InfiAgent-DABench ICML 2024 proceedings](https://proceedings.mlr.press/v235/hu24s.html)
- [MuSiQue paper](https://aclanthology.org/2022.tacl-1.31/)
- [DAB official website and pass@1 aggregation](https://ucbepic.github.io/DataAgentBench/)
- [DAB submission rubric and permitted data sources](https://github.com/ucbepic/DataAgentBench/blob/main/SUBMISSION_RUBRIC.md)
- [τ-bench task schema and evaluation](https://github.com/sierra-research/tau2-bench/blob/main/docs/evaluation.md)
- [τ-bench v1.0.1 grading fixes](https://github.com/sierra-research/tau2-bench/releases/tag/v1.0.1)
- [AppWorld official repository and split/evaluation restrictions](https://github.com/StonyBrookNLP/appworld)
- [BigCodeBench original paper](https://arxiv.org/html/2406.15877v3)
- [DocVQA RRC official tasks and ANLS](http://rrc.cvc.uab.es/?ch=17&com=tasks)
- [SciFact official evaluation guide](https://github.com/allenai/scifact/blob/master/doc/evaluation.md)
- [BioASQ 2026 official task/evaluation information](https://bioasq.org/)
- [PaperBench original paper](https://proceedings.mlr.press/v267/starace25a.html)
- [LongMemEval official QA evaluator](https://github.com/xiaowu0162/LongMemEval/blob/main/src/evaluation/evaluate_qa.py)

This work covers source research and topic exploration. Whether an environment runs correctly on your computer/VM still requires a smoke run after selecting a small number of candidates.
