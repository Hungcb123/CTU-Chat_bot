import os
import sys
import asyncio
import shutil
import logging
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Load environment variables from .env
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from app.services.ocr_service import LlamaParseAsyncClient
from app.utils.clean_md import clean_markdown_file
from app.services.rag_engine import AdvancedChunkingEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def process_all_files():
    input_dir = Path(PROJECT_ROOT) / "data" / "input"
    md_dir = Path(PROJECT_ROOT) / "data" / "markdown"
    done_dir = Path(PROJECT_ROOT) / "data" / "done"
    
    input_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)
    done_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.info(f"Không tìm thấy file PDF nào trong {input_dir}")
        return

    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    if not api_key:
        logger.error("Hệ thống chưa được cấu hình LLAMA_CLOUD_API_KEY trong file .env")
        return

    logger.info(f"Tìm thấy {len(pdf_files)} file PDF mới. Đang khởi động hệ thống Batch Processing...")
    
    client = LlamaParseAsyncClient(api_key=api_key)
    engine = AdvancedChunkingEngine()

    for file_path in pdf_files:
        logger.info(f"Đang xử lý (OCR): {file_path.name}")
        try:
            # 1. OCR (LlamaParse)
            markdown_content = await client.parse_pdf_to_markdown(str(file_path))
            
            # 2. Lưu và làm sạch
            md_file_path = md_dir / f"{file_path.stem}.md"
            md_file_path.write_text(markdown_content, encoding="utf-8")
            clean_markdown_file(md_file_path)
            logger.info(f"Đã xuất ra Markdown: {md_file_path.name}")
            
            # 3. Nạp vào Qdrant & Postgres
            logger.info(f"Đang băm nhỏ và nạp vào Vector DB (Qdrant)...")
            success = engine.ingest_markdown_document(str(md_file_path))
            
            if success:
                # 4. Di chuyển sang Done
                shutil.move(str(file_path), str(done_dir / file_path.name))
                logger.info(f"✅ Xử lý thành công! Đã di chuyển file tới {done_dir.name}")
            else:
                logger.error(f"❌ Lỗi khi nạp file {file_path.name} vào DB.")
                
        except Exception as e:
            logger.error(f"❌ Xảy ra lỗi với file {file_path.name}: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(process_all_files())
