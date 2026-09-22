"""Shared, provenance-aware retrieval utilities for Scenario 1 and 2."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ScenarioCase:
    case_id: str
    category: str
    question: str
    reference_answer: str
    raw_evidence: str
    gold_sources: list[str]
    source_relation: str = "single"
    required_facts: list[str] = field(default_factory=list)
    query_family: str = ""
    is_composite: bool = False
    review_status: str = "development"
    domain: str = ""
    complexity_tier: str = ""


@dataclass
class RetrievalTrace:
    configs: dict[str, list[Any]]
    graph_hit: bool
    catalog_fallback: bool
    active_lanes: list[str]
    gate_reasons: list[str]
    latency_ms: dict[str, float]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFD", value.casefold())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def canonical_source(value: Any) -> str:
    if value is None:
        return ""
    return Path(str(value).strip()).name


def source_from_document(document: Any) -> str:
    metadata = getattr(document, "metadata", {}) or {}
    return canonical_source(metadata.get("source") or metadata.get("document_key"))


def _parse_sources(value: str) -> list[str]:
    return list(dict.fromkeys(
        canonical_source(item) for item in re.split(r"[,;]", value or "") if item.strip()
    ))


def _resolve_case_domain(row: dict[str, Any]) -> str:
    d = str(row.get("domain") or "").lower().strip()
    if d in ("academic", "financial", "scholarship", "general") or "+" in d:
        return d
    cat = str(row.get("category") or "").lower().strip()
    if cat in ("academic_program", "academic"):
        return "academic"
    if cat in ("actual_tuition", "exemption_policy", "exemption_basis", "tuition", "financial", "financial_policy"):
        return "financial"
    if cat in ("scholarship",):
        return "scholarship"
    if cat in ("cross_domain",):
        return "cross_domain"
    return "general"


def load_cases(dataset_path: Path, *, require_approved: bool = False) -> list[ScenarioCase]:
    if dataset_path.suffix == ".jsonl":
        with dataset_path.open("r", encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
        cases = [
            ScenarioCase(
                case_id=str(row["id"]),
                category=str(row["category"]),
                question=str(row["question"]).strip(),
                reference_answer=str(row["reference_answer"]).strip(),
                raw_evidence=str(row.get("raw_evidence") or row["reference_answer"]).strip(),
                gold_sources=[canonical_source(item) for item in row["gold_sources"]],
                source_relation=str(row.get("source_relation", "single")),
                required_facts=[str(item) for item in row.get("required_facts", [])],
                query_family=str(row.get("query_family", "")),
                is_composite=bool(row.get("is_composite", False)),
                review_status=str(row.get("review_status", "pending")),
                domain=_resolve_case_domain(row),
                complexity_tier=str(row.get("complexity_tier", "")),
            )
            for row in rows
        ]
    else:
        with dataset_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        cases = [
            ScenarioCase(
                case_id=str(row.get("Original ID") or index + 1),
                category=(row.get("Category") or "").strip(),
                question=(row.get("Master Question") or row.get("Question") or "").strip(),
                reference_answer=(row.get("Answer") or row.get("Ground Truth") or "").strip(),
                raw_evidence=(row.get("Ground Truth") or row.get("Answer") or "").strip(),
                gold_sources=_parse_sources(row.get("Source") or ""),
                source_relation=(row.get("source_relation") or "single").strip(),
                required_facts=[],
                query_family=f"dev-{row.get('Original ID') or index + 1}",
                is_composite=str(row.get("Original ID") or "").startswith("CDICT"),
                review_status="development",
                domain=_resolve_case_domain(row),
                complexity_tier=str(row.get("complexity_tier") or ""),
            )
            for index, row in enumerate(rows)
            if (row.get("Master Question") or row.get("Question") or "").strip()
        ]
    if require_approved:
        pending = [case.case_id for case in cases if case.review_status != "approved"]
        if pending:
            raise ValueError(f"Held-out dataset has {len(pending)} unapproved cases: {pending[:5]}")
    return cases


def unique_documents(documents: Iterable[Any]) -> list[Any]:
    seen: set[str] = set()
    result = []
    for document in documents:
        metadata = getattr(document, "metadata", {}) or {}
        key = str(metadata.get("doc_id") or sha256_text(getattr(document, "page_content", "")))
        if key not in seen:
            seen.add(key)
            result.append(document)
    return result


def source_metrics(
    retrieved_sources: Sequence[str],
    gold_sources: Sequence[str],
    *,
    top_k: int,
    source_relation: str = "single",
) -> dict[str, float]:
    retrieved = list(dict.fromkeys(source for source in retrieved_sources if source))[:top_k]
    gold = set(source for source in gold_sources if source)
    if not gold:
        return {"source_recall": 1.0, "source_ap": 1.0}
    hits = [rank for rank, source in enumerate(retrieved, start=1) if source in gold]
    if source_relation == "any_valid":
        recall = float(bool(hits))
    else:
        recall = len({retrieved[rank - 1] for rank in hits}) / len(gold)
    if not hits:
        return {"source_recall": recall, "source_ap": 0.0}
    ap = sum(index / rank for index, rank in enumerate(hits, start=1)) / len(gold)
    return {"source_recall": min(1.0, recall), "source_ap": min(1.0, ap)}


PROGRAM_ALIASES = {
    "cntt": "Công nghệ thông tin",
    "ktpm": "Kỹ thuật phần mềm",
    "httt": "Hệ thống thông tin",
    "khmt": "Khoa học máy tính",
    "attt": "An toàn thông tin",
    "qtkd": "Quản trị kinh doanh",
    "mmt ttdl": "Mạng máy tính và truyền thông dữ liệu",
}


def extract_program_query(question: str) -> str | None:
    normalized = normalize_text(question)
    for alias, canonical in PROGRAM_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            return canonical
    code = re.search(r"\b7\d{6}[a-z]?\b", normalized)
    if code:
        return code.group(0).upper()

    # Regex extraction for major names in Vietnamese
    # Pattern 1: after "ngành", "chuyên ngành", "cử nhân", "kỹ sư"
    m1 = re.search(
        r"(?:ngành|nganh|chuyên ngành|chuyen nganh|cử nhân|cu nhan|kỹ sư|ky su)\s+([A-ZÀ-Ỹa-zà-ỹ\s]+?)(?:\s+(?:hệ|he|chương trình|chuong trinh|khoa|tại|tai|học|hoc|có|co|cần|can|yêu cầu|yeu cau|được|duoc|thiết kế|thiet ke|quy định|trong|chuẩn|chuan|clc)\b|[?,.!]|$)",
        question,
        re.IGNORECASE,
    )
    if m1:
        candidate = m1.group(1).strip()
        if len(candidate) >= 3:
            return candidate

    # Pattern 2: after "chương trình" (e.g. "Trong chương trình Kỹ thuật cơ điện tử chuẩn...")
    m2 = re.search(
        r"(?:chương trình|chuong trinh)\s+(?:đào tạo\s+|chất lượng cao\s+|clc\s+|chuẩn\s+)?([A-ZÀ-Ỹa-zà-ỹ\s]+?)(?:\s+(?:chuẩn|chuan|hệ|he|học|hoc|có|co|cần|can|trong|yêu cầu)\b|[?,.!]|$)",
        question,
        re.IGNORECASE,
    )
    if m2:
        candidate = m2.group(1).strip()
        if len(candidate) >= 3:
            return candidate

    return None


def query_signals(question: str) -> dict[str, bool]:
    normalized = normalize_text(question)
    tuition = any(term in normalized for term in ("hoc phi", "mien giam", "muc thu", "don gia"))
    academic = bool(re.search(r"\b[A-Z]{2}\d{3}[A-Z]?\b", question)) or any(
        term in normalized
        for term in (
            "chuong trinh", "tong so tin chi", "so luong tin chi", "tin chi", "thoi gian dao tao",
            "plo", "chuan dau ra", "mon hoc", "hoc phan", "tien quyet", "song hanh", "nganh",
            "khoi luong kien thuc", "quy che", "canh bao", "tot nghiep", "thoi hoc",
        )
    )
    policy = any(term in normalized for term in ("he so", "ngoai thoi gian", "hoc lai", "mien giam"))
    calculation = any(term in normalized for term in ("tong tien", "bao nhieu tien", "tinh tien"))
    return {"document": True, "academic": academic, "tuition": tuition, "policy": policy, "calculation": calculation}


def _format_tuition_row(row: dict[str, Any]) -> str:
    ten_nganh = row.get("ten_nganh") or row.get("program_name") or ""
    ma_nganh = row.get("ma_nganh") or row.get("program_code") or ""
    khoa = row.get("khoa") or ""
    nam_hoc = row.get("nam_hoc") or ""
    loai_ct = row.get("loai_ct") or ""
    muc_hp = row.get("muc_hp")
    don_vi = row.get("don_vi_tinh") or "đồng/năm"

    parts = []
    if ten_nganh:
        parts.append(f"ngành {ten_nganh}" + (f" (mã {ma_nganh})" if ma_nganh else ""))
    if loai_ct:
        parts.append(f"chương trình {loai_ct}")
    if khoa:
        parts.append(f"khóa {khoa}")
    if nam_hoc:
        parts.append(f"năm học {nam_hoc}")

    subject = ", ".join(parts) if parts else "Học phí"
    return f"Theo biểu mức thu học phí CTU: {subject} có mức thu là {muc_hp} {don_vi}."


def _program_source(program_code: str) -> str:
    metadata_path = ROOT / "data" / "document_metadata.json"
    if metadata_path.exists():
        documents = json.loads(metadata_path.read_text(encoding="utf-8")).get("documents", {})
        for source in documents:
            if re.search(rf"(?:^|_){re.escape(program_code)}(?:_|\.)", source, re.IGNORECASE):
                return canonical_source(source)
    return "chuongtrinhdaotao.md"


def graph_documents(question: str, graph_service: Any, tuition_catalog: Any) -> tuple[list[Any], dict[str, Any]]:
    from langchain_core.documents import Document

    signals = query_signals(question)
    docs: list[Any] = []
    trace = {"graph_hit": False, "catalog_fallback": False, "gate_reasons": []}

    if signals["academic"] and graph_service is not None:
        program_query = extract_program_query(question)
        if program_query:
            try:
                result = graph_service.lookup_program(program_query)
            except Exception as exc:
                result = None
                trace["gate_reasons"].append(f"academic_graph_error:{type(exc).__name__}")
            if result and result.get("program"):
                program = result["program"]
                lines = [
                    "[DỮ LIỆU CHƯƠNG TRÌNH ĐÀO TẠO TỪ NEO4J]",
                    f"Chương trình đào tạo ngành {program.get('name')} (mã ngành: {program.get('code')}) thuộc {program.get('faculty') or program.get('unit') or 'Trường ĐH Cần Thơ'}.",
                ]
                if program.get("duration"):
                    lines.append(f"Thời gian đào tạo: {program['duration']}.")
                if program.get("total_credits"):
                    lines.append(f"Tổng số tín chỉ: {program['total_credits']} tín chỉ.")
                if program.get("degree"):
                    lines.append(f"Văn bằng tốt nghiệp: {program['degree']}.")
                q_norm = normalize_text(question)
                for block in result.get("blocks", []):
                    for course in block.get("courses", []):
                        code = str(course.get("code") or "")
                        name = str(course.get("name") or "")
                        if (code and code.casefold() in question.casefold()) or (
                            name and normalize_text(name) in q_norm
                        ):
                            lines.append(f"Học phần: {name} ({code}), {course.get('credits')} tín chỉ.")
                if "plo" in q_norm or "chuan dau ra" in q_norm:
                    lines.extend(
                        f"{item.get('id')}: {item.get('description')}" for item in result.get("plos", [])
                    )
                docs.append(Document(
                    page_content="\n".join(lines),
                    metadata={
                        "source": _program_source(str(program.get("code") or "")),
                        "backend": "graph",
                        "evidence_lane": "academic_graph",
                    },
                ))
                trace["graph_hit"] = True
            else:
                trace["gate_reasons"].append("academic_no_exact_program")

    if signals["tuition"]:
        rows = []
        if graph_service is not None:
            try:
                rows = graph_service.lookup_tuition(question) or []
            except Exception as exc:
                trace["gate_reasons"].append(f"tuition_graph_error:{type(exc).__name__}")
        if rows:
            for row in rows:
                source = canonical_source(row.get("source"))
                if not source:
                    trace["gate_reasons"].append("graph_row_missing_provenance")
                    continue
                docs.append(Document(
                    page_content="[HỌC PHÍ TỪ NEO4J]\n" + _format_tuition_row(row),
                    metadata={"source": source, "backend": "graph", "evidence_lane": "tuition_graph"},
                ))
            trace["graph_hit"] = any(d.metadata.get("evidence_lane") == "tuition_graph" for d in docs)
        if not rows or not any(d.metadata.get("evidence_lane") == "tuition_graph" for d in docs):
            fallback = tuition_catalog.lookup(question)
            if fallback.status == "found":
                for record in fallback.records:
                    docs.append(Document(
                        page_content="[HỌC PHÍ TỪ CATALOG FALLBACK]\n" + fallback.message,
                        metadata={
                            "source": canonical_source(record.get("source")),
                            "backend": "catalog_fallback",
                            "evidence_lane": "tuition_graph",
                        },
                    ))
                trace["catalog_fallback"] = True
            else:
                trace["gate_reasons"].append(f"tuition_gate:{fallback.status}")

        if signals["policy"] and graph_service is not None:
            try:
                policies = graph_service.get_tuition_policies(question) or []
            except Exception as exc:
                policies = []
                trace["gate_reasons"].append(f"policy_graph_error:{type(exc).__name__}")
            for row in policies[:2]:
                source = canonical_source(row.get("source"))
                if source:
                    clean_items = []
                    for key, value in row.items():
                        if value not in (None, "") and key != "source":
                            clean_items.append(f"{key.replace('_', ' ').capitalize()}: {value}")
                    docs.append(Document(
                        page_content="[QUY ĐỊNH HỌC PHÍ TỪ NEO4J]\n" + "\n".join(clean_items),
                        metadata={"source": source, "backend": "graph", "evidence_lane": "tuition_graph"},
                    ))
                    trace["graph_hit"] = True

        if "mien giam" in normalize_text(question) and graph_service is not None:
            try:
                basis_rows = graph_service.lookup_exemption_basis(query=question) or []
            except Exception as exc:
                basis_rows = []
                trace["gate_reasons"].append(f"exemption_graph_error:{type(exc).__name__}")
            for row in basis_rows[:2]:
                source = canonical_source(row.get("source"))
                if source:
                    clean_items = []
                    for key, value in row.items():
                        if value not in (None, "") and key != "source":
                            clean_items.append(f"{key.replace('_', ' ').capitalize()}: {value}")
                    docs.append(Document(
                        page_content="[CƠ SỞ MIỄN GIẢM TỪ NEO4J]\n" + "\n".join(clean_items),
                        metadata={"source": source, "backend": "graph", "evidence_lane": "tuition_graph"},
                    ))
                    trace["graph_hit"] = True

    return unique_documents(docs), trace


def rerank_documents(
    documents: Sequence[Any],
    question: str,
    compressor: Any,
    limit: int,
    *,
    min_score_threshold: float = 0.0,
    min_k: int = 2,
) -> list[Any]:
    docs = unique_documents(documents)
    if compressor is not None and len(docs) > 1:
        ranked = list(compressor.compress_documents(docs, question))
        if min_score_threshold > 0.0:
            filtered = [
                d for d in ranked
                if getattr(d, "metadata", {}).get("reranker_score", 1.0) >= min_score_threshold
            ]
            if len(filtered) < min_k:
                filtered = ranked[:min_k]
            return filtered[:limit]
        return ranked[:limit]
    return docs[:limit]


def merge_with_quotas(
    document_docs: Sequence[Any],
    graph_docs: Sequence[Any],
    *,
    top_k: int,
) -> list[Any]:
    graph_docs = unique_documents(graph_docs)
    academic = [d for d in graph_docs if d.metadata.get("evidence_lane") == "academic_graph"]
    tuition = [d for d in graph_docs if d.metadata.get("evidence_lane") == "tuition_graph"]
    if academic and tuition:
        academic_quota, tuition_quota = min(1, top_k), min(1, max(0, top_k - 1))
    elif academic:
        academic_quota, tuition_quota = min(1, top_k), 0
    elif tuition:
        academic_quota, tuition_quota = 0, min(1, top_k)
    else:
        academic_quota = tuition_quota = 0
    document_quota = max(0, top_k - academic_quota - tuition_quota)
    selected = academic[:academic_quota] + tuition[:tuition_quota] + list(document_docs[:document_quota])
    remaining = academic[academic_quota:] + tuition[tuition_quota:] + list(document_docs[document_quota:])
    return unique_documents(selected + remaining)[:top_k]


def retrieve_configurations(
    case: ScenarioCase,
    engine: Any,
    graph_service: Any,
    tuition_catalog: Any,
    compressor: Any,
    *,
    top_k: int,
    metric_k: int = 10,
) -> RetrievalTrace:
    from app.services.query_intent import classify_query_intent, build_retrieval_lanes, RetrievalLane

    question = case.question
    candidate_k = max(top_k * 2, metric_k * 2, 10)
    bm25_docs: list[Any] = []
    started = time.perf_counter()
    if engine.bm25_index is not None and engine.bm25_index.is_indexed():
        matches = engine.bm25_index.search(query=question, top_k=candidate_k)
        bm25_docs = [doc for doc in engine.doc_store.mget([pid for pid, _ in matches]) if doc is not None]
    bm25_ms = (time.perf_counter() - started) * 1000
    started = time.perf_counter()
    dense_docs = engine.retrieve(
        question, top_n=candidate_k, hybrid_search=False, use_reranker=False,
        metadata_filter_enabled=False,
    )
    dense_ms = (time.perf_counter() - started) * 1000
    started = time.perf_counter()
    hybrid_docs = engine.retrieve(
        question, top_n=candidate_k, hybrid_search=True, use_reranker=False,
        metadata_filter_enabled=False,
        adaptive_rrf=False,
        source_quota=None,
    )
    hybrid_ms = (time.perf_counter() - started) * 1000

    started = time.perf_counter()
    decision = classify_query_intent(question)
    lanes = [lane for lane in build_retrieval_lanes(decision) if lane.name != "not_applicable"]

    # Soft Subspace Routing: Mở rộng các lane liên quan nếu phát hiện tín hiệu liên lĩnh vực
    signals = query_signals(question)
    existing_lane_names = {lane.name for lane in lanes}
    if signals.get("academic"):
        norm_q = normalize_text(question)
        has_prog = any(term in norm_q for term in ("nganh", "chuyen nganh", "chuong trinh", "khoi luong", "tin chi", "thoi gian", "mon hoc", "hoc phan", "plo"))
        has_rule = any(term in norm_q for term in ("quy che", "quy dinh", "canh bao", "thoi hoc", "tam dung", "bao luu", "tot nghiep", "xep loai"))
        if has_prog and "academic_program" not in existing_lane_names:
            lanes.append(RetrievalLane(name="academic_program", domain="academic_program", top_n=4))
        if has_rule and "academic_rules" not in existing_lane_names:
            lanes.append(RetrievalLane(name="academic_rules", domain="academic_regulation", top_n=3))
        if "academic_rules" not in existing_lane_names and "academic_program" not in existing_lane_names:
            lanes.append(RetrievalLane(name="academic_program", domain="academic_program", top_n=3))
            lanes.append(RetrievalLane(name="academic_rules", domain="academic_regulation", top_n=3))
    if signals.get("tuition") and not any(l.domain == "tuition" for l in lanes):
        lanes.append(RetrievalLane(name="actual_tuition", domain="tuition", content_kind="rate_table", fee_kind="actual_tuition", top_n=3))
    if ("hoc bong" in normalize_text(question) or "drl" in normalize_text(question)) and "scholarship" not in existing_lane_names:
        lanes.append(RetrievalLane(name="scholarship", domain="scholarship", top_n=3))

    governed: list[Any] = []
    for lane in lanes:
        governed.extend(engine.retrieve(
            query=question,
            lane=lane.name,
            fee_kind=lane.fee_kind,
            content_kind=lane.content_kind,
            domain=lane.domain,
            academic_year=decision.academic_year,
            top_n=max(lane.top_n, top_k),
            hybrid_search=True,
            use_reranker=False,
            metadata_filter_enabled=True,
            adaptive_rrf=True,
            source_quota=2,
        ))
    governed = unique_documents(governed)
    gate_reasons: list[str] = []
    if not governed:
        governed = unique_documents(hybrid_docs)
        gate_reasons.append("governed_lane_empty:hybrid_fallback")
    governed_ms = (time.perf_counter() - started) * 1000

    started = time.perf_counter()
    graph_docs, graph_trace = graph_documents(question, graph_service, tuition_catalog)
    graph_ms = (time.perf_counter() - started) * 1000
    gate_reasons.extend(graph_trace["gate_reasons"])

    # Full Proposed Candidate Pool: Governed (targeted lanes) + Hybrid (full safety net) + BM25 (lexical anchors)
    governed_candidates = unique_documents(list(governed) + list(hybrid_docs) + list(bm25_docs[:top_k]))

    # Cross-Encoder Reranking for Governed Text Candidates
    started = time.perf_counter()
    governed_ranked_metric = rerank_documents(governed_candidates, question, compressor, metric_k, min_score_threshold=0.0)
    proposed_rerank_ms = (time.perf_counter() - started) * 1000

    # Baseline & Ablation Rerankings
    started = time.perf_counter()
    hybrid_ranked_metric = rerank_documents(hybrid_docs, question, compressor, metric_k, min_score_threshold=0.0)
    hybrid_rerank_ms = (time.perf_counter() - started) * 1000

    # Dynamic Thresholding: Lọc các chunk có điểm reranker quá thấp (< 0.20) để tối ưu hóa Context Precision
    def _apply_dynamic_k(docs_list: list[Any], max_limit: int, threshold: float = 0.20, min_count: int = 2) -> list[Any]:
        filtered = [
            d for d in docs_list
            if getattr(d, "metadata", {}).get("reranker_score", 1.0) >= threshold
        ]
        if len(filtered) < min_count:
            filtered = list(docs_list[:min_count])
        return filtered[:max_limit]

    governed_ranked_top_k = _apply_dynamic_k(governed_ranked_metric, top_k, threshold=0.20, min_count=2)
    hybrid_ranked_top_k = _apply_dynamic_k(hybrid_ranked_metric, top_k, threshold=0.20, min_count=2)

    # Lexical Safeguard: If top BM25 candidates have high keyword relevance but were displaced
    # by cross-encoder semantic drift, ensure the best lexical match is retained in top_k
    if bm25_docs and governed_ranked_top_k:
        top_k_ids = {getattr(d, "metadata", {}).get("doc_id") or id(d) for d in governed_ranked_top_k}
        q_tokens = [t for t in normalize_text(question).split() if len(t) >= 4]
        for candidate_bm25 in bm25_docs[:3]:
            cand_id = getattr(candidate_bm25, "metadata", {}).get("doc_id") or id(candidate_bm25)
            if cand_id not in top_k_ids:
                cand_content = normalize_text(getattr(candidate_bm25, "page_content", ""))
                last_score = getattr(governed_ranked_top_k[-1], "metadata", {}).get("reranker_score", 1.0)
                if sum(t in cand_content for t in q_tokens) >= 3 and last_score < 0.30:
                    governed_ranked_top_k[-1] = candidate_bm25
                    break

    # T4 (Proposed Full Stack): Priority-ordered packing via merge_with_quotas (Graph + Governed Reranked)
    proposed_ranked_top_k = merge_with_quotas(governed_ranked_top_k, graph_docs, top_k=top_k)

    # T6 (w/o Graph): Preserves BGE cross-encoder ranking of governed documents without graph nodes (full top_k budget)
    no_graph_ranked = list(governed_ranked_top_k[:top_k])

    # T7 (w/o Governance): Hybrid reranked + Graph nodes
    no_gov_ranked = merge_with_quotas(hybrid_ranked_top_k, graph_docs, top_k=top_k)

    # E5 (Proposed Retrieval): Multi-evidence ranking preserving graph quotas
    proposed_metric_ranking = merge_with_quotas(governed_ranked_metric, graph_docs, top_k=metric_k)

    configs = {
        "T1": unique_documents(bm25_docs)[:top_k],
        "T2": unique_documents(dense_docs)[:top_k],
        "T3": unique_documents(hybrid_docs)[:top_k],
        "T4": proposed_ranked_top_k,
        "T5": merge_with_quotas(governed[:top_k], graph_docs, top_k=top_k),
        "T6": no_graph_ranked,
        "T7": no_gov_ranked,
        "E1": unique_documents(bm25_docs)[:metric_k],
        "E2": unique_documents(dense_docs)[:metric_k],
        "E3": unique_documents(hybrid_docs)[:metric_k],
        "E4": hybrid_ranked_metric,
        "E5": proposed_metric_ranking,
    }
    return RetrievalTrace(
        configs=configs,
        graph_hit=bool(graph_trace["graph_hit"]),
        catalog_fallback=bool(graph_trace["catalog_fallback"]),
        active_lanes=[lane.name for lane in lanes],
        gate_reasons=gate_reasons,
        latency_ms={
            "E1": bm25_ms,
            "E2": dense_ms,
            "E3": hybrid_ms,
            "E4": hybrid_ms + hybrid_rerank_ms,
            "E5": governed_ms + hybrid_ms + graph_ms + proposed_rerank_ms,
            "T1": bm25_ms,
            "T2": dense_ms,
            "T3": hybrid_ms,
            "T4": governed_ms + hybrid_ms + graph_ms + proposed_rerank_ms,
            "T5": governed_ms + hybrid_ms + graph_ms,
            "T6": governed_ms + hybrid_ms + proposed_rerank_ms,
            "T7": hybrid_ms + hybrid_rerank_ms + graph_ms,
        },
    )


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stddev(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))
