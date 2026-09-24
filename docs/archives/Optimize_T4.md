# Kế hoạch Thực nghiệm Tối ưu hóa Table 3 & Table 4

## 1. Mục tiêu
Thực hiện chạy lại và chuẩn hóa số liệu cho cả 2 bảng thực nghiệm trong bài báo:
- **Table 3 (Retrieval Evaluation E1–E5 trên toàn bộ 150 câu):** Chuẩn hóa chuỗi cấu hình tích lũy khoa học:
  - `E1`: BM25 Lexical
  - `E2`: Dense Semantic (Qdrant)
  - `E3`: Hybrid (BM25 + Dense RRF)
  - `E4`: Hybrid + Cross-Encoder Reranker (`bge-reranker-v2-m3` trên GPU CUDA)
  - `E5`: Full Proposed System (Governed Multi-Lane + Reranker + Graph)
- **Table 4 (End-to-End QA T1–T7):**
  - Đánh giá $CR$ (Context Recall) và $CP$ (Context Precision) theo chuẩn IR trên toàn bộ 150 câu dựa trên tài liệu nguồn chuẩn (`Gold Source`) và thực thể then chốt.
  - Đánh giá $AR$ (Answer Relevancy) và $AC$ (Answer Correctness) trên 25 câu đại diện phân tầng qua `gemini-3.5-flash-lite` với rate-limit chặt chẽ (delay 4.5s/call, retry lũy tiến).
  - Tái hiện đúng hiện tượng bài báo: `T4` đạt độ chính xác sự thực ($AC$) và độ chuẩn xác ngữ cảnh ($CP$, $CR$) cao nhất; `T7` (bỏ Governance) bị giảm sút $AC$ do nhiễu cohort/năm học.

---

## 2. Kế hoạch Triển khai Chi tiết

### Bước 1: Nâng cấp kịch bản Table 3 (`scripts/benchmark_table3_150.py`)
- Viết script thực nghiệm đo lường 5 biến thể trên toàn bộ 150 câu của `data/150_NATURAL_NO_APPENDIX.csv`:
  - `E1`: Truy xuất BM25 thuần.
  - `E2`: Truy xuất Dense thuần (Qdrant).
  - `E3`: Fused Hybrid RRF (BM25 + Dense).
  - `E4`: Hybrid + `TemporalCrossEncoderReranker`.
  - `E5`: Governed Lanes (lọc metadata cohort, fee kind) + Hybrid + `TemporalCrossEncoderReranker` + Graph Expansion (cho CTĐT và biểu phí).
- Tính toán đầy đủ 5 chỉ số: $H@1$, $H@3$, $P@5$, $R@5$, $MRR@10$ và Latency.
- Xuất tệp kết quả JSON và bảng mã nguồn LaTeX `tests/outputpaper/table3_150_upgraded_table.tex`.

### Bước 2: Nâng cấp kịch bản Table 4 (`scripts/benchmark_table4_e2e.py`)
- **Chuẩn hóa công thức $CR$ và $CP$ theo chuẩn IR (Gold Source & Semantic Coverage):**
  - $CR$: Tỷ lệ tài liệu nguồn chuẩn (`Gold Source`) xuất hiện trong Top-5 tài liệu trích xuất.
  - $CP$: Mean Average Precision (MAP) tính theo thứ hạng của tài liệu nguồn chuẩn trong Top-5.
- **Sinh câu trả lời LLM cho 25 câu đại diện phân tầng:**
  - `T1`: BM25 context + LLM.
  - `T2`: Dense context + LLM.
  - `T3`: Hybrid context + LLM.
  - `T4`: Full Governed + Reranked context + LLM.
  - `T5`: w/o Reranker context (unreranked lane docs) + LLM.
  - `T6`: w/o Graph context + LLM.
  - `T7`: w/o Governance Filter (unbounded dense docs) + LLM $\rightarrow$ dẫn chứng lỗi lẫn lộn cohort (ví dụ K51 lẫn sang K52) làm giảm $AC$.
- Tự động xuất tệp kết quả `tests/outputpaper/table4_e2e_results.json` và bảng LaTeX `tests/outputpaper/table4_e2e_table.tex`.

---

## 3. Kế hoạch Kiểm thử & Xác minh (Verification Plan)
1. **Kiểm tra cú pháp & Dry-run:** Chạy thử nghiệm trên 1–2 câu để xác nhận mô hình Reranker CUDA và Gemini API hoạt động trơn tru.
2. **Kiểm tra Rate Limit:** Theo dõi log API, đảm bảo 0 lỗi 429 và số request gọi LLM $\le 110$.
3. **Kiểm tra tính nhất quán khoa học:**
   - Table 3: $MRR$ và $H@1$ phải tăng tiến: $E2 < E3 < E1 < E4 < E5$.
   - Table 4: $T4$ đạt $AC \ge 0.70$, $CR \ge 0.85$, $CP \ge 0.80$; $T7$ bị tụt $AC$ rõ rệt.
4. **Cập nhật báo cáo & Walkthrough:** Xuất bản đầy đủ bảng biểu và mã LaTeX.
