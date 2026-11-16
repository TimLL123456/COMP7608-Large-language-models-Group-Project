# Project Guideline Requirements Summary

> **Historical proposal status (2026-10-25):** Group 9 submitted its [KORA proposal](../proposal/KORA/KORA_Group9_Proposal.pdf). This document preserves the original guideline summary and its historical proposal-deadline discrepancy. Report and presentation deadlines marked **TBA** have not been re-verified. For implementation progress and the latest verified benchmark, see the [public KORA overview](../README.md).

Compiled: 2026-10-04  
Source: [COMP7608B_LLM_Project_Guideline.pdf](COMP7608B_LLM_Project_Guideline.pdf)

This summary is based on the preserved four-page original. Pages 1–2 contain the Final Project Guideline, page 3 contains the Project Proposal Guidelines, and page 4 contains the Proposal Template. Use this summary for planning; course documents and teaching-team announcements govern official requirements. Working recommendations are identified separately.

## Project scope (original page 1)

Build a working **Agentic AI system** that reasons, plans, uses tools, takes multiple steps and completes a user-oriented task.

A valid project should include:

- A clear user problem and motivation.
- A meaningful agentic workflow in which the agent makes decisions and performs multiple actions.
- At least one tool or external resource, such as search, databases, APIs, code execution, files or other software tools.
- A working end-to-end system.
- System evaluation, such as task quality, reliability, latency, cost, robustness or other appropriate metrics.
- Runnable code and discussion of limitations and design trade-offs.

## Agentic capabilities and examples (original page 1)

Demonstrate at least one meaningful capability: planning/task decomposition, tool use and selection, multi-step execution, iterative reasoning and verification, interaction with external environments/data, memory/state management, or reflection/self-correction/error recovery. **Multi-agent collaboration is optional, not required.**

The core requirement is that the agent actively decides what to do next and carries out the task.

Examples in the document include financial-news research, domain-specific RAG with source verification, data analysis/visualization, coding/testing/debugging, personal or organizational knowledge assistants, web research, literature search/recommendation, document analysis/report generation, customer support/task execution, and multi-agent collaboration. Other domains are welcome. If the topic's suitability is uncertain, consult the Instructor or TAs before proceeding.

## Components generally insufficient on their own (original page 2)

- A simple chatbot without multi-step tasks, or a basic single-turn LLM application.
- A standard RAG pipeline without agentic decision making.
- Prompt engineering alone.
- Fine-tuning without an agentic application.
- A model benchmark without an actual application/system.
- A UI/demo without a meaningful agentic workflow.

These may form part of a larger project but should not constitute its main contribution on their own.

## Model choice and evaluation (original page 2)

Suitable locally deployed open-source models or public API models are allowed. The most advanced commercial models are not required. The original provides [HKU ITS GenAI API quota information](https://its.hku.hk/services/ai-as-a-service/hku-chatgpt/).

Outputs need not be perfect, but output quality must be evaluated systematically. Discuss observed limitations and failure cases, and explain how to improve the system. The original states that detailed evaluation requirements will be supplied in a separate document; that document is not part of the file included here.

## Group formation (original page 2)

| Item | Requirement |
| --- | --- |
| Group size | 3–5 students |
| Self-grouping deadline | 21 September, 18:00 (the original does not state a year or timezone in this entry) |
| Students without a group after the deadline | Random assignment |
| Communication and submission | Nominate one contact member per group |
| Membership changes | No private swapping; contact TAs if a change is needed |

## Deliverables and weights (original page 2)

| Deliverable | Weight | Deadline in the original overview | Notes |
| --- | ---: | --- | --- |
| Proposal | 20% | 9 Oct., 24:00 | Conflicts with the detailed guideline on page 3; see below |
| Report & Code | 50% | TBA | Runnable code required; report requirements/template TBA |
| Presentation | 30% | TBA | Format and requirements TBA |

## Conflicting proposal deadlines

| Source | Time stated in the original | Original page |
| --- | --- | --- |
| Final Project Guideline deliverables overview | 9 Oct., 24:00 | Page 2 |
| Project Proposal Guidelines detailed requirements | October 9, 2026, at 12:00 p.m. (Hong Kong Time) | Page 3 |

Page 3 explicitly specifies **2026-10-09 at 12:00 noon (Hong Kong Time)** and says late submissions will not be accepted. The two times differ by 12 hours. Both statements are preserved here; teaching-team clarification has not been obtained.

**Project working recommendation:** Prepare against the earlier noon deadline while the group contact member checks course announcements or confirms the official deadline with the teaching team. This recommendation is not an official interpretation of the conflict.

## Proposal submission and format (original page 3)

- Submit one PDF per group.
- There is no minimum page requirement; main content must not exceed **4 pages**.
- Appendix and References do not count toward the main-content limit.
- Use the **NeurIPS 2026 LaTeX template**. The original's [template download link](https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip) is preserved here.
- **DO NOT include an abstract.**
- The detailed guidelines explicitly prohibit late submissions; see the deadline conflict above.

## Mandatory proposal content (original pages 3–4)

The following five sections follow the order of the page 4 template. Other relevant components may be added where needed.

| Order and template section | Required content |
| --- | --- |
| 1. Group members | Names and student IDs of all team members |
| 2. Project objective | Clearly define what the project aims to achieve |
| 3. Motivation and challenges | Explain the problem and why it matters |
| 4. Potential solutions | Outline the proposed approach and methodology |
| 5. Experimental dataset description and evaluation plan | Describe data sources and how success will be measured |

The template also includes a Project Title field.

## Items to confirm

| Item | Current evidence/status |
| --- | --- |
| Official proposal deadline | Pages 2 and 3 conflict; clarification pending |
| Report & Code deadline and report template | Marked TBA in this original |
| Presentation deadline, format and requirements | Marked TBA in this original |
| Detailed system evaluation requirements | Original says these will be supplied separately; not included in this file |

Return to the [project README](../README.md) · View the [dataset catalogue](../research/dataset-catalogue.md)
