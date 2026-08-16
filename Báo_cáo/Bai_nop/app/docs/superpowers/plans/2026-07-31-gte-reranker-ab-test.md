# GTE Reranker A/B Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run `Alibaba-NLP/gte-multilingual-reranker-base` under the existing 512-token retrieval settings while preserving one-line rollback to BGE.

**Architecture:** Resolve the reranker model from `RAG_RERANKER_MODEL`, defaulting to GTE. Keep the existing LangChain CrossEncoder pipeline, top-15 candidates, top-6 output and 512-token cap unchanged; enable remote model code only for GTE.

**Tech Stack:** Python, unittest, sentence-transformers 5.5.1, transformers 4.39.3, LangChain Community 0.4.2.

## Global Constraints

- Do not change embeddings, Qdrant vectors, chunking, retrieval `k`, rerank `top_n`, or max length 512.
- Do not add dependencies or reindex data.
- Rollback must require changing only `RAG_RERANKER_MODEL` to `BAAI/bge-reranker-v2-m3` and restarting the app.

---

### Task 1: Configurable reranker selection

**Files:**
- Modify: `tests/test_rag_engine_filter.py`
- Modify: `app/services/rag_engine.py`
- Modify: `.env`

**Interfaces:**
- Consumes: `RAG_RERANKER_MODEL`, `RAG_RERANKER_DEVICE`.
- Produces: `_reranker_model_config() -> tuple[str, dict[str, object]]`.

- [ ] Add failing tests asserting GTE is the default with `trust_remote_code=True` and BGE rollback omits that flag.
- [ ] Run `tests.test_rag_engine_filter` and confirm the helper import fails before implementation.
- [ ] Add the minimum helper and use it when constructing `HuggingFaceCrossEncoder`.
- [ ] Add `RAG_RERANKER_MODEL=Alibaba-NLP/gte-multilingual-reranker-base` to `.env`.
- [ ] Run the focused test, full unit suite, compile check and GitNexus change detection.

