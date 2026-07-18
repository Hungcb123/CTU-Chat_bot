# Metadata RAG rollout

Run these commands from the environment that already contains the project's ML
dependencies (normally `wsl_venv`). The commands never call Gemini or Groq.

For the Ubuntu/WSL MVP, the complete guarded rollout and app startup can be run
with one command after stopping the old app:

```bash
bash scripts/rollout_mvp.sh
```

The remaining commands below document the equivalent manual process.

## Build and activate

```bash
./wsl_venv/bin/python scripts/reindex_all.py preflight
./wsl_venv/bin/python scripts/reindex_all.py build --index-version 2026-07-17-metadata-v1
./wsl_venv/bin/python scripts/reindex_all.py validate --index-version 2026-07-17-metadata-v1
```

After validation passes, stop the application (or otherwise pause admin
uploads) for the short alias cutover window. Then run:

```bash
./wsl_venv/bin/python scripts/reindex_all.py activate --index-version 2026-07-17-metadata-v1
./wsl_venv/bin/python scripts/test_retriever.py
```

Do not activate a collection if `build`, `validate`, or the retrieval assertions
return a non-zero exit code. After all retrieval assertions pass, set:

```dotenv
QDRANT_COLLECTION_ALIAS=ctu_scholarship_docs_current
RAG_METADATA_FILTER_ENABLED=true
```

Then restart the application and run only 4-6 Gemini end-to-end questions.

## Rollback

Stop the application, set `RAG_METADATA_FILTER_ENABLED=false`, and move the
alias back to the retained legacy collection:

```bash
./wsl_venv/bin/python scripts/reindex_all.py activate \
  --collection ctu_scholarship_docs_v3 \
  --allow-unvalidated
```

Start the application again. Keep both the previous collection and its parent
rows for at least 48 hours. Parent rows may only be removed after confirming no
retained collection references their `doc_id` values.
