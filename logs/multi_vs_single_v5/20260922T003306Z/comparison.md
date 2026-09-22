# Scenario 3 v5: Dynamic Tool Shortlisting Scalability

Records: **2160**; runtime errors: **0**; schema-guarded failures: **5**.

## Production-tool suite

| Registry | Architecture | Visible | Schema chars | Gold-in-Top-k | Selection | E2E | Input tokens | Latency |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 11 | Monolithic single-agent | 11.0 | 5393 | -- | 96.1% | 91.1% | 1849 | 1188 ms |
| 11 | Static-partition multi-agent | 4.5 | 2069 | -- | 90.6% | 83.3% | 3592 | 2285 ms |
| 11 | Top-k multi-agent | 4.0 | 1886 | 100.0% | 90.6% | 83.3% | 3543 | 2413 ms |
- topk_vs_single at 11: selection -5.6 pp [-11.7, +0.0]; E2E -7.8 pp [-13.9, -2.2].
- static_vs_single at 11: selection -5.6 pp [-11.7, +0.0]; E2E -7.8 pp [-14.4, -1.1].
- topk_vs_static at 11: selection +0.0 pp [+0.0, +0.0]; E2E -0.0 pp [-1.7, +1.7].

| 27 | Monolithic single-agent | 27.0 | 9786 | -- | 91.1% | 85.6% | 2792 | 1489 ms |
| 27 | Static-partition multi-agent | 8.5 | 3153 | -- | 93.3% | 86.7% | 3806 | 2199 ms |
| 27 | Top-k multi-agent | 4.9 | 2031 | 100.0% | 91.7% | 83.3% | 3540 | 2220 ms |
- topk_vs_single at 27: selection +0.6 pp [-7.2, +7.8]; E2E -2.2 pp [-10.6, +5.6].
- static_vs_single at 27: selection +2.2 pp [-3.9, +8.3]; E2E +1.1 pp [-6.7, +8.3].
- topk_vs_static at 27: selection -1.7 pp [-6.1, +2.2]; E2E -3.3 pp [-8.3, +1.1].

| 51 | Monolithic single-agent | 51.0 | 15789 | -- | 90.6% | 85.0% | 4050 | 1575 ms |
| 51 | Static-partition multi-agent | 14.5 | 4690 | -- | 87.2% | 78.3% | 4126 | 2616 ms |
| 51 | Top-k multi-agent | 5.0 | 1947 | 100.0% | 85.6% | 77.8% | 3508 | 2288 ms |
- topk_vs_single at 51: selection -5.0 pp [-11.1, +0.6]; E2E -7.2 pp [-13.9, -1.1].
- static_vs_single at 51: selection -3.3 pp [-10.0, +2.8]; E2E -6.7 pp [-13.9, +0.0].
- topk_vs_static at 51: selection -1.7 pp [-7.2, +3.3]; E2E -0.6 pp [-6.7, +5.0].

## Primary interactions

- topk_vs_single, Δ(51)−Δ(11): selection +0.6 pp [-4.4, +5.6]; E2E +0.6 pp [-5.0, +6.1].
- static_vs_single, Δ(51)−Δ(11): selection +2.2 pp [-3.3, +8.3]; E2E +1.1 pp [-6.7, +8.3].

## Robustness suite

| Registry | Architecture | Tool suppression | E2E | Bounded |
|---:|:---|---:|---:|---:|
| 11 | Monolithic single-agent | 93.3% | 83.3% | 100.0% |
| 11 | Static-partition multi-agent | 88.3% | 75.0% | 100.0% |
| 11 | Top-k multi-agent | 90.0% | 75.0% | 100.0% |
| 27 | Monolithic single-agent | 76.7% | 65.0% | 100.0% |
| 27 | Static-partition multi-agent | 76.7% | 63.3% | 100.0% |
| 27 | Top-k multi-agent | 75.0% | 63.3% | 100.0% |
| 51 | Monolithic single-agent | 76.7% | 66.7% | 100.0% |
| 51 | Static-partition multi-agent | 68.3% | 55.0% | 98.3% |
| 51 | Top-k multi-agent | 71.7% | 56.7% | 96.7% |
