
# Kế hoạch Xây dựng Tests RAGAS Table 5

**Ngày lập**: 2026-08-31
**Trạng thái**: Chờ xem xét & phê duyệt

---

## TÓM TẮT THỰC HIỆN

Xây dựng framework test toàn diện để chạy Table 5 (chỉ số chất lượng câu trả lời) trên 4 cấu hình truy xuất: **dense, sparse, hybrid_rrf, hybrid_rrf_rerank**.

Refactor `evaluate_ragas.py` để cô lập chế độ truy xuất, thêm các hàm test nhận biết cấu hình, và tạo báo cáo RAGAS cho mỗi cấu hình với 4 chỉ số: Answer Relevance, Context Recall, Context Precision, Answer Correctness.

---

## CÁC BƯỚC THỰC HIỆN

### **Giai đoạn 1: Refactor Logic Đánh giá Cơ bản** *(có thể chạy song song 1.1-1.2)*

**Bước 1.1**: Tách logic chế độ truy xuất từ `AdvancedChunkingEngine.retrieve()`

- Tạo hàm helper: `get_retrieval_config(mode)`
- Xác thực `mode ∈ {dense_only, sparse_only, hybrid_rrf, hybrid_rrf_rerank}`
- Trả về wrapper có thể log chế độ + điểm số riêng biệt
- **File**: `app/services/rag_engine.py`

**Bước 1.2**: Tạo class `RetrievalConfigRunner`

- Chấp nhận: `(config_name, engine, dataset_cases)`
- Trả về: tuple `(questions, answers, contexts, ground_truth)` cho RAGAS
- Xử lý caching để tránh chạy lại cấu hình giống nhau
- **File**: `scripts/test_table5_ragas.py` (file mới)

---

### **Giai đoạn 2: Xây dựng Hàm Test Table 5** *(song song với Giai đoạn 1)*

**Bước 2.1**: Triển khai `test_table5_ragas_answer_quality()`

- Vòng lặp 4 cấu hình: `['dense_only', 'sparse_only', 'hybrid_rrf', 'hybrid_rrf_rerank']`
- Cho mỗi cấu hình:
  - Chạy `RetrievalConfigRunner` để lấy Q/A/C/GT
  - Gọi RAGAS evaluator (tái sử dụng LLM có rate limit hiện có)
  - Thu thập 4 chỉ số: answer_relevancy, context_recall, context_precision, answer_correctness
  - Theo dõi số mẫu theo domain (học bổng, miễn học phí, vay, học phí từ `data/dataset.md`)
  - Lưu: JSON results + bảng markdown
- **File output**: `logs/table5_ragas_results_{timestamp}.json` + `.md`

**Bước 2.2**: Tích hợp với RAGAS Evaluator

- Tái sử dụng class `RateLimitedChatGoogleGenerativeAI` từ `evaluate_ragas.py`
- Áp dụng rate limit 15 requests/phút (4.1 giây delay giữa các lệnh gọi)
- Xử lý lỗi: nếu RAGAS scorer thất bại, log error + đánh dấu `NaN`, không dừng

---

### **Giai đoạn 3: Cô lập Cấu hình** *(phụ thuộc vào 1.1)*

**Bước 3.1**: Sửa đổi `AdvancedChunkingEngine.retrieve()`

- Thêm tham số tùy chọn: `force_mode`
- Nếu `force_mode='sparse_only'`: bỏ qua truy xuất dense, chỉ trả BM25
- Nếu `force_mode='dense_only'`: bỏ qua BM25, chỉ trả dense
- Mặc định: tự động phát hiện từ trạng thái engine
- Log chế độ nào đang hoạt động để kiểm toán

**Bước 3.2**: Xác thực Reranker

- Kiểm tra temporal tie-break reranker được kích hoạt ở chế độ `hybrid_rrf_rerank`
- Log tied bucket distribution để audit trail
- **File**: `app/services/rag_engine.py`

---

### **Giai đoạn 4: Xác thực & Báo cáo** *(phụ thuộc vào 2-3)*

**Bước 4.1**: Tạo `validate_table5_results(results_json)`

- Kiểm tra tất cả 4 cấu hình có mặt
- Kiểm tra các chỉ số ∈ [0, 1]
- Kiểm tra số mẫu cho mỗi cấu hình > 0
- Xác minh reranker tie-break có mặt ở chế độ `hybrid_rrf_rerank`

**Bước 4.2**: Tạo báo cáo Markdown

- Bảng khớp định dạng bài báo:
  - Hàng: 4 cấu hình (Dense-only, Sparse-only, Hybrid RRF, Hybrid RRF+Rerank)
  - Cột: Answer Relevance | Context Recall | Context Precision | Answer Correctness
- Footer: số mẫu theo domain (Học bổng, Miễn học phí, Vay, Học phí)
- Báo cáo riêng cho mỗi domain + tổng hợp

**Bước 4.3**: Phân tích Độ lệch (nếu cần)

- So sánh với kết quả trước đó nếu có lịch sử
- Ghi chú bất kỳ giới hạn hay ràng buộc

---

## CÁC FILE LIÊN QUAN


| File                                                                     | Hành động                                                                      | Ghi chú                                                            |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| [scripts/evaluate_ragas.py](scripts/evaluate_ragas.py)                   | **Refactor**: Tách class `RetrievalConfigRunner` + khởi tạo LLM có rate limit | Lái chính của đánh giá RAGAS                                  |
| [app/services/rag_engine.py](app/services/rag_engine.py)                 | **Cập nhật**: Thêm tham số `force_mode` vào `retrieve()`                     | Cô lập logic chế độ truy xuất                                 |
| [data/dataset.md](data/dataset.md)                                       | **Đọc**: Nguồn chân lý cho nhãn domain                                      | Chứa 4 domain × 25 câu hỏi                                      |
| **[scripts/test_table5_ragas.py](scripts/test_table5_ragas.py)**         | **TẠO MỚI**: Hàm test chính + orchestration                                   | Chứa`test_table5_ragas_answer_quality()` + `RetrievalConfigRunner` |
| **[logs/table5_results_{timestamp}/](logs/table5_results_{timestamp}/)** | **TẠO MỚI**: Lưu trữ kết quả (JSON + MD)                                    | Tự động tạo khi chạy test                                      |

---

## CÁC BƯỚC XÁC THỰC

### **Xác thực Chức năng**

- ✓ `test_table5_ragas_answer_quality()` chạy toàn bộ 4 cấu hình mà không timeout (rate limit ở 15 RPM)
- ✓ Mỗi cấu hình tạo JSON với tất cả 4 chỉ số có mặt, giá trị ∈ [0,1]
- ✓ Báo cáo Markdown render đúng, khớp cấu trúc cột

### **Xác thực Dữ liệu**

- ✓ Số mẫu trên cấu hình = 100 (hoặc subset nếu dùng `--limit`)
- ✓ Phân tích theo domain khớp nhãn `dataset.md` (25 học phí, 25 miễn học phí, 25 vay, 25 học bổng)
- ✓ Ground truth từ field `expected_answer` có mặt cho tất cả 100 trường hợp

### **Kiểm tra Hồi quy**

- ✓ Chạy 100 câu hỏi giống nhau với `hybrid_rrf_rerank` (chế độ production hiện tại)
- ✓ Xác minh chỉ số không thấp hơn lần chạy trước (so với lịch sử `logs/`)
- ✓ Đảm bảo logic reranker + tie-break kích hoạt đúng

### **Audit Trail**

- ✓ Log chế độ truy xuất của mỗi cấu hình + điểm số (chế độ verbose)
- ✓ Ghi mô hình LLM judge + temperature trong JSON kết quả

---

## CÁC QUYẾT ĐỊNH


| Quyết định              | Lý do                                                                     | Lựa chọn                                                             |
| ---------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Rate Limiting**          | Tôn trọng giới hạn free tier API Gemini (15 RPM)                       | Tái sử dụng`RateLimitedChatGoogleGenerativeAI` hiện có            |
| **Phạm vi Test**          | Test 100 câu hỏi để khớp bài báo; cho phép`--limit N` cho CI nhanh | Tất cả 100, có flag tùy chọn                                      |
| **Chỉ số RAGAS**         | RAGAS v0.x định nghĩa khác nhau (answer_relevancy ≠ faithfulness)     | Chấp nhận định nghĩa RAGAS; ghi chú rõ ràng                    |
| **Chiến lược Fallback** | Nếu RAGAS scorer thất bại, không hủy toàn bộ                        | Log error + đánh dấu`NaN`, tiếp tục                               |
| **Thứ tự Cấu hình**    | Phát hiện sớm lỗi cơ sở                                              | Thứ tự: dense_only → sparse_only → hybrid_rrf → hybrid_rrf_rerank |

---

## CÁC VẤN ĐỀ CẦN XEM XÉT

### **1. Rủi ro Thời gian Thực hiện** (ĐỌC TRƯỚC)

- **Vấn đề**: Mỗi cấu hình × RAGAS scorer (5 lệnh gọi LLM per Q) = ~500 lệnh gọi LLM tổng (≈2.5 giờ ở 15 RPM)
- **Lựa chọn A** (Hiện tại): Dùng Google Gemini scorer qua API, chờ đợi
- **Lựa chọn B** (Tối ưu): Thêm local embedding scorer (Sentence-Transformers) để bổ sung Gemini cho lặp lại nhanh
- **Khuyến nghị**: Bắt đầu với A, chuyển B nếu lặp lại quá chậm

### **2. Xác thực Reranker**

- **Vấn đề**: Làm sao xác minh temporal tie-break reranker đang hoạt động ở chế độ `hybrid_rrf_rerank` mà không kiểm tra điểm số trực tiếp?
- **Khuyến nghị**: Thêm `log_rerank_stats()` để báo cáo phân phối tied-bucket

### **3. Baseline So sánh**

- **Vấn đề**: Bài báo đánh dấu Table 5 là "pending". Có nên thêm logic phát hiện nếu chỉ số cải thiện/suy giảm so với lần chạy RAGAS trước được lưu lịch sử Git?
- **Khuyến nghị**: Đợi kết quả lần đầu, sau đó thêm baseline comparison

---

## LƯỚI PHỐI HỢP PHỤ THUỘC
