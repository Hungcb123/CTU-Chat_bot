# Hướng dẫn chạy Table 5 RAGAS Test

Tài liệu từng bước chạy benchmark **Table 5** (RAGAS answer-quality, T1–T7) bằng [Test_Ragas/test_table5_ragas.py](../Test_Ragas/test_table5_ragas.py). Chi tiết thay đổi và các comment T1–T7 nằm tại [T1_T7_CODE_CHANGELOG.md](T1_T7_CODE_CHANGELOG.md).

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
# T1-T7: validate the newly built physical collection before changing the live alias.
python scripts/reindex_all.py validate --index-version 2026-09-05-table5

# T1-T7: current CLI uses `activate` (the former `swap` command was removed).
python scripts/reindex_all.py activate --index-version 2026-09-05-table5

# T2-T6: rebuild Sparse BM25 from the newly active Qdrant parent IDs.
python scripts/build_bm25_index.py
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

Chạy **từng T riêng biệt** để dễ theo dõi quota và checkpoint. Với mỗi T, nên
chạy lần lượt 1 câu, 2 câu, rồi toàn bộ. Khi tăng từ `--limit 1` lên
`--limit 2`, câu đầu đã hoàn tất được bỏ qua; khi bỏ `--limit`, các câu đã hoàn
tất tiếp tục được bỏ qua.

### T1 — Dense-only

```powershell
# Thử 1 câu
python Test_Ragas/test_table5_ragas.py --modes dense_only --limit 1

# Thử 2 câu
python Test_Ragas/test_table5_ragas.py --modes dense_only --limit 2

# Chạy toàn bộ 100 câu
python Test_Ragas/test_table5_ragas.py --modes dense_only
```

### T2 — Sparse-only (BM25)

```powershell
# Thử 1 câu
python Test_Ragas/test_table5_ragas.py --modes sparse_only --limit 1

# Thử 2 câu
python Test_Ragas/test_table5_ragas.py --modes sparse_only --limit 2

# Chạy toàn bộ 100 câu
python Test_Ragas/test_table5_ragas.py --modes sparse_only
```

### T3 — Hybrid RRF

```powershell
# Thử 1 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf --limit 1

# Thử 2 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf --limit 2

# Chạy toàn bộ 100 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf
```

T3 lưu candidate pool dùng chung. Nên hoàn tất T3 trước T5 và T6 để hai mode
sau chỉ đọc lại cache Hybrid RRF, không retrieval lại.

### T4 — Hybrid RRF + Reranker

```powershell
# Thử 1 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_rerank --limit 1

# Thử 2 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_rerank --limit 2

# Chạy toàn bộ 100 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_rerank
```

### T5 — Hybrid RRF + Graph

```powershell
# Thử 1 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_graph --limit 1

# Thử 2 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_graph --limit 2

# Chạy toàn bộ 100 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_graph
```

T5 cần Neo4j hoạt động. Graph chỉ bổ sung evidence và không tham gia công thức
RRF.

### T6 — Hybrid RRF + Graph + Reranker

```powershell
# Thử 1 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_graph_rerank --limit 1

# Thử 2 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_graph_rerank --limit 2

# Chạy toàn bộ 100 câu
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_graph_rerank
```

T6 cần Neo4j và reranker. Evidence cuối cùng của từng câu được lưu để T7 dùng
nguyên trạng.

### T7 — Agent dùng đúng evidence của T6

```powershell
# Chỉ chạy sau khi câu tương ứng của T6 đã hoàn tất

# Thử 1 câu (T6 --limit 1 phải hoàn tất trước)
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_graph_rerank_agent --limit 1

# Thử 2 câu (T6 --limit 2 phải hoàn tất trước)
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_graph_rerank_agent --limit 2

# Chạy toàn bộ 100 câu (T6 phải hoàn tất 100/100 trước)
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf_graph_rerank_agent
```

T7 đọc checkpoint T6 và kiểm tra fingerprint; T7 không chạy retrieval hoặc
reranker lại. Nếu T6 chưa hoàn tất câu tương ứng, T7 dừng với lỗi rõ ràng.

### Quy tắc checkpoint

- Giữ nguyên dataset, `--top-n`, `--candidate-depth` và `--checkpoint-dir` giữa
  các lần chạy.
- Output mặc định nằm trong `logs/table5_results_v3/`.
- Mỗi mode tự lưu checkpoint vào
  `logs/table5_results_v3/checkpoints/<mode>/checkpoint.json`.
- Candidate pool dùng chung cho T3–T6 nằm tại
  `logs/table5_results_v3/checkpoints/hybrid_rrf/candidates.json`.
- Nếu hết quota, đổi key hợp lệ rồi chạy lại **đúng lệnh của mode đang dở**.
- Dòng log `[mode] completed X/100 case=Y` cho biết đã lưu đủ answer và bốn
  metrics của câu đó.
- Không xóa `logs/table5_results_v3/checkpoints/` khi muốn resume.

### Tùy chọn nâng cao

```powershell
# Chỉ định dataset khác (hỗ trợ CSV và định dạng dataset.md cũ)
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf --dataset data/dataset/test_experiment/file_test/Hung/dataset.md

# Đổi top_n retrieval; phải giữ cùng giá trị cho toàn bộ chuỗi thí nghiệm
python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf --top-n 10
```

---

## Bước 7 — Đọc kết quả

Output nằm tại `logs/table5_results_v3/`:


| File                              | Nội dung                                                               |
| ----------------------------------- | ------------------------------------------------------------------------- |
| `table5_results_{timestamp}.json` | Kết quả Table 5 T1–T7 theo các mode đã chạy                      |
| `table5_report_{timestamp}.md`    | Bảng Table 5; metric thiếu được ghi incomplete, không ghi pending |

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

## Appendix — T1–T7 được tạo thế nào?

T1–T6 tái sử dụng `rag_engine.py`; Graph là evidence augmentation, không phải RRF lane. T7 dùng exact evidence từ checkpoint T6:


| Mode                            | Cách gọi engine                                                                     |
| --------------------------------- | --------------------------------------------------------------------------------------- |
| `dense_only`                    | `engine.retrieve(query, hybrid_search=False, use_reranker=False)`                     |
| `sparse_only`                   | Gọi thẳng`engine.bm25_index.search()` + `engine.doc_store.mget()` (bỏ kênh dense) |
| `hybrid_rrf`                    | `engine.retrieve(query, hybrid_search=True, use_reranker=False)`                      |
| `hybrid_rrf_rerank`             | `engine.retrieve(query, hybrid_search=True, use_reranker=True)`                       |
| `hybrid_rrf_graph`              | T3 evidence + Graph evidence, giữ nguyên context budget                             |
| `hybrid_rrf_graph_rerank`       | T3 candidate pool + Graph evidence → reranker                                        |
| `hybrid_rrf_graph_rerank_agent` | T6 evidence cố định → Agent không tool/retrieval                                 |

Chi tiết: [Test_Ragas/test_table5_ragas.py](../Test_Ragas/test_table5_ragas.py) — hàm `retrieve_dense_only` / `retrieve_sparse_only` / `retrieve_hybrid_rrf` / `retrieve_hybrid_rrf_rerank`.
