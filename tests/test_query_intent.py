import unittest

from app.services.query_intent import (
    QueryIntent,
    build_retrieval_lanes,
    classify_query_intent,
)


class QueryIntentTests(unittest.TestCase):
    def assert_intent(self, query: str, expected: QueryIntent, rewrite: str | None = None):
        self.assertEqual(classify_query_intent(query, rewrite).intent, expected)

    def test_actual_tuition_with_exemption_negation(self):
        self.assert_intent(
            "Học phí thực tế của GDQP là bao nhiêu? Tôi không hỏi mức miễn giảm.",
            QueryIntent.ACTUAL_TUITION,
        )

    def test_exemption_basis_with_actual_tuition_negation(self):
        self.assert_intent(
            "Tôi hỏi cơ sở miễn giảm, không hỏi học phí thực tế.",
            QueryIntent.EXEMPTION_BASIS,
        )

    def test_exemption_basis(self):
        self.assert_intent(
            "Mức học phí làm cơ sở để tính miễn giảm của GDQP là bao nhiêu?",
            QueryIntent.EXEMPTION_BASIS,
        )

    def test_short_exemption_amount_is_basis(self):
        self.assert_intent("Khối IV miễn giảm bao nhiêu?", QueryIntent.EXEMPTION_BASIS)

    def test_exemption_policy(self):
        self.assert_intent(
            "Đối tượng nào được miễn giảm học phí và cần hồ sơ gì?",
            QueryIntent.EXEMPTION_POLICY,
        )

    def test_exemption_eligibility_is_policy(self):
        self.assert_intent(
            "Sinh viên hộ nghèo có được miễn học phí không?",
            QueryIntent.EXEMPTION_POLICY,
        )

    def test_percentage_eligibility_is_policy_not_calculation(self):
        self.assert_intent(
            "Đối tượng nào được giảm 70% học phí?",
            QueryIntent.EXEMPTION_POLICY,
        )

    def test_calculation(self):
        self.assert_intent(
            "Em được giảm 70% thì còn phải đóng bao nhiêu?",
            QueryIntent.CALCULATION,
        )

    def test_explicit_tuition_calculation(self):
        self.assert_intent("Tính học phí cho 10 tín chỉ", QueryIntent.CALCULATION)

    def test_both(self):
        self.assert_intent(
            "Phân biệt hai mức học phí thực tế và cơ sở miễn giảm.",
            QueryIntent.BOTH,
        )

    def test_ambiguous(self):
        self.assert_intent(
            "Môn Giáo dục quốc phòng một tín chỉ bao nhiêu tiền?",
            QueryIntent.AMBIGUOUS_TUITION,
        )

    def test_specific_major_program_cohort_defaults_to_actual_tuition(self):
        self.assert_intent(
            "Học phí ngành CNTT CLC K49 là bao nhiêu?",
            QueryIntent.ACTUAL_TUITION,
        )

    def test_specific_major_cohort_does_not_trust_opposite_rewrite(self):
        decision = classify_query_intent(
            "Ngành CNTT K49 học phí bao nhiêu?",
            "Mức làm cơ sở tính miễn giảm của ngành CNTT khóa 49 là bao nhiêu?",
        )
        self.assertEqual(decision.intent, QueryIntent.ACTUAL_TUITION)
        self.assertEqual(decision.classified_from, "original")

    def test_rewrite_resolves_short_follow_up(self):
        decision = classify_query_intent(
            "Vậy mức đó thì sao?",
            "Mức học phí làm cơ sở để tính miễn giảm của môn Giáo dục quốc phòng là bao nhiêu?",
        )
        self.assertEqual(decision.intent, QueryIntent.EXEMPTION_BASIS)
        self.assertEqual(decision.classified_from, "rewrite")

    def test_rewrite_resolves_long_referential_follow_up(self):
        decision = classify_query_intent(
            "Vậy ngành Công nghệ thông tin khóa 52 thì mức đó như thế nào?",
            "Học phí thực tế ngành Công nghệ thông tin đại trà khóa 52 là bao nhiêu?",
        )
        self.assertEqual(decision.intent, QueryIntent.ACTUAL_TUITION)
        self.assertEqual(decision.classified_from, "rewrite")

    def test_academic_year(self):
        decision = classify_query_intent("Học phí thực tế năm học 2026-2027 là bao nhiêu?")
        self.assertEqual(decision.academic_year, "2026-2027")

    def test_scholarship_query_uses_scholarship_intent(self):
        self.assert_intent("Học bổng Vallet cần hồ sơ gì?", QueryIntent.SCHOLARSHIP)

    def test_scholarship_lane_filters_domain(self):
        decision = classify_query_intent("Điều kiện nhận học bổng khuyến khích học tập là gì?")
        lanes = build_retrieval_lanes(decision)
        self.assertEqual(len(lanes), 1)
        self.assertEqual(lanes[0].name, "scholarship")
        self.assertEqual(lanes[0].domain, "scholarship")

    def test_gpa_and_conduct_score_route_to_scholarship(self):
        self.assert_intent(
            "GPA 3.6 và điểm rèn luyện 88 thì em được loại gì?",
            QueryIntent.SCHOLARSHIP,
        )

    def test_student_loan_query_uses_student_loan_intent(self):
        self.assert_intent(
            "Sinh viên muốn vay vốn NHCSXH để đóng học phí cần điều kiện gì?",
            QueryIntent.STUDENT_LOAN,
        )

    def test_student_loan_lane_filters_domain(self):
        decision = classify_query_intent("Thủ tục vay tiền qua VietinBank như thế nào?")
        lanes = build_retrieval_lanes(decision)
        self.assertEqual(len(lanes), 1)
        self.assertEqual(lanes[0].name, "student_loan")
        self.assertEqual(lanes[0].domain, "student_loan")

    def test_stem_loan_without_von_keyword(self):
        self.assert_intent(
            "Lãi suất nợ quá hạn của chương trình vay STEM được tính thế nào?",
            QueryIntent.STUDENT_LOAN,
        )

    def test_clear_other_topic_does_not_inherit_rewrite(self):
        decision = classify_query_intent(
            "Học bổng Vallet cần hồ sơ gì?",
            "Học phí thực tế của ngành Công nghệ thông tin là bao nhiêu?",
        )
        self.assertEqual(decision.intent, QueryIntent.SCHOLARSHIP)
        self.assertEqual(decision.classified_from, "original")

    def test_clear_student_loan_does_not_inherit_tuition_rewrite(self):
        decision = classify_query_intent(
            "Vay vốn NHCSXH để đóng học phí cần hồ sơ gì?",
            "Học phí thực tế của ngành Công nghệ thông tin là bao nhiêu?",
        )
        self.assertEqual(decision.intent, QueryIntent.STUDENT_LOAN)
        self.assertEqual(decision.classified_from, "original")

    def test_clear_intent_does_not_inherit_rewritten_year(self):
        decision = classify_query_intent(
            "Học phí thực tế của GDQP là bao nhiêu?",
            "Học phí thực tế của GDQP năm học 2025-2026 là bao nhiêu?",
        )
        self.assertIsNone(decision.academic_year)

    def test_ambiguous_uses_balanced_lanes(self):
        decision = classify_query_intent("GDQP một tín chỉ bao nhiêu tiền?")
        lanes = build_retrieval_lanes(decision)
        self.assertEqual([lane.fee_kind for lane in lanes], ["actual_tuition", "exemption_basis"])
        self.assertEqual([lane.top_n for lane in lanes], [3, 3])


if __name__ == "__main__":
    unittest.main()
