"""Lexical anchor detection for query-adaptive retrieval.

Detects structured tokens in user queries (program codes, course codes,
cohort identifiers, training system labels) that signal BM25 exact-match
should receive a higher weight in Reciprocal Rank Fusion.
"""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field


# ── Defaults (overridable via environment) ──────────────────────────
_DEFAULT_BM25_BOOST = float(os.getenv("RAG_BM25_BOOST_ALPHA", "1.5"))

# ── Patterns ────────────────────────────────────────────────────────
_PROGRAM_CODE_RE = re.compile(r"\b7\d{6}\b")
_COURSE_CODE_RE = re.compile(r"\b[A-Z]{2}\d{3}[A-Z]?\b")
_COHORT_RE = re.compile(r"\b[Kk]\s*([4-5]\d)\b")

_TRAINING_SYSTEMS: dict[str, str] = {
    "clc": "CLC",
    "chat luong cao": "CLC",
    "cttt": "CTTT",
    "chuong trinh tien tien": "CTTT",
    "vlvh": "VLVH",
    "vua lam vua hoc": "VLVH",
    "dai tra": "đại trà",
    "chuong trinh chuan": "đại trà",
    "he chuan": "đại trà",
}


from pathlib import Path
import json

_DEFAULT_SCHOLARSHIP_ENTITIES: dict[str, str] = {
    "vallet": "Vallet",
    "scic": "SCIC",
    "panasonic": "Panasonic",
    "shinhan": "Shinhan",
    "shihan": "Shinhan",
    "luong van can": "Lương Văn Can",
    "luong van cang": "Lương Văn Can",
    "le so": "Lê Sở",
    "scc": "SCC",
    "tay ninh": "Tây Ninh",
}

_CACHED_SCHOLARSHIPS: dict[str, str] | None = None


def get_scholarship_entities() -> dict[str, str]:
    """Return mapping of normalized query terms to canonical scholarship entity names."""
    global _CACHED_SCHOLARSHIPS
    if _CACHED_SCHOLARSHIPS is not None:
        return _CACHED_SCHOLARSHIPS

    entities = dict(_DEFAULT_SCHOLARSHIP_ENTITIES)
    root = Path(__file__).resolve().parents[2]
    meta_path = root / "data" / "document_metadata.json"
    if meta_path.is_file():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for fname, meta in data.items():
                if meta.get("domain") == "scholarship" and fname.startswith("HB_"):
                    stem = fname.removesuffix(".md").removeprefix("HB_")
                    parts = stem.split("_")
                    if parts and parts[0]:
                        sponsor = parts[0]
                        if not sponsor.startswith("K") and not sponsor.isdigit():
                            entities[_strip_diacritics(sponsor)] = sponsor
        except Exception:
            pass

    _CACHED_SCHOLARSHIPS = entities
    return _CACHED_SCHOLARSHIPS


def _strip_diacritics(text: str) -> str:
    """Remove Vietnamese diacritics for case-insensitive matching."""
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    return without_marks.lower().replace("đ", "d")


@dataclass(frozen=True)
class LexicalAnchors:
    """Result of lexical anchor detection on a query string."""

    program_codes: tuple[str, ...] = ()
    course_codes: tuple[str, ...] = ()
    cohorts: tuple[str, ...] = ()
    training_systems: tuple[str, ...] = ()
    scholarships: tuple[str, ...] = ()

    @property
    def has_anchor(self) -> bool:
        return bool(
            self.program_codes
            or self.course_codes
            or self.cohorts
            or self.training_systems
            or self.scholarships
        )

    @property
    def bm25_boost(self) -> float:
        """BM25 weight multiplier for RRF fusion."""
        return _DEFAULT_BM25_BOOST if self.has_anchor else 1.0


def detect_lexical_anchors(query: str) -> LexicalAnchors:
    """Detect structured lexical anchors in a Vietnamese query.

    Returns a ``LexicalAnchors`` dataclass with detected codes and a
    ``bm25_boost`` multiplier that the RRF fusion step should apply to
    the BM25 rank contribution.

    >>> anchors = detect_lexical_anchors("Ngành 7480201 học bao nhiêu tín chỉ?")
    >>> anchors.program_codes
    ('7480201',)
    >>> anchors.bm25_boost
    1.5
    """
    program_codes = tuple(_PROGRAM_CODE_RE.findall(query))
    course_codes = tuple(_COURSE_CODE_RE.findall(query))

    cohort_matches = _COHORT_RE.findall(query)
    cohorts = tuple(f"K{num}" for num in cohort_matches)

    stripped = _strip_diacritics(query)
    training_systems: list[str] = []
    seen_canonical: set[str] = set()
    for key, canonical in _TRAINING_SYSTEMS.items():
        if key in stripped and canonical not in seen_canonical:
            training_systems.append(canonical)
            seen_canonical.add(canonical)

    scholarships: list[str] = []
    entities_map = get_scholarship_entities()
    for key, canonical in entities_map.items():
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, stripped):
            if canonical not in scholarships:
                scholarships.append(canonical)

    return LexicalAnchors(
        program_codes=program_codes,
        course_codes=course_codes,
        cohorts=cohorts,
        training_systems=tuple(training_systems),
        scholarships=tuple(scholarships),
    )
