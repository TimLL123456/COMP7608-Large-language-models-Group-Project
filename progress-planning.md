# KORA — Current Progress and Next Steps

**Current research snapshot: 15 November 2026.** This page tracks the latest verified state rather than previous ticket histories. For earlier ticket statuses, historical project decisions and original roadmap versions, see [Historical Planning](docs/history/progress-planning-pre-current-only-20261115.md).

## Completed research milestones

| Area | Latest verified evidence |
| --- | --- |
| BIRD Mini-Dev 2026 data and read-only SQLite evaluation | Dataset, loader, scorer and CLI implementations exist; see [setup](docs/bird-setup.md) and [scorer](docs/bird-evaluation.md) |
| B0 generalized-v1 | [319/500 (63.80% local EX)](evaluation-results/b0-generalized-v1-gpt6-luna-none-40calls-minidev2026-20261110/README.md) |
| MetadataDiscoveryV2 | [340/500 (68.00% local EX)](evaluation-results/metadata-discovery-v2-descriptions-20261111/README.md) |
| Self Reflection | [350/500 (70.00% local EX), 498/500 SQL outputs](evaluation-results/self-reflection-full-20261113/README.md) |
| Rubric Self Reflection | [326/500 (65.20% local EX)](evaluation-results/rubric-self-reflection-full-20261115/README.md) |
| Role-Specialized Self Reflection | [Implemented with two-shard parallel inference and merging](docs/role-specialized-self-reflection-agent.md); full EX study **not yet verified** |

All results above are local Mini-Dev 2026 results, not official hidden Test results. Different budgets, retries, description availability and workflow conditions prevent attributing differences to an isolated improvement.

## Remaining work / verification

- **Role-specialized experiment:** configure the available Luna/Terra model identifiers, run a new frozen selection and separately score local Dev and Test. Record accuracy, repairs/regressions, token use, latency and model budgets.
- **Matched-compute studies:** compare promising variants under aligned budget and dataset/evidence conditions, if feasible. Existing archived results should not be presented as matched causal evidence.
- **Interactive integration:** verify a real user interface/controller, changed constraints, follow-up questions, end-to-end safety and error recovery. Individual SQL agents do not establish that these requirements are complete.
- **Reliability and non-functional evidence:** test schema errors, timeouts, read-only enforcement, budget exhaustion and response latency/cost under a reproducible protocol.
- **Final deliverables:** reconcile verified implementation with course requirements, produce an honest analysis/report, package reproducible source and experiment evidence, and rehearse a live demo.

No completion dates or ticket ownership are assumed from the historic v4.4 roadmap. Check the current team task tracker for assignments and scheduling.

## Where to continue

Use the [README](README.md) for the current system and [Developer Guide](docs/agent-development.md) for supported paths. Complete experiment artifacts are under [evaluation-results/](evaluation-results/), previous project plans under [Historical Research](docs/history/README.md), and the original course research proposal under [proposal/](proposal/).
