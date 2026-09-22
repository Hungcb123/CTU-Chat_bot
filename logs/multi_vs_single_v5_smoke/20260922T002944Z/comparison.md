# Scenario 3 v5: Dynamic Tool Shortlisting Scalability

Records: **9**; runtime errors: **0**; schema-guarded failures: **0**.

## Production-tool suite

| Registry | Architecture | Visible | Schema chars | Gold-in-Top-k | Selection | E2E | Input tokens | Latency |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 11 | Monolithic single-agent | 11.0 | 5393 | -- | 100.0% | 100.0% | 1844 | 1938 ms |
| 11 | Static-partition multi-agent | 6.0 | 2268 | -- | 100.0% | 100.0% | 3591 | 2920 ms |
| 11 | Top-k multi-agent | 5.0 | 2009 | 100.0% | 100.0% | 100.0% | 3521 | 2445 ms |
- topk_vs_single at 11: selection +0.0 pp [+0.0, +0.0]; E2E +0.0 pp [+0.0, +0.0].
- static_vs_single at 11: selection +0.0 pp [+0.0, +0.0]; E2E +0.0 pp [+0.0, +0.0].
- topk_vs_static at 11: selection +0.0 pp [+0.0, +0.0]; E2E +0.0 pp [+0.0, +0.0].

## Primary interactions


## Robustness suite

| Registry | Architecture | Tool suppression | E2E | Bounded |
|---:|:---|---:|---:|---:|
