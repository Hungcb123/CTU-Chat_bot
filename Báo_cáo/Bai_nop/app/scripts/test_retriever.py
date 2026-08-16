"""Retrieval-only acceptance tests for the metadata-filtered RAG index.

This script calls embeddings/Qdrant/reranking but never calls Gemini or Groq.
It exits non-zero on the first failed acceptance condition.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from app.services.rag_engine import AdvancedChunkingEngine


@dataclass(frozen=True)
class RetrievalCase:
    name: str
    query: str
    filters: dict[str, Any]
    expected_metadata: dict[str, str]
    expected_source: str
    expected_text: tuple[str, ...] = field(default_factory=tuple)


CASES = (
    RetrievalCase(
        name="gdqp_exemption_basis",
        query="Mức học phí làm cơ sở tính miễn giảm của Giáo dục quốc phòng là bao nhiêu?",
        filters={
            "fee_kind": "exemption_basis",
            "content_kind": "rate_table",
            "domain": "tuition",
            "academic_year": "2025-2026",
        },
        expected_metadata={"fee_kind": "exemption_basis"},
        expected_source="MucHocPhi_2526_MienGiam.md",
        expected_text=("451.000", "Giáo dục quốc phòng"),
    ),
    RetrievalCase(
        name="gdqp_actual_tuition",
        query="Học phí thực tế Giáo dục quốc phòng và An ninh một tín chỉ bao nhiêu?",
        filters={
            "fee_kind": "actual_tuition",
            "content_kind": "rate_table",
            "domain": "tuition",
            "academic_year": "2026-2027",
        },
        expected_metadata={"fee_kind": "actual_tuition"},
        expected_source="MucHocPhi_QuyDinhChung.md",
        expected_text=("695.000", "Giáo dục Quốc phòng"),
    ),
    RetrievalCase(
        name="group_iv_exemption_basis",
        query="Mức cơ sở miễn giảm học phí khối ngành IV là bao nhiêu?",
        filters={
            "fee_kind": "exemption_basis",
            "content_kind": "rate_table",
            "domain": "tuition",
            "academic_year": "2025-2026",
        },
        expected_metadata={"fee_kind": "exemption_basis"},
        expected_source="MucHocPhi_2526_MienGiam.md",
        expected_text=("487.000", "Khối ngành IV"),
    ),
    RetrievalCase(
        name="cntt_k52_actual_tuition",
        query="Học phí thực tế ngành Công nghệ thông tin đại trà Khóa 52 là bao nhiêu?",
        filters={
            "fee_kind": "actual_tuition",
            "content_kind": "rate_table",
            "domain": "tuition",
            "academic_year": "2026-2027",
        },
        expected_metadata={"fee_kind": "actual_tuition"},
        expected_source="MucHocPhi_DaiHocChinhQuy_Khoa52.md",
        expected_text=("966.000", "Công nghệ thông tin"),
    ),
    RetrievalCase(
        name="scholarship_metadata_lane",
        query="Điều kiện và mức học bổng Vallet dành cho sinh viên là gì?",
        filters={"lane": "scholarship"},
        expected_metadata={"domain": "scholarship"},
        expected_source="HB_Vallet_Chi_Tiet.md",
        expected_text=("Vallet",),
    ),
    RetrievalCase(
        name="student_loan_metadata_lane",
        query="Sinh viên vay tiền đóng học phí qua VietinBank như thế nào?",
        filters={"lane": "student_loan"},
        expected_metadata={"domain": "student_loan"},
        expected_source="Vayvon_Viettinbank_2025_v2.md",
        expected_text=("VietinBank",),
    ),
)


def _assert_case(engine: AdvancedChunkingEngine, case: RetrievalCase) -> dict[str, Any]:
    documents = engine.retrieve(
        case.query,
        top_n=6,
        metadata_filter_enabled=True,
        **case.filters,
    )
    assert documents, f"{case.name}: retrieval returned no documents"
    for document in documents:
        for key, value in case.expected_metadata.items():
            assert document.metadata.get(key) == value, (
                f"{case.name}: leaked {key}={document.metadata.get(key)!r}; "
                f"expected {value!r}"
            )

    matching_source = [
        document
        for document in documents
        if document.metadata.get("source") == case.expected_source
    ]
    assert matching_source, (
        f"{case.name}: expected source {case.expected_source!r}; got "
        f"{[doc.metadata.get('source') for doc in documents]}"
    )
    combined = "\n".join(document.page_content for document in matching_source)
    for expected in case.expected_text:
        assert expected.casefold() in combined.casefold(), (
            f"{case.name}: {expected!r} not found in expected source chunks"
        )
    return {
        "name": case.name,
        "documents": len(documents),
        "sources": sorted(
            {str(document.metadata.get("source")) for document in documents}
        ),
    }


def _assert_ambiguous_balanced_lanes(engine: AdvancedChunkingEngine) -> dict[str, Any]:
    query = "Môn Giáo dục quốc phòng một tín chỉ bao nhiêu tiền?"
    actual = engine.retrieve(
        query,
        lane="actual_tuition",
        top_n=3,
        metadata_filter_enabled=True,
    )
    basis = engine.retrieve(
        query,
        lane="exemption_basis",
        top_n=3,
        metadata_filter_enabled=True,
    )
    assert actual and basis, "ambiguous query must produce documents from both lanes"
    assert all(doc.metadata.get("fee_kind") == "actual_tuition" for doc in actual)
    assert all(doc.metadata.get("fee_kind") == "exemption_basis" for doc in basis)
    assert any("695.000" in doc.page_content for doc in actual)
    assert any("451.000" in doc.page_content for doc in basis)
    return {"name": "ambiguous_balanced_lanes", "actual": len(actual), "basis": len(basis)}


def _assert_concurrent_filter_isolation(engine: AdvancedChunkingEngine) -> dict[str, Any]:
    def retrieve_lane(lane: str):
        return engine.retrieve(
            "Giáo dục quốc phòng một tín chỉ bao nhiêu?",
            lane=lane,
            top_n=3,
            metadata_filter_enabled=True,
            # The concurrency check targets filter isolation. Avoid running two
            # large GPU reranker batches at once on the project's 4 GB GPU.
            use_reranker=False,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        actual_future = executor.submit(retrieve_lane, "actual_tuition")
        basis_future = executor.submit(retrieve_lane, "exemption_basis")
        actual = actual_future.result()
        basis = basis_future.result()
    assert actual and basis, "concurrent lane retrieval returned no documents"
    assert all(doc.metadata.get("fee_kind") == "actual_tuition" for doc in actual)
    assert all(doc.metadata.get("fee_kind") == "exemption_basis" for doc in basis)
    return {"name": "concurrent_filter_isolation", "passed": True}


def main() -> int:
    try:
        engine = AdvancedChunkingEngine(
            persist_dir=str(PROJECT_ROOT / "parent_doc_storage"),
            metadata_filter_enabled=True,
        )
        point_count = engine.qdrant_client.count(engine.collection_name).count
        assert point_count > 0, f"collection {engine.collection_name!r} is empty"

        results = [_assert_case(engine, case) for case in CASES]
        results.append(_assert_ambiguous_balanced_lanes(engine))
        results.append(_assert_concurrent_filter_isolation(engine))
        print(
            json.dumps(
                {
                    "passed": True,
                    "collection": engine.collection_name,
                    "points": point_count,
                    "tests": results,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {"passed": False, "error": f"{type(exc).__name__}: {exc}"},
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
