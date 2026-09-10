#!/usr/bin/env python3
"""Offline document BM25 diagnostic, NOT the production E1 or RAGAS.

Uses the entire local Markdown corpus, no API, no training, no gold at retrieval.
Emits every ranking and reports core/stress separately. Run after prepare script.
"""
import csv
import hashlib
import json
import math
import re
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report/Research/paper_v2'
OUT.mkdir(parents=True, exist_ok=True)
paths = sorted((ROOT / 'data/markdown').glob('*.md'))
documents = [p.read_text(encoding='utf-8') for p in paths]
counts = [Counter(re.findall(r'\w+', unicodedata.normalize('NFC', d).lower())) for d in documents]
lengths = [sum(c.values()) for c in counts]
average_length = sum(lengths) / len(lengths)
df = Counter(term for c in counts for term in c)
postings = defaultdict(list)
for i, c in enumerate(counts):
    for term, tf in c.items():
        postings[term].append((i, tf))
meta = {r['id']: r for r in map(json.loads, (ROOT / 'data/paper_v2/records.jsonl').read_text().splitlines())}
results, summaries = [], {}
for version, dataset in [('original', ROOT / 'data/150_NATURAL_NO_APPENDIX.csv'),
                         ('revised', ROOT / 'data/paper_v2/150_revised.csv')]:
    rows = list(csv.DictReader(dataset.open(encoding='utf-8-sig')))
    version_results = []
    for r in rows:
        start = time.perf_counter()
        query_tokens = set(re.findall(r'\w+', unicodedata.normalize('NFC', r['Master Question']).lower()))
        scores = defaultdict(float)
        for term in query_tokens:
            idf = math.log(1 + (len(paths) - df[term] + 0.5) / (df[term] + 0.5))
            for i, tf in postings[term]:
                scores[i] += idf * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75 * lengths[i] / average_length))
        ranking = sorted(scores, key=lambda i: (-scores[i], paths[i].name))[:10]
        retrieved = [paths[i].name for i in ranking]
        latency = (time.perf_counter() - start) * 1000
        gold = set(s.strip() for s in r['Source'].split(';') if s.strip())
        relation = r['source_relation']
        hits = [i for i, s in enumerate(retrieved[:5], 1) if s in gold]
        all_hits = [i for i, s in enumerate(retrieved, 1) if s in gold]
        # Conventional set-based document metrics and separately named evidence
        # sufficiency. any_valid must not require retrieving every alternative.
        metrics = {
            'hit_at_1': float(bool(all_hits) and all_hits[0] == 1),
            'hit_at_3': float(bool(all_hits) and all_hits[0] <= 3),
            'precision_at_5': len(hits) / 5,
            'source_recall_at_5': len(hits) / len(gold),
            'ap_at_5': sum(j / rank for j, rank in enumerate(hits, 1)) / min(len(gold), 5),
            'mrr_at_10': 1 / all_hits[0] if all_hits else 0.0,
            'evidence_sufficiency_at_5': float(bool(hits)) if relation == 'any_valid' else float(len(hits) == len(gold)),
        }
        item = {'version': version, 'id': r['Original ID'],
                'subset': meta[r['Original ID']]['subset'], 'category': r['Category'],
                'family_id': meta[r['Original ID']]['family_id'],
                'gold_sources': sorted(gold), 'source_relation': relation,
                'retrieved_sources': retrieved, 'scores': [scores[i] for i in ranking],
                'metrics': metrics, 'latency_ms': latency}
        results.append(item)
        version_results.append(item)
    grouped = defaultdict(list)
    for item in version_results:
        grouped['all_150'].append(item)
        grouped[item['subset']].append(item)
        grouped['category:' + item['category']].append(item)
        grouped['family:' + item['family_id']].append(item)
    summaries[version] = {}
    for group, items in grouped.items():
        summaries[version][group] = {'n': len(items), **{
            key: sum(i['metrics'][key] for i in items) / len(items) for key in metrics}}
    for subset in ['core_100', 'synthetic_stress_50']:
        items = grouped[subset]
        cats = sorted({i['category'] for i in items})
        summaries[version][subset]['category_macro_mrr'] = sum(
            sum(i['metrics']['mrr_at_10'] for i in items if i['category'] == cat)
            / sum(i['category'] == cat for i in items) for cat in cats) / len(cats)

payload = {
    'experiment': 'offline_full_document_bm25_diagnostic',
    'publication_status': 'development_only_unreviewed_labels',
    'not_comparable_to_production_table3': True,
    'bm25': {'k1': 1.5, 'b': 0.75, 'tokenizer': 'NFC lowercase Unicode word; no Vietnamese segmentation'},
    'corpus_document_count': len(paths),
    'corpus_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    'dataset_sha256': {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in
                       [('original', ROOT / 'data/150_NATURAL_NO_APPENDIX.csv'),
                        ('revised', ROOT / 'data/paper_v2/150_revised.csv')]},
    'summaries': summaries,
    'caveat': 'Before/after changes questions AND labels; differences are not a system improvement estimate.',
}
(OUT / 'offline_bm25_results.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
(OUT / 'offline_bm25_rankings.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in results))
lines = ['# Offline BM25 diagnostic', '',
         'Development labels; full-document local BM25, not production E1 or RAGAS.', '',
         '| Version | Subset | n | MRR@10 | Source R@5 | Evidence sufficiency@5 |',
         '|---|---|---:|---:|---:|---:|']
for version in summaries:
    for subset in ['core_100', 'synthetic_stress_50', 'all_150']:
        m = summaries[version][subset]
        lines.append(f"| {version} | {subset} | {m['n']} | {m['mrr_at_10']:.4f} | {m['source_recall_at_5']:.4f} | {m['evidence_sufficiency_at_5']:.4f} |")
lines += ['', payload['caveat'], '', 'All rankings and corpus fingerprints accompany this report.']
(OUT / 'offline_bm25_report.md').write_text('\n'.join(lines) + '\n')
assert len(results) == 300
assert all(0 <= value <= 1 for r in results for value in r['metrics'].values())
assert all(len(r['retrieved_sources']) == len(set(r['retrieved_sources'])) for r in results)
print('\n'.join(lines))
