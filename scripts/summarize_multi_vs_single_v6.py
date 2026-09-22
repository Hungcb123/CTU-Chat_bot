#!/usr/bin/env python3
"""Summarize Scenario 3 v6 with case-level paired bootstrap intervals."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ARCHITECTURES = ("single_full", "single_topk", "routed_generic", "routed_specialist")
QUALITY = ("selection_passed", "arguments_passed", "result_passed", "passed", "bounded_pass")
OPERATIONAL = ("visible_tool_count", "visible_tool_schema_chars", "total_decision_latency_ms", "total_input_tokens", "total_tokens")
CONTRASTS = {
    "specialist_vs_single_topk": ("routed_specialist", "single_topk"),
    "specialist_vs_routed_generic": ("routed_specialist", "routed_generic"),
    "specialist_vs_single_full": ("routed_specialist", "single_full"),
    "single_topk_vs_full": ("single_topk", "single_full"),
}


def bootstrap_ci(values: list[float], *, seed: int, draws: int) -> list[float]:
    array = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(array), size=(draws, len(array)))
    low, high = np.quantile(array[indices].mean(axis=1), [0.025, 0.975])
    return [round(float(low), 4), round(float(high), 4)]


def case_means(records: list[dict[str, Any]]) -> dict[tuple[int, str, str], dict[str, float]]:
    grouped: dict[tuple[int, str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in records:
        if row["partition"] != "primary":
            continue
        key = (int(row["ambiguity_level"]), row["architecture"], row["case_id"])
        for metric in QUALITY + OPERATIONAL:
            grouped[key][metric].append(float(row.get(metric, 0.0)))
    return {key: {metric: statistics.mean(values) for metric, values in metrics.items()} for key, metrics in grouped.items()}


def paired(values: list[float], seed: int, draws: int) -> dict[str, Any]:
    return {"mean": round(statistics.mean(values), 4), "ci95": bootstrap_ci(values, seed=seed, draws=draws)}


def summarize_level(means: dict[tuple[int, str, str], dict[str, float]], level: int, cases: list[str], seed: int, draws: int) -> dict[str, Any]:
    result: dict[str, Any] = {"registry_size": 11 + 10 * level, "unique_cases": len(cases), "architectures": {}, "paired_contrasts": {}}
    for architecture in ARCHITECTURES:
        rows = [means[(level, architecture, case)] for case in cases]
        result["architectures"][architecture] = {metric: round(statistics.mean(row[metric] for row in rows), 4) for metric in QUALITY + OPERATIONAL}
    for name, (left, right) in CONTRASTS.items():
        result["paired_contrasts"][name] = {}
        for metric in QUALITY:
            differences = [means[(level, left, case)][metric] - means[(level, right, case)][metric] for case in cases]
            result["paired_contrasts"][name][metric] = paired(differences, seed, draws)
    return result


def interactions(means: dict[tuple[int, str, str], dict[str, float]], cases: list[str], seed: int, draws: int) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in ("specialist_vs_single_topk", "specialist_vs_routed_generic", "specialist_vs_single_full"):
        left, right = CONTRASTS[name]
        output[name] = {}
        for metric in ("selection_passed", "passed"):
            values = [
                (means[(4, left, case)][metric] - means[(4, right, case)][metric])
                - (means[(0, left, case)][metric] - means[(0, right, case)][metric])
                for case in cases
            ]
            output[name][metric] = paired(values, seed, draws)
    return output


def interval(result: dict[str, Any]) -> str:
    return f"{result['mean'] * 100:+.1f} pp [{result['ci95'][0] * 100:+.1f}, {result['ci95'][1] * 100:+.1f}]"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def markdown(summary: dict[str, Any]) -> str:
    labels = {
        "single_full": "Monolithic full registry",
        "single_topk": "Single-agent global Top-k",
        "routed_generic": "Routed Top-k, generic gate",
        "routed_specialist": "Routed Top-k, specialist gate",
    }
    lines = [
        "# Scenario 3 v6: Intra-Domain Tool Ambiguity",
        "",
        f"Records: **{summary['total_records']}**; runtime errors: **{summary['error_records']}**; schema-guarded failures: **{summary['schema_guard_failures']}**.",
        "",
        "## Primary fixed-case suite",
        "",
        "| Registry | Architecture | Visible | Gold recall | Selection | E2E | Input tokens | Latency |",
        "|---:|:---|---:|---:|---:|---:|---:|---:|",
    ]
    for level in ("0", "2", "4"):
        data = summary["primary"][level]
        for architecture in ARCHITECTURES:
            values = data["architectures"][architecture]
            recall = summary["retrieval_recall"][level].get(architecture)
            recall_text = "--" if recall is None else pct(recall)
            lines.append(
                f"| {data['registry_size']} | {labels[architecture]} | {values['visible_tool_count']:.1f} | {recall_text} | "
                f"{pct(values['selection_passed'])} | {pct(values['passed'])} | {values['total_input_tokens']:.0f} | {values['total_decision_latency_ms']:.0f} ms |"
            )
        for name in ("specialist_vs_single_topk", "specialist_vs_routed_generic", "specialist_vs_single_full"):
            result = data["paired_contrasts"][name]
            lines.append(f"- {name}: selection {interval(result['selection_passed'])}; E2E {interval(result['passed'])}.")
        lines.append("")
    lines.extend(["## Primary high-minus-low interactions", ""])
    for name, result in summary["interactions"].items():
        lines.append(f"- {name}: selection {interval(result['selection_passed'])}; E2E {interval(result['passed'])}.")
    lines.extend([
        "",
        "## Diagnostic conditional on gold being shortlisted",
        "",
        "| Registry | Architecture | Eligible records | Conditional selection |",
        "|---:|:---|---:|---:|",
    ])
    for level in ("0", "2", "4"):
        for architecture in ("single_topk", "routed_generic", "routed_specialist"):
            value = summary["conditional_selection"][level][architecture]
            lines.append(f"| {11 + 10 * int(level)} | {labels[architecture]} | {value['records']} | {pct(value['rate'])} |")
    lines.extend([
        "",
        "## Semantic-neighbor coverage at 51 tools",
        "",
        "| Architecture | Gold recall | Selection | E2E |",
        "|:---|---:|---:|---:|",
    ])
    for architecture in ARCHITECTURES:
        value = summary["coverage"][architecture]
        recall_text = "--" if value["retrieval_recall"] is None else pct(value["retrieval_recall"])
        lines.append(f"| {labels[architecture]} | {recall_text} | {pct(value['selection_passed'])} | {pct(value['passed'])} |")
    return "\n".join(lines) + "\n"


def latex_table(summary: dict[str, Any]) -> str:
    labels = {"single_full": "Full single", "single_topk": "Top-$k$ single", "routed_generic": "Routed generic", "routed_specialist": "Routed specialist"}
    lines = [r"\begin{tabular}{llrrrrr}", r"\toprule", r"Registry & Architecture & Visible & Selection & E2E & Tokens & Latency \\", r"\midrule"]
    for index, level in enumerate(("0", "2", "4")):
        data = summary["primary"][level]
        for architecture in ARCHITECTURES:
            value = data["architectures"][architecture]
            lines.append(f"{data['registry_size']} & {labels[architecture]} & {value['visible_tool_count']:.1f} & {value['selection_passed']*100:.1f}\\% & {value['passed']*100:.1f}\\% & {value['total_input_tokens']:.0f} & {value['total_decision_latency_ms']:.0f} \\\\")
        if index < 2:
            lines.append(r"\midrule")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-draws", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260922)
    args = parser.parse_args()
    records = [json.loads(line) for line in (args.run_dir / "records.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    primary_rows = [row for row in records if row["partition"] == "primary"]
    coverage_rows = [row for row in records if row["partition"] == "coverage"]
    cases = sorted({row["case_id"] for row in primary_rows})
    means = case_means(records)
    summary: dict[str, Any] = {
        "protocol": records[0]["protocol"],
        "total_records": len(records),
        "error_records": sum(bool(row.get("error")) for row in records),
        "schema_guard_failures": sum(not row.get("schema_guard_passed", True) for row in records),
        "primary": {}, "retrieval_recall": {}, "conditional_selection": {},
    }
    for level in (0, 2, 4):
        summary["primary"][str(level)] = summarize_level(means, level, cases, args.seed, args.bootstrap_draws)
        summary["retrieval_recall"][str(level)] = {}
        summary["conditional_selection"][str(level)] = {}
        for architecture in ARCHITECTURES:
            rows = [row for row in primary_rows if int(row["ambiguity_level"]) == level and row["architecture"] == architecture]
            if architecture == "single_full":
                summary["retrieval_recall"][str(level)][architecture] = None
                continue
            eligible = [row for row in rows if row.get("gold_in_candidates")]
            summary["retrieval_recall"][str(level)][architecture] = round(len(eligible) / len(rows), 4)
            summary["conditional_selection"][str(level)][architecture] = {
                "records": len(eligible),
                "rate": round(statistics.mean(float(row["selection_passed"]) for row in eligible), 4) if eligible else 0.0,
            }
    summary["interactions"] = interactions(means, cases, args.seed, args.bootstrap_draws)
    summary["coverage"] = {}
    for architecture in ARCHITECTURES:
        rows = [row for row in coverage_rows if row["architecture"] == architecture]
        summary["coverage"][architecture] = {
            "unique_cases": len(rows),
            "retrieval_recall": None if architecture == "single_full" else round(statistics.mean(float(row.get("gold_in_candidates", False)) for row in rows), 4),
            "selection_passed": round(statistics.mean(float(row["selection_passed"]) for row in rows), 4),
            "passed": round(statistics.mean(float(row["passed"]) for row in rows), 4),
        }
    (args.run_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.run_dir / "comparison.md").write_text(markdown(summary), encoding="utf-8")
    (args.run_dir / "panel_ambiguity.tex").write_text(latex_table(summary), encoding="utf-8")
    print(f"Summarized {len(records)} records with {args.bootstrap_draws} bootstrap draws.")


if __name__ == "__main__":
    main()
