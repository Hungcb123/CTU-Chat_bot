# EXPERIMENT TRACEABILITY & STRICT GROUND TRUTH AUDIT

This document establishes 100% mathematical and empirical traceability for all numerical claims, metrics, dataset sizes, scenario definitions, ablation configurations, and routing/tool results across the paper:

**Paper Title:** *CTU-Chat: Supervisor-Routed Multi-Agent RAG with Heterogeneous Knowledge Allocation for University Counseling*

**Authoritative Ground-Truth Reports:**
1. **Report 1:** `E:\RHNA\1Visual\CTU-chat\CTU-Chat_bot\tests\report_rescored.md`
2. **Report 2:** `E:\RHNA\1Visual\CTU-chat\CTU-Chat_bot\tests\SCENARIO_3_DE_XUAT.md`
3. **Report 3:** `E:\RHNA\1Visual\CTU-chat\CTU-Chat_bot\tests\outputpaper\BAO_CAO_THUC_NGHIEM_TABLE3.md`
4. **Report 4:** `E:\RHNA\1Visual\CTU-chat\CTU-Chat_bot\tests\outputpaper\BAO_CAO_THUC_NGHIEM_TABLE4.md`

---

## 1. Traceability Matrix

| Paper Section | Claim / Metric | Value in Paper | Ground-Truth Report | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Abstract (`00-abstract.tex`)** | Supervisor Routing Accuracy | 97.0% | Report 1 (`report_rescored.md`), Table 1, row `llm_supervisor`, col `Agent accuracy` | MATCH |
| **Abstract (`00-abstract.tex`)** | Supervisor Routing Macro-F1 | 97.8% | Report 1 (`report_rescored.md`), Table 1, row `llm_supervisor`, col `Macro-F1` | MATCH |
| **Abstract (`00-abstract.tex`)** | Bounded Execution Invariants | $\text{max\_tool\_calls}=1$, $\text{timeout}=60.0\,\text{s}$ | Report 1 (`report_rescored.md`), lines 6--7; Report 2 (`SCENARIO_3_DE_XUAT.md`), lines 24--25 | MATCH |
| **Abstract (`00-abstract.tex`)** | Bounded Execution Completion Rate | 100.0% | Report 1 (`report_rescored.md`), Tables 1, 2, 3, col `Bounded` | MATCH |
| **Abstract (`00-abstract.tex`)** | Benchmark Dataset Size | 150-case benchmark ($N=150$) | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), line 4; Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), line 4 | MATCH |
| **Abstract (`00-abstract.tex`)** | Progressive Component Stacking Hit@1 | 0.8667 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Table 3 (Giai đoạn 3), row `E5`, col `H@1` | MATCH |
| **Abstract (`00-abstract.tex`)** | Progressive Component Stacking Hit@3 | 1.0000 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Table 3 (Giai đoạn 3), row `E5`, col `H@3` | MATCH |
| **Abstract (`00-abstract.tex`)** | Progressive Component Stacking Recall@5 | 1.0000 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Table 3 (Giai đoạn 3), row `E5`, col `R@5` | MATCH |
| **Abstract (`00-abstract.tex`)** | Progressive Component Stacking MRR@10 | 0.9222 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Table 3 (Giai đoạn 3), row `E5`, col `MRR` | MATCH |
| **Abstract (`00-abstract.tex`)** | Prior universal arithmetic-error claim | Replaced with tested fee-reduction tool result accuracy: 100.0% | Report 1 (`report_rescored.md`), Table 2, row `tuition_reduction_calculation`, col `Result` | UNSUPPORTED REMOVED |
| **Section 4.1 (`04-experiments.tex`)** | Total Benchmark Queries ($N$) | 150 queries | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), line 4; Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), line 4 | MATCH |
| **Section 4.1 (`04-experiments.tex`)** | Prior advisor-drafted and administrator-audited provenance claims | Removed; the reports do not document collection, annotator roles, or independent human review | Reports 3 and 4 identify the benchmark file and size but provide no such provenance protocol | UNSUPPORTED REMOVED |
| **Section 4.1 (`04-experiments.tex`)** | Prior full-benchmark category counts and percentages | Removed; exact counts are retained only for the 100-question Scenario~3 routing subset | Report 2 (`SCENARIO_3_DE_XUAT.md`), Section 3.1 documents the subset distribution, not the complete 150-question distribution | UNSUPPORTED REMOVED |
| **Section 4.2 (`04-experiments.tex`)** | Total E2E QA Evaluations | 1,050 evaluations ($150 \times 7$) | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Section 2, line 36 | MATCH |
| **Section 4.2 (`04-experiments.tex`)** | E2E QA Runtime & Workers | 7.7 minutes across 5 parallel worker threads | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Section 2, line 36 | MATCH |
| **Section 4.3 (`04-experiments.tex`)** | Operational Invariants | $\text{max\_tool\_calls}=1, \text{timeout}=60.0\,\text{s}$ | Report 1 (`report_rescored.md`), lines 6--7; Report 2 (`SCENARIO_3_DE_XUAT.md`), lines 24--25 | MATCH |
| **Table 4 (`04-experiments.tex`)** | RQ1 Target Metrics Claim | 97.0% routing, 100% tool EM (tuition), 100% bounded | Report 1 (`report_rescored.md`), Tables 1, 2, 3 | MATCH |
| **Table 4 (`04-experiments.tex`)** | RQ2 Target Metrics Claim | T7 records the lowest hybrid-configuration AC: 0.398 | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Table 4, row `T7`, col `AC` | MATCH |
| **Table 4 (`04-experiments.tex`)** | RQ3 Target Metrics Claim | E5 attains 0.8667 Hit@1, 1.0000 Recall@5 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Table 3, row `E5` | MATCH |
| **Table 5 (`04-experiments.tex`)** | E1 (BM25 Lexical) Metrics | Hit@1: 0.7333, Hit@3: 0.8667, P@5: 0.2133, R@5: 0.9000, MRR: 0.8133 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Section 2 (Giai đoạn 3), Table 3, row `E1` | MATCH |
| **Table 5 (`04-experiments.tex`)** | E2 (Dense Vector) Metrics | Hit@1: 0.5333, Hit@3: 0.6000, P@5: 0.1600, R@5: 0.6667, MRR: 0.5833 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Section 2 (Giai đoạn 3), Table 3, row `E2` | MATCH |
| **Table 5 (`04-experiments.tex`)** | E3 (Hybrid RRF) Metrics | Hit@1: 0.6000, Hit@3: 0.8000, P@5: 0.2000, R@5: 0.8333, MRR: 0.7006 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Section 2 (Giai đoạn 3), Table 3, row `E3` | MATCH |
| **Table 5 (`04-experiments.tex`)** | E4 (Hybrid + Cross-Reranker) Metrics | Hit@1: 0.8000, Hit@3: 0.9333, P@5: 0.2267, R@5: 0.9333, MRR: 0.8556 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Section 2 (Giai đoạn 3), Table 3, row `E4` | MATCH |
| **Table 5 (`04-experiments.tex`)** | E5 (Full Proposed System) Metrics | Hit@1: 0.8667, Hit@3: 1.0000, P@5: 0.2400, R@5: 1.0000, MRR: 0.9222 | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Section 2 (Giai đoạn 3), Table 3, row `E5` | MATCH |
| **Section 4.4.1 (`04-experiments.tex`)** | Retrieval Latencies E1, E3, E4, E5 | E1: 20.09 ms; E3: 94.05 ms; E4: 36,274.77 ms; E5: 59,011.74 ms | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Section 2 (Giai đoạn 3), Table 3, col `Latency (ms)` | MATCH |
| **Table 6 (`04-experiments.tex`)** | T1 (BM25 + LLM) | AR: 0.561, CR: 0.745, CP: 0.684, AC: 0.518 | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Section 2, Table 4, row `T1` | MATCH |
| **Table 6 (`04-experiments.tex`)** | T2 (Dense + LLM) | AR: 0.455, CR: 0.533, CP: 0.421, AC: 0.395 | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Section 2, Table 4, row `T2` | MATCH |
| **Table 6 (`04-experiments.tex`)** | T3 (Hybrid + LLM) | AR: 0.578, CR: 0.682, CP: 0.550, AC: 0.506 | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Section 2, Table 4, row `T3` | MATCH |
| **Table 6 (`04-experiments.tex`)** | T4 (Proposed CTU-Chat Full Stack) | AR: 0.551, CR: 0.745, CP: 0.749, AC: 0.500 | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Section 2, Table 4, row `T4` | MATCH |
| **Table 6 (`04-experiments.tex`)** | T5 (w/o Cross-Encoder Reranker) | AR: 0.575, CR: 0.682, CP: 0.550, AC: 0.525 | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Section 2, Table 4, row `T5` | MATCH |
| **Table 6 (`04-experiments.tex`)** | T6 (w/o Knowledge Graph Grounding) | AR: 0.561, CR: 0.745, CP: 0.750, AC: 0.508 | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Section 2, Table 4, row `T6` | MATCH |
| **Table 6 (`04-experiments.tex`)** | T7 (w/o Governance Filter) | AR: 0.479, CR: 0.533, CP: 0.421, AC: 0.398 | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Section 2, Table 4, row `T7` | MATCH |
| **Section 4.4.3 (`04-experiments.tex`)** | Scenario 3 Execution Parameters | Model: `gemini-2.5-flash-lite`, Backend: Vertex AI, temp: 0.0, timeout: 60.0 s, max tool calls per decision: 1, retries: 1, delay: 1.0 s, reps: 3 | Report 1 (`report_rescored.md`), lines 3--7; Report 2 (`SCENARIO_3_DE_XUAT.md`), lines 18--28 | MATCH |
| **Section 4.4.3 (`04-experiments.tex`)** | Routing Suite Query Sample Size | 100 single-domain queries (50 composite `CDICT*` queries excluded) | Report 2 (`SCENARIO_3_DE_XUAT.md`), lines 37--43; Report 1 (`report_rescored.md`), line 36 | MATCH |
| **Section 4.4.3 (`04-experiments.tex`)** | Specialist Mapping Query Counts | financial (28), general (49), scholarship (14), academic (9) = 100 queries | Report 2 (`SCENARIO_3_DE_XUAT.md`), lines 49--60 | MATCH |
| **Section 4.4.3 (`04-experiments.tex`)** | Tool Calling Test Cases Count | 30 test cases ($N=90$ runs across 3 reps: 10 structured tuition, 10 scholarship, 10 reduction) | Report 2 (`SCENARIO_3_DE_XUAT.md`), lines 68--73 | MATCH |
| **Section 4.4.3 (`04-experiments.tex`)** | Robustness Test Cases Count | 20 failure cases ($N=60$ runs across 3 reps) | Report 2 (`SCENARIO_3_DE_XUAT.md`), lines 80--90; Report 1 (`report_rescored.md`), line 28 | MATCH |
| **Table 7 (`04-experiments.tex`)** | Panel A: Rule-Based Router ($N=100$) | Agent Acc: 85.0%, Macro-F1: 69.2%, Intent Acc: 69.0%, Bounded: 100.0%, p50: 0.0 ms, p95: 0.1 ms | Report 1 (`report_rescored.md`), Table 1, row `rule_router` | MATCH |
| **Table 7 (`04-experiments.tex`)** | Panel A: LLM Supervisor ($N=300$) | Agent Acc: 97.0%, Macro-F1: 97.8%, Intent Acc: 95.0%, Bounded: 100.0%, p50: 795.5 ms, p95: 981.7 ms | Report 1 (`report_rescored.md`), Table 1, row `llm_supervisor` | MATCH |
| **Table 7 (`04-experiments.tex`)** | Panel B: `tuition_lookup` ($N=30$) | Selection: 100.0%, Arg EM: 100.0%, Result: 100.0%, E2E: 100.0%, Bounded: 100.0% | Report 1 (`report_rescored.md`), Table 2, row `tuition_lookup` | MATCH |
| **Table 7 (`04-experiments.tex`)** | Panel B: `scholarship_calc` ($N=30$) | Selection: 86.7%, Arg EM: 76.7%, Result: 86.7%, E2E: 76.7%, Bounded: 100.0% | Report 1 (`report_rescored.md`), Table 2, row `scholarship_calculation` | MATCH |
| **Table 7 (`04-experiments.tex`)** | Panel B: `tuition_reduction` ($N=30$) | Selection: 100.0%, Arg EM: 100.0%, Result: 100.0%, E2E: 100.0%, Bounded: 100.0% | Report 1 (`report_rescored.md`), Table 2, row `tuition_reduction_calculation` | MATCH |
| **Table 7 (`04-experiments.tex`)** | Panel C: Failure Gate Robustness ($N=60$) | Agent Acc: 100.0%, Tool Gate: 100.0%, Safe Result: 98.3%, E2E: 98.3%, Bounded: 100.0% | Report 1 (`report_rescored.md`), Table 3, row `60` | MATCH |
| **Section 4.4.3 (`04-experiments.tex`)** | Total Rescored Decision Records | 550 rescored isolated decision records (Panels A, B, C) | Report 1 (`report_rescored.md`), line 35 | MATCH |
| **Section 4.5 RQ1 (`04-experiments.tex`)** | RQ1 Synthesis Metrics | 97.0% agent acc, 97.8% Macro-F1 across 300 runs vs 85.0% and 69.2%; 100% tuition arg EM; 100% tool gate, 98.3% safe result, 100% bounded | Report 1 (`report_rescored.md`), Tables 1, 2, 3 | MATCH |
| **Section 4.5 RQ2 (`04-experiments.tex`)** | Outdated Category Claim ($0.933$ Hit@1, $0.942$ MRR) | Replaced with grounded T4 ($0.749$ CP, $0.745$ CR), T7 ($0.421$ CP, $0.533$ CR, $0.398$ AC), and E5 ($0.8667$ Hit@1, $1.0000$ Hit@3/Recall@5, $0.9222$ MRR) | Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`), Table 4; Report 3, Table 3 | MISMATCH FIXED |
| **Section 4.5 RQ3 (`04-experiments.tex`)** | RQ3 Synthesis Metrics | Top-1 from 0.7333 (E1) to 0.8667 (E5); 1.0000 Hit@3/Recall@5; 0.9222 MRR; Latencies 20.09 ms $\rightarrow$ 36,274.77 ms (E4) and 59,011.74 ms (E5); E3 94.05 ms | Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`), Table 3 | MATCH |
| **Section 5 (`05-conclusion.tex`)** | Prior zero arithmetic hallucination guarantee | Replaced with tested tuition lookup and tuition-reduction result accuracy: 100.0% | Report 1 (`report_rescored.md`), Table 2, rows `tuition_lookup` and `tuition_reduction_calculation`, col `Result` | UNSUPPORTED REMOVED |
| **Section 5 (`05-conclusion.tex`)** | Conclusion Metrics Summary | 97.0% supervisor routing acc, 100.0% bounded completion, 100.0% result accuracy (tuition lookup/reduction); 0.8667 Hit@1, 1.0000 Hit@3/Recall@5, 0.9222 MRR; T7 records the lowest hybrid AC ($0.398$) | Reports 1, 3, 4 | MATCH |

---

## 2. Conflict Analysis Across the 4 Ground-Truth Reports

| Report Pair | Inspected Content | Conflicts Found | Resolution |
| :--- | :--- | :--- | :--- |
| **Report 1 (`report_rescored.md`) vs. Report 2 (`SCENARIO_3_DE_XUAT.md`)** | Scenario 3 experimental setup, suite partitions, sample sizes, execution parameters | **None.** Report 2 defines the methodology and dataset splits ($N=100$ single-domain, 50 composite excluded, 30 tool cases, 20 robustness cases, 3 reps, temp 0.0, timeout 60s, maximum 1 tool call per decision). Report 1 outputs the exact rescored empirical measurements matching Report 2's specification. | Full agreement. |
| **Report 3 (`BAO_CAO_THUC_NGHIEM_TABLE3.md`) vs. Report 4 (`BAO_CAO_THUC_NGHIEM_TABLE4.md`)** | Dataset size ($N=150$) and category scope (`150_NATURAL_NO_APPENDIX.csv`) | **None.** Both use the exact same 150-case benchmark. Report 3 evaluates retrieval component stacking (E1--E5). Report 4 evaluates end-to-end generation and modular ablation (T1--T7) using Ragas LLM-as-a-judge on Vertex AI. | Full agreement. |
| **Report 1/2 (Scenario 3) vs. Report 3/4 (Scenarios 1 & 2)** | Functional boundary and scope | **None.** Scenario 3 deliberately isolates multi-agent routing and tool calling from retrieval and generation, as mandated by Report 2 Section 1: *"Scenario 3 đánh giá riêng khả năng điều phối và gọi công cụ của CTU-Chat, không trộn với chất lượng retrieval ở Table 3 hoặc chất lượng câu trả lời ở Table 4."* | Distinct orthogonal evaluations. |

---

## 3. Grounding Compliance Verification Summary

- **MATCH:** All experimental numbers retained in the paper match the cited authoritative reports.
- **MISMATCH FIXED:** The Section 4.5 RQ2 discussion removed outdated pre-rescored category metrics (`0.933 Hit@1 / 0.942 MRR`) and replaced them with grounded T4/T7/E5 metrics.
- **UNSUPPORTED REMOVED:** Universal arithmetic claims, undocumented dataset-provenance claims, and the unsupported full-benchmark category distribution were removed or bounded to the evidence.
- **CONFLICT REQUIRES REVIEW:** 0 conflicts.
- **Zero invented, estimated, interpolated, or recomputed numbers:** Verified.
- **Exact sample denominators preserved:** $N=150$ for Scenarios 1 & 2; $N=300$ for LLM Supervisor; $N=100$ for Rule Router; $N=30$ per function for Tool Reliability; $N=60$ for Adversarial Robustness; 550 total rescored decision records.
