import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from app.services.rag_engine import AdvancedChunkingEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reindex_all():
    logger.info("Bắt đầu quá trình Re-index toàn bộ dữ liệu...")
    
    # 1. Khởi tạo engine
    engine = AdvancedChunkingEngine()
    
    # 2. Xóa sạch DB cũ
    engine.clear_database()
    logger.info("Đã dọn dẹp sạch sẽ Qdrant và PostgreSQL.")
    
    # 3. Quét toàn bộ file trong thư mục data/markdown
    md_folder = Path(PROJECT_ROOT) / "data" / "markdown"
    md_files = list(md_folder.glob("*.md"))
    
    if not md_files:
        logger.warning(f"Không tìm thấy file Markdown nào trong {md_folder}")
        return
        
    logger.info(f"Tìm thấy {len(md_files)} file Markdown. Đang bắt đầu Ingestion...")
    
    # 4. Nạp lại vào DB
    success_count = 0
    for file_path in md_files:
        logger.info(f"Đang băm nhỏ và nạp: {file_path.name}")
        if engine.ingest_markdown_document(str(file_path)):
            success_count += 1
            
    logger.info(f"Hoàn tất! Đã nạp thành công {success_count}/{len(md_files)} file vào DB.")

if __name__ == "__main__":
    reindex_all()
