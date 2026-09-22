# Sửa Abstract theo Mục 3 hướng dẫn

## Vấn đề phát hiện

Abstract hiện tại (~230 từ) có hai sai sót so với hướng dẫn:

1. **Thiếu câu objective** — nhảy từ problem (câu 1) sang "We present CTU-Chat" (câu 2) mà không phát biểu mục tiêu. Hướng dẫn bước 2: "Phát biểu mục tiêu/câu hỏi nghiên cứu."
2. **Quá dày số liệu** — 8 câu kết quả liên tiếp chứa ~20 con số, CI, token %, latency. Khó đọc nhanh độc lập. Hướng dẫn checklist: "Không dành quá nhiều chỗ cho..."; "Đọc độc lập vẫn hiểu."

## Phân tích cấu trúc hiện tại vs yêu cầu

| Bước hướng dẫn | Hiện tại | Sửa |
|---|---|---|
| 1. Context/problem | ✅ Câu 1 | Giữ nguyên |
| 2. Objective | ❌ Không có | **Thêm 1 câu sau câu 1** |
| 3. Methods | ✅ Câu 2–3 (system + stress test) | Gộp gọn hơn |
| 4. Key results | ⚠️ Câu 4–8 (quá chi tiết) | **Rút gọn, giữ phát hiện chính** |
| 5. Conclusion | ✅ Câu cuối | Giữ nguyên |

## Proposed Changes

### [MODIFY] [00-abstract.tex](file:///E:/RHNA/1Visual/CTU-chat/PAPER/sections/00-abstract.tex)

Rewrite abstract theo cấu trúc 5 bước. Thay đổi cụ thể:

**Câu 1 (Context) — giữ nguyên:**
> University counseling combines relational curricula, cohort-specific fees, policy tables, and narrative regulations, for which a uniform evidence path may be unsuitable.

**Câu 2 (Objective) — THÊM MỚI:**
> This study develops and evaluates a domain-specialized multi-agent system for heterogeneous university counseling.

Câu này khớp với objective ở Introduction ("The objective of this study is to develop and evaluate CTU-Chat for heterogeneous university counseling").

**Câu 3 (Methods) — gộp system description + evaluation design:**
> We present CTU-Chat, a supervisor-routed architecture that assigns queries to four specialists with scoped representations and tools: Neo4j for curricula, structured lookup and deterministic calculation for financial data, and hybrid document retrieval for regulations. We evaluate it through retrieval stacking on a 100-query held-out set, generation ablation across seven configurations (2,100 turns), and a 1,960-decision semantic-neighbor stress test across registries of 11--51 tools.

**Câu 4–5 (Key results) — rút từ 5 câu → 2 câu, giữ phát hiện chính mỗi RQ:**
> At 51 tools, the routed specialist exceeds the global Top-10 single-agent baseline in decision-level end-to-end pass rate by 9.3 percentage points (95\% CI [+2.0, +17.3]), although positive high-minus-low interactions have CIs containing zero. The full retrieval configuration achieves 0.7400 Hit@1 and 0.8608 Recall@5; the full generation configuration reaches 0.8636 Faithfulness and 0.8325 Source Recall, exceeding all retrieval baselines and the no-reranker ablation.

Bỏ: token cost/latency details (52.4%, 70.8%, 2.03×), full-registry vs specialist CI zero, MRR@10, Context Recall riêng. Những chi tiết này có trong Results/Discussion.

**Câu 6 (Conclusion) — giữ nguyên:**
> These findings suggest that domain-specific disambiguation and heterogeneous evidence allocation can support institutional counseling under the evaluated conditions, with configuration-dependent accuracy and cost trade-offs.

## Open Questions

> [!IMPORTANT]
> **Q1:** Bỏ chi tiết token/latency trong Abstract có được không? Hay cần giữ ít nhất 1 câu cost trade-off vì câu conclusion đã nhắc "cost trade-offs"?
>
> **Q2:** Câu objective dùng "develops and evaluates" (present tense theo convention) hay "developed and evaluated" (past tense khớp Conclusion)? Đề xuất present tense vì Abstract thường dùng present/present perfect.

## Verification Plan

- Đếm từ sau sửa (target: 180–230 từ, trong khoảng 150–300)
- Checklist 5 bước: context ✓, objective ✓, methods ✓, results ✓, conclusion ✓
- Đối chiếu số liệu với Tables 1–4
- Kiểm tra không có kết quả trong Abstract mà không có trong Results
