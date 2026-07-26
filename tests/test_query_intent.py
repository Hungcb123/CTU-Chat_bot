import unittest

from app.services.query_intent import (
    QueryIntent,
    build_retrieval_lanes,
    classify_query_intent,
    should_rewrite_query,
    validate_rewritten_query,
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

    def test_named_scholarship_without_generic_keyword_uses_scholarship_lane(self):
        self.assert_intent("Mỗi suất SCC trị giá bao nhiêu?", QueryIntent.SCHOLARSHIP)

    def test_social_support_does_not_fall_back_to_all_domains(self):
        decision = classify_query_intent(
            "Sinh viên sư phạm được hỗ trợ sinh hoạt phí bao nhiêu mỗi tháng?"
        )
        self.assertEqual(decision.intent, QueryIntent.SOCIAL_SUPPORT)
        lanes = build_retrieval_lanes(decision)
        self.assertEqual(len(lanes), 1)
        self.assertEqual(lanes[0].domain, "social_support")

    def test_pedagogy_tuition_is_not_mistaken_for_social_support(self):
        self.assert_intent(
            "Sinh viên Sư phạm Toán học K52 đóng học phí bao nhiêu một tín chỉ?",
            QueryIntent.ACTUAL_TUITION,
        )

    def test_tuition_entitlement_routes_to_exemption_policy(self):
        self.assert_intent(
            "Trẻ bị bỏ rơi không có nguồn nuôi dưỡng được hưởng chế độ học phí thế nào?",
            QueryIntent.EXEMPTION_POLICY,
        )

    def test_actual_tuition_rule_does_not_use_ambiguous_balanced_lanes(self):
        self.assert_intent(
            "Khóa 51 học lại ngoài thời gian thiết kế thì học phí nhân hệ số mấy?",
            QueryIntent.ACTUAL_TUITION,
        )

    def test_actual_tuition_rule_without_hoc_phi_keyword(self):
        self.assert_intent(
            "Học lại môn ngoài thời gian thiết kế chương trình đối với Khóa 52 bị nhân hệ số bao nhiêu?",
            QueryIntent.ACTUAL_TUITION,
        )

    def test_khoa_hoc_may_tinh_is_not_mistaken_for_calculation(self):
        self.assert_intent(
            "Khóa 52 ngành Khoa học máy tính học phí bao nhiêu 1 tín chỉ?",
            QueryIntent.ACTUAL_TUITION,
        )

    def test_natural_student_loan_phrases_use_student_loan_lane(self):
        queries = (
            "Lãi suất cho vay mua máy tính học trực tuyến là bao nhiêu?",
            "Thời hạn cho vay tối đa để mua máy tính học trực tuyến là bao lâu?",
            "Sinh viên thuộc hộ nghèo có thể vay tối đa bao nhiêu tiền mỗi tháng để đi học?",
            "Khoản vay sinh viên ngành STEM hỗ trợ tối đa bao nhiêu mỗi tháng?",
        )
        for query in queries:
            with self.subTest(query=query):
                self.assert_intent(query, QueryIntent.STUDENT_LOAN)

    def test_exemption_entitlement_questions_use_policy_lane(self):
        queries = (
            "Sinh viên dân tộc thiểu số được giảm bao nhiêu phần trăm học phí?",
            "Cha bị tai nạn lao động thì sinh viên được giảm bao nhiêu học phí?",
            "Sinh viên bị kỷ luật có được xét miễn giảm học phí không?",
            "Nếu thuộc nhiều diện miễn giảm cùng lúc thì tính như thế nào?",
            "Sổ hộ nghèo hết hạn thì làm gì để tiếp tục miễn giảm học phí?",
        )
        for query in queries:
            with self.subTest(query=query):
                self.assert_intent(query, QueryIntent.EXEMPTION_POLICY)

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

    def test_clear_queries_skip_rewriter(self):
        clear_queries = (
            "Mức vay tối đa để mua máy tính học trực tuyến là bao nhiêu?",
            "Mỗi suất học bổng SCC trị giá bao nhiêu?",
            "Học phí tiến sĩ khóa 2026 là bao nhiêu?",
            "Học phí đào tạo từ xa khóa 2027 là bao nhiêu?",
            "Sinh viên sư phạm được hỗ trợ sinh hoạt phí bao nhiêu?",
        )
        for query in clear_queries:
            with self.subTest(query=query):
                self.assertFalse(should_rewrite_query(query, None))

    def test_only_vague_follow_up_with_user_context_is_rewritten(self):
        self.assertTrue(
            should_rewrite_query(
                "Vậy K52 thì sao?",
                "Học phí ngành CNTT CLC K51 là bao nhiêu?",
            )
        )
        self.assertFalse(should_rewrite_query("Vậy K52 thì sao?", None))

    def test_uncertain_queries_with_history_use_rewriter(self):
        previous = "Học phí ngành CNTT CLC K51 là bao nhiêu?"
        for query in (
            "ngành cntt á",
            "k49",
            "Nếu em chuyển ngành thì có phải bồi hoàn không?",
        ):
            with self.subTest(query=query):
                self.assertTrue(should_rewrite_query(query, previous))

    def test_rewrite_resolves_slot_like_follow_ups(self):
        cases = (
            (
                "ngành cntt á",
                "Học phí của khối ngành đại cương là bao nhiêu?",
                "Học phí ngành Công nghệ thông tin là bao nhiêu?",
            ),
            (
                "k49",
                "Học phí ngành CNTT là bao nhiêu?",
                "Học phí ngành Công nghệ thông tin khóa K49 là bao nhiêu?",
            ),
        )
        for original, previous, rewritten in cases:
            with self.subTest(original=original):
                accepted, reason = validate_rewritten_query(
                    original_query=original,
                    rewritten_query=rewritten,
                    previous_user_query=previous,
                )
                self.assertTrue(accepted, reason)
                decision = classify_query_intent(original, rewritten)
                self.assertEqual(decision.intent, QueryIntent.ACTUAL_TUITION)
                self.assertEqual(decision.classified_from, "rewrite")

    def test_rewrite_rejects_unrelated_entities_numbers_and_intent(self):
        cases = (
            (
                "Mức vay mua máy tính là bao nhiêu?",
                None,
                "Mức vay mua máy tính qua NHCSXH và VietinBank là bao nhiêu?",
            ),
            (
                "Mỗi suất học bổng SCC trị giá bao nhiêu?",
                None,
                "Học bổng SCC và học bổng khuyến khích học tập trị giá bao nhiêu?",
            ),
            (
                "Vậy K52 thì sao?",
                "Học phí CNTT CLC K51 là bao nhiêu?",
                "Học phí CNTT đại trà K52 là 966.000 đồng/tín chỉ?",
            ),
            (
                "Vậy K52 thì sao?",
                "Học phí CNTT CLC K51 là bao nhiêu?",
                "Học phí ngành Khoa học máy tính CLC K52 là bao nhiêu?",
            ),
            (
                "Vậy mức đó thì sao?",
                "Mức miễn giảm học phí GDQP là bao nhiêu?",
                "Học phí thực tế GDQP là bao nhiêu?",
            ),
        )
        for original, previous, rewritten in cases:
            with self.subTest(rewritten=rewritten):
                accepted, _ = validate_rewritten_query(
                    original_query=original,
                    rewritten_query=rewritten,
                    previous_user_query=previous,
                )
                self.assertFalse(accepted)

    def test_rewrite_accepts_entity_preserving_follow_up(self):
        accepted, reason = validate_rewritten_query(
            original_query="Vậy K52 thì sao?",
            rewritten_query="Học phí ngành Công nghệ thông tin chương trình chất lượng cao Khóa 52 là bao nhiêu?",
            previous_user_query="Học phí ngành CNTT CLC K51 là bao nhiêu?",
        )
        self.assertTrue(accepted, reason)

    def test_rewrite_rejects_multiline_or_answer_text(self):
        for rewritten in (
            "Học phí CNTT CLC K52 là bao nhiêu?\nThông tin bổ sung",
            "Dựa trên thông tin trước đó, học phí CNTT CLC K52 là bao nhiêu?",
        ):
            with self.subTest(rewritten=rewritten):
                accepted, _ = validate_rewritten_query(
                    original_query="Vậy K52 thì sao?",
                    rewritten_query=rewritten,
                    previous_user_query="Học phí CNTT CLC K51 là bao nhiêu?",
                )
                self.assertFalse(accepted)


if __name__ == "__main__":
    unittest.main()
