# Kế hoạch triển khai Scenario 2 full-system: single-agent và multi-agent (T1--T7)

## 1. Mục tiêu và phạm vi

Tài liệu này là đặc tả để một agent khác triển khai thí nghiệm mới mà không phải suy đoán lại thiết kế. Mục tiêu là thay Scenario 2 cũ (một LLM sinh câu trả lời từ các gói context có sẵn) bằng đánh giá **hệ thống hoàn chỉnh**, trong đó có phép so sánh trực tiếp giữa monolithic single-agent và supervisor-routed multi-agent.

Phạm vi được phép:

- Tạo runner, bộ dữ liệu đã bổ sung nhãn, bộ kiểm thử và artefact mới.
- Thêm các tùy chọn benchmark có giá trị mặc định giữ nguyên hành vi production.
- Chạy pilot trên development set, sau đó chạy đúng một lượt chính trên 100 câu evaluation set.
- Chấm lại một tập con bằng câu trả lời đã đóng băng để đo độ ổn định của LLM evaluator.

Không được làm trong giai đoạn này:

- Không ghi đè runner hoặc kết quả Scenario 1--2 cũ.
- Không sửa số liệu trong Paper_V9 trước khi run mới hoàn tất và qua kiểm tra toàn vẹn.
- Không gọi T4 là tốt hơn, vượt trội hoặc chứng minh multi-agent trước khi có khoảng tin cậy ghép cặp.
- Không dùng kết quả của `logs/scenario12/20260921T043243Z/` như kết quả full-system. Run đó chỉ dùng một prompt sinh chung trên context, không gọi toàn bộ LangGraph production.

File kết quả mong muốn:

```text
logs/fullsystem_s2/<UTC_RUN_ID>/
├── manifest.json
├── checkpoint.json
├── records.jsonl
├── answers_frozen.jsonl
├── judge_records.jsonl
├── summary.json
├── comparison.md
├── failures.md
├── table_s2.tex
├── run.log
└── stability/
    ├── subset_manifest.json
    ├── repeated_judgments.jsonl
    └── stability_summary.json
```

## 2. Câu hỏi nghiên cứu và ánh xạ research gap

Thiết kế phải trả lời đúng ba câu sau:

1. **Gap 1 -- orchestration:** Trong điều kiện đánh giá hiện tại, supervisor-routed multi-agent có khác monolithic single-agent khi hai bên được quyền truy cập cùng các backend và domain tools hay không?
2. **Gap 2 -- heterogeneous representation:** Việc phân bổ tri thức theo cấu trúc (document retrieval, Neo4j và deterministic calculators/lookups) có liên quan đến thay đổi chất lượng đầu-cuối hay không?
3. **Gap 3 -- representation-aware retrieval governance:** Retrieval-lane governance và reranking có đóng góp gì khi giữ các thành phần còn lại của hệ thống không đổi?

Ánh xạ phép so sánh:

| Gap | Phép so sánh chính | Diễn giải được phép |
|---|---|---|
| Gap 1 | T4 so với T3 | So sánh hai kiến trúc end-to-end có cùng quyền truy cập backend/tool. Đây là bundled system comparison, không phải bằng chứng rằng routing là nguyên nhân duy nhất. |
| Gap 2 | T3/T4 so với T1/T2; T4 so với T6 | Đánh giá full multi-evidence access và graph grounding trong tập điều kiện đã kiểm thử. |
| Gap 3 | T4 so với T7; T4 so với T5 | Ablation retrieval-lane governance và cross-encoder reranking. |

Scenario 3 hiện có vẫn là bằng chứng bổ sung để cô lập routing/tool-selection. Không gộp số của Scenario 3 vào bảng Scenario 2.

## 3. Cấu hình T1--T7 phải khóa trước khi chạy

| Cfg. | Cấu hình thực thi | Mục đích |
|---|---|---|
| T1 | Monolithic single-agent + dense document retrieval; không Neo4j tools, không structured lookup/calculator | Uniform-representation baseline |
| T2 | Monolithic single-agent + hybrid BM25--dense document retrieval; không Neo4j tools, không structured lookup/calculator | Hybrid document baseline |
| T3 | Monolithic single-agent + full multi-evidence access: governed hybrid retrieval, cross-reranker và toàn bộ production tools | Single-agent control chính |
| T4 | Production supervisor-routed multi-agent + full multi-evidence access | Proposed full system |
| T5 | T4 nhưng tắt cross-encoder reranker | Reranker ablation |
| T6 | T4 nhưng bỏ toàn bộ Neo4j grounding | Representation ablation |
| T7 | T4 nhưng tắt retrieval-lane/subspace governance; supervisor và specialist routing vẫn hoạt động | Retrieval-governance ablation |

### 3.1. Ràng buộc để phép so sánh hợp lệ

- T3 và T4 dùng cùng main model, rewrite model, temperature, timeout, max tool calls, corpus snapshot, Qdrant alias, Neo4j snapshot, catalog, prompts về factuality và seed.
- "Cùng full multi-evidence access" nghĩa là cùng quyền truy cập tài nguyên. Không khẳng định hai kiến trúc nhận cùng một danh sách context, vì routing là một phần của hệ thống và có thể làm đường lấy bằng chứng khác nhau.
- T1 và T2 tuyệt đối không được gọi graph/tool ngầm. Nếu còn Neo4j tool hoặc structured lookup, chúng không còn là uniform-representation baselines.
- T5 chỉ tắt cross-reranker; BM25, dense retrieval, metadata lanes, graph và tools vẫn giữ nguyên.
- T6 phải tắt cả graph evidence được chèn tự động lẫn tất cả graph-backed tools. Đối với câu academic, hệ thống phải fallback sang document retrieval thay vì để một academic agent rỗng tools đoán câu trả lời.
- T7 chỉ tắt metadata lane filtering/subspace governance. Nó vẫn dùng hybrid retrieval, reranker, graph, supervisor và specialist agents. Trong code, tên chính xác nên là `without_retrieval_governance`, không phải `without_intent_governance`.
- Mọi configuration phải bị giới hạn cùng timeout và cùng ngân sách tool-call. Timeout/error được tính là fail, không được bỏ khỏi mẫu.
- Không dùng gold domain, gold intent, gold source hoặc reference answer trong quá trình routing/retrieval/generation.

## 4. Chiến lược sửa code

### 4.1. Quy tắc GitNexus bắt buộc

Trước khi sửa bất kỳ function/class/method hiện có nào, agent triển khai phải chạy:

```text
gitnexus_impact(target="<symbol>", direction="upstream")
```

Với mỗi symbol, ghi vào commentary: direct callers, affected processes và risk level. Nếu HIGH/CRITICAL thì dừng và báo người dùng trước khi sửa. Các symbol dự kiến cần kiểm tra gồm:

- `build_agent_graph`
- `retrieve_configurations` nếu agent quyết định tái sử dụng hoặc thay đổi nó
- `AdvancedChunkingEngine.retrieve` chỉ khi thực sự cần sửa signature/hành vi

Không sửa `AdvancedChunkingEngine.retrieve` nếu có thể truyền các cờ hiện có (`hybrid_search`, `use_reranker`, `metadata_filter_enabled`, `adaptive_rrf`, `source_quota`). Trước commit phải chạy `gitnexus_detect_changes()` và xác nhận chỉ có flow benchmark/graph mong đợi bị tác động.

### 4.2. File nên tạo mới

```text
app/agents/benchmark_options.py
scripts/fullsystem_s2_common.py
scripts/run_fullsystem_s2_experiment.py
scripts/validate_fullsystem_s2_dataset.py
scripts/rescore_fullsystem_s2_stability.py
scripts/summarize_fullsystem_s2.py
tests/test_fullsystem_s2_dataset.py
tests/test_fullsystem_s2_variants.py
tests/test_fullsystem_s2_statistics.py
data/scenario2_fullsystem_heldout_100.jsonl
data/scenario2_fullsystem_dev_pilot.jsonl
```

Không đổi tên hoặc xóa:

```text
scripts/run_scenario12_experiment.py
scripts/scenario12_common.py
data/scenario12_heldout_100.jsonl
logs/scenario12/
```

### 4.3. `app/agents/benchmark_options.py`

Tạo immutable dataclass hoặc Pydantic model, ví dụ:

```python
@dataclass(frozen=True)
class GraphRuntimeOptions:
    retrieval_mode: Literal["dense", "hybrid", "full"] = "full"
    use_cross_reranker: bool = True
    use_graph_grounding: bool = True
    use_retrieval_governance: bool = True
    collect_trace: bool = False
```

Giá trị mặc định phải tái tạo đúng production hiện tại. Không đọc configuration từ gold labels.

### 4.4. Điều chỉnh tối thiểu `build_agent_graph`

Ưu tiên thêm tham số optional `runtime_options: GraphRuntimeOptions | None = None` và chuẩn hóa `None` thành production defaults. Không tách/rewrite toàn bộ graph nếu không cần thiết.

Các nhánh cần hỗ trợ:

- `use_cross_reranker=False`: mọi lệnh `engine.retrieve` trong graph truyền `use_reranker=False`.
- `use_retrieval_governance=False`: không tạo lane-specific metadata filters; retrieval toàn cục với `metadata_filter_enabled=False`, nhưng vẫn dùng hybrid + reranker.
- `use_graph_grounding=False`:
  - không gọi `graph_service.lookup_tuition`;
  - không đăng ký graph-backed academic/financial tools;
  - academic query đi qua document retrieval trước khi sinh câu trả lời;
  - trace phải ghi `graph_disabled_by_config=true`.
- `collect_trace=True`: trả thêm trace không nhạy cảm trong state, gồm raw/repaired route, intent, active lanes, source IDs, backend/evidence lane, tool names, normalized tool args, tool-call count, latency từng stage và fallback reason.

Production callers không truyền options phải không đổi hành vi. Thêm regression test xác nhận default options và `None` cho cùng route/retrieval controls trên mocked services.

### 4.5. Xây monolithic single-agent cho T1--T3

Đặt builder trong `scripts/fullsystem_s2_common.py`, không thêm nó vào API production.

- T1: dense retrieval (`hybrid_search=False`, `use_reranker=False`, `metadata_filter_enabled=False`) rồi một agent sinh câu trả lời từ evidence. Tool list rỗng.
- T2: hybrid BM25--dense (`hybrid_search=True`, `use_reranker=False`, `metadata_filter_enabled=False`, `adaptive_rrf=False`) rồi một agent sinh câu trả lời. Tool list rỗng.
- T3: một ReAct agent duy nhất nhìn thấy hợp của production tools và được cung cấp full governed retrieval context. Nó không được dùng supervisor/specialist routing.
- Dùng cùng system-level answer constraints giữa T3 và T4: không bịa dữ kiện, hỏi làm rõ khi thiếu tham số bắt buộc, ưu tiên nguồn có provenance, giới hạn số tool calls.
- Ghi trace cùng schema với T4 để summary không có logic riêng cho từng architecture.

T3 nhìn thấy nhiều tools hơn từng specialist của T4. Đây chính là khác biệt tool-space partitioning của kiến trúc, vì vậy phải báo số tool exposed và số tool calls trong records.

### 4.6. Runner `scripts/run_fullsystem_s2_experiment.py`

CLI tối thiểu:

```text
--dataset PATH
--configs T1,T2,T3,T4,T5,T6,T7
--model MODEL
--rewrite-model MODEL
--temperature 0
--system-workers N
--timeout-seconds N
--max-tool-calls N
--limit N
--case-ids PATH
--seed N
--fresh | --resume RUN_DIR
--generation-only
--judge-only RUN_DIR
--output-root PATH
```

Hành vi bắt buộc:

1. Load và validate toàn bộ dataset trước khi khởi tạo dịch vụ.
2. Khởi tạo corpus/services đúng một lần cho mỗi process.
3. Randomize thứ tự `(case_id, config)` bằng seed cố định để giảm order/provider confounding.
4. Không chạy hai config của cùng một case đồng thời nếu việc đó có thể tranh chấp GPU/local reranker.
5. Ghi checkpoint theo từng answer bằng atomic replace; resume chỉ nhận run có signature khớp tuyệt đối.
6. Signature/manifest phải hash dataset, runner, relevant app code, prompts, model names, environment flags, Qdrant alias, graph/catalog snapshot, Top-k và metric rubric.
7. Sau generation, tạo `answers_frozen.jsonl`. File stability chỉ đọc file này và tuyệt đối không gọi lại system.
8. Mọi exception, timeout và retry count phải được ghi; không silently drop record.
9. Đóng Neo4j/clients trong `finally`.

Khóa model theo đúng model production tại thời điểm chạy. Hiện code production đang dùng main model `gemini-3.5-flash-lite` và rewrite model `gemini-3.1-flash-lite`; runner phải ghi chính xác model thực nhận từ CLI vào manifest thay vì hard-code mô tả trong report.

## 5. Sửa và khóa file test dataset

### 5.1. Không sửa trực tiếp dataset cũ

Tạo `data/scenario2_fullsystem_heldout_100.jsonl` bằng cách copy nội dung đã author-review từ `data/scenario12_heldout_100.jsonl`, sau đó bổ sung nhãn. Giữ `parent_case_id` để truy nguồn. Dataset cũ đã được dùng cho benchmark trước và đang có thay đổi local; không ghi đè nó.

Mỗi dòng mới phải có tối thiểu:

```json
{
  "id": "HOUT-...",
  "parent_case_id": "HOUT-...",
  "question": "...",
  "reference_answer": "...",
  "required_facts": ["..."],
  "forbidden_facts": [],
  "gold_sources": ["..."],
  "domain": "academic",
  "complexity_tier": "direct",
  "expected_primary_agent": "academic",
  "acceptable_agents": ["academic"],
  "expected_intent": "academic_program",
  "requires_tool": true,
  "acceptable_tools": ["tra_cuu_nganh"],
  "expected_args": {},
  "accepted_args": {},
  "requires_clarification": false,
  "required_evidence_types": ["neo4j"],
  "review_status": "approved",
  "annotation_version": "fullsystem-s2-v1"
}
```

Quy tắc nhãn:

- `acceptable_agents` cho phép nhiều agent ở câu cross-domain, nhưng vẫn phải có một `expected_primary_agent` để tính route accuracy.
- `acceptable_tools=[]` và `requires_tool=false` cho câu không cần tool. Không ép agent gọi tool chỉ để tăng tool-call rate.
- `expected_args` chỉ chứa tham số thực sự được câu hỏi cung cấp; không điền tham số suy đoán.
- `accepted_args` chứa alias/biểu diễn tương đương đã author-review, không dùng fuzzy match tùy ý.
- `forbidden_facts` chứa con số/kết luận dễ nhầm từ nguồn gần giống; nếu không có thì để list rỗng.
- `requires_clarification=true` khi câu hỏi thiếu tham số mà hệ thống không được phép tự đoán.
- `required_evidence_types` chỉ dùng để phân tích coverage, không được truyền cho system lúc chạy.

### 5.2. Audit thủ công bắt buộc

Validator không thể thay thế audit nghĩa. Người triển khai phải xuất một checklist Markdown và kiểm tra từng case:

- Câu hỏi và reference answer trả lời cùng đại lượng.
- `required_facts` không mâu thuẫn với `raw_evidence` và source.
- Gold source thực sự tồn tại trong corpus snapshot.
- Các con số khóa/năm/chương trình chuẩn/CLC nhất quán.
- Tool và args phù hợp với schema production hiện tại.
- Cross-domain case không bị ép thành single-domain nếu cần hai loại bằng chứng.

Đặc biệt kiểm tra các câu có dạng hỏi "tín chỉ bắt buộc" nhưng reference lại trả "tổng số tín chỉ"; đây là lỗi ngữ nghĩa mà schema validator không phát hiện được.

Sau audit, ghi `dataset_sha256` và bảng phân bố domain/complexity/tool-required vào `subset_manifest.json`/`manifest.json`.

### 5.3. Development pilot set

Tạo `data/scenario2_fullsystem_dev_pilot.jsonl` gồm 20 câu lấy từ development set, không lấy 20 câu đầu của held-out set. Stratify theo:

- 4 domain chính;
- single-domain và cross-domain;
- tool-required và no-tool;
- direct, multi-hop/comparison, temporal/adversarial nếu development data có đủ.

Pilot chỉ dùng để bắt lỗi code, prompt, timeout và trace. Không dùng kết quả pilot trong paper.

## 6. Metrics và thống kê

### 6.1. Primary outcome

`end_to_end_task_success` là binary per query. Một record pass khi:

- không error/timeout;
- chứa đầy đủ `required_facts` theo matcher đã unit-test;
- không chứa `forbidden_facts`;
- nếu `requires_clarification=true`, trả lời an toàn/đề nghị làm rõ thay vì bịa tham số;
- nếu `requires_tool=true`, tool được gọi thuộc `acceptable_tools`, args phù hợp và tool execution thành công.

Không dùng Ragas làm điều kiện duy nhất của primary outcome.

### 6.2. Secondary outcomes

- Fact coverage / factual exact match.
- Answer correctness, answer relevancy, faithfulness.
- Context precision và context recall chỉ cho configurations có explicit retrieved contexts; báo `N/A`, không gán 0, nếu đường tool-only không có comparable context.
- Source Recall và Source AP.
- Route accuracy và intent accuracy cho multi-agent configs.
- Tool selection accuracy, argument match, tool execution success.
- Safe-clarification rate.
- Timeout/error rate.
- Latency p50/p95, LLM-call count và tool-call count.

Mọi bảng phải báo cả metric T4 không đứng đầu. Không cherry-pick.

### 6.3. Phân tích ghép cặp

Đơn vị thống kê là **100 unique queries**, không phải số metric cells và không phải số lần LLM judge.

- Tính chênh lệch per-query cho T4--T3, T4--T5, T4--T6 và T4--T7.
- Paired bootstrap 10,000 lần trên 100 query IDs để lấy 95% CI cho chênh lệch mean.
- Với `end_to_end_task_success`, báo thêm McNemar exact test và bảng discordant pairs.
- Không viết "significantly" chỉ vì hai mean khác nhau. Chỉ dùng ngôn ngữ thống kê khi test/CI tương ứng hỗ trợ.
- Nếu CI chứa 0, viết "achieved a higher/lower point estimate, while the paired interval included zero".

### 6.4. Stability check của LLM evaluator

Thiết kế chính:

- 100 câu × 7 configurations × 1 system generation = **700 system runs**.
- Chọn trước 25 câu stratified và ghi IDs vào `stability/subset_manifest.json` trước khi chấm lặp.
- Giữ nguyên/freeze 25 × 7 câu trả lời đã sinh.
- Chấm mỗi câu trả lời tổng cộng 3 lần. Vì lượt chấm đầu đã có trong main run, chỉ cần thêm 25 × 7 × 2 = **350 judge records**.
- Tổng system generation vẫn là 700; tổng answer--evaluation records là 1,050.

Không được:

- gọi 350 lượt chấm thêm là 350 system runs;
- coi ba judge scores là ba mẫu độc lập;
- dùng độ dao động của subset như CI của toàn bộ 100 câu.

Báo mean absolute difference, within-item SD và pass/fail agreement theo metric; ICC chỉ thêm nếu implementation và assumptions được kiểm tra rõ.

## 7. Kiểm thử phải viết trước full run

### 7.1. Dataset tests

`tests/test_fullsystem_s2_dataset.py` phải kiểm tra:

- đúng 100 unique IDs;
- tất cả `review_status=approved`;
- các field bắt buộc không rỗng;
- `expected_primary_agent in acceptable_agents`;
- `requires_tool=true` thì `acceptable_tools` không rỗng;
- tool names tồn tại trong production registry;
- gold source tồn tại;
- không có duplicate normalized question;
- đúng phân bố complexity/domain đã khóa trong manifest.

### 7.2. Variant contract tests

`tests/test_fullsystem_s2_variants.py` dùng mocked engine/graph/tools để xác nhận:

- T1 gọi dense only và không expose tool.
- T2 gọi hybrid, không reranker/governance/tool.
- T3 không gọi supervisor và expose đúng hợp production tools.
- T4 dùng production-default graph path.
- T5 truyền `use_reranker=False` nhưng giữ graph/governance.
- T6 không gọi Neo4j lookup, không expose graph tools và academic đi qua document retrieval fallback.
- T7 truyền `metadata_filter_enabled=False` nhưng vẫn supervisor-route và rerank.
- Tất cả variant enforce timeout/max-tool-calls giống nhau.

### 7.3. Statistics tests

`tests/test_fullsystem_s2_statistics.py` phải có fixture nhỏ với kết quả biết trước để kiểm tra:

- paired differences ghép đúng theo `case_id`, không theo vị trí dòng;
- bootstrap resample unique cases;
- missing/error record được tính fail cho primary outcome;
- McNemar discordant counts đúng;
- repeated judge records không lọt vào primary N;
- summary từ cùng input/seed là deterministic.

## 8. Hướng dẫn chạy chi tiết

Các lệnh dưới đây là interface đích mà agent triển khai phải hỗ trợ.

### 8.1. Preflight

```bash
cd /mnt/d/project/chatbot
git status --short
source wsl_venv/bin/activate
docker compose up -d qdrant neo4j postgres redis
docker compose ps
curl -fsS http://localhost:6333/collections >/dev/null
docker exec chatbot-qdrant sh -c 'true'
```

Kiểm tra biến môi trường mà không in secret:

```bash
wsl_venv/bin/python - <<'PY'
import os
required = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]
print({key: bool(os.getenv(key)) for key in required})
print("GOOGLE_CREDENTIAL_AVAILABLE", bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")))
PY
```

Không `cat .env`, không ghi credential vào manifest/log.

### 8.2. Validate dataset

```bash
wsl_venv/bin/python scripts/validate_fullsystem_s2_dataset.py \
  --dataset data/scenario2_fullsystem_heldout_100.jsonl \
  --write-report docs/FULLSYSTEM_S2_DATASET_AUDIT.md
```

Chỉ tiếp tục nếu validator exit code 0 và checklist thủ công đủ 100/100.

### 8.3. Chạy unit tests

```bash
wsl_venv/bin/python -m pytest \
  tests/test_fullsystem_s2_dataset.py \
  tests/test_fullsystem_s2_variants.py \
  tests/test_fullsystem_s2_statistics.py -q
```

Sau đó chạy regression tests liên quan:

```bash
wsl_venv/bin/python -m pytest \
  tests/test_scenario12_experiment.py \
  tests/test_scenario3_experiment.py \
  tests/test_query_intent.py \
  tests/test_orchestration_contract.py \
  tests/test_tool_execution.py -q
```

### 8.4. Dry run 2 câu

```bash
TOKENIZERS_PARALLELISM=false wsl_venv/bin/python \
  scripts/run_fullsystem_s2_experiment.py \
  --dataset data/scenario2_fullsystem_dev_pilot.jsonl \
  --configs T3,T4 \
  --limit 2 \
  --system-workers 1 \
  --timeout-seconds 180 \
  --max-tool-calls 2 \
  --seed 20260921 \
  --fresh
```

Kiểm tra bằng tay trong records:

- T3 không có supervisor trace.
- T4 có raw và repaired route.
- Tool name/args không chứa object không serialize được.
- Source IDs/provenance có mặt.
- Không có reference answer trong prompt trace.

### 8.5. Pilot 20 câu development

```bash
TOKENIZERS_PARALLELISM=false wsl_venv/bin/python \
  scripts/run_fullsystem_s2_experiment.py \
  --dataset data/scenario2_fullsystem_dev_pilot.jsonl \
  --configs T3,T4 \
  --system-workers 1 \
  --timeout-seconds 180 \
  --max-tool-calls 2 \
  --seed 20260921 \
  --fresh
```

Pilot acceptance gates:

- 40/40 records xuất hiện; không silently missing.
- Error + timeout rate không vượt 5%. Nếu vượt, sửa runner/provider handling rồi chạy pilot mới.
- T3 và T4 dùng đúng cùng model và backend snapshot.
- Trace cho phép xác minh route, sources và tool calls.
- Không chỉnh architecture/prompt dựa trên kết quả held-out.

### 8.6. Full generation: 700 runs

Máy mục tiêu GTX 1650 4 GB VRAM: dùng `--system-workers 1` làm mặc định an toàn vì embedding/reranker chạy local; model generation có thể là remote nhưng không nên tăng concurrency trước khi theo dõi VRAM/RAM ở pilot.

```bash
TOKENIZERS_PARALLELISM=false wsl_venv/bin/python \
  scripts/run_fullsystem_s2_experiment.py \
  --dataset data/scenario2_fullsystem_heldout_100.jsonl \
  --configs T1,T2,T3,T4,T5,T6,T7 \
  --system-workers 1 \
  --timeout-seconds 180 \
  --max-tool-calls 2 \
  --seed 20260921 \
  --fresh
```

Nếu bị ngắt, dùng chính run directory được in ra:

```bash
TOKENIZERS_PARALLELISM=false wsl_venv/bin/python \
  scripts/run_fullsystem_s2_experiment.py \
  --resume logs/fullsystem_s2/<UTC_RUN_ID>
```

Resume phải từ chối nếu dataset/code/model/prompt/config hash thay đổi.

### 8.7. Chấm main answers

Nếu generation và judging được tách:

```bash
TOKENIZERS_PARALLELISM=false wsl_venv/bin/python \
  scripts/run_fullsystem_s2_experiment.py \
  --judge-only logs/fullsystem_s2/<UTC_RUN_ID> \
  --system-workers 1
```

Judge failures phải retry có giới hạn và vẫn được ghi failure nếu hết retry; không backfill thủ công bằng số giả.

### 8.8. Stability rescore trên frozen answers

```bash
wsl_venv/bin/python scripts/rescore_fullsystem_s2_stability.py \
  --run-dir logs/fullsystem_s2/<UTC_RUN_ID> \
  --subset-size 25 \
  --total-judge-repetitions 3 \
  --seed 20260921 \
  --workers 1
```

Script phải reuse chính 175 frozen answers (25 × 7), không gọi lại T1--T7.

### 8.9. Tổng hợp và kiểm tra artefact

```bash
wsl_venv/bin/python scripts/summarize_fullsystem_s2.py \
  --run-dir logs/fullsystem_s2/<UTC_RUN_ID> \
  --bootstrap-draws 10000 \
  --seed 20260921
```

Các invariant cuối:

```text
unique cases                         = 100
configurations                       = 7
primary system records               = 700
records per configuration            = 100
duplicate (case_id, config)           = 0
frozen answers                        = 700
stability subset cases                = 25
extra repeated judge records          = 350
primary statistical N per comparison  = 100 paired queries
```

Nếu một invariant sai, không cập nhật paper.

## 9. Cách đọc kết quả và điều kiện claim

### T4 so với T3

- Nếu paired 95% CI của task-success difference loại 0 theo hướng dương và McNemar phù hợp, có thể viết: "T4 achieved a higher end-to-end task-success rate than T3 under the evaluated conditions."
- Nếu point estimate dương nhưng CI chứa 0, chỉ viết: "T4 had a higher point estimate, while the paired interval included zero."
- Nếu T3 cao hơn, báo đúng negative result và không đổi primary metric sau khi xem số.

### Ablations

- T4--T5 chỉ được diễn giải về reranker.
- T4--T6 được diễn giải về graph grounding bundle, vì nó bỏ cả graph evidence lẫn graph tools.
- T4--T7 chỉ được diễn giải về retrieval-lane governance, không phải toàn bộ supervisor routing.

### Giới hạn bắt buộc báo trong paper

- Evaluation set có 100 câu và thuộc một trường đại học.
- T3--T4 là bundled end-to-end comparison; retrieval paths/context có thể khác.
- LLM-as-judge có biến thiên; stability subset chỉ là diagnostic.
- Mỗi system configuration chỉ sinh một answer/query trong main run.
- Kết quả trên GTX 1650 4 GB và model/API cụ thể không mặc nhiên khái quát sang model/hardware khác.

## 10. Cập nhật Paper_V9 sau khi có kết quả hợp lệ

Chưa sửa paper trong lúc implement runner. Sau khi artefact qua invariant checks:

1. Đổi mô tả Scenario 2 thành full-system end-to-end evaluation.
2. Thay bảng T1--T7 bằng đúng configuration contract ở Mục 3.
3. Báo `N=100`, một system generation/query/configuration và 700 primary runs.
4. Mô tả paired bootstrap trên 100 unique queries.
5. Mô tả 25-case frozen-answer stability analysis riêng; không nhập nó vào CI chính.
6. Cập nhật Results bằng số từ `summary.json`/`table_s2.tex`, không chép số từ log console.
7. Ghi cả metric baseline thắng T4 nếu có.
8. Chạy claim-strength audit: không dùng `proves`, `clearly shows`, `superior`, `always`, hoặc `significantly outperforms` nếu không có test tương ứng.
9. Scenario 1 có thể giữ nếu corpus/index snapshot không đổi; nếu dataset, index, retrieval code hoặc knowledge stores đổi sau run Scenario 1 thì phải chạy lại Scenario 1.

## 11. Definition of done

Implementation chỉ hoàn tất khi tất cả điều sau đều đúng:

- GitNexus impact đã được báo trước mọi symbol edit và detect-changes đã chạy trước commit.
- Production behavior không đổi khi không truyền benchmark options.
- Dataset mới có 100/100 case author-reviewed và hash được khóa.
- Unit + regression tests đều pass.
- Pilot development pass acceptance gates.
- Full run có đúng 700 system records, không duplicate/missing.
- Stability rescore dùng frozen answers và có đúng 350 extra judge records.
- Summary dùng paired query-level statistics.
- Artefact đủ provenance để tái lập.
- Paper chưa được cập nhật bằng số liệu cho tới khi toàn bộ kiểm tra trên hoàn tất.

