# BÁO CÁO TOÀN DIỆN KẾT QUẢ THỰC NGHIỆM SCENARIO 1 & SCENARIO 2
## (HELD-OUT TEST SET — 100 CASES × 7 CẤU HÌNH × 3 REPETITIONS = 2,100 TURNS)

- **Tập dữ liệu:** Held-Out Test Set (100 ca hỏi đáp độc lập, đã qua author-review)
- **Mô hình sinh & chấm:** `gemini-2.5-flash-lite` (Vertex AI `europe-west1`, Temperature = 0.0)
- **Bộ nhớ tri thức & Tìm kiếm:** Neo4j 5.x Graph + BGE/Vietnamese Bi-Encoder + BM25 + Cross-Encoder Reranker
- **Thư viện đánh giá:** Ragas 0.4 (Strictness = 1) + 10,000 Bootstrap Resampling (95% CI)
- **Tỉ lệ hoàn tất dữ liệu:** **100.00%** (10,500 / 10,500 cell hợp lệ, 0 None, 0 Failures)

---

## TÓM TẮT ĐIỂM NHẤN CỐT LÕI (EXECUTIVE SUMMARY)

1. **So sánh cấu hình đầy đủ với ablation không governance ($T_4$ vs $T_7$):**
   - Với cơ chế an toàn 20-candidate hybrid safety net, ngưỡng động 0.20 và làn thực thể Neo4j cho chương trình đào tạo (`academic_program`), $T_4$ có point estimate cao hơn $T_7$ trên Context Recall, Faithfulness, Answer Relevancy, Source Recall và Source AP. Tuy nhiên, các khoảng tin cậy ghép cặp của năm metric Ragas đều chứa 0, nên kết quả không thiết lập một lợi thế đồng đều trên mọi metric:
     - **Context Recall (CR):** $T_4 = \mathbf{0.6534}$ vs $T_7 = 0.6299$ (**+0.0234** / **+2.34%**)
     - **Faithfulness:** $T_4 = \mathbf{0.8636}$ vs $T_7 = 0.8427$ (**+0.0209** / **+2.09%**)
     - **Answer Relevancy (AR):** $T_4 = \mathbf{0.4468}$ vs $T_7 = 0.4304$ (**+0.0165** / **+1.65%**)
     - **Source Recall:** $T_4 = \mathbf{0.8325}$ vs $T_7 = 0.8208$ (**+0.0117** / **+1.17%**)
     - **Source AP:** $T_4 = \mathbf{0.7316}$ vs $T_7 = 0.7277$ (**+0.0039** / **+0.39%**)
     - **Academic Domain Recall:** $T_4 = \mathbf{0.8684}$ vs $T_7 = 0.8421$ (**+2.63%**)
2. **Scenario 1 — Retrieval:**
   - Cấu hình đầy đủ **E5** đạt giá trị tổng thể cao nhất trên năm metric: Hit@1 = 0.7400, Hit@3 = 0.9200, Precision@5 = 0.3020, Recall@5 = 0.8608 và MRR@10 = 0.8333. E4, cấu hình hybrid có neural reranker, đạt Hit@1 = 0.7000 và MRR@10 = 0.8054 với latency thấp hơn E5.
3. **Tính toàn vẹn dữ liệu:**
   - Toàn bộ 10,500 giá trị metric bắt buộc đều hợp lệ, không có cell thiếu (`NaN`/`None`) hoặc evaluation failure.

---

## PHẦN 1: SCENARIO 1 — ĐÁNH GIÁ NĂNG LỰC TRUY XUẤT (RETRIEVAL BENCHMARK)

### Bảng 1.1: Hiệu năng Truy xuất Tổng thể (N = 100 ca)

| Cấu hình | Mô tả kỹ thuật | Hit@1 | Hit@3 | Precision@5 | Recall@5 | MRR@10 | Latency (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| E1 | Naive BM25 (Lexical Only) | 0.5300 | 0.7700 | 0.2060 | 0.6167 | 0.6695 | 7.08 |
| E2 | Naive Dense Vector (Bi-Encoder Only) | 0.4600 | 0.6500 | 0.1760 | 0.5242 | 0.5604 | 33.66 |
| E3 | Hybrid Search (BM25 + Dense Vector) | 0.5200 | 0.7900 | 0.2240 | 0.6625 | 0.6725 | 37.57 |
| E4 | Hybrid + Neural Reranker | 0.7000 | 0.9100 | 0.2540 | 0.7508 | 0.8054 | 15366.33 |
| **E5** | **Full Governed Multi-Evidence Retrieval** | **0.7400** | **0.9200** | **0.3020** | **0.8608** | **0.8333** | 21857.56 |

> **Nhận xét Bảng 1.1:** E5 có các giá trị aggregate cao nhất nhưng cũng có latency lớn nhất. E4 cải thiện Hit@1 từ 0.5200 lên 0.7000 và MRR@10 từ 0.6725 lên 0.8054 so với E3, phù hợp với lợi ích early-rank của neural reranking trong benchmark này.

### Bảng 1.2: Phân rã theo Miền Tri thức (Per-Domain Breakdown)

| Cấu hình | Academic (N=38) | Financial (N=28) | Scholarship (N=17) | General (N=17) | Macro-Avg Hit@1 | Micro-Avg Hit@1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| E1 | 0.5789 | 0.6786 | 0.4118 | 0.3125 | 0.4954 | 0.5300 |
| E2 | 0.3158 | 0.4643 | 0.6471 | 0.2500 | 0.4193 | 0.4600 |
| E3 | 0.4737 | 0.5000 | 0.5882 | 0.3125 | 0.4686 | 0.5200 |
| E4 | 0.7368 | 0.8214 | 0.7647 | 0.3125 | 0.6589 | 0.7000 |
| E5 | 0.7368 | 1.0000 | 0.6471 | 0.3125 | 0.6741 | 0.7400 |

### Bảng 1.3: Phân rã theo Độ phức tạp Câu hỏi (Per-Complexity-Tier Hit@1)

| Cấu hình | Direct (N=40) | Multi-hop (N=20) | Comparison (N=10) | Cross-domain (N=20) | Temporal (N=5) | Adversarial (N=5) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| E1 | 0.4500 | 0.6000 | 0.7000 | 0.5500 | 0.8000 | 0.2000 |
| E2 | 0.4750 | 0.3500 | 0.3000 | 0.6000 | 0.4000 | 0.6000 |
| E3 | 0.4750 | 0.5500 | 0.4000 | 0.7000 | 0.4000 | 0.4000 |
| E4 | 0.6500 | 0.7000 | 0.8000 | 0.7500 | 0.8000 | 0.6000 |
| E5 | 0.6750 | 0.7000 | 0.9000 | 0.8000 | 1.0000 | 0.6000 |

### Bảng 1.4: Phân rã chi tiết theo 13 Danh mục Áp lực (13 Stress Categories Hit@1)

| Cấu hình | academic program | academic rules | actual tuition | adversarial | comparison | cross domain | exemption basis | exemption policy | financial policy | scholarship | social support | student loan | temporal |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| E1 | 0.5000 | 0.4444 | 0.7778 | 0.2000 | 0.7000 | 0.5500 | 0.0000 | 0.5000 | 0.6000 | 0.4667 | 0.0000 | 0.6667 | 0.8000 |
| E2 | 0.3333 | 0.1111 | 0.5556 | 0.6000 | 0.3000 | 0.6000 | 1.0000 | 0.5000 | 0.4000 | 0.7333 | 0.0000 | 0.3333 | 0.4000 |
| E3 | 0.3333 | 0.6667 | 0.5556 | 0.4000 | 0.4000 | 0.7000 | 1.0000 | 0.5000 | 0.4000 | 0.6667 | 0.0000 | 0.3333 | 0.4000 |
| E4 | 0.6667 | 0.4444 | 0.8889 | 0.6000 | 0.8000 | 0.7500 | 1.0000 | 0.5000 | 0.8000 | 0.8000 | 0.5000 | 0.0000 | 0.8000 |
| E5 | 0.8333 | 0.3333 | 1.0000 | 0.6000 | 0.9000 | 0.8000 | 1.0000 | 0.5000 | 1.0000 | 0.6667 | 0.5000 | 0.0000 | 1.0000 |

---

## PHẦN 2: SCENARIO 2 — ĐÁNH GIÁ NĂNG LỰC SINH & CHUẨN ĐỐI SÁNH RAGAS
### (7 Cấu hình × 100 Ca × 3 Repetitions = 2,100 Lượt sinh, Gemini 2.5 Flash Lite)

### Bảng 2.1: Bảng Chuẩn Đối sánh Chính thức (Official Benchmark Table)

| Cấu hình | Mô tả thiết lập | Answer Relevancy (AR) | Context Recall (CR) | Context Precision (CP) | Answer Correctness (AC) | Faithfulness (Faith) | Source Recall | Source AP | Fact Exact Match |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| T1 | Naive BM25 Baseline | 0.3901 ± 0.33 | 0.5349 ± 0.46 | 0.2522 ± 0.34 | 0.4615 ± 0.28 | 0.8042 ± 0.36 | 0.6358 | 0.4637 | 0.5924 |
| T2 | Dense Vector Baseline | 0.2370 ± 0.31 | 0.2648 ± 0.40 | 0.1626 ± 0.32 | 0.3372 ± 0.25 | 0.5817 ± 0.46 | 0.5342 | 0.4094 | 0.5179 |
| T3 | Hybrid RRF Baseline | 0.3972 ± 0.36 | 0.4693 ± 0.45 | 0.2071 ± 0.31 | 0.4361 ± 0.29 | 0.7486 ± 0.38 | 0.6892 | 0.5015 | 0.5792 |
| T4 | Full Governed Multi-Evidence Configuration | 0.4468 ± 0.30 | **0.6534 ± 0.41** | 0.3511 ± 0.39 | 0.4785 ± 0.28 | **0.8636 ± 0.28** | **0.8325** | **0.7316** | 0.6331 |
| T5 | Ablation: w/o Cross-Encoder Reranker | 0.3425 ± 0.32 | 0.5192 ± 0.44 | 0.2248 ± 0.33 | 0.4330 ± 0.28 | 0.7618 ± 0.37 | 0.7892 | 0.6834 | 0.6056 |
| T6 | Ablation: w/o Neo4j Graph Evidence | **0.4719 ± 0.33** | 0.5791 ± 0.44 | **0.3765 ± 0.43** | **0.4913 ± 0.29** | 0.8376 ± 0.31 | 0.6925 | 0.5939 | 0.6184 |
| T7 | Ablation: w/o Subspace Governance | 0.4304 ± 0.30 | 0.6299 ± 0.42 | 0.3541 ± 0.39 | 0.4785 ± 0.28 | 0.8427 ± 0.30 | 0.8208 | 0.7277 | **0.6345** |

### Bảng 2.2: Khoảng Tin cậy Bootstrap 95% (95% Bootstrap Confidence Intervals, B=10,000)

| Cấu hình | Answer Relevancy [95% CI] | Context Recall [95% CI] | Context Precision [95% CI] | Answer Correctness [95% CI] | Faithfulness [95% CI] | N |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| T1 | [0.3531, 0.4272] | [0.4832, 0.5862] | [0.2145, 0.2912] | [0.4299, 0.4932] | [0.7629, 0.8438] | 300 |
| T2 | [0.2025, 0.2727] | [0.2193, 0.3116] | [0.1284, 0.1992] | [0.3089, 0.3659] | [0.5300, 0.6327] | 300 |
| T3 | [0.3560, 0.4388] | [0.4176, 0.5213] | [0.1731, 0.2429] | [0.4032, 0.4690] | [0.7041, 0.7912] | 300 |
| **T4** | **[0.4132, 0.4799]** | **[0.6066, 0.6989]** | **[0.3078, 0.3945]** | **[0.4478, 0.5094]** | **[0.8316, 0.8936]** | 300 |
| T5 | [0.3070, 0.3786] | [0.4695, 0.5695] | [0.1886, 0.2619] | [0.4018, 0.4651] | [0.7192, 0.8036] | 300 |
| T6 | [0.4348, 0.5087] | [0.5292, 0.6284] | [0.3287, 0.4252] | [0.4589, 0.5235] | [0.8019, 0.8713] | 300 |
| T7 | [0.3965, 0.4637] | [0.5821, 0.6767] | [0.3106, 0.3981] | [0.4474, 0.5099] | [0.8071, 0.8763] | 300 |

### Bảng 2.3: Phân tích Cắt giảm ghép cặp (Paired Differences vs T4: Full Pipeline)

| Cặp so sánh (Ablation) | Thước đo | Mean Diff (T4 − Baseline) | 95% Bootstrap CI | N pairs | Kết luận thống kê |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **T4 vs T7** | **CR** | **+0.0234** | **[-0.0022, +0.0510]** | 300 | CI chứa 0 |
| **T4 vs T7** | **Faith** | **+0.0209** | **[-0.0162, +0.0580]** | 300 | CI chứa 0 |
| **T4 vs T7** | AR | +0.0165 | [-0.0091, +0.0424] | 300 | CI chứa 0 |
| **T4 vs T7** | CP | -0.0029 | [-0.0148, +0.0081] | 300 | Tương đương |
| **T4 vs T7** | AC | -0.0000 | [-0.0172, +0.0167] | 300 | Tương đương |
| **T4 vs T6** | **CR** | **+0.0743** | **[+0.0374, +0.1110]** | 300 | CI không chứa 0 |
| **T4 vs T6** | **Faith** | **+0.0260** | **[-0.0049, +0.0568]** | 300 | T4 nhỉnh hơn |
| **T4 vs T6** | AR | -0.0250 | [-0.0527, +0.0021] | 300 | Tương đương |
| **T4 vs T6** | CP | -0.0253 | [-0.0559, +0.0066] | 300 | Tương đương |
| **T4 vs T6** | AC | -0.0128 | [-0.0338, +0.0085] | 300 | Tương đương |
| **T4 vs T5** | **CR** | **+0.1342** | **[+0.0939, +0.1757]** | 300 | CI không chứa 0 |
| **T4 vs T5** | **Faith** | **+0.1018** | **[+0.0548, +0.1475]** | 300 | CI không chứa 0 |
| **T4 vs T5** | AR | +0.1044 | [+0.0666, +0.1423] | 300 | CI không chứa 0 |
| **T4 vs T5** | CP | +0.1263 | [+0.0960, +0.1583] | 300 | CI không chứa 0 |
| **T4 vs T5** | AC | +0.0455 | [+0.0209, +0.0701] | 300 | CI không chứa 0 |

---

## PHẦN 3: PHÂN TÍCH CHUYÊN SÂU & GIẢI TRÌNH HỌC THUẬT (IN-DEPTH DISCUSSION)

### 1. So sánh Subspace Governance ($T_4$ vs $T_7$)
- **Vấn đề tồn tại trước đây:** Ở phiên bản ban đầu, khi Subspace Router kích hoạt, nếu truy vấn chứa các thực thể chuyên ngành thuộc sơ đồ đồ thị đào tạo (Curriculum Graph) nhưng bị xếp nhầm danh mục intent, Subspace Filter sẽ lọc quá chặt làm mất các đoạn tài liệu văn bản gốc, khiến $T_7$ (truy xuất phẳng toàn cục) có Context Recall nhỉnh hơn.
- **Giải pháp khắc phục:**
  1. **Hybrid Safety Net:** Đảm bảo luôn giữ lại 20 ứng viên hàng đầu từ bộ tìm kiếm lai (Hybrid Search) trước khi áp bộ lọc chuyên biệt.
  2. **Dynamic Thresholding (0.20):** Thay thế ngưỡng lọc cứng bằng ngưỡng mềm tương đối, cho phép các đoạn văn bản biên nhưng có độ tương đồng ngữ nghĩa cao được giữ lại.
  3. **Mở rộng làn thực thể Neo4j (`academic_program`):** Cho phép các thực thể đồ thị về chương trình đào tạo, chuyên ngành và quy chế học vụ truyền thẳng vào không gian rerank.
- **Kết quả thực nghiệm:** T4 có Context Recall 0.6534 so với 0.6299 của T7 và Faithfulness 0.8636 so với 0.8427. Tuy nhiên, CI ghép cặp của các metric Ragas đều chứa 0; các khác biệt này vì vậy được trình bày như point estimates, không phải bằng chứng về hiệu ứng đồng đều của governance.

### 2. Vai trò của Cross-Encoder Reranker — $T_4$ vs $T_5$
- T5 giữ governed hybrid candidates và graph evidence nhưng bỏ cross-encoder reranking. So với T5, T4 cao hơn trên cả tám metric; năm khác biệt Ragas ghép cặp đều có CI 95% nằm trên 0. Ví dụ, Context Recall tăng từ 0.5192 lên 0.6534 và Faithfulness tăng từ 0.7618 lên 0.8636.
- Kết quả này phù hợp với đóng góp của reranking trong cấu hình được đánh giá, nhưng không thiết lập tính phổ quát ngoài benchmark hiện tại.

### 3. Vai trò của Neo4j Graph Evidence — $T_4$ vs $T_6$
- T6 giữ governed hybrid retrieval và reranking nhưng bỏ graph evidence. T4 có Context Recall cao hơn (0.6534 so với 0.5791; paired CI $[+0.0374,+0.1110]$), đồng thời có Source Recall, Source AP và Fact EM cao hơn.
- T6 lại có point estimate cao hơn trên Context Precision, Answer Relevancy và Answer Correctness. Do đó, ablation này cho thấy trade-off theo metric thay vì một lợi thế đồng đều của graph evidence.

---

## PHẦN 4: TÍNH TOÀN VẸN DỮ LIỆU & THÔNG TIN TÁI LẬP (REPRODUCIBILITY)

- **Hồ sơ lưu trữ nội bộ:** checkpoint, summary và records JSONL gồm 2,100 dòng chi tiết theo lượt; các checksum được lưu cùng artifact.
- **Tình trạng lỗi:** `Total: 0` (Không có bất kỳ trường hợp nào bị missing metric hoặc out-of-quota).
