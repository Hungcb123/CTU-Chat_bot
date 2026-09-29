# BIÊN BẢN TỔNG HỢP KẾ HOẠCH RÚT GỌN PHẦN 3 (PROPOSED MODEL)
**Dự án Bài báo Khoa học:** Hệ thống Trợ lý ảo Học vụ Thông minh CTU-Chat (Trường ĐH Cần Thơ)  
**Mục tiêu cốt lõi:** Cắt giảm dung lượng Phần 3 từ **~7 trang xuống còn ~4.5 trang**, đưa toàn bộ bài báo từ **20 trang về mốc 15 – 16 trang chuẩn hội nghị** (tránh bị phạt phí vượt trang và xử lý triệt để các nhận xét của Cô).

---

## I. CÂU TRẢ LỜI DỨT KHOÁT VỀ BẢNG 4 (TABLE 4)
> **Câu hỏi của nhóm:** *"Có thật sự nên xóa Bảng 4 (Decision criteria mapping query characteristics to evidence representation mechanisms) không?"*

👉 **QUYẾT ĐỊNH CỦA NHÓM: NÊN GIỮ LẠI BẢNG 4 (Chỉ cần định dạng lại cho nhỏ gọn).**

### Lý do khoa học:
1. **Bảng 4 là "xương sống" trả lời trực tiếp cho RQ3 (Representation-Aware Routing):**  
   Bảng 4 giải thích bản chất phương pháp luận (*Structural Rationale*): Tại sao câu hỏi quan hệ môn học phải đi vào Graph Neo4j? Tại sao văn bản quy chế phải đi vào Hybrid RAG? Tại sao tính học phí phải đi vào Python tool? Reviewer đọc bảng này sẽ hiểu ngay triết lý thiết kế mà không cần đọc nhiều chữ.
2. **Khác biệt hoàn toàn với Bảng 3 (Table 3):**
   * **Bảng 3 (Thừa, đã xóa):** Chỉ liệt kê lại *"Agent nào nối với Database nào"* $\to$ Y hệt Bảng 1, hoàn toàn là dữ liệu trùng lặp.
   * **Bảng 4 (Có giá trị, giữ lại):** Giải thích *"Đặc trưng câu hỏi $\to$ Cơ chế truy xuất $\to$ Lý do học thuật"* $\to$ Đây là đóng góp phương pháp luận, rất đáng giá!
3. **Cách định dạng:** Giữ nguyên bảng, dùng `\small` hoặc thu hẹp khoảng cách dòng để bảng chỉ chiếm khoảng 6–8 dòng là cực kỳ đẹp mắt.

---

## II. DANH SÁCH CÁC HẠNG MỤC ĐÃ XỬ LÝ (ĐÃ XÓA / ĐÃ SỬA)

Các thành viên đã thống nhất và thực hiện xong các phần sau trên file bản thảo:

### 1. ✅ ĐÃ XÓA: Algorithm 2 (`Deterministic Tuition Reduction Calculation` - Trang 11)
* **Lý do xóa:**  
  Thuật toán này thực chất chỉ là 2 phép tính số học cơ bản:
  $$D = B \cdot \frac{p}{100}, \quad P = \max(0, T - D)$$
  Ngay phía trên nó, bài báo **đã có Equation (3) và Equation (4)** viết đầy đủ 2 công thức này.
* **Ý nghĩa:** Việc đưa một phép nhân trừ đơn giản vào khối `Algorithm` trang trọng thường bị reviewer quốc tế coi là "câu trang bằng mã giả cấp 1" (page padding). Bỏ đi giúp bài báo chuyên nghiệp hơn.
* **Dung lượng tiết kiệm:** **~0.4 trang**.

### 2. ✅ ĐÃ XÓA: Bảng 3 (`Table 3: Heterogeneous knowledge allocation` - Trang 12)
* **Lý do xóa:**  
  Lặp lại 100% nội dung của Bảng 1 (Table 1 ở trang 8), chỉ khác tên gọi một số cột.
* **Ý nghĩa:** Triệt tiêu hoàn toàn sự thừa thãi, giúp người đọc không phải đọc lại 2 bảng cùng nội dung.
* **Dung lượng tiết kiệm:** **~0.4 trang**.

### 3. ✅ ĐÃ RÚT GỌN: Bảng 2 (`Table 2: Neo4j Schema` - Trang 9)
* **Lý do rút gọn:**  
  Bảng 2 trước đó liệt kê chi tiết từng thuộc tính nhỏ lẻ (`prog_code, description, rate, unit...`). Đây là chi tiết kỹ thuật của lập trình viên (*implementation details*), không phải đóng góp học thuật cốt lõi của bài báo Multi-Agent RAG.
* **Ý nghĩa:** Rút gọn bảng hoặc cô đọng thành tóm tắt cấu trúc giúp người đọc tập trung vào bản chất đồ thị (10 node labels, 13 relationship types) thay vì chi tiết code.
* **Dung lượng tiết kiệm:** **~0.4 trang**.

---

## III. NHỮNG PHẦN CÒN LẠI CẦN CẮT GỌT TIẾP (TEAM CẦN LÀM TIẾP TRÊN LATEX)

Để đạt mục tiêu tối ưu về 15–16 trang, nhóm cần tiếp tục chỉnh sửa 3 vị trí sau:

### 1. ✂️ Cắt bỏ đoạn lặp lại 4 bước Hybrid RAG (Cuối Trang 12 – Đầu Trang 13)
* **Vị trí trong PDF:** Cuối trang 12 và đầu trang 13, mục `Hybrid Document Retrieval Path` với 4 bước đánh số 1, 2, 3, 4.
* **Vấn đề:** Đang in lại công thức tính RRF $s_{RRF}(d) = \sum \frac{1}{k+r_s(d)}$ với $k=60$ và liệt kê lại 4 gạch đầu dòng dài dòng. **Công thức và quy trình RRF này đã được viết và giải thích chi tiết ở Mục 2.3 (Trang 4)**!
* **Đoạn văn LaTeX thay thế (chỉ 3 dòng, thay thế toàn bộ 4 gạch đầu dòng và công thức):**
```latex
\noindent\textbf{Hybrid Document Retrieval Path:} For narrative administrative regulations and scholarship policies, the General Specialist executes the multi-stage hybrid retrieval pipeline (lexical BM25 and dense Qdrant vector search fused via Reciprocal Rank Fusion ($k=60$) and neural cross-attention reranking via \texttt{BAAI/bge-reranker-v2-m3}, as formulated in Section~\ref{sec:related_hybrid}) over 2,800-character parent chunks stored in PostgreSQL.
```
* **Dung lượng tiết kiệm thêm:** **~0.4 trang**.

---

### 2. ✂️ Thu gọn Algorithm 1 (`Supervisor Routing` - Trang 10)
* **Vị trí trong PDF:** Trang 10, `Algorithm 1: Supervisor Routing and Conditional Evidence-Path Dispatch`.
* **Vấn đề:** Dài tới 16 dòng. Các dòng 11–15 (`if d* = 'academic' then v_next <- 'academic_agent' else...`) thực chất đã được viết thành **Equation (2) ($Edge_{sup}(S)$)** và vẽ bằng mũi tên trong Figure 1.
* **Đoạn mã giả LaTeX rút gọn (chỉ 8 dòng cốt lõi):**
```latex
\begin{algorithm}[!htbp]
\scriptsize
\SetAlFnt{\scriptsize}
\SetAlCapFnt{\scriptsize}
\SetAlCapNameFnt{\scriptsize}
\SetAlgoVlined
\LinesNumbered
\caption{Supervisor Intent Routing and Dispatch}
\label{alg:routing}
\KwIn{Query $q$, Dialogue history $\mathcal{H}$, Shared state $\mathcal{S}$}
\KwOut{Updated state $\mathcal{S}$ and target node $v_{\text{next}}$}
$q_{\text{standalone}} \leftarrow \mathrm{DisambiguateQuery}(q, \mathcal{H})$\;
$\langle d^*, \iota^* \rangle \leftarrow \mathrm{ClassifyDomainAndIntent}(q_{\text{standalone}})$\;
\If{$d^* = \mathrm{NULL}$}{
    $d^* \leftarrow \text{'general'}$;\quad $\iota^* \leftarrow \text{'other'}$\;
}
$\mathcal{S}[\text{'search\_query'}] \leftarrow q_{\text{standalone}}$;\quad $\mathcal{S}[\text{'next\_agent'}] \leftarrow d^*$\;
$v_{\text{next}} \leftarrow \mathrm{Edge}_{\text{sup}}(\mathcal{S})$ \tcp*{Conditional dispatch via Eq.~(2)}
\Return $\langle \mathcal{S}, v_{\text{next}} \rangle$\;
\end{algorithm}
```
* **Dung lượng tiết kiệm thêm:** **~0.2 – 0.3 trang**.

---

### 3. ✂️ Cập nhật Bảng 1 (Table 1 ở Trang 8) thành "Bảng Mẹ"
* **Vị trí trong PDF:** Trang 8, `Table 1: Operational profiles and direct tool availability...`.
* **Cách làm:** Thêm cột `Knowledge Structure` (lấy từ Bảng 3 cũ đã xóa) vào Bảng 1, format lại cho thoáng và rõ chữ:
```latex
\begin{table}[!htbp]
\centering
\small
\caption{Operational profiles, knowledge structures, and resource privileges of the domain-specialized agents in \system{}.}
\label{tab:agent_specs}
\resizebox{\columnwidth}{!}{
\begin{tabular}{lllll}
\toprule
\textbf{Specialist Agent} & \textbf{Knowledge Structure} & \textbf{Evidence Store} & \textbf{Direct Tool Registry} & \textbf{Execution Paradigm} \\
\midrule
\texttt{Academic}    & Relational Curricula & Neo4j Knowledge Graph & 6 Cypher tools (\texttt{tra\_cuu\_nganh}, etc.) & ReAct graph traversal \\
\texttt{Financial}   & Cohort / Rate Matrices & Neo4j, JSON Catalogs  & 4 tools (\texttt{tinh\_toan\_hoc\_phi}, etc.)  & Retrieval + Calc \\
\texttt{Scholarship} & Narrative + Thresholds & Hybrid Document RAG   & 1 tool (\texttt{tinh\_tien\_hoc\_bong})         & Retrieval + Calc \\
\texttt{General}     & Narrative Regulations  & PostgreSQL + Qdrant   & 0 direct tools (Pure synthesis)                & Hybrid RRF + Rerank \\
\bottomrule
\end{tabular}
}
\end{table}
```

---

## IV. BẢNG DỰ BÁO DUNG LƯỢNG TOÀN BÀI SAU KHI HOÀN TẤT

| STT | Hạng mục chỉnh sửa | Vị trí trang cũ | Mức độ cắt giảm | Trạng thái thực hiện |
| :---: | :--- | :---: | :---: | :---: |
| 1 | Xóa Algorithm 2 (Tính học phí) | Trang 11 | **-0.4 trang** | ✅ **Đã xóa** |
| 2 | Xóa Bảng 3 (Allocation lặp lại) | Trang 12 | **-0.4 trang** | ✅ **Đã xóa** |
| 3 | Rút gọn Bảng 2 (Neo4j Schema) | Trang 9 | **-0.4 trang** | ✅ **Đã sửa** |
| 4 | Cắt đoạn lặp 4 bước & công thức RRF | Trang 12–13 | **-0.4 trang** | ⏳ **Cần làm tiếp** |
| 5 | Thu gọn Algorithm 1 (Supervisor) | Trang 10 | **-0.3 trang** | ⏳ **Cần làm tiếp** |
| 6 | Giữ lại Bảng 4 (Lý do định tuyến RQ3)| Trang 12 | Giữ (~0.3 trang) | 📌 **Giữ lại có chọn lọc** |
| **TỔNG** | **DUNG LƯỢNG TIẾT KIỆM PHẦN 3** | | **~1.9 – 2.2 trang** | |

### 🎯 KẾT LUẬN CUỐI CÙNG:
* **Phần 3 (Proposed Model):** Co gọn từ **6.8 trang $\to$ còn ~4.5 trang** (mạch lạc, súc tích, chuyên nghiệp).
* **Tổng thể bài báo:** Giảm từ **20 trang $\to$ còn ~15.8 – 16 trang**, **đạt chuẩn 100% dung lượng hội nghị**, hoàn thành trọn vẹn chỉ đạo của Cô!
