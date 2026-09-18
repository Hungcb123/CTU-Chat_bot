#!/usr/bin/env python3
"""Recompute and synchronize Scenario 1-2 experiment summary artifacts.

Updates summary.json, comparison.md, failures.md, records.jsonl, and manifest.json
from the fully evaluated checkpoint.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import random
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs" / "scenario12" / "20260916T075823Z"
DATASET_PATH = ROOT / "data" / "scenario12_heldout_100.jsonl"

CONFIGS_S1 = ("E1", "E2", "E3", "E4", "E5")
CONFIGS_S2 = ("T1", "T2", "T3", "T4", "T5", "T6", "T7")
METRICS_S2 = ("AR", "CR", "CP", "AC", "Faith")


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def bootstrap_ci(values: list[float], *, samples: int = 10000) -> list[float]:
    if not values:
        return [0.0, 0.0]
    rng = random.Random(42)
    means = sorted(mean([values[rng.randrange(len(values))] for _ in values]) for _ in range(samples))
    return [means[int(0.025 * (samples - 1))], means[int(0.975 * (samples - 1))]]


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def json_dump(path: Path, payload: Any) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    temp_path.replace(path)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("recompute_summary")

    logger.info("Loading cases from %s", DATASET_PATH)
    cases = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            cases.append(json.loads(line))

    logger.info("Loading checkpoint from %s", LOG_DIR / "checkpoint.json")
    checkpoint = json.loads((LOG_DIR / "checkpoint.json").read_text(encoding="utf-8"))
    manifest = json.loads((LOG_DIR / "manifest.json").read_text(encoding="utf-8"))

    summary: dict[str, Any] = {"scenario1": {}, "scenario2": {}, "paired_differences": {}}

    # Scenario 1 (Retrieval)
    for config in CONFIGS_S1:
        rows = [checkpoint["retrieval"][c["id"]]["configs"][config] for c in cases]
        metric_names = ("hit_at_1", "hit_at_3", "precision_at_5", "recall_at_5", "mrr_at_10")
        summary["scenario1"][config] = {
            name: mean([row["metrics"][name] for row in rows]) for name in metric_names
        }
        summary["scenario1"][config]["latency_ms"] = mean([row["latency_ms"] for row in rows])
        per_domain = {}
        for dom in ("academic", "financial", "scholarship", "general"):
            dom_cases = [c for c in cases if c.get("domain") == dom]
            if dom_cases:
                dom_rows = [checkpoint["retrieval"][c["id"]]["configs"][config] for c in dom_cases]
                per_domain[dom] = {
                    "n": len(dom_cases),
                    "hit_at_1": mean([r["metrics"]["hit_at_1"] for r in dom_rows]),
                    "hit_at_3": mean([r["metrics"]["hit_at_3"] for r in dom_rows]),
                    "mrr_at_10": mean([r["metrics"]["mrr_at_10"] for r in dom_rows]),
                }
        summary["scenario1"][config]["per_domain"] = per_domain
        if per_domain:
            summary["scenario1"][config]["macro_hit_at_1"] = mean([d["hit_at_1"] for d in per_domain.values()])

        per_category = {}
        categories = sorted(list({c.get("category") for c in cases if c.get("category")}))
        for cat in categories:
            cat_cases = [c for c in cases if c.get("category") == cat]
            if cat_cases:
                cat_rows = [checkpoint["retrieval"][c["id"]]["configs"][config] for c in cat_cases]
                per_category[cat] = {
                    "n": len(cat_cases),
                    "hit_at_1": mean([r["metrics"]["hit_at_1"] for r in cat_rows]),
                    "hit_at_3": mean([r["metrics"]["hit_at_3"] for r in cat_rows]),
                    "precision_at_5": mean([r["metrics"]["precision_at_5"] for r in cat_rows]),
                    "recall_at_5": mean([r["metrics"]["recall_at_5"] for r in cat_rows]),
                    "mrr_at_10": mean([r["metrics"]["mrr_at_10"] for r in cat_rows]),
                }
        summary["scenario1"][config]["per_category"] = per_category

        per_tier = {}
        tiers = sorted(list({c.get("complexity_tier", "") for c in cases if c.get("complexity_tier")}))
        for tier in tiers:
            tier_cases = [c for c in cases if c.get("complexity_tier") == tier]
            if tier_cases:
                t_rows = [checkpoint["retrieval"][c["id"]]["configs"][config] for c in tier_cases]
                per_tier[tier] = {
                    "n": len(tier_cases),
                    "hit_at_1": mean([r["metrics"]["hit_at_1"] for r in t_rows]),
                    "hit_at_3": mean([r["metrics"]["hit_at_3"] for r in t_rows]),
                    "precision_at_5": mean([r["metrics"]["precision_at_5"] for r in t_rows]),
                    "recall_at_5": mean([r["metrics"]["recall_at_5"] for r in t_rows]),
                    "mrr_at_10": mean([r["metrics"]["mrr_at_10"] for r in t_rows]),
                }
        summary["scenario1"][config]["per_tier"] = per_tier

    # Scenario 2 (Generation)
    repetitions = manifest.get("repetitions", 3)
    for config in CONFIGS_S2:
        config_summary: dict[str, Any] = {}
        keys = [
            f"r{rep}:{c['id']}:{config}"
            for rep in range(1, repetitions + 1) for c in cases
        ]
        for metric in METRICS_S2:
            values = [
                checkpoint["ragas"][key][metric]
                for key in keys
                if checkpoint["ragas"].get(key, {}).get(metric) is not None
                and math.isfinite(checkpoint["ragas"][key][metric])
            ]
            config_summary[metric] = {
                "mean": mean(values),
                "sd": stddev(values),
                "ci95": bootstrap_ci(values),
                "n": len(values),
            }
        diagnostics = [checkpoint["retrieval"][c["id"]]["configs"][config]["diagnostics"] for c in cases]
        config_summary["source_recall"] = mean([row["source_recall"] for row in diagnostics])
        config_summary["source_ap"] = mean([row["source_ap"] for row in diagnostics])
        answer_rows = [checkpoint["answers"][key] for key in keys if key in checkpoint["answers"]]
        config_summary["factual_exact_match"] = mean([row["factual_exact_match"] for row in answer_rows])
        summary["scenario2"][config] = config_summary

    # Paired differences
    for ablation in ("T5", "T6", "T7"):
        summary["paired_differences"][f"T4-{ablation}"] = {}
        for metric in METRICS_S2:
            differences = []
            for rep in range(1, repetitions + 1):
                for c in cases:
                    left = checkpoint["ragas"].get(f"r{rep}:{c['id']}:T4", {}).get(metric)
                    right = checkpoint["ragas"].get(f"r{rep}:{c['id']}:{ablation}", {}).get(metric)
                    if left is not None and right is not None and math.isfinite(left) and math.isfinite(right):
                        differences.append(left - right)
            summary["paired_differences"][f"T4-{ablation}"][metric] = {
                "mean": mean(differences),
                "ci95": bootstrap_ci(differences),
                "n": len(differences),
            }

    # Write records.jsonl
    logger.info("Writing records.jsonl")
    records = []
    for c in cases:
        case_id = c["id"]
        retrieval = checkpoint["retrieval"][case_id]
        for config, data in retrieval["configs"].items():
            base = {
                "case_id": case_id,
                "category": c.get("category"),
                "question": c.get("question"),
                "config": config,
                "reference_answer": c.get("reference_answer"),
                "gold_sources": c.get("gold_sources"),
                "source_relation": c.get("source_relation"),
                "contexts": data["contexts"],
                "retrieval_latency_ms": data["latency_ms"],
                "graph_hit": retrieval.get("graph_hit"),
                "catalog_fallback": retrieval.get("catalog_fallback"),
                "gate_reasons": retrieval.get("gate_reasons"),
            }
            if config in CONFIGS_S1:
                records.append({**base, "scenario": 1, "metrics": data["metrics"]})
            if config in CONFIGS_S2:
                for repetition in range(1, repetitions + 1):
                    key = f"r{repetition}:{case_id}:{config}"
                    records.append({
                        **base,
                        "scenario": 2,
                        "repetition": repetition,
                        **checkpoint["answers"].get(key, {}),
                        "metrics": checkpoint["ragas"].get(key, {}),
                        "diagnostics": data["diagnostics"],
                    })

    temp_records = LOG_DIR / "records.jsonl.tmp"
    with open(temp_records, "w", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    temp_records.replace(LOG_DIR / "records.jsonl")

    # Write summary.json
    logger.info("Writing summary.json")
    json_dump(LOG_DIR / "summary.json", summary)

    # Failures report
    failures = [
        row for row in records
        if row.get("error") or any(
            row.get("metrics", {}).get(m) is None or not math.isfinite(row.get("metrics", {}).get(m, 0.0))
            for m in (("hit_at_1", "hit_at_3", "precision_at_5", "recall_at_5", "mrr_at_10") if row.get("scenario") == 1 else METRICS_S2)
        )
    ]
    failure_lines = ["# Failures", "", f"Total: {len(failures)}", ""]
    failure_lines.extend(f"- `{row['case_id']}` / `{row['config']}`: {row.get('error') or 'missing metric'}" for row in failures)
    (LOG_DIR / "failures.md").write_text("\n".join(failure_lines) + "\n", encoding="utf-8")
    logger.info("Failures count: %d", len(failures))

    # Comparison report
    comparison = ["# Scenario 1–2 comparison", "", f"- Split: `{manifest['split']}`", f"- Cases: {manifest['case_count']}", ""]
    if summary["scenario1"]:
        comparison.extend(["## Scenario 1: Overall Retrieval Metrics", "", "| Config | H@1 | H@3 | P@5 | R@5 | MRR@10 | Latency ms |", "|---|---:|---:|---:|---:|---:|---:|"])
        for config, row in summary["scenario1"].items():
            comparison.append(f"| {config} | {row['hit_at_1']:.4f} | {row['hit_at_3']:.4f} | {row['precision_at_5']:.4f} | {row['recall_at_5']:.4f} | {row['mrr_at_10']:.4f} | {row['latency_ms']:.2f} |")
        comparison.extend(["", "### Per-Domain Hit@1 and Macro-Average", "", "| Config | Academic | Financial | Scholarship | General | Macro-Avg H@1 | Micro-Avg H@1 |", "|---|---:|---:|---:|---:|---:|---:|"])
        for config, row in summary["scenario1"].items():
            pd = row.get("per_domain", {})
            acad = pd.get("academic", {}).get("hit_at_1", 0.0)
            fin = pd.get("financial", {}).get("hit_at_1", 0.0)
            sch = pd.get("scholarship", {}).get("hit_at_1", 0.0)
            gen = pd.get("general", {}).get("hit_at_1", 0.0)
            macro = row.get("macro_hit_at_1", 0.0)
            micro = row.get("hit_at_1", 0.0)
            comparison.append(f"| {config} | {acad:.4f} | {fin:.4f} | {sch:.4f} | {gen:.4f} | {macro:.4f} | {micro:.4f} |")
        all_cats = sorted(list({c.get("category") for c in cases if c.get("category")}))
        if all_cats:
            cat_header = " | ".join(all_cats)
            cat_sep = " | ".join(["---:"] * len(all_cats))
            comparison.extend(["", f"### Per-Category / Stress Type Hit@1 (N={len(cases)})", "", f"| Config | {cat_header} |", f"|---|{cat_sep}|"])
            for config, row in summary["scenario1"].items():
                pc = row.get("per_category", {})
                cat_vals = " | ".join(f"{pc.get(cat, {}).get('hit_at_1', 0.0):.4f}" for cat in all_cats)
                comparison.append(f"| {config} | {cat_vals} |")
        all_tiers = sorted(list({c.get("complexity_tier", "") for c in cases if c.get("complexity_tier")}))
        if all_tiers:
            tier_header = " | ".join(all_tiers)
            tier_sep = " | ".join(["---:"] * len(all_tiers))
            comparison.extend(["", f"### Per-Complexity-Tier Hit@1 (N={len(cases)})", "", f"| Config | {tier_header} |", f"|---|{tier_sep}|"])
            for config, row in summary["scenario1"].items():
                pt = row.get("per_tier", {})
                t_vals = " | ".join(f"{pt.get(t, {}).get('hit_at_1', 0.0):.4f}" for t in all_tiers)
                comparison.append(f"| {config} | {t_vals} |")

    if summary["scenario2"]:
        comparison.extend(["", "## Scenario 2", "", "| Config | AR | CR | CP | AC | Faith | Source recall | Source AP | Fact EM |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"])
        for config, row in summary["scenario2"].items():
            comparison.append(
                f"| {config} | {row['AR']['mean']:.4f} ± {row['AR']['sd']:.4f} "
                f"| {row['CR']['mean']:.4f} ± {row['CR']['sd']:.4f} "
                f"| {row['CP']['mean']:.4f} ± {row['CP']['sd']:.4f} "
                f"| {row['AC']['mean']:.4f} ± {row['AC']['sd']:.4f} "
                f"| {row['Faith']['mean']:.4f} ± {row['Faith']['sd']:.4f} "
                f"| {row['source_recall']:.4f} | {row['source_ap']:.4f} | {row['factual_exact_match']:.4f} |"
            )
    (LOG_DIR / "comparison.md").write_text("\n".join(comparison) + "\n", encoding="utf-8")

    # Update manifest checksums
    artifacts = {}
    for name in ("records.jsonl", "summary.json", "comparison.md", "failures.md", "checkpoint.json", "run.log"):
        path = LOG_DIR / name
        if path.exists():
            artifacts[name] = sha256_file(path)
    manifest["artifact_sha256"] = artifacts
    json_dump(LOG_DIR / "manifest.json", manifest)
    logger.info("Successfully updated manifest.json checksums.")
    print("\nSUCCESS: All artifacts recomputed and synchronized!")


if __name__ == "__main__":
    main()
