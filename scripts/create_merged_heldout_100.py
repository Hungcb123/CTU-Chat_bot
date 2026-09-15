#!/usr/bin/env python3
"""Merge 50 Formal Heldout cases and 50 Semantic Heldout cases into a single 100-case dataset.

Output: data/scenario12_heldout_100.jsonl
All 100 cases have unique IDs and review_status="approved".
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMAL_PATH = ROOT / "data" / "scenario12_heldout.jsonl"
SEMANTIC_PATH = ROOT / "data" / "scenario12_heldout_semantic.jsonl"
MERGED_PATH = ROOT / "data" / "scenario12_heldout_100.jsonl"


def main() -> None:
    with open(FORMAL_PATH, "r", encoding="utf-8") as f:
        formal_cases = [json.loads(line) for line in f if line.strip()]

    with open(SEMANTIC_PATH, "r", encoding="utf-8") as f:
        semantic_cases = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(formal_cases)} formal cases and {len(semantic_cases)} semantic cases.")

    merged_cases = []

    # Formal cases: keep original id or prefix with HOUT-FORMAL-
    for case in formal_cases:
        item = dict(case)
        item["subset"] = "formal"
        item["review_status"] = "approved"
        merged_cases.append(item)

    # Semantic cases: prefix ID with SEM- to prevent collisions in checkpoint
    for case in semantic_cases:
        item = dict(case)
        orig_id = item["id"]
        item["id"] = f"SEM-{orig_id}"
        item["subset"] = "semantic"
        item["review_status"] = "approved"
        merged_cases.append(item)

    assert len(merged_cases) == 100, f"Expected 100 cases, got {len(merged_cases)}"
    unique_ids = {c["id"] for c in merged_cases}
    assert len(unique_ids) == 100, f"IDs are not unique: {len(unique_ids)} unique out of 100"

    with open(MERGED_PATH, "w", encoding="utf-8") as f:
        for case in merged_cases:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

    print(f"Successfully wrote {len(merged_cases)} cases to {MERGED_PATH}")


if __name__ == "__main__":
    main()
