# BÁO CÁO THẨM ĐỊNH CHI TIẾT CĂN CỨ BẢNG 5 (FAILURE TAXONOMY AUDIT)
> **Mục tiêu**: Cung cấp hồ sơ truy vết thủ công (manual trace audit) chứng minh nguồn gốc các con số trong Bảng 5 (`tab:failures`) của bài báo.
> **Tổng số ca thất bại (< 50% Fact Coverage)**: 58 ca (Single Agent: 34, CTU-Chat: 24)
> **File dữ liệu chi tiết JSON**: `report/table5_failure_audit_trace.json`

## 1. BẢNG TỔNG HỢP PHÂN LOẠI LỖI (TABLE 5 SUMMARY)

| Phân loại chính | Dạng lỗi cụ thể | Single Agent (`S1-A`) | CTU-Chat (`S1-C`) | Cơ chế xác định |
| :--- | :--- | :---: | :---: | :--- |
| **Routing** | Corrected misroute | N/A | 1 | Supervisor chọn sai route nhưng cơ chế Contract Repair sửa lại thành công |
| | Unrecoverable misroute | N/A | 3 | Supervisor phân loại sai domain không thể cứu vãn |
| **Retrieval** | Gold source absent | 3 | 3 | Tài liệu chuẩn không nằm trong kho dữ liệu hoặc không được đánh chỉ mục |
| | Cross-domain omission | 3 | 2 | Câu hỏi đa miền bị thiếu nhánh tài liệu của miền thứ hai |
| | Reranker demoted | 7 | 6 | Đoạn văn bản chứa gold fact bị mô hình reranker xếp hạng ngoài top-7 |
| **Tool Execution** | Invalid arguments | 4 | 1 | Agent gọi công cụ nhưng truyền sai định dạng/tên thực thể |
| | Wrong-family call | 3 | 1 | Agent gọi nhầm công cụ thuộc họ nghiệp vụ khác |
| | Unnecessary call | 5 | 1 | Câu hỏi retrieval thuần nhưng agent vẫn kích hoạt gọi công cụ thừa thãi |
| **Generation** | Result ignored | 2 | 1 | Công cụ trả về kết quả đúng nhưng LLM bỏ qua khi tổng hợp câu trả lời |
| | Partial fact omission | 22 | 14 | Retrieval trúng 100% nhưng câu trả lời bỏ sót một phần facts quy định |
| **Tổng số ca lỗi** | *(Non-mutually exclusive)* | **34** | **24** | **CTU-Chat giảm được 10 ca lỗi so với Single Agent** |

## 2. DANH SÁCH CHI TIẾT 34 CA THẤT BẠI CỦA SINGLE AGENT (S1-A)

### [01/34] `HOUT-DIR-ACAD-03` (academic | direct)
- **Câu hỏi**: Ngành Đảm bảo chất lượng và an toàn thực phẩm có bao nhiêu tín chỉ bắt buộc trên tổng số tín chỉ?
- **Fact Coverage**: 33.3% | **Tools gọi**: 1
- **Required Facts**: `['161 tín chỉ', '117 tín chỉ bắt buộc', '44 tín chỉ tự chọn']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Trong tổng số 161 tín chỉ của ngành Đảm bảo chất lượng và an toàn thực phẩm (mã ngành: 7540106), có 127 tín chỉ bắt buộc (bao gồm 32 tín chỉ Giáo dục đại cương, 43 tín chỉ chuyên ngành và 42 tín chỉ c...

### [02/34] `HOUT-DIR-ACAD-06` (academic | direct)
- **Câu hỏi**: Khung đào tạo cử nhân Quản lý thủy sản thiết kế tất cả bao nhiêu tín chỉ trong toàn khóa?
- **Fact Coverage**: 0.0% | **Tools gọi**: 1
- **Required Facts**: `['Quản lý thủy sản', '141 tín chỉ']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: 

### [03/34] `HOUT-DIR-ACAD-07` (academic | direct)
- **Câu hỏi**: Ngành Công nghệ Sau thu hoạch tại Trường ĐHCT có bao nhiêu tín chỉ bắt buộc?
- **Fact Coverage**: 33.3% | **Tools gọi**: 1
- **Required Facts**: `['Công nghệ Sau thu hoạch', '116 tín chỉ bắt buộc', '161']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Trong khối kiến thức cơ sở ngành của ngành Công nghệ Sau thu hoạch (mã ngành: 7540104), có 44 tín chỉ bắt buộc và 6 tín chỉ tự chọn.

### [04/34] `HOUT-DIR-ACAD-08` (academic | direct)
- **Câu hỏi**: Chương trình chất lượng cao ngành Công nghệ thực phẩm yêu cầu tích lũy bao nhiêu tín chỉ?
- **Fact Coverage**: 0.0% | **Tools gọi**: 1
- **Required Facts**: `['Công nghệ thực phẩm chất lượng cao', '161 tín chỉ']`
- **Source Recall**: 1.0 | **Source AP**: 0.5
- **Phản hồi**: Chương trình Chất lượng cao ngành Công nghệ thực phẩm có tổng số 168 tín chỉ.

### [05/34] `HOUT-DIR-ACAD-09` (academic | direct)
- **Câu hỏi**: Số lượng tín chỉ cần hoàn tất đối với sinh viên ngành Kỹ thuật y sinh được quy định là bao nhiêu?
- **Fact Coverage**: 0.0% | **Tools gọi**: 1
- **Required Facts**: `['Kỹ thuật y sinh', '161 tín chỉ']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: 

### [06/34] `HOUT-DIR-ACAD-10` (academic | direct)
- **Câu hỏi**: Trong chương trình Kỹ thuật cơ điện tử chuẩn, phần kiến thức bắt buộc chiếm bao nhiêu tín chỉ?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['Kỹ thuật cơ điện tử', '116 tín chỉ bắt buộc', '161']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Trong chương trình Kỹ thuật cơ điện tử, khối kiến thức chuyên ngành có 42 tín chỉ bắt buộc.

### [07/34] `HOUT-DIR-FIN-04` (financial | direct)
- **Câu hỏi**: Cho em hỏi học phí mỗi tín chỉ ngành Tài chính - Ngân hàng CLC K52 tính bao nhiêu một tín chỉ?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['Tài chính - Ngân hàng', 'CLC', '1.363.000 đồng/tín chỉ']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: 

### [08/34] `HOUT-DIR-FIN-08` (financial | direct)
- **Câu hỏi**: Học phí ngành Thú y chương trình chất lượng cao K52 thu bao nhiêu triệu một năm?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['Thú y', 'CLC', '44 triệu đồng/năm']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Học phí ngành Thú y chương trình chất lượng cao khóa K52 là 41,8 triệu đồng một năm.

### [09/34] `HOUT-DIR-SCH-04` (scholarship | direct)
- **Câu hỏi**: Tân sinh viên Khóa 52 đạt học bổng đầu vào có mức hỗ trợ bình quân trong học kỳ đầu tiên là bao nhiêu?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['5.000.000 đồng', 'học kỳ đầu tiên', 'tân sinh viên']`
- **Source Recall**: 1.0 | **Source AP**: 0.5
- **Phản hồi**: Theo quy định về học bổng cho học kỳ đầu tiên của khóa 52, mức học bổng khuyến khích là 6.000.000 đồng/sinh viên/học kỳ.

### [10/34] `HOUT-DIR-SCH-08` (scholarship | direct)
- **Câu hỏi**: Học bổng SCIC dành cho sinh viên thuộc các ngành học nào?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['SCIC', 'Kinh tế', 'Tài chính']`
- **Source Recall**: 1.0 | **Source AP**: 0.5
- **Phản hồi**: Học bổng SCIC dành cho sinh viên theo học tại Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ.

### [11/34] `HOUT-DIR-GEN-05` (general | direct)
- **Câu hỏi**: Sinh viên được xin tạm nghỉ học vì lý do cá nhân tối đa bao nhiêu học kỳ?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['tạm nghỉ học', 'thời gian học tập tối đa']`
- **Source Recall**: 0.0 | **Source AP**: 0.0
- **Phản hồi**: Theo quy định của Trường Đại học Cần Thơ:

*   **Sinh viên học bổng Hiệp định:** Được tạm dừng học tập tối đa 01 năm học (tương đương 2 học kỳ) nếu có lý do chính đáng và được sự đồng ý của các bên li...

### [12/34] `HOUT-DIR-GEN-10` (general | direct)
- **Câu hỏi**: Hướng dẫn và quy trình tiếp nhận sinh viên chuyển ngành chuyển trường theo văn bản 3924 quy định ra sao?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['3924', 'chuyển ngành', 'chuyển trường']`
- **Source Recall**: 1.0 | **Source AP**: 0.5
- **Phản hồi**: Theo văn bản số 3924/KHTH-ĐT ngày 23/10/2023, đây là "ĐƠN ĐỀ NGHỊ CHUYỂN CHƯƠNG TRÌNH, NGÀNH ĐÀO TẠO". Đơn này bao gồm các thông tin cần thiết khi sinh viên có nguyện vọng chuyển sang học một chương t...

### [13/34] `HOUT-MHOP-FIN-01` (financial | multi_hop)
- **Câu hỏi**: Sinh viên học ngành Kỹ thuật điều khiển và tự động hóa CLC K52 nếu được giảm 70% học phí theo chính sách thì số tiền hỗ trợ được tính dựa trên mức biểu phí nào?
- **Fact Coverage**: 0.0% | **Tools gọi**: 2
- **Required Facts**: `['538.000 đồng/tín chỉ', 'Khối ngành V', 'cơ sở tính miễn giảm']`
- **Source Recall**: 0.6666666666666666 | **Source AP**: 0.6666666666666666
- **Phản hồi**: Dựa trên thông tin bạn cung cấp, mức học phí thực tế cho ngành Kỹ thuật điều khiển và tự động hóa CLC K52 là 1.340.000 đồng/tín chỉ. Tuy nhiên, tôi không tìm thấy thông tin về mức học phí làm cơ sở để...

### [14/34] `HOUT-MHOP-FIN-02` (financial | multi_hop)
- **Câu hỏi**: Học phí toàn khóa ngành Kiến trúc K52 hệ chuẩn là bao nhiêu và chia trung bình mỗi năm học sinh viên đóng khoảng bao nhiêu tiền?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['Kiến trúc', '165,6 triệu đồng', '5 năm']`
- **Source Recall**: 0.5 | **Source AP**: 0.5
- **Phản hồi**: Học phí toàn khóa ngành Kiến trúc hệ chuẩn Khóa 52 là 165.6 triệu đồng.
Chia trung bình mỗi năm, sinh viên đóng khoảng 33.12 triệu đồng.

### [15/34] `HOUT-MHOP-FIN-04` (financial | multi_hop)
- **Câu hỏi**: Tổng học phí toàn khóa ngành Thú y hệ chuẩn K52 so với số tín chỉ toàn khóa 175 tín chỉ thì đơn giá bình quân mỗi tín chỉ là bao nhiêu?
- **Fact Coverage**: 33.3% | **Tools gọi**: 1
- **Required Facts**: `['Thú y', '166,6 triệu', '966.000 đồng/tín chỉ']`
- **Source Recall**: 0.6666666666666666 | **Source AP**: 0.6666666666666666
- **Phản hồi**: Dựa trên thông tin bạn cung cấp, học phí cho ngành Thú y hệ chuẩn K52 là 1.016.000 đồng/tín chỉ. Tuy nhiên, bạn lại đề cập đến tổng số tín chỉ toàn khóa là 175 tín chỉ, trong khi thông tin tra cứu đượ...

### [16/34] `HOUT-MHOP-SCH-01` (scholarship | multi_hop)
- **Câu hỏi**: Học bổng khuyến khích học tập kỳ đầu tiên của tân sinh viên K51 có mức bình quân bao nhiêu và được chi trả vào thời gian nào?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['5.000.000 đồng', 'K51', 'khuyến khích học tập']`
- **Source Recall**: 1.0 | **Source AP**: 0.8333333333333333
- **Phản hồi**: Mức học bổng bình quân cho học kỳ đầu tiên của tân sinh viên Khóa 51 là 5.000.000 đồng/sinh viên/học kỳ.

Thông tin về thời gian chi trả học bổng không có trong tài liệu được cung cấp. Bạn có thể liên...

### [17/34] `HOUT-MHOP-SCH-02` (scholarship | multi_hop)
- **Câu hỏi**: Cách phân bổ quỹ học bổng khuyến khích cho từng ngành học được tính dựa trên tỷ lệ phần trăm nào của tổng học phí sinh viên đã đóng?
- **Fact Coverage**: 33.3% | **Tools gọi**: 1
- **Required Facts**: `['8%', '90%', 'học phí sinh viên cùng khóa, ngành']`
- **Source Recall**: 1.0 | **Source AP**: 0.5833333333333333
- **Phản hồi**: Dựa trên thông tin tôi có, quỹ học bổng khuyến khích học tập được phân bổ cho từng lớp chuyên ngành dựa trên tỷ lệ 8% tổng học phí sinh viên đã đóng của lớp đó. Tuy nhiên, có một số quy định cụ thể ch...

### [18/34] `HOUT-MHOP-SCH-05` (scholarship | multi_hop)
- **Câu hỏi**: Sinh viên đạt học bổng khuyến khích loại Xuất sắc thì số tiền nhận được so với mức học phí đã nộp của kỳ đó được xác định ra sao?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['1,2', '120%', 'học phí đã nộp']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Mức học bổng loại Xuất sắc bằng 1,2 lần mức học bổng loại Khá. Mức học bổng loại Khá được xác định bằng số tiền học phí sinh viên đã đóng trong học kỳ liền trước. Trường hợp được miễn, giảm, được nhà ...

### [19/34] `HOUT-MHOP-GEN-03` (general | multi_hop)
- **Câu hỏi**: Thủ tục xin miễn 100% học phí theo quy định chính sách cần làm đơn theo mẫu nào và nộp vào thời điểm nào trong học kỳ?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['miễn 100% học phí', 'mẫu số 12', 'đầu mỗi học kỳ']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Xin vui lòng cho biết bạn thuộc đối tượng nào trong các trường hợp sau để tôi có thể hướng dẫn cụ thể hơn về thủ tục và thời điểm nộp đơn:

*   Con của người hoạt động cách mạng trước 08/1945; Con của...

### [20/34] `HOUT-MHOP-GEN-04` (general | multi_hop)
- **Câu hỏi**: Quy trình xin chuyển ngành từ năm thứ hai theo văn bản 3924 kết hợp quy chế học vụ yêu cầu điều kiện điểm trung bình tích lũy đạt từ mức nào?
- **Fact Coverage**: 33.3% | **Tools gọi**: 1
- **Required Facts**: `['chuyển ngành', 'năm thứ nhất', 'không bị cảnh báo']`
- **Source Recall**: 0.5 | **Source AP**: 0.25
- **Phản hồi**: Dựa trên thông tin bạn cung cấp, quy trình xin chuyển ngành từ năm thứ hai theo văn bản 3924 kết hợp quy chế học vụ yêu cầu điểm trung bình tích lũy đạt từ 2,00 trở lên.

### [21/34] `HOUT-XDOM-01` (financial+academic | cross_domain)
- **Câu hỏi**: Ngành Nuôi trồng thủy sản chương trình tiên tiến K52 có tổng bao nhiêu tín chỉ và đơn giá mỗi tín chỉ chuyên ngành là bao nhiêu đồng?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['Nuôi trồng thủy sản tiên tiến', '161 tín chỉ', '1.564.000 đồng/tín chỉ']`
- **Source Recall**: 1.0 | **Source AP**: 0.9166666666666666
- **Phản hồi**: Ngành Nuôi trồng thủy sản - Chương trình tiên tiến có tổng số 163 tín chỉ. Đối với chương trình tiên tiến, khóa K52 có đơn giá mỗi tín chỉ là 1.564.000 đồng.

### [22/34] `HOUT-XDOM-07` (financial+scholarship | cross_domain)
- **Câu hỏi**: Học phí một năm của ngành Tài chính - Ngân hàng CLC K52 là bao nhiêu và sinh viên có thể ứng tuyển học bổng SCIC trị giá 10 triệu không?
- **Fact Coverage**: 25.0% | **Tools gọi**: 0
- **Required Facts**: `['Tài chính - Ngân hàng', '38.000.000 đồng/năm', 'SCIC', '10.000.000 đồng']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Học phí một năm của ngành Tài chính – Ngân hàng chương trình chất lượng cao, khóa K52 là 40.000.000 đồng/năm học.

Về học bổng SCIC trị giá 10 triệu đồng, học bổng này chỉ dành cho sinh viên theo học ...

### [23/34] `HOUT-XDOM-09` (financial+scholarship | cross_domain)
- **Câu hỏi**: Quỹ học bổng khuyến khích trích tối thiểu 8% từ nguồn thu học phí, vậy sinh viên đạt loại Xuất sắc ngành Quản trị kinh doanh K52 sẽ nhận mức học bổng tính ra sao so với học phí đã đóng?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['8%', '1,2', 'học phí thực đóng']`
- **Source Recall**: 1.0 | **Source AP**: 0.9166666666666666
- **Phản hồi**: Để tính chính xác mức học bổng loại Xuất sắc cho sinh viên ngành Quản trị kinh doanh K52, bạn vui lòng cho biết thêm thông tin về chương trình đào tạo (ví dụ: chuẩn, chất lượng cao - clc) của ngành nà...

### [24/34] `HOUT-XDOM-13` (financial+social_support | cross_domain)
- **Câu hỏi**: Sinh viên học ngành Quản trị kinh doanh K52 thuộc diện hộ cận nghèo thì được giảm bao nhiêu phần trăm học phí và mức hỗ trợ mỗi tín chỉ là bao nhiêu?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['Khối ngành III', '451.000 đồng/tín chỉ', 'Quản trị kinh doanh']`
- **Source Recall**: 0.0 | **Source AP**: 0.0
- **Phản hồi**: Chào bạn,

Theo thông tin tra cứu được:
*   Học phí thực tế của ngành Quản trị kinh doanh (chương trình chuẩn), khóa K52 là **844.000 đồng/tín chỉ**.
*   Mức học phí làm cơ sở để tính miễn giảm cho ng...

### [25/34] `HOUT-XDOM-16` (academic+scholarship | cross_domain)
- **Câu hỏi**: Sinh viên ngành Nuôi trồng thủy sản chương trình tiên tiến cần tích lũy bao nhiêu tín chỉ và điểm GPA tối thiểu bao nhiêu để nộp hồ sơ học bổng SCC?
- **Fact Coverage**: 25.0% | **Tools gọi**: 0
- **Required Facts**: `['Nuôi trồng thủy sản tiên tiến', '161 tín chỉ', '8.0', 'SCC']`
- **Source Recall**: 0.5 | **Source AP**: 0.25
- **Phản hồi**: Chào bạn,

Chương trình đào tạo ngành Nuôi trồng thủy sản - Chương trình tiên tiến (mã ngành: 7620301T) có tổng số tín chỉ là 163 tín chỉ.

Về học bổng, tôi có thông tin về **Học bổng Vallet** như sau...

### [26/34] `HOUT-XDOM-19` (academic+scholarship | cross_domain)
- **Câu hỏi**: Sinh viên ngành Thú y học trong 5 năm với 175 tín chỉ thì quỹ học bổng khuyến khích có cấp suốt 5 năm học không?
- **Fact Coverage**: 25.0% | **Tools gọi**: 0
- **Required Facts**: `['Thú y', '175 tín chỉ', '5 năm', 'từng học kỳ']`
- **Source Recall**: 0.5 | **Source AP**: 0.25
- **Phản hồi**: Dựa trên thông tin được cung cấp, quỹ học bổng khuyến khích học tập được tính toán dựa trên tổng học phí của sinh viên trong học kỳ liền trước và có quy trình phân bổ cho từng học kỳ (HK1, HK2). Điều ...

### [27/34] `HOUT-COMP-02` (financial | comparison)
- **Câu hỏi**: Học phí toàn khóa ngành Thú y hệ chuẩn K52 cao hơn hay thấp hơn ngành Kiến trúc hệ chuẩn K52 và chênh lệch bao nhiêu triệu?
- **Fact Coverage**: 40.0% | **Tools gọi**: 0
- **Required Facts**: `['Thú y', '166,6 triệu', 'Kiến trúc', '165,6 triệu', 'cao hơn 1,0 triệu']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Tôi tra cứu được học phí ngành Kiến trúc hệ chuẩn K52 là 165.6 triệu đồng/khóa. Tuy nhiên, tôi không tìm thấy thông tin học phí ngành Thú y hệ chuẩn K52. Tôi chỉ tìm thấy thông tin học phí ngành Thú y...

### [28/34] `HOUT-COMP-03` (financial | comparison)
- **Câu hỏi**: Học phí niên chế một năm của hai chuyên ngành chất lượng cao QTKD và Tài chính Ngân hàng khóa 52 chênh nhau như thế nào?
- **Fact Coverage**: 25.0% | **Tools gọi**: 0
- **Required Facts**: `['Quản trị kinh doanh', 'Tài chính - Ngân hàng', 'CLC', '38.000.000 đồng/năm']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Học phí niên chế một năm của hai chuyên ngành Chất lượng cao Quản trị kinh doanh và Tài chính Ngân hàng khóa 52 là như nhau, đều là 40.000.000 đồng/năm học. Do đó, mức chênh lệch giữa hai chuyên ngành...

### [29/34] `HOUT-COMP-07` (academic | comparison)
- **Câu hỏi**: Chương trình đào tạo ngành Thú y hệ chuẩn và ngành Quản lý thủy sản khác nhau bao nhiêu tín chỉ toàn khóa?
- **Fact Coverage**: 40.0% | **Tools gọi**: 2
- **Required Facts**: `['Thú y', '175 tín chỉ', 'Quản lý thủy sản', '141 tín chỉ', '34']`
- **Source Recall**: 0.5 | **Source AP**: 0.25
- **Phản hồi**: Ngành Thú y có 173 tín chỉ, ngành Quản lý thủy sản có 161 tín chỉ. Vậy ngành Thú y có nhiều hơn ngành Quản lý thủy sản là 12 tín chỉ.

### [30/34] `HOUT-COMP-10` (financial | comparison)
- **Câu hỏi**: Giữa ngành Luật hệ chuẩn K52 và ngành Kỹ thuật xây dựng hệ chuẩn K52 thì ngành nào có học phí toàn khóa thấp hơn và thấp hơn bao nhiêu?
- **Fact Coverage**: 40.0% | **Tools gọi**: 0
- **Required Facts**: `['Luật', '114,5 triệu', 'Kỹ thuật xây dựng', '150,3 triệu', 'thấp hơn 35,8 triệu']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Dựa trên thông tin học phí thực tế cho Khóa 52 năm học 2026-2027:

*   **Ngành Luật dân sự và tố tụng dân sự (mã 7380103)** có học phí toàn khóa là 114,500,000 VNĐ.
*   **Ngành Kỹ thuật xây dựng (mã 7...

### [31/34] `HOUT-TEMP-01` (financial | temporal)
- **Câu hỏi**: Học phí một tín chỉ chuyên ngành của ngành Tài chính - Ngân hàng CLC thay đổi như thế nào từ Khóa 49 đến Khóa 52?
- **Fact Coverage**: 25.0% | **Tools gọi**: 3
- **Required Facts**: `['Khóa 49', '1.142.000', 'Khóa 52', '1.363.000']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Học phí một tín chỉ chuyên ngành của ngành Tài chính - Ngân hàng CLC thay đổi như sau:
- Khóa K50: 1.118.000 đồng/tín chỉ
- Khóa K51: 1.363.000 đồng/tín chỉ
- Khóa K52: 1.363.000 đồng/tín chỉ

### [32/34] `HOUT-ADVS-01` (financial | adversarial)
- **Câu hỏi**: Học phí đại học Trường Đại học Cần Thơ năm nay thu bao nhiêu tiền?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['theo tín chỉ', 'tùy thuộc vào ngành học', 'khóa tuyển sinh']`
- **Source Recall**: 0.6666666666666666 | **Source AP**: 0.6666666666666666
- **Phản hồi**: Bạn vui lòng cho biết bạn muốn tra cứu học phí của năm học nào, hệ đào tạo nào (chính quy, VLVH, từ xa, CLC, tiên tiến...), và ngành học cụ thể (hoặc khóa tuyển sinh) để tôi có thể cung cấp thông tin ...

### [33/34] `HOUT-ADVS-02` (scholarship | adversarial)
- **Câu hỏi**: Sinh viên muốn xin học bổng thì cần đáp ứng những tiêu chuẩn chung gì?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['điểm học tập', 'điểm rèn luyện', 'loại Khá trở lên']`
- **Source Recall**: 0.0 | **Source AP**: 0.0
- **Phản hồi**: Để xin học bổng, sinh viên cần đáp ứng các tiêu chuẩn chung sau:

*   **Về học tập:**
    *   Có điểm trung bình học kỳ chính khóa từ 7,5 trở lên (theo thang điểm 10) hoặc từ 3,0 trở lên (theo thang đ...

### [34/34] `HOUT-ADVS-03` (general | adversarial)
- **Câu hỏi**: Trường Đại học Cần Thơ có những chính sách hỗ trợ tài chính nào dành cho sinh viên có hoàn cảnh khó khăn?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['miễn giảm học phí', 'hỗ trợ chi phí học tập', 'trợ cấp xã hội', 'vay vốn']`
- **Source Recall**: 0.25 | **Source AP**: 0.0625
- **Phản hồi**: Trường Đại học Cần Thơ có chính sách hỗ trợ tài chính cho sinh viên có hoàn cảnh khó khăn thông qua việc vận động các cơ quan, tổ chức, cá nhân đóng góp học bổng để giúp sinh viên có hoàn cảnh khó khă...

## 3. DANH SÁCH CHI TIẾT 24 CA THẤT BẠI CỦA CTU-CHAT (S1-C)

### [01/24] `HOUT-DIR-ACAD-03` (academic | direct)
- **Câu hỏi**: Ngành Đảm bảo chất lượng và an toàn thực phẩm có bao nhiêu tín chỉ bắt buộc trên tổng số tín chỉ?
- **Fact Coverage**: 33.3% | **Tools gọi**: 1
- **Required Facts**: `['161 tín chỉ', '117 tín chỉ bắt buộc', '44 tín chỉ tự chọn']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Trong ngành Đảm bảo chất lượng và an toàn thực phẩm, có **121 tín chỉ bắt buộc** trên tổng số 161 tín chỉ.

### [02/24] `HOUT-DIR-ACAD-08` (academic | direct)
- **Câu hỏi**: Chương trình chất lượng cao ngành Công nghệ thực phẩm yêu cầu tích lũy bao nhiêu tín chỉ?
- **Fact Coverage**: 0.0% | **Tools gọi**: 1
- **Required Facts**: `['Công nghệ thực phẩm chất lượng cao', '161 tín chỉ']`
- **Source Recall**: 1.0 | **Source AP**: 0.5
- **Phản hồi**: Chương trình Chất lượng cao ngành Công nghệ Thực phẩm tại Trường Đại học Cần Thơ yêu cầu tích lũy 168 tín chỉ.

### [03/24] `HOUT-DIR-ACAD-10` (academic | direct)
- **Câu hỏi**: Trong chương trình Kỹ thuật cơ điện tử chuẩn, phần kiến thức bắt buộc chiếm bao nhiêu tín chỉ?
- **Fact Coverage**: 33.3% | **Tools gọi**: 1
- **Required Facts**: `['Kỹ thuật cơ điện tử', '116 tín chỉ bắt buộc', '161']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Trong chương trình Kỹ thuật cơ điện tử chuẩn, phần kiến thức bắt buộc chiếm:
- Khối kiến thức Giáo dục đại cương: 39 tín chỉ
- Khối kiến thức chuyên ngành: 42 tín chỉ
- Khối kiến thức cơ sở ngành: 41 ...

### [04/24] `HOUT-DIR-FIN-08` (financial | direct)
- **Câu hỏi**: Học phí ngành Thú y chương trình chất lượng cao K52 thu bao nhiêu triệu một năm?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['Thú y', 'CLC', '44 triệu đồng/năm']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Học phí ngành Thú y, chương trình Chất lượng cao, khóa K52, năm học 2026-2027 là 41,8 triệu đồng/năm học.

### [05/24] `HOUT-DIR-SCH-08` (scholarship | direct)
- **Câu hỏi**: Học bổng SCIC dành cho sinh viên thuộc các ngành học nào?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['SCIC', 'Kinh tế', 'Tài chính']`
- **Source Recall**: 1.0 | **Source AP**: 0.5
- **Phản hồi**: Học bổng SCIC năm 2026 dành cho sinh viên đang theo học tại Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ, có thành tích, giải thưởng về lĩnh vực công nghệ, trí tuệ nhân tạo (AI) và hoạt ...

### [06/24] `HOUT-DIR-GEN-05` (general | direct)
- **Câu hỏi**: Sinh viên được xin tạm nghỉ học vì lý do cá nhân tối đa bao nhiêu học kỳ?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['tạm nghỉ học', 'thời gian học tập tối đa']`
- **Source Recall**: 0.0 | **Source AP**: 0.0
- **Phản hồi**: Tôi không tìm thấy thông tin này trong tài liệu hiện có của Nhà trường.

### [07/24] `HOUT-MHOP-ACAD-03` (academic | multi_hop)
- **Câu hỏi**: Sinh viên muốn nộp đơn xin tạm nghỉ học thì cần đáp ứng điều kiện gì trong quy chế học vụ và thời hạn tối đa nộp đơn trước học kỳ là khi nào?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['tạm nghỉ học', 'ít nhất một học kỳ', 'Quy chế học vụ']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Theo Quy định công tác học vụ dành cho sinh viên trình độ đại học hình thức chính quy, sinh viên có thể làm đơn xin phép nghỉ học tạm thời trong các trường hợp sau:

1.  **Được điều động vào các lực l...

### [08/24] `HOUT-MHOP-ACAD-04` (academic | multi_hop)
- **Câu hỏi**: Nếu sinh viên muốn chuyển chương trình đào tạo sang ngành Kỹ thuật xây dựng thì thủ tục làm đơn và điều kiện số tín chỉ đã tích lũy quy định thế nào?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['chuyển CTĐT', 'Kỹ thuật xây dựng', 'năm thứ nhất']`
- **Source Recall**: 0.5 | **Source AP**: 0.125
- **Phản hồi**: Xin lỗi, tôi không có chức năng tra cứu về thủ tục chuyển chương trình đào tạo hay các quy định về số tín chỉ đã tích lũy. Tôi chỉ có thể cung cấp thông tin về cấu trúc ngành học, môn học, khung chươn...

### [09/24] `HOUT-MHOP-FIN-01` (financial | multi_hop)
- **Câu hỏi**: Sinh viên học ngành Kỹ thuật điều khiển và tự động hóa CLC K52 nếu được giảm 70% học phí theo chính sách thì số tiền hỗ trợ được tính dựa trên mức biểu phí nào?
- **Fact Coverage**: 0.0% | **Tools gọi**: 1
- **Required Facts**: `['538.000 đồng/tín chỉ', 'Khối ngành V', 'cơ sở tính miễn giảm']`
- **Source Recall**: 0.6666666666666666 | **Source AP**: 0.6666666666666666
- **Phản hồi**: Dựa trên thông tin tôi có, tôi không tìm thấy mức học phí làm cơ sở để tính miễn giảm cho ngành Kỹ thuật điều khiển và tự động hóa khóa K52. Do đó, tôi không thể xác định số tiền hỗ trợ cụ thể.

### [10/24] `HOUT-MHOP-FIN-04` (financial | multi_hop)
- **Câu hỏi**: Tổng học phí toàn khóa ngành Thú y hệ chuẩn K52 so với số tín chỉ toàn khóa 175 tín chỉ thì đơn giá bình quân mỗi tín chỉ là bao nhiêu?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['Thú y', '166,6 triệu', '966.000 đồng/tín chỉ']`
- **Source Recall**: 0.6666666666666666 | **Source AP**: 0.6666666666666666
- **Phản hồi**: Theo thông tin từ biểu mức thu học phí năm học 2026-2027, ngành Thú y (mã 7640101), chương trình chuẩn, khóa K52 có mức thu là 1.016.000 VNĐ/tín chỉ.

Tổng số tín chỉ của chương trình này theo dữ liệu...

### [11/24] `HOUT-MHOP-SCH-03` (scholarship | multi_hop)
- **Câu hỏi**: Sinh viên năm cuối ngành Tài chính - Ngân hàng có thể ứng tuyển học bổng SCIC không và hồ sơ cần chuẩn bị những giấy tờ gì?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['SCIC', 'Tài chính - Ngân hàng', 'bảng điểm tích lũy']`
- **Source Recall**: 0.5 | **Source AP**: 0.5
- **Phản hồi**: Chào bạn,

Theo thông tin học bổng SCIC 2026, bạn cần chuẩn bị các giấy tờ sau:
*   Đơn xin học bổng (theo mẫu đính kèm).
*   Bảng điểm có xác nhận của nhà trường.
*   Các minh chứng hợp lệ theo các t...

### [12/24] `HOUT-MHOP-GEN-03` (general | multi_hop)
- **Câu hỏi**: Thủ tục xin miễn 100% học phí theo quy định chính sách cần làm đơn theo mẫu nào và nộp vào thời điểm nào trong học kỳ?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['miễn 100% học phí', 'mẫu số 12', 'đầu mỗi học kỳ']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Để xin miễn 100% học phí, bạn cần làm đơn theo mẫu "ĐƠN ĐỀ NGHỊ MIỄN, GIẢM HỌC PHÍ" (được cung cấp trong tài liệu).

Thông tin về thời điểm nộp đơn trong học kỳ không có trong tài liệu được cung cấp. ...

### [13/24] `HOUT-XDOM-01` (financial+academic | cross_domain)
- **Câu hỏi**: Ngành Nuôi trồng thủy sản chương trình tiên tiến K52 có tổng bao nhiêu tín chỉ và đơn giá mỗi tín chỉ chuyên ngành là bao nhiêu đồng?
- **Fact Coverage**: 0.0% | **Tools gọi**: 0
- **Required Facts**: `['Nuôi trồng thủy sản tiên tiến', '161 tín chỉ', '1.564.000 đồng/tín chỉ']`
- **Source Recall**: 1.0 | **Source AP**: 0.9166666666666666
- **Phản hồi**: Xin lỗi, tôi không thể tra cứu được đơn giá tín chỉ chuyên ngành. Tôi chỉ có thể cung cấp thông tin về tổng số tín chỉ của chương trình đào tạo. Bạn có muốn tôi tra cứu thông tin này không?

### [14/24] `HOUT-XDOM-09` (financial+scholarship | cross_domain)
- **Câu hỏi**: Quỹ học bổng khuyến khích trích tối thiểu 8% từ nguồn thu học phí, vậy sinh viên đạt loại Xuất sắc ngành Quản trị kinh doanh K52 sẽ nhận mức học bổng tính ra sao so với học phí đã đóng?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['8%', '1,2', 'học phí thực đóng']`
- **Source Recall**: 1.0 | **Source AP**: 0.9166666666666666
- **Phản hồi**: Mức học bổng khuyến khích học tập loại Xuất sắc được tính bằng 1.2 lần mức học bổng loại Khá. Mức học bổng loại Khá bằng với số tiền học phí sinh viên đã đóng trong học kỳ liền trước. Do đó, sinh viên...

### [15/24] `HOUT-XDOM-13` (financial+social_support | cross_domain)
- **Câu hỏi**: Sinh viên học ngành Quản trị kinh doanh K52 thuộc diện hộ cận nghèo thì được giảm bao nhiêu phần trăm học phí và mức hỗ trợ mỗi tín chỉ là bao nhiêu?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['Khối ngành III', '451.000 đồng/tín chỉ', 'Quản trị kinh doanh']`
- **Source Recall**: 0.0 | **Source AP**: 0.0
- **Phản hồi**: Chào bạn,

Theo thông tin tra cứu được, học phí cho ngành Quản trị kinh doanh K52 năm học 2026-2027 như sau:
*   Chương trình chuẩn: 844.000 VNĐ/tín chỉ.
*   Chương trình chất lượng cao (CLC): 1.363.0...

### [16/24] `HOUT-XDOM-16` (academic+scholarship | cross_domain)
- **Câu hỏi**: Sinh viên ngành Nuôi trồng thủy sản chương trình tiên tiến cần tích lũy bao nhiêu tín chỉ và điểm GPA tối thiểu bao nhiêu để nộp hồ sơ học bổng SCC?
- **Fact Coverage**: 25.0% | **Tools gọi**: 0
- **Required Facts**: `['Nuôi trồng thủy sản tiên tiến', '161 tín chỉ', '8.0', 'SCC']`
- **Source Recall**: 0.5 | **Source AP**: 0.25
- **Phản hồi**: Xin lỗi, tôi không tìm thấy thông tin về học bổng SCC trong tài liệu được cung cấp.

### [17/24] `HOUT-COMP-02` (financial | comparison)
- **Câu hỏi**: Học phí toàn khóa ngành Thú y hệ chuẩn K52 cao hơn hay thấp hơn ngành Kiến trúc hệ chuẩn K52 và chênh lệch bao nhiêu triệu?
- **Fact Coverage**: 40.0% | **Tools gọi**: 2
- **Required Facts**: `['Thú y', '166,6 triệu', 'Kiến trúc', '165,6 triệu', 'cao hơn 1,0 triệu']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Học phí toàn khóa ngành Thú y hệ chuẩn K52 là 166.6 triệu đồng, cao hơn ngành Kiến trúc hệ chuẩn K52 là 165.6 triệu đồng. Chênh lệch là 1 triệu đồng.

### [18/24] `HOUT-COMP-03` (financial | comparison)
- **Câu hỏi**: Học phí niên chế một năm của hai chuyên ngành chất lượng cao QTKD và Tài chính Ngân hàng khóa 52 chênh nhau như thế nào?
- **Fact Coverage**: 25.0% | **Tools gọi**: 0
- **Required Facts**: `['Quản trị kinh doanh', 'Tài chính - Ngân hàng', 'CLC', '38.000.000 đồng/năm']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Học phí niên chế một năm của ngành Quản trị kinh doanh (chất lượng cao, khóa 52) là 40.000.000 VNĐ/năm học.
Học phí niên chế một năm của ngành Tài chính – Ngân hàng (chất lượng cao, khóa 52) là 40.000...

### [19/24] `HOUT-COMP-05` (financial | comparison)
- **Câu hỏi**: Học phí một năm của ngành Kỹ thuật điều khiển và tự động hóa CLC khóa 51 so với khóa 52 chênh lệch bao nhiêu triệu đồng?
- **Fact Coverage**: 16.7% | **Tools gọi**: 0
- **Required Facts**: `['Kỹ thuật điều khiển và tự động hóa', 'K51', '40 triệu', 'K52', '44 triệu', '4 triệu']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Học phí một năm của ngành Kỹ thuật điều khiển và tự động hóa Chất lượng cao (CLC) khóa 51, năm học 2026-2027 là 37.000.000 VNĐ.

Đối với khóa 52, học phí là 1.251.000 VNĐ/tín chỉ. Với tổng số 161 tín ...

### [20/24] `HOUT-COMP-07` (academic | comparison)
- **Câu hỏi**: Chương trình đào tạo ngành Thú y hệ chuẩn và ngành Quản lý thủy sản khác nhau bao nhiêu tín chỉ toàn khóa?
- **Fact Coverage**: 40.0% | **Tools gọi**: 1
- **Required Facts**: `['Thú y', '175 tín chỉ', 'Quản lý thủy sản', '141 tín chỉ', '34']`
- **Source Recall**: 0.5 | **Source AP**: 0.25
- **Phản hồi**: Ngành Thú y có 173 tín chỉ, còn ngành Quản lý thủy sản có 161 tín chỉ. Như vậy, ngành Thú y có nhiều hơn ngành Quản lý thủy sản 12 tín chỉ toàn khóa.

### [21/24] `HOUT-COMP-10` (financial | comparison)
- **Câu hỏi**: Giữa ngành Luật hệ chuẩn K52 và ngành Kỹ thuật xây dựng hệ chuẩn K52 thì ngành nào có học phí toàn khóa thấp hơn và thấp hơn bao nhiêu?
- **Fact Coverage**: 40.0% | **Tools gọi**: 0
- **Required Facts**: `['Luật', '114,5 triệu', 'Kỹ thuật xây dựng', '150,3 triệu', 'thấp hơn 35,8 triệu']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Chào bạn,

Dựa trên bảng học phí thực tế cho Khóa 52, năm học 2026-2027:

*   **Ngành Luật dân sự và tố tụng dân sự (K52)** có mức học phí toàn khóa là **114,500,000 VNĐ**.
*   **Ngành Kỹ thuật xây dự...

### [22/24] `HOUT-TEMP-04` (academic | temporal)
- **Câu hỏi**: Quy định công tác học vụ năm 2021 (QĐ 1813) và Quy chế học vụ hiện hành có điểm gì cần lưu ý về thời gian tối đa để sinh viên hoàn thành khóa học?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['2 lần thời gian', 'tối đa', 'Quy chế học vụ']`
- **Source Recall**: 1.0 | **Source AP**: 1.0
- **Phản hồi**: Theo Quy định công tác học vụ dành cho sinh viên trình độ đại học hình thức chính quy ban hành kèm theo Quyết định số 1813/QĐ-ĐHCT ngày 12 tháng 7 năm 2021 của Hiệu trưởng Trường Đại học Cần Thơ, có n...

### [23/24] `HOUT-ADVS-02` (scholarship | adversarial)
- **Câu hỏi**: Sinh viên muốn xin học bổng thì cần đáp ứng những tiêu chuẩn chung gì?
- **Fact Coverage**: 33.3% | **Tools gọi**: 0
- **Required Facts**: `['điểm học tập', 'điểm rèn luyện', 'loại Khá trở lên']`
- **Source Recall**: 0.0 | **Source AP**: 0.0
- **Phản hồi**: Để xin học bổng, sinh viên cần đáp ứng các tiêu chuẩn chung sau:

*   **Học bổng Xuất sắc**: GPA từ 3.6 trở lên và Điểm rèn luyện (ĐRL) từ 90 trở lên.
*   **Học bổng Giỏi**: GPA từ 3.2 trở lên và ĐRL ...

### [24/24] `HOUT-ADVS-03` (general | adversarial)
- **Câu hỏi**: Trường Đại học Cần Thơ có những chính sách hỗ trợ tài chính nào dành cho sinh viên có hoàn cảnh khó khăn?
- **Fact Coverage**: 25.0% | **Tools gọi**: 0
- **Required Facts**: `['miễn giảm học phí', 'hỗ trợ chi phí học tập', 'trợ cấp xã hội', 'vay vốn']`
- **Source Recall**: 0.25 | **Source AP**: 0.0625
- **Phản hồi**: Trường Đại học Cần Thơ có các chính sách hỗ trợ tài chính dành cho sinh viên có hoàn cảnh khó khăn như sau:

*   **Hỗ trợ học bổng cho sinh viên có hoàn cảnh khó khăn:**
    *   **Mục đích:** Vận động...
