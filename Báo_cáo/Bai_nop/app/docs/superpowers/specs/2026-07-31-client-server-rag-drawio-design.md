# Client–Server RAG Architecture Draw.io Design

## Mục tiêu

Tạo một file Draw.io có thể chỉnh sửa để trình bày kiến trúc hiện tại của CTU Student Finance Chatbot theo mô hình client–server, bám sát code đang chạy và làm rõ luồng RAG.

## Phạm vi

File `docs/architecture/ctu_chatbot_client_server_rag.drawio` gồm hai trang:

1. **Kiến trúc Client–Server**: trình duyệt sinh viên/quản trị, frontend tĩnh, FastAPI/Uvicorn, các API, dịch vụ nghiệp vụ/AI, kho dữ liệu và dịch vụ AI bên ngoài.
2. **Luồng xử lý POST /chat**: xác thực, lấy lịch sử, rewrite có kiểm soát, intent routing, structured tuition lookup hoặc metadata RAG lanes, Qdrant child search, PostgreSQL parent recovery, BGE reranking, Gemini/tool calling, lưu lịch sử và trả kết quả.

## Quy ước trình bày

- Bố cục trái sang phải, có container theo tầng.
- Xanh dương: client/frontend; cam: API/server; tím: điều phối/RAG/AI cục bộ; xanh lá: lưu trữ; xám nét đứt: API bên ngoài.
- Mũi tên có nhãn giao thức hoặc dữ liệu chính.
- Ghi đúng công nghệ hiện tại: FastAPI/Uvicorn, Redis, PostgreSQL, Qdrant, Vietnamese Bi-Encoder, BGE Reranker v2-m3, Gemini, LlamaParse.
- Phân biệt rõ structured tuition lookup với vector RAG.
- Không mô tả BM25 vì phiên bản hiện tại chưa sử dụng BM25 trong retrieval runtime.

## Tiêu chí hoàn thành

- File XML mở được bằng draw.io desktop.
- Có đúng hai trang và không có cạnh treo, ID trùng hoặc parent hỏng.
- Hai ảnh PNG xem trước đọc được, không cắt nhãn hoặc chồng các thành phần chính.
- Không sửa code ứng dụng.
