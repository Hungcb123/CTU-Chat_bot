
****Làm rõ chế độ chính sách: Học bổng khuyến khích, miễn giảm học phí, trợ cấp xã hội, vay vốn.**

PDF -> OCR -> Chunking -> Embedding -> Lưu trữ -> Retrieval -> Generation

Cấu hình: GTX1650 4Gb Vram

### 1.OCR:

-Dữ liệu là file pdf và scanned pdf

* **Công cụ:** Sử dụng `Unstructured` (chọn cấu hình `strategy="hi_res"` và `ocr_agent="paddleocr"`).
* **Thực thi:** Quét toàn bộ thư mục PDF. Không cần viết code phân loại định tuyến lằng nhằng nữa. Đè tất cả ra cho con GPU 4GB của em chạy PaddleOCR lấy chữ và cấu trúc bảng (Table HTML).
* **Chốt chặn chất lượng (Bắt buộc):** Sau khi tool chạy xong xuất ra file text/HTML, em PHẢI mở lên xem lại bằng mắt thường (Manual Review). Các đoạn văn bản dài có thể sai vài dấu phẩy không sao, nhưng  **con số tiền tệ và điều kiện điểm số phải chuẩn 100%** .

#### Bước 1: Phân tích bố cục vùng (Layout Detection)

Khi gọi partition_pdf(..., strategy="hi_res"), Unstructured sẽ không đọc chữ ngay. Nó sẽ nạp một mô hình phát hiện vật thể (Object Detection như YOLOX) lên CPU/GPU để quét qua trang PDF. Mô hình này sẽ khoanh vùng và phân loại trang giấy thành các khối (Elements) riêng biệt: Title (Tiêu đề), NarrativeText (Đoạn văn hành chính), và Table (Bảng biểu).

#### Bước 2: Kích hoạt OCR Agent (PaddleOCR) theo vùng

* Đối với các vùng là chữ (Title, NarrativeText), nếu file là PDF scan, Unstructured sẽ gọi PaddleOCR xuống để quét và trả về text thô.
* Nếu vùng đó là PDF chuẩn (Native), hệ thống tự động trích xuất text trực tiếp mà không cần chạy qua OCR để tiết kiệm tài nguyên.

#### Bước 3: Xử lý Bảng cấu trúc cao (Table Parsing)

Đây là chỗ ăn tiền nhất từ đính chính của em. Khi phát hiện vùng Table và có cấu hình infer_table_structure=True, Unstructured sẽ kích hoạt một mô hình phụ (thường là Table Transformer) để phân tích các đường kẻ hàng/cột của bảng.

* Nó sẽ map toàn bộ dữ liệu ô chữ thành một chuỗi HTML hoàn chỉnh (gồm đầy đủ các thẻ `<table>`, `<tr>`, `<td>`).
* Chuỗi HTML này sẽ được giấu bên trong trường element.metadata.text_as_html.

Framework quản lý Pipeline: Unstructured (Bản Local Open-source).

Chiến lược Phân mảnh: strategy="hi_res" (Bắt buộc dùng cho các trang có chứa bảng biểu hoặc định dạng phức tạp).

OCR Agent: PaddleOCR (Cấu hình đè lên Tesseract mặc định của Unstructured để lấy độ chính xác Tiếng Việt cao nhất).

Tham số cấu hình Bảng: infer_table_structure=True


### 2.Chunking

-LlamaIndex hoặc LangChain(RecursiveCharacterTextSplitter)

-Đề xuất size chunk chứa khoảng  500-00 token, overlap khoảng 10-15%


### 3.Embedding (Nhúng ngữ nghĩa,  chuyển chunk text tiếng việt thành vector)

-Mô hình Sentence BERT 1 vector 876 chiều keepitreal/vietnamese-sbert


### 4.Vector DB( bắt buộc kèm meta data cho mỗi chunk)

* **Ngả 1 - Lưu vào Vector Database (ChromaDB):** Dành cho dữ liệu dạng  **Văn bản diễn giải (Semantic Text)** .
  * *Bao gồm:* Các quy trình (Xin giấy xác nhận ở đâu, cần nộp hồ sơ gì, quy định chung chung).
  * *Cách lưu:* Băm nhỏ (Chunking) các đoạn text này, đính kèm Metadata phân loại (Ví dụ: `{"doi_tuong": "K48", "chinh_sach": "vay_von"}`). LLM sẽ dùng ChromaDB để trả lời các câu hỏi về thủ tục.
* **Ngả 2 - Lưu vào File JSON tĩnh (Rule-based JSON):** Dành cho dữ liệu dạng  **Quy định cứng & Số liệu (Deterministic Data)** .
  * *Bao gồm:* Các bảng mức học bổng (Khối V là 7.860.000đ, Khối VI là 8.448.000đ), điều kiện TBC tối thiểu.
  * *Cách lưu:* Em tự tay cấu trúc lại cái bảng học bổng trong file Quyết định thành một file JSON chuẩn mực. Ví dụ: file `hoc_bong_K48.json` chứa đích danh các con số.

### 5.Retrieval (Loại bỏ giới hạn context window và triệt tiêu hallucination)

-Purpose: với 4Gb Vram thì cần giới hạn ngữ ảnh để đưa vào LLM, song song đóa có những tài liệu rõ ràng phù hợp với ngữ cảnh câu hỏi thì sẽ tránh được tình trạng hallucination

-Dùng SBERT để biến câu hỏi thành vector

-Dùng Retriever có sẵn của LlamaIndex hoặc langchain, bật cấu hình MMR - Maximal Marginal Relevance  của langChain để tối ưu hóa độ  phong phú của câu trả lời do dữ liệu đầu vào khác biệt lẫn nhau

6.LLM model (Generation)

-qwen2.5:3b







### **System prompt**

Bạn là "Trợ lý Ảo ĐHCT", chuyên viên tư vấn chế độ chính sách sinh viên của Đại học Cần Thơ.

Nhiệm vụ DUY NHẤT của bạn là trả lời câu hỏi dựa trên phần [TÀI LIỆU THAM KHẢO] được cung cấp.

QUY TẮC TỐI THƯỢNG (TUYỆT ĐỐI TUÂN THỦ):

1. RÀNG BUỘC NGỮ CẢNH: CHỈ sử dụng thông tin có trong [TÀI LIỆU THAM KHẢO]. Nếu tài liệu không chứa câu trả lời, NGHIÊM CẤM bịa đặt (hallucinate) hoặc sử dụng kiến thức có sẵn của bạn.
2. XỬ LÝ NGOÀI VÙNG (OUT-OF-SCOPE): Nếu câu hỏi không liên quan đến chính sách ĐHCT (ví dụ: thời tiết, lập trình, viết code, tán gẫu, chính trị), bạn PHẢI TỪ CHỐI bằng câu: "Tôi là Trợ lý Ảo của ĐHCT. Tôi chỉ hỗ trợ giải đáp các quy định về học bổng, học phí và chính sách sinh viên."
3. XỬ LÝ THIẾU THÔNG TIN: Nếu câu hỏi thuộc phạm vi ĐHCT nhưng [TÀI LIỆU THAM KHẢO] không có đáp án, hãy trả lời: "Quy định hiện tại chưa đề cập chi tiết đến vấn đề này. Bạn vui lòng liên hệ trực tiếp Phòng Công tác Sinh viên để được giải quyết."
4. VĂN PHONG: Chuyên nghiệp, ngắn gọn, xưng hô "Tôi" và "Bạn" (hoặc "Sinh viên"). Không dài dòng chào hỏi thừa thãi.

[TÀI LIỆU THAM KHẢO]

{context}

Câu hỏi của sinh viên: {question}

Trả lời:

**
