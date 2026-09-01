#!/usr/bin/env python3
import json
import os
import sys

meta_path = sys.argv[1]

with open(meta_path, 'r', encoding='utf-8') as f:
    raw = json.load(f)

data = raw.get("documents", raw)
nested = "documents" in raw

domain_mapping = {
    'quy_che_general': 'academic_regulation',
    'academic_rules': 'academic_regulation',
    'exemption_policy': 'tuition',
    'exemption_basis': 'tuition',
    'actual_tuition': 'tuition',
    'hoc_vu': 'academic_regulation',
    'hhoc_vu': 'academic_regulation',
    'dao_tao': 'academic_program'
}

valid_domains = {
    'tuition', 'scholarship', 'student_loan', 'social_support',
    'academic_program', 'academic_regulation', 'other'
}

fixed_count = 0
for doc_key, meta in data.items():
    domain = meta.get('domain', '')
    if domain not in valid_domains:
        new_domain = domain_mapping.get(domain, 'other')
        meta['domain'] = new_domain
        fixed_count += 1
        print(f"Fixed {doc_key}: {domain} -> {new_domain}")

if nested:
    raw["documents"] = data
    output = raw
else:
    output = data

with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nFixed {fixed_count} domain metadata entries.")
