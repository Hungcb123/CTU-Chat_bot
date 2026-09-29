# Tổng hợp góp ý chỉnh sửa bản thảo bài báo

> Nguồn: 6 ảnh chụp có đánh dấu và bình luận do tác giả cung cấp. Tài liệu này chỉ tổng hợp các góp ý nhìn thấy trong ảnh; những phần câu bị che hoặc nằm ngoài khung hình không được suy đoán.
>
> Phạm vi: Mục **2.4**, **2.7**, **3.2**, **4.1** và đoạn chuyển tiếp trước Mục 3.

## 1. Bảng tổng hợp góp ý

| STT | Vị trí | Nội dung được đánh dấu | Góp ý trong ảnh | Việc cần sửa |
|---|---|---|---|---|
| 1 | **4.1 — Experimental Benchmark and Protocols** | `is established upon` | “Nên thay bằng: uses” | Thay cụm từ dài, thiếu tự nhiên bằng động từ trực tiếp `uses`; kiểm tra lại ngữ pháp và cấu trúc của cả câu sau khi thay. |
| 2 | **4.1 — Experimental Benchmark and Protocols** | Câu dài bắt đầu bằng `Candidate queries covering diverse conversational phrasing ...` và kết thúc bằng `... ensure query novelty.` | “Câu quá dài. Tách thành 3 câu với từng động từ riêng biệt: generate, review, check duplicate” | Viết thành ba câu lần lượt mô tả **tạo câu hỏi**, **rà soát theo tài liệu chính thức**, **kiểm tra trùng lặp**. |
| 3 | **3.2 — Neo4j Knowledge Graph Specification and Cypher Tool Mechanics** | `without ontological overhead` | “Nên thay bằng: using a simplified schema” | Thay cách diễn đạt mang tính đánh giá bằng mô tả kỹ thuật cụ thể; sửa lại cấu trúc câu nếu cần. |
| 4 | **Đoạn cuối mục 2.7 / ngay trước Mục 3 — Proposed ...** | `structural imperatives` trong câu `These structural imperatives directly motivate ...` | “requirements” | Thay bằng `requirements`; đọc lại câu để bảo đảm cụm danh từ có tiền đề rõ ràng. |
| 5 | **2.7 — Comparative Synthesis and Research Gaps** | Tên ba gap được viết theo kiểu viết hoa chữ cái đầu mỗi từ; cụ thể ảnh hiển thị `(1) Lack of Bounded Multi-Agent Orchestration`, `(2) The Uniform Representation Bottleneck`, và `(3) Absence of ... Routing` (phần giữa của tên thứ ba bị cắt trong ảnh). | “Các gap 1, 2, 3 không nên viết in hoa các chữ cái đầu từ” | Đổi các nhãn gap sang kiểu chữ thường thông thường (*sentence case*), trừ tên riêng và từ viết tắt cần giữ nguyên. Không tự điền phần nhãn thứ ba bị khuất. |
| 6 | **2.7 — Comparative Synthesis and Research Gaps** | `The Uniform Representation Bottleneck` | “Nên thay bằng: The limitations of uniform representation” | Đổi cách đặt tên gap thứ hai theo đúng cụm đề xuất; khi đặt trong câu, cân nhắc chữ hoa đầu câu/đầu nhãn một cách nhất quán với góp ý số 5. |
| 7 | **2.4 — Knowledge Graphs and GraphRAG** | Câu dài bắt đầu `However, universal graph extraction across institutional corpora ...` và kết thúc `... motivating selective rather than universal graph use.` | “Nên tách câu để lập luận mạnh và súc tích hơn.” | Tách phần **hạn chế/rủi ro của trích xuất đồ thị đại trà** khỏi phần **hệ quả đối với lựa chọn kiến trúc**. |

## 2. Đề xuất chỉnh sửa cụ thể

Các câu dưới đây là **gợi ý biên tập**, không phải trích nguyên văn lời người góp ý. Chỉ chốt những chi tiết đã được xác nhận trong bản thảo và thực nghiệm.

### 2.1. Mục 4.1 — Diễn đạt cơ sở đánh giá bằng động từ trực tiếp

**Cụm gốc:** `our evaluation is established upon a corpus of 200 administrative queries`

**Đề xuất:** `our evaluation uses a corpus of 200 administrative queries`

Ví dụ mở đầu sau khi chỉnh:

> To support empirical evaluation across representative counseling scenarios, our evaluation uses a corpus of 200 administrative queries constructed via a document-grounded, semi-automated protocol over official Can Tho University (CTU) statutes.

**Lưu ý:** Việc thay `is established upon` bằng `uses` phải đồng thời lược bỏ `is`; không thay máy móc thành `is uses`.

### 2.2. Mục 4.1 — Tách quy trình xây dựng bộ câu hỏi thành ba câu

**Câu gốc trong ảnh:**

> Candidate queries covering diverse conversational phrasing (e.g., student colloquialisms, prerequisite rules, fee schedules) were generated from statutory articles and underwent author-guided review against official decrees to verify ground-truth intents, gold reference passages, and factual answers, with lexical and semantic duplicate checks applied to ensure query novelty.

**Đề xuất (ba thao tác: generate → review → check duplicates):**

> Candidate queries were generated from statutory articles to cover diverse conversational phrasing (e.g., student colloquialisms, prerequisite rules, and fee schedules). The authors reviewed these queries against official decrees to verify ground-truth intents, gold reference passages, and factual answers. Lexical and semantic duplicate checks were then applied to identify duplicate queries.

**Điểm cần kiểm tra với quy trình thực tế:** Nếu nhóm chỉ phát hiện hoặc loại bỏ câu hỏi trùng thì viết đúng thao tác đã thực hiện; `ensure query novelty` là tuyên bố mạnh hơn việc *kiểm tra* trùng lặp. Giữ nguyên thuật ngữ chỉ nguồn pháp lý/tài liệu (`statutory articles`, `official decrees`) nếu thực sự chính xác với corpus, hoặc đối chiếu lại nguồn gốc tài liệu trước khi nộp.

### 2.3. Mục 3.2 — Mô tả schema một cách cụ thể

**Cụm gốc:** `without ontological overhead`

**Cụm thay thế được đề nghị:** `using a simplified schema`

Ví dụ áp dụng vào câu hiển thị trong ảnh:

> The Neo4j graph models relational dependencies across academic counseling using a simplified schema, comprising over 1,500 entity nodes and 3,800 relationships ...

**Lưu ý:** Phần sau dấu ba chấm không hiển thị đầy đủ trong ảnh; giữ nguyên mô tả loại node, quan hệ và các con số của bản thảo gốc, đồng thời đối chiếu số lượng với dữ liệu/nhật ký ingest trước khi công bố. Nếu cách ghép `using ... , comprising ...` gây mơ hồ, có thể tách thành hai câu: một câu giới thiệu schema và một câu trình bày số lượng node/relationship.

### 2.4. Đoạn chuyển tiếp trước Mục 3 — Thay từ trừu tượng

**Gốc:** `These structural imperatives directly motivate ...`

**Đề xuất tối thiểu:** `These requirements directly motivate ...`

Kiểm tra xem `These requirements` có chỉ rõ các yêu cầu được nêu ở đoạn ngay trước hay không. Nếu không, cần nêu cụ thể các yêu cầu đó thay vì dùng một đại từ quy chiếu không rõ.

### 2.5. Mục 2.7 — Chuẩn hóa tên các research gaps

**Nguyên tắc:** Không dùng *Title Case* cho nhãn gap trong dòng văn xuôi. Với những nhãn có thể đọc được trong ảnh:

| Gốc | Đề xuất |
|---|---|
| `Lack of Bounded Multi-Agent Orchestration` | `Lack of bounded multi-agent orchestration` (hoặc `lack of bounded multi-agent orchestration` nếu nằm giữa câu) |
| `The Uniform Representation Bottleneck` | `The limitations of uniform representation` (hoặc `the limitations of uniform representation` nếu nằm giữa câu) |
| `Absence of ... Routing` | Chuyển thành `Absence of ... routing` theo quy tắc trên; **kiểm tra lại cụm đầy đủ trong bản thảo** vì ảnh không hiển thị trọn nhãn. |

**Cần làm đồng bộ:** Áp dụng một quy tắc viết hoa cho cả ba nhãn; giữ chữ hoa của các tên riêng, ví dụ tên hệ thống, nếu có. Thay `The Uniform Representation Bottleneck` bằng chính cụm được góp ý thay vì chỉ sửa hoa/thường của cụm cũ.

### 2.6. Mục 2.4 — Tách câu lập luận về GraphRAG

**Câu gốc trong ảnh:**

> However, universal graph extraction across institutional corpora can produce spurious or hallucinated relationships, while forcing narrative legal prose into graphs is structurally unnatural, motivating selective rather than universal graph use.

**Đề xuất tách câu:**

> However, universal graph extraction across institutional corpora can produce spurious or hallucinated relationships. Representing narrative legal prose as a graph may also be unsuitable for some content. These limitations motivate selective rather than universal graph use.

**Lưu ý về mức độ khẳng định:** Giữ phần `can produce` và `may` theo hướng thận trọng; nếu đây là nhận định dựa trên nghiên cứu trước, gắn nguồn tham khảo thích hợp. Nếu là quan sát từ thực nghiệm của bài, liên kết với bằng chứng/ablation tương ứng. Không mặc định rằng mọi văn bản pháp lý đều không phù hợp với graph.

## 3. Checklist trước khi sửa trên bản thảo chính

- [ ] **4.1:** Thay `is established upon` bằng cấu trúc `uses` đúng ngữ pháp.
- [ ] **4.1:** Tách câu dài thành ba câu rõ ba công đoạn *generate → review → check duplicates*.
- [ ] **4.1:** Đối chiếu mô tả kiểm tra trùng lặp và loại trùng với quy trình benchmark thực tế.
- [ ] **3.2:** Thay `without ontological overhead` bằng `using a simplified schema`, kiểm tra lại mạch câu.
- [ ] **Đoạn trước Mục 3:** Thay `structural imperatives` bằng `requirements` và kiểm tra quy chiếu.
- [ ] **2.7:** Chuẩn hóa cách viết hoa của cả ba research gaps.
- [ ] **2.7:** Đổi gap thứ hai thành `the limitations of uniform representation` với chữ hoa phù hợp vị trí.
- [ ] **2.4:** Tách câu dài thành nhận định về hạn chế và hệ quả lựa chọn graph có chọn lọc.
- [ ] Đọc lại sau chỉnh sửa để đảm bảo thuật ngữ, dẫn nguồn và tuyên bố về số liệu không thay đổi ngoài ý muốn.

## 4. Thứ tự xử lý được đề xuất

1. Sửa **Mục 4.1** (hai góp ý có liên quan trong cùng đoạn).
2. Sửa **Mục 2.7** (viết hoa ba gap và thay tên gap thứ hai đồng thời).
3. Sửa **Mục 2.4** (tách câu và kiểm tra tính chắc chắn của lập luận).
4. Sửa **Mục 3.2** và đoạn chuyển tiếp trước **Mục 3** (thay cụm từ, đọc lại ngữ pháp).

---

**Giới hạn nguồn:** Các ảnh là trích đoạn kèm nhận xét, không phải toàn văn paper; các gợi ý trên không xác nhận tính đúng đắn của số liệu, phương pháp hay vị trí chính xác của phần văn bản bị che khuất.
