# Báo cáo hoàn thành: Phân tích và xây dựng sơ đồ kiến trúc RAG

Dưới đây là tóm tắt các công việc đã thực hiện để hoàn thành yêu cầu làm rõ luồng kiến trúc cho dự án Chatbot.

## Các công việc đã thực hiện
1. **Phân tích mã nguồn toàn diện:** 
   * Đã quét toàn bộ thư mục `app/` và `scripts/`.
   * Tập trung phân tích chuyên sâu các file cốt lõi: `app/services/rag_engine.py`, `app/api/chat.py`, và `scripts/batch_process.py`.
   * Bóc tách thành công 2 luồng độc lập: Luồng xử lý nạp dữ liệu (Ingestion) và Luồng giao tiếp hỏi đáp (RAG).

2. **Áp dụng skill `mermaid_diagrammer`:** 
   * Đã áp dụng các quy tắc nghiêm ngặt của `mermaid_diagrammer` để khởi tạo hai sơ đồ logic đảm bảo không bị lỗi cú pháp hiển thị.

3. **Lập bản vẽ kiến trúc chi tiết (Mermaid Diagram):**
   * **Sơ đồ 1 (Luồng Ingestion & Chunking):** Mô phỏng chi tiết luồng xử lý từ file PDF đầu vào -> LlamaParse -> Cắt thành khối lớn (Parent) giữ nguyên bảng biểu -> Băm thành khối nhỏ (Child) 400 ký tự -> Lưu vào PostgreSQL (Parent) và Qdrant (Child).
   * **Sơ đồ 2 (Luồng RAG):** Giải trình rõ ràng ranh giới của 3 khái niệm:
     * *Retrieval:* Lấy lịch sử từ Redis -> Viết lại câu hỏi (Rewriter) -> Tìm vector ở Qdrant -> Lấy Parent ở PostgreSQL -> Chấm điểm lại (Re-ranker).
     * *Augmented:* Ghép Câu hỏi + Lịch sử + Top 3 Parents thành một khối Prompt thống nhất.
     * *Generation:* Gemini đọc Prompt và sinh ra câu trả lời (kết hợp với việc gọi tool tính tiền học bổng).

## Kết quả kiểm tra (Validation Results)
- Sơ đồ hoàn toàn tuân thủ theo các logic code được viết trong `rag_engine.py` và `chat.py`. Không có sự thêm thắt hay ảo giác (hallucination).
- Cú pháp Mermaid được kiểm duyệt, sẵn sàng để dán vào các công cụ như Notion, GitHub hoặc Live Mermaid Editor để hiển thị.

Toàn bộ quy trình và kết quả đã được ghi nhận trong file kế hoạch triển khai. Bạn có thể sao chép đoạn code Mermaid từ bản kế hoạch để dán vào tài liệu báo cáo của mình.
