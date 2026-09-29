# Kế hoạch Scenario 3 v3: Multi-Agent vs. Monolithic Tool Scalability tại 11/19/27 Tools

## 1. Mục tiêu

Thiết kế và chạy lại Scenario 3 như một thí nghiệm chính thức về khả năng mở rộng của không gian công cụ, so sánh:

- **Monolithic single-agent:** một tool gate nhìn thấy toàn bộ registry.
- **Supervisor-routed multi-agent:** supervisor chọn domain, sau đó specialist chỉ nhìn thấy registry của domain đó.

Ba kích thước registry được khóa trước khi chạy:

| Protocol level | Distractors/domain | Single-agent visible tools | Academic | Financial | Scholarship | General |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 11 | 6 | 4 | 1 | 0 |
| 2 | 2 | 19 | 8 | 6 | 3 | 2 |
| 4 | 4 | 27 | 10 | 8 | 5 | 4 |

Mục tiêu học thuật không phải chứng minh multi-agent luôn tốt hơn, mà kiểm tra trade-off:

> Domain partitioning có thể tạo routing overhead khi registry nhỏ, nhưng có thể làm giảm tool-selection interference khi registry mở rộng.

## 2. Quan hệ với protocol v2

Run v2 tại `logs/multi_vs_single_v2/20260914T104003Z/` được xem là **exploratory evidence** vì chỉ có hai mức 11 và 27 tools. Không ghép số v2 với level 19 mới.

Protocol v3 phải:

- chạy lại cả 11, 19 và 27 tools trong cùng một batch;
- dùng cùng code, model, datasets, seed policy và provider conditions;
- ghi kết quả vào `logs/multi_vs_single_v3/`;
- không sửa hoặc ghi đè artefact v2;
- khóa manifest trước lần gọi API đầu tiên.

Lý do phải chạy lại endpoint: model backend, code, tool descriptions và thời điểm provider có thể khác run v2. Ghép một midpoint mới với endpoint cũ sẽ làm mất tính matched của phép so sánh.

## 3. Research question và giả thuyết

### 3.1. RQ1 đề xuất

```latex
\item \textbf{RQ1 (Bounded Multi-Agent Orchestration and Tool-Space Scalability):}
How effectively does a centralized supervisor coordinate domain-specialized
agents, and how does the architecture compare with a matched monolithic
single-agent tool gate as the available tool registry expands?
```

RQ1 cố ý giữ hai vế để toàn bộ Scenario 3 cùng trả lời một câu hỏi thống nhất:

- Panels A--C đánh giá supervisor coordination, specialist selection, tool reliability và bounded failure handling.
- Panel D đánh giá matched single--multi comparison khi tool registry tăng từ 11 lên 19 và 27 tools.

### 3.2. Giả thuyết được khóa

```latex
We hypothesize that domain-partitioned tool access can reduce tool-selection
interference as the available registry expands, while introducing additional
routing overhead under compact tool settings.
```

### 3.3. Claim được phép và không được phép

Được phép nếu dữ liệu hỗ trợ:

- Multi-agent maintained higher tool-selection accuracy at the evaluated expanded registry sizes.
- The relative Multi--Single selection difference shifted toward the partitioned architecture as the registry expanded.
- Under the compact production registry, routing overhead was associated with a lower/higher point estimate, tùy kết quả thực tế.

Không được phép:

- Multi-agent is universally better than single-agent.
- Multi-agent produces better full-system QA answers.
- The experiment proves scalability beyond 27 tools.
- Synthetic distractor performance represents a production deployment with 27 real tools.

## 4. Experimental units và cấu hình khóa

### 4.1. Datasets

Primary suite:

- `data/scenario3_production_tools.json`
- 60 unique cases.
- 30 Academic, 20 Financial, 5 Scholarship và 5 General/no-tool cases.

Secondary robustness suite:

- `data/scenario3_robustness_cases.json`
- 20 unique malformed/adversarial cases.
- Báo riêng, không gộp với primary suite.

Không sửa câu hỏi/gold labels sau khi bắt đầu run. Nếu audit phát hiện lỗi trước run, phải tăng dataset/protocol version và ghi hash mới.

### 4.2. Arms

**Single-agent arm**

- Không gọi supervisor.
- Một LLM tool gate nhìn thấy union của mọi production tools và distractors tại level tương ứng.
- Tối đa một tool call.

**Multi-agent arm**

- Gọi live structured supervisor.
- Áp dụng production `repair_route_decision` như v2.
- Specialist gate chỉ nhìn thấy production tools và distractors của predicted domain.
- Tối đa một tool call.

### 4.3. Giữ cố định

- Cùng model identifier và temperature 0.0.
- Cùng queries, tool implementations và deterministic output oracles.
- Cùng timeout, retry policy và maximum tool calls.
- Cùng ba repetitions/case/architecture/level.
- Cùng seed cho job order và tool order.
- Không truyền gold agent, gold intent, expected tool hoặc expected args vào model prompt.

### 4.4. Phạm vi nhân quả: bundled orchestration comparison

Đây là một **bundled architecture comparison**, không phải phép cô lập thuần túy tác động của số lượng agent. Hai arms khác nhau đồng thời ở:

- multi-agent có thêm supervisor decision;
- multi-agent dùng specialist-scoped tool gate/prompt;
- multi-agent chỉ nhìn thấy domain-specific subset;
- single-agent dùng một monolithic gate và toàn bộ registry.

Vì vậy, kết quả chỉ được quy cho bundle `supervisor routing + specialist decision policy + partitioned tool access`. Không được quy toàn bộ chênh lệch riêng cho supervisor, prompt specialization hoặc tool partitioning.

Để giảm confounding trong phạm vi bundle:

- giữ chung task instructions về chọn tool, argument extraction, safe abstention và giới hạn một tool call;
- dùng cùng production tool objects, names, descriptions và schemas giữa hai arms;
- multi-agent chỉ nhận specialist scope sau live supervisor prediction, không nhận gold domain;
- lưu hash của monolithic và specialist gate prompts trong manifest;
- báo prompt specialization như một phần của intervention, không mô tả hai arms là chỉ khác số lượng visible tools.

Một control dùng cùng prompt và chỉ thay visible tool registry có thể cô lập tool partitioning rõ hơn, nhưng nằm ngoài primary protocol v3 và chỉ được thêm như experiment riêng nếu có ngân sách.

## 5. Thiết kế distractor v3

### 5.1. Vấn đề của v2 cần sửa

`make_distractor_tools` hiện nối câu sau vào model-visible description:

```text
Công cụ giả lập chỉ dùng trong scalability stress test
```

Câu này tiết lộ trực tiếp tool nào là distractor và có thể làm giảm độ khó không tự nhiên. Protocol v3 phải bỏ mọi từ khóa model-visible như:

- `synthetic`;
- `distractor`;
- `fake`;
- `giả lập`;
- `stress test`;
- `benchmark-only`.

Paper và manifest vẫn phải công khai rằng đây là synthetic benchmark tools; chỉ model không được nhận nhãn đó.

### 5.2. Registry file mới

Tạo:

```text
data/scenario3_distractor_registry_v3.json
```

Mỗi tool có schema:

```json
{
  "domain": "academic",
  "name": "tra_cuu_nganh_tuyen_sinh",
  "description": "Tra cứu thông tin tuyển sinh theo tên hoặc mã ngành.",
  "parameters": {
    "ten_nganh": {
      "type": "string",
      "description": "Tên hoặc mã ngành cần tra cứu."
    }
  },
  "deterministic_output": "Không có dữ liệu tuyển sinh tương ứng trong registry thử nghiệm.",
  "registry_order": 1
}
```

### 5.3. Yêu cầu chất lượng distractor

- Mỗi domain có đúng 4 distractors.
- Tool names và descriptions hợp lý về nghiệp vụ nhưng không phải đáp án đúng của 60 production cases.
- Không dùng chung một schema `keyword` cho tất cả tools; schemas phải có độ cụ thể gần production tools.
- Không tạo tool trùng tên production.
- Không tạo description chứa câu trả lời hoặc gold tool name.
- Output deterministic và không thay đổi external state.
- Level 2 dùng chính hai distractors đầu/domain; Level 4 dùng cả bốn. Đây là nested registry, không tạo hai bộ khác nhau.
- Registry order được khóa trong JSON và hash trong manifest.

### 5.4. Audit thủ công distractors

Trước run, xuất `docs/SCENARIO3_DISTRACTOR_AUDIT_V3.md` gồm ma trận:

| Distractor | Domain | Closest production tool | Vì sao plausible | Vì sao không đúng cho gold cases | Schema parity |
|---|---|---|---|---|---|

Hai người/agent đọc độc lập nếu có thể. Ít nhất phải xác nhận 60 production queries không có query nào mà distractor mới thực sự là lựa chọn đúng hơn gold production tool.

## 6. Chiến lược code

### 6.1. Không sửa protocol v2 tại chỗ

Tạo runner mới:

```text
scripts/run_multi_vs_single_agent_v3_scalability.py
```

Có thể tái sử dụng các service/bootstrap helpers ổn định từ runner cũ, nhưng protocol version, distractor registry, summary và manifest phải độc lập.

Tạo thêm:

```text
scripts/summarize_multi_vs_single_v3.py
tests/test_multi_vs_single_v3_scalability.py
```

Output root:

```text
logs/multi_vs_single_v3/<UTC_RUN_ID>/
```

### 6.2. GitNexus bắt buộc

Trước khi sửa bất kỳ function/class/method hiện có, chạy:

```text
gitnexus_impact(target="<symbol>", direction="upstream")
```

Các symbol v2 có thể cần tham khảo hoặc refactor:

- `make_distractor_tools`
- `evaluate_one`
- `paired_case_difference`
- `summarize`
- `generate_report`
- `run_protocol`

Nếu chỉ tạo symbol mới trong file v3 thì không sửa symbol v2. Nếu trích helper dùng chung, phải impact-analysis symbol nguồn trước. Báo direct callers, affected processes và risk level; dừng nếu HIGH/CRITICAL. Trước commit chạy `gitnexus_detect_changes()`.

### 6.3. CLI v3

Runner phải hỗ trợ:

```text
--tool-dataset PATH
--robustness-dataset PATH
--distractor-registry PATH
--levels 0,2,4
--suites production_tools,robustness
--model MODEL
--repetitions 3
--workers N
--retries N
--timeout 60
--max-tool-calls 1
--seed N
--limit N
--fresh
--resume RUN_DIR
--output-root PATH
```

Default protocol:

```text
levels=0,2,4
suites=production_tools,robustness
repetitions=3
max_tool_calls=1
temperature=0.0
seed=20260921
```

### 6.4. Checkpoint/resume

V2 ghi `records.partial.jsonl` nhưng không có resume hoàn chỉnh. V3 phải:

- định danh record bằng `(suite, level, architecture, case_key, repetition)`;
- append hoặc atomic-replace checkpoint sau mỗi batch;
- skip record đã hoàn tất khi resume;
- retry lỗi có giới hạn nhưng không xóa failure cuối;
- từ chối resume nếu signature thay đổi.

Signature tối thiểu gồm:

- hashes của hai datasets;
- hash distractor registry;
- hash runner và prompt/tool-gate contract;
- model, temperature, levels, suites, repetitions;
- timeout, max-tool-calls, retry policy;
- seed và tool-order policy;
- hashes hoặc version của production tool registry.

### 6.5. Tool ordering

Tool order có thể tạo positional bias. V3 phải:

- tạo một stable ordering bằng seed đã khóa;
- dùng cùng ordering policy cho mọi repetition;
- record danh sách visible tool names theo đúng thứ tự cho từng decision;
- không đổi order sau khi xem kết quả.

Không cần nhiều order permutations trong protocol chính vì sẽ làm tăng chi phí; ghi fixed-order limitation trong paper.

## 7. Record schema

Mỗi record phải giữ các field v2 và bổ sung:

```json
{
  "protocol": "multi-vs-single-v3.0",
  "suite": "production_tools",
  "registry_size": 19,
  "distractors_per_domain": 2,
  "architecture": "multi_agent",
  "case_key": "production_tools:001:ACA-01",
  "case_id": "ACA-01",
  "repetition": 1,
  "visible_tool_count": 8,
  "visible_tool_names": [],
  "expected_agent": "academic",
  "actual_agent": "academic",
  "raw_agent": "academic",
  "route_repair_reason": null,
  "expected_tool": "tra_cuu_nganh",
  "selected_tool": "tra_cuu_nganh",
  "expected_args": {},
  "selected_args": {},
  "selection_passed": true,
  "arguments_passed": true,
  "result_passed": true,
  "passed": true,
  "bounded_pass": true,
  "route_latency_ms": 0.0,
  "gate_latency_ms": 0.0,
  "tool_latency_ms": 0.0,
  "route_attempts": 1,
  "gate_attempts": 1,
  "error": ""
}
```

Không ghi credentials, API keys hoặc full provider payload.

## 8. Outcomes và thống kê

### 8.1. Primary outcome

Primary outcome của v3:

> Architecture-by-registry interaction in tool-selection accuracy from 11 to 27 tools on the 60 production cases.

Tính theo từng unique case:

1. Lấy mean qua 3 repetitions cho mỗi `(case, architecture, level)`.
2. Tính tại mỗi level:

```text
Delta(level) = Multi(level) - Single(level)
```

3. Tính endpoint interaction:

```text
Interaction = Delta(27) - Delta(11)
```

4. Paired bootstrap 10,000 lần trên 60 unique case IDs.

Nếu 95% CI của interaction loại 0 theo hướng dương, có thể nói relative selection advantage shifted toward the partitioned architecture under the expanded registry.

### 8.2. Vai trò của midpoint 19

Level 19 không chỉ để trang trí. Phải báo:

- `Delta(19)` và paired CI;
- liệu điểm giữa có nằm giữa xu hướng 11 và 27 hay không;
- không gọi xu hướng monotonic nếu metric tại 19 không theo cùng hướng.

Với chỉ ba levels, không gọi đây là một general scalability law hoặc smooth scaling curve.

### 8.3. Secondary outcomes

- Argument Exact Match.
- Deterministic result accuracy.
- End-to-end pass rate.
- Bounded completion.
- Raw/repaired route accuracy của multi-agent.
- Error/timeout rate.
- Route, gate và total latency p50/p95.
- Model attempts/calls per successful case.

Các interaction CI cho secondary outcomes phải được báo là secondary/exploratory, không đổi thành primary sau khi thấy kết quả.

### 8.4. Statistical unit

- Primary statistical `n=60` unique production cases.
- Ba repetitions đo repeatability, không biến `n` thành 180.
- Robustness statistical `n=20`, báo riêng và thừa nhận CI rộng.
- Không gộp production và robustness cases thành `n=80` cho primary claim.

### 8.5. Negative results

Phải báo:

- level nào single-agent cao hơn;
- metric nào multi-agent giảm;
- robustness selection nếu multi-agent kém hơn;
- mọi CI chứa 0;
- routing overhead và additional model-call cost.

## 9. Tests bắt buộc

Tạo `tests/test_multi_vs_single_v3_scalability.py` với các nhóm sau.

### 9.1. Registry validation

- 16 unique distractor names.
- 4 tools/domain.
- Không trùng production tool names.
- Không chứa model-visible disclosure terms.
- Tất cả descriptions và parameter descriptions không rỗng.
- Deterministic functions không gây external mutation.
- Level mapping đúng `0→11`, `2→19`, `4→27` cho single-agent.
- Multi-agent counts đúng bảng ở Mục 1.

### 9.2. Arm isolation

- Single-agent không gọi supervisor.
- Multi-agent không nhìn tools ngoài predicted domain.
- Không arm nào nhận gold labels trong prompt.
- Max tool calls bằng 1.
- Same production tools và same distractor definitions được dùng giữa arms.

### 9.3. Statistics

Dùng fixture nhỏ có kết quả biết trước để kiểm tra:

- aggregation qua repetition;
- pairing bằng `case_key`, không bằng row order;
- `Delta(level)`;
- `Delta(27)-Delta(11)`;
- bootstrap resample unique cases;
- records lỗi vẫn được tính fail, không bị drop;
- robustness không lọt vào primary statistic;
- cùng seed cho cùng summary.

### 9.4. Resume và manifest

- Duplicate key bị từ chối hoặc skip deterministically.
- Resume chỉ chạy missing keys.
- Hash mismatch khiến resume fail trước API call.
- Complete run có đủ artefact hashes.

## 10. Run budget

### 10.1. Full v3 cả hai suites

```text
3 levels × 80 cases × 2 architectures × 3 repetitions
= 1,440 records
```

Nominal model decisions trước retry:

```text
Multi-agent: 3 × 80 × 3 × 2 calls = 1,440
Single-agent: 3 × 80 × 3 × 1 call  =   720
Total nominal model decisions       = 2,160
```

### 10.2. Chỉ chạy primary production suite

```text
3 levels × 60 cases × 2 architectures × 3 repetitions
= 1,080 records
```

Nominal model decisions: khoảng 1,620 trước retry.

Khuyến nghị chạy cả hai suites để không bỏ robustness negative results. Nếu giới hạn thời gian/API, chạy production suite trước nhưng không tuyên bố robustness của v3 cho tới khi suite đó hoàn tất.

## 11. Hướng dẫn chạy

Các lệnh sau là CLI đích mà implementation phải hỗ trợ.

### 11.1. Preflight

```bash
cd /mnt/d/project/chatbot
git status --short
source wsl_venv/bin/activate
docker compose up -d neo4j
docker compose ps
```

Kiểm tra credential mà không in secret:

```bash
wsl_venv/bin/python - <<'PY'
import os
print("GOOGLE_CREDENTIAL_AVAILABLE", bool(
    os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
))
print("NEO4J_CONFIGURED", all(os.getenv(k) for k in (
    "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"
)))
PY
```

Không `cat .env` và không ghi secrets vào log/manifest.

### 11.2. Unit tests

```bash
wsl_venv/bin/python -m pytest \
  tests/test_multi_vs_single_v3_scalability.py \
  tests/test_evaluation_contract.py \
  tests/test_orchestration_contract.py \
  tests/test_tool_execution.py -q
```

### 11.3. Offline validation/dry run

Runner nên có `--validate-only` để kiểm tra datasets, registry, counts và manifest mà không gọi API:

```bash
wsl_venv/bin/python scripts/run_multi_vs_single_agent_v3_scalability.py \
  --levels 0,2,4 \
  --suites production_tools,robustness \
  --repetitions 3 \
  --seed 20260921 \
  --validate-only
```

Expected:

```text
production cases       = 60
robustness cases       = 20
levels                 = [0, 2, 4]
architectures          = 2
repetitions            = 3
expected total records = 1440
```

### 11.4. API smoke test

```bash
wsl_venv/bin/python scripts/run_multi_vs_single_agent_v3_scalability.py \
  --levels 0,2,4 \
  --suites production_tools,robustness \
  --repetitions 1 \
  --limit 2 \
  --workers 2 \
  --timeout 60 \
  --max-tool-calls 1 \
  --seed 20260921 \
  --fresh \
  --output-root logs/multi_vs_single_v3_smoke
```

Expected records:

```text
3 levels × (2 production + 2 robustness) × 2 architectures × 1 repetition
= 24 records
```

Smoke acceptance gates:

- 24/24 records tồn tại.
- Không duplicate keys.
- Visible tool counts đúng level/domain.
- Model không nhìn thấy disclosure metadata.
- Tool execution/oracle comparison hoạt động.
- Route/gate latencies và error fields có mặt.

### 11.5. Full run

Khởi đầu với `workers=4`. Chỉ tăng lên 8 nếu smoke và rate limits ổn định.

```bash
wsl_venv/bin/python scripts/run_multi_vs_single_agent_v3_scalability.py \
  --levels 0,2,4 \
  --suites production_tools,robustness \
  --repetitions 3 \
  --workers 4 \
  --retries 8 \
  --timeout 60 \
  --max-tool-calls 1 \
  --seed 20260921 \
  --fresh \
  --output-root logs/multi_vs_single_v3
```

### 11.6. Resume

```bash
wsl_venv/bin/python scripts/run_multi_vs_single_agent_v3_scalability.py \
  --resume logs/multi_vs_single_v3/<UTC_RUN_ID>
```

Không thay flags khi resume; runner đọc locked manifest và chỉ chạy missing keys.

### 11.7. Recompute summary

```bash
wsl_venv/bin/python scripts/summarize_multi_vs_single_v3.py \
  --run-dir logs/multi_vs_single_v3/<UTC_RUN_ID> \
  --bootstrap-draws 10000 \
  --seed 20260921
```

Summary script chỉ đọc frozen records, không gọi API.

## 12. Artefacts và invariants

Run directory phải có:

```text
logs/multi_vs_single_v3/<UTC_RUN_ID>/
├── manifest.json
├── checkpoint.json
├── records.jsonl
├── summary.json
├── comparison.md
├── failures.md
├── panel_d.tex
├── interaction_plot.pdf
└── run.log
```

Invariants trước khi cập nhật paper:

```text
protocol                                      = multi-vs-single-v3.0
levels                                        = 0,2,4
registry sizes                                = 11,19,27
unique production cases                       = 60
unique robustness cases                       = 20
repetitions                                   = 3
records per level/architecture/production     = 180
records per level/architecture/robustness     = 60
total records                                 = 1440
duplicate record keys                         = 0
primary paired N                              = 60
missing architecture pair                     = 0
```

Nếu có provider failures sau retry, records vẫn đủ 1,440 nhưng error count > 0 và primary fail được tính theo protocol. Không backfill số thủ công.

## 13. Hình và bảng cho paper

### 13.1. Panel D

Panel D nên có 6 rows:

```latex
\multicolumn{...}{l}{\textbf{Panel D: Matched Multi-Agent vs. Monolithic Tool-Space Scalability}} \\
Production (11) & Single & 11 & ... \\
Production (11) & Multi  & 0--6 & ... \\
Expanded (19)   & Single & 19 & ... \\
Expanded (19)   & Multi  & 2--8 & ... \\
Expanded (27)   & Single & 27 & ... \\
Expanded (27)   & Multi  & 4--10 & ... \\
```

Columns tối thiểu:

- registry size;
- architecture;
- visible tools;
- selection;
- argument EM;
- result accuracy;
- E2E pass.

Caption phải nói rõ:

- 60 unique production cases;
- 3 repetitions;
- synthetic distractors tại 19 và 27;
- paired inference over unique cases.

Không gọi 1,080 production records là `N=1,080` nếu đang nói statistical sample size. Viết `60 unique cases, 1,080 arm-level records`.

### 13.2. Interaction plot

Plot:

- x-axis: registry size 11, 19, 27;
- y-axis: tool-selection accuracy;
- hai lines: Single và Multi;
- error bars: query-level bootstrap CI;
- caption nêu specialist-visible counts khác single registry union.

Không kéo đường dự báo vượt ngoài 27.

## 14. Cập nhật Paper_V9 sau run

Chỉ cập nhật paper từ `summary.json` và generated `panel_d.tex` sau khi invariants pass.

### 14.1. Big edits

**Introduction/RQ1**

- Đổi RQ1 theo Mục 3.
- Đổi hypothesis từ broad counseling superiority sang routing-overhead/tool-interference trade-off.

**Abstract và Contribution Statement**

- Chỉ thêm kết quả multi--single sau khi protocol v3 hoàn tất và các invariants pass.
- Abstract phải mô tả đây là matched tool-orchestration evaluation trên 11/19/27-tool registries, không phải full-system QA superiority.
- Contribution C1 phải nêu cả bounded coordination và matched scalability comparison.
- Contribution wording đề xuất:

```latex
A matched evaluation of supervisor-routed and monolithic tool orchestration
across 11-, 19-, and 27-tool registries, examining the trade-off between
routing overhead and tool-selection interference.
```
- Không cần đổi title; bằng chứng v3 được dùng để làm rõ và hỗ trợ thành phần `Multi-Agent` trong title hiện tại.

**Scenario 3**

- Đổi tiêu đề thành `Routing, Tool Reliability, and Tool-Space Scalability`.
- Formalize matched single-vs-multi protocol trong experimental setup.
- Thêm Panel D và interaction plot nếu còn trang.
- Không để comparison chỉ xuất hiện ở Discussion.

### 14.2. Consistency edits

- Gap 1 ở Introduction/Related Work: nêu uncertainty về trade-off giữa routing overhead và tool-selection interference khi registry mở rộng.
- Evaluation Metrics: thêm primary selection interaction và paired bootstrap over unique cases.
- Discussion RQ1: trả lời cả compact-registry result, midpoint và expanded-registry result.
- Threats to Validity: synthetic distractors, fixed tool order, only three sizes, one model, isolated one-decision tool gate, không phải full ReAct/full QA.
- Conclusion: nhắc conditional result, không viết multi-agent universally superior.
- Future Work: chuyển từ "sẽ so sánh matched single/multi" thành mở rộng sang nhiều registry sizes hơn, real production tools và full retrieval-conditioned QA.

### 14.3. Minimal truthfulness edit cho Scenario 2

Không thay cấu trúc hoặc số liệu Scenario 2, nhưng phải sửa nhãn sai:

- `End-to-End QA Generation` → `Controlled Retrieval-Conditioned Generation`.
- `T4: full system` → `T4: full governed multi-evidence configuration`.
- Abstract/Conclusion không gọi số Ragas Scenario 2 là production full-system result.

Thay đổi này không yêu cầu rerun.

### 14.4. Run-count wording

Không cộng mọi panel thành một con số mơ hồ nếu chúng dùng datasets/units khác nhau. Báo per panel:

- Panels A--C: giữ counts riêng hiện tại.
- Panel D primary production scalability: 60 unique cases, 1,080 records.
- V3 robustness analysis: 20 unique cases, 360 records, báo riêng trong text/supplement.

## 15. Claim templates sau kết quả

Nếu interaction CI loại 0:

```latex
Across the evaluated registry expansion from 11 to 27 tools, the relative
tool-selection difference shifted by [X] percentage points toward the
domain-partitioned architecture (paired 95\% bootstrap CI [L, U], $n=60$
unique cases). This pattern suggests reduced tool-selection interference under
the expanded synthetic registry, while not establishing a universal
end-to-end advantage.
```

Nếu interaction CI chứa 0:

```latex
The relative tool-selection point estimate shifted by [X] percentage points
toward the domain-partitioned architecture, although the paired confidence
interval included zero. The evaluated data therefore do not establish a
reliable interaction between architecture and registry size.
```

Nếu single-agent thắng ở 11 tools:

```latex
Under the compact production registry, the monolithic arm retained a higher
[metric] point estimate, consistent with the additional routing decision in
the multi-agent arm.
```

Nếu midpoint không monotonic:

```latex
The midpoint did not follow a monotonic scaling pattern, so the endpoint
difference should be interpreted as condition-specific rather than as a
general scaling trend.
```

## 16. Definition of done

- Protocol v3 manifest được khóa trước API calls.
- Distractor registry qua audit và không tự lộ model-visible labels.
- GitNexus impact được chạy trước mọi existing-symbol edit.
- Unit/regression tests pass.
- Smoke có đủ 24 records và đúng visible-tool counts.
- Full run có đúng 1,440 records và không duplicate/missing pairs.
- Primary statistics dùng 60 unique production cases.
- Interaction và level-specific differences tái lập từ frozen records.
- Negative results và robustness được báo đầy đủ.
- Panel D cùng narrative RQ1 được cập nhật đồng bộ.
- RQ1 giữ cả supervisor-coordination và matched-comparison clauses.
- Abstract và Contribution C1 chỉ dùng claim được protocol v3 hỗ trợ.
- Paper mô tả kết quả như bundled orchestration comparison, không quy chênh lệch cho riêng số lượng agent.
- Scenario 2 chỉ được relabel trung thực, không bị diễn giải như production full-system evaluation.
- `gitnexus_detect_changes()` được chạy trước commit.
