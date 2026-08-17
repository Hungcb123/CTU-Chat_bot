"""Test tie-break với CẶP CHÍNH SÁCH CŨ/MỚI có kiểm soát.

Tạo 2 tài liệu gần giống hệt nhau, index vào collection test RIÊNG (không đụng V5):
  - OLD (2024): "Sinh viên diện đặc biệt được hỗ trợ 500.000 đồng/tháng"
  - NEW (2026): "Sinh viên diện đặc biệt được hỗ trợ 700.000 đồng/tháng"

Khi hỏi "mức hỗ trợ là bao nhiêu", cross-encoder chấm 2 bản gần bằng nhau (nội dung gần
giống). Khi đó:
  - plain: xếp theo score thuần (thứ tự OLD/NEW phụ thuộc float, không đảm bảo bản mới)
  - tie-break: trong rổ điểm chênh <= tolerance, bản mới (timestamp lớn hơn) thắng
    -> bản mới (700.000) được đẩy lên, LLM trả lời ĐÚNG theo chính sách hiện hành.

Tuỳ chọn --llm: gọi Gemini trả lời theo context của từng config và kiểm tra câu trả lời
chứa giá trị nào (700.000 = ĐÚNG, 500.000 = cũ/sai).

    python scripts/test_tiebreak_old_new.py
    python scripts/test_tiebreak_old_new.py --llm
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "logs" / "tiebreak_old_new"
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from langchain_core.documents import Document  # noqa: E402

from app.services.rag_engine import (  # noqa: E402
    DEFAULT_SEARCH_K,
    AdvancedChunkingEngine,
    ParentDocumentRetriever,
)
from app.services.query_intent import RetrievalLane  # noqa: E402

# Tái sử dụng hàm xếp hạng đã verify khớp 2 class thật
_spec = importlib.util.spec_from_file_location(
    "reranker_tiebreak_ab_test",
    str(PROJECT_ROOT / "scripts" / "reranker_tiebreak_ab_test.py"),
)
_ab = importlib.util.module_from_spec(_spec)
sys.modules["reranker_tiebreak_ab_test"] = _ab
_spec.loader.exec_module(_ab)

CONFIGS = [
    ("plain", None),
    ("tie_0.05", 0.05),
    ("tie_0.02", 0.02),
    ("tie_0.01", 0.01),
]

OLD_SOURCE = "TEST_QD_HoTro_2024_Cu.md"
NEW_SOURCE = "TEST_QD_HoTro_2026_Moi.md"
OLD_AMOUNT = "500.000"
NEW_AMOUNT = "700.000"

QUERIES = [
    "Sinh viên thuộc diện hỗ trợ đặc biệt của Trường Đại học Cần Thơ được hỗ trợ chi phí học tập bao nhiêu tiền mỗi tháng?",
    "Mức hỗ trợ chi phí học tập hàng tháng cho sinh viên diện đặc biệt hiện nay là bao nhiêu?",
    "Sinh viên diện đặc biệt nhận được hỗ trợ học phí bao nhiêu một tháng?",
]


def _make_doc(source: str, amount: str, year_start: int, day: int, month: int, year: int) -> Document:
    year_end = year_start + 1
    content = (
        "QUYẾT ĐỊNH VỀ CHẾ ĐỘ HỖ TRỢ CHI PHÍ HỌC TẬP CHO SINH VIÊN THUỘC DIỆN ĐẶC BIỆT\n\n"
        "Điều 1. Sinh viên thuộc diện hỗ trợ đặc biệt của Trường Đại học Cần Thơ được hỗ trợ "
        f"chi phí học tập hàng tháng với mức {amount} đồng mỗi tháng.\n\n"
        f"Điều 2. Quyết định này áp dụng cho năm học {year_start}-{year_end} và thay thế các "
        "quyết định trước đó về cùng chế độ hỗ trợ này.\n\n"
        f"Điều 3. Quyết định này có hiệu lực từ ngày {day:02d} tháng {month:02d} năm {year}."
    )
    return Document(
        page_content=content,
        metadata={
            "source": source,
            "doc_type": "policy",
            "effective_date": f"{year:04d}-{month:02d}-{day:02d}",
            "timestamp": int(datetime(year, month, day).timestamp()),
            "status": "active",
            "index_version": "test-tiebreak-oldnew",
            "ingest_run_id": "run_tiebreak_oldnew",
            "domain": "social_support",
            "content_kind": "policy",
            "fee_kind": "not_applicable",
        },
    )


def retrieve_for_config(
    engine: AdvancedChunkingEngine,
    query: str,
    config: str,
    tolerance: float | None,
) -> tuple[list[Document], dict[str, float]]:
    qdrant_filter = engine.build_filter(
        lane="default",
        fee_kind=None,
        content_kind=None,
        domain=None,
        academic_year=None,
        metadata_filter_enabled=True,
    )
    base = ParentDocumentRetriever(
        vectorstore=engine.vector_store,
        docstore=engine.doc_store,
        child_splitter=engine.child_splitter,
        search_kwargs={"k": DEFAULT_SEARCH_K, "filter": qdrant_filter},
    )
    base_docs = list(base.invoke(query))
    if not base_docs:
        return [], {}
    scores = engine.cross_encoder.score([(query, doc.page_content) for doc in base_docs])
    docs_with_scores = list(zip(base_docs, scores))
    score_by_source: dict[str, float] = {}
    for doc, score in docs_with_scores:
        score_by_source[doc.metadata.get("source")] = score
    if config == "plain":
        ranked = _ab._plain_rank(docs_with_scores, 6)
    else:
        ranked = _ab._tiebreak_rank(docs_with_scores, 6, tolerance)
    return ranked, score_by_source


def rank_of(docs: list[Document], source: str) -> int | None:
    for position, doc in enumerate(docs, start=1):
        if doc.metadata.get("source") == source:
            return position
    return None


def build_context(docs: list[Document]) -> str:
    blocks: list[str] = []
    for doc in docs:
        metadata_prefix = (
            f"[LOẠI: KHÔNG PHÂN LOẠI | NĂM HỌC: không xác định | "
            f"NGUỒN: {doc.metadata.get('source', 'Tài liệu')}]\n"
        )
        blocks.append(f"{metadata_prefix}{doc.page_content}")
    return "\n\n---\n\n".join(blocks)


def llm_answer(question: str, context: str) -> str:
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    prompt = (
        "Bạn là trợ lý của Trường Đại học Cần Thơ. Chỉ dựa vào ngữ cảnh dưới đây, "
        "trả lời câu hỏi bằng tiếng Việt. Nếu ngữ cảnh nêu con số nào thì dùng con số đó.\n\n"
        f"Ngữ cảnh:\n{context}\n\n"
        f"Câu hỏi: {question}"
    )
    response = llm.invoke(prompt)
    if isinstance(response.content, list):
        return " ".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(response.content)


def _judge_amount(answer: str) -> str:
    cleaned = answer.replace(".", "").replace(" ", "")
    has_new = NEW_AMOUNT.replace(".", "") in cleaned
    has_old = OLD_AMOUNT.replace(".", "") in cleaned
    if has_new and not has_old:
        return "new"
    if has_old and not has_new:
        return "old"
    if has_new and has_old:
        return "both"
    return "none"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llm", action="store_true", help="Gọi Gemini trả lời từng config (cần GOOGLE_API_KEY)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--keep-data", action="store_true", help="Không dọn collection test / parent sau khi chạy")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    test_collection = f"test_tiebreak_oldnew_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Test collection: {test_collection}")

    print("Đang khởi tạo engine (collection test)...")
    engine = AdvancedChunkingEngine(
        persist_dir=str(PROJECT_ROOT / "parent_doc_storage"),
        collection_name=test_collection,
        create_collection_if_missing=True,
        metadata_filter_enabled=True,
    )

    old_doc = _make_doc(OLD_SOURCE, OLD_AMOUNT, 2024, 1, 9, 2024)
    new_doc = _make_doc(NEW_SOURCE, NEW_AMOUNT, 2026, 1, 9, 2026)
    engine.base_retriever.add_documents([old_doc, new_doc], ids=None)
    print(
        f"Ingest xong: {OLD_SOURCE} (ts={old_doc.metadata['timestamp']}) | "
        f"{NEW_SOURCE} (ts={new_doc.metadata['timestamp']})"
    )

    records: list[dict[str, Any]] = []
    for query in QUERIES:
        record: dict[str, Any] = {"query": query, "configs": {}}
        for config, tolerance in CONFIGS:
            docs, scores = retrieve_for_config(engine, query, config, tolerance)
            rank_new = rank_of(docs, NEW_SOURCE)
            rank_old = rank_of(docs, OLD_SOURCE)
            new_first = rank_new is not None and (rank_old is None or rank_new < rank_old)
            entry: dict[str, Any] = {
                "rank_new": rank_new,
                "rank_old": rank_old,
                "new_first": bool(new_first),
                "docs": [doc.metadata.get("source") for doc in docs],
            }
            if config == "plain":
                entry["score_old"] = scores.get(OLD_SOURCE)
                entry["score_new"] = scores.get(NEW_SOURCE)
            if args.llm:
                context = build_context(docs)
                answer = llm_answer(query, context)
                entry["answer"] = answer
                entry["judge"] = _judge_amount(answer)
            record["configs"][config] = entry
        records.append(record)
        verdicts = {c: record["configs"][c]["new_first"] for c, _ in CONFIGS}
        print(f"Query: {query[:70]}...")
        print(f"  new_first per config: {verdicts}")
        if args.llm:
            print(
                f"  judge per config: "
                f"{ {c: record['configs'][c]['judge'] for c, _ in CONFIGS} }"
            )

    # --- Report markdown ---
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    report_path = args.output_dir / f"tiebreak_old_new_{stamp}.md"

    lines = [
        "# Test: Tie-break với cặp chính sách cũ/mới",
        "",
        f"- Thời điểm: `{datetime.now(timezone.utc).astimezone().isoformat()}`",
        f"- Collection test: `{test_collection}` (đã dọn sau khi chạy nếu không dùng --keep-data)",
        f"- OLD: `{OLD_SOURCE}` — {OLD_AMOUNT} đ/tháng (2024-2025)",
        f"- NEW: `{NEW_SOURCE}` — {NEW_AMOUNT} đ/tháng (2026-2027)",
        f"- Giá trị đúng theo chính sách hiện hành: **{NEW_AMOUNT}**",
        f"- Cấu hình: plain + tie-break 0.05 / 0.02 / 0.01",
        "",
        "> `new_first = True` nghĩa là bản MỚI (2026, 700.000) được xếp TRƯỚC bản cũ — "
        "điều tie-break cần đạt được khi điểm sát nhau.",
        "",
    ]
    lines.append("## Tổng hợp (retrieval)")
    lines.append("")
    lines.append("| Query | score OLD | score NEW | diff | plain | tie 0.05 | tie 0.02 | tie 0.01 |")
    lines.append("|---|---:|---:|---:|---|---|---|---|")
    for record in records:
        p = record["configs"]["plain"]
        diff = None
        if p.get("score_old") is not None and p.get("score_new") is not None:
            diff = abs(p["score_old"] - p["score_new"])
        diff_str = f"{diff:.4f}" if diff is not None else "-"
        row = [
            record["query"][:45],
            f"{p.get('score_old', '-'):.4f}" if p.get("score_old") is not None else "-",
            f"{p.get('score_new', '-'):.4f}" if p.get("score_new") is not None else "-",
            diff_str,
        ]
        for config, _ in CONFIGS:
            row.append("NEW first" if record["configs"][config]["new_first"] else "OLD first")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    for record in records:
        lines.extend([f"## {record['query']}", ""])
        p = record["configs"]["plain"]
        lines.append(
            f"- score OLD={p.get('score_old'):.4f} | score NEW={p.get('score_new'):.4f} | "
            f"diff={abs(p['score_old']-p['score_new']):.4f}" if p.get("score_old") is not None else "-"
        )
        lines.append("")
        lines.append("| Config | Thứ tự docs (top) | rank NEW | rank OLD |")
        lines.append("|---|---:|---:|---:|")
        for config, _ in CONFIGS:
            entry = record["configs"][config]
            order = " > ".join(str(s) for s in entry["docs"][:4])
            lines.append(
                f"| {config} | {order} | {entry['rank_new'] or '-'} | {entry['rank_old'] or '-'} |"
            )
        if args.llm:
            lines.extend(["", "| Config | Câu trả lời Gemini | Kết quả |", "|---|---|---|"])
            for config, _ in CONFIGS:
                entry = record["configs"][config]
                judge = entry["judge"]
                label = {"new": "ĐÚNG (700.000)", "old": "SAI (500.000 cũ)", "both": "LƯỠNG LỰ", "none": "KHÔNG NÊU"}[judge]
                answer = entry.get("answer", "")
                lines.append(
                    f"| {config} | {answer[:200]} | **{label}** |"
                )
        lines.extend(["", "---", ""])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Markdown report: {report_path}")

    if not args.keep_data:
        for source in (OLD_SOURCE, NEW_SOURCE):
            try:
                engine.doc_store.delete_by_ingest(source, "run_tiebreak_oldnew")
            except Exception as exc:
                print(f"Cleanup docstore {source}: {exc}")
        try:
            engine.qdrant_client.delete_collection(test_collection)
            print(f"Đã xoá collection test: {test_collection}")
        except Exception as exc:
            print(f"Cleanup qdrant: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
