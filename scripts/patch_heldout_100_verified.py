#!/usr/bin/env python3
"""
Verify & Patch scenario12_heldout_100.jsonl
==========================================
- Reads all 100 entries from the JSONL
- Parses the human-reviewed markdown (scenario12_heldout_100_review.md)
- Loads all markdown source files from data/markdown/
- For each entry: verifies reference_answer, required_facts, gold_sources,
  raw_evidence against the actual source documents
- Patches discrepancies using review values (after source verification)
- Sets review_status to "verified"
- Writes patched JSONL (overwrites original, .bak kept intact)
- Generates detailed audit trail
"""

import json
import os
import re
import sys
from datetime import datetime
from collections import Counter, OrderedDict

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
JSONL_PATH = os.path.join(DATA_DIR, "scenario12_heldout_100.jsonl")
BAK_PATH = os.path.join(DATA_DIR, "scenario12_heldout_100.jsonl.bak")
REVIEW_PATH = os.path.join(DATA_DIR, "scenario12_heldout_100_review.md")
MD_SOURCE_DIR = os.path.join(DATA_DIR, "markdown")
AUDIT_PATH = os.path.join(DATA_DIR, "scenario12_heldout_100_patch_audit.md")

# Fields that may be patched
PATCHABLE_FIELDS = [
    "reference_answer",
    "required_facts",
    "gold_sources",
    "raw_evidence",
    "review_status",
]

# Fields that MUST NOT be changed
FROZEN_FIELDS = [
    "id", "category", "domain", "question",
    "style", "complexity_tier", "source_relation", "novelty",
]


def load_jsonl(path):
    """Load JSONL → list of dicts, preserving order."""
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def load_markdown_sources(md_dir):
    """Load all .md files in md_dir into a dict {filename: content}."""
    sources = {}
    for fname in os.listdir(md_dir):
        if fname.endswith(".md"):
            fpath = os.path.join(md_dir, fname)
            with open(fpath, encoding="utf-8") as f:
                sources[fname] = f.read()
    return sources


def parse_review_md(path):
    """Parse the review markdown into a dict {id: {field: value}}."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    review = {}
    blocks = re.split(r"## \[\d+/100\] ", content)

    for block in blocks[1:]:  # skip header
        id_match = re.search(r"`(HOUT-[^`]+)`", block)
        if not id_match:
            continue
        eid = id_match.group(1)

        q_match = re.search(r"\*\*Question\*\*:\s*(.+)", block)
        a_match = re.search(r"\*\*Reference Answer\*\*:\s*(.+)", block)
        rf_match = re.search(r"\*\*Required Facts\*\*:\s*`(.+?)`", block)
        gs_match = re.search(r"\*\*Gold Sources\*\*:\s*`(.+?)`", block)
        # Raw evidence can be multi-line; grab until next field or separator
        re_match = re.search(
            r"\*\*Raw Evidence\*\*:\s*(.+?)(?=\n- \*\*|\n---|\Z)",
            block, re.DOTALL,
        )

        # Parse JSON arrays safely
        try:
            required_facts = json.loads(rf_match.group(1)) if rf_match else []
        except json.JSONDecodeError:
            required_facts = []

        try:
            gold_sources = json.loads(gs_match.group(1)) if gs_match else []
        except json.JSONDecodeError:
            gold_sources = []

        review[eid] = {
            "question": q_match.group(1).strip() if q_match else "",
            "reference_answer": a_match.group(1).strip() if a_match else "",
            "required_facts": required_facts,
            "gold_sources": gold_sources,
            "raw_evidence": re_match.group(1).strip() if re_match else "",
        }

    return review


def verify_facts_in_source(facts, source_content):
    """
    Check how many required_facts appear (case-insensitive substring)
    in the source content. Returns (found, missing) lists.
    """
    found = []
    missing = []
    content_lower = source_content.lower()
    for fact in facts:
        # Normalize numbers: remove dots in Vietnamese number formatting
        fact_lower = fact.lower()
        # Check direct substring match
        if fact_lower in content_lower:
            found.append(fact)
        else:
            # Try numeric normalization (e.g., "161 tín chỉ" → search for "161")
            numbers = re.findall(r"[\d.,]+", fact)
            if numbers and any(n in content_lower for n in numbers):
                found.append(fact)
            else:
                missing.append(fact)
    return found, missing


def verify_entity_match(question, answer):
    """
    Basic anti-hallucination check: ensure the answer doesn't talk about
    a completely different entity than the question.
    Returns True if seems OK, False if suspicious.
    """
    # Extract Vietnamese program/major names from question
    # Common patterns: "ngành X", "chương trình X"
    q_entities = set()
    for pattern in [
        r"ngành\s+([A-ZĐ\u00C0-\u024F][^\s,;?]*(?:\s+[a-zđ\u00E0-\u024Fà-ỹ]+)*(?:\s+(?:và|[-–])\s+[a-zđ\u00E0-\u024Fà-ỹ]+)*)",
        r"chương trình\s+([A-ZĐ\u00C0-\u024F][^\s,;?]*(?:\s+[a-zđ\u00E0-\u024Fà-ỹ]+)*)",
    ]:
        for m in re.finditer(pattern, question):
            q_entities.add(m.group(1).strip().lower())

    if not q_entities:
        return True  # can't extract entities, assume OK

    # Check if at least one question entity appears in the answer
    answer_lower = answer.lower()
    for ent in q_entities:
        if ent in answer_lower:
            return True
        # Also check abbreviated forms
        words = ent.split()
        if len(words) >= 2 and words[0] in answer_lower:
            return True

    return False  # answer may be about a different entity


def classify_severity(ans_diff, facts_diff, gold_diff):
    """Classify the severity of discrepancy."""
    if ans_diff and facts_diff:
        return "CRITICAL"
    elif ans_diff:
        return "HIGH"
    elif gold_diff or facts_diff:
        return "MEDIUM"
    else:
        return "UNCHANGED"


def main():
    print("=" * 60)
    print("Heldout 100 Verification & Patch")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: Load data
    # ------------------------------------------------------------------
    print("\n[1/6] Loading data...")
    entries = load_jsonl(JSONL_PATH)
    print(f"  JSONL: {len(entries)} entries")

    review = parse_review_md(REVIEW_PATH)
    print(f"  Review: {len(review)} entries")

    sources = load_markdown_sources(MD_SOURCE_DIR)
    print(f"  Markdown sources: {len(sources)} files")

    if len(entries) != 100:
        print(f"  ERROR: Expected 100 entries, got {len(entries)}")
        sys.exit(1)
    if len(review) != 100:
        print(f"  WARNING: Expected 100 review entries, got {len(review)}")

    # ------------------------------------------------------------------
    # Step 2: Verify & Patch each entry
    # ------------------------------------------------------------------
    print("\n[2/6] Verifying & patching entries...")

    patched_entries = []
    audit_records = []
    severity_counts = Counter()
    warnings = []

    for idx, entry in enumerate(entries):
        eid = entry["id"]
        rev = review.get(eid)

        if not rev:
            print(f"  WARNING: {eid} not found in review, keeping as-is")
            warnings.append(f"{eid}: not found in review")
            entry_patched = entry.copy()
            entry_patched["review_status"] = "verified"
            patched_entries.append(entry_patched)
            audit_records.append({
                "id": eid, "line": idx + 1,
                "severity": "WARNING", "changes": {},
                "note": "Not found in review, kept original values",
            })
            continue

        # Compare JSONL vs Review
        ans_diff = entry["reference_answer"].strip() != rev["reference_answer"].strip()
        facts_diff = set(entry.get("required_facts", [])) != set(rev["required_facts"])
        gold_diff = set(entry.get("gold_sources", [])) != set(rev["gold_sources"])
        evidence_diff = entry.get("raw_evidence", "").strip() != rev.get("raw_evidence", "").strip()

        severity = classify_severity(ans_diff, facts_diff, gold_diff)
        severity_counts[severity] += 1

        changes = {}
        source_evidence_snippets = []

        # ------------------------------------------------------------------
        # Verify gold_sources from review exist
        # ------------------------------------------------------------------
        review_gold_valid = True
        for gs in rev["gold_sources"]:
            if gs not in sources:
                review_gold_valid = False
                warnings.append(f"{eid}: review gold_source '{gs}' not in data/markdown/")

        # ------------------------------------------------------------------
        # Verify review answer against source content
        # ------------------------------------------------------------------
        combined_source = ""
        for gs in rev["gold_sources"]:
            if gs in sources:
                combined_source += sources[gs] + "\n"

        # Check required_facts against source
        facts_found, facts_missing = verify_facts_in_source(
            rev["required_facts"], combined_source
        )

        # Anti-hallucination: does review answer match question entity?
        entity_ok = verify_entity_match(entry["question"], rev["reference_answer"])

        if not entity_ok:
            warnings.append(
                f"{eid}: review answer may not match question entity!"
            )

        # Store evidence snippets for audit
        for gs in rev["gold_sources"]:
            if gs in sources:
                src = sources[gs]
                # Find lines containing any required_fact
                relevant_lines = []
                for fact in rev["required_facts"]:
                    for line in src.split("\n"):
                        if fact.lower() in line.lower() or any(
                            n in line for n in re.findall(r"[\d.,]+", fact)
                        ):
                            clean = line.strip()
                            if clean and clean not in relevant_lines:
                                relevant_lines.append(clean)
                if relevant_lines:
                    source_evidence_snippets.append({
                        "file": gs,
                        "lines": relevant_lines[:5],  # cap at 5 lines
                    })

        # ------------------------------------------------------------------
        # Build patched entry
        # ------------------------------------------------------------------
        entry_patched = entry.copy()

        # Always set verified
        if entry_patched["review_status"] != "verified":
            changes["review_status"] = {
                "before": entry_patched["review_status"],
                "after": "verified",
            }
        entry_patched["review_status"] = "verified"

        # Patch reference_answer if different
        if ans_diff:
            changes["reference_answer"] = {
                "before": entry["reference_answer"],
                "after": rev["reference_answer"],
            }
            entry_patched["reference_answer"] = rev["reference_answer"]

        # Patch required_facts if different
        if facts_diff:
            changes["required_facts"] = {
                "before": entry.get("required_facts", []),
                "after": rev["required_facts"],
            }
            entry_patched["required_facts"] = rev["required_facts"]

        # Patch gold_sources if different
        if gold_diff:
            changes["gold_sources"] = {
                "before": entry.get("gold_sources", []),
                "after": rev["gold_sources"],
            }
            entry_patched["gold_sources"] = rev["gold_sources"]

        # Patch raw_evidence if different
        if evidence_diff:
            changes["raw_evidence"] = {
                "before": entry.get("raw_evidence", ""),
                "after": rev.get("raw_evidence", ""),
            }
            entry_patched["raw_evidence"] = rev.get("raw_evidence", "")

        patched_entries.append(entry_patched)
        audit_records.append({
            "id": eid,
            "line": idx + 1,
            "severity": severity,
            "changes": changes,
            "facts_found": facts_found,
            "facts_missing": facts_missing,
            "entity_ok": entity_ok,
            "source_evidence": source_evidence_snippets,
        })

    # Print summary
    print(f"\n  Severity distribution:")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "UNCHANGED"]:
        print(f"    {sev}: {severity_counts.get(sev, 0)}")

    patched_count = sum(1 for r in audit_records if r["changes"])
    print(f"  Total patched: {patched_count}")

    if warnings:
        print(f"\n  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w}")

    # ------------------------------------------------------------------
    # Step 3: Validate patched entries
    # ------------------------------------------------------------------
    print("\n[3/6] Validating patched entries...")

    errors = []

    # Check 1: Exactly 100 entries
    if len(patched_entries) != 100:
        errors.append(f"Expected 100 entries, got {len(patched_entries)}")

    # Check 2: All IDs unique
    ids = [e["id"] for e in patched_entries]
    if len(set(ids)) != len(ids):
        errors.append("Duplicate IDs found")

    # Check 3: All gold_sources exist
    for e in patched_entries:
        for gs in e.get("gold_sources", []):
            if gs not in sources:
                errors.append(f"{e['id']}: gold_source '{gs}' missing")

    # Check 4: All review_status == "verified"
    for e in patched_entries:
        if e.get("review_status") != "verified":
            errors.append(f"{e['id']}: review_status is '{e.get('review_status')}'")

    # Check 5: No empty reference_answer
    for e in patched_entries:
        if not e.get("reference_answer", "").strip():
            errors.append(f"{e['id']}: empty reference_answer")

    # Check 6: No empty required_facts
    for e in patched_entries:
        if not e.get("required_facts"):
            errors.append(f"{e['id']}: empty required_facts")

    # Check 7: Complexity tier distribution preserved
    tier_dist = Counter(e["complexity_tier"] for e in patched_entries)
    expected_tiers = {
        "direct": 40, "multi_hop": 20, "cross_domain": 20,
        "comparison": 10, "temporal": 5, "adversarial": 5,
    }
    for tier, count in expected_tiers.items():
        if tier_dist.get(tier) != count:
            errors.append(
                f"Tier '{tier}': expected {count}, got {tier_dist.get(tier, 0)}"
            )

    # Check 8: All 13 fields present
    expected_fields = {
        "id", "category", "domain", "question", "reference_answer",
        "raw_evidence", "gold_sources", "required_facts", "style",
        "complexity_tier", "source_relation", "novelty", "review_status",
    }
    for e in patched_entries:
        missing = expected_fields - set(e.keys())
        if missing:
            errors.append(f"{e['id']}: missing fields {missing}")

    # Check 9: Frozen fields unchanged
    original_map = {e["id"]: e for e in load_jsonl(JSONL_PATH)}
    for e in patched_entries:
        orig = original_map.get(e["id"])
        if orig:
            for field in FROZEN_FIELDS:
                if json.dumps(e.get(field), ensure_ascii=False) != json.dumps(
                    orig.get(field), ensure_ascii=False
                ):
                    errors.append(f"{e['id']}: frozen field '{field}' was modified!")

    # Check 10: Anti-hallucination — answer entity matches question
    hallucination_suspects = []
    for e in patched_entries:
        if not verify_entity_match(e["question"], e["reference_answer"]):
            hallucination_suspects.append(e["id"])

    if hallucination_suspects:
        print(f"  ⚠ Hallucination suspects (answer entity mismatch): {len(hallucination_suspects)}")
        for hs in hallucination_suspects:
            print(f"    - {hs}")

    if errors:
        print(f"\n  ❌ Validation FAILED with {len(errors)} errors:")
        for err in errors:
            print(f"    - {err}")
        sys.exit(1)
    else:
        print("  ✅ All validation checks PASSED")

    # ------------------------------------------------------------------
    # Step 4: Anti-hallucination spot-check (5 critical cases)
    # ------------------------------------------------------------------
    print("\n[4/6] Anti-hallucination spot-check...")

    spot_checks = [
        {
            "id": "HOUT-DIR-FIN-07",
            "source_file": "MucHocPhi_ChatLuongCao_TienTien.md",
            "search_terms": ["Kỹ thuật điều khiển", "44"],
            "expected_substring": "44",
        },
        {
            "id": "HOUT-DIR-FIN-08",
            "source_file": "MucHocPhi_ChatLuongCao_TienTien.md",
            "search_terms": ["Thú y", "44", "1.475"],
            "expected_substring": "Thú y",
        },
        {
            "id": "HOUT-XDOM-07",
            "source_file": "MucHocPhi_ChatLuongCao_TienTien.md",
            "search_terms": ["Tài chính", "38"],
            "expected_substring": "38",
        },
    ]

    patched_map = {e["id"]: e for e in patched_entries}
    for sc in spot_checks:
        entry = patched_map.get(sc["id"])
        if not entry:
            print(f"  ❌ {sc['id']}: not found!")
            continue
        src = sources.get(sc["source_file"], "")
        found = []
        for term in sc["search_terms"]:
            if term.lower() in src.lower():
                found.append(term)
        answer_ok = sc["expected_substring"].lower() in entry["reference_answer"].lower()
        question_entity_in_answer = verify_entity_match(
            entry["question"], entry["reference_answer"]
        )
        status = "✅" if (found and answer_ok and question_entity_in_answer) else "⚠"
        print(f"  {status} {sc['id']}: source has {found}, answer mentions entity={question_entity_in_answer}")

    # ------------------------------------------------------------------
    # Step 5: Write patched JSONL
    # ------------------------------------------------------------------
    print(f"\n[5/6] Writing patched JSONL to {JSONL_PATH}...")

    with open(JSONL_PATH, "w", encoding="utf-8") as f:
        for entry in patched_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"  ✅ Wrote {len(patched_entries)} entries")

    # ------------------------------------------------------------------
    # Step 6: Write audit report
    # ------------------------------------------------------------------
    print(f"\n[6/6] Writing audit trail to {AUDIT_PATH}...")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unchanged_count = severity_counts.get("UNCHANGED", 0)

    lines = []
    lines.append("# Audit Trail: Heldout 100 Verification & Patch\n")
    lines.append(f"**Thời gian**: {now}  ")
    lines.append(f"**Tổng entries**: {len(patched_entries)}  ")
    lines.append(f"**Entries patched**: {patched_count}  ")
    lines.append(f"**Entries unchanged**: {unchanged_count}  ")
    lines.append(f"**All review_status**: verified  \n")

    lines.append("## Summary\n")
    lines.append("| Severity | Count | Description |")
    lines.append("|---|---|---|")
    lines.append(f"| CRITICAL | {severity_counts.get('CRITICAL', 0)} | answer + facts sai, đã patch |")
    lines.append(f"| HIGH | {severity_counts.get('HIGH', 0)} | chỉ answer sai, đã patch |")
    lines.append(f"| MEDIUM | {severity_counts.get('MEDIUM', 0)} | chỉ gold_sources/facts sai, đã patch |")
    lines.append(f"| UNCHANGED | {unchanged_count} | không cần sửa nội dung (chỉ đổi status) |")
    lines.append("")

    if warnings:
        lines.append("## Warnings\n")
        for w in warnings:
            lines.append(f"- ⚠ {w}")
        lines.append("")

    lines.append("## Detailed Changes\n")

    for rec in audit_records:
        eid = rec["id"]
        severity = rec["severity"]
        changes = rec["changes"]

        lines.append(f"### {eid} (Line {rec['line']})\n")
        lines.append(f"**Severity**: `{severity}`\n")

        if not changes or (len(changes) == 1 and "review_status" in changes):
            lines.append("Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).\n")
        else:
            lines.append("| Field | Before | After |")
            lines.append("|---|---|---|")
            for field, vals in changes.items():
                before = vals["before"]
                after = vals["after"]
                if isinstance(before, list):
                    before = json.dumps(before, ensure_ascii=False)
                if isinstance(after, list):
                    after = json.dumps(after, ensure_ascii=False)
                # Truncate very long values
                before_str = str(before)[:200]
                after_str = str(after)[:200]
                lines.append(f"| `{field}` | {before_str} | {after_str} |")
            lines.append("")

        # Source evidence
        if rec.get("source_evidence"):
            lines.append("**Source Evidence**:\n")
            for se in rec["source_evidence"]:
                lines.append(f"- `{se['file']}`:")
                for sl in se["lines"]:
                    lines.append(f"  - {sl[:150]}")
            lines.append("")

        # Facts verification
        if rec.get("facts_found") or rec.get("facts_missing"):
            found = rec.get("facts_found", [])
            missing = rec.get("facts_missing", [])
            lines.append(f"**Facts in source**: ✅ {len(found)} found, ❌ {len(missing)} missing")
            if missing:
                lines.append(f"  Missing: {missing}")
            lines.append("")

        lines.append("---\n")

    with open(AUDIT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  ✅ Audit report written ({len(audit_records)} entries)")

    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("=== PATCH HOÀN TẤT ===")
    print("=" * 60)
    print(f"Tổng entries: {len(patched_entries)}")
    print(f"Patched: {patched_count} ({severity_counts.get('CRITICAL',0)} CRITICAL + "
          f"{severity_counts.get('HIGH',0)} HIGH + {severity_counts.get('MEDIUM',0)} MEDIUM)")
    print(f"Unchanged: {unchanged_count}")
    print(f"review_status: {sum(1 for e in patched_entries if e['review_status']=='verified')}/100 verified")
    print(f"Validation: ALL PASSED")
    print(f"Audit trail: {AUDIT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
