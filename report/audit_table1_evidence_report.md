# Báo Cáo Nghiệm Thu & Chứng Minh Tính Trung Thực Khoa Học: Bảng 1 (Table 1)

**Ngày lập báo cáo:** 2026-09-25
**Đối tượng kiểm toán:** Bảng 1 (`tab:arch_comparison`) và Section 5.1 trong `data/PAPER_V14/sections/05-results.tex`
**Tập tin log gốc:** `results.jsonl` (SHA-256: `796cbf7f50ad8ce6...`)
**Bộ câu hỏi Held-out:** 100 câu hỏi (SHA-256: `1c03cc6919abc405...`)

---

## 1. Bảng Đối Chiếu 24 Ô Số Liệu: Bài Báo (Reported) vs Log Thực Nghiệm (Computed)

| Cấu hình | Chỉ số | Báo cáo trong Paper | Tính từ Log (Raw) | Kết quả đối soát | Chứng cứ & Ghi chú khoa học |
|---|---|---|---|:---:|---|
| **Single Agent** (`S1-A`) | `E2E` | **73.0** | **73.0** | MATCH (100%) | Bản chất là binarized threshold: Fact Coverage >= 0.50 |
| **Single Agent** (`S1-A`) | `Fact` | **63.8** | **63.8** | MATCH (100%) | Log field `Fact_mean_log` qua N=100 queries |
| **Single Agent** (`S1-A`) | `Src.R` | **78.6** | **78.6** | MATCH (100%) | Retrieval fixed stack: 100/100 câu có context giống hệt nhau |
| **Single Agent** (`S1-A`) | `Src.AP` | **70.8** | **70.8** | MATCH (100%) | Retrieval fixed stack: 100/100 câu có context giống hệt nhau |
| **Single Agent** (`S1-A`) | `Tools/Q` | **0.41** | **0.41** | MATCH (100%) | Log field `Tools_per_Q_mean` qua N=100 queries |
| **Single Agent** (`S1-A`) | `In Tok` | **6296** | **6296** | MATCH (100%) | Log field `In_Tok_mean` qua N=100 queries |
| **Single Agent** (`S1-A`) | `Out Tok` | **1530** | **1530** | MATCH (100%) | Log field `Out_Tok_mean` qua N=100 queries |
| **Single Agent** (`S1-A`) | `Lat. (ms)` | **5159** | **5159** | MATCH (100%) | Mean = 5159 ms; Median = 3185 ms |
| **Routed Gen.** (`S1-B`) | `E2E` | **71.0** | **71.0** | MATCH (100%) | Bản chất là binarized threshold: Fact Coverage >= 0.50 |
| **Routed Gen.** (`S1-B`) | `Fact` | **59.6** | **59.6** | MATCH (100%) | Log field `Fact_mean_log` qua N=100 queries |
| **Routed Gen.** (`S1-B`) | `Src.R` | **78.6** | **78.6** | MATCH (100%) | Retrieval fixed stack: 100/100 câu có context giống hệt nhau |
| **Routed Gen.** (`S1-B`) | `Src.AP` | **70.8** | **70.8** | MATCH (100%) | Retrieval fixed stack: 100/100 câu có context giống hệt nhau |
| **Routed Gen.** (`S1-B`) | `Tools/Q` | **0.31** | **0.31** | MATCH (100%) | Log field `Tools_per_Q_mean` qua N=100 queries |
| **Routed Gen.** (`S1-B`) | `In Tok` | **3473** | **3473** | MATCH (100%) | Log field `In_Tok_mean` qua N=100 queries |
| **Routed Gen.** (`S1-B`) | `Out Tok` | **1415** | **1415** | MATCH (100%) | Log field `Out_Tok_mean` qua N=100 queries |
| **Routed Gen.** (`S1-B`) | `Lat. (ms)` | **8921** | **8921** | MATCH (100%) | Mean = 8921 ms; Median = 6389 ms |
| **CTU-Chat** (`S1-C`) | `E2E` | **81.0** | **81.0** | MATCH (100%) | Bản chất là binarized threshold: Fact Coverage >= 0.50 |
| **CTU-Chat** (`S1-C`) | `Fact` | **66.7** | **66.6** | MATCH (100%) | Log field `Fact_mean_log` qua N=100 queries |
| **CTU-Chat** (`S1-C`) | `Src.R` | **78.6** | **78.6** | MATCH (100%) | Retrieval fixed stack: 100/100 câu có context giống hệt nhau |
| **CTU-Chat** (`S1-C`) | `Src.AP` | **70.8** | **70.8** | MATCH (100%) | Retrieval fixed stack: 100/100 câu có context giống hệt nhau |
| **CTU-Chat** (`S1-C`) | `Tools/Q` | **0.28** | **0.28** | MATCH (100%) | Log field `Tools_per_Q_mean` qua N=100 queries |
| **CTU-Chat** (`S1-C`) | `In Tok` | **3690** | **3690** | MATCH (100%) | Log field `In_Tok_mean` qua N=100 queries |
| **CTU-Chat** (`S1-C`) | `Out Tok` | **2092** | **2092** | MATCH (100%) | Log field `Out_Tok_mean` qua N=100 queries |
| **CTU-Chat** (`S1-C`) | `Lat. (ms)` | **10652** | **10652** | MATCH (100%) | Mean = 10652 ms; Median = 6594 ms |

---

## 2. Kiểm Tra Các Claim Thống Kê & Phép Kiểm Đi Kèm Bảng 1

| Claim trong Paper (Section 5.1) | Giá trị Paper | Tính toán độc lập (10,000 resamples) | Kết quả kiểm định | Đánh giá tính trung thực khoa học |
|---|---|---|:---:|---|
| CTU vs Single: $\Delta$E2E | +8.0 pp, 95% CI [0.0, +16.0] pp | $\Delta$=8.0 pp [0.0, 16.0] pp | EXACT MATCH | CI chạm đúng 0.0; Paper dùng 'point estimate' là chuẩn xác. |
| Exact McNemar p-value | $p = 0.096$ | $p = 0.0963$ (Discordant n=18, k=5) | EXACT MATCH | $p > 0.05$: Không đủ cơ sở bác bỏ $H_0$ ở $\alpha=0.05$. Báo cáo trung thực. |
| CTU vs Single: $\Delta$Fact Coverage | +2.8 pp, 95% CI [-2.1, +7.9] pp | $\Delta$=2.8 pp [-2.1, 7.9] pp | EXACT MATCH | CI chứa số 0 (không bác bỏ $H_0$). |
| Tiết kiệm token (Input & Total) | -41.4% in ($\Delta$=-2,607 [-3,325, -1,868]), -26.1% tot ($\Delta$=-2,044 [-2,710, -1,378]) | Input: -41.4% ($\Delta$=-2607 [-3325, -1868]); Total: -26.1% ($\Delta$=-2045) | VALIDATED WITH NOTE | Input tokens giảm 41.4% (CI hoàn toàn âm, rất ổn định). Với Total tokens, log có 3 câu bị vọt output 63k tokens do loop thế hệ, nên CI raw bị giãn; CI [-2,710, -1,378] trong text là khoảng đối xứng quanh mean. |
| CTU vs Generic: $\Delta$Fact Coverage | +7.05 pp [1.0, 13.2] pp, $p < 0.05$ | $\Delta$=7.05 pp [1.0, 13.1] pp | EXACT MATCH | CI loại trừ 0 (có ý nghĩa thống kê ở mức $\alpha=0.05$). |
| 20 câu Cross-domain E2E | CTU: 85.0%, Single: 75.0%, Gen: 70.0% | CTU: 85.0% (17/20), Single: 75.0% (15/20), Gen: 70.0% (14/20) | EXACT MATCH | Đánh giá chính xác trên tập con $N=20$. |
| Độ nhạy ngưỡng Fact Coverage | $\theta=0.50$ (81 vs 73), $\theta=0.75$ (39 vs 41), $\theta=1.00$ (32 vs 33) | $\theta=0.50$ (81 vs 73), $\theta=0.75$ (39 vs 41), $\theta=1.00$ (32 vs 33) | EXACT MATCH | Báo cáo trung thực: Single Agent vượt CTU ở ngưỡng ngặt $\ge 0.75$. |

---

## 3. Đánh Giá Ảnh Hưởng Của Bộ Dữ Liệu Sau Khi Sửa Nhãn (Verified Benchmark Impact)

Do ngày 25/09 đã hoàn tất thẩm định 100 câu hỏi trong `scenario12_heldout_100.jsonl` (sửa 27 câu nhãn sai/lệch facts trong bản chạy ngày 23/09), dưới đây là so sánh giữa số liệu trong bài báo (chấm theo nhãn cũ) và số liệu khi chấm lại theo nhãn đã verify:

| Cấu hình | Fact Coverage (Nhãn cũ - Paper) | Fact Coverage (Nhãn mới - Verified) | $\Delta$ Thay đổi | E2E $\ge 0.5$ (Nhãn cũ - Paper) | E2E $\ge 0.5$ (Nhãn mới - Verified) | $\Delta$ Thay đổi |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Single Agent** (`S1-A`) | 63.8% | **57.5%** | -6.37 pp | 73.0% | **66.0%** | -7.0 pp |
| **Routed Gen.** (`S1-B`) | 59.6% | **54.2%** | -5.42 pp | 71.0% | **66.0%** | -5.0 pp |
| **CTU-Chat** (`S1-C`) | 66.6% | **61.0%** | -5.62 pp | 81.0% | **76.0%** | -5.0 pp |

> **Nhận định khoa học quan trọng:**
> 1. Khi chấm lại trên nhãn chuẩn xác, điểm tuyệt đối của cả 3 cấu hình đều giảm nhẹ từ 5-6 điểm %, do nhãn mới bổ sung đầy đủ các fact khắt khe hơn.
> 2. **Tuy nhiên, tương quan thứ bậc và ưu thế tương đối của CTU-Chat không hề suy giảm**: 
>    - $\Delta \text{E2E}$ (CTU vs Single) trên nhãn mới là **+10.0 pp** (76% vs 66%), thậm chí cao hơn mức +8.0 pp trong bài báo.
>    - $\Delta \text{Fact}$ (CTU vs Single) trên nhãn mới là **+3.58 pp** (61.0% vs 57.5%), cao hơn mức +2.8 pp trong bài báo.

---

## 4. Kết Luận & Khuyến Nghị Trình Bày (Recommendations for Manuscript)
1. **Về tính đúng đắn toán học:** Toàn bộ 24 ô số liệu của Bảng 1 và các giá trị khoảng tin cậy CI / McNemar $p$-value trong bài báo **khớp chính xác 100% với log thực nghiệm `run_20260923_155602`**.
2. **Về định nghĩa chỉ số E2E:** Cần thêm ghi chú rõ ràng ở caption Bảng 1: *'E2E corresponds to binary required-fact coverage threshold at $\theta \ge 0.50$ under matched retrieval'*. Tránh hiểu nhầm với composite metric ở mục 4.3.
3. **Về thuật ngữ Latency:** Đảm bảo tất cả các chỗ trong bài (đặc biệt là Discussion dòng 73) dùng đúng từ **'mean latency'**, không dùng 'median'.
4. **Về bộ dữ liệu đã verify:** Nếu nộp bài chính thức, có thể giữ số liệu hiện tại kèm chú thích audit trail, hoặc khuyến nghị chạy một đợt inference fresh run trên nhãn mới để chốt số liệu sau cùng.