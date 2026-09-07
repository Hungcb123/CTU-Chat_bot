# Nhật ký thay đổi mã cho thực nghiệm Table 5 T1–T7

Ngày cập nhật: 2026-09-05

Mục tiêu của thay đổi này là đo riêng Hybrid Retrieval, Graph evidence, reranker và Agent reasoning. Mã benchmark không dùng `Ground Truth`, `Source` hoặc `Category` để quyết định retrieval hay Graph lookup; các trường đó chỉ phục vụ RAGAS và báo cáo sau khi câu trả lời đã được tạo.

## Phạm vi thay đổi

| File | Dòng sau cập nhật | Thực nghiệm | Nội dung |
|---|---:|---|---|
| `Test_Ragas/table5_experiment.py` | 1–214 | T1–T7 | Helper cho dataset CSV, evidence identity, Graph adapter, fingerprint và checkpoint atomic. |
| `Test_Ragas/test_table5_ragas.py` | 1–442 | T1–T7 | Runner CLI, cache T3, T4/T6 rerank, T5 Graph augmentation, T7 fixed evidence, RAGAS theo từng câu và resume. |
| `app/agents/graph.py` | 75, 120, 229, 359–493 | T7 | Chế độ `fixed_context`: nhận evidence của T6, bỏ retrieval và vô hiệu hóa tool ở mọi specialist agent. |
| `tests/test_table5_experiment.py` | 1–53 | T5, T7, checkpoint | Regression tests cho budget evidence, fingerprint T6→T7 và checkpoint answer rỗng. |
| `requirements.txt` | 32–34 | T1–T7 | Nâng Pydantic lên 2.12.5 để tương thích với FastAPI 0.137.0 và cài được môi trường test. |

Mọi khối code mới đều có comment hoặc docstring `T1–T7`, `T5/T6`, hoặc `T7` ngay trong source, nhằm phân biệt với mã vận hành chatbot thông thường.

`requirements.txt` trước đó khóa `pydantic==2.1`, trong khi `fastapi==0.137.0`
yêu cầu Pydantic từ 2.9.0 trở lên. Thay đổi sang `pydantic==2.12.5` chỉ giải
quyết xung đột cài đặt, không thay đổi retrieval, Graph, reranking, agent,
checkpoint hoặc RAGAS.

Sau khi tạo lại virtual environment, runner còn thiếu `torch` và
`sentence-transformers` dù `rag_engine.py` vẫn dùng embedding local. Hai gói
này được bổ sung cho T1–T6. RAGAS 0.2.15, pytest và
`langchain-openai==1.1.10` cũng được khai báo; bản LangChain OpenAI này giữ
tương thích với `langchain-core==1.4.8` của dự án.

Runner thêm project root vào `sys.path` trước các import nội bộ. Nhờ đó lệnh
`python Test_Ragas/test_table5_ragas.py ...` tìm được package `app`, `scripts`
và `Test_Ragas` khi chạy trực tiếp từ PowerShell.

RAGAS judge embedding trong runner được đổi từ model đã ngừng hoạt động
`text-embedding-004` sang model text ổn định `gemini-embedding-001`. Thay đổi
này sửa lỗi HTTP 404 ở metric Answer Relevancy và không ảnh hưởng embedding
local 768 chiều dùng để truy vấn Qdrant.

Gemini 3.1 có thể trả answer dưới dạng content blocks. Helper
`message_content_text()` chỉ lấy trường text hiển thị, ngăn checkpoint lưu cả
metadata/signature. Schema và output mặc định được nâng lên `v3` để các kết quả
sai định dạng của lần chạy thử cũ không được resume như kết quả hợp lệ.

`RUN_TABLE5.md` được cập nhật theo CLI reindex hiện tại: sau `build` phải chạy
`validate`, rồi dùng `activate --index-version ...`. Lệnh `swap --alias-name`
trong tài liệu cũ không còn được `scripts/reindex_all.py` hỗ trợ.

`scripts/build_bm25_index.py` trước đây tự tạo UUID parent mới từ Markdown nên
không khớp các parent đã ghi vào PostgreSQL bởi reindex. Builder mặc định mới
đọc `page_content` và `metadata.doc_id` từ alias Qdrant đang active, xác nhận
toàn bộ parent tồn tại trong PostgreSQL rồi mới ghi snapshot. Thay đổi này phục
vụ Sparse lane của T2–T6 và bảo đảm T3 thực sự là Hybrid RRF.

Bước 6 trong `RUN_TABLE5.md` được viết lại theo từng T1–T7. Mỗi mode có ba lệnh
riêng để chạy 1 câu, 2 câu và toàn bộ 100 câu, kèm quy tắc resume checkpoint,
phụ thuộc T3→T5/T6 và yêu cầu T6 hoàn tất trước T7.

## Chi tiết theo thực nghiệm

### T1 — Dense-only

`Table5Runner.documents_for_mode()` tại `Test_Ragas/test_table5_ragas.py:196` gọi Dense retrieval độc lập và giới hạn cùng `context_top_k` với các mode khác. T1 dùng chung prompt, generator và RAGAS evaluator với T2–T6.

### T2 — Sparse-only

`Table5Runner.documents_for_mode()` tại `Test_Ragas/test_table5_ragas.py:196` gọi trực tiếp BM25 và `doc_store`. T2 không gọi Dense hoặc reranker.

### T3 — Hybrid RRF

`Table5Runner.t3_candidates()` tại `Test_Ragas/test_table5_ragas.py:171` gọi production `AdvancedChunkingEngine.retrieve()` đúng một lần cho mỗi câu với `hybrid_search=True` và `use_reranker=False`. Candidate pool được lưu tại `checkpoints/hybrid_rrf/candidates.json`; T3 lấy `K` evidence đầu tiên.

### T4 — Hybrid RRF + Reranker

`rerank()` tại `Test_Ragas/test_table5_ragas.py:104` nhận candidate pool đã checkpoint của T3. Hàm dùng `TemporalCrossEncoderReranker` tại `Test_Ragas/test_table5_ragas.py:105`, không gọi Dense, BM25 hay Graph lần nữa.

### T5 — Hybrid RRF + Graph

`graph_evidence_for_query()` tại `Test_Ragas/table5_experiment.py:137` chọn Graph operation từ **intent suy ra từ câu hỏi**. `merge_graph_evidence()` tại `Test_Ragas/table5_experiment.py:71` đặt Graph evidence hợp lệ trước T3 evidence, loại trùng và giới hạn đúng `context_top_k`.

Graph không phải RRF lane: Graph record không nhận RRF score và không được đưa vào công thức RRF. Record được canonicalize thành `Document` cùng provenance `source=neo4j_graph` ở `Test_Ragas/table5_experiment.py:117` để LLM và RAGAS có thể kiểm tra evidence.

### T6 — Hybrid RRF + Graph + Reranker

`combine_evidence()` tại `Test_Ragas/table5_experiment.py:84` tạo candidate pool gồm T3 candidates và Graph evidence. Sau đó `rerank()` tại `Test_Ragas/test_table5_ragas.py:104` sắp xếp lại pool này và lấy `K` evidence. T6 checkpoint lưu full content, metadata, thứ tự và fingerprint tại `Test_Ragas/test_table5_ragas.py:303–320`.

`AcademicGraphService.lookup_exemption_basis()` đổi Cypher parameter từ
`query` sang `query_text`. Sửa lỗi T5/T6 khi Neo4j `Session.run()` nhận cả
câu Cypher theo vị trí và keyword `query`, dẫn đến `TypeError: multiple
values for argument 'query'`. Truy vấn và dữ liệu trả về không thay đổi.

### T7 — Fixed-evidence Agent

T7 chỉ đọc checkpoint T6 trong `Test_Ragas/test_table5_ragas.py:303–310`. Runner kiểm tra fingerprint; nếu evidence T6 không có hoặc khác thứ tự/nội dung, T7 dừng với lỗi rõ ràng và không tự chạy retrieval lại.

`_escape_prompt_literal()` tại `app/agents/graph.py` escape dấu ngoặc JSON
trong fixed evidence trước khi tạo `ChatPromptTemplate`. Sửa lỗi T7 hiểu
trường JSON như `{"don_vi": ...}` thành biến template bị thiếu. Nội dung
evidence sau khi render được giữ nguyên và T7 không gọi retrieval lại.

`build_agent_graph(..., fixed_context=...)` tại `app/agents/graph.py:111–121` là interface benchmark-only. Khi có `fixed_context`:

- `retrieval_node()` tại `app/agents/graph.py:229` trả context cố định và không gọi Qdrant, BM25, Neo4j hay tuition catalog;
- `fixed_evidence_answer()` tại `app/agents/graph.py:359` chỉ tổng hợp câu trả lời từ context đó;
- Academic, Financial, Scholarship và General agent tại `app/agents/graph.py:380–493` không tạo ReAct agent và không được cấp tool lookup/calculation.

Vì vậy T7 đo routing và reasoning/orchestration trên evidence T6; nó không phải phép đánh giá full tool-calling agent. Tool validity và decision accuracy vẫn thuộc Table 6.

## Checkpoint và quota

`CaseCheckpointStore` tại `Test_Ragas/table5_experiment.py:177` ghi atomic theo từng câu. Runner lưu lần lượt evidence, answer và RAGAS metrics tại `Test_Ragas/test_table5_ragas.py:292–360`.

`dataset_sha256()` nhận diện dataset bằng SHA-256 của nội dung thay vì
đường dẫn tuyệt đối. `checkpoint_fingerprint()` được nâng từ schema v3
lên v4 với `dataset_name` và `dataset_sha256`. Thay đổi T1–T7 này cho
phép chuyển checkpoint T3 sang máy khác mà vẫn phát hiện dataset bị
thay đổi. Mỗi mode nay lưu trong folder riêng theo mẫu
`checkpoints/<mode>/checkpoint.json`; candidate pool dùng chung nằm tại
`checkpoints/hybrid_rrf/candidates.json`. Hai checkpoint T3 hiện có đã
được chuyển sang cấu trúc này và schema v4; 100 kết quả cùng
candidate được giữ nguyên. Thay đổi tách folder giúp T5 và T6
chạy trên hai máy mà không ghi chung một file checkpoint.

Khi lỗi quota `429`, `RESOURCE_EXHAUSTED` hoặc daily limit, `is_quota_error()` tại `Test_Ragas/table5_experiment.py:155` phân loại lỗi và runner dừng với exit code `75` sau khi đã ghi checkpoint. Khi đổi API key, chạy lại đúng câu lệnh; các câu đã có answer và đủ bốn metric sẽ được bỏ qua, còn câu dở dang sẽ tiếp tục từ stage chưa hoàn thành.

`is_api_pause_error()` cũng nhận `TimeoutError` là một lần tạm dừng
có thể resume. RAGAS có thể retry nhiều phản hồi 429 rồi chỉ ném
`TimeoutError` rỗng; runner nay ghi `paused_reason=evaluation_timeout`, giữ
answer đã sinh và dừng qua cùng luồng exit code `75`.
`Table5Runner.evaluate_one()` cũng dùng chính helper này, tránh lỗi
`NameError` khi Gemini trả 429 trực tiếp trong một metric RAGAS.

Metric `null`, `NaN`, answer rỗng hoặc lỗi API không được ghi là `success`. Báo cáo dùng trạng thái `incomplete` hoặc `paused_quota`, không dùng `pending` như kết quả thực nghiệm.

## Kiểm thử

`tests/test_table5_experiment.py` kiểm tra năm yêu cầu tối thiểu:

1. Checkpoint của mỗi mode và candidate T3 nằm đúng folder riêng.
2. Dataset giống nội dung tại hai đường dẫn khác nhau có cùng hash.
3. T5 không tăng context budget và loại evidence trùng.
4. T7 chỉ chấp nhận đúng fingerprint evidence T6.
5. Checkpoint có answer rỗng không được xem là hoàn thành.

Chạy smoke test sau khi môi trường Python hoạt động:

```powershell
python -m pytest tests/test_table5_experiment.py -q
python Test_Ragas/test_table5_ragas.py --limit 1 --modes dense_only,sparse_only,hybrid_rrf,hybrid_rrf_rerank,hybrid_rrf_graph,hybrid_rrf_graph_rerank
python Test_Ragas/test_table5_ragas.py --limit 1 --modes hybrid_rrf_graph_rerank_agent
```

T7 phải chạy sau khi checkpoint T6 của cùng dataset/configuration đã hoàn thành.
