# Rubric self-reflection full evaluation

Source commit: `928636c6e9e7c4e4056fca615709c77644c07ffc`. Provider: `chatgpt-siwc`; model: `gpt-6-luna`; reasoning: `none`; B0 prompt: `generalized-v1`. Original default agent budgets were used; split manifests record all limits and prompt hashes.

| Split | Correct | Total | EX |
| --- | ---: | ---: | ---: |
| Dev | 255 | 400 | 63.75% |
| Test | 71 | 100 | 71.00% |
| Overall | 326 | 500 | 65.20% |

All 500 final SQL queries executed in the offline scorer. EX compares their result sets with reference SQL results; reviewer PASS is a separate provisional judgment. Previous SelfReflection achieved 350/500 (70.0%): 38 questions corrected and 62 regressed. This is not a matched-compute causal comparison.

24 dev questions affected by DNS failures were rerun with unchanged source and settings, then their predictions, traces and review records replaced. Original predictions and retry provenance are retained. This is not a strictly single-pass result. Usage totals describe retained records and exclude replaced failed attempts.

`dev/` and `test/` contain final predictions, independently computed scores, paired comparisons, manifests, and gzip-compressed traces/reviews. `inputs/` contains inference inputs without gold SQL. The selection manifest pins the existing local BIRD Mini-Dev 2026 dataset, which is not bundled. This is a 500-question local selection, not the official hidden BIRD test.

To inspect traces, decompress `traces.jsonl.gz` and `reviews/rubric_decisions.jsonl.gz`. Original manifest hashes refer to decompressed contents. Absolute runtime paths are historical provenance. See the source agent CLI documentation for rerunning inference and scoring with the archived inputs and selection manifest.
