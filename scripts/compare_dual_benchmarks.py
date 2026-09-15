#!/usr/bin/env python3
"""Compare Retrieval Scenario 1 (Table 2) across Formal Heldout vs Semantic Heldout.

Computes Hit@1, Hit@3, P@5, Recall@5, MRR@10 for E1 to E5 on both sets
and prints/saves side-by-side Markdown comparison.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any

CONFIGS = [
    ("E1", "BM25 (Pure Lexical)"),
    ("E2", "Dense (BGE-M3 Pure Vector)"),
    ("E3", "Vanilla Hybrid RRF (k=60, α=1.0)"),
    ("E4", "Hybrid RRF + Local Reranker"),
    ("E5", "CTU-Chat (Full Proposed Stack)"),
]

METRICS = [
    ("hit_at_1", "Hit@1"),
    ("hit_at_3", "Hit@3"),
    ("precision_at_5", "P@5"),
    ("recall_at_5", "Recall@5"),
    ("mrr_at_10", "MRR@10"),
]


def load_checkpoint(run_path: Path) -> dict[str, Any]:
    ckpt_file = run_path if run_path.is_file() else run_path / "checkpoint.json"
    if not ckpt_file.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_file}")
    with open(ckpt_file, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_metrics(checkpoint: dict[str, Any]) -> dict[str, dict[str, float]]:
    retrieval_cases = checkpoint.get("retrieval", {})
    results: dict[str, dict[str, float]] = {}

    for cfg_code, _ in CONFIGS:
        cfg_metrics: dict[str, list[float]] = {m_key: [] for m_key, _ in METRICS}
        latencies: list[float] = []

        for case_id, case_data in retrieval_cases.items():
            cfg_data = case_data.get("configs", {}).get(cfg_code, {})
            metrics = cfg_data.get("metrics", {})
            for m_key, _ in METRICS:
                if m_key in metrics and metrics[m_key] is not None:
                    cfg_metrics[m_key].append(float(metrics[m_key]))
            if "latency_ms" in cfg_data:
                latencies.append(float(cfg_data["latency_ms"]))

        results[cfg_code] = {
            m_key: mean(cfg_metrics[m_key]) if cfg_metrics[m_key] else 0.0
            for m_key, _ in METRICS
        }
        results[cfg_code]["latency_ms"] = mean(latencies) if latencies else 0.0

    return results


def format_table(
    formal_res: dict[str, dict[str, float]],
    semantic_res: dict[str, dict[str, float]] | None = None,
) -> str:
    lines = []
    lines.append("# BẢNG SO SÁNH HIỆU NĂNG TRUY XUẤT (SCENARIO 1: PROGRESSIVE RETRIEVAL STACKING)")
    lines.append("")

    if semantic_res is None:
        lines.append("| Config | Phương pháp | Hit@1 | Hit@3 | P@5 | Recall@5 | MRR@10 | Latency (ms) |")
        lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
        for cfg_code, cfg_name in CONFIGS:
            f = formal_res[cfg_code]
            lines.append(
                f"| **{cfg_code}** | {cfg_name} | {f['hit_at_1']:.4f} | {f['hit_at_3']:.4f} | "
                f"{f['precision_at_5']:.4f} | {f['recall_at_5']:.4f} | {f['mrr_at_10']:.4f} | {f['latency_ms']:.1f} |"
            )
    else:
        lines.append("### Đối chiếu giữa Tập A (Formal Administrative) và Tập B (Student Natural Paraphrase)")
        lines.append("")
        lines.append("| Config | Phương pháp | Hit@1 (Set A) | Hit@1 (Set B) | MRR@10 (Set A) | MRR@10 (Set B) | Recall@5 (Set A) | Recall@5 (Set B) |")
        lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
        for cfg_code, cfg_name in CONFIGS:
            f = formal_res[cfg_code]
            s = semantic_res[cfg_code]
            h1_diff = s["hit_at_1"] - f["hit_at_1"]
            mrr_diff = s["mrr_at_10"] - f["mrr_at_10"]
            diff_sign = "+" if h1_diff >= 0 else ""
            lines.append(
                f"| **{cfg_code}** | {cfg_name} | "
                f"{f['hit_at_1']:.4f} | **{s['hit_at_1']:.4f}** ({diff_sign}{h1_diff:.4f}) | "
                f"{f['mrr_at_10']:.4f} | **{s['mrr_at_10']:.4f}** | "
                f"{f['recall_at_5']:.4f} | **{s['recall_at_5']:.4f}** |"
            )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formal", type=Path, required=True, help="Path to formal heldout run directory")
    parser.add_argument("--semantic", type=Path, help="Optional path to semantic heldout run directory")
    parser.add_argument("--output", type=Path, help="Optional output markdown file path")
    args = parser.parse_args()

    formal_ckpt = load_checkpoint(args.formal)
    formal_res = calculate_metrics(formal_ckpt)

    semantic_res = None
    if args.semantic:
        semantic_ckpt = load_checkpoint(args.semantic)
        semantic_res = calculate_metrics(semantic_ckpt)

    report_md = format_table(formal_res, semantic_res)
    print(report_md)

    if args.output:
        args.output.write_text(report_md, encoding="utf-8")
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
