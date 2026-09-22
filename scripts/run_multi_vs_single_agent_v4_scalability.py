#!/usr/bin/env python3
"""Counterbalanced three-arm tool-space scalability benchmark (v4.0).

Protocol v4 compares a monolithic tool gate, an oracle-domain partitioned
control, and the live supervisor-routed multi-agent system at 11, 19, and 27
global tools. Three deterministic order blocks place the expected production
tool first, middle, and last, removing the alphabetical-order confound found
in v3 while preserving nested registries.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage

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
    invoke_tool_gate,
    setup_vertex_environment,
    sha256_file,
)
from scripts.run_multi_vs_single_agent_v3_scalability import (
    build_distractor_tools,
    build_oracles,
    expected_agent,
    expected_intent,
    invoke_without_tools,
    load_distractor_registry,
    make_case_key,
    parse_levels,
    parse_suites,
    score_case,
    stable_json,
    call_with_backoff,
)

PROTOCOL_VERSION = "multi-vs-single-v4.0"
ARCHITECTURES = ("single_agent", "oracle_partitioned", "multi_agent")
ORDER_BLOCKS = ("gold_first", "gold_middle", "gold_last")
DEFAULT_TOOL_DATASET = ROOT / "data" / "scenario3_production_tools.json"
DEFAULT_ROBUSTNESS_DATASET = ROOT / "data" / "scenario3_robustness_cases.json"
DEFAULT_DISTRACTOR_REGISTRY = ROOT / "data" / "scenario3_distractor_registry_v3.json"
DEFAULT_OUTPUT_ROOT = ROOT / "logs" / "multi_vs_single_v4"


def deterministic_rank(seed: int, case_key: str, order_block: int, tool_name: str) -> str:
    payload = f"{seed}:{case_key}:{order_block}:{tool_name}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def counterbalanced_tools(
    tools: list[Any],
    *,
    expected_tool: str | None,
    case_key: str,
    order_block: int,
    seed: int,
) -> list[Any]:
    """Return a deterministic nested order with gold first/middle/last.

    Non-gold tools use a level-independent hash order, so adding distractors
    does not reorder tools already present. For tool-positive cases, the gold
    tool is inserted at a controlled normalized position in each of three
    order blocks. Tool-negative cases use the same deterministic hash order.
    """
    if order_block not in (1, 2, 3):
        raise ValueError(f"order_block must be 1, 2, or 3, got {order_block}")

    unique = {tool.name: tool for tool in tools}
    ordered = sorted(
        unique.values(),
        key=lambda tool: deterministic_rank(seed, case_key, order_block, tool.name),
    )
    if not expected_tool or expected_tool not in unique:
        return ordered

    gold = unique[expected_tool]
    non_gold = [tool for tool in ordered if tool.name != expected_tool]
    insert_at = (0, len(non_gold) // 2, len(non_gold))[order_block - 1]
    return non_gold[:insert_at] + [gold] + non_gold[insert_at:]


def schema_chars(tools: list[Any]) -> int:
    payload = []
    for tool in tools:
        args = getattr(tool, "args", None)
        if args is None and getattr(tool, "args_schema", None) is not None:
            args_schema = tool.args_schema
            args = args_schema.model_json_schema() if hasattr(args_schema, "model_json_schema") else {}
        payload.append({
            "name": tool.name,
            "description": getattr(tool, "description", ""),
            "parameters": args or {},
        })
    return len(stable_json(payload))


def expected_position(tool_names: list[str], expected_tool: str | None) -> tuple[int | None, float | None]:
    if not expected_tool or expected_tool not in tool_names:
        return None, None
    index = tool_names.index(expected_tool)
    denominator = max(1, len(tool_names) - 1)
    return index + 1, round(index / denominator, 4)


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
    ordered_single_tools: list[Any],
    ordered_specialist_tools: dict[str, list[Any]],
    tools_by_name: dict[str, Any],
    oracles: dict[str, str],
    timeout: float,
    max_tool_calls: int,
    retries: int,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    from app.agents.prompts import SUPERVISOR_PROMPT

    if architecture not in ARCHITECTURES:
        raise ValueError(f"Unknown architecture: {architecture}")

    target_agent = expected_agent(case, suite)
    target_intent = expected_intent(case, suite)
    actual_agent: str | None = None
    raw_agent: str | None = None
    actual_intent: str | None = None
    route_repair_reason: str | None = None
    selected_tool: str | None = None
    selected_args: dict[str, Any] = {}
    output = ""
    call_count = 0
    route_bounded = architecture != "multi_agent"
    gate_bounded = False
    route_attempts = 0
    gate_attempts = 0
    route_latency_ms = 0.0
    gate_latency_ms = 0.0
    tool_latency_ms = 0.0
    error_parts: list[str] = []

    if architecture == "oracle_partitioned":
        actual_agent = target_agent
        raw_agent = target_agent
        actual_intent = target_intent
        route_repair_reason = "oracle_domain_control"
    elif architecture == "multi_agent":
        try:
            async def route_once() -> Any:
                async with semaphore:
                    return await bounded_ainvoke(
                        supervisor,
                        [SystemMessage(content=SUPERVISOR_PROMPT), HumanMessage(content=case["query"])],
                        timeout,
                    )

            (decision, route_latency_ms), route_attempts = await call_with_backoff(
                route_once, retries=retries
            )
            raw_agent = decision.next_agent
            repaired = repair_route_decision(case["query"], decision.next_agent, decision.intent)
            actual_agent = repaired.agent
            actual_intent = repaired.intent.value
            route_repair_reason = repaired.reason
            route_bounded = True
        except Exception as exc:
            error_parts.append(f"route={type(exc).__name__}: {exc}")

    if architecture == "single_agent":
        visible_tools = ordered_single_tools
        gate_agent = None
    else:
        visible_tools = ordered_specialist_tools.get(actual_agent or "", [])
        gate_agent = actual_agent

    try:
        gate = llm.bind_tools(visible_tools) if visible_tools else None

        async def gate_once() -> Any:
            async with semaphore:
                if gate is None:
                    return await invoke_without_tools(llm, case["query"], timeout)
                return await invoke_tool_gate(gate, case["query"], timeout, gate_agent)

        gate_result, gate_attempts = await call_with_backoff(gate_once, retries=retries)
        selected_tool, selected_args, response_text, call_count, gate_latency_ms = gate_result
        tool = tools_by_name.get(selected_tool or "")
        if tool is not None:
            started = time.perf_counter()
            output = str(await asyncio.to_thread(tool.invoke, selected_args))
            tool_latency_ms = (time.perf_counter() - started) * 1000
        else:
            output = response_text
        gate_bounded = call_count <= max_tool_calls
    except Exception as exc:
        error_parts.append(f"gate={type(exc).__name__}: {exc}")

    bounded_pass = route_bounded and gate_bounded and not error_parts
    checks = score_case(case, selected_tool, selected_args, output, bounded_pass, oracles)
    visible_names = [tool.name for tool in visible_tools]
    gold_position, gold_position_normalized = expected_position(
        visible_names, case.get("expected_tool")
    )

    return {
        "protocol": PROTOCOL_VERSION,
        "suite": suite,
        "registry_size": 11 + 4 * distractors_per_domain,
        "distractors_per_domain": distractors_per_domain,
        "architecture": architecture,
        "case_key": case_key,
        "case_id": case.get("id"),
        "repetition": repetition,
        "order_block": ORDER_BLOCKS[repetition - 1],
        "visible_tool_count": len(visible_tools),
        "visible_tool_schema_chars": schema_chars(visible_tools),
        "visible_tool_names": visible_names,
        "expected_tool_position": gold_position,
        "expected_tool_position_normalized": gold_position_normalized,
        "query": case["query"],
        "expected_agent": target_agent,
        "actual_agent": actual_agent,
        "raw_agent": raw_agent,
        "route_repair_reason": route_repair_reason,
        "agent_correct": (
            actual_agent == target_agent if architecture != "single_agent" else None
        ),
        "expected_intent": target_intent,
        "actual_intent": actual_intent,
        "intent_correct": (
            actual_intent == target_intent
            if architecture == "multi_agent" and target_intent is not None
            else None
        ),
        "expected_tool": case.get("expected_tool"),
        "selected_tool": selected_tool,
        "expected_args": case.get("expected_args", {}),
        "selected_args": selected_args,
        "tool_call_count": call_count,
        "route_attempts": route_attempts,
        "gate_attempts": gate_attempts,
        "route_latency_ms": round(route_latency_ms, 2),
        "gate_latency_ms": round(gate_latency_ms, 2),
        "tool_latency_ms": round(tool_latency_ms, 2),
        "total_decision_latency_ms": round(route_latency_ms + gate_latency_ms, 2),
        "output": output[:500],
        **checks,
        "bounded_pass": bounded_pass,
        "error": "; ".join(error_parts),
    }


def load_cases(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[tuple[str, str, dict[str, Any]]]]:
    production_cases = json.loads(args.tool_dataset.read_text(encoding="utf-8"))
    robustness_cases = json.loads(args.robustness_dataset.read_text(encoding="utf-8"))
    validate_unique_case_ids(production_cases)
    validate_unique_case_ids(robustness_cases)
    if args.limit:
        production_cases = production_cases[: args.limit]
        robustness_cases = robustness_cases[: args.limit]

    selected: list[tuple[str, str, dict[str, Any]]] = []
    if "production_tools" in args.suites:
        selected.extend(
            ("production_tools", make_case_key("production_tools", idx, case), case)
            for idx, case in enumerate(production_cases, start=1)
        )
    if "robustness" in args.suites:
        selected.extend(
            ("robustness", make_case_key("robustness", idx, case), case)
            for idx, case in enumerate(robustness_cases, start=1)
        )
    return production_cases, robustness_cases, selected


def locked_manifest(args: argparse.Namespace, expected_records: int) -> dict[str, Any]:
    return {
        "protocol": PROTOCOL_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "locked_before_execution",
        "hypothesis": "Domain partitioning exhibits a smaller tool-selection degradation than the monolithic gate as the global registry expands from 11 to 27 tools.",
        "primary_outcome": "Live-multi minus monolithic tool-selection interaction: Delta(27) - Delta(11) on the 60 production cases.",
        "secondary_outcomes": [
            "Oracle-partitioned minus monolithic interaction",
            "Live-multi minus oracle-partitioned routing overhead",
            "End-to-end pass interaction",
            "Visible tool count, schema characters, and decision latency",
            "Robustness-suite results reported separately",
        ],
        "arms": {
            "single_agent": "Monolithic gate exposing the full registry",
            "oracle_partitioned": "Gold-domain specialist gate; mechanistic partitioning control",
            "multi_agent": "Live structured supervisor plus production route repair and predicted-domain gate",
        },
        "ordering_policy": "Three deterministic per-case blocks place the gold tool first, middle, and last. Non-gold hash ordering is level-independent and nested.",
        "order_blocks": list(ORDER_BLOCKS),
        "repetitions": args.repetitions,
        "levels": args.levels,
        "suites": args.suites,
        "expected_records": expected_records,
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
            "distractor_registry": sha256_file(args.distractor_registry),
            "runner": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
    }


def finalize_manifest(run_dir: Path, records_file: Path, record_count: int, error_count: int) -> None:
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update({
        "status": "completed",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "actual_records": record_count,
        "error_records": error_count,
    })
    manifest.setdefault("hashes", {})["records"] = sha256_file(records_file)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


async def execute_run(
    args: argparse.Namespace,
    run_dir: Path,
    selected_cases: list[tuple[str, str, dict[str, Any]]],
    distractor_registry: list[dict[str, Any]],
) -> None:
    from app.agents.graph import RouteDecision

    setup_vertex_environment(args.credentials)
    os.environ["VERTEX_LOCATION"] = args.location
    os.environ["GOOGLE_CLOUD_REGION"] = args.location
    initialize_services()
    base_tools_by_name, real_tools = get_tools()
    llm = get_llm(model=args.model, temperature=0.0)
    supervisor = llm.with_structured_output(RouteDecision)
    semaphore = asyncio.Semaphore(args.workers)

    max_distractors = build_distractor_tools(distractor_registry, max(args.levels))
    tools_by_name = dict(base_tools_by_name)
    for domain_tools in max_distractors.values():
        for tool in domain_tools:
            tools_by_name[tool.name] = tool
    oracles = build_oracles((case for _, _, case in selected_cases), tools_by_name)

    records_file = run_dir / "records.jsonl"
    existing_records: list[dict[str, Any]] = []
    completed_keys: set[str] = set()
    if records_file.exists():
        for line in records_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            existing_records.append(record)
            completed_keys.add(
                f"{record['suite']}:{record['distractors_per_domain']}:{record['architecture']}:{record['case_key']}:{record['repetition']}"
            )
        print(f"Resuming run: found {len(existing_records)} existing records.", flush=True)

    jobs: list[tuple[str, Any]] = []
    for level in args.levels:
        distractors = build_distractor_tools(distractor_registry, level)
        level_tools_by_name = dict(base_tools_by_name)
        all_distractors: list[Any] = []
        for domain_tools in distractors.values():
            for tool in domain_tools:
                level_tools_by_name[tool.name] = tool
                all_distractors.append(tool)
        single_unordered = real_tools + all_distractors

        specialist_unordered = {
            domain: [level_tools_by_name[name] for name in real_names] + distractors[domain]
            for domain, real_names in SPECIALIST_TOOLS.items()
        }

        for repetition in range(1, args.repetitions + 1):
            for suite, case_key, case in selected_cases:
                expected_tool = case.get("expected_tool")
                ordered_single = counterbalanced_tools(
                    single_unordered,
                    expected_tool=expected_tool,
                    case_key=case_key,
                    order_block=repetition,
                    seed=args.seed,
                )
                ordered_specialists = {
                    domain: counterbalanced_tools(
                        domain_tools,
                        expected_tool=expected_tool,
                        case_key=case_key,
                        order_block=repetition,
                        seed=args.seed,
                    )
                    for domain, domain_tools in specialist_unordered.items()
                }

                for architecture in ARCHITECTURES:
                    job_key = f"{suite}:{level}:{architecture}:{case_key}:{repetition}"
                    if job_key in completed_keys:
                        continue
                    jobs.append((
                        job_key,
                        evaluate_one(
                            architecture=architecture,
                            suite=suite,
                            case_key=case_key,
                            case=case,
                            repetition=repetition,
                            distractors_per_domain=level,
                            llm=llm,
                            supervisor=supervisor,
                            ordered_single_tools=ordered_single,
                            ordered_specialist_tools=ordered_specialists,
                            tools_by_name=level_tools_by_name,
                            oracles=oracles,
                            timeout=args.timeout,
                            max_tool_calls=args.max_tool_calls,
                            retries=args.retries,
                            semaphore=semaphore,
                        ),
                    ))

    random.Random(args.seed).shuffle(jobs)
    print(
        f"Total jobs to execute: {len(jobs)} (already completed: {len(existing_records)})",
        flush=True,
    )

    records = list(existing_records)
    for offset in range(0, len(jobs), args.workers):
        batch = jobs[offset: offset + args.workers]
        batch_records = await asyncio.gather(*(task for _, task in batch))
        records.extend(batch_records)
        with records_file.open("a", encoding="utf-8") as handle:
            for record in batch_records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Progress: {len(records)}/{len(jobs) + len(existing_records)} records written.", flush=True)

    error_count = sum(bool(record.get("error")) for record in records)
    finalize_manifest(run_dir, records_file, len(records), error_count)
    print(f"Run completed: {len(records)} records, {error_count} execution errors.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-dataset", type=Path, default=DEFAULT_TOOL_DATASET)
    parser.add_argument("--robustness-dataset", type=Path, default=DEFAULT_ROBUSTNESS_DATASET)
    parser.add_argument("--distractor-registry", type=Path, default=DEFAULT_DISTRACTOR_REGISTRY)
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--location", default="europe-west1")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--levels", type=parse_levels, default=parse_levels("0,2,4"))
    parser.add_argument("--suites", type=parse_suites, default=parse_suites("production_tools,robustness"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--retries", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--max-tool-calls", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260921)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    if args.repetitions != 3:
        parser.error("Protocol v4 is locked to exactly 3 counterbalanced order blocks")
    distractor_registry = load_distractor_registry(args.distractor_registry)
    production_cases, robustness_cases, selected_cases = load_cases(args)
    expected_records = len(selected_cases) * len(args.levels) * len(ARCHITECTURES) * args.repetitions

    if args.validate_only:
        print("=== VALIDATE ONLY (OFFLINE DRY-RUN) ===")
        print(f"protocol               = {PROTOCOL_VERSION}")
        print(f"production cases       = {len(production_cases)}")
        print(f"robustness cases       = {len(robustness_cases)}")
        print(f"suites                 = {args.suites}")
        print(f"levels                 = {args.levels}")
        print(f"architectures          = {len(ARCHITECTURES)} {ARCHITECTURES}")
        print(f"order blocks           = {ORDER_BLOCKS}")
        print(f"expected total records = {expected_records}")
        print("Validation PASSED.")
        return

    if args.resume:
        run_dir = args.resume
        manifest_path = run_dir / "manifest.json"
        if not manifest_path.exists():
            parser.error(f"manifest.json missing in resume directory: {run_dir}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("protocol") != PROTOCOL_VERSION:
            parser.error(f"Cannot resume protocol {manifest.get('protocol')} with {PROTOCOL_VERSION}")
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = args.output_root / stamp
        run_dir.mkdir(parents=True, exist_ok=False)
        manifest = locked_manifest(args, expected_records)
        (run_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    asyncio.run(execute_run(args, run_dir, selected_cases, distractor_registry))


if __name__ == "__main__":
    main()
