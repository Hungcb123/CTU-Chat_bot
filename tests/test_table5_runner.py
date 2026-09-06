"""Regression tests for Table 5 runner API error boundaries."""

import unittest
from unittest.mock import patch

from langchain_core.documents import Document

import Test_Ragas.test_table5_ragas as table5_runner
from Test_Ragas.table5_experiment import BenchmarkCase, QuotaPausedError


class Table5RunnerTests(unittest.TestCase):
    def test_t1_t7_ragas_quota_error_pauses_in_evaluate_one(self):
        """T1-T7: evaluate_one converts a wrapped Gemini 429 into a safe pause."""
        runner = table5_runner.Table5Runner.__new__(table5_runner.Table5Runner)
        runner.judge = object()
        runner.judge_embeddings = object()
        case = BenchmarkCase("1", "question", "category", "reference")

        with patch.object(
            table5_runner,
            "evaluate",
            side_effect=RuntimeError("429 RESOURCE_EXHAUSTED"),
        ):
            with self.assertRaises(QuotaPausedError):
                runner.evaluate_one(case, "answer", [Document(page_content="evidence")])


if __name__ == "__main__":
    unittest.main()
