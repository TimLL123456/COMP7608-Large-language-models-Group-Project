# Luna/Terra role-specialized full evaluation

| Split | Correct | Total | Execution Accuracy |
| --- | ---: | ---: | ---: |
| Dev | 321 | 400 | 80.25% |
| Test | 80 | 100 | 80.00% |

The frozen BIRD Mini-Dev 2026 local selection contains 400 Dev and 100 Test questions. This is not the official hidden BIRD Test. Execution accuracy compares result sets; reviewer PASS is a separate judgment.

Generator/investigator: `gpt-6-luna`. Reviewer: `gpt-6.1-terra`. Both use `chatgpt-siwc`, provider-default reasoning effort, and the `generalized-v1` prompt. Original default budgets are recorded in `provenance/inference_config.json`. The completed run used one sequential 500-question shard.

## Recovery and provenance

Run ID: `luna-terra-sequential-20261115T150108Z`; selection ID: `sr-full-20261113`. The first 107 retained records were generated at commit `78f19dfd68224b0259fcc105d342a217f3b959c8`. SIWC limits interrupted the original run after 109 saved records. Recovery at `3aaa618077debceccb0d84c7c67399f0d044ce6f` preserved positions 1–107 byte-for-byte, replaced reviewer-error positions 108–109 (question IDs 131 and 133), and generated positions 110–500 in place. Both replaced records are archived under `provenance/replaced-records/`. The complete original backup remains locally preserved.

The legacy interrupted run had no original configuration manifest; its launch command verifies prompt and budget settings, while recovery validates saved identities and selection. This is a resumed, mixed-revision result, not a single uninterrupted pass. The earlier failed parallel experiment is excluded.

## Missing SQL

Question 466 (Dev): final output contained an unquoted apostrophe in an alias; output validation rejected it and forced finalization produced no accepted SQL. Question 73 (Test): the generated candidate timed out after 300 seconds during reviewer execution and was ineligible as a safe final fallback. Both count as incorrect in the scores. Neither retained trace shows the prior SIWC usage-limit error. Test results were not used to tune prompts or configuration.

## Contents and verification

`dev/` and `test/` contain predictions, independently calculated scores, inference manifests, Trace Explorers, and gzip-compressed traces/reviews. `inputs/` contains the original public inference inputs without gold SQL; the selection manifest pins dataset provenance. Database files and credentials are not bundled.

`performance-summary.json` reports tokens, calls, latency, review counts and regeneration. Usage covers retained records only and excludes replaced or unsaved failed calls; summed question latency is not total wall-clock time. No monetary cost is inferred.

`checksums.sha256` covers the packaged files. Runtime manifest trace/review hashes refer to decompressed JSONL contents. Historical absolute paths are retained as provenance. For reproduction, use the role-specialized CLI documentation with a local copy of the pinned dataset and this frozen selection; use fresh output directories. Source revisions and original/recovery commands are under `provenance/`.
