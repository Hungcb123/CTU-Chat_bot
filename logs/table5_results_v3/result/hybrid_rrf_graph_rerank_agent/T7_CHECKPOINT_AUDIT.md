# Kiểm tra Answer Correctness của T7

Nguồn đối chiếu:

- T6: `checkpoints/hybrid_rrf_graph_rerank/checkpoint.json`
- T7: `checkpoints/hybrid_rrf_graph_rerank_agent/checkpoint.json`
- Dataset: `data/dataset/100.csv`

## Tổng quan

| Chỉ báo | Số câu |
|---|---:|
| Tổng số câu | 100 |
| T7 Answer Correctness dưới 0.5 | 61 |
| T7 Answer Correctness dưới 0.4 | 35 |
| T7 giảm trên 0.3 so với T6 | 50 |
| T7 cải thiện so với T6 | 14 |
| T7 dài hơn T6 trên 5 lần | 58 |

Độ dài câu trả lời trung bình tăng từ 176 ký tự ở T6 lên 787 ký tự ở T7.
Context Recall và Context Precision của T6/T7 giống nhau, nên phần giảm chủ yếu
đến từ cách Agent viết câu trả lời, không phải thay đổi evidence.

## Nhóm giảm theo category

| Category | Số câu | T6 | T7 | Mức giảm | Tỷ lệ độ dài T7/T6 |
|---|---:|---:|---:|---:|---:|
| exemption_basis | 5 | 0.92 | 0.39 | 0.53 | 7.3x |
| actual_tuition | 14 | 0.91 | 0.45 | 0.46 | 6.5x |
| scholarship | 14 | 0.89 | 0.48 | 0.41 | 5.8x |
| exemption_policy | 9 | 0.75 | 0.39 | 0.36 | 6.2x |
| student_loan | 12 | 0.79 | 0.48 | 0.31 | 5.6x |
| social_support | 11 | 0.71 | 0.44 | 0.27 | 5.0x |
| other | 12 | 0.77 | 0.65 | 0.12 | 4.6x |
| academic_rules | 14 | 0.50 | 0.49 | 0.01 | 3.5x |
| academic_program | 9 | 0.58 | 0.59 | -0.01 | 1.7x |

## 30 câu lỗi/hạn chế riêng của T7

Tiêu chí: T6 có Answer Correctness từ 0.8 trở lên nhưng T7 dưới 0.5.

`5, 6, 7, 86, 14, 13, 11, 37, 10, 35, 33, 53, 17, 79, 76, 77, 31, 32, 34, 39, 87, 29, 36, 28, 30, 84, 20, Q003, R18, 24`

Các trường hợp giảm mạnh nhất:

| Case | Category | T6 | T7 | Hiện tượng chính |
|---|---|---:|---:|---|
| 5 | exemption_policy | 0.97 | 0.34 | Đáp án đúng 50% nhưng thêm hồ sơ, ngoại lệ và tư vấn ngoài câu hỏi |
| 6 | exemption_policy | 0.99 | 0.37 | Đáp án đúng “không” nhưng thêm nhiều trường hợp loại trừ |
| 7 | exemption_policy | 0.96 | 0.36 | Đáp án đúng “hưởng mức cao nhất” nhưng mở rộng thêm nhiều quy tắc |
| 86 | scholarship | 0.96 | 0.36 | Đúng GPA 2.5 nhưng thêm thu nhập, cam kết và hồ sơ |
| 14 | exemption_basis | 0.97 | 0.39 | Đúng 335.000 đồng/tín chỉ nhưng thêm giải thích và đề nghị tính toán |
| 13 | exemption_basis | 0.97 | 0.39 | Đúng 753.000 đồng/tín chỉ nhưng thêm thông tin không được hỏi |
| 11 | exemption_basis | 0.97 | 0.39 | Đúng 451.000 đồng/tín chỉ nhưng câu trả lời dài hơn Ground Truth nhiều lần |
| 37 | actual_tuition | 0.96 | 0.38 | Câu hỏi một con số nhưng Agent tạo câu trả lời nhiều đoạn |
| 10 | exemption_basis | 0.96 | 0.39 | Câu hỏi một mức phí nhưng Agent mở rộng ngữ cảnh |
| 35 | actual_tuition | 0.97 | 0.41 | Đúng dữ kiện chính nhưng thêm diễn giải ngoài Ground Truth |

## 16 câu T6 đã thấp từ trước

Các case này có T6 dưới 0.5, nên cần kiểm tra Ground Truth, evidence và retrieval
trước khi đánh giá lỗi Agent:

`26, Q032, Q034, Q050, Q076, R12, R15, R21, R22, R17, 54, 22, R04, Q005, Q009, 9`

Ví dụ case `26`: Ground Truth là 695.000 đồng/tín chỉ, trong khi evidence Graph
được checkpoint có nhiều mức theo khóa và T6 cũng chỉ đạt khoảng 0.20. Đây không
phải lỗi chỉ xuất hiện ở T7.

## 14 câu T7 cải thiện

`Q009, R23, R22, R09, R06, R01, Q076, R14, R21, Q005, Q032, Q034, Q001, R15`

T7 cải thiện rõ ở một số câu cần tổng hợp hoặc giải thích nhiều bước, chẳng hạn
`Q009` tăng từ 0.17 lên 0.74 và `R23` tăng từ 0.57 lên 0.82.

## Hướng sửa T7

1. Chỉ đưa evidence T6 vào prompt một lần.
2. Dùng prompt benchmark riêng: trả lời trực tiếp, không chào hỏi, không tư vấn
   thêm và không nêu chi tiết không được hỏi.
3. Không đưa mô tả tool vào prompt fixed-evidence vì T7 không được gọi tool.
4. Giữ supervisor routing để đo Agent orchestration.
5. Sau khi sửa, xóa hoặc đổi tên riêng checkpoint T7 cũ và chạy lại đủ 100 câu;
   giữ checkpoint hiện tại làm kết quả đối chứng của phiên bản prompt cũ.
