# Biên Bản Họp & Checklist Chỉnh Sửa Bài Báo Khoa Học
**Đề tài:** Hệ thống Trợ lý ảo / Graph RAG Multi-Agent (Trường Đại học Cần Thơ)  
**Mục tiêu bài báo:** Rút gọn từ 22 trang xuống còn $12 - 16$ trang, hoàn thiện để nộp hội nghị (Phú Quốc / Cần Thơ).

---

## II. Checklist Chỉnh Sửa Chi Tiết Từng Phần (Action Items)

### 1. Abstract (Tóm Tắt)
- [ ] **Lược bớt chi tiết kỹ thuật:** Cắt bớt các số liệu thực nghiệm rải rác, không liệt kê quá vụn vặt.
- [ ] **Bổ sung kết luận cốt lõi (Main Takeaway):** Nêu rõ thông điệp kết luận cuối cùng của nghiên cứu (hệ thống mang lại giải pháp gì, giá trị ra sao so với phương pháp truyền thống).
- [ ] **Đảm bảo độ dài:** Viết ngắn gọn, cô đọng (thường dưới 250 từ).

### 2. Introduction (Mở Đầu)
- [ ] **Xử lý trùng lặp nội dung với Mục 3.1:**
  - Gom phần mô tả sơ bộ 4 thành phần kiến trúc kết hợp với đoạn 2 của Introduction.
  - Mục tiêu đoạn này: Làm nổi bật ngữ cảnh thực tế (Context) và động lực nghiên cứu (Motivation) cho bài toán chatbot tại ĐH Cần Thơ.
- [ ] **Phần Research Gaps (Đoạn 4):**
  - Trong Introduction chỉ liệt kê tên ngắn gọn các thách thức (ví dụ: *Challenge 1, Challenge 2, Challenge 3*).
  - Không phân tích chi tiết tại đây; đẩy toàn bộ phân tích sâu về **Mục 2.6 (Related Work)**.
- [ ] **Phần Đóng góp nghiên cứu (Contributions):**
  - Tránh lặp lại nguyên văn các câu hỏi nghiên cứu ($RQ1, RQ2, RQ3$).
  - Viết ngắn gọn, nhấn mạnh giải pháp đề xuất đã giải quyết các khoảng trống nghiên cứu như thế nào.
- [ ] **Bổ sung cấu trúc bài báo (Paper Outline):** Thêm đoạn chuyển ý ở cuối Introduction:  
  *"The remainder of this paper is organized as follows: Section 2 reviews related literature; Section 3 details the proposed architecture..."*
- [ ] **Rà soát văn phong:** Lọc bỏ các từ hoa mỹ, đao to búa lớn (dấu hiệu sinh bằng AI), đưa về văn phong học thuật chuẩn mực.
- [ ] **Kiểm soát dung lượng:** Cắt giảm toàn bài về khoảng $12 - 16$ trang (tránh trả phí phụ thu trang phụ trội).

### 3. Related Work (Nghiên Cứu Liên Quan)
- [ ] **Bổ sung cơ sở lý thuyết NLP Tiếng Việt:** Đưa thêm các trích dẫn và tài liệu tham khảo về xử lý ngôn ngữ tự nhiên cho tiếng Việt (mô hình ngôn ngữ, tokenizer, đặc thù tiếng Việt).
- [ ] **Phân tích so sánh với nghiên cứu của K48 (anh Chí Tâm - ĐH Cần Thơ):**
  - **Mục tiêu:** Chứng minh tính mới và sự khác biệt để phản biện không chất vấn.
  - **Điểm khác biệt cốt lõi:**
    - Nghiên cứu trước chỉ dùng bài toán phân lớp ý định (Intent Classification) / Text đơn thuần.
    - Nghiên cứu này dùng **Graph RAG kết hợp Multi-Agent** (LangGraph StateGraph), xử lý suy luận điều kiện phức tạp (học phí, quy chế đào tạo).
  - **Lập luận về độ đo:** Phân tích rõ vì bản chất bài toán khác nhau (phân lớp văn bản tính $F_1$-score vs. sinh câu trả lời RAG tính bằng Ragas), do đó **không thể so sánh số liệu thực nghiệm trực tiếp**.

### 4. Proposed Methodology / Architecture (Mục 3)
- [ ] **Rút gọn dung lượng:** Phần mô tả kiến trúc đang dài tới 8 trang; cần cô đọng lại, đặc biệt từ Mục 3.6 đến 3.9.
- [ ] **Chuẩn hóa sơ đồ kiến trúc:** Vẽ lại sơ đồ trên **Draw.io**, căn chỉnh đường nối thẳng thớm, rõ ràng, trực quan.
- [ ] **Chuẩn hóa bảng biểu (Table 1, Table 3...):**
  - Loại bỏ các từ ngữ lặp thừa trong từng ô để mở rộng không gian hiển thị (ví dụ: thay vì ghi `Total: 64 samples`, chỉ để số `64` và ghi chú ở tiêu đề cột; thay vì ghi `Max tokens: 1110`, chỉ ghi `1110`).
- [ ] **Làm rõ tính đặc thù của LangGraph StateGraph:**
  - Giải thích điểm sáng tạo so với StateGraph mặc định: các agent hoạt động độc lập, tự chủ, cơ chế định tuyến qua các cạnh điều kiện (conditional edges).
- [ ] **Làm rõ các giải thuật đề xuất (Algorithms 1, 2):**
  - Bổ sung công thức toán học tường minh cho thuật toán tính toán học phí (các hệ số, biến số, trọng số ràng buộc).
  - Mô tả rõ các ưu điểm và điểm đặc trưng của thuật toán.
- [ ] **Đặc tả cơ sở dữ liệu đồ thị Neo4j:**
  - Bổ sung chi tiết **Graph Schema**: Số lượng loại Node (Node types: Quy định học vụ, Học phí, Chương trình đào tạo), số lượng thuộc tính và các loại quan hệ (Relationships).
  - Mô tả hoạt động của **Cypher Tool**: Cách thức chuyển đổi từ yêu cầu người dùng sang truy vấn đồ thị Cypher (truy vấn thuộc tính, truy vấn cấu trúc hay tìm kiếm hybrid).

### 5. Experiments & Results (Thực Nghiệm)
- [ ] **Chuẩn hóa tên gọi Baseline:** Sửa các ký hiệu $E_1, E_2, E_3$ thành tên chuẩn để người đọc nhận biết ngay mô hình đối chứng (ví dụ: `Baseline: BM25`, `Baseline: Dense Retriever`).
- [ ] **Mô tả quy trình thực nghiệm:**
  - Làm rõ quy mô tập kiểm thử (100 - 150 câu truy vấn).
  - Nêu rõ phương pháp phân chia dữ liệu ($K$-fold cross-validation hay Train/Test split), số lần chạy lặp lại để lấy giá trị trung bình.
  - Trình bày bộ độ đo đánh giá từ framework **Ragas** (*Faithfulness, Answer Relevance, Context Precision, Context Recall*).
- [ ] **Phân tích mục Thảo luận (Discussion):**
  - Giải thích hiện tượng thực nghiệm khi **loại bỏ Graph (Without Graph)**: Tại sao một số câu hỏi đơn giản không cần đồ thị lại đạt điểm số cao hơn? (Giải thích: Do đồ thị có thể gây thừa context/nhiễu context đối với các truy vấn thực thể đơn lẻ; đồ thị chỉ thể hiện sức mạnh vượt trội ở các truy vấn quan hệ đa bước).

### 6. Conclusion & Future Work
- [ ] **Tách biệt Conclusion và Abstract:** Viết lại Conclusion tập trung vào kết quả đạt được từ thực nghiệm và đóng góp thực tiễn, không lặp lại nguyên văn tóm tắt.
- [ ] **Mở rộng Future Work:** Không để cụt (hiện tại chỉ có 1–2 dòng). Đề xuất hướng phát triển cụ thể: mở rộng Ontology cho các khoa viện khác, thử nghiệm các mô hình LLM mã nguồn mở chuyên sâu tiếng Việt, cải tiến cơ chế tự động sửa truy vấn Cypher.

---

## III. Kế Hoạch Đăng Bài & Hành Chính Hội Nghị

* **Lựa chọn địa điểm hội nghị:**
  * **Hội nghị Phú Quốc:** Diễn ra vào Thứ 6, Thứ 7, Chủ nhật (Tuần 12). Cần kiểm tra lịch thi học kỳ để tránh trùng lịch. Nếu lịch thi không vướng cuối tuần thì ưu tiên nộp bài sớm.
  * **Hội nghị Cần Thơ:** Phương án dự phòng an toàn về mặt di chuyển.
* **Chi phí đăng bài (Publication Fee):**
  * Cô hướng dẫn sẽ hỗ trợ đóng lệ phí bài báo cho nhóm; chi phí di chuyển/ăn ở sinh viên tự túc.
  * Đăng ký kết hợp 2 bài báo qua Thầy Quý để được giảm giá (ước tính $\approx 800\text{ GBP}$ cho cả 2 bài, thay vì đóng lẻ hơn $500\text{ GBP}$/bài).