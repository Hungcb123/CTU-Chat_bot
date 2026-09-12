#!/usr/bin/env python3
"""Rescore a Scenario 3 run with the current routing inclusion and label rules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_scenario3_experiment import (
    DEFAULT_ROBUSTNESS_DATASET,
    DEFAULT_ROUTING_DATASET,
    DEFAULT_ROUTING_LABELS,
    arguments_match,
    load_json_cases,
    load_routing_cases,
    render_report,
    sha256_file,
    summarize_records,
)


def rescore_run(
    run_dir: Path,
    routing_dataset: Path,
    routing_labels: Path,
    robustness_dataset: Path,
) -> dict:
    records_path = run_dir / "records.jsonl"
    manifest_path = run_dir / "manifest.json"
    if not records_path.exists() or not manifest_path.exists():
        raise FileNotFoundError(f"Run directory thiếu records.jsonl hoặc manifest.json: {run_dir}")

    routing_targets = {
        str(case["id"]): case
        for case in load_routing_cases(routing_dataset, routing_labels)
    }
    robustness_targets = {
        str(case["id"]): case
        for case in load_json_cases(robustness_dataset)
    }
    original_records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    rescored_records = []
    excluded_routing_records = 0
    relabeled_routing_records = 0
    for record in original_records:
        if record.get("suite") == "robustness":
            target = robustness_targets.get(str(record.get("id")))
            if target is None:
                rescored_records.append(record)
                continue
            updated = dict(record)
            for field in (
                "failure_mode", "query", "expected_agent", "expected_intent",
                "expected_tool", "expected_args", "expected_contains",
                "expected_response_any",
            ):
                if field in target:
                    updated[field] = target[field]
                else:
                    updated.pop(field, None)
            updated["agent_correct"] = updated.get("actual_agent") == target["expected_agent"]
            updated["intent_correct"] = updated.get("actual_intent") == target["expected_intent"]
            updated["tool_decision_correct"] = updated.get("selected_tool") == target.get("expected_tool")
            updated["arguments_passed"] = updated["tool_decision_correct"] and arguments_match(
                target.get("expected_args", {}), updated.get("selected_args", {})
            )
            folded = str(updated.get("output", "")).casefold()
            expected_contains = target.get("expected_contains", [])
            expected_response_any = target.get("expected_response_any", [])
            updated["result_passed"] = (
                all(token.casefold() in folded for token in expected_contains)
                if expected_contains
                else any(token.casefold() in folded for token in expected_response_any)
            )
            updated["passed"] = all((
                updated["agent_correct"],
                updated["intent_correct"],
                updated["tool_decision_correct"],
                updated["arguments_passed"],
                updated["result_passed"],
                updated.get("bounded_pass", False),
            ))
            rescored_records.append(updated)
            continue

        if record.get("suite") != "routing":
            rescored_records.append(record)
            continue

        target = routing_targets.get(str(record.get("id")))
        if target is None:
            excluded_routing_records += 1
            continue

        updated = dict(record)
        previous_target = (updated.get("expected_agent"), updated.get("expected_intent"))
        current_target = (target["expected_agent"], target["expected_intent"])
        if previous_target != current_target:
            relabeled_routing_records += 1
        updated.update({
            "expected_agent": target["expected_agent"],
            "expected_intent": target["expected_intent"],
            "label_source": target["label_source"],
            "agent_correct": updated.get("actual_agent") == target["expected_agent"],
            "intent_correct": updated.get("actual_intent") == target["expected_intent"],
        })
        rescored_records.append(updated)

    summary = summarize_records(rescored_records)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rescore_metadata = {
        "source_run": str(run_dir),
        "original_record_count": len(original_records),
        "rescored_record_count": len(rescored_records),
        "excluded_routing_records": excluded_routing_records,
        "relabeled_routing_records": relabeled_routing_records,
        "routing_dataset_sha256": sha256_file(routing_dataset),
        "routing_labels_sha256": sha256_file(routing_labels),
        "robustness_dataset_sha256": sha256_file(robustness_dataset),
    }
    report = render_report(summary, manifest)
    report += (
        "\n## Rescore metadata\n\n"
        f"- Original records: `{len(original_records)}`\n"
        f"- Rescored records: `{len(rescored_records)}`\n"
        f"- Excluded composite routing records: `{excluded_routing_records}`\n"
        f"- Relabeled routing records: `{relabeled_routing_records}`\n"
    )

    with (run_dir / "records_rescored.jsonl").open("w", encoding="utf-8") as handle:
        for record in rescored_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    (run_dir / "summary_rescored.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (run_dir / "report_rescored.md").write_text(report, encoding="utf-8")
    (run_dir / "rescore_manifest.json").write_text(
        json.dumps(rescore_metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"summary": summary, "metadata": rescore_metadata}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--routing-dataset", type=Path, default=DEFAULT_ROUTING_DATASET)
    parser.add_argument("--routing-labels", type=Path, default=DEFAULT_ROUTING_LABELS)
    parser.add_argument("--robustness-dataset", type=Path, default=DEFAULT_ROBUSTNESS_DATASET)
    args = parser.parse_args()
    result = rescore_run(
        args.run_dir,
        args.routing_dataset,
        args.routing_labels,
        args.robustness_dataset,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Rescored report: {args.run_dir / 'report_rescored.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
