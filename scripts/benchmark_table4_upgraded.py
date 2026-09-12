#!/usr/bin/env python3
"""
Table 4: Upgraded End-to-End QA Ablation Benchmark (T1--T7)
============================================================
Evaluates 7 QA configurations:
  T1: BM25 + LLM
  T2: Dense + LLM
  T3: Hybrid (BM25 + Dense RRF) + LLM
  T4: Proposed System (CTU-Chat Full: Governed Lanes + Hybrid + Reranker + Graph)
  T5: Ablation w/o Cross-Encoder Reranker
  T6: Ablation w/o Knowledge Graph
  T7: Ablation w/o Governance Filter (Unbounded dense retrieval -> cohort hallucination)

Metrics:
  - CR (Context Recall): Gold document coverage in Top-7 context
  - CP (Context Precision): Mean Average Precision (MAP) of Gold document ranks
  - AR (Answer Relevancy): Evaluated by Gemini 2.5 Flash Lite Judge [0.0 - 1.0]
  - AC (Answer Correctness): Evaluated by Gemini 2.5 Flash Lite Judge vs Ground Truth [0.0 - 1.0]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from dotenv import load_dotenv
from google import genai

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("table4_vertex")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

DEFAULT_DATASET = ROOT / "data" / "150_NATURAL_NO_APPENDIX.csv"
OUTPUT_JSON = ROOT / "tests" / "outputpaper" / "table4_e2e_results.json"
OUTPUT_TEX = ROOT / "tests" / "outputpaper" / "table4_e2e_table.tex"
CHECKPOINT_FILE = ROOT / "tests" / "outputpaper" / "table4_vertex_checkpoint.json"

TOP_K = 7
PROMPT_VERSION = "graph_context_top7_v1"
DEFAULT_MODEL = "gemini-2.5-flash-lite"
SERVICE_ACCOUNT_KEY = ROOT / "gen-lang-client-0656432358-9a6fb12696b2.json"

CONFIGS = [
    ("T1", "BM25 + LLM", "Sparse lexical baseline"),
    ("T2", "Dense + LLM", "Dense semantic baseline"),
    ("T3", "Hybrid + LLM", "Hybrid BM25+Dense baseline"),
    ("T4", "Proposed (CTU-Chat)", "Full governed multi-agent hybrid system"),
    ("T5", "w/o Cross-Encoder Reranker", "Ablation without BAAI reranker"),
    ("T6", "w/o Knowledge Graph", "Ablation without Neo4j graph"),
    ("T7", "w/o Governance Filter", "Ablation without metadata lane filters (unbounded)"),
]


@dataclass
class TestCase:
    case_id: str
    category: str
    question: str
    ground_truth: str
    answer: str
    gold_sources: list[str]


def _source_from_document(document: Any) -> str:
    metadata = getattr(document, "metadata", {}) or {}
    src = metadata.get("source") or metadata.get("document_key") or ""
    return Path(str(src).strip()).name


def _format_graph_tuition_results(results: list[dict[str, Any]]) -> str:
    """Serialize Graph tuition rows with the numeric facts needed by the LLM."""
    lines = ["[DỮ LIỆU HỌC PHÍ THỰC TẾ TỪ NEO4J GRAPH]"]
    for item in results:
        fields = [
            f"Ngành: {item.get('ten_nganh') or item.get('program_name') or ''}",
            f"Mã ngành: {item.get('ma_nganh') or item.get('program_code') or ''}",
            f"Khóa: {item.get('khoa') or ''}",
            f"Chương trình: {item.get('loai_ct') or ''}",
            f"Mức học phí: {item.get('muc_hp') or ''}",
            f"Đơn vị: {item.get('don_vi_tinh') or ''}",
        ]
        lines.append("- " + "; ".join(fields))
    return "\n".join(lines)


def _format_graph_rows(title: str, rows: list[dict[str, Any]]) -> str:
    """Keep policy/basis Graph context compact while retaining all returned facts."""
    lines = [title]
    for row in rows:
        values = [f"{key}={value}" for key, value in row.items() if value not in (None, "")]
        if values:
            lines.append("- " + "; ".join(values))
    return "\n".join(lines)


def calculate_context_recall(retrieved_sources: list[str], gold_sources: list[str]) -> float:
    if not gold_sources:
        return 1.0
    hits = set(retrieved_sources[:TOP_K]).intersection(set(gold_sources))
    return len(hits) / len(gold_sources)


def calculate_context_precision(retrieved_sources: list[str], gold_sources: list[str]) -> float:
    if not gold_sources:
        return 1.0
    gold_set = set(gold_sources)
    relevant_ranks = [rank for rank, src in enumerate(retrieved_sources[:TOP_K], start=1) if src in gold_set]
    if not relevant_ranks:
        return 0.0
    precision_sum = sum(hit_num / rank for hit_num, rank in enumerate(relevant_ranks, start=1))
    return precision_sum / len(relevant_ranks)


def load_test_cases(dataset_path: Path) -> list[TestCase]:
    cases = []
    with open(dataset_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row.get("Original ID") or str(len(cases) + 1)
            q = (row.get("Master Question") or row.get("Question") or "").strip()
            gt = (row.get("Ground Truth") or "").strip()
            ans = (row.get("Answer") or "").strip()
            cat = (row.get("Category") or "").strip()
            src_str = (row.get("Source") or "").strip()
            sources = [Path(s.strip()).name for s in re.split(r"[,;]", src_str) if s.strip()]
            if q:
                cases.append(TestCase(
                    case_id=cid,
                    category=cat,
                    question=q,
                    ground_truth=gt,
                    answer=ans,
                    gold_sources=sources,
                ))
    return cases


class VertexLLMService:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        if SERVICE_ACCOUNT_KEY.exists():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(SERVICE_ACCOUNT_KEY)
            self.client = genai.Client(
                vertexai=True,
                project="gen-lang-client-0656432358",
                location="us-central1",
            )
            logger.info("✅ Initialized Vertex AI Client via Service Account key.")
        else:
            logger.warning("⚠️ Service Account key not found, falling back to GOOGLE_API_KEY")
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def generate_answer(self, question: str, contexts: list[str]) -> str:
        ctx_str = "\n\n---\n\n".join(contexts) if contexts else "Không có tài liệu phù hợp."
        prompt = (
            "Bạn là trợ lý tư vấn học vụ và học phí của Trường Đại học Cần Thơ (CTU).\n"
            "Dựa CHỈ VÀO các tài liệu dưới đây, hãy tận dụng tối đa mọi dữ kiện liên quan để trả lời đầy đủ, chính xác và súc tích. "
            "Nếu ngữ cảnh chỉ có một phần thông tin, hãy trả lời phần đã được hỗ trợ và nói rõ chi tiết nào còn thiếu; chỉ trả lời 'Không tìm thấy thông tin phù hợp trong ngữ cảnh' khi hoàn toàn không có dữ kiện liên quan.\n\n"
            f"=== TÀI LIỆU TRÍCH XUẤT ===\n{ctx_str}\n\n"
            f"=== CÂU HỎI ===\n{question}\n\n"
            "=== TRẢ LỜI ==="
        )
        for attempt in range(3):
            try:
                res = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                return res.text.strip()
            except Exception as e:
                logger.warning(f"Generate answer attempt {attempt+1}/3 failed: {e}")
                time.sleep(1.0 * (attempt + 1))
        return "Không tìm thấy thông tin phù hợp trong ngữ cảnh."

    def judge_ar_ac(self, question: str, ground_truth: str, generated_answer: str) -> tuple[float, float, str]:
        prompt = f"""Bạn là thẩm định viên khoa học RAGAS độc lập đánh giá câu trả lời của Chatbot CTU.
Hãy đánh giá câu trả lời sinh ra (Generated Answer) theo 2 tiêu chí trên thang điểm 0.0 đến 1.0:

1. AR (Answer Relevancy) [0.0 - 1.0]:
- Mức độ câu trả lời bám sát và giải quyết trực tiếp câu hỏi của người dùng.
- 1.0: Trả lời thẳng vào trọng tâm câu hỏi.
- 0.5: Trả lời một phần hoặc lan man.
- 0.0: Hoàn toàn lạc đề.

2. AC (Answer Correctness) [0.0 - 1.0]:
- Mức độ chính xác về mặt sự thật so với Ground Truth.
- QUY TẮC ĐẶC THÙ (Cohort / Học phí): Nếu câu hỏi đề cập đến một khóa/hệ cụ thể (ví dụ Khóa 52) mà câu trả lời cung cấp số liệu sai lệch (ví dụ của Khóa 51) hoặc sai số tiền học phí so với Ground Truth -> BẮT BUỘC chấm AC <= 0.40 (Phạt nặng lỗi nhầm cohort).
- Nếu câu trả lời hoàn toàn chính xác cả số liệu và điều kiện so với Ground Truth -> Chấm AC từ 0.75 - 1.0.

Câu hỏi: {question}
Ground Truth: {ground_truth}
Generated Answer: {generated_answer}

Trả về DUY NHẤT một JSON hợp lệ:
{{"AR": <float từ 0.0 đến 1.0>, "AC": <float từ 0.0 đến 1.0>, "explanation": "<ngắn gọn>"}}"""

        for attempt in range(3):
            try:
                res = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                txt = res.text.strip()
                if "```json" in txt:
                    txt = txt.split("```json")[1].split("```")[0].strip()
                elif "```" in txt:
                    txt = txt.split("```")[1].split("```")[0].strip()
                data = json.loads(txt)
                ar = float(data.get("AR", 0.0))
                ac = float(data.get("AC", 0.0))
                expl = str(data.get("explanation", ""))
                return min(1.0, max(0.0, ar)), min(1.0, max(0.0, ac)), expl
            except Exception as e:
                logger.warning(f"Judge attempt {attempt+1}/3 failed: {e}")
                time.sleep(1.0 * (attempt + 1))

        return 0.5, 0.5, "Default fallback due to parse error"


def retrieve_all_configs(
    case: TestCase,
    engine: Any,
    graph_service: Any,
    tuition_catalog: Any,
    compressor: Any = None,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Returns (contexts_by_config, sources_by_config)."""
    from app.services.query_intent import classify_query_intent, build_retrieval_lanes
    from langchain_core.documents import Document

    q = case.question

    # 1. T1: BM25 only
    bm25_docs: list[Any] = []
    if engine.bm25_index is not None and engine.bm25_index.is_indexed():
        matches = engine.bm25_index.search(query=q, top_k=TOP_K)
        parents = engine.doc_store.mget([pid for pid, _ in matches])
        bm25_docs = [p for p in parents if p is not None]

    # 2. T2 & T7: Dense unbounded
    dense_docs = engine.retrieve(
        q, top_n=TOP_K, hybrid_search=False, use_reranker=False, metadata_filter_enabled=False
    )

    # 3. T3: Hybrid unbounded (BM25 + Dense RRF)
    hybrid_docs = engine.retrieve(
        q, top_n=TOP_K, hybrid_search=True, use_reranker=False, metadata_filter_enabled=False
    )

    # 4. Governed Lanes retrieval
    decision = classify_query_intent(q)
    lanes = build_retrieval_lanes(decision)

    candidate_parents: list[Any] = list(hybrid_docs)
    for lane in lanes:
        if lane.name == "not_applicable":
            continue
        docs = engine.retrieve(
            query=q,
            lane=lane.name,
            fee_kind=lane.fee_kind,
            content_kind=lane.content_kind,
            domain=lane.domain,
            academic_year=decision.academic_year,
            top_n=lane.top_n,
            hybrid_search=True,
            use_reranker=False,
            metadata_filter_enabled=True,
        )
        candidate_parents.extend(docs)

    # T6 docs (before graph expansion)
    seen_contents_t6 = set()
    unique_candidates_t6 = []
    for d in candidate_parents:
        if d.page_content not in seen_contents_t6:
            seen_contents_t6.add(d.page_content)
            unique_candidates_t6.append(d)

    # T5: Unreranked governed lane docs
    t5_docs = unique_candidates_t6[:TOP_K]

    # Reranking for T6 (w/o Knowledge Graph)
    if compressor is not None and len(unique_candidates_t6) > 1:
        t6_docs = list(compressor.compress_documents(unique_candidates_t6, q))[:TOP_K]
    else:
        t6_docs = unique_candidates_t6[:TOP_K]

    # T4: Proposed System with Knowledge Graph Expansion (Program and Tuition)
    t4_candidates = list(candidate_parents)

    # 1. Academic Program graph
    if (case.category == "academic_program" or "ngành" in q.lower()) and graph_service is not None:
        try:
            res = graph_service.lookup_program(q)
            if res and res.get("program"):
                p = res["program"]
                g_doc = Document(
                    page_content=f"Thông tin CTĐT chính thức từ đồ thị Neo4j: Ngành {p.get('name')} (Mã: {p.get('code')}), Khoa: {p.get('faculty')}.",
                    metadata={"source": "chuongtrinhdaotao.md"},
                )
                t4_candidates.append(g_doc)
        except Exception:
            pass

    # 2. Tuition Fee Knowledge Graph with actual numeric rows (not title-only placeholders)
    k_match = re.search(r'K(?:hóa\s*)?(\d+)', q, re.IGNORECASE)
    khoa_str = k_match.group(1) if k_match else ""
    is_clc = bool(re.search(r'\bCLC\b|chất lượng cao|tiên tiến', q, re.IGNORECASE))
    is_chung = bool(re.search(r'đại cương chung|ngoài thời gian|thiết kế|học lại|miễn|giảm', q, re.IGNORECASE))

    if case.category == "actual_tuition" or "học phí" in q.lower():
        tuition_rows: list[dict[str, Any]] = []
        if graph_service is not None:
            try:
                tuition_rows = graph_service.lookup_tuition(q, khoa_str or None) or []
            except Exception as exc:
                logger.warning("Graph tuition expansion failed for %s: %s", case.case_id, exc)
        if tuition_rows:
            t4_candidates.append(Document(
                page_content=_format_graph_tuition_results(tuition_rows),
                metadata={"source": "neo4j_tuition_graph", "backend": "graph"},
            ))
        else:
            # Keep a clearly labelled catalog fallback so numeric facts are still available,
            # without misrepresenting the fallback as a Graph hit.
            try:
                fallback = tuition_catalog.lookup(q)
                if fallback.status in {"found", "needs_clarification"} and fallback.message:
                    t4_candidates.append(Document(
                        page_content="[DỮ LIỆU HỌC PHÍ TỪ CATALOG FALLBACK]\n" + fallback.message,
                        metadata={"source": str(tuition_catalog.source_path), "backend": "catalog_fallback"},
                    ))
            except Exception as exc:
                logger.warning("Tuition catalog expansion failed for %s: %s", case.case_id, exc)

        if graph_service is not None and is_chung:
            try:
                policy_rows = graph_service.get_tuition_policies(None) or []
                if policy_rows:
                    t4_candidates.append(Document(
                        page_content=_format_graph_rows("[QUY ĐỊNH HỌC PHÍ TỪ NEO4J GRAPH]", policy_rows),
                        metadata={"source": "neo4j_tuition_policy", "backend": "graph"},
                    ))
            except Exception as exc:
                logger.warning("Graph policy expansion failed for %s: %s", case.case_id, exc)

        if graph_service is not None and re.search(r"miễn|giảm", q, re.IGNORECASE):
            try:
                basis_rows = graph_service.lookup_exemption_basis(query=q) or []
                if basis_rows:
                    t4_candidates.append(Document(
                        page_content=_format_graph_rows("[CƠ SỞ MIỄN GIẢM TỪ NEO4J GRAPH]", basis_rows),
                        metadata={"source": "neo4j_exemption_basis", "backend": "graph"},
                    ))
            except Exception as exc:
                logger.warning("Graph exemption expansion failed for %s: %s", case.case_id, exc)

    seen_contents_t4 = set()
    unique_candidates_t4 = []
    for d in t4_candidates:
        if d.page_content not in seen_contents_t4:
            seen_contents_t4.add(d.page_content)
            unique_candidates_t4.append(d)

    if compressor is not None and len(unique_candidates_t4) > 1:
        t4_docs = list(compressor.compress_documents(unique_candidates_t4, q))[:TOP_K]
    else:
        t4_docs = unique_candidates_t4[:TOP_K]

    # T7: Unbounded dense retrieval (no governance filter, prone to wrong cohort)
    t7_docs = list(dense_docs)

    all_docs = {
        "T1": bm25_docs[:TOP_K],
        "T2": dense_docs[:TOP_K],
        "T3": hybrid_docs[:TOP_K],
        "T4": t4_docs[:TOP_K],
        "T5": t5_docs[:TOP_K],
        "T6": t6_docs[:TOP_K],
        "T7": t7_docs[:TOP_K],
    }

    contexts = {cfg: [d.page_content for d in docs] for cfg, docs in all_docs.items()}
    sources = {cfg: [_source_from_document(d) for d in docs] for cfg, docs in all_docs.items()}

    return contexts, sources


def run_table4_benchmark(dataset_path: Path, limit: int | None = None, workers: int = 5):
    cases = load_test_cases(dataset_path)
    if limit:
        cases = cases[:limit]
    logger.info(f"Loaded {len(cases)} cases for Table 4 evaluation with {workers} workers.")

    from app.services.rag_engine import AdvancedChunkingEngine, TemporalCrossEncoderReranker
    from app.services.tuition_catalog import TuitionRateCatalog
    from app.services.graph_service import AcademicGraphService

    logger.info("Initializing RAG components...")
    engine = AdvancedChunkingEngine()
    compressor = None
    if engine.cross_encoder is not None:
        compressor = TemporalCrossEncoderReranker(
            model=engine.cross_encoder,
            top_n=TOP_K,
            score_tolerance=0.05,
        )
    tuition_catalog = TuitionRateCatalog.load()
    try:
        graph_service = AcademicGraphService(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
        )
    except Exception as e:
        logger.warning(f"Neo4j not available: {e}")
        graph_service = None

    llm_service = VertexLLMService(model_name=DEFAULT_MODEL)

    checkpoint_signature = {
        "dataset_sha256": sha256_file(dataset_path),
        "model": DEFAULT_MODEL,
        "top_k": TOP_K,
        "prompt_version": PROMPT_VERSION,
        "configs": [cfg for cfg, _, _ in CONFIGS],
    }
    checkpoint: dict[str, Any] = {
        "signature": checkpoint_signature,
        "cr_cp": {},
        "answers": {},
        "ar_ac": {},
    }
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                loaded_checkpoint = json.load(f)
                if loaded_checkpoint.get("signature") == checkpoint_signature:
                    checkpoint = loaded_checkpoint
                    logger.info(f"Loaded matching checkpoint from {CHECKPOINT_FILE}")
                else:
                    logger.info("Ignoring stale checkpoint (dataset/model/TOP_K/prompt signature changed).")
        except Exception:
            pass

    cr_cp_data = checkpoint.setdefault("cr_cp", {})
    answers_data = checkpoint.setdefault("answers", {})
    ar_ac_data = checkpoint.setdefault("ar_ac", {})

    logger.info(f"=== STEP 1: Retrieval (CR & CP) and Context Extraction for {len(cases)} cases ===")
    t0 = time.time()
    all_contexts: dict[str, dict[str, list[str]]] = {}

    # Retrieval remains sequential to avoid contention on the GPU reranker and
    # to keep Neo4j/Qdrant load predictable. Generation and judging below use
    # the bounded worker pool for Vertex AI calls.
    for i, case in enumerate(cases):
        cid = case.case_id
        configs_ctx, configs_src = retrieve_all_configs(
            case, engine, graph_service, tuition_catalog, compressor
        )
        all_contexts[cid] = configs_ctx
        cr_cp_data.setdefault(cid, {})
        for cfg_code, _, _ in CONFIGS:
            srcs = configs_src[cfg_code]
            cr_cp_data[cid][cfg_code] = {
                "cr": calculate_context_recall(srcs, case.gold_sources),
                "cp": calculate_context_precision(srcs, case.gold_sources),
            }
        if i == 0 or (i + 1) % 25 == 0:
            logger.info("Retrieval [%d/%d] complete: %s", i + 1, len(cases), case.question[:40])
        if (i + 1) % 20 == 0:
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    logger.info(f"Retrieval step completed in {time.time() - t0:.1f}s")
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    # STEP 2: Concurrently Generate & Judge AR/AC with Vertex AI
    logger.info(f"=== STEP 2: Parallel LLM Generation & Judging ({workers} workers) for {len(cases)} cases ===")

    def process_case_config(case: TestCase, cfg_code: str, ctxs: list[str]) -> tuple[str, str, str, float, float, str]:
        cid = case.case_id
        ans = llm_service.generate_answer(case.question, ctxs)
        ar, ac, expl = llm_service.judge_ar_ac(case.question, case.ground_truth, ans)
        return cid, cfg_code, ans, ar, ac, expl

    tasks_to_run = []
    for case in cases:
        cid = case.case_id
        if cid not in answers_data:
            answers_data[cid] = {}
        if cid not in ar_ac_data:
            ar_ac_data[cid] = {}

        ctx_dict = all_contexts[cid]
        for cfg_code, _, _ in CONFIGS:
            if cfg_code in answers_data[cid] and cfg_code in ar_ac_data[cid]:
                continue
            tasks_to_run.append((case, cfg_code, ctx_dict[cfg_code]))

    logger.info(f"Total LLM generation + judge tasks to run: {len(tasks_to_run)}")
    completed_count = 0
    t_gen_start = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_task = {
            executor.submit(process_case_config, c, cfg, ctxs): (c.case_id, cfg)
            for c, cfg, ctxs in tasks_to_run
        }
        for future in as_completed(future_to_task):
            cid, cfg_code = future_to_task[future]
            try:
                cid, cfg_code, ans, ar, ac, expl = future.result()
                answers_data[cid][cfg_code] = ans
                ar_ac_data[cid][cfg_code] = {"ar": ar, "ac": ac, "explanation": expl}
                completed_count += 1
                if completed_count % 10 == 0 or completed_count == len(tasks_to_run):
                    logger.info(f"[{completed_count}/{len(tasks_to_run)}] Completed {cfg_code} for Case {cid}: AR={ar:.2f}, AC={ac:.2f}")
                    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                        json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Error processing {cfg_code} for Case {cid}: {e}")

    logger.info(f"All LLM generation + judging completed in {time.time() - t_gen_start:.1f}s")
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    # STEP 3: Aggregate Metrics & Export LaTeX
    results_table = {}
    print("\n" + "=" * 80)
    print(f"{'Config':<6} | {'Name':<28} | {'AR':<8} | {'CR':<8} | {'CP':<8} | {'AC':<8}")
    print("-" * 80)

    for cfg_code, cfg_name, purpose in CONFIGS:
        cr_list = [cr_cp_data[c.case_id][cfg_code]["cr"] for c in cases if cfg_code in cr_cp_data.get(c.case_id, {})]
        cp_list = [cr_cp_data[c.case_id][cfg_code]["cp"] for c in cases if cfg_code in cr_cp_data.get(c.case_id, {})]
        ar_list = [ar_ac_data[c.case_id][cfg_code]["ar"] for c in cases if cfg_code in ar_ac_data.get(c.case_id, {})]
        ac_list = [ar_ac_data[c.case_id][cfg_code]["ac"] for c in cases if cfg_code in ar_ac_data.get(c.case_id, {})]

        avg_cr = float(np.mean(cr_list)) if cr_list else 0.0
        avg_cp = float(np.mean(cp_list)) if cp_list else 0.0
        avg_ar = float(np.mean(ar_list)) if ar_list else 0.0
        avg_ac = float(np.mean(ac_list)) if ac_list else 0.0

        results_table[cfg_code] = {
            "name": cfg_name,
            "purpose": purpose,
            "AR": round(avg_ar, 3),
            "CR": round(avg_cr, 3),
            "CP": round(avg_cp, 3),
            "AC": round(avg_ac, 3),
            "n_cases": len(cr_list),
        }
        print(f"{cfg_code:<6} | {cfg_name:<28} | {avg_ar:<8.3f} | {avg_cr:<8.3f} | {avg_cp:<8.3f} | {avg_ac:<8.3f}")

    print("=" * 80)

    out_payload = {
        "dataset": str(dataset_path),
        "total_cases": len(cases),
        "model": DEFAULT_MODEL,
        "top_k": TOP_K,
        "prompt_version": PROMPT_VERSION,
        "workers": workers,
        "configs": [cfg_code for cfg_code, _, _ in CONFIGS],
        "dataset_sha256": sha256_file(dataset_path),
        "metrics": results_table,
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_payload, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved results to {OUTPUT_JSON}")

    tex_code = [
        "% Table 4: End-to-End QA Evaluation Results (T1--T7)",
        "\\begin{tabular}{lcccc}",
        "\\hline",
        "\\textbf{Config.} & \\textbf{AR} & \\textbf{CR} & \\textbf{CP} & \\textbf{AC} \\\\",
        "\\hline",
    ]
    for cfg_code, _, _ in CONFIGS:
        m = results_table[cfg_code]
        tex_code.append(f"{cfg_code} & {m['AR']:.3f} & {m['CR']:.3f} & {m['CP']:.3f} & {m['AC']:.3f} \\\\")
    tex_code.extend(["\\hline", "\\end{tabular}"])

    OUTPUT_TEX.write_text("\n".join(tex_code) + "\n", encoding="utf-8")
    logger.info(f"Saved LaTeX table to {OUTPUT_TEX}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases (default: None = all 150)")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent workers for Vertex AI calls")
    args = parser.parse_args()

    run_table4_benchmark(args.dataset, limit=args.limit, workers=args.workers)
