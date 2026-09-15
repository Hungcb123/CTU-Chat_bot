# Triển khai cải thiện CTU-Chat và kiểm thử bằng Colab reranker

## Tóm tắt

Thực hiện toàn bộ kế hoạch theo từng gate: sửa phép đo → routing → tool calling → retrieval/reranking → evidence assembly → đánh giá lại. Không chỉnh Paper_v6 trong đợt này.

GitNexus cho thấy `classify_query_intent` có mức ảnh hưởng **CRITICAL**: 22 caller trực tiếp, 52 symbol và 7 luồng benchmark/RAG. Vì vậy phải giữ nguyên signature hiện tại, bổ sung contract/validator tương thích và chạy regression trước khi đi tiếp. `build_agent_graph`, retrieval, reranker và `retrieve_configurations` hiện có blast radius LOW.

Reranker sẽ chạy trên Colab theo chế độ **fail-closed**. Nếu endpoint lỗi, benchmark phải dừng; tuyệt đối không trộn kết quả có reranker và không reranker.

## Thay đổi chính

### 1. Khóa measurement contract

- Tạo scorer dùng chung cho smoke-20, Scenario 3 và multi-vs-single:
  - Numeric: so sánh sau type coercion.
  - Khóa: chuẩn hóa `52`, `K52`, `khóa 52`.
  - Alias: `VLVH` ↔ `vừa làm vừa học`, `Khối IV` ↔ `Khối ngành IV`.
  - Free text: normalized containment hoặc functional equivalence.
  - Tool hai entity: chấp nhận đảo thứ tự nếu semantics đối xứng.
- Tách kết quả thành `Route`, `Intent`, `Tool Selection`, `Argument Validity`, `Execution`, `Retrieval`, `Answer`.
- Metric ba trạng thái: `pass`, `fail`, `not_evaluated`.
- 44/60 case không có result oracle phải được ghi `not_evaluated`, không tự động pass.
- Không sửa log lịch sử; rescore vào run directory mới kèm hash dataset, prompt, model, tool schema và commit/diff.
- Duplicate ID robustness hiện đã được xử lý; thêm validation để không tái diễn.

### 2. Hợp nhất routing và tool contract

- Tạo contract machine-readable duy nhất cho từng intent, gồm:
  - Positive triggers và exclusions/precedence.
  - Specialist owner.
  - Retrieval lanes.
  - Allowed tools.
  - Required/optional arguments.
- Giữ nguyên `QueryIntent`, `RouteDecision` và signature `classify_query_intent`.
- Thêm validator sau LLM supervisor:
  - Lưu `raw_agent/raw_intent`.
  - Repair agent–intent pair không hợp lệ.
  - Chỉ override LLM khi deterministic rule có tín hiệu mạnh; không override bằng `other` hoặc `ambiguous_tuition`.
  - Lưu `repaired_agent/repaired_intent/reason`.
- Supervisor prompt, deterministic router, specialist tool lists và evaluator đều lấy mapping từ cùng contract.
- Thêm feature flag để tắt route repair và rollback nhanh.
- Thêm confusion tests cho học phí sư phạm, vay tiền đóng học phí, học bổng tài trợ, lệ phí hành chính, miễn thi và VLVH.

Tool calling:

- Sinh tool-gate instruction theo từng specialist từ contract, không dùng một prompt chung chứa rule thừa.
- Chuẩn hóa argument trước khi invoke nhưng không đổi public tool signatures.
- Validate GPA, ĐRL, phần trăm, số tiền và số lượng entity trước execution.
- Phân loại tool output thành `found`, `valid_no_result`, `invalid_argument`, `backend_failure`.
- Nếu query đủ dữ kiện nhưng agent không gọi tool bắt buộc, cho đúng một repair pass; tổng tool call vẫn không vượt policy.
- Production graph và benchmark phải dùng chung normalization/validation, tránh trường hợp chỉ “sửa điểm benchmark”.

### 3. Cải thiện retrieval và reranking

First-stage retrieval:

- Giữ `AdvancedChunkingEngine.retrieve()` trả `List[Document]` để không phá caller.
- Gắn trace vào metadata/log: dense rank/score, BM25 rank/score, RRF score, lane, source và parent/child ID.
- Thêm lexical-anchor detector cho:
  - Mã ngành/môn/quyết định.
  - `K45`–`K52`, năm học.
  - CLC, CTTT, VLVH.
  - Vallet, SCIC, Robocon và tên biểu mẫu.
- Dùng query-adaptive weighted RRF; BM25 được tăng trọng số khi có lexical anchor.
- Deduplicate/quota theo source trước rerank; một source không được chiếm candidate pool bằng nhiều parent chunks.
- Candidate pool dựa trên recall ceiling, không tiếp tục cố định `max(2 × top_n, 8)`.

Reranker:

- Rerank source representatives bằng:
  - Metadata header.
  - Best-matching child/table row.
  - Span bao quanh lexical hits.
- Bỏ cách luôn lấy 1.000 ký tự đầu parent; giới hạn mới cấu hình được và mặc định 2.400 ký tự của evidence discriminative.
- Ghi cross-encoder score cho từng candidate.
- Temporal prior chỉ áp dụng khi query hỏi mới nhất/hiện hành; năm cụ thể dùng metadata match, không mặc định ưu tiên tài liệu mới hơn.
- Exact entity/code candidate của BM25 được bảo vệ; chỉ bị đẩy xuống khi cross-encoder vượt calibrated margin.
- Tune trên `scenario12_dev.jsonl`, không dùng current held-out để chọn tham số:
  - BM25 weight: `1.0, 1.25, 1.5, 2.0`.
  - Candidate pool: `20, 30, 40`.
  - Source quota: `1, 2`.
  - Reranker override margin: `0.05, 0.10, 0.15, 0.20`.
- Chọn cấu hình theo thứ tự: không mất exact-anchor gold top-3 → Hit@1 cao nhất → MRR@10 cao nhất → candidate pool nhỏ hơn.

Re-index:

- Tạo compact row children cho bảng học phí với metadata canonical về program, code, cohort, program type và unit.
- Dùng blue-green re-index với version mới sinh theo UTC; không ghi đè collection đang live.
- Chạy `preflight → build → validate`; ghi lại alias cũ.
- Smoke retrieval và dev suite phải đạt gate trên collection mới trước khi chuyển alias.
- Chuyển alias atomically; nếu post-activation smoke fail thì trả alias về collection cũ.

### 4. Evidence assembly và answer generation

- Context packing đa dạng theo source; mặc định tối đa hai evidence blocks/source.
- Structured tool/graph result đi trong evidence envelope có tool name, normalized args, status và provenance.
- Thứ tự ưu tiên khi xung đột:
  1. Structured tool result hợp lệ.
  2. Neo4j/catalog đã chuẩn hóa.
  3. Tài liệu chính thức khớp năm/phiên bản.
  4. Evidence retrieval còn lại.
- Nếu hai nguồn cùng mức ưu tiên mâu thuẫn, câu trả lời phải báo uncertainty.
- Mọi numeric answer phải có evidence span hoặc structured result trong trace.
- Không dùng Ragas Faithfulness làm bằng chứng duy nhất.

## Quy trình kiểm thử

1. **Deterministic gate**
   - Chạy unit tests bằng `unittest` vì environment hiện chưa cài `pytest`.
   - Kiểm tra contract parity, normalization, invalid arguments, route repair, fusion, temporal gating và remote failure.
   - Chạy `git diff --check`.

2. **Routing/tool gate**
   - Smoke-20 strict ba lần liên tiếp: 20/20 mỗi lần.
   - Full routing: accuracy không dưới 97%, không domain nào giảm quá 2 percentage points.
   - Full 60 tools: selection ≥ 0.98, functional arguments ≥ 0.97.
   - Robustness suppression ≥ 0.95.

3. **Colab preflight**
   - Người dùng chạy `notebooks/ctu_remote_reranker_colab.ipynb` và tự đặt URL/key vào `.env`; không đưa secret vào git/chat.
   - Đặt `RAG_RERANKER_BACKEND=remote` và `RAG_REMOTE_RERANKER_FAIL_OPEN=false`.
   - Health/ranking sentinel phải pass.
   - Mọi benchmark record phải xác nhận remote reranker thành công; lỗi HTTP làm run fail.

4. **Retrieval gate**
   - Bật Qdrant, PostgreSQL và Neo4j bằng Docker Compose.
   - Chạy smoke retrieval strict; hai target Vallet và bản sao văn bằng phải Hit@1.
   - Candidate Recall@10 trên smoke đạt 1.0.
   - Tune chỉ trên dev.
   - Sau khi freeze config, chạy current 50-case held-out đúng một lần:
     - Không mất 48 case E5 vốn đúng.
     - Hai lỗi cũ phải được sửa nếu không gây regression.
     - Báo aggregate, per-domain, per-case và confidence interval.
   - Vì current held-out đã từng được xem để phân tích lỗi, kết quả mới chỉ được gọi là post-hoc regression; không dùng như một unbiased test mới trong paper.

5. **Answer và architecture gate**
   - Chạy smoke `--mode all --execute-tools --strict-targets`.
   - Kiểm tra numeric provenance và conflict handling.
   - Rerun multi-vs-single protocol v2 ở 11 và 27 tools với cùng model, query, retry và budget.
   - Chỉ kết luận multi-agent tốt hơn nếu paired CI không cắt 0; nếu không, báo descriptive trend.

6. **Hoàn tất**
   - Chạy toàn bộ regression liên quan.
   - Chạy GitNexus impact trước từng symbol được sửa.
   - Chạy `npx gitnexus detect-changes -r SchoolChatBot` trước commit.
   - Báo rõ changed symbols, execution flows, run directories, cấu hình thắng và mọi gate chưa đạt.
   - Không commit nếu chưa được yêu cầu.

## Giả định đã khóa

- Không sửa Paper_v6 trong đợt này.
- Không reset hoặc ghi đè các thay đổi hiện có trong worktree.
- Cho phép versioned re-index và atomic alias switch; không re-index in-place.
- Colab reranker chạy fail-closed; không dùng CPU fallback trong benchmark chính.
- Không chỉnh fixture/oracle sau khi thấy patch fail, trừ khi chứng minh label sai và ghi migration rõ ràng.
- Nếu một acceptance gate không đạt, dừng trước full held-out/Phase 6, giữ log và báo nguyên nhân; không hạ threshold để làm kết quả đẹp.
