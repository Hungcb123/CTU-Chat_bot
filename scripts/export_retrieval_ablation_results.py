#!/usr/bin/env python3
"""
Export Table 4 Ablation Results & Chart (5 Configurations)
==========================================================
Xuất số liệu cho 5 cấu hình theo chuẩn Table 4:
  1. BM25
  2. Dense
  3. BM25 + Dense + RRF
  4. BM25 + Dense + RRF + Graph
  5. BM25 + Dense + RRF + Graph + Agent

Dữ liệu nguồn:
  - tests/outputpaper/table4_results.json (Tập tổng quát N=100)
  - tests/outputpaper/table4_academic_results.json (Tập học vụ / CTĐT N=9)
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TABLE4_JSON = ROOT / "tests" / "outputpaper" / "table4_results.json"
TABLE4_ACAD_JSON = ROOT / "tests" / "outputpaper" / "table4_academic_results.json"
OUTPUT_DIR = ROOT / "tests" / "outputpaper"

CONFIGS_ORDER = [
    ("E1", "BM25"),
    ("E2", "Dense"),
    ("E3", "BM25 + Dense + RRF"),
    ("E4", "BM25 + Dense + RRF + Graph"),
    ("E5", "BM25 + Dense + RRF + Graph + Agent"),
]


def compute_metrics(json_path: Path):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    results = {}
    for code, display_name in CONFIGS_ORDER:
        var_data = data["variants"][code]
        details = var_data["details"]
        h1 = [
            1.0
            if (
                item.get("first_relevant_rank") is not None
                and item["first_relevant_rank"] <= 1
            )
            else 0.0
            for item in details
        ]
        h3 = [
            1.0
            if (
                item.get("first_relevant_rank") is not None
                and item["first_relevant_rank"] <= 3
            )
            else 0.0
            for item in details
        ]
        p5 = var_data["precision_at_5"]
        r5 = var_data["recall_at_5"]
        mrr = var_data["mrr"]
        results[display_name] = {
            "H@1": float(np.mean(h1)),
            "H@3": float(np.mean(h3)),
            "P@5": float(p5),
            "Recall@5": float(r5),
            "MRR": float(mrr),
        }
    return results


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results_100 = compute_metrics(TABLE4_JSON)

    print("=" * 75)
    print(f"{'Configuration':<38} | {'P@5':<8} | {'Recall@5':<10} | {'MRR':<8}")
    print("-" * 75)
    for cfg, m in results_100.items():
        print(f"{cfg:<38} | {m['P@5']:<8.4f} | {m['Recall@5']:<10.4f} | {m['MRR']:<8.4f}")
    print("=" * 75)

    # Export LaTeX (3-column version)
    latex_code_3col = (
        "\\begin{tabular}{lccc}\n"
        "\\hline\n"
        "Configuration & P@5 & Recall@5 & MRR \\\\\n"
        "\\hline\n"
    )
    for cfg, m in results_100.items():
        latex_code_3col += f"{cfg} & {m['P@5']:.4f} & {m['Recall@5']:.4f} & {m['MRR']:.4f} \\\\\n"
    latex_code_3col += "\\hline\n\\end{tabular}\n"

    # Export LaTeX (5-column version)
    latex_code_5col = (
        "\\begin{tabular}{lccccc}\n"
        "\\hline\n"
        "Configuration & H@1 & H@3 & P@5 & Recall@5 & MRR \\\\\n"
        "\\hline\n"
    )
    for cfg, m in results_100.items():
        latex_code_5col += f"{cfg} & {m['H@1']:.4f} & {m['H@3']:.4f} & {m['P@5']:.4f} & {m['Recall@5']:.4f} & {m['MRR']:.4f} \\\\\n"
    latex_code_5col += "\\hline\n\\end{tabular}\n"

    table_file = OUTPUT_DIR / "table4_5configs_table.tex"
    table_file.write_text(latex_code_3col + "\n\n% Phiên bản đầy đủ 5 chỉ số:\n" + latex_code_5col, encoding="utf-8")
    print(f"LaTeX tables saved to: {table_file}")


if __name__ == "__main__":
    main()
