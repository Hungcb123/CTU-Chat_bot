import os
import logging
from pathlib import Path
from pdf2image import convert_from_path
from typing import List

# Cấu hình Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PDF_to_Image_Layer")

class DocumentRasterizer:
    """
    Module chuyển đổi PDF thành Ma trận điểm ảnh (Rasterization).
    Tối ưu hóa DPI để phục vụ cho các mô hình VLM/OCR.
    """
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_pages(self, pdf_path: str, dpi: int = 100) -> List[str]:
        """
        Băm nhỏ PDF thành các file ảnh JPG chất lượng cao.
        Trade-off: DPI=300 là tiêu chuẩn vàng cho OCR. 
        Thấp hơn (150) sẽ làm mờ chữ nhỏ, cao hơn (600) sẽ đốt cháy RAM/Ổ cứng vô ích.
        """
        source_file = Path(pdf_path)
        if not source_file.exists():
            logger.error(f"I/O Error: File {source_file} không tồn tại.")
            raise FileNotFoundError(f"Missing file: {source_file}")

        logger.info(f"Đang băm file: {source_file.name} (DPI: {dpi})...")
        image_paths = []

        try:
            # Gọi core Poppler để render PDF thành RAM-based Images
            pages = convert_from_path(str(source_file), dpi=dpi)
            
            for page_num, page_image in enumerate(pages, start=1):
                # Naming Convention rõ ràng để dễ mapping lại sau khi xử lý
                image_name = f"{source_file.stem}_page_{page_num:03d}.jpg"
                save_path = self.output_dir / image_name
                
                # Ép chất lượng JPEG cao nhất để chống nhiễu (compression artifacts)
                page_image.save(str(save_path), "JPEG", quality=95)
                image_paths.append(str(save_path))
                
            logger.info(f"Thành công! Đã băm {len(pages)} trang ảnh vào {self.output_dir}")
            return image_paths

        except Exception as e:
            logger.critical("Engine Poppler sụp đổ! Hãy chắc chắn đã chạy 'sudo apt-get install poppler-utils'.", exc_info=True)
            raise e

if __name__ == "__main__":
    # Test Architecture
    PDF_FILE = "/mnt/d/Project/Chatbot/Data/Input/General/Tài liệu phân bổ quỹ học bổng.pdf"
    OUT_FOLDER = "/mnt/d/Project/Chatbot/Data/Images"
    
    rasterizer = DocumentRasterizer(output_dir=OUT_FOLDER)
    generated_images = rasterizer.extract_pages(PDF_FILE, dpi=150)
    
    # Kết nối vào Pipeline OCR
    print("\n[Pipeline Handover] Truyền các ảnh sau vào DeepSeekExtractor:")
    for img in generated_images:
        print(f" -> {img}")