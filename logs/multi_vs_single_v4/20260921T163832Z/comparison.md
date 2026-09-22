# Scenario 3 v4: Counterbalanced Three-Arm Tool-Space Scalability

Total records: **2160**; execution errors: **13**.

## Production-tool suite

| Registry | Architecture | Visible tools | Schema chars | Selection | Argument EM | Result Acc. | E2E Pass | Decision latency |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 11 | Monolithic single-agent | 11.0 | 5393 | 93.9% | 93.9% | 88.3% | 87.8% | 1039 ms |
| 11 | Oracle-partitioned control | 4.4 | 2027 | 92.2% | 91.7% | 83.9% | 83.9% | 890 ms |
| 11 | Live supervisor multi-agent | 4.5 | 2069 | 92.2% | 92.2% | 84.4% | 84.4% | 1703 ms |

- Live multi vs. monolithic at 11 tools: selection -1.7 pp [-7.8, +3.9]; E2E -3.3 pp [-9.4, +2.8].
- Oracle partition vs. monolithic at 11 tools: selection -1.7 pp [-7.8, +3.9]; E2E -3.9 pp [-10.0, +2.2].
- Live multi vs. oracle partition at 11 tools: selection +0.0 pp [+0.0, +0.0]; E2E +0.6 pp [+0.0, +1.7].

| 19 | Monolithic single-agent | 19.0 | 7627 | 94.4% | 93.9% | 88.9% | 88.9% | 1097 ms |
| 19 | Oracle-partitioned control | 6.4 | 2591 | 91.1% | 91.1% | 83.9% | 83.9% | 858 ms |
| 19 | Live supervisor multi-agent | 6.5 | 2635 | 91.1% | 91.1% | 83.9% | 83.9% | 1702 ms |

- Live multi vs. monolithic at 19 tools: selection -3.3 pp [-8.9, +1.7]; E2E -5.0 pp [-11.7, +1.7].
- Oracle partition vs. monolithic at 19 tools: selection -3.3 pp [-8.9, +1.7]; E2E -5.0 pp [-11.7, +1.7].
- Live multi vs. oracle partition at 19 tools: selection +0.0 pp [+0.0, +0.0]; E2E +0.0 pp [+0.0, +0.0].

| 27 | Monolithic single-agent | 27.0 | 9786 | 95.6% | 94.4% | 89.4% | 89.4% | 1143 ms |
| 27 | Oracle-partitioned control | 8.4 | 3110 | 93.3% | 92.8% | 85.6% | 85.6% | 911 ms |
| 27 | Live supervisor multi-agent | 8.5 | 3153 | 93.9% | 93.3% | 86.1% | 86.1% | 1728 ms |

- Live multi vs. monolithic at 27 tools: selection -1.7 pp [-6.7, +2.2]; E2E -3.3 pp [-8.9, +2.2].
- Oracle partition vs. monolithic at 27 tools: selection -2.2 pp [-7.2, +2.2]; E2E -3.9 pp [-9.4, +1.7].
- Live multi vs. oracle partition at 27 tools: selection +0.6 pp [+0.0, +1.7]; E2E +0.6 pp [+0.0, +1.7].

## Primary interaction

- live_vs_single, selection Δ(27)−Δ(11): +0.0 pp [-5.0, +5.6]; E2E: +0.0 pp [-5.6, +6.1].
- oracle_vs_single, selection Δ(27)−Δ(11): -0.6 pp [-5.6, +4.4]; E2E: +0.0 pp [-6.1, +6.7].

## Robustness suite

| Registry | Architecture | Tool suppression/selection | E2E Pass | Bounded |
|---:|:---|---:|---:|---:|
| 11 | Monolithic single-agent | 95.0% | 86.7% | 100.0% |
| 11 | Oracle-partitioned control | 95.0% | 70.0% | 100.0% |
| 11 | Live supervisor multi-agent | 95.0% | 71.7% | 100.0% |
| 19 | Monolithic single-agent | 86.7% | 76.7% | 100.0% |
| 19 | Oracle-partitioned control | 86.7% | 65.0% | 100.0% |
| 19 | Live supervisor multi-agent | 86.7% | 65.0% | 100.0% |
| 27 | Monolithic single-agent | 80.0% | 68.3% | 98.3% |
| 27 | Oracle-partitioned control | 73.3% | 56.7% | 100.0% |
| 27 | Live supervisor multi-agent | 73.3% | 56.7% | 100.0% |

## Order-block sensitivity

| Gold position block | Architecture | N | Selection | E2E Pass |
|:---|:---|---:|---:|---:|
| gold_first | Monolithic single-agent | 180 | 93.9% | 91.7% |
| gold_first | Oracle-partitioned control | 180 | 96.7% | 89.4% |
| gold_first | Live supervisor multi-agent | 180 | 96.7% | 89.4% |
| gold_middle | Monolithic single-agent | 180 | 93.3% | 86.7% |
| gold_middle | Oracle-partitioned control | 180 | 88.3% | 81.1% |
| gold_middle | Live supervisor multi-agent | 180 | 88.9% | 81.7% |
| gold_last | Monolithic single-agent | 180 | 96.7% | 87.8% |
| gold_last | Oracle-partitioned control | 180 | 91.7% | 82.8% |
| gold_last | Live supervisor multi-agent | 180 | 91.7% | 83.3% |
