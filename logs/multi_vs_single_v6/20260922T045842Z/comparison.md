# Scenario 3 v6: Intra-Domain Tool Ambiguity

Records: **1960**; runtime errors: **19**; schema-guarded failures: **4**.

## Primary fixed-case suite

| Registry | Architecture | Visible | Gold recall | Selection | E2E | Input tokens | Latency |
|---:|:---|---:|---:|---:|---:|---:|---:|
| 11 | Monolithic full registry | 11.0 | -- | 94.0% | 86.0% | 1663 | 1098 ms |
| 11 | Single-agent global Top-k | 10.0 | 100.0% | 93.3% | 83.3% | 1541 | 1148 ms |
| 11 | Routed Top-k, generic gate | 5.1 | 98.0% | 90.7% | 80.0% | 1204 | 1889 ms |
| 11 | Routed Top-k, specialist gate | 5.1 | 98.0% | 93.3% | 85.3% | 1441 | 1983 ms |
- specialist_vs_single_topk: selection -0.0 pp [-5.3, +4.7]; E2E +2.0 pp [-4.0, +7.3].
- specialist_vs_routed_generic: selection +2.7 pp [-2.0, +7.3]; E2E +5.3 pp [-0.7, +11.3].
- specialist_vs_single_full: selection -0.7 pp [-6.0, +4.7]; E2E -0.7 pp [-6.7, +5.3].

| 31 | Monolithic full registry | 31.0 | -- | 91.3% | 84.7% | 2706 | 1157 ms |
| 31 | Single-agent global Top-k | 10.0 | 98.0% | 90.0% | 81.3% | 1149 | 1033 ms |
| 31 | Routed Top-k, generic gate | 9.8 | 98.0% | 88.0% | 79.3% | 1396 | 1958 ms |
| 31 | Routed Top-k, specialist gate | 9.8 | 98.0% | 93.3% | 88.7% | 1830 | 2015 ms |
- specialist_vs_single_topk: selection +3.3 pp [-2.7, +9.3]; E2E +7.3 pp [+0.7, +14.7].
- specialist_vs_routed_generic: selection +5.3 pp [+2.0, +8.7]; E2E +9.3 pp [+5.3, +14.0].
- specialist_vs_single_full: selection +2.0 pp [-3.3, +7.3]; E2E +4.0 pp [-2.0, +10.0].

| 51 | Monolithic full registry | 51.0 | -- | 92.7% | 83.3% | 3722 | 1289 ms |
| 51 | Single-agent global Top-k | 10.0 | 96.0% | 86.7% | 78.7% | 1036 | 997 ms |
| 51 | Routed Top-k, generic gate | 9.8 | 98.0% | 91.3% | 82.7% | 1340 | 1907 ms |
| 51 | Routed Top-k, specialist gate | 9.8 | 98.0% | 92.7% | 88.0% | 1770 | 2021 ms |
- specialist_vs_single_topk: selection +6.0 pp [-1.3, +14.0]; E2E +9.3 pp [+2.0, +17.3].
- specialist_vs_routed_generic: selection +1.3 pp [-1.3, +4.0]; E2E +5.3 pp [+0.7, +10.7].
- specialist_vs_single_full: selection +0.0 pp [-5.3, +5.3]; E2E +4.7 pp [-1.3, +11.3].

## Primary high-minus-low interactions

- specialist_vs_single_topk: selection +6.0 pp [-0.0, +13.3]; E2E +7.3 pp [-0.0, +15.3].
- specialist_vs_routed_generic: selection -1.3 pp [-7.3, +5.3]; E2E -0.0 pp [-7.3, +8.0].
- specialist_vs_single_full: selection +0.7 pp [-5.3, +7.3]; E2E +5.3 pp [-2.7, +14.0].

## Diagnostic conditional on gold being shortlisted

| Registry | Architecture | Eligible records | Conditional selection |
|---:|:---|---:|---:|
| 11 | Single-agent global Top-k | 150 | 93.3% |
| 11 | Routed Top-k, generic gate | 147 | 92.5% |
| 11 | Routed Top-k, specialist gate | 147 | 95.2% |
| 31 | Single-agent global Top-k | 147 | 91.8% |
| 31 | Routed Top-k, generic gate | 147 | 89.8% |
| 31 | Routed Top-k, specialist gate | 147 | 95.2% |
| 51 | Single-agent global Top-k | 144 | 90.3% |
| 51 | Routed Top-k, generic gate | 147 | 93.2% |
| 51 | Routed Top-k, specialist gate | 147 | 94.6% |

## Semantic-neighbor coverage at 51 tools

| Architecture | Gold recall | Selection | E2E |
|:---|---:|---:|---:|
| Monolithic full registry | -- | 92.5% | 80.0% |
| Single-agent global Top-k | 92.5% | 82.5% | 77.5% |
| Routed Top-k, generic gate | 92.5% | 82.5% | 75.0% |
| Routed Top-k, specialist gate | 92.5% | 92.5% | 82.5% |
