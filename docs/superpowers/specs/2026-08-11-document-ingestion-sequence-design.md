# Document Ingestion Sequence Diagram Design

## Objective

Create a new editable Draw.io artifact named `ingestion_sequence.drawio` that documents the current admin PDF-upload and RAG-ingestion implementation. Preserve the existing `ingestion_pipeline.drawio` unchanged.

The current application code is the source of truth. The supplied pipeline image and sequence-diagram image are visual references only.

## Artifact Structure

The Draw.io file will contain two pages so the full behavior remains readable:

1. `01_Admin_Upload_Sequence` — end-to-end orchestration from the administrator's upload request through the HTTP success/error response.
2. `02_RAG_Ingestion_Sequence` — internal ingestion, parent/child persistence, embedding, Qdrant storage, and rollback.

Both pages will use UML sequence-diagram conventions: participant headers, dashed lifelines, synchronous message arrows, dashed return arrows, activation bars, and `alt`/`opt` fragments for conditional behavior.

## Page 1: Admin Upload Sequence

Participants, from left to right:

- Admin
- Document API (`POST /documents/upload`)
- File System
- LlamaParse
- Metadata Catalog
- RAG Engine

Main success flow:

1. Admin uploads a PDF with `document_class` and optional `academic_year`.
2. Document API authenticates the admin and validates filename, document metadata, MIME type, API key, and duplicate paths.
3. Document API saves a validated temporary PDF under `data/input`.
4. Document API asks LlamaParse to upload, process, and return Markdown.
5. Document API writes and cleans the Markdown file under `data/markdown`.
6. Document API adds the normalized metadata entry to the catalog.
7. Document API calls `RAG Engine.ingest_markdown_document()` with a unique `ingest_run_id`.
8. After ingestion succeeds, Document API moves the original PDF to `data/done`.
9. Document API returns the success payload to Admin.

Failure behavior will be shown in an `alt` fragment. Validation and parsing failures return an HTTP error after temporary-file cleanup. Failures after ingestion starts trigger RAG purge, catalog rollback, Markdown deletion, temporary PDF deletion, and an HTTP error response.

## Page 2: RAG Ingestion Sequence

Participants, from left to right:

- Document API
- RAG Engine
- Metadata Catalog
- Markdown Splitters
- PostgreSQL
- Embedding Model
- Qdrant

Main success flow:

1. RAG Engine reads UTF-8 Markdown, computes SHA-256, loads business metadata, resolves `index_version`, and extracts an effective date/timestamp.
2. Markdown header splitting creates first-level parents.
3. Business and technical metadata are attached to every parent.
4. Parent/table-aware splitting produces final parent chunks.
5. ParentDocumentRetriever splits parents into child chunks.
6. Parent content and JSONB metadata are stored in PostgreSQL through `PostgresDocStore`.
7. Child chunks are embedded with the Vietnamese bi-encoder into 768-dimensional vectors.
8. Child vectors, payload metadata, and parent IDs are stored in Qdrant.
9. RAG Engine returns success to Document API.

An `alt ingestion failure` fragment will show `purge_document(source, ingest_run_id)`: delete matching Qdrant points, delete matching PostgreSQL parents, and return failure. The outer upload flow then removes the catalog entry and generated files.

## Visual Design

- Landscape pages with a white background and dark text.
- Blue participant headers, blue dashed lifelines, and restrained blue message arrows.
- Pale green success fragment and pale red failure/rollback fragment.
- Participant labels include the code-level component name where useful.
- Messages use concise Vietnamese descriptions plus exact method names for key calls.
- Layout prioritizes readable message order and avoids line crossings.

## Validation

- Confirm the Draw.io XML parses successfully.
- Confirm both expected page names exist.
- Confirm participant, lifeline, message, activation, and combined-fragment shapes are present.
- Render or open each page for visual review when a compatible renderer is available.
- Verify `ingestion_pipeline.drawio` remains unchanged.

## Out of Scope

- Batch ingestion through `scripts/batch_process.py`.
- Blue-green full reindexing through `scripts/reindex_all.py` and `scripts/rollout_mvp.sh`.
- Chat retrieval and answer generation after ingestion completes.
- Any source-code behavior change.
