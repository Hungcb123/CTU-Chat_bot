"""Shared deterministic evaluation and tool-argument contract.

The benchmark scripts used to implement slightly different exact-match rules.
This module deliberately contains no LLM or database dependency so every suite
can score the same record in the same way.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence


class MetricState(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_EVALUATED = "not_evaluated"


@dataclass(frozen=True)
class OutputEvaluation:
    state: MetricState
    passed: bool | None
    reason: str


SYMMETRIC_ARGUMENT_PAIRS: dict[str, tuple[str, str]] = {
    "so_sanh_nganh": ("nganh_1", "nganh_2"),
    "mon_chung_giua_nganh": ("nganh_1", "nganh_2"),
}

_ALIASES = {
    "vlvh": "vua lam vua hoc",
    "he vua lam vua hoc": "vua lam vua hoc",
    "chat luong cao": "clc",
    "chuong trinh chat luong cao": "clc",
    "chuong trinh tien tien": "cttt",
    "tien tien": "cttt",
}


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFD", str(value).casefold())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = text.replace("đ", "d")
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    return re.sub(r"\s+", " ", text)


def _canonical_string(value: str, key: str | None = None) -> str:
    text = normalize_text(value)
    text = _ALIASES.get(text, text)
    if key == "khoa" or re.fullmatch(r"(?:khoa |k)?[4-9]\d", text):
        match = re.search(r"([4-9]\d)", text)
        if match:
            return f"k{match.group(1)}"
    if "khoi" in (key or "") or text.startswith("khoi"):
        _roman_to_int = {
            "i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5",
            "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10",
        }
        roman = re.search(r"\b(i{1,3}|iv|v|vi{0,3}|ix|x)\b", text)
        number = re.search(r"\b([1-9]|10)\b", text)
        if roman:
            return f"khoi {_roman_to_int.get(roman.group(1), roman.group(1))}"
        if number:
            return f"khoi {number.group(1)}"
    return text


def canonical_value(value: Any, key: str | None = None) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else value
    if isinstance(value, str):
        stripped = value.strip()
        if re.fullmatch(r"[-+]?\d+(?:[.,]\d+)?", stripped):
            return float(stripped.replace(",", "."))
        return _canonical_string(stripped, key)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [canonical_value(item, key) for item in value]
    if isinstance(value, Mapping):
        return {name: canonical_value(item, name) for name, item in value.items()}
    return value


def values_equivalent(expected: Any, actual: Any, *, key: str | None = None) -> bool:
    expected_value = canonical_value(expected, key)
    actual_value = canonical_value(actual, key)
    if isinstance(expected_value, float) and isinstance(actual_value, float):
        return math.isclose(expected_value, actual_value, rel_tol=0.0, abs_tol=1e-6)
    if expected_value == actual_value:
        return True
    if isinstance(expected_value, str) and isinstance(actual_value, str):
        return bool(
            expected_value
            and actual_value
            and (expected_value in actual_value or actual_value in expected_value)
        )
    return False


def arguments_match(
    expected: Mapping[str, Any],
    actual: Mapping[str, Any],
    *,
    tool_name: str | None = None,
    accepted: Mapping[str, Sequence[Any]] | None = None,
) -> bool:
    accepted = accepted or {}

    def matches_key(key: str, expected_value: Any, actual_value: Any) -> bool:
        alternatives = [expected_value, *accepted.get(key, ())]
        return any(values_equivalent(candidate, actual_value, key=key) for candidate in alternatives)

    if not all(key in actual and matches_key(key, value, actual[key]) for key, value in expected.items()):
        pair = SYMMETRIC_ARGUMENT_PAIRS.get(tool_name or "")
        if not pair or not all(key in expected and key in actual for key in pair):
            return False
        left, right = pair
        non_pair = {key: value for key, value in expected.items() if key not in pair}
        if not all(key in actual and matches_key(key, value, actual[key]) for key, value in non_pair.items()):
            return False
        return matches_key(left, expected[left], actual[right]) and matches_key(
            right, expected[right], actual[left]
        )
    return True


def evaluate_output(case: Mapping[str, Any], output: str) -> OutputEvaluation:
    required = list(case.get("expected_contains") or [])
    any_of = list(case.get("expected_response_any") or [])
    forbidden = list(case.get("expected_not_contains") or [])
    if not required and not any_of and not forbidden:
        return OutputEvaluation(MetricState.NOT_EVALUATED, None, "no_result_oracle")

    folded = normalize_text(output)
    contains_required = all(normalize_text(token) in folded for token in required)
    contains_any = not any_of or any(normalize_text(token) in folded for token in any_of)
    avoids_forbidden = all(normalize_text(token) not in folded for token in forbidden)
    passed = contains_required and contains_any and avoids_forbidden
    return OutputEvaluation(
        MetricState.PASS if passed else MetricState.FAIL,
        passed,
        "oracle_satisfied" if passed else "oracle_not_satisfied",
    )


def validate_unique_case_ids(cases: Iterable[Mapping[str, Any]]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for case in cases:
        case_id = str(case.get("id", "")).strip()
        if not case_id:
            raise ValueError("Every evaluation case must have a non-empty id")
        if case_id in seen:
            duplicates.add(case_id)
        seen.add(case_id)
    if duplicates:
        raise ValueError(f"Duplicate evaluation case IDs: {sorted(duplicates)}")
