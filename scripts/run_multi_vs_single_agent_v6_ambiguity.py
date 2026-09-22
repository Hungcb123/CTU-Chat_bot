#!/usr/bin/env python3
"""Scenario 3 v6: scalability under intra-domain tool ambiguity.

The locked protocol compares a full-registry monolithic agent, a global
Top-k single-agent, a supervisor-routed generic gate, and a supervisor-routed
specialist gate. Semantic-neighbor density grows from zero to four added
neighbors per production tool family. Route decisions are shared across the
two routed arms and all density levels so the primary downstream comparison
is not confounded by different supervisor samples.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from pydantic import Field, create_model

from app.services.evaluation_contract import validate_unique_case_ids
from app.services.orchestration_contract import repair_route_decision
from scripts.run_multi_vs_single_agent_experiment import (
    DEFAULT_CREDENTIALS,
    DEFAULT_MODEL,
    SPECIALIST_TOOLS,
    bounded_ainvoke,
    get_llm,
    get_tools,
    initialize_services,
    normalize_tool_name,
    setup_vertex_environment,
    sha256_file,
)
from scripts.run_multi_vs_single_agent_v3_scalability import (
    build_oracles,
    call_with_backoff,
    make_case_key,
    score_case,
)
from scripts.run_multi_vs_single_agent_v4_scalability import (
    ORDER_BLOCKS,
    counterbalanced_tools,
    expected_position,
    schema_chars,
)
from scripts.run_multi_vs_single_agent_v5_scalability import (
    bm25_shortlist,
    extract_usage,
    validate_args,
)

PROTOCOL_VERSION = "multi-vs-single-v6.0"
ARCHITECTURES = ("single_full", "single_topk", "routed_generic", "routed_specialist")
LEVELS = (0, 2, 4)
DEFAULT_DATASET = ROOT / "data" / "scenario3_production_tools.json"
DEFAULT_REGISTRY = ROOT / "data" / "scenario3_semantic_neighbor_registry_v6.json"
DEFAULT_OUTPUT_ROOT = ROOT / "logs" / "multi_vs_single_v6"

GENERIC_GATE_PROMPT = """Bạn là cổng chọn công cụ của chatbot sinh viên CTU.
Chọn tối đa MỘT công cụ dựa trên ý định cụ thể của câu hỏi và hợp đồng công cụ.
Không chọn chỉ vì tên công cụ có từ khóa giống câu hỏi. Chỉ gọi khi đủ tham số
bắt buộc, không tự bịa giá trị còn thiếu, và không gọi công cụ ngoài phạm vi."""

DISTILLED_SUPERVISOR_PROMPT = """Bạn là Supervisor Agent của chatbot Trường Đại học Cần Thơ (CTU).
Nhiệm vụ: Phân tích câu hỏi người dùng và chọn chính xác:
1. next_agent (chọn 1 trong 4):
- academic: Chương trình đào tạo, cấu trúc ngành học, danh sách môn, số tín chỉ, môn tiên quyết, so sánh ngành, tìm ngành theo tiêu chí (điểm chuẩn, học phí), chuẩn đầu ra ngành, lớp học phần mở môn, giảng viên dạy môn.
- financial: Mọi vấn đề về học phí (mức học phí thực tế, mức trần cơ sở miễn giảm, đối tượng chính sách miễn giảm, tính số tiền phải đóng sau miễn giảm, quy định hoàn học phí khi rút môn, phạt chậm đóng học phí).
- scholarship: Học bổng khuyến khích học tập (KKHT theo GPA/ĐRL), học bổng doanh nghiệp/tài trợ ngoài trường.
- general: Vay vốn sinh viên, trợ cấp xã hội, SV sư phạm (NĐ 116), quy chế học vụ chung (điều kiện tốt nghiệp, bảo lưu, thôi học, chuyển ngành, điểm I, điểm M, hoãn thi, thi lại), Sinh viên 5 tốt, KTX, điểm rèn luyện, đời sống SV.

2. intent:
- academic_program (nếu academic)
- actual_tuition / exemption_basis / exemption_policy / calculation / both / ambiguous_tuition (nếu financial)
- scholarship (nếu scholarship)
- student_loan / social_support / academic_rules / other (nếu general)
"""

BASE_POLICIES: dict[str, tuple[str, str]] = {
    "tra_cuu_nganh": ("thông tin tổng quan một chương trình, tín chỉ hoặc văn bằng", "tuyển sinh, học phí, chuẩn đầu ra riêng lẻ hoặc việc làm"),
    "so_sanh_nganh": ("so sánh tổng thể hai chương trình đào tạo", "chỉ so sánh điểm chuẩn, học phí, chuẩn đầu ra hoặc việc làm"),
    "tim_nganh": ("tìm danh sách ngành theo từ khóa hay lĩnh vực", "tìm theo điểm chuẩn, học phí, khoa quản lý hoặc nghề cụ thể"),
    "xem_chuoi_tien_quyet": ("toàn bộ chuỗi môn phải hoàn thành trước một môn", "chỉ môn trực tiếp, song hành, tương đương hoặc lộ trình theo học kỳ"),
    "mon_chung_giua_nganh": ("các môn học thực sự trùng giữa hai chương trình", "tổ hợp tuyển sinh, chuẩn đầu ra, chuyển đổi tín chỉ hoặc học kỳ tương tự"),
    "tim_nganh_co_mon": ("ngành đào tạo nào chứa chính xác một môn", "lớp học phần, giảng viên, môn tương đương hoặc chuyên ngành hẹp"),
    "tra_cuu_hoc_phi_graph": ("mức học phí thực tế hiện hành theo ngành và khóa", "tổng hóa đơn, lịch sử, phụ thu hoặc học lại"),
    "tra_cuu_co_so_mien_giam_graph": ("mức trần tiền làm cơ sở tính miễn giảm", "đối tượng, tỷ lệ, hồ sơ hoặc lịch sử nhiều năm"),
    "tra_cuu_quy_dinh_hoc_phi": ("quy định mức thu hoặc hệ số theo loại hình đào tạo", "hạn đóng, hoàn tiền, phạt chậm đóng hoặc trả góp"),
    "tinh_toan_hoc_phi": ("số tiền còn đóng sau miễn giảm với đủ ba đại lượng", "tổng theo tín chỉ, tiền phạt, tiền hoàn hoặc chia đợt"),
    "tinh_tien_hoc_bong": ("tính loại và số tiền học bổng từ GPA và điểm rèn luyện", "học phí hoặc chương trình đào tạo"),
}


def load_registry(path: Path) -> list[dict[str, Any]]:
    registry = json.loads(path.read_text(encoding="utf-8"))
    if len(registry) != 40:
        raise ValueError(f"v6 requires exactly 40 semantic neighbors, got {len(registry)}")
    names = [item["name"] for item in registry]
    if len(names) != len(set(names)):
        raise ValueError("Semantic-neighbor names must be unique")
    families = Counter(item["target_family"] for item in registry)
    expected = set(BASE_POLICIES) - {"tinh_tien_hoc_bong"}
    if set(families) != expected or any(value != 4 for value in families.values()):
        raise ValueError(f"Expected four neighbors for each of ten families, got {families}")
    for item in registry:
        if item["level"] not in (1, 2, 3, 4):
            raise ValueError(f"Invalid neighbor level for {item['name']}")
        text = f"{item['description']} {item['use_when']} {item['avoid_when']}".casefold()
        if any(term in text for term in ("synthetic", "distractor", "benchmark", "giả lập")):
            raise ValueError(f"{item['name']} discloses its evaluation role")
    return registry


def build_neighbor_tools(registry: list[dict[str, Any]], level: int) -> dict[str, list[StructuredTool]]:
    if level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}")
    result = {domain: [] for domain in ("academic", "financial", "scholarship", "general")}
    type_mapping = {"string": (str, ...), "integer": (int, ...), "number": (float, ...), "boolean": (bool, ...)}
    for item in registry:
        if int(item["level"]) > level:
            continue
        fields = {}
        for name, spec in item.get("parameters", {}).items():
            py_type, default = type_mapping.get(spec.get("type", "string"), (str, ...))
            fields[name] = (py_type, Field(default, description=spec.get("description", "")))
        schema = create_model(f"{item['name']}_v6_schema", **fields)
        output = item["deterministic_output"]

        def handler_factory(value: str):
            def handler(**_: Any) -> str:
                return value
            return handler

        result[item["domain"]].append(StructuredTool.from_function(
            func=handler_factory(output),
            name=item["name"],
            description=item["description"],
            args_schema=schema,
        ))
    return result


def coverage_cases(registry: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cases = []
    for index, item in enumerate(registry, 1):
        cases.append({
            "id": f"AMB-{index:02d}",
            "agent": item["domain"],
            "function": item["name"],
            "query": item["coverage_query"],
            "expected_tool": item["name"],
            "expected_args": item["coverage_args"],
            "expected_contains": [item["deterministic_output"]],
            "test_focus": "semantic_neighbor_coverage",
            "benchmark_partition": "coverage",
        })
    return cases


def specialist_prompt(visible_tools: list[Any], policy_by_name: dict[str, tuple[str, str]]) -> str:
    lines = [GENERIC_GATE_PROMPT, "\nQuy tắc phân biệt chức năng trong miền này:"]
    for tool in visible_tools:
        use_when, avoid_when = policy_by_name.get(tool.name, (getattr(tool, "description", ""), "các mục đích khác"))
        lines.append(f"- {tool.name}: dùng khi {use_when}; không dùng khi {avoid_when}.")
    return "\n".join(lines)


async def invoke_gate(runnable: Any, query: str, prompt: str, timeout: float) -> tuple[str | None, dict[str, Any], str, int, float, dict[str, int]]:
    response, latency_ms = await bounded_ainvoke(
        runnable,
        [SystemMessage(content=prompt), HumanMessage(content=query)],
        timeout,
    )
    calls = response.tool_calls or []
    first = calls[0] if calls else None
    selected_tool = normalize_tool_name(first.get("name")) if first else None
    selected_args = first.get("args", {}) if first else {}
    content = response.content if isinstance(response.content, str) else str(response.content or "")
    return selected_tool, selected_args, content, len(calls), latency_ms, extract_usage(response)


async def obtain_route(case: dict[str, Any], supervisor: Any, timeout: float, retries: int, semaphore: asyncio.Semaphore) -> dict[str, Any]:
    try:
        async def route_once() -> Any:
            async with semaphore:
                return await bounded_ainvoke(
                    supervisor,
                    [SystemMessage(content=DISTILLED_SUPERVISOR_PROMPT), HumanMessage(content=case["query"])],
                    timeout,
                )
        (payload, latency), attempts = await call_with_backoff(route_once, retries=retries)
        parsed = payload.get("parsed")
        raw = payload.get("raw")
        if parsed is None:
            raise ValueError(f"Structured route parsing failed: {payload.get('parsing_error')}")
        repaired = repair_route_decision(case["query"], parsed.next_agent, parsed.intent)
        return {
            "actual_agent": repaired.agent,
            "actual_intent": repaired.intent.value,
            "raw_agent": parsed.next_agent,
            "route_repair_reason": repaired.reason,
            "route_latency_ms": latency,
            "route_usage": extract_usage(raw),
            "route_attempts": attempts,
            "route_error": "",
        }
    except Exception as exc:
        return {
            "actual_agent": None,
            "actual_intent": None,
            "raw_agent": None,
            "route_repair_reason": None,
            "route_latency_ms": 0.0,
            "route_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "route_attempts": retries,
            "route_error": f"{type(exc).__name__}: {exc}",
        }


async def evaluate_one(
    *, architecture: str, partition: str, case_key: str, case: dict[str, Any],
    repetition: int, level: int, llm: Any, route: dict[str, Any] | None,
    all_tools: list[Any], domain_tools: dict[str, list[Any]], tools_by_name: dict[str, Any],
    policy_by_name: dict[str, tuple[str, str]], oracles: dict[str, str], top_k: int,
    timeout: float, retries: int, semaphore: asyncio.Semaphore, seed: int,
) -> dict[str, Any]:
    routed = architecture.startswith("routed_")
    route_data = route if routed and route is not None else {
        "actual_agent": None, "actual_intent": None, "raw_agent": None,
        "route_repair_reason": None, "route_latency_ms": 0.0,
        "route_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        "route_attempts": 0, "route_error": "",
    }
    error_parts = [f"route={route_data['route_error']}"] if route_data["route_error"] else []
    retrieval_latency = gate_latency = tool_latency = 0.0
    retrieval_candidates: list[Any] = []
    retrieval_scores: dict[str, float] = {}

    if architecture == "single_full":
        visible_tools = counterbalanced_tools(all_tools, expected_tool=case["expected_tool"], case_key=case_key, order_block=repetition, seed=seed)
    else:
        source_tools = all_tools if architecture == "single_topk" else domain_tools.get(route_data["actual_agent"] or "", [])
        started = time.perf_counter()
        retrieval_candidates, retrieval_scores = bm25_shortlist(case["query"], source_tools, top_k)
        retrieval_latency = (time.perf_counter() - started) * 1000
        visible_tools = counterbalanced_tools(retrieval_candidates, expected_tool=case["expected_tool"], case_key=case_key, order_block=repetition, seed=seed)

    prompt = specialist_prompt(visible_tools, policy_by_name) if architecture == "routed_specialist" else GENERIC_GATE_PROMPT
    selected_tool = None
    selected_args: dict[str, Any] = {}
    output = ""
    tool_calls = gate_attempts = 0
    gate_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    schema_valid, schema_error = True, ""
    gate_bounded = False
    try:
        runnable = llm.bind_tools(visible_tools)

        async def gate_once() -> Any:
            async with semaphore:
                return await invoke_gate(runnable, case["query"], prompt, timeout)

        gate_result, gate_attempts = await call_with_backoff(gate_once, retries=retries)
        selected_tool, selected_args, response_text, tool_calls, gate_latency, gate_usage = gate_result
        tool = tools_by_name.get(selected_tool or "")
        if tool is not None:
            schema_valid, schema_error = validate_args(tool, selected_args)
            if schema_valid:
                started = time.perf_counter()
                output = str(await asyncio.to_thread(tool.invoke, selected_args))
                tool_latency = (time.perf_counter() - started) * 1000
            else:
                output = "Yêu cầu công cụ không hợp lệ; hệ thống không thực thi công cụ."
        else:
            output = response_text
        gate_bounded = tool_calls <= 1
    except Exception as exc:
        schema_valid = False
        error_parts.append(f"gate={type(exc).__name__}: {exc}")

    bounded_pass = (not routed or not route_data["route_error"]) and gate_bounded and not error_parts
    checks = score_case(case, selected_tool, selected_args, output, bounded_pass, oracles)
    visible_names = [tool.name for tool in visible_tools]
    position, normalized = expected_position(visible_names, case["expected_tool"])
    route_usage = route_data["route_usage"]
    return {
        "protocol": PROTOCOL_VERSION,
        "partition": partition,
        "ambiguity_level": level,
        "registry_size": 11 + 10 * level,
        "architecture": architecture,
        "case_key": case_key,
        "case_id": case["id"],
        "repetition": repetition,
        "order_block": ORDER_BLOCKS[repetition - 1],
        "query": case["query"],
        "expected_agent": case["agent"],
        "actual_agent": route_data["actual_agent"],
        "raw_agent": route_data["raw_agent"],
        "actual_intent": route_data["actual_intent"],
        "route_repair_reason": route_data["route_repair_reason"],
        "agent_correct": route_data["actual_agent"] == case["agent"] if routed else None,
        "expected_tool": case["expected_tool"],
        "selected_tool": selected_tool,
        "expected_args": case["expected_args"],
        "selected_args": selected_args,
        "visible_tool_count": len(visible_tools),
        "visible_tool_schema_chars": schema_chars(visible_tools),
        "visible_tool_names": visible_names,
        "expected_tool_position": position,
        "expected_tool_position_normalized": normalized,
        "retrieval_candidate_names": [tool.name for tool in retrieval_candidates],
        "retrieval_scores": {name: round(score, 6) for name, score in retrieval_scores.items()},
        "gold_in_candidates": case["expected_tool"] in {tool.name for tool in retrieval_candidates} if architecture != "single_full" else None,
        "schema_guard_passed": schema_valid,
        "schema_guard_error": schema_error,
        "tool_call_count": tool_calls,
        "route_attempts": route_data["route_attempts"],
        "gate_attempts": gate_attempts,
        "route_latency_ms": round(route_data["route_latency_ms"], 2),
        "tool_retrieval_latency_ms": round(retrieval_latency, 4),
        "gate_latency_ms": round(gate_latency, 2),
        "tool_latency_ms": round(tool_latency, 2),
        "total_decision_latency_ms": round(route_data["route_latency_ms"] + retrieval_latency + gate_latency, 2),
        "route_usage": route_usage,
        "gate_usage": gate_usage,
        "total_input_tokens": route_usage["input_tokens"] + gate_usage["input_tokens"],
        "total_output_tokens": route_usage["output_tokens"] + gate_usage["output_tokens"],
        "total_tokens": route_usage["total_tokens"] + gate_usage["total_tokens"],
        "output": output[:500],
        **checks,
        "bounded_pass": bounded_pass,
        "error": "; ".join(error_parts),
    }


async def execute_run(args: argparse.Namespace, run_dir: Path, primary: list[dict[str, Any]], coverage: list[dict[str, Any]], registry: list[dict[str, Any]]) -> None:
    from app.agents.graph import RouteDecision

    setup_vertex_environment(args.credentials)
    os.environ["VERTEX_LOCATION"] = args.location
    os.environ["GOOGLE_CLOUD_REGION"] = args.location
    initialize_services()
    base_tools, real_tools = get_tools()
    llm = get_llm(model=args.model, temperature=0.0)
    supervisor = llm.with_structured_output(RouteDecision, include_raw=True)
    semaphore = asyncio.Semaphore(args.workers)

    max_neighbors = build_neighbor_tools(registry, 4)
    max_tools = dict(base_tools)
    for tools in max_neighbors.values():
        max_tools.update({tool.name: tool for tool in tools})
    all_cases = primary + coverage
    oracles = build_oracles(all_cases, max_tools)
    policy_by_name = dict(BASE_POLICIES)
    policy_by_name.update({item["name"]: (item["use_when"], item["avoid_when"]) for item in registry})

    route_specs: list[tuple[str, dict[str, Any], int]] = []
    for index, case in enumerate(primary, 1):
        case_key = make_case_key("ambiguity_primary", index, case)
        for repetition in range(1, 4):
            route_specs.append((case_key, case, repetition))
    for index, case in enumerate(coverage, 1):
        route_specs.append((make_case_key("ambiguity_coverage", index, case), case, 1))

    route_cache: dict[tuple[str, int], dict[str, Any]] = {}
    print(f"Collecting {len(route_specs)} shared supervisor decisions.", flush=True)
    for offset in range(0, len(route_specs), args.workers):
        batch = route_specs[offset:offset + args.workers]
        results = await asyncio.gather(*(obtain_route(case, supervisor, args.timeout, args.retries, semaphore) for _, case, _ in batch))
        for (case_key, _, repetition), result in zip(batch, results):
            route_cache[(case_key, repetition)] = result
        print(f"Route progress: {min(offset + len(batch), len(route_specs))}/{len(route_specs)}", flush=True)

    jobs: list[Any] = []
    for level in LEVELS:
        neighbors = build_neighbor_tools(registry, level)
        tools_by_name = dict(base_tools)
        for tools in neighbors.values():
            tools_by_name.update({tool.name: tool for tool in tools})
        all_tools = real_tools + [tool for tools in neighbors.values() for tool in tools]
        domain_tools = {
            domain: [tools_by_name[name] for name in names] + neighbors[domain]
            for domain, names in SPECIALIST_TOOLS.items()
        }
        for index, case in enumerate(primary, 1):
            case_key = make_case_key("ambiguity_primary", index, case)
            for repetition in range(1, 4):
                for architecture in ARCHITECTURES:
                    jobs.append(evaluate_one(
                        architecture=architecture, partition="primary", case_key=case_key, case=case,
                        repetition=repetition, level=level, llm=llm, route=route_cache[(case_key, repetition)],
                        all_tools=all_tools, domain_tools=domain_tools, tools_by_name=tools_by_name,
                        policy_by_name=policy_by_name, oracles=oracles, top_k=args.top_k,
                        timeout=args.timeout, retries=args.retries, semaphore=semaphore, seed=args.seed,
                    ))
        if level == 4:
            for index, case in enumerate(coverage, 1):
                case_key = make_case_key("ambiguity_coverage", index, case)
                for architecture in ARCHITECTURES:
                    jobs.append(evaluate_one(
                        architecture=architecture, partition="coverage", case_key=case_key, case=case,
                        repetition=1, level=level, llm=llm, route=route_cache[(case_key, 1)],
                        all_tools=all_tools, domain_tools=domain_tools, tools_by_name=tools_by_name,
                        policy_by_name=policy_by_name, oracles=oracles, top_k=args.top_k,
                        timeout=args.timeout, retries=args.retries, semaphore=semaphore, seed=args.seed,
                    ))

    random.Random(args.seed).shuffle(jobs)
    records_file = run_dir / "records.jsonl"
    records: list[dict[str, Any]] = []
    print(f"Total evaluation jobs: {len(jobs)}", flush=True)
    for offset in range(0, len(jobs), args.workers):
        batch = jobs[offset:offset + args.workers]
        results = await asyncio.gather(*batch)
        records.extend(results)
        with records_file.open("a", encoding="utf-8") as handle:
            for record in results:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Progress: {len(records)}/{len(jobs)}", flush=True)

    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update({
        "status": "completed",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "actual_records": len(records),
        "error_records": sum(bool(record["error"]) for record in records),
        "schema_guard_failures": sum(not record["schema_guard_passed"] for record in records),
    })
    manifest["hashes"]["records"] = sha256_file(records_file)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Completed {len(records)} records.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--location", default="europe-west1")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--retries", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--seed", type=int, default=20260922)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    production = json.loads(args.dataset.read_text(encoding="utf-8"))
    validate_unique_case_ids(production)
    primary = [dict(case, benchmark_partition="primary") for case in production if case.get("agent") in {"academic", "financial"}]
    registry = load_registry(args.registry)
    coverage = coverage_cases(registry)
    validate_unique_case_ids(coverage)
    expected_records = len(primary) * len(LEVELS) * len(ARCHITECTURES) * 3 + len(coverage) * len(ARCHITECTURES)
    expected_routes = len(primary) * 3 + len(coverage)

    if len(primary) != 50 or expected_records != 1960:
        parser.error(f"Locked v6 design expected 50 primary cases and 1960 records, got {len(primary)} and {expected_records}")
    if args.top_k <= 0:
        parser.error("top_k must be positive")
    if args.validate_only:
        print(f"protocol={PROTOCOL_VERSION}")
        print(f"levels={LEVELS}; registry_sizes={[11 + 10 * level for level in LEVELS]}")
        print(f"architectures={ARCHITECTURES}; top_k={args.top_k}")
        print(f"primary_cases={len(primary)}; coverage_cases={len(coverage)}")
        print(f"shared_route_calls={expected_routes}; expected_records={expected_records}")
        print("Validation PASSED")
        return

    run_dir = args.output_root / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "protocol": PROTOCOL_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "locked_before_execution",
        "hypothesis": "Supervisor-routed specialist gating degrades less than matched single-agent gating as intra-domain semantic-neighbor density increases.",
        "primary_outcome": "Routed-specialist minus single-Top-k selection interaction Delta(high)-Delta(low) on the 50 fixed production cases.",
        "secondary_outcome": "Routed-specialist minus routed-generic selection contrast isolates the contribution of contrastive specialist policy under shared routing.",
        "arms": list(ARCHITECTURES),
        "ambiguity_levels": list(LEVELS),
        "registry_sizes": [11 + 10 * level for level in LEVELS],
        "top_k": args.top_k,
        "primary_cases": len(primary),
        "coverage_cases": len(coverage),
        "repetitions": 3,
        "coverage_repetitions": 1,
        "expected_route_calls": expected_routes,
        "shared_route_policy": "One live supervisor decision per case and order block is replayed across routed arms and ambiguity levels.",
        "expected_records": expected_records,
        "seed": args.seed,
        "temperature": 0.0,
        "model": args.model,
        "location": args.location,
        "hashes": {
            "dataset": sha256_file(args.dataset),
            "semantic_neighbor_registry": sha256_file(args.registry),
            "base_runner_helpers": sha256_file(ROOT / "scripts" / "run_multi_vs_single_agent_experiment.py"),
            "v3_helpers": sha256_file(ROOT / "scripts" / "run_multi_vs_single_agent_v3_scalability.py"),
            "v4_helpers": sha256_file(ROOT / "scripts" / "run_multi_vs_single_agent_v4_scalability.py"),
            "v5_helpers": sha256_file(ROOT / "scripts" / "run_multi_vs_single_agent_v5_scalability.py"),
            "runner": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    asyncio.run(execute_run(args, run_dir, primary, coverage, registry))


if __name__ == "__main__":
    main()
