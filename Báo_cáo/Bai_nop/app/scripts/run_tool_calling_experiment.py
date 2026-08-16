"""Run the isolated 30-case financial-function experiment and write Markdown evidence."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.tools.scholarship import tinh_tien_hoc_bong
from app.tools.tuition import tinh_toan_hoc_phi
from app.tools.tuition_lookup import tra_cuu_hoc_phi


DEFAULT_DATASET = ROOT / "data" / "tool_calling_experiment.json"
DEFAULT_OUTPUT = ROOT / "logs" / "tool_calling_experiment_results.md"
FUNCTIONS = {
    "tuition_lookup": tra_cuu_hoc_phi,
    "scholarship_calculation": tinh_tien_hoc_bong,
    "tuition_reduction_calculation": tinh_toan_hoc_phi,
}
TOOL_SYSTEM_PROMPT = """You are testing tool selection for a Vietnamese student-finance chatbot.
Call exactly one tool when the user asks you to calculate a scholarship from supplied GPA and conduct score,
or asks you to calculate tuition remaining after a reduction from supplied actual tuition, exemption basis,
and reduction percentage. Use the supplied values exactly. Do not calculate mentally and do not answer directly."""


def _same_value(expected: Any, actual: Any) -> bool:
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(expected) - float(actual)) < 1e-9
    expected_text = str(expected).strip().casefold()
    actual_text = str(actual).strip().casefold()
    if not expected_text or not actual_text:
        return expected_text == actual_text
    return expected_text == actual_text or expected_text in actual_text or actual_text in expected_text


def evaluate_case(case: dict[str, Any], *, selected_tool: str | None, selected_args: dict[str, Any], output: str) -> dict[str, Any]:
    expected_args = case.get("expected_args", {})
    selection_passed = selected_tool == case["expected_tool"]
    arguments_passed = selection_passed and all(
        key in selected_args and _same_value(value, selected_args[key]) for key, value in expected_args.items()
    )
    folded = output.casefold()
    result_passed = all(token.casefold() in folded for token in case["expected_contains"]) and all(
        token.casefold() not in folded for token in case.get("expected_not_contains", [])
    )
    return {
        **case,
        "selected_tool": selected_tool,
        "selected_args": selected_args,
        "output": output,
        "selection_passed": selection_passed,
        "arguments_passed": arguments_passed,
        "result_passed": result_passed,
        "passed": selection_passed and arguments_passed and result_passed,
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["function"]].append(record)

    def counts(items: list[dict[str, Any]]) -> dict[str, int]:
        return {
            "total": len(items),
            "selection_passed": sum(bool(item["selection_passed"]) for item in items),
            "arguments_passed": sum(bool(item["arguments_passed"]) for item in items),
            "result_passed": sum(bool(item["result_passed"]) for item in items),
            "passed": sum(bool(item["passed"]) for item in items),
        }

    return {"by_function": {name: counts(items) for name, items in grouped.items()}, "overall": counts(records)}


def run_case(case: dict[str, Any], llm_with_tools: Any) -> dict[str, Any]:
    if case["function"] == "tuition_lookup":
        args = {"cau_hoi": case["query"]}
        output = tra_cuu_hoc_phi.invoke(args)
        return evaluate_case(case, selected_tool="tra_cuu_hoc_phi", selected_args=args, output=output)

    response = llm_with_tools.invoke([SystemMessage(content=TOOL_SYSTEM_PROMPT), HumanMessage(content=case["query"])])
    call = response.tool_calls[0] if response.tool_calls else None
    selected_tool = call.get("name") if call else None
    selected_args = call.get("args", {}) if call else {}
    tool = {"tinh_tien_hoc_bong": tinh_tien_hoc_bong, "tinh_toan_hoc_phi": tinh_toan_hoc_phi}.get(selected_tool)
    output = tool.invoke(selected_args) if tool else str(response.content)
    return evaluate_case(case, selected_tool=selected_tool, selected_args=selected_args, output=output)


def write_report(path: Path, records: list[dict[str, Any]], model: str, started_at: str) -> None:
    summary = summarize(records)
    labels = {
        "tuition_lookup": "Structured tuition lookup",
        "scholarship_calculation": "Scholarship tool calling",
        "tuition_reduction_calculation": "Tuition-reduction tool calling",
    }
    lines = [
        "# Financial Function Experiment Results", "",
        f"- Started: `{started_at}`",
        f"- Gemini model for tool selection: `{model}`",
        f"- Dataset: `{DEFAULT_DATASET.relative_to(ROOT).as_posix()}`",
        "- Design: 10 cases per financial function; isolated sessions; deterministic result checks.", "",
        "> Tuition lookup is a structured orchestration step. Scholarship and tuition-reduction calculations are Gemini tool calls.", "",
        "## Summary", "",
        "| Function | Selection/path | Arguments | Result | End-to-end case pass |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("tuition_lookup", "scholarship_calculation", "tuition_reduction_calculation"):
        item = summary["by_function"][name]
        total = item["total"]
        lines.append(
            f"| {labels[name]} | {item['selection_passed']}/{total} | {item['arguments_passed']}/{total} | "
            f"{item['result_passed']}/{total} | {item['passed']}/{total} |"
        )
    overall = summary["overall"]
    lines.append(
        f"| **Overall** | **{overall['selection_passed']}/{overall['total']}** | "
        f"**{overall['arguments_passed']}/{overall['total']}** | **{overall['result_passed']}/{overall['total']}** | "
        f"**{overall['passed']}/{overall['total']}** |"
    )
    lines += ["", "## Case-level evidence", ""]
    for record in records:
        status = "PASS" if record["passed"] else "FAIL"
        lines += [
            f"### Case {record['id']:02d} - {status}", "",
            f"- Function: `{record['function']}`",
            f"- Focus: `{record['test_focus']}`",
            f"- Query: {record['query']}",
            f"- Expected tool/path: `{record['expected_tool']}`",
            f"- Selected tool/path: `{record['selected_tool']}`",
            f"- Expected arguments: `{json.dumps(record['expected_args'], ensure_ascii=False)}`",
            f"- Selected arguments: `{json.dumps(record['selected_args'], ensure_ascii=False)}`",
            f"- Checks: selection/path={'PASS' if record['selection_passed'] else 'FAIL'}, "
            f"arguments={'PASS' if record['arguments_passed'] else 'FAIL'}, result={'PASS' if record['result_passed'] else 'FAIL'}",
            "", "**Tool output**", "", "```text", record["output"], "```", "",
        ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default="gemini-3.5-flash-lite")
    parser.add_argument("--delay", type=float, default=5.0, help="Seconds between Gemini requests")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        raise SystemExit("GOOGLE_API_KEY or GEMINI_API_KEY is required")
    cases = json.loads(args.dataset.read_text(encoding="utf-8"))
    model = ChatGoogleGenerativeAI(model=args.model, temperature=0.0)
    llm_with_tools = model.bind_tools([tinh_tien_hoc_bong, tinh_toan_hoc_phi])
    started_at = datetime.now().astimezone().isoformat()
    records = []
    for case in cases:
        record = run_case(case, llm_with_tools)
        records.append(record)
        print(f"[{case['id']:02d}/30] {'PASS' if record['passed'] else 'FAIL'} {case['function']}")
        if case["function"] != "tuition_lookup" and case["id"] != cases[-1]["id"]:
            time.sleep(args.delay)
    write_report(args.output, records, args.model, started_at)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
