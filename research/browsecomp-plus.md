# BrowseComp-Plus

> **Historical research note (2026-10-25):** This benchmark was explored as an alternative during topic selection. Group 9 has selected **KORA** on the **original BIRD Mini-Dev** for its Text-to-SQL evaluation. This file is retained as earlier topic-selection research; see the [submitted KORA proposal](../proposal/KORA/KORA_Group9_Proposal.pdf).

BrowseComp-Plus is a benchmark for evaluating **Deep Research / search agents** in a controlled retrieval setting. It starts from reasoning-intensive questions derived from OpenAI's BrowseComp, but replaces live-web search with a fixed corpus. This makes it possible to compare retrievers and LLM agents under the same information environment instead of depending on changing web pages or search-engine rankings.

For this project, its main value is that it lets us separate two questions:

1. **Did the retriever find the right evidence?**
2. **Given the evidence, did the agent reason, verify and answer correctly?**

That separation is useful when studying how to improve an agentic system rather than only reporting one final accuracy number.

## 1. What is in the dataset?

The official release contains **830 queries** and a fixed corpus of **100,195 documents**. The dataset card reports per-query averages of **6.1 evidence documents**, **2.9 gold documents** and **76.28 hard-negative documents**.

The important document labels are:

- **Evidence documents:** documents needed to answer the query.
- **Gold documents:** documents needed to answer the query that also semantically contain the final answer.
- **Negative documents:** hard negatives that look relevant but should not be treated as the answer evidence.

A query record contains the following fields:

```text
query_id
query
answer
evidence_docs
  - docid
  - text
  - url
gold_docs
  - docid
  - text
  - url
negative_docs
  - docid
  - text
  - url
```

Except for `query_id`, the query release is obfuscated to reduce benchmark leakage. The official repository provides a de-obfuscation script, while the document corpus is distributed separately and is not obfuscated.

## 2. BrowseComp vs. BrowseComp-Plus

| Aspect | BrowseComp | BrowseComp-Plus |
| --- | --- | --- |
| Search environment | Live web | Fixed document corpus |
| Reproducibility | Search results can change over time | Same corpus can be reused across experiments |
| Retriever control | Limited by the external search engine | Retriever can be replaced and measured directly |
| Main use | Test difficult web research | Test deep-research agents and retrieval quality under controlled conditions |

This difference matters experimentally. If two agents browse the live web at different times, they may receive different pages even if their reasoning is identical. BrowseComp-Plus holds the corpus fixed, so a change in results is easier to attribute to the retriever, agent workflow, model or search strategy.

## 3. Worked example: football search question

A qualitative case study in Databricks' KARL paper analyzes **BrowseComp-Plus Query 280**. The question gives several indirect clues about an early-2000s football match and asks for the away team's third substitute. The correct answer is **Sol Campbell**.

The reported successful path can be summarized as:

```text
Indirect football clues
        ↓
Narrow candidate teams and match
        ↓
Identify Bolton vs Arsenal, 29 Apr 2002
        ↓
Establish Arsenal as the away team
        ↓
Inspect substitution information
        ↓
Lee Dixon → Nwankwo Kanu → Sol Campbell
        ↓
Answer: Sol Campbell
```

The point is not football knowledge by itself. The agent must search iteratively, connect clues from different facts, reject incomplete leads and keep going until the requested detail is verified. In the KARL comparison, other agents either stopped early or searched for many steps without resolving the final detail.

## 4. Worked example: correct retrieval but wrong reasoning

The same KARL paper analyzes **BrowseComp-Plus Query 61**. The question uses biographical clues to identify an author and then asks for the genre of that person's first book. The benchmark answer is **Swahili poetry**.

This example is useful because an agent can locate much of the correct biography and still fail. One compared model identified **Wallah bin Wallah** and his first book, **Malenga wa Ziwa Kuu**, but then made an unsupported assumption that the work was fiction. The evidence instead indicated poetry.

This gives a clear failure category:

```text
Relevant evidence retrieved
        ↓
Correct person / book identified
        ↓
Unsupported inference about genre
        ↓
Wrong final answer
```

So a failed benchmark question does not automatically mean retrieval failed. It can be a **reasoning or grounding failure after successful retrieval**.

## 5. What capabilities does it evaluate?

A BrowseComp-Plus agent can be viewed as the following loop:

```text
Question
  ↓
Plan what to search
  ↓
Retrieve candidate documents
  ↓
Assess whether evidence is sufficient
  ↓
Reformulate / search again when needed
  ↓
Reason across evidence
  ↓
Verify constraints
  ↓
Final answer
```

The benchmark is therefore useful for evaluating more than factual recall. It can expose whether an agent can decompose a difficult question, perform iterative search, distinguish strong evidence from distractors, synthesize information across documents and stop only when the answer is sufficiently supported.

## 6. Failure modes to analyze

| Failure | What it means | Example diagnostic |
| --- | --- | --- |
| Retrieval failure | Relevant evidence was never retrieved | Low evidence/gold Recall@K |
| Search-strategy failure | The agent keeps searching the wrong direction | Many calls but poor recall |
| Reasoning failure | Evidence is present but interpreted incorrectly | Gold docs retrieved, wrong answer |
| Grounding failure | The final answer contains an unsupported assumption | Answer not justified by retrieved evidence |
| Verification failure | A plausible candidate is accepted too early | Partial clues match but constraints remain unchecked |
| Efficiency failure | The agent eventually succeeds but uses excessive search/tool calls | High latency, token use or cost |

This decomposition is especially useful for an agentic-system project because an improvement can be tied to a specific failure mode instead of changing many components at once.

## 7. How we could use it in the COMP7608 project

A clean research question would be:

> **Does improving retrieval quality increase end-to-end deep-research agent accuracy enough to justify the additional retrieval and inference cost?**

A simple experiment can keep the LLM agent and prompts fixed while changing only the retriever:

```text
Baseline
BM25
  + same agent
  + same top-k
  + same context limit
  + same maximum tool calls

Improvement
Dense retriever (for example Qwen3-Embedding-8B)
  + same agent
  + same top-k
  + same context limit
  + same maximum tool calls
```

If time permits, a later extension could test hybrid retrieval or a better query-reformulation strategy, but the first experiment should change only one major component so the result is interpretable.

For development, use a clearly separated subset of queries for tuning and keep another subset untouched for the final comparison. Because the official answers can be de-obfuscated, accidental overfitting is a real risk if the same questions are repeatedly inspected while changing the system.

## 8. Evaluation metrics

BrowseComp-Plus supports both end-to-end and retrieval-only evaluation.

| Layer | Metric | What it tells us |
| --- | --- | --- |
| Final task | Answer accuracy / official judge | Did the agent solve the question? |
| Retrieval | Evidence Recall@5/100/1000 | Did search retrieve documents needed for reasoning? |
| Retrieval | Gold Recall@5/100/1000 | Did search retrieve documents containing the final answer? |
| Ranking | Evidence / Gold nDCG@10 | Were useful documents ranked near the top? |
| Agent efficiency | Search/tool-call count | How much iterative work was required? |
| Runtime efficiency | Latency | How long did the system take? |
| Resource efficiency | Tokens / estimated cost | Was the improvement worth the compute? |
| Reliability | Completion/failure rate | Did runs terminate successfully? |

The official repository's end-to-end run format also records `tool_call_counts`, retrieved document IDs, completion status and final model output, which makes these measurements practical.

## 9. Strengths and limitations

**Strengths**

- Fixed corpus makes comparisons reproducible.
- Human-verified evidence and gold-document labels make retrieval errors measurable.
- Hard negatives make retrieval more realistic than a corpus containing only obviously relevant documents.
- Difficult multi-step questions expose search, reasoning and verification failures.
- The same benchmark can evaluate retrievers alone or complete research agents.

**Limitations**

- Fixed-corpus search is not the same as live-web browsing.
- Indexing roughly 100K long documents adds engineering and storage work.
- Results depend on retrieval configuration, context limits, tool-call budgets and the answer judge, so these must be pinned for a fair comparison.
- The benchmark is deliberately difficult; running all 830 questions with frontier models can be expensive.
- Because the answers are available after de-obfuscation, experiment discipline is needed to avoid tuning on the final evaluation questions.

## 10. Practical setup

The official repository provides scripts to:

1. download and de-obfuscate the 830 queries, answers and relevance judgements;
2. download the separate document corpus;
3. use pre-built BM25 or Qwen3-Embedding indexes, or plug in a custom retriever;
4. run a Deep Research agent against the local retrieval tool;
5. evaluate final answers and retrieval metrics.

This makes BrowseComp-Plus suitable for a staged project: first reproduce a small baseline, then modify one retrieval or agent component, and finally analyze which failure types changed.

## References

- BrowseComp-Plus official repository: https://github.com/texttron/BrowseComp-Plus
- BrowseComp-Plus dataset card: https://huggingface.co/datasets/Tevatron/browsecomp-plus
- BrowseComp-Plus paper: https://arxiv.org/abs/2508.06600
- BrowseComp: https://openai.com/index/browsecomp/
- KARL case studies used for the two worked examples: https://www.databricks.com/de/sites/default/files/2026-03/karl.pdf
