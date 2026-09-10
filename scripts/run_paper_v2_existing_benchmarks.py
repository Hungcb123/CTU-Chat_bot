#!/usr/bin/env python3
"""Run existing benchmarks in an isolated output directory; retain legacy caveats."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / 'tests/outputpaper' / ('paper_v2_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
OUT.mkdir(parents=True, exist_ok=False)
DATASET = ROOT / 'data/paper_v2/150_revised.csv'
manifest = {
    'status': 'running', 'output_directory': str(OUT),
    'dataset': str(DATASET), 'dataset_sha256': hashlib.sha256(DATASET.read_bytes()).hexdigest(),
    'model': 'gemini-3.5-flash-lite', 'delay_seconds': 6.0,
    'retrieval_n': 150, 'generation_n': 25,
    'caveats': ['Exploratory legacy benchmark, not publication-ready RAGAS.',
                'Table 4 AR/AC/CR/CP are legacy heuristic proxies.',
                'T7 duplicates T2; T5 removes graph as well as reranker.',
                'Sampling is first-per-category, not randomized.',
                'Legacy generator returns fallback text after exhausted retries; inspect log.',
                'Dataset remains development data pending independent review.'],
    'scripts_sha256': {name: hashlib.sha256((ROOT / 'scripts' / name).read_bytes()).hexdigest()
                       for name in ['benchmark_table4_e2e.py', 'benchmark_table3_upgraded.py']},
}
print('OUTPUT_DIRECTORY=' + str(OUT), flush=True)
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
try:
    from scripts import benchmark_table4_e2e as table4
    table4.OUTPUT_JSON = OUT / 'table4_legacy_proxy_results.json'
    table4.OUTPUT_TEX = OUT / 'table4_legacy_proxy_table.tex'
    table4.CHECKPOINT_FILE = OUT / 'table4_checkpoint.json'
    table4.LLM_DELAY_SECONDS = 6.0
    from langchain_google_genai import ChatGoogleGenerativeAI
    smoke = ChatGoogleGenerativeAI(model=manifest['model'], temperature=0.0,
                                  max_output_tokens=16, max_retries=0, timeout=60)
    response = smoke.invoke('Reply with exactly OK.')
    if not response.content:
        raise RuntimeError('API smoke test returned empty content')
    print('API_SMOKE_OK', flush=True)
    manifest['api_smoke'] = 'passed'
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    table4.run_table4_benchmark(DATASET, limit_e2e=25)
    manifest['table4'] = 'completed'
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    from scripts import benchmark_table3_upgraded as table3
    table3.OUTPUT_JSON = OUT / 'table3_results.json'
    table3.OUTPUT_TEX = OUT / 'table3_table.tex'
    table3.run_benchmark(DATASET)
    manifest['table3'] = 'completed'
    manifest['status'] = 'completed'
except BaseException as exc:
    manifest['status'] = 'failed'
    manifest['error_type'] = type(exc).__name__
    raise
finally:
    manifest['finished_at'] = datetime.now(timezone.utc).isoformat()
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
