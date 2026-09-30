# Rà nhãn held-out: số liệu trước/sau để duyệt

Ngày kiểm tra: 2026-09-29. Chưa cập nhật PAPER_V15 hoặc ghi đè bộ dữ liệu và log gốc.

## Nguồn và cách tính

- Nhãn: `data/scenario12_heldout_100.jsonl` (SHA-256 `A1E484D75F089AA8A28B64AB2B49424D8D40B0186ABEB8E3C152EC3C7CE890D5`).
- Câu trả lời cố định: `logs/v13_architecture/run_20260923_155602/results.jsonl` (SHA-256 `28A68220469A68BB6DA0895C6829088995B7EF349DDF7D8F533581A552299C7A`): đủ 100 câu cho mỗi cấu hình trong 7 cấu hình.
- Dùng đúng hàm `compute_fact_coverage`, `bootstrap_ci` (10.000 mẫu, seed 42) và `exact_mcnemar` trong `scripts/recompute_verified_stats.py`. Pass khi tỷ lệ cụm `required_facts` xuất hiện trong câu trả lời đạt ít nhất 0,50.
- **Bản gốc:** 100 nhãn hiện tại. **Thêm đáp số:** thêm `393.000` vào `required_facts` của `HOUT-MHOP-FIN-05`, giữ 100 câu. **Độ nhạy N=99:** cũng loại `HOUT-XDOM-13` do câu hỏi thiếu điều kiện hưởng chính sách. Các thay đổi được tính trong bộ nhớ từ cùng log; không gọi mô hình.

## Tỷ lệ đạt và Fact Coverage

| Cấu hình | Gốc N=100: đạt; FactCov | Thêm `393.000`, N=100: đạt; FactCov | Thêm `393.000` và loại XDOM-13, N=99: đạt; FactCov |
| --- | ---: | ---: | ---: |
| S1-A Single Agent | 66/100 = 66,0%; 57,45% | 66/100 = 66,0%; 57,28% | 66/99 = 66,67%; 57,53% |
| S1-B Routed Generic | 66/100 = 66,0%; 54,18% | 66/100 = 66,0%; 54,02% | 66/99 = 66,67%; 54,23% |
| S1-C CTU-Chat | 76/100 = 76,0%; 61,03% | 76/100 = 76,0%; 60,87% | 76/99 = 76,77%; 61,14% |
| S2-A2 No Tool Isolation | 76/100 = 76,0%; 61,97% | 76/100 = 76,0%; 61,80% | 76/99 = 76,77%; 62,09% |
| S2-A3 Uniform Text-RAG | 67/100 = 67,0%; 58,85% | 67/100 = 67,0%; 58,68% | 67/99 = 67,68%; 58,94% |
| S2-A4 No Deterministic Calculation | 72/100 = 72,0%; 60,10% | 72/100 = 72,0%; 59,93% | 72/99 = 72,73%; 60,54% |
| S2-A5 No Route Repair | 74/100 = 74,0%; 59,77% | 74/100 = 74,0%; 59,60% | 74/99 = 74,75%; 59,87% |

| So sánh CTU-Chat − Single Agent | Gốc N=100 | Thêm đáp số, N=100 | Thêm đáp số + loại XDOM-13, N=99 |
| --- | ---: | ---: | ---: |
| Chênh lệch pass | +10,0 pp | +10,0 pp | +10,10 pp |
| Paired bootstrap 95% CI | [+2,0; +19,0] pp | [+2,0; +19,0] pp | [+1,01; +19,19] pp |
| McNemar exact | b=15, c=5, p=0,0414 | b=15, c=5, p=0,0414 | b=15, c=5, p=0,0414 |
| Chênh lệch FactCov | +3,58 pp | +3,58 pp | +3,62 pp |
| FactCov 95% CI | [−1,22; +8,48] pp | [−1,22; +8,48] pp | [−1,20; +8,59] pp |

Các chênh lệch ablation so với S1-C cũng được tính lại theo cặp. Thêm đáp số FIN-05 không đổi các chênh lệch N=100; khi loại XDOM-13:

| Cấu hình − S1-C | Gốc và thêm đáp số, N=100: Δ pass [95% CI] | Thêm đáp số + loại XDOM-13, N=99: Δ pass [95% CI] |
| --- | ---: | ---: |
| S1-B No Specialist Policy | −10,0 [−19,0; −1,0] pp | −10,10 [−19,19; −1,01] pp |
| S2-A2 No Tool Isolation | 0,0 [−6,0; +6,0] pp | 0,0 [−6,06; +6,06] pp |
| S2-A3 Uniform Text-RAG | −9,0 [−15,0; −4,0] pp | −9,09 [−15,15; −4,04] pp |
| S2-A4 No Deterministic Calculation | −4,0 [−9,0; 0,0] pp | −4,04 [−9,09; 0,0] pp |
| S2-A5 No Route Repair | −2,0 [−7,0; +3,0] pp | −2,02 [−7,07; +3,03] pp |

Ở nhóm liên miền, tỷ lệ gốc của CTU-Chat/Single/Generic là 16/20 (80,0%)/14/20 (70,0%)/13/20 (65,0%). Khi loại XDOM-13, cả ba giữ nguyên tử số: 16/19 (84,21%)/14/19 (73,68%)/13/19 (68,42%). Đây là **phân tích độ nhạy hậu kiểm**, không thay thế kết quả chính N=100.

## Hai ca cần quyết định nhãn

### HOUT-MHOP-FIN-05

Tệp nguồn ghi 844.000 đồng/tín chỉ cho Quản trị kinh doanh K52 và 451.000 đồng/tín chỉ làm cơ sở miễn giảm Khối III; chênh lệch đúng là 393.000 đồng/tín chỉ. Nhãn gốc thiếu đáp số trong `required_facts` dù `reference_answer` có đáp số.

Tất cả 7 câu trả lời trong log cố định đều **không nêu 393.000**. Ba kiến trúc chính đạt 2/3 cụm từ ở nhãn gốc và vẫn đạt 2/4 sau khi thêm đáp số. Vì vậy, phép sửa nhãn này giảm Fact Coverage nhưng **không loại được điểm pass sai** ở ngưỡng 50%. Kiểm tra riêng đáp số cho ca này: **0/7 đúng số**. Muốn pass chính phụ thuộc đáp số, cần quy tắc bắt buộc đáp số áp dụng nhất quán cho mọi câu hỏi tương tự, rồi chấm lại toàn bộ log; không sửa riêng tiêu chí của một ca sau khi thấy kết quả.

Chỉ để thấy độ lớn của lỗi, nếu ép riêng ca này phải có `393.000` (quy tắc hậu kiểm, **không phải metric của bài**), S1-C sẽ là 75/100 và S1-A là 65/100; chênh lệch theo cặp vẫn +10,0 pp vì cả hai cùng mất một điểm.

### HOUT-XDOM-13

Câu hỏi chỉ cho biết sinh viên thuộc hộ cận nghèo, chưa đủ điều kiện xác định tỷ lệ miễn/giảm. Thông báo CTU ngày 14-04-2026 và Nghị định 238/2025/NĐ-CP nêu thêm điều kiện về dân tộc thiểu số đối với diện hộ cận nghèo được miễn học phí; giảm 70% là một diện khác có điều kiện nơi thường trú. Reference hiện tại không trả lời tỷ lệ nhưng `required_facts` vẫn có thể thưởng điểm cho tên ngành và mức cơ sở 451.000. Trong log, cả S1-A, S1-B, S1-C đều trượt ca này (FactCov 1/3). Phân tích N=99 ở trên cho thấy tác động nếu loại ca không xác định được đáp án duy nhất; việc loại hậu kiểm phải được công bố rõ.

Nguồn chính sách: [Thông báo CTU](https://cse.ctu.edu.vn/images/upload/sinhvien/chinhquy/2026/14-4-2026-TB_mghp_hk3_25_26.pdf), [Nghị định 238/2025/NĐ-CP](https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-238-2025-nd-cp-46152/58861.htm).

## Phát hiện thêm khi đối chiếu 9 ca học phí trực tiếp

Chưa tìm thấy danh sách ID và rubric tái lập cho câu PAPER_V15 viết `8/9` CTU-Chat so với `3/9` No Deterministic Calculation. Nếu 9 ca đó là `HOUT-DIR-FIN-01` đến `09`, đối chiếu đáp số trong log cho thấy:

| Rubric đáp số | S1-C | S2-A4 |
| --- | ---: | ---: |
| Theo reference hiện tại | 6/9 | 6/9 |
| Sửa FIN-07/08 theo bảng nguồn nội bộ | 8/9 | 8/9 |

Trong `data/markdown/MucHocPhi_ChatLuongCao_TienTien.md`, hàng K52 ghi Kỹ thuật điều khiển và tự động hóa **41 triệu/năm** và Thú y **41,8 triệu/năm**; reference của FIN-07/08 hiện ghi **44 triệu/năm** cho cả hai. Cả S1-C và S2-A4 trong log đều trả lời 41 và 41,8. FIN-03 là ca còn sai ở cả hai khi đối chiếu với 40 triệu/năm. Do đó, **không được dùng kiểm tra 9 ca trực tiếp này để chứng minh `8/9` so với `3/9`**. Nếu con số bài báo đến từ 9 ca khác, cần cung cấp ID, gold amounts, đáp án từng cấu hình và quy tắc chấm trước khi giữ claim đó.

## Ranh giới sử dụng

- Số N=100 sau thêm đáp số là phép chấm lại theo **cùng định nghĩa lexical hiện hành**; chênh lệch chính giữ nguyên nhưng lỗi pass giả của FIN-05 còn tồn tại.
- Số N=99 là **sensitivity analysis** sau khi phát hiện nhãn không xác định; không thay thế kết quả chính nếu chưa công bố tiêu chí loại và phiên bản dữ liệu.
- PAPER_V15, dataset gốc và log chưa được sửa trong lượt này để người viết duyệt số liệu trước.
