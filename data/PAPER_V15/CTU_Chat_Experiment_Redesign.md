# CTU-Chat — Đề cương làm lại bài báo và thiết kế lại thực nghiệm

> Mục tiêu của tài liệu này: tái cấu trúc bài báo để **đánh giá trực tiếp kiến trúc supervisor-routed multi-agent chatbot**, thay vì chủ yếu đánh giá các thành phần retrieval/tool-selection rời rạc. Tài liệu này dựa trên bản paper hiện tại của CTU-Chat và đề xuất một kế hoạch thực nghiệm mới có thể chạy lại từ đầu.

---

## 1. Chẩn đoán vấn đề của bài hiện tại

Bản hiện tại có một kiến trúc khá rõ: một **centralized supervisor** nhận truy vấn, rewrite và phân loại domain/intent, sau đó route sang một trong bốn specialist agents; mỗi specialist có evidence path và tool privileges riêng. Academic đi graph/Neo4j; Financial dùng structured lookup và deterministic calculation; Scholarship và General dựa nhiều hơn vào document retrieval; các tool được partition theo specialist và không có peer-to-peer delegation.

Tuy nhiên, phần thực nghiệm hiện tại chưa đặt câu hỏi trung tâm theo kiểu:

> **Kiến trúc multi-agent được đề xuất có thực sự đem lại khác biệt đáng kể so với một kiến trúc single-agent tương đương hay không?**

Thay vào đó, ba hướng đánh giá hiện tại chủ yếu là:

1. retrieval stacking: BM25 → dense → hybrid → reranker → full retrieval;
2. generation/retrieval ablation;
3. tool ambiguity stress test với 11/31/51 tools.

Ba hướng này đều có liên quan đến hệ thống, nhưng chúng chủ yếu kiểm tra **các submechanism**. Chúng chưa trực tiếp kiểm tra **giá trị của toàn kiến trúc supervisor + bounded specialists + scoped tools + heterogeneous evidence paths**.

Vì vậy, bài mới nên thay đổi logic như sau:

> **Đề xuất kiến trúc → so sánh kiến trúc với đối chứng tương đương → tháo từng thành phần để xem cơ chế nào đóng góp → stress-test cơ chế specialization khi tool registry trở nên khó hơn.**

Đây sẽ là xương sống của toàn bài.

---

# 2. Thesis mới của bài báo

## 2.1. Câu chuyện trung tâm

Không nên bán paper như “multi-agent tốt hơn single-agent” một cách tổng quát.

Nên định vị chính xác hơn:

> **CTU-Chat là một supervisor-routed, bounded-specialist architecture trong đó specialization không chỉ nằm ở prompt, mà còn nằm ở evidence representation, tool visibility và deterministic execution policy.**

Giả thuyết cần kiểm tra là:

> Khi một hệ thống tư vấn đại học phải xử lý nhiều dạng tri thức khác nhau và nhiều tool có ngữ nghĩa gần nhau, việc route truy vấn tới specialist với evidence/tool scope phù hợp có thể cải thiện độ tin cậy end-to-end ở một số điều kiện, nhưng phải đánh đổi bằng latency và coordination cost.

Đây là claim vừa đủ mạnh để thú vị, nhưng không overclaim.

---

# 3. Ba Research Questions mới

## RQ1 — Architecture-Level Effectiveness

> **RQ1: How does the proposed supervisor-routed multi-agent architecture compare with a functionally matched single-agent architecture in end-to-end counseling reliability, evidence grounding, and computational cost?**

Tiếng Việt:

> **Kiến trúc supervisor-routed multi-agent của CTU-Chat khác gì so với một single-agent có cùng model, cùng knowledge, cùng tools và cùng retrieval stack về độ đúng end-to-end, grounding và chi phí vận hành?**

### Ý nghĩa

Đây phải là câu hỏi quan trọng nhất, vì nó test trực tiếp contribution C1: kiến trúc multi-agent.

---

## RQ2 — Architectural Mechanism and Ablation

> **RQ2: What are the contributions of specialist policies, scoped tool access, representation-specific evidence allocation, and deterministic computation to CTU-Chat's end-to-end behavior?**

Tiếng Việt:

> **Những thành phần nào của kiến trúc — specialist policy, tool isolation, heterogeneous evidence allocation, deterministic arithmetic — thực sự tạo ra khác biệt?**

### Ý nghĩa

RQ1 cho biết toàn hệ thống có khác biệt hay không. RQ2 giải thích **tại sao**.

---

## RQ3 — Robustness under Tool Ambiguity

> **RQ3: How does bounded specialist routing affect tool-selection reliability and computational cost as semantically overlapping tools expand the registry?**

Tiếng Việt:

> **Khi số tool gần nghĩa tăng, bounded specialization giữ được reliability như thế nào và phải trả giá bao nhiêu về token/latency?**

### Ý nghĩa

Đây là stress test của cơ chế specialization. Phần semantic-neighbor experiment hiện tại có thể giữ lại gần như nguyên vẹn, nhưng nên đặt ở vị trí RQ3 thay vì làm thành câu chuyện chính.

---

# 4. Scenario 1 — End-to-End Architecture Comparison

## 4.1. Mục tiêu

Scenario này phải trả lời trực tiếp RQ1:

> Có gì khác khi dùng full CTU-Chat multi-agent thay vì một single-agent được cấp cùng capability?

Đây là experiment hiện bài thiếu nhất.

---

## 4.2. Nguyên tắc quan trọng nhất: baseline phải functionally matched

Không được tạo một single-agent baseline yếu một cách giả tạo.

Single-agent baseline phải dùng:

- cùng LLM;
- cùng temperature;
- cùng knowledge sources;
- cùng Neo4j graph;
- cùng BM25/dense/reranker stack;
- cùng structured tuition data;
- cùng calculators;
- cùng production tools;
- cùng answer-generation constraints;
- cùng retry/tool-call budget ở mức có thể match công bằng.

Khác biệt chính chỉ nên là **orchestration architecture**.

Nếu không làm vậy, reviewer có thể nói kết quả đến từ capability mismatch chứ không phải architecture.

---

## 4.3. Các configuration nên chạy

### S1-A. Unified Single Agent — Full Capability Baseline

Một agent duy nhất nhìn thấy toàn bộ production tools và evidence interfaces.

**Có:**

- Neo4j graph tools;
- tuition lookup;
- scholarship lookup/calculation;
- document retrieval;
- deterministic calculators;
- chat history;
- same generator model.

**Không có:**

- supervisor;
- domain routing;
- separate specialist prompts;
- partitioned tool privileges.

### Prompt design

Prompt phải mô tả rõ tool contracts, khi nào dùng graph, khi nào retrieval, khi nào calculator.

Không nên cố tình viết prompt kém hơn specialist prompts.

### Mục đích

Đây là đối chứng trực tiếp cho câu hỏi:

> Một LLM với tất cả capability có cần decomposition thành multi-agent hay không?

---

### S1-B. Routed Generic Worker

Có supervisor route domain, nhưng worker phía sau dùng một policy chung/generic.

**Có:**

- supervisor;
- domain route;
- evidence path tương ứng;
- scoped tool registry.

**Không có:**

- specialist-specific contrastive prompt/policy.

### Mục đích

Tách hai hiệu ứng:

1. hiệu ứng của routing/scoping;
2. hiệu ứng của specialist policy.

Nếu B đã tốt hơn A, routing/scoping có đóng góp.

Nếu C tốt hơn B, specialist policy có đóng góp thêm.

---

### S1-C. Full CTU-Chat — Proposed Architecture

Đúng architecture đề xuất:

`Query → History/Rewrite → Supervisor → Contract Check/Repair → Evidence Path → Specialist → Tool/Generation → Answer`

Bao gồm:

- supervisor structured decision;
- route repair;
- four specialists;
- scoped tools;
- heterogeneous evidence paths;
- deterministic calculations;
- final answer generation.

---

## 4.4. Dataset cho Scenario 1

Có thể giữ bộ 100 held-out queries hiện tại, nhưng nên audit lại kỹ vì giờ nó là benchmark chính của architecture.

### Minimum composition

Nên giữ hoặc tái tạo phân bố tương tự:

- 40 direct single-hop;
- 20 within-domain multi-hop;
- 20 cross-domain;
- 10 entity comparison;
- 5 temporal;
- 5 adversarial.

Ngoài ra nên annotate mỗi query theo các dimension sau:

- domain;
- required evidence type;
- requires tool? yes/no;
- requires graph traversal? yes/no;
- requires deterministic calculation? yes/no;
- requires multiple sources? yes/no;
- cross-domain? yes/no;
- needs clarification? yes/no;
- adversarial or malformed? yes/no.

Những annotation này giúp breakdown failure rõ hơn.

---

## 4.5. Cross-domain queries phải được đặc biệt chú ý

Đây là điểm dễ bị reviewer hỏi nhất, vì kiến trúc route tới một specialist nhưng benchmark có cross-domain questions.

Cần định nghĩa rõ một trong các policy sau:

### Option 1 — Single-owner with multi-evidence prefetch

Supervisor chọn một owner specialist nhưng retrieval layer được phép thu thập evidence từ nhiều domain trước khi giao cho owner.

### Option 2 — Sequential specialist composition

Supervisor cho phép một bounded two-step path, ví dụ Academic → Financial hoặc ngược lại.

### Option 3 — Cross-domain composite specialist

Thêm một cross-domain synthesis node chỉ dùng khi query cần evidence từ nhiều domain.

Nếu không muốn sửa architecture, Option 1 hợp nhất với implementation hiện tại nhất.

Nhưng phải mô tả cực rõ:

- ai là owner;
- evidence nào được phép lấy ngoài domain;
- specialist cuối có được dùng tool ngoài scope hay không;
- nếu cần hai tools ở hai domains thì xử lý thế nào.

### Cross-domain reporting

Bắt buộc report riêng:

- answer correctness;
- source recall;
- required-fact coverage;
- tool execution success;
- latency;
- route repair rate.

Không chỉ report aggregate.

---

## 4.6. Repetitions

Khuyến nghị:

- **3 repetitions/query/configuration** nếu ngân sách vừa phải;
- tốt hơn: **5 repetitions** nếu stochasticity đáng kể;
- temperature = 0 vẫn nên repeat vì backend/model serving có thể không hoàn toàn deterministic.

Với 100 queries × 3 configs × 3 reps:

- 900 end-to-end runs.

Nếu 5 reps:

- 1,500 runs.

---

## 4.7. Metrics cho Scenario 1

Nên chia metric thành 4 nhóm.

### A. Final-answer quality

- Answer Correctness;
- Answer Relevancy;
- Faithfulness;
- Required-Fact Coverage;
- citation/source correctness nếu answer có source IDs;
- hallucinated-fact count nếu có thể đánh programmatically/human review.

### B. Evidence quality

- Source Recall;
- Source AP;
- Context Recall;
- Context Precision;
- Hit@k/MRR chỉ dùng ở subsystem analysis, không nên là headline metric của S1.

### C. Execution reliability

Chỉ áp dụng cho các query cần tool:

- Tool Selection Accuracy;
- Argument Exact/Contract Match;
- Result Accuracy;
- E2E Tool Pass;
- invalid parameter rate;
- unnecessary tool-call rate;
- clarification correctness;
- bounded-execution rate;
- route repair rate;
- execution runtime-error rate.

### D. Operational cost

- input tokens;
- output tokens;
- total tokens;
- number of LLM calls;
- number of retrieval calls;
- number of tool calls;
- wall-clock latency;
- p50/p95 latency;
- optional estimated cost/query.

---

## 4.8. Primary endpoints

Không nên có 15 metric mà không biết metric nào quan trọng.

Nên predefine primary endpoints.

### Primary reliability endpoints

1. **End-to-End Success Rate**
2. **Answer Correctness**
3. **Faithfulness**
4. **Source Recall**

### Primary cost endpoints

5. **Input Tokens**
6. **Latency**

Các metric còn lại là secondary diagnostics.

---

## 4.9. Định nghĩa End-to-End Success Rate mới

Nên định nghĩa theo query type.

### Với retrieval/generation query

Pass nếu:

- required facts đạt threshold;
- answer không chứa unsupported critical claim;
- required sources được retrieved;
- answer đáp ứng user intent.

### Với tool query

Pass nếu đồng thời:

- đúng route hoặc route được repair hợp lệ;
- đúng tool;
- arguments hợp lệ;
- tool result đúng oracle;
- final answer phản ánh đúng result;
- không có execution error.

### Với adversarial/clarification query

Pass nếu:

- không gọi tool không cần thiết;
- trả clarification/refusal theo expected behavior;
- không hallucinate answer.

Nên ghi rõ rubric trước khi chạy.

---

## 4.10. Statistical analysis cho Scenario 1

Vì các configuration chạy trên cùng query, đây là paired design.

Khuyến nghị:

1. Average repetitions within query trước.
2. Tính paired difference giữa configs theo query.
3. Dùng **10,000 query-level bootstrap resamples** cho 95% CI.
4. Report cả point estimate và CI.
5. Không chỉ report p-value.

Ví dụ:

- Full CTU-Chat − Unified Single Agent;
- Full CTU-Chat − Routed Generic;
- Routed Generic − Unified Single Agent.

### Với binary E2E pass

Có thể thêm:

- paired bootstrap CI;
- McNemar test như secondary analysis.

### Multiple comparisons

Nếu report quá nhiều pairwise tests, nên:

- xác định trước 2–3 primary comparisons;
- các comparison khác ghi exploratory;
- hoặc dùng Holm correction cho inferential tests.

---

# 5. Scenario 2 — Architectural Ablation

## 5.1. Mục tiêu

Scenario 2 trả lời RQ2:

> Thành phần nào của architecture tạo ra behavior quan sát được ở Scenario 1?

Điểm quan trọng: ablation phải ánh xạ trực tiếp lên các khối trong architecture diagram.

Reviewer nhìn Figure architecture rồi nhìn ablation table phải hiểu ngay từng row đã tháo khối nào.

---

## 5.2. Configurations đề xuất

### S2-A0. Full CTU-Chat

Control/reference.

Bao gồm đầy đủ:

- supervisor;
- route repair;
- specialist policies;
- scoped tools;
- representation-specific evidence paths;
- deterministic computation.

---

### S2-A1. No Specialist Policy

Giữ:

- supervisor;
- route;
- evidence path;
- tool scopes.

Thay:

- domain-specific specialist prompts bằng một generic worker policy.

### Câu hỏi nó trả lời

> Specialist policy thực sự đóng góp hay chỉ cần route + scoped tools là đủ?

### Expected interpretation

Nếu Full > No Specialist Policy ở tool selection/E2E:

- specialist policy có thêm giá trị.

Nếu gần như bằng nhau:

- phần lợi ích chủ yếu đến từ routing/scoping chứ không phải prompt specialization.

Không được cố ép conclusion.

---

### S2-A2. No Tool Isolation / Full Tool Visibility

Giữ:

- supervisor;
- specialist prompts;
- evidence paths.

Thay:

- mỗi specialist nhìn thấy toàn bộ production tools.

### Câu hỏi

> Partitioned tool privileges có giảm semantic confusion và tool misuse không?

### Metrics trọng tâm

- tool selection;
- unnecessary tool calls;
- argument errors;
- E2E pass;
- input tokens;
- latency.

---

### S2-A3. Uniform Evidence Representation

Giữ:

- supervisor;
- specialists;
- tool policy nếu có thể.

Thay:

- ép tất cả institutional knowledge qua một uniform document retrieval path.

Ví dụ:

- curriculum cũng chuyển thành text chunks;
- tuition tables cũng index như documents;
- regulations vẫn documents.

Không dùng graph traversal riêng cho curriculum trong config này.

### Câu hỏi

> Heterogeneous evidence allocation có thực sự cần thiết so với “RAG everything” không?

### Metrics trọng tâm

- Source Recall;
- Fact Coverage;
- correctness ở prerequisite/multi-hop queries;
- correctness ở cohort-specific tuition queries;
- faithfulness;
- latency.

### Quan trọng

Uniform baseline phải được xây cẩn thận. Nếu text conversion của graph quá sơ sài, reviewer sẽ nói baseline bị handicap.

Nên document rõ cách serialize graph/curriculum thành text.

---

### S2-A4. No Deterministic Calculation

Chỉ chạy trên subset có arithmetic.

Giữ:

- retrieval;
- structured lookup;
- specialist.

Thay:

- LLM tự tính kết quả thay vì gọi deterministic calculator.

### Câu hỏi

> Deterministic arithmetic có tăng numeric reliability không?

### Metrics

- exact numeric accuracy;
- unit correctness;
- percentage application correctness;
- final-answer correctness;
- hallucinated arithmetic rate;
- latency/token difference.

### Lưu ý

Đây là một subset experiment. Không cần ép nó chạy trên toàn 100 queries.

---

### S2-A5. No Route Repair — Optional but Valuable

Giữ raw supervisor output, bỏ deterministic ownership contract/repair.

### Câu hỏi

> Route repair đóng góp gì vào robustness?

### Metrics

- raw route accuracy;
- repaired route accuracy;
- end-to-end pass;
- wrong-domain tool invocation;
- clarification rate.

Config này rất ăn với kiến trúc vì route repair đang là một design choice rõ ràng.

Nếu ngân sách hạn chế, A5 có thể là experiment phụ.

---

## 5.3. Không nên đưa mọi retrieval baseline vào ablation chính

BM25, dense, hybrid, reranker vẫn có giá trị, nhưng nên chuyển thành:

> **Supporting Retrieval Subsystem Evaluation**

Chúng dùng để chứng minh evidence stack được xây hợp lý, không phải để đại diện cho kiến trúc multi-agent.

---

## 5.4. Dataset cho Scenario 2

Có thể dùng cùng 100 held-out queries để tận dụng paired comparison.

Nhưng nên report cả:

- aggregate;
- query-type-specific;
- evidence-type-specific.

### Breakdown đặc biệt nên có

#### Graph-sensitive subset

Ví dụ:

- prerequisite chain;
- shared courses;
- program comparison;
- reverse course-to-program lookup.

#### Structured-financial subset

- cohort tuition lookup;
- exemption basis;
- tuition reduction.

#### Narrative-regulation subset

- policy interpretation;
- scholarship eligibility;
- administrative procedures.

#### Cross-domain subset

- query cần 2 loại evidence trở lên.

Ablation sẽ dễ hiểu hơn rất nhiều nếu cho thấy component nào ảnh hưởng mạnh nhất ở đúng loại query mà nó được thiết kế để xử lý.

---

## 5.5. Ablation reporting

Một bảng chính nên có dạng:

| Config | Answer Corr. | Faith | Fact Cov. | Src Recall | Tool Acc. | E2E Pass | Input Tok. | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Full CTU-Chat | | | | | | | | |
| No specialist policy | | | | | | | | |
| Full tool visibility | | | | | | | | |
| Uniform evidence | | | | | | | | |
| No deterministic calc. | subset | subset | subset | subset | subset | subset | | |
| No route repair | | | | | | | | |

Sau đó có một bảng hoặc figure breakdown theo query family.

---

# 6. Scenario 3 — Semantic-Neighbor Tool Ambiguity Stress Test

## 6.1. Mục tiêu

Scenario này kiểm tra cơ chế specialization trong điều kiện tool registry trở nên khó hơn.

Đây là nơi experiment 11 → 31 → 51 tools hiện tại phát huy giá trị.

---

## 6.2. Configurations giữ lại

### S3-C1. Full-Registry Single Agent

Single agent nhìn toàn bộ tool registry.

### S3-C2. Global Top-k Single Agent

Một global retriever/gate lấy Top-k tools rồi single agent chọn.

Giữ k cố định, ví dụ k = 10.

### S3-C3. Routed Generic

Supervisor route domain → generic downstream gate với scoped candidate set.

### S3-C4. Routed Specialist

Supervisor route domain → specialist downstream gate với contrastive use/avoid rules.

---

## 6.3. Registry sizes

Giữ ba mức:

- 11 tools;
- 31 tools;
- 51 tools.

Nếu có ngân sách, thêm 71 hoặc 91 tools sẽ giúp nói về trend tốt hơn.

Tuy nhiên, nếu distractor tools là synthetic/evaluation-only, càng tăng nhiều càng phải chứng minh chúng plausible.

---

## 6.4. Semantic-neighbor construction protocol

Đây là chỗ phải làm reproducibility tốt hơn bản hiện tại.

Mỗi production tool family nên có:

- canonical tool;
- 2–4 semantic neighbors;
- mô tả use case;
- contrastive boundary;
- expected gold cases;
- examples of confusing queries.

Ví dụ dạng tài liệu:

| Tool family | Canonical tool | Neighbor | Main distinction |
|---|---|---|---|
| Tuition lookup | lookup_tuition | lookup_tuition_by_cohort | cohort explicitly required |
| Tuition lookup | lookup_tuition | lookup_tuition_policy | asks policy text, not amount |
| Program info | lookup_program | compare_programs | one entity vs two entities |

Không nhất thiết dùng đúng các tên này; mục tiêu là reviewer nhìn thấy distractors không phải được bịa vô lý để “gài” baseline.

---

## 6.5. Primary cases

Giữ fixed-case design.

Khuyến nghị:

- ít nhất 50 production-tool cases;
- cân bằng theo tool family;
- mỗi case có gold tool;
- gold arguments;
- deterministic expected result nếu có.

Mỗi case chạy:

- mỗi registry size;
- mỗi configuration;
- 3 order blocks hoặc nhiều random order seeds.

---

## 6.6. Coverage suite

Coverage suite hiện tại là ý tưởng tốt nhưng chỉ one repetition thì yếu.

Bản mới nên:

- mỗi semantic-neighbor tool được làm gold ít nhất một lần;
- tốt hơn: 2–3 cases/tool;
- tối thiểu 3 repetitions/case;
- counterbalance tool order.

Như vậy có thể chứng minh system không chỉ giỏi tránh distractor mà còn thật sự chọn được neighbor khi neighbor là đúng tool.

---

## 6.7. Metrics cho Scenario 3

### Tool accessibility

- Gold@k;
- mean visible tool count.

### Selection quality

- selection accuracy;
- family-level macro-F1 nếu classes lệch;
- confusion matrix theo tool family.

### Execution quality

- Argument EM/Contract Match;
- Result Accuracy;
- E2E Pass;
- bounded execution.

### Cost

- input tokens;
- output tokens;
- latency;
- LLM call count.

### Failure taxonomy

Nên log riêng:

- wrong tool same family;
- wrong tool cross-family;
- gold tool omitted from Top-k;
- correct tool, wrong args;
- runtime error;
- schema-guard failure;
- unnecessary clarification.

---

## 6.8. Statistical analysis cho Scenario 3

Không chỉ so 11 vs 51 bằng point estimate.

Nên làm hai lớp analysis.

### Layer 1 — Fixed-level comparisons

Tại mỗi registry size:

- Routed Specialist − Global Top-k;
- Routed Specialist − Routed Generic;
- Routed Specialist − Full Registry.

Report paired bootstrap CI.

### Layer 2 — Degradation / interaction

Đánh giá change từ low → high registry:

`Δ = score_51 − score_11`

Sau đó interaction:

`Δ_specialist − Δ_baseline`

Nếu CI chứa zero, phải nói inconclusive.

Không nên gọi là scaling advantage nếu chỉ có 3 registry sizes và interaction không significant.

### Nếu có thể thêm registry levels

Ví dụ 11, 21, 31, 41, 51, 71.

Khi đó có thể fit mixed-effects/logistic model:

- fixed effects: architecture, registry size, interaction;
- random intercept by case/tool family.

Cái này mạnh hơn rất nhiều cho scaling claims.

---

# 7. Supporting Evaluation — Retrieval Subsystem

Phần retrieval hiện tại vẫn nên giữ, nhưng không còn là một trong ba main RQs.

## 7.1. Mục tiêu

Chứng minh evidence subsystem được lựa chọn hợp lý trước khi dùng nó trong architecture-level experiments.

## 7.2. Configurations

- BM25;
- dense;
- hybrid RRF;
- hybrid + reranker;
- full representation-aware retrieval.

## 7.3. Metrics

- Hit@1;
- Hit@3;
- Recall@5;
- MRR@10;
- Precision@5;
- latency.

## 7.4. Cách viết trong paper

Không nói:

> “RQ3 asks whether our retrieval method is better.”

Nên nói:

> “We first validate the evidence retrieval subsystem to ensure that architecture-level comparisons are not confounded by a weak evidence backend.”

Hoặc:

> “This analysis is supporting rather than a principal architectural research question.”

---

# 8. Fairness controls giữa các architectures

Đây là phần cực kỳ quan trọng.

## 8.1. Same generator

Tất cả configs dùng cùng model version.

Ghi rõ exact model identifier và evaluation date.

## 8.2. Same decoding

- temperature;
- top-p;
- max output tokens;
- seed nếu API hỗ trợ.

## 8.3. Same knowledge snapshot

Freeze:

- document corpus;
- graph snapshot;
- tuition records;
- tool schemas.

Không update giữa các experiment batches.

## 8.4. Same retrieval budget

Nếu compare retrieval/generation, nên cố giữ tương đương:

- candidate count;
- reranker top-k;
- final context budget.

Nếu architecture cố tình dùng scope nhỏ hơn, report rõ đó là architectural effect chứ không giấu.

## 8.5. Same maximum execution budget

Ví dụ:

- max tool calls/query;
- max retries;
- max clarification loops.

Nếu CTU-Chat có two-hop supervisor + worker nhưng single-agent chỉ one call, phải report call count và token/latency để người đọc thấy trade-off.

---

# 9. Logging schema nên chuẩn hóa từ đầu

Mỗi run nên ghi một JSON record đầy đủ.

Ví dụ schema khái niệm:

```json
{
  "query_id": "Q042",
  "configuration": "full_ctuchat",
  "repetition": 2,
  "query_type": "cross_domain",
  "gold_domain": ["academic", "financial"],
  "raw_route": "financial",
  "repaired_route": "financial",
  "repair_reason": null,
  "visible_tools": ["..."],
  "selected_tool": "...",
  "gold_tool": "...",
  "arguments": {},
  "argument_match": true,
  "tool_result": "...",
  "result_correct": true,
  "retrieved_source_ids": ["..."],
  "gold_source_ids": ["..."],
  "final_answer": "...",
  "input_tokens": 0,
  "output_tokens": 0,
  "latency_ms": 0,
  "runtime_error": null,
  "schema_guard_failure": false
}
```

Phải log cả raw và repaired route nếu route repair là contribution.

---

# 10. Human evaluation nên thêm hay không?

Nếu có manpower, nên thêm một human-evaluation subset vì paper hiện phụ thuộc khá nhiều vào automated metrics/Ragas.

## 10.1. Sample

Khoảng 30–50 queries, stratified theo query type.

## 10.2. Blind evaluation

Reviewer không biết answer thuộc config nào.

## 10.3. Rubric

Chấm 1–5 hoặc binary trên:

- factual correctness;
- completeness;
- grounding/source support;
- harmful/misleading advisory risk;
- clarity/usefulness.

## 10.4. Inter-rater agreement

Ít nhất 2 raters/query.

Report:

- Cohen’s kappa cho binary;
- weighted kappa hoặc ICC cho ordinal score.

Human evaluation không bắt buộc, nhưng sẽ làm paper mạnh lên rõ rệt, nhất là vì đây là counseling system.

---

# 11. Latency measurement phải làm lại cho sạch

Bản hiện tại có retrieval latency vài milliseconds cho BM25/dense nhưng reranker/full stack lên hàng chục giây. Điều này có thể đúng với GTX 1650, nhưng reviewer sẽ hỏi rất kỹ.

Bản chạy lại nên tách latency thành components:

- routing latency;
- retrieval latency;
- reranking latency;
- graph query latency;
- tool execution latency;
- generation latency;
- total end-to-end latency.

## 11.1. Warm vs cold

Report rõ:

- model warmed up hay chưa;
- first-run excluded hay included;
- reranker model load time có tính vào mỗi query không;
- database caches có warm không.

## 11.2. p50/p95

Không chỉ average latency.

Nên report:

- mean;
- median (p50);
- p95.

## 11.3. Hardware note

Nếu dùng GTX 1650 4GB, ghi rõ đây là evaluation hardware, không đại diện production deployment.

---

# 12. Failure analysis bắt buộc nên có

Một architecture paper rất cần failure analysis.

Nên annotate ít nhất các nhóm lỗi sau:

## Routing failures

- wrong domain;
- wrong intent;
- route repair failed;
- ambiguous query unresolved.

## Retrieval failures

- gold source absent;
- wrong cohort;
- cross-domain evidence omitted;
- reranker demoted gold source.

## Tool failures

- wrong tool;
- correct family but wrong semantic neighbor;
- wrong argument;
- runtime error;
- schema guard failure.

## Generation failures

- ignores correct tool result;
- arithmetic restatement error;
- unsupported policy statement;
- incomplete multi-source synthesis.

## Safety/robustness failures

- should clarify but guesses;
- unnecessary refusal;
- adversarial query causes tool misuse.

Nên có một table khoảng 20–30 failure cases manually classified.

---

# 13. Revised paper structure

## 1. Introduction

Đi thẳng vào problem:

- heterogeneous institutional knowledge;
- tool ambiguity;
- need for bounded specialization;
- trade-off between reliability and coordination cost.

Kết thúc Introduction bằng 3 RQs mới.

## 2. Related Work

Giữ:

- RAG;
- GraphRAG;
- agentic tool use;
- educational advising systems.

Giảm bớt thuật ngữ tự đặt nếu không cần.

## 3. CTU-Chat Architecture

### 3.1 Overall architecture

### 3.2 Supervisor and route contract

### 3.3 Specialist agents and tool scopes

### 3.4 Representation-specific evidence paths

### 3.5 Deterministic execution

### 3.6 Cross-domain query handling

Phần 3.6 rất nên bổ sung.

## 4. Experimental Setup

### 4.1 Dataset and annotation

### 4.2 Baselines and matched controls

### 4.3 Metrics

### 4.4 Statistical protocol

### 4.5 Supporting retrieval subsystem validation

## 5. Results

### 5.1 Scenario 1 — Architecture-level comparison

### 5.2 Scenario 2 — Architectural ablation

### 5.3 Scenario 3 — Tool ambiguity stress test

### 5.4 Failure analysis

## 6. Discussion

Trả lời đúng RQ1 → RQ2 → RQ3.

## 7. Threats to Validity

## 8. Conclusion

---

# 14. Contribution statements nên viết lại

## C1 — Supervisor-Routed Bounded Multi-Agent Architecture

> We design a centralized supervisor that dispatches each query to a bounded specialist with isolated tool privileges and representation-specific evidence access.

## C2 — Architecture-Level Comparative Evaluation

> We compare CTU-Chat with functionally matched single-agent and routed-generic alternatives under the same model, knowledge, and tool capabilities.

Đây là contribution hiện paper còn thiếu về mặt thực nghiệm.

## C3 — Mechanism and Stress-Test Analysis

> We perform architectural ablations and semantic-neighbor tool-registry stress tests to isolate the effects of specialization, tool scoping, heterogeneous evidence allocation, and registry ambiguity.

Nếu vẫn muốn giữ retrieval contribution, cho nó thành secondary contribution hoặc một phần của C3.

---

# 15. Cách diễn giải kết quả sau khi chạy lại

Không nên viết trước rằng CTU-Chat sẽ thắng.

Có vài outcome đều publishable.

## Outcome A — Multi-agent tốt hơn rõ ở reliability, chậm hơn

Story:

> bounded specialization improves reliability under heterogeneous evidence/tool ambiguity, at the cost of additional coordination latency.

Đây là outcome đẹp nhất.

## Outcome B — Gần như ngang single-agent nhưng tool misuse ít hơn

Story:

> architecture does not uniformly improve answer metrics but provides bounded execution and lower tool-confusion risk.

Vẫn tốt.

## Outcome C — Single-agent ngang hoặc hơn phần lớn metric

Story:

> multi-agent decomposition should not be assumed beneficial; its value appears conditional on ambiguity, tool scope, or safety constraints.

Nếu Scenario 3 vẫn cho thấy specialist tốt hơn khi tool registry khó, paper thậm chí còn thú vị:

> multi-agent specialization is not universally superior but becomes useful under specific operational complexity.

Đây là conclusion khoa học hơn nhiều so với ép “multi-agent wins”.

---

# 16. Minimum rerun plan nếu thời gian/ngân sách hạn chế

Nếu chỉ đủ chạy thêm một experiment lớn, ưu tiên như sau.

## Priority 1 — Must run

### Unified Single Agent vs Full CTU-Chat

- 100 held-out queries;
- 3 reps;
- same model/tools/knowledge;
- answer + evidence + tool + cost metrics.

Đây là experiment quan trọng nhất.

## Priority 2 — Strongly recommended

### Routed Generic vs Full CTU-Chat

Có thể reuse logic từ current Scenario 3 nhưng chạy end-to-end trên 100-query benchmark.

## Priority 3 — Recommended

### No Tool Isolation

Cho specialist thấy toàn production tools.

## Priority 4 — Recommended

### Uniform Evidence Representation

Graph/structured data được chuyển sang common RAG path.

## Priority 5 — Keep existing stress test

11/31/51 tool semantic-neighbor experiment, nhưng rerun coverage suite có repetitions tốt hơn.

---

# 17. Full recommended run matrix

Giả sử 100 queries, 3 repetitions.

## Scenario 1

- Unified Single Agent: 300 runs
- Routed Generic: 300 runs
- Full CTU-Chat: 300 runs

**Total: 900 runs**

## Scenario 2

- Full CTU-Chat: có thể reuse 300 runs từ S1
- No Specialist Policy: có thể reuse Routed Generic nếu protocol giống hệt
- No Tool Isolation: 300 runs
- Uniform Evidence: 300 runs
- No Route Repair: 300 runs
- No Deterministic Calculation: chỉ numeric subset, ví dụ 20 queries × 3 = 60 runs

Nếu reuse tốt, thêm khoảng **960 runs**.

## Scenario 3

Giữ fixed-case design:

- 50 cases;
- 4 configs;
- 3 registry sizes;
- 3 order/repetition blocks.

= **1,800 decisions**

Coverage suite nên nâng từ 1 rep lên 3 reps.

Nếu 40 neighbor tools × 4 configs × 3 reps:

= **480 additional decisions**

### Tổng gần đúng

- End-to-end architecture/ablation: ~1,860 runs
- Tool ambiguity: ~2,280 decisions

Có thể giảm bằng cách reuse configurations và chỉ chạy subset cho ablations domain-specific.

---

# 18. Bảng kết quả nên chuẩn bị trước

## Table A — Architecture-Level Comparison

| Architecture | E2E Success | Answer Corr. | Faith | Fact Cov. | Src Recall | Tool Acc. | Input Tok. | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Unified Single | | | | | | | | |
| Routed Generic | | | | | | | | |
| Full CTU-Chat | | | | | | | | |

Thêm 95% CI cho pairwise deltas trong text hoặc table phụ.

---

## Table B — Architectural Ablations

| Config | Δ E2E | Δ Faith | Δ Src Recall | Δ Tool Acc. | Δ Tokens | Δ Latency |
|---|---:|---:|---:|---:|---:|---:|
| No specialist policy | | | | | | |
| Full tool visibility | | | | | | |
| Uniform evidence | | | | | | |
| No route repair | | | | | | |
| No deterministic calc. | | | | | | |

Reference = Full CTU-Chat.

---

## Table C — Tool Ambiguity

| Registry | Architecture | Gold@10 | Selection | Arg Match | E2E Pass | Visible | Input Tok. | Latency |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 11 | Full Registry Single | | | | | | | |
| 11 | Global Top-10 | | | | | | | |
| 11 | Routed Generic | | | | | | | |
| 11 | Routed Specialist | | | | | | | |
| ... | ... | | | | | | | |

---

# 19. Figures nên có

## Figure 1 — Clean architecture figure

Nên đơn giản hơn implementation diagram hiện tại.

Flow chính:

`User → Supervisor → Specialist → Evidence/Tools → Response`

Bên dưới specialist chỉ ghi backend chính:

- Academic → Neo4j graph
- Financial → structured data + calculator
- Scholarship → retrieval + calculator
- General → document retrieval

Route repair và retrieval details có thể đưa sang Figure 2.

## Figure 2 — Experiment design

Một figure rất có giá trị:

- Same model/knowledge/tools
- split thành Unified Single vs Routed Generic vs Full CTU-Chat
- nhấn mạnh cái gì được controlled.

## Figure 3 — Tool-registry stress curve

X-axis: registry size.

Y-axis:

- E2E pass;
- selection accuracy;
- tokens;
- latency.

Mỗi architecture một line.

Không nên claim asymptotic scaling từ ba points; figure chỉ để minh họa trend.

---

# 20. Checklist trước khi chạy

## Benchmark

- [ ] Freeze 100-query held-out set
- [ ] Audit duplicate/leakage
- [ ] Annotate query types
- [ ] Annotate required tools
- [ ] Annotate gold sources
- [ ] Annotate required facts
- [ ] Annotate cross-domain ownership policy

## Configurations

- [ ] Unified Single Agent
- [ ] Routed Generic
- [ ] Full CTU-Chat
- [ ] No Tool Isolation
- [ ] Uniform Evidence
- [ ] No Route Repair
- [ ] No Deterministic Calculation subset

## Fairness

- [ ] Same model
- [ ] Same temperature
- [ ] Same corpus snapshot
- [ ] Same tool schemas
- [ ] Same retrieval data
- [ ] Comparable context/tool-call budgets
- [ ] Exact prompt versions archived

## Logging

- [ ] Raw route
- [ ] Repaired route
- [ ] Visible tool list
- [ ] Tool selection
- [ ] Arguments
- [ ] Tool results
- [ ] Retrieved source IDs
- [ ] Final answer
- [ ] Tokens
- [ ] Latency components
- [ ] Runtime errors

## Statistics

- [ ] Repetitions averaged within query
- [ ] Paired bootstrap CIs
- [ ] Primary comparisons declared in advance
- [ ] Query-level resampling, not raw-turn resampling
- [ ] Interaction analysis for registry growth

## Reproducibility

- [ ] Tool contracts archived
- [ ] Semantic-neighbor definitions published in appendix
- [ ] Prompt templates included
- [ ] Graph schema documented
- [ ] Retrieval hyperparameters documented
- [ ] Hardware/software versions documented

---

# 21. Một phiên bản rất ngắn để giao việc cho nhóm

## RQ1 — Có cần multi-agent không?

Chạy:

1. Unified Single Agent
2. Routed Generic
3. Full CTU-Chat

Trên cùng 100 queries, cùng model/tools/knowledge.

Đo:

- E2E success
- answer correctness
- faithfulness
- source recall
- tool accuracy
- tokens
- latency

---

## RQ2 — Thành phần nào quan trọng?

Từ Full CTU-Chat, ablate:

1. bỏ specialist policy;
2. bỏ tool isolation;
3. bỏ heterogeneous evidence allocation;
4. bỏ deterministic calculator;
5. optional: bỏ route repair.

Đo cùng metrics với RQ1.

---

## RQ3 — Khi tool nhiều lên thì sao?

Giữ stress test:

- 11 tools
- 31 tools
- 51 tools

So:

1. Full-registry Single
2. Global Top-10 Single
3. Routed Generic
4. Routed Specialist

Đo:

- Gold@10
- Selection
- Argument Match
- E2E Pass
- Visible Tools
- Tokens
- Latency

Coverage suite phải rerun với nhiều repetitions hơn.

---

# 22. Kết luận thiết kế

Điểm quan trọng nhất của lần làm lại là **căn thẳng contribution với evaluation**.

Nếu contribution số 1 là:

> supervisor-routed multi-agent architecture,

thì experiment số 1 phải trực tiếp trả lời:

> architecture đó khác gì một single-agent tương đương?

Sau đó mới hỏi:

> thành phần nào tạo ra khác biệt?

và cuối cùng:

> cơ chế specialization có còn hữu ích khi tool ambiguity tăng lên không?

Nếu làm đúng ba tầng này, paper sẽ coherent hơn hẳn:

**Architecture → Controlled comparison → Mechanism ablation → Stress test.**

Đây là cấu trúc nên dùng để viết lại toàn bộ paper.
