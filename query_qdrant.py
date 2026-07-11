import asyncio
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

embeddings = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")
client = QdrantClient(url="http://localhost:6333")
vector_store = QdrantVectorStore(
    client=client,
    collection_name="ctu_scholarship_docs_v3",
    embedding=embeddings
)

docs = vector_store.similarity_search("học phí ngành cntt clc k49 là bao nhiêu", k=5)
for i, doc in enumerate(docs):
    print(f"\n--- Chunk {i+1} ---")
    print(doc.page_content)
