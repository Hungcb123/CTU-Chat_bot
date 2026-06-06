import os
import json
import logging
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Table

# Cấu hình Logging chuẩn Production để theo dõi Memory & Pipeline
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Unstructured_POC")

def run_unstructured_poc(pdf_path: str, output_dir: str):
    """
    Pipeline trích xuất Dữ liệu Định biên (Bảng) và Ngữ nghĩa (Text) 
    bằng chiến lược hi_res của Unstructured.
    """
    if not os.path.exists(pdf_path):
        logger.error(f"I/O Error: Không tìm thấy file tại {pdf_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "unstructured_extracted_data.json")

    try:
        logger.info(f"Khởi động Engine OCR (hi_res) cho tài liệu: {pdf_path}")
        logger.warning("Cảnh báo Trade-off: infer_table_structure=True sẽ ngốn khoảng 2.5GB - 3.5GB VRAM.")
        
        # Core Extraction Logic
        elements = partition_pdf(
            filename=pdf_path,
            strategy="hi_res",
            # ocr_agent="unstructured.partition.utils.ocr_models.paddle_ocr.PaddleOCR",
            ocr_agent="unstructured.partition.utils.ocr_models.paddle_ocr.OCRAgentPaddle",
            languages=["vie"], # Ép PaddleOCR sử dụng trọng số Tiếng Việt
            infer_table_structure=True, # Bắt buộc kích hoạt Table Transformer của Microsoft
            hi_res_model_name="yolox" # Backbone phát hiện Layout nhẹ nhất
        )

        extracted_data = []
        for el in elements:
            block = {
                "element_type": type(el).__name__,
                "raw_text": el.text
            }
            
            # Khai thác mỏ vàng: Mã HTML của Bảng biểu
            if isinstance(el, Table) and hasattr(el, 'metadata') and el.metadata.text_as_html:
                block["table_html"] = el.metadata.text_as_html
            
            extracted_data.append(block)

        # Lưu rành mạch ra file tĩnh
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
            
        logger.info(f"Thành công! Toàn bộ cấu trúc được lưu tại: {output_file}")

    except Exception as e:
        logger.critical("Pipeline Crash! Kiểm tra lại VRAM (Lỗi OOM) hoặc Dependency.", exc_info=True)

if __name__ == "__main__":
    # Test case: Bảng phân bổ quỹ học bổng khóa 48/49/51
    # Lấy đường dẫn gốc của project
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target_pdf = os.path.join(project_root, "Data", "General", "Tài liệu phân bổ quỹ học bổng.pdf")
    out_folder = os.path.join(project_root, "Data", "Output")
    
    run_unstructured_poc(target_pdf, out_folder)