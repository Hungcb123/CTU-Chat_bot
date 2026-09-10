#!/usr/bin/env python3
"""Summarize an existing benchmark run without changing its measurements."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
folder = Path(sys.argv[1])
manifest = json.loads((folder / 'manifest.json').read_text())
lines = ['# Kết quả chạy thực nghiệm CSV v2', '',
         f"Trạng thái: {manifest['status']}. Dataset SHA-256: `{manifest['dataset_sha256']}`.", '',
         '**Đây là kết quả exploratory của script hiện có, không phải RAGAS chính thức.**', '',
         '## Table 4 — các chỉ số proxy của script cũ', '',
         '| Cấu hình | AR proxy | CR token | CP heuristic | AC proxy | n retrieval | n QA |',
         '|---|---:|---:|---:|---:|---:|---:|']
t4 = folder / 'table4_legacy_proxy_results.json'
if t4.exists():
    d = json.loads(t4.read_text())
    for code, m in d['metrics'].items():
        lines.append(f"| {code} | {m['AR']:.3f} | {m['CR']:.3f} | {m['CP']:.3f} | {m['AC']:.3f} | {m['n_cr_cp']} | {m['n_ar_ac']} |")
else:
    lines += ['', 'Chưa có bảng Table 4 hoàn tất.']
t3 = folder / 'table3_results.json'
if t3.exists():
    lines += ['', '## Table 3 — truy xuất', '',
              '| Cấu hình | H@1 | H@3 | P@5 | R@5 | MRR@10 | Latency ms |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for code, m in json.loads(t3.read_text())['results'].items():
        lines.append(f"| {code} | {m['hit_at_1']:.4f} | {m['hit_at_3']:.4f} | {m['precision_at_5']:.4f} | {m['recall_at_5']:.4f} | {m['mrr_at_10']:.4f} | {m['latency_ms']:.2f} |")
checkpoint = folder / 'table4_checkpoint.json'
if checkpoint.exists():
    cp = json.loads(checkpoint.read_text())
    fallback = [(cid, code) for cid, configs in cp.get('answers', {}).items()
                for code, answer in configs.items()
                if answer == 'Không tìm thấy thông tin phù hợp trong ngữ cảnh.']
    lines += ['', '## Độ đầy đủ và giới hạn', '',
              f"- Checkpoint truy xuất: {len(cp.get('cr_cp', {}))} câu.",
              f"- Checkpoint đáp án: {len(cp.get('answers', {}))} câu.",
              f'- Đáp án trùng chuỗi fallback của script: {len(fallback)}. Phải đối chiếu log để phân biệt lỗi API và câu trả lời thật.']
    meta = {r['id']: r for r in map(json.loads, (ROOT / 'data/paper_v2/records.jsonl').read_text().splitlines())}
    ids = list(cp.get('answers', {}))
    lines += [f"- Số câu stress trong mẫu QA: {sum(meta[cid]['subset'] == 'synthetic_stress_50' for cid in ids)}.",
              '- ID mẫu QA: ' + ', '.join(ids) + '.']
lines += ['', *['- ' + c for c in manifest['caveats']], '',
          'Không so trực tiếp mức tăng/giảm với bảng cũ khi dataset và nhãn đã thay đổi. '
          'Các bảng này không chứng minh T4 là full agent pipeline hoặc T7 cô lập Governance.']
(folder / 'results_report.md').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
