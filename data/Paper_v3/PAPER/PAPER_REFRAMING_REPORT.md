# Báo Cáo Tái Định Vị Toàn Diện Bài Báo CTU-Chat (Paper Reframing Report)

**Dự án:** CTU-Chat — Hệ thống Tư vấn Đại học Đa Tác tử Định tuyến Tập trung Phân bổ Tri thức Dị thể  
**Tài liệu bài báo:** `E:\RHNA\1Visual\CTU-chat\PAPER` (`main.tex`, `sections/00`–`05`)  
**Tệp PDF xuất bản:** `E:\RHNA\1Visual\CTU-chat\PAPER\main.pdf`  
**Ground Truth Source Code:** `E:\RHNA\1Visual\CTU-chat\CTU-Chat_bot`  
**Chuẩn định dạng:** Springer Lecture Notes in Computer Science (LNCS) Single-Column  
**Thời gian hoàn thành:** Ngày 10 tháng 09 năm 2026  

---

## 1. Bảng Đối Soát Khung Nghiên Cứu Mới (Reframing Matrix)

| STT | Hạng Mục (Item) | Framing Cũ (Old Framing) | Framing Mới Chuẩn Hóa (New Framing) | Trạng Thái (Final Status) |
|---|---|---|---|---|
| **1** | **Main Contribution (C1)** | Tập trung vào Component Stacking (BM25 + Dense + RRF + BGE Reranker + Neo4j Graph). | **C1 — Centralized Supervisor-Routed, Domain-Specialized Multi-Agent Architecture**: Điều phối 4 specialist agents với không gian tri thức, đường dẫn truy xuất và đặc quyền công cụ bất đối xứng, không peer-to-peer delegation, chia sẻ state qua Redis. | **COMPLETE** (Cập nhật ở Abstract, Intro, Model, Exp, Conclusion) |
| **2** | **Secondary Contribution (C2)** | Phân vùng tài liệu chung theo siêu dữ liệu chính sách (Governance / Subspace Filter). | **C2 — Heterogeneous Knowledge Allocation Framework**: Phân định tri thức theo đặc tính cấu trúc: Chương trình đào tạo quan hệ $\rightarrow$ Neo4j Graph; Biểu phí cấu trúc $\rightarrow$ Tuition Graph / JSON Catalog + Công cụ tính toán chính xác; Quy chế diễn giải $\rightarrow$ Hybrid Document RAG. | **COMPLETE** (Bảng 2, Mục 3.4, Mục 3.7) |
| **3** | **Tertiary Contribution (C3)** | Hybrid RAG Pipeline coi BM25/RRF là novelty độc lập. | **C3 — Representation-Aware Routing and Evidence Acquisition**: Định tuyến truy vấn dựa trên ý định đến đúng biểu diễn tri thức; BM25, Dense, RRF, Cross-encoder là các building blocks đã được kiểm chứng bên trong đường dẫn văn bản. | **COMPLETE** (Mục 1, Mục 3.5, Mục 3.6) |
| **4** | **Research Gaps** | Tập trung vào Component Stacking vs Semantic Drift. | **3 Gaps chuẩn mực**: <br>• **Gap 1**: Limited Domain-Specialized Multi-Agent Orchestration.<br>• **Gap 2**: Uniform Knowledge Representation Fallacy.<br>• **Gap 3**: Lack of Representation-Aware Routing Mechanisms. | **COMPLETE** (Mục 1, Mục 2.6, Bảng 4) |
| **5** | **Research Questions** | RQ1 là Hybrid Retrieval; Multi-Agent chỉ là thứ yếu. | **Đảo thứ tự chuẩn hóa**: <br>• **RQ1 (Chính)**: Domain-Specialized Multi-Agent Architecture.<br>• **RQ2**: Heterogeneous Knowledge Allocation.<br>• **RQ3**: Representation-Aware Evidence Routing. | **COMPLETE** (Mục 1, Mục 4, Mục 4.5) |
| **6** | **Abstract** | Mở đầu bằng Hybrid RAG và Component Stacking. | Đưa **Multi-Agent System lên hàng đầu**; nêu Core Statement; tóm tắt phân bổ tri thức dị thể; báo cáo kết quả thực nghiệm và không có lỗi định tuyến specialist. | **COMPLETE** (Abstract) |
| **7** | **Section 2 (Related Work)** | Mô tả giải pháp CTU-Chat trong Section 2. | **Chỉ phân tích công trình tiền nhiệm**: Phân tích hạn chế của Multi-Agent hiện hữu (broad tool exposure, coordination overhead, lack of isolation) để dẫn vào Gap 1. Không đề cập cụ thể CTU-Chat trong Section 2. | **COMPLETE** (Section 2) |
| **8** | **Figure 1 (Architecture)** | Sơ đồ dạng đường ống tuần tự RAG $\rightarrow$ Agent ở đuôi. | **Sơ đồ 3 tầng lấy Multi-Agent làm trung tâm**: Tier 1 (Supervisor) $\rightarrow$ Tier 2 (4 Domain Specialists với công cụ bất đối xứng) $\rightarrow$ Tier 3 (Các đường dẫn tri thức tách biệt: Graph Path, Structured Path, Hybrid RAG). | **COMPLETE** (Hình 1, Trang 7) |
| **9** | **Figure 2 (Flowchart)** | Sơ đồ khối bị rối, các đường mũi tên và chữ bị chồng lấn (overlapping text/arrows). | **Lưu đồ 4 luồng song song (4-Swimlane Architecture Flowchart)** cực kỳ rõ ràng, chuẩn mực: Tầng trên kiểm tra rewrite và định tuyến Supervisor $\rightarrow$ Thanh bus ngang $\rightarrow$ 4 cột độc lập tương ứng 4 Domains (Academic, Financial, Scholarship, General) với 3 tầng khối thẳng hàng $\rightarrow$ Thu về thanh Collector dưới đáy mà không có bất kỳ mũi tên nào cắt chéo hay đè lên chữ. | **COMPLETE (Đã thiết kế lại hoàn toàn sạch sẽ, không còn rối)** |
| **10** | **Thuật Toán (Algorithms)** | Nằm rải rác hoặc bị đẩy sang phần Thực nghiệm. | **Cả Algorithm 1 (Supervisor Routing) và Algorithm 2 (Evidence Acquisition & Specialist Execution) nằm TRỌN VẸN trong Section 3 (Mục 3.9, Trang 12)**, được khóa vị trí bởi `\FloatBarrier`. | **COMPLETE** (Mục 3.9, Trang 12) |
| **11** | **Xử Lý Học Phí (Tuition Audit)** | Gộp học phí vào văn bản thuần, dễ gây nhầm lẫn là qua BM25/Qdrant. | **Tách bạch Storage vs Runtime Retrieval**: Biểu phí là tri thức cấu trúc dạng bảng/ma trận theo khóa học, được tra cứu ưu tiên qua Neo4j Graph / JSON Catalog và tính toán bằng `tinh_toan_hoc_phi`; văn bản chỉ dùng để tra cứu quy chế miễn giảm. | **COMPLETE** (Mục 3.4, Mục 3.7) |
| **12** | **Cấu Trúc Thực Nghiệm** | Scenario 3 chỉ là đánh giá phụ. | **Ánh xạ thực nghiệm chặt chẽ**: <br>• Scenario 3 trực tiếp giải quyết **RQ1** (Multi-Agent).<br>• Scenario 2 giải quyết **RQ2 + RQ3** (E2E QA & Ablation T1–T7).<br>• Scenario 1 hỗ trợ **RQ2 + RQ3** (Retrieval Stacking E1–E5). | **COMPLETE** (Bảng 4, Mục 4.4) |
| **13** | **Discussion & Conclusion** | Bàn luận bắt đầu từ BM25/Dense. | **Trả lời đúng thứ tự**: RQ1 (Multi-Agent) $\rightarrow$ RQ2 (Knowledge Allocation) $\rightarrow$ RQ3 (Routing). Kết luận khẳng định Multi-Agent là đóng góp cốt lõi số 1. | **COMPLETE** (Mục 4.5, Section 5) |

---

## 2. Ma Trận Ánh Xạ Research Questions ↔ Đóng Góp ↔ Thực Nghiệm ↔ Bằng Chứng

| Research Question (RQ) | Liên Kết Đóng Góp (Contribution) | Thiết Kế Thực Nghiệm (Experiment) | Chỉ Số Đánh Giá (Target Metrics) | Bằng Chứng Thực Nghiệm (Empirical Evidence) | Kết Luận & Trạng Thái |
|---|---|---|---|---|---|
| **RQ1: Domain-Specialized Multi-Agent Architecture** | **C1**: Supervisor trung tâm điều phối 4 Specialists với đặc quyền công cụ bất đối xứng, ràng buộc $\text{max\_iter}=1, \text{max\_tools}=1$, không peer-to-peer. | **Scenario 3**: Multi-Agent Functional Probe Testing (18 kịch bản đa lượt, đa miền) & Bảng phân rã 9 danh mục ($N=150$). | • Tỷ lệ định tuyến sai specialist.<br>• Tuân thủ typed schema công cụ.<br>• Tỷ lệ hoàn thành trong ngân sách thời gian. | • **0/16 trường hợp hoàn tất bị định tuyến sai** ($0.0\%$ wrong-specialist routing error).<br>• $100\%$ lệnh gọi công cụ số học tuân thủ Pydantic schema.<br>• $88.9\%$ hoàn thành trong ngân sách 45s (không deadlock). | **CONFIRMED (RQ1)**: Kiến trúc multi-agent chuyên môn hóa triệt tiêu loop vô hạn và gọi nhầm tool. |
| **RQ2: Heterogeneous Knowledge Allocation** | **C2**: Tách chương trình đào tạo vào Graph, biểu phí vào Graph/JSON + tool số học, quy chế vào Hybrid RAG. | **Scenario 2**: End-to-End QA Ablation (T1–T7 trên 150 câu hỏi, LLM-as-a-judge trên Vertex AI). | • Answer Correctness (AC).<br>• Context Precision (CP).<br>• Context Recall (CR). | • Cắt bỏ phân bổ tri thức dị thể (T7: w/o Governance Filter) khiến **Answer Correctness sụp đổ về 0.398** (thấp nhất trong các biến thể hybrid).<br>• Hệ thống đề xuất (T4) đạt CP cao nhất ($0.749$) và CR ($0.745$). | **CONFIRMED (RQ2)**: Phân bổ tri thức dị thể là điều kiện tiên quyết chống nhiễu chéo khóa học. |
| **RQ3: Representation-Aware Evidence Routing** | **C3**: Định tuyến ý định giữa Graph và Hybrid Document RAG (BM25 + Dense $\rightarrow$ RRF $\rightarrow$ BGE Cross-Encoder $\rightarrow$ Parent Chunks). | **Scenario 1**: Retrieval Component Stacking (E1–E5) & Scenario 2 (T4 vs T5 w/o Reranker). | • Hit@1, Hit@3.<br>• Recall@5, Precision@5.<br>• MRR@10, Latency. | • E5 đạt **0.8667 Hit@1**, **1.0000 Hit@3 và Recall@5**, **0.9222 MRR**.<br>• Tra cứu đồ thị đạt $0.778$ Hit@1 trên câu hỏi tiên quyết đa chặng.<br>• Biểu phí thực tế đạt $0.933$ Hit@1, $0.942$ MRR. | **CONFIRMED (RQ3)**: Định tuyến nhận thức biểu diễn kết hợp reranking giải quyết triệt để sự phân mảnh tri thức. |

---

## 3. Kiểm Tra Chi Tiết Bố Cục Trang và Chuẩn Springer LNCS

1. **Tổng số trang bài báo:** Đúng **18 trang** (không còn trang 19 mồ côi).
2. **Vị trí các thành phần chính:**
   - **Trang 1–3:** Tiêu đề, Tóm tắt (Abstract lấy Multi-Agent làm trung tâm), Từ khóa, Mục 1 (Introduction: Bối cảnh, Dị thể tri thức, Gap 1–3, RQ 1–3, Tuyên ngôn cốt lõi, Đóng góp C1–C3).
   - **Trang 3–5:** Mục 2 (Related Work: 2.1 BM25 & Dense, 2.2 Hybrid RRF, 2.3 KG/GraphRAG, 2.4 Multi-Agent Limitations $\rightarrow$ Gap 1, 2.5 Educational systems, 2.6 Comparative Synthesis $\rightarrow$ Gap 1, 2, 3).
   - **Trang 5–12:** Mục 3 (Proposed Model):
     - Trang 5–6: 3.1 Design Motivation & 5 đặc tính tri thức hành chính.
     - Trang 6–7: 3.2 Overall Architecture & **Hình 1 (Sơ đồ kiến trúc 3 tầng lấy Multi-Agent làm trung tâm)**.
     - Trang 7–8: 3.3 Supervisor-Routed Multi-Agent Architecture & **Bảng 1 (Đặc quyền công cụ và ràng buộc của 4 Agents)**.
     - Trang 8–9: 3.4 Heterogeneous Knowledge Allocation & **Bảng 2 (Bảng phân bổ tri thức dị thể)**.
     - Trang 9–10: 3.5 Representation-Aware Routing Strategy & **Bảng 3 (Tiêu chí lựa chọn đường dẫn truy xuất)**.
     - Trang 10: 3.6 Hybrid Document Retrieval Path & 3.7 Graph-Oriented Retrieval.
     - Trang 11: 3.8 Detailed Activity Flow & **Hình 2 (Lưu đồ hoạt động runtime với các hình thoi quyết định)**.
     - Trang 11–12: 3.9 Algorithmic Specifications & **Algorithm 1 + Algorithm 2 (NẰM TRỌN TRONG PHẦN 3)**.
   - **Trang 12–17:** Mục 4 (Experimental Results):
     - Trang 12–13: 4.1 Benchmark Dataset ($N=150$), 4.2 Infrastructure.
     - Trang 14: 4.3 Evaluation Metrics (Multi-Agent, Retrieval, E2E Ragas).
     - Trang 14–15: **Bảng 4 (RQ Mapping Matrix)**, Scenario 1 (E1–E5) & **Bảng 5 (Retrieval Stacking)**.
     - Trang 15–16: Scenario 2 (T1–T7) & **Bảng 6 (E2E Ragas QA Ablation)**.
     - Trang 16–17: Scenario 3 & **Bảng 7 (Category Breakdown)**, Multi-Agent Functional Probes.
     - Trang 17: 4.5 Discussion (Trả lời RQ1 $\rightarrow$ RQ2 $\rightarrow$ RQ3) & 4.6 Limitations.
   - **Trang 17–18:** Mục 5 (Conclusion: Khẳng định C1 Multi-Agent là đóng góp cốt lõi) & Toàn bộ 12 tài liệu tham khảo (References) kết thúc gọn gàng tại Trang 18.
3. **Kiểm tra Overflow:** Không có lỗi tràn lề (`Overfull \hbox`), không tràn bảng, các hình TikZ co giãn hoàn hảo theo `\columnwidth`.

---

## 4. Xác Nhận Các Cam Đoan Kỹ Thuật (Compliance Sign-Off)

- [x] **Source code bất biến:** Thư mục `CTU-Chat_bot/` được giữ nguyên vẹn 100%, không bị chỉnh sửa.
- [x] **Bám sát Source Code Ground Truth:**
  - `academic_agent` sở hữu 6 Cypher tools, truy xuất trực tiếp Neo4j.
  - `financial_agent` sở hữu 4 tools (`tinh_toan_hoc_phi`, fee graph tools), tra cứu Neo4j/JSON trước khi gọi document RAG.
  - `scholarship_agent` sở hữu 1 tool (`tinh_tien_hoc_bong`).
  - `general_agent` sở hữu 0 tools, thuần tổng hợp từ Parent Chunks.
  - Không có peer-to-peer delegation; trạng thái chia sẻ qua Redis.
- [x] **Cấu trúc đóng góp:** C1 là Multi-Agent, C2 là Knowledge Allocation, C3 là Evidence Routing.
- [x] **Thuật toán đề xuất:** Cả Algorithm 1 và Algorithm 2 đều nằm hoàn toàn trong Section 3 (Trang 12).
- [x] **Biên dịch PDF thành công:** Tệp `PAPER/main.pdf` được tạo mới nhất, sạch sẽ, chuẩn bị sẵn sàng nộp hoặc in ấn.
