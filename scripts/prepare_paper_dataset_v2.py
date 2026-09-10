#!/usr/bin/env python3
"""Build an auditable development dataset; never overwrite the original or corpus.

Run: python3 scripts/prepare_paper_dataset_v2.py
All records remain pending independent human review. Original reference excerpts
are preserved separately from concise reference answers, not silently discarded.
"""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/paper_v2'
OUT.mkdir(parents=True, exist_ok=True)
original_path = ROOT / 'data/150_NATURAL_NO_APPENDIX.csv'
original_bytes = original_path.read_bytes()
original = list(csv.DictReader(original_bytes.decode('utf-8-sig').splitlines(keepends=True)))
patches = json.loads((OUT / 'corrections.json').read_text())
assert len(original) == 150
assert len({r['Original ID'] for r in original}) == 150
assert set(patches) <= {r['Original ID'] for r in original}
records, revised, changes, source_manifest = [], [], [], {}

for old in original:
    r = {k: v.strip() for k, v in old.items()}
    cid = r['Original ID']
    reasons = []
    if cid in patches:
        r.update(patches[cid])
        reasons.append('Explicit source/scope/unit correction; see corrections.json')
    q = r['Master Question']
    cat = r['Category']
    synthetic = cid.startswith('CDICT')
    sources = [s.strip() for s in r['Source'].split(';') if s.strip()]
    flags = []
    scope = 'corpus_snapshot_only'
    if cat == 'actual_tuition' and not re.search(r'2026\s*[-–]\s*2027', q):
        q = 'Trong năm học 2026-2027, ' + q[0].lower() + q[1:]
        reasons.append('Make fee academic year explicit')
    if cat == 'exemption_basis':
        q = 'Trong năm học 2025-2026, ' + q[0].lower() + q[1:]
        reasons.append('Distinguish historical exemption basis from actual tuition')
    if cid in {'30', '31', '33', '38', '39'}:
        q = q.rstrip('?') + ' (chương trình chuẩn, khối đại cương ngành/cơ sở ngành/chuyên ngành)?'
        reasons.append('Specify fee block and program instead of conflating all credits')
    if cid == '37':
        q = q.rstrip('?') + ' (chương trình chuẩn)?'
    if cid in {'79', '80'}:
        q = 'Trong học kỳ 1 năm học 2025-2026, ' + q[0].lower() + q[1:]
        reasons.append('Scope scholarship amount to source period')
    if cid == '81':
        q = 'Từ học kỳ 2 năm học 2025-2026, ' + q[0].lower() + q[1:]
        reasons.append('Use the explicit K51 effective semester in the source table')
    if cid in {'82', '83', '84', '85', '86'}:
        q = 'Trong đợt học bổng năm 2026, ' + q[0].lower() + q[1:]
        reasons.append('Scope annual scholarship announcement')
    if cid in {'87', '88', '89'}:
        q = 'Trong năm học 2025-2026, ' + q[0].lower() + q[1:]
        reasons.append('Scope SCC announcement')
    if cid in {'51', '52', '53', '54', '55'}:
        q = 'Theo chính sách mua thiết bị học trực tuyến ban hành năm 2022, ' + q[0].lower() + q[1:]
        scope = 'historical_policy_2022'
        reasons.append('Historical document QA; no claim that applications remain open')

    # These are controlled cross-document tasks, not evidence that a 2025
    # curriculum actually applied to an older intake. Preserve that distinction.
    if synthetic:
        n = int(cid[5:])
        if n <= 22 or 31 <= n <= 46:
            q = 'Giả sử dùng CTĐT 2025 để đối chiếu: ' + q
            scope = 'hypothetical_curriculum_fee_join'
            reasons.append('Remove unsupported historical cohort/curriculum applicability claim')
        if 23 <= n <= 30:
            q = 'Theo quy định học vụ ban hành năm 2024, ' + q[0].lower() + q[1:]
        if 47 <= n <= 50:
            q = ('Đối chiếu CTĐT ban hành năm 2025 với quy định học vụ năm 2024; '
                 'giả sử sinh viên không có tín chỉ được công nhận/chuyển đổi làm giảm thời hạn học. ' + q)
            reasons.append('State no-transfer-credit assumption for maximum study duration')
        family = ('curriculum_annual_fee' if n <= 12 else
                  'curriculum_credit_fee' if n <= 22 else
                  'credit_cap_calculation' if n <= 30 else
                  'course_fee_calculation' if n <= 40 else
                  'standard_clc_comparison' if n <= 46 else 'maximum_study_duration')
        flags.append('synthetic_template_family_not_independent_natural_queries')
    else:
        family = 'source_' + hashlib.sha256('|'.join(sorted(sources)).encode()).hexdigest()[:12]
    if cid == 'Q023':
        q = ('Theo quy định học vụ năm 2024, với sinh viên không có tín chỉ được '
             'công nhận/chuyển đổi làm giảm thời hạn học, ' + q[0].lower() + q[1:])

    answer = r['Answer']
    # UI citations and greetings are not factual answer criteria.
    answer = re.split(r'\n---\s*\n', answer)[0].strip()
    if answer.startswith('Chào bạn,') and '\n\n' in answer:
        answer = answer.split('\n\n', 1)[1].strip()
    if synthetic and 41 <= int(cid[5:]) <= 46:
        answer = 'Chương trình CLC nhiều hơn chương trình chuẩn 7 tín chỉ. ' + answer
        reasons.append('Answer the requested credit difference explicitly')
    if synthetic and int(cid[5:]) <= 22:
        answer = 'Theo giả định đối chiếu CTĐT 2025: ' + answer
    r['Master Question'] = q
    r['Answer'] = answer
    r['Ground Truth'] = answer
    reasons.append('Canonical concise answer; preserve original evidence in records.jsonl')
    assert r['source_relation'] in {'single', 'all_required', 'any_valid'}
    assert len(sources) == len(set(sources))
    assert (len(sources) == 1) == (r['source_relation'] == 'single')
    evidence = []
    for source in sources:
        p = ROOT / 'data/markdown' / source
        assert p.is_file(), (cid, source)
        content = p.read_bytes()
        source_manifest[source] = hashlib.sha256(content).hexdigest()
        evidence.append({'source': source, 'sha256': source_manifest[source]})
    if cat in {'exemption_policy', 'social_support'}:
        flags.append('policy_effective_scope_requires_review')
    if cid in {'85', '86'}:
        flags.append('Panasonic_source_heading_2025_conflicts_with_body_2026')
    if r['source_relation'] == 'any_valid':
        flags.append('confirm_each_alternative_independently_supports_answer')
    records.append({
        'id': cid, 'question': q, 'reference_answer': answer, 'category': cat,
        'sources': sources, 'source_relation': r['source_relation'],
        'source_fingerprints': evidence, 'scope': scope,
        'subset': 'synthetic_stress_50' if synthetic else 'core_100',
        'family_id': family, 'split': 'development',
        'review_status': 'pending_independent_human_review', 'review_flags': flags,
        'original_question': old['Master Question'],
        'original_reference_excerpt': old['Ground Truth'],
        'original_answer': old['Answer'],
    })
    revised.append(r)
    for field in old:
        if old[field] != r[field]:
            changes.append({'id': cid, 'field': field, 'before': old[field],
                            'after': r[field], 'reasons': reasons})

for name, pool in [('150_revised.csv', revised),
                   ('core_100.csv', revised[:100]), ('synthetic_stress_50.csv', revised[100:])]:
    if name == 'core_100.csv':
        pool = [r for r in revised if not r['Original ID'].startswith('CDICT')]
    elif name == 'synthetic_stress_50.csv':
        pool = [r for r in revised if r['Original ID'].startswith('CDICT')]
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(original[0]))
        writer.writeheader()
        writer.writerows(pool)
(OUT / 'records.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records))
(OUT / 'change_log.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2) + '\n')
manifest = {
    'version': 2, 'status': 'development_not_publication_ready',
    'original_sha256': hashlib.sha256(original_bytes).hexdigest(),
    'dataset_sha256': hashlib.sha256((OUT / '150_revised.csv').read_bytes()).hexdigest(),
    'builder_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'corrections_sha256': hashlib.sha256((OUT / 'corrections.json').read_bytes()).hexdigest(),
    'rows': len(records), 'changed_rows': len({c['id'] for c in changes}),
    'field_changes': len(changes), 'categories': dict(Counter(r['category'] for r in records)),
    'subsets': dict(Counter(r['subset'] for r in records)),
    'review_flags': dict(Counter(flag for r in records for flag in r['review_flags'])),
    'corpus_source_sha256': source_manifest,
    'human_verified_rows': 0, 'held_out_test_rows': 0,
}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
assert original_path.read_bytes() == original_bytes
print(json.dumps({k: v for k, v in manifest.items() if k != 'corpus_source_sha256'}, ensure_ascii=False, indent=2))
