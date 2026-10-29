# KORA — COMP7608B Group Project

**Group 9 | COMP7608B Large Language Models | 2026–2027 Semester 1**  
**Planning status:** v3.1 teammate review draft · 28 October 2026

> **Start here:** [Progress Planning & Development Tickets](progress-planning.md) — canonical development roadmap for this **public group collaboration repository**.

## Project Goal

KORA (Knowledge-Oriented Reasoning Agent) explores a bounded, evidence-guided Text-to-SQL system evaluated on the **original BIRD Mini-Dev**. The submitted academic proposal governs the benchmark and research scope. The core comparison uses one fixed SQL script with **S0 first-attempt** and **S1 bounded error-repair** metrics, compared with an adaptive **B0** agent. Advanced modules B1 graph, B2 planner, B3 router and B4 full KORA are evaluated separately and together.

## Development Workstreams

| Workstream | Tickets | Status |
| --- | --- | --- |
| BIRD data and scoring | KORA-02–03 | Planned |
| S0/S1 and B0 SQL baseline | KORA-04–05 | Planned; prototypes exist **only in private HKU repo** |
| Graph / planner / router / full KORA | KORA-06–09 | Planned |
| Controlled experiments and academic deliverables | KORA-10–12 | Planned |
| **Document RAG agent** | **KORA-13** | **P2 optional; only if progress and team time permit** |
| SQL-first backend, frontend and integration | KORA-14–16 | Planned; must work **without RAG** |
| **Synthetic relational demo/test data** | **KORA-17** | **P0 foundation**; reproducible fictional SQLite fixtures |

## Planned Application (Not Yet Implemented Here)

~~~text
Frontend (SQL question, results, traces)
    |
Python Backend API
    |
Text-to-SQL Agent (S0/S1 or B0–B4)
    |
Read-only SQLite  <-- Synthetic fixture for development and demo
    |
BIRD evaluator (separate official benchmark workflow)
~~~

The document-RAG path is optional and should only appear in the app after it is implemented and validated. The SQL application must remain usable without an RAG agent.

## Repositories and Current State

- **This repository (public):** canonical planning documentation; **no source code, datasets, generated SQL results, frontend or backend implementation has been migrated here yet**.
- **[Original HKU project documentation](https://github.com/TimLL123456/HKU/blob/main/2026-2027/Sem1/COMP7608%20-%20Large%20language%20models/Group%20Project/README.md) (private):** submitted proposal, research, existing SQL/RAG Deep Agents scaffolds, toy evaluators and offline tests. Private content links require GitHub access; do **not** assume collaborators can read them.
- **Source-of-truth rule:** update [progress-planning.md](progress-planning.md) in this public repository first after team agreement; keep the HKU planning copy synchronized if useful. The submitted proposal remains authoritative for research commitments.

## Initial Priorities

1. Review the [planning tickets](progress-planning.md), assign teammates and confirm evidence/evaluation protocol.
2. Build the original BIRD loader and evaluator (**KORA-02/03**) in parallel with synthetic demo fixtures (**KORA-17**).
3. Deliver the fixed S0/S1 SQL baseline and adaptive B0 (**KORA-04/05**) and compare under the same constraints.
4. Build a minimal **SQL-only** backend and frontend (**KORA-14–16**) while research enhancements (**KORA-06–09**) proceed.
5. Run controlled experiments, prepare report and demo (**KORA-10–12**); assess optional RAG (**KORA-13**) only after core progress is satisfactory.

**Data and security:** Synthetic demo/test scores are not official BIRD EX. Do not commit API keys, personal records, proprietary data, or unreviewed copies of files from the private HKU repository. This README is a plan, not evidence that the application runs.
