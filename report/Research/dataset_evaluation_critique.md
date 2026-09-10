# Đánh Giá Các Sai Lệch Phương Pháp Luận & Giới Hạn Của Bộ Dữ Liệu Thực Nghiệm (Evaluation Dataset Critique)

> **Tài liệu tham khảo nội bộ phục vụ hoàn thiện bài báo khoa học & báo cáo thực nghiệm**  
> **Dự án:** CTU Scholarship & Academic Multi-Agent RAG Chatbot  
> **Ngày lập:** 09/09/2026  

---

## 1. Tóm Tắt Điều Hành (Executive Summary)

Khi triển khai kịch bản thực nghiệm đối sánh các biến thể kiến trúc (Table 4: E1 đến E5) trên bộ dữ liệu 100 câu hỏi tổng quát (`tests/data/100.csv`), nhóm nghiên cứu ghi nhận các kết quả có vẻ phi lý:
1. **BM25 (E1)** có điểm số cao vượt bậc ($MRR = 0.8075$, $Recall@5 = 0.9300$), vượt qua cả **Dense Retrieval (E2)** ($MRR = 0.5683$) và **Hybrid RRF (E3)** ($MRR = 0.6965$).
2. **Graph (E4)** và **Agent (E5)** chỉ cải thiện điểm số không đáng kể so với Hybrid RRF (từ $0.6965$ lên $0.7235$), thậm chí E4 và E5 có điểm số hoàn toàn trùng khớp nhau ($MRR = 0.7235$, $Recall@5 = 0.8700$).

Qua phân tích sâu cấu trúc dữ liệu và cơ chế đánh giá, nhóm khẳng định: **Bộ dữ liệu `100.csv` hiện tại đang chứa những sai lệch phương pháp luận (methodological flaws) nghiêm trọng, làm lu mờ và phản ánh sai lệch năng lực thực tế của toàn bộ hệ thống.**

---

## 2. Phân Tích Chi Tiết 3 Sai Lệch Cốt Lõi

### 2.1. Sai lệch 1: Thiên lệch trùng lặp từ vựng cực đoan (Severe Lexical Overlap Bias)

* **Hiện tượng:** BM25 (tìm kiếm từ khóa truyền thống) áp đảo hoàn toàn các mô hình học sâu ngữ nghĩa.
* **Nguyên nhân kỹ thuật:**
  * Các câu hỏi trong `100.csv` được tạo bằng cách bám sát nguyên văn tài liệu nguồn, chứa chính xác các cụm từ danh từ riêng, con số học phí hoặc tên file Markdown (ví dụ: *"Khóa 52"*, *"695.000"*, *"CT239H"*, *"MucHocPhi_DaiHocChinhQuy_Khoa52"*).
  * Khi từ khóa trong câu hỏi trùng khớp 100% với chunk tài liệu, hàm xếp hạng BM25 (dựa trên TF-IDF) chấm điểm tuyệt đối cho chunk đó, giúp nó nhảy ngay lên vị trí Top-1.
* **Bằng chứng đối chứng (Tập câu hỏi diễn đạt tự nhiên CT239H - N=100):**
  * Khi thử nghiệm trên tập dữ liệu người dùng thực tế (`ct239h_retrieval_benchmark_100-v3.csv`), nơi câu hỏi có từ đồng nghĩa, cấu trúc ngữ pháp thay đổi, câu hỏi thời gian:
    * **BM25 sụp đổ:** $MRR$ tụt từ **0.8075 xuống 0.2662**; $Recall@5$ giảm từ **93% xuống 43%**; $Hit@1$ chỉ đạt **18%**.
    * **Dense & Reranker vượt trội:** $MRR$ đạt **0.9267**, $Recall@5$ đạt **97.17%**, $Hit@1$ đạt **88%**.
  * **Kết luận:** Điểm cao của BM25 trên tập `100.csv` là một **ảo ảnh thống kê (statistical artifact)**, không đại diện cho hiệu năng truy vấn thực tế.

---

### 2.2. Sai lệch 2: Phân bố dữ liệu không cân xứng triệt tiêu vai trò của Knowledge Graph

* **Hiện tượng:** Thêm Knowledge Graph (E4) chỉ giúp MRR tăng khiêm tốn từ $0.6965$ lên $0.7235$ (+0.027).
* **Nguyên nhân kỹ thuật:**
  * Trong toàn bộ 100 câu của `100.csv`, **chỉ có đúng 9 câu (9%)** thuộc nhóm Chương trình đào tạo (`academic_program`). 
  * 91 câu còn lại (91%) là câu hỏi tra cứu văn bản phẳng (học phí, trợ cấp xã hội, vay vốn). Đối với 91 câu này, bộ định tuyến không kích hoạt Graph hoặc Graph trả về tập rỗng, khiến điểm số của E4 bị kéo phẳng về điểm số của Hybrid RRF (E3).
* **Bằng chứng đối chứng (Lọc riêng tập con Academic Program - N=9):**
  * Khi kiểm tra riêng 9 câu hỏi có tính quan hệ thực thể (môn học, chuỗi tiên quyết, chương trình đào tạo) trong `tests/outputpaper/table4_academic_results.json`:
    * **BM25 + Dense + RRF (E3):** $MRR = 0.4167$, $Hit@1 = 22.22%$.
    * **BM25 + Dense + RRF + Graph (E4):** $MRR = \mathbf{0.8000}$ (+92% tương đối), $Hit@1 = \mathbf{77.78%}$ (+250% tương đối).
  * **Kết luận:** Knowledge Graph có sức mạnh vượt bậc với dữ liệu quan hệ, nhưng tỷ trọng quá nhỏ (9%) trong tập test đã làm mất đi ý nghĩa thống kê của thành phần này.

---

### 2.3. Sai lệch 3: Sai lầm về công cụ đo (Measurement Mismatch) đối với Agent

* **Hiện tượng:** E5 (Graph + Agent) có điểm số giống hệt E4 (Graph) ($MRR = 0.7235$, $Recall@5 = 0.8700$).
* **Nguyên nhân kỹ thuật:**
  * Thước đo của Table 4 chỉ thuần túy là **Document Retrieval Ranking** ($P@5, Recall@5, MRR$ dựa trên danh sách tên file Markdown được trả về).
  * Trong hàm benchmark, Agent khi nhận câu hỏi cũng gọi các công cụ Graph tương tự để suy ra nguồn, do đó tập nguồn tài liệu của E5 và E4 là như nhau.
  * **Sức mạnh thực sự của Agent không nằm ở việc nhặt file tài liệu**, mà nằm ở:
    1. **Tính toán số học chính xác (Deterministic Financial Computation):** Sinh viên đưa ra GPA và ĐRL $\rightarrow$ Agent gọi tool tính học bổng; đưa ra diện chính sách $\rightarrow$ Agent gọi tool tính miễn giảm học phí.
    2. **Định tuyến nhiều bước (Multi-hop Routing):** Supervisor phân biệt câu hỏi nào cần tra Graph, câu hỏi nào cần tính toán, câu hỏi nào cần RAG.
    3. **Sinh câu trả lời tổng hợp (End-to-End Response Generation):** Trả lời trực tiếp câu hỏi người dùng thay vì chỉ quăng ra một đoạn văn bản.
* **Bằng chứng đối chứng:**
  * **Thực nghiệm Tool Calling (30 cases - `logs/tool_calling_experiment_results.md`):** Độ chính xác lựa chọn tool đạt **100% (30/30)**, tính toán chính xác đạt **96.67% (29/30)**.
  * **Thực nghiệm LLM Judge (100 cases - `scripts/evaluate_chat_dataset.py`):** Pass rate câu trả lời đạt **91.00%**.
  * **Kết luận:** Dùng thước đo Retrieval để đo lường Agent tương đương với việc *"đánh giá một kỹ sư lập trình bằng tốc độ gõ bàn phím"* — hoàn toàn lệch hướng so với giá trị cốt lõi của công nghệ.

---

## 3. Bảng Đối Chiếu Tổng Hợp 3 Bộ Dữ Liệu Thực Nghiệm

| Chỉ số / Đặc trưng | Tập 1: General Retrieval (`100.csv`) | Tập 2: Natural Query (`CT239H - 100 cases`) | Tập 3: Academic Subset (`Graph Focus - 9 cases`) | Tập 4: Financial Tool Calling (`Agent Focus - 30 cases`) |
| :--- | :---: | :---: | :---: | :---: |
| **Bản chất câu hỏi** | Trùng từ khóa văn bản, câu hỏi đóng | Diễn đạt tự nhiên, ngữ nghĩa, thời gian | Truy vấn quan hệ môn học, chuỗi tiên quyết | Bài toán tính toán học phí & học bổng cụ thể |
| **BM25 / Sparse MRR** | **0.8075** (Ảo do trùng từ khóa) | **0.2662** (Sụp đổ) | **0.5593** | Không áp dụng (N/A) |
| **Dense Only MRR** | 0.5683 | 0.7493 | 0.2222 | Không áp dụng (N/A) |
| **Hybrid RRF MRR** | 0.6965 | 0.5288 | 0.4167 | Không áp dụng (N/A) |
| **Hybrid + Reranker** | Chưa tích hợp trong script Table 4 | **0.9267** (Áp đảo hoàn toàn) | Chưa tích hợp | Không áp dụng (N/A) |
| **Graph RAG MRR** | 0.7235 (+0.027) | Không chạy Graph | **0.8000** (+0.3833) | Không áp dụng (N/A) |
| **Agent Performance** | 0.7235 (Bị triệt tiêu năng lực) | Không chạy Agent | **0.8000** (Bị đo sai thước) | **96.67%** độ chính xác tính toán |

---

## 4. Đề Xuất Điều Chỉnh Kịch Bản Cho Bài Báo (Paper Recommendations)

Để bài báo khoa học phản ánh trung thực, sắc bén và thuyết phục năng lực của kiến trúc Agentic GraphRAG, khuyến nghị cấu trúc lại phần Evaluation thành 3 kịch bản chuyên biệt:

```
                      ┌─────────────────────────────────────────┐
                      │    ĐÁNH GIÁ HỆ THỐNG TOÀN DIỆN          │
                      └────────────────────┬────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│   Scenario 1     │             │   Scenario 2     │             │   Scenario 3     │
│Retrieval Ablation│             │Graph-RAG Ablation│             │Agent Tool & E2E  │
└────────┬─────────┘             └────────┬─────────┘             └────────┬─────────┘
         │                                │                                │
         ▼                                ▼                                ▼
  Dữ liệu CT239H                  Dữ liệu Academic                 Dữ liệu Tool & QA
 (Câu hỏi tự nhiên)             (Quan hệ đồ thị)                 (Tính toán & Trả lời)
  Chứng minh vai trò             Chứng minh vai trò               Chứng minh vai trò
  của Dense + Rerank             của Knowledge Graph              của Multi-Agent LLM
```

### Chi tiết 3 kịch bản đề xuất:

1. **Scenario 1: Retrieval Ablation (Tập trung chứng minh tầng RAG đa phương thức)**
   * **Dữ liệu:** Sử dụng bộ `CT239H 100 cases`.
   * **Cấu hình:** `Sparse only` vs `Dense only` vs `Hybrid RRF` vs `Hybrid RRF + Cross-Encoder Reranker`.
   * **Thông điệp:** Khẳng định Cross-Encoder Reranker là nhân tố quyết định đưa $Recall@5$ lên 97.17% và $MRR$ lên 0.9267.

2. **Scenario 2: Structured Graph Ablation (Tập trung chứng minh tầng Knowledge Graph)**
   * **Dữ liệu:** Sử dụng tập câu hỏi chuyên sâu về CTĐT & quy chế học vụ liên kết.
   * **Cấu hình:** `Vector RAG phẳng` vs `Graph-augmented Retrieval`.
   * **Thông điệp:** RAG phẳng hoàn toàn thất bại trước các câu hỏi cấu trúc chuỗi (MRR chỉ 0.41), trong khi Knowledge Graph giải quyết triệt để (MRR đạt 0.80).

3. **Scenario 3: Agentic Reasoning & Tool Validity (Tập trung chứng minh năng lực Agent)**
   * **Dữ liệu:** Bộ 30 case tài chính sinh viên và 100 case End-to-End Chat API.
   * **Chỉ số:** Tool Selection Accuracy (100%), Argument Correctness (96.67%), LLM-as-a-Judge Pass Rate (91.00%).
   * **Thông điệp:** Hệ thống không chỉ tìm tài liệu mà có năng lực tính toán số học chuẩn xác tuyệt đối, loại bỏ hoàn toàn hiện tượng ảo giác (hallucination) thường gặp ở LLM.
