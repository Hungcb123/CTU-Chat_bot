# Đối chiếu bài báo với Hướng dẫn viết

Checklist theo từng mục của [guild_writting.md](file:///E:/RHNA/1Visual/CTU-chat/CTU-Chat_bot/guild_writting.md).
Đánh dấu: ✅ đạt · ⚠️ cần xem lại · ❌ vi phạm rõ.

---

## 1. Title (Mục 2 hướng dẫn)

| Tiêu chí | Đánh giá |
|---|---|
| Nêu đối tượng/vấn đề chính | ✅ "Supervisor-Routed Multi-Agent RAG … University Counseling" |
| Có phương pháp/bối cảnh phân biệt | ✅ "Heterogeneous Knowledge Allocation" |
| Không tính từ tự đánh giá | ✅ |
| Không viết tắt không cần thiết | ✅ RAG phổ biến |

**Kết luận Title: ✅ Đạt**

---

## 2. Abstract (Mục 3 hướng dẫn)

| Tiêu chí | Đánh giá | Ghi chú |
|---|---|---|
| 5 bước: context → objective → methods → results → conclusion | ⚠️ | **Thiếu câu objective rõ** ("This study aims to…"). Abstract nhảy từ problem thẳng sang "We present CTU-Chat" mà không phát biểu mục tiêu nghiên cứu. |
| Có kết quả cụ thể (số liệu) | ✅ | Nhiều số liệu chi tiết |
| Không dành quá nhiều chỗ cho lý thuyết | ✅ | |
| Không trích dẫn trong Abstract | ✅ | |
| Kết luận/hàm ý bám sát kết quả | ✅ | Câu cuối có hedging phù hợp |
| **Độ dài** | ⚠️ | ~230 từ, nằm trong khoảng 150–300, nhưng rất dày số liệu → khó đọc nhanh. Hướng dẫn nói Abstract cần "đọc độc lập vẫn hiểu". Quá nhiều con số kỹ thuật (CI, token %, latency) có thể cản trở mục đích này. |

> [!WARNING]
> **Sai sót chính:** Thiếu câu phát biểu mục tiêu nghiên cứu tường minh. Hướng dẫn bước 2 yêu cầu "Phát biểu mục tiêu/câu hỏi nghiên cứu" rõ ràng.

---

## 3. Introduction (Mục 4 hướng dẫn — 6 thành phần)

| Thành phần | Đánh giá | Vị trí |
|---|---|---|
| Topic Introduction | ✅ | Đoạn 1: CTU, quy mô, nhu cầu tư vấn |
| Topic Background | ✅ | Đoạn 1–2: CAAS, REBot, RAG, GraphRAG, có trích dẫn |
| Research Problem/Gap | ✅ | Đoạn 3: ba gaps rõ ràng |
| Research Objective | ✅ | Đoạn 4: "The objective of this study…" + 3 RQs |
| Research Methodology (brief) | ✅ | Đoạn 5: hypothesis, approach summary |
| Paper Outline | ✅ | Đoạn cuối: Section 2–5 |
| Contributions | ✅ | C1–C3 có và cụ thể |

**Kiểm tra bổ sung:**

| Tiêu chí | Đánh giá | Ghi chú |
|---|---|---|
| Khoảng trống có bằng chứng nguồn | ⚠️ | Gaps ở đoạn 3 nói "Together with the representative literature synthesized in Section 2" — gap tự nó không có trích dẫn trực tiếp tại chỗ, phải đọc sang Section 2 mới thấy. Hướng dẫn mục 4.2 đoạn 3: "Khoảng trống phải có thể kiểm chứng bằng tài liệu liên quan." |
| Contributions = đã thực hiện, không phải kỳ vọng | ✅ | "We implement…", "We model…", "We evaluate…" |
| Outline khớp sections thực tế | ✅ | Sec 2–5 tồn tại |

> [!NOTE]
> **Sai sót nhỏ:** Ba gaps nên có ít nhất một trích dẫn trực tiếp tại chỗ thay vì chỉ tham chiếu "Section 2".

**Kết luận Introduction: ✅ Cơ bản đạt, cần bổ sung trích dẫn cho gaps.**

---

## 4. Related Work → đóng vai trò Topic Background mở rộng

Hướng dẫn không bắt buộc phần riêng Related Work. Bài dùng cấu trúc LNCS nên tách riêng — hợp lý.

| Tiêu chí | Đánh giá | Ghi chú |
|---|---|---|
| Nhóm theo cách tiếp cận, không liệt kê rời rạc | ✅ | 6 subsections theo chủ đề |
| Tạo thành lập luận dẫn đến gap | ✅ | §2.7 Comparative Synthesis |
| Trích dẫn đúng | ✅ | Mỗi claim có cite |

**Kết luận Related Work: ✅ Đạt**

---

## 5. Proposed Model ≈ Methods (Mục 5 hướng dẫn)

| Tiêu chí | Đánh giá | Ghi chú |
|---|---|---|
| Study design/setup | ✅ | Architecture 3 tiers, design principles |
| Data/materials | ⚠️ | Neo4j schema (1500 nodes, 3800 edges, 113 curricula) có, nhưng **nguồn dữ liệu gốc** (244 documents, 559 records) chỉ nhắc ở Section 4. Methods nên nói rõ nguồn dữ liệu đầu vào. |
| Procedure/method | ✅ | Routing algorithm, Cypher tools, hybrid retrieval |
| Baselines/comparison | ⚠️ | **Không có trong Section 3** — baselines chỉ xuất hiện ở Section 4. Hướng dẫn nói Methods cần "Phương pháp đối chứng, lý do chọn." |
| Metrics | ❌ | **Metrics nằm hoàn toàn ở Section 4.** Hướng dẫn nói Methods cần "Chỉ số chính và phụ, cách tính." |
| Analysis approach | ⚠️ | Bootstrap CI protocol chỉ ở Section 4 |
| Reproducibility | ⚠️ | Chunk sizes, model names có. Nhưng **LLM model, temperature, hardware** chỉ ở Section 4. |

> [!IMPORTANT]
> **Sai sót chính:** Section 3 (Proposed Model) chỉ mô tả kiến trúc, thiếu nhiều thành phần Methods theo hướng dẫn: baselines, metrics, analysis protocol, model/hardware specs. Tất cả đẩy sang Section 4 — hợp lý về mặt bố cục LNCS, nhưng nếu đối chiếu nghiêm ngặt với hướng dẫn thì Methods chưa đầy đủ tại một phần duy nhất.

**Kết luận: ⚠️ Nội dung Methods đầy đủ nhưng phân tán giữa Section 3 và 4. Với format LNCS thường chấp nhận, nhưng hướng dẫn khuyến nghị gom.**

---

## 6. Results (Mục 6 hướng dẫn)

| Tiêu chí | Đánh giá | Ghi chú |
|---|---|---|
| Sắp xếp theo RQ | ✅ | 3 Scenarios → 3 RQs |
| Bối cảnh → chỉ số → bảng → quan sát | ✅ | Mỗi scenario nêu setup → bảng → highlight |
| Đơn vị, số mẫu đầy đủ | ✅ | N, R, CI rõ |
| Không chỉ nói "better" mà thiếu bằng chứng | ✅ | Luôn có số, CI |
| Tham chiếu Figure/Table đúng | ✅ | |
| **Không trộn quá nhiều bình luận** | ⚠️ | Phần Discussion nằm cùng Section 4 (§4.4) — kỹ thuật không vi phạm, nhưng ranh giới Results vs Discussion mờ. Scenario descriptions pha trộn kết quả với một số diễn giải nhẹ. |

**Kết luận Results: ✅ Cơ bản đạt**

---

## 7. Discussion (Mục 7 hướng dẫn — 6 bước)

| Bước | Đánh giá | Ghi chú |
|---|---|---|
| Recap phát hiện chính | ✅ | Mỗi RQ mở bằng recap |
| Interpret/giải thích | ⚠️ | Có interpretation nhưng **hầu như không giải thích cơ chế tại sao** specialist tốt hơn hay kém hơn — chủ yếu report CI và point estimates. |
| Compare/đối chiếu nghiên cứu trước | ❌ | **Không có bất kỳ trích dẫn nào trong Discussion.** Hướng dẫn mục 7 bước 3: "Đối chiếu các nghiên cứu trước bằng trích dẫn chính xác." |
| Contribution | ⚠️ | Ngụ ý qua kết quả nhưng không phát biểu tường minh "This study contributes…" trong Discussion. |
| Strengths and limitations | ✅ | §4.5 Threats to Validity riêng, chi tiết |
| Implications and future work | ⚠️ | Implications rất ít trong Discussion — chủ yếu ở Conclusion |

> [!CAUTION]
> **Sai sót nghiêm trọng nhất:** Discussion hoàn toàn **không đối chiếu với nghiên cứu liên quan**. Không có trích dẫn nào. Hướng dẫn yêu cầu rõ: "Đối chiếu nghiên cứu khác" và "giải thích tương đồng hoặc khác biệt."

> [!WARNING]
> **Discussion quá nặng về báo cáo số liệu**, đọc giống Results phần 2 hơn là thảo luận ý nghĩa. Hướng dẫn phân biệt: "kết quả này có thể do cơ chế Y và có ý nghĩa Z" thuộc Discussion.

---

## 8. Conclusion (Mục 8 hướng dẫn — 5 bước)

| Bước | Đánh giá | Ghi chú |
|---|---|---|
| Restate aim | ✅ | "This study developed and evaluated CTU-Chat…" |
| Summarize findings | ✅ | 3 RQs tóm tắt |
| Explain significance | ✅ | Đoạn 2 "consistent with the interpretation that…" |
| Implications/limitations | ✅ | Deployment implications + limitations rõ |
| Closing/future direction | ✅ | 3 hướng cụ thể |
| **Không chép Abstract nguyên văn** | ⚠️ | Nhiều câu gần giống Abstract (cùng số liệu, cùng cấu trúc). Không chép 100%, nhưng overlap đáng kể. Hướng dẫn hình 4 cảnh báo lỗi: "Chép Abstract nguyên văn." |
| Không thêm dữ liệu mới | ✅ | |

> [!WARNING]
> **Conclusion trùng lặp nhiều với Abstract.** Đoạn 1 Conclusion gần như restate toàn bộ số liệu đã có trong Abstract. Hướng dẫn mục 9 bảng so sánh: Conclusion phải "phát triển hơn phần diễn giải, đóng góp… không chỉ đọc lại Abstract."

---

## 9. Abstract vs Conclusion (Mục 9)

| Khía cạnh | Đánh giá |
|---|---|
| Abstract cho cái nhìn nhanh, độc lập | ✅ |
| Conclusion chốt câu trả lời + ý nghĩa | ⚠️ Ý nghĩa có nhưng ngắn so với lượng số lặp |
| Conclusion ≠ Abstract copy | ⚠️ Overlap cao |

---

## 10. References (Mục 10)

| Tiêu chí | Đánh giá |
|---|---|
| Có nguồn cho phát biểu hiện trạng | ✅ |
| Cặp cite ↔ bib khớp | Cần kiểm tra bib file, chưa audit |
| Thống nhất chuẩn | ✅ splncs04.bst |

---

## 11. Hình, bảng, caption, alt text (Mục 11)

| Tiêu chí | Đánh giá | Ghi chú |
|---|---|---|
| Figure có caption cụ thể | ✅ | Fig 1 caption chi tiết |
| Table có caption + footnote giải thích | ✅ | Tables 1–4 có parbox notes |
| Tham chiếu trong bài đúng | ✅ | |
| **Alt text** | ❌ | **Không có alt text cho Figure 1.** `\includegraphics` không có alt text mechanism trong LaTeX mặc định, nhưng hướng dẫn yêu cầu "hình mang thông tin có alt text phù hợp nếu bản xuất bản hỗ trợ/yêu cầu." |

---

## 12. Traceability (Mục 12.2)

| RQ | Methods | Results | Discussion | Conclusion |
|---|---|---|---|---|
| RQ1 | ✅ Scenario 3 protocol | ✅ Table 4 | ✅ Answering RQ1 | ✅ |
| RQ2 | ✅ Scenario 2 protocol | ✅ Table 3 | ✅ Answering RQ2 | ✅ |
| RQ3 | ✅ Scenario 1 protocol | ✅ Tables 1–2 | ✅ Answering RQ3 | ✅ |

**Kết luận Traceability: ✅ Đạt — mọi RQ có đường dẫn đầy đủ.**

---

## Tổng hợp sai sót theo mức độ

### ❌ Cần sửa

| # | Vấn đề | Vị trí | Tham chiếu hướng dẫn |
|---|---|---|---|
| 1 | **Discussion không đối chiếu nghiên cứu trước** — zero citations | [04-experiments.tex §4.4](file:///E:/RHNA/1Visual/CTU-chat/PAPER/sections/04-experiments.tex#L172-L181) | Mục 7 bước 3 |
| 2 | **Abstract thiếu câu objective** ("This study aims to…") | [00-abstract.tex](file:///E:/RHNA/1Visual/CTU-chat/PAPER/sections/00-abstract.tex#L4-L5) | Mục 3.1 bước 2 |

### ⚠️ Nên cải thiện

| # | Vấn đề | Vị trí | Tham chiếu hướng dẫn |
|---|---|---|---|
| 3 | Discussion đọc như Results phần 2 — thiếu giải thích cơ chế | §4.4 | Mục 7 bước 2 |
| 4 | Conclusion overlap cao với Abstract (cùng số liệu, cùng cấu trúc) | [05-conclusion.tex](file:///E:/RHNA/1Visual/CTU-chat/PAPER/sections/05-conclusion.tex#L7) | Mục 8, Mục 9 |
| 5 | Introduction gaps thiếu trích dẫn trực tiếp tại chỗ | [01-introduction.tex L13](file:///E:/RHNA/1Visual/CTU-chat/PAPER/sections/01-introduction.tex#L13) | Mục 4.2 đoạn 3 |
| 6 | Abstract quá dày số liệu kỹ thuật cho mục đích "đọc nhanh độc lập" | 00-abstract.tex | Mục 3.2 checklist |
| 7 | Figure không có alt text | 03-proposed-model.tex | Mục 11 |
| 8 | Methods phân tán giữa Section 3 và 4 (baselines, metrics, hardware ở §4) | — | Mục 5 |

---

## Đối chiếu Review Comments ([paper_review_comments.md](file:///E:/RHNA/1Visual/CTU-chat/CTU-Chat_bot/paper_review_comments.md))

7 góp ý từ reviewer, đã grep toàn bộ sections — **tất cả đã sửa**, không còn cụm gốc nào:

| # | Góp ý | Cụm gốc cần tìm | Trạng thái |
|---|---|---|---|
| 1 | §4.1: thay `is established upon` → `uses` | `is established upon` | ✅ Đã sửa |
| 2 | §4.1: tách câu dài generate→review→check | `ensure query novelty` | ✅ Đã sửa |
| 3 | §3.2: thay `without ontological overhead` → `using a simplified schema` | `without ontological overhead` | ✅ Đã sửa |
| 4 | Trước §3: thay `structural imperatives` → `requirements` | `structural imperatives` | ✅ Đã sửa |
| 5 | §2.7: gaps không dùng Title Case | `Lack of Bounded` | ✅ Đã sửa |
| 6 | §2.7: gap 2 đổi tên → `limitations of uniform representation` | `Uniform Representation Bottleneck` | ✅ Đã sửa |
| 7 | §2.4: tách câu GraphRAG dài | `motivating selective rather than universal graph use` | ✅ Đã sửa |

> [!TIP]
> Tất cả 7 review comments đã được xử lý trong bản hiện tại. Không cần sửa thêm cho phần này.

### So với hướng dẫn Discussion (Mục 7)

Review comments tập trung vào **diễn đạt/ngữ pháp** (§2.4, §2.7, §3.2, §4.1), không đề cập đến yêu cầu **đối chiếu nghiên cứu trước** trong Discussion. Sai sót ❌ #1 (Discussion zero citations) và ⚠️ #3 (Discussion thiếu giải thích cơ chế) trong audit vẫn chưa được reviewer chỉ ra nhưng **vẫn vi phạm hướng dẫn mục 7 bước 2–3**:

- **Bước 2 (Interpret):** Discussion hiện tại hầu như chỉ report CI và point estimates, thiếu "Diễn giải cơ chế/khả năng giải thích."
- **Bước 3 (Compare):** Zero citations trong Discussion — không đối chiếu REBot, CAAS, AutoGen hay bất kỳ prior work nào.
- **Bước 4 (Contribution):** Không phát biểu tường minh đóng góp trong Discussion.
- **Bước 6 (Implications):** Implications rất ít — chủ yếu đẩy sang Conclusion.
