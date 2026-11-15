# Metadata Discovery V2 — A1/B1/C1 Research Workflow

## Architecture and implementation

**Status (15 November 2026):** Opt-in implementation available as `MetadataDiscoveryV2`. The [11 November BIRD Mini-Dev 2026 full experiment](../evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) achieved **340/500 (68.00%) local strict EX**, versus historical generalized-v1 B0 **319/500 (63.80%)**. The +4.20 percentage-point descriptive difference does **not** isolate the metadata contribution because budgets, description availability, workflow and history differ.
v1 stays the default. Metadata Discovery V2 has its own MetadataDiscoveryV2 result and
experiment directories. Do not reuse a v1 experiment ID or v1 notes to
claim a new, empty metadata-discovery-v2 experiment.

The graph uses langgraph StateGraph with the following nodes:

- **A1 discovery (up to three visits including the first):** search and read
  relevant notes, inspect schema and values, and create/update definitions
  when evidence supports a reusable fact. Every visit logs an explicit
  decision: created, updated, reused, no_note, insufficient_evidence,
  decision_missing or decision_inconsistent.
- **B1 sufficiency evaluator:** one JSON model judgement per attempt,
  checking relevant table purpose, granularity, columns, value meanings,
  joins, filters and output granularity. Insufficiency returns a targeted
  list of missing information for the next A1 visit.
- **C1 SQL agent:** the pre-existing B0 SQL harness and read-only SQLite
  tools. Receives A1 findings marked provisional/untrusted, generates
  the same Final SQL Query format, and retains the same SQL safety guard.
- **Exhausted:** after three unsuccessful A1/B1 cycles, or if B1 provides
  no actionable missing information, stops without inventing SQL.

**The sufficiency decision is relative to the current question.**
An unrelated column does not need a complete definition before C1 can run.

### Knowledge schema

One table-definition note per exact (db_id, table_name); four ordered sections:

1. Business Summary — purpose and business information represented
2. Business Use Cases — useful analyses and restrictions
3. Data Granularity — what a row represents; do not assume uniqueness
4. Data Scope & Exclusions — verified inclusions/exclusions and unknowns

One column-definition note per exact (db_id, table_name, column_name);
four ordered sections:

1. Business Meaning — business interpretation
2. Business Usage — grouping, filtering, reporting, calculations and caveats
3. Value Meaning — units, codes, flags, NULL and other special values;
   N/A if no special interpretation applies
4. Calculation Meaning — derivation for computed columns; N/A for
   pass-through/source columns; Unknown if derivation is unverified

All sections must appear, in that order, as Markdown headings prefixed
with two hash signs. If information is unknown, write Unknown / Not verified,
not a fabricated business definition. Source references must be present.
All new metadata-discovery-v2 notes stay provisional; the engine verifies format,
identity, source-reference syntax, revision and length, **not** the semantic
truth of every natural-language sentence.

Metadata Discovery V2 uses only table/column note writes. The older general-purpose
v1 metric/concept notes are not migrated or deleted. A column note's
concept_id is its exact schema column name, even when that name contains
spaces or unusual characters; storage paths still use opaque SHA note IDs.

### Run Metadata Discovery V2 with a NEW experiment ID

Run the original B0 prepare step as documented above, then:

~~~powershell
uv run python -m scr.cli.run_bird_metadata_eval infer \
  --workflow metadata-discovery-v2 \
  --selection-id metadata-full-001 \
  --dataset-root data/bird/mini-dev-2026 \
  --split dev --run-id metadata-discovery-v2-dev-001 \
  --experiment-id metadata-discovery-v2-001 \
  --provider chatgpt-siwc --model YOUR_EXISTING_MODEL \
  --prompt-variant generalized-v1
~~~

Repeat for split test and a different run ID, using the SAME metadata-discovery-v2
experiment ID, provider/model and other configuration settings.

For optional scoring, use the same score command but add
--workflow metadata-discovery-v2. For visualization add --workflow metadata-discovery-v2.
The evaluator recognizes the MetadataDiscoveryV2 variant but uses the same
SQL execution-accuracy algorithm; historical Metadata/v1 and B0 results
are untouched.

Metadata Discovery V2 supports the same strict, conservative --resume audit, using
its own run and store paths. Partial-question metadata activity causes
resume rejection; never bypass this check.

### Budget / traces

Metadata Discovery V2 now uses independent question-wide hard ceilings of **120 model calls,
200 total tool calls and 80 SQL executions**. Historical B0 and Metadata v1
retain their original **40/40/40** settings. The larger Metadata Discovery V2 limits are
safety ceilings, not consumption targets.

A1 retains at most **3 visits**, each allowing **20 model calls, 40 tools and
20 SQL inspections** (at most 60/120/60 over three visits). At least **30 model,
40 tool and 20 SQL calls** remain reserved for C1, with additional global
headroom. B1 uses up to one model decision per visit, and counts against the
same global budget. If A1 reaches its visit or reserved-resource limit, B1
hands off accumulated findings and explicit missing information to C1 rather
than unconditionally stopping at knowledge_exhausted. C1 still may decline
unsupported SQL. To reduce premature middleware errors, A1 is instructed
to finalize its structured discovery decision before reaching the ceiling.

Metadata Discovery V2 metadata reads allow **20,000 unique note characters per question**.
Repeated reads of the same note revision do not charge this character
allowance again; repeated tool calls still count as calls and token usage.
Automatic full-note preloading on every A1 attempt was removed. The legacy
Metadata v1 context allowance remains 6,000 characters.

Metadata Discovery V2 metadata writes use a per-database in-process mutex covering the
complete index read–modify–write operation, plus a portable filesystem
write marker to **fail closed** on simultaneous cross-process writers or
interrupted writes. The engine checks notes/index consistency before mutations;
it never silently repairs or deletes orphaned notes. Preserve historical run
artifacts and investigate any integrity or resume rejection. Do not resume
the previously rejected partial-question checkpoint.

Experiment manifests now record the effective limits; traces record A1
allocations/usage and the B1-to-C1 fallback. A new experiment ID is necessary
for comparison with previous Metadata Discovery V2 results.

Trace events identify their node and knowledge decision. Each question
reports a1_attempts, b1_evaluations, knowledge_decisions, and node_metrics
in its report, and the original predictions/trace format is preserved.
The B1 strict JSON parser is provider-agnostic, but real-provider format
compliance needs an integration smoke test. The existing B0 trace observer
is reused for A1 and C1; JSON A1 answers are not counted as final SQL.

### Testing and interpretation

Run offline tests:

~~~powershell
uv sync
uv run python -m unittest tests.test_metadata_discovery_v2_workflow \
  tests.test_metadata_discovery_v2_cli \
  tests.test_metadata_engine tests.test_metadata_agent \
  tests.test_metadata_resume -v
~~~

Start with a tiny Dev selection to confirm actual agent note creation,
cross-question reuse, A1/B1 routing and tool counters, then use a fresh
full 400-Dev/100-Test experiment. Compare under matched model, prompt,
budget and question order. Repeated notes and increased context can make the workflow more expensive; the archived experiment measured increased observed token usage and inference time. Do not infer a causal quality gain from the unmatched historical comparison.

The Metadata Discovery V2 implementation currently uses the langgraph version
already present in the project's uv.lock as a dependency of Deep Agents;
no pyproject/lockfile changes were needed for this opt-in implementation.

