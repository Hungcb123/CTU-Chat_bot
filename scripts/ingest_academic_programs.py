"""Ingest academic program markdown files into the existing Qdrant collection.

Usage::

    python scripts/ingest_academic_programs.py

This script:
1. Reads all ``*.md`` files from ``data/markdown_graph/``.
2. Parses YAML frontmatter for metadata.
3. Splits content using ``MarkdownHeaderTextSplitter``.
4. Assigns ``domain='academic_program'`` (or ``academic_regulation`` for
   ``quychehocvu.md``).
5. Ingests into the same Qdrant collection used by the main pipeline.
"""

from __future__ import annotations

import logging
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [INGEST_ACADEMIC] - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

MARKDOWN_GRAPH_DIR = PROJECT_ROOT / "data" / "markdown_graph"
QUY_CHE_FILE = "quychehocvu.md"

# Chunking config
PARENT_HEADERS = [
    ("#", "Header_1"),
    ("##", "Header_2"),
    ("###", "Header_3"),
]
CHILD_CHUNK_SIZE = 600
CHILD_CHUNK_OVERLAP = 100


def _extract_frontmatter(content: str) -> Dict[str, str]:
    """Parse YAML-like frontmatter."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    meta: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta


def _strip_frontmatter(content: str) -> str:
    """Remove the YAML frontmatter block."""
    return re.sub(r"^---\s*\n.*?\n---\s*\n?", "", content, count=1, flags=re.DOTALL)


def process_program_file(file_path: Path) -> List[Document]:
    """Read a markdown file and return chunked Documents with metadata."""
    content = file_path.read_text(encoding="utf-8")
    frontmatter = _extract_frontmatter(content)
    body = _strip_frontmatter(content)

    is_quy_che = file_path.name == QUY_CHE_FILE

    # Base metadata for this file
    base_meta: Dict[str, Any] = {
        "source": file_path.name,
        "domain": "academic_regulation" if is_quy_che else "academic_program",
        "content_kind": (
            "quy_che_hoc_vu" if is_quy_che else "chuong_trinh_dao_tao"
        ),
    }
    if not is_quy_che:
        base_meta["nganh_hoc"] = frontmatter.get("nganh_hoc", "")
        base_meta["ma_nganh"] = ""
        # Try to extract ma_nganh from filename (e.g. 108_7480107_TriTueNhanTao.md)
        ma_match = re.search(r"_(\d{7})_", file_path.name)
        if ma_match:
            base_meta["ma_nganh"] = ma_match.group(1)
        base_meta["don_vi"] = frontmatter.get("don_vi", "")
        base_meta["trinh_do"] = frontmatter.get("trinh_do", "")
        base_meta["nam_ban_hanh"] = frontmatter.get("nam_ban_hanh", "")

    # --- Step 1: Split by Markdown headers → Parent chunks ---
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=PARENT_HEADERS,
        strip_headers=False,
    )
    parent_docs = header_splitter.split_text(body)

    # --- Step 2: Further split into child chunks ---
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHILD_CHUNK_SIZE,
        chunk_overlap=CHILD_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "],
    )

    all_docs: List[Document] = []
    for parent in parent_docs:
        parent_meta = {**base_meta, **parent.metadata}

        children = child_splitter.split_text(parent.page_content)
        for child_text in children:
            doc = Document(
                page_content=child_text,
                metadata={
                    **parent_meta,
                    "doc_id": str(uuid.uuid4()),
                    "parent_content": parent.page_content[:200],
                },
            )
            all_docs.append(doc)

    return all_docs


def main():
    """Main entry point — ingest all academic program files."""
    if not MARKDOWN_GRAPH_DIR.exists():
        logger.error("Directory not found: %s", MARKDOWN_GRAPH_DIR)
        sys.exit(1)

    md_files = sorted(MARKDOWN_GRAPH_DIR.glob("*.md"))
    logger.info("Found %d markdown files in %s", len(md_files), MARKDOWN_GRAPH_DIR)

    all_documents: List[Document] = []
    for md_file in md_files:
        try:
            docs = process_program_file(md_file)
            all_documents.extend(docs)
            logger.info("  ✅ %s → %d chunks", md_file.name, len(docs))
        except Exception as exc:
            logger.error("  ❌ %s → %s: %s", md_file.name, type(exc).__name__, exc)

    logger.info(
        "Total: %d documents from %d files", len(all_documents), len(md_files)
    )

    if not all_documents:
        logger.warning("No documents to ingest. Exiting.")
        return

    # --- Ingest into Qdrant ---
    from app.services.rag_engine import AdvancedChunkingEngine

    engine = AdvancedChunkingEngine(
        persist_dir=str(PROJECT_ROOT / "qdrant_storage")
    )

    logger.info("Ingesting %d documents into Qdrant...", len(all_documents))

    # Use the engine's vector store to add documents
    texts = [doc.page_content for doc in all_documents]
    metadatas = [doc.metadata for doc in all_documents]

    engine.vector_store.add_texts(texts=texts, metadatas=metadatas)

    logger.info("✅ Ingestion complete! %d documents added.", len(all_documents))

    # Summary
    domains = {}
    for doc in all_documents:
        d = doc.metadata.get("domain", "unknown")
        domains[d] = domains.get(d, 0) + 1
    for domain, count in sorted(domains.items()):
        logger.info("  Domain '%s': %d chunks", domain, count)


if __name__ == "__main__":
    main()
