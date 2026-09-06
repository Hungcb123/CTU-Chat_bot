"""Table 5 RAGAS runner for the controlled T1–T7 experiment."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# T1-T7: allow this benchmark to import `app`, `scripts`, and `Test_Ragas`
# when invoked directly as `python Test_Ragas/test_table5_ragas.py`.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

# T1–T7: RAGAS compatibility shim must execute before importing RAGAS.
import types
try:
    import langchain_community.chat_models.vertexai  # noqa: F401
except ModuleNotFoundError:
    vertexai_stub = types.ModuleType("langchain_community.chat_models.vertexai")
    vertexai_stub.ChatVertexAI = object
    sys.modules["langchain_community.chat_models.vertexai"] = vertexai_stub

from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
from ragas.metrics import answer_correctness, answer_relevancy, context_precision, context_recall
from ragas.run_config import RunConfig

from app.agents.graph import build_agent_graph
from app.services.graph_service import AcademicGraphService
from app.services.query_intent import classify_query_intent
from app.services.rag_engine import AdvancedChunkingEngine, TemporalCrossEncoderReranker
from app.services.tuition_catalog import TuitionRateCatalog
from app.tools.academic_program import (
    mon_chung_giua_nganh, set_graph_service, so_sanh_nganh, tim_nganh,
    tim_nganh_co_mon, tra_cuu_nganh, xem_chuoi_tien_quyet,
)
from app.tools.scholarship import tinh_tien_hoc_bong
from app.tools.tuition import tinh_toan_hoc_phi
from app.tools.tuition_graph import (
    set_tuition_catalog, set_tuition_graph_service, tra_cuu_co_so_mien_giam_graph,
    tra_cuu_hoc_phi_graph, tra_cuu_quy_dinh_hoc_phi,
)
from scripts.evaluate_chat_dataset import parse_dataset
from scripts.evaluate_ragas import RateLimitedChatGoogleGenerativeAI
from Test_Ragas.table5_experiment import (
    BenchmarkCase, CaseCheckpointStore, IncompleteMetricError, QuotaPausedError,
    checkpoint_file_path, combine_evidence, dataset_sha256, deserialize_documents,
    evidence_fingerprint,
    graph_evidence_for_query, is_api_pause_error, is_completed_case, load_csv_dataset,
    merge_graph_evidence, message_content_text, serialize_documents,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("table5_ragas")

# T1–T7: one common generator, evaluator, context budget, and metric set.
DATASET_PATH = PROJECT_ROOT / "data" / "dataset" / "100.csv"
OUTPUT_DIR = PROJECT_ROOT / "logs" / "table5_results_v3"
CONTEXT_TOP_K = 6
CANDIDATE_DEPTH = 15
METRICS = [answer_relevancy, context_precision, context_recall, answer_correctness]
METRIC_NAMES = ("answer_relevancy", "context_recall", "context_precision", "answer_correctness")
MODES = (
    "dense_only", "sparse_only", "hybrid_rrf", "hybrid_rrf_rerank",
    "hybrid_rrf_graph", "hybrid_rrf_graph_rerank", "hybrid_rrf_graph_rerank_agent",
)


def load_cases(path: Path) -> list[BenchmarkCase]:
    """T1–T7: accept the current CSV while retaining compatibility with legacy Markdown."""
    if path.suffix.casefold() == ".csv":
        return load_csv_dataset(path)
    return [
        BenchmarkCase(str(case.case_id), case.question, case.category, case.expected_answer)
        for case in parse_dataset(path)
    ]


def format_context(documents: list[Document]) -> str:
    """T1–T7: keep the same source-aware context representation for every configuration."""
    blocks = []
    for document in documents:
        source = document.metadata.get("source", "unknown")
        blocks.append(f"[SOURCE: {source}]\n{document.page_content}")
    return "\n\n---\n\n".join(blocks)


def generation_prompt(question: str, documents: list[Document]) -> str:
    """T1–T6: generation is shared; only evidence may differ across configurations."""
    return (
        "Chỉ dùng evidence dưới đây để trả lời ngắn gọn và chính xác. "
        "Nếu evidence không đủ, hãy nói rõ không đủ dữ liệu.\n\n"
        f"Evidence:\n{format_context(documents)}\n\nCâu hỏi: {question}"
    )


def rerank(engine: AdvancedChunkingEngine, query: str, candidates: list[Document], top_k: int) -> list[Document]:
    """T4/T6: rerank an existing pool only; never retrieve or add documents."""
    if engine.cross_encoder is None:
        raise RuntimeError("Reranker is unavailable; T4/T6/T7 cannot run.")
    compressor = TemporalCrossEncoderReranker(
        model=engine.cross_encoder, top_n=top_k, score_tolerance=0.05,
    )
    return list(compressor.compress_documents(candidates, query))[:top_k]

def checkpoint_fingerprint(args: argparse.Namespace, mode: str) -> dict[str, Any]:
    """T1–T7: prevents resuming a run with a different dataset or experimental setup."""
    dataset_path = Path(args.dataset)
    return {
        "schema": "table5-t1-t7-v4",
        "mode": mode,
        # T1-T7: hash dataset content so T3 candidates can be shared across machines.
        "dataset_name": dataset_path.name,
        "dataset_sha256": dataset_sha256(dataset_path),
        "candidate_depth": args.candidate_depth,
        "context_top_k": args.top_n,
        "generator_model": args.generator_model,
        "judge_model": args.judge_model,
        "ragas_version": "0.2.15",
    }


class Table5Runner:
    """Controlled T1–T7 orchestration; production retrieval and tools are reused."""

    def __init__(self, args: argparse.Namespace, cases: list[BenchmarkCase]):
        self.args = args
        self.cases = cases
        self.engine = AdvancedChunkingEngine()
        self.generator = RateLimitedChatGoogleGenerativeAI(
            model=args.generator_model, temperature=0
        )
        self.judge = RateLimitedChatGoogleGenerativeAI(model=args.judge_model, temperature=0)
        # T1-T7: RAGAS Answer Relevancy needs a live text-embedding endpoint;
        # text-embedding-004 was retired, so use Gemini's stable replacement.
        self.judge_embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        # T5/T6: Graph is used as structured evidence augmentation, never as an RRF lane.
        self.graph_service = AcademicGraphService(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
        )
        if not self.graph_service.verify_connectivity():
            self.graph_service.close()
            self.graph_service = None
        else:
            self.graph_service.ensure_data_loaded()

        # T7: initialize the same production dependencies as app/main.py.
        self.tuition_catalog = TuitionRateCatalog.load()
        set_tuition_catalog(self.tuition_catalog)
        if self.graph_service is not None:
            set_graph_service(self.graph_service)
            set_tuition_graph_service(self.graph_service)

        self.base_store = CaseCheckpointStore(
            # T3-T6: share the saved T3 candidate pool from the T3 mode directory.
            checkpoint_file_path(
                Path(args.checkpoint_dir), "hybrid_rrf", filename="candidates.json"
            ),
            fingerprint=checkpoint_fingerprint(args, "hybrid_rrf_candidates"),
        )

    def close(self) -> None:
        if self.graph_service is not None:
            self.graph_service.close()

    def store_for_mode(self, mode: str) -> CaseCheckpointStore:
        """T1-T7: isolate each mode checkpoint for independent runs and Git merges."""
        return CaseCheckpointStore(
            checkpoint_file_path(Path(self.args.checkpoint_dir), mode),
            fingerprint=checkpoint_fingerprint(self.args, mode),
        )

    def t3_candidates(self, case: BenchmarkCase) -> list[Document]:
        """T3/T4/T5/T6: retrieve the Hybrid RRF candidate pool once and checkpoint it."""
        saved = self.base_store.get(case.case_id)
        if saved and saved.get("retrieval_status") == "completed":
            return deserialize_documents(saved["candidates"])

        documents = self.engine.retrieve(
            case.question,
            hybrid_search=True,
            use_reranker=False,
            top_n=self.args.candidate_depth,
            metadata_filter_enabled=self.engine.metadata_filter_enabled,
        )
        self.base_store.upsert(case.case_id, {
            "retrieval_status": "completed",
            "candidates": serialize_documents(documents),
            "candidate_fingerprint": evidence_fingerprint(documents),
        })
        return documents

    def graph_documents(self, case: BenchmarkCase) -> list[Document]:
        """T5/T6: routing comes from the query, never from CSV Category or Ground Truth."""
        inferred_intent = classify_query_intent(case.question).intent.value
        return graph_evidence_for_query(self.graph_service, case.question, inferred_intent)

    def documents_for_mode(self, mode: str, case: BenchmarkCase) -> list[Document]:
        """T1–T6: construct evidence only; generation happens in one shared path."""
        if mode == "dense_only":
            return self.engine.retrieve(
                case.question, hybrid_search=False, use_reranker=False,
                top_n=self.args.top_n, metadata_filter_enabled=self.engine.metadata_filter_enabled,
            )
        if mode == "sparse_only":
            matches = self.engine.bm25_index.search(
                query=case.question,
                filter_dict=self.engine.build_bm25_filter(
                    metadata_filter_enabled=self.engine.metadata_filter_enabled
                ),
                top_k=self.args.candidate_depth,
            )
            return [doc for doc in self.engine.doc_store.mget([item[0] for item in matches]) if doc][
                :self.args.top_n
            ]

        candidates = self.t3_candidates(case)
        if mode == "hybrid_rrf":
            return candidates[:self.args.top_n]
        if mode == "hybrid_rrf_rerank":
            return rerank(self.engine, case.question, candidates, self.args.top_n)

        graph_documents = self.graph_documents(case)
        if mode == "hybrid_rrf_graph":
            return merge_graph_evidence(candidates, graph_documents, context_top_k=self.args.top_n)
        if mode in {"hybrid_rrf_graph_rerank", "hybrid_rrf_graph_rerank_agent"}:
            return rerank(
                self.engine, case.question,
                combine_evidence(candidates, graph_documents),
                self.args.top_n,
            )
        raise ValueError(f"Unsupported Table 5 mode: {mode}")

    async def t7_answer(self, case: BenchmarkCase, documents: list[Document]) -> str:
        """T7: run production routing/reasoning against the exact T6 evidence and no tools."""
        fixed_context = format_context(documents)
        graph = build_agent_graph(
            llm=self.generator,
            rewrite_llm=self.generator,
            engine=self.engine,
            tuition_catalog=self.tuition_catalog,
            graph_service=self.graph_service,
            academic_tools=[tra_cuu_nganh, so_sanh_nganh, tim_nganh, xem_chuoi_tien_quyet,
                            mon_chung_giua_nganh, tim_nganh_co_mon],
            financial_tools=[tra_cuu_hoc_phi_graph, tra_cuu_co_so_mien_giam_graph,
                             tra_cuu_quy_dinh_hoc_phi, tinh_toan_hoc_phi],
            scholarship_tools=[tinh_tien_hoc_bong],
            fixed_context=fixed_context,
        )
        result = await graph.ainvoke({
            "query": case.question,
            "chat_history": [],
            "search_query": "",
            "next_agent": "",
            "routing_decision": None,
            "context": "",
            "retrieval_instruction": "",
            "fixed_context": fixed_context,
            "response": "",
        })
        answer = str(result.get("response") or "").strip()
        if not answer:
            raise RuntimeError("T7 agent returned an empty answer.")
        return answer

    def evaluate_one(self, case: BenchmarkCase, answer: str, documents: list[Document]) -> dict[str, float]:
        """T1–T7: evaluate one case so every API boundary is checkpointed and resumable."""
        sample = SingleTurnSample(
            user_input=case.question,
            retrieved_contexts=[doc.page_content for doc in documents],
            response=answer,
            reference=case.expected_answer,
        )
        try:
            result = evaluate(
                EvaluationDataset([sample]),
                metrics=METRICS,
                llm=self.judge,
                embeddings=self.judge_embeddings,
                run_config=RunConfig(timeout=120, max_retries=2, max_workers=1, max_wait=4),
                raise_exceptions=True,
            )
            row = result.to_pandas().iloc[0]
            metrics = {name: (None if name not in row else row[name]) for name in METRIC_NAMES}
        except Exception as error:
            # T1-T7: classify both direct Gemini 429 errors and RAGAS timeouts
            # through the same checkpoint-safe pause path.
            if is_api_pause_error(error):
                raise QuotaPausedError(
                    str(error) or "API evaluation timed out after quota/rate-limit retries."
                ) from error
            raise

        if any(value is None or getattr(value, "item", lambda: value)() != getattr(value, "item", lambda: value)() for value in metrics.values()):
            raise IncompleteMetricError(f"RAGAS returned incomplete metrics for case {case.case_id}: {metrics}")
        return {name: float(getattr(value, "item", lambda: value)()) for name, value in metrics.items()}

    def run_mode(self, mode: str) -> dict[str, Any]:
        """T1–T7: resume each case and persist retrieval, answer, then metrics separately."""
        store = self.store_for_mode(mode)
        for index, case in enumerate(self.cases, start=1):
            saved = store.get(case.case_id)
            if is_completed_case(saved):
                logger.info("[%s] resume %s/%s case=%s", mode, index, len(self.cases), case.case_id)
                continue

            try:
                if mode == "hybrid_rrf_graph_rerank_agent":
                    # T7: load T6 output only; a missing T6 record is an explicit experiment error.
                    t6_record = self.store_for_mode("hybrid_rrf_graph_rerank").get(case.case_id)
                    if not is_completed_case(t6_record):
                        raise RuntimeError(f"T7 requires completed T6 evidence for case {case.case_id}.")
                    documents = deserialize_documents(t6_record["evidence"])
                    expected_fingerprint = str(t6_record["evidence_fingerprint"])
                    if evidence_fingerprint(documents) != expected_fingerprint:
                        raise RuntimeError(f"T6 evidence fingerprint mismatch for case {case.case_id}.")
                else:
                    documents = self.documents_for_mode(mode, case)
                    expected_fingerprint = evidence_fingerprint(documents)

                store.upsert(case.case_id, {
                    "retrieval_status": "completed",
                    "evidence": serialize_documents(documents),
                    "evidence_fingerprint": expected_fingerprint,
                })

                saved = store.get(case.case_id) or {}
                answer = str(saved.get("answer") or "").strip()
                if not answer:
                    if mode == "hybrid_rrf_graph_rerank_agent":
                        answer = asyncio.run(self.t7_answer(case, documents))
                    else:
                        # T1-T6: Gemini may return structured content blocks; persist
                        # only visible answer text, never signatures or block metadata.
                        answer = message_content_text(
                            self.generator.invoke(generation_prompt(case.question, documents)).content
                        )
                    if not answer:
                        raise RuntimeError("Generator returned an empty answer.")
                    store.upsert(case.case_id, {
                        "generation_status": "completed",
                        "answer": answer,
                        "generation_error": None,
                    })

                saved = store.get(case.case_id) or {}
                # T1–T7: a completed flag without all numeric metrics is resumable, never success.
                if not is_completed_case(saved):
                    metrics = self.evaluate_one(case, answer, documents)
                    store.upsert(case.case_id, {
                        "evaluation_status": "completed",
                        "metrics": metrics,
                        "evaluation_error": None,
                    })
                logger.info("[%s] completed %s/%s case=%s", mode, index, len(self.cases), case.case_id)

            except QuotaPausedError as error:
                store.upsert(case.case_id, {
                    "last_error": str(error),
                    "paused_reason": "quota_exhausted",
                })
                raise
            except Exception as error:
                # T1-T7: RAGAS may turn repeated 429 responses into TimeoutError;
                # preserve the current stage and stop with the same resumable exit path.
                if is_api_pause_error(error):
                    store.upsert(case.case_id, {
                        "last_error": str(error) or type(error).__name__,
                        "paused_reason": (
                            "evaluation_timeout" if isinstance(error, TimeoutError)
                            else "quota_exhausted"
                        ),
                    })
                    raise QuotaPausedError(
                        str(error) or "API evaluation timed out after quota/rate-limit retries."
                    ) from error
                store.upsert(case.case_id, {"last_error": str(error)})
                raise

        return summarize_mode(mode, store, self.cases)


def summarize_mode(mode: str, store: CaseCheckpointStore, cases: list[BenchmarkCase]) -> dict[str, Any]:
    """T1–T7: report only completed numeric metrics; incomplete cases remain visible failures."""
    completed = [store.get(case.case_id) for case in cases if is_completed_case(store.get(case.case_id))]
    if len(completed) != len(cases):
        return {"mode": mode, "status": "incomplete", "completed": len(completed), "total": len(cases)}
    metrics = {
        name: sum(record["metrics"][name] for record in completed) / len(completed)
        for name in METRIC_NAMES
    }
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case, record in zip(cases, completed):
        groups[case.category].append(record)
    return {
        "mode": mode,
        "status": "completed",
        "completed": len(completed),
        "total": len(cases),
        "metrics": metrics,
        "per_category": {
            category: {name: sum(row["metrics"][name] for row in rows) / len(rows) for name in METRIC_NAMES}
            for category, rows in groups.items()
        },
    }


def write_report(results: list[dict[str, Any]], output_dir: Path) -> None:
    """T1–T7: never render null scores as successful pending measurements."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"table5_results_{stamp}.json").write_text(
        json.dumps({"results": results}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = ["# Table 5 T1–T7", "", "| Mode | Status | Answer Relevance | Context Recall | Context Precision | Answer Correctness |", "|---|---|---:|---:|---:|---:|"]
    for result in results:
        if result["status"] != "completed":
            lines.append(f"| {result['mode']} | {result['status']} ({result['completed']}/{result['total']}) | — | — | — | — |")
            continue
        lines.append("| {mode} | completed | {answer_relevancy:.4f} | {context_recall:.4f} | {context_precision:.4f} | {answer_correctness:.4f} |".format(
            mode=result["mode"], **result["metrics"]
        ))
    (output_dir / f"table5_report_{stamp}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlled T1–T7 Table 5 RAGAS benchmark")
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument("--modes", default=",".join(MODES))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--top-n", type=int, default=CONTEXT_TOP_K)
    parser.add_argument("--candidate-depth", type=int, default=CANDIDATE_DEPTH)
    parser.add_argument("--checkpoint-dir", type=Path, default=OUTPUT_DIR / "checkpoints")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--generator-model", default="gemini-3.1-flash-lite")
    parser.add_argument("--judge-model", default="gemini-3.1-flash-lite")
    args = parser.parse_args()

    modes = [mode.strip() for mode in args.modes.split(",") if mode.strip()]
    unknown = sorted(set(modes) - set(MODES))
    if unknown:
        parser.error(f"Unsupported modes: {unknown}")
    if args.top_n < 1 or args.candidate_depth < args.top_n:
        parser.error("--candidate-depth must be at least --top-n")

    cases = load_cases(args.dataset)
    if args.limit is not None:
        cases = cases[:args.limit]
    runner = Table5Runner(args, cases)
    results: list[dict[str, Any]] = []
    try:
        # T5–T7: fail explicitly when Graph is unavailable; never silently compare T3/T4 twice.
        if any("graph" in mode for mode in modes) and runner.graph_service is None:
            raise RuntimeError("T5–T7 require Neo4j Graph evidence, but Neo4j is unavailable.")
        for mode in modes:
            results.append(runner.run_mode(mode))
            write_report(results, args.output_dir)
    except QuotaPausedError as error:
        write_report(results + [{"mode": mode, "status": "paused_quota", "completed": 0, "total": len(cases)}], args.output_dir)
        logger.error("Paused after checkpointing. Configure another API key and rerun the same command: %s", error)
        return 75
    finally:
        runner.close()

    write_report(results, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
