# Rà soát dữ liệu và thực nghiệm cho bản Rev3

## Kết quả thực hiện

Đã dựng bản v2 đủ 150 câu, bảo toàn CSV gốc và các thay đổi có sẵn trong repo. 129 câu thay đổi ít nhất một trường, tổng 246 thay đổi trường; số lượng này gồm chuẩn hóa đáp án, không phải 129 lỗi sự thật. Đã kiểm tra 300 lượt truy xuất BM25 offline trên hai phiên bản và 18 phép nhân học phí trong đáp án. Các phép nhân đều nhất quán về số học; kiểm tra này không xác minh học phần thực tế thuộc nhóm đơn giá nào.

Kết quả chi tiết nằm trong `offline_bm25_report.md`, `offline_bm25_results.json`, `offline_bm25_rankings.jsonl` và `arithmetic_checks.json`. Đây là BM25 trên toàn văn Markdown local, không phải E1 production. Không dùng mức thay đổi trước/sau để khẳng định hệ thống cải thiện vì cả câu hỏi và nhãn đã thay đổi.

## Các lỗi dữ liệu có bằng chứng

| Vị trí | Vấn đề | Xử lý v2 |
|---|---|---|
| ID 26 | Hỏi CNTT K49 không chỉ rõ hệ; đáp án có cả chuẩn và CLC nhưng nguồn chỉ có quy định chung | Hỏi rõ cả hai hệ, thêm nguồn CLC, dùng all_required |
| ID 27 | Câu chỉ hỏi giá đại cương K52 nhưng yêu cầu cả hai nguồn | Giữ nguồn bảng K52 có trực tiếp mức 695.000; dùng single |
| ID 28 | Câu chỉ hỏi hệ số nhưng yêu cầu cả bảng giá | Giữ quy định chung, làm rõ chương trình chuẩn và ngành thứ nhất |
| ID 30/31/33/38/39 | Giá theo ngành bị diễn đạt như giá của mọi tín chỉ | Chỉ rõ chương trình chuẩn và khối học phần |
| ID 10–14 | Thiếu năm cho cơ sở tính miễn giảm | Ghi 2025–2026, tách khỏi giá thực thu 2026–2027 |
| ID 51–55 | Chính sách mua máy tính năm 2022 được hỏi như dịch vụ hiện tại | Ghi rõ phạm vi lịch sử |
| ID 81 | Mức học bổng CLC K51 có điều kiện hiệu lực học kỳ 2 | Bổ sung học kỳ 2 năm học 2025–2026 |
| CDICT001–022/031–046 | CTĐT theo QĐ 3922 năm 2025 bị gắn với nhiều cohort mà không có bằng chứng áp dụng | Đặt giả định đối chiếu; đánh dấu synthetic stress |
| CDICT037–040 | Đơn giá 1.254/1.438/1.308/1.366 thiếu đơn vị nghìn đồng | Chuẩn hóa thành đồng/tín chỉ theo bảng hiện có |
| CDICT041–046 | Hỏi độ chênh nhưng đáp án chỉ nêu 161 và 168 | Thêm chênh lệch 7 tín chỉ |
| Q023, CDICT047–050 | Thời hạn 9 năm chưa nêu ngoại lệ giảm do công nhận/chuyển đổi tín chỉ | Thêm giả định không có tín chỉ làm giảm thời hạn |
| Các câu Q về CTĐT | Đáp án chứa lời chào, vai trò chatbot, link giao diện | Bỏ phần trình bày khỏi đáp án tham chiếu, lưu bản gốc riêng |

Chưa xác nhận tính đúng của toàn bộ đáp án kế thừa. Đặc biệt còn 20 câu chính sách cần kiểm tra phạm vi hiệu lực; nguồn Panasonic có tiêu đề năm 2025 nhưng nội dung thông báo năm 2026; hai hàng any_valid cần kiểm tra độc lập từng nguồn. Corpus có nhiều đoạn “thường được tra cứu” giống câu hỏi đánh giá; manifest đóng băng trạng thái đang có, chưa chứng minh corpus chưa bị sửa dựa trên benchmark. Cần so với tài liệu nguồn chính thức trước khi công bố.

## Các lỗi thực nghiệm phải sửa trước Table 3/4

Đối chiếu trực tiếp `scripts/benchmark_table4_e2e.py` và PDF Rev3:

1. `retrieve_all_configs` đặt T7 bằng dense context của T2. Vì vậy kết quả T2/T7 giống nhau, không phải ablation Governance. T7 đúng phải giữ Hybrid, reranker và graph như T4, chỉ tắt Governance.
2. T5 hiện bỏ cả reranker lẫn graph so với T4. Ablation reranker phải giữ graph. T4 chèn mô tả CTĐT ngắn, không gọi toàn bộ workflow agent hay công cụ tính; không đủ cơ sở gọi là full multi-agent E2E.
3. Graph chỉ được kích hoạt theo `case.category == academic_program`, dùng nhãn đánh giá để định tuyến và bỏ qua câu ghép được gắn actual_tuition. Định tuyến phải dựa trên câu hỏi, không nhận category/gold của bộ test.
4. CR hiện là giao token của ground truth với context; CP dùng ngưỡng ROUGE/token overlap rồi chia cho số hit đã tìm được. Đây không phải đánh giá bằng gold source, cũng không phải chạy RAGAS. Chỉ một hit ở rank 1 có thể cho CP=1 dù thiếu các bằng chứng khác.
5. AC là trung bình ROUGE-L recall và cosine, AR là tỷ số cosine question/answer với question/GT. Chúng là proxy, chưa đo chính xác sự thật về cohort, giá hay thời gian và không chứng minh đã chạy RAGAS.
6. Sample chọn các hàng đầu của mỗi category; không phải lấy mẫu ngẫu nhiên phân tầng. Checkpoint dùng ID mà không khóa theo hash câu hỏi, corpus, model, prompt hay config; sửa dữ liệu mà dùng checkpoint cũ sẽ trộn thực nghiệm.
7. Khi API thất bại nhiều lần, script trả câu từ chối như một câu trả lời bình thường. Cần lưu trạng thái lỗi, không chấm lỗi dịch vụ như hành vi QA. Reranker/graph thiếu cũng không được âm thầm đổi cấu hình.
8. Kế hoạch 25 câu × 7 cấu hình cần tối đa 175 lần sinh, chưa gồm judge và retry; trần 110 không bảo đảm. Chỉ tái sử dụng khi toàn bộ model/settings/prompt/context giống nhau và ghi rõ cache hit.

PDF còn ghi 100 câu trong khi CSV có 150; abstract dùng M0–M4 còn phần thực nghiệm dùng E1–E5/T1–T7. Table 4 trong PDF ghi T6 AC=0.752 cao hơn T4=0.751: không thể mô tả T4 có AC cao nhất. Các H@1 ở Table 3 gần các phân số mẫu 9 câu; đây là dấu hiệu cần truy nguồn số liệu, chưa đủ để kết luận bảng thực sự dùng n=9.

## Thiết kế đánh giá thay thế

Đóng băng dữ liệu đã được kiểm duyệt và corpus trước khi chạy; tạo holdout mới theo nhóm tình huống. Dùng `core_100` và `synthetic_stress_50` để phát triển, báo cáo hai phần riêng. Giữ lại câu có mã môn/tên ngành hợp lý: BM25 mạnh không tự nó chứng minh dataset sai.

Table 3 ghi rõ E1 lexical, E2 dense, E3 hybrid, E4 hybrid+reranker; E5 là phần mở rộng có nhiều thành phần nên không diễn giải chênh lệch E4/E5 là đóng góp riêng của graph. Lưu top-10 doc ID cùng provenance, điểm, thời gian và trạng thái cho từng câu. Đo Source P@5, Source R@5, MRR@10; thêm Evidence Sufficiency@5 (all_required cần đủ mọi nguồn; any_valid chỉ cần một nguồn hợp lệ). Đánh giá đoạn bằng chứng riêng vì một file đúng chưa chắc chứa đoạn đúng.

Table 4 giữ các cấu hình ablation chỉ khác đúng một thành phần. Chạy cùng danh sách câu và cùng thiết lập generator; lưu toàn bộ prompt/context/model/config hashes và câu trả lời. Nếu chỉ chạy document IR, đặt tên chỉ số rõ như Source Recall/MAP, không đổi tên thành RAGAS CR/CP. Nếu cần giữ RAGAS, phải thực sự chạy evaluator tương ứng và ghi phiên bản, judge, embedding model, language và lỗi; đối chiếu thủ công một mẫu có con số, cohort, đơn vị và ngoại lệ.

Chọn sample bằng seed cố định trước khi sinh đáp án, công bố ID và tỷ trọng; tính trung bình theo câu và theo category. Dùng paired bootstrap theo family khi báo cáo độ bất định của câu theo mẫu. Không đặt điều kiện T4 phải thắng, T7 phải giảm hay E2<E3<E1<E4<E5. Kết luận đi theo số liệu thực tế, kể cả khi một thành phần không có lợi.

## Môi trường và giới hạn chạy

Đã kiểm tra ngoài sandbox: GPU GTX 1650 4 GB; các cổng local Qdrant 6333, Neo4j 7687, PostgreSQL 5432 và Redis 6379 nhận TCP. Đây chỉ là preflight, chưa xác nhận credentials, nội dung index, inference CUDA hay pipeline hoạt động. Môi trường `wsl_venv` báo Python 3.10.12, khác Python 3.12 trong PDF; cần ghi môi trường thực sự dùng cho lần chạy chính thức.

GitNexus CLI query không có kết quả và báo FTS không ghi được vào DB read-only. Impact cho `retrieve_all_configs` trả Target not found, risk UNKNOWN; chưa xác định được direct callers/affected processes. Không sửa hàm ứng dụng hay benchmark cũ; các công cụ mới chạy độc lập. Không commit. Chưa chạy lại E1–E5/T1–T7 hoặc tạo số liệu RAGAS mới: chạy nguyên các script đang có sẽ không giải quyết các lỗi đối chứng/đo lường nêu trên.

## Đoạn phương pháp có thể dùng làm bản nháp

“We constructed a revised development benchmark comprising 100 core questions and 50 synthetic cross-document stress cases. Revisions make temporal scope and assumptions explicit and separate reference answers from source excerpts. Source-level retrieval metrics are complemented by evidence sufficiency, which requires all annotated sources for conjunctive questions and at least one valid source for alternative-source questions. Synthetic families are reported separately to avoid treating templated variants as independent natural user queries. Independent human verification and evaluation on an unseen test set remain to be completed.”

Đoạn này mô tả đúng phần đã làm; chưa dùng các bảng cũ để thêm tuyên bố cải thiện hay human-verified.
