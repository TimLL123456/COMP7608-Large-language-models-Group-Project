# Self Reflection Agent — V2 SQL-First Workflow (V1.1 historical design retained)

> **Current status (15 November 2026): Implemented, full local BIRD Mini-Dev 2026 benchmark completed (350/500, 70.00% strict EX).** Historical 12–13 November draft/implementation milestones below are retained as dated evidence.
>
> **Project:** HKU COMP7608 KORA Text-to-SQL · **Variant:** `SelfReflection`  
> **Date:** 12 November 2026 · **Scope:** Implementation, versioned runtime Reviewer Prompt, and preserved design specification.  
> **Approved architecture:** New, independent Self Reflection Agent that imports the existing B0 Baseline Agent unchanged.  
> **Core evaluation rule:** Generalizable SQL correctness principles, **not** memorized benchmark cases, question identifiers, answers, or corrections.


## Current performance evidence — 13 November 2026

The archived [Self Reflection full 500-question evaluation](../evaluation-results/self-reflection-full-20261113/README.md) scored **350/500 (70.00%)** local strict EX (Dev 280/400; Test 70/100) and produced final SQL for **498/500 questions**. Results use a local Mini-Dev 2026 selection, **not** the official hidden benchmark. Preserve the separate recorded budgets, reviewer statuses, failures and provenance; reviewer PASS does not guarantee EX correctness. This is evidence from a later run than the implementation-only notes below.

## V2 — SQL-first workflow (13 November 2026)

**Primary objective:** maximize safe, executable SQL output within the assigned per-agent and global budgets. Reviewer PASS is desirable but is **not** a prerequisite for output. Never label an unverified candidate as PASS; never return known unsafe or non-executable SQL as usable output.

### Workflow

1. **B0 investigation:** run the unchanged standalone B0 prompt/tools with **SelfReflection-only** middleware caps of 39 model calls, 39 tool calls and 39 SQL executions. Standalone B0 retains defaults of 40/40/40.
2. **B0 SQL finalization:** if no final SQL, use the reserved 40th model call (if needed) to synthesize a read-only candidate from the question, authorized evidence and collected tool observations. A previously observed final SQL can be reused. Reserve one tool/SQL execution to verify the candidate. No new investigation occurs here.
3. **Independent reviewer:** execute exact candidate SQL read-only, then investigate material uncertainty in multiple rounds. Reviewer maximums are **40 model calls, 40 total tools (one initial execution + up to 39 inspections), and 40 SQL executions**. Stop as soon as PASS/FAIL is supported. The last model call, or the next call when inspections run out, is a no-tools review finalization.
4. **Router:** PASS accepts SQL; FAIL with actionable feedback invokes another B0 attempt when within global budget; UNCERTAIN retains the candidate as unverified. At most three B0 attempts by default.
5. **Output selection:** prefer PASS, then executable UNCERTAIN, then executable FAIL (known issues explicitly recorded), then executable ERROR/unreviewed candidate. Never conflate successful SQL execution with semantic correctness.

### Budgets and accounting

- **Per B0 or Reviewer attempt:** at most 40 model, 40 tool, 40 SQL calls including finalization; finalization is reserved **inside**, not on top of, these limits.
- **Global default for three complete B0+review attempts:** 240 model, 240 tool, 240 SQL calls. Stop rather than exceeding the global budget. No guaranteed SQL when no safe executable candidate exists or a provider fails.
- **Outputs:** \`final_sql\`, \`output_status\` (\`verified\`, \`generated_unverified\`, \`generated_known_issues\`, \`missing\`), \`review_status\`, \`finalization_triggered\`, detailed call/token traces and stop reason.
- **Evaluation:** SQL Output Rate first; independently track strict BIRD EX, budget violations (target zero), review quality, false positives/negatives, calls, tokens and latency. Reviewer PASS is not a gold label. Do not use BIRD gold SQL/evaluations during inference.
- **Historical invariants:** no changes to baseline experiment definitions, historical run artifacts, public group repository or evaluation gold data. No MKE/KG/planner/router addition.

### Verification state

Implementation is committed with targeted regression tests, but test execution and full Mini-Dev inference require a compatible project environment and provider credentials. Do not claim EX improvement until measured.

---

## Historical V1.1 architecture, criteria and design record

The remainder of this document preserves the original V1.1 specification for audit and comparison; it describes historical defaults and **does not override the V2 behavior above**.

## 1. Objective and research question

Build a **standalone Self Reflection Agent** to improve the reliability and execution accuracy of an existing Text-to-SQL baseline through an **independent SQL Reflection Reviewer**. The Reviewer checks the submitted final SQL and observed read-only SQL results against the original user question and its authorized evidence. It returns a structured diagnosis; if a material failure is supported by evidence, the **whole B0 agent** is invoked again with targeted feedback.

**Research question:** Does evidence-based SQL review followed by bounded regeneration improve strict BIRD Execution Accuracy (EX) versus unchanged B0, and at what cost in calls, tokens, SQL executions, latency, and regressions?

This document preserves the original implementation specification and describes the source implementation added in Section 17. V1 source files now exist, but a complete dependency-resolved regression run, live provider inference, and BIRD EX improvement have **not** been verified.

## 2. Architecture and ownership of responsibilities

```text
             ┌─────────────────────────┐
             │  1. User Question       │
             └───────────┬─────────────┘
                         │
          ┌──────────────▼──────────────────┐
          │       Self Reflection Agent      │
          │         (new coordinator)        │
          │                                  │
     ┌────┼──► 2. Existing B0 Baseline Agent │
     │    │          (unchanged)             │
     │    │                 │                │
     │    │                 ▼                │
     │    │    3. SQLReflectionReviewer      │
     │    │         (SQL + results)          │
     │    └─────────┬───────────┬────────────┘
     │           FAIL           │ PASS
     │    targeted feedback     ▼
     └───────────────►      Final SQL
```

The agreed **three workflow nodes** are User Question, B0 Baseline Agent, and Reflection Reviewer. The **Self Reflection Agent** is the outer orchestrator; it is not a fourth SQL-generation component. B0 retains its own schema exploration, table and value inspection, SQL drafting, read-only execution, tool calling, and inference lifecycle.

| Component | Owns | Must not do |
| --- | --- | --- |
| User Question | Natural-language requirements and permitted evidence | Supply gold SQL, gold results, or evaluation labels |
| Existing B0 | Interpret, investigate, generate and return final candidate SQL | Be rewritten or modified to support reflection |
| SQLReflectionReviewer | Independently inspect candidate logic and available execution evidence; issue structured PASS/FAIL/UNCERTAIN | Write or submit replacement final SQL; infer gold answers |
| SelfReflectionAgent coordinator | Prompt/input adaptation outside B0, attempts, review handoffs, aggregate budget, trace, final output | Silently accept unverified output or overwrite baseline runs |

**Feedback path:** Reviewer FAIL → concrete diagnostic findings → *fresh full B0 invocation* with an attempt-local augmented input. It is not a direct replacement-query generator. The system name “Self Reflection” denotes external critique and iterative refinement; a reviewer PASS is **provisional acceptance**, not a proof of semantic correctness.

## 3. Scope and invariants

**Agreed requirements**

- **No edits to B0 files or behavior:** Preserve `scr/baselines/bird_b0.py`, `scr/cli/run_bird_b0_eval.py`, their prompts, limits, tools, middleware, and existing tests.
- Use new and independently runnable agent, reviewer, CLI, tests, output directories and manifest. Do not migrate B0 or couple it to a mandatory reviewer.
- Reuse the existing pinned BIRD dataset handling, selection manifests, read-only SQLite adapter, and strict independent EX evaluator. Preserve B0 and historical experiment artifacts.
- No MKE, Knowledge Graph, Query Planner, Model Router, saved Metadata Discovery V2 notes, vector store, or new agent framework is required in V1.
- **Gold isolation:** Agent and Reviewer must never load `BirdEvaluationReferences`, gold SQL, gold result rows, offline failure inventories or per-question reference diagnoses at inference time. These are evaluator/research-only.
- All reviewer rules and live prompt instructions must be **schema-agnostic and database-agnostic**. Do not encode any benchmark question identifiers, fixed answers, known corrections, or dataset-specific conditions.
- Keep missing or unsupported evidence explicit. Never equate SQL execution success, a plausible preview, or an empty result with semantic correctness.
- Log review reasoning and observed usage. Separate confirmed facts from inference and uncertainty.

**Historical V1.1 design-only milestone (before implementation):** No Python runtime files, no evaluator registration, no generated results, no model API calls, no full-dataset benchmark, no edits to the public group repository.

## 4. Naming and existing integration points

| Element | Naming |
| --- | --- |
| Agent | **Self Reflection Agent** (not “B0 Self-Reflection Agent”) |
| Main class | `SelfReflectionAgent` |
| Reviewer | `SQLReflectionReviewer` |
| Evaluation variant | `SelfReflection` |
| Module | `scr/agents/self_reflection_agent.py` |
| Reviewer module | `scr/agents/sql_reflection_reviewer.py` |
| CLI module | `scr.cli.run_bird_self_reflection_eval` |
| Results subdirectory | `SelfReflection/` |

The existing source package is named **`scr/`**, not `src/`. Inspected integration points include `scr.baselines.bird_b0.make_agent(store, model, prompt_variant)`, `run_one(question, agent, ...)`, `extract_final_sql(...)`, and `scr.baselines.sqlite_readonly.ReadOnlySqlite`. B0 `run_one()` reports the *actual final SQL* separately from SQL observed in tool traces; the Reviewer must inspect the **actual final SQL**. The existing EX evaluator currently keeps an allowed-variant registry; if registration is needed during implementation, modify only its allowlist, not its scoring behavior.

## 5. Reviewer workflow

**Stage A — Requirement extraction:** Translate the original question and provided evidence into inspectable requirements: requested entities and output columns, calculations and metrics, populations and exclusions, grouping grain, dates and temporal interpretation, order/limit, representation, precision, and explicit conditions. Record ungrounded implications as uncertain rather than inventing business rules.

**Stage B — SQL and result verification:** Match each applicable requirement to SQL structure, database metadata, and the **bounded observed result**. Check deterministic SQL constraints first, then use independent LLM semantic review. Only perform targeted, read-only inspection to resolve a *specific* uncertainty.

**Stage C — Evidence-based decision:** Emit a per-criterion review and an overall PASS/FAIL/UNCERTAIN/ERROR, with supporting evidence, missing evidence, and action-oriented feedback for B0. No speculative rewrites or automatic acceptance of incomplete checks.

These are *internal reviewer stages*, not additional top-level agents.

## 6. Ten-category generalized validation rubric

Every check has `PASS`, `FAIL`, `UNCERTAIN`, or `N/A` status. **N/A only means the check is inapplicable; it is not positive proof.** Judge relevant requirements, not the presence of particular SQL syntax.

| # | Criterion | Generalized correctness standard | Typical evidence |
| --- | --- | --- | --- |
| 1 | **Requirement Coverage** | Ensure all explicitly and contextually required information is represented; detect omitted or unrelated outputs and unmet constraints. | Question/evidence mapped to output expressions and predicates |
| 2 | **Table & Column Selection** | Confirm source tables, columns and metric definitions represent the intended business concept and measure, rather than a similarly named proxy. | Schema, column descriptions, verified values |
| 3 | **JOIN & Relationship** | Check join keys, relationship paths, inclusion/exclusion effects, optional rows and many-to-many or one-to-many multiplication. Do not assume FK implies unique rows without evidence. | Table grain, keys, DDL, bounded data checks |
| 4 | **Aggregation Logic** | Check functions, denominators, ratios, distinctness and null handling; calculations must correspond to the requested population and measure. | Question, SQL expressions, group scope |
| 5 | **Filtering Logic** | Detect absent, contradictory, overly narrow, overly broad or unsupported predicates; distinguish WHERE versus HAVING and interpret business filters cautiously. | Question/evidence, condition expressions, verified category meanings |
| 6 | **Data Granularity** | Verify counting, deduplication, joins and grouping at the intended entity/observation grain; check whether distinctness applies across the required group. | Requested unit of analysis, schema grain, GROUP BY and join behavior |
| 7 | **Value Semantics** | Verify business codes, categories, case, placeholder values, NULL treatment, numeric units and representations. Never invent code meanings. | Value distributions, metadata, supplied business definitions |
| 8 | **Temporal Logic** | Distinguish date intervals, exclusive/inclusive bounds, as-of snapshots, latest-known records, same-day updates and time zones where material. | Question and SQL predicates, date column meanings |
| 9 | **Output Requirements** | Match requested output columns, their meanings, column count/order where relevant, formatting, precision, categorical representation, ordering and LIMIT. | Result-column names, expressions, stated output contract |
| 10 | **Execution & Result Consistency** | Verify the **exact final submitted SQL** is safe and executable, resolves identifiers and aliases, and has no directly evidenced output contradiction. A plausible result is not correctness proof. | Read-only compilation/execution, status, columns, bounded rows |

**Generalization safeguard:** The rubric is a reusable checklist of *types of reasoning*, not a list of previously failed benchmark questions, database-specific fix recipes, known expected answers or memorized predicates. A criterion may be N/A, and any required unverifiable semantic condition should be marked UNCERTAIN.

## 7. Decision policy and precedence

| Overall status | Standard | Coordinator action |
| --- | --- | --- |
| `PASS` | All material applicable requirements have support from inspected evidence, no substantiated defect is identified, and mandatory safety/execution checks pass. This is **provisional**. | Accept current SQL, preserve review trace |
| `FAIL` | At least one material mismatch or a confirmed *candidate SQL defect* (e.g. a genuine compilation/name-resolution error), supported by specific evidence. | Send diagnosis to a fresh full B0 attempt within budget |
| `UNCERTAIN` | Material semantics or required evidence cannot be verified; suspicion alone cannot establish a defect. | Targeted bounded investigation if useful, otherwise safe stop as unverified |
| `ERROR` | Reviewer parser/provider/tool/infrastructure failure prevents a reliable review. | Record separate error, retry only within policy, never fabricate PASS |

**Precedence:** A confirmed unsafe/invalid final SQL or a material evidenced mismatch yields FAIL, even if other criteria pass. A reviewer/tool infrastructure failure is ERROR unless an independently verified candidate defect is already known. In the absence of confirmed failure, unresolved *material* criteria yield UNCERTAIN; only supported applicable requirements can support PASS.

Evidence must distinguish **directly observed** (original wording, SQL clause, schema/DDL, result columns or execution error), **corroborated metadata**, **inference**, and **unknown**. There is no universal LLM confidence threshold that overrides these standards. Severity should reflect whether a finding changes correctness, not how surprising it feels. Do not FAIL on an unexplained empty set, a short result preview, unsupported expectations of row counts, or a subjective preference for different-but-equivalent SQL.

## 8. Evidence contract and false-positive protection

Every reported FAIL issue must identify:

1. **Violated requirement:** What exactly the original question/evidence requires.
2. **Observed behavior:** The SQL clause, result shape, schema fact or execution error under review.
3. **Grounding:** Which evidence supports the mismatch; cite the relevant clause/field rather than claiming nonexistent database knowledge.
4. **Action:** What B0 should verify or reconsider, **without submitting replacement final SQL**.

When an interpretation depends on undocumented business semantics, mark UNCERTAIN and request narrow inspection rather than treating a guessed meaning as fact. Preserve viable logic; do not suggest changes merely because another SQL formulation is possible. Retain all candidate versions so offline scoring can identify regressions, false positive reviews and false negative reviews.

**Review-result limitation:** On BIRD, an offline EX mismatch indicates failure of strict benchmark execution-result agreement, not necessarily indisputable human semantic error when a question/annotation is ambiguous. Report this distinction rather than forcing every EX mismatch into a confirmed semantic label.

## 9. Generalized Reviewer Prompt — V1 draft

The following is the original database-independent prompt design. The implemented runtime Reviewer uses the versioned `scr/agents/prompts/sql_reflection_v1.txt` file. Both must exclude per-question research answers, gold SQL and benchmark-specific corrections.

```text
ROLE
You are an independent SQL Reflection Reviewer.

OBJECTIVE
Assess whether the candidate final SQL faithfully answers the user's
question, based only on authorized question text, evidence, database
metadata and observed read-only execution results.

PROCEDURE
1. Extract explicit and contextually required outputs, business
   calculations, population, exclusions, grouping, time conditions
   and representation constraints.
2. Map each applicable requirement to SQL expressions, relationships,
   predicates, grouping and observed result structure.
3. Evaluate table/column selection, JOIN semantics, aggregation,
   filtering, granularity, value meanings, temporal logic, output
   representation and final SQL execution consistency.
4. Check both missing conditions and additional unsupported conditions.
   Do not assume that plausible extra restrictions are intended.
5. Examine whether joins, counting, distinctness and denominators
   act at the requested entity and group level.
6. Distinguish date windows, as-of states, latest-known records and
   same-day events where relevant.
7. Review the exact final SQL, not an earlier tool-tested candidate.
   Safe compilation/execution is necessary when applicable, but it
   does not establish semantic correctness.
8. Investigate only a concrete gap through bounded, read-only
   metadata/value inspection. Preserve uncertainty when unresolved.
9. Output FAIL only for material evidence-backed mismatches.
   Output UNCERTAIN for unverified material semantics.
   Output ERROR for review or infrastructure failure.
   Output PASS only as provisional acceptance after applicable checks.
10. Preserve correct logic. Never recommend a speculative correction,
    generate a replacement final SQL, or assert a benchmark gold answer.
11. Return the prescribed structured findings and diagnostic feedback.
12. Do not request, read, infer from or include benchmark gold SQL,
    gold results, question-specific scored cases or reference analyses.
```

**Prompt exclusions:** No BIRD question IDs; no particular database/tabular answers, business-code literals, fixed filters or known correct query texts; no instance-specific failure-analysis excerpts; no dataset-specific “when you see X, rewrite to Y” rules. Offline observations may inform the *general category definitions* but must not contaminate live inference context.

## 10. Targeted inspection, safe execution and evidence scope

Use existing read-only tools such as `list_tables()`, `inspect_table()` and `ReadOnlySqlite.execute()`, with time/row limits and strict SQL safety. A Reviewer investigation should name the uncertainty it is resolving and stop once sufficient evidence is found or the inspection budget is exhausted.

- **Candidate SQL gate:** Check the exact `final_sql` supplied to the evaluator. A safe, bounded SQLite compilation/name-resolution check (for example, suitably guarded EXPLAIN) may catch compiler defects; follow with bounded execution when appropriate. Do not assume a previous B0 `execute_sql` call proves its later final output compiles.
- A compilation gate does **not** prove that SQL answers the user, and must never execute unsafe statements or unlimited queries.
- Distinguish bounded observed rows from a full result; retain `truncated` and execution error flags.
- Schema, foreign keys, row counts and observed values are different grades of evidence. Do not infer uniqueness or code semantics from technical names alone.
- Mini-Dev 2026 verified table/column description CSVs can be used **optionally** after matching schema/dataset revision, but the agent must remain usable without them. Do not load another agent's persisted Metadata Discovery V2 notes by default.
- Gold/reference files and historical per-question evaluation artifacts must never be placed in reviewer tool-accessible paths or context.

## 11. Structured reviewer response contract

Proposed stable response format (illustrative generic placeholders, **not** a benchmark case):

```json
{
  "status": "FAIL",
  "requirements": [
    {
      "name": "requested_calculation",
      "expected": "Required calculation semantics",
      "observed": "SQL calculation semantics",
      "status": "FAIL",
      "evidence": "Specific question and SQL clauses"
    }
  ],
  "issues": [
    {
      "category": "aggregation_logic",
      "severity": "critical",
      "description": "A material, evidence-backed mismatch",
      "evidence": "Observed clause and grounded requirement",
      "suggested_action": "Reconsider the calculation"
    }
  ],
  "feedback": "Check the diagnosed calculation and regenerate the query.",
  "needs_more_evidence": false
}
```

Per-requirement status supports `PASS`, `FAIL`, `UNCERTAIN`, `N/A`. Overall `ERROR` may include a separate error descriptor; an empty `issues` list does not by itself establish PASS. Enforce parsing, known enums, evidence presence for FAIL, safe content lengths and reviewer/provider failure states. Unknown or missing usage fields are `null`, not silently zero. An optional confidence number is diagnostic only and **never** replaces documented evidence.

The Reviewer is a *diagnostic component*: it cannot inject an unreviewed replacement query into the final prediction.

## 12. Full-B0 feedback loop and safe termination

**First attempt:** Invoke existing B0 with unchanged user question/evidence, prompt variant and provider/model. Keep the original BIRD input record immutable.

**On candidate:** Extract the actual final SQL from `run_one()`; retain original B0 report, timestamps, observed token usage and SQL tool calls. Run safe final-SQL checks and Reviewer.

**On FAIL:** Construct an **attempt-local copy** of the input, preserving the original question/evidence, with a separately delineated prior-SQL/diagnosis block. Instantiate a **fresh B0 agent**. B0 itself investigates and regenerates SQL.

**On PASS:** Return that candidate as provisionally accepted. **On UNCERTAIN:** bounded targeted investigation if useful; otherwise record `unverified`. **On ERROR:** record tool/provider/parsing failure and stop or retry under an explicit separate error policy. Do not pretend to have reviewed a candidate.

**Termination:** Maximum attempts, no final SQL, unsafe final SQL, no-progress repeated candidate/feedback, aggregate resource exhaustion or infrastructure failure. Never submit unsafe SQL. If no candidate passed review, a *safe and executable* candidate may be retained for independent scoring as `unverified`; otherwise set `predicted_sql` to `null`. Track final decision and stop reason separately from scoring result.

**Proposed initial settings, not validated optima:**

| Setting | V1 proposal |
| --- | --- |
| Total complete B0 attempts | 3 (one initial + two repairs) |
| Reviewer decisions | Up to 3 |
| Reviewer provider/model | Same configured provider/model as B0 initially, independently configurable later |
| B0 per-invocation middleware limits | Unchanged |
| Outer per-question budget | New aggregate caps across all B0 and Reviewer invocations; exact numeric calls/tokens to be selected before paid inference |
| No-progress | Stop repeating identical/substantially unchanged SQL and feedback without new evidence |
| Retry on failure | Evidence-backed FAIL only; bounded targeted UNCERTAIN and infrastructure policies are distinct |

Fresh B0 invocations are simple and reproducible but can repeat schema work. Record and disclose this overhead; do not secretly grant unlimited retries.

## 13. Proposed implementation files and artifact contract

**Project root:** Run commands from the group repository root.

| Path | Future action | Responsibility |
| --- | --- | --- |
| `scr/agents/self_reflection_agent.py` | NEW | `SelfReflectionAgent` coordinator, history, review/repair loop and aggregate limits |
| `scr/agents/sql_reflection_reviewer.py` | NEW | `SQLReflectionReviewer`, deterministic validation and independent semantic review |
| `scr/cli/run_bird_self_reflection_eval.py` | NEW | Opt-in infer/score/compare/visualize runner, manifests and trace output |
| `tests/test_self_reflection_agent.py` | NEW | B0 orchestration, retries, safe-stop |
| `tests/test_sql_reflection_reviewer.py` | NEW | Structured decisions, grounding, tool/error behavior |
| `tests/test_self_reflection_eval.py` | NEW | CLI and EX scorer/manifest compatibility |
| `docs/self-reflection-agent.md` | THIS DOCUMENT | Architecture, rubric and reproducible implementation specification |
| `scr/evaluation/bird.py` | MINIMAL FUTURE EDIT ONLY IF NEEDED | Register `SelfReflection` as a valid variant; do not change EX logic |

**Do not modify existing B0 files.** The new runner should reuse `scr.cli.run_bird_b0_eval` selection and prediction conventions, `scr.cli.evaluate_bird` and `scr.evaluation.bird` scoring, and existing trace viewer capabilities where compatible. No new framework or duplicate dataset installer/evaluator is needed.

Historical proposed opt-in CLI (now implemented): `uv run python -m scr.cli.run_bird_self_reflection_eval` with `infer`, `score`, `compare`, `visualize` subcommands. Preserve dataset root, selection ID, split, run ID, model/provider, reasoning effort and result-root semantics. At the time of this design draft these commands were planned; the current source implements them (see Section 17).

```text
scr/evaluation/result/SELECTION_ID/
  B0/                                    # preserved baseline
  SelfReflection/
    dev/RUN_ID/
      inference_manifest.json
      predictions.jsonl
      traces.jsonl
      reflection_decisions.jsonl
      scores/
        summary.json
        per_question.jsonl
        report.md
      comparison_report.md
```

Predictions must remain compatible with the existing evaluator's `question_id`, `db_id`, and `predicted_sql` contract. Per-attempt traces include candidate SQL, review criteria/results, evidence, feedback, provider/model, total calls, SQL executions, input/output/cache/reasoning tokens when observed, latency and termination status. The manifest freezes dataset revision/hash, selection IDs, code revision, prompt/reviewer version, model/effort, budgets, and result hashes. Refuse accidental overwrites; reconcile model labels with actual provider configuration, not hard-coded B0 defaults.

## 14. Future offline testing and implementation acceptance

| Stage | Planned work | Acceptance |
| --- | --- | --- |
| Baseline contract inspection | Freeze source commit, verify existing B0 and SQLite/evaluator interfaces | B0 code and tests unchanged |
| Reviewer | Build deterministic final-SQL check, semantic rubric, parser and targeted inspection | Correctly distinguish PASS/FAIL/UNCERTAIN/ERROR |
| Coordinator | Invoke complete B0, route diagnosis, fresh B0 retry, safe stop | No direct reviewer SQL rewriting or input mutation |
| Budgets/trace | Cumulative limits, no-progress guard, per-stage usage and logs | Finite attempts, explicit stop reasons |
| CLI/scorer | Opt-in independent runner and frozen selection/manifests | Existing strict EX scorer accepts artifacts |
| Offline fixtures | Synthetic read-only SQLite and mocked model/reviewer | Agent logic, safety, review errors and regressions covered |
| Delivery | Docs, focused private commit and review | No paid benchmark or historical run mutation during build |

Required tests: initial correct candidate PASS without retry; evidenced wrong aggregation/filter/join/grain/temporal/output FAIL; Reviewer incorrectly flags a valid candidate (false positive); Reviewer overlooks a defective candidate (false negative); empty/truncated result; unknown value semantics; malformed structured output; final SQL syntax/alias failures; SQL read-only safety; provider timeout; budget exhaustion; repeated unchanged candidates; Gold/reference isolation; B0 behavior unchanged.

**Development milestone ≠ benchmark completed.** Do not automatically run the full 500-question inference as part of implementation.

## 15. Later paired evaluation and research context

Evaluate unchanged **B0** against **Self Reflection Agent** on the **same pinned Mini-Dev 2026 SQLite revision**, matching question IDs/split, evidence policy, model/provider and disclosed compute budgets. Record strict EX (whole-result agreement), final SQL rate, corrected and regressed paired cases, Reviewer false positives and negatives, database/difficulty/category breakdowns, model/tool/SQL calls, observed tokens and latency. Reviewer classification quality must be checked by independent offline scoring and/or human semantic adjudication, not by its own confidence.

**Generalized lessons from prior research:** Semantic mismatches can survive successful execution; extra unsupported restrictions can silently narrow a population; joins and aggregation can change counting grain; additional investigation can fix some questions and regress others; compute budgets can strongly confound comparisons. These are *general validation principles*, not per-question prompt rules.

The latest archived Metadata Discovery V2 evaluation with descriptions reports **340/500 EX (68.0%)** against historical generalized-v1 B0 **319/500 (63.8%)**, with **89 corrected / 68 regressed** paired results, **9.11× observed input tokens** and **5.86× observed inference time**. This is **not** evidence that a Reflection Reviewer causes a gain, nor a description-only or budget-matched causal comparison. These aggregate observations motivate safeguards, not question memorization.

Sources (research-only; **never provide these artifacts to inference-time tools or prompts**):

- [Metadata Discovery V2 archive and limitations](../evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md)
- [Metadata Discovery V2 aggregate resource comparison](../evaluation-results/metadata-discovery-v2-descriptions-20261111/analysis-report/b0-resource-comparison.json)
- [BIRD Mini-Dev dataset version and pinned revision](bird-dataset-versions.md)
- [B0 workflow](bird-b0.md) and [EX scoring](bird-evaluation.md)

MKE/Metadata Discovery V2 is a **separate research variant**. Combining it with Self Reflection would require another separately controlled experiment, not a silent change to this V1 design.

## 16. Open decisions and revision record

**Still open before paid experiment:** Reviewer metadata/context-size policy; whether to allow a second targeted investigation on UNCERTAIN; exact aggregate model/tool/token limits; candidate-equivalence/no-progress detection; fallback selection when multiple safe unverified candidates exist; calibration of review false positives; matched-compute control design.

**Decision history**

- **Original concept:** Independent Validator after complete B0, with failed review returning to full B0.
- **Isolation decision:** Implement a separate agent; never modify B0 merely to integrate reflection.
- **Final naming:** **Self Reflection Agent**; reviewer `SQLReflectionReviewer`; experiment variant `SelfReflection`.
- **Rubric decision:** Adopt ten generalized criteria and evidence-backed PASS / FAIL / UNCERTAIN / ERROR.
- **Generalization correction:** Do not place individual BIRD question IDs, specific benchmark mistakes, gold SQL/results, or known corrections into Reviewer prompts. Use only generalizable semantic/structural instructions.
- **Historical V1.1 documentation milestone:** Initially, this document contained design decisions only. Section 17 now records the later implementation. Live inference, full-project tests and measured EX improvement remain unverified.

**Related design record:** [Self Reflection Agent Notion draft](https://app.notion.com/p/415ce09ce40c81f9b308e898d523f161). The Notion page is an architectural planning source, not a source of model-visible gold labels.


## 17. V1 implementation and usage (12 November 2026)

**Implementation state:** New \`SelfReflectionAgent\`, \`SQLReflectionReviewer\`, a versioned generalized reviewer prompt, a standalone evaluation CLI and three offline regression test modules are now present in this private repository. The original B0 baseline source/prompt/runner are unmodified. The BIRD strict EX scorer has only a new allowed variant, \`SelfReflection\`; its scoring algorithm is unchanged.

**Validation limits:** 17 targeted synthetic-SQLite/fake-model/CLI tests passed in an isolated local workspace using lightweight shims for the unavailable project dependencies. All new Python modules compiled. This is **not** a full project/environment regression test: the dependency-resolved \`uv\` suite and real provider calls were **not** executed here. No Mini-Dev EX accuracy or performance improvement is claimed.

### How the implementation works

1. The first B0 invocation uses the original question and evidence, unchanged. Its \`run_one()\` output supplies the actual final candidate SQL.
2. The Reviewer checks that exact SQL through \`ReadOnlySqlite.execute()\`, a bounded read-only compilation/execution gate. Confirmed SQL failures produce evidence-backed FAIL without an LLM call. Successful execution alone does not prove semantic correctness.
3. An independent model checks the ten generalized rubric dimensions, returns strict structured JSON and may request up to two targeted read-only inspections (limited to \`list_tables\`, \`inspect_table\`, \`execute_sql\`).
4. A supported FAIL with actionable feedback triggers a **fresh full B0** attempt. Feedback is put in an **attempt-local evidence block**, since B0's unchanged \`make_prompt()\` consumes only \`question\` and \`evidence\`. The original dataset row and question text remain unchanged.
5. PASS accepts provisionally. UNCERTAIN, ERROR, repetition and exhaustion stop safely. A previously read-only executable candidate can remain \`unverified\`; otherwise \`predicted_sql\` is null.
6. By default, at most three B0 attempts, two review model calls per candidate, two targeted inspection calls per candidate and three reviewed candidates. Outer resource ceilings reserve each unchanged B0's worst-case configured middleware allowance before starting an invocation. Calls not observed by the original B0 tracing hooks cannot be represented as fully measured usage.

### Commands (run from the project root)

Create/select a dataset selection using the unchanged B0 CLI. For a pinned Mini-Dev 2026 installation, use an existing selection with the same \`--dataset-root\` and \`--selection-id\` on all actions:

\`\`\`bash
# A pre-existing BIRD Mini-Dev 2026 selection is required.
uv run python -m scr.cli.run_bird_self_reflection_eval infer \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id minidev2026-full --split dev --run-id sr-dev-001 \
  --provider nvidia --model nvidia/nemotron-3.5-super-vl-120b-a12b \
  --prompt-variant generalized-v1

uv run python -m scr.cli.run_bird_self_reflection_eval score \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id minidev2026-full --split dev --run-id sr-dev-001

uv run python -m scr.cli.run_bird_self_reflection_eval visualize \
  --selection-id minidev2026-full --split dev --run-id sr-dev-001

# Compare ONLY when a B0 run has already been scored on the same
# dataset, selection, model/provider, and B0 prompt configuration.
uv run python -m scr.cli.run_bird_self_reflection_eval compare \
  --dataset-root data/bird/mini-dev-2026 \
  --selection-id minidev2026-full --split dev --run-id sr-dev-001 \
  --baseline-run-id BASELINE_RUN_ID

# Offline project test suite (requires project dependencies):
uv run python -m unittest discover -s tests -t . -v
\`\`\`

**Credentials:** Supply the provider credential through environment variables as in the B0 tutorial, never CLI args or committed files. The NVIDIA example initiates model calls and is **not** an executed result in this implementation commit. Other providers supported by the shared factory may be selected explicitly.

### Artifacts and reproducibility

The independent output is \`scr/evaluation/result/SELECTION_ID/SelfReflection/SPLIT/RUN_ID/\`, containing \`predictions.jsonl\`, \`traces.jsonl\`, \`reviews/reflection_decisions.jsonl\`, \`inference_manifest.json\` and offline \`scores/\` after scoring. Detailed reviews live in \`reviews/\` so the existing trace viewer does not misread them as duplicate primary runs. The primary trace includes labeled \`reflection_review\` events. No run or score is overwritten, and the scorer alone loads gold SQL during offline evaluation.

**Historical 12 November remaining-work note (subsequently superseded by the 13 November archived benchmark):** Run the dependency-resolved complete project regression suite in the actual HKU repository; validate a real provider inference and full trace UI; then run a separate BIRD Mini-Dev paired benchmark with budgets, token/latency trade-offs, corrected/regressed cases and reviewer misdiagnosis rates. This commit itself does not run a full 500-question inference.
