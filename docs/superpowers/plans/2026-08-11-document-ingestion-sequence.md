# Document Ingestion Sequence Diagram Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `ingestion_sequence.drawio`, an editable two-page UML sequence diagram that accurately documents the current admin PDF-upload and internal RAG-ingestion flows, including success and rollback behavior.

**Architecture:** Generate each page's lifelines, activation bars, and message geometry with the repository's Draw.io skill helper `seqlayout.py`. Merge the two generated `<diagram>` elements into one uncompressed `<mxfile>`, then add only the unsupported UML combined fragments and page annotations by editing the generated XML. Preserve the existing `ingestion_pipeline.drawio` and all application source files.

**Tech Stack:** Draw.io uncompressed XML, repository-local `AIDraw/drawio-skill`, Python 3, PowerShell, XML structural validation.

## Global Constraints

- Treat `app/api/document.py` and `app/services/rag_engine.py` as the behavioral source of truth.
- Do not modify application functions, classes, configuration, or the existing `ingestion_pipeline.drawio`.
- Keep the final artifact at `D:\Project\Chatbot\ingestion_sequence.drawio`.
- Use concise Vietnamese message labels while retaining exact method/component names where they clarify the code path.
- Clearly distinguish the success path from failure and rollback behavior.
- Do not claim rendered visual verification because no compatible Draw.io/LibreOffice renderer is currently available on PATH.

---

## Task 1: Capture the two sequence-page specifications

**Files:**

- Create temporary input: `D:\Project\Chatbot\.tmp_ingestion_admin_sequence.json`
- Create temporary input: `D:\Project\Chatbot\.tmp_ingestion_rag_sequence.json`
- Reference: `D:\Project\Chatbot\app\api\document.py:102`
- Reference: `D:\Project\Chatbot\app\services\rag_engine.py:870`

- [ ] Define page 1 participants in this exact order: Admin, Document API, File System, LlamaParse, Metadata Catalog, RAG Engine.
- [ ] Encode the main upload messages: request, authentication/validation, temporary PDF write, PDF parsing, Markdown write/clean, catalog add, `ingest_markdown_document()`, move PDF to `data/done`, and HTTP success return.
- [ ] Encode cleanup/rollback messages after a failed ingestion attempt: `purge_document()`, catalog removal, generated Markdown removal, temporary PDF removal, and HTTP error return.
- [ ] Define page 2 participants in this exact order: Document API, RAG Engine, Metadata Catalog, Markdown Splitters, PostgreSQL, Embedding Model, Qdrant.
- [ ] Encode the internal ingestion messages: read/hash/metadata resolution, header split, metadata attachment, table-preserving parent split, child split, parent persistence, embedding, Qdrant upsert, and success return.
- [ ] Encode the internal failure messages: `purge_document(source, ingest_run_id)`, matching Qdrant deletion, matching PostgreSQL deletion, and failure return.
- [ ] Validate both JSON inputs by loading them with Python's standard `json` module.

Command:

```powershell
python -c "import json; [json.load(open(p, encoding='utf-8')) for p in ('.tmp_ingestion_admin_sequence.json', '.tmp_ingestion_rag_sequence.json')]; print('sequence JSON valid')"
```

Expected: `sequence JSON valid` and exit code 0.

## Task 2: Generate deterministic UML geometry

**Files:**

- Read/execute: `D:\Project\Chatbot\AIDraw\drawio-skill\scripts\seqlayout.py`
- Generate temporary output: `D:\Project\Chatbot\.tmp_ingestion_admin.drawio`
- Generate temporary output: `D:\Project\Chatbot\.tmp_ingestion_rag.drawio`

- [ ] Run `seqlayout.py` once for each JSON specification.
- [ ] Confirm the helper reports the expected participant and message counts.
- [ ] Parse each generated file as XML before merging.

Commands:

```powershell
python AIDraw/drawio-skill/scripts/seqlayout.py .tmp_ingestion_admin_sequence.json -o .tmp_ingestion_admin.drawio
python AIDraw/drawio-skill/scripts/seqlayout.py .tmp_ingestion_rag_sequence.json -o .tmp_ingestion_rag.drawio
python -c "import xml.etree.ElementTree as ET; [ET.parse(p) for p in ('.tmp_ingestion_admin.drawio', '.tmp_ingestion_rag.drawio')]; print('generated XML valid')"
```

Expected: two `wrote ...` messages followed by `generated XML valid`.

## Task 3: Assemble the final two-page Draw.io artifact

**Files:**

- Create: `D:\Project\Chatbot\ingestion_sequence.drawio`
- Read: `D:\Project\Chatbot\.tmp_ingestion_admin.drawio`
- Read: `D:\Project\Chatbot\.tmp_ingestion_rag.drawio`

- [ ] Merge the two generated `<diagram>` nodes under one `<mxfile>`.
- [ ] Set stable unique page IDs and exact page names `01_Admin_Upload_Sequence` and `02_RAG_Ingestion_Sequence`.
- [ ] Add a title and short scope note to each page without changing generated lifeline/message geometry.
- [ ] Add `alt/opt` combined-fragment rectangles behind the relevant generated messages, using pale green for success and pale red for failure/rollback.
- [ ] Apply restrained blue participant/message styling while retaining UML lifelines, standard sync arrows, dashed returns, and activation bars.
- [ ] Ensure fragment cells appear before message cells in XML so frames do not cover arrows or labels.
- [ ] Save as uncompressed Draw.io XML.

Expected: one editable `ingestion_sequence.drawio` containing exactly two pages and no application-source changes.

## Task 4: Run structural and content verification

**Files:**

- Verify: `D:\Project\Chatbot\ingestion_sequence.drawio`
- Verify unchanged: `D:\Project\Chatbot\ingestion_pipeline.drawio`
- Execute: `D:\Project\Chatbot\AIDraw\drawio-skill\scripts\validate.py`

- [ ] Parse the final file with Python's XML parser.
- [ ] Run the Draw.io skill validator and quality score.
- [ ] Assert there are exactly two `<diagram>` pages with the expected names.
- [ ] Assert each page contains UML lifelines, activation bars, message edges, return edges, and its success/failure fragment labels.
- [ ] Confirm key labels exist: `POST /documents/upload`, `ingest_markdown_document()`, `PostgresDocStore`, `Embedding 768-D`, `Qdrant upsert`, and `purge_document()`.
- [ ] Compare the current checksum of `ingestion_pipeline.drawio` with the checksum captured before implementation.
- [ ] Inspect `git status --short` and confirm only the planned new documentation/artifact files were added by this task; preserve all pre-existing unrelated changes.

Commands:

```powershell
python AIDraw/drawio-skill/scripts/validate.py ingestion_sequence.drawio
python AIDraw/drawio-skill/scripts/validate.py ingestion_sequence.drawio --score
python -c "import xml.etree.ElementTree as ET; r=ET.parse('ingestion_sequence.drawio').getroot(); names=[d.get('name') for d in r.findall('diagram')]; assert names==['01_Admin_Upload_Sequence','02_RAG_Ingestion_Sequence'], names; print(names)"
git status --short
```

Expected: validator exit code 0, both expected page names printed, and no modification to `ingestion_pipeline.drawio`.

## Task 5: Clean temporary generation inputs and report verification boundaries

**Files:**

- Remove generated temporary files only:
  - `D:\Project\Chatbot\.tmp_ingestion_admin_sequence.json`
  - `D:\Project\Chatbot\.tmp_ingestion_rag_sequence.json`
  - `D:\Project\Chatbot\.tmp_ingestion_admin.drawio`
  - `D:\Project\Chatbot\.tmp_ingestion_rag.drawio`
- Retain:
  - `D:\Project\Chatbot\ingestion_sequence.drawio`
  - `D:\Project\Chatbot\docs\superpowers\specs\2026-08-11-document-ingestion-sequence-design.md`
  - `D:\Project\Chatbot\docs\superpowers\plans\2026-08-11-document-ingestion-sequence.md`

- [ ] Delete only the four explicitly named task-owned temporary files after validation succeeds.
- [ ] Re-run the XML parser and Draw.io validator on the retained final artifact.
- [ ] Report that XML structure and skill validation passed, and explicitly note that visual rendering was not verified because a compatible renderer was unavailable.
- [ ] Provide clickable links to the final `.drawio`, design specification, and implementation plan.

