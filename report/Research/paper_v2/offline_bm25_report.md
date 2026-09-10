# Offline BM25 diagnostic

Development labels; full-document local BM25, not production E1 or RAGAS.

| Version | Subset | n | MRR@10 | Source R@5 | Evidence sufficiency@5 |
|---|---|---:|---:|---:|---:|
| original | core_100 | 100 | 0.6438 | 0.7900 | 0.7900 |
| original | synthetic_stress_50 | 50 | 0.8114 | 0.5900 | 0.2600 |
| original | all_150 | 150 | 0.6996 | 0.7233 | 0.6133 |
| revised | core_100 | 100 | 0.7178 | 0.8450 | 0.8400 |
| revised | synthetic_stress_50 | 50 | 0.7075 | 0.4500 | 0.1200 |
| revised | all_150 | 150 | 0.7144 | 0.7133 | 0.6000 |

Before/after changes questions AND labels; differences are not a system improvement estimate.

All rankings and corpus fingerprints accompany this report.
