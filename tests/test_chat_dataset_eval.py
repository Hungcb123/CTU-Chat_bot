import unittest

from scripts.evaluate_chat_dataset import (
    DEFAULT_DATASET,
    parse_dataset,
    score_answer,
)


class ChatDatasetEvaluationTests(unittest.TestCase):
    def test_parse_all_80_cases(self):
        cases = parse_dataset(DEFAULT_DATASET)
        self.assertEqual(len(cases), 80)
        self.assertEqual(cases[0].case_id, 1)
        self.assertEqual(cases[-1].case_id, 80)
        self.assertEqual(cases[0].expected_sources, ("mghp.md",))
        self.assertIn("Học bổng", cases[-1].category)

    def test_correct_numeric_paraphrase_passes(self):
        result = score_answer(
            "Mức hưởng là 6.000.000 đồng/học kỳ",
            "Sinh viên được nhận 6 triệu đồng cho mỗi học kỳ.",
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.numeric_recall, 1.0)

    def test_wrong_amount_fails_numeric_gate(self):
        result = score_answer(
            "Mức học phí là 695.000 đồng/tín chỉ",
            "Mức học phí là 451.000 đồng cho một tín chỉ.",
        )
        self.assertFalse(result.passed)
        self.assertIn("num:695000", result.missing_facts)

    def test_equivalent_date_formats_match(self):
        result = score_answer(
            "Hạn cuối là ngày 29/4/2026",
            "Hồ sơ được nhận đến hết ngày 29-04-2026.",
        )
        self.assertEqual(result.numeric_recall, 1.0)


if __name__ == "__main__":
    unittest.main()
