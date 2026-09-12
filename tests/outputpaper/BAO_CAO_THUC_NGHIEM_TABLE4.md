# Báo cáo Table 4 — Top-7 Graph-injection rerun

**Dataset:** `data/150_NATURAL_NO_APPENDIX.csv` (150 câu)
**Model:** `gemini-2.5-flash-lite` qua Vertex AI
**Cấu hình:** T1–T7, cùng cửa sổ context Top-7, 5 worker
**Prompt:** `graph_context_top7_v1`
**Dataset SHA-256:** `53b10c3ad4ad1426753b1de777eb1b8d49b610101b03401b25ff209fbb5195cb`

## Kết quả thực tế

| Cấu hình | Mô tả | AR | CR (Top-7) | CP (Top-7) | AC |
|---|---|---:|---:|---:|---:|
| T1 | BM25 + LLM | 0.737 | 0.790 | 0.653 | 0.596 |
| T2 | Dense + LLM | 0.580 | 0.583 | 0.415 | 0.482 |
| T3 | Hybrid + LLM | 0.730 | 0.758 | 0.531 | 0.600 |
| **T4** | **Proposed (CTU-Chat)** | **0.781** | 0.795 | 0.722 | **0.647** |
| T5 | w/o Cross-Encoder Reranker | 0.723 | 0.758 | 0.531 | 0.612 |
| T6 | w/o Knowledge Graph | 0.750 | **0.798** | **0.739** | 0.642 |
| T7 | w/o Governance Filter | 0.579 | 0.583 | 0.415 | 0.482 |

Mỗi cấu hình có đủ 150 case; tổng cộng 1.050 lượt sinh đáp án và 1.050 lượt judge. Kết quả được tính từ lần chạy Top-7 mới, không tái sử dụng checkpoint Top-5. T4 đạt AC cao nhất và cải thiện so với T3; T6 nhỉnh hơn T4 ở CR/CP nên không kết luận T4 đứng đầu mọi metric. T7 suy giảm mạnh về AR/CR/CP khi bỏ governance.

## Kiểm tra Graph

T4 dùng Graph injection với nội dung học phí/policy thực tế và catalog fallback có nhãn nguồn. Fallback không được gọi là Graph hit. Bản runner hiện tại chỉ xuất CR/CP theo cấu hình và chưa lưu bộ đếm Graph-hit/fallback theo case; vì vậy báo cáo này không suy diễn tỷ lệ Graph-hit từ các metric tổng hợp. Việc bổ sung bộ đếm riêng được để cho lần chạy instrumentation tiếp theo.

## Tệp sinh ra

- `table4_e2e_results.json` — số liệu và chữ ký dataset/model/Top-K/prompt.
- `table4_e2e_table.tex` — bảng LaTeX tương ứng.
- `table4_vertex_checkpoint.json` — checkpoint generation/judge.
