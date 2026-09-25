# Audit PAPER_V14

Ngày kiểm tra: 2026-09-25  
Phạm vi: `data/PAPER_V14`, bộ câu hỏi held-out và log thí nghiệm liên quan.  
Phương pháp: đọc skill trong `.agents/skills`, chạy `lncs-layout-checker` ở chế độ chỉ đọc, đối chiếu bản thảo với dữ liệu và bản rà soát câu hỏi. Không chỉnh sửa dữ liệu hoặc kết quả thí nghiệm.

## Kết luận

**Chưa nên dùng các bảng kết quả hiện tại để nộp bài.** Dữ liệu chuẩn của benchmark có các mục không khớp bản rà soát; cần xác minh nhãn và tính lại chỉ số trước khi chốt các claim định lượng.

## Phát hiện theo mức ưu tiên

### 1. Nghiêm trọng — nhãn benchmark không khớp bản rà soát

Đối chiếu 100 mục trong `data/scenario12_heldout_100.jsonl` với `data/scenario12_heldout_100_review.md` cho thấy **27 `reference_answer` khác nhau**, trong đó **26 mục cũng khác `required_facts`**. Sự khác biệt cần được duyệt từng mục; phép so sánh văn bản không tự phân biệt sửa câu chữ với sai nội dung.

Hai mục có lỗi nội dung rõ ràng:

| ID | Câu hỏi hỏi về | Đáp án/facts trong JSONL | Bản rà soát |
|---|---|---|---|
| `HOUT-DIR-FIN-07` | Học phí Kỹ thuật điều khiển và tự động hóa CLC K52 | Công nghệ thực phẩm hệ chuẩn, 1.016.000 đồng/tín chỉ | Kỹ thuật điều khiển và tự động hóa CLC K52, 44.000.000 đồng/năm |
| `HOUT-DIR-FIN-08` | Học phí Thú y CLC K52 | Kỹ thuật điện hệ chuẩn, 1.016.000 đồng/tín chỉ | Thú y CLC K52, 44 triệu đồng/năm |

Nguồn: `data/scenario12_heldout_100.jsonl` dòng 17–18; `data/scenario12_heldout_100_review.md` mục 017–018. Log `logs/v13_architecture/run_20260923_155602/results.jsonl` chứa các `reference_answer` sai này, nên ít nhất lượt chạy đó đã dùng nhãn không khớp câu hỏi.

**Cần làm:** đối chiếu cả 27 mục với chứng cứ gốc, sửa bản dữ liệu chuẩn, sau đó chạy lại việc chấm điểm và cập nhật các bảng/CI/claim chịu ảnh hưởng. Không thay riêng số liệu trong bản thảo trước khi có kết quả tính lại.

### 2. Cao — trạng thái duyệt dữ liệu chưa đáp ứng quy tắc của bản thảo

Cả 100 mục trong `data/scenario12_heldout_100.jsonl` có `review_status=approved`. Trong khi đó, `data/PAPER_V14/README.md` dòng 35 quy định bảng chính chỉ dùng câu hỏi có `review_status=verified`.

**Cần làm:** hoàn tất kiểm chứng theo quy trình thực tế và chỉ đổi trạng thái những mục đã được xác nhận. Sau đó tạo lại bảng chính từ tập hợp đủ điều kiện.

### 3. Trung bình — nhận định về độ nhạy ngưỡng vượt quá số liệu

`data/PAPER_V14/sections/05-results.tex` dòng 34 viết rằng kiểm tra độ nhạy “confirms stability” và lợi thế quan sát được “is not an artifact of threshold selection”. Tuy nhiên, tại ngưỡng 0,75, CTU-Chat đạt 39% so với Single Agent 41%; tại ngưỡng 1,00 là 32% so với 33%. Lợi thế điểm ước lượng chỉ xuất hiện ở các ngưỡng 0,50 và 0,60 được liệt kê.

**Cần làm:** sau khi tính lại từ benchmark đã xác minh, báo cáo diễn biến theo từng ngưỡng và giới hạn kết luận theo kết quả thực tế.

### 4. Thấp — sơ đồ kiến trúc ở định dạng raster

`lncs-layout-checker` báo hình `data/PAPER_V14/figures/architecture.jpg` là JPG; skill khuyến nghị PDF/EPS vector cho sơ đồ đường nét. Đây là cảnh báo chất lượng trình bày, không phải lỗi kiểm tra định dạng.

**Cần làm:** nếu còn nguồn sơ đồ, xuất trực tiếp sang PDF/EPS vector rồi kiểm tra lại khả năng đọc ở kích thước in.

## Kết quả kiểm tra LNCS/PDF

- Bộ `lncs-layout-checker/scripts/check_lncs.py` trả về **22 PASS, 0 FAIL, 1 WARN** với giới hạn mặc định 16 trang.
- `main.pdf` có **15 trang**.
- Kiểm tra tài nguyên font trong PDF bằng `pypdf` thấy `/Type0` và `/Type1`, **không thấy `/Type3`**.
- Bản kiểm tra này chưa xác minh độc lập tính chính xác của từng tài liệu tham khảo hoặc toàn bộ số liệu thí nghiệm khác.

## Thứ tự xử lý đề nghị

1. Xác minh 27 mục khác bản rà soát, ưu tiên hai mục `HOUT-DIR-FIN-07/08`.
2. Áp dụng trạng thái `verified` theo đúng quy trình, rồi chấm điểm/tính thống kê lại.
3. Đồng bộ bảng, Abstract, Results, Discussion và Conclusion với số liệu mới; sửa nhận định về ngưỡng.
4. Xuất sơ đồ vector nếu có nguồn, biên dịch PDF và chạy lại bộ kiểm tra LNCS.

## Rà claim theo `rule paper/guild_writting.md`

Ngày cập nhật: 2026-09-25. Đối chiếu theo nguyên tắc của hướng dẫn: Abstract/Conclusion không vượt quá bằng chứng ở Results; Results ưu tiên số đo trực tiếp; Discussion tách quan sát khỏi giả thuyết cơ chế. Những chỉnh sửa bên dưới chỉ thay cách diễn đạt, **không xác nhận lại số liệu**. Vấn đề nhãn benchmark ở mục 1–2 vẫn phải được giải quyết trước khi nộp bài.

| Vị trí | Vấn đề | Đã chỉnh |
|---|---|---|
| `sections/00-abstract.tex` | “has not been directly evaluated in prior work” bao quát quá mức; “preserves” hàm ý ổn định. | Dùng “remains underexplored” và mô tả điểm đo 88.0% tại 51 tools. |
| `sections/04-experiments.tex` và `sections/05-results.tex` | “attributable purely” / “stem entirely” quy kết nguyên nhân cho từng yếu tố dù Scenario 1 thay đổi nhiều yếu tố cùng lúc. | Nêu đây là tương quan với **nhóm thay đổi orchestration**; Scenario 1 không tách tác động riêng của từng yếu tố. |
| `sections/05-results.tex` | “routing without policy specialization is insufficient” khi CI so với Single Agent chứa 0. | Giữ chênh lệch điểm và CI, bỏ kết luận tổng quát. |
| `sections/05-results.tex` | “confirms stability” và “not an artifact of threshold selection” không khớp các ngưỡng 0.75/1.00. | Báo cáo rõ CTU-Chat cao hơn ở 0.50/0.60 và Single Agent cao hơn nhẹ ở 0.75/1.00. |
| `sections/05-results.tex` | Đoạn retrieval gán nguyên nhân cho từng thành phần; “confirms”, “overcomes” vượt số liệu. | Giữ các số đo trực tiếp và nêu không thể quy riêng chênh lệch của cấu hình đầy đủ cho một thành phần. |
| `sections/05-results.tex` | Kết luận “retrieval quality is an orthogonal bottleneck” từ đếm lỗi nhỏ. | Chỉ báo cáo số đếm lỗi quan sát được. |
| `sections/06-discussion.tex` | “demonstrates”, “requires”, “confirm”, “preserves” và diễn giải cơ chế chắc chắn. | Dùng ngôn ngữ giới hạn theo benchmark; tách chênh lệch điểm khỏi kết luận về độ dốc suy giảm. |
| `sections/06-discussion.tex` | Gọi 10,652 và 5,159 ms là “median” dù các giá trị này khớp trung bình từ log `run_20260923_155602`. | Đổi thành “mean latency”. |
| `sections/07-conclusion.tex` | Kết luận RQ1 nói “achieves higher” nhưng CI chạm 0 và McNemar p=0.096; RQ2 gọi hai thành phần là “most impactful” trên các thước đo khác nhau. | Ghi “higher point estimate” cùng giới hạn thống kê; mô tả từng ablation theo đúng thước đo. |

Trong lần biên dịch lại, `sections/05-results.tex` còn dùng `\FloatBarrier` nhưng bản thảo không nạp gói định nghĩa lệnh. Đã bỏ lệnh ở ranh giới giữa hai mục Results; không thay đổi bảng hoặc số liệu.

**Kiểm tra sau chỉnh sửa:** `tectonic.exe main.tex --keep-logs` hoàn tất và tạo lại `main.pdf` (15 trang). Bộ kiểm tra LNCS vẫn báo **22 PASS, 0 FAIL, 1 WARN**; Abstract 244 từ; cảnh báo còn lại là sơ đồ JPG. Kiểm tra font của PDF mới thấy `/Type0` và `/Type1`, không thấy `/Type3`. Bản biên dịch vẫn ghi một số cảnh báo `Overfull \hbox`; chưa xử lý dàn trang chi tiết trong lượt chỉnh claim này.

**Còn cần kiểm tra sau khi sửa benchmark:** toàn bộ phần trăm, khoảng tin cậy, p-value, so sánh ngưỡng và các câu định lượng trong Abstract/Conclusion. Việc làm mềm claim không thay thế cho tính lại kết quả từ nhãn đã xác minh.
