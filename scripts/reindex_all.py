"""Blue-green RAG index lifecycle CLI.

Examples:
    python scripts/reindex_all.py preflight
    python scripts/reindex_all.py build --index-version 2026-07-17-v1
    python scripts/reindex_all.py validate --index-version 2026-07-17-v1
    python scripts/reindex_all.py activate --index-version 2026-07-17-v1

The script never clears the live collection or the shared parent-document table.
Activating an older physical collection is also the rollback operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from app.services.document_metadata import (  # noqa: E402
    DEFAULT_MANIFEST_PATH,
    DEFAULT_MARKDOWN_DIR,
    DocumentMetadataCatalog,
    validate_catalog,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [REINDEX] - %(levelname)s - %(message)s",
)
logger = logging.getLogger("rag_reindex")

DEFAULT_QDRANT_URL = "http://localhost:6333"
DEFAULT_QDRANT_TIMEOUT_SECONDS = int(os.getenv("QDRANT_TIMEOUT_SECONDS", "60"))
DEFAULT_COLLECTION_ALIAS = "ctu_scholarship_docs_current"
COLLECTION_PREFIX = "ctu_scholarship_docs_"
DEFAULT_EXPECTED_DOCUMENT_COUNT = 46
REQUIRED_METADATA_FIELDS = {
    "domain",
    "content_kind",
    "fee_kind",
    "academic_year",
    "status",
    "source",
    "source_sha256",
    "metadata_schema_version",
    "index_version",
    "ingest_run_id",
    "doc_id",
}
REQUIRED_PARENT_METADATA_FIELDS = REQUIRED_METADATA_FIELDS - {"doc_id"}
REQUIRED_PAYLOAD_INDEXES = {
    "metadata.status",
    "metadata.domain",
    "metadata.content_kind",
    "metadata.fee_kind",
    "metadata.academic_year",
    "metadata.index_version",
    "metadata.source",
    "metadata.ingest_run_id",
}


def _normalize_index_version(value: str) -> str:
    value = value.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
        raise ValueError(
            "index version must start with an alphanumeric character and only "
            "contain letters, digits, underscore or dash"
        )
    return value


def physical_collection_name(index_version: str) -> str:
    return COLLECTION_PREFIX + _normalize_index_version(index_version)


def _collection_from_args(args: argparse.Namespace) -> str:
    if getattr(args, "collection", None):
        return args.collection
    if not getattr(args, "index_version", None):
        raise ValueError("provide --collection or --index-version")
    return physical_collection_name(args.index_version)


def _catalog_errors(report: Any, expected_count: int | None) -> list[str]:
    errors: list[str] = []
    for field in (
        "manifest_errors",
        "filesystem_errors",
        "missing_entries",
        "orphan_entries",
        "invalid_utf8_files",
    ):
        for item in getattr(report, field, ()):
            errors.append(f"{field}: {item}")
    if expected_count is not None:
        if report.manifest_count != expected_count:
            errors.append(
                f"manifest_count={report.manifest_count}, expected={expected_count}"
            )
        if report.markdown_count != expected_count:
            errors.append(
                f"markdown_count={report.markdown_count}, expected={expected_count}"
            )
    return errors


def run_preflight(
    *,
    markdown_dir: Path,
    manifest_path: Path,
    expected_count: int | None,
) -> bool:
    """Validate catalog/file parity and UTF-8 without loading ML/Qdrant code."""
    report = validate_catalog(markdown_dir, manifest_path)
    errors = _catalog_errors(report, expected_count)
    summary = {
        "valid": bool(report.valid and not errors),
        "manifest": str(manifest_path),
        "markdown_dir": str(markdown_dir),
        "manifest_count": report.manifest_count,
        "markdown_count": report.markdown_count,
        "errors": errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return bool(summary["valid"])


def run_build(args: argparse.Namespace) -> bool:
    if not run_preflight(
        markdown_dir=args.markdown_dir,
        manifest_path=args.manifest,
        expected_count=args.expected_count,
    ):
        logger.error("Preflight failed; no collection was created.")
        return False

    # Heavy ML/Qdrant imports are intentionally deferred until build.
    from qdrant_client import QdrantClient
    from app.services.rag_engine import AdvancedChunkingEngine

    collection_name = _collection_from_args(args)
    index_version = _normalize_index_version(args.index_version)
    client = QdrantClient(
        url=args.qdrant_url,
        timeout=DEFAULT_QDRANT_TIMEOUT_SECONDS,
    )
    if client.collection_exists(collection_name):
        logger.error(
            "Physical collection %s already exists; refusing to overwrite it.",
            collection_name,
        )
        return False

    build_run_id = str(uuid.uuid4())
    engine = AdvancedChunkingEngine(
        qdrant_url=args.qdrant_url,
        collection_name=collection_name,
        index_version=index_version,
        create_collection_if_missing=True,
        load_reranker=False,
        metadata_filter_enabled=True,
        metadata_catalog_path=str(args.manifest),
    )
    markdown_files = sorted(
        args.markdown_dir.glob("*.md"), key=lambda path: path.name.casefold()
    )
    failures: list[str] = []
    for position, path in enumerate(markdown_files, start=1):
        logger.info("[%d/%d] Ingesting %s", position, len(markdown_files), path.name)
        if not engine.ingest_markdown_document(
            str(path),
            ingest_run_id=build_run_id,
            index_version=index_version,
        ):
            failures.append(path.name)

    result = {
        "success": not failures,
        "collection": collection_name,
        "index_version": index_version,
        "ingest_run_id": build_run_id,
        "ingested": len(markdown_files) - len(failures),
        "total": len(markdown_files),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        logger.error(
            "Build is incomplete and was not activated. The non-live collection "
            "%s was left intact for diagnosis.",
            collection_name,
        )
    return not failures


def _iter_points(client: Any, collection_name: str) -> Iterable[Any]:
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=collection_name,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        yield from points
        if offset is None:
            return


def _chunks(values: list[str], size: int = 500) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def run_validate(args: argparse.Namespace) -> bool:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams
    from app.models.schema import ParentDocument as DBParentDocument
    from app.core.database import SyncSessionLocal

    if not run_preflight(
        markdown_dir=args.markdown_dir,
        manifest_path=args.manifest,
        expected_count=args.expected_count,
    ):
        return False

    collection_name = _collection_from_args(args)
    expected_index_version = args.index_version
    client = QdrantClient(
        url=args.qdrant_url,
        timeout=DEFAULT_QDRANT_TIMEOUT_SECONDS,
    )
    if not client.collection_exists(collection_name):
        logger.error("Collection %s does not exist.", collection_name)
        return False

    catalog = DocumentMetadataCatalog.load(args.manifest)
    expected_sources = set(catalog.sources)
    expected_hashes = {
        source: hashlib.sha256((args.markdown_dir / source).read_bytes()).hexdigest()
        for source in expected_sources
    }
    collection_info = client.get_collection(collection_name)
    payload_indexes = set((collection_info.payload_schema or {}).keys())
    errors = [
        f"missing payload index: {field}"
        for field in sorted(REQUIRED_PAYLOAD_INDEXES - payload_indexes)
    ]
    vectors_config = collection_info.config.params.vectors
    if not isinstance(vectors_config, VectorParams):
        errors.append("collection must use one unnamed dense vector")
    else:
        if vectors_config.size != 768:
            errors.append(f"dense vector size={vectors_config.size}, expected=768")
        if vectors_config.distance != Distance.COSINE:
            errors.append(
                f"dense vector distance={vectors_config.distance}, expected=Cosine"
            )

    sources: set[str] = set()
    parent_ids: set[str] = set()
    point_count = 0
    for point in _iter_points(client, collection_name):
        point_count += 1
        payload = point.payload or {}
        metadata = payload.get("metadata")
        if not isinstance(metadata, dict):
            errors.append(f"point {point.id}: missing metadata payload")
            continue
        missing = REQUIRED_METADATA_FIELDS - set(metadata)
        if missing:
            errors.append(f"point {point.id}: missing {sorted(missing)}")
            continue
        source = metadata["source"]
        sources.add(source)
        parent_ids.add(metadata["doc_id"])
        if source not in expected_sources:
            errors.append(f"point {point.id}: unknown source {source!r}")
            continue
        if metadata["source_sha256"] != expected_hashes[source]:
            errors.append(f"point {point.id}: checksum mismatch for {source}")
        if expected_index_version and metadata["index_version"] != expected_index_version:
            errors.append(
                f"point {point.id}: index_version={metadata['index_version']!r}"
            )
        expected_business = catalog.get_payload(source)
        for key, value in expected_business.items():
            if metadata.get(key) != value:
                errors.append(
                    f"point {point.id}: {source} metadata {key} mismatch"
                )

    if point_count == 0:
        errors.append("collection contains no points")
    missing_sources = expected_sources - sources
    extra_sources = sources - expected_sources
    if missing_sources:
        errors.append(f"sources without children: {sorted(missing_sources)}")
    if extra_sources:
        errors.append(f"unknown sources in collection: {sorted(extra_sources)}")

    # Every child doc_id must resolve to a parent row with matching technical
    # metadata. Old parent rows can coexist for the rollback window.
    found_parent_ids: set[str] = set()
    parent_id_list = sorted(parent_ids)
    with SyncSessionLocal() as session:
        for id_batch in _chunks(parent_id_list):
            rows = (
                session.query(DBParentDocument)
                .filter(DBParentDocument.id.in_(id_batch))
                .all()
            )
            for row in rows:
                found_parent_ids.add(row.id)
                metadata = row.metadata_json or {}
                missing = REQUIRED_PARENT_METADATA_FIELDS - set(metadata)
                if missing:
                    errors.append(f"parent {row.id}: missing {sorted(missing)}")
                    continue
                source = metadata.get("source")
                if source not in expected_sources:
                    errors.append(f"parent {row.id}: unknown source {source!r}")
                    continue
                if metadata.get("source_sha256") != expected_hashes[source]:
                    errors.append(f"parent {row.id}: checksum mismatch for {source}")
                if (
                    expected_index_version
                    and metadata.get("index_version") != expected_index_version
                ):
                    errors.append(f"parent {row.id}: wrong index_version")
                expected_business = catalog.get_payload(source)
                for key, value in expected_business.items():
                    if metadata.get(key) != value:
                        errors.append(
                            f"parent {row.id}: {source} metadata {key} mismatch"
                        )
    orphan_ids = parent_ids - found_parent_ids
    if orphan_ids:
        sample = sorted(orphan_ids)[:20]
        errors.append(
            f"{len(orphan_ids)} child doc_id values have no PostgreSQL parent; "
            f"sample={sample}"
        )

    # Keep output actionable without flooding the console on a systemic error.
    result = {
        "valid": not errors,
        "collection": collection_name,
        "index_version": expected_index_version,
        "points": point_count,
        "parents": len(found_parent_ids),
        "sources": len(sources),
        "error_count": len(errors),
        "errors": errors[:100],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if len(errors) > 100:
        logger.error("Validation produced %d additional errors.", len(errors) - 100)
    return not errors


def run_activate(args: argparse.Namespace) -> bool:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import (
        CreateAlias,
        CreateAliasOperation,
        DeleteAlias,
        DeleteAliasOperation,
    )

    collection_name = _collection_from_args(args)
    client = QdrantClient(
        url=args.qdrant_url,
        timeout=DEFAULT_QDRANT_TIMEOUT_SECONDS,
    )
    if not client.collection_exists(collection_name):
        logger.error("Collection %s does not exist.", collection_name)
        return False
    if not args.allow_unvalidated and not run_validate(args):
        logger.error("Activation refused because validation failed.")
        return False

    aliases = {item.alias_name: item.collection_name for item in client.get_aliases().aliases}
    current = aliases.get(args.alias)
    if current == collection_name:
        logger.info("Alias %s already points to %s.", args.alias, collection_name)
        return True

    operations = []
    if current is not None:
        operations.append(
            DeleteAliasOperation(delete_alias=DeleteAlias(alias_name=args.alias))
        )
    operations.append(
        CreateAliasOperation(
            create_alias=CreateAlias(
                collection_name=collection_name,
                alias_name=args.alias,
            )
        )
    )
    client.update_collection_aliases(change_aliases_operations=operations)
    logger.info(
        "Alias %s atomically moved from %s to %s.",
        args.alias,
        current or "<none>",
        collection_name,
    )
    return True


def _common_parser_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="canonical document metadata manifest",
    )
    parser.add_argument(
        "--markdown-dir",
        type=Path,
        default=DEFAULT_MARKDOWN_DIR,
        help="directory containing canonical Markdown sources",
    )
    parser.add_argument(
        "--expected-count",
        type=int,
        default=int(
            os.getenv("RAG_EXPECTED_MARKDOWN_COUNT", DEFAULT_EXPECTED_DOCUMENT_COUNT)
        ),
        help="expected manifest and Markdown count; use 0 to disable the count gate",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    preflight = commands.add_parser("preflight", help="validate manifest/files only")
    _common_parser_options(preflight)

    build = commands.add_parser("build", help="build a new physical collection")
    _common_parser_options(build)
    build.add_argument("--index-version", required=True)
    build.add_argument("--collection")
    build.add_argument(
        "--qdrant-url", default=os.getenv("QDRANT_URL", DEFAULT_QDRANT_URL)
    )

    validate = commands.add_parser("validate", help="validate a built collection")
    _common_parser_options(validate)
    validate.add_argument("--index-version")
    validate.add_argument("--collection")
    validate.add_argument(
        "--qdrant-url", default=os.getenv("QDRANT_URL", DEFAULT_QDRANT_URL)
    )

    activate = commands.add_parser(
        "activate", help="atomically point the live alias at a physical collection"
    )
    _common_parser_options(activate)
    activate.add_argument("--index-version")
    activate.add_argument("--collection")
    activate.add_argument(
        "--alias",
        default=os.getenv("QDRANT_COLLECTION_ALIAS", DEFAULT_COLLECTION_ALIAS),
    )
    activate.add_argument(
        "--qdrant-url", default=os.getenv("QDRANT_URL", DEFAULT_QDRANT_URL)
    )
    activate.add_argument(
        "--allow-unvalidated",
        action="store_true",
        help="explicitly allow initial legacy alias setup or rollback",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.manifest = args.manifest.resolve()
    args.markdown_dir = args.markdown_dir.resolve()
    if args.expected_count == 0:
        args.expected_count = None
    try:
        if args.command == "preflight":
            ok = run_preflight(
                markdown_dir=args.markdown_dir,
                manifest_path=args.manifest,
                expected_count=args.expected_count,
            )
        elif args.command == "build":
            ok = run_build(args)
        elif args.command == "validate":
            ok = run_validate(args)
        elif args.command == "activate":
            ok = run_activate(args)
        else:  # pragma: no cover - argparse guarantees a known subcommand
            parser.error(f"unknown command: {args.command}")
            return 2
    except (OSError, RuntimeError, ValueError) as exc:
        logger.error("%s", exc)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
