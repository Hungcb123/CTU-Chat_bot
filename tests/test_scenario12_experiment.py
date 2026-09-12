from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from langchain_core.documents import Document

from app.services.graph_service import AcademicGraphService
from Graph_DB.app.ingest_tuition import _attach_provenance
from scripts.prepare_scenario12_datasets import QUOTAS, build_dev, tuition_cases
from scripts.scenario12_common import (
    extract_program_query,
    graph_documents,
    load_cases,
    merge_with_quotas,
    query_signals,
    source_metrics,
)


class _Session:
    def __init__(self, rows):
        self.rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def run(self, *_args, **_kwargs):
        return self.rows


class _Driver:
    def __init__(self, rows):
        self.rows = rows

    def session(self):
        return _Session(self.rows)


class _Catalog:
    def __init__(self, status="not_found", records=(), message=""):
        self.result = SimpleNamespace(status=status, records=records, message=message)

    def lookup(self, _question):
        return self.result


class Scenario12Tests(unittest.TestCase):
    def test_development_normalization_uses_answer_as_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dev.jsonl"
            with patch("scripts.prepare_scenario12_datasets.DEV_OUTPUT", output):
                rows = build_dev()
            cases = load_cases(output)
        self.assertEqual(len(rows), 150)
        self.assertEqual(len(cases), 150)
        self.assertTrue(all(case.reference_answer for case in cases))
        self.assertTrue(any(case.raw_evidence != case.reference_answer for case in cases))
        self.assertTrue(all(case.review_status == "development" for case in cases))

    def test_heldout_tuition_quota_and_required_fields(self):
        rows = tuition_cases()
        self.assertEqual(len(rows), QUOTAS["actual_tuition"])
        self.assertEqual(len({row["query_family"] for row in rows}), 20)
        self.assertTrue(all(row["review_status"] == "pending" for row in rows))
        self.assertTrue(all(row["gold_sources"] and row["required_facts"] for row in rows))

    def test_load_cases_blocks_unapproved_heldout(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "heldout.jsonl"
            path.write_text(json.dumps({
                "id": "H1", "category": "other", "question": "Q", "reference_answer": "A",
                "raw_evidence": "E", "gold_sources": ["x.md"], "required_facts": ["A"],
                "query_family": "f1", "review_status": "pending",
            }) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unapproved"):
                load_cases(path, require_approved=True)

    def test_source_metrics_respect_all_sources_and_rank(self):
        metrics = source_metrics(["a.md", "noise.md", "b.md"], ["a.md", "b.md"], top_k=7)
        self.assertEqual(metrics["source_recall"], 1.0)
        self.assertAlmostEqual(metrics["source_ap"], (1.0 + 2 / 3) / 2)
        any_valid = source_metrics(["b.md"], ["a.md", "b.md"], top_k=7, source_relation="any_valid")
        self.assertEqual(any_valid["source_recall"], 1.0)

    def test_query_signals_and_aliases_do_not_need_dataset_labels(self):
        signals = query_signals("Học phí ngành CNTT CLC khóa 52 và tổng số tín chỉ là bao nhiêu?")
        self.assertTrue(signals["tuition"])
        self.assertTrue(signals["academic"])
        self.assertEqual(extract_program_query("Cho hỏi CNTT khóa 52"), "Công nghệ thông tin")

    def test_top7_composite_quota_is_three_documents_two_per_graph_lane(self):
        document_docs = [Document(page_content=f"d{i}", metadata={"source": f"d{i}.md"}) for i in range(8)]
        graph_docs = [
            *[Document(page_content=f"a{i}", metadata={"source": f"a{i}.md", "evidence_lane": "academic_graph"}) for i in range(3)],
            *[Document(page_content=f"t{i}", metadata={"source": f"t{i}.md", "evidence_lane": "tuition_graph"}) for i in range(3)],
        ]
        merged = merge_with_quotas(document_docs, graph_docs, top_k=7)
        lanes = [doc.metadata.get("evidence_lane", "document") for doc in merged]
        self.assertEqual(len(merged), 7)
        self.assertEqual(lanes.count("document"), 3)
        self.assertEqual(lanes.count("academic_graph"), 2)
        self.assertEqual(lanes.count("tuition_graph"), 2)

    def test_graph_tuition_exact_constraints_and_provenance(self):
        rows = [
            {"id": "wrong", "ma_nganh": "7480201", "khoa": "K51_ve_truoc", "nam_hoc": "2026-2027", "loai_ct": "chuan", "don_vi_tinh": "dong/tin_chi", "muc_hp": 695000, "ten_nganh": "Công nghệ thông tin", "program_name": "", "program_code": "", "source": "k51.md", "source_section": "s", "source_table": "t"},
            {"id": "right", "ma_nganh": "7480201", "khoa": "K52", "nam_hoc": "2026-2027", "loai_ct": "chuan", "don_vi_tinh": "dong/tin_chi", "muc_hp": 781000, "ten_nganh": "Công nghệ thông tin", "program_name": "", "program_code": "", "source": "k52.md", "source_section": "s", "source_table": "t"},
            {"id": "wrong-program", "ma_nganh": "7480201", "khoa": "K52", "nam_hoc": "2026-2027", "loai_ct": "clc", "don_vi_tinh": "dong/tin_chi", "muc_hp": 1200000, "ten_nganh": "Công nghệ thông tin", "program_name": "", "program_code": "", "source": "clc.md", "source_section": "s", "source_table": "t"},
        ]
        service = AcademicGraphService.__new__(AcademicGraphService)
        service._driver = _Driver(rows)
        result = service.lookup_tuition("Học phí mỗi tín chỉ ngành CNTT hệ chuẩn khóa 52?")
        self.assertEqual([row["id"] for row in result], ["right"])
        self.assertEqual(result[0]["source"], "k52.md")

    def test_graph_documents_does_not_count_catalog_fallback_as_graph_hit(self):
        catalog = _Catalog(
            status="found",
            records=({"source": "MucHocPhi_DaiHocChinhQuy_Khoa52.md"},),
            message="Ngành CNTT K52: 781.000 đồng/tín chỉ",
        )
        graph = SimpleNamespace(lookup_tuition=lambda _query: [])
        docs, trace = graph_documents("Học phí mỗi tín chỉ ngành CNTT khóa 52?", graph, catalog)
        self.assertTrue(docs)
        self.assertTrue(trace["catalog_fallback"])
        self.assertFalse(trace["graph_hit"])
        self.assertEqual(docs[0].metadata["backend"], "catalog_fallback")

    def test_ingest_attaches_canonical_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "official.md"
            source.write_text("# Official tuition table\n", encoding="utf-8")
            rows = _attach_provenance([{"id": "fee-1"}], source, {"content_kind": "rate_table"})
        self.assertEqual(rows[0]["source"], "official.md")
        self.assertEqual(rows[0]["source_table"], "rate_table")
        self.assertEqual(rows[0]["source_section"], "Official tuition table")


if __name__ == "__main__":
    unittest.main()
