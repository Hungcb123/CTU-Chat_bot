"""Deterministic routing for business-specific retrieval lanes.

The router deliberately uses rules instead of another LLM call.  Its main job
is not to understand every possible question, but to prevent a clearly stated
tuition intent from being rewritten into the opposite retrieval lane.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace
from enum import Enum


class QueryIntent(str, Enum):
    CALCULATION = "calculation"
    BOTH = "both"
    EXEMPTION_POLICY = "exemption_policy"
    EXEMPTION_BASIS = "exemption_basis"
    ACTUAL_TUITION = "actual_tuition"
    AMBIGUOUS_TUITION = "ambiguous_tuition"
    SCHOLARSHIP = "scholarship"
    STUDENT_LOAN = "student_loan"
    OTHER = "other"


@dataclass(frozen=True)
class QueryRoutingDecision:
    intent: QueryIntent
    academic_year: str | None = None
    classified_from: str = "original"


@dataclass(frozen=True)
class RetrievalLane:
    name: str
    domain: str | None = None
    content_kind: str | None = None
    fee_kind: str | None = None
    top_n: int = 6


_ACADEMIC_YEAR_RE = re.compile(r"\b(20\d{2})\s*[-–/]\s*(20\d{2})\b")


def _normalise(text: str | None) -> str:
    decomposed = unicodedata.normalize("NFD", text or "")
    without_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    lowered = without_marks.casefold().replace("đ", "d")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9%]+", " ", lowered)).strip()


def _extract_academic_year(*texts: str | None) -> str | None:
    for text in texts:
        match = _ACADEMIC_YEAR_RE.search(text or "")
        if match and int(match.group(2)) == int(match.group(1)) + 1:
            return f"{match.group(1)}-{match.group(2)}"
    return None


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def _is_vague_follow_up(text: str | None) -> bool:
    """Return whether an otherwise unclassified question needs chat context.

    A clear question about another domain (for example a scholarship) must not
    inherit a tuition lane merely because the query rewriter mentioned tuition.
    """

    value = _normalise(text)
    if not value:
        return True
    if _contains_any(
        value,
        (
            "hoc bong",
            "vay von",
            "vay tien",
            "tro cap",
            "ho tro xa hoi",
            "ren luyen",
        ),
    ):
        return False
    reference_phrases = (
        "muc do",
        "cai do",
        "truong hop do",
        "truong hop nay",
        "nhu vay",
        "nhu the",
        "con cai nay",
        "con muc nay",
        "thi sao",
        "the nao",
    )
    if _contains_any(value, reference_phrases):
        return True
    return len(value.split()) <= 12 and value.startswith(("vay ", "con ", "the ", "neu "))


def _classify_one(text: str | None) -> QueryIntent:
    value = _normalise(text)
    if not value:
        return QueryIntent.OTHER

    # These domains have dedicated metadata lanes. Detect them before tuition
    # because loan questions commonly contain the phrase "đóng học phí" but
    # must still search student-loan documents rather than tuition tables.
    if _contains_any(
        value,
        (
            "hoc bong",
            "khuyen khich hoc tap",
            "hoc bong vallet",
        ),
    ) or (
        _contains_any(value, ("gpa", "diem trung binh"))
        and _contains_any(value, ("drl", "diem ren luyen"))
    ):
        return QueryIntent.SCHOLARSHIP
    if _contains_any(
        value,
        (
            "vay von",
            "vay tien",
            "vay stem",
            "chuong trinh vay",
            "nhcsxh",
            "ngan hang chinh sach xa hoi",
            "vietinbank",
            "quyet dinh 157",
            "qd 157",
            "quyet dinh 29",
            "qd 29",
        ),
    ):
        return QueryIntent.STUDENT_LOAN

    has_tuition = _contains_any(
        value,
        (
            "hoc phi",
            "tin chi bao nhieu",
            "bao nhieu mot tin chi",
            "bao nhieu 1 tin chi",
            "tien phai dong",
        ),
    )
    has_exemption = _contains_any(
        value,
        (
            "mien giam",
            "mien hoc phi",
            "giam hoc phi",
            "giam 70",
            "giam 50",
            "mien 100",
        ),
    )
    has_actual = _contains_any(
        value,
        (
            "hoc phi thuc te",
            "muc thuc te",
            "muc thu",
            "muc dong",
            "dong binh thuong",
            "phai dong binh thuong",
            "hoc phi phai nop",
            "khong xet mien giam",
            "khong tinh mien giam",
            "khong hoi mien giam",
            "khong hoi muc mien giam",
        ),
    )
    has_basis = _contains_any(
        value,
        (
            "co so de tinh",
            "co so tinh",
            "lam co so",
            "dung de tinh mien giam",
            "dung lam co so",
            "muc tran",
            "muc co so",
            "xet mien giam",
            "muc mien giam",
            "ap dung mien giam",
        ),
    )

    # Calculation and explicit comparisons need balanced retrieval from both
    # rate tables, so they take precedence over single-lane keywords.
    has_calculation = _contains_any(
        value,
        (
            "con phai dong bao nhieu",
            "con dong bao nhieu",
            "sau mien giam",
            "tinh tien phai dong",
            "tinh hoc phi phai dong",
        ),
    ) or (
        has_tuition
        and _contains_any(
            value,
            ("tinh hoc phi", "tinh tien", "tinh so tien", "tinh giup"),
        )
    )
    if has_calculation:
        return QueryIntent.CALCULATION

    explicitly_requests_both = _contains_any(
        value,
        (
            "ca hai muc",
            "hai muc",
            "phan biet",
            "so sanh",
            "dung tron lan",
            "khong tron lan",
            "neu ro hai",
        ),
    )
    actual_negation = _contains_any(
        value,
        (
            "khong hoi mien giam",
            "khong hoi muc mien giam",
            "khong phai co so",
            "khong xet mien giam",
            "khong tinh mien giam",
        ),
    )
    basis_negation = _contains_any(
        value,
        (
            "khong phai hoc phi thuc te",
            "khong phai muc hoc phi thuc te",
            "khong hoi hoc phi thuc te",
            "khong hoi muc thuc te",
            "khong phai muc thu",
        ),
    )
    if explicitly_requests_both or (
        has_actual and has_basis and not actual_negation and not basis_negation
    ):
        return QueryIntent.BOTH

    # Explicit contrast/negation must win over the mere presence of the words
    # "mien giam" in phrases such as "toi khong hoi muc mien giam".
    if has_actual and actual_negation:
        return QueryIntent.ACTUAL_TUITION
    if has_basis and basis_negation:
        return QueryIntent.EXEMPTION_BASIS

    if has_exemption and _contains_any(
        value,
        (
            "doi tuong",
            "ai duoc",
            "dieu kien",
            "ho so",
            "giay to",
            "thu tuc",
            "nop o dau",
            "han nop",
            "phan tram",
            "chinh sach",
            "quy dinh",
            "thuoc dien",
            "co duoc mien",
            "co duoc giam",
            "duoc mien khong",
            "duoc giam khong",
            "muc giam 70",
            "muc giam 50",
        ),
    ):
        return QueryIntent.EXEMPTION_POLICY

    # Once policy/document wording has been ruled out, a plain request for a
    # monetary exemption amount belongs to the exemption-basis rate table.
    if has_basis or has_exemption:
        return QueryIntent.EXEMPTION_BASIS
    if has_actual:
        return QueryIntent.ACTUAL_TUITION
    # A concrete request naming an industry/program/cohort is an ordinary fee
    # lookup. Treating it as ambiguous caused the exemption table to compete
    # with the actual-tuition table even when the user never mentioned aid.
    if has_tuition and (
        _contains_any(
            value,
            (
                "nganh",
                "khoa",
                "chuong trinh",
                "chat luong cao",
                "clc",
                "tien tien",
                "dai tra",
            ),
        )
        or re.search(r"\bk\s*[4-9]\d\b", value)
    ):
        return QueryIntent.ACTUAL_TUITION
    if has_tuition:
        return QueryIntent.AMBIGUOUS_TUITION
    return QueryIntent.OTHER


def classify_query_intent(
    original_query: str,
    rewritten_query: str | None = None,
) -> QueryRoutingDecision:
    """Classify the original query, using the rewrite only as ambiguity help."""

    original_year = _extract_academic_year(original_query)
    original_intent = _classify_one(original_query)
    if original_intent not in {QueryIntent.AMBIGUOUS_TUITION, QueryIntent.OTHER}:
        return QueryRoutingDecision(original_intent, original_year, "original")

    may_use_rewrite = (
        original_intent is QueryIntent.AMBIGUOUS_TUITION
        or _is_vague_follow_up(original_query)
    )
    if not may_use_rewrite:
        return QueryRoutingDecision(original_intent, original_year, "original")

    rewritten_intent = _classify_one(rewritten_query)
    academic_year = original_year or _extract_academic_year(rewritten_query)
    if rewritten_query and rewritten_intent not in {QueryIntent.OTHER, QueryIntent.AMBIGUOUS_TUITION}:
        return QueryRoutingDecision(rewritten_intent, academic_year, "rewrite")

    # A genuinely ambiguous tuition question remains ambiguous even if the
    # rewriter simply paraphrases it without choosing a fee type.
    final_intent = (
        QueryIntent.AMBIGUOUS_TUITION
        if QueryIntent.AMBIGUOUS_TUITION in {original_intent, rewritten_intent}
        else QueryIntent.OTHER
    )
    return QueryRoutingDecision(final_intent, academic_year, "original")


def build_retrieval_lanes(decision: QueryRoutingDecision) -> tuple[RetrievalLane, ...]:
    """Translate an intent into balanced, independently filtered searches."""

    actual = RetrievalLane(
        name="actual_tuition",
        domain="tuition",
        content_kind="rate_table",
        fee_kind="actual_tuition",
        top_n=3,
    )
    basis = RetrievalLane(
        name="exemption_basis",
        domain="tuition",
        content_kind="rate_table",
        fee_kind="exemption_basis",
        top_n=3,
    )
    if decision.intent == QueryIntent.ACTUAL_TUITION:
        return (replace(actual, top_n=6),)
    if decision.intent == QueryIntent.EXEMPTION_BASIS:
        return (replace(basis, top_n=6),)
    if decision.intent == QueryIntent.EXEMPTION_POLICY:
        return (
            RetrievalLane(
                name="exemption_policy",
                domain="tuition",
                content_kind="exemption_policy",
                fee_kind="not_applicable",
                top_n=6,
            ),
        )
    if decision.intent == QueryIntent.SCHOLARSHIP:
        return (
            RetrievalLane(
                name="scholarship",
                domain="scholarship",
                top_n=6,
            ),
        )
    if decision.intent == QueryIntent.STUDENT_LOAN:
        return (
            RetrievalLane(
                name="student_loan",
                domain="student_loan",
                top_n=6,
            ),
        )
    if decision.intent in {
        QueryIntent.CALCULATION,
        QueryIntent.BOTH,
        QueryIntent.AMBIGUOUS_TUITION,
    }:
        return (actual, basis)
    return (RetrievalLane(name="default", top_n=6),)


def build_answer_instruction(decision: QueryRoutingDecision) -> str:
    if decision.intent == QueryIntent.ACTUAL_TUITION:
        return (
            "Chỉ dùng ngữ cảnh có loại HỌC PHÍ THỰC TẾ; nêu rõ năm học. "
            "Không thay bằng mức cơ sở miễn giảm."
        )
    if decision.intent == QueryIntent.EXEMPTION_BASIS:
        return (
            "Chỉ dùng ngữ cảnh có loại CƠ SỞ TÍNH MIỄN GIẢM; nêu rõ năm học. "
            "Không thay bằng học phí thực tế."
        )
    if decision.intent == QueryIntent.EXEMPTION_POLICY:
        return "Chỉ trả lời về đối tượng, điều kiện, tỷ lệ hoặc hồ sơ miễn giảm từ tài liệu chính sách."
    if decision.intent == QueryIntent.SCHOLARSHIP:
        return (
            "Chỉ dùng tài liệu thuộc nhóm HỌC BỔNG; không lấy quy định vay vốn, "
            "học phí hoặc trợ cấp để thay thế."
        )
    if decision.intent == QueryIntent.STUDENT_LOAN:
        return (
            "Chỉ dùng tài liệu thuộc nhóm VAY VỐN SINH VIÊN; phân biệt rõ nguồn vay, "
            "đối tượng, điều kiện, hạn mức và thủ tục nếu tài liệu có nêu."
        )
    if decision.intent == QueryIntent.AMBIGUOUS_TUITION:
        return (
            "Câu hỏi chưa nói rõ loại học phí. Bắt buộc trình bày cả HỌC PHÍ THỰC TẾ và "
            "CƠ SỞ TÍNH MIỄN GIẢM thành hai dòng riêng, mỗi dòng có năm học và nguồn; "
            "nếu thiếu một loại thì nói rõ không tìm thấy, không tự bịa."
        )
    if decision.intent in {QueryIntent.BOTH, QueryIntent.CALCULATION}:
        return (
            "Giữ học phí thực tế và cơ sở tính miễn giảm thành hai đại lượng riêng. "
            "Nêu nhãn và năm học của từng mức trước khi so sánh hoặc tính toán."
        )
    return "Áp dụng ngữ cảnh truy xuất phù hợp và không suy diễn ngoài tài liệu."
