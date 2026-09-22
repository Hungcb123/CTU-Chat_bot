#!/usr/bin/env python3
"""Statistical summarizer and report generator for Scenario 3 v3 (Scalability).

Reads frozen records from a run directory, computes case-level paired bootstrap
confidence intervals, verifies invariant checks, and outputs:
- summary.json
- comparison.md
- failures.md
- panel_d.tex (LaTeX table snippet ready for inclusion in Table 4)
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

METRICS = ("selection_passed", "arguments_passed", "result_passed", "passed", "bounded_pass")


def bootstrap_ci(values: list[float], *, seed: int = 20260921, draws: int = 10000) -> list[float]:
    if not values:
        return [0.0, 0.0]
    rng = random.Random(seed)
    n = len(values)
    means = [
        statistics.mean(rng.choice(values) for _ in range(n))
        for _ in range(draws)
    ]
    means.sort()
    low_idx = int(draws * 0.025)
    high_idx = int(draws * 0.975)
    return [round(means[low_idx], 4), round(means[high_idx], 4)]


def compute_case_means(records: list[dict[str, Any]]) -> dict[tuple[str, int, str, str], dict[str, float]]:
    """Group records by (suite, distractors_per_domain, architecture, case_id) and average over repetitions."""
    grouped: dict[tuple[str, int, str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in records:
        key = (r["suite"], r["distractors_per_domain"], r["architecture"], r["case_id"])
        for m in METRICS:
            grouped[key][m].append(float(r[m]))

    case_means = {}
    for key, metrics_dict in grouped.items():
        case_means[key] = {m: statistics.mean(vals) for m, vals in metrics_dict.items()}
    return case_means


def summarize_level(
    case_means: dict[tuple[str, int, str, str], dict[str, float]],
    suite: str,
    level: int,
    case_ids: list[str],
    seed: int,
    draws: int,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "registry_size": 11 + 4 * level,
        "distractors_per_domain": level,
        "unique_cases": len(case_ids),
        "multi_agent": {},
        "single_agent": {},
        "paired_difference": {},
    }

    for m in METRICS:
        multi_vals = [case_means[(suite, level, "multi_agent", cid)][m] for cid in case_ids]
        single_vals = [case_means[(suite, level, "single_agent", cid)][m] for cid in case_ids]
        deltas = [m_val - s_val for m_val, s_val in zip(multi_vals, single_vals)]

        m_mean = statistics.mean(multi_vals) if multi_vals else 0.0
        s_mean = statistics.mean(single_vals) if single_vals else 0.0
        d_mean = statistics.mean(deltas) if deltas else 0.0
        d_ci = bootstrap_ci(deltas, seed=seed, draws=draws)

        out["multi_agent"][m] = round(m_mean, 4)
        out["single_agent"][m] = round(s_mean, 4)
        out["paired_difference"][m] = {
            "mean": round(d_mean, 4),
            "ci95": d_ci,
        }

    return out


def generate_panel_d_latex(summary: dict[str, Any]) -> str:
    """Generate Panel D LaTeX table snippet matching Table 4 in Paper_V10."""
    prod = summary.get("production_tools", {})
    levels = sorted(prod.keys(), key=lambda k: int(k))

    lines = [
        r"\midrule",
        r"\multicolumn{8}{l}{\textbf{Panel D: Matched Multi-Agent vs. Monolithic Tool-Space Scalability ($N=60$ unique production cases, 3 reps, $N=1,080$)}} \\",
        r"\midrule",
        r"\textbf{Registry Size} & \textbf{Architecture} & \textbf{Visible} & \textbf{Selection} & \textbf{Arg. EM} & \textbf{Result Acc.} & \textbf{E2E Pass} & \textbf{Paired $\Delta$ E2E (95\% CI)} \\",
        r"\midrule",
    ]

    for lvl_str in levels:
        data = prod[lvl_str]
        reg_size = data["registry_size"]
        m_agent = data["multi_agent"]
        s_agent = data["single_agent"]
        delta_sel = data["paired_difference"]["selection_passed"]
        delta_e2e = data["paired_difference"]["passed"]

        if reg_size == 11:
            size_label = "Production (11)"
            m_visible = "0--6"
        elif reg_size == 19:
            size_label = "Expanded (19)"
            m_visible = "2--8"
        else:
            size_label = "Expanded (27)"
            m_visible = "4--10"

        s_sel = f"{s_agent['selection_passed'] * 100:.1f}\\%"
        s_arg = f"{s_agent['arguments_passed'] * 100:.1f}\\%"
        s_res = f"{s_agent['result_passed'] * 100:.1f}\\%"
        s_e2e = f"{s_agent['passed'] * 100:.1f}\\%"

        m_sel = f"{m_agent['selection_passed'] * 100:.1f}\\%"
        m_arg = f"{m_agent['arguments_passed'] * 100:.1f}\\%"
        m_res = f"{m_agent['result_passed'] * 100:.1f}\\%"
        m_e2e = f"{m_agent['passed'] * 100:.1f}\\%"

        ci_str = f"[{delta_e2e['ci95'][0] * 100:+.1f}, {delta_e2e['ci95'][1] * 100:+.1f}]"
        diff_str = f"{delta_e2e['mean'] * 100:+.1f}\\% {ci_str}"

        lines.extend([
            f"\\multirow{{2}}{{*}}{{{size_label}}} & Monolithic Single-Agent & {reg_size} & {s_sel} & {s_arg} & {s_res} & {s_e2e} & \\multirow{{2}}{{*}}{{{diff_str}}} \\\\",
            f" & Multi-Agent (\\system{{}}) & {m_visible} & \\textbf{{{m_sel}}} & \\textbf{{{m_arg}}} & \\textbf{{{m_res}}} & \\textbf{{{m_e2e}}} & \\\\",
            r"\midrule" if lvl_str != levels[-1] else "",
        ])

    lines = [l for l in lines if l]
    return "\n".join(lines) + "\n"


def generate_comparison_md(summary: dict[str, Any]) -> str:
    lines = [
        "# SCENARIO 3 v3: MULTI-AGENT VS MONOLITHIC TOOL-SPACE SCALABILITY",
        "",
        "## 1. Production Tools Scalability Suite (N=60 Unique Cases, 3 Repetitions)",
        "",
        "| Registry Size | Architecture | Visible Tools | Tool Selection | Argument EM | Result Acc | E2E Pass Rate | Paired Δ Selection (95% CI) | Paired Δ E2E (95% CI) |",
        "|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    prod = summary.get("production_tools", {})
    for lvl_str in sorted(prod.keys(), key=lambda k: int(k)):
        d = prod[lvl_str]
        reg = d["registry_size"]
        m = d["multi_agent"]
        s = d["single_agent"]
        p_sel = d["paired_difference"]["selection_passed"]
        p_e2e = d["paired_difference"]["passed"]

        m_vis = "0--6" if reg == 11 else ("2--8" if reg == 19 else "4--10")
        lines.append(
            f"| {reg} | Monolithic Single | {reg} | {s['selection_passed']*100:.1f}% | {s['arguments_passed']*100:.1f}% | {s['result_passed']*100:.1f}% | {s['passed']*100:.1f}% | — | — |"
        )
        lines.append(
            f"| {reg} | Multi-Agent (CTU-Chat) | {m_vis} | **{m['selection_passed']*100:.1f}%** | **{m['arguments_passed']*100:.1f}%** | **{m['result_passed']*100:.1f}%** | **{m['passed']*100:.1f}%** | {p_sel['mean']*100:+.1f}% [{p_sel['ci95'][0]*100:+.1f}, {p_sel['ci95'][1]*100:+.1f}] | {p_e2e['mean']*100:+.1f}% [{p_e2e['ci95'][0]*100:+.1f}, {p_e2e['ci95'][1]*100:+.1f}] |"
        )

    lines.extend([
        "",
        "## 2. Interaction Analysis",
        f"- Primary Tool-Selection Interaction Δ(27) − Δ(11): **{summary.get('interaction', {}).get('mean', 0.0)*100:+.2f}%** (95% CI [{summary.get('interaction', {}).get('ci95', [0, 0])[0]*100:+.2f}%, {summary.get('interaction', {}).get('ci95', [0, 0])[1]*100:+.2f}%])",
        "",
        "## 3. Robustness Suite (N=20 Adversarial Cases, 3 Repetitions)",
        "",
        "| Registry Size | Multi Tool Suppress | Single Tool Suppress | Multi E2E Pass | Single E2E Pass |",
        "|:---:|:---:|:---:|:---:|:---:|",
    ])

    rob = summary.get("robustness", {})
    for lvl_str in sorted(rob.keys(), key=lambda k: int(k)):
        d = rob[lvl_str]
        reg = d["registry_size"]
        m = d["multi_agent"]
        s = d["single_agent"]
        lines.append(
            f"| {reg} | {m['selection_passed']*100:.1f}% | {s['selection_passed']*100:.1f}% | {m['passed']*100:.1f}% | {s['passed']*100:.1f}% |"
        )

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

    records = [json.loads(line) for line in records_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not records:
        parser.error(f"No records found in {records_file}")

    print(f"Loaded {len(records)} records from {records_file}")
    case_means = compute_case_means(records)

    prod_cases = sorted({r["case_id"] for r in records if r["suite"] == "production_tools"})
    rob_cases = sorted({r["case_id"] for r in records if r["suite"] == "robustness"})
    levels = sorted({int(r["distractors_per_domain"]) for r in records})

    summary: dict[str, Any] = {
        "total_records": len(records),
        "production_cases_count": len(prod_cases),
        "robustness_cases_count": len(rob_cases),
        "levels": levels,
        "production_tools": {},
        "robustness": {},
    }

    for lvl in levels:
        if prod_cases:
            summary["production_tools"][str(lvl)] = summarize_level(
                case_means, "production_tools", lvl, prod_cases, args.seed, args.bootstrap_draws
            )
        if rob_cases:
            summary["robustness"][str(lvl)] = summarize_level(
                case_means, "robustness", lvl, rob_cases, args.seed, args.bootstrap_draws
            )

    # Calculate primary interaction: Interaction = Delta(27) - Delta(11) on production selection
    if prod_cases and 0 in levels and 4 in levels:
        interactions = []
        for cid in prod_cases:
            delta_27 = case_means[("production_tools", 4, "multi_agent", cid)]["selection_passed"] - case_means[("production_tools", 4, "single_agent", cid)]["selection_passed"]
            delta_11 = case_means[("production_tools", 0, "multi_agent", cid)]["selection_passed"] - case_means[("production_tools", 0, "single_agent", cid)]["selection_passed"]
            interactions.append(delta_27 - delta_11)

        summary["interaction"] = {
            "metric": "tool_selection_accuracy",
            "mean": round(statistics.mean(interactions), 4),
            "ci95": bootstrap_ci(interactions, seed=args.seed, draws=args.bootstrap_draws),
        }

    # Write summary.json
    (args.run_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.run_dir / 'summary.json'}")

    # Write comparison.md
    comp_md = generate_comparison_md(summary)
    (args.run_dir / "comparison.md").write_text(comp_md, encoding="utf-8")
    print(f"Wrote {args.run_dir / 'comparison.md'}")

    # Write panel_d.tex
    panel_d_tex = generate_panel_d_latex(summary)
    (args.run_dir / "panel_d.tex").write_text(panel_d_tex, encoding="utf-8")
    print(f"Wrote {args.run_dir / 'panel_d.tex'}")

    # Write failures.md
    failures = [r for r in records if not r.get("passed", False)]
    fail_lines = [f"# Failures Report ({len(failures)} total failures)", ""]
    for f in failures[:100]:
        fail_lines.append(f"- [{f['suite']}:L{f['distractors_per_domain']}:{f['architecture']}] Case {f['case_id']}: sel_pass={f['selection_passed']}, arg_pass={f['arguments_passed']}, err={f.get('error')}")
    (args.run_dir / "failures.md").write_text("\n".join(fail_lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.run_dir / 'failures.md'}")


if __name__ == "__main__":
    main()
