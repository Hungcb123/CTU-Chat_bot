import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

from Chunking.sematic_chunking_rerank import AdvancedChunkingEngine

def main():
    engine = AdvancedChunkingEngine(persist_dir=os.path.join(PROJECT_ROOT, "qdrant_storage"))
    
    count = engine.qdrant_client.count("ctu_scholarship_docs_v3")
    print(f"Tổng số vectors trong Qdrant: {count}")

    # Thử search chay không qua Parent/Reranker
    print("\nThử search trực tiếp trên VectorStore:")
    results = engine.vector_store.similarity_search("học bổng và trợ cấp xã hội", k=3)
    print(f"Vector Store tìm thấy {len(results)} kết quả.")
    for r in results:
        print(r.metadata)
        
if __name__ == "__main__":
    main()
