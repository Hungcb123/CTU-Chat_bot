# Tuition Exemption Calculation Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Route explicit money-after-exemption questions through all three required evidence sources without changing the calculation formula.

**Architecture:** Keep the existing deterministic router and structured tuition catalog. Classify only explicit monetary exemption questions as `CALCULATION`; retrieve actual tuition, exemption basis, and exemption policy independently, then let the existing tool-calling path calculate only when Gemini has all three values.

**Tech Stack:** Python, unittest, FastAPI, existing Qdrant metadata lanes, existing `tuition_catalog` and `tinh_toan_hoc_phi`.

## Global Constraints

- Do not modify Markdown, metadata, Qdrant collections, or the calculation formula.
- Preserve policy-only questions such as percentage and eligibility queries.
- Keep the diff small enough to reverse with an exact patch.

---

### Task 1: Protect intent boundaries

**Files:**
- Modify: `tests/test_query_intent.py`
- Modify: `app/services/query_intent.py`

**Interfaces:**
- Consumes: `classify_query_intent(query, rewrite=None)`.
- Produces: `QueryIntent.CALCULATION` only for explicit monetary calculation wording.

- [ ] Add a failing test for `được giảm bao nhiêu tiền` and regression assertions for percentage, eligibility, and exemption-basis wording.
- [ ] Run `python -m unittest tests.test_query_intent` and confirm the new monetary case fails as `EXEMPTION_POLICY`.
- [ ] Move/extend the calculation rule so explicit monetary wording wins without broadening generic `được giảm`.
- [ ] Run the intent tests and confirm all cases pass.

### Task 2: Retrieve all calculation inputs

**Files:**
- Modify: `tests/test_query_intent.py`
- Modify: `app/services/query_intent.py`

**Interfaces:**
- Consumes: `build_retrieval_lanes(QueryRoutingDecision)`.
- Produces: calculation lanes `actual_tuition`, `exemption_basis`, and `exemption_policy`.

- [ ] Add a failing test asserting all three calculation lanes and their metadata filters.
- [ ] Run the focused test and confirm `exemption_policy` is missing.
- [ ] Reuse the existing exemption-policy lane in the calculation branch with a balanced `top_n`.
- [ ] Run the full intent suite, compile check, diff check, and GitNexus change detection.

