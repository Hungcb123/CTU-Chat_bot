import json
import unittest
from pathlib import Path

from scripts.run_tool_calling_experiment import _same_value, evaluate_case, summarize


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "tool_calling_experiment.json"


class ToolCallingDatasetTests(unittest.TestCase):
    def test_dataset_has_ten_cases_per_financial_function(self):
        cases = json.loads(DATASET.read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 30)
        self.assertEqual([case["id"] for case in cases], list(range(1, 31)))
        counts = {name: sum(case["function"] == name for case in cases) for name in {
            "tuition_lookup", "scholarship_calculation", "tuition_reduction_calculation"
        }}
        self.assertEqual(counts, {
            "tuition_lookup": 10,
            "scholarship_calculation": 10,
            "tuition_reduction_calculation": 10,
        })
        for case in cases:
            self.assertTrue(case["query"])
            self.assertTrue(case["expected_contains"])
            self.assertIn("expected_tool", case)

    def test_evaluate_case_separates_selection_from_result_correctness(self):
        case = {
            "id": 1,
            "function": "scholarship_calculation",
            "query": "x",
            "expected_tool": "tinh_tien_hoc_bong",
            "expected_args": {"gpa": 3.6, "drl": 90, "khoi_nganh": "CNTT"},
            "expected_contains": ["Xuất sắc", "10.560.000"],
            "expected_not_contains": ["chưa đủ điều kiện"],
        }
        result = evaluate_case(
            case,
            selected_tool="tinh_tien_hoc_bong",
            selected_args={"gpa": 3.6, "drl": 90, "khoi_nganh": "CNTT"},
            output="Học bổng Xuất sắc: 10.560.000 đồng",
        )
        self.assertTrue(result["selection_passed"])
        self.assertTrue(result["arguments_passed"])
        self.assertTrue(result["result_passed"])
        self.assertTrue(result["passed"])

    def test_summary_reports_each_function_independently(self):
        records = [
            {"function": "tuition_lookup", "selection_passed": True, "arguments_passed": True, "result_passed": True, "passed": True},
            {"function": "scholarship_calculation", "selection_passed": False, "arguments_passed": False, "result_passed": False, "passed": False},
        ]
        summary = summarize(records)
        self.assertEqual(summary["overall"]["passed"], 1)
        self.assertEqual(summary["overall"]["total"], 2)
        self.assertEqual(summary["by_function"]["tuition_lookup"]["selection_passed"], 1)

    def test_sector_argument_accepts_a_more_specific_equivalent_label(self):
        self.assertTrue(_same_value("Kinh doanh", "Kinh doanh và quản lý"))

    def test_empty_actual_argument_does_not_match_expected_text(self):
        case = {
            "id": 19,
            "function": "scholarship_calculation",
            "query": "Em học chương trình chất lượng cao khóa 51.",
            "expected_tool": "tinh_tien_hoc_bong",
            "expected_args": {"gpa": 3.3, "drl": 85, "khoi_nganh": "chất lượng cao khóa 51"},
            "expected_contains": ["13.600.000 đồng"],
        }
        result = evaluate_case(
            case,
            selected_tool="tinh_tien_hoc_bong",
            selected_args={"gpa": 3.3, "drl": 85, "khoi_nganh": ""},
            output="13.600.000 đồng",
        )
        self.assertFalse(result["arguments_passed"])
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
