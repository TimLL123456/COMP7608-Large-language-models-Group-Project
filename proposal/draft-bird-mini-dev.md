# Draft A — BIRD Mini-Dev

> **Superseded proposal draft (2026-10-25):** This earlier candidate proposal is retained for historical reference. The [submitted KORA proposal](KORA/KORA_Group9_Proposal.pdf) is authoritative.

**Project Title: Reliable and Cost-Efficient Self-Service Data Analytics through Agentic Text-to-SQL**

## 1. Group Members

- [Name] — [Student ID]
- [Name] — [Student ID]
- [Name] — [Student ID]

## 2. Project Objective

This project aims to develop and evaluate an **agentic Text-to-SQL system** that helps users with limited SQL expertise retrieve reliable answers from relational databases through natural-language questions. We study how agentic system design can improve both **query correctness** and **computational efficiency**, rather than focusing only on SQL generation.

**Intended users and needs.** Our primary users are **business and operations analysts** who regularly need data but may not know the database schema or how to write complex SQL. **Junior data analysts** are secondary users who may need support with joins, aggregations, and debugging. These users need: (1) accessible natural-language querying; (2) automatic discovery of relevant tables, columns, and PK/FK relationships; (3) reliable handling of complex analyses and SQL errors; and (4) timely answers at reasonable inference cost.

We first build an agentic baseline that explores schemas, generates and executes SQL, and debugs failed queries. We then evaluate two targeted improvements:

1. **Query Planner:** Decompose complex analytical questions into logical steps before SQL generation.
2. **Adaptive Controller:** Route simpler questions to a normal model and harder questions to a stronger reasoning model.

**Research questions**

- **RQ1:** Does explicit query planning improve Text-to-SQL execution accuracy, especially on moderate and challenging queries?
- **RQ2:** Can adaptive model routing maintain strong query accuracy while reducing latency, token usage, and estimated model cost compared with always using a strong model?

## 3. Motivation and Challenges

Self-service analytics is difficult when users must understand unfamiliar schemas, identify correct joins, express multi-step calculations, and fix SQL errors. For example, a retail analyst may ask: **"Which three products had the largest sales increase between 2022 and 2023?"** Answering this requires finding the right sales and product data, aggregating by year, matching products, calculating differences, and ranking results.

A Text-to-SQL agent can make this workflow more accessible, but it may choose incorrect tables or columns, misunderstand relationships, generate logically wrong SQL that still executes, or fail to recover from execution errors. Stronger models and additional reasoning may help, but increase cost and response time. The challenge is to determine **which agentic mechanisms improve answer reliability and whether their computational overhead is justified**.

The design connects concrete user needs to agent features:

| User need | Agent capability |
|:--|:--|
| Query data without writing SQL | Natural-language input and executable SQL output |
| Navigate unfamiliar databases | Active table, column, and PK/FK exploration |
| Answer multi-step business questions | Explicit Query Planner |
| Reduce manual query debugging | Execution feedback and self-correction |
| Obtain timely, affordable responses | Adaptive model routing |

## 4. Potential Solution

### 4.1 Baseline — Agentic Schema Search and Query Debugging

The baseline is an agentic, tool-using system rather than a one-shot LLM. It inspects relevant tables, columns, and PK/FK relationships, creates SQL, executes it, examines execution feedback, and revises failed queries within a bounded retry budget.

```text
User Question
      |
      v
Search Tables / Columns / PK-FK
      |
      v
Generate SQL --> Execute SQL --> Success? --> Yes --> SQL + Query Result
                       ^               |
                       |               No
                       |               v
                       +---------- Debug / Revise
```

A successful execution does **not** guarantee a correct answer; correctness is measured by benchmark evaluation, not just by the absence of runtime errors. The user-facing prototype presents the SQL and query results, without requiring a full analytics dashboard.

### 4.2 Improvement 1 — Query Planner

The Query Planner explicitly decomposes a question into steps before SQL generation. For the retail example above, it would: (1) calculate 2022 sales per product; (2) calculate 2023 sales; (3) join the corresponding products; (4) compute the increase; and (5) sort and return the top three. The plan then informs SQL generation and the existing execution/debug loop.

```text
User Question --> Schema Search --> Query Planner --> Logical Plan
                                                     |
                                                     v
                                              Generate / Execute SQL
                                                     |
                                               Debug if needed
                                                     |
                                                     v
                                              SQL + Query Result
```

**Hypothesis:** Planning improves accuracy most for queries involving multi-table joins, aggregation, comparisons, nested operations, or ranking, but it may add latency and tokens.

### 4.3 Improvement 2 — Adaptive Controller

The Adaptive Controller estimates query difficulty from information available **at inference time** and selects a normal or stronger model for the baseline workflow; it does not use benchmark difficulty labels as routing inputs.

```text
                  User Question
                        |
                Adaptive Controller
                    /       \
              General       Hard
                 |            |
           Normal Model  Strong Model
                 \            /
                  Baseline Agent
                        |
                 SQL + Query Result
```

Compare (A) normal-model-only, (B) strong-model-only, and (C) adaptive routing, keeping the remaining agent tools and retry policy comparable. If time permits, test a combined Planner + Adaptive system.

**Hypothesis:** Adaptive routing approaches the accuracy of strong-model-only execution with lower overall token usage, latency, and estimated model cost.

## 5. Experimental Dataset and Evaluation Plan

**Dataset.** We will use **BIRD Mini-Dev** for controlled evaluation. Its natural-language questions, relational databases, schemas, reference SQL, and difficulty annotations support execution-based scoring and analysis by query complexity. We will check the selected split, evaluation script, and availability of each metric before reporting results.

### 5.1 System Comparison

| Configuration | Schema Search + Debug | Planner | Adaptive Routing |
|:--|:--:|:--:|:--:|
| Baseline (normal model) | Yes | No | No |
| Baseline + Query Planner | Yes | Yes | No |
| Baseline (strong model) | Yes | No | No |
| Baseline + Adaptive Controller | Yes | No | Yes |
| Planner + Adaptive Controller (optional) | Yes | Yes | Yes |

To isolate improvements, use the same dataset, database permissions, execution environment, tool access, prompt conventions, and retry limits wherever possible. The Planner experiment uses a fixed base model; the routing experiment explicitly compares normal-only, strong-only, and adaptive configurations.

### 5.2 Correctness and Reliability

- **Execution Accuracy (EX)**, with **Soft F1** and **R-VES** where supported by the chosen evaluation implementation.
- Accuracy by difficulty (**simple / moderate / challenging**), particularly for RQ1.
- **First-attempt accuracy**, **final accuracy after debugging**, and **debug recovery rate**.
- Error analysis of incorrect schema selection, joins, logic, execution failures, and unsuccessful retries.

### 5.3 Efficiency and Agent Traces

- **Efficiency:** input/output tokens, LLM calls, database/tool calls, retries, end-to-end latency, and estimated model cost per query.
- **Schema exploration:** table recall and column recall, using reference SQL as a *diagnostic approximation* of required objects rather than exhaustive schema ground truth.
- **Debugging:** number of retries and fraction of initially incorrect queries corrected after retries.
- **Routing:** fraction routed to the strong model, accuracy and cost by routing decision, and cost savings relative to strong-model-only execution. Difficulty labels are used **only for post-hoc analysis**, not as routing ground truth.

### 5.4 Evaluation Aligned to User Needs

| User need | Evaluation evidence |
|:--|:--|
| Accurate answers to business questions | EX, Soft F1, accuracy by difficulty |
| Reliable handling of complex queries | Moderate/challenging EX, first-attempt vs final accuracy |
| Reduced debugging effort | Debug recovery rate, retries, failure categories |
| Fast and affordable querying | End-to-end latency, tokens/query, estimated cost/query |

**Scope and limitations.** BIRD assesses SQL correctness and agent efficiency, **not actual user satisfaction, usability, or business impact**. We will therefore describe the intended users as the *application motivation*, not claim that benchmark gains establish real-world user acceptance. A small illustrative business question may be included in the demo; formal usability testing is optional and outside the core experiment.

**Expected contribution.** Compare **correctness**, **efficiency**, and **observable agent behavior** to explain when explicit planning helps and when stronger reasoning is worth its cost for practical self-service analytics.
