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
import logging
import re
from datetime import datetime
from typing import List, Sequence, Optional, Iterator, Tuple
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
from qdrant_client.http.models import Distance, VectorParams, HnswConfigDiff, Filter, FieldCondition, MatchValue

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

class AdvancedChunkingEngine:
    """
    Engine phân mảnh dữ liệu áp dụng chiến lược Small-to-Big.
    Khắc phục triệt để hiện tượng mất ngữ cảnh của LLM.
    """
    def __init__(self, persist_dir: str = "./parent_doc_storage"):
        self.persist_dir = persist_dir
        
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
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "] # Ưu tiên cắt theo đoạn/dòng trước
        )
        
        # 3. KHỞI TẠO HẠ TẦNG LƯU TRỮ (Storage Infrastructure)
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        self.doc_store = PostgresDocStore()
        self.qdrant_client = QdrantClient("http://localhost:6333")
        
        # Tạo Collection (Bảng) nếu chưa có. 
        # vietnamese-bi-encoder sinh ra Vector 768 chiều, khoảng cách Cosine.
        collection_name = "ctu_scholarship_docs_v3"
        if not self.qdrant_client.collection_exists(collection_name):
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                hnsw_config=HnswConfigDiff(m=16, ef_construct=100), # Cấu hình thuật toán HNSW
            )

        # Trỏ Vector Store về Qdrant
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=collection_name,
            embedding=HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder"),
        )
        
        # 4. ORCHESTRATOR: BỘ ĐIỀU PHỐI PARENT-CHILD & RE-RANKING
        # Bước 6 (Theo lý thuyết): Tìm kiếm cơ sở (Lưới rộng Top 10)
        self.base_retriever = ParentDocumentRetriever(
            vectorstore=self.vector_store,
            docstore=self.doc_store,
            child_splitter=self.child_splitter,
            search_kwargs={
                "k": 10, # Giảm từ 20 xuống 10 để tránh quá tải GPU (OOM)
                "filter": Filter(
                    must=[
                        FieldCondition(
                            key="metadata.status",
                            match=MatchValue(value="active")
                        )
                    ]
                )
            }
        )

        # Bước 7 (Theo lý thuyết): Xếp hạng lại (Re-ranking) bằng Cross-Encoder
        logger.info("Đang nạp mô hình Cross-Encoder (Re-ranker) vào hệ thống...")
        self.cross_encoder = HuggingFaceCrossEncoder(
            model_name="BAAI/bge-reranker-v2-m3", # Mô hình tối ưu cho đa ngôn ngữ và tiếng Việt
            model_kwargs={"device": "cuda"}
        )
        # BẮT BUỘC: Giới hạn số token đưa vào mô hình để tránh lỗi CUDA Out of Memory (GPU 4GB)
        self.cross_encoder.client.max_length = 512
        self.reranker = TemporalCrossEncoderReranker(
            model=self.cross_encoder,
            top_n=3, # Chấm điểm 10 kết quả trên, và lọc ra đúng 3 kết quả xuất sắc nhất
            score_tolerance=0.05 # Chênh điểm <= 0.05 coi như "gần bằng" -> ưu tiên bản mới hơn
        )

        # Nối Base Retriever và Reranker lại thành một Pipeline truy xuất hoàn chỉnh
        self.retriever = ContextualCompressionRetriever(
            base_compressor=self.reranker,
            base_retriever=self.base_retriever
        )

    def clear_database(self):
        """Xóa toàn bộ dữ liệu cũ trong VectorDB và Parent Doc Store để tránh trùng lặp."""
        import os
        import glob
        logger.info("Bắt đầu xóa dữ liệu cũ (Clear Database)...")
        
        collection_name = "ctu_scholarship_docs_v3"
        if self.qdrant_client.collection_exists(collection_name):
            self.qdrant_client.delete_collection(collection_name)
            logger.info(f"Đã xóa collection '{collection_name}' trong Qdrant.")
            
            # Tạo lại collection trống
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
            )
            
        store_path = str(Path(self.persist_dir) / "parent_doc_store")
        for f in glob.glob(store_path + "*"):
            try:
                os.remove(f)
                logger.info(f"Đã xóa file dữ liệu cũ: {f}")
            except Exception as e:
                logger.warning(f"Không thể xóa {f}: {e}")
                
        # --- BƯỚC MỚI: Xóa dữ liệu trong PostgreSQL ---
        from app.core.database import SyncSessionLocal
        from app.models.schema import ParentDocument as DBParentDocument
        try:
            with SyncSessionLocal() as session:
                deleted_rows = session.query(DBParentDocument).delete()
                session.commit()
            logger.info(f"Đã xóa {deleted_rows} Parent Documents cũ trong PostgreSQL.")
        except Exception as e:
            logger.warning(f"Lỗi khi xóa PostgreSQL: {e}")
                
        logger.info("Hoàn tất dọn dẹp dữ liệu cũ!")

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

    def _split_parent_preserving_tables(self, raw_parent_docs: List[Document]) -> List[Document]:
        """Hướng A: chặt prose bằng RecursiveCharacterTextSplitter (lọc rác < 50 chars),
        nhưng giữ bảng nguyên khối để không mất header cột."""
        result: List[Document] = []
        for doc in raw_parent_docs:
            for seg_type, seg_text in self._segment_by_table(doc.page_content):
                if seg_type == "table":
                    for tbl in self._chunk_table(seg_text):
                        if tbl.strip():  # bảng không bị lọc theo ngưỡng 50 chars
                            result.append(Document(page_content=tbl, metadata=dict(doc.metadata)))
                else:
                    for piece in self.parent_splitter.split_text(seg_text):
                        if len(piece.strip()) >= 50:
                            result.append(Document(page_content=piece, metadata=dict(doc.metadata)))
        return result

    def ingest_markdown_document(self, file_path: str) -> bool:
        """Thực thi luồng Ingestion nạp dữ liệu vào Hệ thống."""
        target_file = Path(file_path)
        if not target_file.exists():
            logger.error(f"Lỗi I/O: Không tìm thấy file {target_file}")
            return False

        logger.info(f"Bắt đầu Ingestion Pipeline cho: {target_file.name}")
        try:
            # Bước A: Đọc Raw Markdown
            raw_text = target_file.read_text(encoding='utf-8')
            
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
            
            # --- MÀNG LỌC CẤP 2 (Hướng A: Chặt prose, GIỮ NGUYÊN bảng) ---
            # Prose vượt ngưỡng bị chặt + lọc rác < 50 chars; bảng giữ nguyên khối
            # (nếu quá dài mới cắt theo dòng và tiêm lại header cột vào từng mảnh).
            parent_docs = self._split_parent_preserving_tables(raw_parent_docs)

            logger.info(f"Đã cắt thành {len(parent_docs)} Parent Chunks (Chặt prose + Giữ bảng nguyên khối).")
            
            # Tiêm thêm Metadata hệ thống + Temporal Metadata
            for doc in parent_docs:
                doc.metadata['source'] = target_file.name
                doc.metadata['doc_type'] = "policy"
                doc.metadata['effective_date'] = effective_date
                doc.metadata['timestamp'] = timestamp
                doc.metadata['status'] = "active"

            # Bước C: Bơm vào Orchestrator
            # Thằng này sẽ tự động: 
            # 1. Băm Parent thành các Children bằng RecursiveCharacterTextSplitter.
            # 2. Nhúng (Embed) Children vào Qdrant DB.
            # 3. Lưu Parent vào LocalShelveStore và tạo Mapping ID (Link).
            self.base_retriever.add_documents(parent_docs, ids=None)
            logger.info("Hoàn tất nhúng Vector (Children) và lưu trữ nguyên bản (Parents).")
            
            return True

        except Exception as e:
            logger.critical("Engine Chunking sụp đổ trong quá trình Ingestion!", exc_info=True)
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