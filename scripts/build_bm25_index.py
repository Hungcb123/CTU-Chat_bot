"""Script xây dựng hoặc đồng bộ lại toàn bộ BM25 index từ thư mục data/markdown."""

import hashlib
import json
import logging
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from app.services.bm25_service import VietnameseBM25Index, BM25ChildRecord
from app.services.document_metadata import get_document_metadata

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [BM25_BUILDER] - %(levelname)s - %(message)s",
)
logger = logging.getLogger("bm25_builder")


class SmartChildSplitter(RecursiveCharacterTextSplitter):
    """Splitter thông minh cho Child Chunks (Bảng + Prose)."""

    def split_text(self, text: str):
        if "Nội dung chi tiết:\n|" in text or text.strip().startswith("|"):
            if "Nội dung chi tiết:\n" in text:
                prefix, table_text = text.split("Nội dung chi tiết:\n", 1)
                prefix += "Nội dung chi tiết:\n"
            else:
                prefix = ""
                table_text = text

            lines = table_text.split("\n")
            is_separator = lambda s: bool(re.fullmatch(r"\|?[\s:\-|]+\|?", s)) and "-" in s and "|" in s

            if len(lines) >= 2 and is_separator(lines[1]):
                header = lines[:2]
                body = lines[2:]
            else:
                header = lines[:1]
                body = lines[1:]

            chunks = []
            current_chunk_lines = list(header)
            last_category_row = None
            current_len = len(prefix) + sum(len(l) + 1 for l in current_chunk_lines)

            for line in body:
                if not line.strip():
                    continue

                cells = [c.strip() for c in line.split("|")[1:-1] if c.strip()]
                is_category_row = len(cells) <= 2

                if is_category_row:
                    last_category_row = line

                if current_len + len(line) + 1 > self._chunk_size and len(current_chunk_lines) > len(header):
                    chunks.append(prefix + "\n".join(current_chunk_lines))
                    current_chunk_lines = list(header)
                    if last_category_row and not is_category_row:
                        current_chunk_lines.append(last_category_row)
                    current_len = len(prefix) + sum(len(l) + 1 for l in current_chunk_lines)

                current_chunk_lines.append(line)
                current_len += len(line) + 1

            if len(current_chunk_lines) > len(header):
                chunks.append(prefix + "\n".join(current_chunk_lines))

            return chunks
        else:
            marker = "Nội dung chi tiết:\n"
            if marker in text:
                prefix, content = text.split(marker, 1)
                prefix = prefix + marker
                return [
                    chunk if chunk.startswith(prefix) else prefix + chunk
                    for chunk in super().split_text(content)
                ]
            return super().split_text(text)


def _is_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.count("|") >= 2


def _is_table_separator(line: str) -> bool:
    s = line.strip()
    return bool(re.fullmatch(r"\|?[\s:\-|]+\|?", s)) and "-" in s and "|" in s


def _segment_by_table(text: str):
    lines = text.split("\n")
    segments = []
    buffer = []
    in_table = False
    for line in lines:
        is_tbl = _is_table_row(line)
        if is_tbl and not in_table:
            if buffer:
                segments.append(("prose", "\n".join(buffer)))
            buffer = [line]
            in_table = True
        elif not is_tbl and in_table:
            segments.append(("table", "\n".join(buffer)))
            buffer = [line]
            in_table = False
        else:
            buffer.append(line)
    if buffer:
        segments.append(("table" if in_table else "prose", "\n".join(buffer)))
    return segments


def _chunk_table(table_text: str, parent_chunk_size: int = 2800):
    if len(table_text) <= parent_chunk_size:
        return [table_text]
    lines = table_text.split("\n")
    if len(lines) >= 2 and _is_table_separator(lines[1]):
        header = lines[:2]
        body = lines[2:]
    else:
        header = lines[:1]
        body = lines[1:]
    header_text = "\n".join(header)
    chunks = []
    current = list(header)
    current_len = len(header_text)
    for line in body:
        if current_len + len(line) + 1 > parent_chunk_size and len(current) > len(header):
            chunks.append("\n".join(current))
            current = list(header)
            current_len = len(header_text)
        current.append(line)
        current_len += len(line) + 1
    if len(current) > len(header):
        chunks.append("\n".join(current))
    return chunks


def _business_metadata_label(metadata):
    fee_labels = {
        "actual_tuition": "HỌC PHÍ THỰC TẾ",
        "exemption_basis": "CƠ SỞ TÍNH MIỄN GIẢM",
        "not_applicable": "KHÔNG ÁP DỤNG",
    }
    domain_labels = {
        "tuition": "HỌC PHÍ",
        "scholarship": "HỌC BỔNG",
        "student_loan": "VAY VỐN SINH VIÊN",
        "social_support": "HỖ TRỢ XÃ HỘI",
        "other": "TÀI LIỆU KHÁC",
    }
    content_labels = {
        "rate_table": "BẢNG MỨC THU",
        "exemption_policy": "QUY ĐỊNH MIỄN GIẢM",
        "policy": "CHÍNH SÁCH",
        "procedure": "THỦ TỤC",
        "announcement": "THÔNG BÁO",
        "form": "BIỂU MẪU",
        "other": "NỘI DUNG KHÁC",
    }
    parts = []
    domain = metadata.get("domain")
    content_kind = metadata.get("content_kind")
    fee_kind = metadata.get("fee_kind")
    if domain:
        parts.append(f"CHỦ ĐỀ: {domain_labels.get(domain, str(domain).upper())}")
    if content_kind:
        parts.append(f"NỘI DUNG: {content_labels.get(content_kind, str(content_kind).upper())}")
    if fee_kind and fee_kind != "not_applicable":
        parts.append(f"LOẠI MỨC: {fee_labels.get(fee_kind, str(fee_kind).upper())}")
    if metadata.get("academic_year"):
        parts.append(f"NĂM HỌC: {metadata['academic_year']}")
    if metadata.get("source"):
        parts.append(f"NGUỒN: {metadata['source']}")
    return f"[METADATA | {' | '.join(parts)}]" if parts else ""


def build_all_bm25_indexes(output_dirs=None):
    if output_dirs is None:
        output_dirs = [
            PROJECT_ROOT / "parent_doc_storage" / "bm25_index",
            PROJECT_ROOT / "qdrant_storage" / "bm25_index",
        ]

    markdown_dir = PROJECT_ROOT / "data" / "markdown"

    headers_to_split_on = [
        ("#", "Header_1_QuyetDinh"),
        ("##", "Header_2_ChuyenMuc"),
        ("###", "Header_3_NguoiKy"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False
    )
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2800, chunk_overlap=100, separators=["\n\n", "\n", ".", " "]
    )
    child_splitter = SmartChildSplitter(
        chunk_size=400, chunk_overlap=50, separators=["\n\n", "\n", ".", " "]
    )

    all_child_records: list[BM25ChildRecord] = []

    md_files = sorted(markdown_dir.glob("*.md"))
    logger.info(f"Tìm thấy {len(md_files)} file markdown. Bắt đầu xử lý...")

    for file_path in md_files:
        source = file_path.name
        raw_text = file_path.read_text(encoding="utf-8")
        
        try:
            record = get_document_metadata(source)
            business_metadata = record.model_dump(mode="json", exclude_none=True) if hasattr(record, "model_dump") else dict(record)
        except Exception:
            business_metadata = {"source": source}

        # Temporal extraction
        effective_date = "1970-01-01"
        timestamp = 0
        match_vn = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", raw_text, re.IGNORECASE)
        match_short = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", raw_text)
        if match_vn:
            d, m, y = match_vn.groups()
            effective_date = f"{y}-{int(m):02d}-{int(d):02d}"
        elif match_short:
            d, m, y = match_short.groups()
            effective_date = f"{y}-{int(m):02d}-{int(d):02d}"
        if effective_date != "1970-01-01":
            try:
                dt = datetime.strptime(effective_date, "%Y-%m-%d")
                timestamp = int(dt.timestamp())
            except ValueError:
                pass

        technical_metadata = {
            "source": source,
            "doc_type": "policy",
            "effective_date": effective_date,
            "timestamp": timestamp,
            "status": "active",
        }

        raw_parent_docs = md_splitter.split_text(raw_text)
        for doc in raw_parent_docs:
            doc.metadata.update(business_metadata)
            doc.metadata.update(technical_metadata)
            doc.metadata["metadata_label"] = _business_metadata_label(doc.metadata)

        # Split parents preserving tables
        parent_docs = []
        for doc in raw_parent_docs:
            header_context = " ".join([f"{k}: {v}" for k, v in doc.metadata.items() if k.startswith("Header")])
            metadata_label = doc.metadata.get("metadata_label", "")
            prefix_parts = []
            if metadata_label:
                prefix_parts.append(metadata_label)
            if header_context:
                prefix_parts.append(f"Ngữ cảnh tài liệu - {header_context}")
            prefix_text = "\n".join(prefix_parts)
            if prefix_text:
                prefix_text += "\nNội dung chi tiết:\n"

            for seg_type, seg_text in _segment_by_table(doc.page_content):
                if seg_type == "table":
                    for tbl in _chunk_table(seg_text):
                        if tbl.strip():
                            parent_docs.append(Document(page_content=prefix_text + tbl, metadata=dict(doc.metadata)))
                else:
                    for piece in parent_splitter.split_text(seg_text):
                        if len(piece.strip()) >= 50:
                            parent_docs.append(Document(page_content=prefix_text + piece, metadata=dict(doc.metadata)))

        # Split into children and create BM25 records
        for pdoc in parent_docs:
            parent_id = str(uuid.uuid4())
            sub_docs = child_splitter.split_documents([pdoc])
            for sdoc in sub_docs:
                all_child_records.append(
                    BM25ChildRecord(
                        child_text=sdoc.page_content,
                        parent_id=parent_id,
                        metadata=dict(sdoc.metadata),
                    )
                )

    logger.info(f"Tổng cộng đã tạo {len(all_child_records)} Child Chunks từ {len(md_files)} tài liệu.")

    # Build and persist BM25 index to targets
    index = VietnameseBM25Index()
    index.build_index(all_child_records)

    for out_dir in output_dirs:
        out_dir = Path(out_dir)
        index.save(out_dir)
        logger.info(f"✅ Đã lưu BM25 Index vào: {out_dir}")

    return index


if __name__ == "__main__":
    index = build_all_bm25_indexes()
    print("\n--- TEST TRUY VẤN BM25 ---")
    test_queries = [
        "Học phí ngành Kỹ thuật phần mềm",
        "Miễn giảm học phí cho sinh viên khuyết tật",
        "Học bổng khuyến khích học tập loại xuất sắc",
    ]
    for q in test_queries:
        print(f"\nQuery: '{q}'")
        res = index.search(q, top_k=3)
        print(f"Kết quả ({len(res)} parents):", res)
