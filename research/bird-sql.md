# BIRD-SQL / BIRD Mini-Dev

> **Dataset update — 8 November 2026:** Use **Mini-Dev 2026** for new harness experiments. The original Mini-Dev instructions and archived 59.8% EX remain historical reproduction evidence. See [dataset versions and migration](../docs/bird-dataset-versions.md) for the Docker-free download command, changed IDs, and fresh evaluation workflow. Full Dev 20251106 is a separate optional benchmark.

> **Project status (2026-10-25):** Original BIRD Mini-Dev was selected for KORA. The preliminary agent experiment and ablation suggestions below are historical research ideas; use the [submitted KORA S0/S1/B0–B4 evaluation design](../proposal/KORA/KORA_Group9_Proposal.pdf) as the current specification.

BIRD (**BIg Bench for LaRge-scale Database Grounded Text-to-SQL Evaluation**) evaluates whether a system can turn natural-language questions into SQL that correctly answers questions over realistic databases.

For this project, BIRD is especially useful because it can be studied as more than a one-shot text-to-SQL task. A SQL agent can inspect schemas and values, generate a query, execute it, observe errors or suspicious results, repair the query, and then submit a final answer.

The full BIRD-SQL benchmark contains **12,751+ question-SQL pairs, 95 databases, 33.4 GB of database content, and more than 37 professional domains**. For development, this project should start with the **original BIRD Mini-Dev 500-question setting**, which gives a much smaller and cheaper evaluation loop.

> **Version note:** the Mini-Dev repository also contains newer Mini-Dev V2 / LiveSQLBench material. This note treats the original 500-example SELECT-only Mini-Dev setting as a separate benchmark configuration. Do not combine versions, SQL dialects or task types into one score.

## 1. What problem does BIRD test?

A simple text-to-SQL system looks like this:

```text
Natural-language question
          ↓
         LLM
          ↓
         SQL
```

BIRD makes the task harder because the model must ground the question in a real database:

```text
Question
  ↓
Understand the user's meaning
  ↓
Find relevant tables and columns
  ↓
Understand relationships and database values
  ↓
Generate SQL
  ↓
Execute against the database
  ↓
Return the correct result
```

This is closer to a real data-analysis workflow than evaluating SQL syntax alone.

BIRD is useful for asking:

- Can the system select the correct tables and columns?
- Can it infer joins and relationships?
- Can it map natural-language concepts to database values?
- Can it use supplementary domain evidence correctly?
- Can execution feedback help repair incorrect SQL?
- Does an agentic workflow improve correctness enough to justify extra cost and latency?

## 2. Why use Mini-Dev first?

The official Mini-Dev release was created to support faster and cheaper development cycles.

The original Mini-Dev setting contains:

- **500 high-quality text-to-SQL examples**;
- **11 databases**;
- SQLite, MySQL and PostgreSQL versions;
- natural-language questions;
- database identifiers;
- expert-annotated evidence;
- reference SQL;
- database schema/value descriptions;
- executable database contents;
- evaluation code.

This is a practical size for repeated experiments:

```text
Baseline
  ↓
Run 500 questions
  ↓
Analyze failures
  ↓
Add one agent improvement
  ↓
Re-run the controlled evaluation
```

For a first prototype, SQLite is the simplest setting because it avoids running an external database server.

## 3. What is inside one example?

A public Mini-Dev record contains fields such as:

```json
{
  "question_id": 707,
  "db_id": "codebase_community",
  "question": "Among the posts with views ranging from 100 to 150, what is the comment with the highest score?",
  "evidence": "views ranging from 100 to 150 refers to ViewCount BETWEEN 100 and 150; comment with the highest score refers to Text where MAX(Score);",
  "SQL": "SELECT Text FROM comments WHERE PostId IN ( SELECT Id FROM posts WHERE ViewCount BETWEEN 100 AND 150 ) ORDER BY Score DESC LIMIT 1",
  "difficulty": "moderate"
}
```

| Field | Meaning | Agent-evaluation use |
| --- | --- | --- |
| `question_id` | Example identifier | Trace and error analysis |
| `db_id` | Database to query | Select the correct environment |
| `question` | Natural-language request | Agent input |
| `evidence` | Expert-provided external/domain knowledge | Optional grounding context |
| `SQL` | Reference SQL | Gold reference for evaluation/debugging |
| `difficulty` | Difficulty label | Break down results by difficulty |

The database release also provides schema/value descriptions and executable database contents. This means an agent can inspect the database rather than relying only on a schema pasted into the prompt.

## 4. Worked example

Consider this Mini-Dev example:

> **Question:** Among the posts with views ranging from 100 to 150, what is the comment with the highest score?

The supplied evidence maps the natural-language phrases to database logic:

```text
"views ranging from 100 to 150"
    → ViewCount BETWEEN 100 AND 150

"comment with the highest score"
    → return Text for the highest Score
```

The reference SQLite query is:

```sql
SELECT Text
FROM comments
WHERE PostId IN (
    SELECT Id
    FROM posts
    WHERE ViewCount BETWEEN 100 AND 150
)
ORDER BY Score DESC
LIMIT 1;
```

A useful decomposition is:

```text
Question
  ↓
Relevant entity: posts
  ↓
Filter: ViewCount BETWEEN 100 AND 150
  ↓
Relationship: posts.Id → comments.PostId
  ↓
Relevant entity: comments
  ↓
Rank: Score DESC
  ↓
Output: Text
  ↓
Take the top row
```

This single example tests:

| Capability | Required inference |
| --- | --- |
| Question understanding | The requested view range is numeric |
| Schema grounding | The range applies to `posts.ViewCount` |
| Relationship reasoning | Comments connect through `comments.PostId = posts.Id` |
| Filtering | Use `BETWEEN 100 AND 150` |
| Ranking | Highest score means descending order |
| Output selection | Return comment `Text`, not the score or post ID |
| Cardinality | Return one top-ranked row |

Equivalent SQL can also be written with a join. This is one reason execution-based evaluation is more meaningful than comparing SQL strings character by character.

## 5. Why is BIRD harder than a toy SQL dataset?

### Database values matter

Real databases often encode user language differently from the question.

```text
Question:
customers from Hong Kong

Possible database value:
country_code = 'HKG'
```

A model that only reads column names may fail. An agent can inspect distinct values or sample rows before generating SQL.

### Business or external knowledge matters

A user may ask for a concept that is not a literal column name:

```text
"successful transaction"
        ↓
status = 1
```

BIRD includes expert evidence to represent this kind of mapping.

### Relationships matter

The answer may require several tables. The system must choose both the relevant tables and the correct join path.

### Correct syntax is not enough

A query can execute successfully and still answer the wrong question. Therefore **SQL execution success** and **answer correctness** should be reported separately.

## 6. From text-to-SQL model to SQL agent

A one-shot baseline could be:

```text
Question + schema + evidence
          ↓
         LLM
          ↓
         SQL
          ↓
       Execute
```

A more agentic system could expose tools such as:

```python
list_tables()
get_schema(table)
sample_rows(table)
search_column_values(table, column, keyword)
execute_sql(sql)
submit_answer(sql)
```

The workflow becomes:

```text
User question
     ↓
Inspect available tables
     ↓
Inspect relevant schemas
     ↓
Need value grounding?
 ├─ Yes → inspect/search database values
 └─ No
     ↓
Generate candidate SQL
     ↓
Execute SQL
     ↓
Error or suspicious result?
 ├─ Yes → understand failure → repair → execute again
 └─ No  → validate result → final SQL
```

The agent is not rewarded merely for using more tools. Tools are useful only when they improve the probability of returning the correct database result.

## 7. What should the agent be allowed to see?

For a clean experiment, separate **task inputs** from **evaluation-only information**.

A reasonable agent input is:

- the natural-language question;
- database access;
- schema/table descriptions;
- the official evidence field, if the selected setting includes it.

The agent may use tools to inspect:

- tables;
- columns and keys;
- sample rows;
- distinct or searched values;
- execution errors;
- candidate-query results.

The agent should **not** receive:

- reference SQL during prediction;
- reference execution results;
- hidden evaluation answers;
- evaluator internals that reveal the solution.

Gold SQL should be reserved for scoring and post-hoc failure analysis.

## 8. Evaluation

### Execution Accuracy (EX)

The core idea is to execute the predicted SQL and compare its result with the reference result.

For example, these two queries are textually different:

```sql
SELECT COUNT(*)
FROM customers
WHERE country = 'HK';
```

```sql
SELECT COUNT(customer_id)
FROM customers
WHERE country = 'HK';
```

If both return the same correct answer, exact SQL-string matching would be unnecessarily strict. Execution-based evaluation is better aligned with the task.

### SQL execution success

Also record whether generated SQL runs without error.

```text
SQL runs successfully
        ≠
SQL answers the question correctly
```

This is a diagnostic metric, not a replacement for correctness.

### R-VES and Soft F1

Mini-Dev also provides **Reward-based Valid Efficiency Score (R-VES)** and **Soft F1-Score** as additional evaluation metrics. For this project, EX should remain the clearest primary correctness metric, with R-VES and Soft F1 reported as supplementary Mini-Dev metrics.

## 9. Recommended project experiment

A clean research question is:

> **Does schema/value inspection plus execution-feedback repair improve BIRD Mini-Dev execution accuracy compared with one-shot SQL generation, and is the gain worth the additional tool calls, tokens and latency?**

### Baseline A — one-shot generation

```text
Question + schema + evidence
          ↓
         LLM
          ↓
         SQL
          ↓
       Execute once
```

### Agent B — execution repair

```text
Question + schema + evidence
          ↓
         LLM
          ↓
      Candidate SQL
          ↓
        Execute
          ↓
    SQL error?
     ├─ Yes → repair → execute again
     └─ No  → submit
```

### Agent C — schema/value inspection + repair

```text
Question
  ↓
Inspect relevant schema
  ↓
Inspect values only when needed
  ↓
Generate SQL
  ↓
Execute
  ↓
Check error/result
  ↓
Repair if needed
  ↓
Submit
```

Keep these fixed across systems:

- the same base LLM;
- the same 500 examples;
- the same SQLite databases;
- the same evidence policy;
- the same maximum context;
- the same evaluator;
- a fixed maximum number of repair/tool steps.

The main variable should be the **agent workflow**, not a simultaneous model change.

## 10. Recommended metrics

| Layer | Metric | Purpose |
| --- | --- | --- |
| Final correctness | Execution Accuracy | Did the query produce the correct result? |
| Query validity | SQL execution success rate | Did the SQL run without error? |
| Result similarity | Soft F1 | Additional Mini-Dev diagnostic metric |
| Efficiency | R-VES | Additional Mini-Dev efficiency-oriented metric |
| Agent behavior | Average tool calls | Cost of exploration and repair |
| Repair | First-attempt vs final EX | Did self-correction recover failures? |
| Cost | Tokens / model cost per task | Whether gains are economical |
| Latency | Seconds per task | Practical overhead of agent loops |
| Reliability | Repeated-run success | Sensitivity to stochastic behavior |

Also break results down by difficulty, database, number of tables used, whether value inspection was used, and whether repair was triggered.

## 11. Failure analysis

Do not stop at one aggregate score. Label the root cause of failed examples.

| Failure type | Example |
| --- | --- |
| Wrong table | Queries `users` instead of `comments` |
| Wrong column | Uses `Score` where `ViewCount` is required |
| Wrong join | Correct tables but incorrect relationship |
| Missing condition | Ignores one part of the question |
| Wrong aggregation | Uses `COUNT` instead of `SUM` |
| Wrong ranking/limit | Finds valid rows but not the requested maximum |
| Value grounding | Fails to map language to a stored value |
| Evidence misuse | Interprets supplementary evidence incorrectly |
| SQL syntax/runtime | Query cannot execute |
| Repair failure | Error is observed but the next query does not fix it |
| Over-exploration | Unnecessary tool calls add cost |

This supports a real improvement cycle:

```text
V1 evaluation
  ↓
Identify dominant failure category
  ↓
Add one targeted capability
  ↓
V2 evaluation
```

## 12. Useful ablation study

If the full agent performs better, test which component actually helped.

| Setting | Schema inspection | Value inspection | Execution repair |
| --- | :---: | :---: | :---: |
| Baseline | Fixed prompt only | No | No |
| Repair only | Fixed prompt only | No | Yes |
| Schema agent | Yes | No | Yes |
| Full agent | Yes | Yes | Yes |

This is stronger than concluding only that "agents work better."

## 13. Main limitations

### Mini-Dev is development data

The 500 examples come from BIRD development data. If prompts and policies are repeatedly tuned on all 500 examples, the final score is not a clean held-out result.

For a course experiment, create a documented development/held-out split or use a separate compatible evaluation set, and describe any project split as a **custom split**, not the official BIRD test leaderboard.

### Evidence can simplify the task

The expert evidence field already provides semantic mappings. Compare systems under the same evidence policy.

### Tool permissions change the task

Allowing unrestricted schema/value inspection makes the system more capable than a standard one-shot text-to-SQL baseline. That is acceptable for an agent study, but tool permissions must be stated clearly.

### Execution equivalence is imperfect

Different SQL can produce the same result, while two logically different queries can occasionally agree on one database instance. Execution-based scoring is practical but not a perfect proof of semantic equivalence.

### Newer BIRD resources are separate settings

Mini-Dev V2 / LiveSQLBench, BIRD-Interact and BIRD-Critic are useful future extensions, but their results should not be mixed with the original 500-example Mini-Dev score.

## 14. Why BIRD is a strong candidate for this project

Compared with a pure QA benchmark, BIRD gives a clear tool-using loop:

```text
Natural language
      +
Database exploration
      +
Schema reasoning
      +
SQL generation
      +
Execution
      +
Failure recovery
```

It supports a straightforward research cycle:

```text
Build
  ↓
Evaluate
  ↓
Analyze failures
  ↓
Improve one capability
  ↓
Re-evaluate
```

A concrete project question is:

> Does an agent that decides when to inspect schemas/values and repair failed queries outperform one-shot generation under the same model and a controlled cost budget?

## 15. Official sources

- [BIRD-SQL official website](https://bird-bench.github.io/)
- [BIRD Mini-Dev official GitHub](https://github.com/bird-bench/mini_dev)
- [BIRD Mini-Dev canonical Hugging Face dataset](https://huggingface.co/datasets/birdsql/bird_mini_dev)
- [BIRD Data Intelligence Index](https://github.com/bird-bench/Data-Intelligence-Index)

For implementation, pin the exact Mini-Dev dataset/database version and repository commit used by the experiment.
