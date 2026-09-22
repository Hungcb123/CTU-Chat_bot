# SCENARIO 3 v3: MULTI-AGENT VS MONOLITHIC TOOL-SPACE SCALABILITY

## 1. Production Tools Scalability Suite (N=60 Unique Cases, 3 Repetitions)

| Registry Size | Architecture | Visible Tools | Tool Selection | Argument EM | Result Acc | E2E Pass Rate | Paired Δ Selection (95% CI) | Paired Δ E2E (95% CI) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 11 | Monolithic Single | 11 | 73.9% | 73.9% | 65.6% | 65.6% | — | — |
| 11 | Multi-Agent (CTU-Chat) | 0--6 | **87.2%** | **87.2%** | **80.6%** | **80.6%** | +13.3% [+0.6, +25.6] | +15.0% [+2.2, +27.8] |
| 19 | Monolithic Single | 19 | 96.7% | 96.7% | 90.0% | 90.0% | — | — |
| 19 | Multi-Agent (CTU-Chat) | 2--8 | **92.2%** | **92.2%** | **83.9%** | **83.9%** | -4.4% [-11.7, +2.2] | -6.1% [-13.9, +1.1] |
| 27 | Monolithic Single | 27 | 96.1% | 96.1% | 91.7% | 91.7% | — | — |
| 27 | Multi-Agent (CTU-Chat) | 4--10 | **98.3%** | **98.3%** | **91.7%** | **91.7%** | +2.2% [+0.0, +6.1] | +0.0% [-4.4, +5.0] |

## 2. Interaction Analysis
- Primary Tool-Selection Interaction Δ(27) − Δ(11): **-11.11%** (95% CI [-23.33%, +1.11%])

## 3. Robustness Suite (N=20 Adversarial Cases, 3 Repetitions)

| Registry Size | Multi Tool Suppress | Single Tool Suppress | Multi E2E Pass | Single E2E Pass |
|:---:|:---:|:---:|:---:|:---:|
| 11 | 91.7% | 85.0% | 71.7% | 71.7% |
| 19 | 80.0% | 90.0% | 60.0% | 86.7% |
| 27 | 70.0% | 80.0% | 65.0% | 70.0% |
