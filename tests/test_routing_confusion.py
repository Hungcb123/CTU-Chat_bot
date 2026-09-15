"""Routing confusion tests — boundary cases from PLAN_cai_thien §2.

Each test encodes a query that historically confused the deterministic router
or the LLM supervisor, plus a ``repair_route_decision`` round-trip to verify
that the orchestration contract repairs cross-domain misrouting.
"""

import unittest

from app.services.query_intent import QueryIntent, classify_query_intent
from app.services.orchestration_contract import (
    owner_for_intent,
    repair_route_decision,
)


class RoutingConfusionTests(unittest.TestCase):
    """Confusion boundaries that the plan explicitly requires coverage for."""

    # ── classify_query_intent confusion boundaries ──────────────────

    def test_su_pham_sinh_hoat_phi_is_social_support(self):
        """Sinh viên sư phạm → social_support, NOT actual_tuition."""
        result = classify_query_intent(
            "Sinh viên sư phạm được hỗ trợ sinh hoạt phí thế nào?"
        )
        self.assertEqual(result.intent, QueryIntent.SOCIAL_SUPPORT)

    def test_su_pham_hoc_phi_is_actual_tuition(self):
        """Học phí ngành sư phạm → actual_tuition (real fee lookup)."""
        result = classify_query_intent(
            "Học phí ngành sư phạm Toán bao nhiêu?"
        )
        self.assertEqual(result.intent, QueryIntent.ACTUAL_TUITION)

    def test_vay_tien_dong_hoc_phi_is_student_loan(self):
        """'Vay tiền đóng học phí' → student_loan, NOT actual_tuition."""
        result = classify_query_intent(
            "Em muốn vay tiền đóng học phí theo NHCSXH"
        )
        self.assertEqual(result.intent, QueryIntent.STUDENT_LOAN)

    def test_hoc_bong_tai_tro_panasonic_is_scholarship(self):
        """Học bổng tài trợ Panasonic → scholarship, NOT calculation."""
        result = classify_query_intent(
            "Học bổng Panasonic yêu cầu hồ sơ gì?"
        )
        self.assertEqual(result.intent, QueryIntent.SCHOLARSHIP)

    def test_hoc_bong_scic_is_scholarship(self):
        """Học bổng SCIC → scholarship."""
        result = classify_query_intent(
            "Học bổng SCIC tài trợ sinh viên ngành nào?"
        )
        self.assertEqual(result.intent, QueryIntent.SCHOLARSHIP)

    def test_le_phi_xet_tuyen_is_other(self):
        """Lệ phí xét tuyển → other, NOT actual_tuition."""
        result = classify_query_intent(
            "Lệ phí xét tuyển của trường là bao nhiêu?"
        )
        self.assertEqual(result.intent, QueryIntent.OTHER)

    def test_mien_thi_is_academic_rules(self):
        """Miễn thi học phần → academic_rules, NOT academic_program."""
        result = classify_query_intent(
            "Sinh viên được miễn thi học phần nào?"
        )
        self.assertEqual(result.intent, QueryIntent.ACADEMIC_RULES)

    def test_vlvh_hoc_phi_is_actual_tuition(self):
        """VLVH + học phí → actual_tuition, NOT other."""
        result = classify_query_intent(
            "Mức học phí VLVH ngành CNTT khóa 52?"
        )
        self.assertEqual(result.intent, QueryIntent.ACTUAL_TUITION)

    def test_bao_luu_is_academic_rules(self):
        """Bảo lưu kết quả → academic_rules."""
        result = classify_query_intent(
            "Điều kiện bảo lưu kết quả học tập?"
        )
        self.assertEqual(result.intent, QueryIntent.ACADEMIC_RULES)

    def test_vay_von_nhcsxh_is_student_loan(self):
        """Vay vốn NHCSXH → student_loan."""
        result = classify_query_intent(
            "Em muốn vay vốn ngân hàng chính sách xã hội"
        )
        self.assertEqual(result.intent, QueryIntent.STUDENT_LOAN)

    # ── repair_route_decision cross-domain corrections ──────────────

    def test_repair_loan_mislabelled_as_financial(self):
        """LLM says financial/actual_tuition but query is about vay tiền."""
        result = repair_route_decision(
            "Em muốn vay tiền đóng học phí theo NHCSXH",
            "financial",
            "actual_tuition",
        )
        self.assertTrue(result.repaired)
        self.assertEqual(result.agent, "general")
        self.assertEqual(result.intent, QueryIntent.STUDENT_LOAN)

    def test_repair_scholarship_mislabelled_as_general(self):
        """LLM says general/other but query is about học bổng Vallet."""
        result = repair_route_decision(
            "Điều kiện nhận học bổng Vallet?",
            "general",
            "scholarship",
        )
        # agent should be repaired to scholarship (invalid_agent_intent_pair)
        self.assertEqual(result.agent, "scholarship")

    def test_repair_does_not_override_with_other(self):
        """Plan rule: repair must NOT override with other/ambiguous_tuition."""
        result = repair_route_decision(
            "Học phí trường mình bao nhiêu?",
            "financial",
            "ambiguous_tuition",
        )
        # ambiguous_tuition owner is financial, so no repair needed
        self.assertFalse(result.repaired)
        self.assertEqual(result.agent, "financial")

    def test_repair_social_support_from_financial(self):
        """Sinh viên sư phạm sinh hoạt phí → should repair to general."""
        result = repair_route_decision(
            "Sinh viên sư phạm được hỗ trợ sinh hoạt phí thế nào?",
            "financial",
            "actual_tuition",
        )
        self.assertTrue(result.repaired)
        self.assertEqual(result.agent, "general")
        self.assertEqual(result.intent, QueryIntent.SOCIAL_SUPPORT)


if __name__ == "__main__":
    unittest.main()
