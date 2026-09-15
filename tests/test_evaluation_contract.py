import unittest

from app.services.evaluation_contract import (
    MetricState,
    arguments_match,
    evaluate_output,
    validate_unique_case_ids,
)


class EvaluationContractTests(unittest.TestCase):
    def test_numeric_and_cohort_coercion(self):
        self.assertTrue(arguments_match(
            {"khoa": "K52", "phan_tram_giam": 70},
            {"khoa": "khóa 52", "phan_tram_giam": "70"},
        ))

    def test_alias_and_containment(self):
        self.assertTrue(arguments_match(
            {"doi_tuong": "VLVH"}, {"doi_tuong": "hệ vừa làm vừa học"}
        ))
        self.assertTrue(arguments_match(
            {"tieu_chi": "nông nghiệp"},
            {"tieu_chi": "ngành liên quan đến nông nghiệp"},
        ))

    def test_symmetric_tools_accept_swapped_entities(self):
        self.assertTrue(arguments_match(
            {"nganh_1": "CNTT", "nganh_2": "Trí tuệ nhân tạo"},
            {"nganh_1": "Trí tuệ nhân tạo", "nganh_2": "CNTT"},
            tool_name="so_sanh_nganh",
        ))

    def test_missing_oracle_is_not_evaluated(self):
        result = evaluate_output({"expected_contains": []}, "anything")
        self.assertEqual(result.state, MetricState.NOT_EVALUATED)
        self.assertIsNone(result.passed)

    def test_duplicate_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_unique_case_ids([{"id": "F14"}, {"id": "F14"}])

    def test_khoi_nganh_alias(self):
        """Khối IV ↔ Khối ngành IV alias equivalence."""
        self.assertTrue(arguments_match(
            {"ten_nganh_hoac_khoi": "Khối IV"},
            {"ten_nganh_hoac_khoi": "Khối ngành IV"},
        ))
        self.assertTrue(arguments_match(
            {"ten_nganh_hoac_khoi": "Khối ngành IV"},
            {"ten_nganh_hoac_khoi": "khối 4"},
        ))

    def test_free_text_normalized_containment(self):
        """Free text should match via normalized containment."""
        self.assertTrue(arguments_match(
            {"tieu_chi": "công nghệ thông tin"},
            {"tieu_chi": "Ngành Công nghệ Thông tin và Truyền thông"},
        ))

    def test_forbidden_token_blocks_output(self):
        """expected_not_contains blocks the answer even when required passes."""
        result = evaluate_output(
            {"expected_contains": ["CTU"], "expected_not_contains": ["Harvard"]},
            "CTU và Harvard đều có ngành CNTT.",
        )
        self.assertEqual(result.state, MetricState.FAIL)
        self.assertFalse(result.passed)

    def test_expected_response_any_matches_one(self):
        """Any-of oracle passes when at least one alternative matches."""
        result = evaluate_output(
            {"expected_response_any": ["Trí tuệ nhân tạo", "AI"]},
            "Ngành Trí tuệ nhân tạo có 150 tín chỉ.",
        )
        self.assertEqual(result.state, MetricState.PASS)
        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
