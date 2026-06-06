import re
import unicodedata
import logging
from pathlib import Path

# Cấu hình Logging chuẩn Production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CLEANSER_LAYER] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataCleanser")

class DocumentCleanser:
    """
    Tầng Điều hòa Dữ liệu (Data Harmonization Layer).
    Nhiệm vụ: Chuyển đổi Raw Markdown (chứa rác, tọa độ, lỗi font) thành Pure Markdown 
    để chuẩn bị cho quá trình Semantic Chunking và Vector Embedding.
    """
    def __init__(self, input_path: str):
        self.input_path = Path(input_path)
        if not self.input_path.exists():
            logger.error(f"I/O Error: Không tìm thấy file {self.input_path}")
            raise FileNotFoundError(f"Missing file: {self.input_path}")

    def normalize_unicode(self, text: str) -> str:
        """
        Bảo vệ Vector Space: Ép kiểu Unicode về chuẩn Dựng sẵn (NFC) 
        và triệt tiêu Ký tự ẩn (Zero-width characters).
        """
        # 1. Ép về chuẩn NFC (Gộp các ký tự tổ hợp thành 1 block nguyên khối)
        text = unicodedata.normalize('NFC', text)
        
        # 2. Quét sạch bóng ma Ký tự ẩn làm điên loạn Tokenizer
        text = re.sub(r'[\u200b\u200c\u200d\ufeff\xad]', '', text)
        
        return text

    def clean_deepseek_tags(self, text: str) -> str:
        """
        Triệt tiêu Spatial Metadata (Siêu dữ liệu Không gian) do DeepSeek-OCR sinh ra.
        """
        # Xóa thẻ <|ref|>...<|/ref|>
        text = re.sub(r'<\|ref\|>.*?<\|/ref\|>', '', text)
        
        # Xóa thẻ <|det|>...<|/det|> (Ví dụ: <|det|>[[440, 131, 603, 153]]<|/det|>)
        text = re.sub(r'<\|det\|>.*?<\|/det\|>', '', text)
        
        return text

    def remove_watermarks_and_noise(self, text: str) -> str:
        """
        Xóa bỏ các cụm từ nhiễu, header/footer của nền tảng tải tài liệu (StuDocu)
        và lỗi nhận diện ảnh cục bộ.
        """
        # 1. Xóa các thẻ markdown chèn ảnh cục bộ rỗng: ![](images/...)
        text = re.sub(r'!\[.*?\]\(images/[^\)]+\)', '', text)

        # 2. Xóa các Watermark hệ thống
        text = re.sub(r'messages\.[a-z_]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'studeersnel', '', text, flags=re.IGNORECASE)

        # 3. Xóa Header/Footer cố định vô nghĩa
        noise_patterns = [
            r'DUC VA TRUONG 0 DAIHO CANTHO',
            r'Kế toán tài chính 1 \(Trường Đại học Cần Thơ\)'
        ]
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
        return text

    def optimize_context_window(self, text: str) -> str:
        """
        Tối ưu hóa Token: Gom khoảng trắng thừa và sửa lỗi dính chữ cấp độ 1.
        """
        # Quy đổi \xa0, \t về 1 khoảng trắng chuẩn
        text = re.sub(r'[ \t\xa0]+', ' ', text)
        
        # Heuristic: Thêm khoảng cách sau dấu câu nếu bị dính chữ (ví dụ: "thơ,ngày" -> "thơ, ngày")
        # Chỉ áp dụng khi dấu câu kẹp giữa 2 chữ cái/số để tránh phá vỡ định dạng Markdown
        text = re.sub(r'([a-zA-Z0-9áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĐ])([,;:!?])([a-zA-ZáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĐ])', r'\1\2 \3', text)
        
        # Nén dấu xuống dòng (3 dấu trở lên gom thành 2) để giữ block Markdown
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()

    def execute_pipeline(self, output_path: str) -> bool:
        """
        Thực thi toàn bộ dòng chảy làm sạch.
        """
        try:
            # Đọc Raw Data
            content = self.input_path.read_text(encoding='utf-8')
            original_size = len(content)

            # Chạy qua các màng lọc theo thứ tự Kiến trúc
            content = self.normalize_unicode(content)
            content = self.clean_deepseek_tags(content)
            content = self.remove_watermarks_and_noise(content)
            content = self.optimize_context_window(content)

            # Xuất Pure Markdown
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(content, encoding='utf-8')
            
            # Tính toán Token tiết kiệm được (ước lượng 1 token ~ 4 chars)
            saved_tokens = max(0, (original_size - len(content)) // 4)
            logger.info(f"Đã dọn dẹp xong. Cứu được khoảng {saved_tokens} Tokens vô ích.")
            return True

        except Exception as e:
            logger.critical("Tiến trình Cleansing sụp đổ!", exc_info=True)
            return False

if __name__ == "__main__":
    # Test độc lập Module Cleanser
    INPUT = "/mnt/d/Project/Chatbot/Data/Output/deepseek_extracted.md"
    OUTPUT = "/mnt/d/Project/Chatbot/Data/Cleaned/Cleaned_Tài_liệu.md"
    
    cleanser = DocumentCleanser(INPUT)
    cleanser.execute_pipeline(OUTPUT)