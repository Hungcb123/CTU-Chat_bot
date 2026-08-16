"""
Script chẩn đoán pipeline retrieval từng bước:
1. Qdrant vector search (child vectors)
2. Parent document lookup (PostgreSQL)
3. Reranker output
"""
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

print("=" * 60)
print("BƯỚC 0: Kiểm tra Qdrant collection")
print("=" * 60)
client = QdrantClient("http://localhost:6333")
info = client.get_collection("ctu_scholarship_docs_v3")
print(f"  Tổng vectors: {info.points_count}")
print(f"  Status: {info.status}")

# Lấy 1 point mẫu để xem cấu trúc payload
sample = client.scroll("ctu_scholarship_docs_v3", limit=1)
if sample[0]:
    point = sample[0][0]
    print(f"\n  Payload mẫu (point id={point.id}):")
    for key, val in point.payload.items():
        if key == "page_content":
            print(f"    {key}: {str(val)[:150]}...")
        else:
            print(f"    {key}: {val}")

print("\n" + "=" * 60)
print("BƯỚC 1: Vector Search trực tiếp (KHÔNG có filter)")
print("=" * 60)
embeddings = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")
query = "Học phí ngành Công nghệ thông tin chương trình chất lượng cao"
query_vector = embeddings.embed_query(query)

from qdrant_client.http.models import QueryRequest
results_no_filter = client.query_points(
    collection_name="ctu_scholarship_docs_v3",
    query=query_vector,
    limit=5
).points
print(f"  Tìm thấy: {len(results_no_filter)} kết quả (không filter)")
for i, r in enumerate(results_no_filter):
    content = r.payload.get("page_content", "N/A")[:120]
    status = r.payload.get("metadata", {}).get("status", "MISSING")
    print(f"  [{i+1}] Score: {r.score:.4f} | status={status}")
    print(f"       Content: {content}...")

print("\n" + "=" * 60)
print("BƯỚC 2: Vector Search CÓ filter metadata.status=active")
print("=" * 60)
results_with_filter = client.query_points(
    collection_name="ctu_scholarship_docs_v3",
    query=query_vector,
    limit=5,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="metadata.status",
                match=MatchValue(value="active")
            )
        ]
    )
).points
print(f"  Tìm thấy: {len(results_with_filter)} kết quả (có filter status=active)")
for i, r in enumerate(results_with_filter):
    content = r.payload.get("page_content", "N/A")[:120]
    print(f"  [{i+1}] Score: {r.score:.4f} | Content: {content}...")

print("\n" + "=" * 60)
print("BƯỚC 3: Kiểm tra Parent Documents trong PostgreSQL")
print("=" * 60)
# Lấy doc_id từ child metadata
if results_no_filter:
    parent_ids = set()
    for r in results_no_filter:
        doc_id = r.payload.get("metadata", {}).get("doc_id")
        if doc_id:
            parent_ids.add(doc_id)
    print(f"  Parent IDs tìm thấy trong child metadata: {len(parent_ids)}")
    if parent_ids:
        print(f"  Mẫu IDs: {list(parent_ids)[:3]}")
    
    # Thử lấy từ PostgreSQL
    from app.services.rag_engine import PostgresDocStore
    store = PostgresDocStore()
    parents = store.mget(list(parent_ids)[:5])
    found = sum(1 for p in parents if p is not None)
    print(f"  PostgreSQL tìm thấy: {found}/{min(5, len(parent_ids))} parent docs")
    if found == 0:
        print("  ⚠️ PARENT DOCS KHÔNG TỒN TẠI TRONG POSTGRESQL! Đây là nguyên nhân retriever trả về 0!")
    else:
        for p in parents:
            if p:
                print(f"    Parent content: {p.page_content[:150]}...")
                break

print("\n" + "=" * 60)
print("BƯỚC 4: Test ParentDocumentRetriever trực tiếp")
print("=" * 60)
from app.services.rag_engine import AdvancedChunkingEngine
engine = AdvancedChunkingEngine()
base_docs = engine.base_retriever.invoke(query)
print(f"  base_retriever trả về: {len(base_docs)} docs")

final_docs = engine.retriever.invoke(query)
print(f"  retriever (sau rerank) trả về: {len(final_docs)} docs")

print("\n✅ Chẩn đoán hoàn tất!")
