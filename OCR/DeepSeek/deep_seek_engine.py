import time
import logging
from pathlib import Path
from ollama import chat

# Cấu hình Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DeepSeek_Engine")

class DeepSeekExtractor:
    """
    Engine trích xuất Markdown sử dụng DeepSeek-OCR qua giao thức Ollama.
    Tối ưu hóa cho phần cứng giới hạn (GTX 1650 4GB).
    """
    def __init__(self, model_name: str = 'deepseek-ocr'):
        self.model_name = model_name
        # Trigger Prompt của DeepSeek để ép xuất Markdown giữ nguyên cấu trúc
        self.system_prompt = "<|grounding|>Convert the document to markdown."

    def process_image(self, image_path: str, output_path: str) -> bool:
        target_file = Path(image_path)
        if not target_file.exists():
            logger.error(f"I/O Error: Không tìm thấy ảnh tại {target_file}")
            return False

        logger.info(f"Đang nạp ảnh {target_file.name} vào luồng xử lý...")
        logger.warning("Cảnh báo Trade-off: Quá trình này sẽ Offload một phần sang RAM CPU do giới hạn 4GB VRAM. Vui lòng kiên nhẫn.")

        start_time = time.time()
        try:
            # Gửi Request xuống Ollama C++ Engine
            response = chat(
                model=self.model_name,
                messages=[{
                    'role': 'user',
                    'content': self.system_prompt,
                    'images': [str(target_file.resolve())]
                }],
                options={
                    # Ép Context Window nhỏ lại (mặc định là 8192, ta hạ xuống 2048 hoặc 4096)
                    # Điều này giới hạn bộ nhớ mở rộng, ép Model vừa vặn vào 4GB VRAM
                    'num_ctx': 4096 
                }
            )
            
            markdown_content = response.message.content  
            # Lưu rành mạch ra file tĩnh
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(markdown_content, encoding='utf-8')
            
            process_time = round(time.time() - start_time, 2)
            logger.info(f"Thành công! Mất {process_time}s. Output lưu tại: {out_file}")
            return True

        except Exception as e:
            logger.critical("Engine Ollama sụp đổ! Kiểm tra xem service 'ollama serve' đã chạy chưa.", exc_info=True)
            return False

if __name__ == "__main__":
    # Đưa thử 1 trang PDF đã chuyển sang ảnh (ví dụ trang 1)
    # Lưu ý Kiến trúc: VLM đọc ảnh (Pixels), không đọc file PDF tĩnh. 
    # Em sẽ phải dùng pdf2image băm file của ĐH Cần Thơ ra thành .jpg trước khi nạp vào đây.
    TEST_IMAGE = "/mnt/d/Project/Chatbot/Data/Images/Tài liệu phân bổ quỹ học bổng_page_002.jpg"
    OUTPUT_MD = "/mnt/d/Project/Chatbot/Data/Output/deepseek_extracted.md"
    
    extractor = DeepSeekExtractor()
    extractor.process_image(TEST_IMAGE, OUTPUT_MD)