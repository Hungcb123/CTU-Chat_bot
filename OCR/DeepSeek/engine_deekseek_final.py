import magic
import mammoth
import logging
from pathlib import Path

# Nhập khẩu các vũ khí em đã rèn từ các hiệp trước
# DeepSeekExtractor gọi Ollama (xem deep_seek_engine.py)
from deep_seek_engine import DeepSeekExtractor
from pdf_processor import DocumentRasterizer
from data_cleanser import DocumentCleanser # Tái sử dụng class Cleanser

# Config Logging of Master Pipeline
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [MASTER_PIPELINE] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Orchestrator")

# Pipeline : File Input -> Magic Bytes Detection -> Dynamic Routing (DOCX vs PDF) -> Extraction (Mammoth vs DeepSeek) -> Cleansing -> Final Markdown Output
class EnterpriseIngestionPipeline:
    """
    Tầng điều phối tối cao của hệ thống RAG.
    Đảm bảo dòng chảy: Router -> Extractor -> Cleanser -> Pure Markdown.
    """
    def __init__(self, workspace_dir: str):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.raw_dir = self.workspace / "raw_extracted"
        self.raw_dir.mkdir(exist_ok=True)
        
        self.clean_dir = self.workspace / "clean_markdown"
        self.clean_dir.mkdir(exist_ok=True)

        # Khởi tạo các Engines
        logger.info("Đang khởi động Engine Deepseek và Rasterize")
        self.vlm_extractor = DeepSeekExtractor()
        self.pdf_rasterizer = DocumentRasterizer(output_dir=str(self.workspace / "temp_images"))

    def execute(self, file_path: str):
        # Convert file_path into type Path
        target_file = Path(file_path)
        
        if not target_file.exists():
            logger.error(f"File không tồn tại: {target_file}")
            return

        # BƯỚC 1: XÁC THỰC BẢO MẬT VÀ PHÂN LOẠI (MAGIC BYTES)
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(str(target_file))
        logger.info(f"Phát hiện tệp: {target_file.name} | Định dạng thật: {mime_type}")

        raw_output_path = self.raw_dir / f"{target_file.stem}_raw.md"
        clean_output_path = self.clean_dir / f"{target_file.stem}_final.md"

        # BƯỚC 2: BỘ ĐỊNH TUYẾN ĐỘNG 
        is_extracted = False

        if "openxmlformats-officedocument.wordprocessingml.document" in mime_type:

            # LUỒNG 1: DOCX -> CPU Parser (Mammoth)
            logger.info("-> Luồng DOCX: Kích hoạt Zero-GPU Parser...")

            try:
                # Read file docx using read binary
                with open(target_file, "rb") as docx_file:
                    result = mammoth.convert_to_markdown(docx_file)
                    raw_output_path.write_text(result.value, encoding='utf-8')
                    is_extracted = True

            except Exception as e:
                logger.error("Sụp đổ tại luồng DOCX", exc_info=True)

        elif "pdf" in mime_type:

            # LUỒNG 2: PDF -> GPU VLM (DeepSeek-OCR)
            
            logger.info("-> Luồng PDF: Kích hoạt Heavy-GPU Pipeline...")
            try:
                
                # 2.1 Băm PDF thành ảnh 
                images = self.pdf_rasterizer.extract_pages(str(target_file))
                full_raw_md = ""
                
                # 2.2 VLM Inference từng ảnh
                for img_path in images:
                    temp_md = self.workspace / f"temp_{Path(img_path).stem}.md"
                    if self.vlm_extractor.process_image(img_path, str(temp_md)):
                        full_raw_md += temp_md.read_text(encoding='utf-8') + "\n\n"
                        temp_md.unlink() # Xóa file temp ngay sau khi đọc
                
                raw_output_path.write_text(full_raw_md, encoding='utf-8')
                is_extracted = True
            except Exception as e:
                logger.error("Sụp đổ tại luồng PDF", exc_info=True)
                
        else:
            logger.warning(f"Hệ thống từ chối xử lý định dạng: {mime_type}")
            return

        # BƯỚC 3: MÀNG LỌC DỮ LIỆU (DATA HARMONIZATION)
        if is_extracted:
            logger.info("-> Kích hoạt Màng lọc Cleansing (Regex + Unicode)...")
            cleanser = DocumentCleanser(str(raw_output_path))
            # Hàm execute_pipeline của em đã chứa logic xóa <|det|>, Watermark và Normalize Unicode
            success = cleanser.execute_pipeline(str(clean_output_path))
            
            if success:
                logger.info(f"🚀 PIPELINE HOÀN TẤT! Dữ liệu tinh khiết sẵn sàng cho RAG: {clean_output_path}")

if __name__ == "__main__":
    # Khởi tạo Pipeline
    pipeline = EnterpriseIngestionPipeline(workspace_dir="/mnt/d/Project/Chatbot/")
    
    # Test luồng PDF
    # pipeline.execute("/mnt/d/Project/Chatbot/Data/Input/General/VayVon.pdf")

    input_path = Path("/mnt/d/Project/Chatbot/Data/Input/General/")
    for file_path in input_path.iterdir():
        if file_path.is_file():
            pipeline.execute(str(file_path))

    # Test luồng DOCX (Hãy tạo 1 file docx để test)
    # pipeline.execute("/mnt/d/Project/Chatbot/Data/General/Báo_cáo.docx")