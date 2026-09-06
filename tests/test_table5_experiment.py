"""Regression tests for the T1–T7 Table 5 experiment helpers."""

import json
import tempfile
import unittest
from pathlib import Path

from langchain_core.documents import Document

from Test_Ragas.table5_experiment import (
    CaseCheckpointStore,
    dataset_sha256,
    merge_graph_evidence,
    is_completed_case,
    message_content_text,
)


class Table5ExperimentTests(unittest.TestCase):
    def test_t1_t7_dataset_hash_depends_on_content_not_path(self):
        """T1-T7 checkpoints remain portable when the same dataset is copied elsewhere."""
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first" / "100.csv"
            second = Path(directory) / "second" / "renamed.csv"
            first.parent.mkdir()
            second.parent.mkdir()
            first.write_bytes(b"id,question\n1,test\n")
            second.write_bytes(first.read_bytes())

            self.assertEqual(dataset_sha256(first), dataset_sha256(second))

    def test_t1_t6_extract_visible_text_from_gemini_content_blocks(self):
        """T1-T6 checkpoints contain answer text, not Gemini block metadata."""
        content = [{"type": "text", "text": "Câu trả lời", "extras": {"signature": "secret"}}]
        self.assertEqual(message_content_text(content), "Câu trả lời")

    def test_t5_graph_augmentation_keeps_the_shared_context_budget(self):
        """T5 adds graph evidence without increasing the T1–T6 context budget."""
        baseline = [
            Document(page_content="vector document", metadata={"doc_id": "v1"}),
            Document(page_content="shared document", metadata={"doc_id": "shared"}),
        ]
        graph = [
            Document(page_content="graph document", metadata={"doc_id": "g1"}),
            Document(page_content="shared document", metadata={"doc_id": "shared"}),
        ]

        merged = merge_graph_evidence(baseline, graph, context_top_k=2)

        self.assertEqual([doc.metadata["doc_id"] for doc in merged], ["g1", "v1"])

    def test_t7_checkpoint_requires_the_exact_t6_evidence_fingerprint(self):
        """T7 can resume only from the exact evidence emitted by T6."""
        record = {
            "answer": "answer generated from T6 evidence",
            "generation_status": "completed",
            "evaluation_status": "completed",
            "metrics": {"faithfulness": 1.0},
            "evidence_fingerprint": "t6-evidence",
        }
        self.assertTrue(is_completed_case(record, evidence_fingerprint="t6-evidence"))
        self.assertFalse(is_completed_case(record, evidence_fingerprint="different-evidence"))

    def test_checkpoint_does_not_mark_empty_answer_as_completed(self):
        """A quota failure must remain resumable instead of becoming a false success."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            store = CaseCheckpointStore(path, fingerprint={"mode": "dense_only"})
            store.upsert("1", {"generation_status": "failed", "answer": ""})

            saved = json.loads(path.read_text(encoding="utf-8"))
            record = saved["cases"]["1"]
            self.assertFalse(is_completed_case(record))


if __name__ == "__main__":
    unittest.main()
