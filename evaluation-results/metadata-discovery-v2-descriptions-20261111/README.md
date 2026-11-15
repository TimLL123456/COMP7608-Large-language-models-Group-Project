# Metadata Discovery V2 with restored BIRD descriptions — Mini-Dev 2026

| Split | Correct | Questions | EX |
| --- | ---: | ---: | ---: |
| Dev | 272 | 400 | 68.00% |
| Local Test | 68 | 100 | 68.00% |
| Overall | 340 | 500 | 68.00% |

This is the complete `metadata-discovery-v2-descriptions-20261111` experiment on the prepared `metadata-discovery-v2-resource-full-20261111` selection. It used `metadata-discovery-v2`, `chatgpt-siwc`, `gpt-6-luna`, reasoning effort `none`, and `generalized-v1`. Global model/tool/SQL limits were 120/200/80; A1 model/tool limits were 20/40 per attempt, with at most three attempts. Source inference code was commit `465bde31b67c6fb01d9ffbba7fec665a23d63a01`.

Dev began with an empty knowledge store. Test used the same writable store after Dev. This is a local, continual, same-database evaluation, not official hidden Test or unseen-database generalization. Gold SQL was reserved for the scorer and offline review.

The 160 failures comprise 154 result mismatches, four SQL execution errors and two missing SQL answers after provider overload. The final store contains 572 notes, with no detected orphaned files, missing index entries or hash inconsistencies.

Against historical generalized-v1 B0, the net gain is **21 correct answers (+4.20 percentage points)**: 89 improvements and 68 regressions. Observed input tokens increased 9.11 times and recorded inference time 5.86 times. Description availability, budgets, workflow fixes, model-service timing and knowledge history are confounded; this is not evidence of a description-only or budget-only improvement.

## Read the results

- [Complete performance report](performance-report.md): accuracy by split, difficulty and database; A1/B1/C1 behavior; resources, errors and limitations.
- [Failure review](analysis-report/failure-review.md): 16 directly reviewed result mismatches and four compiler diagnostics. This is selected review, not an exhaustive semantic classification of every mismatch.
- [All-failure inventory](analysis-report/failure-inventory.csv) and [SQL-difference review](analysis-report/failure-semantic-review.csv): the tracked SQL-difference file omits the evaluator-only gold SQL column.
- [Dev](dev/scores/summary.json) and [Test](test/scores/summary.json) scoring summaries.
- [Resource comparison](analysis-report/b0-resource-comparison.json) and paired [Dev](analysis-report/comparison-b0-dev.md)/[Test](analysis-report/comparison-b0-test.md) comparisons. EX differences in those source reports are percentage-point differences.
- [Reproduction instructions](reproduce.md), [source receipt](provenance/archive-receipt.json), and [local artifact receipt](provenance/local-artifacts.json).

## What is preserved

The archive contains all 500 predictions, inference manifests, independent scores, analysis, restored-description provenance, selected execution logs, all 572 final notes and indexes, and the metadata-operation history. Original inference/scoring/knowledge files were copied without modification; the receipt identifies the portable report edits and removal of the gold SQL column. Archived manifests may contain original absolute paths, retained as provenance rather than runnable commands.

`knowledge/` contains the original database note directories plus `knowledge_operations.jsonl`. The original experiment kept the operation log beside its `knowledge/` directory. When independently checking its snapshot, hash only the database note/index directories, excluding the relocated operation log. Do not treat this archive as an inference checkpoint or resume it.

Raw traces, generated HTML explorers, databases, description CSVs, the downloaded official package, credentials, caches and temporary controllers remain local. Their relevant paths and hashes are in the local artifact receipt. A Git-only clone can inspect all saved predictions/scores/knowledge and rescore with the matching dataset, but cannot reconstruct the original detailed Trace Explorers without the retained local raw traces or fresh inference.

The official legacy package required two documented adaptations: removing a nonexistent `formula_1.constructors.wins` row and supplying schema-only columns for `toxicology.element` from the pinned official 2026 schema. No semantic descriptions were invented for those two columns. All original dataset hashes were preserved.

The source full-run artifacts were frozen before the portable restoration helper and this archive were added. `provenance/final-validation.json` describes that source snapshot, not the later archiving commit. The portable helper was verified against the existing restored dataset without rewriting it; its tests and verification are also retained under `provenance/`.

Run `sha256sum --check checksums.sha256` from this directory to verify the archive. No new inference or replacement predictions were created while packaging these results.
