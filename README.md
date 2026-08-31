# 🎓 CTU Scholarship & Academic Chatbot (Advanced RAG System)

Trợ lý ảo AI thông minh hỗ trợ giải đáp chính sách sinh viên, tính toán mức học phí, chính sách miễn giảm và xét duyệt học bổng cho sinh viên **Trường Đại học Cần Thơ (CTU)**.

Hệ thống được xây dựng trên kiến trúc **Hybrid RAG tiên tiến** (Dense Vector Search + Sparse BM25 + Temporal Cross-Encoder Reranking + Dynamic Tool Calling).

---

## 🌟 Tính Năng Nổi Bật

- **Hybrid Retrieval (Tìm kiếm kết hợp)**: Kết hợp sức mạnh ngữ nghĩa của **Vector Search (Qdrant)** và độ chính xác từ khóa của **BM25s (tách từ tiếng Việt với PyVi)** qua thuật toán **Reciprocal Rank Fusion (RRF)**.
- **Temporal Cross-Encoder Re-ranking**: Tái xếp hạng tài liệu với mô hình Cross-Encoder đa ngôn ngữ (`BAAI/bge-reranker-v2-m3`) kết hợp thuật toán **Tie-breaking thông minh theo thời gian** (ưu tiên văn bản quy định mới nhất khi điểm ngữ nghĩa tương đồng).
- **Tự động gọi công cụ tính toán (Function Calling / Tool Use)**:
  - 🏆 `tinh_tien_hoc_bong`: Tính toán chính xác loại học bổng (Xuất sắc, Giỏi, Khá) và số tiền nhận được dựa trên GPA, Điểm Rèn Luyện (ĐRL) và ngành học.
  - 💰 `tinh_toan_hoc_phi`: Tính số tiền được miễn giảm và số tiền thực đóng dựa trên quy chế miễn giảm học phí và bảng giá trần theo quy định nhà nước.
- **Quản lý Session & Bộ nhớ đệm đa tầng**:
  - **Redis**: Lưu trữ bộ đệm hội thoại ngắn hạn (Short-term buffer) và quản lý session siêu tốc.
  - **PostgreSQL**: Lưu trữ lịch sử trò chuyện dài hạn (Long-term chat history), quản lý tài khoản người dùng và văn bản gốc (Parent Documents).
- **Nạp tài liệu tự động (Document Ingestion & OCR)**: Tích hợp LlamaParse tự động trích xuất cấu trúc bảng biểu từ file PDF thành định dạng Markdown chuẩn và lập chỉ mục hai cấp độ Parent-Child.
- **Hỗ trợ chạy hoàn toàn Offline cho các mô hình nhúng**: Tải trước các mô hình AI cục bộ vào máy để khởi động tức thì, không phụ thuộc vào kết nối mạng HuggingFace.

---

## 🏗️ Kiến Trúc Hệ Thống (Architecture)

```mermaid
flowchart TD
    UserQuery([Câu hỏi người dùng]) --> Rewriter[Query Rewriter & Intent Classifier]
    Rewriter --> Router{Phân loại tác vụ}

    Router -->|Tra cứu chung / RAG| Hybrid[Hybrid Search Engine]
    Router -->|Tính toán trực tiếp| Tools[Tool Calling Engine]

    subgraph Hybrid Search Pipeline
        Hybrid --> Vector[Dense Vector Search\nQdrant + Bi-Encoder]
        Hybrid --> BM25[Sparse Lexical Search\nBM25s + PyVi]
        Vector & BM25 --> RRF[Reciprocal Rank Fusion\nRRF k=60]
        RRF --> Rerank[Temporal Cross-Encoder Reranker\nbge-reranker-v2-m3]
    end

    Rerank --> Context[Context Builder + Tuition Catalog]
    Context --> LLM[Google Gemini 1.5/2.0 Flash]
    Tools --> LLM
    LLM --> Response([Câu trả lời hoàn chỉnh])
```

---

## 📋 Yêu Cầu Môi Trường (Prerequisites)

- **Hệ điều hành**: Linux (Ubuntu 20.04/22.04 LTS khuyên dùng) hoặc Windows 10/11 với **WSL 2**.
- **Python**: Phiên bản `3.10` hoặc `3.11`.
- **Docker & Docker Compose**: Để chạy cụm dịch vụ Qdrant, PostgreSQL, Redis.
- **Phần cứng đề xuất**:
  - RAM: Tối thiểu 8 GB (Khuyên dùng 16 GB).
  - GPU (Tùy chọn): GPU NVIDIA hỗ trợ CUDA để tăng tốc Embedding và Cross-Encoder. Hệ thống vẫn hỗ trợ chạy tốt trên CPU.

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy (Step-by-Step)

### Bước 1: Clone Repository & Tạo Môi Trường Ảo

```bash
# Clone dự án về máy
git clone https://github.com/Hungcb123/CTU-Chat_bot.git
cd CTU-Chat_bot

# Tạo virtual environment
python3 -m venv wsl_venv

# Kích hoạt môi trường ảo
source wsl_venv/bin/activate
or
wsl_venv\Scripts\activate.bat
or with powershell
cmd /k "wsl_venv\Scripts\activate.bat"
```

---

### Bước 2: Cài Đặt Thư Viện Phụ Thuộc

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Bước 3: Cấu Hình Biến Môi Trường (`.env`)

Sao chép file cấu hình mẫu `.env.example` thành `.env`:

```bash
cp .env.example .env
```

Mở file `.env` và điền các API Key cần thiết:

```env
# 1. API Keys bắt buộc
GOOGLE_API_KEY=AIzaSy...your_gemini_key_here
LLAMA_CLOUD_API_KEY=llx-...your_llama_cloud_key_here

# 2. Cơ sở dữ liệu (mặc định khớp với docker-compose.yml)
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/ctu_chatbot
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_ALIAS=ctu_scholarship_docs_current

# 3. Bảo mật
JWT_SECRET_KEY=ctu_chatbot_secret_key_2026_change_in_prod

# 4. Cấu hình RAG & Mô hình Offline
RAG_METADATA_FILTER_ENABLED=true
RAG_EMBEDDING_MODEL=./models/vietnamese-bi-encoder
RAG_RERANKER_MODEL=./models/bge-reranker-v2-m3
RAG_RERANKER_DEVICE=cuda  # hoặc 'cpu' nếu máy không có card NVIDIA
```

---

### Bước 4: Khởi Động Hạ Tầng Dịch Vụ (Docker)

Chạy lệnh Docker Compose để bật đồng thời **Qdrant (Vector DB)**, **PostgreSQL (CSDL quan hệ)** và **Redis (Bộ nhớ đệm)**:

```bash
docker compose up -d
```

Kiểm tra trạng thái các container:

```bash
docker compose ps
```

_(Đảm bảo cả 3 container `chatbot-qdrant`, `ctu-chatbot-postgres`, `ctu-chatbot-redis` đều ở trạng thái `running` / `Up`)._

---

### Bước 5: Tải Mô Hình AI Về Máy Cục Bộ (Chạy Offline 100%)

Tải sẵn các mô hình Embedding và Cross-Encoder vào thư mục `models/` để ứng dụng nạp thẳng từ ổ cứng lúc khởi động, không cần chờ tải qua internet:

```bash
python -c "
from huggingface_hub import snapshot_download
print('📥 Đang tải Embedding Model...')
snapshot_download(repo_id='bkai-foundation-models/vietnamese-bi-encoder', local_dir='models/vietnamese-bi-encoder')
print('📥 Đang tải Cross-Encoder Reranker Model...')
snapshot_download(repo_id='BAAI/bge-reranker-v2-m3', local_dir='models/bge-reranker-v2-m3')
print('✅ Đã tải xong toàn bộ mô hình về ./models/!')
"
```

---

### Bước 6: Xây Dựng Chỉ Mục Dữ Liệu (Indexing)

Hệ thống cung cấp các file markdown quy chế mẫu sẵn tại `data/markdown/`. Bạn cần tạo chỉ mục cho chúng:

1. **Xây dựng chỉ mục BM25 (Lexical Search)**:
   ```bash
   python scripts/build_bm25_index.py
   ```
2. **Nạp và tạo chỉ mục Vector trong Qdrant**:
   ```bash
   python scripts/reindex_all.py build --index-version 2026-08-31-v1
   ```

---

### Bước 7: Khởi Động Ứng Dụng (Start Backend & UI)

Chạy ứng dụng thông qua script khởi động:

```bash
./start_env.sh
```

Hoặc chạy trực tiếp bằng Python:

```bash
python app/main.py
```

Hoặc chạy qua máy chủ Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

Sau khi máy chủ báo `🚀 Toàn bộ Engine đã sẵn sàng tiếp nhận Request!`, hãy mở trình duyệt web và truy cập:

👉 **`http://localhost:8000`**

---

## 📁 Cấu Trúc Thư Mục Dự Án (Project Structure)

```text
├── app/
│   ├── api/                     # Các Endpoint API (FastAPI Routers)
│   │   ├── auth.py              # Đăng ký, đăng nhập & cấp phát JWT token
│   │   ├── chat.py              # Xử lý hội thoại, RAG Pipeline & Stream response
│   │   ├── document.py          # API upload, OCR PDF và nạp tài liệu
│   │   └── history.py           # Quản lý lịch sử đoạn chat người dùng
│   ├── core/
│   │   └── database.py          # Cấu hình SQLAlchemy kết nối PostgreSQL Async/Sync
│   ├── models/                  # Định nghĩa Data Schemas (Pydantic & SQLAlchemy ORM)
│   │   ├── pydantic.py
│   │   └── schema.py
│   ├── services/                # Các dịch vụ xử lý AI & Nghiệp vụ cốt lõi
│   │   ├── bm25_service.py      # BM25 Lexical Indexing & PyVi Vietnamese Tokenizer
│   │   ├── document_metadata.py # Quản lý Metadata kinh doanh của tài liệu
│   │   ├── llm_service.py       # Wrapper tương tác với LLM
│   │   ├── ocr_service.py       # Tích hợp LlamaParse OCR
│   │   ├── query_intent.py      # Phân loại Intent & Điều hướng truy vấn
│   │   ├── rag_engine.py        # Core RAG: Splitter, Hybrid Search, Reranker, Ingestion
│   │   └── tuition_catalog.py   # Catalog tra cứu học phí theo ngành/khóa
│   ├── tools/                   # Các Tool Calling chuyên dụng cho sinh viên
│   │   ├── scholarship.py       # Công cụ tính điểm xét học bổng
│   │   └── tuition.py           # Công cụ tính toán học phí miễn giảm
│   └── main.py                  # Entrypoint chính khởi động FastAPI & Lifespan
├── data/
│   ├── markdown/                # Kho văn bản quy chế đã được cấu trúc thành Markdown
│   ├── document_metadata.json   # Metadata thông tin văn bản
│   └── tuition_catalog.json     # Bảng giá học phí các ngành học
├── frontend/                    # Giao diện Chatbot SPA (HTML5/CSS3/Vanilla JS)
│   ├── css/
│   ├── js/
│   └── index.html
├── models/                      # Thư mục lưu trữ trọng số mô hình AI cục bộ (Offline)
│   ├── bge-reranker-v2-m3/
│   └── vietnamese-bi-encoder/
├── scripts/                     # Bộ công cụ CLI & Đánh giá (Evaluation scripts)
│   ├── build_bm25_index.py      # Script build nhanh chỉ mục BM25
│   ├── reindex_all.py           # Script Blue-Green reindexing toàn diện
│   ├── batch_process.py         # Batch OCR tài liệu PDF
│   └── run_tool_calling_experiment.py
├── docker-compose.yml           # Định nghĩa các container Qdrant, Postgres, Redis
├── requirements.txt             # Danh sách thư viện Python
├── start_env.sh                 # Script nạp biến môi trường và chạy app nhanh
└── README.md                    # Tài liệu hướng dẫn sử dụng
```

---

## 🛠️ Bộ Lệnh Dòng Lệnh Tiện Ích (CLI Tools)

| Lệnh                                                                                                                              | Mô Tả                                                       |
| :-------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------- |
| `python scripts/build_bm25_index.py`                                                                                              | Quét 244 văn bản Markdown và tái tạo chỉ mục BM25           |
| `python scripts/reindex_all.py build --index-version 2026-08-31-v1`                                                              | Nạp toàn bộ dữ liệu vào collection mới của Qdrant           |
| `python scripts/reindex_all.py swap --alias-name ctu_scholarship_docs_current --target-collection ctu_scholarship_docs_<version>` | Chuyển đổi Alias Qdrant sang collection mới (Zero-downtime) |
| `docker compose logs -f`                                                                                                          | Xem log trực tiếp của các container hạ tầng                 |

---

## 🤝 Đóng Góp & Phát Triển

Dự án được xây dựng phục vụ nghiên cứu và hỗ trợ sinh viên Trường Đại học Cần Thơ. Mọi đóng góp (Pull Request, Báo lỗi Issue) đều được chào đón!

---

_Phát triển với ❤️ dành cho sinh viên Trường Đại học Cần Thơ._
