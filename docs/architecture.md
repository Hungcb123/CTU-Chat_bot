# Chatbot Học bổng ĐHCT — Mô tả Kiến trúc Hệ thống

Chatbot hỏi–đáp tiếng Việt về **chính sách học bổng, miễn giảm học phí, trợ cấp xã hội và vay vốn** của Trường Đại học Cần Thơ. Hệ thống dùng kiến trúc **RAG nâng cao** (Small-to-Big + Re-ranking) để trả lời chính xác dựa trên văn bản hành chính đã số hóa.

> **Cảnh báo bảo mật:** File `.env` chứa secret dạng plaintext (`GOOGLE_API_KEY`, `GROQ_API_KEY`, `LLAMA_CLOUD_API_KEY`, `ZHIPUAI_API_KEY`). Nên xoay vòng key và đưa ra khỏi version control.

---

## 1. Tổng quan kiến trúc

```
                    ┌─────────────────────────────────────────────┐
                    │              NGƯỜI DÙNG (Browser)             │
                    │        UI/static: HTML + Vanilla JS           │
                    └──────────────────────┬──────────────────────┘
                                           │ fetch (JWT cookie)
                    ┌──────────────────────▼──────────────────────┐
                    │           FastAPI (Uvicorn :8000)             │
                    │  auth_controller · chat_controller · history  │
                    └───┬───────────────┬───────────────┬──────────┘
                        │               │               │
              ┌─────────▼──┐   ┌─────────▼────────┐  ┌───▼─────────┐
              │  Redis     │   │  RAG Engine       │  │ PostgreSQL  │
              │ (bộ nhớ    │   │ (Chunking +       │  │ (users,     │
              │  ngắn hạn) │   │  Qdrant + Rerank) │  │  sessions,  │
              └────────────┘   └───┬──────────┬────┘  │  messages,  │
                                   │          │       │  parent_docs)│
                          ┌────────▼──┐  ┌────▼─────┐ └─────────────┘
                          │  Qdrant   │  │ Gemini / │
                          │ (vector)  │  │ Groq LLM │
                          └───────────┘  └──────────┘
```

Backend chạy trên **host** (WSL/Windows). Ba dịch vụ dữ liệu (Postgres, Qdrant, Redis) chạy qua **Docker Compose**.

---

## 2. Thành phần chi tiết

### 2.1. Tầng Web API — [controller/](controller/)

- **Framework:** FastAPI, phục vụ bởi Uvicorn tại `0.0.0.0:8000`. CORS mở toàn bộ (`allow_origins=["*"]`). UI tĩnh mount tại `/`.
- **Khởi tạo (`lifespan`):** [controller/main.py](controller/main.py) nạp toàn bộ tài nguyên dùng chung vào `app.state` khi khởi động: client Redis, tạo bảng Postgres, khởi tạo RAG engine, LLM chính (Gemini), LLM viết lại (Groq), tool và prompt template.
- **Xác thực:** JWT (HS256) lưu trong **cookie HTTP-only** tên `access_token` (không dùng bearer header). Mật khẩu băm bằng bcrypt (passlib). Token TTL 7 ngày. `get_current_user` đọc cookie → giải mã JWT → nạp `User` từ Postgres.

**Các endpoint:**

| Method | Path | Chức năng |
|---|---|---|
| POST | `/auth/register` | Đăng ký (username unique, băm bcrypt) |
| POST | `/auth/login` | Đăng nhập, set JWT cookie |
| POST | `/auth/logout` | Xóa cookie |
| GET | `/auth/me` | Thông tin user hiện tại |
| POST | `/chat` | Chat RAG chính (cần auth), body `{query}` → `{answer}` |
| POST | `/new-chat` | Xóa key lịch sử Redis của user |
| POST | `/clear-history` | Tương tự (xóa lịch sử Redis) |

> Lưu ý: **không có streaming** — `/chat` trả về một JSON duy nhất; UI chỉ giả lập hiệu ứng đang gõ.

### 2.2. Tầng lưu trữ — [models/](models/)

- **PostgreSQL** với hai engine: **async** (`asyncpg`) phục vụ API, và **sync** (`psycopg`) phục vụ RAG docstore. Xem [models/database.py](models/database.py).
- **Redis** làm bộ nhớ hội thoại ngắn hạn: key `user:{id}:chat_history`, giới hạn 50 tin nhắn gần nhất.

**Các bảng ORM** (SQLAlchemy, khóa chính UUID dạng chuỗi) — xem [models/schema.py](models/schema.py):

| Bảng | Cột chính | Vai trò |
|---|---|---|
| `users` | id, username (unique), hashed_password, role, created_at | Tài khoản |
| `chat_sessions` | id, user_id (FK), title, created_at, updated_at | Phiên chat |
| `chat_messages` | id, session_id (FK), role (`human`/`ai`), content, created_at | Tin nhắn |
| `parent_documents` | id (map với vector Qdrant), content, **metadata_json (JSONB)**, created_at | DocStore của RAG |

### 2.3. LLM & RAG — [LLM/](LLM/) và [Chunking/sematic_chunking_rerank.py](Chunking/sematic_chunking_rerank.py)

RAG sản xuất nằm trong `AdvancedChunkingEngine` (khởi tạo tại [main.py](controller/main.py)). File [LLM/llm.py](LLM/llm.py) chỉ là bản demo CLI cũ.

**Các mô hình:**

| Vai trò | Mô hình | Ghi chú |
|---|---|---|
| Sinh câu trả lời + tool calling | Google **Gemini** `gemini-3.1-flash-lite` | temp 0.4 |
| Viết lại câu hỏi (Rewriter) | Groq **Llama** `llama-3.1-8b-instant` | temp 0.0, siêu tốc |
| Embedding | `bkai-foundation-models/vietnamese-bi-encoder` | 768 chiều, cosine |
| Re-ranking | `BAAI/bge-reranker-v2-m3` (CrossEncoder, CUDA) | max_length 512 |

**Kiến trúc truy xuất (Small-to-Big + Re-rank):**

1. `ParentDocumentRetriever` trên Qdrant (collection `ctu_scholarship_docs_v3`, HNSW m=16/ef=100) làm vector store; `PostgresDocStore` (bảng `parent_documents`) làm parent docstore.
2. Truy xuất cơ sở: top **k=10** child chunk, lọc `metadata.status == "active"`, rồi lấy parent tương ứng từ Postgres.
3. Re-rank: `ContextualCompressionRetriever` bọc `TemporalCrossEncoderReranker(top_n=3)` — 10 parent vào, giữ 3 tốt nhất.

**Ưu tiên ngày gần nhất (tie-break mềm):** `TemporalCrossEncoderReranker` (kế thừa `CrossEncoderReranker`) vẫn xếp hạng chính theo điểm liên quan của Cross-Encoder. Chỉ khi hai parent có điểm **chênh ≤ `score_tolerance` (0.05)** — coi như "gần bằng nhau" — thì mới ưu tiên parent có `timestamp` mới hơn. Nhờ vậy văn bản cũ còn hiệu lực không bị loại oan, mà bản mới cùng chủ đề được đẩy lên trên. Văn bản mới nhưng lạc đề (điểm thấp) vẫn bị loại khỏi top 3.

**Chiến lược chunking (Hướng A — bảo toàn bảng):**
- Cắt theo header Markdown (`#`/`##`/`###`, giữ header).
- Cắt cấp 2 giữ nguyên bảng: prose chặt ~2800 chars/overlap 100; **bảng giữ nguyên khối**, nếu quá dài mới cắt theo dòng và tiêm lại header cột + dòng phân cách vào mỗi mảnh (tránh mất tên cột).
- Lọc rác < 50 chars chỉ áp cho prose, không áp cho bảng.
- Child chunk 400 chars/overlap 50 để vector match nhạy.
- Trích ngày ban hành bằng regex → metadata thời gian (`effective_date`, `timestamp`).

**Tool calling:** [Tools/scholarship_tool.py](Tools/scholarship_tool.py) — hàm `tinh_tien_hoc_bong(gpa, drl, khoi_nganh)` đọc `data/hoc_bong.json` (quy định Quyết định 3530), phân loại và trả về mức học bổng theo khối ngành. Bind qua `llm.bind_tools`.

### 2.4. Số hóa / OCR — [OCR/](OCR/)

- **Đường active (cloud):** [OCR/API/llama.py](OCR/API/llama.py) gọi **LlamaParse** (LlamaIndex Cloud) với `language=vi`, `premium_mode=true` cho ảnh scan. Luồng batch: đọc PDF từ `Data/Input/` → parse song song → ghi `.md` vào `clean_markdown/API_Llama/` → làm sạch → chuyển PDF sang `Data/Done/`.
- **Làm sạch:** `EnterpriseMarkdownCleanser` trong [OCR/API/new_clean.py](OCR/API/new_clean.py) — regex loại nhiễu parser, watermark, boilerplate hành chính; chuẩn hóa bảng; **giữ lại dòng ngày tháng** cho metadata thời gian.
- **Đường thay thế (local, không dùng active):** `OCR/MinerU/` — bộ OCR local đầy đủ (layout/formula/VLM).

### 2.5. Giao diện — [UI/static/](UI/static/)

- **Stack:** Vanilla JS (không framework), `marked.js` (CDN) render markdown, Google Fonts (Inter).
- **Gọi backend:** `fetch` tới `/chat`, `/new-chat`, `/clear-history`, `/auth/*`. Cookie JWT tự đính kèm (same-origin).
- **Tính năng:** modal đăng nhập/đăng ký, kiểm tra trạng thái auth khi tải, gửi chat với hiệu ứng đang gõ (không streaming thật), nút New Chat / Clear History, render markdown câu trả lời. Nút đính kèm file có trên UI nhưng chưa có handler.

### 2.6. Hạ tầng — [docker-compose.yml](docker-compose.yml)

Compose v3.8 định nghĩa **ba dịch vụ dữ liệu** (app chạy trên host, không trong compose):

| Service | Image | Port | Volume |
|---|---|---|---|
| qdrant | `qdrant/qdrant:latest` | 6333 (HTTP), 6334 (gRPC) | `./qdrant_storage` |
| redis | `redis:7-alpine` | 6379 | `./redis_data` |
| postgres | `postgres:15-alpine` | 5432 | `postgres_data` (db `ctu_chatbot`) |

Không có Dockerfile cho app ở gốc; không có `requirements.txt` ở gốc project (chỉ nằm trong `venv`/`wsl_venv`/`MinerU`). `start_env.sh` nạp `.env`. Chạy trên WSL (đường dẫn `/mnt/d/Project/Chatbot/...` hardcode trong script ingestion).

---

## 3. Luồng dữ liệu đầu-cuối

### 3.1. Nạp dữ liệu (Ingestion): PDF → OCR → Markdown → Chunking → Vector DB

1. Đặt PDF vào `Data/Input/`. [OCR/API/llama.py](OCR/API/llama.py) đẩy lên **LlamaParse cloud**, poll job, lấy markdown.
2. Ghi markdown vào `clean_markdown/API_Llama/`, làm sạch bằng `EnterpriseMarkdownCleanser`, chuyển PDF sang `Data/Done/`.
3. [Chunking/ingest_all.py](Chunking/ingest_all.py) tạo bảng Postgres, khởi tạo engine, `clear_database()` (xóa Qdrant + `parent_documents`), rồi nạp mọi file `.md`.
4. Mỗi file: trích ngày → chia theo header → cắt cấp 2 (giữ bảng nguyên khối) → gắn metadata (`source`, `doc_type=policy`, `effective_date`, `timestamp`, `status=active`).
5. Parent lưu vào `PostgresDocStore`; child (400 chars) embed bằng `vietnamese-bi-encoder` và upsert lên Qdrant, mỗi child map về parent id.

### 3.2. Truy vấn (Query): Câu hỏi → Truy xuất → Re-rank → LLM → Trả lời

1. `POST /chat` (đã auth) với `{query}`. Nạp 5 lượt chat gần nhất từ Redis.
2. Nếu có lịch sử → **Groq Llama** viết lại câu hỏi thành truy vấn độc lập (bỏ qua ở câu đầu để tối ưu tốc độ).
3. `engine.retriever.invoke(search_query)`: Qdrant tìm top k=10 child (lọc `status=active`) → lấy parent từ Postgres.
4. **BGE reranker-v2-m3** (qua `TemporalCrossEncoderReranker`) chấm lại 10 parent, giữ top 3 → ghép thành chuỗi `{context}`. Khi điểm gần bằng nhau thì ưu tiên văn bản có `timestamp` mới hơn.
5. Dựng prompt (luật phạm vi + context + lịch sử + câu hỏi gốc) → gọi **Gemini** đã bind tool. Nếu Gemini yêu cầu `tinh_tien_hoc_bong` → chạy tool → nạp `ToolMessage` → gọi lại Gemini để sinh câu trả lời cuối.
6. Trả `{answer}`; đẩy human+AI vào Redis (trim 50); background task lưu vào Postgres `chat_messages`.

---

## 4. Ghi chú vận hành & bảo mật

- **Secret trong `.env`** đang ở dạng plaintext → nên xoay vòng key và đưa ra khỏi version control.
- **CORS mở toàn bộ** (`allow_origins=["*"]`) → cần siết theo domain thật khi lên production.
- **Session Postgres suy ra từ MD5 của history key** → mỗi user chỉ có một phiên cố định, không tách theo từng cuộc hội thoại.
- **Đường dẫn WSL hardcode** (`/mnt/d/Project/Chatbot/...`) trong script ingestion — chạy Windows trực tiếp sẽ không thấy file.
- **GPU 4GB:** reranker giới hạn `max_length=512` và `k=10` để tránh CUDA OOM.
