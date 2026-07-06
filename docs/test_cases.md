# Bộ Test Case Đánh Giá Khả Năng Gọi Tool của Chatbot Học Bổng

File này chứa các kịch bản kiểm thử (Test Cases) nhằm đánh giá khả năng phân biệt và quyết định của Chatbot: khi nào **BẮT BUỘC phải gọi Tool** (`tinh_tien_hoc_bong`) và khi nào **KHÔNG ĐƯỢC gọi Tool** (chỉ dùng RAG để trả lời dựa trên tài liệu).

---

## Phần 1: Các trường hợp BẮT BUỘC sử dụng Tool (Tool Calling)
*Mục đích: Kiểm tra xem Chatbot có nhận diện được các con số (GPA, ĐRL) để gọi hàm `tinh_tien_hoc_bong` và trả về số tiền chính xác hay không.*

1. **Test Case 1 (Cơ bản, đủ tham số):**
   - **Prompt:** "Điểm GPA của mình là 3.6 và điểm rèn luyện là 90, mình học ngành CNTT thì được bao nhiêu tiền học bổng?"
   - **Kỳ vọng:** Chatbot GỌI TOOL `tinh_tien_hoc_bong(gpa=3.6, drl=90, khoi_nganh="CNTT")`. Output in ra số tiền cụ thể của khối ngành CNTT.

2. **Test Case 2 (Thiếu khối ngành):**
   - **Prompt:** "Kỳ vừa rồi mình đạt 4.0 GPA và điểm rèn luyện là 85. Mình có được học bổng không?"
   - **Kỳ vọng:** Chatbot GỌI TOOL `tinh_tien_hoc_bong(gpa=4.0, drl=85, khoi_nganh="")`. Output in ra chúc mừng đạt loại Khá/Giỏi/Xuất sắc và liệt kê danh sách tiền của *toàn bộ* các khối ngành.

3. **Test Case 3 (Không đủ điều kiện):**
   - **Prompt:** "Mình được GPA 2.0 và ĐRL 60. Tính giúp mình tiền học bổng nhé."
   - **Kỳ vọng:** Chatbot GỌI TOOL `tinh_tien_hoc_bong(gpa=2.0, drl=60, khoi_nganh="")`. Output trả về câu thông báo rất tiếc chưa đủ điều kiện.

4. **Test Case 4 (Hỏi lắt léo):**
   - **Prompt:** "Cho mình biết mức học bổng của một sinh viên sư phạm toán có gpa 3.8, đrl 95."
   - **Kỳ vọng:** Chatbot GỌI TOOL với `khoi_nganh` chứa từ khóa "sư phạm" hoặc tương tự.

---

## Phần 2: Các trường hợp KHÔNG ĐƯỢC sử dụng Tool (RAG / Normal QA)
*Mục đích: Kiểm tra xem Chatbot có bị "ảo giác" tự gọi Tool khi không có số liệu cụ thể hay không. Ở các câu này, bot phải đọc tài liệu PDF/Markdown từ Qdrant (RAG) để trả lời.*

1. **Test Case 5 (Hỏi điều kiện chung):**
   - **Prompt:** "Điều kiện để nhận học bổng khuyến khích học tập là gì?"
   - **Kỳ vọng:** KHÔNG gọi Tool. Bot liệt kê các điều kiện chung (phải trong thời gian thiết kế chuẩn, không bị kỷ luật, v.v.) dựa trên tài liệu Quyết định 3530.

2. **Test Case 6 (Hỏi về quy trình/hồ sơ):**
   - **Prompt:** "Sinh viên năm nhất có cần nộp hồ sơ xin học bổng không hay trường tự xét?"
   - **Kỳ vọng:** KHÔNG gọi Tool. Bot trả lời về quy trình xét duyệt của trường.

3. **Test Case 7 (Cố tình gài bẫy dùng từ khóa 'tính tiền' nhưng không cho số):**
   - **Prompt:** "Bạn tính tiền học bổng giúp mình với, mình học loại giỏi."
   - **Kỳ vọng:** KHÔNG gọi Tool (vì thiếu số liệu cụ thể). Bot phải lịch sự phản hồi: "Vui lòng cung cấp cho tôi điểm GPA và Điểm rèn luyện của bạn để tôi có thể tính toán chính xác."

4. **Test Case 8 (Hỏi đối tượng bị loại trừ):**
   - **Prompt:** "Mình bị rớt 1 môn thì có bị mất quyền xét học bổng không?"
   - **Kỳ vọng:** KHÔNG gọi Tool. Bot truy xuất tài liệu và trả lời quy định về việc nợ môn / rớt môn.

---

## Phần 3: Các trường hợp Edge Cases (Giao tiếp nhiều lượt / Hội thoại)
*Mục đích: Kiểm tra khả năng lưu trữ ngữ cảnh bằng Redis Memory.*

1. **Test Case 9 (Chia nhỏ thông tin - Lượt 1):**
   - **Prompt:** "Kỳ này mình được GPA 3.7"
   - **Kỳ vọng:** Bot KHÔNG gọi tool tính toán, mà hỏi lại: "Chúc mừng bạn! Bạn có thể cho biết thêm điểm rèn luyện của bạn là bao nhiêu để mình tính học bổng không?"

2. **Test Case 10 (Chia nhỏ thông tin - Lượt 2):**
   - **Prompt:** "Điểm rèn luyện của mình là 82 nhé."
   - **Kỳ vọng:** Do có Redis nhớ ngữ cảnh trước đó (GPA=3.7), bot nhận ra đã đủ 2 biến -> GỌI TOOL `tinh_tien_hoc_bong(gpa=3.7, drl=82)`.

3. **Test Case 11 (Chuyển đổi chủ đề):**
   - **Prompt:** "Vậy học bổng ngoài ngân sách thì sao?"
   - **Kỳ vọng:** KHÔNG gọi Tool. Trả lời bằng RAG về quy định học bổng ngoài ngân sách (tài trợ doanh nghiệp, v.v.).
