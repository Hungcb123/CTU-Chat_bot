import shelve
import json
from pathlib import Path
from langchain_core.documents import Document

def export_shelve_to_json(db_path: str, output_json: str):
    db_file = Path(db_path)
    
    # Kiểm tra xem có file nào chứa tên db_path không (vì shelve có thể sinh ra .dat, .dir, .db)
    if not any(Path(db_file.parent).glob(f"{db_file.name}*")):
        print(f"❌ Không tìm thấy database tại: {db_path}")
        print("Hãy chắc chắn bạn đã chạy file sematic_chunking.py để nạp dữ liệu trước.")
        return

    data_to_export = {}
    total_docs = 0
    
    try:
        print(f"🔍 Đang mở kho dữ liệu tại: {db_path}...")
        with shelve.open(db_path) as db:
            for doc_id, doc_obj in db.items():
                total_docs += 1
                # Trích xuất dữ liệu từ object Langchain Document
                data_to_export[doc_id] = {
                    "metadata": doc_obj.metadata,
                    "content": doc_obj.page_content,
                    "length": len(doc_obj.page_content)
                }
                
        # Lưu ra file JSON với định dạng đẹp (indent=4)
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data_to_export, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Xong! Đã xuất thành công {total_docs} Parent Documents.")
        print(f"👉 Mở file '{output_json}' trong VS Code để xem dữ liệu một cách trực quan nhất!")
        
    except Exception as e:
        print(f"❌ Có lỗi xảy ra khi đọc file DB: {e}")

if __name__ == "__main__":
    # Đường dẫn tới thư mục lưu trữ (tương đối so với vị trí bạn đang chạy code)
    DB_PATH = "./qdrant_storage/parent_doc_store"
    OUTPUT_FILE = "xem_du_lieu_kho.json"
    
    export_shelve_to_json(DB_PATH, OUTPUT_FILE)
