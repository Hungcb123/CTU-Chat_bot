# Chạy BGE reranker trên Google Colab

## 1. Mở notebook

Upload hoặc mở file `notebooks/ctu_remote_reranker_colab.ipynb` bằng Google Colab, chọn `Runtime → Change runtime type → GPU`, sau đó chạy lần lượt tất cả cell.

Notebook sẽ:

1. cài `FlagEmbedding`, FastAPI và `cloudflared`;
2. yêu cầu một API key tạm thời dài ít nhất 16 ký tự;
3. tải `BAAI/bge-reranker-v2-m3` lên GPU;
4. mở FastAPI tại cổng 8000;
5. tạo một URL tạm `https://....trycloudflare.com`;
6. in ba dòng cấu hình cần đặt vào `.env` local.

## 2. Cấu hình máy local

Không commit URL hoặc API key thật. Thêm vào `.env` local:

```env
RAG_USE_RERANKER=true
RAG_RERANKER_BACKEND=remote
RAG_REMOTE_RERANKER_URL=https://your-random-url.trycloudflare.com
RAG_REMOTE_RERANKER_API_KEY=your-session-key
RAG_REMOTE_RERANKER_TIMEOUT_SECONDS=30
RAG_REMOTE_RERANKER_FAIL_OPEN=true
RAG_REMOTE_RERANKER_MAX_DOCUMENTS=64
RAG_REMOTE_RERANKER_MODEL_NAME=BAAI/bge-reranker-v2-m3
```

`RAG_RERANKER_MODEL` có thể giữ nguyên; biến này chỉ được dùng cho backend local/OpenRouter.

Khởi động lại tiến trình backend sau khi thay `.env`.

## 3. Kiểm tra endpoint trước khi chạy RAG

```bash
wsl_venv/bin/python scripts/test_remote_reranker.py
```

Hoặc truyền trực tiếp mà không sửa `.env`:

```bash
wsl_venv/bin/python scripts/test_remote_reranker.py \
  --url https://your-random-url.trycloudflare.com \
  --api-key your-session-key
```

Script chỉ pass khi endpoint health hoạt động và evidence về bản sao văn bằng được chấm cao hơn tài liệu học phí.

## 4. Chạy regression

Khi Qdrant, PostgreSQL và Neo4j local đã hoạt động:

```bash
wsl_venv/bin/python scripts/run_smoke20_regression.py --mode retrieval
```

Sau đó mới chạy Scenario 1 hoặc full benchmark. Mỗi request rerank gửi một query cùng candidate snippets; database và toàn bộ corpus vẫn ở local.

## 5. Failure behavior

- `RAG_REMOTE_RERANKER_FAIL_OPEN=true`: HTTP lỗi hoặc Colab ngắt thì giữ nguyên candidate order trước rerank; retrieval vẫn chạy.
- `RAG_REMOTE_RERANKER_FAIL_OPEN=false`: lỗi remote được ném ra để benchmark dừng ngay, phù hợp khi cần bảo đảm mọi record thực sự dùng GPU reranker.
- Quick Tunnel đổi URL sau mỗi Colab session. Cập nhật lại `.env` khi reconnect.
- Đây là cấu hình thử nghiệm. Không dùng Colab/Quick Tunnel làm endpoint production lâu dài.
