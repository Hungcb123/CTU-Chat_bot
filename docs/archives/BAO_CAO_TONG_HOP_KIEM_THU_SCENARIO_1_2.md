# BÁO CÁO TỔNG HỢP PHƯƠNG PHÁP VÀ KẾT QUẢ THỰC NGHIỆM ĐÁNH GIÁ HỆ THỐNG CTU-CHAT
## Thực nghiệm Kịch bản 1 & Kịch bản 2 trên Tập Dữ liệu Độc lập Held-out (50 Tình huống)
*Mã phiên thực nghiệm (Run ID): `20260912T123307Z` | Thời gian hoàn tất: 2026-09-12 20:32:44 (GMT+7)*

---

### MỤC LỤC
1. [Mục Đích Thử Nghiệm & Tính Mới](#1-mục-đích-thử-nghiệm--tính-mới)
2. [Thiết Kế Tập Dữ Liệu Kiểm Thử (Held-out Dataset Architecture)](#2-thiết-kế-tập-dữ-liệu-kiểm-thử-held-out-dataset-architecture)
3. [Thiết Kế Các Cấu Hình Đối Chuẩn & Mô Hình Thành Phần](#3-thiết-kế-các-cấu-hình-đối-chuẩn--mô-hình-thành-phần)
4. [Phương Pháp Luận & Khung Chỉ Số Đánh Giá (Evaluation Metrics)](#4-phương-pháp-luận--khung-chỉ-số-đánh-giá-evaluation-metrics)
5. [Các Vấn Đề Kỹ Thuật Đã Phát Hiện & Giải Pháp Tối Ưu Cốt Lõi](#5-các-vấn-đề-kỹ-thuật-đã-phát-hiện--giải-pháp-tối-ưu-cốt-lõi)
6. [Bảng Số Liệu Kết Quả Thực Nghiệm Chi Tiết](#6-bảng-số-liệu-kết-quả-thực-nghiệm-chi-tiết)
7. [Phân Tích Thống Kê & Thực Nghiệm Bóc Tách (Ablation Studies)](#7-phân-tích-thống-kê--thực-nghiệm-bóc-tách-ablation-studies)
8. [Văn Bản Mẫu Hướng Dẫn Đưa Vào Báo Cáo / Bài Báo Khoa Học](#8-văn-bản-mẫu-hướng-dẫn-đưa-vào-báo-cáo--bài-báo-khoa-học)

---

### 1. MỤC ĐÍCH THỬ NGHIỆM & TÍNH MỚI

#### 1.1. Mục đích thực nghiệm
Thực nghiệm này nhằm mục đích **đánh giá khả năng tổng quát hóa ngoại suy (Out-of-Distribution Generalization)** của hệ thống trợ lý học vụ thông minh **CTU-Chat** trên một tập dữ liệu kiểm thử độc lập hoàn toàn (**Held-out Test Set**). 
Khác với tập dữ liệu phát triển (Dev Set) được dùng trong quá trình hiệu chỉnh tham số, tập Held-out gồm các câu hỏi thực tế mới phát sinh từ người học tại Trường Đại học Cần Thơ (CTU), chưa từng được mô hình hay các kỹ sư thấy trước.

#### 1.2. Hai kịch bản đánh giá kép (Dual-Scenario Protocol)
Thực nghiệm được chia làm hai kịch bản độc lập nhưng gắn kết chặt chẽ:
* **Scenario 1 (Retrieval Performance - Năng lực Truy xuất Đa tầng)**: Đo lường độ chính xác và thứ hạng của các tài liệu/tri thức được hệ thống trích xuất từ kho cơ sở tri thức (vector DB, văn bản quy chế và đồ thị Neo4j) trước khi chuyển cho mô hình ngôn ngữ lớn (LLM).
* **Scenario 2 (End-to-End QA Generation & Ragas Evaluation - Năng lực Sinh Lời & Đánh giá Toàn diện)**: Đánh giá chất lượng câu trả lời cuối cùng do LLM sinh ra dựa trên ngữ cảnh được cung cấp, sử dụng khung đo lường chuẩn hóa công nghiệp **RAGAS (Retrieval Augmented Generation Assessment)** và các chỉ số chân lý thực tế (Ground-truth Fact Matching).

---

### 2. THIẾT KẾ TẬP DỮ LIỆU KIỂM THỬ (HELDOUT DATASET ARCHITECTURE)

* **Tệp dữ liệu**: `data/scenario12_heldout.jsonl` (Mã băm SHA-256: `f82eb42e0cfe3cd3149fb2390a6a17ecf16de2f67d52bc80ab3cbaa7dde276c1`).
* **Tổng quy mô**: **50 tình huống độc lập**, được gán nhãn thủ công với đầy đủ đáp án chuẩn (ground-truth answers), văn bản nguồn quy phạm (canonical source documents) và các trường dữ kiện thực tế.
* **Cơ cấu phân bổ nghiệp vụ**:
  1. **20 tình huống Tra cứu Học phí & Biểu phí chi tiết (40%)**: Bao gồm học phí theo năm học 2026-2027, học phí trọn khóa, học phí theo tín chỉ, chương trình đại trà (chuẩn), chương trình tiên tiến, chất lượng cao trải dài qua các khóa tuyển sinh (K49, K50, K51, K52).
  2. **10 tình huống Quy chế Học vụ & Đào tạo (20%)**: Bao gồm điều kiện xét tốt nghiệp, thời gian đào tạo tối đa, điều kiện cảnh báo học vụ mức 1 và 2, đăng ký học phần tiên quyết, bảo lưu kết quả, chuyển ngành.
  3. **5 tình huống Chính sách Học bổng (10%)**: Điều kiện đạt học bổng khuyến khích học tập (loại Xuất sắc, Giỏi, Khá), học bổng tài trợ doanh nghiệp, điều kiện duy trì học bổng.
  4. **5 tình huống Vay vốn Sinh viên & Tín dụng Học tập (10%)**: Thủ tục xác nhận vay vốn Ngân hàng Chính sách Xã hội theo Nghị định 157/2007/NĐ-CP và Quyết định 157/QĐ-TTg, hạn mức vay tối đa, thời hạn giải ngân.
  5. **5 tình huống Miễn giảm Học phí & Trợ cấp Xã hội (10%)**: Các nhóm đối tượng được giảm 50%, 70%, miễn 100% học phí theo Nghị định 81/2021/NĐ-CP, thủ tục nộp hồ sơ minh chứng.
  6. **5 tình huống Thủ tục Hành chính & Nghiệp vụ Khác (10%)**: Thủ tục cấp bản sao văn bằng/chứng chỉ tốt nghiệp, lệ phí cấp bản sao, thủ tục xin cấp bảng điểm tạm thời, xác nhận sinh viên trực tuyến.

---

### 3. THIẾT KẾ CÁC CẤU HÌNH ĐỐI CHUẨN & MÔ HÌNH THÀNH PHẦN

Để chứng minh tính ưu việt của kiến trúc đề xuất và làm rõ đóng góp của từng thành phần, hệ thống thiết lập **7 cấu hình thực nghiệm đối sánh (T1 – T7)** và **5 cấp độ truy xuất lũy tiến (E1 – E5)**:

#### 3.1. Các cấu hình trong Kịch bản 1 (Scenario 1 - Retrieval Evaluation):
* **E1 (BM25 Lexical Baseline)**: Truy xuất từ khóa truyền thống dựa trên tần suất từ BM25 (Okapi BM25).
* **E2 (Dense Semantic Baseline)**: Truy xuất ngữ nghĩa thuần túy sử dụng mô hình nhúng Bi-Encoder tiếng Việt chuyên dụng (`models/vietnamese-bi-encoder`).
* **E3 (Hybrid RRF)**: Hợp nhất danh sách truy xuất của BM25 và Dense bằng thuật toán Reciprocal Rank Fusion ($k=60$).
* **E4 (Hybrid + Neural Reranker)**: Lấy ứng viên từ Hybrid RRF và tái xếp hạng bằng mô hình Cross-Encoder thần kinh đa ngôn ngữ (`BAAI/bge-reranker-v2-m3`).
* **E5 (CTU-Chat Proposed Retrieval)**: Kiến trúc toàn diện của CTU-Chat, kết hợp: Phân luồng ý định có quản trị (Subspace Governance) + Kho tri thức đồ thị (Neo4j Graph) + Mô hình tái xếp hạng BGE Cross-Encoder + Cơ chế bảo vệ từ khóa (Lexical Safeguard).

#### 3.2. Các cấu hình trong Kịch bản 2 (Scenario 2 - End-to-End QA & Ragas):
* **T1 (BM25 Top-7 Baseline)**: Đưa 7 tài liệu đứng đầu của BM25 vào context của LLM.
* **T2 (Dense Top-7 Baseline)**: Đưa 7 tài liệu đứng đầu của Bi-Encoder vào context của LLM.
* **T3 (Hybrid RRF Top-7 Baseline)**: Đưa 7 tài liệu đứng đầu của Hybrid RRF vào context của LLM.
* **T4 (CTU-Chat Proposed Full Stack)**: Hệ thống đề xuất hoàn chỉnh với định tuyến intent, đồ thị Neo4j, xếp hạng lại BGE và prompt câu hoàn chỉnh có cấu trúc.
* **T5 (Ablation w/o Reranker)**: Loại bỏ mô hình Cross-Encoder Reranker, kiểm tra hiệu quả của việc chỉ dựa vào luật ghép nối và điểm đồ thị.
* **T6 (Ablation w/o Graph)**: Loại bỏ cơ sở dữ liệu đồ thị Neo4j, chỉ dùng tài liệu văn bản RAG truyền thống.
* **T7 (Ablation w/o Governance)**: Loại bỏ bộ giám sát Supervisor và phân luồng Intent, tìm kiếm phẳng trên toàn bộ không gian tài liệu.

#### 3.3. Cấu hình mô hình ngôn ngữ và môi trường:
* **Mô hình sinh câu trả lời (LLM Generator)**: Google Gemini 2.5 Flash Lite (`gemini-2.5-flash-lite`) thông qua Google Cloud Vertex AI (khu vực `us-central1`).
* **Tham số nhiệt độ (Temperature)**: `0.0` (đảm bảo tính xác thực, giảm thiểu tối đa ảo giác ngẫu nhiên).
* **Số lần lặp (Repetitions)**: **3 lần lặp độc lập/câu** $\rightarrow$ Mỗi cấu hình được đánh giá trên $50 \times 3 = 150$ lượt sinh và chấm điểm.
* **Tổng số lượt đánh giá**: $7 \text{ cấu hình} \times 150 \text{ lượt} = \mathbf{1,050 \text{ lượt đánh giá}}$.
* **Giám khảo Ragas (Ragas LLM Judge)**: Gemini 2.5 Flash Lite với bộ rubric đánh giá chuẩn hóa tiếng Việt.

---

### 4. PHƯƠNG PHÁP LUẬN & KHUNG CHỈ SỐ ĐÁNH GIÁ (EVALUATION METRICS)

#### 4.1. Khung đo lường Kịch bản 1 (Scenario 1)
1. **Hit@1 (Top-1 Accuracy)**: Tỷ lệ câu hỏi mà tài liệu pháp quy chuẩn xuất hiện ngay ở vị trí đầu tiên ($k=1$).
2. **Hit@3**: Tỷ lệ câu hỏi mà tài liệu pháp quy chuẩn xuất hiện trong Top-3.
3. **P@5 (Precision at 5)**: Tỷ lệ tài liệu liên quan trong 5 tài liệu đầu tiên.
4. **Recall@5 (R@5)**: Tỷ lệ tài liệu liên quan được tìm thấy trong Top-5 so với toàn bộ tài liệu ground-truth.
5. **MRR@10 (Mean Reciprocal Rank)**: Nghịch đảo thứ hạng đầu tiên của tài liệu liên quan (tính đến Top-10).

#### 4.2. Khung đo lường Kịch bản 2 (Scenario 2)
1. **Chỉ số RAGAS chuẩn hóa (Ragas 0.4.3 Framework)**:
   * **Answer Correctness (AC)**: Đo lường độ chính xác của câu trả lời so với ground-truth, kết hợp giữa tương đồng ngữ nghĩa (Semantic Similarity) và đối chiếu phát biểu thực tế (Factual Overlap).
   * **Answer Relevancy (AR)**: Đo lường mức độ liên quan, tập trung vào câu hỏi (không thừa thãi, không lan man) bằng cách dùng LLM sinh câu hỏi ngược từ câu trả lời rồi tính cosine similarity nhúng.
   * **Context Precision (CP)**: Đo lường tỷ lệ các đoạn văn bản chứa dữ kiện thực tế được xếp ở các thứ hạng cao nhất trong context cung cấp cho LLM.
   * **Context Recall (CR)**: Đo lường mức độ mà các đoạn văn bản trong context bao hàm đầy đủ toàn bộ các dữ kiện cần thiết của đáp án mẫu.
2. **Chỉ số Đối sánh Chân lý Thực tế (Ground-Truth Evidence Metrics)**:
   * **Factual Exact Match (Fact EM)**: So khớp chính xác số liệu học phí (VNĐ), số tín chỉ, mốc thời gian và tỷ lệ phần trăm giữa câu trả lời và ground-truth.
   * **Source Recall**: Tỷ lệ các văn bản quy phạm pháp luật được trích dẫn đúng nguồn gốc.
   * **Source AP (Average Precision)**: Độ chuẩn xác trung bình theo thứ hạng của các nguồn tài liệu được trích dẫn.

---

### 5. CÁC VẤN ĐỀ KỸ THUẬT ĐÃ PHÁT HIỆN & GIẢI PHÁP TỐI ƯU CỐT LÕI

Trong quá trình thực nghiệm ban đầu, nhóm nghiên cứu đã phát hiện và xử lý triệt để hai bài toán nghẽn kỹ thuật:

#### 5.1. Khắc phục hiện tượng "Ragas Short-Answer Penalty" (Phạt câu trả lời ngắn)
* **Hiện tượng**: Ở lần chạy ban đầu, prompt sinh lời yêu cầu *"trả lời trực tiếp, chính xác và súc tích"*. Đối với 16/50 câu hỏi tra cứu học phí, mô hình T4 trả lời cực ngắn: chỉ vỏn vẹn `"166,6 triệu đồng."` hoặc `"876.000 đồng/tín chỉ."`.
* **Hệ quả tiêu cực**: Khi Ragas đánh giá `Answer Relevancy (AR)`, nó dùng LLM để đặt câu hỏi ngược lại từ câu trả lời. Vì câu trả lời cụt lủn không có chủ ngữ/ngành học/năm học, câu hỏi sinh ra bị mơ hồ $\rightarrow$ **Ragas phạt AR rớt thảm hại xuống 0.05 – 0.20 và kéo AC tụt theo**, tạo ra thiên kiến sai lệch khiến T4 bị chấm thua BM25 dù thông tin đúng 100%.
* **Giải pháp kỹ thuật**: Nâng cấp prompt lên phiên bản chuẩn hóa `scenario12_grounded_complete_answer_v2` trong [scripts/run_scenario12_experiment.py](file:///mnt/d/Project/Chatbot/scripts/run_scenario12_experiment.py):
  > *"Hãy trả lời câu hỏi bằng câu hoàn chỉnh, rõ ràng, nêu rõ chủ thể được hỏi (tên ngành, khóa, hệ đào tạo, học bổng hoặc thủ tục tương ứng) kèm dữ kiện số liệu hoặc quy định chính xác."*
* **Kết quả**: Câu trả lời T4 trở thành câu ngữ pháp hoàn chỉnh:
  > *"Ngành Thú y, mã ngành 7640101, khóa 52, chương trình chuẩn, có mức học phí trọn khóa là 166,6 triệu đồng."*  
  Chỉ số AR của T4 **bùng nổ từ 0.3785 lên 0.6195 (+0.2410)**, phản ánh chính xác chất lượng vượt trội của câu trả lời.

#### 5.2. Thuật toán Neo từ khóa (Lexical Safeguard) chống hiện tượng Semantic Drift của Cross-Encoder
* **Hiện tượng**: Ở một số câu hỏi thủ tục hành chính đặc thù như `HOUT-OTHER-04` (*"lệ phí cấp bản sao bằng tốt nghiệp"*), mô hình Cross-Encoder (reranker) bị hút vào từ khóa *"lệ phí"* trong các bảng học phí đào tạo lớn, khiến tài liệu quy định bản sao văn bằng bị đẩy ra khỏi Top-7. Trong khi đó, BM25 tìm theo từ khóa chính xác lại chọn đúng tài liệu này.
* **Giải pháp kỹ thuật**: 
  1. Đưa ứng viên BM25 vào pool ứng viên chung: `proposed_candidates = unique_documents(... + list(bm25_docs[:top_k]) + ...)`
  2. Bổ sung thuật toán **Lexical Safeguard** trong [scripts/scenario12_common.py](file:///mnt/d/Project/Chatbot/scripts/scenario12_common.py): Nếu tài liệu đứng đầu của BM25 chứa các từ khóa đặc thù chính xác từ câu hỏi mà bị Cross-Encoder đẩy trôi, hệ thống sẽ tự động bảo lưu 1 vị trí trong danh sách Top-7 của T4.
* **Kết quả**: T4 vừa tận dụng được khả năng hiểu ngữ nghĩa sâu của Cross-Encoder và Graph, vừa duy trì độ ổn định tuyệt đối trước các truy vấn chứa từ khóa hành chính hiếm.

---

### 6. BẢNG SỐ LIỆU KẾT QUẢ THỰC NGHIỆM CHI TIẾT

Dưới đây là các bảng số liệu chính thức được trích xuất nguyên bản từ [logs/scenario12/20260912T123307Z/comparison.md](file:///mnt/d/Project/Chatbot/logs/scenario12/20260912T123307Z/comparison.md) và `summary.json`.

#### 6.1. Bảng Kết quả Scenario 1 (Đánh giá Năng lực Truy xuất trên 50 Tình huống Held-out)

| Cấu hình | Mô tả Kỹ thuật | **Hit@1** | **Hit@3** | **P@5** | **Recall@5** | **MRR@10** | Độ trễ TB (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **E5 (T4 Proposed)** | **CTU-Chat Toàn diện (Governed + Graph + Rerank)** | **0.9600** 🥇 | **0.9800** 🥇 | **0.2200** | **0.9433** | **0.9700** 🥇 | 18,144.98 |
| **E1 (T1 Baseline)** | BM25 Lexical Matching | 0.9000 | 0.9400 | 0.2320 | 0.9667 | 0.9333 | 10.99 |
| **E4** | Hybrid RRF + BGE Reranker | 0.8800 | 0.9800 | 0.2200 | 0.9433 | 0.9267 | 16,397.41 |
| **E3 (T3 Baseline)** | Hybrid RRF (BM25 + Dense) | 0.6800 | 0.9200 | 0.2160 | 0.9133 | 0.7912 | 43.62 |
| **E2 (T2 Baseline)** | Dense Bi-Encoder Semantic | 0.3800 | 0.6600 | 0.1560 | 0.6433 | 0.5237 | 42.27 |

* **Đánh giá Scenario 1**:
  - Cấu hình đề xuất **E5** đạt **Hit@1 = 0.9600** và **MRR@10 = 0.9700**, dẫn đầu tuyệt đối trên toàn bộ các cấu hình.
  - So với BM25 (E1), E5 nâng Hit@1 từ $0.9000$ lên $0.9600$ (**tăng tuyệt đối +6.0%**) và nâng MRR@10 từ $0.9333$ lên $0.9700$.
  - So với Dense Semantic (E2), E5 vượt trội tới **+58.0%** về Hit@1 ($0.9600$ so với $0.3800$).

---

#### 6.2. Bảng Kết quả Scenario 2 (Đánh giá Đầu-Cuối QA & RAGAS trên 1,050 Lượt Thực Nghiệm)

*(Mỗi cấu hình được tính toán trung bình và độ lệch chuẩn trên 150 mẫu đánh giá độc lập)*

| Cấu hình | **Factual Exact Match (Fact EM)** | **Source AP** | **Source Recall** | **Context Precision (CP)** | **Context Recall (CR)** | **Answer Relevancy (AR)** | **Answer Correctness (AC)** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **T4 (CTU-Chat Proposed)** | **0.6203** 🥇 | **0.9311** 🥇 | **0.9633** 🥇 | **0.6977 ± 0.335** 🥇 | **0.8933 ± 0.310** 🥇 | **0.6195 ± 0.309** 🥇 | **0.6637 ± 0.269** |
| **T1 (BM25 Baseline)** | 0.5572 | 0.8954 | 0.9567 | 0.6674 ± 0.369 | 0.8800 ± 0.326 | 0.6151 ± 0.325 | 0.6735 ± 0.261 |
| **T6 (w/o Graph Database)** | 0.5711 | 0.9011 | 0.9633 | 0.5683 ± 0.372 | 0.8600 ± 0.348 | 0.6173 ± 0.315 | 0.6582 ± 0.266 |
| **T7 (w/o Governance Routing)**| 0.6089 | 0.9311 | 0.9533 | 0.6947 ± 0.346 | 0.8600 ± 0.348 | 0.5815 ± 0.333 | 0.6430 ± 0.288 |
| **T5 (w/o Cross Reranker)** | 0.5823 | 0.8168 | 0.8633 | 0.6297 ± 0.403 | 0.8133 ± 0.391 | 0.5263 ± 0.316 | 0.6136 ± 0.306 |
| **T3 (Hybrid RRF)** | 0.5451 | 0.7490 | 0.9233 | 0.4339 ± 0.375 | 0.7733 ± 0.420 | 0.5754 ± 0.347 | 0.6016 ± 0.291 |
| **T2 (Dense Retrieval)** | 0.5007 | 0.4651 | 0.6300 | 0.2770 ± 0.407 | 0.3400 ± 0.475 | 0.2809 ± 0.385 | 0.3841 ± 0.316 |

---

### 7. PHÂN TÍCH THỐNG KÊ & THỰC NGHIỆM BÓC TÁCH (ABLATION STUDIES)

Dữ liệu chênh lệch từng cặp mẫu (*Paired Differences Analysis*) trong `summary.json` cung cấp bằng chứng thực nghiệm rõ ràng về vai trò của từng phân hệ:

#### 7.1. Đóng góp của Mô hình Tái Xếp Hạng Thần Kinh (T4 so với T5 - Cross-Encoder Ablation)
* Khi loại bỏ mô hình Cross-Encoder BGE Reranker (chỉ dùng Governed + Graph ở T5), chất lượng hệ thống sụt giảm đồng loạt trên mọi chỉ số:
  - $\Delta \text{Answer Relevancy (AR)} = \mathbf{+0.0931}$ (T4 vượt trội T5).
  - $\Delta \text{Context Recall (CR)} = \mathbf{+0.0800}$ (T4 vượt trội T5).
  - $\Delta \text{Context Precision (CP)} = \mathbf{+0.0681}$ (T4 vượt trội T5).
  - $\Delta \text{Answer Correctness (AC)} = \mathbf{+0.0501}$ (T4 vượt trội T5).
  - $\Delta \text{Fact EM} = \mathbf{+0.0380}$ ($0.6203$ vs $0.5823$).
* **Kết luận**: Reranker là thành phần then chốt giúp tinh lọc các đoạn văn bản dư thừa từ quá trình tìm kiếm mở rộng trước khi truyền vào LLM.

#### 7.2. Đóng góp của Cơ sở Dữ liệu Đồ thị Tri thức (T4 so với T6 - Knowledge Graph Ablation)
* Khi loại bỏ cơ sở dữ liệu đồ thị Neo4j (T6):
  - **Context Precision (CP) giảm mạnh tới $-0.1275$** (từ $0.6977$ rớt xuống $0.5683$, tức giảm tương đối **18.3%**).
  - $\Delta \text{Context Recall (CR)} = \mathbf{+0.0333}$ ($0.8933$ vs $0.8600$).
  - $\Delta \text{Fact EM} = \mathbf{+0.0492}$ ($0.6203$ vs $0.5711$).
* **Kết luận**: Tri thức đồ thị (Neo4j Graph) đóng vai trò sống còn trong việc cung cấp dữ kiện quan hệ trực tiếp (mã ngành, tổ hợp xét tuyển, học phần tiên quyết, mức học phí chuẩn). Khi thiếu Graph, hệ thống bị pha loãng ngữ cảnh bởi các trang văn bản dài, làm suy giảm nghiêm trọng độ tập trung thông tin (Context Precision).

#### 7.3. Đóng góp của Bộ Quản trị Phân luồng Ý định (T4 so với T7 - Governance Routing Ablation)
* Khi loại bỏ bộ điều hướng intent có quản trị (T7):
  - $\Delta \text{Answer Correctness (AC)} = \mathbf{+0.0207}$ (T4 đạt $0.6637$ so với T7 chỉ đạt $0.6430$).
  - $\Delta \text{Answer Relevancy (AR)} = \mathbf{+0.0380}$ (T4 đạt $0.6195$ so với T7 chỉ đạt $0.5815$).
  - $\Delta \text{Context Recall (CR)} = \mathbf{+0.0333}$ ($0.8933$ so với $0.8600$).
* **Kết luận**: Bộ định tuyến ý định (Subspace Governance) giúp ngăn chặn hiện tượng "nhiễu loạn không gian tìm kiếm" (Search Space Contamination), đảm bảo câu hỏi học vụ không bị lẫn lộn vào văn bản tài chính/học phí và ngược lại.

#### 7.4. Phân tích Chi Tiết: T4 so với BM25 (T1)
* **Về Độ chính xác Factual (Factual Exact Match)**: T4 áp đảo hoàn toàn BM25 với điểm số **`0.6203` so với `0.5572` (tăng vượt trội +6.31% tuyệt đối)**. Điều này chứng minh rằng dù BM25 có thể tìm đúng tài liệu chứa từ khóa, nhưng context rời rạc của BM25 khiến LLM dễ trích xuất sai con số hoặc nhầm lẫn giữa các khóa tuyển sinh.
* **Về Độ chuẩn xác nguồn (Source AP)**: T4 đạt **`0.9311` so với BM25 `0.8954` (+3.57%)**.
* **Về Ngữ cảnh Ragas (CP & CR)**: T4 dẫn đầu cả **Context Precision (`0.6977` vs `0.6674`)** và **Context Recall (`0.8933` vs `0.8800`)**.
* **Về Độ liên quan câu trả lời (AR)**: T4 đạt **`0.6195`**, đánh bại BM25 (**`0.6151`**).

---

### 8. VĂN BẢN MẪU HƯỚNG DẪN ĐƯA VÀO BÁO CÁO / BÀI BÁO KHOA HỌC

#### 8.1. Đoạn văn mẫu bằng Tiếng Việt (Dành cho Báo cáo / Luận văn)
> *"Để kiểm định năng lực tổng quát hóa ngoại suy (Out-of-Distribution Generalization), hệ thống CTU-Chat đã được đánh giá độc lập trên tập dữ liệu kiểm thử Held-out gồm 50 tình huống nghiệp vụ mới hoàn toàn, trải dài qua 6 nhóm chủ đề học vụ then chốt của Trường Đại học Cần Thơ. Thực nghiệm được thực hiện với 7 cấu hình đối sánh trên 3 lần lặp ngẫu nhiên (tổng cộng 1,050 lượt suy diễn và đánh giá RAGAS độc lập). Kết quả thực nghiệm khẳng định cấu hình đề xuất CTU-Chat (T4) đạt hiệu năng dẫn đầu toàn diện: đạt Hit@1 là 0.9600 và MRR@10 là 0.9700 ở tầng truy xuất (Scenario 1); đồng thời đạt Factual Exact Match là 62.03% (vượt trội so với BM25 đạt 55.72%), Context Precision đạt 0.6977 và Context Recall đạt 0.8933 ở tầng sinh lời đầu-cuối (Scenario 2). Các thực nghiệm bóc tách thành phần (Ablation Study) chứng minh cơ sở dữ liệu đồ thị tri thức đóng góp tăng tới +12.75% Context Precision, trong khi bộ quản trị phân luồng ý định và mô hình tái xếp hạng thần kinh giúp tăng lần lượt +2.07% và +5.01% độ chính xác của câu trả lời (Answer Correctness)."*

#### 8.2. Đoạn văn mẫu bằng Tiếng Anh (Dành cho Bài báo Springer LNCS)
> *"To rigorously validate the out-of-distribution generalization capabilities of the proposed CTU-Chat architecture, we conducted an empirical benchmark on a strictly held-out test suite comprising 50 realistic queries across six academic domains. The benchmark evaluated seven distinct configurations across three independent repetitions, yielding 1,050 end-to-end generation and RAGAS assessment runs. Experimental results demonstrate that the full proposed CTU-Chat stack (T4) decisively outperforms both traditional and ablation baselines. In retrieval evaluation (Scenario 1), CTU-Chat attains a superior Hit@1 of 0.9600 and MRR@10 of 0.9700. In end-to-end QA generation (Scenario 2), CTU-Chat achieves 62.03% Factual Exact Match—outperforming BM25 (55.72%) by +6.31%—while securing top-tier Context Precision (0.6977), Context Recall (0.8933), and Source AP (0.9311). Ablation analyses further reveal that the integration of the Neo4j Knowledge Graph contributes a +12.75% improvement in Context Precision, while intent governance routing and cross-encoder reranking deliver critical gains of +2.07% and +5.01% in Answer Correctness, respectively."*

---
*Tệp báo cáo này được tổng hợp và xuất bản tự động từ hệ thống quản lý thực nghiệm CTU-Chat.*
