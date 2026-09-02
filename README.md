  

# 🎓 CTU Academic Chatbot — Multi-Agent RAG System

<div align="center">

---

## 🌟 Tính Năng Nổi Bật

### 🤖 Multi-Agent System (LangGraph)

Kiến trúc **Supervisor Pattern** với 4 Agent chuyên biệt, mỗi agent được trang bị bộ tools riêng:

| Agent                         | Chuyên môn                                       | Tools                         |
| :---------------------------- | :------------------------------------------------- | :---------------------------- |
| 🎯**Supervisor**        | Phân tích intent, query rewrite, routing         | Structured Output (Gemini)    |
| 📚**Academic Agent**    | Chương trình đào tạo, ngành học, môn học | 6 Neo4j Graph Tools (ReAct)   |
| 💰**Financial Agent**   | Học phí, miễn giảm, tính toán tài chính    | 3 Tools (Graph + JSON + Calc) |
| 🏆**Scholarship Agent** | Học bổng khuyến khích học tập                | 1 Calculator Tool             |
| 📋**General Agent**     | Quy chế học vụ, thủ tục, tuyển sinh          | RAG Context only              |

### 🔍 Hybrid RAG Pipeline

- **Dense Vector Search**: Qdrant DB + Vietnamese Bi-Encoder (`bkai-foundation-models/vietnamese-bi-encoder`)
- **Sparse Lexical Search**: BM25s + tách từ tiếng Việt với PyVi
- **Reciprocal Rank Fusion (RRF)**: Kết hợp kết quả từ cả hai kênh (k=60)
- **Temporal Cross-Encoder Reranking**: `BAAI/bge-reranker-v2-m3` với Tie-breaking thông minh theo thời gian — ưu tiên văn bản quy định mới nhất khi điểm ngữ nghĩa tương đồng
- **Parent-Child Chunking**: Small-to-Big retrieval, Child tìm kiếm (400 chars) → Parent trả context đầy đủ

### 🕸️ Neo4j Knowledge Graph

- Lưu trữ **toàn bộ chương trình đào tạo** dưới dạng đồ thị: `Program → Block → Course`, quan hệ tiên quyết `REQUIRES`
- **Lazy auto-ingest**: Khởi động tự kiểm tra và nạp dữ liệu nếu graph rỗng
- **6 Academic Tools**: Tra cứu ngành, so sánh ngành, tìm ngành, chuỗi tiên quyết, môn chung, tìm ngành theo môn
- **2 Tuition Tools**: Tra cứu học phí từ graph (ưu tiên) với JSON fallback, tra cứu quy định học phí

### 🧠 LLM-powered Intent Classification

- **Gemini Flash Lite** phân loại intent với structured output (`lane`, `confidence`, `params`)
- **Rule-based fallback**: Hệ thống từ khóa deterministic dự phòng khi LLM unavailable
- **11 intent lanes**: ACTUAL_TUITION, EXEMPTION_BASIS, EXEMPTION_POLICY, CALCULATION, BOTH, AMBIGUOUS_TUITION, SCHOLARSHIP, STUDENT_LOAN, SOCIAL_SUPPORT, ACADEMIC_PROGRAM, ACADEMIC_RULES, OTHER

### ⚡ Bộ Công Cụ Tính Toán (11 LangChain Tools)

<details>
<summary><b>📚 Academic Tools (6)</b> — Neo4j Graph-backed</summary>

| Tool                     | Mô tả                                                                     |
| :----------------------- | :-------------------------------------------------------------------------- |
| `tra_cuu_nganh`        | Tra cứu chi tiết 1 ngành (danh sách môn, tín chỉ, khối kiến thức) |
| `so_sanh_nganh`        | So sánh 2 ngành side-by-side (môn chung, môn riêng)                    |
| `tim_nganh`            | Tìm ngành theo tiêu chí tự do (khoa, tín chỉ, bằng cấp)            |
| `xem_chuoi_tien_quyet` | Chuỗi môn tiên quyết (variable-length path traversal)                   |
| `mon_chung_giua_nganh` | Môn học chung giữa 2 ngành (graph intersection)                         |
| `tim_nganh_co_mon`     | Tìm ngành nào có dạy môn X (reverse traversal)                        |

</details>

<details>
<summary><b>💰 Financial Tools (3)</b> — Graph + JSON + Calculator</summary>

| Tool                         | Mô tả                                                                             |
| :--------------------------- | :---------------------------------------------------------------------------------- |
| `tra_cuu_hoc_phi_graph`    | Tra cứu học phí theo ngành + khóa từ Neo4j (ưu tiên), JSON fallback         |
| `tra_cuu_quy_dinh_hoc_phi` | Tra cứu quy định chung (hệ số ngoài giờ, VLVH, từ xa, thạc sĩ, tiến sĩ) |
| `tinh_toan_hoc_phi`        | Tính số tiền thực đóng sau miễn giảm                                        |

</details>

<details>
<summary><b>🏆 Scholarship Tools (2)</b> — Calculator</summary>

| Tool                   | Mô tả                                                                                |
| :--------------------- | :------------------------------------------------------------------------------------- |
| `tinh_tien_hoc_bong` | Tính loại học bổng (Xuất sắc / Giỏi / Khá) và số tiền dựa trên GPA + ĐRL |
| `tuition_lookup`     | Tra cứu nhanh mức học phí theo ngành                                              |

</details>

### 🗄️ Quản Lý Session & Lưu Trữ Đa Tầng

- **Redis**: Session cache ngắn hạn, chat buffer siêu tốc
- **PostgreSQL**: Lịch sử trò chuyện dài hạn, quản lý tài khoản, Parent Document Store
- **Qdrant**: Vector embeddings cho Dense Search
- **Neo4j**: Knowledge Graph chương trình đào tạo & học phí

### 📄 Nạp Tài Liệu Tự Động

- **LlamaParse OCR**: Trích xuất bảng biểu từ PDF → Markdown chuẩn
- **Parent-Child Indexing**: Lập chỉ mục 2 cấp độ cho retrieval chất lượng cao
- **BM25 Vietnamese Tokenizer**: Tách từ tiếng Việt với PyVi cho lexical search
- **Offline AI Models**: Tải trước Embedding & Cross-Encoder, khởi động tức thì không cần internet

---

## 🏗️ Kiến Trúc Hệ Thống

```mermaid
flowchart TD
    UserQuery([👤 Câu hỏi người dùng]) --> Supervisor

    subgraph Supervisor["🎯 Supervisor Agent"]
        QR[Query Rewriter<br/>Gemini 3.1 Flash Lite] --> IC[Intent Classifier<br/>Structured Output]
    end

    Supervisor -->|"academic"| AcademicAgent
    Supervisor -->|"financial / scholarship / general"| Retrieval

    subgraph AcademicAgent["📚 Academic Agent (ReAct)"]
        Neo4jTools["6 Neo4j Graph Tools<br/>tra_cuu · so_sanh · tim_nganh<br/>tien_quyet · mon_chung · tim_theo_mon"]
    end

    subgraph Retrieval["🔍 Hybrid RAG Retrieval"]
        VS[Dense Vector Search<br/>Qdrant + Bi-Encoder] & BM25[Sparse BM25<br/>PyVi Tokenizer]
        VS & BM25 --> RRF[Reciprocal Rank Fusion<br/>k=60]
        RRF --> Rerank[Temporal Cross-Encoder<br/>bge-reranker-v2-m3]
        GraphLookup[Neo4j Tuition Lookup<br/>→ JSON Fallback] --> Context
        Rerank --> Context[Context Builder]
    end

    Retrieval -->|"financial"| FinAgent["💰 Financial Agent<br/>3 Tools (Graph + JSON + Calc)"]
    Retrieval -->|"scholarship"| SchoAgent["🏆 Scholarship Agent<br/>1 Calculator Tool"]
    Retrieval -->|"general"| GenAgent["📋 General Agent<br/>RAG Context Only"]

    AcademicAgent --> Response
    FinAgent --> Response
    SchoAgent --> Response
    GenAgent --> Response([💬 Câu trả lời])
```

### Luồng Xử Lý Chi Tiết

```
START → supervisor (Query Rewrite + Intent Routing)
    ├── "academic" → academic_agent (ReAct + Neo4j Tools) → END
    └── "financial|scholarship|general" → retrieval (Hybrid RAG)
            ├── "financial" → financial_agent (RAG + Tools) → END
            ├── "scholarship" → scholarship_agent (RAG + Tool) → END
            └── "general" → general_agent (RAG only) → END
```

---

## 📋 Yêu Cầu Môi Trường

| Thành phần     | Yêu cầu                                                                  |
| :--------------- | :------------------------------------------------------------------------- |
| **OS**     | Linux (Ubuntu 20.04/22.04 LTS) hoặc Windows 10/11 với WSL 2              |
| **Python** | 3.10 hoặc 3.11                                                            |
| **Docker** | Docker Engine + Docker Compose (4 containers)                              |
| **RAM**    | Tối thiểu 8 GB · Khuyên dùng 16 GB                                    |
| **GPU**    | *Tùy chọn* — NVIDIA CUDA cho Embedding & Cross-Encoder (hỗ trợ CPU) |

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### Bước 1: Clone & Tạo Môi Trường Ảo

```bash
git clone https://github.com/Hungcb123/CTU-Chat_bot.git
cd CTU-Chat_bot

python3 -m venv wsl_venv
source wsl_venv/bin/activate
or
wsl_venv\Scripts\activate.bat
or with powershell
cmd /k "wsl_venv\Scripts\activate.bat"
```

### Bước 2: Cài Đặt Thư Viện

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 3: Cấu Hình Biến Môi Trường

```bash
cp .env.example .env
```

Mở `.env` và điền các giá trị:

```env
# ── API Keys (Bắt buộc) ──
GOOGLE_API_KEY=AIzaSy...your_gemini_key
LLAMA_CLOUD_API_KEY=llx-...your_llama_cloud_key

# ── Databases (mặc định khớp docker-compose.yml) ──
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/ctu_chatbot
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_ALIAS=ctu_scholarship_docs_current

# ── Bảo mật ──
JWT_SECRET_KEY=your_super_secret_jwt_key_here_change_in_production

# ── RAG & Mô hình Offline ──
RAG_METADATA_FILTER_ENABLED=true
RAG_EMBEDDING_MODEL=./models/vietnamese-bi-encoder
RAG_RERANKER_MODEL=./models/bge-reranker-v2-m3
RAG_RERANKER_DEVICE=cuda    # hoặc 'cpu' nếu không có GPU NVIDIA
```

### Bước 4: Khởi Động Hạ Tầng Docker (4 Services)

```bash
docker compose up -d
```

Kiểm tra tất cả 4 container đã chạy:

```bash
docker compose ps
```

| Container                | Service           | Port                                |
| :----------------------- | :---------------- | :---------------------------------- |
| `chatbot-qdrant`       | Qdrant Vector DB  | `6333`, `6334`                  |
| `ctu-chatbot-postgres` | PostgreSQL 15     | `5432`                            |
| `ctu-chatbot-redis`    | Redis 7           | `6379`                            |
| `ctu-chatbot-neo4j`    | Neo4j 5.20 + APOC | `7474` (Browser), `7687` (Bolt) |

### Bước 5: Tải Mô Hình AI Offline

```bash
python -c "
from huggingface_hub import snapshot_download
print('📥 Đang tải Embedding Model...')
snapshot_download(repo_id='bkai-foundation-models/vietnamese-bi-encoder', local_dir='models/vietnamese-bi-encoder')
print('📥 Đang tải Cross-Encoder Reranker Model...')
snapshot_download(repo_id='BAAI/bge-reranker-v2-m3', local_dir='models/bge-reranker-v2-m3')
print('✅ Hoàn tất!')
"
```

### Bước 6: Xây Dựng Chỉ Mục Dữ Liệu

### Bước 6: Xây Dựng Chỉ Mục Dữ Liệu (Indexing)

Hệ thống cung cấp các file markdown quy chế mẫu sẵn tại `data/markdown/`. Bạn cần tạo chỉ mục cho chúng:

```bash
# BM25 Index (Lexical Search)
python scripts/build_bm25_index.py

# Vector Index (Qdrant)
python scripts/reindex_all.py build --index-version 2026-09-02-v1

# Kiểm tra collection trước khi kích hoạt
python scripts/reindex_all.py validate --index-version 2026-09-02-v1

# Kích hoạt alias live cho ứng dụng và benchmark
python scripts/reindex_all.py activate --index-version 2026-09-02-v1 --alias ctu_scholarship_docs_current
```

> **📝 Note:** Neo4j Knowledge Graph sẽ tự động được nạp dữ liệu (lazy init) khi ứng dụng khởi động lần đầu. Có thể nạp thủ công bằng `python Graph_DB/app/ingest.py`.

---

### Bước 7: Khởi Động Ứng Dụng (Start Backend & UI)

```bash
# Cách 1: Script khởi động nhanh
./start_env.sh

# Cách 2: Chạy trực tiếp
python app/main.py

# Cách 3: Uvicorn với hot-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

Sau khi thấy `🚀 Toàn bộ Engine đã sẵn sàng tiếp nhận Request!`, truy cập:

🌐 **http://localhost:8000**

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
CTU-Chat_bot/
├── app/
│   ├── agents/                         # 🤖 Multi-Agent System (LangGraph)
│   │   ├── graph.py                    #   Supervisor Pattern StateGraph (6 nodes)
│   │   └── prompts.py                  #   System prompts cho 5 agents
│   ├── api/                            # 🌐 FastAPI Routers
│   │   ├── auth.py                     #   Đăng ký, đăng nhập & JWT
│   │   ├── chat.py                     #   Xử lý hội thoại & Stream response
│   │   ├── document.py                 #   Upload, OCR PDF & nạp tài liệu
│   │   └── history.py                  #   Quản lý lịch sử chat
│   ├── core/
│   │   └── database.py                 #   SQLAlchemy Async Engine (PostgreSQL)
│   ├── models/                         # 📊 Data Schemas
│   │   ├── pydantic.py                 #   Request/Response models
│   │   └── schema.py                   #   SQLAlchemy ORM (User, Session, Message)
│   ├── services/                       # ⚙️ Business Logic & AI Services
│   │   ├── bm25_service.py             #   BM25 + PyVi Vietnamese Tokenizer
│   │   ├── document_metadata.py        #   Metadata quản lý tài liệu (JSON)
│   │   ├── document_metadata_pg.py     #   Metadata quản lý tài liệu (PostgreSQL)
│   │   ├── graph_service.py            #   Neo4j Cypher queries + Auto-ingest
│   │   ├── llm_classifier.py           #   LLM Intent Classifier + Rule fallback
│   │   ├── llm_service.py              #   LLM wrapper (Gemini)
│   │   ├── ocr_service.py              #   LlamaParse OCR integration
│   │   ├── query_intent.py             #   Deterministic intent routing (12 lanes)
│   │   ├── rag_engine.py               #   Core RAG: Chunking, Hybrid Search, Reranker
│   │   └── tuition_catalog.py          #   Structured tuition rate catalog (JSON)
│   ├── tools/                          # 🔧 LangChain Tool Definitions
│   │   ├── academic_program.py         #   6 Neo4j academic graph tools
│   │   ├── scholarship.py              #   Scholarship calculator
│   │   ├── tuition.py                  #   Tuition fee calculator
│   │   ├── tuition_graph.py            #   2 Neo4j tuition lookup tools
│   │   └── tuition_lookup.py           #   Quick tuition lookup helper
│   ├── utils/
│   │   └── clean_md.py                 #   Markdown cleaning utilities
│   └── main.py                         #   🚀 Entrypoint: FastAPI + Lifespan init
├── data/
│   ├── markdown/                       #   Kho văn bản quy chế (Markdown)
│   ├── markdown_graph/                 #   Dữ liệu chương trình đào tạo (Neo4j source)
│   ├── document_metadata.json          #   Metadata thông tin văn bản
│   ├── tuition_rates.json              #   Bảng giá học phí theo ngành/khóa
│   └── hoc_bong.json                   #   Dữ liệu quy chế học bổng
├── frontend/                           # 🎨 Chatbot SPA (HTML5/CSS3/Vanilla JS)
│   ├── assets/                         #   Static assets (icons, images)
│   ├── index.html                      #   Trang chính
│   ├── support.html                    #   Trang hỗ trợ
│   ├── script.js                       #   Logic frontend
│   └── style.css                       #   Styling
├── models/                             # 🧠 AI Models (Offline, local weights)
│   ├── vietnamese-bi-encoder/          #   Embedding model
│   └── bge-reranker-v2-m3/            #   Cross-Encoder reranker
├── scripts/                            # 🛠️ CLI Tools & Evaluation
│   ├── build_bm25_index.py             #   Build BM25 lexical index
│   ├── reindex_all.py                  #   Blue-Green reindexing (Qdrant)
│   ├── ingest_academic_programs.py     #   Nạp chunk CTĐT vào Qdrant
│   ├── batch_process.py                #   Batch OCR tài liệu PDF
│   ├── evaluate_chat_dataset.py        #   Đánh giá chất lượng chatbot
│   ├── run_ablation_test.py            #   Ablation testing RAG components
│   ├── reranker_tiebreak_ab_test.py    #   A/B test thuật toán tie-breaking
│   └── run_tool_calling_experiment.py  #   Thí nghiệm tool calling accuracy
├── tests/                              # ✅ Test Suite
│   ├── test_query_intent.py            #   Intent classification tests
│   ├── test_document_metadata.py       #   Document metadata tests
│   ├── test_document_upload.py         #   Upload flow tests
│   ├── test_finance_tools.py           #   Financial tool tests
│   ├── test_tuition_catalog.py         #   Tuition catalog tests
│   └── ...
├── docker-compose.yml                  #   4 services: Qdrant, Postgres, Redis, Neo4j
├── requirements.txt                    #   Python dependencies
├── start_env.sh                        #   Quick start script
└── README.md
```

---

## 🛠️ Bộ Lệnh CLI

| Lệnh                                                                                                                               | Mô Tả                                                   |
| :---------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------- |
| `python scripts/build_bm25_index.py`                                                                                              | Quét 244 văn bản Markdown và tái tạo chỉ mục BM25 |
| `python scripts/reindex_all.py build --index-version 2026-09-02-v1`                                                               | Nạp toàn bộ dữ liệu vào Qdrant collection mới      |
| `python scripts/reindex_all.py validate --index-version 2026-09-02-v1`                                                           | Kiểm tra collection Qdrant trước khi activate      |
| `python scripts/reindex_all.py activate --index-version 2026-09-02-v1 --alias ctu_scholarship_docs_current`                     | Kích hoạt alias Qdrant cho ứng dụng (zero-downtime) |
| `python Graph_DB/app/ingest.py`                                                                                                  | Nạp chương trình đào tạo vào Neo4j Graph          |
| `python scripts/batch_process.py`                                                                                                 | Batch OCR hàng loạt PDF                                 |
| `python scripts/evaluate_chat_dataset.py`                                                                                         | Đánh giá chất lượng chatbot trên dataset           |
| `python scripts/run_ablation_test.py`                                                                                             | Ablation test cho từng component RAG                     |
| `docker compose logs -f`                                                                                                          | Xem log trực tiếp các container                        |

---

## 🧪 Chạy Tests

```bash
# Chạy toàn bộ test suite
python -m pytest tests/ -v

# Chạy test cho module cụ thể
python -m pytest tests/test_query_intent.py -v
python -m pytest tests/test_finance_tools.py -v
```

---

## ⚙️ Tech Stack

| Layer                     | Công nghệ                                                             |
| :------------------------ | :---------------------------------------------------------------------- |
| **LLM**             | Google Gemini 3.5 Flash Lite (chính), Gemini 3.1 Flash Lite (rewriter) |
| **Orchestration**   | LangGraph (Supervisor Pattern), LangChain                               |
| **Knowledge Graph** | Neo4j 5.20 + APOC                                                       |
| **Vector DB**       | Qdrant v1.18.1                                                          |
| **Embedding**       | `bkai-foundation-models/vietnamese-bi-encoder`                        |
| **Reranker**        | `BAAI/bge-reranker-v2-m3` (Cross-Encoder)                             |
| **Lexical Search**  | BM25s + PyVi (Vietnamese Tokenizer)                                     |
| **Backend**         | FastAPI + Uvicorn                                                       |
| **Database**        | PostgreSQL 15 (SQLAlchemy Async)                                        |
| **Cache**           | Redis 7                                                                 |
| **OCR**             | LlamaParse (LlamaCloud)                                                 |
| **Frontend**        | HTML5, CSS3, Vanilla JavaScript (SPA)                                   |
| **Auth**            | JWT Token                                                               |

---

## 🤝 Đóng Góp & Phát Triển

Dự án được xây dựng phục vụ nghiên cứu và hỗ trợ sinh viên Trường Đại học Cần Thơ. Mọi đóng góp (Pull Request, Báo lỗi Issue) đều được chào đón!

1. Fork repository
2. Tạo branch: `git checkout -b feature/tinh-nang-moi`
3. Commit: `git commit -m "feat: thêm tính năng mới"`
4. Push: `git push origin feature/tinh-nang-moi`
5. Mở Pull Request

---

<div align="center">
