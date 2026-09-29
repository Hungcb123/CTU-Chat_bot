# Kế hoạch cải thiện CTU-Chat dựa trên log retrieval và tool calling

Ngày phân tích: 2026-09-14
Phạm vi: routing, retrieval, reranking, tool selection, argument extraction và regression testing.
Ngoài phạm vi ở bước hiện tại: sửa production code, re-index dữ liệu, thay nội dung Paper_v6 hoặc tuyên bố multi-agent tốt hơn single-agent.

## 1. Kết luận ngắn

Hệ thống không hỏng đồng loạt. Điểm yếu tập trung ở ba ranh giới:

1. **Dense/hybrid làm loãng exact lexical evidence.** BM25 rất mạnh với mã ngành, khóa, tên học bổng và tên biểu mẫu, nhưng equal-weight RRF cho dense và BM25 có thể đẩy tài liệu exact-match xuống.
2. **Reranker đôi khi phá một ranking vốn đã đúng.** Case xin bản sao văn bằng có BM25 và hybrid top-1 đúng, nhưng sau rerank tài liệu vàng biến mất khỏi top-10.
3. **Tool orchestration chưa có contract thống nhất.** Supervisor, deterministic intent classifier, tool-gate prompt và benchmark labels không hoàn toàn đồng ý về intent; argument evaluator cũ còn chấm sai các paraphrase hợp lệ.

Không nên tối ưu để “multi thắng single” bằng prompt thiên vị hay dữ liệu chọn lọc. Kết quả hiện tại cho thấy multi-agent chỉ bắt đầu có lợi thế khi tool-space lớn hơn, nhưng lợi thế chưa có ý nghĩa thống kê. Mục tiêu đúng là làm multi-agent ổn định hơn, rồi chạy lại protocol đã khóa.

## 2. Evidence đã kiểm tra

### 2.1 Retrieval — run approved

Nguồn: `logs/scenario12/20260912T123307Z`.

| Cấu hình | Hit@1 | Số query sai top-1 trên 50 |
|---|---:|---:|
| E1 BM25 | 0.9000 | 5 |
| E2 dense | 0.3800 | 31 |
| E3 hybrid RRF | 0.6800 | 16 |
| E4 hybrid + reranker | 0.8800 | 6 |
| E5 integrated bundle | 0.9600 | 2 |

Hai lỗi top-1 còn lại của E5:

- `HOUT-SCHOLARSHIP-03`: hỏi Vallet 2026 nhưng `HB_SCIC_2026.md` đứng top-1; `HB_Vallet_Chi_Tiet.md` đứng rank 2. Đây là lỗi phân biệt entity trong cùng domain, không phải routing sai domain.
- `HOUT-OTHER-04`: hỏi lệ phí cấp bản sao văn bằng; BM25 và E3 đưa đúng biểu mẫu lên top-1, nhưng E4/E5 đưa các tài liệu học phí lên đầu và gold source không còn trong top-10. Đây là lỗi reranker/intent signal, không phải thiếu tài liệu.

Các pattern khác:

- 11 query có E1 top-1 đúng nhưng E3 top-1 sai. Chúng tập trung ở mã/tên ngành, quy định có cụm từ chính xác, học bổng cụ thể, khóa tuyển sinh và CLC/chương trình chuẩn.
- E3 → E4 tăng Hit@1 từ 0.6800 lên 0.8800: reranker nhìn chung hữu ích, nhưng có failure mode nghiêm trọng ở một số lexical-anchor query.
- E4 → E5 sửa được nhiều query học phí CLC nhờ cả bundle governed lanes + lexical candidates + graph/catalog; log không cô lập được contribution của từng thành phần.

### 2.2 Nguyên nhân kỹ thuật retrieval có thể kiểm chứng từ code

- `app/services/rag_engine.py`: dense và BM25 được cộng RRF bằng cùng trọng số với `RRF_K = 60`.
- Candidate pool bị cắt ở `max(result_limit * 2, 8)` trước reranking. Một source exact-match bị đẩy khỏi đoạn này thì reranker không thể cứu lại.
- `TemporalCrossEncoderReranker` chỉ chấm 1.000 ký tự đầu mỗi parent document. Với bảng dài hoặc biểu mẫu có dữ kiện nằm sâu, model không nhìn thấy đoạn discriminative.
- Tài liệu có score cách nhau không quá `0.05` được sắp lại theo timestamp. Tie-break này không kiểm tra query có thực sự hỏi “mới nhất” hay không.
- Lexical safeguard trong `scenario12_common.py` chỉ giữ một BM25 candidate ở cuối top-k khi có ít nhất hai token dài từ bốn ký tự xuất hiện. Nó không bảo vệ top-1 và không xử lý tốt mã ngành, mã quyết định, khóa `K52`, acronym hoặc entity ngắn.
- Source được deduplicate ở metric layer, nhưng candidate/rerank vẫn có nhiều parent chunks cùng source. Một source có nhiều chunks có thể chiếm nhiều vị trí và làm giảm source diversity.

### 2.3 Tool calling — protocol v2 đã hoàn tất

Nguồn: `logs/multi_vs_single_v2/20260914T104003Z`.

| Tool space | Suite | Multi E2E | Single E2E | Multi − Single | 95% paired bootstrap CI |
|---|---|---:|---:|---:|---:|
| 11 production tools | production | 0.8833 | 0.9333 | -0.0500 | [-0.1167, 0.0000] |
| 11 production tools | robustness | 0.9167 | 0.8667 | +0.0500 | [-0.1000, 0.2500] |
| 27 tools, synthetic stress | production | 0.9000 | 0.8667 | +0.0333 | [-0.0500, 0.1167] |
| 27 tools, synthetic stress | robustness | 0.6500 | 0.6000 | +0.0500 | [-0.1500, 0.2500] |

Diễn giải đúng:

- Với 11 tools hiện tại, multi-agent chưa tốt hơn single-agent ở production cases.
- Khi tăng tool-space lên 27, partition theo specialist tạo lợi thế selection quan sát được, nhưng CI vẫn cắt 0 nên chưa thể tuyên bố superiority.
- Route của multi khá tốt: 0.9833 ở production và 1.0000 ở robustness. Bottleneck lớn hơn nằm sau routing: chọn tool trong specialist và chuẩn hóa argument.
- 15 lỗi multi ở nhóm `tim_nganh` cấu hình sạch đều chọn đúng tool; evaluator exact-match chấm paraphrase như “ngành liên quan đến nông nghiệp” khác “nông nghiệp”. Đây là lỗi measurement contract, không nhất thiết là lỗi chức năng.
- Có lỗi thật: đôi lúc không gọi `tra_cuu_hoc_phi_graph`/`tra_cuu_co_so_mien_giam_graph`; case học phí mơ hồ có label dataset `general` nhưng supervisor contract lại quy định `financial + ambiguous_tuition`.
- Dataset cũ có 44/60 case để `expected_contains=[]`; evaluator cũ tự cho `result_passed=True`. Vì vậy result accuracy cũ bị thổi phồng và không nên dùng làm evidence.

### 2.4 Smoke-20 baseline

Fixture: `data/smoke20_regression.jsonl`.
Runner: `scripts/run_smoke20_regression.py`.
Baseline route/tool đã xác nhận: `logs/smoke20/20260914T160805Z`.

- 20 câu, đúng 5 câu cho mỗi specialist domain: Academic, Financial, Scholarship, General.
- 18/20 pass sau khi oracle công nhận đúng “Khối ngành IV” tương đương “Khối IV”.
- Hai lỗi thực còn lại:
  - `SMK-ACA-02`: câu Logistics có đủ tên ngành nhưng tool gate không gọi `tra_cuu_nganh`, lại yêu cầu khóa không cần thiết.
  - `SMK-FIN-04`: chọn đúng `financial` và đúng `tra_cuu_quy_dinh_hoc_phi`, nhưng LLM supervisor gán `ambiguous_tuition`; deterministic classifier hiện gán `actual_tuition`.
- Retrieval mode chưa chạy được tại thời điểm audit vì local Qdrant `localhost:6333` và Neo4j `localhost:7687` không hoạt động. Đây là environment failure, không được tính thành model failure.

## 3. Bộ smoke-20 và cách dùng

### 3.1 Ba mức chạy

Kiểm tra nhanh prompt/routing/tool schema, không cần database:

```bash
wsl_venv/bin/python scripts/run_smoke20_regression.py
```

Kiểm tra retrieval source ranking, cần Qdrant/Postgres/Neo4j hoạt động:

```bash
wsl_venv/bin/python scripts/run_smoke20_regression.py --mode retrieval
```

Kiểm tra toàn bộ và thực thi tool thật:

```bash
wsl_venv/bin/python scripts/run_smoke20_regression.py --mode all --execute-tools
```

Hai case `target` không chặn mặc định vì đang là lỗi đã biết. Khi đã sửa xong, bật hard gate:

```bash
wsl_venv/bin/python scripts/run_smoke20_regression.py --mode all --execute-tools --strict-targets
```

### 3.2 Contract của suite

- `required`: lỗi làm command trả exit code 1, dùng để chống regression.
- `target`: luôn hiện trong report, chỉ block khi dùng `--strict-targets`.
- Route/tool mode kiểm tra: agent, intent, đúng tool hoặc suppression, argument có giá trị tương đương và giới hạn tối đa một tool call.
- Retrieval mode kiểm tra E5 source rank sau deduplication theo source.
- Không dùng LLM-as-judge trong smoke; mọi assertion đều deterministic.
- Không thay smoke-20 sau khi thấy kết quả của một patch, trừ khi chứng minh được label/oracle sai và ghi rõ lý do.

## 4. Kế hoạch cải thiện chi tiết

### Phase 0 — Khóa baseline và sửa measurement trước khi sửa model

Mục tiêu: bảo đảm số tăng/giảm phản ánh hành vi thật.

1. Khóa hash cho smoke fixture, prompt, tool schemas và retrieval config vào manifest mỗi run.
2. Chuẩn hóa ID trùng trong `scenario3_robustness_cases.json` (`F14`) bằng migration có log, không âm thầm đổi lịch sử.
3. Thay argument exact-match bằng schema-aware scorer:
   - numeric: exact sau type coercion;
   - code/cohort: canonical exact (`52` ↔ `K52` nếu schema cho phép);
   - enum/alias: canonical map (`VLVH` ↔ `vừa làm vừa học`);
   - free-text search: functional output equivalence hoặc normalized containment, không bắt model copy nguyên cụm câu hỏi;
   - hai-entity tools: kiểm tra đủ hai entity và hỗ trợ permutation khi tool semantics đối xứng.
4. Result accuracy phải dựa trên deterministic oracle/tool execution; không có oracle thì metric là `not evaluated`, không tự động pass.
5. Tách metric thành `Route`, `Intent`, `Tool Selection`, `Argument Validity`, `Execution`, `Retrieval`, `Answer`; không gộp một lỗi upstream thành nhiều bằng chứng độc lập.

Acceptance gate:

- 100% fixture có oracle hoặc đánh dấu rõ metric không áp dụng.
- Không còn duplicate case ID.
- Rescore log cũ phải giải thích được chênh lệch giữa exact argument EM và functional argument accuracy.

### Phase 1 — Đồng bộ một routing contract duy nhất

Mục tiêu: LLM supervisor và deterministic router không tự mâu thuẫn.

1. Tạo một bảng contract machine-readable cho mỗi intent:
   - positive triggers;
   - exclusions/precedence;
   - specialist owner;
   - retrieval lanes;
   - allowed tools;
   - required vs optional tool arguments.
2. Sinh prompt examples và validation rules từ contract này hoặc ít nhất test parity tự động.
3. Sau LLM supervisor, chạy deterministic validator:
   - nếu high-confidence rule nhận ra vay vốn, hỗ trợ sư phạm, học bổng tài trợ, academic rule hoặc VLVH thì override/repair intent;
   - nếu agent và intent không hợp lệ theo mapping thì repair trước retrieval;
   - log cả raw decision, repaired decision và reason.
4. Không route câu “học phí chưa rõ ngành/khóa” sang General. Contract hiện tại đúng hơn là `financial + ambiguous_tuition`; sửa label benchmark cũ cho nhất quán sau review.
5. Thêm confusion tests cho từ khóa chéo domain: `lệ phí`, `hỗ trợ học phí sư phạm`, `vay tiền đóng học phí`, `miễn thi`, `học bổng doanh nghiệp`.

Acceptance gate:

- Smoke route+intent 20/20 trong ba lần độc lập.
- Full routing held-out không thấp hơn 97%; không giảm bất kỳ domain nào quá 2 percentage points.
- Không có agent/intent pair ngoài contract.

### Phase 2 — Sửa tool gating và argument normalization

Mục tiêu: route đúng phải dẫn đến tool decision ổn định.

1. Tách prompt chung thành phần invariant và rule theo từng specialist; tránh đưa quy tắc không liên quan cho mỗi agent.
2. Ghi rõ required arguments từ schema thật, không suy ra từ ví dụ. `tra_cuu_nganh` không được đòi cohort nếu tool schema không yêu cầu.
3. Thêm canonicalization trước tool invoke:
   - ngành: code, tên, acronym;
   - khóa: `52`, `K52`, `khóa 52`;
   - khối: `Khối IV`, `Khối ngành IV`;
   - loại hệ: chuẩn, CLC, tiên tiến, VLVH, từ xa.
4. Thêm precondition validator deterministic cho GPA, ĐRL, phần trăm và số tiền. Model chỉ quyết định tool/args; validator quyết định có được execute hay cần hỏi lại.
5. Khi tool lookup trả “không tìm thấy”, không coi là success chỉ vì call không exception. Phân loại thành `valid_no_result`, `invalid_argument`, `backend_failure` hoặc `found`.
6. Với query đủ dữ kiện nhưng model không gọi tool, chạy một repair pass giới hạn một lần bằng schema nhỏ của specialist; vẫn giữ total execution bounded.

Acceptance gate:

- Smoke tool/argument 20/20, ba lần.
- Full 60 production cases: functional argument accuracy ≥ 0.97 và tool selection ≥ 0.98.
- Robustness: invalid/missing argument suppression ≥ 0.95.
- Không tăng max executed tool calls quá policy đã định.

### Phase 3 — Cải thiện first-stage retrieval, giữ lexical anchors

Mục tiêu: không để dense nhiễu phá exact identifiers.

1. Log raw rank và score của từng backend trước fusion: BM25 child score, parent aggregation, dense score, lane filter và source.
2. A/B các fusion variant trên dev, không đụng held-out:
   - weighted RRF với BM25 weight > dense cho query có code/cohort/entity;
   - query-adaptive fusion dựa trên lexical-anchor detector;
   - rank normalization hoặc relative-score fusion nếu dense score calibration đủ tin cậy;
   - giữ một lexical quota thay vì chỉ thêm BM25 vào candidate pool.
3. Lexical-anchor detector phải nhận được:
   - mã ngành/môn/quyết định;
   - `K45`–`K52`, năm học;
   - acronym CLC/CTTT/VLVH;
   - tên entity học bổng/biểu mẫu;
   - cụm ngắn có tính phân biệt như Vallet, SCIC, Robocon.
4. Candidate pool phải deduplicate theo source trước source-level rerank hoặc áp quota tối đa chunks/source.
5. Tăng candidate pool dựa trên recall diagnostics thay vì cố định `max(2 * top_n, 8)`; đo recall ceiling trước reranker.
6. Với bảng học phí, index thêm compact row documents chứa metadata canonical (program, code, cohort, program type, unit) để lexical/dense đều nhìn thấy đúng row.

Acceptance gate:

- Candidate recall@10 = 1.0 trên smoke retrieval và không thấp hơn approved run trên full held-out.
- E3 không còn làm mất top-3 gold source ở query có exact code/cohort/entity mà E1 đã tìm đúng.
- BM25 P@5/Recall@5 không bị giảm do thay đổi metric hoặc dedup sai.

### Phase 4 — Sửa reranking theo query và structure

Mục tiêu: giữ lợi ích E3 → E4 nhưng chặn catastrophic rerank.

1. Ghi cross-encoder score cho từng candidate vào trace; hiện log chỉ có final ordering nên khó giải thích.
2. Không cắt mù 1.000 ký tự đầu:
   - dùng best-matching child chunk + metadata header;
   - với table, dùng row đã match thay vì toàn parent;
   - với form/policy, dùng surrounding span chứa lexical hits.
3. Temporal prior chỉ bật khi query có tín hiệu “mới nhất”, năm học hoặc văn bản hiện hành; không tie-break theo thời gian cho câu hỏi biểu mẫu cố định.
4. Thêm lexical preservation constraint:
   - nếu BM25 top-1 có exact entity/code match mạnh, reranker chỉ được đẩy xuống khi score margin đủ lớn;
   - hoặc ensemble score `cross_encoder + lexical_anchor + metadata_match`.
5. Rerank source representatives trước, sau đó mới chọn thêm chunks cùng source cho generation.
6. Calibrate threshold/margin trên dev bằng grid search; không chọn threshold dựa trên hai held-out misses.

Acceptance gate:

- `SMK-GEN-01` và `SMK-SCH-01` đạt E5 Hit@1.
- Không regression trên 48/50 query E5 đã đúng top-1.
- E4/E5 Hit@1 tăng hoặc giữ nguyên, với per-domain report và confidence interval.

### Phase 5 — Evidence assembly và answer generation

Mục tiêu: retrieval đúng phải biến thành câu trả lời đúng và có provenance.

1. Dùng source-diverse context packing; không để năm chunks cùng source chiếm budget nếu một chunk đã đủ.
2. Với query cần nhiều nguồn, giữ quota theo source relation và lane.
3. Tool result phải được đưa vào evidence envelope có provenance, input args và status; generation không tự suy ra số thay tool.
4. Nếu retrieval và structured tool mâu thuẫn, áp explicit precedence theo loại dữ liệu và báo uncertainty.
5. Trả lời phải trích source/document key nội bộ trong trace dù UI có ẩn citation.

Acceptance gate:

- Answer correctness không giảm khi retrieval tăng.
- Mọi numeric answer có evidence span hoặc structured tool result tương ứng.
- Không dùng Ragas Faithfulness như bằng chứng duy nhất; đối chiếu thêm deterministic required facts và sample human review.

### Phase 6 — Đánh giá lại multi-agent vs single-agent

Mục tiêu: kiểm tra kiến trúc sau khi chất lượng thật đã cải thiện.

1. Freeze code, data, prompts, model, temperature và manifest trước run.
2. Chạy protocol ở ít nhất hai tool-space sizes: production 11 và scalability stress 27.
3. Dùng cùng query, cùng tool implementations, cùng retry/budget cho hai arm.
4. Báo paired difference và CI trên unique cases; repetitions chỉ đo stability, không giả làm independent samples.
5. Breakdown theo failure type và function, không chỉ aggregate.
6. Chỉ claim multi-agent advantage nếu CI không cắt 0 hoặc mô tả rõ đây là numerical/descriptive trend.

Acceptance gate đề xuất trước khi đưa vào paper:

- Multi không thua single ở production E2E.
- Multi tốt hơn rõ ở stress selection/robustness hoặc paper hạ claim thành scalability trade-off.
- Không có result metric nào dựa trên empty oracle.

## 5. Thứ tự triển khai khuyến nghị

| Ưu tiên | Việc | Lý do | Effort tương đối |
|---:|---|---|---:|
| P0 | Measurement contract + rescore | Nếu thước đo sai thì mọi tối ưu sau đó đều sai hướng | 0.5–1 ngày |
| P0 | Routing contract parity | Đang có LLM/deterministic divergence rõ ràng | 0.5–1 ngày |
| P0 | Tool required-arg rules + canonicalization | Sửa ngay lỗi Logistics, cohort, block, alias | 1 ngày |
| P1 | Retrieval tracing raw ranks/scores | Điều kiện cần để tune fusion/reranker có căn cứ | 0.5–1 ngày |
| P1 | Query-adaptive lexical preservation | Nhắm đúng 11 hybrid regressions và OTHER-04 | 1–2 ngày |
| P1 | Structure-aware rerank input | Khắc phục giới hạn 1.000 ký tự đầu | 1–2 ngày |
| P2 | Source-diverse context assembly | Giảm duplicate chunks và tăng coverage | 0.5–1 ngày |
| P2 | Full ablation + multi/single rerun | Chỉ chạy sau khi smoke và dev gates xanh | 1 ngày chạy/đọc log |

## 6. Quy trình mỗi lần sửa

1. Viết hypothesis một câu và liệt kê case dự kiến cải thiện/case không được regression.
2. Chạy smoke route/tool.
3. Nếu sửa retrieval, bật services và chạy smoke retrieval.
4. Chạy dev set/targeted ablation; không xem held-out để tune.
5. Chỉ khi dev gate đạt mới chạy full held-out một lần.
6. So sánh theo case, domain và metric; không chỉ nhìn aggregate.
7. Ghi manifest, hash, diff code và dependency versions.
8. Chạy `git diff --check` và `npx gitnexus detect-changes -r SchoolChatBot` trước commit.

## 7. Definition of done

- Smoke-20 strict pass 20/20 trong ba run liên tiếp khi services đầy đủ.
- Hai target retrieval (`Vallet`, `lệ phí bản sao`) đạt E5 Hit@1 mà không làm mất bất kỳ required case nào.
- Routing/tool full set đạt thresholds Phase 1–2.
- Retrieval full held-out không regression aggregate hoặc bất kỳ domain quan trọng nào; subgroup nhỏ phải báo raw N.
- Multi-vs-single được rerun bằng locked protocol v2; claim trong paper khớp CI và không có causal overclaim.
- Production logs đủ raw trace để lần sau biết lỗi nằm ở route, lane, candidate recall, fusion, reranker, tool arguments hay generation.
