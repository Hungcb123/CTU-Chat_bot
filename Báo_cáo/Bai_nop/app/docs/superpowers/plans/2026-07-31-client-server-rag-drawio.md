# Client–Server RAG Draw.io Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tạo sơ đồ Draw.io hai trang mô tả chính xác kiến trúc client–server và luồng RAG của CTU Student Finance Chatbot.

**Architecture:** Dùng XML Draw.io đa trang với các swimlane theo tầng và đường nối trực giao. Trang tổng quan thể hiện ranh giới client/server/external/data; trang luồng `/chat` thể hiện hai nhánh structured tuition lookup và metadata-filtered vector RAG trước khi Gemini sinh câu trả lời.

**Tech Stack:** Draw.io XML, draw.io desktop CLI 30.2.6, validation script của `AIDraw/drawio-skill`.

## Global Constraints

- Chỉ tạo tài liệu và artifact sơ đồ; không sửa code chạy.
- File có đúng hai trang.
- Nhãn tiếng Việt, tên công nghệ giữ nguyên.
- Không đưa BM25 vào kiến trúc runtime.

---

### Task 1: Tạo source Draw.io hai trang

**Files:**
- Create: `docs/architecture/ctu_chatbot_client_server_rag.drawio`

**Interfaces:**
- Consumes: kiến trúc hiện tại trong `app/main.py`, `app/api/chat.py`, `app/api/document.py`, `app/services/rag_engine.py`, `app/services/tuition_catalog.py`, `frontend/script.js`, `docker-compose.yml`
- Produces: một `mxfile` gồm trang `01 - Kiến trúc Client-Server` và `02 - Luồng xử lý POST chat`

- [ ] **Step 1: Dựng trang tổng quan**

Thể hiện client sinh viên/quản trị, frontend, FastAPI API layer, application services, AI runtime, data stores và external AI APIs.

- [ ] **Step 2: Dựng trang luồng chat**

Thể hiện đầy đủ quyết định rewrite, routing, tuition lookup/RAG retrieval, reranking, Gemini/tool calling và persistence.

- [ ] **Step 3: Lưu XML chuẩn**

Mỗi trang có root cell `0`, `1`; mọi edge có `mxGeometry relative="1"`.

### Task 2: Kiểm tra cấu trúc và khả năng đọc

**Files:**
- Test: `docs/architecture/ctu_chatbot_client_server_rag.drawio`

**Interfaces:**
- Consumes: Draw.io source từ Task 1
- Produces: validation report không có lỗi cấu trúc

- [ ] **Step 1: Chạy structural validation**

Run:

```powershell
python AIDraw/drawio-skill/scripts/validate.py docs/architecture/ctu_chatbot_client_server_rag.drawio --score
```

Expected: không có dangling edge, duplicate ID hoặc broken parent.

- [ ] **Step 2: Sửa các lỗi validation nếu có**

Chỉnh trực tiếp ID, parent, source/target hoặc hình học tương ứng.

### Task 3: Xuất và rà ảnh xem trước

**Files:**
- Create: `docs/architecture/ctu_chatbot_client_server_rag_page1.png`
- Create: `docs/architecture/ctu_chatbot_client_server_rag_page2.png`

**Interfaces:**
- Consumes: Draw.io source đã validate
- Produces: hai PNG để xem nhanh trong báo cáo/review

- [ ] **Step 1: Xuất từng trang không nhúng XML**

Run:

```powershell
& 'C:\Program Files\draw.io\draw.io.exe' -x -f png --width 2000 --page-index 1 -o docs/architecture/ctu_chatbot_client_server_rag_page1.png docs/architecture/ctu_chatbot_client_server_rag.drawio
& 'C:\Program Files\draw.io\draw.io.exe' -x -f png --width 2000 --page-index 2 -o docs/architecture/ctu_chatbot_client_server_rag_page2.png docs/architecture/ctu_chatbot_client_server_rag.drawio
```

- [ ] **Step 2: Rà trực quan**

Kiểm tra nhãn bị cắt, node chồng nhau, đường nối đi xuyên node và hướng luồng không rõ.

- [ ] **Step 3: Chạy validation lần cuối**

Run lại `validate.py --score` sau mọi chỉnh sửa.
