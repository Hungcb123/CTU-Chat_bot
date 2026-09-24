# Scenario 1–2: held-out evaluation protocol

## Dataset split

- `data/scenario12_dev.jsonl` contains the 150 existing development questions.
  `reference_answer` is copied from the CSV `Answer` column; `raw_evidence` is
  retained from `Ground Truth`; `Source` is normalized to canonical filenames.
- `data/scenario12_heldout.jsonl` contains 50 newly generated candidates from
  CTU Markdown documents and structured tuition records. The quota is 20 actual
  tuition, 6 academic rules, 5 scholarship, 4 student loan, 4 social support,
  4 other, 3 academic program, 2 exemption policy, and 2 exemption basis.
- All held-out records start with `review_status: pending`. They are not eligible
  for a final run until every checklist entry is approved.

## Author review

Review `data/scenario12_heldout_review.md`. For every case verify the question,
reference answer, required facts, evidence excerpt, and canonical source. Change
only the exact line `- [ ] Approved` to `- [x] Approved`, then apply it with:

```bash
wsl_venv/bin/python scripts/prepare_scenario12_datasets.py --apply-review
```

The runner rejects any held-out case whose JSON status is not `approved`. This is
an author-reviewed split; it is not independent annotation.

## Runner

```bash
# Retrieval smoke test (no Vertex generation)
wsl_venv/bin/python scripts/run_scenario12_experiment.py \
  --scenario 1 --split dev --limit 3 --repetitions 1 --workers 10 --fresh

# Development run: one repetition is useful for freezing the configuration.
wsl_venv/bin/python scripts/run_scenario12_experiment.py \
  --scenario all --split dev --workers 10 --repetitions 1 --fresh

# Final held-out run, only after author review is applied.
wsl_venv/bin/python scripts/run_scenario12_experiment.py \
  --scenario all --split heldout --workers 10 --repetitions 3 --fresh
```

`--resume` searches for a checkpoint with an exact signature over dataset,
retrieval code, prompts, judge rubric, Graph/catalog data, model, Ragas version,
cutoffs, and generation parameters. Changing the model or embedding backend
requires `--fresh`; old answers are not silently reused.

## Metrics and artifacts

Scenario 1 reports H@1, H@3, P@5, R@5, MRR@10, and retrieval latency. Scenario 2
uses Ragas 0.4 for AR, CR, CP, and AC, with source-level recall/AP and structured
fact exact match as diagnostics. Each UTC run directory under `logs/scenario12/`
contains `manifest.json`, `run.log`, `records.jsonl`, `summary.json`,
`comparison.md`, `failures.md`, and `checkpoint.json`.

Graph records include `source`, `source_section`, `source_table`, `backend`, and
`graph_hit`/`catalog_fallback` flags. A catalog fallback is never reported as a
Graph hit. The paper must be updated only from the approved held-out summary;
development numbers remain diagnostic.
