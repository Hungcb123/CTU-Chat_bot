"""Hybrid contextual rewriting and deterministic business retrieval routing."""

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
    SOCIAL_SUPPORT = "social_support"
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


def should_rewrite_query(query: str, previous_user_query: str | None) -> bool:
    """Contextualize only queries the deterministic router cannot settle."""

    if not (previous_user_query or "").strip():
        return False
    return _classify_one(query) in {
        QueryIntent.OTHER,
        QueryIntent.AMBIGUOUS_TUITION,
    }


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
            "scc",
            "vallet",
            "panasonic",
            "luong van can",
            "shinhan",
            "scic",
            "thap sang niem tin",
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
            "cho vay",
            "vay mua",
            "vay toi da",
            "khoan vay sinh vien",
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
    if _contains_any(
        value,
        (
            "tro cap xa hoi",
            "ho tro chi phi hoc tap",
            "ho tro chi phi dao tao",
            "ho tro sinh hoat phi",
        ),
    ) or (
        "sinh vien su pham" in value
        and _contains_any(value, ("boi hoan", "cong tac trong nganh giao duc", "chi tra"))
    ):
        return QueryIntent.SOCIAL_SUPPORT

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
            "duoc giam",
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

    if "che do hoc phi" in value and _contains_any(
        value,
        ("duoc huong", "co duoc", "thuoc dien", "nhu the nao", "the nao"),
    ):
        return QueryIntent.EXEMPTION_POLICY

    if (
        has_exemption
        and not _contains_any(
            value,
            ("con phai dong", "con dong bao nhieu", "sau mien giam", "tinh tien phai dong"),
        )
        and _contains_any(
            value,
            (
                "duoc giam",
                "co duoc xet",
                "ky luat",
                "nhieu dien",
                "cung luc",
                "het han",
                "gia han",
                "tiep tuc",
                "lam gi",
                "tinh nhu the nao",
            ),
        )
    ):
        return QueryIntent.EXEMPTION_POLICY

    if _contains_any(
        value,
        (
            "hoc lai",
            "ngoai thoi gian thiet ke",
            "ngoai gio hanh chinh",
            "cham tien do",
            "he so hoc phi",
            "bo sung kien thuc",
            "vua lam vua hoc",
            "vlvh",
            "dao tao tu xa",
        ),
    ) and (has_tuition or _contains_any(value, ("hoc lai", "he so"))):
        return QueryIntent.ACTUAL_TUITION

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
        and "may tinh hoc phi" not in value
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


_PROTECTED_REWRITE_ENTITIES = (
    ("nhcsxh", "ngan hang chinh sach xa hoi"),
    ("vietinbank",),
    ("clc", "chat luong cao"),
    ("tien tien",),
    ("dai tra", "chuong trinh chuan", "he chuan"),
    ("mien giam", "co so tinh mien giam", "lam co so de tinh mien giam"),
    ("khuyen khich hoc tap",),
    ("hoc bong tai tro", "hoc bong doanh nghiep", "doanh nghiep ben ngoai"),
    ("scc",),
    ("vallet",),
    ("panasonic",),
    ("luong van can",),
    ("shinhan",),
    ("scic",),
    ("thap sang niem tin",),
)

_REWRITE_META_PHRASES = (
    "toi khong",
    "xin loi",
    "khong the",
    "dua tren",
    "cau tra loi",
)

_REWRITE_FILLER_TOKENS = {
    "ai",
    "bao",
    "cai",
    "cho",
    "chuong",
    "con",
    "cua",
    "do",
    "duoc",
    "gi",
    "hay",
    "khoa",
    "la",
    "mot",
    "muc",
    "nganh",
    "nhieu",
    "nhu",
    "sao",
    "the",
    "thi",
    "trinh",
    "vay",
    "ve",
}


def _contains_entity(text: str, aliases: tuple[str, ...]) -> bool:
    return any(re.search(rf"(?:^| ){re.escape(alias)}(?: |$)", text) for alias in aliases)


def _canonical_rewrite_tokens(text: str) -> set[str]:
    value = _normalise(text)
    replacements = (
        (("cong nghe thong tin", "cntt"), "entitycntt"),
        (("chat luong cao", "clc"), "entityclc"),
        (("giao duc quoc phong va an ninh", "giao duc quoc phong", "gdqp"), "entitygdqp"),
    )
    for aliases, canonical in replacements:
        for alias in aliases:
            value = re.sub(rf"(?:^| ){re.escape(alias)}(?= |$)", f" {canonical}", value)
    value = re.sub(r"\b(?:khoa|k)\s*([4-9]\d)\b", r" cohort\1 ", value)
    return {
        token
        for token in value.split()
        if token not in _REWRITE_FILLER_TOKENS and not token.isdigit()
    }


def validate_rewritten_query(
    original_query: str,
    rewritten_query: str,
    previous_user_query: str | None,
) -> tuple[bool, str]:
    """Reject rewrites that add facts or change the user's business intent."""

    candidate = rewritten_query.strip().strip('"').strip("'")
    if not candidate:
        return False, "empty"
    if "\n" in candidate or "\r" in candidate:
        return False, "multiline"
    if len(candidate) > 320:
        return False, "too_long"

    candidate_normalised = _normalise(candidate)
    if _contains_any(candidate_normalised, _REWRITE_META_PHRASES):
        return False, "answer_or_meta_text"

    allowed_text = " ".join(
        part for part in (previous_user_query, original_query) if part
    )
    allowed_normalised = _normalise(allowed_text)
    for aliases in _PROTECTED_REWRITE_ENTITIES:
        if _contains_entity(candidate_normalised, aliases) and not _contains_entity(
            allowed_normalised, aliases
        ):
            return False, f"added_entity:{aliases[0]}"

    candidate_numbers = set(re.findall(r"\d+", candidate))
    allowed_numbers = set(re.findall(r"\d+", allowed_text))
    if not candidate_numbers.issubset(allowed_numbers):
        return False, "added_number"

    base_intent = _classify_one(original_query)
    if base_intent in {QueryIntent.OTHER, QueryIntent.AMBIGUOUS_TUITION}:
        base_intent = _classify_one(previous_user_query)
    candidate_intent = _classify_one(candidate)
    if (
        base_intent not in {QueryIntent.OTHER, QueryIntent.AMBIGUOUS_TUITION}
        and candidate_intent != base_intent
    ):
        return False, "changed_intent"

    allowed_tokens = _canonical_rewrite_tokens(allowed_text)
    added_tokens = _canonical_rewrite_tokens(candidate) - allowed_tokens
    if added_tokens:
        return False, f"added_terms:{','.join(sorted(added_tokens))}"
    return True, "accepted"


def classify_query_intent(
    original_query: str,
    rewritten_query: str | None = None,
) -> QueryRoutingDecision:
    """Prefer a clear original intent, otherwise classify a validated rewrite."""

    original_year = _extract_academic_year(original_query)
    original_intent = _classify_one(original_query)
    if original_intent not in {QueryIntent.AMBIGUOUS_TUITION, QueryIntent.OTHER}:
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
    if decision.intent == QueryIntent.SOCIAL_SUPPORT:
        return (
            RetrievalLane(
                name="social_support",
                domain="social_support",
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
    if decision.intent == QueryIntent.SOCIAL_SUPPORT:
        return (
            "Chỉ dùng tài liệu thuộc nhóm TRỢ CẤP VÀ HỖ TRỢ SINH VIÊN; không lấy "
            "học bổng, vay vốn hoặc bảng học phí để thay thế."
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
