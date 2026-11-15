## Concrete failure review and follow-up

All 160 failures are indexed. The following 16 result mismatches were selected for a direct question/evidence/predicted/reference SQL review across databases; they are not a random sample or an exhaustive semantic categorization of all 154 mismatches. Differences below are verified in the saved SQL. Except for compiler diagnostics and the already-scored constant answer, no corrective SQL counterfactual was evaluated.

| Question | Verified difference category | Finding |
| --- | --- | --- |
| 8 | output coverage | Only AdmEmail1 is returned; the request and reference unify all three administrator email fields. |
| 15 | row scope | The reference constrains SAT rows to rtype=S; the prediction omits this row-type condition. The text difference is verified; no single-change counterfactual was scored. |
| 40 | unsupported cohort restriction | The prediction adds School Type=High Schools (Public), narrowing a request covering regular non-charter schools; it also differs in code matching and FRPM share derivation. |
| 70 | value semantics | The prediction fixes frameVersion=future and returns that label; the reference computes the maximum numeric frame-version year. |
| 91 | unsupported cohort restriction | The prediction adds rarity=common even though the requested printing population is determined by pauper legality and paper availability. |
| 115 | wrong output measure | The prediction returns totalSetSize as the third column rather than the count of official translation languages. |
| 162 | ungrounded constant answer | The final prediction is SELECT 0 instead of deriving the requested count from customers and yearmonth. The stored EX confirms the constant is wrong. |
| 193 | temporal snapshot | The prediction uses only player-attribute rows dated July 12; the question explicitly requires all players with their latest ratings in force on that date. |
| 221 | unsupported cohort restriction | The prediction narrows withdrawal operations and standing orders to selected operations and SIPO; neither restriction appears in the request/reference. |
| 249 | table choice and result grain | The prediction orders results.fastestLapTime rows and takes 20 rows; the reference uses lapTimes, aggregates each driver minimum, and selects 20 drivers. |
| 304 | distinctness across groups | Summing distinct attendees per event can count a member repeatedly across multiple events of the same type; the reference counts distinct members per event type. |
| 344 | entity confusion | Strength attribute membership is used to identify heroes instead of membership in the Super Strength superpower. |
| 384 | age boundary | The prediction uses a 51-year cutoff; the reference uses Birthday < 1976-10-09 for older than 50 on the stated date. |
| 411 | patient versus visit grain | The prediction divides examination-row counts; the reference divides distinct patient counts. |
| 431 | extra output column | The prediction adds a total-patients column and returns three columns; the request/reference require two laboratory-related counts. |
| 483 | benchmark output representation | The prediction labels bond types single/double/triple while the reference returns encoded bond symbols. This is a strict EX representation mismatch; the wording permits a semantic ambiguity and is not proof that the plain-English labels are useless. |

These cases show recurring output-contract errors, unsupported extra filters, temporal cohort errors and incorrect counting grain. Restored descriptions can explain columns and encoded values, but they do not guarantee that C1 obeys the requested population, time scope, grouping or projection. No claim is made that a particular note caused these errors.

Four final SQL statements fail SQLite compilation:

| Question | SQLite compiler error | Final SQL present in observed execute_sql arguments |
| --- | --- | --- |
| 66 | no such column: t.translation | False |
| 201 | unrecognized token: "1997.0_total" | False |
| 219 | 1st ORDER BY term does not match any column in the result set | False |
| 73 | 1st ORDER BY term does not match any column in the result set | False |

Q66 references t.translation after its derived table projected only setCode; Q201 has unquoted numeric-leading aliases and invalid numeric identifier tokens; Q219 orders a compound SELECT by an expression not projected as an output column; Q73 references releaseDate outside the projected compound-result columns. A final read-only EXPLAIN gate on the exact returned SQL would catch these syntax/name-resolution defects. This recommendation has not been implemented and its net EX effect has not been measured.

Primary actionable changes supported by the review: (1) check the requested output columns and units before finalizing; (2) reject unrequested cohort restrictions unless grounded in the question; (3) explicitly track entity/counting grain and whether distinctness spans the whole requested group; (4) distinguish as-of snapshots from same-day updates; (5) compile the exact final SQL; (6) add bounded retry/backoff for transient provider overload, preserving attempts and usage. These would require a separate reviewed code change and evaluation; this run remains unchanged.

## Resource tradeoff against generalized-v1 B0

| Measure | B0 total (n) | Metadata Discovery V2 total (n) | Ratio |
| --- | --- | --- | --- |
| model_calls | 3043 (500) | 14422 (500) | 4.739 |
| tool_calls | 3677 (500) | 22156 (500) | 6.026 |
| sql_calls | 1689 (500) | 4282 (500) | 2.535 |
| input_tokens | 12795143 (500) | 116588268 (500) | 9.112 |
| output_tokens | 233182 (500) | 1997321 (500) | 8.566 |
| cached_input_tokens | 6723200 (500) | 37872128 (500) | 5.633 |
| reasoning_tokens | 0 (500) | 0 (500) | n/a |
| latency_ms | 12599540.0 (500) | 73864826.0 (500) | 5.863 |

Against the matched historical generalized-v1 B0, EX rises by 21/500 = 4.20 percentage points, with 89 corrected questions and 68 regressions. The comparison is historical rather than randomized; resource and workflow changes are confounded. Separate per-split paired reports are comparison-b0-dev.md and comparison-b0-test.md. The earlier 58.8% B0 differs by +9.2 percentage points; historical Metadata v1 at 65.2% differs by +2.8 points, without available per-question v1 artifacts for a new paired audit.

## Completion checks and export recovery

All 500 prediction IDs and 500 matching traces were checked against their exact ordered selections, with 400 Dev/100 Test scores. The scorer prints SMOKE SUBSET ONLY because this runner passes explicit question IDs; exact set/count validation confirms these are the complete splits. This is a misleading generic log label, not evidence of sampling.

The standard Dev Trace Explorer export hit its default 50 MiB input cap (Dev trace approximately 58 MiB). export_traces.py called the same viewer.write_html with a process-local, bounded 100 MiB cap for these verified local files. Both complete HTML explorers were generated. Original traces and repository code remain unchanged; the initial failed export log and successful recovery log are retained. The Test export used the same bounded process configuration.

Deep Agents also emits built-in filesystem tools such as grep, read_file and edit_file. The inspected installed create_deep_agent implementation defaults to StateBackend(), an agent-state virtual filesystem; the project passes no host filesystem backend or gold files. These calls are accounted for in tool counts and do not establish access to host gold SQL. No gold was supplied to inference.

Reported model calls count observed A1/C1 AI messages plus B1 invocations. Provider failures before an AI-message observer event can be absent from A1/C1 counts. Token totals are observed usage and therefore lower bounds for any unreported failed calls; B1 has one invocation with no usage. The per-call coverage ratio alone does not recover usage for those failed streams. Costs remain unavailable.

Additional evidence: sql-error-diagnostics.json, b0-resource-comparison.json, comparison-b0-dev.md, comparison-b0-test.md, trace-export-recovery.log, export_traces.py and execution-status.json.
