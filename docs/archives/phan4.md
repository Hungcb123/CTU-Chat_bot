Kết luận: đánh giá trên phần lớn đúng. Trong 5 vấn đề, số 1, 3, 4 và lỗi tổng Scenario 3 là các lỗi có thể chứng minh trực tiếp từ bản hiện tại.
Vấn đề	Phán định	Mức độ
RQ3 không được trả lời đầy đủ	Đúng	Rất cao
Thiếu matched single-agent baseline	Đúng nhưng cần diễn đạt chính xác hơn	Cao
RQ2 bị confounded	Đúng	Rất cao
Benchmark validity bị tuyên bố quá mức	Đúng, có mâu thuẫn artifact	Rất cao
Tổng Scenario 3 sai	Đúng chắc chắn	Rất cao
Repetitions và uncertainty	Đúng một phần	Trung bình–cao
Thiếu bảng domain	Đúng	Trung bình


1. RQ3: nhận xét hoàn toàn đúng
[RQ3 (line 27)](E:/RHNA/1Visual/CTU-chat/PAPER/sections/01-introduction.tex:27) hỏi cả:
- Retrieval effectiveness.
- Answer accuracy.
- Ảnh hưởng của intent-guided routing.
- Khác biệt giữa các domain.
Nhưng Scenario 1 chỉ đo retrieval. Hơn nữa, E5 đồng thời thêm intent governance, graph grounding và parent-child mapping. Paper tự thừa nhận tại [04-experiments.tex (line 132)](E:/RHNA/1Visual/CTU-chat/PAPER/sections/04-experiments.tex:132) rằng không thể quy kết riêng cho routing.
Do đó RQ3 hiện hỏi rộng và có tính causal hơn thiết kế thực nghiệm có thể trả lời.
Không rerun thì nên đổi RQ3 thành:
How does the complete representation-aware evidence configuration compare
with sparse, dense, hybrid, and reranked baselines in retrieval effectiveness,
both overall and across counseling domains?
2. Multi-agent baseline: đúng nhưng không làm RQ1 hoàn toàn vô hiệu
Paper không có đối chứng giữ nguyên model, tools, knowledge và context budget rồi chỉ thay:
single agent ↔ domain-specialized multi-agent
Rule router chỉ so sánh cơ chế routing. T1–T3 cũng không phải matched architectural baseline.
Tuy nhiên, [RQ1 (line 21)](E:/RHNA/1Visual/CTU-chat/PAPER/sections/01-introduction.tex:21) hiện hỏi hệ thống phối hợp “how effectively”, không hỏi multi-agent có tốt hơn single-agent hay không. Vì vậy Scenario 3 vẫn trả lời được operational effectiveness, nhưng không chứng minh comparative benefit of decomposition.
Không rerun thì phải giữ claim theo hướng:
CTU-Chat demonstrates reliable coordination under the evaluated configuration.

Không được viết:
Multi-agent decomposition outperforms or mitigates failures relative to a monolithic agent.

3. RQ2: nhận xét đúng
RQ2 hỏi heterogeneous allocation ảnh hưởng thế nào “compared with a uniform retrieval representation”. Nhưng:
- T1–T3 và T4 khác nhiều thành phần.
- T6 chỉ bỏ Neo4j, không kiểm định toàn bộ heterogeneous allocation.
- Paper chưa giải thích rõ evidence path thay thế khi từng component bị bỏ.
Discussion hiện đã giảm claim khá tốt bằng is associated with và:
do not establish uniform causal effects

Nhưng câu hỏi RQ2 vẫn mang nghĩa causal/comparative mạnh hơn bằng chứng.
Nên thu hẹp thành:
What differences in context and answer quality are observed between the full
heterogeneous configuration, uniform retrieval baselines, and its component
ablations?
4. Benchmark validity: đúng và nghiêm trọng nhất về factual accuracy
Paper hiện tuyên bố tại [04-experiments.tex (line 13)](E:/RHNA/1Visual/CTU-chat/PAPER/sections/04-experiments.tex:13):
- two independent annotators;
- inter-annotator reliability;
- out-of-distribution;
- blind Held-Out Test Set;
- tránh data contamination.
Nhưng artifact [SCENARIO12_HELDOUT_PROTOCOL.md (line 15)](E:/RHNA/1Visual/CTU-chat/CTU-Chat_bot/docs/SCENARIO12_HELDOUT_PROTOCOL.md:15) ghi rõ:
This is an author-reviewed split; it is not independent annotation.

Bộ 50 câu cũng được sinh từ chính CTU Markdown documents và structured tuition records. Có kiểm tra exact duplicate, five-gram similarity và embedding similarity, nhưng điều đó chỉ hỗ trợ query novelty, chưa đủ để gọi là distribution shift hoặc blind evaluation.
Vì vậy các cụm sau phải bỏ nếu không có artifact khác:
two independent annotators
inter-annotator reliability
out-of-distribution
blind
avoid data contamination
Có thể mô tả đúng là:
a document-grounded, author-reviewed held-out query set with lexical and semantic duplicate checks.

5. Tổng Scenario 3: nhận xét đúng chắc chắn
Paper ghi N=550, nhưng chính breakdown hiện tại là:
Rule router        100
LLM supervisor     300
Tool reliability   180
Robustness          60
Total              640
Trong khi [report_rescored.md (line 34)](E:/RHNA/1Visual/CTU-chat/CTU-Chat_bot/tests/report_rescored.md:34) ghi 550 vì report đó chỉ có:
100 + 300 + 90 + 60 = 550
Đây là một conflict thật:
- Paper: Panel B = 180, total = 550.
- report_rescored.md: Panel B = 90, total = 550.
- SCENARIO_3_DE_XUAT.md: 30 tool cases × 3 = 90.
- scenario3_production_tools.json: hiện có 60 cases, tương ứng 180 runs, nhưng chưa có trong báo cáo ground truth chính thức.
Không được chỉ sửa 550 → 640 trước khi xác nhận bộ 60-case là kết quả chính thức. Nếu bộ mở rộng là kết quả cuối, cần có report tương ứng rồi dùng 640. Nếu bám report_rescored.md, phải trả Panel B về 90 runs và bỏ các kết quả academic tools chưa được report đó hỗ trợ.
Các ý còn lại
- Gọi ba repetitions là independent repetitions không chính xác; nên gọi repeated evaluation runs.
- Không có SD/CI không tự động làm benchmark vô hiệu, nhưng không được suy luận statistical significance.
- Academic N=3 và Scholarship N=5 quá nhỏ; paper đã thừa nhận hạn chế này.
- Kết quả domain chỉ nằm trong prose, chưa có bảng kiểm chứng E1/E4/E5 theo domain. Nhận xét này đúng.