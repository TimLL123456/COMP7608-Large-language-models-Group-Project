# Reference Answer Availability for 34 Agent Datasets and Benchmarks

Checked: 2026-10-04 (Hong Kong Time)  
Scope: The 34 resources across 11 domains in the [dataset catalogue](dataset-catalogue.md).  
Project status update (2026-10-25): **KORA** was selected with the **original BIRD Mini-Dev** for evaluation. This 34-resource survey is historical dataset-selection research, not a current shortlist; see the [final proposal](../proposal/KORA/KORA_Group9_Proposal.pdf).

## Finding

**Not all 34 resources provide a question and a publicly viewable reference answer for every task or split.**

Some publish direct answers, some publish reference SQL, code or classification labels, and others publish task goals, state checks or grading rubrics. A benchmark can evaluate success without releasing a complete reference response.

This record answers the practical question: **after an agent responds to a dataset question or task, what reference material can the researcher inspect to review correctness?** It does not establish a common scoring scale across benchmarks.

## How to read the availability column

| Availability | Meaning |
| --- | --- |
| Available | The specified released setting provides inspectable reference answers or structured reference solutions. This does not imply that every other version or split has public answers. |
| Split-dependent | Reference material is released for specified splits, while another split does not release it. |
| Task/category-dependent | Some tasks provide answers or expected calls; others use action or state checks. |
| Task outcome rather than Q&A | The reference is a goal, final state, metric, demonstration or rubric, rather than one standard written answer to each question. |

**Train** means training data; **dev/validation** means development or validation data; **test** means evaluation data. Answers described as available are available to the researcher/evaluator under the source's access conditions, and should not be supplied to the agent as test inputs.

## 1. Databases, SQL and data analysis

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 1. [BIRD Mini-Dev](https://github.com/bird-bench/mini_dev) | Natural-language database question, schema/database and supplementary evidence | Available: reference SQL | The original 500-question setting includes `question` and annotated `SQL`, plus a gold SQL file. Execute the reference SQL on the matching database to obtain the expected result. Keep this setting separate from newer V2/LiveSQLBench material. |
| 2. [Spider 2.0](https://spider2-sql.github.io/) | Enterprise SQL workflow or analysis request | Available: gold output results | The official release provides examples and gold answers for self-evaluation. Only a limited amount of gold SQL is released, so do not assume every task has a reference SQL program. Use the gold result files and evaluator for the selected Lite/Snow/DBT setting. |
| 3. [Data Agent Benchmark (DAB)](https://github.com/ucbepic/DataAgentBench) | Data-analysis query over one or more data sources | Available | The documented query layout includes `query.json`, `ground_truth.csv` and `validate.py`. The reference answer can be inspected directly; the validator checks the required result. |
| 4. [InfiAgent-DABench](https://github.com/InfiAgent/InfiAgent/tree/main/examples/DA-Agent) | CSV analysis question, constraints and required output format | Split-dependent | Public validation questions are in `data/da-dev-questions.jsonl`; matching labels are in `data/da-dev-labels.jsonl`, including `common_answers`. The official README states that only validation is kept public, not the test dataset. |
| 5. [DS-1000](https://huggingface.co/datasets/xlangai/DS-1000) | Python data-science programming problem | Available: reference code | The released data include `prompt`, `reference_code` and `code_context` with testing support. The reference is executable code rather than a prose answer. |
| 6. [MLAgentBench](https://github.com/snap-stanford/MLAgentBench) | ML research/engineering task, starter code and data | Task outcome rather than Q&A | Provides research goals, starter baselines and performance evaluators. There is no single standard written response for each task; review the submitted implementation and achieved performance against the task goal/baseline. |

## 2. Knowledge retrieval, RAG and research QA

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 7. [HotpotQA](https://hotpotqa.github.io/) | Multi-hop question and article context or retrieval corpus | Split-dependent | Train/dev provide reference answers and supporting facts. The official test questions do not come with publicly released answer labels for local review; official test scoring uses the submission process. |
| 8. [MuSiQue](https://github.com/StonyBrookNLP/musique) | Multi-hop question and paragraphs | Available in public train/dev | Public train/dev provide answers, accepted answer aliases and supporting-paragraph annotations. MuSiQue-Full also includes unanswerable examples: an answerability label is the correct reference for those cases, rather than a substantive answer. This check does not make an additional claim about test-label availability. |
| 9. [BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus) | Research question and fixed document corpus | Available | The official download/deobfuscation workflow supplies queries, answers and relevance judgments. The answers are inspectable after following that workflow. |
| 10. [GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) | Tool-assisted question, sometimes with attachments | Split-dependent | The public dev/validation setting contains `Question` and `Final answer`. Official test answers and annotator metadata are private. Access is gated and subject to the dataset's terms. |

## 3. APIs, tool selection and tool calling

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 11. [BFCL](https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard) | User request, function definitions and, for some categories, multi-turn context | Task/category-dependent | Function-calling categories use expected calls/parameters or execution references. Other categories check whether a tool should be called, clarification behavior or state progression. It is not a uniform collection of complete reference prose responses, and reference formats vary by BFCL version/category. |
| 12. [API-Bank](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/api-bank) | Tool-use dialogue and available APIs | Available: dialogue and API annotations | Published dialogue data include user utterances, assistant responses and annotated API calls with inputs/outputs. The author [dataset release](https://huggingface.co/datasets/liminghao1630/API-Bank) also provides expected-output formats. Review the appropriate dialogue/API reference for the selected evaluation level. |
| 13. [ToolSandbox](https://github.com/apple/ToolSandbox) | Stateful scenario and simulated user conversation | Task outcome rather than Q&A | Scenario code defines intermediate/final milestones and target-state constraints; some include expected communication conditions. It does not supply one complete standard assistant response for every possible conversation. |

## 4. Customer service, CRM and cross-app workflows

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 14. [tau-bench family (tau2/tau3)](https://github.com/sierra-research/tau2-bench) | Customer-service scenario, business policy, tools and simulated user | Task/category-dependent | Customer-service tasks specify expected actions, information to communicate and/or outcome requirements. Inspect the task schema and evaluator for the chosen domain/release; do not assume each task has a complete gold dialogue or a single standard final reply. |
| 15. [CRMArena-Pro](https://huggingface.co/datasets/Salesforce/CRMArenaPro) | CRM work request and task metadata/context | Available | The official data card explicitly defines `query` and ground-truth `answer`. Depending on the task, the answer can be a value, record ID or list rather than a paragraph. Answer availability does not supply the required CRM environment by itself. |
| 16. [AppWorld](https://github.com/StonyBrookNLP/appworld) | Cross-app task instruction and initial application data | Split-dependent: reference programs | Train/dev release setup, validation solution and evaluation programs. Test-normal/test-challenge release evaluation programs but not the authors' written solutions or setup programs. Test success can be scored locally even when the reference solution is unavailable. |

## 5. Software development and repair

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 17. [SWE-bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified) | Repository issue/problem statement and base revision | Available: reference patch | The public data include `problem_statement`, a reference `patch`, `test_patch` and test lists. The patch is inspectable; correctness is evaluated through the task tests, since other valid patches need not match the reference text. |
| 18. [BigCodeBench](https://huggingface.co/datasets/bigcode/bigcodebench) | Python function implementation prompt | Available: reference code | The released data include prompts, `canonical_solution` and `test`. These provide a readable reference implementation and executable checks. |

## 6. Browser and desktop operation

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 19. [WebArena](https://github.com/web-arena-x/webarena/blob/main/config_files/test.raw.json) | Website question or browser action request | Task/category-dependent | Question-answering tasks can contain `eval.reference_answers`. Action tasks instead use URL, page-content or backend-state checks. Not every task has a reference written answer. |
| 20. [WorkArena](https://github.com/ServiceNow/WorkArena) | ServiceNow information request or UI workflow task | Task/category-dependent | Knowledge-base/chart QA tasks have expected answers; action tasks use validators and hand-written oracle/`cheat()` programs. These reference programs can be inspected or run in the required environment; there is no uniform prose-answer list for all tasks. |
| 21. [OSWorld / OSWorld-Verified](https://github.com/xlang-ai/OSWorld) | Desktop action instruction, files and initial application state | Task outcome rather than Q&A | Task evaluators compare expected files, application settings or final state. Some tasks have reference output files; others check conditions directly. These are not standard chat answers. See the [original evaluation design](https://arxiv.org/html/2404.07972v2). |

## 7. Financial reports and numerical reasoning

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 22. [FinQA](https://github.com/czyssrs/FinQA) | Financial-report text/table and numerical question | Split-dependent | Train/dev and public `test.json` provide answers and calculation programs. `private_test.json` contains questions without public gold references. |
| 23. [TAT-QA](https://github.com/NExTplusplus/TAT-QA) | Question over financial-report tables and text | Available in the original released setting | Provides reference answers and annotations such as answer type and scale. The authors released the original test-set ground truth in January 2024, in addition to train/dev annotations. |
| 24. [FinanceBench](https://github.com/patronus-ai/financebench) | Financial-report question and source documents | Available for the public 150-example sample | The public examples provide `question`, human-annotated `answer`, evidence and justification. This statement concerns the public sample, not public access to the entire collection described in the paper. |

## 8. Documents, contracts and clause understanding

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 25. [DocVQA (original Single Document setting)](https://www.docvqa.org/datasets/docvqa) | Question and document image | Split-dependent | Train/validation provide question-answer annotations, including accepted answer strings. Official test answer labels are withheld for challenge evaluation. Download access follows the RRC portal's terms; this record concerns the original setting, not later competitions. |
| 26. [CUAD](https://huggingface.co/datasets/theatticusproject/cuad) | Contract text and clause-extraction question | Available: annotated text spans | The SQuAD-style release supplies questions and answer spans. An empty answer is a valid reference when the requested clause is absent; it should not automatically be treated as a missing annotation. |
| 27. [ContractNLI](https://stanfordnlp.github.io/contract-nli/) | Contract and hypothesis/statement | Available: classification labels | Provides `Entailment`, `Contradiction` or `NotMentioned` labels and evidence annotations. Evidence is defined for entailment/contradiction. It is a labeled verification task, not open-ended QA. |

## 9. Scientific literature and research workflows

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 28. [SciFact](https://github.com/allenai/scifact) | Scientific claim and candidate paper abstracts | Split-dependent: labels/evidence | Train/dev provide evidence and support/refutation annotations. The official README states that test labels are not released. The reference is claim classification/evidence rather than a standard written answer. |
| 29. [BioASQ (Task b)](https://www.bioasq.org/participate/challenges) | Biomedical question and literature-search task | Split-dependent / challenge-stage-dependent | Published historical training data include gold articles/snippets and exact/ideal answers as applicable to question type. New challenge test questions do not provide gold answers during the response phase; availability depends on the annual release and stage. |
| 30. [PaperBench](https://openai.com/index/paperbench/) | ML paper and replication requirements | Task outcome rather than Q&A | Provides paper-replication tasks and detailed grading rubrics. There is no single reference written answer or unique complete implementation for every task. Inspect the rubric and replication evidence rather than comparing final response text. |

## 10. Long-term memory and personal assistants

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 31. [LongMemEval (original/cleaned setting)](https://github.com/xiaowu0162/LongMemEval) | Question, timestamped history and cross-session conversations | Available | The original/cleaned question records include reference `answer` values. Abstention tasks also have expected-answer behavior. The cleaned release is linked from the official repository; this record does not extend the claim to V2 agent-trajectory tasks. |

## 11. Planning, shopping and simulated actions

| # / Resource and official source | Question or task input | Availability | Reference material and public scope |
| --- | --- | --- | --- |
| 32. [TravelPlanner](https://huggingface.co/datasets/osunlp/TravelPlanner) | Travel request, constraints and travel databases | Split-dependent: reference plans | Training supplies human `annotated_plan` demonstrations (45 query-plan pairs). Validation has no human-annotated plans, and test does not publish reference plans. Correctness is mainly checked against constraints; multiple different plans can be valid. |
| 33. [WebShop](https://github.com/princeton-nlp/WebShop/blob/master/web_agent_site/engine/goal.py) | Shopping instruction and simulated product catalogue | Task outcome rather than Q&A | Goal data specify target products/attributes, options and price constraints for reward calculation. These are inspectable success targets, not a standard written answer paragraph for each request. |
| 34. [ALFWorld (text environment)](https://github.com/alfworld/alfworld/tree/master/alfworld/data) | Household task instruction and simulated world | Task outcome rather than Q&A | Provides task goals, success conditions and expert demonstration data. Demonstration representation depends on the selected setting. Review action traces and final-state success rather than similarity to a gold written response. |

## Implications for reviewing an agent response

- For direct-answer datasets, inspect the reference answer from the selected public annotated split.
- For SQL/code/patch tasks, the reference solution is inspectable, but correct alternatives can differ textually; use the official result/test criteria.
- For classification/extraction tasks, compare the required labels or spans.
- For action/planning tasks, inspect the target state, constraints, reference program or rubric. A statement such as "done" is not evidence that the task succeeded.
- Where test answers are private, use a public labeled development split for local answer review, or the official test evaluator/submission process for test scoring.

Reference availability alone does not provide a universal "percentage of correct points" for a response. Scoring definitions remain benchmark-specific; see the [catalogue's evaluation discussion](dataset-catalogue.md#common-metrics).

## Verification scope and limitations

This check reviewed official websites, author repositories, dataset cards, documented fields, visible samples and evaluation descriptions. It did not download and audit every record in all 34 resources, obtain gated access, install benchmark environments or run agents/evaluators.

**"Available" is a statement about the documented release/schema and inspected examples, not a guarantee that every record is complete or that every split/version publishes answers.** No claim of withheld labels is inferred merely from a missing answer field in an inaccessible page. Before experiments, pin the actual release/split and check question-to-answer joins and missing labels in the downloaded files.

Source links are attached to each row. The data counts and task versions described here should be rechecked against the chosen release before implementation.

[Back to project README](../README.md) · [Full dataset catalogue](dataset-catalogue.md)
