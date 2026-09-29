# Scenario 3 đề xuất — Multi-Agent Routing and Tool Reliability

## 1. Mục tiêu

Scenario 3 đánh giá riêng khả năng điều phối và gọi công cụ của CTU-Chat, không
trộn với chất lượng retrieval ở Table 3 hoặc chất lượng câu trả lời ở Table 4.

Ba câu hỏi thực nghiệm:

1. Supervisor có chọn đúng specialist và intent hay không?
2. Khi cần tính toán, mô hình có chọn đúng tool, truyền đúng tham số và nhận đúng
   kết quả hay không?
3. Với đầu vào thiếu, sai hoặc cố tình ép gọi tool, hệ thống có dừng trong giới
   hạn và phản hồi an toàn hay không?

## 2. Mô hình và môi trường cố định

- LLM: `gemini-2.5-flash-lite`.
- Backend: Google Cloud Vertex AI.
- Region mặc định: `us-central1`.
- Credential mặc định:
  `gen-lang-client-0656432358-9a6fb12696b2.json`.
- Temperature: `0.0`.
- Timeout cho mỗi quyết định LLM: `60 giây`.
- Số tool call tối đa cho mỗi quyết định: `1`.
- Retry ở tầng SDK: `1`.
- Chạy tuần tự, delay mặc định `1 giây` giữa các request.
- Chạy chính thức: `3 lần/câu`; dry-run chỉ chạy `1 lần/câu`.

Credential chỉ được đọc để thiết lập Vertex AI. Runner không ghi private key vào
log, manifest hoặc báo cáo. File credential đã thuộc nhóm ignore của Git.

## 3. Dữ liệu

### 3.1. Routing và specialist selection

Nguồn: 100 câu single-domain được chọn từ
`data/Paper/150_NATURAL_NO_APPENDIX.csv`.

50 câu có ID `CDICT*` kết hợp đồng thời chương trình đào tạo, quy chế và học phí
được loại khỏi phép đo single-agent routing. Kiến trúc hiện tại chỉ chọn một
specialist, vì vậy ép các câu đa miền này vào nhãn `actual_tuition` sẽ chấm sai
những quyết định `academic_program`, `calculation` hoặc `both` vẫn hợp lý.

100 câu còn lại thuộc chín nhóm nguồn và được ánh xạ thành bốn agent bằng
`data/scenario3_routing_labels.json`. Ba câu có category nguồn không phản ánh
đúng routing intent được override riêng và có ghi lý do trong file nhãn.

| Source category | Số câu | Expected agent |
|---|---:|---|
| `actual_tuition` | 14 | `financial` |
| `academic_rules` | 14 | `general` hoặc override |
| `scholarship` | 14 | `scholarship` |
| `student_loan` | 12 | `general` |
| `other` | 12 | `general` |
| `social_support` | 11 | `general` |
| `academic_program` | 9 | `academic` |
| `exemption_policy` | 9 | `financial` |
| `exemption_basis` | 5 | `financial` |

Runner đo cả rule-based router và LLM Supervisor trên cùng tập 100 câu.

Nếu đã lỡ chạy bằng bộ nhãn cũ gồm cả 50 câu `CDICT*`, không cần gọi Gemini lại.
Dùng lệnh rescore ở cuối tài liệu để lọc và chấm lại từ `records.jsonl`.

### 3.2. Tool reliability

Nguồn: `data/tool_calling_experiment.json`, gồm:

- 10 ca structured tuition lookup;
- 10 ca gọi `tinh_tien_hoc_bong`;
- 10 ca gọi `tinh_toan_hoc_phi`.

Các ca tuition lookup là kiểm tra deterministic structured path. Các ca học bổng
và tính miễn giảm mới là LLM tool-selection. Khi viết bài không được mô tả cả 30
ca là LLM tool calling.

### 3.3. Robustness và failure cases

Nguồn: `data/scenario3_robustness_cases.json`, gồm 20 ca:

- thiếu tham số bắt buộc;
- GPA, ĐRL hoặc phần trăm miễn giảm ngoài miền hợp lệ;
- câu hỏi chính sách không cần tool tính toán;
- câu hỏi thuộc agent khác;
- học phí thiếu khóa cần clarification;
- định dạng số thập phân tiếng Việt;
- thiếu tham số tùy chọn;
- câu hỏi follow-up không có context;
- prompt injection yêu cầu tự bịa tham số.

## 4. Các chỉ số

### Routing

- **Agent Accuracy**: tỷ lệ `actual_agent = expected_agent`.
- **Macro-F1**: F1 tính riêng trên từng agent rồi lấy trung bình. Chỉ số này giảm
  ảnh hưởng của nhóm `actual_tuition` có 60 câu.
- **Intent Accuracy**: tỷ lệ intent chi tiết được dự đoán đúng.
- **Bounded Completion Rate**: tỷ lệ quyết định hoàn thành trong timeout.
- **Latency p50/p95**: trung vị và phân vị 95 của thời gian routing.

### Tool reliability

- **Selection/Path Accuracy**: đúng tool hoặc đúng structured path.
- **Argument Exact Match**: mọi tham số bắt buộc có mặt và giá trị khớp ground
  truth. Chuỗi được so sánh không phân biệt hoa thường; số phải bằng nhau.
- **Result Accuracy**: output chứa các token đúng và không chứa token bị cấm.
- **End-to-End Pass**: đồng thời đúng selection, arguments và result.
- **Bounded Completion Rate**: không vượt quá `max_tool_calls` và không lỗi.

### Robustness

- **Tool/No-tool Decision Accuracy**: gọi tool khi đủ dữ liệu và không gọi khi
  thiếu/sai dữ liệu hoặc câu hỏi không thuộc tool.
- **Safe Result Behavior**: trả đúng kết quả hoặc chỉ rõ thông tin cần bổ sung.
- **Bounded Completion Rate**: cả routing lẫn tool gate đều hoàn thành trong giới
  hạn.
- **End-to-End Robustness Pass**: đúng agent, intent, tool/no-tool, tham số, hành
  vi kết quả và giới hạn thực thi.

## 5. Lệnh chạy

Kiểm tra schema và số lượng dữ liệu, không gọi Gemini:

```bash
python3 scripts/run_scenario3_experiment.py --validate-only
```

Smoke test ba câu mỗi suite:

```bash
wsl_venv/bin/python scripts/run_scenario3_experiment.py \
  --suite all \
  --dry-run
```

Chạy chính thức:

```bash
wsl_venv/bin/python scripts/run_scenario3_experiment.py \
  --suite all \
  --model gemini-2.5-flash-lite \
  --repetitions 3 \
  --timeout 60 \
  --max-tool-calls 1 \
  --max-retries 1 \
  --delay 1
```

Chạy riêng từng phần:

```bash
wsl_venv/bin/python scripts/run_scenario3_experiment.py --suite routing --repetitions 3
wsl_venv/bin/python scripts/run_scenario3_experiment.py --suite tools --repetitions 3
wsl_venv/bin/python scripts/run_scenario3_experiment.py --suite robustness --repetitions 3
```

Chấm lại một run cũ sau khi cập nhật nhãn, không gọi Gemini:

```bash
python3 scripts/rescore_scenario3_results.py \
  logs/scenario3/<timestamp>
```

## 6. Giải thích tham số dòng lệnh

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `--suite` | `all` | Chạy `routing`, `tools`, `robustness` hoặc cả ba |
| `--model` | `gemini-2.5-flash-lite` | Model ra quyết định routing và tool calling |
| `--credentials` | file JSON ở project root | Service-account credential cho Vertex AI |
| `--project` | đọc từ credential | Ghi đè Google Cloud project nếu cần |
| `--location` | `us-central1` | Vertex AI region |
| `--repetitions` | `1` | Số lần chạy lại mỗi câu; official run dùng `3` |
| `--timeout` | `60` | Số giây tối đa cho một lần gọi LLM |
| `--max-tool-calls` | `1` | Số tool call tối đa trong một quyết định isolated |
| `--max-retries` | `1` | Retry do SDK thực hiện khi gọi model lỗi |
| `--delay` | `1` | Khoảng nghỉ giữa request để hạn chế rate limit |
| `--limit` | không giới hạn | Chỉ chạy N câu đầu của mỗi suite |
| `--dry-run` | tắt | Ép `limit=3` và `repetitions=1` |
| `--validate-only` | tắt | Chỉ kiểm tra dữ liệu, không dùng credential/LLM |
| `--output-root` | `logs/scenario3` | Thư mục cha chứa kết quả |

## 7. Output

Mỗi lần chạy tạo một thư mục UTC mới trong `logs/scenario3/`:

```text
logs/scenario3/<timestamp>/
├── manifest.json
├── records.jsonl
├── summary.json
└── report.md
```

- `manifest.json`: model, backend, tham số chạy và SHA-256 của các dataset.
- `records.jsonl`: bằng chứng chi tiết từng câu và từng lần lặp.
- `summary.json`: số liệu tổng hợp để xử lý tự động.
- `report.md`: bảng kết quả có thể dùng để điền vào paper.

Runner không đọc checkpoint cũ và không ghi đè kết quả lần chạy trước.

## 8. Bảng dự kiến trong paper

| Configuration | Agent Acc. | Macro-F1 | Intent Acc. | Tool/Path Acc. | Arg. EM | E2E Pass | Bounded | p95 Lat. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Rule Router | -- | -- | -- | -- | -- | -- | -- | -- |
| LLM Supervisor | -- | -- | -- | -- | -- | -- | -- | -- |
| Full Scenario 3 | -- | -- | -- | -- | -- | -- | -- | -- |

Chỉ điền bảng sau khi official run hoàn thành. Không dùng lại
`ablation_results.json` cũ vì file đó sử dụng checkpoint/dataset khác và chưa thu
được full-system tool trace.

## 9. Phạm vi tuyên bố

Thực nghiệm này chứng minh routing, specialist selection, financial tool
selection, argument extraction và bounded isolated decisions. Nó chưa mô phỏng
lỗi hạ tầng thật của Neo4j/Qdrant và chưa chứng minh bounded execution của toàn
bộ nested ReAct graph. Nếu paper muốn tuyên bố hai nội dung đó, cần thêm fault
injection ở dependency layer và thu LangGraph execution trace.
