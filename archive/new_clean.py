import os
import re
import logging
from pathlib import Path

# Tiêu chuẩn Production: Bắt buộc dùng Logging thay vì print()
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [DATA_CLEANSER] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MarkdownCleanser")

class EnterpriseMarkdownCleanser:
    """
    Tầng xử lý dữ liệu (Data Harmonization Layer).
    Tối ưu hóa Token và bảo vệ không gian Vector khỏi rác hệ thống.
    """
    def __init__(self, target_folder: str):
        self.folder_path = Path(target_folder)
        if not self.folder_path.exists():
            logger.error(f"Thư mục không tồn tại: {self.folder_path}")
            raise FileNotFoundError(f"Missing folder: {self.folder_path}")

    def normalize_content(self, content: str) -> str:
        # TIER 1: TIÊU DIỆT RÁC HỆ THỐNG VÀ WATERMARK (Nuke the Noise)
        # Bắt toàn bộ các chuỗi bắt đầu bằng 'messages.' (rác do PDF parser/StuDocu sinh ra)
        content = re.sub(r'messages\.[a-z_]+', '', content, flags=re.IGNORECASE)
        
        # Xóa các cụm từ vô nghĩa không mang giá trị RAG
        noise_words = [
            r'studeersnel', 
            r'QR Code', 
            r'\*?Ấn dấu đỏ:.*?\*?', # Bắt các cụm chú thích dấu mộc đỏ
            r'\*?Chữ ký\*?'
        ]
        for noise in noise_words:
            content = re.sub(noise, '', content, flags=re.IGNORECASE | re.MULTILINE)

        # TIER 2: CHUẨN HÓA BẢNG BIỂU (Table Normalization)
        # LLM hiểu Markdown thuần túy. Xóa các thẻ <br/> trong Table Header thành khoảng trắng
        content = re.sub(r'<br\s*/?>', ' ', content, flags=re.IGNORECASE)

        # TIER 3: XÓA RÁC HÀNH CHÍNH (Administrative Noise)
        # (KHÔNG đưa dòng chứa "ngày ... tháng ... năm" vào đây để tránh hệ thống mất Metadata)
        admin_noise = [
            r'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM',
            r'Độc lập [–\-] Tự do [–\-] Hạnh phúc',
            r'ĐẠI HỌC CẦN THƠ',
            r'PHÒNG CÔNG TÁC SINH VIÊN',
            r'Số:\s*\d+\s*/[A-Z\-]+',
            r'Nơi nhận:',
            r'-\s*Như trên;',
            r'-\s*Lưu:\s*[A-Z]+'
        ]
        for noise in admin_noise:
            content = re.sub(noise, '', content, flags=re.IGNORECASE | re.MULTILINE)

        # TIER 4: TỐI ƯU CẤU TRÚC (Context Window Optimization)
        # Xóa khoảng trắng thừa ở cuối dòng (O(N) time complexity)
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
        
        # Xóa dải gạch ngang phân trang (---) nhưng KHÔNG làm hỏng Markdown Table (|---|)
        content = re.sub(r'^\s*---\s*$', '', content, flags=re.MULTILINE)

        # Nén Memory: Biến 3+ dòng trống thành đúng 2 dòng trống để giữ lại cấu trúc Paragraph
        content = re.sub(r'\n{3,}', '\n\n', content)

        return content.strip() + '\n'

    def execute_pipeline(self):
        md_files = list(self.folder_path.glob("*.md"))
        if not md_files:
            logger.warning("Không tìm thấy file .md nào để xử lý.")
            return

        logger.info(f"Kích hoạt luồng làm sạch cho {len(md_files)} files...")
        
        total_tokens_saved = 0
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_len = len(content)
                cleaned_content = self.normalize_content(content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                # Metric đánh giá Trade-off: Giả định trung bình 1 token ~ 4 ký tự
                saved_chars = original_len - len(cleaned_content)
                tokens_saved = max(0, saved_chars // 4)
                total_tokens_saved += tokens_saved
                
                logger.info(f"[{file_path.name}] Sạch sẽ. Cứu được ~{tokens_saved} tokens.")
                
            except Exception as e:
                logger.error(f"Sụp đổ tại file {file_path.name}", exc_info=True)

        logger.info(f"=== PIPELINE HOÀN TẤT. Tổng số Token rác đã xóa: ~{total_tokens_saved} ===")

if __name__ == "__main__":
    # Kiến trúc đường dẫn chuẩn
    TARGET_DIR = "/mnt/d/Project/Chatbot/clean_markdown/API_Llama"
    
    cleanser_engine = EnterpriseMarkdownCleanser(TARGET_DIR)
    cleanser_engine.execute_pipeline()