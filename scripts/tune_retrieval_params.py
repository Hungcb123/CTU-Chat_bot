#!/usr/bin/env python3
"""Grid-search tuning script for retrieval parameters.

Tunes BM25 boost α, source quota, and reranker score tolerance
on scenario12_dev.jsonl using retrieval-only metrics (no LLM generation).

Usage:
    python scripts/tune_retrieval_params.py \\
        --dataset data/scenario12_dev.jsonl \\
        [--output logs/tuning/results.json]

Requires: Qdrant + PostgreSQL running (Docker Compose).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from itertools import product
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ── Parameter grid ──────────────────────────────────────────────────
ALPHA_VALUES = [1.0, 1.25, 1.5, 1.75, 2.0]
SOURCE_QUOTA_VALUES = [1, 2, 3]
SCORE_TOLERANCE_VALUES = [0.01, 0.03, 0.05, 0.08, 0.10]


@dataclass
class TuningResult:
    alpha: float
    source_quota: int
    score_tolerance: float
    hit_at_1: float = 0.0
    hit_at_3: float = 0.0
    source_recall: float = 0.0
    source_ap: float = 0.0
    mean_cp_proxy: float = 0.0
    n_cases: int = 0

    @property
    def composite_score(self) -> float:
        """Weighted composite for ranking configs."""
        return (
            0.3 * self.hit_at_1
            + 0.2 * self.hit_at_3
            + 0.3 * self.source_ap
            + 0.2 * self.mean_cp_proxy
        )


def load_dataset(path: str) -> list[dict]:
    """Load JSONL dataset with expected_sources and query."""
    cases = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            case = json.loads(line)
            if "query" in case:
                cases.append(case)
    logger.info("Loaded %d cases from %s", len(cases), path)
    return cases


def evaluate_retrieval(
    engine: Any,
    cases: list[dict],
    alpha: float,
    source_quota: int,
    score_tolerance: float,
) -> TuningResult:
    """Run retrieval for all cases with given params and compute metrics."""
    # Temporarily override env vars
    os.environ["RAG_BM25_BOOST_ALPHA"] = str(alpha)
    os.environ["RAG_SOURCE_QUOTA"] = str(source_quota)
    os.environ["RAG_RERANKER_SCORE_TOLERANCE"] = str(score_tolerance)

    # Force reload of module-level constants
    import app.services.rag_engine as rag_mod
    import app.services.lexical_anchors as anchor_mod

    rag_mod.SOURCE_QUOTA = source_quota
    rag_mod.DEFAULT_SCORE_TOLERANCE = score_tolerance
    anchor_mod._DEFAULT_BM25_BOOST = alpha

    hits_1 = 0
    hits_3 = 0
    source_recalls = []
    source_aps = []
    cp_proxies = []

    for case in cases:
        query = case["query"]
        expected_sources = set(case.get("expected_sources", []))
        lane = case.get("lane", None)
        fee_kind = case.get("fee_kind", None)

        try:
            docs = engine.retrieve(
                query,
                lane=lane,
                fee_kind=fee_kind,
                top_n=7,
                metadata_filter_enabled=True,
            )
        except Exception as exc:
            logger.warning("Retrieval failed for '%s': %s", query[:50], exc)
            continue

        if not expected_sources:
            continue

        retrieved_sources = [
            doc.metadata.get("source", "") for doc in docs
        ]

        # Hit@1
        if retrieved_sources and retrieved_sources[0] in expected_sources:
            hits_1 += 1

        # Hit@3
        top3_sources = set(retrieved_sources[:3])
        if top3_sources & expected_sources:
            hits_3 += 1

        # Source recall
        retrieved_set = set(retrieved_sources)
        recall = len(retrieved_set & expected_sources) / len(expected_sources) if expected_sources else 0
        source_recalls.append(recall)

        # Source average precision
        num_relevant = 0
        precision_sum = 0.0
        for i, src in enumerate(retrieved_sources):
            if src in expected_sources:
                num_relevant += 1
                precision_sum += num_relevant / (i + 1)
        ap = precision_sum / len(expected_sources) if expected_sources else 0
        source_aps.append(ap)

        # CP proxy: fraction of top-k that are relevant sources
        relevant_in_top = sum(1 for s in retrieved_sources if s in expected_sources)
        cp_proxies.append(relevant_in_top / len(retrieved_sources) if retrieved_sources else 0)

    n = len(source_recalls)
    if n == 0:
        return TuningResult(alpha=alpha, source_quota=source_quota, score_tolerance=score_tolerance)

    return TuningResult(
        alpha=alpha,
        source_quota=source_quota,
        score_tolerance=score_tolerance,
        hit_at_1=hits_1 / n,
        hit_at_3=hits_3 / n,
        source_recall=sum(source_recalls) / n,
        source_ap=sum(source_aps) / n,
        mean_cp_proxy=sum(cp_proxies) / n,
        n_cases=n,
    )


def main():
    parser = argparse.ArgumentParser(description="Grid-search retrieval parameter tuning")
    parser.add_argument("--dataset", required=True, help="Path to scenario12_dev.jsonl")
    parser.add_argument("--output", default=None, help="Output JSON path (default: logs/tuning/)")
    parser.add_argument("--alpha", nargs="*", type=float, default=ALPHA_VALUES, help="BM25 boost values")
    parser.add_argument("--quota", nargs="*", type=int, default=SOURCE_QUOTA_VALUES, help="Source quota values")
    parser.add_argument("--tolerance", nargs="*", type=float, default=SCORE_TOLERANCE_VALUES, help="Score tolerance values")
    args = parser.parse_args()

    cases = load_dataset(args.dataset)
    if not cases:
        logger.error("No cases loaded. Aborting.")
        sys.exit(1)

    # Initialize RAG engine (requires Qdrant + PostgreSQL)
    try:
        from app.services.rag_engine import AdvancedChunkingEngine as RAGEngine
        engine = RAGEngine()
        logger.info("RAG engine initialized successfully")
    except Exception as exc:
        logger.error("Failed to initialize RAG engine: %s", exc)
        logger.error("Make sure Docker Compose (Qdrant + PostgreSQL) is running.")
        sys.exit(1)

    # Run grid search
    grid = list(product(args.alpha, args.quota, args.tolerance))
    logger.info("Grid search: %d combinations", len(grid))

    results: list[dict] = []
    best: TuningResult | None = None

    for i, (alpha, quota, tolerance) in enumerate(grid, 1):
        logger.info(
            "[%d/%d] α=%.2f, quota=%d, tolerance=%.2f",
            i, len(grid), alpha, quota, tolerance,
        )
        t0 = time.time()
        result = evaluate_retrieval(engine, cases, alpha, quota, tolerance)
        elapsed = time.time() - t0

        logger.info(
            "  → Hit@1=%.3f, Hit@3=%.3f, SourceAP=%.3f, CP≈%.3f, composite=%.4f (%.1fs)",
            result.hit_at_1, result.hit_at_3, result.source_ap,
            result.mean_cp_proxy, result.composite_score, elapsed,
        )

        results.append({
            "alpha": alpha,
            "source_quota": quota,
            "score_tolerance": tolerance,
            "hit_at_1": result.hit_at_1,
            "hit_at_3": result.hit_at_3,
            "source_recall": result.source_recall,
            "source_ap": result.source_ap,
            "cp_proxy": result.mean_cp_proxy,
            "composite": result.composite_score,
            "n_cases": result.n_cases,
            "elapsed_sec": round(elapsed, 1),
        })

        if best is None or result.composite_score > best.composite_score:
            best = result

    # Sort by composite score
    results.sort(key=lambda r: r["composite"], reverse=True)

    # Output
    output_dir = Path(args.output or f"logs/tuning/{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}")
    output_dir.mkdir(parents=True, exist_ok=True)

    results_path = output_dir / "results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "grid_size": len(grid)}, f, indent=2, ensure_ascii=False)

    # Best config recommendation
    if best:
        recommendation = {
            "RAG_BM25_BOOST_ALPHA": best.alpha,
            "RAG_SOURCE_QUOTA": best.source_quota,
            "RAG_RERANKER_SCORE_TOLERANCE": best.score_tolerance,
            "composite_score": best.composite_score,
            "hit_at_1": best.hit_at_1,
            "source_ap": best.source_ap,
        }
        rec_path = output_dir / "best_config.json"
        with open(rec_path, "w", encoding="utf-8") as f:
            json.dump(recommendation, f, indent=2)

        logger.info("=" * 60)
        logger.info("BEST CONFIG:")
        logger.info("  RAG_BM25_BOOST_ALPHA=%.2f", best.alpha)
        logger.info("  RAG_SOURCE_QUOTA=%d", best.source_quota)
        logger.info("  RAG_RERANKER_SCORE_TOLERANCE=%.2f", best.score_tolerance)
        logger.info("  Composite=%.4f | Hit@1=%.3f | SourceAP=%.3f", best.composite_score, best.hit_at_1, best.source_ap)
        logger.info("=" * 60)
        logger.info("Results: %s", results_path)
        logger.info("Best config: %s", rec_path)


if __name__ == "__main__":
    main()
