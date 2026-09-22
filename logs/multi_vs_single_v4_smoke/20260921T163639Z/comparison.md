# Scenario 3 v4: Counterbalanced Three-Arm Tool-Space Scalability

Total records: **9**; execution errors: **0**.

## Production-tool suite

| Registry | Architecture | Visible tools | Schema chars | Selection | Argument EM | Result Acc. | E2E Pass | Decision latency |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 11 | Monolithic single-agent | 11.0 | 5393 | 100.0% | 100.0% | 100.0% | 100.0% | 1622 ms |
| 11 | Oracle-partitioned control | 6.0 | 2268 | 100.0% | 100.0% | 100.0% | 100.0% | 1710 ms |
| 11 | Live supervisor multi-agent | 6.0 | 2268 | 100.0% | 100.0% | 100.0% | 100.0% | 3329 ms |

- Live multi vs. monolithic at 11 tools: selection +0.0 pp [+0.0, +0.0]; E2E +0.0 pp [+0.0, +0.0].
- Oracle partition vs. monolithic at 11 tools: selection +0.0 pp [+0.0, +0.0]; E2E +0.0 pp [+0.0, +0.0].
- Live multi vs. oracle partition at 11 tools: selection +0.0 pp [+0.0, +0.0]; E2E +0.0 pp [+0.0, +0.0].

## Primary interaction


## Robustness suite

| Registry | Architecture | Tool suppression/selection | E2E Pass | Bounded |
|---:|:---|---:|---:|---:|

## Order-block sensitivity

| Gold position block | Architecture | N | Selection | E2E Pass |
|:---|:---|---:|---:|---:|
| gold_first | Monolithic single-agent | 1 | 100.0% | 100.0% |
| gold_first | Oracle-partitioned control | 1 | 100.0% | 100.0% |
| gold_first | Live supervisor multi-agent | 1 | 100.0% | 100.0% |
| gold_middle | Monolithic single-agent | 1 | 100.0% | 100.0% |
| gold_middle | Oracle-partitioned control | 1 | 100.0% | 100.0% |
| gold_middle | Live supervisor multi-agent | 1 | 100.0% | 100.0% |
| gold_last | Monolithic single-agent | 1 | 100.0% | 100.0% |
| gold_last | Oracle-partitioned control | 1 | 100.0% | 100.0% |
| gold_last | Live supervisor multi-agent | 1 | 100.0% | 100.0% |
