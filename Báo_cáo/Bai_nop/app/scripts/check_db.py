import os
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from app.core.database import SyncSessionLocal
from app.models.schema import ParentDocument as DBParentDocument
import json

def check_db():
    print("=== KIỂM TRA TRONG POSTGRESQL ===")
    with SyncSessionLocal() as session:
        # Lấy tất cả các Parent Document thuộc về file MucHocPhi_2526_MienGiam.md
        docs = session.query(DBParentDocument).all()
        target_docs = []
        for doc in docs:
            # metadata lưu dưới dạng dict/JSON
            if doc.metadata_json and doc.metadata_json.get("source") == "MucHocPhi_2526_MienGiam.md":
                target_docs.append(doc)
                
        print(f"Tìm thấy {len(target_docs)} Parent Chunks cho file MucHocPhi_2526_MienGiam.md\n")
        
        for i, doc in enumerate(target_docs):
            print(f"--- Chunk {i+1} ---")
            print(f"Metadata: {doc.metadata_json}")
            content_snippet = doc.content[:200].replace("\n", "\\n")
            print(f"Content (200 ký tự đầu): {content_snippet}...")
            
            if "Mức học phí một tín chỉ" in doc.content:
                print(">> [BÁO CÁO]: TÌM THẤY CHỮ 'Mức học phí một tín chỉ' TRONG CHUNK NÀY!")
            print("-" * 50)

if __name__ == "__main__":
    check_db()
