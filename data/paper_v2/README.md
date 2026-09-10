# Bộ dữ liệu phát triển v2

Đây là bản sửa có truy vết của `data/150_NATURAL_NO_APPENDIX.csv`, phục vụ cải thiện thiết kế đánh giá. **Chưa phải tập test độc lập hoặc bộ dữ liệu đã được người kiểm duyệt xác nhận.** Không dùng tên file “NATURAL” để khẳng định câu hỏi là log người dùng thật.

- `150_revised.csv`: đủ 150 ID, giữ schema cũ để kiểm tra tương thích. `Ground Truth` là đáp án tham chiếu ngắn gọn; `Answer` là alias cho công cụ cũ, không phải câu trả lời của mô hình.
- `core_100.csv`: 100 câu không mang tiền tố CDICT; “core” không có nghĩa là được lấy từ người dùng thật hay được xác minh.
- `synthetic_stress_50.csv`: 50 câu CDICT, báo cáo riêng theo sáu nhóm mẫu trong `family_id`. Không coi 50 biến thể là 50 tình huống độc lập.
- `records.jsonl`: bản ưu tiên cho công cụ mới; giữ câu hỏi, đáp án và trích dẫn gốc, nguồn và SHA-256, phạm vi áp dụng, nhóm mẫu, trạng thái kiểm duyệt.
- `corrections.json`, `change_log.json`: sửa có chủ đích và toàn bộ thay đổi trước/sau. Các chỉnh sửa quy tắc nằm trong script dựng dữ liệu.
- `manifest.json`: dấu vân tay dữ liệu/corpus, số lượng, cờ cần rà soát. `has_ground_truth=True` chỉ biểu thị có văn bản tham chiếu, không chứng nhận văn bản đó đúng.
- `review_queue.csv`: hàng đợi kiểm duyệt với cột reviewer và ghi chú trống. Điền sau khi đối chiếu cả câu hỏi, đáp án, phiên bản và đoạn bằng chứng.

Chạy lại từ thư mục gốc:

```bash
python3 scripts/prepare_paper_dataset_v2.py
python3 scripts/audit_paper_retrieval_v2.py
```

Script chuẩn bị sẽ dựng lại các file CSV/JSON do nó quản lý từ dữ liệu gốc và corrections; không sửa corpus hoặc CSV gốc. Hàng đợi kiểm duyệt là file làm việc riêng, không bị script chuẩn bị ghi đè. Nếu thay đổi dữ liệu sau kiểm duyệt, phải đối chiếu lại hàng đợi theo ID và manifest.

`single`: một nguồn đủ trả lời. `all_required`: cần toàn bộ các nguồn để trả lời đầy đủ. `any_valid`: bất kỳ một nguồn trong danh sách đều đủ; phải kiểm chứng riêng từng nguồn. Retrieval trên tên file chỉ đo được mức tài liệu, chưa chứng minh đúng đoạn, đúng con số hoặc đúng cohort.

Các câu ghép CTĐT 2025 và học phí của khóa cũ được ghi rõ là giả định đối chiếu. Muốn dùng chúng làm tình huống sinh viên thật, cần tài liệu CTĐT đúng khóa; không được bỏ phần giả định mà giữ nguyên nhãn. Các câu chính sách cũ là QA trên snapshot, không xác nhận chính sách đang còn hiệu lực tại thời điểm sử dụng.

Tất cả 150 câu hiện thuộc development vì đã dùng để kiểm tra và sửa. Tạo test mới, tách theo nhóm mẫu trước khi tối ưu hệ thống; không đổi nhãn các câu đã xem thành test. Báo cáo cả trung bình theo câu, theo loại và riêng stress; không thay đổi tỷ trọng để chọn cấu hình thắng.
