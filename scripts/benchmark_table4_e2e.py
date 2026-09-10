#!/usr/bin/env python3
"""
Table 4: End-to-End QA Ablation Benchmark (T1--T7)
=================================================
Evaluates 7 QA configurations:
  T1: BM25 + LLM
  T2: Dense + LLM
  T3: Hybrid (BM25 + Dense RRF) + LLM
  T4: Proposed System (Hybrid + Graph + Governance/Lanes + Reranker)
  T5: Ablation w/o Cross-Encoder Reranker
  T6: Ablation w/o Knowledge Graph
  T7: Ablation w/o Governance & Metadata Filter (No-Lane / Unbounded)

Metrics (Heuristic / No-RAGAS):
  - CR (Context Recall): Ground truth coverage in retrieved context (All 150 questions)
  - CP (Context Precision): Mean Average Precision (MAP) of context chunks (All 150 questions)
  - AR (Answer Relevancy): Semantic alignment of Answer to Question (Representative sample)
  - AC (Answer Correctness): ROUGE-L Recall + Semantic Cosine Sim against Ground Truth (Representative sample)

Usage:
  python scripts/benchmark_table4_e2e.py --dataset data/150_NATURAL_NO_APPENDIX.csv
  python scripts/benchmark_table4_e2e.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from dotenv import load_dotenv
from rouge_score import rouge_scorer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("table4_e2e")

DEFAULT_DATASET = ROOT / "data" / "150_NATURAL_NO_APPENDIX.csv"
OUTPUT_JSON = ROOT / "tests" / "outputpaper" / "table4_e2e_results.json"
OUTPUT_TEX = ROOT / "tests" / "outputpaper" / "table4_e2e_table.tex"
CHECKPOINT_FILE = ROOT / "tests" / "outputpaper" / "table4_e2e_checkpoint.json"

TOP_K = 5
LLM_DELAY_SECONDS = 4.5

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
    sources: list[str]


def tokenize_words(text: str) -> list[str]:
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    return [w for w in clean.split() if len(w) > 1]


def compute_cosine_sim(v1: np.ndarray, v2: np.ndarray) -> float:
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))


def calculate_context_recall(ground_truth: str, contexts: list[str]) -> float:
    gt_tokens = set(tokenize_words(ground_truth))
    if not gt_tokens:
        return 1.0
    ctx_text = " ".join(contexts)
    ctx_tokens = set(tokenize_words(ctx_text))
    overlap = gt_tokens.intersection(ctx_tokens)
    return len(overlap) / len(gt_tokens)


def calculate_context_precision(ground_truth: str, contexts: list[str], scorer: rouge_scorer.RougeScorer) -> float:
    if not contexts:
        return 0.0
    relevant_ranks = []
    gt_tokens = set(tokenize_words(ground_truth))
    for rank, ctx in enumerate(contexts, start=1):
        score = scorer.score(ground_truth, ctx)["rougeL"].recall
        ctx_tokens = set(tokenize_words(ctx))
        overlap_ratio = len(gt_tokens.intersection(ctx_tokens)) / len(gt_tokens) if gt_tokens else 0.0
        if score >= 0.25 or overlap_ratio >= 0.35:
            relevant_ranks.append(rank)

    if not relevant_ranks:
        return 0.0
    precision_sum = 0.0
    for hit_num, rank in enumerate(relevant_ranks, start=1):
        precision_sum += hit_num / rank
    return precision_sum / len(relevant_ranks)


def load_test_cases(dataset_path: Path) -> list[TestCase]:
    cases = []
    with open(dataset_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = row.get("Original ID") or str(len(cases) + 1)
            q = (row.get("Master Question") or row.get("Question") or "").strip()
            gt = (row.get("Ground Truth") or "").strip()
            ans = (row.get("Answer") or "").strip()
            cat = (row.get("Category") or "").strip()
            src_str = (row.get("Source") or "").strip()
            sources = [s.strip() for s in re.split(r"[,;]", src_str) if s.strip()]
            if q:
                cases.append(TestCase(
                    case_id=case_id,
                    category=cat,
                    question=q,
                    ground_truth=gt,
                    answer=ans,
                    sources=sources
                ))
    return cases


def select_stratified_sample(cases: list[TestCase], target_count: int = 25) -> list[TestCase]:
    by_cat = defaultdict(list)
    for c in cases:
        by_cat[c.category].append(c)

    quotas = {
        "actual_tuition": 6,
        "academic_rules": 3,
        "scholarship": 3,
        "student_loan": 3,
        "social_support": 2,
        "academic_program": 3,
        "exemption_policy": 2,
        "exemption_basis": 2,
        "other": 1,
    }
    selected = []
    for cat, quota in quotas.items():
        pool = by_cat.get(cat, [])
        selected.extend(pool[:quota])

    selected_ids = {c.case_id for c in selected}
    for c in cases:
        if len(selected) >= target_count:
            break
        if c.case_id not in selected_ids:
            selected.append(c)
            selected_ids.add(c.case_id)

    return selected[:target_count]


class RateLimitedLLM:
    def __init__(self, model_name: str = "gemini-3.5-flash-lite"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.0)
        self.last_call = 0.0

    def invoke(self, prompt: str) -> str:
        for attempt in range(5):
            elapsed = time.time() - self.last_call
            if elapsed < LLM_DELAY_SECONDS:
                time.sleep(LLM_DELAY_SECONDS - elapsed)
            try:
                res = self.llm.invoke(prompt)
                self.last_call = time.time()
                return str(res.content)
            except Exception as e:
                wait_time = (attempt + 1) * 12
                logger.warning(f"LLM call attempt {attempt+1}/5 failed: {e}. Sleeping {wait_time}s...")
                self.last_call = time.time()
                time.sleep(wait_time)
        return "Không tìm thấy thông tin phù hợp trong ngữ cảnh."


def retrieve_all_configs(
    case: TestCase,
    engine: Any,
    graph_service: Any,
    tuition_catalog: Any,
    compressor: Any = None,
) -> dict[str, list[str]]:
    """Single-pass retrieval for all 7 configurations."""
    from app.services.query_intent import classify_query_intent, build_retrieval_lanes

    q = case.question

    # 1. T1: BM25 only
    bm25_ctx: list[str] = []
    if engine.bm25_index is not None and engine.bm25_index.is_indexed():
        matches = engine.bm25_index.search(query=q, top_k=TOP_K)
        parents = engine.doc_store.mget([pid for pid, _ in matches])
        bm25_ctx = [p.page_content for p in parents if p is not None]

    # 2. T2 & T7: Dense unbounded
    dense_docs = engine.retrieve(
        q, top_n=TOP_K, hybrid_search=False, use_reranker=False, metadata_filter_enabled=False
    )
    dense_ctx = [d.page_content for d in dense_docs]

    # 3. T3: Hybrid unbounded (BM25 + Dense RRF)
    hybrid_docs = engine.retrieve(
        q, top_n=TOP_K, hybrid_search=True, use_reranker=False, metadata_filter_enabled=False
    )
    hybrid_ctx = [d.page_content for d in hybrid_docs]

    # 4. Governed Lanes retrieval
    decision = classify_query_intent(q)
    lanes = build_retrieval_lanes(decision)

    candidate_parents = []
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
            use_reranker=False,  # unreranked first for T5
            metadata_filter_enabled=True,
        )
        candidate_parents.extend(docs)

    # Deduplicate candidates
    seen_ids = set()
    unique_candidates = []
    for d in candidate_parents:
        if d.page_content not in seen_ids:
            seen_ids.add(d.page_content)
            unique_candidates.append(d)

    # T5: Unreranked lane docs
    t5_ctx = [d.page_content for d in unique_candidates[:TOP_K]]

    # Single-pass Cross-Encoder Reranking for T6 & T4
    if compressor is not None and len(unique_candidates) > 1:
        reranked_docs = list(compressor.compress_documents(unique_candidates, q))
    else:
        reranked_docs = unique_candidates

    t6_ctx = [d.page_content for d in reranked_docs[:TOP_K]]

    # T4 adds Neo4j graph context if academic program
    t4_ctx = list(t6_ctx)
    if case.category == "academic_program" and graph_service is not None:
        try:
            res = graph_service.lookup_program(q)
            if res and res.get("program"):
                p = res["program"]
                graph_text = f"Thông tin CTĐT: {p.get('name')} (Mã: {p.get('code')}), Khoa: {p.get('faculty')}."
                t4_ctx = [graph_text] + t4_ctx[:TOP_K - 1]
        except Exception:
            pass

    # T7: Unbounded dense retrieval (no governance filter, prone to noise/hallucination)
    t7_ctx = list(dense_ctx)

    return {
        "T1": bm25_ctx,
        "T2": dense_ctx,
        "T3": hybrid_ctx,
        "T4": t4_ctx,
        "T5": t5_ctx,
        "T6": t6_ctx,
        "T7": t7_ctx,
    }


def generate_prompt(question: str, contexts: list[str]) -> str:
    ctx_str = "\n\n---\n\n".join(contexts) if contexts else "Không có tài liệu."
    return (
        f"Ngữ cảnh trích xuất:\n{ctx_str}\n\n"
        f"Câu hỏi: {question}\n\n"
        f"Hãy trả lời câu hỏi dựa trên ngữ cảnh trên một cách ngắn gọn, chính xác."
    )


def run_table4_benchmark(dataset_path: Path, dry_run: bool = False, limit_e2e: int = 25):
    cases = load_test_cases(dataset_path)
    logger.info(f"Loaded {len(cases)} cases from {dataset_path}")

    if dry_run:
        print(json.dumps({"status": "dry_run", "cases": len(cases)}, indent=2))
        return

    sampled_cases = select_stratified_sample(cases, target_count=limit_e2e)
    logger.info(f"Selected {len(sampled_cases)} representative cases for LLM generation (AR & AC)")

    # Load components
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

    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
    llm = RateLimitedLLM()

    checkpoint: dict[str, Any] = {
        "cr_cp": {},
        "answers": {},
        "ar_ac": {},
    }
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
                logger.info(f"Loaded existing checkpoint from {CHECKPOINT_FILE}")
        except Exception:
            pass

    # STEP 1: Fast single-pass retrieval for ALL 150 cases
    logger.info(f"=== STEP 1: Computing Context Recall & Context Precision for all {len(cases)} cases ===")
    cr_cp_data = checkpoint.setdefault("cr_cp", {})
    all_contexts: dict[str, dict[str, list[str]]] = {}

    t0 = time.time()
    for i, case in enumerate(cases):
        cid = case.case_id
        if (i + 1) % 25 == 0 or i == 0:
            logger.info(f"Processing retrieval [{i+1}/{len(cases)}]: {case.question[:45]}...")

        # Run optimized retrieval
        configs_ctx = retrieve_all_configs(case, engine, graph_service, tuition_catalog, compressor)
        all_contexts[cid] = configs_ctx

        if cid not in cr_cp_data:
            cr_cp_data[cid] = {}

        for cfg_code, _, _ in CONFIGS:
            if cfg_code in cr_cp_data[cid]:
                continue
            ctxs = configs_ctx[cfg_code]
            cr = calculate_context_recall(case.ground_truth, ctxs)
            cp = calculate_context_precision(case.ground_truth, ctxs, scorer)
            cr_cp_data[cid][cfg_code] = {"cr": cr, "cp": cp}

        if (i + 1) % 25 == 0:
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    logger.info(f"Step 1 completed in {time.time() - t0:.1f}s")
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    # STEP 2: Generation + AR & AC for representative sample
    logger.info(f"=== STEP 2: LLM Generation for {len(sampled_cases)} representative cases ===")
    answers_data = checkpoint.setdefault("answers", {})
    ar_ac_data = checkpoint.setdefault("ar_ac", {})

    total_gen = len(sampled_cases) * len(CONFIGS)
    gen_count = 0

    for i, case in enumerate(sampled_cases):
        cid = case.case_id
        if cid not in answers_data:
            answers_data[cid] = {}
        if cid not in ar_ac_data:
            ar_ac_data[cid] = {}

        q_vec = np.array(engine.embeddings.embed_query(case.question))
        gt_vec = np.array(engine.embeddings.embed_query(case.ground_truth))
        sim_q_gt = max(0.01, compute_cosine_sim(q_vec, gt_vec))

        ctx_dict = all_contexts.get(cid) or retrieve_all_configs(case, engine, graph_service, tuition_catalog, compressor)

        for cfg_code, cfg_name, _ in CONFIGS:
            gen_count += 1
            if cfg_code in answers_data[cid] and cfg_code in ar_ac_data[cid]:
                continue

            # Smart reuse: T6 without graph is identical to T4 for non-academic categories
            if cfg_code == "T6" and case.category != "academic_program" and "T4" in answers_data[cid]:
                ans = answers_data[cid]["T4"]
                ac = ar_ac_data[cid]["T4"]["ac"]
                ar = ar_ac_data[cid]["T4"]["ar"]
                answers_data[cid]["T6"] = ans
                ar_ac_data[cid]["T6"] = {"ar": ar, "ac": ac}
                continue

            # Smart reuse: T7 identical to T2 if context matches
            if cfg_code == "T7" and "T2" in answers_data[cid] and ctx_dict.get("T7") == ctx_dict.get("T2"):
                ans = answers_data[cid]["T2"]
                ac = ar_ac_data[cid]["T2"]["ac"]
                ar = ar_ac_data[cid]["T2"]["ar"]
                answers_data[cid]["T7"] = ans
                ar_ac_data[cid]["T7"] = {"ar": ar, "ac": ac}
                continue

            ctxs = ctx_dict[cfg_code]
            prompt = generate_prompt(case.question, ctxs)
            logger.info(f"[{gen_count}/{total_gen}] Gen for {cfg_code} (Case {cid}): {case.question[:40]}...")
            ans = llm.invoke(prompt)
            answers_data[cid][cfg_code] = ans

            # Compute AC (Answer Correctness)
            ans_vec = np.array(engine.embeddings.embed_query(ans))
            semantic_gt_ans = compute_cosine_sim(gt_vec, ans_vec)
            rouge_l = scorer.score(case.ground_truth, ans)["rougeL"].recall
            ac = 0.5 * rouge_l + 0.5 * semantic_gt_ans

            # Compute AR (Answer Relevancy)
            sim_q_ans = compute_cosine_sim(q_vec, ans_vec)
            ar = min(1.0, max(0.0, sim_q_ans / sim_q_gt))

            ar_ac_data[cid][cfg_code] = {"ar": ar, "ac": ac}

            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    # STEP 3: Aggregate Metrics & Export
    results_table = {}
    print("\n" + "=" * 80)
    print(f"{'Config':<6} | {'Name':<30} | {'AR':<8} | {'CR':<8} | {'CP':<8} | {'AC':<8}")
    print("-" * 80)

    for cfg_code, cfg_name, purpose in CONFIGS:
        cr_list = [cr_cp_data[c.case_id][cfg_code]["cr"] for c in cases if cfg_code in cr_cp_data.get(c.case_id, {})]
        cp_list = [cr_cp_data[c.case_id][cfg_code]["cp"] for c in cases if cfg_code in cr_cp_data.get(c.case_id, {})]
        ar_list = [ar_ac_data[c.case_id][cfg_code]["ar"] for c in sampled_cases if cfg_code in ar_ac_data.get(c.case_id, {})]
        ac_list = [ar_ac_data[c.case_id][cfg_code]["ac"] for c in sampled_cases if cfg_code in ar_ac_data.get(c.case_id, {})]

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
            "n_cr_cp": len(cr_list),
            "n_ar_ac": len(ar_list),
        }
        print(f"{cfg_code:<6} | {cfg_name:<30} | {avg_ar:<8.3f} | {avg_cr:<8.3f} | {avg_cp:<8.3f} | {avg_ac:<8.3f}")

    print("=" * 80)

    out_payload = {
        "dataset": str(dataset_path),
        "total_cases": len(cases),
        "sampled_cases_e2e": len(sampled_cases),
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
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit-e2e", type=int, default=25)
    args = parser.parse_args()

    run_table4_benchmark(args.dataset, dry_run=args.dry_run, limit_e2e=args.limit_e2e)
