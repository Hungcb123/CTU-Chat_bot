# Scenario 3 v6: Intra-Domain Tool Ambiguity

Records: **1960**; runtime errors: **0**; schema-guarded failures: **6**.

## Primary fixed-case suite

| Registry | Architecture | Visible | Gold recall | Selection | E2E | Input tokens | Latency |
|---:|:---|---:|---:|---:|---:|---:|---:|
| 11 | Monolithic full registry | 11.0 | -- | 95.3% | 88.0% | 1663 | 1566 ms |
| 11 | Single-agent global Top-k | 7.0 | 100.0% | 93.3% | 84.0% | 1139 | 1310 ms |
| 11 | Routed Top-k, generic gate | 5.2 | 100.0% | 92.7% | 82.0% | 3621 | 2546 ms |
| 11 | Routed Top-k, specialist gate | 5.2 | 100.0% | 95.3% | 87.3% | 3862 | 2348 ms |
- specialist_vs_single_topk: selection +2.0 pp [-3.3, +6.7]; E2E +3.3 pp [-2.7, +8.7].
- specialist_vs_routed_generic: selection +2.7 pp [-2.0, +7.3]; E2E +5.3 pp [-0.7, +11.3].
- specialist_vs_single_full: selection +0.0 pp [-5.3, +4.7]; E2E -0.7 pp [-6.0, +4.7].

| 31 | Monolithic full registry | 31.0 | -- | 90.7% | 83.3% | 2706 | 1643 ms |
| 31 | Single-agent global Top-k | 7.0 | 98.0% | 88.7% | 78.0% | 870 | 1299 ms |
| 31 | Routed Top-k, generic gate | 7.0 | 100.0% | 89.3% | 80.0% | 3623 | 2441 ms |
| 31 | Routed Top-k, specialist gate | 7.0 | 100.0% | 96.0% | 89.3% | 3935 | 2818 ms |
- specialist_vs_single_topk: selection +7.3 pp [+1.3, +14.0]; E2E +11.3 pp [+4.7, +18.7].
- specialist_vs_routed_generic: selection +6.7 pp [+3.3, +10.7]; E2E +9.3 pp [+4.0, +14.7].
- specialist_vs_single_full: selection +5.3 pp [+0.0, +11.3]; E2E +6.0 pp [-0.0, +13.3].

| 51 | Monolithic full registry | 51.0 | -- | 92.7% | 83.3% | 3722 | 1736 ms |
| 51 | Single-agent global Top-k | 7.0 | 94.0% | 85.3% | 76.0% | 789 | 1195 ms |
| 51 | Routed Top-k, generic gate | 7.0 | 94.0% | 84.7% | 75.3% | 3569 | 2368 ms |
| 51 | Routed Top-k, specialist gate | 7.0 | 94.0% | 90.0% | 84.0% | 3881 | 2558 ms |
- specialist_vs_single_topk: selection +4.7 pp [+0.7, +8.7]; E2E +8.0 pp [+2.0, +14.0].
- specialist_vs_routed_generic: selection +5.3 pp [+1.3, +10.0]; E2E +8.7 pp [+2.7, +15.3].
- specialist_vs_single_full: selection -2.7 pp [-10.0, +3.3]; E2E +0.7 pp [-8.0, +8.7].

## Primary high-minus-low interactions

- specialist_vs_single_topk: selection +2.7 pp [-4.7, +10.7]; E2E +4.7 pp [-3.3, +13.3].
- specialist_vs_routed_generic: selection +2.7 pp [-4.0, +10.7]; E2E +3.3 pp [-4.7, +12.0].
- specialist_vs_single_full: selection -2.7 pp [-10.7, +5.3]; E2E +1.3 pp [-8.0, +11.3].

## Diagnostic conditional on gold being shortlisted

| Registry | Architecture | Eligible records | Conditional selection |
|---:|:---|---:|---:|
| 11 | Single-agent global Top-k | 150 | 93.3% |
| 11 | Routed Top-k, generic gate | 150 | 92.7% |
| 11 | Routed Top-k, specialist gate | 150 | 95.3% |
| 31 | Single-agent global Top-k | 147 | 90.5% |
| 31 | Routed Top-k, generic gate | 150 | 89.3% |
| 31 | Routed Top-k, specialist gate | 150 | 96.0% |
| 51 | Single-agent global Top-k | 141 | 90.8% |
| 51 | Routed Top-k, generic gate | 141 | 90.1% |
| 51 | Routed Top-k, specialist gate | 141 | 95.7% |

## Semantic-neighbor coverage at 51 tools

| Architecture | Gold recall | Selection | E2E |
|:---|---:|---:|---:|
| Monolithic full registry | -- | 92.5% | 80.0% |
| Single-agent global Top-k | 92.5% | 82.5% | 77.5% |
| Routed Top-k, generic gate | 77.5% | 67.5% | 62.5% |
| Routed Top-k, specialist gate | 77.5% | 77.5% | 70.0% |
