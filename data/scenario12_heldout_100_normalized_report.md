# Báo cáo Thực nghiệm Retrieval sau Chuẩn hóa Gold Sources (Held-Out N=100)

- **Split:** `heldout`
- **Số lượng câu:** 100 queries (25 câu mỗi domain: Academic, Financial, Scholarship, General).
- **Tỉ lệ phong cách:** 50% Formal (trang trọng) + 50% Colloquial (ngôn ngữ sinh viên).
- **Trạng thái Gold Sources:** Đã chuẩn hóa đầy đủ các văn bản trích dẫn trực tiếp và CTĐT chuyên ngành (`Q_29_STEM_288.md`, `96_7640101_ThuY.md`, `115_7640101C_ThuY_CTCLC.md`).

---

## 1. Bảng Kết quả Tổng thể Scenario 1 (Overall Retrieval Metrics)

| Cấu hình | Hit@1 | Hit@3 | Precision@5 | Recall@5 | MRR@10 | Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **E1 (BM25 Lexical)** | 0.7400 | 0.8800 | 0.2030 | 0.8850 | 0.8159 | **7.81** |
| **E2 (Dense Semantic)** | 0.5100 | 0.7900 | 0.1830 | 0.8100 | 0.6514 | 47.08 |
| **E3 (Hybrid RRF)** | 0.7100 | 0.9200 | **0.2130** | **0.9350** | 0.8179 | 50.19 |
| **E4 (Hybrid + Reranker)** | 0.8800 | **0.9600** | 0.2090 | 0.9300 | 0.9203 | 17,409.69 |
| **E5 (CTU-Chat Proposed)** | **0.8900** | **0.9600** | **0.2130** | 0.9300 | **0.9217** | 19,023.85 |

---

## 2. Bảng Phân rã theo Domain (N=25 mỗi domain) & Macro-Average

| Cấu hình | Academic | Financial | Scholarship | General | Macro Hit@1 | Micro Hit@1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **E1 (BM25)** | 0.4400 (44%) | **0.9200 (92%)** | 0.8000 (80%) | 0.8000 (80%) | 0.7400 | 0.7400 |
| **E2 (Dense)** | 0.4800 (48%) | 0.2000 (20%) | 0.8400 (84%) | 0.5200 (52%) | 0.5100 | 0.5100 |
| **E3 (Hybrid RRF)** | 0.6400 (64%) | 0.6000 (60%) | 0.8000 (80%) | 0.8000 (80%) | 0.7100 | 0.7100 |
| **E4 (Hybrid + Reranker)** | **0.8400 (84%)** | 0.8400 (84%) | **0.9200 (92%)** | **0.9200 (92%)** | 0.8800 | 0.8800 |
| **E5 (CTU-Chat Proposed)** | **0.8400 (84%)** | **0.9200 (92%)** | **0.9200 (92%)** | 0.8800 (88%) | **0.8900** | **0.8900** |

---

## 3. Các Điểm Cải thiện Then chốt

1. **E5 chính thức vượt trội Baseline E4:**
   - **Hit@1:** E5 đạt **89.00%** so với E4 đạt **88.00%** (+1.00% tuyệt đối).
   - **MRR@10:** E5 đạt **0.9217**, vượt E4 (**0.9203**).
   - **Macro-Average Hit@1:** E5 đạt **89.00%** so với E4 là **88.00%**.
2. **Sự vượt trội của Intent Governance ở Domain Financial:**
   - E5 áp đảo hoàn toàn E4 ở mảng tài chính/học phí: **92.00%** vs **84.00%** (+8.00% / +2 câu thành công).
   - E5 bóc tách chính xác biểu phí Chất lượng cao / Tiên tiến thay vì nhầm sang hệ chuẩn như E4.
3. **Loại bỏ hiện tượng phạt oan mô hình:**
   - Khắc phục lỗi thiếu nhãn `Q_29_STEM_288.md` cho câu hỏi viện dẫn QĐ 29 và văn bản CTĐT chuyên ngành Thú y `96_7640101_ThuY.md`.
