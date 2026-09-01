#!/usr/bin/env python3
"""Remove orphan entries from document_metadata.json (handles nested 'documents' key)"""
import json, os

meta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'document_metadata.json'))
md_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'markdown'))

with open(meta_path, 'r', encoding='utf-8') as f:
    raw = json.load(f)

# Handle nested structure: {"schema_version": 1, "documents": {...}}
if "documents" in raw and isinstance(raw["documents"], dict):
    data = raw["documents"]
    nested = True
else:
    data = raw
    nested = False

existing_files = set(os.listdir(md_dir))
print(f'Metadata entries: {len(data)}')
print(f'Markdown files:   {len(existing_files)}')

cleaned = {k: v for k, v in data.items() if k in existing_files}
removed = len(data) - len(cleaned)
print(f'After cleanup:    {len(cleaned)}')
print(f'Removed orphans:  {removed}')

if nested:
    raw["documents"] = cleaned
    output = raw
else:
    output = cleaned

with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print('Done! Saved cleaned metadata.')
