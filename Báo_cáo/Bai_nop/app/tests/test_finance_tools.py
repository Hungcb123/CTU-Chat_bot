import unittest

from app.tools.scholarship import tinh_tien_hoc_bong
from app.tools.tuition import tinh_toan_hoc_phi
from app.tools.tuition_lookup import tra_cuu_hoc_phi


class FinanceToolTests(unittest.TestCase):
    def test_tuition_lookup_tool_cntt_clc_k49(self):
        result = tra_cuu_hoc_phi.invoke({"cau_hoi": "Học phí CNTT CLC K49 là bao nhiêu?"})
        self.assertIn("36.000.000", result)
        self.assertIn("1.254.000", result)
        self.assertIn("441.000", result)

    def test_tuition_lookup_tool_general_common_k52(self):
        result = tra_cuu_hoc_phi.invoke({"cau_hoi": "Học phí chung K52 bao nhiêu?"})
        self.assertIn("695.000", result)
        self.assertNotIn("966.000", result)

    def test_tuition_calculator_70_percent(self):
        result = tinh_toan_hoc_phi.invoke(
            {"gia_hoc_phi_thuc_te": 832000, "muc_tran_mien_giam": 538000, "phan_tram_giam": 70}
        )
        self.assertIn("455.400", result)
        self.assertIn("376.600", result)

    def test_tuition_calculator_100_percent_basis_cap(self):
        result = tinh_toan_hoc_phi.invoke(
            {"gia_hoc_phi_thuc_te": 695000, "muc_tran_mien_giam": 451000, "phan_tram_giam": 100}
        )
        self.assertIn("244.000", result)

    def test_tuition_calculator_rejects_invalid_percentage(self):
        result = tinh_toan_hoc_phi.invoke(
            {"gia_hoc_phi_thuc_te": 832000, "muc_tran_mien_giam": 538000, "phan_tram_giam": 120}
        )
        self.assertIn("Phần trăm giảm phải nằm", result)

    def test_scholarship_tool_excellent_cntt(self):
        result = tinh_tien_hoc_bong.invoke({"gpa": 3.7, "drl": 92, "khoi_nganh": "CNTT"})
        self.assertIn("Xuất sắc", result)
        self.assertIn("10.560.000", result)

    def test_scholarship_tool_good_business(self):
        result = tinh_tien_hoc_bong.invoke({"gpa": 3.3, "drl": 85, "khoi_nganh": "Kinh doanh"})
        self.assertIn("Giỏi", result)
        self.assertIn("7.920.000", result)

    def test_scholarship_tool_rejects_low_gpa(self):
        result = tinh_tien_hoc_bong.invoke({"gpa": 2.4, "drl": 95, "khoi_nganh": "CNTT"})
        self.assertIn("chưa đủ điều kiện", result)


class MvpDatasetTests(unittest.TestCase):
    def test_dataset_has_exactly_30_well_formed_cases(self):
        import json
        from pathlib import Path

        path = Path(__file__).resolve().parents[1] / "data" / "test_dataset_rag.json"
        cases = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 30)
        self.assertEqual([case["id"] for case in cases], list(range(1, 31)))
        self.assertEqual(
            {case["category"] for case in cases},
            {"Học phí", "Miễn giảm học phí", "Vay vốn", "Học bổng khuyến khích"},
        )
        for case in cases:
            self.assertTrue(case["query"])
            self.assertTrue(case["expected_contains"])
            self.assertIn("expected_tool", case)


if __name__ == "__main__":
    unittest.main()
