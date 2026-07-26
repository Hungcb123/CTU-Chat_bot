import re
import unittest

from langchain_core.runnables import RunnableLambda

from scripts.evaluate_chat_dataset import (
    DEFAULT_DATASET,
    ScoreResult,
    parse_dataset,
    score_answer,
)


class FakeJudge:
    def __init__(self, result: ScoreResult | None = None, error: Exception | None = None):
        self.result = result
        self.error = error
        self.prompt = ""

    def with_structured_output(self, _schema):
        def judge(prompt):
            self.prompt = prompt.to_string()
            if self.error is not None:
                raise self.error
            return self.result

        return RunnableLambda(judge)


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

    def test_llm_judge_receives_answers_and_threshold_controls_pass(self):
        judge = FakeJudge(
            ScoreResult(score=0.8, passed=True, reasoning="Mostly correct")
        )

        result = score_answer(
            "Expected policy answer",
            "Actual chatbot answer",
            llm=judge,
            threshold=0.9,
        )

        self.assertEqual(result.score, 0.8)
        self.assertFalse(result.passed)
        self.assertIn("Expected policy answer", judge.prompt)
        self.assertIn("Actual chatbot answer", judge.prompt)

    def test_llm_judge_error_becomes_failed_score(self):
        result = score_answer(
            "Expected",
            "Actual",
            llm=FakeJudge(error=RuntimeError("judge unavailable")),
        )

        self.assertEqual(result.score, 0.0)
        self.assertFalse(result.passed)
        self.assertIn("judge unavailable", result.reasoning)


if __name__ == "__main__":
    unittest.main()
