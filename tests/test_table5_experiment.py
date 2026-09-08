"""Regression tests for the T1–T7 Table 5 experiment helpers."""

import json
import tempfile
import unittest
from pathlib import Path

from langchain_core.documents import Document

from Test_Ragas.table5_experiment import (
    CaseCheckpointStore,
    T7_DISABLED_TOOL_GUIDANCE,
    build_t7_fixed_evidence_messages,
    checkpoint_file_path,
    dataset_sha256,
    merge_graph_evidence,
    is_api_pause_error,
    is_completed_case,
    message_content_text,
    mode_checkpoint_file_path,
)


class Table5ExperimentTests(unittest.TestCase):
    def test_t7_fixed_evidence_appears_exactly_once_in_agent_messages(self):
        """T7: the exact T6 context must not be duplicated across prompt messages."""
        evidence = "UNIQUE-T6-EVIDENCE"

        for agent_name in ("academic", "financial", "scholarship", "general"):
            messages = build_t7_fixed_evidence_messages(
                agent_name=agent_name,
                question="Câu hỏi kiểm thử",
                context=evidence,
            )
            rendered = "\n".join(str(message.content) for message in messages)
            self.assertEqual(rendered.count(evidence), 1, agent_name)

    def test_t7_fixed_evidence_keeps_agent_rules_and_marks_tools_precompleted(self):
        """T7: preserve production rules while declaring lookup instructions pre-completed."""
        messages = build_t7_fixed_evidence_messages(
            agent_name="financial",
            question="Học phí ngành CNTT là bao nhiêu?",
            context="Kết quả Graph từ T6",
        )
        system_text = str(messages[0].content)

        self.assertIn("Phân biệt rạch ròi 2 loại mức học phí", system_text)
        self.assertIn("đã được thực hiện ở T6", system_text)
        self.assertIn("không gọi lại công cụ", system_text)
        self.assertNotIn("trả lời ngắn", system_text.casefold())
        self.assertIn("tra_cuu_hoc_phi_graph", T7_DISABLED_TOOL_GUIDANCE["financial"])

    def test_t7_fixed_evidence_rejects_unknown_agent(self):
        """T7: an invalid router result must fail instead of silently choosing a prompt."""
        with self.assertRaisesRegex(ValueError, "Unsupported T7 agent"):
            build_t7_fixed_evidence_messages(
                agent_name="unknown",
                question="question",
                context="evidence",
            )

    def test_t1_t7_evaluator_timeout_is_a_resumable_api_pause(self):
        """T1-T7: RAGAS quota retries ending in TimeoutError must pause safely."""
        self.assertTrue(is_api_pause_error(TimeoutError()))

    def test_t1_t7_checkpoint_paths_are_grouped_by_mode(self):
        """T1-T7 checkpoints use one directory per mode to avoid Git conflicts."""
        root = Path("checkpoints")

        self.assertEqual(
            checkpoint_file_path(root, "hybrid_rrf_graph"),
            root / "hybrid_rrf_graph" / "checkpoint.json",
        )
        self.assertEqual(
            checkpoint_file_path(root, "hybrid_rrf", filename="candidates.json"),
            root / "hybrid_rrf" / "candidates.json",
        )

    def test_fixed_t7_uses_a_new_checkpoint_without_overwriting_old_results(self):
        """T7: corrected prompts must not resume the completed legacy T7 answers."""
        root = Path("checkpoints")

        self.assertEqual(
            mode_checkpoint_file_path(root, "hybrid_rrf_graph_rerank_agent"),
            root / "hybrid_rrf_graph_rerank_agent" / "checkpoint_fixed_v2.json",
        )
        self.assertEqual(
            mode_checkpoint_file_path(root, "hybrid_rrf_graph_rerank"),
            root / "hybrid_rrf_graph_rerank" / "checkpoint.json",
        )

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
