#!/usr/bin/env python3
"""Matched multi-agent versus monolithic tool-orchestration benchmark.

This v2 protocol fixes three limitations of the earlier exploratory runner:

* the multi-agent arm uses the live structured supervisor prediction instead of
  the gold domain label;
* tool outputs are checked against deterministic executions of the expected
  production tool instead of being accepted when ``expected_contains`` is empty;
* paired uncertainty is computed over unique cases, not over API repetitions.

The optional scalability levels add the same number of synthetic, explicitly
labelled distractor tools to every specialist. The monolithic arm sees all
distractors, whereas the multi-agent arm sees only those assigned to the
predicted specialist. This is a stress test of tool-space partitioning, not a
claim about the distractor tools' production quality.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

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
    sha256_file,
)
from app.services.evaluation_contract import (  # noqa: E402
    arguments_match,
    validate_unique_case_ids,
)
from app.services.orchestration_contract import repair_route_decision  # noqa: E402

PROTOCOL_VERSION = "multi-vs-single-v2.0"
DEFAULT_TOOL_DATASET = ROOT / "data" / "scenario3_production_tools.json"
DEFAULT_ROBUSTNESS_DATASET = ROOT / "data" / "scenario3_robustness_cases.json"
DEFAULT_OUTPUT_ROOT = ROOT / "logs" / "multi_vs_single_v2"

DISTRACTOR_SPECS: dict[str, list[tuple[str, str]]] = {
    "academic": [
        ("tra_cuu_nganh_tuyen_sinh", "Tra cứu ngành tuyển sinh theo tên hoặc mã ngành."),
        ("tim_nganh_theo_diem_chuan", "Tìm ngành theo điểm chuẩn hoặc phương thức xét tuyển."),
        ("tra_cuu_mon_tuong_duong", "Tra cứu học phần tương đương theo tên hoặc mã môn."),
        ("tra_cuu_lich_hoc", "Tra cứu lịch học dự kiến của một học phần."),
    ],
    "financial": [
        ("tra_cuu_hoc_phi_sau_dai_hoc", "Tra cứu học phí sau đại học theo ngành hoặc khóa."),
        ("tinh_hoc_phi_hoc_lai", "Tính học phí học lại từ học phần và số tín chỉ."),
        ("tra_cuu_hoan_hoc_phi", "Tra cứu điều kiện và tiến độ hoàn học phí."),
        ("tra_cuu_cong_no", "Tra cứu công nợ học phí của sinh viên."),
    ],
    "scholarship": [
        ("tra_cuu_hoc_bong_doanh_nghiep", "Tra cứu học bổng doanh nghiệp theo tên chương trình."),
        ("kiem_tra_dieu_kien_hoc_bong", "Kiểm tra điều kiện hồ sơ học bổng."),
        ("tra_cuu_han_nop_hoc_bong", "Tra cứu hạn nộp của một học bổng."),
        ("tinh_ho_tro_sinh_vien", "Tính mức hỗ trợ sinh viên theo diện chính sách."),
    ],
    "general": [
        ("tra_cuu_ky_tuc_xa", "Tra cứu thông tin ký túc xá và chỗ ở sinh viên."),
        ("tra_cuu_bao_hiem_y_te", "Tra cứu quy định bảo hiểm y tế sinh viên."),
        ("tra_cuu_vay_von", "Tra cứu chính sách vay vốn sinh viên."),
        ("tra_cuu_quy_che_sinh_vien", "Tra cứu quy chế và thủ tục sinh viên."),
    ],
}


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalized_output(value: Any) -> str:
    text = str(value).casefold()
    return re.sub(r"\s+", " ", text).strip()


def make_distractor_tools(per_domain: int) -> dict[str, list[Any]]:
    """Build deterministic synthetic tools for the declared scalability stress."""
    if per_domain < 0 or per_domain > 4:
        raise ValueError("distractors per domain must be between 0 and 4")
    from langchain_core.tools import StructuredTool

    result: dict[str, list[Any]] = {domain: [] for domain in DISTRACTOR_SPECS}
    for domain, specs in DISTRACTOR_SPECS.items():
        for name, description in specs[:per_domain]:
            def placeholder(keyword: str = "", *, _name: str = name) -> str:
                return f"SYNTHETIC_DISTRACTOR:{_name}:{keyword}"

            result[domain].append(StructuredTool.from_function(
                func=placeholder,
                name=name,
                description=(
                    description
                    + " Công cụ giả lập chỉ dùng trong scalability stress test; "
                    "tham số keyword chứa cụm từ cần tra cứu."
                ),
            ))
    return result


def expected_agent(case: dict[str, Any], suite: str) -> str:
    return str(case.get("agent") if suite == "production_tools" else case.get("expected_agent"))


def expected_intent(case: dict[str, Any], suite: str) -> str | None:
    if suite == "production_tools":
        return None
    value = case.get("expected_intent")
    return str(value) if value is not None else None


def make_case_key(suite: str, index: int, case: dict[str, Any]) -> str:
    # Keep the row index for stable pairing even though duplicate IDs are rejected.
    return f"{suite}:{index:03d}:{case.get('id', 'unknown')}"


def build_oracles(cases: Iterable[dict[str, Any]], tools_by_name: dict[str, Any]) -> dict[str, str]:
    """Execute expected production tools once to create deterministic output oracles."""
    oracles: dict[str, str] = {}
    for case in cases:
        tool_name = case.get("expected_tool")
        if not tool_name:
            continue
        tool = tools_by_name.get(tool_name)
        if tool is None:
            raise KeyError(f"Unknown expected tool: {tool_name}")
        oracle_key = stable_json({"tool": tool_name, "args": case.get("expected_args", {})})
        if oracle_key not in oracles:
            oracles[oracle_key] = normalized_output(tool.invoke(case.get("expected_args", {})))
    return oracles


def score_case(
    case: dict[str, Any],
    selected_tool: str | None,
    selected_args: dict[str, Any],
    output: str,
    bounded_pass: bool,
    oracles: dict[str, str],
) -> dict[str, bool]:
    wanted_tool = case.get("expected_tool")
    selection_passed = selected_tool == wanted_tool
    arguments_passed = selection_passed and (
        wanted_tool is None or arguments_match(
            case.get("expected_args", {}), selected_args,
            tool_name=wanted_tool, accepted=case.get("accepted_args", {}),
        )
    )

    if wanted_tool:
        oracle_key = stable_json({"tool": wanted_tool, "args": case.get("expected_args", {})})
        result_passed = (
            arguments_passed
            and oracle_key in oracles
            and normalized_output(output) == oracles[oracle_key]
        )
    else:
        accepted_phrases = case.get("expected_response_any", [])
        folded = normalized_output(output)
        result_passed = (
            any(normalized_output(token) in folded for token in accepted_phrases)
            if accepted_phrases else True
        )

    passed = selection_passed and arguments_passed and result_passed and bounded_pass
    return {
        "selection_passed": selection_passed,
        "arguments_passed": arguments_passed,
        "result_passed": result_passed,
        "passed": passed,
    }


async def invoke_without_tools(llm: Any, query: str, timeout: float) -> tuple[str | None, dict[str, Any], str, int, float]:
    from langchain_core.messages import HumanMessage, SystemMessage

    response, latency_ms = await bounded_ainvoke(
        llm,
        [SystemMessage(content=TOOL_GATE_PROMPT), HumanMessage(content=query)],
        timeout,
    )
    content = response.content if isinstance(response.content, str) else str(response.content or "")
    return None, {}, content, 0, latency_ms


async def call_with_backoff(factory: Any, *, retries: int) -> tuple[Any, int]:
    """Retry a complete model decision after the client-level retry is exhausted."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return await factory(), attempt
        except Exception as exc:  # Provider exceptions vary across SDK versions.
            last_error = exc
            if attempt == retries:
                break
            await asyncio.sleep(min(60.0, (2 ** attempt) + random.random()))
    assert last_error is not None
    raise last_error


async def evaluate_one(
    *,
    architecture: str,
    suite: str,
    case_key: str,
    case: dict[str, Any],
    repetition: int,
    distractors_per_domain: int,
    llm: Any,
    supervisor: Any,
    specialist_gates: dict[str, Any | None],
    specialist_tool_counts: dict[str, int],
    single_gate: Any,
    single_tool_count: int,
    tools_by_name: dict[str, Any],
    oracles: dict[str, str],
    timeout: float,
    max_tool_calls: int,
    retries: int,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    from app.agents.prompts import SUPERVISOR_PROMPT
    from langchain_core.messages import HumanMessage, SystemMessage

    actual_agent: str | None = None
    actual_intent: str | None = None
    selected_tool: str | None = None
    selected_args: dict[str, Any] = {}
    output = ""
    call_count = 0
    route_bounded = architecture == "single_agent"
    gate_bounded = False
    route_attempts = 0
    gate_attempts = 0
    error_parts: list[str] = []

    if architecture == "multi_agent":
        try:
            async def route_once() -> Any:
                async with semaphore:
                    return await bounded_ainvoke(
                        supervisor,
                        [SystemMessage(content=SUPERVISOR_PROMPT), HumanMessage(content=case["query"])],
                        timeout,
                    )

            (decision, _), route_attempts = await call_with_backoff(route_once, retries=retries)
            repaired = repair_route_decision(
                case["query"], decision.next_agent, decision.intent
            )
            actual_agent = repaired.agent
            actual_intent = repaired.intent.value
            route_bounded = True
        except Exception as exc:
            error_parts.append(f"route={type(exc).__name__}: {exc}")

    try:
        gate = specialist_gates.get(actual_agent) if architecture == "multi_agent" else single_gate
        async def gate_once() -> Any:
            async with semaphore:
                if gate is None:
                    return await invoke_without_tools(llm, case["query"], timeout)
                return await invoke_tool_gate(
                    gate, case["query"], timeout,
                    actual_agent if architecture == "multi_agent" else None,
                )

        gate_result, gate_attempts = await call_with_backoff(gate_once, retries=retries)
        selected_tool, selected_args, response_text, call_count, _ = gate_result
        tool = tools_by_name.get(selected_tool or "")
        output = str(await asyncio.to_thread(tool.invoke, selected_args)) if tool is not None else response_text
        gate_bounded = call_count <= max_tool_calls
    except Exception as exc:
        error_parts.append(f"gate={type(exc).__name__}: {exc}")

    bounded_pass = route_bounded and gate_bounded and not error_parts
    checks = score_case(case, selected_tool, selected_args, output, bounded_pass, oracles)
    target_agent = expected_agent(case, suite)
    target_intent = expected_intent(case, suite)

    return {
        "protocol": PROTOCOL_VERSION,
        "architecture": architecture,
        "suite": suite,
        "case_key": case_key,
        "case_id": case.get("id"),
        "repetition": repetition,
        "distractors_per_domain": distractors_per_domain,
        "visible_tool_count": (
            specialist_tool_counts.get(actual_agent or "", 0)
            if architecture == "multi_agent" else single_tool_count
        ),
        "query": case["query"],
        "expected_agent": target_agent,
        "actual_agent": actual_agent,
        "agent_correct": actual_agent == target_agent if architecture == "multi_agent" else None,
        "expected_intent": target_intent,
        "actual_intent": actual_intent,
        "intent_correct": (
            actual_intent == target_intent
            if architecture == "multi_agent" and target_intent is not None else None
        ),
        "expected_tool": case.get("expected_tool"),
        "selected_tool": selected_tool,
        "expected_args": case.get("expected_args", {}),
        "selected_args": selected_args,
        "tool_call_count": call_count,
        "route_attempts": route_attempts,
        "gate_attempts": gate_attempts,
        "output": output[:500],
        **checks,
        "bounded_pass": bounded_pass,
        "error": "; ".join(error_parts),
    }


def mean_bool(rows: list[dict[str, Any]], key: str) -> float:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return statistics.mean(values) if values else 0.0


def bootstrap_ci(values: list[float], *, seed: int = 20260914, draws: int = 10000) -> list[float]:
    if not values:
        return [0.0, 0.0]
    rng = random.Random(seed)
    samples = []
    for _ in range(draws):
        samples.append(statistics.mean(rng.choice(values) for _ in values))
    samples.sort()
    return [samples[int(0.025 * draws)], samples[int(0.975 * draws)]]


def paired_case_difference(rows: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        grouped[(row["architecture"], row["case_key"])].append(float(row[metric]))
    differences = []
    case_keys = sorted({key for _, key in grouped})
    for key in case_keys:
        multi = grouped.get(("multi_agent", key), [])
        single = grouped.get(("single_agent", key), [])
        if multi and single:
            differences.append(statistics.mean(multi) - statistics.mean(single))
    return {
        "mean": statistics.mean(differences) if differences else 0.0,
        "ci95": bootstrap_ci(differences),
        "unique_cases": len(differences),
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"protocol": PROTOCOL_VERSION, "levels": {}}
    levels = sorted({int(row["distractors_per_domain"]) for row in records})
    for level in levels:
        level_rows = [row for row in records if row["distractors_per_domain"] == level]
        level_summary: dict[str, Any] = {"suites": {}}
        for suite in ("production_tools", "robustness"):
            suite_rows = [row for row in level_rows if row["suite"] == suite]
            suite_summary: dict[str, Any] = {}
            for architecture in ("multi_agent", "single_agent"):
                rows = [row for row in suite_rows if row["architecture"] == architecture]
                suite_summary[architecture] = {
                    "runs": len(rows),
                    "unique_cases": len({row["case_key"] for row in rows}),
                    "tool_selection_accuracy": mean_bool(rows, "selection_passed"),
                    "argument_exact_match": mean_bool(rows, "arguments_passed"),
                    "result_accuracy": mean_bool(rows, "result_passed"),
                    "end_to_end_pass_rate": mean_bool(rows, "passed"),
                    "bounded_completion_rate": mean_bool(rows, "bounded_pass"),
                    "routing_agent_accuracy": (
                        mean_bool(rows, "agent_correct") if architecture == "multi_agent" else None
                    ),
                    "routing_intent_accuracy": (
                        mean_bool(rows, "intent_correct")
                        if architecture == "multi_agent"
                        and any(row.get("intent_correct") is not None for row in rows)
                        else None
                    ),
                    "errors": sum(bool(row["error"]) for row in rows),
                }
            suite_summary["paired_multi_minus_single"] = {
                metric: paired_case_difference(suite_rows, metric)
                for metric in ("selection_passed", "arguments_passed", "result_passed", "passed")
            }
            level_summary["suites"][suite] = suite_summary
        summary["levels"][str(level)] = level_summary
    return summary


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def generate_report(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Multi-Agent vs. Monolithic Tool Orchestration — v2",
        "",
        "This locked protocol uses live supervisor predictions for the multi-agent arm, "
        "deterministic tool-output oracles, and paired bootstrap intervals over unique cases.",
        "Synthetic distractors, when enabled, are a scalability stress test and are not production tools.",
        "",
    ]
    for level, payload in summary["levels"].items():
        lines.extend([f"## Distractors per specialist: {level}", ""])
        for suite, suite_payload in payload["suites"].items():
            lines.extend([
                f"### {suite}",
                "",
                "| Architecture | Unique cases | Runs | Selection | Arg EM | Result | E2E pass | Route acc. |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ])
            for architecture in ("multi_agent", "single_agent"):
                row = suite_payload[architecture]
                route = row["routing_agent_accuracy"]
                lines.append(
                    f"| {architecture} | {row['unique_cases']} | {row['runs']} | "
                    f"{row['tool_selection_accuracy']:.4f} | {row['argument_exact_match']:.4f} | "
                    f"{row['result_accuracy']:.4f} | {row['end_to_end_pass_rate']:.4f} | "
                    f"{route:.4f} |" if route is not None else
                    f"| {architecture} | {row['unique_cases']} | {row['runs']} | "
                    f"{row['tool_selection_accuracy']:.4f} | {row['argument_exact_match']:.4f} | "
                    f"{row['result_accuracy']:.4f} | {row['end_to_end_pass_rate']:.4f} | -- |"
                )
            paired = suite_payload["paired_multi_minus_single"]["passed"]
            lines.extend([
                "",
                f"Paired E2E difference (Multi − Single): **{paired['mean']:+.4f}**, "
                f"95% bootstrap CI [{paired['ci95'][0]:+.4f}, {paired['ci95'][1]:+.4f}] "
                f"over {paired['unique_cases']} unique cases.",
                "",
            ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


async def run_protocol(args: argparse.Namespace, run_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from app.agents.graph import RouteDecision

    setup_vertex_environment(args.credentials)
    initialize_services()
    tools_by_name, real_tools = get_tools()
    production_cases = json.loads(args.tool_dataset.read_text(encoding="utf-8"))
    robustness_cases = json.loads(args.robustness_dataset.read_text(encoding="utf-8"))
    validate_unique_case_ids(production_cases)
    validate_unique_case_ids(robustness_cases)
    if args.limit:
        production_cases = production_cases[: args.limit]
        robustness_cases = robustness_cases[: args.limit]

    indexed_cases: list[tuple[str, str, dict[str, Any]]] = []
    for suite, cases in (("production_tools", production_cases), ("robustness", robustness_cases)):
        for index, case in enumerate(cases, start=1):
            indexed_cases.append((suite, make_case_key(suite, index, case), case))

    oracles = build_oracles((case for _, _, case in indexed_cases), tools_by_name)
    llm = get_llm(model=args.model, temperature=0.0)
    supervisor = llm.with_structured_output(RouteDecision)
    semaphore = asyncio.Semaphore(args.workers)
    records: list[dict[str, Any]] = []

    jobs = []
    for level in args.levels:
        distractors = make_distractor_tools(level)
        specialist_gates: dict[str, Any | None] = {}
        specialist_tool_counts: dict[str, int] = {}
        all_distractors = []
        for domain, real_names in SPECIALIST_TOOLS.items():
            domain_tools = [tools_by_name[name] for name in real_names] + distractors[domain]
            specialist_gates[domain] = llm.bind_tools(domain_tools) if domain_tools else None
            specialist_tool_counts[domain] = len(domain_tools)
            all_distractors.extend(distractors[domain])
        single_tools = real_tools + all_distractors
        single_gate = llm.bind_tools(single_tools)

        for repetition in range(1, args.repetitions + 1):
            for suite, case_key, case in indexed_cases:
                for architecture in ("multi_agent", "single_agent"):
                    jobs.append(evaluate_one(
                        architecture=architecture,
                        suite=suite,
                        case_key=case_key,
                        case=case,
                        repetition=repetition,
                        distractors_per_domain=level,
                        llm=llm,
                        supervisor=supervisor,
                        specialist_gates=specialist_gates,
                        specialist_tool_counts=specialist_tool_counts,
                        single_gate=single_gate,
                        single_tool_count=len(single_tools),
                        tools_by_name=tools_by_name,
                        oracles=oracles,
                        timeout=args.timeout,
                        max_tool_calls=args.max_tool_calls,
                        retries=args.retries,
                        semaphore=semaphore,
                    ))

    # Fixed shuffle prevents architecture/order confounding while keeping the run reproducible.
    random.Random(args.seed).shuffle(jobs)
    for offset in range(0, len(jobs), args.workers):
        batch = jobs[offset: offset + args.workers]
        batch_records = await asyncio.gather(*batch)
        records.extend(batch_records)
        write_jsonl(run_dir / "records.partial.jsonl", records)
        print(f"completed {len(records)}/{len(jobs)}", flush=True)

    summary = summarize(records)
    return records, summary


def parse_levels(raw: str) -> list[int]:
    levels = sorted({int(item.strip()) for item in raw.split(",") if item.strip()})
    if not levels or any(level < 0 or level > 4 for level in levels):
        raise argparse.ArgumentTypeError("levels must be comma-separated integers between 0 and 4")
    return levels


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-dataset", type=Path, default=DEFAULT_TOOL_DATASET)
    parser.add_argument("--robustness-dataset", type=Path, default=DEFAULT_ROBUSTNESS_DATASET)
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--levels", type=parse_levels, default=parse_levels("0,4"))
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retries", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--max-tool-calls", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260914)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.repetitions < 1 or args.workers < 1 or args.retries < 1 or args.limit < 0:
        parser.error("repetitions/workers must be positive and limit must be non-negative")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.output_root / stamp
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "protocol": PROTOCOL_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "locked_before_execution",
        "primary_outcome": "paired unique-case end_to_end_pass_rate difference (multi - single)",
        "interpretation": "superiority only if the paired 95% bootstrap CI excludes zero",
        "multi_agent_arm": "live structured supervisor, then predicted-specialist tool gate",
        "single_agent_arm": "one monolithic gate exposing all available tools",
        "synthetic_distractors": "same count per specialist; monolithic arm sees their union",
        "repetitions": args.repetitions,
        "levels": args.levels,
        "workers": args.workers,
        "outer_retries": args.retries,
        "temperature": 0.0,
        "model": args.model,
        "limit": args.limit,
        "datasets": {
            "production_tools": str(args.tool_dataset.resolve()),
            "production_tools_sha256": sha256_file(args.tool_dataset),
            "robustness": str(args.robustness_dataset.resolve()),
            "robustness_sha256": sha256_file(args.robustness_dataset),
        },
        "script_sha256": sha256_file(Path(__file__)),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    records, summary = asyncio.run(run_protocol(args, run_dir))
    write_jsonl(run_dir / "records.jsonl", records)
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    generate_report(summary, run_dir / "comparison.md")
    manifest["status"] = "complete"
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["artifacts"] = {
        name: sha256_file(run_dir / name)
        for name in ("records.jsonl", "summary.json", "comparison.md")
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    partial = run_dir / "records.partial.jsonl"
    if partial.exists():
        partial.unlink()
    print(f"complete: {run_dir}")


if __name__ == "__main__":
    main()
