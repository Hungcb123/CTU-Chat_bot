# FINAL NUMERICAL AUDIT — Table 4 Top-7 rerun

**Date:** 2026-09-11  
**Dataset:** `data/150_NATURAL_NO_APPENDIX.csv`  
**Dataset SHA-256:** `53b10c3ad4ad1426753b1de777eb1b8d49b610101b03401b25ff209fbb5195cb`  
**Model:** `gemini-2.5-flash-lite`  
**Top-K:** 7 for retrieval, reranking, CR and CP  
**Prompt version:** `graph_context_top7_v1`  
**Configurations:** T1–T7  
**Evaluation size:** 150 questions × 7 configurations = 1,050 generations and 1,050 judge calls  
**Workers:** 5

## Table 4 cross-check

| Config. | AR | CR (Top-7) | CP (Top-7) | AC | n |
|---|---:|---:|---:|---:|---:|
| T1 | 0.737 | 0.790 | 0.653 | 0.596 | 150 |
| T2 | 0.580 | 0.583 | 0.415 | 0.482 | 150 |
| T3 | 0.730 | 0.758 | 0.531 | 0.600 | 150 |
| T4 | 0.781 | 0.795 | 0.722 | 0.647 | 150 |
| T5 | 0.723 | 0.758 | 0.531 | 0.612 | 150 |
| T6 | 0.750 | 0.798 | 0.739 | 0.642 | 150 |
| T7 | 0.579 | 0.583 | 0.415 | 0.482 | 150 |

All seven rows in `04-experiments.tex` and `table4_e2e_table.tex` match `table4_e2e_results.json`. T4 has the highest AC; T6 has the highest CR/CP. No claim that T4 dominates every metric is made.

## Pipeline and consistency checks

- Checkpoint signature includes dataset hash, model, Top-K, prompt version, and configuration list; the prior Top-5 checkpoint is rejected.
- The generation prompt uses partial supported context and refuses only when no relevant context exists.
- Graph tuition/policy context is injected with actual returned fields; catalog fallback is explicitly labeled and is not counted as a Graph hit.
- The current result JSON does not persist per-case Graph-hit/fallback counters, so no Graph-hit rate is asserted here.
- `TOP_K=7` is used consistently in the upgraded Table 4 runner and its CR/CP cutoff.
