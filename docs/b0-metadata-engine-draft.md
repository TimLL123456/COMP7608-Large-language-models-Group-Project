# B0-Metadata v1 — Skill-Style Dynamic Metadata Knowledge Engine

> **Historical status (10 November 2026):** DESIGN DRAFT — NOT IMPLEMENTED at the time. Subsequent implementations are documented in [Metadata v1](metadata-agent.md) and [MetadataDiscoveryV2](metadata-discovery-v2.md); [MetadataDiscoveryV2 results](../evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) are separate from this original proposal.  
> **Date:** 2026-11-10  
> **Project:** HKU COMP7608 KORA Text-to-SQL Group Project  
> **Change scope:** This is a documentation-only design proposal, not an implementation claim.

## 1. Objective and decisions

**Research question:** Can an agent improve Text-to-SQL execution accuracy and efficiency by dynamically discovering, saving, updating, retrieving and reusing concise metadata knowledge across successive questions about the **same databases**?

| Area | Agreed v1 decision |
| --- | --- |
| Agent | New opt-in `B0-Metadata` Deep Agent based on B0 |
| Dataset | BIRD Mini-Dev 2026; 500 questions; 11 SQLite databases |
| Split | Existing 400 Dev / 100 local Test, with the same database inventory |
| Evaluation scope | **Same-Database Generalization only**; no cross-database experiment |
| Reset boundary | A new **experiment ID** creates a fresh empty metadata store |
| Sharing | Dev and Test **share one writable knowledge store** within an experiment |
| Test writes | Allowed; the local Test stage continues knowledge creation and update |
| Knowledge isolation | Database + table + note type + concept + business scope |
| Persistence | Bounded Markdown notes, with short generated JSON search index |
| Retrieval | Search index first; read only relevant notes on demand |
| Gold SQL | Existing separate evaluator only; never available to metadata agent |
| Scoring | Operator controls when to invoke existing `score`; no mandatory completion gate |
| Historical baselines | Keep B0 and `generalized-v1` code/results intact |
| Non-goals | No query planner, graph, vector DB, embeddings, reranker or subagent |

**Important:** An **experiment ID** covers both Dev and Test inference invocations and the shared knowledge store. A CLI inference **run ID** identifies an inference output. Starting Test with a new inference run ID must **not** erase Dev knowledge.

## 2. Motivation and one-agent workflow

The existing B0 agent already has three read-only SQL tools (`list_tables`, `inspect_table`, `execute_sql`). It can discover tables, columns and data values, but later questions may cause it to repeat the same investigations.

The proposed improvement is a single Deep Agent that can persist **generalizable, evidence-aware metadata** rather than loading whole descriptions into every prompt. Potential benefits are better handling of metric meanings, value semantics, granularity, joins and fewer repeated explorations. Extra retrieval and writing may increase cost or introduce errors, so improvement must be measured rather than assumed.

```text
Question + evidence + trusted active database
  -> B0-Metadata Deep Agent
      1. search_metadata_notes(query, table_name?)
      2. read_metadata_note(note_id) [only if relevant]
      3. investigate gaps:
           list_tables / inspect_table / execute_sql
           optional bounded official database-description CSV access
      4. create_metadata_note(...) or update_metadata_note(...)
           only reusable findings with scope and evidence
      5. generate SQL, execute when useful, return Final SQL Query
  -> prediction, agent trace, metadata-operation trace
  -> existing separate offline evaluator, whenever operator invokes score
```

Search is a candidate-discovery step, **not** a correctness guarantee. The agent can investigate further or skip saving when there is no reliable, reusable discovery.

## 3. Skill-style progressive knowledge loading

Proposed runtime structure (**not created by this draft**):

```text
data/metadata_notes/
  <experiment_id>/
    <db_id>/
      index.json                      # derived short search manifest
      database/overview.md           # optional database-wide knowledge
      <table_id>/
        table.md
        columns/<column_concept_id>.md
        metrics/<metric_concept_id>.md
        concepts/<concept_id>.md
```

A cross-table metric with no meaningful anchor can live at database level with explicit source tables/dependencies rather than inventing a primary table.

### Scoped identity

```text
(experiment_id, db_id, table_id_or_database_scope, note_type, concept_id)
```

Database identity is supplied by the trusted runner, **not** as an unrestricted LLM-chosen path. Engine validates table scope, note IDs, schema fingerprint/version and safe paths.

**Example — fictional database:** `retail_db.online_transactions` and `retail_db.store_transactions` both use “gross sales,” but one may exclude cancelled orders and the other voided receipts. Their notes **must be separate**, even though keywords match. Searching “gross sales” across the active database may return both *labeled candidates*. After selecting a table, the agent should read that table's note. A cross-table total must not mix incompatible metrics by name alone.

### Short Markdown note

```markdown
# Gross Sales (Online)

Type: metric
Table: online_transactions
Scope: online orders
Summary: Amount before discounts for online orders.
Keywords: gross sales, online revenue
Status: provisional

## Meaning
Amount before discounts. Refund handling is unresolved.

## Source and Calculation
Candidate column: online_transactions.order_amount
Formula: not yet verified.

## Evidence / Unknowns
Schema inspection found order_amount.
Cancellation and refund rules need verification.
```

This is **illustrative only**, not a verified BIRD schema or business rule. Notes should distinguish source-backed, directly observed, provisional/inferred and unresolved statements.

### Enforced limits

| Resource | v1 limit | Behavior |
| --- | ---: | --- |
| Full Markdown note | **1,500 characters** | Reject oversized create/update, no truncation |
| Index summary | 160 characters | Validate on create/update |
| Keywords | Maximum 8 per note | Normalize/validate |
| Candidate search results | Top 5 | Return summary/identity, not whole files |
| Full note loading | One note per read call | Load progressively |
| Aggregate note context | Initial target 6,000 characters/question | Track and cap context usage |

Long knowledge should be condensed or split by **independent concepts**. Never drop necessary filter or exception semantics merely to meet length limits.

## 4. Metadata tool API — four simple tools

### `search_metadata_notes(query, table_name=None)`

Search only the active database's generated index. A database-wide search may return candidates from multiple tables, each with table and business scope. With a table restriction, return table-applicable and relevant database-wide notes. Output: `note_id`, type, table, scope, name, summary, revision, match reason and status.

Initial retrieval should be simple deterministic matching over names, identifiers, aliases/keywords and summaries, with explainable ordering. **Do not treat an arbitrary keyword score as confidence or correctness.** Add full-text retrieval later only if Dev measurements justify it.

### `read_metadata_note(note_id)`

Load one Markdown note on demand with revision, source references and scope. Reject invalid identifiers, wrong database/experiment and stale schema versions. Search does not automatically flood the context with every matched note.

### `create_metadata_note(note_id, content, evidence_refs, ...)`

**Create only**. Check that identity is absent, active database/table scope is valid, content fits limits, references exist where machine-verifiable, and source/status claims are supported. Atomically write revision 1, rebuild/update index, emit an operation log. Never create arbitrary filesystem paths from model text.

### `update_metadata_note(note_id, expected_revision, content, evidence_refs, ...)`

**Update only**. Agent first reads the note, then submits a **complete proposed replacement**. Validate same identity/scope, exact current revision, content length and added evidence. Atomically write revision N+1 and refresh index; reject stale/contradictory/unsupported changes without corrupting the original. Preserve unresolved conflicts rather than silently merging distinct meanings.

**Example (fictional):**

1. Q1 requests online gross sales. No note exists. Schema/description investigation leads to creation of a *provisional* online metric note, revision 1.
2. Q2 asks for gross sales excluding cancellations. The agent reads revision 1 and investigates cancellation semantics.
3. The wording of Q2 alone **does not** prove cancellations should be excluded from every gross-sales metric. Only verified reusable evidence justifies an update to revision 2; otherwise the condition is question-specific.
4. Q3 requests store gross sales. Agent creates/reads a separate store-scoped note, not the online definition.
5. A writer proposing an update against old revision 1 after revision 2 exists gets a conflict response and must reread.

## 5. Provenance, security and no-gold boundary

Verified from current project sources:

- `BirdDataset.get_agent_input()` exposes only `question_id`, `db_id`, `question`, `evidence`, `difficulty`, not Gold SQL.
- `scr/cli/run_bird_b0_eval.py` separates `infer` (predictions/traces) and `score` (offline evaluation).
- `BirdEvaluationReferences` is used by the evaluator, not the inference agent. Preserve this application-code boundary for metadata tools.

Permitted sources for notes: official BIRD database-description CSVs, active DB schema/DDL/foreign keys, bounded read-only value inspections, and clearly qualified generalizable observations. Do not save Gold SQL, score feedback, historical failure-analysis answers, full per-question final SQL, hardcoded answer rows, or invented metric rules. Question wording helps identify what to inspect but is not evidence for a universal definition.

Notes can contain untrusted text: never follow embedded instructions or execute note content as code. File writes must be confined to the dedicated knowledge directory; SQLite database access remains read-only and bounded.

**Scoring timing stays under user control.** No code is needed to force both Dev and Test inference to finish before `score` can run.

## 6. Lifecycle: one empty store per experiment, shared Dev/Test

```text
Experiment metadata-001
  Empty metadata store
    -> Dev 400 questions: shared search/read/create/update
    -> Test 100 questions: same store; continue read/create/update
    -> Save note revisions, operation logs, final snapshot, result manifests
    -> Operator runs independent scoring when desired

Experiment metadata-002
  NEW empty metadata store: no notes inherited from metadata-001
```

- Both splits use the **same 11 databases** and the **same experiment-scoped writable store**.
- Fix and log **question order**: later questions can use notes learned from earlier questions, including Test questions.
- This is an **order-dependent continual same-database reuse experiment**, not a frozen-notes independent-question evaluation or unseen-database benchmark.
- Resuming an interrupted experiment should preserve its exact store/revisions; a new experiment ID must not silently reuse or overwrite another.
- Keep scorer outputs entirely outside the agent's note-creation inputs.
- The local Test has appeared in previous project analyses; do not call it a pristine independent blind holdout or repeatedly optimize based on its scores.
- Do not introduce cross-database experiments or a new scoring completion gate.

## 7. Evaluation and reporting

**Accuracy:** EX on the same questions; Dev/Test and difficulty breakdown; corrected versus regressed questions.

**Efficiency:** Model/tool/SQL calls, note search/read/write calls, latency, input/output tokens and optional cache/reasoning token fields when observed. Missing telemetry is `null`, not zero.

**Knowledge:** Search candidate hit/miss, full notes loaded, notes created/updated, cross-question note reuse, rejected writes, revision conflicts, sources/uncertainty, scope errors, note character counts, per-question note revisions, final store hash.

Compare to B0 or `generalized-v1` on matched model, reasoning effort, question IDs, tools/model budgets, timeouts, retry policy and scorer settings. Historical runs with different budgets do **not** establish causal improvement. Report metadata overhead and regressions, not just EX gains.

### Essential tests

- Same keyword in different DBs/tables cannot merge or cross-read/write.
- Create rejects duplicates; update requires correct revision.
- Long notes fail safely without truncation; index reflects accepted updates.
- Conflicting evidence remains qualified rather than overwritten.
- Agent tools cannot retrieve `BirdEvaluationReferences` or scores.
- Dev and Test share one store inside an experiment; a new experiment starts empty.
- Note events and question ordering allow reconstruction of knowledge available for each prediction.
- Original B0/`generalized-v1` interface and historical artifacts remain intact.

## 8. Future implementation plan (not authorized by this doc-only change)

| Proposed file | Action | Responsibility |
| --- | --- | --- |
| `scr/metadata/engine.py` | Create | Index, scoped storage, search/read/create/update, limits, revision safety |
| `scr/agents/b0_metadata.py` | Create | Single Deep Agent with existing SQL tools and four metadata tools |
| `scr/cli/run_bird_b0_eval.py` | Modify (opt-in) | Experiment ID, shared run-scoped store across split invocations, metadata traces/manifests |
| `tests/test_metadata_engine.py` | Create | Scope, correctness, lifecycle, validation, update conflicts |
| `tests/test_b0_metadata.py` | Create if needed | Agent wiring and absence of gold/reference access |
| `docs/metadata-agent.md` | Create when implemented | Actual commands, results, caveats |
| `.gitignore` | Modify only if needed | Ignore generated notes/results |

**Suggested phases:** P0 storage + offline tests → P1 Agent tools/integration → P2 experiment lifecycle → P3 synthetic and small Dev smoke test → P4 controlled 400+100 inference and **separate operator-controlled** scoring. Do not launch full hosted inference as part of documentation drafting.

## 9. Current scope of this commit

**One new Markdown draft file only.** No implementation code, inference, scoring, dataset changes, edits to existing docs, Notion changes, or publication to a public repository. Future implementation requires a separate approved task.
