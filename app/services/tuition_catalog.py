"""Deterministic lookup for structured actual-tuition rate tables."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TUITION_RATES_PATH = PROJECT_ROOT / "data" / "tuition_rates.json"


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFD", value.casefold())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


PROGRAM_LABELS = {
    "standard": "Đại trà/chuẩn",
    "high_quality": "Chất lượng cao (CLC)",
    "advanced": "Tiên tiến",
    "other": "Khác",
}

RATE_LABELS = {
    "per_academic_year": "Học phí cố định mỗi năm học",
    "per_full_course": "Học phí toàn khóa",
    "per_credit": "Học phí mỗi tín chỉ",
}

SCOPE_LABELS = {
    "general_common": "khối kiến thức đại cương chung",
    "major": "khối kiến thức ngành/cơ sở ngành/chuyên ngành",
    "all": "áp dụng chung",
    "other": "phạm vi khác",
}

MAJOR_ALIASES = {
    "cntt": "cong nghe thong tin",
    "it": "cong nghe thong tin",
    "khmt": "khoa hoc may tinh",
    "ktpm": "ky thuat phan mem",
    "attt": "an toan thong tin",
    "qtkd": "quan tri kinh doanh",
    "cnsh": "cong nghe sinh hoc",
}


@dataclass(frozen=True)
class TuitionLookupResult:
    status: str
    message: str
    records: tuple[dict[str, Any], ...] = ()

    @property
    def authoritative(self) -> bool:
        return self.status in {"found", "needs_clarification", "not_found"}


class TuitionRateCatalog:
    """Load validated JSON once and perform exact entity-based lookup."""

    def __init__(self, records: Iterable[dict[str, Any]], *, source_path: Path):
        self.source_path = source_path
        self.records = tuple(records)
        self._major_names = sorted(
            {
                normalize_text(str(record["major_name"])): str(record["major_name"])
                for record in self.records
                if record.get("major_name")
            }.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

    @classmethod
    def load(cls, path: str | Path = DEFAULT_TUITION_RATES_PATH) -> "TuitionRateCatalog":
        path = Path(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != "1.0" or payload.get("currency") != "VND":
            raise ValueError("tuition_rates.json has an unsupported schema or currency")
        records = payload.get("records")
        if not isinstance(records, list) or not records:
            raise ValueError("tuition_rates.json must contain a non-empty records array")

        seen_ids: set[str] = set()
        required = {
            "id", "fee_kind", "academic_year", "education_level", "study_mode",
            "program_type", "cohort_min", "cohort_max", "entity_type",
            "major_code", "major_name", "course_name", "knowledge_scope",
            "rate_type", "amount_vnd", "source", "source_section",
        }
        for position, record in enumerate(records, start=1):
            missing = required - set(record)
            if missing:
                raise ValueError(f"tuition record {position} is missing {sorted(missing)}")
            if record["id"] in seen_ids:
                raise ValueError(f"duplicate tuition record id: {record['id']}")
            seen_ids.add(record["id"])
            if record["fee_kind"] != "actual_tuition":
                raise ValueError(f"record {record['id']} is not actual_tuition")
            if not isinstance(record["amount_vnd"], int) or record["amount_vnd"] <= 0:
                raise ValueError(f"record {record['id']} has invalid amount_vnd")
        return cls(records, source_path=path)

    @staticmethod
    def _extract_program(query: str) -> str | None:
        if re.search(r"\bclc\b|chat luong cao", query):
            return "high_quality"
        if "tien tien" in query:
            return "advanced"
        if re.search(r"\bdai tra\b|chuong trinh chuan|he chuan", query):
            return "standard"
        return None

    @staticmethod
    def _extract_cohort(query: str) -> int | None:
        match = re.search(r"\b(?:k|khoa)\s*([4-9]\d)\b", query)
        return int(match.group(1)) if match else None

    def _extract_major(self, query: str) -> tuple[str | None, str | None]:
        for alias, canonical in MAJOR_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", query):
                for normalized, original in self._major_names:
                    if normalized == canonical:
                        return normalized, original
        for normalized, original in self._major_names:
            if re.search(rf"(?:^| ){re.escape(normalized)}(?: |$)", query):
                return normalized, original
        code_match = re.search(r"\b(7\d{6})\b", query)
        if code_match:
            code = code_match.group(1)
            for record in self.records:
                if record.get("major_code") == code and record.get("major_name"):
                    return normalize_text(record["major_name"]), record["major_name"]
        return None, None

    @staticmethod
    def _cohort_applies(record: dict[str, Any], cohort: int) -> bool:
        lower = record.get("cohort_min")
        upper = record.get("cohort_max")
        return (lower is None or cohort >= lower) and (upper is None or cohort <= upper)

    @staticmethod
    def _requests_general_common(query: str) -> bool:
        return any(
            phrase in query
            for phrase in (
                "hoc phi chung",
                "dai cuong chung",
                "hoc phan dai cuong",
                "khoi kien thuc dai cuong chung",
            )
        )

    def rewrite_is_safe_for_lookup(self, original_query: str, rewritten_query: str) -> bool:
        """Allow a rewrite to fill omissions, never to replace explicit entities."""

        original = normalize_text(original_query)
        rewritten = normalize_text(rewritten_query)
        exemption_phrases = ("mien giam", "co so tinh", "lam co so", "muc tran")
        if any(item in rewritten for item in exemption_phrases) and not any(
            item in original for item in exemption_phrases
        ):
            return False

        original_program = self._extract_program(original)
        rewritten_program = self._extract_program(rewritten)
        if original_program is not None and rewritten_program != original_program:
            return False

        original_cohort = self._extract_cohort(original)
        rewritten_cohort = self._extract_cohort(rewritten)
        if original_cohort is not None and rewritten_cohort != original_cohort:
            return False

        original_major, _ = self._extract_major(original)
        rewritten_major, _ = self._extract_major(rewritten)
        if original_major is not None and rewritten_major != original_major:
            return False

        if self._requests_general_common(original) and not self._requests_general_common(rewritten):
            return False
        return True

    def lookup(self, raw_query: str) -> TuitionLookupResult:
        query = normalize_text(raw_query)
        cohort = self._extract_cohort(query)
        program = self._extract_program(query)
        major_key, major_name = self._extract_major(query)
        general_common = self._requests_general_common(query)
        looks_like_major_lookup = bool(
            cohort is not None
            or program is not None
            or "nganh" in query.split()
            or major_key is not None
            or general_common
        )
        if not looks_like_major_lookup:
            return TuitionLookupResult("not_applicable", "")
        if major_key is None and not general_common:
            return TuitionLookupResult(
                "needs_clarification",
                "Bạn vui lòng cho biết tên hoặc mã ngành cần tra cứu học phí.",
            )
        if cohort is None:
            subject = (
                "mức học phí đại cương chung"
                if general_common
                else f"ngành {major_name}"
            )
            return TuitionLookupResult(
                "needs_clarification",
                f"Bạn vui lòng cho biết khóa tuyển sinh của {subject} (ví dụ K49 hoặc K52).",
            )
        if program is None:
            program = "standard"

        matches: list[dict[str, Any]] = []
        for record in self.records:
            if record.get("fee_kind") != "actual_tuition":
                continue
            if record.get("education_level") != "undergraduate":
                continue
            if record.get("study_mode") != "full_time":
                continue
            if record.get("program_type") != program:
                continue
            if not self._cohort_applies(record, cohort):
                continue
            record_major = record.get("major_name")
            is_major_record = bool(
                not general_common
                and record_major
                and normalize_text(record_major) == major_key
            )
            is_common_record = (
                record.get("entity_type") == "all_students"
                and record.get("knowledge_scope") == "general_common"
            )
            if is_major_record or (is_common_record and (general_common or major_key is not None)):
                matches.append(record)

        if not matches:
            subject = "đại cương chung" if general_common else f"ngành {major_name}"
            return TuitionLookupResult(
                "not_found",
                f"Không tìm thấy học phí thực tế {subject}, "
                f"chương trình {PROGRAM_LABELS[program]}, khóa {cohort} trong bảng chuẩn hóa.",
            )

        unique: dict[tuple[Any, ...], dict[str, Any]] = {}
        for record in matches:
            key = (
                record["rate_type"], record["knowledge_scope"], record["amount_vnd"],
                record["source"], record["source_section"],
            )
            unique[key] = record
        matches = sorted(
            unique.values(),
            key=lambda item: (
                {"per_academic_year": 0, "per_full_course": 1, "per_credit": 2}.get(item["rate_type"], 9),
                {"major": 0, "general_common": 1}.get(item["knowledge_scope"], 9),
            ),
        )
        lines = [
            "[KẾT QUẢ TRA CỨU HỌC PHÍ CẤU TRÚC - NGUỒN ƯU TIÊN]",
            (
                "Phạm vi: Khối kiến thức đại cương chung"
                if general_common
                else f"Ngành: {major_name}"
            ),
            f"Chương trình: {PROGRAM_LABELS[program]}",
            f"Khóa tuyển sinh: {cohort}",
        ]
        sources: set[str] = set()
        years: set[str] = set()
        for record in matches:
            label = RATE_LABELS.get(record["rate_type"], record["rate_type"])
            scope = SCOPE_LABELS.get(record["knowledge_scope"], record["knowledge_scope"])
            lines.append(f"- {label} ({scope}): {record['amount_vnd']:,} đồng".replace(",", "."))
            sources.add(record["source"])
            years.add(record["academic_year"])
        lines.append(f"Năm học của văn bản: {', '.join(sorted(years))}")
        lines.append(f"Nguồn: {', '.join(sorted(sources))}")
        lines.append("Phải dùng các con số trên; không thay bằng kết quả vector search khác.")
        return TuitionLookupResult("found", "\n".join(lines), tuple(matches))
