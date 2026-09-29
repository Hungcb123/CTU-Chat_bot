#!/usr/bin/env python3
"""Corrected retrieval subsystem evaluation for Table 5 (V13 paper).

Evaluates 5 progressive retrieval configurations with CORRECT component stacking:
  E1: BM25 lexical baseline only
  E2: Dense vector semantic only
  E3: Hybrid RRF (BM25 + Dense) — NO reranker
  E4: Hybrid RRF + Neural Reranker (bge-reranker-v2-m3)
  E5: Full CTU-Chat retrieval (Hybrid RRF + Reranker + Graph grounding)

KEY FIXES vs old benchmark_table4.py:
  - E4 now uses load_reranker=True (was False — reranker was never loaded!)
  - E5 adds graph evidence ON TOP of reranked results (was: graph only, no reranker)
  - All configs evaluated on ALL queries (not just academic subset for graph)

Services required: PostgreSQL, Qdrant, Neo4j.
Usage:
  python scripts/run_retrieval_evaluation_v13.py --dataset tests/data/100.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_DATASET = PROJECT_ROOT / "tests" / "data" / "100.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "tests" / "outputpaper" / "table5_v13_results.json"
TOP_K = 5
METRIC_K = 10
RRF_K = 60
SOURCE_QUOTA = 2
GRAPH_DATA_DIR = PROJECT_ROOT / "data" / "markdown_graph"


@dataclass(frozen=True)
class Case:
    case_id: str
    question: str
    gold_sources: tuple[str, ...]
    category: str = ""


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _parse_source_list(value: Any) -> list[str]:
    raw = _text(value)
    if not raw:
        return []
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = []
        if isinstance(parsed, list):
            return [_text(item) for item in parsed if _text(item)]
    return [item.strip().strip("\"'") for item in re.split(r"[,;]", raw) if item.strip()]


def load_cases(path: Path) -> list[Case]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    cases = []
    for row in rows:
        question = _text(row.get("Master Question")) or _text(row.get("Question"))
        gold = tuple(dict.fromkeys(_parse_source_list(row.get("Source"))))
        if question and gold:
            cases.append(Case(
                case_id=_text(row.get("Original ID")),
                question=question,
                gold_sources=gold,
                category=_text(row.get("Category")),
            ))
    return cases


def _source_from_document(doc: Any) -> str:
    md = getattr(doc, "metadata", {}) or {}
    return _text(md.get("source") or md.get("document_key"))


def _unique_sources(values) -> list[str]:
    return list(dict.fromkeys(v for v in values if v))


def _apply_source_quota(docs: list, quota: int = SOURCE_QUOTA) -> list:
    """Apply per-source document quota, matching engine's SourceQuota filter."""
    if quota <= 0:
        return docs
    source_count: dict[str, int] = {}
    filtered: list = []
    for doc in docs:
        src = _source_from_document(doc)
        if source_count.get(src, 0) < quota:
            filtered.append(doc)
            source_count[src] = source_count.get(src, 0) + 1
    return filtered


def _rrf_merge(list_a: list[str], list_b: list[str], limit: int = METRIC_K) -> list[str]:
    scores: dict[str, float] = {}
    first_seen: dict[str, int] = {}
    for lane in (list_a, list_b):
        for rank, src in enumerate(_unique_sources(lane)):
            scores[src] = scores.get(src, 0.0) + 1.0 / (RRF_K + rank + 1)
            first_seen.setdefault(src, rank)
    ranked = sorted(scores, key=lambda s: (-scores[s], first_seen[s], s))
    return ranked[:limit]


def _graph_file_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for p in GRAPH_DATA_DIR.glob("*.md"):
        match = re.search(r"_(\d{7}C?)_", p.name)
        if match:
            mapping[match.group(1)] = p.name
    return mapping


def _graph_sources(graph_service: Any, question: str, category: str, file_by_code: dict[str, str]) -> list[str]:
    if graph_service is None or category.casefold() != "academic_program":
        return []
    results: list[dict[str, Any]] = []
    try:
        direct = graph_service.lookup_program(question)
        if direct and direct.get("program"):
            results.append(direct["program"])
    except Exception:
        pass
    try:
        results.extend(graph_service.search_programs(question) or [])
    except Exception:
        pass
    return _unique_sources(
        file_by_code[_text(r.get("code"))]
        for r in results
        if _text(r.get("code")) in file_by_code
    )


def compute_metrics(retrieved: Sequence[str], gold: Sequence[str]) -> dict[str, Any]:
    top5 = _unique_sources(retrieved)[:TOP_K]
    top10 = _unique_sources(retrieved)[:METRIC_K]
    gold_set = set(gold)
    if not gold_set:
        return {"precision_at_5": None, "recall_at_5": None, "mrr_at_10": None,
                "hit_at_1": None, "hit_at_3": None, "first_relevant_rank": None}
    hits5 = [i + 1 for i, s in enumerate(top5) if s in gold_set]
    hits10 = [i + 1 for i, s in enumerate(top10) if s in gold_set]
    return {
        "precision_at_5": len(hits5) / TOP_K,
        "recall_at_5": len(hits5) / len(gold_set),
        "mrr_at_10": 1.0 / hits10[0] if hits10 else 0.0,
        "hit_at_1": float(any(r <= 1 for r in hits10)),
        "hit_at_3": float(any(r <= 3 for r in hits10)),
        "first_relevant_rank": hits5[0] if hits5 else None,
    }


def mean_metric(rows: list[dict], key: str) -> Optional[float]:
    vals = [float(r[key]) for r in rows if r.get(key) is not None]
    return sum(vals) / len(vals) if vals else None


def run_evaluation(dataset_path: Path, output_path: Path) -> int:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")

    cases = load_cases(dataset_path)
    print(f"Loaded {len(cases)} evaluable cases from {dataset_path}")
    cats = Counter(c.category for c in cases)
    print(f"Categories: {dict(cats)}")

    # --- Init engines ---
    from app.services.rag_engine import AdvancedChunkingEngine

    # Engine WITHOUT reranker (for E1, E2, E3)
    print("Loading RAG engine (no reranker) for E1-E3...")
    engine_no_reranker = AdvancedChunkingEngine(
        persist_dir=str(PROJECT_ROOT / "parent_doc_storage"),
        load_reranker=False,
        metadata_filter_enabled=False,
    )

    # Engine WITH reranker (for E4, E5)
    print("Loading RAG engine (WITH reranker) for E4-E5...")
    engine_with_reranker = AdvancedChunkingEngine(
        persist_dir=str(PROJECT_ROOT / "parent_doc_storage"),
        load_reranker=True,
        metadata_filter_enabled=False,
    )

    # Neo4j graph service (for E5)
    graph_service = None
    graph_error = None
    try:
        from app.services.graph_service import AcademicGraphService
        graph_service = AcademicGraphService(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
        )
        if not graph_service.ensure_data_loaded():
            graph_error = "Neo4j graph data could not be loaded"
            graph_service = None
    except Exception as exc:
        graph_error = f"{type(exc).__name__}: {exc}"
    print(f"Neo4j: {'available' if graph_service else f'unavailable ({graph_error})'}")

    file_by_code = _graph_file_map()

    # --- Run evaluation ---
    per_variant: dict[str, list[dict]] = {f"E{i}": [] for i in range(1, 6)}
    errors: list[dict] = []

    for idx, case in enumerate(cases):
        try:
            latencies: dict[str, float] = {}

            # === E1: BM25 only (with source_quota for fair comparison) ===
            t0 = time.perf_counter()
            bm25_docs = []
            if engine_no_reranker.bm25_index and engine_no_reranker.bm25_index.is_indexed():
                matches = engine_no_reranker.bm25_index.search(query=case.question, top_k=METRIC_K * 3)
                parents = engine_no_reranker.doc_store.mget([pid for pid, _ in matches])
                bm25_docs = _apply_source_quota([d for d in parents if d is not None])
            latencies["E1"] = (time.perf_counter() - t0) * 1000
            e1_sources = _unique_sources(_source_from_document(d) for d in bm25_docs)

            # === E2: Dense only ===
            t0 = time.perf_counter()
            dense_docs = engine_no_reranker.retrieve(
                case.question, top_n=METRIC_K,
                hybrid_search=False, use_reranker=False, metadata_filter_enabled=False,
            )
            latencies["E2"] = (time.perf_counter() - t0) * 1000
            e2_sources = _unique_sources(_source_from_document(d) for d in dense_docs)

            # === E3: Hybrid RRF (no reranker) ===
            t0 = time.perf_counter()
            hybrid_docs = engine_no_reranker.retrieve(
                case.question, top_n=METRIC_K,
                hybrid_search=True, use_reranker=False, metadata_filter_enabled=False,
            )
            latencies["E3"] = (time.perf_counter() - t0) * 1000
            e3_sources = _unique_sources(_source_from_document(d) for d in hybrid_docs)

            # === E4: Hybrid RRF + Neural Reranker ===
            t0 = time.perf_counter()
            reranked_docs = engine_with_reranker.retrieve(
                case.question, top_n=METRIC_K,
                hybrid_search=True, use_reranker=True, metadata_filter_enabled=False,
            )
            latencies["E4"] = (time.perf_counter() - t0) * 1000
            e4_sources = _unique_sources(_source_from_document(d) for d in reranked_docs)

            # === E5: Full CTU-Chat retrieval (Reranker + Graph grounding) ===
            t0 = time.perf_counter()
            # Same reranked results as E4, plus graph evidence for academic queries
            graph_srcs = _graph_sources(graph_service, case.question, case.category, file_by_code)
            if graph_srcs:
                e5_sources = _rrf_merge(e4_sources, graph_srcs, limit=METRIC_K)
            else:
                e5_sources = e4_sources
            latencies["E5"] = (time.perf_counter() - t0) * 1000 + latencies["E4"]

            # Compute metrics for all variants
            variant_sources = {
                "E1": e1_sources,
                "E2": e2_sources,
                "E3": e3_sources,
                "E4": e4_sources,
                "E5": e5_sources,
            }
            for var, sources in variant_sources.items():
                m = compute_metrics(sources, case.gold_sources)
                per_variant[var].append({
                    "case_id": case.case_id,
                    "category": case.category,
                    "question": case.question,
                    "gold_sources": list(case.gold_sources),
                    "retrieved": sources[:TOP_K],
                    "graph_sources": graph_srcs if var == "E5" else [],
                    "latency_ms": latencies[var],
                    **m,
                })

            status = "✓" if all(
                per_variant[v][-1].get("recall_at_5", 0) and per_variant[v][-1]["recall_at_5"] > 0
                for v in ["E4", "E5"]
            ) else "·"
            print(f"  [{idx+1:3d}/{len(cases)}] {status} {case.case_id:>4s} {case.category:<20s} "
                  f"E1={per_variant['E1'][-1].get('recall_at_5', 0):.2f} "
                  f"E3={per_variant['E3'][-1].get('recall_at_5', 0):.2f} "
                  f"E4={per_variant['E4'][-1].get('recall_at_5', 0):.2f} "
                  f"E5={per_variant['E5'][-1].get('recall_at_5', 0):.2f}")

        except Exception as exc:
            errors.append({"case_id": case.case_id, "error": f"{type(exc).__name__}: {exc}"})
            print(f"  [{idx+1:3d}/{len(cases)}] ✗ {case.case_id} ERROR: {exc}")

    # --- Aggregate results ---
    labels = {
        "E1": "BM25 Lexical Baseline",
        "E2": "Dense Vector Semantic",
        "E3": "Hybrid RRF (BM25 + Dense)",
        "E4": "Hybrid + Neural Reranker",
        "E5": "CTU-Chat Full Retrieval",
    }
    summary: dict[str, dict] = {}
    for var, rows in per_variant.items():
        summary[var] = {
            "configuration": labels[var],
            "cases": len(rows),
            "hit_at_1": mean_metric(rows, "hit_at_1"),
            "hit_at_3": mean_metric(rows, "hit_at_3"),
            "precision_at_5": mean_metric(rows, "precision_at_5"),
            "recall_at_5": mean_metric(rows, "recall_at_5"),
            "mrr_at_10": mean_metric(rows, "mrr_at_10"),
            "latency_ms": mean_metric(rows, "latency_ms"),
            "details": rows,
        }

    payload = {
        "status": "completed" if not errors else "completed_with_errors",
        "benchmark": "Table 5 V13 - Corrected Retrieval Evaluation",
        "dataset": str(dataset_path),
        "cases_loaded": len(cases),
        "errors": errors,
        "graph": {"available": graph_service is not None, "error": graph_error},
        "variants": summary,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Print summary table
    print("\n" + "=" * 90)
    print(f"{'Configuration':<35s} | {'Hit@1':>6s} | {'Hit@3':>6s} | {'P@5':>6s} | {'R@5':>6s} | {'MRR':>6s} | {'Lat(ms)':>8s}")
    print("-" * 90)
    for var in ["E1", "E2", "E3", "E4", "E5"]:
        s = summary[var]
        def fmt(v):
            return f"{v:.4f}" if v is not None else "N/A"
        def fmtl(v):
            return f"{v:.1f}" if v is not None else "N/A"
        print(f"{labels[var]:<35s} | {fmt(s['hit_at_1']):>6s} | {fmt(s['hit_at_3']):>6s} | "
              f"{fmt(s['precision_at_5']):>6s} | {fmt(s['recall_at_5']):>6s} | "
              f"{fmt(s['mrr_at_10']):>6s} | {fmtl(s['latency_ms']):>8s}")
    print("=" * 90)
    print(f"\nResults saved to: {output_path}")
    if errors:
        print(f"WARNING: {len(errors)} errors occurred!")
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return run_evaluation(args.dataset, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
