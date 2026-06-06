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

class LocalShelveStore(BaseStore[str, Document]):
    """Kho lưu trữ Parent Document vĩnh viễn xuống ổ cứng (thay vì dùng RAM)."""
    def __init__(self, path: str):
        self.path = path
        
    def mset(self, key_value_pairs: Sequence[Tuple[str, Document]]) -> None:
        with shelve.open(self.path) as db:
            for k, v in key_value_pairs:
                db[k] = v
                
    def mget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        with shelve.open(self.path) as db:
            return [db.get(k) for k in keys]
            
    def mdelete(self, keys: Sequence[str]) -> None:
        with shelve.open(self.path) as db:
            for k in keys:
                if k in db:
                    del db[k]
                    
    def yield_keys(self, prefix: Optional[str] = None) -> Iterator[str]:
        with shelve.open(self.path) as db:
            keys = list(db.keys())
        for k in keys:
            if prefix is None or k.startswith(prefix):
                yield k

class AdvancedChunkingEngine:
    """
    Engine phân mảnh dữ liệu áp dụng chiến lược Small-to-Big.
    Khắc phục triệt để hiện tượng mất ngữ cảnh của LLM.
    """
    def __init__(self, persist_dir: str = "./vector_db"):
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
        
        # 2. CẤU HÌNH CHILD SPLITTER (Độ phân giải Vector cao)
        # Chunk cực nhỏ (400 chars) để thuật toán Cosine Similarity đối sánh cực nhạy
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "] # Ưu tiên cắt theo đoạn/dòng trước
        )
        
        # 3. KHỞI TẠO HẠ TẦNG LƯU TRỮ (Storage Infrastructure)
        # Đã thay thế InMemoryStore bằng ổ đĩa cứng thực thụ
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        self.doc_store = LocalShelveStore(str(Path(self.persist_dir) / "parent_doc_store"))
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
        
        # 4. ORCHESTRATOR: BỘ ĐIỀU PHỐI PARENT-CHILD
        # ÁP DỤNG METADATA FILTERING: Chỉ tìm kiếm trên những tài liệu có status='active'
        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vector_store,
            docstore=self.doc_store,
            child_splitter=self.child_splitter,
            search_kwargs={
                "k": 3, # Lấy ra 3 đoạn văn bản sát nghĩa nhất
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
            
            # Bước B: Cắt Parent bằng Markdown Splitter
            # Lúc này, mỗi 'parent_doc' là một cụm logic hoàn chỉnh (VD: Toàn bộ Điều 1)
            # Kèm theo Metadata tự động sinh (VD: {'Header_1_QuyetDinh': 'QUYẾT ĐỊNH', ...})
            parent_docs: List[Document] = self.md_splitter.split_text(raw_text)
            logger.info(f"Đã cắt thành {len(parent_docs)} Parent Chunks (Khối cấu trúc).")
            
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
            # 2. Nhúng (Embed) Children vào Chroma DB.
            # 3. Lưu Parent vào InMemoryStore và tạo Mapping ID (Link).
            self.retriever.add_documents(parent_docs, ids=None)
            logger.info("Hoàn tất nhúng Vector (Children) và lưu trữ nguyên bản (Parents).")
            
            return True

        except Exception as e:
            logger.critical("Engine Chunking sụp đổ trong quá trình Ingestion!", exc_info=True)
            return False

if __name__ == "__main__":
    # Kịch bản tích hợp (Integration Scenario)
    MD_FILE = "/mnt/d/Project/Chatbot/clean_markdown/API_Llama/Tài liệu phân bổ quỹ học bổng.md"

    engine = AdvancedChunkingEngine()
    engine.ingest_markdown_document(MD_FILE)
    
    # ---------------------------------------------------------
    # GÓC NHÌN TEST CHỨNG MINH KIẾN TRÚC (Proof of Concept)
    # ---------------------------------------------------------
    print("\n--- TEST TRUY XUẤT (RETRIEVAL PHASE) ---")
    query = "Sinh viên khối ngành Sức khỏe được học bổng bao nhiêu tiền?"
    
    # Khi gọi invoke, hệ thống ngầm tìm Children chứa chữ "Sức khỏe",
    # nhưng kết quả nó trả về là toàn bộ cái PARENT chứa cái bảng đó.
    retrieved_parents = engine.retriever.invoke(query)
    
    print(f"Hệ thống truy xuất được {len(retrieved_parents)} Parent Document.")
    print(f"Metadata của Parent được gọi lên: {retrieved_parents[0].metadata}")
    print(f"Bức tranh tổng thể gửi cho LLM:\n{retrieved_parents[0].page_content[:5000]}...\n")