#!/usr/bin/env python3
"""Scenario 3 v5: static versus dynamically shortlisted tool scalability.

The locked experiment compares three complete decision paths at global
registries of 11, 27, and 51 tools:

1. monolithic single-agent with the full registry;
2. supervisor-routed static multi-agent with all predicted-domain tools;
3. supervisor-routed Top-k multi-agent with a local BM25 shortlist (k=5).

Three deterministic order blocks place an available gold tool first, middle,
and last. A schema guard converts invalid tool arguments into bounded failures
instead of runtime exceptions.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import random
import re
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
    TOOL_GATE_PROMPT,
    bounded_ainvoke,
    get_llm,
    get_tools,
    initialize_services,
    normalize_tool_name,
    setup_vertex_environment,
    sha256_file,
    tool_gate_prompt,
)
from scripts.run_multi_vs_single_agent_v3_scalability import (
    build_oracles,
    call_with_backoff,
    expected_agent,
    expected_intent,
    make_case_key,
    parse_suites,
    score_case,
    stable_json,
)
from scripts.run_multi_vs_single_agent_v4_scalability import (
    ORDER_BLOCKS,
    counterbalanced_tools,
    expected_position,
    schema_chars,
)

PROTOCOL_VERSION = "multi-vs-single-v5.0"
ARCHITECTURES = ("single_agent", "static_multi", "topk_multi")
ALLOWED_LEVELS = (0, 4, 10)
DEFAULT_TOOL_DATASET = ROOT / "data" / "scenario3_production_tools.json"
DEFAULT_ROBUSTNESS_DATASET = ROOT / "data" / "scenario3_robustness_cases.json"
DEFAULT_BASE_DISTRACTORS = ROOT / "data" / "scenario3_distractor_registry_v3.json"
DEFAULT_EXTENSION_DISTRACTORS = ROOT / "data" / "scenario3_distractor_registry_v5_extension.json"
DEFAULT_OUTPUT_ROOT = ROOT / "logs" / "multi_vs_single_v5"

DISCLOSURE_TERMS = ("synthetic", "distractor", "fake", "giả lập", "stress test", "benchmark-only")

# Metadata is derived from production tool contracts, not benchmark case labels.
TOOL_RETRIEVAL_HINTS = {
    "tra_cuu_nganh": "thông tin tổng quan một ngành mã ngành tín chỉ thời gian đào tạo văn bằng chương trình",
    "so_sanh_nganh": "so sánh đối chiếu khác nhau giữa hai ngành chương trình",
    "tim_nganh": "tìm kiếm liệt kê các ngành theo lĩnh vực tiêu chí từ khóa",
    "xem_chuoi_tien_quyet": "chuỗi môn tiên quyết học trước cần học qua thứ tự môn",
    "mon_chung_giua_nganh": "môn học chung giống nhau trùng nhau giữa hai ngành",
    "tim_nganh_co_mon": "ngành nào có chứa một môn học môn xuất hiện trong ngành nào",
    "tra_cuu_hoc_phi_graph": "mức học phí thực tế theo ngành khóa tuyển sinh",
    "tra_cuu_co_so_mien_giam_graph": "mức trần cơ sở tính miễn giảm học phí theo ngành khối khóa",
    "tra_cuu_quy_dinh_hoc_phi": "quy định chung hệ số học phí từ xa vừa làm vừa học thạc sĩ tiến sĩ",
    "tinh_toan_hoc_phi": "tính số tiền còn đóng từ học phí thực tế mức trần phần trăm miễn giảm đủ ba số",
    "tinh_tien_hoc_bong": "tính tiền học bổng khuyến khích từ GPA điểm rèn luyện khối ngành",
}


def parse_levels(raw: str) -> list[int]:
    levels = sorted({int(item.strip()) for item in raw.split(",") if item.strip()})
    if not levels or any(level not in ALLOWED_LEVELS for level in levels):
        raise argparse.ArgumentTypeError(f"levels must be selected from {ALLOWED_LEVELS}")
    return levels


def load_registry(base_path: Path, extension_path: Path) -> list[dict[str, Any]]:
    registry = json.loads(base_path.read_text(encoding="utf-8"))
    registry.extend(json.loads(extension_path.read_text(encoding="utf-8")))
    if len(registry) != 40:
        raise ValueError(f"v5 requires exactly 40 distractors, got {len(registry)}")
    names = [item["name"] for item in registry]
    if len(names) != len(set(names)):
        raise ValueError("Distractor names must be unique")
    domains = Counter(item["domain"] for item in registry)
    if domains != Counter({"academic": 10, "financial": 10, "scholarship": 10, "general": 10}):
        raise ValueError(f"Expected 10 distractors/domain, got {domains}")
    for item in registry:
        description = item.get("description", "").casefold()
        for term in DISCLOSURE_TERMS:
            if term in description:
                raise ValueError(f"{item['name']} discloses benchmark role via '{term}'")
    return registry


def build_distractor_tools(
    registry: list[dict[str, Any]], distractors_per_domain: int
) -> dict[str, list[StructuredTool]]:
    if distractors_per_domain not in ALLOWED_LEVELS:
        raise ValueError(f"Unsupported v5 level: {distractors_per_domain}")
    result = {domain: [] for domain in ("academic", "financial", "scholarship", "general")}
    type_mapping = {
        "string": (str, ...),
        "integer": (int, ...),
        "number": (float, ...),
        "boolean": (bool, ...),
    }
    for item in registry:
        if int(item.get("registry_order", 999)) > distractors_per_domain:
            continue
        fields = {}
        for name, spec in item.get("parameters", {}).items():
            py_type, default = type_mapping.get(spec.get("type", "string"), (str, ...))
            fields[name] = (py_type, Field(default, description=spec.get("description", "")))
        schema = create_model(f"{item['name']}_v5_schema", **fields)
        deterministic_output = item.get("deterministic_output", "OK")

        def handler_factory(value: str):
            def handler(**_: Any) -> str:
                return value
            return handler

        result[item["domain"]].append(
            StructuredTool.from_function(
                func=handler_factory(deterministic_output),
                name=item["name"],
                description=item["description"],
                args_schema=schema,
            )
        )
    return result


def tokenize(text: str) -> list[str]:
    normalized = text.casefold().replace("_", " ")
    tokens = re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)
    return tokens + [f"{a}::{b}" for a, b in zip(tokens, tokens[1:])]


def tool_document(tool: Any) -> list[str]:
    hints = TOOL_RETRIEVAL_HINTS.get(tool.name, "")
    return tokenize(f"{tool.name} {getattr(tool, 'description', '')} {hints}")


def bm25_shortlist(query: str, tools: list[Any], top_k: int) -> tuple[list[Any], dict[str, float]]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if len(tools) <= top_k:
        return list(tools), {tool.name: 0.0 for tool in tools}
    documents = [tool_document(tool) for tool in tools]
    query_terms = tokenize(query)
    document_frequency = Counter()
    for document in documents:
        document_frequency.update(set(document))
    n_docs = len(documents)
    average_length = sum(len(document) for document in documents) / n_docs
    k1, b = 1.5, 0.75
    scores: dict[str, float] = {}
    for tool, document in zip(tools, documents):
        frequencies = Counter(document)
        score = 0.0
        for term in query_terms:
            frequency = frequencies.get(term, 0)
            if not frequency:
                continue
            df = document_frequency[term]
            inverse_frequency = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
            denominator = frequency + k1 * (1.0 - b + b * len(document) / average_length)
            score += inverse_frequency * frequency * (k1 + 1.0) / denominator
        scores[tool.name] = score
    ranked = sorted(tools, key=lambda tool: (-scores[tool.name], tool.name))
    return ranked[:top_k], scores


def extract_usage(message: Any) -> dict[str, int]:
    usage = getattr(message, "usage_metadata", None) or {}
    if not usage:
        usage = (getattr(message, "response_metadata", None) or {}).get("usage_metadata", {})
    return {
        "input_tokens": int(usage.get("input_tokens", usage.get("prompt_token_count", 0)) or 0),
        "output_tokens": int(usage.get("output_tokens", usage.get("candidates_token_count", 0)) or 0),
        "total_tokens": int(usage.get("total_tokens", usage.get("total_token_count", 0)) or 0),
    }


async def invoke_gate(
    runnable: Any, query: str, timeout: float, agent: str | None
) -> tuple[str | None, dict[str, Any], str, int, float, dict[str, int]]:
    response, latency_ms = await bounded_ainvoke(
        runnable,
        [
            SystemMessage(content=tool_gate_prompt(agent) if agent else TOOL_GATE_PROMPT),
            HumanMessage(content=query),
        ],
        timeout,
    )
    calls = response.tool_calls or []
    first = calls[0] if calls else None
    selected_tool = normalize_tool_name(first.get("name")) if first else None
    selected_args = first.get("args", {}) if first else {}
    content = response.content if isinstance(response.content, str) else str(response.content or "")
    return selected_tool, selected_args, content, len(calls), latency_ms, extract_usage(response)


def validate_args(tool: Any, selected_args: dict[str, Any]) -> tuple[bool, str]:
    schema = getattr(tool, "args_schema", None)
    if schema is None:
        return True, ""
    try:
        schema.model_validate(selected_args)
        return True, ""
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


async def evaluate_one(
    *,
    architecture: str,
    suite: str,
    case_key: str,
    case: dict[str, Any],
    repetition: int,
    level: int,
    llm: Any,
    supervisor: Any,
    ordered_single_tools: list[Any],
    ordered_static_tools: dict[str, list[Any]],
    unordered_domain_tools: dict[str, list[Any]],
    tools_by_name: dict[str, Any],
    oracles: dict[str, str],
    top_k: int,
    timeout: float,
    max_tool_calls: int,
    retries: int,
    semaphore: asyncio.Semaphore,
    seed: int,
) -> dict[str, Any]:
    from app.agents.prompts import SUPERVISOR_PROMPT

    target_agent = expected_agent(case, suite)
    target_intent = expected_intent(case, suite)
    actual_agent = raw_agent = actual_intent = route_reason = None
    route_latency = gate_latency = tool_latency = retrieval_latency = 0.0
    route_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    gate_usage = dict(route_usage)
    route_attempts = gate_attempts = tool_calls = 0
    route_bounded = architecture == "single_agent"
    gate_bounded = False
    selected_tool = None
    selected_args: dict[str, Any] = {}
    output = ""
    error_parts: list[str] = []

    if architecture != "single_agent":
        try:
            async def route_once() -> Any:
                async with semaphore:
                    return await bounded_ainvoke(
                        supervisor,
                        [SystemMessage(content=SUPERVISOR_PROMPT), HumanMessage(content=case["query"])],
                        timeout,
                    )
            (route_payload, route_latency), route_attempts = await call_with_backoff(
                route_once, retries=retries
            )
            parsed = route_payload.get("parsed")
            raw_message = route_payload.get("raw")
            if parsed is None:
                raise ValueError(f"Structured route parsing failed: {route_payload.get('parsing_error')}")
            route_usage = extract_usage(raw_message)
            raw_agent = parsed.next_agent
            repaired = repair_route_decision(case["query"], parsed.next_agent, parsed.intent)
            actual_agent = repaired.agent
            actual_intent = repaired.intent.value
            route_reason = repaired.reason
            route_bounded = True
        except Exception as exc:
            error_parts.append(f"route={type(exc).__name__}: {exc}")

    retrieval_candidates: list[Any] = []
    retrieval_scores: dict[str, float] = {}
    if architecture == "single_agent":
        visible_tools = ordered_single_tools
        gate_agent = None
    elif architecture == "static_multi":
        visible_tools = ordered_static_tools.get(actual_agent or "", [])
        gate_agent = actual_agent
    else:
        started = time.perf_counter()
        retrieval_candidates, retrieval_scores = bm25_shortlist(
            case["query"], unordered_domain_tools.get(actual_agent or "", []), top_k
        )
        retrieval_latency = (time.perf_counter() - started) * 1000
        visible_tools = counterbalanced_tools(
            retrieval_candidates,
            expected_tool=case.get("expected_tool"),
            case_key=case_key,
            order_block=repetition,
            seed=seed,
        )
        gate_agent = actual_agent

    try:
        if visible_tools:
            gate = llm.bind_tools(visible_tools)

            async def gate_once() -> Any:
                async with semaphore:
                    return await invoke_gate(gate, case["query"], timeout, gate_agent)
        else:
            async def gate_once() -> Any:
                async with semaphore:
                    response, latency = await bounded_ainvoke(
                        llm,
                        [SystemMessage(content=TOOL_GATE_PROMPT), HumanMessage(content=case["query"])],
                        timeout,
                    )
                    content = response.content if isinstance(response.content, str) else str(response.content or "")
                    return None, {}, content, 0, latency, extract_usage(response)

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
            schema_valid, schema_error = True, ""
            output = response_text
        gate_bounded = tool_calls <= max_tool_calls
    except Exception as exc:
        schema_valid, schema_error = False, ""
        error_parts.append(f"gate={type(exc).__name__}: {exc}")

    bounded_pass = route_bounded and gate_bounded and not error_parts
    checks = score_case(case, selected_tool, selected_args, output, bounded_pass, oracles)
    visible_names = [tool.name for tool in visible_tools]
    position, normalized_position = expected_position(visible_names, case.get("expected_tool"))
    expected_tool_name = case.get("expected_tool")

    return {
        "protocol": PROTOCOL_VERSION,
        "suite": suite,
        "registry_size": 11 + 4 * level,
        "distractors_per_domain": level,
        "architecture": architecture,
        "case_key": case_key,
        "case_id": case.get("id"),
        "repetition": repetition,
        "order_block": ORDER_BLOCKS[repetition - 1],
        "query": case["query"],
        "expected_agent": target_agent,
        "actual_agent": actual_agent,
        "raw_agent": raw_agent,
        "route_repair_reason": route_reason,
        "agent_correct": actual_agent == target_agent if architecture != "single_agent" else None,
        "expected_intent": target_intent,
        "actual_intent": actual_intent,
        "expected_tool": expected_tool_name,
        "selected_tool": selected_tool,
        "expected_args": case.get("expected_args", {}),
        "selected_args": selected_args,
        "visible_tool_count": len(visible_tools),
        "visible_tool_schema_chars": schema_chars(visible_tools),
        "visible_tool_names": visible_names,
        "expected_tool_position": position,
        "expected_tool_position_normalized": normalized_position,
        "retrieval_candidate_names": [tool.name for tool in retrieval_candidates],
        "retrieval_scores": {name: round(score, 6) for name, score in retrieval_scores.items()},
        "gold_in_candidates": (
            expected_tool_name in {tool.name for tool in retrieval_candidates}
            if architecture == "topk_multi" and expected_tool_name
            else None
        ),
        "schema_guard_passed": schema_valid,
        "schema_guard_error": schema_error,
        "tool_call_count": tool_calls,
        "route_attempts": route_attempts,
        "gate_attempts": gate_attempts,
        "route_latency_ms": round(route_latency, 2),
        "tool_retrieval_latency_ms": round(retrieval_latency, 4),
        "gate_latency_ms": round(gate_latency, 2),
        "tool_latency_ms": round(tool_latency, 2),
        "total_decision_latency_ms": round(route_latency + retrieval_latency + gate_latency, 2),
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


def finalize_manifest(run_dir: Path, records_file: Path, records: list[dict[str, Any]]) -> None:
    path = run_dir / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest.update({
        "status": "completed",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "actual_records": len(records),
        "error_records": sum(bool(record.get("error")) for record in records),
        "schema_guard_failures": sum(not record.get("schema_guard_passed", True) for record in records),
    })
    manifest["hashes"]["records"] = sha256_file(records_file)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


async def execute_run(args: argparse.Namespace, run_dir: Path, cases: list[tuple[str, str, dict[str, Any]]], registry: list[dict[str, Any]]) -> None:
    from app.agents.graph import RouteDecision

    setup_vertex_environment(args.credentials)
    os.environ["VERTEX_LOCATION"] = args.location
    os.environ["GOOGLE_CLOUD_REGION"] = args.location
    initialize_services()
    base_tools, real_tools = get_tools()
    llm = get_llm(model=args.model, temperature=0.0)
    supervisor = llm.with_structured_output(RouteDecision, include_raw=True)
    semaphore = asyncio.Semaphore(args.workers)

    max_distractors = build_distractor_tools(registry, max(args.levels))
    all_tools = dict(base_tools)
    for tools in max_distractors.values():
        all_tools.update({tool.name: tool for tool in tools})
    oracles = build_oracles((case for _, _, case in cases), all_tools)

    records_file = run_dir / "records.jsonl"
    records: list[dict[str, Any]] = []
    completed: set[str] = set()
    if records_file.exists():
        for line in records_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            records.append(record)
            completed.add(f"{record['suite']}:{record['distractors_per_domain']}:{record['architecture']}:{record['case_key']}:{record['repetition']}")
        print(f"Resuming with {len(records)} records.", flush=True)

    jobs: list[tuple[str, Any]] = []
    for level in args.levels:
        distractors = build_distractor_tools(registry, level)
        tools_by_name = dict(base_tools)
        for tools in distractors.values():
            tools_by_name.update({tool.name: tool for tool in tools})
        domain_tools = {
            domain: [tools_by_name[name] for name in names] + distractors[domain]
            for domain, names in SPECIALIST_TOOLS.items()
        }
        single_tools = real_tools + [tool for tools in distractors.values() for tool in tools]

        for repetition in range(1, args.repetitions + 1):
            for suite, case_key, case in cases:
                ordered_single = counterbalanced_tools(
                    single_tools,
                    expected_tool=case.get("expected_tool"),
                    case_key=case_key,
                    order_block=repetition,
                    seed=args.seed,
                )
                ordered_static = {
                    domain: counterbalanced_tools(
                        tools,
                        expected_tool=case.get("expected_tool"),
                        case_key=case_key,
                        order_block=repetition,
                        seed=args.seed,
                    )
                    for domain, tools in domain_tools.items()
                }
                for architecture in ARCHITECTURES:
                    key = f"{suite}:{level}:{architecture}:{case_key}:{repetition}"
                    if key in completed:
                        continue
                    jobs.append((key, evaluate_one(
                        architecture=architecture,
                        suite=suite,
                        case_key=case_key,
                        case=case,
                        repetition=repetition,
                        level=level,
                        llm=llm,
                        supervisor=supervisor,
                        ordered_single_tools=ordered_single,
                        ordered_static_tools=ordered_static,
                        unordered_domain_tools=domain_tools,
                        tools_by_name=tools_by_name,
                        oracles=oracles,
                        top_k=args.top_k,
                        timeout=args.timeout,
                        max_tool_calls=args.max_tool_calls,
                        retries=args.retries,
                        semaphore=semaphore,
                        seed=args.seed,
                    )))

    random.Random(args.seed).shuffle(jobs)
    print(f"Total jobs: {len(jobs)}; completed: {len(records)}", flush=True)
    for offset in range(0, len(jobs), args.workers):
        batch = jobs[offset:offset + args.workers]
        batch_records = await asyncio.gather(*(task for _, task in batch))
        records.extend(batch_records)
        with records_file.open("a", encoding="utf-8") as handle:
            for record in batch_records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Progress: {len(records)}/{len(records) + len(jobs) - offset - len(batch)}", flush=True)
    finalize_manifest(run_dir, records_file, records)
    print(f"Completed {len(records)} records.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-dataset", type=Path, default=DEFAULT_TOOL_DATASET)
    parser.add_argument("--robustness-dataset", type=Path, default=DEFAULT_ROBUSTNESS_DATASET)
    parser.add_argument("--base-distractors", type=Path, default=DEFAULT_BASE_DISTRACTORS)
    parser.add_argument("--extension-distractors", type=Path, default=DEFAULT_EXTENSION_DISTRACTORS)
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--location", default="europe-west1")
    parser.add_argument("--levels", type=parse_levels, default=parse_levels("0,4,10"))
    parser.add_argument("--suites", type=parse_suites, default=parse_suites("production_tools,robustness"))
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--retries", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--max-tool-calls", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260922)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.repetitions != 3:
        parser.error("v5 is locked to three order blocks")

    production = json.loads(args.tool_dataset.read_text(encoding="utf-8"))
    robustness = json.loads(args.robustness_dataset.read_text(encoding="utf-8"))
    validate_unique_case_ids(production)
    validate_unique_case_ids(robustness)
    if args.limit:
        production, robustness = production[:args.limit], robustness[:args.limit]
    cases: list[tuple[str, str, dict[str, Any]]] = []
    if "production_tools" in args.suites:
        cases.extend(("production_tools", make_case_key("production_tools", i, case), case) for i, case in enumerate(production, 1))
    if "robustness" in args.suites:
        cases.extend(("robustness", make_case_key("robustness", i, case), case) for i, case in enumerate(robustness, 1))
    registry = load_registry(args.base_distractors, args.extension_distractors)
    expected_records = len(cases) * len(args.levels) * len(ARCHITECTURES) * args.repetitions

    if args.validate_only:
        print(f"protocol={PROTOCOL_VERSION}")
        print(f"levels={args.levels}; registry_sizes={[11 + 4 * x for x in args.levels]}")
        print(f"architectures={ARCHITECTURES}; top_k={args.top_k}")
        print(f"production={len(production)}; robustness={len(robustness)}")
        print(f"expected_records={expected_records}")
        print("Validation PASSED")
        return

    if args.resume:
        run_dir = args.resume
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("protocol") != PROTOCOL_VERSION:
            parser.error("Resume protocol mismatch")
    else:
        run_dir = args.output_root / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir.mkdir(parents=True, exist_ok=False)
        manifest = {
            "protocol": PROTOCOL_VERSION,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "locked_before_execution",
            "hypothesis": "Dynamic within-domain Top-k shortlisting maintains selection quality while bounding tool exposure as the global registry grows from 11 to 51 tools.",
            "primary_outcome": "Top-k multi minus monolithic selection interaction Delta(51)-Delta(11) on production cases.",
            "noninferiority_margin": "Exploratory -5 percentage points; superiority interaction remains primary.",
            "arms": list(ARCHITECTURES),
            "levels": args.levels,
            "registry_sizes": [11 + 4 * level for level in args.levels],
            "top_k": args.top_k,
            "order_blocks": list(ORDER_BLOCKS),
            "expected_records": expected_records,
            "suites": args.suites,
            "repetitions": args.repetitions,
            "workers": args.workers,
            "timeout": args.timeout,
            "max_tool_calls": args.max_tool_calls,
            "seed": args.seed,
            "temperature": 0.0,
            "model": args.model,
            "location": args.location,
            "limit": args.limit,
            "hashes": {
                "tool_dataset": sha256_file(args.tool_dataset),
                "robustness_dataset": sha256_file(args.robustness_dataset),
                "base_distractors": sha256_file(args.base_distractors),
                "extension_distractors": sha256_file(args.extension_distractors),
                "base_runner_helpers": sha256_file(ROOT / "scripts" / "run_multi_vs_single_agent_experiment.py"),
                "v3_helpers": sha256_file(ROOT / "scripts" / "run_multi_vs_single_agent_v3_scalability.py"),
                "v4_helpers": sha256_file(ROOT / "scripts" / "run_multi_vs_single_agent_v4_scalability.py"),
                "runner": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            },
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    asyncio.run(execute_run(args, run_dir, cases, registry))


if __name__ == "__main__":
    main()
