import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)
from Chunking.sematic_chunking import AdvancedChunkingEngine

print("Đang khởi tạo Engine và kết nối Vector DB...")
engine = AdvancedChunkingEngine(persist_dir=os.path.join(PROJECT_ROOT, "qdrant_storage"))
print("✅ Khởi tạo thành công!\n")

while True:
    try:
        query = input("🔍 Nhập từ khóa tìm kiếm (hoặc 'exit' để thoát): ")
        if query.lower() in ['exit', 'quit', 'q']:
            break
        
        if not query.strip():
            continue

        print("⏳ Đang truy xuất...")
        docs = engine.retriever.invoke(query)
        
        print(f"\n🎯 TÌM THẤY {len(docs)} PARENT DOCUMENTS")
        print("=" * 70)
        
        for i, doc in enumerate(docs):
            print(f"\n[TÀI LIỆU {i+1}]")
            print(f"📄 Nguồn: {doc.metadata.get('source', 'Unknown')}")
            print(f"🏷️ Trích xuất Metadata: {doc.metadata}")
            print("📝 NỘI DUNG PARENT DOC:")
            print(doc.page_content)
            print("-" * 70)
            
    except KeyboardInterrupt:
        break

print("\n👋 Đã thoát chương trình test.")
