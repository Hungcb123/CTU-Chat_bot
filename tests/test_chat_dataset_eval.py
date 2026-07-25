import re
import unittest

from scripts.evaluate_chat_dataset import (
    DEFAULT_DATASET,
    parse_dataset,
    score_answer,
)


class ChatDatasetEvaluationTests(unittest.TestCase):
    def test_parse_all_100_cases(self):
        cases = parse_dataset(DEFAULT_DATASET)
        self.assertEqual(len(cases), 100)
        self.assertEqual([case.case_id for case in cases], list(range(1, 101)))
        self.assertEqual(cases[0].expected_sources, ("mghp.md",))
        self.assertIn("Học bổng", cases[-1].category)

    def test_questions_do_not_require_legal_document_numbers(self):
        cases = parse_dataset(DEFAULT_DATASET)
        banned = re.compile(
            r"\b(?:quyết định|nghị định|qđ(?:-ttg)?|nđ)\b",
            re.IGNORECASE,
        )
        violations = [case.case_id for case in cases if banned.search(case.question)]
        self.assertEqual(violations, [])

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
        self.assertIn("money:695000", result.missing_facts)

    def test_equivalent_date_formats_match(self):
        result = score_answer(
            "Hạn cuối là ngày 29/4/2026",
            "Hồ sơ được nhận đến hết ngày 29-04-2026.",
        )
        self.assertEqual(result.numeric_recall, 1.0)

    def test_abstention_cannot_pass_from_query_term_overlap(self):
        result = score_answer(
            "Không áp dụng miễn giảm học phí khi sinh viên học lưu ban",
            "Tôi không tìm thấy thông tin sinh viên học lưu ban có được miễn giảm "
            "học phí hay không trong tài liệu hiện có.",
        )
        self.assertTrue(result.abstained)
        self.assertFalse(result.passed)

    def test_equivalent_alternative_amount_passes(self):
        result = score_answer(
            "Mức học phí là 6.000.000 đồng/học kỳ "
            "(hoặc 12.000.000 đồng/năm học)",
            "Mức học phí là 6 triệu đồng cho mỗi học kỳ.",
        )
        self.assertEqual(result.numeric_recall, 1.0)
        self.assertTrue(result.passed)

    def test_correct_numeric_answer_survives_unrelated_abstention(self):
        result = score_answer(
            "Tối đa 695.000 đồng/tín chỉ",
            "Mức tối đa là 695.000 đồng/tín chỉ. Tôi không tìm thấy thông tin "
            "về mức làm cơ sở tính miễn giảm.",
        )
        self.assertFalse(result.abstained)
        self.assertTrue(result.passed)

    def test_context_year_does_not_hide_abstention(self):
        result = score_answer(
            "Chỉ cần giấy chứng nhận hộ nghèo năm 2025",
            "Tôi không tìm thấy thông tin cụ thể về đợt năm 2025 trong tài liệu.",
        )
        self.assertTrue(result.abstained)
        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
