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

    def test_course_name_lookup_does_not_require_major(self):
        result = self.catalog.lookup("Môn Năng lực số Khóa 51 học phí bao nhiêu một tín chỉ?")
        self.assertEqual(result.status, "found")
        self.assertIn("Năng lực số", result.message)
        self.assertIn("695.000 đồng", result.message)
        self.assertTrue(all(record["course_name"] == "Năng lực số" for record in result.records))

    def test_course_alias_lookup_finds_gdqp_record(self):
        result = self.catalog.lookup("GDQP K51 bao nhiêu tiền một tín chỉ?")
        self.assertEqual(result.status, "found")
        self.assertIn("Giáo dục Quốc phòng và An ninh", result.message)
        self.assertIn("695.000 đồng", result.message)

    def test_compound_course_names_accept_each_natural_name(self):
        cases = (
            ("Pháp luật đại cương K51 học phí bao nhiêu?", "Pháp luật đại cương"),
            ("Anh văn căn bản K51 học phí bao nhiêu?", "Anh văn hoặc Pháp văn căn bản"),
        )
        for query, expected_name in cases:
            with self.subTest(query=query):
                result = self.catalog.lookup(query)
                self.assertEqual(result.status, "found")
                self.assertIn(expected_name, result.message)

    def test_special_rule_lookup_returns_matching_multiplier(self):
        result = self.catalog.lookup(
            "Khóa 51 học lại ngoài thời gian thiết kế thì học phí nhân hệ số mấy?"
        )
        self.assertEqual(result.status, "found")
        self.assertIn("1,3 lần", result.message)
        self.assertIn("MucHocPhi_QuyDinhChung.md", result.message)

    def test_master_after_hours_rule_returns_multiplier(self):
        result = self.catalog.lookup(
            "Học viên cao học học ngoài giờ hành chính bị nhân hệ số học phí thế nào?"
        )
        self.assertEqual(result.status, "found")
        self.assertIn("1,5 lần", result.message)

    def test_rule_lookup_defaults_unspecified_program_to_standard(self):
        result = self.catalog.lookup(
            "Học lại môn ngoài thời gian thiết kế chương trình đối với Khóa 52 bị nhân hệ số bao nhiêu?"
        )
        self.assertEqual(result.status, "found")
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records[0]["program_type"], "standard")

    def test_remaining_special_rule_shapes_are_supported(self):
        cases = (
            ("Học phí tốt nghiệp chậm tiến độ thạc sĩ tính thế nào?", "0,5 lần"),
            ("Hệ VLVH nếu lớp dưới 30 sinh viên thì hệ số tối đa bao nhiêu?", "1,5 lần"),
            ("Đào tạo từ xa nếu lớp dưới 25 sinh viên thì hệ số tối đa bao nhiêu?", "1,5 lần"),
            ("Học bổ sung kiến thức dự thi thạc sĩ tối đa bao nhiêu?", "695.000 đồng"),
        )
        for query, expected in cases:
            with self.subTest(query=query):
                result = self.catalog.lookup(query)
                self.assertEqual(result.status, "found")
                self.assertIn(expected, result.message)

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
