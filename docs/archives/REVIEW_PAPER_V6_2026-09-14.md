# Rà soát Paper v6 — 2026-09-14

## Phạm vi rà soát

- Bản nguồn hiện hành: `data/Paper_v6/`.
- PDF build hiện hành: `data/Paper_v6/main.pdf` — 16 trang, build lúc 14:12 ngày 2026-09-14.
- File `main (2).pdf` được gửi kèm là một snapshot khác: 18 trang và không trùng hash với `data/Paper_v6/main.pdf`.
- Báo cáo này lấy **Paper v6 hiện tại** làm nguồn sự thật. Không chỉnh manuscript, code, dataset hoặc log.

## Kết luận nhanh

Paper v6 đã sửa được hai lỗi thấy trong PDF snapshot: Abstract hiện ghi đúng `0.9600 Hit@1`, citation về quy mô CTU đã render thành `[1]`, và PDF hiện còn 16 trang.

Tuy nhiên, chuỗi Gap 3 → RQ3 → Scenario 1 → Discussion → Conclusion vẫn chưa đồng bộ. Panel B domain-stratified đã bị mất khỏi bảng Scenario 1. Đoạn “Multi-Agent Decomposition vs. Monolithic Single-Agent Baseline” không cần thiết ở cấu trúc hiện tại và đang làm lập luận yếu đi.

## Failure rate có thật sự cần thiết không?

### Khuyến nghị: bỏ toàn bộ đoạn này

Đoạn cần cân nhắc bỏ nằm tại `sections/04-experiments.tex`, dòng 130–131.

Nó không cần thiết để trả lời RQ1 vì Scenario 3 đã có ba nguồn bằng chứng trực tiếp:

1. LLM supervisor so với rule-based router.
2. Độ tin cậy của các specialist tools.
3. Adversarial gating và bounded execution.

Giữ đoạn failure-rate hiện tại tạo ra năm vấn đề:

- Paper chỉ công bố riêng failure `33.3%` của `tra_cuu_nganh`, nhưng không công bố bảng tổng thể multi-agent vs. single-agent.
- Artifact đầy đủ cho kết quả mixed, không chứng minh multi-agent thắng tổng thể:
  - End-to-End Pass: Multi `87.78%`, Single `88.89%`.
  - Argument EM: Multi `87.78%`, Single `88.89%`.
  - Result Accuracy: Multi `98.33%`, Single `99.44%`.
  - Safe Result: Multi `88.33%`, Single `91.67%`.
  - `tra_cuu_nganh` là một subgroup mà Multi thắng `100.0%` so với `66.7%`; dùng riêng subgroup này dễ bị xem là cherry-picking.
- T4→T7 là so sánh full stack với “w/o Subspace Governance”, không phải cùng benchmark monolithic 11-tool vừa được nhắc ở đầu đoạn.
- T4→T7 thay đổi nhiều yếu tố, nên không cô lập riêng tác động của domain decomposition.
- Claim `p < 0.001` không có statistical-test protocol, test statistic hoặc bảng kết quả hỗ trợ. Faithfulness `0.8677 vs. 0.8415` cũng xuất hiện trong prose nhưng không có trong bảng Scenario 2.

### Khi nào mới nên giữ?

Chỉ nên giữ nếu paper bổ sung đầy đủ thiết kế benchmark, bảng aggregate multi-vs-single, cách tính significance và diễn giải trung tính các metric mà Single tốt hơn. Việc này tốn diện tích và không giúp nhiều cho RQ1 hiện tại, nên phương án hợp lý nhất là bỏ.

## Các lỗi quan trọng còn lại trong Paper v6

### 1. Gap 3 và RQ3 vẫn lệch với thí nghiệm

- Introduction dòng 13: Gap 3 là “lack of representation-aware evidence routing”.
- Related Work dòng 53: Gap 3 vừa nói routing vừa kéo deterministic arithmetic vào.
- RQ3 dòng 27–28 hỏi intent-guided selection “affect” retrieval effectiveness **và answer accuracy**.
- Scenario 1 chỉ đo retrieval metrics.
- Discussion lại có tiêu đề “Representation-Aware Retrieval Effectiveness” và thận trọng không quy causal effect cho routing.

RQ3 hiện hỏi một causal effect và answer accuracy mà Scenario 1 không trực tiếp kiểm định. Nên đưa Gap 3/RQ3 về comparative retrieval effectiveness như phiên bản đã thống nhất, hoặc phải thiết kế lại evaluation. Với ràng buộc không rerun, phương án đầu hợp lý hơn.

### 2. Panel B domain-stratified đã bị mất

Paper v6 vẫn:

- tuyên bố Scenario 1 đánh giá aggregate và domain-stratified;
- báo bốn giá trị domain của E5 trong Results;
- Discussion so sánh pattern E1/E4/E5 theo domain.

Nhưng Table Scenario 1 hiện chỉ còn bảng aggregate E1–E5. Không còn Panel B chứa toàn bộ E1–E5 theo bốn domain. Vì vậy người đọc không thể kiểm chứng các nhận xét “Financial tập trung lợi ích”, “General E4=E5”, hay “Academic/Scholarship không hơn E1” từ paper.

Nên khôi phục Panel B từ approved run và ghi rõ đây là descriptive subgroup analysis, không phải controlled causal ablation.

### 3. Conclusion kéo answer metric trở lại RQ3

Conclusion dòng 7 đặt `Fact EM 62.03%` ngay trong câu trả lời RQ3. Fact EM là end-to-end answer metric của Scenario 2/RQ2, không phải retrieval metric của Scenario 1/RQ3. Điều này tái tạo đúng lỗi chồng lấn Results–Discussion đã sửa trước đó.

### 4. Hai cách diễn đạt số liệu cần sửa

- `62.03% − 55.72% = 6.31 percentage points`, không phải “+6.31% absolute gain”. Nếu muốn relative improvement thì là khoảng `11.32%` so với T1.
- Context Precision `0.6977 → 0.5683` giảm `0.1294`, tức `12.94 percentage points`, hoặc `18.55% relative to T4`. Con số `−18.3% relative` hiện không khớp các giá trị đã làm tròn trong bảng.

### 5. Claim benchmark construction mạnh hơn bằng chứng được báo cáo

Experimental Benchmark dòng 13 nói hai annotator và “ensuring high ... inter-annotator reliability”, nhưng paper không báo raw agreement, Cohen’s kappa hay metric reliability nào. Consensus resolution không tự chứng minh inter-annotator reliability.

Cùng đoạn đó gọi test set là “out-of-distribution” và “blind”, dù test vẫn dùng cùng chín category và paper không mô tả distribution shift hoặc quy trình giữ blind. Nếu không có protocol riêng, chỉ nên gọi là held-out test set.

### 6. Tên GPU có khả năng sai

Computational Infrastructure dòng 17 ghi `NVIDIA RTX 1060 GPU (4 GB VRAM)`. Dòng sản phẩm phổ biến là **GeForce GTX 1060**, không phải RTX 1060. Cần đối chiếu máy thực tế và sửa đúng model; không nên suy đoán model khác.

### 7. Một số kết luận Scenario 2 vẫn hơi mạnh

Các cụm “consistently outperforms all baselines”, “substantially reduces ... hallucinations”, và “provides effective anchors against relation hallucination and decision drift” cần metric/test tương ứng. Table 2 cho thấy T1 vẫn cao hơn T4 ở Answer Correctness, còn paper không định nghĩa hallucination rate hoặc decision-drift metric.

## Những phần hiện đã ổn

- Abstract của Paper v6 dùng đúng `0.9600 Hit@1`.
- Citation quy mô CTU render đúng `[1]` trong PDF v6 hiện tại.
- PDF v6 hiện đúng 16 trang.
- Scenario 1 aggregate báo đúng: E5 đứng đầu Hit@1/MRR@10, hòa E4 ở Hit@3; E1 cao hơn ở P@5/Recall@5.
- E3→E4 được dùng hợp lý để nhận xét tác động của reranker.
- E4→E5 đã được mô tả là integrated bundle, không quy riêng cho routing.
- RQ3 Discussion không lặp cụm số aggregate và không đưa latency result vào.
- `timeout=60s` được giữ đúng vai trò safety bound.
- AC vẫn nằm trong Scenario 2; vấn đề không phải bỏ AC, mà là không kéo answer metrics sang RQ3.

## Thứ tự xử lý đề xuất

1. Bỏ paragraph multi-agent vs. monolithic single-agent hiện tại.
2. Đồng bộ Gap 3 và RQ3 với retrieval effectiveness không-causal.
3. Khôi phục Panel B domain-stratified.
4. Bỏ Fact EM khỏi câu trả lời RQ3 trong Conclusion.
5. Sửa hai phép diễn đạt percentage/relative change.
6. Hạ claim annotation/OOD/blind nếu không có bằng chứng bổ sung.
7. Xác minh tên GPU.
8. Build lại và giữ giới hạn 16 trang.
