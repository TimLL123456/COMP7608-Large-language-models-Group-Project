# KORA — COMP7608B Group 9 final project proposal

This directory preserves the latest KORA proposal. The PDF submitted to Moodle is the authoritative submission copy and is included as `KORA_Group9_Proposal.pdf` (SHA-256: `376099b0b3dded9916bdf16539d7ff1aff46d786557b5f30493204185bc063cc`).

- `main.tex`: LaTeX source with all five mandatory sections, bibliography and appendix.
- `original_chart_crop.png`: raster image of the original architecture chart from the submitted proposal (SHA-256: `58fbef0f7afd9c6f0787b088c32e54566cdba9e7848823a7e98b57afba482672`).
- `original_chart.tex`: editable TikZ reproduction; the current LaTeX source uses this recreation rather than the raster image, so for exact submission appearance use the PDF.
- `proposal.md`: editable Markdown transcription, aligned with the latest proposal text.
- `neurips_2026.sty`: NeurIPS style file used by the LaTeX build.
- `references.bib`: bibliography entries maintained as reference metadata; the current LaTeX source typesets references inline.

Run `pdflatex main.tex` twice to compile. The footer conference notice is suppressed; no abstract is included. The four Group 9 student IDs are confirmed. The intended user needs appear within the Project objective.

**Scope:** The committed implementation and evaluation target BIRD Mini-Dev Text-to-SQL. A generic knowledge assistant/document adapter is a future extension, not a claimed experimental result.

## Revised working draft (not submitted)

- **[Final proposal draft](final-proposal-draft.md)**: A group-discussion revision that retains the submitted BIRD Mini-Dev Text-to-SQL track and proposes **MuSiQue multi-hop document QA**, a **Hybrid SQL + Document Reasoning** demonstration, and a **synthetic retail product evaluation**.
- **Frontend — TO BE CONFIRMED (TBC):** A simple interface is proposed; **Streamlit** is only a provisional candidate.
- **Backend — TO BE CONFIRMED (TBC):** A simple Python API layer is proposed; **FastAPI** is only a provisional candidate.
- The proposed document track, hybrid demonstration, product domain, frontend and backend are **not yet approved or implemented**. The submitted `KORA_Group9_Proposal.pdf` remains authoritative and unchanged.
