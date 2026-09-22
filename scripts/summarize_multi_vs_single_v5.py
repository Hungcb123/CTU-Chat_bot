#!/usr/bin/env python3
"""Summarize Scenario 3 v5 with case-level paired bootstrap intervals."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ARCHITECTURES = ("single_agent", "static_multi", "topk_multi")
QUALITY = ("selection_passed", "arguments_passed", "result_passed", "passed", "bounded_pass")
OPERATIONAL = (
    "visible_tool_count",
    "visible_tool_schema_chars",
    "total_decision_latency_ms",
    "total_input_tokens",
    "total_tokens",
)
CONTRASTS = {
    "topk_vs_single": ("topk_multi", "single_agent"),
    "static_vs_single": ("static_multi", "single_agent"),
    "topk_vs_static": ("topk_multi", "static_multi"),
}


def bootstrap_ci(values: list[float], *, seed: int, draws: int) -> list[float]:
    if not values:
        return [0.0, 0.0]
    array = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(array), size=(draws, len(array)))
    means = array[indices].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return [round(float(low), 4), round(float(high), 4)]


def case_means(records: list[dict[str, Any]]) -> dict[tuple[str, int, str, str], dict[str, float]]:
    grouped: dict[tuple[str, int, str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in records:
        key = (row["suite"], int(row["distractors_per_domain"]), row["architecture"], row["case_id"])
        for metric in QUALITY + OPERATIONAL:
            grouped[key][metric].append(float(row.get(metric, 0.0)))
    return {
        key: {metric: statistics.mean(values) for metric, values in metrics.items()}
        for key, metrics in grouped.items()
    }


def summarize_level(
    means: dict[tuple[str, int, str, str], dict[str, float]],
    suite: str,
    level: int,
    cases: list[str],
    seed: int,
    draws: int,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "registry_size": 11 + 4 * level,
        "unique_cases": len(cases),
        "architectures": {},
        "paired_contrasts": {},
    }
    for architecture in ARCHITECTURES:
        rows = [means[(suite, level, architecture, case)] for case in cases]
        result["architectures"][architecture] = {
            metric: round(statistics.mean(row[metric] for row in rows), 4)
            for metric in QUALITY + OPERATIONAL
        }
    for name, (left, right) in CONTRASTS.items():
        result["paired_contrasts"][name] = {}
        for metric in QUALITY:
            differences = [
                means[(suite, level, left, case)][metric] - means[(suite, level, right, case)][metric]
                for case in cases
            ]
            result["paired_contrasts"][name][metric] = {
                "mean": round(statistics.mean(differences), 4),
                "ci95": bootstrap_ci(differences, seed=seed, draws=draws),
            }
    return result


def interactions(
    means: dict[tuple[str, int, str, str], dict[str, float]],
    cases: list[str],
    seed: int,
    draws: int,
) -> dict[str, Any]:
    output = {}
    for name in ("topk_vs_single", "static_vs_single"):
        left, right = CONTRASTS[name]
        output[name] = {}
        for metric in ("selection_passed", "passed"):
            values = []
            for case in cases:
                delta_51 = means[("production_tools", 10, left, case)][metric] - means[("production_tools", 10, right, case)][metric]
                delta_11 = means[("production_tools", 0, left, case)][metric] - means[("production_tools", 0, right, case)][metric]
                values.append(delta_51 - delta_11)
            output[name][metric] = {
                "mean": round(statistics.mean(values), 4),
                "ci95": bootstrap_ci(values, seed=seed, draws=draws),
            }
    return output


def interval(result: dict[str, Any]) -> str:
    return f"{result['mean'] * 100:+.1f} pp [{result['ci95'][0] * 100:+.1f}, {result['ci95'][1] * 100:+.1f}]"


def percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def markdown(summary: dict[str, Any]) -> str:
    labels = {
        "single_agent": "Monolithic single-agent",
        "static_multi": "Static-partition multi-agent",
        "topk_multi": "Top-k multi-agent",
    }
    lines = [
        "# Scenario 3 v5: Dynamic Tool Shortlisting Scalability",
        "",
        f"Records: **{summary['total_records']}**; runtime errors: **{summary['error_records']}**; schema-guarded failures: **{summary['schema_guard_failures']}**.",
        "",
        "## Production-tool suite",
        "",
        "| Registry | Architecture | Visible | Schema chars | Gold-in-Top-k | Selection | E2E | Input tokens | Latency |",
        "|---:|:---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for level in sorted(summary["production_tools"], key=int):
        data = summary["production_tools"][level]
        recall = summary["topk_retrieval_recall"][level]
        for architecture in ARCHITECTURES:
            values = data["architectures"][architecture]
            recall_text = percent(recall) if architecture == "topk_multi" else "--"
            lines.append(
                f"| {data['registry_size']} | {labels[architecture]} | {values['visible_tool_count']:.1f} | "
                f"{values['visible_tool_schema_chars']:.0f} | {recall_text} | {percent(values['selection_passed'])} | "
                f"{percent(values['passed'])} | {values['total_input_tokens']:.0f} | {values['total_decision_latency_ms']:.0f} ms |"
            )
        for contrast in ("topk_vs_single", "static_vs_single", "topk_vs_static"):
            values = data["paired_contrasts"][contrast]
            lines.append(
                f"- {contrast} at {data['registry_size']}: selection {interval(values['selection_passed'])}; E2E {interval(values['passed'])}."
            )
        lines.append("")
    lines.extend(["## Primary interactions", ""])
    for name, metrics in summary["interactions"].items():
        lines.append(
            f"- {name}, Δ(51)−Δ(11): selection {interval(metrics['selection_passed'])}; E2E {interval(metrics['passed'])}."
        )
    lines.extend([
        "",
        "## Robustness suite",
        "",
        "| Registry | Architecture | Tool suppression | E2E | Bounded |",
        "|---:|:---|---:|---:|---:|",
    ])
    for level in sorted(summary["robustness"], key=int):
        data = summary["robustness"][level]
        for architecture in ARCHITECTURES:
            values = data["architectures"][architecture]
            lines.append(
                f"| {data['registry_size']} | {labels[architecture]} | {percent(values['selection_passed'])} | "
                f"{percent(values['passed'])} | {percent(values['bounded_pass'])} |"
            )
    return "\n".join(lines) + "\n"


def latex_table(summary: dict[str, Any]) -> str:
    labels = {"single_agent": "Monolithic", "static_multi": "Static multi", "topk_multi": "Top-$k$ multi"}
    lines = [
        r"\begin{tabular}{llrrrrrr}",
        r"\toprule",
        r"Registry & Architecture & Visible & Schema chars & Selection & E2E & Tokens & Latency \\",
        r"\midrule",
    ]
    levels = sorted(summary["production_tools"], key=int)
    for level_index, level in enumerate(levels):
        data = summary["production_tools"][level]
        values_by_arch = data["architectures"]
        best_selection = max(values["selection_passed"] for values in values_by_arch.values())
        best_e2e = max(values["passed"] for values in values_by_arch.values())
        for architecture in ARCHITECTURES:
            values = values_by_arch[architecture]
            selection = f"{values['selection_passed'] * 100:.1f}\\%"
            e2e = f"{values['passed'] * 100:.1f}\\%"
            if values["selection_passed"] == best_selection:
                selection = f"\\textbf{{{selection}}}"
            if values["passed"] == best_e2e:
                e2e = f"\\textbf{{{e2e}}}"
            lines.append(
                f"{data['registry_size']} & {labels[architecture]} & {values['visible_tool_count']:.1f} & "
                f"{values['visible_tool_schema_chars']:.0f} & {selection} & {e2e} & "
                f"{values['total_input_tokens']:.0f} & {values['total_decision_latency_ms']:.0f} \\\\"
            )
        if level_index != len(levels) - 1:
            lines.append(r"\midrule")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-draws", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260922)
    args = parser.parse_args()
    records = [
        json.loads(line)
        for line in (args.run_dir / "records.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    means = case_means(records)
    levels = sorted({int(row["distractors_per_domain"]) for row in records})
    production_cases = sorted({row["case_id"] for row in records if row["suite"] == "production_tools"})
    robustness_cases = sorted({row["case_id"] for row in records if row["suite"] == "robustness"})
    summary: dict[str, Any] = {
        "protocol": records[0]["protocol"],
        "total_records": len(records),
        "error_records": sum(bool(row.get("error")) for row in records),
        "schema_guard_failures": sum(not row.get("schema_guard_passed", True) for row in records),
        "levels": levels,
        "production_tools": {},
        "robustness": {},
        "topk_retrieval_recall": {},
    }
    for level in levels:
        if production_cases:
            summary["production_tools"][str(level)] = summarize_level(
                means, "production_tools", level, production_cases, args.seed, args.bootstrap_draws
            )
            topk_rows = [
                row for row in records
                if row["suite"] == "production_tools"
                and int(row["distractors_per_domain"]) == level
                and row["architecture"] == "topk_multi"
                and row.get("expected_tool")
            ]
            summary["topk_retrieval_recall"][str(level)] = round(
                statistics.mean(float(row.get("gold_in_candidates", False)) for row in topk_rows), 4
            )
        if robustness_cases:
            summary["robustness"][str(level)] = summarize_level(
                means, "robustness", level, robustness_cases, args.seed, args.bootstrap_draws
            )
    if production_cases and {0, 10}.issubset(levels):
        summary["interactions"] = interactions(means, production_cases, args.seed, args.bootstrap_draws)
    else:
        summary["interactions"] = {}

    (args.run_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.run_dir / "comparison.md").write_text(markdown(summary), encoding="utf-8")
    (args.run_dir / "panel_scalability.tex").write_text(latex_table(summary), encoding="utf-8")
    print(f"Summarized {len(records)} records with {args.bootstrap_draws} bootstrap draws.")


if __name__ == "__main__":
    main()
