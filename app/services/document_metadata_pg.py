"""Đồng bộ document business metadata giữa JSON manifest và PostgreSQL.

Module này cung cấp các hàm để:
- Đọc toàn bộ metadata từ ``document_metadata.json`` rồi nạp vào bảng
  ``document_metadata`` trong PostgreSQL (dùng khi re-ingest).
- Upsert/delete metadata cho từng tài liệu (dùng khi upload/rollback).

Tất cả hàm public đều nhận ``session`` từ caller để caller quản lý
commit/rollback. Module KHÔNG tự commit.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import delete as sa_delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models.schema import DocumentMetadataRecord
from app.services.document_metadata import (
    DEFAULT_MANIFEST_PATH,
    DocumentMetadataCatalog,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Bulk sync  (re-ingest / reindex)
# ---------------------------------------------------------------------------

def sync_metadata_from_json(
    session: Session,
    manifest_path: str | Path | None = None,
) -> int:
    """Xóa toàn bộ bảng ``document_metadata`` rồi INSERT lại từ JSON manifest.

    Chạy trong cùng transaction do caller cung cấp (caller phải ``commit``).

    Returns:
        Số lượng document metadata records đã insert.
    """
    path = Path(manifest_path or DEFAULT_MANIFEST_PATH).resolve()
    catalog = DocumentMetadataCatalog.load(path)

    # Xóa toàn bộ rows cũ trong cùng transaction
    deleted = session.execute(sa_delete(DocumentMetadataRecord))
    logger.info(
        "Đã xóa %d document metadata rows cũ.",
        deleted.rowcount,
    )

    count = 0
    for source in catalog.sources:
        meta = catalog.get(source)
        record = DocumentMetadataRecord(
            source=source,
            domain=meta.domain.value,
            content_kind=meta.content_kind.value,
            fee_kind=meta.fee_kind.value,
            academic_year=meta.academic_year,
            status=meta.status.value,
            original_filename=meta.original_filename,
            uploaded_by=meta.uploaded_by,
            uploaded_at=meta.uploaded_at,
        )
        session.add(record)
        count += 1

    session.flush()
    logger.info(
        "Đã nạp %d document metadata records từ %s vào PostgreSQL.",
        count,
        path.name,
    )
    return count


# ---------------------------------------------------------------------------
# Single-document operations  (upload / rollback)
# ---------------------------------------------------------------------------

def upsert_document_metadata(
    session: Session,
    source: str,
    metadata_dict: dict[str, Any],
) -> None:
    """Upsert 1 document metadata row (INSERT … ON CONFLICT UPDATE).

    ``metadata_dict`` là output của ``DocumentMetadata.as_dict()`` hoặc
    ``normalize_document_class()``.
    """
    uploaded_at_raw = metadata_dict.get("uploaded_at")
    uploaded_at: datetime | None = None
    if uploaded_at_raw is not None:
        if isinstance(uploaded_at_raw, str):
            uploaded_at = datetime.fromisoformat(uploaded_at_raw)
        elif isinstance(uploaded_at_raw, datetime):
            uploaded_at = uploaded_at_raw
        if uploaded_at is not None and uploaded_at.tzinfo is None:
            uploaded_at = uploaded_at.replace(tzinfo=timezone.utc)

    values = {
        "source": source,
        "domain": metadata_dict["domain"],
        "content_kind": metadata_dict["content_kind"],
        "fee_kind": metadata_dict["fee_kind"],
        "academic_year": metadata_dict.get("academic_year"),
        "status": metadata_dict.get("status", "active"),
        "original_filename": metadata_dict.get("original_filename"),
        "uploaded_by": metadata_dict.get("uploaded_by"),
        "uploaded_at": uploaded_at,
    }

    stmt = pg_insert(DocumentMetadataRecord).values(**values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["source"],
        set_={
            "domain": stmt.excluded.domain,
            "content_kind": stmt.excluded.content_kind,
            "fee_kind": stmt.excluded.fee_kind,
            "academic_year": stmt.excluded.academic_year,
            "status": stmt.excluded.status,
            "original_filename": stmt.excluded.original_filename,
            "uploaded_by": stmt.excluded.uploaded_by,
            "uploaded_at": stmt.excluded.uploaded_at,
        },
    )
    session.execute(stmt)
    session.flush()
    logger.info("Upsert document metadata cho source=%s.", source)


def delete_document_metadata(
    session: Session,
    source: str,
    *,
    missing_ok: bool = True,
) -> bool:
    """Xóa 1 document metadata row theo ``source``.

    Returns:
        ``True`` nếu row đã bị xóa, ``False`` nếu không tìm thấy.
    """
    result = session.execute(
        sa_delete(DocumentMetadataRecord).where(
            DocumentMetadataRecord.source == source
        )
    )
    deleted = result.rowcount > 0
    if deleted:
        session.flush()
        logger.info("Đã xóa document metadata cho source=%s.", source)
    elif not missing_ok:
        raise ValueError(f"Không tìm thấy document metadata cho source={source!r}")
    return deleted


def get_all_document_metadata(session: Session) -> list[dict[str, Any]]:
    """Trả về toàn bộ document metadata rows dưới dạng list of dicts."""
    rows = session.query(DocumentMetadataRecord).order_by(
        DocumentMetadataRecord.source
    ).all()
    result = []
    for row in rows:
        entry: dict[str, Any] = {
            "source": row.source,
            "domain": row.domain,
            "content_kind": row.content_kind,
            "fee_kind": row.fee_kind,
            "academic_year": row.academic_year,
            "status": row.status,
        }
        if row.original_filename is not None:
            entry["original_filename"] = row.original_filename
            entry["uploaded_by"] = row.uploaded_by
            entry["uploaded_at"] = (
                row.uploaded_at.isoformat() if row.uploaded_at else None
            )
        result.append(entry)
    return result
