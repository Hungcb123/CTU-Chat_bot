"""Rebuild the BM25 snapshot from the current Qdrant + PostgreSQL state.

Usage:
    python scripts/rebuild_bm25.py
    python scripts/rebuild_bm25.py --collection ctu_scholarship_docs_fix_llm_ingest_v5

The script reads all child chunks from the live Qdrant collection (resolved
via the alias) and their metadata, then rebuilds qdrant_storage/bm25_index/
so that parent_ids match the current PostgreSQL parent_documents table.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient  # noqa: E402
from app.services.bm25_service import BM25ChildRecord, VietnameseBM25Index  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [REBUILD-BM25] - %(levelname)s - %(message)s",
)
logger = logging.getLogger("rebuild_bm25")

DEFAULT_QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
DEFAULT_ALIAS = os.getenv(
    "QDRANT_COLLECTION_ALIAS", "ctu_scholarship_docs_current"
)
DEFAULT_PERSIST_DIR = str(PROJECT_ROOT / "qdrant_storage" / "bm25_index")


def resolve_collection(client: QdrantClient, alias: str) -> str:
    """Resolve alias to physical collection name."""
    for item in client.get_aliases().aliases:
        if item.alias_name == alias:
            logger.info("Alias %s → %s", alias, item.collection_name)
            return item.collection_name
    raise ValueError(f"Alias {alias!r} not found")


def iter_all_points(client: QdrantClient, collection: str):
    """Scroll through all points in a collection."""
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=collection,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        yield from points
        if offset is None:
            return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--collection",
        default=None,
        help="Physical collection name (default: resolve from alias)",
    )
    parser.add_argument("--alias", default=DEFAULT_ALIAS)
    parser.add_argument("--qdrant-url", default=DEFAULT_QDRANT_URL)
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_PERSIST_DIR,
        help="Directory to save the BM25 snapshot",
    )
    args = parser.parse_args(argv)

    client = QdrantClient(url=args.qdrant_url, timeout=60)

    collection = args.collection
    if not collection:
        collection = resolve_collection(client, args.alias)
    logger.info("Reading child chunks from collection: %s", collection)

    records: list[BM25ChildRecord] = []
    point_count = 0
    for point in iter_all_points(client, collection):
        point_count += 1
        payload = point.payload or {}
        text = payload.get("page_content") or payload.get("text") or ""
        metadata = payload.get("metadata") or {}
        parent_id = metadata.get("doc_id", "")

        if not text.strip() or not parent_id:
            continue

        records.append(
            BM25ChildRecord(
                child_text=text,
                parent_id=parent_id,
                metadata=metadata,
            )
        )

    logger.info(
        "Scanned %d points, %d usable child records", point_count, len(records)
    )

    if not records:
        logger.error("No records to index. Aborting.")
        return 1

    # Detect index_version from the first record
    index_version = records[0].metadata.get("index_version", "")

    bm25 = VietnameseBM25Index(index_version=index_version)
    bm25.build_index(records)
    bm25.save(args.output_dir)
    
    # Đồng bộ sang cả parent_doc_storage/bm25_index để đảm bảo tính tương thích
    alt_output_dir = str(PROJECT_ROOT / "parent_doc_storage" / "bm25_index")
    if Path(args.output_dir).resolve() != Path(alt_output_dir).resolve():
        bm25.save(alt_output_dir)

    logger.info(
        "✅ BM25 index rebuilt: %d records, saved to %s (and %s)",
        len(records),
        args.output_dir,
        alt_output_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
