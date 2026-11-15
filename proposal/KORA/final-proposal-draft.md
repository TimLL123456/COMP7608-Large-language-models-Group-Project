# KORA: An Agentic Knowledge Assistant for Multi-Step Retrieval and Reasoning

**COMP7608B · Group 9 · Final Proposal Draft (for group discussion)**  
**Status:** Revised working draft — **not** a replacement for the previously submitted `KORA_Group9_Proposal.pdf`.  
**Last updated:** 2026-10-28 (HKT)  
**Approval status:** Additional scope is **proposed and pending group agreement**, especially document QA, hybrid integration, product domain, frontend and backend.

> **Scope distinction.** The submitted proposal formally commits to BIRD Mini-Dev Text-to-SQL evaluation. This document retains that research design and proposes adding a Multi-hop Knowledge Retrieval track and a product-oriented Hybrid demonstration. It does **not** claim that the proposed additions have been approved, built, evaluated, or submitted to the course.

## 1. Group Members

Group 9 membership is unchanged from the original submitted proposal. The official PDF contains the confirmed member names and student IDs; this working draft does not alter the roster.

## 2. Project Objective

**KORA (Knowledge-Oriented Reasoning Agent)** is a modular agentic AI system designed to understand complex user questions, choose relevant tools, retrieve and connect structured and unstructured evidence, perform multi-step reasoning, and revise its actions using observable feedback.

The proposed system has two complementary abilities:

1. **Knowledge-guided Text-to-SQL (confirmed):** Discover database schemas, identify tables/columns and join relationships, generate read-only SQL, execute queries, inspect errors/results, and attempt bounded repair. Evaluate this ability on **the original BIRD Mini-Dev**.
2. **Multi-hop Knowledge Retrieval and Reasoning (proposed, pending group confirmation):** Decompose dependent questions, retrieve evidence from multiple passages or documents, follow intermediate entities, verify claims, and answer with traceable supporting sources. Evaluate this ability on **MuSiQue-Ans** as the candidate primary benchmark; consider **HotpotQA** as an optional supplementary benchmark.

A **Hybrid SQL + Document Reasoning** mode is proposed for an interactive product demonstration. It would combine quantitative database results and document evidence within one task. Because neither BIRD nor MuSiQue measures cross-source integration, this mode requires a separate controlled evaluation.

The shared research goal is to investigate **whether reusable agentic planning, tool selection, knowledge/relationship exploration, iterative verification, and selective model escalation improve answer correctness, grounding, recovery, and computation efficiency**. Improvements are hypotheses, not predetermined conclusions.

**Product direction (proposed):** Retail Operations Intelligence Copilot for analysts and business users. Product use case, exact data sources, interaction design, and deployment scope are **to be confirmed with the group**.

## 3. Motivation and Challenges

Real business questions can span relational tables and written policies, incident reports, promotion plans, or operational notes. One-shot Text-to-SQL can choose wrong tables or joins even if its generated query runs; one-shot RAG may retrieve only a partial explanation when evidence depends on several documents. Hybrid questions additionally require connecting numerical trends to relevant context without claiming unsupported causality.

Key challenges:

- **Selective grounding:** Retrieve enough schema, data values, or document passages without exceeding context budgets.
- **Relationship discovery:** Trace foreign-key joins in databases and bridge entities/supporting passages in documents.
- **Multi-step reasoning:** Decompose questions and use earlier observations to decide the next useful lookup.
- **Adaptive recovery:** React to SQL errors, irrelevant retrieval results, contradictions, or missing evidence.
- **Evidence-based answers:** Cite source documents; distinguish SQL execution success from semantic correctness; abstain or qualify unsupported claims.
- **Efficiency and safety:** Bound iterations, tool calls, query duration, context, tokens, and model escalation; restrict SQL access to read-only operations.
- **Product integration:** Expose understandable results and observable agent traces through a simple interface without making UI implementation the research contribution.

## 4. Proposed Solution and Architecture

### 4.1 Reusable KORA Agent Core

Implement a stateful bounded loop:

**Understand → Decide/Plan → Select Tool → Act → Observe/Reflect → Continue or Stop**

The controller maintains question and task state, retrieved evidence with source identifiers, optional plans, candidate relationships, SQL attempts, tool results/errors, selected model, remaining budget, and a final grounded answer. Model decisions must be validated against typed tool definitions by a deterministic tool dispatcher. The controller should select actions rather than follow a fixed sequence on every question. LangGraph (or an equivalent orchestration framework) is a candidate implementation, not a mandatory dependency.

### 4.2 Domain Adapters and Tools

| Adapter | Candidate tools/operations | Output |
| --- | --- | --- |
| **SQL Adapter — confirmed research track** | `search_knowledge()` for schema/evidence; `inspect_source()` for tables, columns and permitted values; `explore_relationships()` for join paths; generate / execute read-only SQL; repair or stop | Executed SQL, answer rows, execution observations and trace |
| **Document Adapter — proposed** | Search document/passages; retrieve source chunks; inspect full source; follow entity or citation links; verify support and handle missing evidence | Grounded answer, passage/source citations, intermediate-step trace |
| **Hybrid Mode — proposed** | Controller selects SQL and/or document adapter actions, aligns entities and time periods, and reconciles findings | Integrated answer with separate numeric and documentary evidence |

A lightweight graph may represent `HAS_COLUMN` edges, verified foreign keys and provenance-linked terminology for SQL; document-side links may represent entities, passages or citations. Unverified inferred edges must be distinguished from verified relations. Reuse the controller and logging interface, not every domain-specific algorithm.

### 4.3 Optional Reasoning Modules

- **Query Planner:** For SQL, identify tables, join paths, filters, aggregations and expected outputs before generation. For document QA, optionally generate explicit sub-questions and intermediate evidence requirements.
- **Knowledge / Graph Explorer:** Perform bounded traversal to find indirect joins or multi-hop evidence paths; record provenance.
- **Adaptive Model Router:** Select normal versus stronger models based on inference-time signals such as plan complexity, retrieval sufficiency, or tool errors; compare against fixed-model baselines. Do not use gold evaluation labels for routing decisions.
- **Verification & Recovery:** Observe SQL exceptions or questionable outputs, check document citation support, retrieve more evidence, repair or terminate within limits. Successful SQL execution alone is not proof of a correct answer.

### 4.4 Frontend — **TO BE CONFIRMED (TBC)**

A lightweight web UI is **proposed**, not an approved deliverable or fixed technology choice. **Streamlit is a provisional candidate**, subject to group agreement.

Potential MVP features: chat-style question entry, final response, SQL query/result table, linked document citations, agent tool-step trace, and simple session history. A UI demo should reuse the same agent runtime evaluated offline, rather than implement separate business logic.

### 4.5 Backend — **TO BE CONFIRMED (TBC)**

A Python API layer is **proposed**, not an approved deliverable or fixed technology choice. **FastAPI is a provisional candidate**, subject to group agreement.

Potential responsibilities: request/response contract (for example `POST /chat` and `GET /health`), basic session state, controller invocation, database/retriever adapters, SQL safety checks, bounded runtime, logging, error handling and returned citations/traces. It must not expose benchmark gold answers to inference or accept arbitrary unrestricted SQL execution.

**Provisional integration shape (UI and API TBC):**

```text
[Streamlit UI — TBC] <--> [FastAPI backend — TBC]
                                  |
                       [Shared KORA Controller]
                                  |
                        [Typed Tool Dispatcher]
                              /        \
                    [SQL Adapter]   [Document Adapter]
                         |                |
                  [SQLite / BIRD]    [Passage Index]
                              \        /
                        [Grounded Answer]
```

The project can still execute all benchmark harnesses directly without a frontend or HTTP backend if these components are not approved.

## 5. Datasets, Experiments and Evaluation

### 5.1 Track A — Text-to-SQL (**existing approved proposal scope**)

**Dataset:** Original **BIRD Mini-Dev**, 500 SELECT-only questions across 11 databases; pin the exact release, SQLite database versions, prompt/evidence policy, and official evaluator. Do not mix the original setting with Mini-Dev V2.

| Variant | Configuration / purpose |
| --- | --- |
| **S0** | One-shot SQL generation with the same initial schema/evidence, execute once |
| **S1** | Fixed generate–execute–check–repair sequence with bounded retries |
| **B0** | Agentic controller selects search, inspection, SQL execution, repair or stop |
| **B1** | B0 + graph exploration and retrieved join paths |
| **B2** | B0 + explicit SQL query planner (fixed model) |
| **B3** | B0 + normal/strong model routing |
| **B4** | Full KORA: B0 + graph + planner + router |

**Primary metric:** Execution Accuracy (EX). **Diagnostics:** first-attempt versus final EX, repair recovery, schema/table/column recall as an imperfect reference-SQL proxy, viable join-path coverage and SQL execution success. **Efficiency:** tokens, tool/model calls, latency, estimated cost and strong-model fraction. Report per-question paired comparisons, bootstrap confidence intervals and failure categories; include matched compute-budget comparisons where applicable.

The original research questions remain: RQ1 adaptive control, RQ2 graph-guided schema/joins, RQ3 query planning, and RQ4 cost-aware model routing.

### 5.2 Track B — Multi-hop Knowledge Retrieval (**proposed; group confirmation required**)

**Candidate primary dataset:** **MuSiQue-Ans**, with explicit 2-, 3- and 4-hop questions, supporting evidence annotations and publicly available development references. **Optional:** HotpotQA for bridge/comparison QA and supporting-fact checks. Choose and pin dataset release, split, corpus mode and evaluator before reporting scores.

| Variant | Configuration / purpose |
| --- | --- |
| **D0 — Traditional RAG** | Single retrieval and answer generation |
| **D1 — Iterative Retrieval** | Bounded sequence of dependent searches based on earlier results |
| **D2 — Agentic Knowledge Reasoning** | Shared KORA controller + optional decomposition, tool selection, iterative retrieval and source verification |

**Metrics:** Answer exact match/F1 as appropriate to the selected evaluator; supporting-paragraph/fact recall and F1; intermediate-answer/hop success diagnostics where labels are available; unsupported-answer/abstention analysis where applicable; retrieval steps, tokens, latency and cost. Break down MuSiQue results by hop count and difficulty.

**Evaluation safeguards:** Gold answer, supporting evidence annotations and gold decomposition must be hidden from the agent during inference. Define whether retrieval is over candidate paragraphs or a larger fixed corpus; the two settings are not directly comparable. Use a held-out subset for final evaluation, with prompt/tool policy tuning confined to development data. Avoid training/development leakage, including MuSiQue's source-question overlap concerns.

### 5.3 Track C — Hybrid Product Demonstration (**proposed, not a standard benchmark**)

Construct a **small controlled synthetic retail operations environment** with relational sales/inventory/promotions tables plus incident reports, policy documents and promotion notes. Design approximately **20–30 hybrid questions** initially; this is a demo/diagnostic sample size, not a reliable general-population accuracy estimate.

**Ground-truth-first generation and checking:**

1. Define business rules, schema, event ledger, primary/foreign keys and canonical timestamps.
2. Generate seeded data and verify numerical answers with independent SQL calculations.
3. Let GPT help write natural-language documents/questions grounded in the canonical event ledger.
4. Record each reference answer as **verified numeric results + document IDs/passages + expected linkage**, with explicit uncertainty where causes are not established.
5. Validate entity/date consistency, FK integrity, exact numeric reconciliation, evidence provenance and ambiguous questions; manually review all demo questions.
6. Freeze evaluation records and ensure the agent cannot see reference SQL, answers or event-ledger labels at inference time.

Include cases for SQL-only, document-only, cross-source reasoning, missing documents, contradictory sources, incorrect joins and insufficient evidence. Report task success and evidence correctness separately from BIRD EX and MuSiQue answer F1. A document event that coincides with a sales change is **not** automatically its cause.

**Illustrative product question:** "Which stores had declining sales in October, and which stock shortages or promotion changes might be relevant?" The SQL adapter determines which stores declined; the document adapter retrieves incident/promotion evidence; the controller joins findings by store/time and returns a grounded, qualified explanation.

### 5.4 Fairness, Reproducibility and Limitations

- Hold dataset release, accessible evidence, model, decoding parameters, prompts, tool/retry ceilings, timeouts and scoring procedure fixed within comparisons where applicable.
- Use matched token/tool budgets or report cost–accuracy trade-offs; strong-only and normal-only controls are needed for router analysis.
- Separate model-facing inputs from gold/reference scoring data.
- Capture per-question trace, SQL attempts, retrieved source IDs, model choice, tokens, latency, errors and final answer.
- Report negative results and distinguish syntactic SQL success from answer correctness.
- **No unified accuracy percentage:** BIRD EX, MuSiQue answer F1, and hybrid task success evaluate different phenomena.
- The synthetic product dataset establishes controlled integration behavior, not validated real-world production effectiveness.

## 6. Product Demonstration and Deliverables

**Proposed use case (TBC with group):** **Retail Operations Intelligence Copilot**, aimed at business analysts or store operations teams. Example user tasks:

- **SQL-only:** Which stores had the largest month-over-month sales decline?
- **Document-only:** How did the returns policy change across its last two revisions?
- **Hybrid:** Which declining stores had documented stock shortages or campaign changes during the period?

**Deliverables and commitment levels:**

| Deliverable | Status |
| --- | --- |
| Reusable bounded agent runtime, SQL tools and BIRD Mini-Dev S0/S1/B0–B4 evaluation | **Existing submitted scope** |
| Multi-hop document adapter and MuSiQue-Ans D0–D2 evaluation | **Proposed — pending group agreement** |
| Hybrid synthetic retail data, questions, verification records and demo | **Proposed — pending group agreement** |
| Simple frontend and Streamlit choice | **TO BE CONFIRMED (TBC)** |
| Simple backend and FastAPI choice | **TO BE CONFIRMED (TBC)** |
| Product domain, deployment and real-time data-update requirements | **To be confirmed** |

**Recommended sequence, not confirmed project deadlines:** (1) agree scope and evaluation rules; (2) implement a common tool/runtime contract and SQL baseline; (3) run the SQL agent experiments; (4) implement and assess a focused document track if approved; (5) create/verify hybrid synthetic records; (6) connect optional UI/API and perform the product demonstration; (7) finalize evaluation, failure analysis, report and presentation.

## 7. Decisions Needed from Group 9

- Approve or reject MuSiQue-Ans as the primary document reasoning evaluation, and decide whether HotpotQA is also necessary.
- Confirm whether document QA is a formally evaluated second research track or only an optional extension.
- Confirm scope and evaluation effort for Hybrid SQL + Document reasoning.
- Approve or change the retail operations product domain and synthetic-dataset assumptions.
- Confirm **whether any frontend is required**, and if so whether **Streamlit** is acceptable (**TBC**).
- Confirm **whether a separate backend is required**, and if so whether **FastAPI** is acceptable (**TBC**).
- Decide model access/budget, team ownership and milestones; check whether teaching-team sign-off is needed for changes from the submitted proposal.

## References and Related Project Materials

- **Authoritative submitted copy:** [`KORA_Group9_Proposal.pdf`](KORA_Group9_Proposal.pdf)
- **Original editable submission text:** [`proposal.md`](proposal.md) and [`main.tex`](main.tex)
- **Benchmark research:** [BIRD Mini-Dev](../../research/bird-sql.md), [MuSiQue](../../research/musique.md), [HotpotQA](../../research/hotpotqa.md)
- **BIRD official:** https://github.com/bird-bench/mini_dev
- **MuSiQue official:** https://github.com/StonyBrookNLP/musique
- **HotpotQA official:** https://hotpotqa.github.io/
- **LangGraph:** https://docs.langchain.com/oss/python/langgraph/workflows-agents
- **ReAct:** https://arxiv.org/abs/2210.03629

**Reminder:** This is a **final proposal draft for discussion**, not an updated official submission and not evidence of implemented results. All newly proposed scope and the optional frontend/backend remain subject to group confirmation.
