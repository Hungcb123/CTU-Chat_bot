import os
from pathlib import Path
import re

def clean_markdown_file(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Xóa khoảng trắng thừa ở cuối mỗi dòng
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Loại bỏ các dải gạch ngang (thường do OCR ngắt trang tạo ra)
    # Nếu bạn muốn giữ lại --- thì có thể comment dòng này
    content = re.sub(r'^\s*---\s*$', '', content, flags=re.MULTILINE)

    # Thay thế 3 dòng trống liên tiếp trở lên thành 2 dòng trống
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Xóa dòng trống ở đầu và cuối file
    content = content.strip() + '\n'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Đã dọn dẹp file: {file_path.name}")

def main():
    folder_path = Path(os.path.join(PROJECT_ROOT, "data", "markdown"))
    
    md_files = list(folder_path.glob("*.md"))
    if not md_files:
        print("Không tìm thấy file .md nào trong thư mục.")
        return

    print(f"Bắt đầu dọn dẹp {len(md_files)} files...")
    for file in md_files:
        clean_markdown_file(file)
        
    print("\n=== HOÀN TẤT DỌN DẸP ===")

if __name__ == "__main__":
    main()
