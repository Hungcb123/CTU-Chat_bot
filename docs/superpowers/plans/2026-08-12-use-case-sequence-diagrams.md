# Use Case Sequence Diagrams Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a readable, code-grounded, seven-page A4 landscape Draw.io sequence-diagram artifact.

**Architecture:** Describe each use case as participant/message JSON and reuse `AIDraw/drawio-skill/scripts/seqlayout.py` for deterministic UML geometry. Merge the generated pages into one `mxfile`, set A4 landscape page metadata, validate structurally, then export and inspect each page.

**Tech Stack:** Draw.io XML, repository-local AIDraw `seqlayout.py`, Python standard library, Draw.io Desktop CLI 31.1.8.

## Global Constraints

- Do not modify `use_cases.drawio` or any other existing diagram.
- Use one A4 landscape page per use case.
- Keep labels readable and grounded in the current frontend and FastAPI code.
- Distinguish structural validation from visual rendering QA.

---

### Task 1: Generate the five UML pages

**Files:**
- Create: `use_case_sequences.drawio`
- Reuse: `AIDraw/drawio-skill/scripts/seqlayout.py`

**Interfaces:**
- Consumes: five participant/message specifications matching the current endpoints.
- Produces: five native Draw.io pages with deterministic lifelines and messages.

- [ ] Generate each page with `seqlayout.py`.
- [ ] Merge the pages into one `mxfile` without altering their native cells.
- [ ] Set every page to A4 landscape metadata and add page titles.

### Task 2: Verify and export

**Files:**
- Test: `use_case_sequences.drawio`
- Create: `use_case_sequences_preview_*.png`
- Create: `use_case_sequences.pdf`

**Interfaces:**
- Consumes: the merged Draw.io artifact.
- Produces: structural validation output and visually reviewed exports.

- [ ] Run `AIDraw/drawio-skill/scripts/validate.py use_case_sequences.drawio --score`.
- [ ] Verify seven unique pages and required endpoint labels.
- [ ] Export each page to a width-capped PNG without embedded XML.
- [ ] Inspect all previews for clipping, overlap, and legibility.
- [ ] Export the final multi-page PDF.
