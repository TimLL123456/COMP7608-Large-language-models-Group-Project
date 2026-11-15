# Reproduction and provenance

Start from the Group Project root. Follow docs/bird-b0.md to verify the pinned Mini-Dev2026 dataset, sign in to the explicitly authorized SIWC account, prepare all500 questions with seed42 and original400/100 split, infer only generalized-v1 with gpt-6-luna / effort none / preview20, then score each split. Use fresh selection/run IDs. The current source sets40 model /40 shared total tool /40 SQL calls; SQL and model-request timeouts are300s. No API-key provider fallback. New inference consumes quota and can yield different SQL.

For offline rescoring of this archive, run `uv run python -m scr.cli.evaluate_bird --variant B0 --split dev --dataset-root data/bird/mini-dev-2026 --predictions evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/dev/predictions.jsonl --output-dir results/generalized-v1-rescore --run-id dev`. Repeat for test with test paths and a fresh run-id. Omitting --question-ids lets the evaluator report full-split coverage. Do not overwrite archived scores.

Q60 initial HTTP504 attempt and replacement are documented in q60-rerun-receipt.json. Final500-result token totals exclude that initial attempt; analysis-report/metrics.json separately includes its recorded usage in501-attempt totals. Failed HTTP requests can have missing usage; costs remain unknown.

## Local traces

The full500-question structured traces, case HTML pages and offline trace explorer are preserved in the original local output folder `outputs/b0-generalized-v1-40calls-20261110/analysis-report/` of the originating Codex chat, and in its local ZIP deliverable. They are intentionally not embedded in Git. To build a new viewer for a newly inferred run, use the repository's `scr.cli.run_bird_b0_eval visualize` command as documented in docs/bird-b0.md. These are observable outputs and tool events, not private chain-of-thought.

The root-cause CSVs contain evidence-based primary candidates, with confirmed mechanisms distinguished from SQL differences and unresolved reference interpretation. Diagnostic SQL interventions are offline only; none were substituted into model predictions. Statistical methods: Wilson95% EX intervals,20,000 seed42 split-stratified paired bootstrap draws and exact two-sided McNemar. Query categories are overlapping regex features over Gold SQL, not official categories. Source/provenance checks and SHA256 checksums accompany this archive.
