#!/usr/bin/env python3
"""Matched multi-agent versus monolithic tool-space scalability benchmark (v3.0).

Protocol v3 evaluates the trade-off between routing overhead and tool-selection
interference across locked tool registry sizes (11, 19, and 27 tools).

- Single-agent arm: One monolithic tool gate exposing all available tools at the given level.
- Multi-agent arm: Live structured supervisor + production route repair, then specialist
  tool gate exposing only tools assigned to the predicted domain.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import random
import re
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from pydantic import Field, create_model

from app.services.evaluation_contract import (
    arguments_match as contract_arguments_match,
    validate_unique_case_ids,
)
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
    normalize_tool_name,
    setup_vertex_environment,
    sha256_file,
    tool_gate_prompt,
)

PROTOCOL_VERSION = "multi-vs-single-v3.0"
DEFAULT_TOOL_DATASET = ROOT / "data" / "scenario3_production_tools.json"
DEFAULT_ROBUSTNESS_DATASET = ROOT / "data" / "scenario3_robustness_cases.json"
DEFAULT_DISTRACTOR_REGISTRY = ROOT / "data" / "scenario3_distractor_registry_v3.json"
DEFAULT_OUTPUT_ROOT = ROOT / "logs" / "multi_vs_single_v3"

DISCLOSURE_TERMS = (
    "synthetic",
    "distractor",
    "fake",
    "giả lập",
    "stress test",
    "benchmark-only",
)


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalized_output(value: Any) -> str:
    text = str(value).casefold()
    return re.sub(r"\s+", " ", text).strip()


def parse_levels(raw: str) -> list[int]:
    levels = sorted({int(item.strip()) for item in raw.split(",") if item.strip()})
    if not levels or any(level not in (0, 2, 4) for level in levels):
        raise argparse.ArgumentTypeError("levels must be comma-separated integers from {0, 2, 4}")
    return levels


def parse_suites(raw: str) -> list[str]:
    suites = [item.strip() for item in raw.split(",") if item.strip()]
    allowed = {"production_tools", "robustness"}
    for suite in suites:
        if suite not in allowed:
            raise argparse.ArgumentTypeError(f"unknown suite '{suite}', allowed: {allowed}")
    return suites


def load_distractor_registry(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Distractor registry not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data) != 16:
        raise ValueError(f"Distractor registry must contain exactly 16 tools, got {len(data)}")
    
    # Audit for forbidden disclosure terms in descriptions
    for item in data:
        desc = item.get("description", "").lower()
        for term in DISCLOSURE_TERMS:
            if term in desc:
                raise ValueError(
                    f"Distractor '{item.get('name')}' contains forbidden disclosure term '{term}'"
                )
    return data


def build_distractor_tools(
    registry: list[dict[str, Any]], distractors_per_domain: int
) -> dict[str, list[StructuredTool]]:
    """Build StructuredTool instances from distractor registry for a given level."""
    if distractors_per_domain not in (0, 2, 4):
        raise ValueError(f"distractors_per_domain must be 0, 2, or 4, got {distractors_per_domain}")

    result: dict[str, list[StructuredTool]] = {
        "academic": [],
        "financial": [],
        "scholarship": [],
        "general": [],
    }
    if distractors_per_domain == 0:
        return result

    type_mapping = {
        "string": (str, ...),
        "integer": (int, ...),
        "number": (float, ...),
        "boolean": (bool, ...),
    }

    for item in registry:
        domain = item["domain"]
        order = item.get("registry_order", 999)
        if order <= distractors_per_domain:
            fields = {}
            for p_name, p_spec in item.get("parameters", {}).items():
                py_type, def_val = type_mapping.get(p_spec.get("type", "string"), (str, ...))
                fields[p_name] = (py_type, Field(def_val, description=p_spec.get("description", "")))

            schema_model = create_model(f"{item['name']}_schema", **fields)
            out_str = item.get("deterministic_output", "OK")

            def make_handler(ret_val: str):
                def handler(**kwargs: Any) -> str:
                    return ret_val
                return handler

            tool = StructuredTool.from_function(
                func=make_handler(out_str),
                name=item["name"],
                description=item["description"],
                args_schema=schema_model,
            )
            result[domain].append(tool)

    return result


def make_case_key(suite: str, index: int, case: dict[str, Any]) -> str:
    return f"{suite}:{index:03d}:{case.get('id', 'unknown')}"


def expected_agent(case: dict[str, Any], suite: str) -> str:
    return str(case.get("agent") if suite == "production_tools" else case.get("expected_agent"))


def expected_intent(case: dict[str, Any], suite: str) -> str | None:
    if suite == "production_tools":
        return None
    value = case.get("expected_intent")
    return str(value) if value is not None else None


def build_oracles(cases: Iterable[dict[str, Any]], tools_by_name: dict[str, Any]) -> dict[str, str]:
    oracles: dict[str, str] = {}
    for case in cases:
        tool_name = case.get("expected_tool")
        if not tool_name:
            continue
        tool = tools_by_name.get(tool_name)
        if tool is None:
            continue
        oracle_key = stable_json({"tool": tool_name, "args": case.get("expected_args", {})})
        if oracle_key not in oracles:
            try:
                oracles[oracle_key] = normalized_output(tool.invoke(case.get("expected_args", {})))
            except Exception:
                oracles[oracle_key] = ""
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
        wanted_tool is None
        or contract_arguments_match(
            case.get("expected_args", {}),
            selected_args,
            tool_name=selected_tool,
            accepted=case.get("accepted_args", {}),
        )
    )

    if wanted_tool is None:
        expected_responses = case.get("expected_response_any") or []
        lowered_output = output.lower()
        result_passed = (
            any(phrase.lower() in lowered_output for phrase in expected_responses)
            if expected_responses
            else True
        )
    else:
        oracle_key = stable_json({"tool": wanted_tool, "args": case.get("expected_args", {})})
        expected_output = oracles.get(oracle_key, "")
        norm_actual = normalized_output(output)
        if expected_output:
            result_passed = norm_actual == expected_output or expected_output in norm_actual
        else:
            result_passed = selection_passed and arguments_passed

    passed = selection_passed and arguments_passed and result_passed and bounded_pass
    return {
        "selection_passed": selection_passed,
        "arguments_passed": arguments_passed,
        "result_passed": result_passed,
        "passed": passed,
    }


async def call_with_backoff(factory: Any, *, retries: int) -> tuple[Any, int]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return await factory(), attempt
        except Exception as exc:
            last_error = exc
            if attempt == retries:
                break
            await asyncio.sleep(min(30.0, (2 ** attempt) + random.random()))
    assert last_error is not None
    raise last_error


async def invoke_without_tools(llm: Any, query: str, timeout: float) -> tuple[None, dict[str, Any], str, int, float]:
    response, latency_ms = await bounded_ainvoke(
        llm,
        [SystemMessage(content=TOOL_GATE_PROMPT), HumanMessage(content=query)],
        timeout,
    )
    content = response.content if isinstance(response.content, str) else str(response.content or "")
    return None, {}, content, 0, latency_ms


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
    specialist_tool_names: dict[str, list[str]],
    single_gate: Any,
    single_tool_count: int,
    single_tool_names: list[str],
    tools_by_name: dict[str, Any],
    oracles: dict[str, str],
    timeout: float,
    max_tool_calls: int,
    retries: int,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    from app.agents.prompts import SUPERVISOR_PROMPT

    actual_agent: str | None = None
    raw_agent: str | None = None
    actual_intent: str | None = None
    route_repair_reason: str | None = None
    selected_tool: str | None = None
    selected_args: dict[str, Any] = {}
    output = ""
    call_count = 0
    route_bounded = architecture == "single_agent"
    gate_bounded = False
    route_attempts = 0
    gate_attempts = 0
    route_latency_ms = 0.0
    gate_latency_ms = 0.0
    tool_latency_ms = 0.0
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

            (decision, r_ms), route_attempts = await call_with_backoff(route_once, retries=retries)
            route_latency_ms = r_ms
            raw_agent = decision.next_agent
            repaired = repair_route_decision(
                case["query"], decision.next_agent, decision.intent
            )
            actual_agent = repaired.agent
            actual_intent = repaired.intent.value
            route_repair_reason = repaired.reason
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
        selected_tool, selected_args, response_text, call_count, gate_latency_ms = gate_result
        tool = tools_by_name.get(selected_tool or "")
        if tool is not None:
            t0 = time.perf_counter()
            output = str(await asyncio.to_thread(tool.invoke, selected_args))
            tool_latency_ms = (time.perf_counter() - t0) * 1000
        else:
            output = response_text
        gate_bounded = call_count <= max_tool_calls
    except Exception as exc:
        error_parts.append(f"gate={type(exc).__name__}: {exc}")

    bounded_pass = route_bounded and gate_bounded and not error_parts
    checks = score_case(case, selected_tool, selected_args, output, bounded_pass, oracles)
    target_agent = expected_agent(case, suite)
    target_intent = expected_intent(case, suite)

    if architecture == "multi_agent":
        visible_count = specialist_tool_counts.get(actual_agent or "", 0)
        visible_names = specialist_tool_names.get(actual_agent or "", [])
    else:
        visible_count = single_tool_count
        visible_names = single_tool_names

    # Registry size mapping: level 0 -> 11, level 2 -> 19, level 4 -> 27
    registry_size = 11 + 4 * distractors_per_domain

    return {
        "protocol": PROTOCOL_VERSION,
        "suite": suite,
        "registry_size": registry_size,
        "distractors_per_domain": distractors_per_domain,
        "architecture": architecture,
        "case_key": case_key,
        "case_id": case.get("id"),
        "repetition": repetition,
        "visible_tool_count": visible_count,
        "visible_tool_names": visible_names,
        "query": case["query"],
        "expected_agent": target_agent,
        "actual_agent": actual_agent,
        "raw_agent": raw_agent,
        "route_repair_reason": route_repair_reason,
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
        "route_latency_ms": round(route_latency_ms, 2),
        "gate_latency_ms": round(gate_latency_ms, 2),
        "tool_latency_ms": round(tool_latency_ms, 2),
        "output": output[:500],
        **checks,
        "bounded_pass": bounded_pass,
        "error": "; ".join(error_parts),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    content = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"
    path.write_text(content, encoding="utf-8")


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
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--resume", type=Path, default=None)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    production_cases = json.loads(args.tool_dataset.read_text(encoding="utf-8"))
    robustness_cases = json.loads(args.robustness_dataset.read_text(encoding="utf-8"))
    validate_unique_case_ids(production_cases)
    validate_unique_case_ids(robustness_cases)
    distractor_registry = load_distractor_registry(args.distractor_registry)

    if args.limit:
        production_cases = production_cases[: args.limit]
        robustness_cases = robustness_cases[: args.limit]

    selected_cases: list[tuple[str, str, dict[str, Any]]] = []
    if "production_tools" in args.suites:
        for idx, case in enumerate(production_cases, start=1):
            selected_cases.append(("production_tools", make_case_key("production_tools", idx, case), case))
    if "robustness" in args.suites:
        for idx, case in enumerate(robustness_cases, start=1):
            selected_cases.append(("robustness", make_case_key("robustness", idx, case), case))

    total_expected_records = (
        len(selected_cases) * len(args.levels) * 2 * args.repetitions
    )

    if args.validate_only:
        print("=== VALIDATE ONLY (OFFLINE DRY-RUN) ===")
        print(f"protocol               = {PROTOCOL_VERSION}")
        print(f"production cases       = {len(production_cases)}")
        print(f"robustness cases       = {len(robustness_cases)}")
        print(f"suites                 = {args.suites}")
        print(f"levels                 = {args.levels}")
        print(f"architectures          = 2 (multi_agent, single_agent)")
        print(f"repetitions            = {args.repetitions}")
        print(f"expected total records = {total_expected_records}")
        print("Validation PASSED.")
        sys.exit(0)

    if args.resume:
        run_dir = args.resume
        if not run_dir.exists():
            parser.error(f"Resume directory does not exist: {run_dir}")
        manifest_file = run_dir / "manifest.json"
        if not manifest_file.exists():
            parser.error(f"manifest.json missing in resume directory: {run_dir}")
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = args.output_root / stamp
        run_dir.mkdir(parents=True, exist_ok=False)

        manifest = {
            "protocol": PROTOCOL_VERSION,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "locked_before_execution",
            "primary_outcome": "Architecture-by-registry interaction in tool-selection accuracy from 11 to 27 tools on the 60 production cases",
            "multi_agent_arm": "Live structured supervisor + production route repair, then predicted-specialist tool gate",
            "single_agent_arm": "Monolithic tool gate exposing all available tools at the given registry level",
            "repetitions": args.repetitions,
            "levels": args.levels,
            "suites": args.suites,
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
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    asyncio.run(execute_run(args, run_dir, selected_cases, distractor_registry))


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
    tools_by_name, real_tools = get_tools()

    oracles = build_oracles((case for _, _, case in selected_cases), tools_by_name)
    llm = get_llm(model=args.model, temperature=0.0)
    supervisor = llm.with_structured_output(RouteDecision)
    semaphore = asyncio.Semaphore(args.workers)

    records_file = run_dir / "records.jsonl"
    existing_records: list[dict[str, Any]] = []
    completed_keys: set[str] = set()
    if records_file.exists():
        for line in records_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                existing_records.append(rec)
                k = f"{rec['suite']}:{rec['distractors_per_domain']}:{rec['architecture']}:{rec['case_key']}:{rec['repetition']}"
                completed_keys.add(k)
        print(f"Resuming run: found {len(existing_records)} existing records.", flush=True)

    records: list[dict[str, Any]] = list(existing_records)
    jobs = []

    for level in args.levels:
        distractor_dict = build_distractor_tools(distractor_registry, level)
        for domain_distractors in distractor_dict.values():
            for d_tool in domain_distractors:
                tools_by_name[d_tool.name] = d_tool

        specialist_gates: dict[str, Any | None] = {}
        specialist_tool_counts: dict[str, int] = {}
        specialist_tool_names: dict[str, list[str]] = {}
        all_distractors = []

        for domain, real_names in SPECIALIST_TOOLS.items():
            domain_tools = [tools_by_name[name] for name in real_names] + distractor_dict[domain]
            # Stable order
            domain_tools = sorted(domain_tools, key=lambda t: t.name)
            specialist_gates[domain] = llm.bind_tools(domain_tools) if domain_tools else None
            specialist_tool_counts[domain] = len(domain_tools)
            specialist_tool_names[domain] = [t.name for t in domain_tools]
            all_distractors.extend(distractor_dict[domain])

        single_tools = sorted(real_tools + all_distractors, key=lambda t: t.name)
        single_gate = llm.bind_tools(single_tools)
        single_tool_names = [t.name for t in single_tools]

        for repetition in range(1, args.repetitions + 1):
            for suite, case_key, case in selected_cases:
                for architecture in ("multi_agent", "single_agent"):
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
                            specialist_gates=specialist_gates,
                            specialist_tool_counts=specialist_tool_counts,
                            specialist_tool_names=specialist_tool_names,
                            single_gate=single_gate,
                            single_tool_count=len(single_tools),
                            single_tool_names=single_tool_names,
                            tools_by_name=tools_by_name,
                            oracles=oracles,
                            timeout=args.timeout,
                            max_tool_calls=args.max_tool_calls,
                            retries=args.retries,
                            semaphore=semaphore,
                        )
                    ))

    random.Random(args.seed).shuffle(jobs)
    print(f"Total jobs to execute: {len(jobs)} (already completed: {len(existing_records)})", flush=True)

    batch_size = args.workers
    for offset in range(0, len(jobs), batch_size):
        batch = jobs[offset: offset + batch_size]
        batch_tasks = [task for _, task in batch]
        batch_records = await asyncio.gather(*batch_tasks)
        records.extend(batch_records)

        with open(records_file, "a", encoding="utf-8") as f:
            for rec in batch_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        total_done = len(records)
        total_target = len(jobs) + len(existing_records)
        print(f"Progress: {total_done}/{total_target} records written.", flush=True)

    print(f"Run finished successfully. Records saved to {records_file}", flush=True)


if __name__ == "__main__":
    main()
