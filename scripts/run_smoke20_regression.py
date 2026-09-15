#!/usr/bin/env python3
"""Fast 20-case regression gate for routing, tool calls, and retrieval.

The fixture deliberately contains both required cases and two known target cases.
Required failures produce a non-zero exit code. Target failures are reported but
only become blocking when ``--strict-targets`` is supplied.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_multi_vs_single_agent_experiment import (  # noqa: E402
    DEFAULT_CREDENTIALS,
    DEFAULT_MODEL,
    SPECIALIST_TOOLS,
    TOOL_GATE_PROMPT,
    bounded_ainvoke,
    get_llm,
    get_tools,
    initialize_services,
    invoke_tool_gate,
    setup_vertex_environment,
)
from app.services.evaluation_contract import (  # noqa: E402
    arguments_match as contract_arguments_match,
    validate_unique_case_ids,
)
from app.services.orchestration_contract import repair_route_decision  # noqa: E402
from scripts.run_multi_vs_single_agent_v2_experiment import (  # noqa: E402
    call_with_backoff,
    invoke_without_tools,
)

PROTOCOL_VERSION = "smoke20-v1.0"
DEFAULT_DATASET = ROOT / "data" / "smoke20_regression.jsonl"
DEFAULT_OUTPUT_ROOT = ROOT / "logs" / "smoke20"


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [str(case["id"]) for case in cases]
    if len(cases) != 20 or len(ids) != len(set(ids)):
        raise ValueError("Smoke fixture must contain exactly 20 uniquely identified cases")
    validate_unique_case_ids(cases)
    counts = Counter(str(case["domain"]) for case in cases)
    if counts != Counter({"academic": 5, "financial": 5, "scholarship": 5, "general": 5}):
        raise ValueError(f"Smoke fixture must contain five cases per domain, got {dict(counts)}")
    return cases


def normalize(value: Any) -> Any:
    if isinstance(value, str):
        decomposed = unicodedata.normalize("NFD", value.casefold())
        folded = "".join(
            character for character in decomposed
            if unicodedata.category(character) != "Mn"
        ).replace("đ", "d")
        return re.sub(r"[^a-z0-9]+", " ", folded).strip()
    if isinstance(value, (int, float)):
        return round(float(value), 6)
    return value


def argument_value_matches(expected: Any, actual: Any, alternatives: list[Any]) -> bool:
    expected_n = normalize(expected)
    actual_n = normalize(actual)
    if expected_n == actual_n or any(normalize(item) == actual_n for item in alternatives):
        return True
    if isinstance(expected_n, str) and isinstance(actual_n, str):
        return bool(expected_n and actual_n and (expected_n in actual_n or actual_n in expected_n))
    return False


def arguments_match(case: dict[str, Any], actual: dict[str, Any]) -> bool:
    return contract_arguments_match(
        case.get("expected_args", {}), actual,
        tool_name=case.get("expected_tool"), accepted=case.get("accepted_args", {}),
    )


async def run_route_tool_checks(
    cases: list[dict[str, Any]],
    *,
    timeout: float,
    retries: int,
    workers: int,
    execute_tools: bool,
) -> list[dict[str, Any]]:
    from app.agents.graph import RouteDecision
    from app.agents.prompts import SUPERVISOR_PROMPT
    from langchain_core.messages import HumanMessage, SystemMessage

    if execute_tools:
        initialize_services()
    tools_by_name, _ = get_tools()
    llm = get_llm(model=DEFAULT_MODEL, temperature=0.0)
    supervisor = llm.with_structured_output(RouteDecision)
    specialist_gates = {
        domain: llm.bind_tools([tools_by_name[name] for name in names]) if names else None
        for domain, names in SPECIALIST_TOOLS.items()
    }
    semaphore = asyncio.Semaphore(max(1, workers))

    async def evaluate(case: dict[str, Any]) -> dict[str, Any]:
        error = ""
        actual_agent = actual_intent = selected_tool = None
        selected_args: dict[str, Any] = {}
        output = ""
        call_count = 0
        try:
            async def route_once() -> Any:
                async with semaphore:
                    response, _ = await bounded_ainvoke(
                        supervisor,
                        [SystemMessage(content=SUPERVISOR_PROMPT), HumanMessage(content=case["query"])],
                        timeout,
                    )
                    return response

            decision, _ = await call_with_backoff(route_once, retries=retries)
            repaired = repair_route_decision(
                case["query"], decision.next_agent, decision.intent
            )
            actual_agent, actual_intent = repaired.agent, repaired.intent.value

            async def gate_once() -> Any:
                gate = specialist_gates.get(actual_agent)
                async with semaphore:
                    if gate is None:
                        return await invoke_without_tools(llm, case["query"], timeout)
                    return await invoke_tool_gate(
                        gate, case["query"], timeout, actual_agent
                    )

            gate_result, _ = await call_with_backoff(gate_once, retries=retries)
            selected_tool, selected_args, response_text, call_count, _ = gate_result
            tool = tools_by_name.get(selected_tool or "")
            if execute_tools and tool is not None:
                output = str(await asyncio.to_thread(tool.invoke, selected_args))
            else:
                output = response_text
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        agent_pass = actual_agent == case["expected_agent"]
        intent_pass = actual_intent == case["expected_intent"]
        selection_pass = selected_tool == case.get("expected_tool")
        args_pass = selection_pass and (
            selected_tool is None or arguments_match(case, selected_args)
        )
        execution_pass = (
            not error and (selected_tool is None or bool(output.strip()))
            if execute_tools else None
        )
        passed = (
            agent_pass and intent_pass and selection_pass and args_pass and call_count <= 1
            and (execution_pass is not False)
        )
        return {
            "id": case["id"],
            "domain": case["domain"],
            "tier": case["tier"],
            "check": "route_tool",
            "passed": passed,
            "agent_passed": agent_pass,
            "intent_passed": intent_pass,
            "selection_passed": selection_pass,
            "arguments_passed": args_pass,
            "execution_checked": execute_tools,
            "execution_passed": execution_pass,
            "expected_agent": case["expected_agent"],
            "actual_agent": actual_agent,
            "expected_intent": case["expected_intent"],
            "actual_intent": actual_intent,
            "expected_tool": case.get("expected_tool"),
            "selected_tool": selected_tool,
            "expected_args": case.get("expected_args", {}),
            "selected_args": selected_args,
            "tool_call_count": call_count,
            "output": output[:300],
            "error": error,
        }

    return await asyncio.gather(*(evaluate(case) for case in cases))


def run_retrieval_checks(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from scripts.run_scenario12_experiment import initialize_retrieval
    from scripts.scenario12_common import ScenarioCase, retrieve_configurations, source_from_document

    eligible = [case for case in cases if case.get("gold_sources")]
    engine, graph, catalog, compressor = initialize_retrieval()
    records: list[dict[str, Any]] = []
    try:
        for case in eligible:
            scenario_case = ScenarioCase(
                case_id=case["id"],
                category=case["expected_intent"],
                question=case["query"],
                reference_answer="smoke retrieval check",
                raw_evidence="smoke retrieval check",
                gold_sources=list(case["gold_sources"]),
                source_relation=case.get("source_relation", "single"),
                review_status="approved",
            )
            trace = retrieve_configurations(
                scenario_case, engine, graph, catalog, compressor, top_k=7, metric_k=10,
            )
            sources = []
            for document in trace.configs["E5"]:
                source = source_from_document(document)
                if source and source not in sources:
                    sources.append(source)
            gold = set(case["gold_sources"])
            rank = next((index for index, source in enumerate(sources, start=1) if source in gold), None)
            threshold = int(case.get("retrieval_k", 3))
            records.append({
                "id": case["id"],
                "domain": case["domain"],
                "tier": case["tier"],
                "check": "retrieval",
                "passed": rank is not None and rank <= threshold,
                "gold_sources": case["gold_sources"],
                "gold_rank": rank,
                "required_rank": threshold,
                "retrieved_sources": sources[:10],
                "active_lanes": trace.active_lanes,
                "gate_reasons": trace.gate_reasons,
            })
    finally:
        graph.close()
    return records


def write_smoke_report(records: list[dict[str, Any]], output_path: Path) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["check"]].append(record)
    lines = [
        "# Smoke-20 Regression Report",
        "",
        f"Protocol: `{PROTOCOL_VERSION}`  ",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        "",
    ]
    for check, rows in grouped.items():
        lines.extend([
            f"## {check}",
            "",
            f"Passed: **{sum(row['passed'] for row in rows)}/{len(rows)}**",
            "",
            "| ID | Domain | Tier | Result | Diagnostic |",
            "|---|---|---|---:|---|",
        ])
        for row in rows:
            if check == "retrieval":
                diagnostic = f"gold rank={row['gold_rank']}; required <= {row['required_rank']}"
            else:
                failed = [
                    key.removesuffix("_passed") for key, value in row.items()
                    if key.endswith("_passed") and value is False
                ]
                diagnostic = ", ".join(failed) if failed else "ok"
            lines.append(
                f"| {row['id']} | {row['domain']} | {row['tier']} | "
                f"{'PASS' if row['passed'] else 'FAIL'} | {diagnostic} |"
            )
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


async def async_main(args: argparse.Namespace) -> int:
    cases = load_cases(Path(args.dataset))
    records: list[dict[str, Any]] = []
    environment_errors: list[str] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_ROOT / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.mode in {"route-tool", "all"}:
        try:
            setup_vertex_environment(Path(args.credentials))
            records.extend(await run_route_tool_checks(
                cases,
                timeout=args.timeout,
                retries=args.retries,
                workers=args.workers,
                execute_tools=args.execute_tools,
            ))
        except Exception as exc:
            environment_errors.append(f"route-tool: {type(exc).__name__}: {exc}")
    if args.mode in {"retrieval", "all"}:
        try:
            records.extend(await asyncio.to_thread(run_retrieval_checks, cases))
        except Exception as exc:
            environment_errors.append(f"retrieval: {type(exc).__name__}: {exc}")

    with (output_dir / "records.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    write_smoke_report(records, output_dir / "report.md")
    summary = {
        "protocol": PROTOCOL_VERSION,
        "mode": args.mode,
        "total_checks": len(records),
        "passed": sum(record["passed"] for record in records),
        "required_failures": [
            record["id"] + ":" + record["check"]
            for record in records if record["tier"] == "required" and not record["passed"]
        ],
        "target_failures": [
            record["id"] + ":" + record["check"]
            for record in records if record["tier"] == "target" and not record["passed"]
        ],
        "environment_errors": environment_errors,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"report: {output_dir / 'report.md'}")
    blocking = (
        summary["environment_errors"]
        or summary["required_failures"]
        or (args.strict_targets and summary["target_failures"])
    )
    return 1 if blocking else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the balanced 20-case regression gate")
    parser.add_argument("--mode", choices=("route-tool", "retrieval", "all"), default="route-tool")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--credentials", default=str(DEFAULT_CREDENTIALS))
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--execute-tools",
        action="store_true",
        help="Execute selected tools; requires the local Neo4j-backed services to be available.",
    )
    parser.add_argument("--strict-targets", action="store_true")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(async_main(args)))


if __name__ == "__main__":
    main()
