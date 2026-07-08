import os
import shutil
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Request, HTTPException

router = APIRouter(prefix="/document", tags=["Document"])
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.services.ocr_service import LlamaParseAsyncClient
from app.utils.clean_md import clean_markdown_file

@router.post("/upload")
async def upload_document(request: Request, file: UploadFile = File(...)):
    """
    Nhận file PDF, gửi lên LlamaParse OCR, làm sạch, và tự động Ingest vào DB.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tải lên file PDF.")
        
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Hệ thống chưa được cấu hình LLAMA_CLOUD_API_KEY.")
        
    try:
        # 1. Tạo thư mục tạm và lưu file
        input_dir = Path(PROJECT_ROOT) / "data" / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        
        md_dir = Path(PROJECT_ROOT) / "data" / "markdown"
        md_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = input_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Đã nhận file upload: {file_path}")
        
        # 2. Xử lý OCR qua LlamaParse
        client = LlamaParseAsyncClient(api_key=api_key)
        markdown_content = await client.parse_pdf_to_markdown(str(file_path))
        
        # 3. Lưu và làm sạch Markdown
        md_file_path = md_dir / f"{file_path.stem}.md"
        md_file_path.write_text(markdown_content, encoding="utf-8")
        
        clean_markdown_file(md_file_path)
        logger.info(f"Đã làm sạch file markdown: {md_file_path}")
        
        # 4. Đẩy vào Chunking Engine (Postgres + Qdrant)
        engine = request.app.state.engine
        success = engine.ingest_markdown_document(str(md_file_path))
        
        if not success:
            raise HTTPException(status_code=500, detail="Lỗi khi lưu dữ liệu vào cơ sở dữ liệu Vector.")
            
        # 5. Dọn dẹp (Chuyển file PDF sang thư mục Done)
        done_dir = Path(PROJECT_ROOT) / "data" / "done"
        done_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(done_dir / file.filename))
        
        return {
            "status": "success", 
            "message": f"Tài liệu {file.filename} đã được xử lý và học thành công."
        }
        
    except Exception as e:
        logger.error(f"Lỗi khi xử lý document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
