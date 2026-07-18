import unittest

from app.services.tuition_catalog import TuitionRateCatalog


class TuitionRateCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = TuitionRateCatalog.load()

    def test_cntt_clc_k49_returns_exact_structured_rates(self):
        result = self.catalog.lookup("Học phí ngành CNTT CLC K49 là bao nhiêu?")
        self.assertEqual(result.status, "found")
        self.assertIn("36.000.000 đồng", result.message)
        self.assertIn("1.254.000 đồng", result.message)
        self.assertIn("441.000 đồng", result.message)
        self.assertIn("MucHocPhi_ChatLuongCao_TienTien.md", result.message)

    def test_cntt_standard_k49_defaults_to_standard_program(self):
        result = self.catalog.lookup("Ngành CNTT K49 học phí bao nhiêu?")
        self.assertEqual(result.status, "found")
        self.assertIn("832.000 đồng", result.message)
        self.assertNotIn("1.254.000 đồng", result.message)

    def test_cntt_standard_k52_returns_course_and_credit_rates(self):
        result = self.catalog.lookup("Học phí thực tế CNTT đại trà khóa 52")
        self.assertEqual(result.status, "found")
        self.assertIn("150.300.000 đồng", result.message)
        self.assertIn("966.000 đồng", result.message)

    def test_policy_query_does_not_trigger_actual_lookup(self):
        result = self.catalog.lookup("Ai được miễn giảm học phí và cần hồ sơ gì?")
        self.assertEqual(result.status, "not_applicable")

    def test_missing_cohort_requests_clarification(self):
        result = self.catalog.lookup("Học phí ngành CNTT CLC là bao nhiêu?")
        self.assertEqual(result.status, "needs_clarification")

    def test_general_common_k52_does_not_require_major(self):
        result = self.catalog.lookup("Học phí chung của K52 là bao nhiêu?")
        self.assertEqual(result.status, "found")
        self.assertIn("695.000 đồng", result.message)
        self.assertIn("Khối kiến thức đại cương chung", result.message)
        self.assertNotIn("966.000 đồng", result.message)

    def test_safe_rewrite_may_fill_missing_major(self):
        self.assertTrue(
            self.catalog.rewrite_is_safe_for_lookup(
                "Vậy K52 thì sao?",
                "Học phí thực tế ngành Công nghệ thông tin đại trà khóa 52 là bao nhiêu?",
            )
        )

    def test_rewrite_cannot_inject_exemption_intent(self):
        self.assertFalse(
            self.catalog.rewrite_is_safe_for_lookup(
                "Ngành CNTT K49 học phí bao nhiêu?",
                "Mức làm cơ sở tính miễn giảm ngành CNTT khóa 49 là bao nhiêu?",
            )
        )


if __name__ == "__main__":
    unittest.main()
