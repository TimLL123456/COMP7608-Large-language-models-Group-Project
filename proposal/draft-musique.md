# Draft B — MuSiQue

> **Superseded proposal draft (2026-10-25):** This earlier candidate proposal is retained for historical reference. The [submitted KORA proposal](KORA/KORA_Group9_Proposal.pdf) is authoritative.

**Project Title: Adaptive Multi-Hop Reasoning Agent with Iterative Retrieval**

## 1. Group Members

- [Name] — [Student ID]
- [Name] — [Student ID]
- [Name] — [Student ID]

## 2. Project Objective

Develop an **adaptive multi-hop reasoning agent** that answers complex questions by generating sub-questions and retrieving evidence iteratively.

The agent identifies missing information, retrieves relevant evidence, extracts an intermediate answer, and uses that answer to determine its next action.

**Research question:**

> Can adaptive decomposition and iterative retrieval improve multi-hop question answering compared with one-shot RAG under the same LLM?

## 3. Motivation and Challenges

Some questions require several dependent reasoning steps. For example:

```text
Identify a Film’s Distributor
   ↓
Use the Distributor’s Name
   ↓
Identify a Founder of That Distributor
```

Later retrieval steps depend on earlier answers. A single retrieval may therefore miss information needed to complete the reasoning.

The agent must decide what to search next, how to use intermediate answers, and when sufficient evidence has been collected.

The main challenge is improving reasoning accuracy while controlling retrieval calls, latency and token cost.

## 4. Potential Solution

The agent will use retrieval and evidence-management tools to generate sub-questions, find relevant paragraphs, and accumulate evidence.

**Baseline workflow**

```text
Question
   ↓
Retrieve Once
   ↓
LLM Generates Answer
   ↓
Final Answer
```

**Agent workflow**

```text
Question
   ↓
Identify Required Facts
   ↓
Generate Next Sub-question ◄──────────────────┐
   ↓                                          │
Retrieve Relevant Paragraphs                  │
   ↓                                          │
Extract Intermediate Answer                   │
   ↓                                          │
Update Collected Evidence                     │
   ↓                                          │
More Information Needed?                      │
   ├── Yes ───────────────────────────────────┘
   └── No → Verify Evidence → Final Answer
```

Each new sub-question uses the intermediate answers and evidence already collected. The number of retrieval steps will be adaptive.

The same LLM will be used in both settings so that the main difference is the agentic workflow.

## 5. Experimental Dataset and Evaluation Plan

We plan to use **MuSiQue**, which contains **2-hop, 3-hop and 4-hop questions** designed for connected multi-hop reasoning.

The dataset provides final questions and answers, candidate paragraphs, supporting-paragraph annotations, intermediate answers and question decompositions.

Gold decompositions will be used only for evaluation and failure analysis, not as agent input.

**Main metrics:**

- Answer F1
- Support F1

**Additional metrics:**

- Supporting-paragraph recall
- Intermediate-answer accuracy
- Number of retrieval/tool calls
- Token usage
- Latency

Results will be compared across 2-hop, 3-hop and 4-hop questions. Failure analysis will examine decomposition, retrieval, intermediate-answer, evidence-selection and reasoning errors.

The experiment will assess whether adaptive retrieval improves reasoning enough to justify its additional computational cost.
