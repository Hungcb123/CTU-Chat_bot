# BIÊN BẢN HỌP HƯỚNG DẪN & KẾ HOẠCH CHỈNH SỬA BÀI BÁO KHOA HỌC

- **Chủ đề nghiên cứu:** Hệ thống Multi-Agent hỗ trợ sinh viên dựa trên StateGraph / LangGraph và Cơ sở dữ liệu đồ thị Neo4j.
- **Giảng viên hướng dẫn chỉ đạo:** Cô hướng dẫn
- **Nguồn tổng hợp:** File ghi âm góp ý chuyên môn

---

## I. YÊU CẦU TỔNG QUAN VỀ DUNG LƯỢNG & VĂN PHONG

| Hạng mục | Thực trạng hiện tại | Yêu cầu chuẩn hóa | Mục tiêu cần đạt |
| :--- | :--- | :--- | :--- |
| **Dung lượng bài** | Dài 22 trang | Cắt giảm còn **12 – 16 trang** (chuẩn conference) | Tránh phát sinh phí phạt vượt trang (overlength page charges). |
| **Văn phong khoa học** | Bị ảnh hưởng bởi AI, dùng nhiều từ ngữ "đao to búa lớn", rườm rà | Rà soát, chuẩn hóa văn phong học thuật, trung tính, tự nhiên | Đảm bảo tính khoa học, mạch lạc, dễ hiểu. |

---

## II. CHI TIẾT CÁC YÊU CẦU CHỈNH SỬA THEO TỪNG MỤC

### 1. Tóm tắt (Abstract)
- **Tiết giảm chi tiết kỹ thuật:** Lược bỏ các mô tả quá sâu về thuật ngữ kỹ thuật và số liệu thực nghiệm chi tiết không cần thiết.
- **Bổ sung câu kết luận:** Bổ sung 1–2 câu tổng kết cốt lõi ở cuối Abstract (ý nghĩa thực tiễn, đóng góp chính của hệ thống).

### 2. Giới thiệu (Introduction - Mục 1)
- **Hợp nhất Mục 3.1 vào Introduction:**
  - *Vấn đề:* Đoạn mô tả dữ liệu/thành phần ở Mục 3.1 bị trùng lặp với Đoạn 2 của Introduction.
  - *Giải pháp:* Xóa bỏ tiểu mục 3.1 ở phần mô hình; chuyển toàn bộ nội dung này sang làm rõ ngữ cảnh (*context*) và động lực nghiên cứu (*motivation*) tại Đoạn 2 của Introduction. Tiết kiệm ~1 trang.
- **Xử lý khoảng trống nghiên cứu (Research Gaps - Đoạn 4):**
  - *Giải pháp:* Tại Introduction chỉ liệt kê ngắn gọn tên các thách thức (*Challenge 1, 2, 3...*).
  - Toàn bộ nội dung phân tích chi tiết bản chất của gap sẽ chuyển sang **Mục 2.6 (Related Work)** để tránh trùng lặp.
- **Rút gọn Đóng góp nghiên cứu (Contributions - C1, C2, C3):**
  - *Vấn đề:* Đang sao chép nguyên văn các câu hỏi nghiên cứu (*Research Questions - RQ1, RQ2, RQ3*).
  - *Giải pháp:* Viết lại ngắn gọn, nhấn mạnh vào *giải pháp và kết quả đạt được* nhằm trả lời các RQ tương ứng.
- **Bổ sung Cấu trúc bài báo (Paper Outline):**
  - Bổ sung đoạn kết ngắn gọn cho Section 1: giới thiệu bố cục các phần kế tiếp (*"The remainder of this paper is organized as follows: Section 2 reviews related work..."*).

### 3. Nghiên cứu liên quan (Related Work - Mục 2)
- **So sánh làm nổi bật tính mới với công trình của anh La Trí Tâm (K48) - Hệ thống ViBot:**
  - *Công trình trước:* Kiến trúc nguyên khối (*Monolithic*), tập dữ liệu quy mô cũ.
  - *Công trình của nhóm:* Kiến trúc **Multi-Agent (3 tác tử tự chủ/độc lập)**, cấu trúc mở rộng linh hoạt, tập dữ liệu mới và cập nhật hơn.
  - *Lưu ý:* Phân tích rõ hạn chế của kiến trúc cũ để làm đòn bẩy cho mô hình mới.
- **Bổ sung trích dẫn NLP tiếng Việt:**
  - Bài báo xử lý ngôn ngữ tự nhiên trên văn bản tiếng Việt nhưng thiếu tài liệu nền tảng.
  - Cần bổ sung các trích dẫn tiêu biểu về mô hình ngôn ngữ và tài nguyên NLP tiếng Việt (ví dụ: PhoBERT, ViBERT, PhoGPT, Vietcuna,...).

### 4. Phương pháp & Mô hình đề xuất (Proposed Model - Mục 3)
- **Tối ưu dung lượng:**
  - Cắt giảm Section 3 hiện đang quá dài (~8 trang, từ tiểu mục 3.1 đến 3.9).
  - Bỏ hẳn tiểu mục 3.1 như đã thống nhất.
- **Chuẩn hóa Bảng biểu (Đặc biệt là Table 1):**
  - Font chữ trong bảng hiện quá nhỏ, khó đọc.
  - Xóa bỏ việc lặp từ khóa như *Total*, *Max* ở các hàng. Chỉ để lại giá trị số thuần túy (ví dụ: `6 4 10` thay vì ghi lặp chữ *Total*, ghi `11` cho *Max*).
  - Rà soát toàn bộ các bảng trong bài, điều chỉnh độ rộng và độ tương phản.
- **Làm nổi bật tính mới của LangGraph / StateGraph:**
  - Nhấn mạnh thiết kế kiến trúc: các agent/node hoạt động **hoàn toàn độc lập, tự chủ (autonomous)**, không phụ thuộc cứng hay chuyển tiếp tuần tự dạng dây chuyền đơn giản.
- **Mô tả Giải thuật (Algorithms):**
  - Bổ sung công thức toán học, định nghĩa tham số, trọng số cụ thể (ví dụ: công thức tính toán/truy vấn học phí) ngay bên dưới phần giải thuật.
- **Cấu trúc Cơ sở dữ liệu Neo4j & Query Tools:**
  - Bổ sung sơ đồ Schema đồ thị: số lượng Node, các nhãn Node (2 nhóm văn bản chính: *Chương trình đào tạo* và *Học phí*), các loại Quan hệ (*Relationships*).
  - Mô tả rõ danh mục công cụ (*Query Tools*) mà Agent sử dụng: Graph Tool, Vector Search Tool, hoặc Hybrid Search Tool.

### 5. Thực nghiệm & Thảo luận (Experiments & Discussion - Mục 4 & 5)
- **Định danh Baseline minh bạch:**
  - Làm rõ các phương pháp đối chuẩn (Baseline bên ngoài) thay vì chỉ so sánh nội bộ giữa các biến thể (*ablation study*).
  - Ghi rõ tên và thư viện triển khai (ví dụ: BM25 - thư viện cụ thể, Base Vector Retrieval).
  - *Không cần so sánh độ đo trực tiếp với bài của anh Tâm* do bài toán và metric đánh giá khác nhau hoàn toàn (bài trước: phân loại văn bản / $F_1$-score; bài này: hiệu năng truy xuất tác tử / *Agent retrieval*).
- **Độ tin cậy của Thực nghiệm:**
  - Tuyệt đối không chỉ chạy dataset 150 câu 1 lần duy nhất để lấy kết quả báo cáo.
  - Cần chạy thực nghiệm lặp lại nhiều lần để lấy giá trị trung bình/độ lệch chuẩn hoặc áp dụng phương pháp kiểm chứng chặt chẽ (cross-validation).
- **Phân tích Thảo luận (Discussion):**
  - Không chỉ dừng lại ở việc đọc số liệu từ bảng; cần phân tích sâu ý nghĩa, tính mới và nguyên nhân kỹ thuật.
  - Phân tích sự đánh đổi (*trade-offs*): Lý giải vì sao ở một số khía cạnh/trường hợp cụ thể, cấu hình *without graph* lại cho điểm số cao hơn.
- **Xử lý vấn đề Bias (Gemini 2.5 Flash làm LLM-as-a-Judge):**
  - *Vấn đề:* Dùng Gemini 2.5 Flash đánh giá lại chính câu hỏi do nó sinh ra (do giới hạn credit) tiềm ẩn thiên vị (*evaluator bias*).
  - *Giải pháp:* Chủ động nêu rõ đây là hạn chế (*Limitation*) của nghiên cứu trong bài báo; đưa việc đánh giá chéo bằng các mô hình LLM độc lập khác (GPT-4o, Claude 3.5 Sonnet, Open-source LLMs) vào phần *Future Work*.
- **Loại bỏ cột Độ trễ (Latency):**
  - Hệ thống hiện mất khoảng ~1 phút để phản hồi, độ trễ còn cao.
  - **Xóa bỏ hoàn toàn 2 cột Latency** trong toàn bộ các bảng kết quả để tránh bị reviewer trừ điểm.

### 6. Kết luận & Hướng phát triển (Conclusion & Future Work)
- Viết lại Conclusion chuẩn cấu trúc bài báo khoa học, tách bạch rõ ràng với tóm tắt ở Abstract.
- Bổ sung Future Work: đánh giá đa mô hình LLM để loại bỏ bias và mở rộng tập ngữ liệu đào tạo.

---

## III. KẾ HOẠCH ĐĂNG KÝ HỘI NGHỊ & KINH PHÍ

### 1. Chính sách Phí đăng bài (Registration Fee)
- Giảng viên hướng dẫn sẽ hỗ trợ chi trả toàn bộ lệ phí đăng bài cho nhóm.
- Đăng ký theo gói combo 2 bài: Tổng chi phí khoảng **800 GBP** cho cả 2 bài (tiết kiệm đáng kể so với mức $500–$600 hoặc 500+ GBP/bài đơn lẻ).

### 2. Địa điểm Báo cáo & Lịch trình
- **Địa điểm chốt:** **Phú Quốc** (Nhóm thống nhất chọn để có cơ hội học hỏi và giao lưu học thuật).
- **Thời gian dự kiến:** Thứ Sáu, Thứ Bảy, Chủ Nhật của **Tuần 12**.
- **Xử lý trùng lịch thi:** Nếu Tuần 12 trùng với lịch thi học kỳ (Tuần 11–13), GVHD sẽ trực tiếp làm việc và hỗ trợ xin phép Thầy Hiệp tạo điều kiện hoãn/dời lịch thi cho nhóm.

---

## IV. BẢNG PHÂN CÔNG CÔNG VIỆC & TIẾN ĐỘ THỰC HIỆN

| STT | Nhiệm vụ chi tiết | Người phụ trách | Hạn hoàn thành | Trạng thái |
| :---: | :--- | :---: | :---: | :---: |
| 1 | Cắt gọt bài viết từ 22 trang xuống $\le$ 16 trang; chuẩn hóa văn phong | Cả nhóm | Ngày D+2 | ⏳ Đang làm |
| 2 | Chuyển Mục 3.1 vào Section 1; tách gap sang Mục 2.6; viết lại Contribution | Thành viên A | Ngày D+3 | ⏳ Đang làm |
| 3 | Bổ sung trích dẫn NLP tiếng Việt; làm nổi bật so sánh với ViBot | Thành viên B | Ngày D+3 | ⏳ Đang làm |
| 4 | Bổ sung Neo4j Schema, công thức toán cho Algorithm, chỉnh sửa Table 1 | Thành viên C | Ngày D+4 | ⏳ Đang làm |
| 5 | Chạy lại thực nghiệm lặp nhiều lần; xóa cột Latency; viết lại Discussion & Limitations | Cả nhóm | Ngày D+5 | ⏳ Đang làm |
| 6 | Hoàn thiện Conclusion & Future Work; kiểm tra toàn diện Format trước khi gửi GVHD | Cả nhóm | Ngày D+6 | ⏳ Đang làm |