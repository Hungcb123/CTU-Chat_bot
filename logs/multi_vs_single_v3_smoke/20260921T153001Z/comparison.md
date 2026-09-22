# SCENARIO 3 v3: MULTI-AGENT VS MONOLITHIC TOOL-SPACE SCALABILITY

## 1. Production Tools Scalability Suite (N=60 Unique Cases, 3 Repetitions)

| Registry Size | Architecture | Visible Tools | Tool Selection | Argument EM | Result Acc | E2E Pass Rate | Paired Δ Selection (95% CI) | Paired Δ E2E (95% CI) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 11 | Monolithic Single | 11 | 100.0% | 100.0% | 100.0% | 100.0% | — | — |
| 11 | Multi-Agent (CTU-Chat) | 0--6 | **100.0%** | **100.0%** | **100.0%** | **100.0%** | +0.0% [+0.0, +0.0] | +0.0% [+0.0, +0.0] |
| 19 | Monolithic Single | 19 | 100.0% | 100.0% | 100.0% | 100.0% | — | — |
| 19 | Multi-Agent (CTU-Chat) | 2--8 | **100.0%** | **100.0%** | **100.0%** | **100.0%** | +0.0% [+0.0, +0.0] | +0.0% [+0.0, +0.0] |
| 27 | Monolithic Single | 27 | 100.0% | 100.0% | 100.0% | 100.0% | — | — |
| 27 | Multi-Agent (CTU-Chat) | 4--10 | **100.0%** | **100.0%** | **100.0%** | **100.0%** | +0.0% [+0.0, +0.0] | +0.0% [+0.0, +0.0] |

## 2. Interaction Analysis
- Primary Tool-Selection Interaction Δ(27) − Δ(11): **+0.00%** (95% CI [+0.00%, +0.00%])

## 3. Robustness Suite (N=20 Adversarial Cases, 3 Repetitions)

| Registry Size | Multi Tool Suppress | Single Tool Suppress | Multi E2E Pass | Single E2E Pass |
|:---:|:---:|:---:|:---:|:---:|
| 11 | 100.0% | 100.0% | 100.0% | 100.0% |
| 19 | 100.0% | 100.0% | 100.0% | 100.0% |
| 27 | 100.0% | 100.0% | 100.0% | 100.0% |
