"""Single machine-readable routing and tool ownership contract."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from app.services.evaluation_contract import normalize_text
from app.services.query_intent import QueryIntent, classify_query_intent


@dataclass(frozen=True)
class IntentPolicy:
    owner: str
    lanes: tuple[str, ...]
    allowed_tools: tuple[str, ...]
    positive_triggers: tuple[str, ...] = ()
    exclusions: tuple[str, ...] = ()


ACADEMIC_TOOLS = (
    "tra_cuu_nganh",
    "so_sanh_nganh",
    "tim_nganh",
    "xem_chuoi_tien_quyet",
    "mon_chung_giua_nganh",
    "tim_nganh_co_mon",
)
FINANCIAL_TOOLS = (
    "tra_cuu_hoc_phi_graph",
    "tra_cuu_co_so_mien_giam_graph",
    "tra_cuu_quy_dinh_hoc_phi",
    "tinh_toan_hoc_phi",
)
SCHOLARSHIP_TOOLS = ("tinh_tien_hoc_bong",)


INTENT_POLICIES: Mapping[QueryIntent, IntentPolicy] = {
    QueryIntent.ACTUAL_TUITION: IntentPolicy(
        "financial", ("actual_tuition",), FINANCIAL_TOOLS,
        ("hoc phi", "muc thu", "vua lam vua hoc", "vlvh"),
    ),
    QueryIntent.AMBIGUOUS_TUITION: IntentPolicy(
        "financial", ("actual_tuition", "exemption_basis"), FINANCIAL_TOOLS,
    ),
    QueryIntent.EXEMPTION_BASIS: IntentPolicy(
        "financial", ("exemption_basis",), FINANCIAL_TOOLS,
        ("co so tinh mien giam", "muc tran mien giam"),
    ),
    QueryIntent.EXEMPTION_POLICY: IntentPolicy(
        "financial", ("exemption_policy",), FINANCIAL_TOOLS,
        ("doi tuong duoc mien", "ho so mien giam", "giam 70"),
    ),
    QueryIntent.CALCULATION: IntentPolicy(
        "financial", ("actual_tuition", "exemption_basis", "exemption_policy"), FINANCIAL_TOOLS,
        ("con dong bao nhieu", "tinh hoc phi", "tinh so tien"),
    ),
    QueryIntent.BOTH: IntentPolicy(
        "financial", ("actual_tuition", "exemption_basis"), FINANCIAL_TOOLS,
        ("ca hai muc", "phan biet hoc phi"),
    ),
    QueryIntent.SCHOLARSHIP: IntentPolicy(
        "scholarship", ("scholarship",), SCHOLARSHIP_TOOLS,
        ("hoc bong", "vallet", "scic", "shinhan", "panasonic"),
    ),
    QueryIntent.STUDENT_LOAN: IntentPolicy(
        "general", ("student_loan",), (),
        ("vay von", "vay tien", "nhcsxh", "vietinbank"),
    ),
    QueryIntent.SOCIAL_SUPPORT: IntentPolicy(
        "general", ("social_support",), (),
        ("tro cap xa hoi", "ho tro sinh hoat phi", "sinh vien su pham"),
    ),
    QueryIntent.ACADEMIC_PROGRAM: IntentPolicy(
        "academic", ("academic_program",), ACADEMIC_TOOLS,
        ("chuong trinh dao tao", "ma nganh", "mon tien quyet", "so sanh nganh"),
    ),
    QueryIntent.ACADEMIC_RULES: IntentPolicy(
        "general", ("academic_rules",), (),
        ("mien thi", "bao luu", "canh bao hoc vu", "xet tot nghiep"),
    ),
    QueryIntent.OTHER: IntentPolicy("general", ("default",), ()),
}

SPECIALIST_TOOLS: Mapping[str, tuple[str, ...]] = {
    "academic": ACADEMIC_TOOLS,
    "financial": FINANCIAL_TOOLS,
    "scholarship": SCHOLARSHIP_TOOLS,
    "general": (),
}


@dataclass(frozen=True)
class RouteRepairResult:
    raw_agent: str
    raw_intent: str
    agent: str
    intent: QueryIntent
    repaired: bool
    reason: str


def owner_for_intent(intent: QueryIntent | str) -> str:
    try:
        parsed = intent if isinstance(intent, QueryIntent) else QueryIntent(intent)
    except ValueError:
        return "general"
    return INTENT_POLICIES[parsed].owner


def _has_strong_signal(query: str, intent: QueryIntent) -> bool:
    if intent in {QueryIntent.OTHER, QueryIntent.AMBIGUOUS_TUITION}:
        return False
    value = normalize_text(query)
    policy = INTENT_POLICIES[intent]
    return any(normalize_text(trigger) in value for trigger in policy.positive_triggers)


def repair_route_decision(query: str, raw_agent: str, raw_intent: str) -> RouteRepairResult:
    try:
        llm_intent = QueryIntent(raw_intent)
    except ValueError:
        llm_intent = QueryIntent.OTHER
    llm_owner = owner_for_intent(llm_intent)
    rule_intent = classify_query_intent(query).intent

    if os.getenv("ROUTING_REPAIR_ENABLED", "true").lower() not in {"true", "1", "yes"}:
        return RouteRepairResult(raw_agent, raw_intent, raw_agent, llm_intent, False, "disabled")
    if _has_strong_signal(query, rule_intent) and rule_intent != llm_intent:
        return RouteRepairResult(
            raw_agent, raw_intent, owner_for_intent(rule_intent), rule_intent, True,
            f"strong_rule:{rule_intent.value}",
        )
    if raw_agent != llm_owner:
        return RouteRepairResult(
            raw_agent, raw_intent, llm_owner, llm_intent, True, "invalid_agent_intent_pair",
        )
    return RouteRepairResult(raw_agent, raw_intent, raw_agent, llm_intent, False, "accepted")


def tool_gate_prompt(agent: str) -> str:
    tools = ", ".join(SPECIALIST_TOOLS.get(agent, ())) or "không có công cụ"
    common = (
        "Chỉ gọi đúng MỘT công cụ khi câu hỏi có đủ tham số bắt buộc và hợp lệ. "
        "Không bịa tham số còn thiếu. GPA phải trong [0,4], điểm rèn luyện trong [0,100], "
        "phần trăm trong [0,100], và các số tiền không âm. "
    )
    return f"Bạn là cổng công cụ của specialist {agent}. Công cụ được phép: {tools}. {common}"
