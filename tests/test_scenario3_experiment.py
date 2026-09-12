import argparse
import unittest

from scripts.run_scenario3_experiment import (
    ROOT,
    arguments_match,
    load_routing_cases,
    macro_f1,
    same_value,
    validate_datasets,
)


class Scenario3DatasetTests(unittest.TestCase):
    def _args(self) -> argparse.Namespace:
        return argparse.Namespace(
            routing_dataset=ROOT / "data" / "Paper" / "150_NATURAL_NO_APPENDIX.csv",
            routing_labels=ROOT / "data" / "scenario3_routing_labels.json",
            tool_dataset=ROOT / "data" / "scenario3_production_tools.json",
            robustness_dataset=ROOT / "data" / "scenario3_robustness_cases.json",
        )

    def test_official_dataset_sizes(self):
        result = validate_datasets(self._args())
        self.assertEqual(result["routing_cases"], 100)
        self.assertEqual(result["tool_cases"], 60)
        self.assertEqual(result["robustness_cases"], 20)

    def test_all_routing_categories_have_targets(self):
        args = self._args()
        cases = load_routing_cases(args.routing_dataset, args.routing_labels)
        self.assertEqual(len({case["category"] for case in cases}), 9)
        self.assertEqual(
            {case["expected_agent"] for case in cases},
            {"academic", "financial", "scholarship", "general"},
        )
        self.assertFalse(any(str(case["id"]).startswith("CDICT") for case in cases))

    def test_known_source_category_mismatches_are_overridden(self):
        args = self._args()
        by_id = {
            str(case["id"]): case
            for case in load_routing_cases(args.routing_dataset, args.routing_labels)
        }
        self.assertEqual(by_id["78"]["expected_intent"], "other")
        self.assertEqual(by_id["R12"]["expected_agent"], "academic")
        self.assertEqual(by_id["R24"]["expected_intent"], "other")


class Scenario3MetricTests(unittest.TestCase):
    def test_value_and_argument_matching(self):
        self.assertTrue(same_value(3.6, 3.6))
        self.assertTrue(same_value("CNTT", "cntt"))
        self.assertTrue(arguments_match({"gpa": 3.6, "drl": 90}, {"gpa": 3.6, "drl": 90}))
        self.assertFalse(arguments_match({"gpa": 3.6, "drl": 90}, {"gpa": 3.6}))

    def test_macro_f1_is_one_for_perfect_routes(self):
        records = [
            {"expected_agent": "academic", "actual_agent": "academic"},
            {"expected_agent": "financial", "actual_agent": "financial"},
            {"expected_agent": "scholarship", "actual_agent": "scholarship"},
            {"expected_agent": "general", "actual_agent": "general"},
        ]
        self.assertEqual(macro_f1(records), 1.0)


if __name__ == "__main__":
    unittest.main()
