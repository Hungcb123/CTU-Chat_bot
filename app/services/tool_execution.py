"""Deterministic validation and provenance helpers around LLM tool decisions."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from app.services.evaluation_contract import canonical_value, normalize_text


class ToolOutcome(str, Enum):
    FOUND = "found"
    VALID_NO_RESULT = "valid_no_result"
    INVALID_ARGUMENT = "invalid_argument"
    BACKEND_FAILURE = "backend_failure"


@dataclass(frozen=True)
class ToolValidation:
    valid: bool
    normalized_args: dict[str, Any]
    errors: tuple[str, ...] = ()


REQUIRED_ARGUMENTS: dict[str, tuple[str, ...]] = {
    "tra_cuu_nganh": ("ten_nganh",),
    "so_sanh_nganh": ("nganh_1", "nganh_2"),
    "tim_nganh": ("tieu_chi",),
    "xem_chuoi_tien_quyet": ("ma_mon",),
    "mon_chung_giua_nganh": ("nganh_1", "nganh_2"),
    "tim_nganh_co_mon": ("ten_mon",),
    "tra_cuu_hoc_phi_graph": ("ten_nganh",),
    "tra_cuu_co_so_mien_giam_graph": (),
    "tra_cuu_quy_dinh_hoc_phi": (),
    "tinh_tien_hoc_bong": ("gpa", "drl"),
    "tinh_toan_hoc_phi": (
        "gia_hoc_phi_thuc_te", "muc_tran_mien_giam", "phan_tram_giam",
    ),
}


def normalize_tool_name(tool_name: str | None) -> str | None:
    """Strip provider namespace prefix (e.g. 'default_api.tra_cuu_nganh' -> 'tra_cuu_nganh')."""
    if not tool_name:
        return None
    cleaned = str(tool_name).strip()
    if "." in cleaned:
        cleaned = cleaned.split(".")[-1].strip()
    return cleaned


def normalize_tool_arguments(tool_name: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
    canonical_tool = normalize_tool_name(tool_name) or tool_name
    normalized = dict(arguments)
    if "khoa" in normalized and normalized["khoa"] not in (None, ""):
        normalized["khoa"] = canonical_value(normalized["khoa"], "khoa")
        normalized["khoa"] = str(normalized["khoa"]).upper()
    for key in ("gpa", "drl", "gia_hoc_phi_thuc_te", "muc_tran_mien_giam", "phan_tram_giam"):
        if key in normalized:
            normalized[key] = canonical_value(normalized[key], key)
    for key in ("doi_tuong", "ten_nganh_hoac_khoi"):
        if key in normalized and isinstance(normalized[key], str):
            canonical = canonical_value(normalized[key], key)
            if key == "doi_tuong" and canonical == "vua lam vua hoc":
                normalized[key] = "VLVH"
            elif key == "ten_nganh_hoac_khoi" and canonical.startswith("khoi "):
                suffix = canonical.split(" ", 1)[1].upper()
                normalized[key] = f"Khối {suffix}"
    return normalized


def validate_tool_arguments(tool_name: str, arguments: Mapping[str, Any]) -> ToolValidation:
    canonical_tool = normalize_tool_name(tool_name) or tool_name
    normalized = normalize_tool_arguments(canonical_tool, arguments)
    errors: list[str] = []
    for key in REQUIRED_ARGUMENTS.get(canonical_tool, ()):
        if key not in normalized or normalized[key] in (None, ""):
            errors.append(f"missing:{key}")

    ranges = {
        "gpa": (0.0, 4.0),
        "drl": (0.0, 100.0),
        "phan_tram_giam": (0.0, 100.0),
        "gia_hoc_phi_thuc_te": (0.0, float("inf")),
        "muc_tran_mien_giam": (0.0, float("inf")),
    }
    for key, (lower, upper) in ranges.items():
        if key not in normalized:
            continue
        value = normalized[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"not_numeric:{key}")
        elif not lower <= float(value) <= upper:
            errors.append(f"out_of_range:{key}")

    for left, right in (("nganh_1", "nganh_2"),):
        if left in normalized and right in normalized:
            if normalize_text(normalized[left]) == normalize_text(normalized[right]):
                errors.append(f"duplicate_entities:{left},{right}")
    return ToolValidation(not errors, normalized, tuple(errors))


def classify_tool_outcome(output: str = "", error: BaseException | None = None) -> ToolOutcome:
    if error is not None:
        return ToolOutcome.BACKEND_FAILURE
    folded = normalize_text(output)
    if any(token in folded for token in ("khong tim thay", "khong co du lieu", "khong co ket qua")):
        return ToolOutcome.VALID_NO_RESULT
    return ToolOutcome.FOUND


def recommend_required_tool(agent: str, query: str) -> str | None:
    value = normalize_text(query)
    if agent == "academic":
        if "so sanh" in value or "khac" in value and "nganh" in value:
            return "so_sanh_nganh"
        if "tien quyet" in value or "hoc truoc" in value:
            return "xem_chuoi_tien_quyet"
        if "nganh nao co mon" in value or "mon" in value and "nganh nao" in value:
            return "tim_nganh_co_mon"
        if "tim nganh" in value or "nganh nao" in value:
            return "tim_nganh"
        if "nganh" in value or re.search(r"\b7\d{6}\b", value):
            return "tra_cuu_nganh"
    if agent == "financial":
        if all(token in value for token in ("hoc phi", "mien giam")) and any(
            token in value for token in ("con dong", "tinh", "%", "phan tram")
        ):
            return "tinh_toan_hoc_phi"
        if "co so" in value and "mien giam" in value or "muc tran" in value:
            return "tra_cuu_co_so_mien_giam_graph"
        if any(token in value for token in ("vlvh", "vua lam vua hoc", "ngoai gio", "hoc lai")):
            return "tra_cuu_quy_dinh_hoc_phi"
        if "hoc phi" in value and "mien giam" not in value:
            return "tra_cuu_hoc_phi_graph"
    if agent == "scholarship" and "gpa" in value and (
        "drl" in value or "diem ren luyen" in value
    ):
        return "tinh_tien_hoc_bong"
    return None


def evidence_envelope(
    *, tool_name: str, arguments: Mapping[str, Any], status: ToolOutcome, output: str
) -> str:
    canonical_tool = normalize_tool_name(tool_name) or tool_name
    header = json.dumps(
        {"tool": canonical_tool, "arguments": dict(arguments), "status": status.value},
        ensure_ascii=False,
        sort_keys=True,
    )
    return f"[STRUCTURED_EVIDENCE {header}]\n{output}"


def normalize_and_validate_before_invoke(
    tool_name: str,
    arguments: Mapping[str, Any],
) -> tuple[ToolValidation, ToolOutcome | None]:
    """Normalize, validate, and pre-classify tool arguments.

    Production graph calls this before ``tool.invoke()`` to share the same
    normalization/validation logic used in the benchmark scorer. If validation
    fails, the caller should return the errors to the user (or trigger a repair)
    instead of invoking the tool with known-bad arguments.

    Returns:
        A ``(validation, early_outcome)`` pair. *early_outcome* is ``None``
        when the arguments look valid and the tool should proceed; otherwise
        it is ``ToolOutcome.INVALID_ARGUMENT`` and the caller should skip
        invocation.
    """
    canonical_tool = normalize_tool_name(tool_name) or tool_name
    validation = validate_tool_arguments(canonical_tool, arguments)
    if not validation.valid:
        return validation, ToolOutcome.INVALID_ARGUMENT
    return validation, None

