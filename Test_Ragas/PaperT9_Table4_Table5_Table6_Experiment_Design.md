# PaperT9 — Thiết kế thực nghiệm Table 4, Table 5 và Table 6

## 1. Tổng quan

Ba bảng thực nghiệm được thiết kế để đo ba khía cạnh khác nhau của hệ thống:

- **Table 4 — Retrieval Effectiveness**: đo khả năng truy hồi đúng evidence.
- **Table 5 — End-to-End RAG Quality**: đo chất lượng context và câu trả lời cuối bằng RAGAS.
- **Table 6 — Graph and Agent Mechanism Ablation**: đo cụ thể đóng góp của routing, Graph, EvidencePolicy và Agent.

Mục tiêu là tránh để các thành phần bị trộn lẫn trong cùng một phép so sánh, từ đó giữ tính ablation rõ ràng và dễ bảo vệ trong bài báo.

---

# 2. Table 4 — Retrieval Effectiveness Ablation

## 2.1. Bảng đề xuất

| Configuration | H@1 | H@3 | P@5 | Recall@5 | MRR@10 | Latency (ms) |
|---|---:|---:|---:|---:|---:|---:|
| **E1 — BM25** | pending | pending | pending | pending | pending | pending |
| **E2 — Dense** | pending | pending | pending | pending | pending | pending |
| **E3 — Hybrid RRF** | pending | pending | pending | pending | pending | pending |
| **E4 — Hybrid RRF + Graph** | pending | pending | pending | pending | pending | pending |
| **E5 — E4 Evidence + Agent** | pending | pending | pending | pending | pending | pending |

## 2.2. Kiến trúc

```text
E1 = BM25

E2 = Dense

E3 = RRF(
       BM25_rank,
       Dense_rank
     )

E4 = RRF(
       BM25_rank,
       Dense_rank,
       Graph_rank
     )

E5 = Agent(E4_evidence)
```

## 2.3. Ý nghĩa ablation

```text
E1 vs E2
→ lexical vs semantic retrieval

E1/E2 vs E3
→ contribution của hybrid retrieval

E3 vs E4
→ contribution của Graph

E4 vs E5
→ contribution của Agent
```

## 2.4. Lưu ý quan trọng

Nếu E5 không thay đổi ranking của E4 thì retrieval metrics của E4 và E5 có thể giống nhau. Không nên cố tạo khác biệt nhân tạo chỉ để E5 có điểm khác E4.

Table 4 nên báo cáo thêm **Graph-target subset**:

- `actual_tuition`
- `academic_program`

Đặc biệt cần phân tích **E3 vs E4** trên subset này để đánh giá contribution của Graph rõ hơn.

---

# 3. Table 5 — RAGAS End-to-End Answer-Quality Ablation

## 3.1. Bảng đề xuất

| Configuration | Answer Relevance | Context Recall | Context Precision | Answer Correctness |
|---|---:|---:|---:|---:|
| **Dense-only** | pending | pending | pending | pending |
| **Sparse-only (BM25)** | pending | pending | pending | pending |
| **Hybrid RRF** | pending | pending | pending | pending |
| **Hybrid RRF + Reranker** | pending | pending | pending | pending |
| **Hybrid RRF + Graph** | pending | pending | pending | pending |
| **Hybrid RRF + Graph + Reranker** | pending | pending | pending | pending |
| **Full Agentic System** | pending | pending | pending | pending |

## 3.2. Pipeline từng cấu hình

### Dense-only

```text
Query
  ↓
Dense
  ↓
Context
  ↓
LLM
  ↓
Answer
```

### Sparse-only (BM25)

```text
Query
  ↓
BM25
  ↓
Context
  ↓
LLM
  ↓
Answer
```

### Hybrid RRF

```text
BM25 ─┐
      ├─ RRF → Context → LLM → Answer
Dense ┘
```

### Hybrid RRF + Reranker

```text
BM25 ─┐
      ├─ RRF → Candidate Pool → Reranker → Context → LLM → Answer
Dense ┘
```

### Hybrid RRF + Graph

```text
BM25 ─┐
Dense ├─ RRF → Context/Evidence → LLM → Answer
Graph ┘
```

### Hybrid RRF + Graph + Reranker

```text
BM25 ─┐
Dense ├─ RRF → Candidate Pool → Reranker → Context/Evidence → LLM → Answer
Graph ┘
```

### Full Agentic System

```text
BM25 ─┐
Dense ├─ RRF → Reranker → Evidence → Agent → Answer
Graph ┘
```

## 3.3. Vai trò của Reranker

Reranker không phải một retrieval lane độc lập.

Không dùng:

```text
RRF(BM25, Dense, Graph, Reranker)
```

Mà dùng:

```text
RRF(BM25, Dense, Graph)
        ↓
Candidate Pool
        ↓
Reranker
```

Tức là reranker chỉ sắp xếp lại candidate đã được retrieval tạo ra, không gọi lại BM25, Dense hay Graph.

## 3.4. Các phép so sánh chính

```text
Hybrid RRF
vs
Hybrid RRF + Reranker
→ contribution của Reranker
```

```text
Hybrid RRF
vs
Hybrid RRF + Graph
→ contribution của Graph
```

```text
Hybrid RRF + Graph
vs
Hybrid RRF + Graph + Reranker
→ contribution của Reranker khi có Graph
```

```text
Hybrid RRF + Graph + Reranker
vs
Full Agentic System
→ contribution của Agent
```

## 3.5. Vai trò của Table 5

Table 5 trả lời câu hỏi:

> Context cuối cùng và câu trả lời end-to-end có tốt hơn khi thêm Hybrid Retrieval, Graph, Reranker và Agent hay không?

Các metric chính:

- Answer Relevance
- Context Recall
- Context Precision
- Answer Correctness

Có thể báo thêm latency để phân tích trade-off giữa chất lượng và chi phí.

---

# 4. Table 6 — Graph and Agent Mechanism Ablation

## 4.1. Bảng đề xuất

| Variant | Route Accuracy | Tool Validity | Evidence Coverage | Decision Accuracy | Answer Correctness |
|---|---:|---:|---:|---:|---:|
| **Graph-only** | N/A | N/A | pending | N/A | pending |
| **Fixed Router + Hybrid** | pending | pending | N/A | pending | pending |
| **Supervisor + Hybrid** | pending | pending | N/A | pending | pending |
| **Supervisor + Hybrid + Graph** | pending | pending | pending | pending | pending |
| **Full Agentic System** | pending | pending | pending | pending | pending |

## 4.2. Ý nghĩa các phép so sánh

### Routing / Supervisor contribution

```text
Fixed Router + Hybrid
        vs
Supervisor + Hybrid
```

Đo contribution của Supervisor hoặc dynamic routing.

### Graph grounding contribution

```text
Supervisor + Hybrid
        vs
Supervisor + Hybrid + Graph
```

Đo contribution của Graph evidence trong cùng routing condition.

### Evidence-aware Agent contribution

```text
Supervisor + Hybrid + Graph
        vs
Full Agentic System
```

Đo contribution của EvidencePolicy + Agent reasoning.

## 4.3. Evidence Coverage

Đề xuất định nghĩa:

\[
EvidenceCoverage =
\frac{
\text{number of required interpretations supported}
}{
\text{number of expected interpretations}
}
\]

Ví dụ câu hỏi có hai interpretation hợp lệ:

```text
standard
CLC
```

Graph lấy đủ cả hai:

\[
Coverage = 2/2 = 1.0
\]

Graph chỉ lấy được một:

\[
Coverage = 1/2 = 0.5
\]

Metric này phù hợp với kiến trúc mới:

```text
EntityResolver
   ↓
Evidence Retrieval
   ↓
EvidencePolicy
   ↓
ANSWER / ANSWER_ALL / CLARIFY / ABSTAIN
```

## 4.4. Decision Accuracy

Decision Accuracy đánh giá Agent có chọn đúng hành vi:

- `ANSWER`
- `ANSWER_ALL`
- `CLARIFY`
- `ABSTAIN`

Ví dụ:

```text
Question thiếu program_type
Evidence có đủ standard + CLC

Gold decision = ANSWER_ALL
Agent decision = ANSWER
```

Khi đó Decision Accuracy = 0, dù một phần fact trong câu trả lời có thể vẫn đúng.

## 4.5. Tool Validity

Có thể định nghĩa:

\[
ToolValidity =
\frac{
\text{valid tool actions}
}{
\text{total attempted tool actions}
}
\]

Một tool action hợp lệ khi:

- tool phù hợp với intent;
- arguments hợp lệ;
- entity resolution hợp lệ;
- không gọi tool không cần thiết;
- execution thành công.

Không dùng `Ground Truth`, `Source`, `source_relation` hoặc benchmark ID để chọn tool.

---

# 5. Vai trò của ba bảng

## Table 4 — Retrieval Effectiveness

Trả lời:

> Hệ thống retrieve đúng evidence tốt đến đâu?

Các thành phần chính:

```text
BM25
Dense
Hybrid RRF
+ Graph
+ Agent
```

Metric:

- H@1
- H@3
- P@5
- Recall@5
- MRR@10
- Latency

---

## Table 5 — End-to-End RAG Quality

Trả lời:

> Context và câu trả lời cuối tốt đến đâu?

Các thành phần chính:

```text
Dense
BM25
Hybrid RRF
+ Reranker
+ Graph
+ Reranker
+ Agent
```

Metric:

- Answer Relevance
- Context Recall
- Context Precision
- Answer Correctness

---

## Table 6 — Graph / Agent Mechanism Ablation

Trả lời:

> Graph và Agent thực sự cải thiện hệ thống thông qua cơ chế nào?

Các thành phần được đánh giá:

```text
Routing
Tool use
Graph evidence
Evidence coverage
Agent decision
```

Metric:

- Route Accuracy
- Tool Validity
- Evidence Coverage
- Decision Accuracy
- Answer Correctness

---

# 6. Tóm tắt kiến trúc thực nghiệm

```text
TABLE 4
Retrieval Effectiveness
────────────────────────
BM25
Dense
Hybrid RRF
+ Graph
+ Agent
```

```text
TABLE 5
End-to-End RAG Quality
────────────────────────
Hybrid
+ Reranker
+ Graph
+ Reranker
+ Agent
```

```text
TABLE 6
Graph / Agent Mechanism Ablation
─────────────────────────────────
Routing
Tool use
Graph evidence
Evidence coverage
Agent decision
```

Ba bảng được thiết kế để không đo lặp cùng một mục tiêu:

- **Table 4** tập trung vào retrieval.
- **Table 5** tập trung vào context và answer quality.
- **Table 6** tập trung vào cơ chế Graph/Agent.

Điều này giúp tách riêng contribution của từng thành phần và làm ablation study dễ giải thích hơn trong bài báo.
