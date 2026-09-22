# Scenario 3 Experiment Results

- Model: `gemini-2.5-flash-lite`
- Backend: `vertex_ai_service_account`
- Repetitions: `3`
- Timeout per LLM decision: `60.0 s`
- Maximum tool calls per decision: `1`

## Routing and specialist selection

| Variant | N | Agent accuracy | Macro-F1 | Intent accuracy | Bounded | p50 (ms) | p95 (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| rule_router | 100 | 85.0% | 69.2% | 69.0% | 100.0% | 0.0 | 0.1 |
| llm_supervisor | 300 | 97.0% | 97.8% | 95.0% | 100.0% | 795.5 | 981.7 |

## Tool reliability

| Function | N | Selection/path | Argument EM | Result | End-to-end | Bounded |
|---|---:|---:|---:|---:|---:|---:|
| tuition_lookup | 30 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| scholarship_calculation | 30 | 86.7% | 76.7% | 86.7% | 76.7% | 100.0% |
| tuition_reduction_calculation | 30 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

## Robustness and bounded failure handling

| N | Agent accuracy | Intent accuracy | Tool/no-tool decision | Result behavior | Bounded | End-to-end |
|---:|---:|---:|---:|---:|---:|---:|
| 60 | 100.0% | 100.0% | 100.0% | 98.3% | 100.0% | 98.3% |

> `tra_cuu_hoc_phi` cases are deterministic structured-path checks. Scholarship and tuition-reduction cases are LLM tool-selection checks.

## Rescore metadata

- Original records: `750`
- Rescored records: `550`
- Excluded composite routing records: `200`
- Relabeled routing records: `12`
