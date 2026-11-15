# MuSiQue

> **Historical research note (2026-10-25):** MuSiQue was explored as an alternative multi-hop QA benchmark. Group 9 has selected **KORA** on the **original BIRD Mini-Dev** for its Text-to-SQL evaluation. This file is retained as earlier topic-selection research; see the [submitted KORA proposal](../proposal/KORA/KORA_Group9_Proposal.pdf).

MuSiQue (**Multihop Questions via Single-hop Question Composition**) is a benchmark for evaluating **connected multi-hop reasoning**. It was introduced by Trivedi et al. in TACL 2022 to address a recurring weakness in earlier multi-hop QA benchmarks: a model can sometimes obtain the correct answer through shortcuts without actually connecting all required reasoning steps.

The core construction idea is bottom-up. MuSiQue starts from verified single-hop questions, composes them into connected reasoning graphs, and filters candidates so that later steps depend on answers from earlier steps. The released MuSiQue-Ans dataset contains **24,814 answerable 2–4 hop questions**. MuSiQue-Full adds matched unanswerable variants, producing a stricter setting that also tests whether a system recognizes insufficient evidence.

For this project, MuSiQue is a strong candidate for studying whether an agentic workflow adds value beyond one-shot RAG.

## 1. Why MuSiQue exists

A nominally multi-hop question may look like this:

```text
Fact A
  ↓
Fact B
  ↓
Final answer
```

but a model may exploit a lexical clue, memorized fact or annotation artifact and jump directly to the answer:

```text
Question ─────────────→ Final answer
```

MuSiQue was designed to reduce this problem. Its construction pipeline explicitly targets **connected reasoning**, where a later sub-question cannot be solved reliably without resolving an earlier one.

The paper reports that MuSiQue is harder to solve through disconnected reasoning than earlier benchmarks and creates a substantially larger human–machine performance gap.

## 2. How the questions are constructed

MuSiQue begins with single-hop question-answer-context tuples. Two questions are composable when an answer from one question acts as a bridge entity needed by another.

A simple 2-hop pattern is:

```text
Question 1
  ↓
Intermediate answer A
  ↓
Question 2 uses A
  ↓
Final answer B
```

These connections can be chained into several reasoning-graph structures with **2, 3 or 4 hops**.

The construction pipeline also:

- filters noisy single-hop examples;
- checks bridge-entity compatibility;
- filters questions that can be answered without the required dependency;
- limits reuse of bridge entities and source questions;
- reduces overlap across train, dev and test splits;
- adds hard distractor paragraphs;
- crowdsources a natural final multi-hop question from the reasoning graph.

This means the decomposition is not merely an explanation generated after the fact; it is a direct result of how the multi-hop question was built.

## 3. Dataset size and splits

The MuSiQue paper reports the following counts for **MuSiQue-Ans**:

| Split | 2-hop | 3-hop | 4-hop | Total |
| --- | ---: | ---: | ---: | ---: |
| Train | 14,376 | 4,387 | 1,175 | 19,938 |
| Dev | 1,252 | 760 | 405 | 2,417 |
| Test | 1,271 | 763 | 425 | 2,459 |
| **Total** | **16,899** | **5,910** | **2,005** | **24,814** |

MuSiQue-Full creates a corresponding unanswerable case for each answerable instance, so it contains roughly twice as many examples.

The official repository distributes train, dev and test files for both MuSiQue-Ans and MuSiQue-Full. The repository demonstrates local ground-truth evaluation on the dev sets and provides leaderboard submission instructions for test predictions.

## 4. What is in a record?

A representative MuSiQue-Ans record contains fields such as:

```json
{
  "id": "2hop__252311_366220",
  "question": "Who founded the company that distributed the film UHF?",
  "answer": "Mike Medavoy",
  "answer_aliases": [],
  "answerable": true,
  "question_decomposition": [
    {
      "question": "UHF >> distributed by",
      "answer": "Orion Pictures",
      "paragraph_support_idx": 10
    },
    {
      "question": "#1 >> founded by",
      "answer": "Mike Medavoy",
      "paragraph_support_idx": 6
    }
  ],
  "paragraphs": [
    {
      "idx": 0,
      "title": "...",
      "paragraph_text": "...",
      "is_supporting": false
    }
  ]
}
```

The exact release should be inspected before implementation, but these fields are especially useful for agent evaluation:

| Field | Meaning | Project use |
| --- | --- | --- |
| `question` | Final multi-hop question | Agent input |
| `answer` | Gold final answer | Answer evaluation |
| `answer_aliases` | Accepted alternative answer strings | Robust answer matching |
| `paragraphs` | Candidate evidence and distractors | Retrieval / context |
| `is_supporting` | Gold supporting-paragraph flag | Evidence evaluation |
| `question_decomposition` | Gold sequence of dependent sub-questions and intermediate answers | Failure analysis / decomposition evaluation |
| `paragraph_support_idx` | Supporting paragraph for a sub-question | Map reasoning step to evidence |
| `answerable` | Whether the supplied context is sufficient | Abstention evaluation in Full |

A normal question context contains **20 paragraphs**, combining the required supporting paragraphs with distractors.

## 5. Worked example

A public MuSiQue validation example is:

> Who founded the company that distributed the film UHF?

Gold answer:

> Mike Medavoy

The supplied decomposition is:

```text
Hop 1
UHF >> distributed by
  ↓
Orion Pictures

Hop 2
#1 >> founded by
  ↓
Mike Medavoy
```

An agent should therefore behave approximately like this:

```text
Question
  ↓
Identify the first missing relation
  ↓
Find evidence about UHF
  ↓
Intermediate answer: Orion Pictures
  ↓
Use Orion Pictures in the next step
  ↓
Find founder evidence
  ↓
Final answer: Mike Medavoy
```

The important point is not only whether the agent eventually outputs **Mike Medavoy**. The dataset also lets us examine whether it:

1. identified the correct first sub-question;
2. found the correct supporting paragraph;
3. extracted the correct intermediate entity;
4. used that entity in the next step;
5. selected the correct second supporting paragraph;
6. produced the correct final answer.

This is much more informative than one final accuracy number.

## 6. MuSiQue-Ans vs MuSiQue-Full

### MuSiQue-Ans

All examples are designed to be answerable from the supplied context.

The main evaluation targets are:

```text
Question
  ↓
Find supporting evidence
  ↓
Connect the hops
  ↓
Answer
```

This is the cleaner starting point for evaluating decomposition and iterative retrieval.

### MuSiQue-Full

For every answerable example, the construction process creates a contrasting unanswerable version by making one required single-hop step unsupported by the context.

The question remains the same while the evidence changes.

```text
Question
  ↓
Hop 1 ✓
  ↓
Hop 2 ✗ required evidence missing
  ↓
Do not fabricate an answer
```

This adds an important agent capability:

> **Can the system recognize that the evidence is insufficient and stop instead of hallucinating?**

MuSiQue-Full is therefore useful when the project moves from retrieval/reasoning accuracy to **reliability and abstention**.

## 7. Official evaluation

The repository provides `evaluate_v1.0.py`.

For MuSiQue-Ans, the official examples report:

- `answer_f1`
- `support_f1`

These separate final-answer quality from supporting-evidence quality.

For MuSiQue-Full, the evaluator additionally reports group-level sufficiency metrics, including:

- `group_answer_sufficiency_f1`
- `group_support_sufficiency_f1`

This makes it possible to distinguish:

```text
Correct answer?
Correct evidence?
Correctly recognize sufficient vs insufficient context?
```

For a project report, the official metrics should remain the primary benchmark metrics. Extra agent metrics can be added separately rather than replacing the benchmark evaluator.

## 8. What agent capabilities can MuSiQue evaluate?

| Capability | Evaluation question |
| --- | --- |
| Question decomposition | Did the agent identify useful dependent sub-questions? |
| Retrieval | Did it find the gold supporting paragraphs? |
| Intermediate-answer extraction | Did it obtain the bridge entity needed for the next hop? |
| Query reformulation | Did it use the previous result to form the next useful retrieval? |
| Multi-hop reasoning | Did it correctly connect 2–4 dependent steps? |
| Evidence selection | Did it distinguish gold evidence from hard distractors? |
| Grounding | Is the final answer supported by the selected evidence? |
| Stopping | Did the agent stop when enough evidence was found? |
| Abstention | In MuSiQue-Full, did it detect missing required evidence? |
| Efficiency | How many searches, tool calls, tokens and seconds were required? |

The gold decomposition is particularly useful for **diagnosis**. It lets us identify whether a failure came from planning, retrieval, an intermediate answer, or final reasoning.

## 9. Suggested agent workflow

A natural MuSiQue agent is:

```text
Question
  ↓
Planner / Decomposer
  ↓
Generate next sub-question
  ↓
Retrieve evidence
  ↓
Extract intermediate answer
  ↓
Is another dependent fact required?
  ├─ Yes → formulate next query using the intermediate answer
  └─ No
       ↓
Check evidence sufficiency
       ↓
Final answer / Abstain
```

The project does not need to expose hidden model chain-of-thought. Observable execution data is enough:

- generated sub-questions;
- retrieval queries;
- retrieved paragraph IDs/titles;
- selected supporting paragraphs;
- intermediate answers;
- number of iterations;
- final answer or abstention;
- latency;
- token/tool usage.

These traces can be compared with the released decomposition and supporting-paragraph annotations.

## 10. Recommended project experiment

A clean first study is:

> **Does explicit question decomposition plus iterative retrieval improve multi-hop QA accuracy and evidence quality compared with one-shot RAG, and is the gain worth the additional cost?**

### Baseline: one-shot RAG

```text
Question
  ↓
One retrieval
  ↓
Top-k paragraphs
  ↓
LLM
  ↓
Final answer
```

### Agent improvement

```text
Question
  ↓
Decompose next required fact
  ↓
Retrieve
  ↓
Extract intermediate answer
  ↓
Use intermediate answer in next query
  ↓
Repeat until evidence is complete
  ↓
Verify support
  ↓
Final answer
```

For a fair experiment, keep the following fixed:

- LLM;
- corpus;
- retriever / embedding model;
- top-k policy where applicable;
- context limit;
- official evaluator;
- maximum tool-call or retrieval budget.

The main variable should be **retrieval orchestration**, not a simultaneous change of model and prompt.

## 11. Recommended metrics

### Official benchmark metrics

| Layer | Metric | Purpose |
| --- | --- | --- |
| Final answer | Answer F1 | Correctness of the answer |
| Evidence | Support F1 | Correctness of selected supporting paragraphs |
| Sufficiency (Full) | Group answer sufficiency F1 | Whether answer behavior matches context sufficiency |
| Sufficiency (Full) | Group support sufficiency F1 | Whether support behavior matches context sufficiency |

### Additional project metrics

| Layer | Metric | Purpose |
| --- | --- | --- |
| Planning | Decomposition / hop success | Where the reasoning chain breaks |
| Retrieval | Supporting-paragraph recall | Whether required evidence was retrieved |
| Intermediate reasoning | Intermediate-answer accuracy | Whether the bridge entity was extracted correctly |
| Reliability | Abstention accuracy | Whether missing evidence is recognized |
| Reliability | Unsupported-answer rate | Hallucination / grounding failure |
| Efficiency | Retrieval / tool-call count | Agent overhead |
| Efficiency | Tokens | Model usage |
| Efficiency | Latency | End-to-end runtime |
| Stability | Repeated-run success | Sensitivity to stochastic behavior |

The gold decomposition should be used for **evaluation and analysis**, not exposed to the tested agent as an input.

## 12. Failure analysis

MuSiQue supports a useful failure taxonomy:

- **Decomposition failure:** wrong or incomplete sub-question.
- **Retrieval failure:** required supporting paragraph is not found.
- **Bridge failure:** correct intermediate answer is found but not used in the next step.
- **Extraction failure:** correct paragraph is retrieved but the intermediate answer is wrong.
- **Reasoning failure:** all required facts are available but combined incorrectly.
- **Evidence-selection failure:** distractors are selected instead of gold support.
- **Grounding failure:** final answer is correct or plausible but unsupported.
- **Stopping failure:** the agent continues retrieving after evidence is complete.
- **Abstention failure:** the agent invents an answer when a required step is unsupported.
- **Efficiency failure:** the agent succeeds but uses excessive searches, tokens or time.

Results should also be stratified by **2-hop, 3-hop and 4-hop** questions. A method that improves 2-hop accuracy but collapses on 4-hop questions may not actually improve long-horizon reasoning.

## 13. Data leakage caution

The official repository contains an explicit leakage warning.

MuSiQue was composed from single-hop questions originating from:

- SQuAD;
- T-REx;
- Natural Questions;
- MLQA;
- Zero Shot RE.

If a model or retrieval system is trained or tuned using those source datasets, some single-hop questions related to MuSiQue dev/test can leak into training.

To reduce this risk, the release includes IDs of source single-hop questions used in MuSiQue dev/test in:

`data/dev_test_singlehop_questions_v1.0.json`

Before a formal experiment, check whether any training, fine-tuning, demonstrations or retrieval corpus construction use those source questions.

For this project, the safest first experiment is to use a fixed pretrained model without fine-tuning on MuSiQue or its seed questions, tune the workflow on a development subset, and reserve untouched examples for final comparison.

## 14. Strengths and limitations

**Strengths**

- Explicitly designed to reduce shortcut-based multi-hop solving.
- Contains 2-, 3- and 4-hop questions.
- Provides supporting-paragraph supervision.
- Provides a decomposition created by the dataset-construction process.
- Hard distractors make evidence selection meaningful.
- MuSiQue-Full adds insufficient-evidence / abstention behavior.
- Official evaluator and prediction format are available.
- Fits a clear baseline-vs-agent experiment.

**Limitations**

- The benchmark is public and from 2022, so modern foundation models may have encountered related content during pretraining.
- The supplied context is a controlled reading-comprehension setting, not automatically equivalent to open-web research.
- Gold decomposition can create leakage if accidentally given to the agent.
- Results depend on whether the experiment uses supplied candidate paragraphs or constructs a larger retrieval corpus.
- MuSiQue-Full adds reliability evaluation but also makes the task definition and scoring more complex.
- Additional agent steps can improve accuracy while increasing cost and latency.

## 15. Practical starting plan

If MuSiQue is shortlisted for implementation:

1. Pin the dataset release and repository commit.
2. Download the official data using the repository instructions.
3. Inspect and validate the dev JSONL schema.
4. Start with MuSiQue-Ans rather than Full.
5. Build a small deterministic dev subset stratified by hop count.
6. Implement the official output format and reproduce the evaluator locally.
7. Build a one-shot RAG baseline.
8. Add explicit decomposition and iterative retrieval.
9. Record observable agent traces and efficiency metrics.
10. Evaluate overall and by hop count.
11. Classify failures using the released support/decomposition annotations.
12. Only then test MuSiQue-Full for abstention and evidence sufficiency.

This keeps the initial project narrow while preserving a clear path to a more advanced reliability experiment.

## 16. Project fit

At the time of initial research, MuSiQue was a **strong candidate**, but it was **not selected** for KORA.

Its main value for the COMP7608 project is that it supports a focused agentic research question with measurable internal behavior:

```text
One-shot RAG
vs.
Decompose → Retrieve → Intermediate Answer → Retrieve Again → Verify
```

A positive result would show not merely that a larger workflow gets more answers correct, but **which agent behavior improves connected multi-hop reasoning and at what additional cost**.

## License

The official repository distributes MuSiQue under **CC BY 4.0**. Reuse and adaptation are permitted subject to the license's attribution requirements. Any project report or released derivative should cite the dataset and its authors.

## References

- Official MuSiQue repository: https://github.com/StonyBrookNLP/musique
- Trivedi, H., Balasubramanian, N., Khot, T., & Sabharwal, A. (2022). *MuSiQue: Multihop Questions via Single-hop Question Composition*. Transactions of the Association for Computational Linguistics, 10, 539–554: https://aclanthology.org/2022.tacl-1.31/
- MIT Press article: https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00475/110996/MuSiQue-Multihop-Questions-via-Single-hop-Question
- Public validation viewer used to inspect the worked record/schema: https://huggingface.co/datasets/fladhak/musique
