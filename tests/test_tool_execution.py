import unittest

from app.services.tool_execution import (
    ToolOutcome,
    classify_tool_outcome,
    evidence_envelope,
    recommend_required_tool,
    validate_tool_arguments,
)


class ToolExecutionTests(unittest.TestCase):
    def test_normalizes_and_validates(self):
        result = validate_tool_arguments(
            "tra_cuu_hoc_phi_graph", {"ten_nganh": "CNTT", "khoa": "khóa 52"}
        )
        self.assertTrue(result.valid)
        self.assertEqual(result.normalized_args["khoa"], "K52")

    def test_rejects_invalid_ranges(self):
        result = validate_tool_arguments("tinh_tien_hoc_bong", {"gpa": 4.5, "drl": 95})
        self.assertFalse(result.valid)
        self.assertIn("out_of_range:gpa", result.errors)

    def test_recommends_logistics_lookup_without_cohort(self):
        self.assertEqual(
            recommend_required_tool(
                "academic", "Chương trình đào tạo ngành Logistics có bao nhiêu tín chỉ?"
            ),
            "tra_cuu_nganh",
        )

    def test_outcome_and_envelope(self):
        self.assertEqual(classify_tool_outcome("Không tìm thấy ngành"), ToolOutcome.VALID_NO_RESULT)
        envelope = evidence_envelope(
            tool_name="tra_cuu_nganh", arguments={"ten_nganh": "CNTT"},
            status=ToolOutcome.FOUND, output="ok",
        )
        self.assertIn('"status": "found"', envelope)

    def test_rejects_duplicate_entities(self):
        """Two identical ngành arguments should be flagged."""
        result = validate_tool_arguments(
            "so_sanh_nganh", {"nganh_1": "CNTT", "nganh_2": "CNTT"}
        )
        self.assertFalse(result.valid)
        self.assertIn("duplicate_entities:nganh_1,nganh_2", result.errors)

    def test_recommends_financial_calculation(self):
        """Financial specialist with 'tính tiền còn đóng' → tinh_toan_hoc_phi."""
        self.assertEqual(
            recommend_required_tool(
                "financial",
                "Học phí thực tế 832000, miễn giảm 538000, giảm 70%. Tính tiền còn đóng."
            ),
            "tinh_toan_hoc_phi",
        )

    def test_recommends_scholarship_calculation(self):
        """Scholarship specialist with GPA + DRL → tinh_tien_hoc_bong."""
        self.assertEqual(
            recommend_required_tool(
                "scholarship",
                "GPA 3.6, điểm rèn luyện 90, ngành CNTT"
            ),
            "tinh_tien_hoc_bong",
        )

    def test_missing_required_argument_detected(self):
        """Missing ten_nganh for tra_cuu_nganh should error."""
        result = validate_tool_arguments("tra_cuu_nganh", {})
        self.assertFalse(result.valid)
        self.assertIn("missing:ten_nganh", result.errors)

    def test_normalize_vlvh_doi_tuong(self):
        """VLVH alias → normalized to VLVH in doi_tuong."""
        from app.services.tool_execution import normalize_tool_arguments
        result = normalize_tool_arguments(
            "tra_cuu_hoc_phi_graph",
            {"ten_nganh": "CNTT", "doi_tuong": "vừa làm vừa học"},
        )
        self.assertEqual(result["doi_tuong"], "VLVH")


if __name__ == "__main__":
    unittest.main()
