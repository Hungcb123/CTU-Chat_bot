import json
import logging
import re
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import bm25s
from pyvi import ViTokenizer

logger = logging.getLogger(__name__)

PUNCTUATION_PATTERN = re.compile(r"[^\w\s_]")


def tokenize_vietnamese(text: str) -> List[str]:
    """Tách từ tiếng Việt bằng PyVi, chuẩn hóa chữ thường và lọc ký tự đặc biệt."""
    if not text or not text.strip():
        return []
    try:
        tokenized_text = ViTokenizer.tokenize(text)
        cleaned = PUNCTUATION_PATTERN.sub(" ", tokenized_text).lower()
        tokens = [token.strip() for token in cleaned.split() if token.strip()]
        return tokens
    except Exception as exc:
        logger.warning(f"Lỗi khi tách từ tiếng Việt: {exc}, fallback về whitespace split")
        cleaned = PUNCTUATION_PATTERN.sub(" ", text).lower()
        return [token.strip() for token in cleaned.split() if token.strip()]


@dataclass
class BM25ChildRecord:
    child_text: str
    parent_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "child_text": self.child_text,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BM25ChildRecord":
        return cls(
            child_text=data["child_text"],
            parent_id=data["parent_id"],
            metadata=data.get("metadata", {}),
        )


class VietnameseBM25Index:
    """Chỉ mục BM25 cho các Child Chunks tiếng Việt, kết nối với Parent Documents."""

    def __init__(
        self,
        persist_dir: Optional[str | Path] = None,
        index_version: Optional[str] = None,
    ):
        self.persist_dir = Path(persist_dir) if persist_dir else None
        self.index_version = index_version or ""
        self.records: List[BM25ChildRecord] = []
        self.retriever: Optional[bm25s.BM25] = None

        if self.persist_dir and self.persist_dir.exists():
            self.load(self.persist_dir)

    def is_indexed(self) -> bool:
        return self.retriever is not None and len(self.records) > 0

    def build_index(self, records: Sequence[BM25ChildRecord]) -> None:
        """Xây dựng chỉ mục BM25 từ danh sách BM25ChildRecord."""
        self.records = list(records)
        if not self.records:
            self.retriever = None
            logger.info("Chỉ mục BM25 trống (0 bản ghi).")
            return

        logger.info(f"Bắt đầu xây dựng chỉ mục BM25 với {len(self.records)} Child Chunks...")
        corpus_texts = [r.child_text for r in self.records]
        corpus_tokens = [tokenize_vietnamese(text) for text in corpus_texts]

        # Khởi tạo mô hình bm25s không lưu corpus để truy xuất theo index mượt mà
        retriever = bm25s.BM25(method="lucene", k1=1.5, b=0.75)
        retriever.index(corpus_tokens)
        self.retriever = retriever
        logger.info("✅ Xây dựng chỉ mục BM25 thành công!")

    def add_documents(
        self,
        child_docs: Sequence[Tuple[str, str, Dict[str, Any]]],
        auto_persist: bool = True,
    ) -> None:
        """
        Nạp thêm các Child Chunks vào BM25:
        child_docs: list of (child_text, parent_id, metadata)
        """
        if not child_docs:
            return

        new_records = [
            BM25ChildRecord(child_text=text, parent_id=pid, metadata=meta)
            for text, pid, meta in child_docs
        ]
        all_records = self.records + new_records
        self.build_index(all_records)

        if auto_persist and self.persist_dir:
            self.save(self.persist_dir)

    def purge_by_source(
        self,
        source: str,
        ingest_run_id: Optional[str] = None,
        auto_persist: bool = True,
    ) -> int:
        """Xóa các bản ghi thuộc về source (hoặc ingest_run_id cụ thể) và cập nhật lại chỉ mục."""
        initial_count = len(self.records)
        kept_records = []
        for r in self.records:
            if r.metadata.get("source") == source:
                if ingest_run_id is None or r.metadata.get("ingest_run_id") == ingest_run_id:
                    continue
            kept_records.append(r)

        deleted_count = initial_count - len(kept_records)
        if deleted_count > 0:
            logger.info(f"Đã xóa {deleted_count} Child Chunks của source={source} khỏi BM25.")
            self.build_index(kept_records)
            if auto_persist and self.persist_dir:
                self.save(self.persist_dir)
        return deleted_count

    def search(
        self,
        query: str,
        filter_dict: Optional[Dict[str, Any]] = None,
        top_k: int = 15,
    ) -> List[Tuple[str, float]]:
        """
        Tìm kiếm Top Parent Documents bằng BM25:
        1. Tokenize query tiếng Việt.
        2. Truy xuất Top Child Chunks từ bm25s.
        3. Áp dụng bộ lọc Metadata (status, domain, fee_kind, academic_year, ...).
        4. Gom nhóm theo Parent ID và lấy max score của Child tương ứng.
        5. Trả về danh sách (parent_id, bm25_score) giảm dần.
        """
        if not self.is_indexed() or not query or not query.strip():
            return []

        query_tokens = tokenize_vietnamese(query)
        if not query_tokens:
            return []

        search_k = min(len(self.records), max(top_k * 5, 50))
        try:
            doc_indices, scores = self.retriever.retrieve(
                [query_tokens],
                k=search_k,
                return_as="tuple",
            )
        except Exception as exc:
            logger.error(f"Lỗi truy xuất BM25: {exc}", exc_info=True)
            return []

        if len(doc_indices) == 0 or len(doc_indices[0]) == 0:
            return []

        matched_indices = doc_indices[0]
        matched_scores = scores[0]

        parent_scores: Dict[str, float] = {}

        for idx, score in zip(matched_indices, matched_scores):
            if score <= 0.0:
                continue

            if idx < 0 or idx >= len(self.records):
                continue

            record = self.records[idx]
            if filter_dict:
                matches = True
                for k, v in filter_dict.items():
                    if v is not None and record.metadata.get(k) != v:
                        matches = False
                        break
                if not matches:
                    continue

            pid = record.parent_id
            if pid not in parent_scores or score > parent_scores[pid]:
                parent_scores[pid] = float(score)

        sorted_parents = sorted(
            parent_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        return sorted_parents[:top_k]

    def save(self, directory: str | Path) -> None:
        """Lưu snapshot BM25 index và danh sách metadata ra đĩa."""
        target_dir = Path(directory)
        target_dir.mkdir(parents=True, exist_ok=True)

        if self.retriever is not None:
            try:
                self.retriever.save(target_dir)
            except Exception as exc:
                logger.warning(f"bm25s native save warning: {exc}")

        manifest = {
            "index_version": self.index_version,
            "num_records": len(self.records),
            "records": [r.to_dict() for r in self.records],
        }
        with open(target_dir / "records.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        logger.info(f"Đã lưu BM25 snapshot vào {target_dir} ({len(self.records)} records)")

    def load(self, directory: str | Path) -> bool:
        """Nạp snapshot BM25 index từ đĩa."""
        target_dir = Path(directory)
        records_file = target_dir / "records.json"
        if not records_file.exists():
            logger.info(f"Không tìm thấy file snapshot BM25 tại {target_dir}")
            return False

        try:
            with open(records_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            self.index_version = manifest.get("index_version", "")
            raw_records = manifest.get("records", [])
            self.records = [BM25ChildRecord.from_dict(d) for d in raw_records]

            if target_dir.exists() and (target_dir / "params.index.json").exists():
                try:
                    self.retriever = bm25s.BM25.load(target_dir, load_corpus=False)
                    logger.info(f"Đã nạp BM25 snapshot từ {target_dir} ({len(self.records)} records)")
                    return True
                except Exception as load_err:
                    logger.warning(f"Lỗi nạp bm25s model: {load_err}, đang re-build từ records...")
                    self.build_index(self.records)
                    return True
            else:
                self.build_index(self.records)
                return True
        except Exception as exc:
            logger.error(f"Lỗi nạp BM25 snapshot từ {target_dir}: {exc}", exc_info=True)
            return False
