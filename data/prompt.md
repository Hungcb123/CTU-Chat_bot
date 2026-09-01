# KIỂM TRA DOMAIN CỦA DOCUMENT METADATA

Bạn có một tập tài liệu nguồn đã được tải lên NotebookLM và một file `document_metadata.json`.

Nhiệm vụ duy nhất:

**Kiểm tra xem giá trị `domain` hiện tại của từng document trong `document_metadata.json` có phù hợp với NỘI DUNG THỰC TẾ của document đó hay không.**

Không phân loại câu hỏi người dùng.
Không phân loại `intent`.
Không suy luận `next_agent`.

═══════════════════════════════════════════

## 1. DOMAIN ĐƯỢC PHÉP

═══════════════════════════════════════════

`domain` CHỈ được phép thuộc đúng một trong 13 giá trị sau:

* `actual_tuition`
* `exemption_basis`
* `exemption_policy`
* `calculation`
* `both`
* `ambiguous_tuition`
* `scholarship`
* `student_loan`
* `social_support`
* `academic_rules`
* `quy_che_general`
* `other`
* `academic_program`

KHÔNG được tạo thêm domain mới.

Ví dụ các domain sau KHÔNG hợp lệ:

* `tuition`
* `academic_regulation`
* `financial`
* `academic`
* `general`

Nếu metadata hiện tại chứa các giá trị này thì phải xác định domain đúng trong 13 giá trị được phép ở trên.

═══════════════════════════════════════════

## 2. Ý NGHĨA CỦA DOMAIN

═══════════════════════════════════════════

### HỌC PHÍ

`actual_tuition`
→ Document chứa mức học phí THỰC TẾ phải đóng.

`exemption_basis`
→ Document chứa mức học phí/mức tiền được dùng làm CƠ SỞ để tính miễn giảm.

`exemption_policy`
→ Document chứa chính sách, đối tượng, điều kiện, thủ tục hoặc hồ sơ miễn giảm học phí.

`calculation`
→ Document chứa công thức/quy tắc dùng để TÍNH số tiền phải đóng sau miễn giảm.

`both`
→ Document thực sự chứa cả thông tin về học phí thực tế và cơ sở/mức dùng để tính miễn giảm.

`ambiguous_tuition`
→ Chỉ sử dụng khi bản thân document có nội dung về học phí nhưng không thể xác định rõ thuộc loại học phí nào ở trên.

### HỌC BỔNG

`scholarship`
→ Document về học bổng, đặc biệt học bổng khuyến khích học tập.

### HỖ TRỢ TÀI CHÍNH

`student_loan`
→ Document về vay vốn sinh viên, NHCSXH, Vietinbank, vay STEM, Quyết định 157 hoặc các chương trình vay vốn dành cho sinh viên.

`social_support`
→ Document về trợ cấp xã hội, hỗ trợ chi phí học tập/đào tạo và các chính sách hỗ trợ sinh viên có tính chất hỗ trợ xã hội.

### HỌC VỤ / ĐÀO TẠO

`academic_rules`
→ Quy chế học vụ hoặc quy định đào tạo CỤ THỂ, ví dụ bảo lưu, cảnh báo học vụ, điều kiện học tập, xử lý kết quả học tập.

`quy_che_general`
→ Quy định chung của trường nhưng không thuộc một nhóm chuyên biệt khác.

`academic_program`
→ Chương trình đào tạo, ngành học, môn học, cấu trúc chương trình, chuẩn đầu ra hoặc nội dung đào tạo của ngành.

### KHÁC

`other`
→ Document không phù hợp với bất kỳ domain nào ở trên.

═══════════════════════════════════════════

## 3. QUY TẮC PHÂN LOẠI DOCUMENT

═══════════════════════════════════════════

### QUY TẮC 1 — PHẢI ĐỌC NỘI DUNG DOCUMENT

Không được quyết định domain chỉ dựa trên:

* tên file
* tên văn bản
* số quyết định
* `content_kind`
* `fee_kind`
* từ khóa trong metadata

Phải dựa chủ yếu vào NỘI DUNG THỰC TẾ của document.

Tên file chỉ được dùng làm tín hiệu hỗ trợ.

### QUY TẮC 2 — KHÔNG NHẦM DOCUMENT VỀ MIỄN GIẢM VỚI HỌC PHÍ THỰC TẾ

Ví dụ:

Document nói về:

* đối tượng được miễn giảm
* điều kiện miễn giảm
* hồ sơ miễn giảm
* thủ tục miễn giảm

→ `exemption_policy`

Document nói về:

* mức học phí dùng để tính số tiền miễn giảm
* mức trần
* mức cơ sở tính miễn giảm

→ `exemption_basis`

Document nói về:

* số tiền học phí sinh viên thực tế phải đóng

→ `actual_tuition`

### QUY TẮC 3 — KHÔNG DÙNG `calculation` CHỈ VÌ DOCUMENT CÓ SỐ

`calculation` chỉ dùng khi document thực sự chứa công thức, phương pháp hoặc quy tắc tính toán số tiền sau miễn giảm.

Một bảng mức học phí thông thường vẫn là `actual_tuition` hoặc `exemption_basis`, không phải `calculation`.

### QUY TẮC 4 — DOCUMENT VỀ NGÀNH/CHƯƠNG TRÌNH

Nếu document nói về:

* chương trình đào tạo
* ngành học
* danh sách môn học
* tín chỉ
* chuẩn đầu ra
* cấu trúc chương trình

→ `academic_program`

Không gán thành `actual_tuition` chỉ vì document có đề cập học phí.

### QUY TẮC 5 — DOCUMENT VỀ QUY CHẾ

Nếu document là quy chế học vụ cụ thể:

→ `academic_rules`

Nếu là quy định chung nhưng không thuộc học vụ cụ thể:

→ `quy_che_general`

### QUY TẮC 6 — VAY VỐN VÀ TRỢ CẤP

Nếu nội dung chính là vay tiền/vay vốn:

→ `student_loan`

Nếu nội dung chính là trợ cấp, hỗ trợ xã hội hoặc hỗ trợ chi phí học tập:

→ `social_support`

Không gán các document này thành `scholarship`.

### QUY TẮC 7 — HỌC BỔNG

Document về học bổng:

→ `scholarship`

Bao gồm:

* mức học bổng
* tiêu chuẩn học bổng
* điều kiện nhận học bổng
* danh sách/chương trình học bổng
* quyết định cấp học bổng

═══════════════════════════════════════════

## 4. KIỂM TRA DOMAIN HIỆN TẠI

═══════════════════════════════════════════

Với MỖI document trong `document_metadata.json`:

1. Xác định `domain` hiện tại.
2. Đọc/đối chiếu nội dung document tương ứng trong NotebookLM.
3. Xác định domain phù hợp nhất theo taxonomy ở trên.
4. So sánh domain hiện tại với domain phù hợp.
5. Kết luận:

   * `CORRECT` nếu domain hiện tại đúng.
   * `INCORRECT` nếu domain hiện tại sai.
   * `INVALID` nếu domain hiện tại không nằm trong 13 domain được phép.
   * `UNCERTAIN` nếu nội dung không đủ để xác định chắc chắn.

═══════════════════════════════════════════

## 5. OUTPUT

═══════════════════════════════════════════

Chỉ tập trung vào việc kiểm tra `domain`.

Không kiểm tra:

* `content_kind`
* `fee_kind`
* `academic_year`
* `status`
* `next_agent`
* `intent`

Kết quả trình bày theo bảng:

| Document | Current domain | Expected domain | Status | Evidence |
| -------- | -------------- | --------------- | ------ | -------- |

Trong đó:

* `Current domain`: domain đang có trong JSON.
* `Expected domain`: domain đúng theo nội dung document.
* `Status`: CORRECT / INCORRECT / INVALID / UNCERTAIN.
* `Evidence`: mô tả NGẮN GỌN phần nội dung chứng minh domain.

═══════════════════════════════════════════

## 6. QUAN TRỌNG

═══════════════════════════════════════════

Không được tự động giữ nguyên domain hiện tại.

Nếu domain hiện tại sai, phải đề xuất domain đúng.

Đặc biệt phải kiểm tra kỹ các trường hợp:

`tuition`
→ phải map vào một trong:
actual_tuition / exemption_basis / exemption_policy / calculation / both / ambiguous_tuition

`academic_regulation`
→ phải map vào:
academic_rules hoặc quy_che_general

Không được trả về `tuition` hoặc `academic_regulation` vì chúng KHÔNG nằm trong taxonomy được phép.

Nếu một document không thể xác định rõ:
→ `other`
hoặc `UNCERTAIN` nếu thực sự thiếu thông tin để kết luận.

Mục tiêu cuối cùng là tạo ra một `document_metadata.json` trong đó **mọi giá trị `domain` đều thuộc đúng 13 domain được phép và phù hợp với nội dung document**.
