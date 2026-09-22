#!/usr/bin/env python3
"""Summarize the counterbalanced Scenario 3 v4 scalability benchmark."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

ARCHITECTURES = ("single_agent", "oracle_partitioned", "multi_agent")
QUALITY_METRICS = (
    "selection_passed",
    "arguments_passed",
    "result_passed",
    "passed",
    "bounded_pass",
)
OPERATIONAL_METRICS = (
    "visible_tool_count",
    "visible_tool_schema_chars",
    "route_latency_ms",
    "gate_latency_ms",
    "total_decision_latency_ms",
)
CONTRASTS = {
    "live_vs_single": ("multi_agent", "single_agent"),
    "oracle_vs_single": ("oracle_partitioned", "single_agent"),
    "live_vs_oracle": ("multi_agent", "oracle_partitioned"),
}


def bootstrap_ci(values: list[float], *, seed: int, draws: int) -> list[float]:
    if not values:
        return [0.0, 0.0]
    rng = random.Random(seed)
    n = len(values)
    means = sorted(
        statistics.mean(rng.choice(values) for _ in range(n))
        for _ in range(draws)
    )
    return [
        round(means[int(draws * 0.025)], 4),
        round(means[min(draws - 1, int(draws * 0.975))], 4),
    ]


def grouped_case_means(records: list[dict[str, Any]]) -> dict[tuple[str, int, str, str], dict[str, float]]:
    grouped: dict[tuple[str, int, str, str], dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for record in records:
        key = (
            record["suite"],
            int(record["distractors_per_domain"]),
            record["architecture"],
            record["case_id"],
        )
        for metric in QUALITY_METRICS + OPERATIONAL_METRICS:
            grouped[key][metric].append(float(record.get(metric, 0.0)))
    return {
        key: {metric: statistics.mean(values) for metric, values in metrics.items()}
        for key, metrics in grouped.items()
    }


def summarize_level(
    case_means: dict[tuple[str, int, str, str], dict[str, float]],
    *,
    suite: str,
    level: int,
    case_ids: list[str],
    seed: int,
    draws: int,
) -> dict[str, Any]:
    output: dict[str, Any] = {
        "registry_size": 11 + 4 * level,
        "distractors_per_domain": level,
        "unique_cases": len(case_ids),
        "architectures": {},
        "paired_contrasts": {},
    }
    for architecture in ARCHITECTURES:
        values = [case_means[(suite, level, architecture, case_id)] for case_id in case_ids]
        output["architectures"][architecture] = {
            metric: round(statistics.mean(row[metric] for row in values), 4)
            for metric in QUALITY_METRICS + OPERATIONAL_METRICS
        }

    for contrast_name, (left, right) in CONTRASTS.items():
        output["paired_contrasts"][contrast_name] = {}
        for metric in QUALITY_METRICS:
            differences = [
                case_means[(suite, level, left, case_id)][metric]
                - case_means[(suite, level, right, case_id)][metric]
                for case_id in case_ids
            ]
            output["paired_contrasts"][contrast_name][metric] = {
                "mean": round(statistics.mean(differences), 4),
                "ci95": bootstrap_ci(differences, seed=seed, draws=draws),
            }
    return output


def compute_interactions(
    case_means: dict[tuple[str, int, str, str], dict[str, float]],
    case_ids: list[str],
    *,
    seed: int,
    draws: int,
) -> dict[str, Any]:
    interactions: dict[str, Any] = {}
    for contrast_name, (left, right) in CONTRASTS.items():
        if contrast_name == "live_vs_oracle":
            continue
        interactions[contrast_name] = {}
        for metric in ("selection_passed", "passed"):
            case_interactions = []
            for case_id in case_ids:
                delta_27 = (
                    case_means[("production_tools", 4, left, case_id)][metric]
                    - case_means[("production_tools", 4, right, case_id)][metric]
                )
                delta_11 = (
                    case_means[("production_tools", 0, left, case_id)][metric]
                    - case_means[("production_tools", 0, right, case_id)][metric]
                )
                case_interactions.append(delta_27 - delta_11)
            interactions[contrast_name][metric] = {
                "mean": round(statistics.mean(case_interactions), 4),
                "ci95": bootstrap_ci(case_interactions, seed=seed, draws=draws),
            }
    return interactions


def order_block_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for block in ("gold_first", "gold_middle", "gold_last"):
        output[block] = {}
        for architecture in ARCHITECTURES:
            rows = [
                record
                for record in records
                if record["suite"] == "production_tools"
                and record["order_block"] == block
                and record["architecture"] == architecture
            ]
            output[block][architecture] = {
                "n": len(rows),
                "selection_passed": round(
                    statistics.mean(float(row["selection_passed"]) for row in rows), 4
                ) if rows else 0.0,
                "passed": round(
                    statistics.mean(float(row["passed"]) for row in rows), 4
                ) if rows else 0.0,
            }
    return output


def percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def interval(result: dict[str, Any]) -> str:
    return (
        f"{result['mean'] * 100:+.1f} pp "
        f"[{result['ci95'][0] * 100:+.1f}, {result['ci95'][1] * 100:+.1f}]"
    )


def comparison_markdown(summary: dict[str, Any]) -> str:
    labels = {
        "single_agent": "Monolithic single-agent",
        "oracle_partitioned": "Oracle-partitioned control",
        "multi_agent": "Live supervisor multi-agent",
    }
    lines = [
        "# Scenario 3 v4: Counterbalanced Three-Arm Tool-Space Scalability",
        "",
        f"Total records: **{summary['total_records']}**; execution errors: **{summary['error_records']}**.",
        "",
        "## Production-tool suite",
        "",
        "| Registry | Architecture | Visible tools | Schema chars | Selection | Argument EM | Result Acc. | E2E Pass | Decision latency |",
        "|---:|:---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for level in sorted(summary["production_tools"], key=int):
        data = summary["production_tools"][level]
        for architecture in ARCHITECTURES:
            values = data["architectures"][architecture]
            lines.append(
                f"| {data['registry_size']} | {labels[architecture]} | "
                f"{values['visible_tool_count']:.1f} | {values['visible_tool_schema_chars']:.0f} | "
                f"{percentage(values['selection_passed'])} | {percentage(values['arguments_passed'])} | "
                f"{percentage(values['result_passed'])} | {percentage(values['passed'])} | "
                f"{values['total_decision_latency_ms']:.0f} ms |"
            )
        contrasts = data["paired_contrasts"]
        lines.extend([
            "",
            f"- Live multi vs. monolithic at {data['registry_size']} tools: selection "
            f"{interval(contrasts['live_vs_single']['selection_passed'])}; E2E "
            f"{interval(contrasts['live_vs_single']['passed'])}.",
            f"- Oracle partition vs. monolithic at {data['registry_size']} tools: selection "
            f"{interval(contrasts['oracle_vs_single']['selection_passed'])}; E2E "
            f"{interval(contrasts['oracle_vs_single']['passed'])}.",
            f"- Live multi vs. oracle partition at {data['registry_size']} tools: selection "
            f"{interval(contrasts['live_vs_oracle']['selection_passed'])}; E2E "
            f"{interval(contrasts['live_vs_oracle']['passed'])}.",
            "",
        ])

    lines.extend(["## Primary interaction", ""])
    for contrast, metrics in summary.get("interactions", {}).items():
        lines.append(
            f"- {contrast}, selection Δ(27)−Δ(11): {interval(metrics['selection_passed'])}; "
            f"E2E: {interval(metrics['passed'])}."
        )

    lines.extend([
        "",
        "## Robustness suite",
        "",
        "| Registry | Architecture | Tool suppression/selection | E2E Pass | Bounded |",
        "|---:|:---|---:|---:|---:|",
    ])
    for level in sorted(summary["robustness"], key=int):
        data = summary["robustness"][level]
        for architecture in ARCHITECTURES:
            values = data["architectures"][architecture]
            lines.append(
                f"| {data['registry_size']} | {labels[architecture]} | "
                f"{percentage(values['selection_passed'])} | {percentage(values['passed'])} | "
                f"{percentage(values['bounded_pass'])} |"
            )

    lines.extend([
        "",
        "## Order-block sensitivity",
        "",
        "| Gold position block | Architecture | N | Selection | E2E Pass |",
        "|:---|:---|---:|---:|---:|",
    ])
    for block, block_data in summary["order_blocks"].items():
        for architecture in ARCHITECTURES:
            values = block_data[architecture]
            lines.append(
                f"| {block} | {labels[architecture]} | {values['n']} | "
                f"{percentage(values['selection_passed'])} | {percentage(values['passed'])} |"
            )
    return "\n".join(lines) + "\n"


def panel_latex(summary: dict[str, Any]) -> str:
    labels = {
        "single_agent": "Monolithic",
        "oracle_partitioned": "Oracle partition",
        "multi_agent": "Live multi-agent",
    }
    lines = [
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"Registry & Architecture & Visible & Schema chars & Selection & E2E & Latency (ms) \\",
        r"\midrule",
    ]
    levels = sorted(summary["production_tools"], key=int)
    for level_index, level in enumerate(levels):
        data = summary["production_tools"][level]
        architectures = data["architectures"]
        best_selection = max(values["selection_passed"] for values in architectures.values())
        best_e2e = max(values["passed"] for values in architectures.values())
        for architecture in ARCHITECTURES:
            values = architectures[architecture]
            selection = f"{values['selection_passed'] * 100:.1f}\\%"
            e2e = f"{values['passed'] * 100:.1f}\\%"
            if values["selection_passed"] == best_selection:
                selection = f"\\textbf{{{selection}}}"
            if values["passed"] == best_e2e:
                e2e = f"\\textbf{{{e2e}}}"
            lines.append(
                f"{data['registry_size']} & {labels[architecture]} & "
                f"{values['visible_tool_count']:.1f} & {values['visible_tool_schema_chars']:.0f} & "
                f"{selection} & {e2e} & {values['total_decision_latency_ms']:.0f} \\\\"
            )
        if level_index != len(levels) - 1:
            lines.append(r"\midrule")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-draws", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260921)
    args = parser.parse_args()

    records_file = args.run_dir / "records.jsonl"
    if not records_file.exists():
        parser.error(f"records.jsonl not found in {args.run_dir}")
    records = [
        json.loads(line)
        for line in records_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not records:
        parser.error("No records found")

    case_means = grouped_case_means(records)
    levels = sorted({int(record["distractors_per_domain"]) for record in records})
    prod_cases = sorted({record["case_id"] for record in records if record["suite"] == "production_tools"})
    robust_cases = sorted({record["case_id"] for record in records if record["suite"] == "robustness"})
    summary: dict[str, Any] = {
        "protocol": records[0].get("protocol"),
        "total_records": len(records),
        "error_records": sum(bool(record.get("error")) for record in records),
        "production_cases_count": len(prod_cases),
        "robustness_cases_count": len(robust_cases),
        "levels": levels,
        "production_tools": {},
        "robustness": {},
    }

    for level in levels:
        if prod_cases:
            summary["production_tools"][str(level)] = summarize_level(
                case_means,
                suite="production_tools",
                level=level,
                case_ids=prod_cases,
                seed=args.seed,
                draws=args.bootstrap_draws,
            )
        if robust_cases:
            summary["robustness"][str(level)] = summarize_level(
                case_means,
                suite="robustness",
                level=level,
                case_ids=robust_cases,
                seed=args.seed,
                draws=args.bootstrap_draws,
            )

    if prod_cases and 0 in levels and 4 in levels:
        summary["interactions"] = compute_interactions(
            case_means, prod_cases, seed=args.seed, draws=args.bootstrap_draws
        )
    summary["order_blocks"] = order_block_summary(records)

    (args.run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (args.run_dir / "comparison.md").write_text(
        comparison_markdown(summary), encoding="utf-8"
    )
    (args.run_dir / "panel_scalability.tex").write_text(
        panel_latex(summary), encoding="utf-8"
    )
    failures = [record for record in records if not record.get("passed")]
    failure_lines = [f"# Failures ({len(failures)})", ""]
    failure_lines.extend(
        f"- [{row['suite']}:L{row['distractors_per_domain']}:{row['architecture']}:{row['order_block']}] "
        f"{row['case_id']}: selected={row.get('selected_tool')}, expected={row.get('expected_tool')}, "
        f"error={row.get('error') or '-'}"
        for row in failures
    )
    (args.run_dir / "failures.md").write_text("\n".join(failure_lines) + "\n", encoding="utf-8")
    print(f"Summarized {len(records)} records in {args.run_dir}")


if __name__ == "__main__":
    main()
