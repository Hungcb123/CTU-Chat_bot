"""
Test RAGAS cho Bảng 5 (Table 5): So sánh chất lượng trả lời theo 4 chế độ retrieval.

KHÔNG sửa rag_engine.py — 4 chế độ được tạo ra từ tham số có sẵn:

| Mode               | Cách gọi                                                              |
|--------------------|-----------------------------------------------------------------------|
| dense_only         | engine.retrieve(hybrid_search=False, use_reranker=False)              |
| sparse_only        | engine.bm25_index.search() + engine.doc_store.mget() trực tiếp        |
| hybrid_rrf         | engine.retrieve(hybrid_search=True, use_reranker=False)               |
| hybrid_rrf_rerank  | engine.retrieve(hybrid_search=True, use_reranker=True)                |

Ví dụ chạy:
    python Test_Ragas/test_table5_ragas.py --limit 5          # smoke test
    python Test_Ragas/test_table5_ragas.py                    # đủ 103 câu × 4 mode
    python Test_Ragas/test_table5_ragas.py --modes hybrid_rrf,hybrid_rrf_rerank

Lưu ý môi trường: ragas import `langchain_community.chat_models.vertexai` (đã bị
xoá trong langchain-community 0.4.x) nên cần stub trước khi `import ragas`.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

# --- Stub vertexai cho ragas (phải chạy trước khi import ragas) ---
try:
    import langchain_community.chat_models.vertexai  # noqa: F401
except ModuleNotFoundError:
    _stub = types.ModuleType("langchain_community.chat_models.vertexai")

    class ChatVertexAI:  # pragma: no cover — ragas chỉ đăng ký, không dùng thật
        def __init__(self, *args, **kwargs):
            raise ImportError("ChatVertexAI stub — cài langchain-google-vertexai nếu cần thật")

    _stub.ChatVertexAI = ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = _stub

import argparse
import json
import logging
from datetime import datetime

from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
from ragas.metrics import (
    answer_correctness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.run_config import RunConfig
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.services.rag_engine import AdvancedChunkingEngine
from scripts.evaluate_chat_dataset import parse_dataset
from scripts.evaluate_ragas import RateLimitedChatGoogleGenerativeAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("table5_ragas")

DATASET_PATH = PROJECT_ROOT / "data" / "dataset.md"
OUTPUT_DIR = PROJECT_ROOT / "logs" / "table5_results"

# Phải trùng DEFAULT_SEARCH_K / DEFAULT_RERANK_TOP_N trong rag_engine.py
SEARCH_K = 15
TOP_N = 6

TABLE5_METRICS = [answer_relevancy, context_precision, context_recall, answer_correctness]

METRIC_LABELS = {
    "answer_relevancy": "Answer Relevance",
    "context_recall": "Context Recall",
    "context_precision": "Context Precision",
    "answer_correctness": "Answer Correctness",
}


# ─────────────────────────────────────────────────────────────────────
# 4 CHẾ ĐỘ RETRIEVAL (không sửa engine)
# ─────────────────────────────────────────────────────────────────────

def retrieve_dense_only(engine: AdvancedChunkingEngine, query: str, top_n: int):
    return engine.retrieve(
        query, hybrid_search=False, use_reranker=False,
        top_n=top_n, metadata_filter_enabled=engine.metadata_filter_enabled,
    )


def retrieve_sparse_only(engine: AdvancedChunkingEngine, query: str, top_n: int):
    """BM25 thuần: gọi thẳng bm25_index + doc_store, bỏ qua kênh dense."""
    matches = engine.bm25_index.search(
        query=query,
        filter_dict=engine.build_bm25_filter(
            metadata_filter_enabled=engine.metadata_filter_enabled
        ),
        top_k=SEARCH_K,
    )
    parents = engine.doc_store.mget([pid for pid, _ in matches])
    return [doc for doc in parents if doc is not None][:top_n]


def retrieve_hybrid_rrf(engine: AdvancedChunkingEngine, query: str, top_n: int):
    return engine.retrieve(
        query, hybrid_search=True, use_reranker=False,
        top_n=top_n, metadata_filter_enabled=engine.metadata_filter_enabled,
    )


def retrieve_hybrid_rrf_rerank(engine: AdvancedChunkingEngine, query: str, top_n: int):
    return engine.retrieve(
        query, hybrid_search=True, use_reranker=True,
        top_n=top_n, metadata_filter_enabled=engine.metadata_filter_enabled,
    )


RETRIEVAL_MODES = {
    "dense_only": retrieve_dense_only,
    "sparse_only": retrieve_sparse_only,
    "hybrid_rrf": retrieve_hybrid_rrf,
    "hybrid_rrf_rerank": retrieve_hybrid_rrf_rerank,
}


# ─────────────────────────────────────────────────────────────────────
# PIPELINE: contexts → answer → RAGAS sample
# ─────────────────────────────────────────────────────────────────────

def build_generation_prompt(question: str, contexts: list[str]) -> str:
    context_text = "\n\n---\n\n".join(contexts)
    return (
        f"Ngữ cảnh:\n{context_text}\n\n"
        f"Câu hỏi: {question}\n\n"
        "Hãy trả lời câu hỏi dựa vào ngữ cảnh trên một cách ngắn gọn, súc tích."
    )


def collect_cases_for_mode(
    engine: AdvancedChunkingEngine,
    gen_llm: ChatGoogleGenerativeAI,
    cases: list,
    mode: str,
    top_n: int,
) -> list[SingleTurnSample]:
    retriever = RETRIEVAL_MODES[mode]
    samples: list[SingleTurnSample] = []
    empty_context = 0

    for i, case in enumerate(cases):
        try:
            docs = retriever(engine, case.question, top_n)
        except Exception as exc:
            logger.error("[%s] retrieval lỗi câu %s: %s", mode, case.case_id, exc)
            docs = []
        contexts = [doc.page_content for doc in docs]

        if contexts:
            try:
                answer = str(gen_llm.invoke(build_generation_prompt(case.question, contexts)).content)
            except Exception as exc:
                logger.error("[%s] generation lỗi câu %s: %s", mode, case.case_id, exc)
                answer = ""
        else:
            empty_context += 1
            answer = "Hệ thống không tìm thấy tài liệu phù hợp."

        logger.info("[%s] %d/%d %s → %d contexts", mode, i + 1, len(cases), case.case_id, len(contexts))
        samples.append(
            SingleTurnSample(
                user_input=case.question,
                retrieved_contexts=contexts,
                response=answer,
                reference=case.expected_answer,
            )
        )

    logger.info("[%s] Hoàn tất: %d samples, %d câu không có context", mode, len(samples), empty_context)
    return samples


def evaluate_mode(
    engine: AdvancedChunkingEngine,
    gen_llm: ChatGoogleGenerativeAI,
    judge_llm: ChatGoogleGenerativeAI,
    judge_embeddings,
    cases: list,
    mode: str,
    top_n: int,
) -> dict:
    logger.info("=" * 80)
    logger.info("ĐÁNH GIÁ MODE: %s (%d câu)", mode, len(cases))
    logger.info("=" * 80)

    samples = collect_cases_for_mode(engine, gen_llm, cases, mode, top_n)
    if not samples:
        return {"mode": mode, "status": "error", "reason": "empty_dataset"}

    try:
        result = evaluate(
            EvaluationDataset(samples),
            metrics=TABLE5_METRICS,
            llm=judge_llm,
            embeddings=judge_embeddings,
            run_config=RunConfig(timeout=120, max_retries=10, max_workers=1, max_wait=4),
            raise_exceptions=False,
        )
        df = result.to_pandas()
    except Exception as exc:
        logger.error("[%s] RAGAS evaluate lỗi: %s", mode, exc)
        return {"mode": mode, "status": "error", "reason": str(exc)}

    metrics_avg = {
        name: float(df[name].mean()) if name in df and df[name].notna().any() else None
        for name in METRIC_LABELS
    }
    failed_counts = {
        name: int(df[name].isna().sum()) if name in df else len(df)
        for name in METRIC_LABELS
    }

    # Thống kê theo domain (category của dataset)
    per_domain: dict[str, dict] = {}
    df = df.reset_index(drop=True)
    for category in sorted({c.category for c in cases}):
        idx = [i for i, c in enumerate(cases) if c.category == category and i < len(df)]
        sub = df.loc[idx]
        per_domain[category] = {
            "n_samples": len(idx),
            **{
                name: float(sub[name].mean()) if name in sub and sub[name].notna().any() else None
                for name in METRIC_LABELS
            },
        }

    logger.info("[%s] Kết quả: %s", mode, {k: (round(v, 4) if v is not None else None) for k, v in metrics_avg.items()})
    return {
        "mode": mode,
        "status": "success",
        "n_samples": len(samples),
        "metrics": metrics_avg,
        "failed_counts": failed_counts,
        "per_domain": per_domain,
    }


# ─────────────────────────────────────────────────────────────────────
# BÁO CÁO
# ─────────────────────────────────────────────────────────────────────

def _fmt(value) -> str:
    return f"{value:.4f}" if isinstance(value, float) else "pending"


def build_markdown_report(results: list[dict], config: dict) -> str:
    lines = [
        "# Bảng 5 — RAGAS Answer-Quality Metrics",
        "",
        f"- Thời gian: `{datetime.now().isoformat()}`",
        f"- Dataset: `{config['dataset']}` ({config['n_cases']} câu)",
        f"- Judge/Generation LLM: `{config['judge_model']}` (rate limit 15 RPM)",
        f"- Embeddings (RAGAS): `{config['embeddings_model']}`",
        f"- RAGAS version: `{config['ragas_version']}` | top_n: {config['top_n']}",
        "",
        "## Kết quả tổng hợp",
        "",
        "| Configuration | " + " | ".join(METRIC_LABELS.values()) + " |",
        "|---" * (len(METRIC_LABELS) + 1) + "|",
    ]
    for r in results:
        if r.get("status") != "success":
            lines.append(f"| {r['mode']} | ERROR: {r.get('reason', '?')} |")
            continue
        row = [r["mode"]] + [_fmt(r["metrics"][name]) for name in METRIC_LABELS]
        lines.append("| " + " | ".join(row) + " |")

    lines += ["", "## Số câu lỗi per metric (NaN)", ""]
    for r in results:
        if r.get("status") != "success":
            continue
        failed = ", ".join(f"{METRIC_LABELS[k]}: {v}" for k, v in r["failed_counts"].items())
        lines.append(f"- **{r['mode']}** ({r['n_samples']} mẫu): {failed}")

    lines += ["", "## Theo domain", ""]
    domains = sorted({d for r in results if r.get("status") == "success" for d in r["per_domain"]})
    header = "| Domain | n | " + " | ".join(METRIC_LABELS.values()) + " |"
    lines += [header, "|---" * (len(METRIC_LABELS) + 2) + "|"]
    for r in results:
        if r.get("status") != "success":
            continue
        for domain in domains:
            stats = r["per_domain"].get(domain)
            if not stats:
                continue
            row = [r["mode"], domain, str(stats["n_samples"])] + [
                _fmt(stats[name]) for name in METRIC_LABELS
            ]
            lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Table 5 RAGAS benchmark (4 retrieval modes)")
    parser.add_argument("--limit", type=int, default=None, help="Số câu hỏi tối đa (mặc định: tất cả)")
    parser.add_argument("--modes", type=str, default=",".join(RETRIEVAL_MODES),
                        help="Danh sách mode, phân cách bởi dấu phẩy")
    parser.add_argument("--dataset", type=str, default=str(DATASET_PATH))
    parser.add_argument("--top-n", type=int, default=TOP_N)
    args = parser.parse_args()

    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    unknown = [m for m in modes if m not in RETRIEVAL_MODES]
    if unknown:
        parser.error(f"Mode không hợp lệ: {unknown}. Hợp lệ: {sorted(RETRIEVAL_MODES)}")

    cases = parse_dataset(Path(args.dataset))
    if args.limit:
        cases = cases[: args.limit]
    logger.info("Loaded %d câu hỏi từ %s", len(cases), args.dataset)

    # ── Khởi tạo engine + guard cho từng mode ──
    engine = AdvancedChunkingEngine()

    if "sparse_only" in modes and (engine.bm25_index is None or not engine.bm25_index.is_indexed()):
        raise RuntimeError(
            "Mode 'sparse_only' cần BM25 index. Chạy: python scripts/build_bm25_index.py"
        )
    if "hybrid_rrf_rerank" in modes and engine.cross_encoder is None:
        raise RuntimeError(
            "Mode 'hybrid_rrf_rerank' cần Cross-Encoder reranker nhưng engine không nạp được "
            "(kiểm tra RAG_USE_RERANKER / RAG_RERANKER_MODEL / models/bge-reranker-v2-m3). "
            "Không thể ghi kết quả rerank khi reranker bị tắt."
        )

    gen_llm = RateLimitedChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)
    judge_llm = RateLimitedChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    judge_embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    import ragas

    config = {
        "dataset": str(Path(args.dataset).relative_to(PROJECT_ROOT)),
        "n_cases": len(cases),
        "judge_model": "gemini-3.1-flash-lite",
        "embeddings_model": "models/text-embedding-004",
        "ragas_version": ragas.__version__,
        "top_n": args.top_n,
    }

    results = []
    for mode in modes:
        results.append(
            evaluate_mode(engine, gen_llm, judge_llm, judge_embeddings, cases, mode, args.top_n)
        )

        # Lưu dần sau mỗi mode để không mất kết quả nếu dừng giữa chừng
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUTPUT_DIR / f"table5_results_{stamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"config": config, "results": results}, f, ensure_ascii=False, indent=2)
        report_path = OUTPUT_DIR / f"table5_report_{stamp}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(build_markdown_report(results, config))

    logger.info("=" * 80)
    logger.info("TÓM TẮT TABLE 5:")
    for r in results:
        if r.get("status") == "success":
            logger.info("  %s: %s", r["mode"], {k: _fmt(v) for k, v in r["metrics"].items()})
        else:
            logger.info("  %s: ERROR (%s)", r["mode"], r.get("reason"))
    logger.info("Kết quả lưu tại: %s", OUTPUT_DIR)


if __name__ == "__main__":
    main()
