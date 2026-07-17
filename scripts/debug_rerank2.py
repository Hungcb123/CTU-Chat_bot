import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from app.services.rag_engine import AdvancedChunkingEngine

engine = AdvancedChunkingEngine()
query = "Học phí của ngành Kỹ thuật Phần mềm, mã ngành CLC, khóa 49 tại Trường Đại học Cần Thơ là bao nhiêu?"

base_docs = engine.base_retriever.invoke(query)
print(f"Base docs: {len(base_docs)}")

scores = engine.cross_encoder.score([(query, doc.page_content) for doc in base_docs])
docs_with_scores = list(zip(base_docs, scores))
ranked = sorted(docs_with_scores, key=lambda x: x[1], reverse=True)

for i, (doc, score) in enumerate(ranked):
    source = doc.metadata.get('source')
    content = doc.page_content.replace(chr(10), ' ')[:150]
    print(f"[{i+1}] Score: {score:.4f} | Source: {source} | Preview: {content}")
