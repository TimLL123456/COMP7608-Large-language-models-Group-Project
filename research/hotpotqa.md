# HotpotQA

> **Historical research note (2026-10-25):** This benchmark was explored as an alternative during topic selection. Group 9 has selected **KORA** on the **original BIRD Mini-Dev** for its Text-to-SQL evaluation. This file is retained as earlier topic-selection research; see the [submitted KORA proposal](../proposal/KORA/KORA_Group9_Proposal.pdf).

HotpotQA is a benchmark for **diverse, explainable multi-hop question answering**. Instead of asking questions that can usually be answered from one passage, it is designed so that a system often needs to connect information from multiple Wikipedia documents before producing the final answer.

Introduced at EMNLP 2018, HotpotQA contains about **113,000 Wikipedia-based question-answer pairs**. A key feature is that it annotates not only the final answer but also the **sentence-level supporting facts** needed to justify it.

For this project, that lets us separate three questions:

1. **Did the system find the right evidence?**
2. **Did it combine the evidence correctly?**
3. **Did it return the correct answer with the correct supporting facts?**

This makes HotpotQA useful for evaluating a retrieval-and-reasoning agent rather than only a language model's final response.

## 1. What is in the dataset?

A simplified record looks like this:

```json
{
  "_id": "...",
  "question": "Which magazine was started first Arthur's Magazine or First for Women?",
  "answer": "Arthur's Magazine",
  "supporting_facts": [
    ["Arthur's Magazine", 0],
    ["First for Women", 0]
  ],
  "context": [
    ["Arthur's Magazine", ["..."]],
    ["First for Women", ["..."]],
    ["Other article", ["..."]]
  ],
  "type": "comparison",
  "level": "medium"
}
```

| Field | Meaning | Evaluation use |
| --- | --- | --- |
| `_id` | Unique example identifier | Match predictions to examples |
| `question` | Natural-language multi-hop question | Agent input |
| `answer` | Gold final answer | Answer evaluation |
| `supporting_facts` | Gold evidence as `[title, sentence_id]` pairs | Evidence evaluation |
| `context` | Wikipedia paragraphs and sentences | Retrieval/reading context |
| `type` | `comparison` or `bridge` | Analyze reasoning type |
| `level` | `easy`, `medium` or `hard` | Analyze difficulty |

The official test data does not expose the gold answer or supporting facts.

## 2. Two important question types

### Comparison questions

A comparison question requires facts about two entities and a final comparison:

```text
Question
  ↓
Find fact about entity A
  ↓
Find fact about entity B
  ↓
Compare A and B
  ↓
Final answer
```

### Bridge questions

A bridge question uses one result to reveal the entity or fact needed for the next retrieval:

```text
Question
  ↓
Retrieve evidence A
  ↓
Discover bridge entity
  ↓
Retrieve evidence B
  ↓
Final answer
```

The bridge pattern is especially relevant to an iterative search agent because the next useful query may only become clear after reading the first result.

## 3. Worked example: comparison question

A well-known HotpotQA example asks:

> Which magazine was started first Arthur's Magazine or First for Women?

The gold answer is **Arthur's Magazine**.

A useful decomposition is:

```text
When was Arthur's Magazine started?
  → 1844

When was First for Women started?
  → 1989

Compare 1844 and 1989
  ↓
Answer: Arthur's Magazine
```

The system therefore needs to retrieve two separate facts and compare them correctly. Possible failures include retrieving only one magazine, extracting the wrong year, comparing incorrectly, or answering correctly with the wrong evidence.

## 4. Worked example: bridge question

Another HotpotQA example asks:

> The Oberoi family is part of a hotel company that has a head office in what city?

The gold answer is **Delhi**.

The reasoning chain is:

```text
Oberoi family
  ↓
The Oberoi Group
  ↓
Head office
  ↓
Delhi
```

A natural agent trajectory is:

```text
Search: Oberoi family
  ↓
Evidence: involvement through The Oberoi Group
  ↓
Search: The Oberoi Group head office
  ↓
Evidence: head office in Delhi
  ↓
Answer: Delhi
```

The first retrieval reveals the bridge entity needed for the second retrieval.

## 5. Distractor vs. fullwiki settings

### Distractor setting

The system receives a small candidate set containing relevant passages and distractors:

```text
Question + candidate paragraphs
  ↓
Select evidence
  ↓
Reason
  ↓
Answer
```

This is useful for controlled evidence-selection and reasoning experiments. However, placing every candidate passage directly into one long prompt can reduce the need for an agent.

### Fullwiki setting

The fullwiki setting is intended for open-domain retrieval. The official repository explicitly allows researchers to replace the supplied retrieved paragraphs with results from their own information-retrieval system.

```text
Question
  ↓
Search / retrieve
  ↓
Assess evidence
  ↓
Search again if incomplete
  ↓
Reason across evidence
  ↓
Answer + supporting facts
```

For an agentic-system project, fullwiki is the more natural setting when the research question involves iterative search.

## 6. What capabilities can it evaluate?

| Capability | Evaluation question |
| --- | --- |
| Retrieval | Did the system find documents containing the needed facts? |
| Question decomposition | Did it identify the sub-questions needed for the answer? |
| Query reformulation | Did earlier evidence lead to a useful next search? |
| Evidence selection | Did it separate supporting facts from distractors? |
| Multi-hop reasoning | Did it combine facts across documents correctly? |
| Comparison | Did it correctly compare dates, quantities or attributes? |
| Grounding | Is the answer supported by the selected evidence? |
| Stopping | Did it stop only when the evidence was sufficient? |
| Efficiency | How many searches, tokens and tool calls were required? |

Supporting-fact labels are particularly valuable because they separate **answer success** from **evidence success**.

## 7. Suggested agent workflow

```text
Question
  ↓
Identify missing facts / sub-questions
  ↓
Search or retrieve
  ↓
Read candidate evidence
  ↓
Is evidence sufficient?
  ├─ No → reformulate query / search again
  └─ Yes
       ↓
Reason across evidence
       ↓
Select supporting facts
       ↓
Final answer
```

The experiment does not need hidden chain-of-thought. Observable traces are enough for analysis:

- search queries;
- retrieved document IDs/titles;
- selected evidence sentences;
- iteration count;
- final answer;
- predicted supporting facts;
- latency and token/tool usage.

## 8. Recommended project experiment

A clean first experiment is to test whether **iterative evidence-completeness checking** improves performance over one-shot retrieval.

### Baseline

```text
Question
  ↓
One retrieval step
  ↓
Top-k passages
  ↓
LLM answer + supporting facts
```

### Agent improvement

```text
Question
  ↓
Plan sub-question / search
  ↓
Retrieve top-k
  ↓
Check whether required evidence is complete
  ↓
If incomplete: reformulate and retrieve again
  ↓
Answer + supporting facts
```

Keep the same LLM, retriever/index, corpus, top-k, context limit, evaluator and maximum tool-call budget. Vary only the iterative evidence-checking behavior.

A useful research question is:

> Does iterative retrieval with an evidence-completeness check improve joint answer-and-support accuracy enough to justify its extra tool calls, latency and tokens?

## 9. Evaluation metrics

The official evaluation script reports answer, supporting-fact and joint metrics.

| Layer | Metric | Meaning |
| --- | --- | --- |
| Final answer | Answer EM | Exact normalized answer match |
| Final answer | Answer F1 | Token overlap with the gold answer |
| Evidence | Supporting-fact EM | Exact supporting-fact set match |
| Evidence | Supporting-fact F1 | Precision/recall overlap of supporting facts |
| Joint | Joint EM | Both answer EM and supporting-fact EM succeed |
| Joint | Joint F1 | Combined answer/evidence precision and recall |
| Efficiency | Search/tool-call count | Extra iterative work |
| Efficiency | Latency | End-to-end runtime |
| Efficiency | Tokens / estimated cost | Resource use |
| Reliability | Completion/error rate | Whether runs finish successfully |

For an agent project, **joint EM/F1** are especially useful because a correct answer without the correct evidence should not be treated as fully successful.

## 10. Failure analysis

HotpotQA supports a practical failure taxonomy:

- **Retrieval failure:** required evidence is never retrieved.
- **Bridge failure:** the first fact is found, but the agent does not use the bridge entity for the next query.
- **Evidence-selection failure:** relevant passages are retrieved but distractors are selected instead.
- **Reasoning failure:** correct evidence is retrieved but combined or compared incorrectly.
- **Grounding failure:** the final answer is plausible/correct but the predicted supporting facts do not justify it.
- **Efficiency failure:** the agent succeeds but uses unnecessary searches, latency or tokens.

This makes improvement work more targeted than optimizing only one accuracy score.

## 11. Strengths and limitations

**Strengths**

- About 113K questions provide a large established benchmark.
- Questions are designed for multi-document reasoning.
- Sentence-level supporting facts enable explainable evaluation.
- Comparison and bridge types support structured failure analysis.
- Distractor and fullwiki settings support controlled and retrieval-based experiments.
- Official evaluation code measures answers and evidence jointly.

**Limitations**

- It is a widely used public benchmark, so modern LLMs may have seen some examples during training.
- Distractor performance does not establish open-domain retrieval ability.
- Fullwiki results depend on the corpus, index and retrieval configuration.
- Some questions may be answerable through lexical shortcuts or model memory without the intended reasoning chain.
- Giving all candidate passages directly to a long-context model can reduce the need for an agent.
- Extra searches can improve accuracy while increasing latency and cost.

## 12. Practical setup

1. Download the official train/dev data.
2. Use a small development subset for pipeline validation.
3. Reproduce the official prediction format with `answer` and `sp`.
4. Build a one-shot retrieval baseline.
5. Add iterative retrieval and evidence-completeness checking.
6. Keep model, corpus, retriever and budgets fixed across the comparison.
7. Evaluate answer, supporting-fact and joint metrics.
8. Record search count, latency, tokens/cost and failures.
9. Analyze bridge and comparison questions separately.
10. Keep a held-out subset untouched while designing the workflow.

This provides both an end-to-end benchmark result and a concrete explanation of **why** the agent improves or fails.

## References

- HotpotQA official website: https://hotpotqa.github.io/
- Official repository: https://github.com/hotpotqa/hotpot
- Yang et al. (2018), *HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering*: https://aclanthology.org/D18-1259/
- Official evaluation script: https://github.com/hotpotqa/hotpot/blob/master/hotpot_evaluate_v1.py
