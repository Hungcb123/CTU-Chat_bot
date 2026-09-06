# Hướng chỉnh sửa thực nghiệm Table 5 — PaperT9

## 1. Mục tiêu của Table 5

Table 5 nên được dùng để đánh giá **chất lượng context và câu trả lời end-to-end** khi lần lượt bổ sung các thành phần của hệ thống.

Các metric chính giữ nguyên:

- Answer Relevance
- Context Recall
- Context Precision
- Answer Correctness

Không thay thế Table 4:

- **Table 4**: retrieval effectiveness.
- **Table 5**: end-to-end RAG quality.
- **Table 6**: cơ chế Graph / Agent.

---

## 2. Cấu hình đề xuất cho Table 5

| ID | Configuration | Mục đích |
|---|---|---|
| T1 | Dense-only | Semantic retrieval baseline |
| T2 | Sparse-only (BM25) | Lexical retrieval baseline |
| T3 | Hybrid RRF | Traditional Hybrid RAG baseline |
| T4 | Hybrid RRF + Reranker | Đo đóng góp của reranker |
| T5 | Hybrid RRF + Graph | Đo đóng góp của Graph |
| T6 | Hybrid RRF + Graph + Reranker | Graph + reranking |
| T7 | Hybrid RRF + Graph + Reranker + Agent | Đo đóng góp của Agent |

Các phép so sánh chính:

- **T1 vs T2** → lexical vs semantic retrieval.
- **T1/T2 vs T3** → contribution của hybrid retrieval.
- **T3 vs T4** → contribution của reranker.
- **T3 vs T5** → contribution của Graph.
- **T5 vs T6** → contribution của reranker khi có Graph.
- **T6 vs T7** → contribution của Agent khi evidence đầu vào được giữ cố định.

---

## 3. Pipeline đề xuất

### T1 — Dense-only

```text
Query
  ↓
Dense Retrieval
  ↓
Top-K Context
  ↓
LLM
  ↓
Answer
```

### T2 — BM25-only

```text
Query
  ↓
BM25
  ↓
Top-K Context
  ↓
LLM
  ↓
Answer
```

### T3 — Hybrid RRF

```text
BM25 ─┐
      ├─ RRF
Dense ┘
       ↓
Top-K Context
       ↓
LLM
       ↓
Answer
```

### T4 — Hybrid RRF + Reranker

```text
BM25 ─┐
      ├─ RRF
Dense ┘
       ↓
Candidate Pool
       ↓
Reranker
       ↓
Top-K Context
       ↓
LLM
       ↓
Answer
```

### T5 — Hybrid RRF + Graph

Graph chỉ nên được đưa trực tiếp vào RRF nếu implementation hiện tại có thể chuyển kết quả Graph thành một ranked list `Evidence[]` có canonical identity tương thích với BM25/Dense.

Nếu có:

```text
BM25 ─┐
Dense ├─ RRF
Graph ┘
       ↓
Top-K Evidence
       ↓
LLM
       ↓
Answer
```

Nếu Graph trả về structured records khác loại document/chunk, nên canonicalize trước:

```text
Graph Result
    ↓
Evidence Serialization / Canonicalization
    ↓
Graph_rank
```

rồi mới đưa vào RRF.

Không nên ép Graph vào RRF nếu production implementation không hỗ trợ một ranked evidence representation hợp lệ.

### T6 — Hybrid RRF + Graph + Reranker

```text
BM25 ─┐
Dense ├─ RRF
Graph ┘
       ↓
Candidate Pool
       ↓
Reranker
       ↓
Top-K Evidence
       ↓
LLM
       ↓
Answer
```

Reranker:

- chỉ rerank candidate đã có;
- không gọi lại BM25;
- không gọi lại Dense;
- không query Graph lại;
- không thêm candidate mới;
- không dùng Ground Truth / Source để rerank.

### T7 — Agent Ablation

```text
T6 Evidence
    ↓
Agent
    ↓
ANSWER / ANSWER_ALL / CLARIFY / ABSTAIN
    ↓
Final Answer
```

Để T6 vs T7 là ablation sạch:

- T7 phải nhận đúng evidence đầu ra của T6;
- Agent không được retrieval lại;
- Agent không được tự gọi thêm BM25/Dense/Graph trong phép test này;
- Agent chỉ thực hiện reasoning, evidence selection, ambiguity handling và answer synthesis.

Nếu Agent bị giới hạn như trên, tên chính xác hơn là:

**Hybrid + Graph + Reranker + Agent Orchestration**

thay vì gọi tuyệt đối là **Full Agentic System**.

---

## 4. Fairness cần giữ cố định

T1–T6 phải dùng cùng:

- dataset;
- corpus/index version;
- generation model;
- system prompt / generation prompt;
- temperature;
- max tokens;
- `context_top_k`;
- formatting context;
- ordering rule;
- evaluator model;
- RAGAS version.

Các cấu hình chỉ được khác ở đúng thành phần đang ablate.

Ví dụ:

```text
candidate_depth = L
context_top_k = K
rrf_k = R
```

phải được giữ thống nhất giữa các variant tương ứng.

Ground Truth, expected answer, Source, `source_relation`, benchmark ID chỉ được evaluator dùng **sau khi answer/context đã sinh xong**.

---

## 5. Graph-target subset

Ngoài kết quả toàn dataset, nên báo cáo riêng subset mà Graph được thiết kế để hỗ trợ, ví dụ:

- `actual_tuition`
- `academic_program`

Ít nhất so sánh:

- T3 — Hybrid RRF
- T4 — Hybrid RRF + Reranker
- T5 — Hybrid RRF + Graph
- T6 — Hybrid RRF + Graph + Reranker
- T7 — Agent

Điểm quan trọng nhất là:

- **T3 vs T5**: Graph contribution.
- hoặc nếu production baseline luôn dùng reranker: **T4 vs T6**.
- **T6 vs T7**: Agent contribution.

Không nên chỉ dựa vào overall average vì Graph có thể chỉ cải thiện mạnh trên các câu hỏi quan hệ / học phí / chương trình đào tạo.

---

## 6. Output Table 5 đề xuất

### TABLE 5 — RAGAS END-TO-END ANSWER QUALITY

| Configuration | Answer Relevance | Context Recall | Context Precision | Answer Correctness |
|---|---:|---:|---:|---:|
| Dense-only | | | | |
| Sparse-only (BM25) | | | | |
| Hybrid RRF | | | | |
| Hybrid RRF + Reranker | | | | |
| Hybrid RRF + Graph | | | | |
| Hybrid RRF + Graph + Reranker | | | | |
| Hybrid + Graph + Reranker + Agent | | | | |

Ngoài bảng chính nên lưu:

- per-question scores;
- failed RAGAS cases;
- latency;
- retrieved evidence IDs;
- Graph provenance;
- pre/post-rerank rank;
- Agent decision;
- subset/domain label.

---

## 7. Có phải chỉ sửa file test không?

**Có thể chỉ cần sửa file test/test runner nếu code production hiện tại đã modular và đã có sẵn tất cả các entry point sau:**

- BM25-only retrieval;
- Dense-only retrieval;
- Hybrid RRF;
- Graph retrieval/evidence;
- Reranker nhận candidate pool có sẵn;
- Generator nhận context/evidence truyền vào;
- Agent nhận fixed evidence mà không bắt buộc retrieval lại.

Khi đó phần lớn công việc là:

```text
test runner
  ↓
chọn configuration
  ↓
gọi đúng các hàm production có sẵn
  ↓
thu context + answer
  ↓
chạy RAGAS
```

Không nên viết lại retrieval riêng chỉ dành cho benchmark.

### Tuy nhiên, không thể khẳng định 100% chỉ sửa các lời gọi hàm nếu chưa audit source code.

Có thể cần sửa nhỏ ngoài file test nếu hiện tại:

1. Graph chưa trả về cùng abstraction `Evidence`.
2. Graph chưa có ranked output để tham gia RRF.
3. Reranker đang tự gọi retrieval bên trong thay vì nhận candidate pool.
4. Agent luôn tự retrieval/tool-call và chưa hỗ trợ chế độ `fixed_evidence`.
5. Dense/BM25/Hybrid chưa có mode bật/tắt độc lập.
6. Context construction đang hard-code theo production path.
7. Logging chưa giữ được provenance/rank/evidence ID cần cho thực nghiệm.

Trong các trường hợp đó, nên thêm **adapter hoặc configuration flag nhỏ trong shared production code**, không tạo một pipeline benchmark riêng.

Nguyên tắc:

> **Reuse production implementation, test runner chỉ orchestration các variant.**

---

## 8. Hướng sửa code nên ưu tiên

Thứ tự audit:

1. Xác định các hàm retrieval hiện có.
2. Kiểm tra BM25/Dense có gọi độc lập được không.
3. Kiểm tra RRF nhận ranked list nào.
4. Xác định Graph output hiện tại.
5. Kiểm tra Graph có thể canonicalize thành `Evidence[]` không.
6. Kiểm tra reranker có nhận candidate pool từ bên ngoài không.
7. Kiểm tra generation có nhận context cố định không.
8. Kiểm tra Agent có chế độ nhận fixed evidence không.
9. Kiểm tra Ground Truth không đi vào production path.
10. Sau đó mới patch test runner.

Nếu 1–8 đã hỗ trợ đầy đủ thì **chủ yếu chỉ sửa file test/configuration runner**.

Nếu chưa hỗ trợ, chỉ bổ sung interface tối thiểu cần thiết trong production/shared modules rồi test runner gọi lại interface đó.

---

## 9. Kết luận

Hướng Table 5 nên tập trung vào chuỗi:

```text
Dense / BM25
    ↓
Hybrid RRF
    ↓
+ Reranker
    ↓
+ Graph
    ↓
+ Graph + Reranker
    ↓
+ Agent
```

Mục tiêu chính là làm rõ ba contribution:

1. Hybrid Retrieval.
2. Graph Evidence.
3. Agent Orchestration.

Không cần rewrite toàn bộ hệ thống để chạy Table 5.

Nếu các module production đã tách tốt, **chỉ cần sửa test runner và cách gọi/config các hàm**. Chỉ khi Graph, reranker hoặc Agent chưa expose interface phù hợp mới cần sửa thêm một lượng nhỏ shared code.
