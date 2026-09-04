# Hướng dẫn chạy Table 5 RAGAS Test

Tài liệu từng bước chạy benchmark **Table 5** (RAGAS answer-quality, 4 chế độ retrieval) bằng [Test_Ragas/test_table5_ragas.py](../Test_Ragas/test_table5_ragas.py) — **không cần sửa `rag_engine.py`**.

---

## Bước 0 — Điều kiện tiên quyết


| Thành phần   | Yêu cầu                                                 |
| ---------------- | ----------------------------------------------------------- |
| OS             | Windows 10/11 (PowerShell) hoặc Linux/WSL                |
| Python         | 3.10 – 3.11                                              |
| Docker Desktop | Đang chạy (cần 4 container)                            |
| RAM            | Tối thiểu 8 GB (model embedding + reranker chạy local) |
| API Key        | `GOOGLE_API_KEY` (Gemini) trong `.env`                    |

> GPU NVIDIA là *tùy chọn* — không có thì embedding/reranker chạy CPU, chậm hơn nhưng vẫn chạy được.

---

## Bước 1 — Cài dependencies

```powershell
# Từ thư mục gốc dự án
cd D:\Code\CTU_Student_Service\CTU-Chat_bot

# (Tùy chọn) tạo virtual environment
python -m venv wsl_venv
.\wsl_venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

# Thư viện benchmark (không nằm trong requirements.txt)
pip install "ragas==0.2.15"
```

> ⚠️ **Cài đúng `ragas==0.2.15`**. Bản 0.3.x/0.4.x hard-import `langchain_community.chat_models.vertexai` — module đã bị xoá ở `langchain-community==0.4.2` mà dự án đang pin → `import ragas` sẽ fail. File test có sẵn stub tự xử lý, nhưng bản 0.2.15 là bản đã được xác thực chạy được.

> Sau khi cài ragas, nếu `pip check` báo `langchain-openai` yêu cầu `langchain-core>=1.5.1`, hạ xuống bản tương thích với pin `langchain-core==1.4.8` của dự án:
>
> ```powershell
> pip install "langchain-openai==1.3.3" "langchain-core==1.4.8"
> ```

---

## Bước 2 — Cấu hình `.env`

```powershell
# Nếu chưa có .env
Copy-Item .env.example .env   # nếu có; nếu không thì tạo tay theo mẫu dưới
```

Mở `.env` và điền các biến sau (file `.env` hiện tại của repo đã đủ):

```env
# ── Bắt buộc ──
GOOGLE_API_KEY=AIzaSy...your_gemini_key
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/ctu_chatbot
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_ALIAS=ctu_scholarship_docs_current

# ── Neo4j ──
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# ── RAG (embedding + reranker local) ──
RAG_METADATA_FILTER_ENABLED=true
RAG_EMBEDDING_MODEL=./models/vietnamese-bi-encoder
RAG_RERANKER_MODEL=./models/bge-reranker-v2-m3
RAG_USE_RERANKER=true
```

> Test script đọc `.env` từ thư mục gốc dự án (tự `load_dotenv`), không cần export tay.

---

## Bước 3 — Khởi động hạ tầng Docker

```powershell
# Khởi động 4 services: Qdrant, PostgreSQL, Redis, Neo4j
docker compose up -d

# Kiểm tra cả 4 container đang chạy
docker compose ps
```


| Container              | Service          | Port   |
| ------------------------ | ------------------ | -------- |
| `chatbot-qdrant`       | Qdrant Vector DB | `6333` |
| `ctu-chatbot-postgres` | PostgreSQL 15    | `5432` |
| `ctu-chatbot-redis`    | Redis 7          | `6379` |
| `ctu-chatbot-neo4j`    | Neo4j 5.20       | `7687` |

> Nếu Docker Desktop chưa mở, chạy `Docker Desktop` trước rồi mới `docker compose up -d`.

---

## Bước 4 — Tải mô hình AI offline (lần đầu)

```powershell
python download_models.py
```

Sau bước này thư mục `models/` chứa:

- `models/vietnamese-bi-encoder/` — embedding model (768 dims)
- `models/bge-reranker-v2-m3/` — cross-encoder reranker

> Bỏ qua nếu thư mục `models/` đã có sẵn 2 thư mục này.

---

## Bước 5 — Xây dựng chỉ mục dữ liệu (lần đầu)

### 5.1 — Vector Index (Qdrant)

```powershell
python scripts/reindex_all.py build --index-version 2026-08-31-v1

# Trỏ alias sang collection mới (zero-downtime)
python scripts/reindex_all.py swap --alias-name ctu_scholarship_docs_current --target-collection ctu_scholarship_docs_2026-08-31-v1
```

### 5.2 — BM25 Index (Sparse)

```powershell
python scripts/build_bm25_index.py
```

> **Bỏ qua bước 5 nếu đã từng index.** Kiểm tra nhanh:
>
> ```powershell
> # Trình duyệt mở http://localhost:6333/dashboard — thấy collection có points là OK
> ```

> Neo4j Knowledge Graph **tự nạp dữ liệu** khi engine khởi động (lazy auto-ingest), không cần lệnh riêng cho Table 5.

---

## Bước 6 — Chạy Table 5 RAGAS Test

### Smoke test trước (3 câu × 1 mode, ~2 phút)

```powershell
python Test_Ragas/test_table5_ragas.py --limit 3 --modes dense_only
```

Kết quả mong đợi: log `ĐÁNH GIÁ MODE: dense_only` → `Kết quả: {...}` → `Kết quả lưu tại: logs\table5_results`.

### Chạy đủ 4 mode trên subset (kiểm tra pipeline end-to-end)

```powershell
python Test_Ragas/test_table5_ragas.py --limit 3
```

### Chạy thật — full 103 câu × 4 mode (~3 giờ, rate limit 15 RPM)

```powershell
# Chạy nền để không mất terminal
Start-Process -NoNewWindow python -ArgumentList "Test_Ragas/test_table5_ragas.py" -RedirectStandardOutput logs\table5_stdout.log -RedirectStandardError logs\table5_stderr.log
```

### Các tùy chọn hữu ích

```powershell
# Chỉ định mode riêng (dense_only | sparse_only | hybrid_rrf | hybrid_rrf_rerank)
python Test_Ragas/test_table5_ragas.py --modes sparse_only,hybrid_rrf_rerank

# Tăng số câu (mặc định: tất cả 103 câu trong data/dataset.md)
python Test_Ragas/test_table5_ragas.py --limit 25

# Chỉ định dataset khác
python Test_Ragas/test_table5_ragas.py --dataset data/dataset/test_experiment/file_test/Hung/dataset.md

# Đổi top_n retrieval (mặc định 6 — khớp DEFAULT_RERANK_TOP_N của engine)
python Test_Ragas/test_table5_ragas.py --top-n 10
```

---

## Bước 7 — Đọc kết quả

Output nằm tại `logs/table5_results/`:


| File                              | Nội dung                                                   |
| ----------------------------------- | ------------------------------------------------------------- |
| `table5_results_{timestamp}.json` | Kết quả chi tiết: metrics, failed_counts, per_domain     |
| `table5_report_{timestamp}.md`    | Bảng**Table 5** — 4 config × 4 metrics, kèm theo domain |

Bảng kết quả định dạng khớp paper (RAG.pdf, trang 10):


| Configuration     | Answer Relevance | Context Recall | Context Precision | Answer Correctness |
| ------------------- | ------------------ | ---------------- | ------------------- | -------------------- |
| dense_only        | ...              | ...            | ...               | ...                |
| sparse_only       | ...              | ...            | ...               | ...                |
| hybrid_rrf        | ...              | ...            | ...               | ...                |
| hybrid_rrf_rerank | ...              | ...            | ...               | ...                |

> Kết quả được **lưu dần sau mỗi mode** — nếu dừng giữa chừng (Ctrl+C), các mode đã xong vẫn còn trong file.

---

## Xử lý lỗi thường gặp


| Lỗi                                                        | Nguyên nhân                | Cách xử lý                                                                                             |
| ------------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `RuntimeError: Mode 'sparse_only' cần BM25 index`          | Chưa build BM25             | `python scripts/build_bm25_index.py` (Bước 5.2)                                                         |
| `RuntimeError: Mode 'hybrid_rrf_rerank' cần Cross-Encoder` | Reranker không load được | Kiểm tra`models/bge-reranker-v2-m3/` tồn tại, `RAG_USE_RERANKER=true`; xem log khi engine khởi động |
| `ModuleNotFoundError: No module named 'vertexai'`           | ragas ≥0.3                  | `pip install "ragas==0.2.15"` (Bước 1)                                                                  |
| `ValueError: DATABASE_URL is not set`                       | Thiếu`.env`                 | Làm Bước 2                                                                                             |
| `redis.RedisError` / Qdrant timeout                         | Container chưa chạy        | `docker compose up -d` + `docker compose ps` (Bước 3)                                                   |
| `429 RESOURCE_EXHAUSTED`                                    | Vượt rate limit Gemini     | Chờ 1-2 phút rồi chạy lại; script có rate limit 15 RPM sẵn                                         |
| Chạy xong metric toàn`NaN`                                | LLM judge lỗi ở câu đó  | Xem`failed_counts` trong JSON; script không dừng giữa chừng                                           |

---

## Appendix — 4 chế độ retrieval được tạo thế nào?

File test **không sửa** `rag_engine.py` — 4 mode map lên tham số có sẵn:


| Mode                | Cách gọi engine                                                                     |
| --------------------- | --------------------------------------------------------------------------------------- |
| `dense_only`        | `engine.retrieve(query, hybrid_search=False, use_reranker=False)`                     |
| `sparse_only`       | Gọi thẳng`engine.bm25_index.search()` + `engine.doc_store.mget()` (bỏ kênh dense) |
| `hybrid_rrf`        | `engine.retrieve(query, hybrid_search=True, use_reranker=False)`                      |
| `hybrid_rrf_rerank` | `engine.retrieve(query, hybrid_search=True, use_reranker=True)`                       |

Chi tiết: [Test_Ragas/test_table5_ragas.py](../Test_Ragas/test_table5_ragas.py) — hàm `retrieve_dense_only` / `retrieve_sparse_only` / `retrieve_hybrid_rrf` / `retrieve_hybrid_rrf_rerank`.
