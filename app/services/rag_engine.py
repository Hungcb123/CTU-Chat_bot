"""
=============================================================================
KIẾN TRÚC RAG NÂNG CAO (ADVANCED RAG PIPELINE)
Tệp này đóng vai trò là "Trái tim" của hệ thống truy xuất dữ liệu, giải quyết 
vấn đề mất ngữ cảnh bằng chiến lược: Small-to-Big (Parent-Child) & Re-ranking.

[QUY TRÌNH NẠP DỮ LIỆU - INGESTION]
1. Đọc Markdown: Trích xuất "ngày tháng năm" ban hành làm Metadata (Temporal).
2. Cắt Parent: Cắt tài liệu thành các khối logic lớn theo thẻ Markdown (#, ##).
3. Cắt Child: Băm Parent thành các mảnh siêu nhỏ (400 chars) để tăng độ nhạy Vector.
4. Nhúng & Lưu trữ: 
   - Mã hóa Child thành Vector và lưu vào Qdrant DB (để search nhanh).
   - Lưu Parent nguyên bản vào LocalShelveStore (lưu ổ cứng, tránh tràn RAM).

[QUY TRÌNH TRUY XUẤT - RETRIEVAL]
1. Tìm kiếm cơ sở (Vector Search): Quét Qdrant tìm Top 10 mảnh Child khớp nhất, 
   từ đó tự động lấy ra 10 khối Parent to tướng chứa các mảnh Child đó.
2. Chấm điểm lại (Re-ranking): Đưa 10 khối Parent qua mô hình Cross-Encoder 
   chuyên dụng để chấm điểm lại bằng AI. 
3. Xuất kết quả: Chỉ giữ lại Top 3 văn bản xuất sắc nhất để gửi cho LLM.
=============================================================================
"""
import hashlib
import logging
import re
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Sequence, Optional, Iterator, Tuple
from pathlib import Path
import shelve

# Langchain Core Modules
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_core.stores import InMemoryStore, BaseStore

# Import thêm các class để làm Re-ranking
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

# Giả lập Vector DB và Embedding Model cho môi trường Local
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    HnswConfigDiff,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
    FilterSelector,
)

# Cấu hình Logging cấp độ Enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CHUNKING_ENGINE] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SemanticChunker")

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import operator
from collections.abc import Sequence as AbcSequence
from langchain_core.callbacks import Callbacks


DEFAULT_QDRANT_URL = "http://localhost:6333"
DEFAULT_QDRANT_TIMEOUT_SECONDS = int(os.getenv("QDRANT_TIMEOUT_SECONDS", "60"))
LEGACY_COLLECTION_NAME = "ctu_scholarship_docs_v3"
DEFAULT_COLLECTION_ALIAS = "ctu_scholarship_docs_current"
VECTOR_SIZE = 768
DEFAULT_SEARCH_K = 15
DEFAULT_RERANK_TOP_N = 6

# LangChain's QdrantVectorStore nests Document.metadata under the `metadata`
# payload key. Index and filter the fully-qualified paths below.
PAYLOAD_INDEX_FIELDS = (
    "metadata.status",
    "metadata.domain",
    "metadata.content_kind",
    "metadata.fee_kind",
    "metadata.academic_year",
    "metadata.index_version",
    "metadata.source",
    "metadata.ingest_run_id",
)


class RetrievalLane(str, Enum):
    """Business-specific retrieval lanes used by the chat intent router."""

    DEFAULT = "default"
    ACTUAL_TUITION = "actual_tuition"
    EXEMPTION_BASIS = "exemption_basis"
    EXEMPTION_POLICY = "exemption_policy"
    SCHOLARSHIP = "scholarship"
    STUDENT_LOAN = "student_loan"


LANE_METADATA: Dict[RetrievalLane, Dict[str, str]] = {
    RetrievalLane.ACTUAL_TUITION: {
        "domain": "tuition",
        "content_kind": "rate_table",
        "fee_kind": "actual_tuition",
    },
    RetrievalLane.EXEMPTION_BASIS: {
        "domain": "tuition",
        "content_kind": "rate_table",
        "fee_kind": "exemption_basis",
    },
    RetrievalLane.EXEMPTION_POLICY: {
        "domain": "tuition",
        "content_kind": "exemption_policy",
    },
    RetrievalLane.SCHOLARSHIP: {
        "domain": "scholarship",
    },
    RetrievalLane.STUDENT_LOAN: {
        "domain": "student_loan",
    },
}


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

class TemporalCrossEncoderReranker(CrossEncoderReranker):
    """Reranker có ưu tiên MỀM theo thời gian (tie-break).

    Vẫn xếp hạng chính theo điểm Cross-Encoder (độ liên quan). Chỉ khi hai
    tài liệu có điểm GẦN BẰNG NHAU (chênh lệch <= score_tolerance) thì mới
    ưu tiên tài liệu có 'timestamp' mới hơn. Nhờ vậy văn bản cũ nhưng vẫn
    khớp nội dung không bị loại oan, mà bản mới cùng chủ đề được đẩy lên trên.
    """
    score_tolerance: float = 0.05

    def compress_documents(
        self,
        documents: AbcSequence[Document],
        query: str,
        callbacks: Callbacks | None = None,
    ) -> AbcSequence[Document]:
        scores = self.model.score([(query, doc.page_content) for doc in documents])
        docs_with_scores = list(zip(documents, scores))
        # Sắp theo (điểm liên quan giảm dần, timestamp giảm dần) để tie-break sơ bộ
        ranked = sorted(
            docs_with_scores,
            key=lambda ds: (ds[1], ds[0].metadata.get("timestamp", 0) or 0),
            reverse=True,
        )
        # Trong từng "rổ" điểm gần bằng nhau, ưu tiên bản mới hơn (timestamp lớn hơn)
        reordered: List[Tuple[Document, float]] = []
        bucket: List[Tuple[Document, float]] = []
        bucket_top: Optional[float] = None
        for doc, score in ranked:
            if bucket_top is None or (bucket_top - score) <= self.score_tolerance:
                bucket.append((doc, score))
                bucket_top = score if bucket_top is None else bucket_top
            else:
                bucket.sort(key=lambda ds: ds[0].metadata.get("timestamp", 0) or 0, reverse=True)
                reordered.extend(bucket)
                bucket = [(doc, score)]
                bucket_top = score
        if bucket:
            bucket.sort(key=lambda ds: ds[0].metadata.get("timestamp", 0) or 0, reverse=True)
            reordered.extend(bucket)
        return [doc for doc, _ in reordered[: self.top_n]]

from sqlalchemy.orm import Session
from app.core.database import SyncSessionLocal
from app.models.schema import ParentDocument as DBParentDocument
import json

class SmartChildSplitter(RecursiveCharacterTextSplitter):
    """
    Splitter thông minh:
    - Nếu là văn bản thường (prose), dùng RecursiveCharacterTextSplitter.
    - Nếu là Bảng (table), tự động băm theo từng dòng, NHƯNG luôn đính kèm:
      1. Prefix text (ngữ cảnh Header).
      2. Tiêu đề cột (Table Headers).
      3. Dòng Category gần nhất (Ví dụ: "Chương trình chất lượng cao").
    Đảm bảo 100% ngữ cảnh semantic không bao giờ bị mất!
    """
    def split_text(self, text: str) -> List[str]:
        if "Nội dung chi tiết:\n|" in text or text.strip().startswith("|"):
            if "Nội dung chi tiết:\n" in text:
                prefix, table_text = text.split("Nội dung chi tiết:\n", 1)
                prefix += "Nội dung chi tiết:\n"
            else:
                prefix = ""
                table_text = text

            lines = table_text.split("\n")
            is_separator = lambda s: bool(re.fullmatch(r'\|?[\s:\-|]+\|?', s)) and '-' in s and '|' in s
            
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
                    
                cells = [c.strip() for c in line.split('|')[1:-1] if c.strip()]
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
            # Recursive splitting would otherwise keep the metadata/header
            # prefix only on the first child. Re-inject it into every prose
            # child so each embedding carries the business distinction.
            marker = "Nội dung chi tiết:\n"
            if marker in text:
                prefix, content = text.split(marker, 1)
                prefix = prefix + marker
                return [
                    chunk if chunk.startswith(prefix) else prefix + chunk
                    for chunk in super().split_text(content)
                ]
            return super().split_text(text)

class PostgresDocStore(BaseStore[str, Document]):
    """Kho lưu trữ Parent Document trên PostgreSQL để đảm bảo an toàn & tốc độ cao."""
    def __init__(self):
        # Không cần path nữa vì lưu thẳng vào DB
        pass

    def _get_session(self) -> Session:
        return SyncSessionLocal()
        
    def mset(self, key_value_pairs: Sequence[Tuple[str, Document]]) -> None:
        with self._get_session() as session:
            for key, doc in key_value_pairs:
                db_doc = session.query(DBParentDocument).filter_by(id=key).first()
                if not db_doc:
                    db_doc = DBParentDocument(
                        id=key, 
                        content=doc.page_content, 
                        metadata_json=doc.metadata
                    )
                    session.add(db_doc)
                else:
                    db_doc.content = doc.page_content
                    db_doc.metadata_json = doc.metadata
            session.commit()
                
    def mget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        with self._get_session() as session:
            db_docs = session.query(DBParentDocument).filter(DBParentDocument.id.in_(keys)).all()
            doc_map = {db_doc.id: Document(page_content=db_doc.content, metadata=db_doc.metadata_json or {}) for db_doc in db_docs}
            return [doc_map.get(k) for k in keys]
            
    def mdelete(self, keys: Sequence[str]) -> None:
        with self._get_session() as session:
            session.query(DBParentDocument).filter(DBParentDocument.id.in_(keys)).delete(synchronize_session=False)
            session.commit()
                    
    def yield_keys(self, prefix: Optional[str] = None) -> Iterator[str]:
        with self._get_session() as session:
            query = session.query(DBParentDocument.id)
            if prefix:
                query = query.filter(DBParentDocument.id.startswith(prefix))
            for row in query.all():
                yield row[0]

    def delete_by_ingest(self, source: str, ingest_run_id: Optional[str] = None) -> int:
        """Delete only parent rows produced by one source/ingestion run."""
        with self._get_session() as session:
            query = session.query(DBParentDocument).filter(
                DBParentDocument.metadata_json["source"].astext == source
            )
            if ingest_run_id is not None:
                query = query.filter(
                    DBParentDocument.metadata_json["ingest_run_id"].astext
                    == ingest_run_id
                )
            deleted = query.delete(synchronize_session=False)
            session.commit()
            return int(deleted or 0)

class AdvancedChunkingEngine:
    """
    Engine phân mảnh dữ liệu áp dụng chiến lược Small-to-Big.
    Khắc phục triệt để hiện tượng mất ngữ cảnh của LLM.
    """
    def __init__(
        self,
        persist_dir: str = "./parent_doc_storage",
        *,
        qdrant_url: Optional[str] = None,
        collection_name: Optional[str] = None,
        index_version: Optional[str] = None,
        create_collection_if_missing: Optional[bool] = None,
        load_reranker: bool = True,
        metadata_filter_enabled: Optional[bool] = None,
        metadata_catalog_path: Optional[str] = None,
    ):
        self.persist_dir = persist_dir
        configured_index_version = index_version or os.getenv("RAG_INDEX_VERSION")
        self._index_version_is_explicit = bool(configured_index_version)
        self.index_version = configured_index_version or ""
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", DEFAULT_QDRANT_URL)
        configured_alias = os.getenv("QDRANT_COLLECTION_ALIAS")
        configured_collection = os.getenv("QDRANT_COLLECTION_NAME")
        self.collection_name = (
            collection_name
            or configured_alias
            or configured_collection
            or LEGACY_COLLECTION_NAME
        )
        self.collection_alias = configured_alias or DEFAULT_COLLECTION_ALIAS
        self.metadata_filter_enabled = (
            _env_flag("RAG_METADATA_FILTER_ENABLED", False)
            if metadata_filter_enabled is None
            else metadata_filter_enabled
        )
        self.metadata_catalog_path = metadata_catalog_path or os.getenv(
            "DOCUMENT_METADATA_PATH"
        )

        # A configured alias must already exist. Creating a physical collection
        # with the alias name would make a later atomic alias swap impossible.
        if create_collection_if_missing is None:
            create_collection_if_missing = not (
                collection_name is None and configured_alias is not None
            )
        
        # 1. CẤU HÌNH PARENT SPLITTER (Trích xuất theo Cấu trúc Markdown)
        # Hệ thống sẽ tự động bắt các thẻ này và biến chúng thành Metadata
        self.headers_to_split_on = [
            ("#", "Header_1_QuyetDinh"),
            ("##", "Header_2_ChuyenMuc"),
            ("###", "Header_3_NguoiKy"),
        ]
        self.md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False # GIỮ LẠI Header trong Text để LLM hiểu bối cảnh
        )
        
        # 1.5 CẤU HÌNH PARENT SPLITTER CẤP 2 (Máy chém Double-Split)
        # Chỉ chặt block vượt ngưỡng; block nhỏ giữ nguyên vẹn (prose + bảng + header đi cùng nhau)
        self.parent_chunk_size = 2800
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.parent_chunk_size,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " "]
        )
        
        # 2. CẤU HÌNH CHILD SPLITTER (Độ phân giải Vector cao)
        # Chunk cực nhỏ (400 chars) để thuật toán Cosine Similarity đối sánh cực nhạy
        self.child_splitter = SmartChildSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "] # Ưu tiên cắt theo đoạn/dòng trước
        )
        
        # 3. KHỞI TẠO HẠ TẦNG LƯU TRỮ (Storage Infrastructure)
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        self.doc_store = PostgresDocStore()
        self.qdrant_client = QdrantClient(
            url=self.qdrant_url,
            timeout=DEFAULT_QDRANT_TIMEOUT_SECONDS,
        )
        if not self.index_version:
            self.index_version = self._resolve_active_index_version()
        
        # Tạo Collection (Bảng) nếu chưa có. 
        # vietnamese-bi-encoder sinh ra Vector 768 chiều, khoảng cách Cosine.
        if not self.qdrant_client.collection_exists(self.collection_name):
            if not create_collection_if_missing:
                raise RuntimeError(
                    f"Qdrant alias/collection '{self.collection_name}' does not exist. "
                    "Activate an indexed collection before enabling QDRANT_COLLECTION_ALIAS."
                )
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                hnsw_config=HnswConfigDiff(m=16, ef_construct=100), # Cấu hình thuật toán HNSW
            )
        self.ensure_payload_indexes()

        # Trỏ Vector Store về Qdrant
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name,
            embedding=HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder"),
        )
        
        # 4. ORCHESTRATOR: BỘ ĐIỀU PHỐI PARENT-CHILD & RE-RANKING
        # Bước 6 (Theo lý thuyết): Tìm kiếm cơ sở (Lưới rộng Top 15)
        self.base_retriever = ParentDocumentRetriever(
            vectorstore=self.vector_store,
            docstore=self.doc_store,
            child_splitter=self.child_splitter,
            search_kwargs={
                "k": DEFAULT_SEARCH_K,
                "filter": self.build_filter(metadata_filter_enabled=False),
            }
        )

        # Bước 7 (Theo lý thuyết): Xếp hạng lại (Re-ranking) bằng Cross-Encoder
        self.cross_encoder = None
        self.reranker = None
        if load_reranker:
            logger.info("Đang nạp mô hình Cross-Encoder (Re-ranker) vào hệ thống...")
            self.cross_encoder = HuggingFaceCrossEncoder(
                model_name="BAAI/bge-reranker-v2-m3",
                model_kwargs={"device": os.getenv("RAG_RERANKER_DEVICE", "cuda")},
            )
            # BẮT BUỘC: Giới hạn số token đưa vào mô hình để tránh lỗi CUDA Out of Memory (GPU 4GB)
            self.cross_encoder.client.max_length = 512
            self.reranker = TemporalCrossEncoderReranker(
                model=self.cross_encoder,
                top_n=DEFAULT_RERANK_TOP_N,
                score_tolerance=0.05,
            )

        # Nối Base Retriever và Reranker lại thành một Pipeline truy xuất hoàn chỉnh
        self.retriever = (
            ContextualCompressionRetriever(
                base_compressor=self.reranker,
                base_retriever=self.base_retriever,
            )
            if self.reranker is not None
            else self.base_retriever
        )

    def ensure_payload_indexes(self) -> None:
        """Create the keyword indexes used by all business metadata filters."""
        collection = self.qdrant_client.get_collection(self.collection_name)
        existing = set((collection.payload_schema or {}).keys())
        for field_name in PAYLOAD_INDEX_FIELDS:
            if field_name in existing:
                continue
            self.qdrant_client.create_payload_index(
                collection_name=self.collection_name,
                field_name=field_name,
                field_schema=PayloadSchemaType.KEYWORD,
                wait=True,
            )

    @staticmethod
    def _index_version_from_collection_name(collection_name: str) -> str:
        if collection_name == LEGACY_COLLECTION_NAME:
            return "legacy-v3"
        prefix = "ctu_scholarship_docs_"
        if collection_name.startswith(prefix):
            return collection_name[len(prefix) :]
        return collection_name

    def _resolve_active_index_version(self) -> str:
        """Resolve an alias at ingest time so an alias swap cannot tag uploads stale."""

        if self._index_version_is_explicit and self.index_version:
            return self.index_version
        aliases = {
            item.alias_name: item.collection_name
            for item in self.qdrant_client.get_aliases().aliases
        }
        physical_name = aliases.get(self.collection_name, self.collection_name)
        resolved = self._index_version_from_collection_name(physical_name)
        self.index_version = resolved
        return resolved

    @staticmethod
    def build_filter(
        *,
        lane: RetrievalLane | str | None = None,
        fee_kind: Optional[str] = None,
        content_kind: Optional[str] = None,
        domain: Optional[str] = None,
        academic_year: Optional[str] = None,
        metadata_filter_enabled: bool = True,
    ) -> Filter:
        """Build an immutable Qdrant filter for one retrieval request.

        The active-status guard always applies. Business fields only apply when
        the metadata feature flag is enabled, allowing a safe alias-first rollout
        from the legacy collection.
        """
        must = [
            FieldCondition(
                key="metadata.status",
                match=MatchValue(value="active"),
            )
        ]
        if not metadata_filter_enabled:
            return Filter(must=must)

        resolved: Dict[str, str] = {}
        if lane is not None:
            try:
                lane_value = lane if isinstance(lane, RetrievalLane) else RetrievalLane(lane)
            except ValueError as exc:
                raise ValueError(f"Unsupported retrieval lane: {lane}") from exc
            resolved.update(LANE_METADATA.get(lane_value, {}))

        # Explicit request fields override lane defaults. This makes the public
        # API usable for non-tuition domains without adding a lane per domain.
        for key, value in (
            ("domain", domain),
            ("content_kind", content_kind),
            ("fee_kind", fee_kind),
            ("academic_year", academic_year),
        ):
            if value is not None:
                resolved[key] = value

        must.extend(
            FieldCondition(
                key=f"metadata.{key}",
                match=MatchValue(value=value),
            )
            for key, value in resolved.items()
        )
        return Filter(must=must)

    def _request_retriever(
        self,
        *,
        qdrant_filter: Filter,
        top_n: int,
        use_reranker: bool = True,
    ):
        """Create request-scoped retrievers while sharing stores and models."""
        base_retriever = ParentDocumentRetriever(
            vectorstore=self.vector_store,
            docstore=self.doc_store,
            child_splitter=self.child_splitter,
            search_kwargs={"k": DEFAULT_SEARCH_K, "filter": qdrant_filter},
        )
        if self.cross_encoder is None or not use_reranker:
            return base_retriever
        compressor = TemporalCrossEncoderReranker(
            model=self.cross_encoder,
            top_n=top_n,
            score_tolerance=0.05,
        )
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever,
        )

    def retrieve(
        self,
        query: str,
        *,
        lane: RetrievalLane | str | None = None,
        fee_kind: Optional[str] = None,
        content_kind: Optional[str] = None,
        domain: Optional[str] = None,
        academic_year: Optional[str] = None,
        top_n: Optional[int] = None,
        metadata_filter_enabled: Optional[bool] = None,
        use_reranker: bool = True,
    ) -> List[Document]:
        """Retrieve documents with a filter isolated to this request."""
        if not query or not query.strip():
            return []
        enabled = (
            self.metadata_filter_enabled
            if metadata_filter_enabled is None
            else metadata_filter_enabled
        )
        result_limit = top_n or DEFAULT_RERANK_TOP_N
        if result_limit < 1:
            raise ValueError("top_n must be at least 1")
        qdrant_filter = self.build_filter(
            lane=lane,
            fee_kind=fee_kind,
            content_kind=content_kind,
            domain=domain,
            academic_year=academic_year,
            metadata_filter_enabled=enabled,
        )
        request_retriever = self._request_retriever(
            qdrant_filter=qdrant_filter,
            top_n=result_limit,
            use_reranker=use_reranker,
        )
        documents = list(request_retriever.invoke(query))
        return documents[:result_limit]

    def purge_document(
        self,
        source: str,
        ingest_run_id: Optional[str] = None,
    ) -> Tuple[int, int]:
        """Purge Qdrant children and PostgreSQL parents for a source/run.

        Returns `(qdrant_operations, deleted_parent_rows)`. Passing an ingestion
        run ID is strongly preferred so a failed replacement cannot remove the
        previously active version of the same source.
        """
        if ingest_run_id is None:
            logger.warning(
                "Broad purge requested for every indexed version of source=%s",
                source,
            )
        must = [
            FieldCondition(
                key="metadata.source",
                match=MatchValue(value=source),
            )
        ]
        if ingest_run_id is not None:
            must.append(
                FieldCondition(
                    key="metadata.ingest_run_id",
                    match=MatchValue(value=ingest_run_id),
                )
            )

        qdrant_operations = 0
        rollback_errors: List[str] = []
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=FilterSelector(filter=Filter(must=must)),
                wait=True,
            )
            qdrant_operations = 1
        except Exception as exc:
            rollback_errors.append(f"Qdrant: {exc}")
            logger.exception(
                "Failed to purge Qdrant points for source=%s run=%s",
                source,
                ingest_run_id,
            )

        deleted_parents = 0
        try:
            deleted_parents = self.doc_store.delete_by_ingest(source, ingest_run_id)
        except Exception as exc:
            rollback_errors.append(f"PostgreSQL: {exc}")
            logger.exception(
                "Failed to purge parent rows for source=%s run=%s",
                source,
                ingest_run_id,
            )
        if rollback_errors:
            raise RuntimeError(
                "Document rollback was incomplete: " + "; ".join(rollback_errors)
            )
        return qdrant_operations, deleted_parents

    def clear_database(self):
        """Prevent the legacy destructive reindex path from being used."""
        raise RuntimeError(
            "clear_database() is disabled. Use scripts/reindex_all.py "
            "preflight/build/validate/activate for a blue-green reindex."
        )

    @staticmethod
    def _is_table_row(line: str) -> bool:
        s = line.strip()
        return s.startswith("|") and s.count("|") >= 2

    @staticmethod
    def _is_table_separator(line: str) -> bool:
        # Dòng phân cách bảng, ví dụ: |---|---| hoặc |:--|--:|
        s = line.strip()
        return bool(re.fullmatch(r'\|?[\s:\-|]+\|?', s)) and '-' in s and '|' in s

    def _segment_by_table(self, text: str) -> List[Tuple[str, str]]:
        """Tách một block thành các đoạn xen kẽ ('prose', text) và ('table', text)."""
        lines = text.split("\n")
        segments: List[Tuple[str, str]] = []
        buffer: List[str] = []
        in_table = False
        for line in lines:
            is_tbl = self._is_table_row(line)
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

    def _chunk_table(self, table_text: str) -> List[str]:
        """Giữ bảng nguyên khối. Nếu bảng dài quá ngưỡng thì cắt theo dòng
        và tiêm lại 2 dòng header (tiêu đề cột + phân cách) vào mỗi mảnh."""
        if len(table_text) <= self.parent_chunk_size:
            return [table_text]
        lines = table_text.split("\n")
        if len(lines) >= 2 and self._is_table_separator(lines[1]):
            header = lines[:2]
            body = lines[2:]
        else:
            header = lines[:1]
            body = lines[1:]
        header_text = "\n".join(header)
        chunks: List[str] = []
        current = list(header)
        current_len = len(header_text)
        for line in body:
            if current_len + len(line) + 1 > self.parent_chunk_size and len(current) > len(header):
                chunks.append("\n".join(current))
                current = list(header)
                current_len = len(header_text)
            current.append(line)
            current_len += len(line) + 1
        if len(current) > len(header):
            chunks.append("\n".join(current))
        return chunks

    @staticmethod
    def _business_metadata_label(metadata: Dict[str, Any]) -> str:
        """Create a compact label that is visible to embeddings and the LLM."""
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
            parts.append(
                f"NỘI DUNG: {content_labels.get(content_kind, str(content_kind).upper())}"
            )
        if fee_kind and fee_kind != "not_applicable":
            parts.append(f"LOẠI MỨC: {fee_labels.get(fee_kind, str(fee_kind).upper())}")
        if metadata.get("academic_year"):
            parts.append(f"NĂM HỌC: {metadata['academic_year']}")
        if metadata.get("source"):
            parts.append(f"NGUỒN: {metadata['source']}")
        return f"[METADATA | {' | '.join(parts)}]" if parts else ""

    def _catalog_metadata(self, source: str) -> Dict[str, Any]:
        """Load validated business metadata through the catalog service."""
        from app.services.document_metadata import (
            METADATA_SCHEMA_VERSION,
            get_document_metadata,
        )

        if self.metadata_catalog_path:
            record = get_document_metadata(
                source,
                catalog_path=Path(self.metadata_catalog_path),
            )
        else:
            record = get_document_metadata(source)
        if hasattr(record, "model_dump"):
            payload = record.model_dump(mode="json", exclude_none=True)
        elif isinstance(record, dict):
            payload = dict(record)
        else:
            raise TypeError(
                "get_document_metadata() must return a Pydantic model or dict"
            )
        payload["metadata_schema_version"] = METADATA_SCHEMA_VERSION
        return payload

    def _split_parent_preserving_tables(self, raw_parent_docs: List[Document]) -> List[Document]:
        """Hướng A: chặt prose bằng RecursiveCharacterTextSplitter (lọc rác < 50 chars),
        nhưng giữ bảng nguyên khối để không mất header cột.
        Đồng thời TIÊM (INJECT) các thẻ Metadata (Header 1, Header 2...) vào đầu mỗi Chunk
        để Mô hình nhúng (Embedding Model) không bị mất ngữ cảnh."""
        result: List[Document] = []
        for doc in raw_parent_docs:
            # Tạo chuỗi Ngữ cảnh từ Metadata
            header_context = " ".join([f"{k}: {v}" for k, v in doc.metadata.items() if k.startswith("Header")])
            metadata_label = doc.metadata.get("metadata_label") or self._business_metadata_label(doc.metadata)
            prefix_parts = []
            if metadata_label:
                prefix_parts.append(metadata_label)
            if header_context:
                prefix_parts.append(f"Ngữ cảnh tài liệu - {header_context}")
            prefix_text = "\n".join(prefix_parts)
            if prefix_text:
                prefix_text += "\nNội dung chi tiết:\n"
            
            for seg_type, seg_text in self._segment_by_table(doc.page_content):
                if seg_type == "table":
                    for tbl in self._chunk_table(seg_text):
                        if tbl.strip():  # bảng không bị lọc theo ngưỡng 50 chars
                            # Tiêm trực tiếp Ngữ cảnh vào nội dung Bảng
                            tbl_with_context = prefix_text + tbl
                            result.append(Document(page_content=tbl_with_context, metadata=dict(doc.metadata)))
                else:
                    for piece in self.parent_splitter.split_text(seg_text):
                        if len(piece.strip()) >= 50:
                            # Tiêm trực tiếp Ngữ cảnh vào nội dung Prose
                            piece_with_context = prefix_text + piece
                            result.append(Document(page_content=piece_with_context, metadata=dict(doc.metadata)))
        return result

    def ingest_markdown_document(
        self,
        file_path: str,
        *,
        ingest_run_id: Optional[str] = None,
        index_version: Optional[str] = None,
    ) -> bool:
        """Thực thi luồng Ingestion nạp dữ liệu vào Hệ thống."""
        target_file = Path(file_path)
        if not target_file.exists():
            logger.error(f"Lỗi I/O: Không tìm thấy file {target_file}")
            return False

        run_id = ingest_run_id or str(uuid.uuid4())
        source = target_file.name
        logger.info(f"Bắt đầu Ingestion Pipeline cho: {target_file.name}")
        try:
            # Bước A: Đọc Raw Markdown
            raw_bytes = target_file.read_bytes()
            raw_text = raw_bytes.decode("utf-8", errors="strict")
            source_sha256 = hashlib.sha256(raw_bytes).hexdigest()
            business_metadata = self._catalog_metadata(source)
            resolved_index_version = (
                index_version or self._resolve_active_index_version()
            )
            
            # --- BƯỚC MỚI: TRÍCH XUẤT THỜI GIAN (Temporal Extraction) ---
            effective_date = "1970-01-01" # Giá trị mặc định nếu không tìm thấy
            timestamp = 0
            
            # 1. Quét tìm định dạng: "ngày DD tháng MM năm YYYY" (Thường gặp trong văn bản hành chính)
            match_vn = re.search(r'ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})', raw_text, re.IGNORECASE)
            # 2. Quét tìm định dạng: "DD/MM/YYYY" hoặc "DD-MM-YYYY"
            match_short = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', raw_text)
            
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
            logger.info(f"Đã trích xuất Date: {effective_date} (Timestamp: {timestamp})")
            
            # Bước B: Cắt Parent bằng Markdown Splitter (Lọc cấp 1)
            # Trích xuất Metadata từ thẻ Heading
            raw_parent_docs: List[Document] = self.md_splitter.split_text(raw_text)

            # Business and technical metadata are attached before the second
            # parent/table split so every derived parent and child inherits the
            # exact same filterable payload.
            technical_metadata = {
                "source": source,
                "doc_type": "policy",
                "effective_date": effective_date,
                "timestamp": timestamp,
                "source_sha256": source_sha256,
                "index_version": resolved_index_version,
                "ingest_run_id": run_id,
            }
            for doc in raw_parent_docs:
                doc.metadata.update(business_metadata)
                doc.metadata.update(technical_metadata)
                doc.metadata.setdefault("status", "active")
                doc.metadata["metadata_label"] = self._business_metadata_label(
                    doc.metadata
                )
            
            # --- MÀNG LỌC CẤP 2 (Hướng A: Chặt prose, GIỮ NGUYÊN bảng) ---
            # Prose vượt ngưỡng bị chặt + lọc rác < 50 chars; bảng giữ nguyên khối
            # (nếu quá dài mới cắt theo dòng và tiêm lại header cột vào từng mảnh).
            parent_docs = self._split_parent_preserving_tables(raw_parent_docs)

            logger.info(f"Đã cắt thành {len(parent_docs)} Parent Chunks (Chặt prose + Giữ bảng nguyên khối).")
            if not parent_docs:
                raise ValueError(f"No indexable content found in {source}")

            # Bước C: Bơm vào Orchestrator
            # Thằng này sẽ tự động: 
            # 1. Băm Parent thành các Children bằng RecursiveCharacterTextSplitter.
            # 2. Nhúng (Embed) Children vào Qdrant DB.
            # 3. Lưu Parent vào LocalShelveStore và tạo Mapping ID (Link).
            self.base_retriever.add_documents(parent_docs, ids=None)
            logger.info("Hoàn tất nhúng Vector (Children) và lưu trữ nguyên bản (Parents).")
            
            return True

        except Exception:
            logger.critical("Engine Chunking sụp đổ trong quá trình Ingestion!", exc_info=True)
            self.purge_document(source, run_id)
            return False

if __name__ == "__main__":
    # Kịch bản tích hợp (Integration Scenario)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    md_folder = Path(os.path.join(PROJECT_ROOT, "data", "markdown"))
    md_files = list(md_folder.glob("*.md"))
    
    engine = AdvancedChunkingEngine()
    
    if not md_files:
        print(f"Không tìm thấy file .md nào trong {md_folder}")
    else:
        print(f"Tìm thấy {len(md_files)} file .md. Bắt đầu quá trình Ingestion...")
        for file_path in md_files:
            print(f"Đang xử lý file: {file_path.name}")
            engine.ingest_markdown_document(str(file_path))
        print("Đã nạp toàn bộ file vào Vector DB thành công!")
    
    # ---------------------------------------------------------
    # GÓC NHÌN TEST CHỨNG MINH KIẾN TRÚC (Proof of Concept)
    # ---------------------------------------------------------
    print("\n--- TEST TRUY XUẤT (RETRIEVAL PHASE) ---")
    query = "Sinh viên khối ngành Sức khỏe được học bổng bao nhiêu tiền?"
    
    # Khi gọi invoke, hệ thống ngầm tìm Children chứa chữ "Sức khỏe",
    # nhưng kết quả nó trả về là toàn bộ cái PARENT chứa cái bảng đó.
    retrieved_parents = engine.retriever.invoke(query)
    
    print(f"Hệ thống truy xuất được {len(retrieved_parents)} Parent Document.")
    if retrieved_parents:
        print(f"Metadata của Parent được gọi lên: {retrieved_parents[0].metadata}")
        print(f"Bức tranh tổng thể gửi cho LLM:\n{retrieved_parents[0].page_content[:500]}...\n")
