from huggingface_hub import snapshot_download

print("📥 Đang tải Embedding Model...")

snapshot_download(
    repo_id="bkai-foundation-models/vietnamese-bi-encoder",
    local_dir="models/vietnamese-bi-encoder"
)

print("📥 Đang tải Cross-Encoder Reranker Model...")

snapshot_download(
    repo_id="BAAI/bge-reranker-v2-m3",
    local_dir="models/bge-reranker-v2-m3"
)

print("✅ Đã tải xong toàn bộ mô hình về ./models/!")