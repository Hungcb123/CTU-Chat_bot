import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from app.services.rag_engine import AdvancedChunkingEngine

engine = AdvancedChunkingEngine()
query = "Học phí của ngành Kỹ thuật Phần mềm, mã ngành CLC, khóa 49 tại Trường Đại học Cần Thơ là bao nhiêu?"

print("--- TÌM KIẾM TRỰC TIẾP TỪ QDRANT (Base Retriever) ---")
base_docs = engine.base_retriever.invoke(query)
for i, d in enumerate(base_docs):
    print(f"[{i+1}] Source: {d.metadata.get('source')} | Preview: {d.page_content[:150].replace(chr(10), ' ')}")

print("\n--- TÌM KIẾM SAU RERANKER (Final Retriever) ---")
final_docs = engine.retriever.invoke(query)
for i, d in enumerate(final_docs):
    print(f"[{i+1}] Source: {d.metadata.get('source')} | Preview: {d.page_content[:150].replace(chr(10), ' ')}")
