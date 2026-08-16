# Use Case Sequence Diagrams Design

## Goal

Create an editable Draw.io artifact containing seven code-grounded UML sequence diagrams for: Ask a Question, Upload File, Register, Login, Delete Conversation, View Conversation, and New Conversation.

## Layout

- One use case per page.
- Seven A4 landscape pages so labels remain readable when pasted into a report.
- Vietnamese labels with endpoint and technology names retained where they clarify the code path.
- UML lifelines, activation bars, synchronous calls, dashed returns, and short notes for important alternate/error behavior.

## Code-grounded scope

- Ask a Question: authenticated `POST /chat`, Redis history, query rewrite/routing, RAG retrieval, Gemini/tool handling, Redis update, and background PostgreSQL persistence.
- Upload File: admin-only `POST /document/upload`, validation, LlamaParse, Markdown/metadata creation, RAG ingestion, final file move, and rollback on failure.
- Register: `POST /auth/register`, duplicate username check, bcrypt hashing, PostgreSQL insert, and success/error response.
- Login: `POST /auth/login`, user lookup, bcrypt verification, JWT creation, HTTP-only cookie, and success/error response.
- Delete Conversation: confirmation in the UI, authenticated `DELETE /sessions/{session_id}`, ownership check, PostgreSQL cascade deletion, Redis history deletion, and UI refresh.
- View Conversation: select a session, refresh its active state, authenticated message retrieval, ownership check, PostgreSQL message loading, Redis history reconstruction, and UI rendering.
- New Conversation: reset the current client-side session and chat area, refresh the session list, and explicitly show that persistence begins only after the first `POST /chat`.

## Deliverables and verification

- `use_case_sequences.drawio`: editable seven-page source.
- `use_case_sequences_preview_*.png`: clean page previews for visual inspection.
- `use_case_sequences.pdf`: A4-ready multi-page export if the local Draw.io CLI succeeds.
- Structural validation and image review are reported separately.
