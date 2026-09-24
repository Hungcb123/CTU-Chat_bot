#!/usr/bin/env python3
"""V13 Result Summarizer — Aggregate results from architecture experiments.

Reads results.jsonl from an experiment run and produces:
1. Scenario 1 summary table (S1-A vs S1-B vs S1-C)
2. Scenario 2 ablation delta table
3. Cross-domain query breakdown
4. Query-family breakdown
5. Bootstrap confidence intervals for pairwise comparisons
6. LaTeX-ready table fragments

Usage:
  python scripts/summarize_v13_results.py logs/v13_architecture/run_YYYYMMDD_HHMMSS/
  python scripts/summarize_v13_results.py logs/v13_architecture/run_YYYYMMDD_HHMMSS/ --latex
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

import numpy as np


def load_results(results_path: Path) -> list[dict[str, Any]]:
    """Load all result records from a JSONL file."""
    records = []
    with results_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                record = json.loads(line)
                if "error" not in record:
                    records.append(record)
    return records


def group_by(records: list[dict], key: str) -> dict[str, list[dict]]:
    groups = defaultdict(list)
    for r in records:
        groups[r[key]].append(r)
    return dict(groups)


def aggregate_query(records: list[dict]) -> dict[str, float]:
    """Aggregate metrics for a single query across repetitions (mean)."""
    return {
        "source_recall": np.mean([r["source_recall"] for r in records]),
        "source_ap": np.mean([r["source_ap"] for r in records]),
        "fact_coverage": np.mean([r["fact_coverage"] for r in records]),
        "input_tokens": np.mean([r["input_tokens"] for r in records]),
        "output_tokens": np.mean([r["output_tokens"] for r in records]),
        "latency_ms": np.mean([r["latency_ms"] for r in records]),
        "tool_calls": np.mean([r["tool_calls"] for r in records]),
        "llm_calls": np.mean([r["llm_calls"] for r in records]),
    }


def config_summary(records: list[dict]) -> dict[str, float]:
    """Compute config-level means from query-level aggregated records."""
    by_query = group_by(records, "query_id")
    query_aggs = [aggregate_query(recs) for recs in by_query.values()]

    metrics = {}
    for key in query_aggs[0]:
        values = [qa[key] for qa in query_aggs]
        metrics[f"{key}_mean"] = np.mean(values)
        metrics[f"{key}_std"] = np.std(values, ddof=1) if len(values) > 1 else 0.0
    metrics["n_queries"] = len(query_aggs)
    return metrics


def bootstrap_ci(
    values_a: Sequence[float],
    values_b: Sequence[float],
    n_bootstrap: int = 10000,
    ci: float = 0.95,
) -> dict[str, float]:
    """Compute paired bootstrap CI for mean difference (a - b)."""
    rng = np.random.default_rng(42)
    n = len(values_a)
    assert n == len(values_b), "Paired comparison requires same length"

    diffs = np.array(values_a) - np.array(values_b)
    boot_means = np.array([
        np.mean(rng.choice(diffs, size=n, replace=True))
        for _ in range(n_bootstrap)
    ])

    alpha = (1 - ci) / 2
    return {
        "mean_diff": float(np.mean(diffs)),
        "ci_lower": float(np.percentile(boot_means, 100 * alpha)),
        "ci_upper": float(np.percentile(boot_means, 100 * (1 - alpha))),
        "n": n,
    }


def pairwise_analysis(
    records: list[dict],
    config_a: str,
    config_b: str,
    metric: str,
) -> dict[str, Any]:
    """Compute paired bootstrap CI between two configs for a given metric."""
    by_config = group_by(records, "configuration")
    recs_a = by_config.get(config_a, [])
    recs_b = by_config.get(config_b, [])

    # Aggregate to query level
    qa_a = {qid: aggregate_query(recs) for qid, recs in group_by(recs_a, "query_id").items()}
    qa_b = {qid: aggregate_query(recs) for qid, recs in group_by(recs_b, "query_id").items()}

    common = sorted(set(qa_a.keys()) & set(qa_b.keys()))
    if not common:
        return {"error": f"No common queries between {config_a} and {config_b}"}

    values_a = [qa_a[qid][metric] for qid in common]
    values_b = [qa_b[qid][metric] for qid in common]

    return {
        "config_a": config_a,
        "config_b": config_b,
        "metric": metric,
        **bootstrap_ci(values_a, values_b),
    }


def print_scenario1_table(records: list[dict]):
    """Print Scenario 1 architecture comparison summary."""
    print("\n" + "=" * 80)
    print("SCENARIO 1: Architecture-Level Comparison")
    print("=" * 80)

    s1_configs = ["S1-A", "S1-B", "S1-C"]
    by_config = group_by(records, "configuration")

    headers = ["Config", "Src.R↑", "Src.AP↑", "FactCov↑", "InTok↓", "Lat(ms)↓", "Tools", "N"]
    print(f"{'Config':<25} {'Src.R':>7} {'Src.AP':>7} {'FactCov':>8} {'InTok':>8} {'Lat(ms)':>8} {'Tools':>6} {'N':>4}")
    print("-" * 80)

    for config in s1_configs:
        recs = by_config.get(config, [])
        if not recs:
            print(f"{config:<25} {'---':>7}")
            continue
        s = config_summary(recs)
        print(
            f"{config:<25} "
            f"{s['source_recall_mean']:>7.3f} "
            f"{s['source_ap_mean']:>7.3f} "
            f"{s['fact_coverage_mean']:>8.3f} "
            f"{s['input_tokens_mean']:>8.0f} "
            f"{s['latency_ms_mean']:>8.0f} "
            f"{s['tool_calls_mean']:>6.1f} "
            f"{s['n_queries']:>4}"
        )

    # Pairwise comparisons
    print("\nPairwise Bootstrap CIs (95%):")
    primary_pairs = [("S1-C", "S1-A"), ("S1-C", "S1-B"), ("S1-B", "S1-A")]
    primary_metrics = ["source_recall", "fact_coverage", "input_tokens", "latency_ms"]

    for config_a, config_b in primary_pairs:
        for metric in primary_metrics:
            result = pairwise_analysis(records, config_a, config_b, metric)
            if "error" in result:
                continue
            print(
                f"  {config_a} - {config_b} | {metric}: "
                f"Δ={result['mean_diff']:.4f} "
                f"[{result['ci_lower']:.4f}, {result['ci_upper']:.4f}] "
                f"n={result['n']}"
            )


def print_scenario2_table(records: list[dict]):
    """Print Scenario 2 ablation delta table."""
    print("\n" + "=" * 80)
    print("SCENARIO 2: Architectural Ablation (Δ from Full CTU-Chat)")
    print("=" * 80)

    ref_config = "S1-C"  # or S2-A0 if present
    by_config = group_by(records, "configuration")

    # Find reference
    ref_recs = by_config.get(ref_config, by_config.get("S2-A0", []))
    if not ref_recs:
        print("No reference config found (S1-C or S2-A0)")
        return

    ref_summary = config_summary(ref_recs)

    ablations = ["S2-A1", "S2-A2", "S2-A3", "S2-A4", "S2-A5"]
    print(f"{'Ablation':<25} {'ΔSrc.R':>8} {'ΔFactCov':>9} {'ΔInTok':>8} {'ΔLat':>8}")
    print("-" * 60)

    for abl in ablations:
        recs = by_config.get(abl, [])
        if not recs:
            print(f"{abl:<25} {'---':>8}")
            continue
        s = config_summary(recs)
        d_src = s["source_recall_mean"] - ref_summary["source_recall_mean"]
        d_fact = s["fact_coverage_mean"] - ref_summary["fact_coverage_mean"]
        d_tok = s["input_tokens_mean"] - ref_summary["input_tokens_mean"]
        d_lat = s["latency_ms_mean"] - ref_summary["latency_ms_mean"]
        print(
            f"{abl:<25} "
            f"{d_src:>+8.3f} "
            f"{d_fact:>+9.3f} "
            f"{d_tok:>+8.0f} "
            f"{d_lat:>+8.0f}"
        )


def print_domain_breakdown(records: list[dict]):
    """Print domain-level breakdown."""
    print("\n" + "=" * 80)
    print("DOMAIN BREAKDOWN")
    print("=" * 80)

    by_config = group_by(records, "configuration")
    configs = sorted(by_config.keys())

    for config in configs:
        recs = by_config[config]
        by_domain = group_by(recs, "domain")
        print(f"\n  {config}:")
        for domain in sorted(by_domain.keys()):
            domain_recs = by_domain[domain]
            n = len(set(r["query_id"] for r in domain_recs))
            sr = np.mean([r["source_recall"] for r in domain_recs])
            fc = np.mean([r["fact_coverage"] for r in domain_recs])
            print(f"    {domain:<20} n={n:>3}  Src.R={sr:.3f}  FactCov={fc:.3f}")


def generate_latex(records: list[dict]) -> str:
    """Generate LaTeX table fragments for the paper."""
    lines = []
    by_config = group_by(records, "configuration")

    # Scenario 1 table
    lines.append("% Scenario 1 LaTeX table data")
    for config in ["S1-A", "S1-B", "S1-C"]:
        recs = by_config.get(config, [])
        if recs:
            s = config_summary(recs)
            name = {
                "S1-A": "Unified Single Agent",
                "S1-B": "Routed Generic",
                "S1-C": "\\textbf{Full CTU-Chat}",
            }[config]
            lines.append(
                f"{name} & "
                f"{s['source_recall_mean']:.3f} & "
                f"{s['source_ap_mean']:.3f} & "
                f"{s['fact_coverage_mean']:.3f} & "
                f"{s['input_tokens_mean']:.0f} & "
                f"{s['latency_ms_mean']:.0f} & "
                f"{s['tool_calls_mean']:.1f} \\\\"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="V13 Result Summarizer")
    parser.add_argument("run_dir", type=str, help="Path to experiment run directory")
    parser.add_argument("--latex", action="store_true", help="Generate LaTeX table fragments")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    results_path = run_dir / "results.jsonl"

    if not results_path.exists():
        print(f"ERROR: {results_path} not found")
        sys.exit(1)

    records = load_results(results_path)
    print(f"Loaded {len(records)} records from {results_path}")

    # Load metadata
    meta_path = run_dir / "metadata.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"Model: {meta.get('model')}, Reps: {meta.get('reps')}, Cases: {meta.get('dataset_size')}")

    print_scenario1_table(records)
    print_scenario2_table(records)
    print_domain_breakdown(records)

    if args.latex:
        print("\n" + "=" * 80)
        print("LATEX TABLE FRAGMENTS")
        print("=" * 80)
        print(generate_latex(records))


if __name__ == "__main__":
    main()
