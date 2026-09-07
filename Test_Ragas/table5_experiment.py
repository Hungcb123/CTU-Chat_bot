"""T1–T7 benchmark helpers kept separate from the production chat path."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from langchain_core.documents import Document


class QuotaPausedError(RuntimeError):
    """Raised when a run must stop safely and resume with another API key."""


class IncompleteMetricError(RuntimeError):
    """Raised when RAGAS returns a missing score instead of a valid measurement."""


@dataclass(frozen=True)
class BenchmarkCase:
    """T1–T7: normalized benchmark row; labels are evaluator-only metadata."""

    case_id: str
    question: str
    category: str
    expected_answer: str


def checkpoint_file_path(
    checkpoint_dir: Path, mode: str, *, filename: str = "checkpoint.json"
) -> Path:
    """T1-T7: keep each mode's resumable files in its own directory."""
    return Path(checkpoint_dir) / mode / filename


def dataset_sha256(path: Path) -> str:
    """T1-T7: identify dataset content so checkpoints can move between machines."""
    digest = hashlib.sha256()
    with path.open("rb") as dataset_file:
        for block in iter(lambda: dataset_file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_csv_dataset(path: Path) -> list[BenchmarkCase]:
    """T1–T7: load the 100.csv experiment dataset without exposing labels to retrieval."""
    with path.open("r", encoding="utf-8-sig", newline="") as dataset_file:
        rows = list(csv.DictReader(dataset_file))
    required = {"Original ID", "Master Question", "Category", "Ground Truth"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"CSV dataset must contain {sorted(required)}")
    return [
        BenchmarkCase(
            case_id=str(row["Original ID"]).strip(),
            question=str(row["Master Question"]).strip(),
            category=str(row["Category"]).strip(),
            expected_answer=str(row["Ground Truth"]).strip(),
        )
        for row in rows
        if str(row["Master Question"]).strip() and str(row["Ground Truth"]).strip()
    ]


def document_key(document: Document) -> str:
    """T1–T7: stable identity used for deduplication and evidence provenance."""
    return str(document.metadata.get("doc_id") or hashlib.sha256(
        document.page_content.encode("utf-8")
    ).hexdigest())


def evidence_fingerprint(documents: Iterable[Document]) -> str:
    """T6→T7: prove that T7 consumes exactly the evidence emitted by T6."""
    payload = [
        {"key": document_key(doc), "content": doc.page_content, "metadata": dict(doc.metadata)}
        for doc in documents
    ]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def message_content_text(content: Any) -> str:
    """T1-T7: extract visible text from Gemini string or content-block responses."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        text = content.get("text")
        return str(text).strip() if text is not None else ""
    if isinstance(content, (list, tuple)):
        return "\n".join(
            part for item in content if (part := message_content_text(item))
        ).strip()
    return str(content or "").strip()


def merge_graph_evidence(
    baseline_documents: Iterable[Document],
    graph_documents: Iterable[Document],
    *,
    context_top_k: int,
) -> list[Document]:
    """T5: Graph augments T3 evidence; it is deliberately not a third RRF lane."""
    if context_top_k < 1:
        raise ValueError("context_top_k must be at least 1")
    baseline = list(baseline_documents)
    baseline_keys = {document_key(document) for document in baseline}
    # T5: only genuinely new Graph facts may displace a T3 result. A Graph copy
    # of an existing T3 document must not consume the shared context budget.
    graph_additions = [
        document for document in graph_documents
        if document_key(document) not in baseline_keys
    ]
    merged = combine_evidence(baseline, graph_additions)
    return merged[:context_top_k]


def combine_evidence(
    baseline_documents: Iterable[Document],
    graph_documents: Iterable[Document],
) -> list[Document]:
    """T6: create the reranker pool from T3 candidates plus Graph evidence, without RRF."""
    merged: list[Document] = []
    seen: set[str] = set()
    # T5/T6: Graph facts have priority; Graph does not receive an RRF score.
    for document in [*graph_documents, *baseline_documents]:
        key = document_key(document)
        if key not in seen:
            seen.add(key)
            merged.append(document)
    return merged


def serialize_documents(documents: Iterable[Document]) -> list[dict[str, Any]]:
    """T6→T7: persist ordered evidence so a resumed T7 cannot retrieve again."""
    return [
        {"page_content": doc.page_content, "metadata": dict(doc.metadata)}
        for doc in documents
    ]


def deserialize_documents(records: Iterable[dict[str, Any]]) -> list[Document]:
    """T6→T7: reconstruct ordered LangChain documents from a checkpoint."""
    return [
        Document(page_content=str(record["page_content"]), metadata=dict(record.get("metadata") or {}))
        for record in records
    ]


def graph_records_to_documents(records: Iterable[dict[str, Any]], operation: str) -> list[Document]:
    """T5/T6: canonicalize structured Graph records into inspectable evidence documents."""
    documents: list[Document] = []
    for record in records:
        if not record:
            continue
        content = json.dumps(record, ensure_ascii=False, sort_keys=True)
        entity = record.get("id") or record.get("program_code") or record.get("code")
        doc_id = f"graph::{operation}::{entity or hashlib.sha256(content.encode('utf-8')).hexdigest()}"
        documents.append(Document(
            page_content=content,
            metadata={
                "doc_id": doc_id,
                "source": "neo4j_graph",
                "retrieval_source": "graph",
                "graph_operation": operation,
            },
        ))
    return documents


def graph_evidence_for_query(
    graph_service: Any, query: str, inferred_intent: str
) -> list[Document]:
    """T5/T6: select Graph evidence from production intent, never the benchmark label."""
    if graph_service is None:
        return []
    if inferred_intent == "actual_tuition":
        return graph_records_to_documents(graph_service.lookup_tuition(query), "lookup_tuition")
    if inferred_intent == "exemption_basis":
        return graph_records_to_documents(
            graph_service.lookup_exemption_basis(query=query), "lookup_exemption_basis"
        )
    if inferred_intent == "academic_program":
        records = graph_service.search_programs(query)
        return graph_records_to_documents(records, "search_programs")
    return []


def is_quota_error(error: BaseException) -> bool:
    """T1–T7: identify errors that require a checkpointed pause, not a fake score."""
    message = str(error).casefold()
    return any(token in message for token in (
        "resource_exhausted", "quota exceeded", "daily limit", "429",
    ))


def is_api_pause_error(error: BaseException) -> bool:
    """T1-T7: pause safely when RAGAS hides exhausted retries as TimeoutError."""
    return isinstance(error, TimeoutError) or is_quota_error(error)


def is_completed_case(record: dict[str, Any] | None, *, evidence_fingerprint: str | None = None) -> bool:
    """T1–T7: a case is complete only after a non-empty answer and valid metrics exist."""
    if not record or not str(record.get("answer") or "").strip():
        return False
    if record.get("generation_status") != "completed":
        return False
    if record.get("evaluation_status") != "completed":
        return False
    metrics = record.get("metrics") or {}
    if not metrics or any(value is None for value in metrics.values()):
        return False
    return evidence_fingerprint is None or record.get("evidence_fingerprint") == evidence_fingerprint


class CaseCheckpointStore:
    """T1–T7: atomic, per-case checkpoint store for quota-safe resume."""

    def __init__(self, path: Path, *, fingerprint: dict[str, Any]):
        self.path = path
        self.fingerprint = fingerprint
        self.data = self._load_or_initialize()

    def _load_or_initialize(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"fingerprint": self.fingerprint, "cases": {}}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if data.get("fingerprint") != self.fingerprint:
            raise ValueError(
                f"Checkpoint {self.path} belongs to a different experiment configuration. "
                "Use a new output directory or remove the incompatible checkpoint."
            )
        return data

    def get(self, case_id: str) -> dict[str, Any] | None:
        return self.data["cases"].get(str(case_id))

    def upsert(self, case_id: str, values: dict[str, Any]) -> None:
        """T1–T7: write one completed stage atomically before the next API call."""
        record = dict(self.get(case_id) or {})
        record.update(values)
        self.data["cases"][str(case_id)] = record
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f"{self.path.name}.", suffix=".tmp", dir=self.path.parent, text=True
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as checkpoint_file:
                json.dump(self.data, checkpoint_file, ensure_ascii=False, indent=2)
                checkpoint_file.flush()
                os.fsync(checkpoint_file.fileno())
            Path(temporary_name).replace(self.path)
        finally:
            if Path(temporary_name).exists():
                Path(temporary_name).unlink()
