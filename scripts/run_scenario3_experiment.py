#!/usr/bin/env python3
"""Run Scenario 3: multi-agent routing, tool reliability, and robustness.

The runner intentionally keeps this experiment separate from the retrieval and
end-to-end QA benchmarks used for Tables 3 and 4. Every run is written to a new
timestamped directory so results cannot be silently reused across datasets.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import os
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_ROUTING_DATASET = ROOT / "data" / "Paper" / "150_NATURAL_NO_APPENDIX.csv"
DEFAULT_ROUTING_LABELS = ROOT / "data" / "scenario3_routing_labels.json"
DEFAULT_TOOL_DATASET = ROOT / "data" / "scenario3_production_tools.json"
DEFAULT_ROBUSTNESS_DATASET = ROOT / "data" / "scenario3_robustness_cases.json"
DEFAULT_CREDENTIALS = ROOT / "gen-lang-client-0656432358-9a6fb12696b2.json"
DEFAULT_OUTPUT_ROOT = ROOT / "logs" / "scenario3"
DEFAULT_MODEL = "gemini-2.5-flash-lite"


TOOL_GATE_PROMPT = """Bạn đang kiểm thử cổng gọi công cụ của chatbot sinh viên CTU.
Chỉ gọi đúng MỘT công cụ khi câu hỏi có đủ tham số bắt buộc và các giá trị hợp lệ.

- tinh_tien_hoc_bong: chỉ gọi khi có GPA trong [0,4] và điểm rèn luyện trong [0,100].
  khoi_nganh là tùy chọn; dùng chuỗi rỗng nếu người dùng nói chưa rõ khối ngành.
- tinh_toan_hoc_phi: chỉ gọi khi có học phí thực tế, mức cơ sở miễn giảm không âm,
  và phần trăm giảm trong [0,100].
- tra_cuu_hoc_phi_graph: gọi cho yêu cầu tra cứu mức học phí thực tế theo ngành/chương trình;
  công cụ có thể yêu cầu làm rõ khóa tuyển sinh.

Không dùng công cụ tính toán cho câu hỏi chính sách, học bổng tài trợ, vay vốn,
quy chế học vụ hoặc chương trình đào tạo. Không tự bịa tham số còn thiếu. Nếu chưa
đủ dữ liệu hoặc dữ liệu không hợp lệ, không gọi công cụ và trả lời ngắn gọn rằng
người dùng cần bổ sung hoặc sửa thông tin nào."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def same_value(expected: Any, actual: Any) -> bool:
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(expected) - float(actual)) < 1e-9
    expected_text = str(expected).strip().casefold()
    actual_text = str(actual).strip().casefold()
    if not expected_text or not actual_text:
        return expected_text == actual_text
    return (
        expected_text == actual_text
        or expected_text in actual_text
        or actual_text in expected_text
    )


def arguments_match(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    return all(key in actual and same_value(value, actual[key]) for key, value in expected.items())


def parse_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                text = block.get("text")
                if text:
                    parts.append(str(text))
            elif block:
                parts.append(str(block))
        return " ".join(parts)
    return str(content or "")


def load_routing_cases(dataset: Path, labels_path: Path) -> list[dict[str, Any]]:
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    excluded_prefixes = tuple(labels.get("_exclude_id_prefixes", []))
    overrides = labels.get("_overrides", {})
    cases: list[dict[str, Any]] = []
    with dataset.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required_columns = {"Original ID", "Master Question", "Category"}
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Routing CSV thiếu cột: {sorted(missing)}")
        for row_number, row in enumerate(reader, start=1):
            case_id = (row.get("Original ID") or str(row_number)).strip()
            query = (row.get("Master Question") or "").strip()
            category = (row.get("Category") or "").strip()
            if excluded_prefixes and case_id.startswith(excluded_prefixes):
                continue
            if not query:
                raise ValueError(f"Routing CSV có câu hỏi rỗng ở dòng dữ liệu {row_number}")
            if category not in labels:
                raise ValueError(f"Category chưa có nhãn Scenario 3: {category!r}")
            target = overrides.get(case_id, labels[category])
            cases.append({
                "id": case_id,
                "category": category,
                "query": query,
                "expected_agent": target["expected_agent"],
                "expected_intent": target["expected_intent"],
                "label_source": "override" if case_id in overrides else "category",
            })
    return cases


def load_json_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"Dataset phải là JSON array không rỗng: {path}")
    return payload


def validate_datasets(args: argparse.Namespace) -> dict[str, Any]:
    routing = load_routing_cases(args.routing_dataset, args.routing_labels)
    tools = load_json_cases(args.tool_dataset)
    if len(tools) != 60:
        raise ValueError(f"Production tool dataset phải có đúng 60 ca, nhận {len(tools)}")
    expected_functions = {
        "tra_cuu_nganh", "so_sanh_nganh", "tim_nganh", "xem_chuoi_tien_quyet",
        "mon_chung_giua_nganh", "tim_nganh_co_mon", "tra_cuu_hoc_phi_graph",
        "tra_cuu_co_so_mien_giam_graph", "tra_cuu_quy_dinh_hoc_phi",
        "tinh_toan_hoc_phi", "tinh_tien_hoc_bong", "no_tool",
    }
    observed = Counter(case.get("function") for case in tools)
    missing = expected_functions.difference(observed)
    if missing or any(observed[name] != 5 for name in expected_functions):
        raise ValueError(f"Mỗi function phải có đúng 5 ca; thiếu={sorted(missing)}, counts={dict(observed)}")
    for case in tools:
        for key in ("id", "agent", "function", "query", "expected_tool", "expected_args"):
            if key not in case:
                raise ValueError(f"Tool case {case.get('id')} thiếu {key}")
    robustness = load_json_cases(args.robustness_dataset)

    ids = [str(case["id"]) for case in robustness]
    if len(ids) != len(set(ids)):
        raise ValueError("Robustness dataset có ID trùng nhau")
    for case in robustness:
        for key in ("failure_mode", "query", "expected_agent", "expected_intent"):
            if key not in case:
                raise ValueError(f"Robustness case {case.get('id')} thiếu {key}")
        if case.get("expected_tool") and "expected_args" not in case:
            raise ValueError(f"Robustness case {case['id']} có tool nhưng thiếu expected_args")

    return {
        "routing_cases": len(routing),
        "routing_categories": dict(sorted(Counter(c["category"] for c in routing).items())),
        "tool_cases": len(tools),
        "tool_functions": dict(sorted(Counter(c["function"] for c in tools).items())),
        "robustness_cases": len(robustness),
        "failure_modes": dict(sorted(Counter(c["failure_mode"] for c in robustness).items())),
    }


def configure_vertex_auth(credentials_path: Path, project_override: str | None) -> str | None:
    project = project_override
    if credentials_path.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path.resolve())
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
        if not project:
            credential_metadata = json.loads(credentials_path.read_text(encoding="utf-8"))
            project = credential_metadata.get("project_id")
    if project:
        os.environ["GOOGLE_CLOUD_PROJECT"] = project
    return project


def create_llm(args: argparse.Namespace):
    from dotenv import load_dotenv
    from langchain_google_genai import ChatGoogleGenerativeAI

    load_dotenv(ROOT / ".env")
    project = configure_vertex_auth(args.credentials, args.project)
    kwargs: dict[str, Any] = {
        "model": args.model,
        "temperature": 0.0,
        "max_retries": args.max_retries,
        "timeout": args.timeout,
    }
    if project:
        kwargs.update(vertexai=True, project=project, location=args.location)
    return ChatGoogleGenerativeAI(**kwargs), project


async def bounded_ainvoke(runnable: Any, payload: Any, timeout: float) -> tuple[Any, float]:
    started = time.perf_counter()
    result = await asyncio.wait_for(runnable.ainvoke(payload), timeout=timeout)
    return result, (time.perf_counter() - started) * 1000


def rule_route(query: str) -> tuple[str, str]:
    from app.services.query_intent import QueryIntent, classify_query_intent

    intent_to_agent = {
        QueryIntent.ACTUAL_TUITION: "financial",
        QueryIntent.AMBIGUOUS_TUITION: "financial",
        QueryIntent.EXEMPTION_BASIS: "financial",
        QueryIntent.EXEMPTION_POLICY: "financial",
        QueryIntent.CALCULATION: "financial",
        QueryIntent.BOTH: "financial",
        QueryIntent.SCHOLARSHIP: "scholarship",
        QueryIntent.STUDENT_LOAN: "general",
        QueryIntent.SOCIAL_SUPPORT: "general",
        QueryIntent.ACADEMIC_PROGRAM: "academic",
        QueryIntent.ACADEMIC_RULES: "general",
        QueryIntent.OTHER: "general",
    }
    decision = classify_query_intent(query)
    return intent_to_agent.get(decision.intent, "general"), decision.intent.value


async def run_routing_suite(
    cases: list[dict[str, Any]], llm: Any, args: argparse.Namespace
) -> list[dict[str, Any]]:
    from langchain_core.messages import HumanMessage, SystemMessage
    from app.agents.graph import RouteDecision
    from app.agents.prompts import SUPERVISOR_PROMPT

    selected = cases[: args.limit] if args.limit else cases
    records: list[dict[str, Any]] = []
    for case in selected:
        started = time.perf_counter()
        actual_agent, actual_intent = rule_route(case["query"])
        latency_ms = (time.perf_counter() - started) * 1000
        records.append({
            **case,
            "suite": "routing",
            "variant": "rule_router",
            "repetition": 1,
            "actual_agent": actual_agent,
            "actual_intent": actual_intent,
            "agent_correct": actual_agent == case["expected_agent"],
            "intent_correct": actual_intent == case["expected_intent"],
            "bounded_pass": True,
            "latency_ms": round(latency_ms, 3),
            "error": "",
        })

    supervisor = llm.with_structured_output(RouteDecision)
    for repetition in range(1, args.repetitions + 1):
        for index, case in enumerate(selected, start=1):
            error = ""
            actual_agent = "error"
            actual_intent = "error"
            latency_ms = 0.0
            bounded_pass = False
            try:
                decision, latency_ms = await bounded_ainvoke(
                    supervisor,
                    [
                        SystemMessage(content=SUPERVISOR_PROMPT),
                        HumanMessage(content=case["query"]),
                    ],
                    args.timeout,
                )
                actual_agent = decision.next_agent
                actual_intent = decision.intent
                bounded_pass = True
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
            records.append({
                **case,
                "suite": "routing",
                "variant": "llm_supervisor",
                "repetition": repetition,
                "actual_agent": actual_agent,
                "actual_intent": actual_intent,
                "agent_correct": actual_agent == case["expected_agent"],
                "intent_correct": actual_intent == case["expected_intent"],
                "bounded_pass": bounded_pass,
                "latency_ms": round(latency_ms, 3),
                "error": error,
            })
            print(
                f"[routing r{repetition} {index}/{len(selected)}] "
                f"agent={'PASS' if actual_agent == case['expected_agent'] else 'FAIL'} "
                f"intent={'PASS' if actual_intent == case['expected_intent'] else 'FAIL'}"
            )
            if args.delay and not (repetition == args.repetitions and index == len(selected)):
                await asyncio.sleep(args.delay)
    return records


def get_tools() -> tuple[dict[str, Any], list[Any]]:
    from app.tools.academic_program import (
        mon_chung_giua_nganh, so_sanh_nganh, tim_nganh, tim_nganh_co_mon,
        tra_cuu_nganh, xem_chuoi_tien_quyet,
    )
    from app.tools.scholarship import tinh_tien_hoc_bong
    from app.tools.tuition import tinh_toan_hoc_phi
    from app.tools.tuition_graph import (
        tra_cuu_co_so_mien_giam_graph, tra_cuu_hoc_phi_graph,
        tra_cuu_quy_dinh_hoc_phi,
    )
    tools = {
        "tra_cuu_nganh": tra_cuu_nganh,
        "so_sanh_nganh": so_sanh_nganh,
        "tim_nganh": tim_nganh,
        "xem_chuoi_tien_quyet": xem_chuoi_tien_quyet,
        "mon_chung_giua_nganh": mon_chung_giua_nganh,
        "tim_nganh_co_mon": tim_nganh_co_mon,
        "tra_cuu_hoc_phi_graph": tra_cuu_hoc_phi_graph,
        "tra_cuu_co_so_mien_giam_graph": tra_cuu_co_so_mien_giam_graph,
        "tra_cuu_quy_dinh_hoc_phi": tra_cuu_quy_dinh_hoc_phi,
        "tinh_tien_hoc_bong": tinh_tien_hoc_bong,
        "tinh_toan_hoc_phi": tinh_toan_hoc_phi,
    }
    return tools, list(tools.values())


def initialize_production_tool_services() -> None:
    """Inject the same shared Graph/catalog services used by app.main."""
    from app.services.graph_service import AcademicGraphService
    from app.services.tuition_catalog import TuitionRateCatalog
    from app.tools.academic_program import set_graph_service
    from app.tools.tuition_graph import set_tuition_catalog, set_tuition_graph_service

    service = AcademicGraphService(
        uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
        user=os.environ.get("NEO4J_USER", "neo4j"),
        password=os.environ.get("NEO4J_PASSWORD", "password"),
    )
    service.ensure_data_loaded()
    set_graph_service(service)
    set_tuition_graph_service(service)
    set_tuition_catalog(TuitionRateCatalog.load())


SPECIALIST_TOOLS = {
    "academic": ["tra_cuu_nganh", "so_sanh_nganh", "tim_nganh", "xem_chuoi_tien_quyet", "mon_chung_giua_nganh", "tim_nganh_co_mon"],
    "financial": ["tra_cuu_hoc_phi_graph", "tra_cuu_co_so_mien_giam_graph", "tra_cuu_quy_dinh_hoc_phi", "tinh_toan_hoc_phi"],
    "scholarship": ["tinh_tien_hoc_bong"],
    "general": [],
}


def evaluate_tool_result(
    case: dict[str, Any], selected_tool: str | None, selected_args: dict[str, Any], output: str
) -> dict[str, bool]:
    selection_passed = selected_tool == case.get("expected_tool")
    arguments_passed = selection_passed and arguments_match(case.get("expected_args", {}), selected_args)
    folded = output.casefold()
    result_passed = all(
        token.casefold() in folded for token in case.get("expected_contains", [])
    ) and all(
        token.casefold() not in folded for token in case.get("expected_not_contains", [])
    )
    return {
        "selection_passed": selection_passed,
        "arguments_passed": arguments_passed,
        "result_passed": result_passed,
        "passed": selection_passed and arguments_passed and result_passed,
    }


async def invoke_tool_gate(
    runnable: Any, query: str, timeout: float
) -> tuple[str | None, dict[str, Any], str, int, float]:
    from langchain_core.messages import HumanMessage, SystemMessage

    response, latency_ms = await bounded_ainvoke(
        runnable,
        [SystemMessage(content=TOOL_GATE_PROMPT), HumanMessage(content=query)],
        timeout,
    )
    calls = response.tool_calls or []
    first = calls[0] if calls else None
    selected_tool = first.get("name") if first else None
    selected_args = first.get("args", {}) if first else {}
    return selected_tool, selected_args, parse_content(response.content), len(calls), latency_ms


async def run_tool_suite(
    cases: list[dict[str, Any]], llm: Any, args: argparse.Namespace
) -> list[dict[str, Any]]:
    tools_by_name, _ = get_tools()
    selected = cases[: args.limit] if args.limit else cases
    records: list[dict[str, Any]] = []

    for repetition in range(1, args.repetitions + 1):
        for index, case in enumerate(selected, start=1):
            error = ""
            selected_tool: str | None = None
            selected_args: dict[str, Any] = {}
            output = ""
            call_count = 0
            latency_ms = 0.0
            bounded_pass = False
            graph_backend = "not_applicable"
            try:
                allowed_names = SPECIALIST_TOOLS.get(case.get("agent"), [])
                gate = llm.bind_tools([tools_by_name[name] for name in allowed_names])
                selected_tool, selected_args, output, call_count, latency_ms = await invoke_tool_gate(
                    gate, case["query"], args.timeout
                )
                tool = tools_by_name.get(selected_tool or "")
                if tool is not None:
                    output = tool.invoke(selected_args)
                if case["function"] in {"tra_cuu_hoc_phi_graph", "tra_cuu_co_so_mien_giam_graph", "tra_cuu_quy_dinh_hoc_phi"}:
                    graph_backend = "graph" if "GRAPH" in output.upper() else "fallback_or_empty"
                bounded_pass = call_count <= args.max_tool_calls
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
            checks = evaluate_tool_result(case, selected_tool, selected_args, output)
            records.append({
                **case,
                "suite": "tools",
                "variant": "llm_tool_call" if case["function"] != "no_tool" else "no_tool_gate",
                "repetition": repetition,
                "selected_tool": selected_tool,
                "selected_args": selected_args,
                "tool_call_count": call_count,
                "output": output,
                "graph_backend": graph_backend,
                **checks,
                "bounded_pass": bounded_pass and not error,
                "latency_ms": round(latency_ms, 3),
                "error": error,
            })
            print(
                f"[tools r{repetition} {index}/{len(selected)}] "
                f"{'PASS' if checks['passed'] and not error else 'FAIL'} {case['function']}"
            )
            if args.delay:
                await asyncio.sleep(args.delay)
    return records


async def run_robustness_suite(
    cases: list[dict[str, Any]], llm: Any, args: argparse.Namespace
) -> list[dict[str, Any]]:
    from langchain_core.messages import HumanMessage, SystemMessage
    from app.agents.graph import RouteDecision
    from app.agents.prompts import SUPERVISOR_PROMPT

    tools_by_name, _ = get_tools()
    supervisor = llm.with_structured_output(RouteDecision)
    selected = cases[: args.limit] if args.limit else cases
    records: list[dict[str, Any]] = []

    for repetition in range(1, args.repetitions + 1):
        for index, case in enumerate(selected, start=1):
            error_parts: list[str] = []
            actual_agent = "error"
            actual_intent = "error"
            selected_tool: str | None = None
            selected_args: dict[str, Any] = {}
            output = ""
            response_text = ""
            call_count = 0
            total_latency = 0.0
            route_bounded = False
            gate_bounded = False

            try:
                decision, route_latency = await bounded_ainvoke(
                    supervisor,
                    [
                        SystemMessage(content=SUPERVISOR_PROMPT),
                        HumanMessage(content=case["query"]),
                    ],
                    args.timeout,
                )
                total_latency += route_latency
                actual_agent = decision.next_agent
                actual_intent = decision.intent
                route_bounded = True
            except Exception as exc:
                error_parts.append(f"route={type(exc).__name__}: {exc}")

            try:
                allowed_names = SPECIALIST_TOOLS.get(case.get("expected_agent"), [])
                gate = llm.bind_tools([tools_by_name[name] for name in allowed_names])
                selected_tool, selected_args, response_text, call_count, gate_latency = await invoke_tool_gate(gate, case["query"], args.timeout)
                total_latency += gate_latency
                tool = tools_by_name.get(selected_tool or "")
                if tool is not None:
                    output = tool.invoke(selected_args)
                else:
                    output = response_text
                gate_bounded = call_count <= args.max_tool_calls
            except Exception as exc:
                error_parts.append(f"tool_gate={type(exc).__name__}: {exc}")

            agent_correct = actual_agent == case["expected_agent"]
            intent_correct = actual_intent == case["expected_intent"]
            tool_decision_correct = selected_tool == case.get("expected_tool")
            args_correct = tool_decision_correct and arguments_match(
                case.get("expected_args", {}), selected_args
            )
            folded = output.casefold()
            expected_contains = case.get("expected_contains", [])
            expected_response_any = case.get("expected_response_any", [])
            result_correct = (
                all(token.casefold() in folded for token in expected_contains)
                if expected_contains
                else any(token.casefold() in folded for token in expected_response_any)
            )
            bounded_pass = route_bounded and gate_bounded and not error_parts
            passed = (
                agent_correct
                and intent_correct
                and tool_decision_correct
                and args_correct
                and result_correct
                and bounded_pass
            )
            records.append({
                **case,
                "suite": "robustness",
                "variant": "llm_supervisor_and_tool_gate",
                "repetition": repetition,
                "actual_agent": actual_agent,
                "actual_intent": actual_intent,
                "selected_tool": selected_tool,
                "selected_args": selected_args,
                "tool_call_count": call_count,
                "output": output,
                "agent_correct": agent_correct,
                "intent_correct": intent_correct,
                "tool_decision_correct": tool_decision_correct,
                "arguments_passed": args_correct,
                "result_passed": result_correct,
                "bounded_pass": bounded_pass,
                "passed": passed,
                "latency_ms": round(total_latency, 3),
                "error": "; ".join(error_parts),
            })
            print(
                f"[robustness r{repetition} {index}/{len(selected)}] "
                f"{'PASS' if passed else 'FAIL'} {case['id']} {case['failure_mode']}"
            )
            if args.delay:
                await asyncio.sleep(args.delay)
    return records


def macro_f1(records: list[dict[str, Any]]) -> float:
    labels = sorted({r["expected_agent"] for r in records} | {r["actual_agent"] for r in records})
    scores = []
    for label in labels:
        tp = sum(r["expected_agent"] == label and r["actual_agent"] == label for r in records)
        fp = sum(r["expected_agent"] != label and r["actual_agent"] == label for r in records)
        fn = sum(r["expected_agent"] == label and r["actual_agent"] != label for r in records)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return statistics.mean(scores) if scores else 0.0


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    routing = [record for record in records if record["suite"] == "routing"]
    routing_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in routing:
        routing_groups[record["variant"]].append(record)
    summary["routing"] = {}
    for variant, items in routing_groups.items():
        latencies = [float(item["latency_ms"]) for item in items]
        summary["routing"][variant] = {
            "n": len(items),
            "agent_accuracy": sum(item["agent_correct"] for item in items) / len(items),
            "macro_f1": macro_f1(items),
            "intent_accuracy": sum(item["intent_correct"] for item in items) / len(items),
            "bounded_completion_rate": sum(item["bounded_pass"] for item in items) / len(items),
            "latency_p50_ms": round(percentile(latencies, 0.50), 3),
            "latency_p95_ms": round(percentile(latencies, 0.95), 3),
        }

    tools = [record for record in records if record["suite"] == "tools"]
    summary["tools"] = {}
    tool_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in tools:
        tool_groups[record["function"]].append(record)
    for function, items in tool_groups.items():
        item_summary = {
            "n": len(items),
            "selection_accuracy": sum(item["selection_passed"] for item in items) / len(items),
            "argument_exact_match": sum(item["arguments_passed"] for item in items) / len(items),
            "result_accuracy": sum(item["result_passed"] for item in items) / len(items),
            "end_to_end_pass_rate": sum(item["passed"] and not item["error"] for item in items) / len(items),
            "bounded_completion_rate": sum(item["bounded_pass"] for item in items) / len(items),
        }
        graph_items = [item for item in items if item.get("graph_backend") != "not_applicable"]
        if graph_items:
            item_summary["graph_hit_rate"] = sum(item.get("graph_backend") == "graph" for item in graph_items) / len(graph_items)
            item_summary["graph_fallback_or_empty_rate"] = sum(item.get("graph_backend") != "graph" for item in graph_items) / len(graph_items)
        summary["tools"][function] = item_summary

    robustness = [record for record in records if record["suite"] == "robustness"]
    if robustness:
        summary["robustness"] = {
            "n": len(robustness),
            "agent_accuracy": sum(item["agent_correct"] for item in robustness) / len(robustness),
            "intent_accuracy": sum(item["intent_correct"] for item in robustness) / len(robustness),
            "tool_decision_accuracy": sum(item["tool_decision_correct"] for item in robustness) / len(robustness),
            "result_accuracy": sum(item["result_passed"] for item in robustness) / len(robustness),
            "bounded_completion_rate": sum(item["bounded_pass"] for item in robustness) / len(robustness),
            "end_to_end_pass_rate": sum(item["passed"] for item in robustness) / len(robustness),
        }
    return summary


def percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_report(summary: dict[str, Any], manifest: dict[str, Any]) -> str:
    lines = [
        "# Scenario 3 Experiment Results",
        "",
        f"- Model: `{manifest['model']}`",
        f"- Backend: `{manifest['backend']}`",
        f"- Repetitions: `{manifest['repetitions']}`",
        f"- Timeout per LLM decision: `{manifest['timeout_seconds']} s`",
        f"- Maximum tool calls per decision: `{manifest['max_tool_calls']}`",
        "",
        "## Routing and specialist selection",
        "",
        "| Variant | N | Agent accuracy | Macro-F1 | Intent accuracy | Bounded | p50 (ms) | p95 (ms) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant, item in summary.get("routing", {}).items():
        lines.append(
            f"| {variant} | {item['n']} | {percent(item['agent_accuracy'])} | "
            f"{percent(item['macro_f1'])} | {percent(item['intent_accuracy'])} | "
            f"{percent(item['bounded_completion_rate'])} | {item['latency_p50_ms']:.1f} | "
            f"{item['latency_p95_ms']:.1f} |"
        )
    lines += [
        "",
        "## Tool reliability",
        "",
        "| Function | N | Selection/path | Argument EM | Result | End-to-end | Bounded | Graph hit |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for function, item in summary.get("tools", {}).items():
        lines.append(
            f"| {function} | {item['n']} | {percent(item['selection_accuracy'])} | "
            f"{percent(item['argument_exact_match'])} | {percent(item['result_accuracy'])} | "
            f"{percent(item['end_to_end_pass_rate'])} | {percent(item['bounded_completion_rate'])} | "
            f"{percent(item['graph_hit_rate']) if 'graph_hit_rate' in item else 'n/a'} |"
        )
    robust = summary.get("robustness")
    if robust:
        lines += [
            "",
            "## Robustness and bounded failure handling",
            "",
            "| N | Agent accuracy | Intent accuracy | Tool/no-tool decision | Result behavior | Bounded | End-to-end |",
            "|---:|---:|---:|---:|---:|---:|---:|",
            f"| {robust['n']} | {percent(robust['agent_accuracy'])} | "
            f"{percent(robust['intent_accuracy'])} | {percent(robust['tool_decision_accuracy'])} | "
            f"{percent(robust['result_accuracy'])} | {percent(robust['bounded_completion_rate'])} | "
            f"{percent(robust['end_to_end_pass_rate'])} |",
        ]
    lines += [
        "",
        "> Graph-backed cases record `graph_backend` separately; `fallback_or_empty` is not counted as a Graph hit.",
        "",
    ]
    return "\n".join(lines)


def create_output_dir(root: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = root / timestamp
    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir


async def async_main(args: argparse.Namespace) -> int:
    validation = validate_datasets(args)
    if args.validate_only:
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 0

    llm, project = create_llm(args)
    routing_cases = load_routing_cases(args.routing_dataset, args.routing_labels)
    tool_cases = load_json_cases(args.tool_dataset)
    robustness_cases = load_json_cases(args.robustness_dataset)
    if args.suite in {"tools", "robustness", "all"}:
        initialize_production_tool_services()
    if args.dry_run:
        args.limit = 3
        args.repetitions = 1

    output_dir = create_output_dir(args.output_root)
    backend = "vertex_ai_service_account" if args.credentials.exists() else "gemini_api"
    manifest = {
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "suite": args.suite,
        "model": args.model,
        "backend": backend,
        "project": project,
        "location": args.location if project else None,
        "repetitions": args.repetitions,
        "timeout_seconds": args.timeout,
        "max_tool_calls": args.max_tool_calls,
        "max_retries": args.max_retries,
        "delay_seconds": args.delay,
        "dataset_validation": validation,
        "dataset_sha256": {
            "routing": sha256_file(args.routing_dataset),
            "routing_labels": sha256_file(args.routing_labels),
            "tools": sha256_file(args.tool_dataset),
            "robustness": sha256_file(args.robustness_dataset),
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    records: list[dict[str, Any]] = []
    try:
        if args.suite in {"routing", "all"}:
            records.extend(await run_routing_suite(routing_cases, llm, args))
        if args.suite in {"tools", "all"}:
            records.extend(await run_tool_suite(tool_cases, llm, args))
        if args.suite in {"robustness", "all"}:
            records.extend(await run_robustness_suite(robustness_cases, llm, args))

        with (output_dir / "records.jsonl").open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        summary = summarize_records(records)
        (output_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (output_dir / "report.md").write_text(
            render_report(summary, manifest), encoding="utf-8"
        )
        manifest["status"] = "completed"
        manifest["record_count"] = len(records)
    except BaseException as exc:
        manifest["status"] = "failed"
        manifest["error_type"] = type(exc).__name__
        raise
    finally:
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(f"Scenario 3 results: {output_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("routing", "tools", "robustness", "all"), default="all")
    parser.add_argument("--routing-dataset", type=Path, default=DEFAULT_ROUTING_DATASET)
    parser.add_argument("--routing-labels", type=Path, default=DEFAULT_ROUTING_LABELS)
    parser.add_argument("--tool-dataset", type=Path, default=DEFAULT_TOOL_DATASET)
    parser.add_argument("--robustness-dataset", type=Path, default=DEFAULT_ROBUSTNESS_DATASET)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    parser.add_argument("--project", default=None)
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--max-tool-calls", type=int, default=1)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--limit", type=int, default=None, help="Limit cases in each selected suite")
    parser.add_argument("--dry-run", action="store_true", help="Run three cases per suite, one repetition")
    parser.add_argument("--validate-only", action="store_true", help="Validate datasets without calling Gemini")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.repetitions < 1:
        raise SystemExit("--repetitions phải >= 1")
    if args.timeout <= 0:
        raise SystemExit("--timeout phải > 0")
    if args.max_tool_calls < 1:
        raise SystemExit("--max-tool-calls phải >= 1")
    return asyncio.run(async_main(args))


if __name__ == "__main__":
    raise SystemExit(main())
