import os
import sys
import glob
from pathlib import Path

# Thêm thư mục gốc vào sys.path để Python có thể nhận diện thư mục 'models'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from sematic_chunking_rerank import AdvancedChunkingEngine
from models.database import sync_engine
from models.schema import Base

if __name__ == "__main__":
    # Tự động tạo bảng PostgreSQL nếu chưa có
    print("📡 Đang kiểm tra và khởi tạo các bảng trong PostgreSQL...")
    Base.metadata.create_all(bind=sync_engine)
    
    # Khởi tạo Engine (Kết nối Qdrant)
    engine = AdvancedChunkingEngine(persist_dir="./parent_doc_storage")
    
    # Xóa dữ liệu cũ trước khi nạp để tránh trùng lặp parent_doc và chunks
    engine.clear_database()
    
    # Đường dẫn tới thư mục chứa toàn bộ file Markdown đã parse
    md_folder = "/mnt/d/Project/Chatbot/clean_markdown/API_Llama/"
    
    # Lấy toàn bộ file .md
    md_files = glob.glob(os.path.join(md_folder, "*.md"))
    
    print(f"🔍 Tìm thấy {len(md_files)} file Markdown cần nạp vào DB...")
    
    for file_path in md_files:
        print(f"⏳ Đang nạp: {Path(file_path).name}")
        # Hàm này sẽ tự đọc, chunking và nhúng vector vào Qdrant
        engine.ingest_markdown_document(file_path)
        
    print("✅ Đã nạp xong toàn bộ kiến thức vào Vector DB!")