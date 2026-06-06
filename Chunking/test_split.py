from langchain_text_splitters import MarkdownHeaderTextSplitter
from pathlib import Path
import json

file_path = "/mnt/d/Project/Chatbot/clean_markdown/API_Llama/Tài liệu phân bổ quỹ học bổng.md"
raw_text = Path(file_path).read_text(encoding='utf-8')

headers_to_split_on = [
    ("#", "Header_1_QuyetDinh"),
    ("##", "Header_2_ChuyenMuc"),
    ("###", "Header_3_NguoiKy"),
]
md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False 
)

docs = md_splitter.split_text(raw_text)

for i, doc in enumerate(docs):
    print(f"--- Parent Chunk {i+1} ---")
    print("Metadata:", json.dumps(doc.metadata, ensure_ascii=False))
    print(f"Độ dài: {len(doc.page_content)} ký tự")
    content_preview = doc.page_content[:2000].replace('\n', ' \\n ')
    print(f"Nội dung (150 ký tự đầu): {content_preview}...")
    print("")
