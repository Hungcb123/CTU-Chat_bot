"""A/B test độ chính xác của kỹ thuật "soft tie-break" trong TemporalCrossEncoderReranker.

So sánh 2 biến thể reranker trên toàn bộ dataset ``data/dataset.md`` (100 câu):

  A. ``tie_break`` : TemporalCrossEncoderReranker (score_tolerance=0.05) — production hiện tại
  B. ``plain``     : CrossEncoderReranker gốc (langchain_classic) — chỉ xếp hạng theo điểm cross-encoder

Mỗi câu được định tuyến intent -> lane giống hệt ``app/api/chat.py`` (kể cả fast-path
tuition catalog), rồi chạy retrieval từng lane với cả 2 biến thể (dùng chung cross_encoder).

Độ đo:
  - hit: ít nhất 1 "expected source" (tên file gốc trong dataset) xuất hiện trong docs trả về
  - rank: vị trí đầu tiên của expected source trong danh sách docs đã dedup (1-based)

Kết quả ghi ra ``logs/reranker_ab_test/reranker_ab_<timestamp>.md`` kèm JSONL evidence.
Không gọi Gemini/LLM, không cần server chat — chỉ cần Qdrant + PostgreSQL đang chạy.

Ví dụ:
    python scripts/reranker_tiebreak_ab_test.py --dry-run
    python scripts/reranker_tiebreak_ab_test.py --limit 5
    python scripts/reranker_tiebreak_ab_test.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "dataset.md"
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs" / "reranker_ab_test"
DEFAULT_OUTPUT_DIR = DEFAULT_LOG_DIR
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from langchain_core.documents import Document  # noqa: E402
from langchain_core.cross_encoders import BaseCrossEncoder  # noqa: E402

from app.services.rag_engine import (  # noqa: E402
    DEFAULT_SEARCH_K,
    AdvancedChunkingEngine,
    ContextualCompressionRetriever,
    CrossEncoderReranker,
    ParentDocumentRetriever,
    TemporalCrossEncoderReranker,
)
from app.services.query_intent import (  # noqa: E402
    QueryIntent,
    RetrievalLane,
    build_retrieval_lanes,
    classify_query_intent,
)
from app.services.tuition_catalog import TuitionRateCatalog  # noqa: E402

VARIANTS = ("tie_break", "plain")
VARIANT_LABELS = {
    "tie_break": "Tie-break (A)",
    "plain": "Plain (B)",
}
DEFAULT_TOLERANCE = 0.05

# --- Parsing dataset (regex giống scripts/evaluate_chat_dataset.py) -------------

SECTION_RE = re.compile(r"(?m)^\s*\d+\.\s*Ngữ cảnh:\s*(.+?)\s*$")
QUESTION_RE = re.compile(
    r"(?ms)^\s*Câu hỏi\s+(\d+):\s*(.*?)\s*"
    r"Câu trả lời mong đợi:\s*(.*?)\s*\n\s*\.\s*Tên file gốc:\s*"
    r"(.*?)(?=^\s*Câu hỏi\s+\d+:|^\s*\d+\.\s*Ngữ cảnh:|\Z)"
)


@dataclass(frozen=True)
class DatasetCase:
    case_id: int
    category: str
    question: str
    expected_answer: str
    expected_sources: tuple[str, ...]


def parse_dataset(path: Path) -> list[DatasetCase]:
    text = path.read_text(encoding="utf-8")
    sections = [
        (match.start(), match.group(1).strip())
        for match in SECTION_RE.finditer(text)
    ]
    if not sections:
        raise ValueError(f"No 'Ngữ cảnh' sections found in {path}")

    cases: list[DatasetCase] = []
    seen_ids: set[int] = set()
    for match in QUESTION_RE.finditer(text):
        case_id = int(match.group(1))
        if case_id in seen_ids:
            raise ValueError(f"Duplicate question id {case_id}")
        seen_ids.add(case_id)
        category = next(
            (name for position, name in reversed(sections) if position < match.start()),
            "Không phân loại",
        )
        source_text = re.sub(r"\s+", " ", match.group(4)).strip().rstrip(".")
        sources = tuple(
            part.strip() for part in source_text.split(",") if part.strip()
        )
        cases.append(
            DatasetCase(
                case_id=case_id,
                category=category,
                question=re.sub(r"\s+", " ", match.group(2)).strip(),
                expected_answer=re.sub(r"\s+", " ", match.group(3)).strip(),
                expected_sources=sources,
            )
        )
    if not cases:
        raise ValueError(f"No questions found in {path}")
    return sorted(cases, key=lambda case: case.case_id)


# --- Retrieval (giống engine._request_retriever + chat.py) ----------------------

def _deduplicate_documents(documents: Iterable[Document]) -> list[Document]:
    unique: list[Document] = []
    seen: set[Any] = set()
    for doc in documents:
        key = doc.metadata.get("doc_id") or (
            doc.metadata.get("source"),
            doc.page_content,
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(doc)
    return unique


def _plain_rank(
    docs_with_scores: list[tuple[Document, float]], top_n: int
) -> list[Document]:
    """Tái hiện đúng CrossEncoderReranker.compress_documents (langchain_classic):
    chỉ sort theo điểm cross-encoder giảm dần, lấy top_n."""
    ranked = sorted(docs_with_scores, key=lambda ds: ds[1], reverse=True)
    return [doc for doc, _ in ranked[:top_n]]


def _tiebreak_rank(
    docs_with_scores: list[tuple[Document, float]],
    top_n: int,
    tolerance: float,
) -> list[Document]:
    """Tái hiện đúng TemporalCrossEncoderReranker.compress_documents
    (app/services/rag_engine.py:165-195): tie-break theo timestamp trong rổ
    điểm chênh lệch <= tolerance."""
    ranked = sorted(
        docs_with_scores,
        key=lambda ds: (ds[1], ds[0].metadata.get("timestamp", 0) or 0),
        reverse=True,
    )
    reordered: list[tuple[Document, float]] = []
    bucket: list[tuple[Document, float]] = []
    bucket_top: float | None = None
    for doc, score in ranked:
        if bucket_top is None or (bucket_top - score) <= tolerance:
            bucket.append((doc, score))
            bucket_top = score if bucket_top is None else bucket_top
        else:
            bucket.sort(
                key=lambda ds: ds[0].metadata.get("timestamp", 0) or 0,
                reverse=True,
            )
            reordered.extend(bucket)
            bucket = [(doc, score)]
            bucket_top = score
    if bucket:
        bucket.sort(
            key=lambda ds: ds[0].metadata.get("timestamp", 0) or 0,
            reverse=True,
        )
        reordered.extend(bucket)
    return [doc for doc, _ in reordered[:top_n]]


def _retrieve_both(
    engine: AdvancedChunkingEngine,
    query: str,
    lane: RetrievalLane,
    tolerance: float,
) -> dict[str, list[Document]]:
    """Chạy 1 lần base retrieval + 1 lần cross-encoder score, rồi áp dụng cả 2
    thuật toán xếp hạng. Kết quả tương đương khi chạy 2 compressor riêng biệt
    vì cùng bộ docs đầu vào và cùng mô hình score."""
    qdrant_filter = engine.build_filter(
        lane=lane.name,
        fee_kind=lane.fee_kind,
        content_kind=lane.content_kind,
        domain=lane.domain,
        academic_year=None,
        metadata_filter_enabled=True,
    )
    base_retriever = ParentDocumentRetriever(
        vectorstore=engine.vector_store,
        docstore=engine.doc_store,
        child_splitter=engine.child_splitter,
        search_kwargs={"k": DEFAULT_SEARCH_K, "filter": qdrant_filter},
    )
    base_docs = list(base_retriever.invoke(query))
    if not base_docs:
        return {"tie_break": [], "plain": []}
    scores = engine.cross_encoder.score(
        [(query, doc.page_content) for doc in base_docs]
    )
    docs_with_scores: list[tuple[Document, float]] = list(zip(base_docs, scores))
    return {
        "tie_break": _tiebreak_rank(docs_with_scores, lane.top_n, tolerance),
        "plain": _plain_rank(docs_with_scores, lane.top_n),
    }


def _expected_hit(expected_sources: tuple[str, ...], docs: list[Document]) -> tuple[bool, int | None]:
    expected = tuple(src.casefold().strip() for src in expected_sources)
    for position, doc in enumerate(docs, start=1):
        src = str(doc.metadata.get("source") or "").casefold().strip()
        if src in expected:
            return True, position
    return False, None


def _doc_key(doc: Document) -> Any:
    return doc.metadata.get("doc_id") or (
        doc.metadata.get("source"),
        doc.page_content,
    )


def run_case(
    engine: AdvancedChunkingEngine,
    catalog: TuitionRateCatalog,
    case: DatasetCase,
    tolerance: float,
) -> dict[str, Any]:
    decision = classify_query_intent(case.question)
    lookup = catalog.lookup(case.question)
    lookup_found = lookup.status == "found"
    intent = decision.intent
    lanes = build_retrieval_lanes(decision)
    bypass = intent is QueryIntent.ACTUAL_TUITION and lookup_found

    per_variant: dict[str, dict[str, Any]] = {
        variant: {"docs": [], "hit": False, "rank": None} for variant in VARIANTS
    }
    if not bypass:
        for lane in lanes:
            if lane.name == "actual_tuition" and lookup_found:
                continue
            lane_results = _retrieve_both(engine, case.question, lane, tolerance)
            for variant in VARIANTS:
                for doc in lane_results[variant]:
                    doc.metadata = dict(doc.metadata)
                    doc.metadata["retrieval_lane"] = lane.name
                per_variant[variant]["docs"].extend(lane_results[variant])
        for variant in VARIANTS:
            docs = _deduplicate_documents(per_variant[variant]["docs"])
            hit, rank = _expected_hit(case.expected_sources, docs)
            per_variant[variant] = {"docs": docs, "hit": hit, "rank": rank}

    docs_a = per_variant["tie_break"]["docs"]
    docs_b = per_variant["plain"]["docs"]
    keys_a = [_doc_key(doc) for doc in docs_a]
    keys_b = [_doc_key(doc) for doc in docs_b]
    order_changed = not bypass and keys_a != keys_b

    hit_a = per_variant["tie_break"]["hit"]
    hit_b = per_variant["plain"]["hit"]
    rank_a = per_variant["tie_break"]["rank"]
    rank_b = per_variant["plain"]["rank"]

    if bypass:
        outcome = "bypass"
    elif hit_a and not hit_b:
        outcome = "a_only"
    elif hit_b and not hit_a:
        outcome = "b_only"
    elif hit_a and hit_b:
        outcome = "both"
    else:
        outcome = "miss"

    return {
        "case_id": case.case_id,
        "category": case.category,
        "question": case.question,
        "expected_sources": list(case.expected_sources),
        "intent": intent.value,
        "lanes": [lane.name for lane in lanes],
        "catalog_status": lookup.status,
        "bypass": bypass,
        "outcome": outcome,
        "order_changed": order_changed,
        "variants": {
            variant: {
                "hit": per_variant[variant]["hit"],
                "rank": per_variant[variant]["rank"],
                "sources": [
                    {
                        "source": doc.metadata.get("source"),
                        "lane": doc.metadata.get("retrieval_lane"),
                        "effective_date": doc.metadata.get("effective_date"),
                    }
                    for doc in per_variant[variant]["docs"]
                ],
            }
            for variant in VARIANTS
        },
    }


# --- Báo cáo markdown -----------------------------------------------------------

def _fmt_sources(record: dict[str, Any], variant: str) -> str:
    expected = tuple(src.casefold().strip() for src in record["expected_sources"])
    lines: list[str] = []
    for position, src in enumerate(record["variants"][variant]["sources"], start=1):
        source = str(src.get("source") or "?")
        marker = "*" if source.casefold().strip() in expected else " "
        date = src.get("effective_date") or "-"
        lane = src.get("lane") or "-"
        lines.append(f"{position}. [{marker}] {source} ({lane}, {date})")
    return "\n".join(lines) if lines else "(không có docs — bypass catalog)"


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    active = [r for r in records if not r["bypass"]]
    both_hit = [r for r in active if r["outcome"] == "both"]
    rank_better_a = sum(1 for r in both_hit if r["variants"]["tie_break"]["rank"] < r["variants"]["plain"]["rank"])
    rank_better_b = sum(1 for r in both_hit if r["variants"]["plain"]["rank"] < r["variants"]["tie_break"]["rank"])
    rank_equal = sum(1 for r in both_hit if r["variants"]["tie_break"]["rank"] == r["variants"]["plain"]["rank"])

    hit_a = [r for r in active if r["variants"]["tie_break"]["hit"]]
    hit_b = [r for r in active if r["variants"]["plain"]["hit"]]

    def avg_rank(items: list[dict[str, Any]], variant: str) -> float | None:
        ranks = [r["variants"][variant]["rank"] for r in items if r["variants"][variant]["rank"] is not None]
        return sum(ranks) / len(ranks) if ranks else None

    return {
        "total": len(records),
        "bypass": sum(1 for r in records if r["bypass"]),
        "active": len(active),
        "hit_a": len(hit_a),
        "hit_b": len(hit_b),
        "a_only": sum(1 for r in active if r["outcome"] == "a_only"),
        "b_only": sum(1 for r in active if r["outcome"] == "b_only"),
        "both": len(both_hit),
        "miss": sum(1 for r in active if r["outcome"] == "miss"),
        "order_changed": sum(1 for r in active if r["order_changed"]),
        "rank_better_a": rank_better_a,
        "rank_better_b": rank_better_b,
        "rank_equal": rank_equal,
        "avg_rank_a": avg_rank(active, "tie_break"),
        "avg_rank_b": avg_rank(active, "plain"),
    }


def _write_report(
    path: Path,
    records: list[dict[str, Any]],
    *,
    dataset_path: Path,
    tolerance: float,
    started_at: str,
    collection_name: str,
    points_count: int,
    reranker_model: str,
) -> None:
    summary = _aggregate(records)
    active = summary["active"]
    hit_rate_a = summary["hit_a"] / active * 100 if active else 0.0
    hit_rate_b = summary["hit_b"] / active * 100 if active else 0.0
    avg_a = f"{summary['avg_rank_a']:.2f}" if summary["avg_rank_a"] is not None else "-"
    avg_b = f"{summary['avg_rank_b']:.2f}" if summary["avg_rank_b"] is not None else "-"

    category_rows: list[str] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["category"]].append(record)
    for category, items in sorted(grouped.items()):
        act = [r for r in items if not r["bypass"]]
        cat_active = len(act)
        cat_hit_a = sum(1 for r in act if r["variants"]["tie_break"]["hit"])
        cat_hit_b = sum(1 for r in act if r["variants"]["plain"]["hit"])
        cat_rows = len(items)
        category_rows.append(
            f"| {category} | {cat_rows} | {cat_active} | "
            f"{cat_hit_a}/{cat_active} ({cat_hit_a/cat_active*100:.1f}%) | "
            f"{cat_hit_b}/{cat_active} ({cat_hit_b/cat_active*100:.1f}%) |"
        )

    outcome_labels = {
        "both": "Cả hai đều truy xuất được",
        "a_only": "Chỉ tie-break truy xuất được",
        "b_only": "Chỉ plain truy xuất được",
        "miss": "Cả hai đều miss",
        "bypass": "Bypass (catalog exact)",
    }

    lines = [
        "# A/B Test: Soft Tie-break Reranker vs Plain Cross-Encoder Reranker",
        "",
        f"- Thời điểm: `{started_at}`",
        f"- Dataset: `{dataset_path}`",
        f"- Collection: `{collection_name}` ({points_count} points)",
        f"- Reranker model: `{reranker_model}`",
        f"- score_tolerance: `{tolerance}`",
        f"- Số câu tổng: **{summary['total']}**",
        f"- Số câu có RAG retrieval (không bypass): **{summary['active']}**",
        f"- Số câu bypass catalog exact: **{summary['bypass']}**",
        "",
        "> Độ đo: expected source (tên file gốc trong dataset) có xuất hiện trong docs "
        "sau rerank + dedup hay không (hit), và vị trí rank (1-based) đầu tiên của nó.",
        "",
        "## Tổng quan",
        "",
        "| Chỉ số | Tie-break (A) | Plain (B) |",
        "|---|---:|---:|",
        f"| Hit (có expected source trong top docs) | {summary['hit_a']}/{active} (**{hit_rate_a:.2f}%**) | {summary['hit_b']}/{active} (**{hit_rate_b:.2f}%**) |",
        f"| Avg rank của expected source (khi hit) | {avg_a} | {avg_b} |",
        f"| Số câu thay đổi thứ tự docs | {summary['order_changed']} (chung) |",
        f"| Chỉ A thắng / chỉ B thắng / cả hai hit / cả hai miss | {summary['a_only']} / {summary['b_only']} / {summary['both']} / {summary['miss']} |",
        f"| Khi cả hai hit: A rank tốt hơn / B rank tốt hơn / bằng | {summary['rank_better_a']} / {summary['rank_better_b']} / {summary['rank_equal']} |",
        "",
        "## Kết quả theo nhóm",
        "",
        "| Lĩnh vực | Tổng | Active | Hit A | Hit B |",
        "|---|---:|---:|---:|---:|",
        *category_rows,
        "",
        "## Phân bố kết quả từng câu",
        "",
        "| Kết quả | Số câu |",
        "|---|---:|",
    ]
    outcome_counts: dict[str, int] = defaultdict(int)
    for record in records:
        outcome_counts[record["outcome"]] += 1
    for key, label in outcome_labels.items():
        lines.append(f"| {label} | {outcome_counts.get(key, 0)} |")
    lines.extend(["", "## Chi tiết từng câu", ""])

    for record in records:
        variant = record["variants"]
        marker_a = "PASS" if variant["tie_break"]["hit"] else "FAIL"
        marker_b = "PASS" if variant["plain"]["hit"] else "FAIL"
        lines.extend(
            [
                f"### Câu {record['case_id']} · {outcome_labels[record['outcome']]}",
                "",
                f"- Lĩnh vực: {record['category']}",
                f"- Intent: `{record['intent']}` | Lanes: `{', '.join(record['lanes'])}` | Catalog: `{record['catalog_status']}`",
                f"- Nguồn kỳ vọng: `{', '.join(record['expected_sources'])}`",
                f"- Thay đổi thứ tự giữa A và B: **{'có' if record['order_changed'] else 'không'}**",
                "",
                f"**Câu hỏi**",
                "",
                f"> {record['question']}",
                "",
                "**Tie-break (A)**",
                "",
                f"- Hit: **{marker_a}** | Rank: {variant['tie_break']['rank'] or '-'}",
                "",
                _fmt_sources(record, "tie_break"),
                "",
                "**Plain (B)**",
                "",
                f"- Hit: **{marker_b}** | Rank: {variant['plain']['rank'] or '-'}",
                "",
                _fmt_sources(record, "plain"),
                "",
                "---",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


# --- CLI ------------------------------------------------------------------------

def _filter_cases(cases: list[DatasetCase], args: argparse.Namespace) -> list[DatasetCase]:
    selected = [
        case
        for case in cases
        if (args.from_id is None or case.case_id >= args.from_id)
        and (args.to_id is None or case.case_id <= args.to_id)
        and (args.category is None or args.category.casefold() in case.category.casefold())
    ]
    if args.limit is not None:
        selected = selected[: args.limit]
    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE)
    parser.add_argument("--from-id", type=int)
    parser.add_argument("--to-id", type=int)
    parser.add_argument("--category", help="Case-insensitive category substring")
    parser.add_argument("--limit", type=int, help="Run only the first N selected cases")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--embed-device",
        default="cuda",
        help="Device cho mô hình embedding (query). Dùng 'cpu' nếu GPU 4GB bị quá tải "
        "vì cross-encoder cũng nằm trên cuda (mặc định giống production: 'cuda')",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse and list cases without retrieval")
    parser.add_argument(
        "--merge-jsonl",
        type=Path,
        action="append",
        help="Gộp nhiều file JSONL evidence (đã chạy trước đó) và sinh báo cáo .md",
    )
    parser.add_argument("--collection", default="ctu_scholarship_docs_current")
    parser.add_argument("--points", type=int, default=1303)
    parser.add_argument("--reranker-model", default="BAAI/bge-reranker-v2-m3")
    return parser


def _run_merge(args: argparse.Namespace, dataset_path: Path) -> int:
    records_by_id: dict[int, dict[str, Any]] = {}
    for path in args.merge_jsonl:
        source = path.resolve()
        count = 0
        for line in source.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            records_by_id[int(record["case_id"])] = record
            count += 1
        print(f"Loaded {count} records from {source}")
    records = [records_by_id[i] for i in sorted(records_by_id)]
    if not records:
        raise SystemExit("No records loaded from --merge-jsonl files")

    started = datetime.now(timezone.utc).astimezone()
    stamp = started.strftime("%Y%m%d_%H%M%S")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = args.output_dir / f"reranker_ab_test_merged_{stamp}.jsonl"
    report_path = args.output_dir / f"reranker_ab_test_merged_{stamp}.md"
    with jsonl_path.open("w", encoding="utf-8") as jsonl:
        for record in records:
            jsonl.write(json.dumps(record, ensure_ascii=False) + "\n")
    _write_report(
        report_path,
        records=records,
        dataset_path=dataset_path,
        tolerance=args.tolerance,
        started_at=started.isoformat(),
        collection_name=args.collection,
        points_count=args.points,
        reranker_model=args.reranker_model,
    )
    summary = _aggregate(records)
    active = summary["active"] or 1
    print(
        f"Completed (merged {len(records)}): hit A={summary['hit_a']}/{summary['active']} "
        f"({summary['hit_a']/active*100:.2f}%) | "
        f"hit B={summary['hit_b']}/{summary['active']} "
        f"({summary['hit_b']/active*100:.2f}%)"
    )
    print(f"Merged JSONL: {jsonl_path}")
    print(f"Markdown report: {report_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 0 <= args.tolerance <= 1:
        raise SystemExit("--tolerance must be between 0 and 1")
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    dataset_path = args.dataset.resolve()
    cases = _filter_cases(parse_dataset(dataset_path), args)
    if not cases:
        raise SystemExit("No dataset cases matched the selected filters")
    print(f"Parsed {len(cases)} cases from {dataset_path}")

    if args.merge_jsonl:
        return _run_merge(args, dataset_path)

    if args.dry_run:
        for case in cases:
            decision = classify_query_intent(case.question)
            print(
                f"[{case.case_id:02d}] {case.category}: {case.question}\n"
                f"    intent={decision.intent.value} expected={case.expected_sources}"
            )
        print("Dry-run complete; no retrieval was executed.")
        return 0

    print("Đang khởi tạo engine (load embedding + cross-encoder)...")
    started = datetime.now().astimezone()
    engine = AdvancedChunkingEngine(
        persist_dir=str(PROJECT_ROOT / "parent_doc_storage"),
        metadata_filter_enabled=True,
    )
    catalog = TuitionRateCatalog.load()
    point_count = engine.qdrant_client.count(engine.collection_name).count
    print(
        f"Engine sẵn sàng: collection={engine.collection_name} points={point_count} "
        f"model={engine.cross_encoder.model_name}"
    )

    if args.embed_device and args.embed_device != "cuda":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_qdrant import QdrantVectorStore

        print(f"Chuyển embedding model sang Gemini API (embed_device={args.embed_device} bỏ qua)...")
        engine.vector_store = QdrantVectorStore(
            client=engine.qdrant_client,
            collection_name=engine.collection_name,
            embedding=GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
            ),
        )
        # engine.__init__ giữ tham chiếu vector_store cũ qua base_retriever/retriever;
        # thả chúng để bản embedding cũ được thu hồi.
        engine.base_retriever = None
        engine.retriever = None
        import gc

        gc.collect()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = started.strftime("%Y%m%d_%H%M%S")
    jsonl_path = args.output_dir / f"reranker_ab_{stamp}.jsonl"
    report_path = args.output_dir / f"reranker_ab_{stamp}.md"
    records: list[dict[str, Any]] = []

    print(f"Chạy {len(cases)} câu x {len(VARIANTS)} biến thể...")
    print(f"JSONL evidence: {jsonl_path}")
    with jsonl_path.open("w", encoding="utf-8") as jsonl:
        for position, case in enumerate(cases, start=1):
            started_case = time.perf_counter()
            record = run_case(engine, catalog, case, args.tolerance)
            record["duration_seconds"] = round(time.perf_counter() - started_case, 3)
            records.append(record)
            jsonl.write(json.dumps(record, ensure_ascii=False) + "\n")
            jsonl.flush()
            v = record["variants"]
            print(
                f"[{position:02d}/{len(cases):02d}] case={case.case_id:02d} "
                f"intent={record['intent']:<18} outcome={record['outcome']:<7} "
                f"hit A={v['tie_break']['hit']} (rank {v['tie_break']['rank']}) "
                f"B={v['plain']['hit']} (rank {v['plain']['rank']}) "
                f"order_changed={record['order_changed']} "
                f"time={record['duration_seconds']:.1f}s"
            )

    reranker_model = getattr(engine.cross_encoder, "model_name", None) or ""
    _write_report(
        report_path,
        records=records,
        dataset_path=dataset_path,
        tolerance=args.tolerance,
        started_at=started.isoformat(),
        collection_name=engine.collection_name,
        points_count=point_count,
        reranker_model=reranker_model,
    )
    summary = _aggregate(records)
    print(
        f"Completed: hit A={summary['hit_a']}/{summary['active']} "
        f"({summary['hit_a']/summary['active']*100:.2f}%) | "
        f"hit B={summary['hit_b']}/{summary['active']} "
        f"({summary['hit_b']/summary['active']*100:.2f}%)"
    )
    print(f"Markdown report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
