# Multi-Agent vs. Monolithic Tool Orchestration — v2

This locked protocol uses live supervisor predictions for the multi-agent arm, deterministic tool-output oracles, and paired bootstrap intervals over unique cases.
Synthetic distractors, when enabled, are a scalability stress test and are not production tools.

## Distractors per specialist: 0

### production_tools

| Architecture | Unique cases | Runs | Selection | Arg EM | Result | E2E pass | Route acc. |
|---|---:|---:|---:|---:|---:|---:|---:|
| multi_agent | 60 | 180 | 0.9667 | 0.8833 | 0.8833 | 0.8833 | 0.9833 |
| single_agent | 60 | 180 | 0.9833 | 0.9333 | 0.9333 | 0.9333 | -- |

Paired E2E difference (Multi − Single): **-0.0500**, 95% bootstrap CI [-0.1167, +0.0000] over 60 unique cases.

### robustness

| Architecture | Unique cases | Runs | Selection | Arg EM | Result | E2E pass | Route acc. |
|---|---:|---:|---:|---:|---:|---:|---:|
| multi_agent | 20 | 60 | 0.9667 | 0.9667 | 0.9167 | 0.9167 | 1.0000 |
| single_agent | 20 | 60 | 0.9500 | 0.9500 | 0.9167 | 0.8667 | -- |

Paired E2E difference (Multi − Single): **+0.0500**, 95% bootstrap CI [-0.1000, +0.2500] over 20 unique cases.

## Distractors per specialist: 4

### production_tools

| Architecture | Unique cases | Runs | Selection | Arg EM | Result | E2E pass | Route acc. |
|---|---:|---:|---:|---:|---:|---:|---:|
| multi_agent | 60 | 180 | 1.0000 | 0.9000 | 0.9000 | 0.9000 | 0.9833 |
| single_agent | 60 | 180 | 0.9167 | 0.8667 | 0.8667 | 0.8667 | -- |

Paired E2E difference (Multi − Single): **+0.0333**, 95% bootstrap CI [-0.0500, +0.1167] over 60 unique cases.

### robustness

| Architecture | Unique cases | Runs | Selection | Arg EM | Result | E2E pass | Route acc. |
|---|---:|---:|---:|---:|---:|---:|---:|
| multi_agent | 20 | 60 | 0.7000 | 0.7000 | 0.6500 | 0.6500 | 1.0000 |
| single_agent | 20 | 60 | 0.8000 | 0.8000 | 0.6000 | 0.6000 | -- |

Paired E2E difference (Multi − Single): **+0.0500**, 95% bootstrap CI [-0.1500, +0.2500] over 20 unique cases.

