#!/usr/bin/env python3
"""V13 Scenario 1 & 2 — Architecture-Level Comparison and Ablation Runner.

Implements 3 architectural configurations for Scenario 1 (RQ1):
  S1-A: Unified Single Agent (all tools, no routing)
  S1-B: Routed Generic Worker (routing + scoped tools, generic prompt)
  S1-C: Full CTU-Chat (routing + scoped tools + specialist prompts)

And 5 ablation variants for Scenario 2 (RQ2):
  S2-A1: No Specialist Policy (= S1-B, shared)
  S2-A2: No Tool Isolation (specialist prompts, but full tool visibility)
  S2-A3: Uniform Evidence (all evidence via document retrieval, no graph)
  S2-A4: No Deterministic Calculation (LLM generates arithmetic directly)
  S2-A5: No Route Repair (raw supervisor output, no contract repair)

All configurations share:
  - Same LLM (Gemini 2.5 Flash Lite, temperature 0.0)
  - Same knowledge sources (Neo4j, structured tuition, 244 docs)
  - Same retrieval stack (BM25 + dense + RRF + bge-reranker-v2-m3)
  - Same tool schemas and implementations
  - Same answer-generation constraints

Usage:
  python scripts/run_v13_architecture_experiment.py --scenario s1 --reps 3
  python scripts/run_v13_architecture_experiment.py --scenario s2 --reps 3
  python scripts/run_v13_architecture_experiment.py --scenario both --reps 3
  python scripts/run_v13_architecture_experiment.py --scenario s1 --configs S1-A S1-C --reps 1  # selective
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
import copy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

from scripts.scenario12_common import (  # noqa: E402
    ScenarioCase,
    load_cases,
    mean,
    normalize_text,
    retrieve_configurations,
    sha256_file,
    source_from_document,
    source_metrics,
)

logger = logging.getLogger("v13_arch")

# ── Constants ──
MODEL = "gemini-2.5-flash-lite"
TEMPERATURE = 0.0
TOP_K = 7
METRIC_K = 10
HELDOUT_DATASET = ROOT / "data" / "scenario12_heldout_100.jsonl"
LOG_ROOT = ROOT / "logs" / "v13_architecture"
SERVICE_ACCOUNT = ROOT / "gen-lang-client-0656432358-9a6fb12696b2.json"

# ── Prompts ──

UNIFIED_SINGLE_AGENT_PROMPT = """Bạn là trợ lý tư vấn học vụ và hành chính toàn diện của Trường Đại học Cần Thơ (CTU).
Bạn có quyền truy cập TẤT CẢ các công cụ sau, hãy chọn công cụ phù hợp nhất cho câu hỏi:

CÔNG CỤ HỌC VỤ (dùng khi hỏi về chương trình đào tạo, ngành, môn học, tiên quyết):
- tra_cuu_nganh: Tra cứu thông tin chi tiết một ngành theo tên hoặc mã ngành
- so_sanh_nganh: So sánh hai chương trình đào tạo
- tim_nganh: Tìm kiếm ngành theo từ khóa
- xem_chuoi_tien_quyet: Xem chuỗi tiên quyết của một học phần
- mon_chung_giua_nganh: Tìm môn học chung giữa hai ngành
- tim_nganh_co_mon: Tìm ngành có chứa một học phần cụ thể

CÔNG CỤ TÀI CHÍNH (dùng khi hỏi về học phí, miễn giảm, tính toán):
- tra_cuu_hoc_phi_graph: Tra cứu mức học phí thực tế theo ngành/chương trình
- tra_cuu_co_so_mien_giam_graph: Tra cứu cơ sở tính miễn giảm học phí
- tra_cuu_quy_dinh_hoc_phi: Tra cứu quy định học phí
- tinh_toan_hoc_phi: Tính toán học phí sau miễn giảm (cần: học phí thực tế, cơ sở miễn giảm, % giảm)

CÔNG CỤ HỌC BỔNG:
- tinh_tien_hoc_bong: Tính tiền học bổng (cần: GPA trong [0,4], điểm rèn luyện trong [0,100])

QUY TẮC:
- Chỉ gọi đúng MỘT công cụ khi có đủ tham số bắt buộc và hợp lệ.
- Không bịa tham số. Nếu thiếu thông tin, hỏi lại người dùng.
- Với câu hỏi chính sách, quy chế, vay vốn: KHÔNG gọi công cụ, trả lời từ EVIDENCE.
- GPA trong [0,4], điểm rèn luyện trong [0,100], % trong [0,100], số tiền ≥ 0.

EVIDENCE:
{context}

{retrieval_instruction}"""

GENERIC_WORKER_PROMPT = """Bạn là trợ lý tư vấn của Trường Đại học Cần Thơ (CTU).
Trả lời câu hỏi dựa trên EVIDENCE được cung cấp. Nếu có công cụ phù hợp, hãy sử dụng.
Chỉ gọi công cụ khi có đủ tham số bắt buộc và hợp lệ. Không bịa tham số.

EVIDENCE:
{context}

{retrieval_instruction}"""


# ── Scenario Config Registry ──

SCENARIO_1_CONFIGS = ("S1-A", "S1-B", "S1-C")
SCENARIO_2_CONFIGS = ("S2-A0", "S2-A1", "S2-A2", "S2-A3", "S2-A4", "S2-A5")
ALL_CONFIGS = (*SCENARIO_1_CONFIGS, *SCENARIO_2_CONFIGS)


# ═══════════════════════════════════════════════════════════════════════
# Infrastructure setup
# ═══════════════════════════════════════════════════════════════════════

def configure_vertex(credentials: Path, project: str | None) -> str:
    if credentials.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials.resolve())
        metadata = json.loads(credentials.read_text(encoding="utf-8"))
        project = project or metadata.get("project_id")
    if not project:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise RuntimeError("Cannot determine Google Cloud project for Vertex AI")
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project
    return project


def init_services():
    """Initialize all shared services (LLM, RAG engine, graph, tools)."""
    from google import genai
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model=MODEL,
        temperature=TEMPERATURE,
        convert_system_message_to_human=False,
    )
    rewrite_llm = ChatGoogleGenerativeAI(
        model=MODEL,
        temperature=TEMPERATURE,
        convert_system_message_to_human=False,
    )

    # RAG engine
    from app.services.rag_engine import RAGEngine
    engine = RAGEngine()

    # Graph service
    from app.services.graph_service import AcademicGraphService
    try:
        graph_service = AcademicGraphService()
        graph_service.ensure_data_loaded()
    except Exception as e:
        logger.warning("Neo4j unavailable, graph features disabled: %s", e)
        graph_service = None

    # Tuition catalog
    from app.services.tuition_catalog import TuitionRateCatalog
    tuition_catalog = TuitionRateCatalog.load()

    # Tools — import individual functions (matching app/main.py pattern)
    from app.tools.academic_program import (
        tra_cuu_nganh, so_sanh_nganh, tim_nganh,
        xem_chuoi_tien_quyet, mon_chung_giua_nganh, tim_nganh_co_mon,
        set_graph_service,
    )
    from app.tools.tuition_graph import (
        tra_cuu_hoc_phi_graph, tra_cuu_quy_dinh_hoc_phi,
        tra_cuu_co_so_mien_giam_graph,
        set_tuition_graph_service, set_tuition_catalog,
    )
    from app.tools.tuition import tinh_toan_hoc_phi
    from app.tools.scholarship import tinh_tien_hoc_bong

    # Inject services into tool modules (same as app/main.py lifespan)
    if graph_service:
        set_graph_service(graph_service)
        set_tuition_graph_service(graph_service)
    set_tuition_catalog(tuition_catalog)

    academic_tools = [
        tra_cuu_nganh, so_sanh_nganh, tim_nganh,
        xem_chuoi_tien_quyet, mon_chung_giua_nganh, tim_nganh_co_mon,
    ] if graph_service else []
    financial_tools = [
        tra_cuu_hoc_phi_graph, tra_cuu_co_so_mien_giam_graph,
        tra_cuu_quy_dinh_hoc_phi, tinh_toan_hoc_phi,
    ]
    scholarship_tools = [tinh_tien_hoc_bong]
    all_tools = academic_tools + financial_tools + scholarship_tools

    # Reranker from engine (supports local GPU CUDA, remote Colab tunnel, or OpenRouter)
    compressor = getattr(engine, "reranker", None)
    if compressor is not None:
        logger.info("Using engine reranker: %s", type(compressor).__name__)
    else:
        logger.warning("Reranker is not enabled on engine")

    return {
        "llm": llm,
        "rewrite_llm": rewrite_llm,
        "engine": engine,
        "graph_service": graph_service,
        "tuition_catalog": tuition_catalog,
        "academic_tools": academic_tools,
        "financial_tools": financial_tools,
        "scholarship_tools": scholarship_tools,
        "all_tools": all_tools,
        "compressor": compressor,
    }


# ═══════════════════════════════════════════════════════════════════════
# Architecture Configurations
# ═══════════════════════════════════════════════════════════════════════

async def run_unified_single_agent(case: ScenarioCase, services: dict) -> dict[str, Any]:
    """S1-A: Unified Single Agent — one agent, all tools, no routing."""
    from langgraph.prebuilt import create_react_agent
    from langchain_core.messages import HumanMessage, SystemMessage
    from app.agents.graph import attach_validation_to_tool, _parse_llm_content

    llm = services["llm"]
    all_tools = [attach_validation_to_tool(t) for t in services["all_tools"]]

    # Retrieve evidence (full stack, same as CTU-Chat)
    trace = retrieve_configurations(
        case, services["engine"], services["graph_service"],
        services["tuition_catalog"], services["compressor"],
        top_k=TOP_K, metric_k=METRIC_K,
    )
    # Use T4 (full proposed retrieval) for context
    context_docs = trace.configs.get("T4", [])
    context_str = "\n\n---\n\n".join(
        getattr(doc, "page_content", str(doc)) for doc in context_docs
    ) or "Không có tài liệu liên quan."

    from app.services.query_intent import classify_query_intent, build_answer_instruction
    decision = classify_query_intent(case.question)
    retrieval_instruction = build_answer_instruction(
        type("D", (), {"intent": decision.intent, "academic_year": decision.academic_year, "classified_from": "rule"})()
    )

    prompt = UNIFIED_SINGLE_AGENT_PROMPT.format(
        context=context_str,
        retrieval_instruction=retrieval_instruction,
    )
    agent = create_react_agent(model=llm, tools=all_tools, prompt=prompt)

    t0 = time.perf_counter()
    result = await agent.ainvoke({
        "messages": [HumanMessage(content=case.question)],
    })
    latency_ms = (time.perf_counter() - t0) * 1000

    final_msg = result["messages"][-1]
    response = _parse_llm_content(final_msg.content)

    # Count tokens and tool calls
    from langchain_core.messages import ToolMessage
    tool_calls = sum(1 for m in result["messages"] if isinstance(m, ToolMessage))
    input_tokens = sum(
        getattr(m, "usage_metadata", {}).get("input_tokens", 0)
        for m in result["messages"] if hasattr(m, "usage_metadata") and m.usage_metadata
    )
    output_tokens = sum(
        getattr(m, "usage_metadata", {}).get("output_tokens", 0)
        for m in result["messages"] if hasattr(m, "usage_metadata") and m.usage_metadata
    )

    retrieved_sources = [source_from_document(d) for d in context_docs]

    return {
        "config": "S1-A",
        "config_name": "Unified Single Agent",
        "response": response,
        "retrieved_sources": retrieved_sources,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tool_calls": tool_calls,
        "llm_calls": len([m for m in result["messages"] if hasattr(m, "usage_metadata")]),
        "route": "none",
        "route_repair": "N/A",
    }


async def run_full_ctuchat(case: ScenarioCase, services: dict, 
                           *, disable_specialist_policy: bool = False,
                           disable_tool_isolation: bool = False,
                           disable_graph: bool = False,
                           disable_deterministic_calc: bool = False,
                           disable_route_repair: bool = False,
                           config_label: str = "S1-C") -> dict[str, Any]:
    """Run the full CTU-Chat pipeline (or an ablated variant).

    Ablation flags:
      disable_specialist_policy: Use generic prompt for all specialists (S1-B / S2-A1)
      disable_tool_isolation: Give all specialists full tool access (S2-A2)
      disable_graph: Force all evidence through document retrieval (S2-A3)
      disable_deterministic_calc: Skip external calculators (S2-A4)
      disable_route_repair: Skip contract-based route repair (S2-A5)
    """
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langgraph.prebuilt import create_react_agent
    from pydantic import BaseModel, Field
    from typing import Literal

    from app.agents.prompts import (
        ACADEMIC_PROMPT, FINANCIAL_PROMPT, GENERAL_PROMPT,
        SCHOLARSHIP_PROMPT, SUPERVISOR_PROMPT,
    )
    from app.agents.graph import (
        RouteDecision, attach_validation_to_tool, _parse_llm_content,
    )
    from app.services.orchestration_contract import (
        repair_route_decision, tool_gate_prompt, SPECIALIST_TOOLS,
    )
    from app.services.query_intent import (
        classify_query_intent, build_retrieval_lanes, build_answer_instruction,
        QueryRoutingDecision,
    )
    from app.services.tool_execution import recommend_required_tool

    llm = services["llm"]
    graph_service = None if disable_graph else services["graph_service"]

    # ── Tools setup (with or without isolation) ──
    academic_tools = [attach_validation_to_tool(t) for t in services["academic_tools"]]
    financial_tools_raw = services["financial_tools"]
    scholarship_tools_raw = services["scholarship_tools"]

    # Remove deterministic calculators if ablating
    if disable_deterministic_calc:
        financial_tools_raw = [t for t in financial_tools_raw if t.name != "tinh_toan_hoc_phi"]
        scholarship_tools_raw = [t for t in scholarship_tools_raw if t.name != "tinh_tien_hoc_bong"]

    financial_tools = [attach_validation_to_tool(t) for t in financial_tools_raw]
    scholarship_tools = [attach_validation_to_tool(t) for t in scholarship_tools_raw]
    all_tools = academic_tools + financial_tools + scholarship_tools

    # If disabling tool isolation, every specialist sees all tools
    if disable_tool_isolation:
        academic_tools = financial_tools = scholarship_tools = all_tools

    # ── Step 1: Supervisor routing ──
    supervisor_llm = llm.with_structured_output(RouteDecision)
    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=case.question),
    ]

    t0 = time.perf_counter()

    try:
        route: RouteDecision = await supervisor_llm.ainvoke(messages)
        raw_agent = route.next_agent
        raw_intent = route.intent
    except Exception:
        raw_agent = "general"
        raw_intent = "other"

    # Route repair
    if disable_route_repair:
        from app.services.query_intent import QueryIntent
        try:
            intent_enum = QueryIntent(raw_intent)
        except ValueError:
            intent_enum = QueryIntent.OTHER
        next_agent = raw_agent
        intent = intent_enum
        repair_reason = "disabled"
    else:
        repaired = repair_route_decision(case.question, raw_agent, raw_intent)
        next_agent = repaired.agent
        intent = repaired.intent
        repair_reason = repaired.reason

    # ── Step 2: Evidence retrieval ──
    trace = retrieve_configurations(
        case, services["engine"], graph_service,
        services["tuition_catalog"], services["compressor"],
        top_k=TOP_K, metric_k=METRIC_K,
    )
    context_docs = trace.configs.get("T4", [])
    context_str = "\n\n---\n\n".join(
        getattr(doc, "page_content", str(doc)) for doc in context_docs
    ) or "Không có tài liệu liên quan."

    rule_decision = classify_query_intent(case.question)
    routing_decision = QueryRoutingDecision(
        intent=intent,
        academic_year=rule_decision.academic_year,
        classified_from="supervisor",
    )
    retrieval_instruction = build_answer_instruction(routing_decision)

    # ── Step 3: Specialist execution ──
    if disable_specialist_policy:
        specialist_prompt = GENERIC_WORKER_PROMPT.format(
            context=context_str,
            retrieval_instruction=retrieval_instruction,
        )
    else:
        prompt_map = {
            "academic": ACADEMIC_PROMPT,
            "financial": FINANCIAL_PROMPT.format(
                context=context_str, retrieval_instruction=retrieval_instruction,
            ),
            "scholarship": SCHOLARSHIP_PROMPT.format(
                context=context_str, retrieval_instruction=retrieval_instruction,
            ),
            "general": GENERAL_PROMPT.format(
                context=context_str, retrieval_instruction=retrieval_instruction,
            ),
        }
        specialist_prompt = prompt_map.get(next_agent, GENERIC_WORKER_PROMPT.format(
            context=context_str, retrieval_instruction=retrieval_instruction,
        ))

    tool_map = {
        "academic": academic_tools,
        "financial": financial_tools,
        "scholarship": scholarship_tools,
        "general": [],
    }
    specialist_tools = tool_map.get(next_agent, [])

    # Add tool gate prompt
    if not disable_tool_isolation:
        specialist_prompt = f"{specialist_prompt}\n\n{tool_gate_prompt(next_agent)}"

    if next_agent == "academic" and not disable_specialist_policy:
        # Academic uses the prompt from ACADEMIC_PROMPT + ReAct
        agent = create_react_agent(model=llm, tools=specialist_tools, prompt=ACADEMIC_PROMPT)
        gate_msg = SystemMessage(content=tool_gate_prompt("academic"))
        result = await agent.ainvoke({
            "messages": [gate_msg, HumanMessage(content=case.question)],
        })
    elif specialist_tools:
        agent = create_react_agent(model=llm, tools=specialist_tools, prompt=specialist_prompt)
        result = await agent.ainvoke({
            "messages": [HumanMessage(content=case.question)],
        })
    else:
        # General agent — no tools, just LLM + context
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=specialist_prompt),
            ("human", "{question}"),
        ])
        chain = prompt_template | llm | StrOutputParser()
        answer = await chain.ainvoke({"question": case.question})
        result = {"messages": [type("FakeMsg", (), {"content": answer, "usage_metadata": None})()]}

    latency_ms = (time.perf_counter() - t0) * 1000

    final_msg = result["messages"][-1]
    response = _parse_llm_content(final_msg.content)

    tool_call_count = sum(1 for m in result["messages"] if isinstance(m, ToolMessage))
    input_tokens = sum(
        getattr(m, "usage_metadata", {}).get("input_tokens", 0)
        for m in result["messages"] if hasattr(m, "usage_metadata") and m.usage_metadata
    )
    output_tokens = sum(
        getattr(m, "usage_metadata", {}).get("output_tokens", 0)
        for m in result["messages"] if hasattr(m, "usage_metadata") and m.usage_metadata
    )
    retrieved_sources = [source_from_document(d) for d in context_docs]

    return {
        "config": config_label,
        "config_name": _config_display_name(config_label),
        "response": response,
        "retrieved_sources": retrieved_sources,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tool_calls": tool_call_count,
        "llm_calls": 2,  # supervisor + specialist
        "route": next_agent,
        "raw_route": raw_agent,
        "raw_intent": raw_intent,
        "route_repair": repair_reason,
    }


def _config_display_name(label: str) -> str:
    return {
        "S1-A": "Unified Single Agent",
        "S1-B": "Routed Generic Worker",
        "S1-C": "Full CTU-Chat",
        "S2-A0": "Full CTU-Chat (ref)",
        "S2-A1": "No Specialist Policy",
        "S2-A2": "No Tool Isolation",
        "S2-A3": "Uniform Evidence",
        "S2-A4": "No Deterministic Calc",
        "S2-A5": "No Route Repair",
    }.get(label, label)


async def run_config(config: str, case: ScenarioCase, services: dict) -> dict[str, Any]:
    """Dispatch to the appropriate architecture configuration."""
    if config == "S1-A":
        return await run_unified_single_agent(case, services)
    elif config == "S1-B":
        return await run_full_ctuchat(
            case, services,
            disable_specialist_policy=True,
            config_label="S1-B",
        )
    elif config in ("S1-C", "S2-A0"):
        return await run_full_ctuchat(case, services, config_label=config)
    elif config == "S2-A1":
        return await run_full_ctuchat(
            case, services,
            disable_specialist_policy=True,
            config_label="S2-A1",
        )
    elif config == "S2-A2":
        return await run_full_ctuchat(
            case, services,
            disable_tool_isolation=True,
            config_label="S2-A2",
        )
    elif config == "S2-A3":
        return await run_full_ctuchat(
            case, services,
            disable_graph=True,
            config_label="S2-A3",
        )
    elif config == "S2-A4":
        return await run_full_ctuchat(
            case, services,
            disable_deterministic_calc=True,
            config_label="S2-A4",
        )
    elif config == "S2-A5":
        return await run_full_ctuchat(
            case, services,
            disable_route_repair=True,
            config_label="S2-A5",
        )
    else:
        raise ValueError(f"Unknown config: {config}")


# ═══════════════════════════════════════════════════════════════════════
# Evaluation helpers
# ═══════════════════════════════════════════════════════════════════════

def evaluate_run(case: ScenarioCase, result: dict[str, Any]) -> dict[str, Any]:
    """Compute source-level metrics for a single run."""
    src = source_metrics(
        result["retrieved_sources"],
        case.gold_sources,
        top_k=METRIC_K,
        source_relation=case.source_relation,
    )
    # Required-fact coverage (programmatic matching)
    fact_cov = 0.0
    if case.required_facts:
        norm_answer = normalize_text(result["response"])
        matched = sum(
            1 for fact in case.required_facts
            if normalize_text(fact) in norm_answer
        )
        fact_cov = matched / len(case.required_facts)

    return {
        **result,
        "query_id": case.case_id,
        "query_type": case.complexity_tier,
        "domain": case.domain,
        "source_recall": src["source_recall"],
        "source_ap": src["source_ap"],
        "fact_coverage": fact_cov,
        "gold_sources": case.gold_sources,
    }


# ═══════════════════════════════════════════════════════════════════════
# Main runner
# ═══════════════════════════════════════════════════════════════════════

def build_run_record(case: ScenarioCase, result: dict[str, Any], rep: int) -> dict[str, Any]:
    """Build a JSON-serializable log record per the V13 logging schema."""
    return {
        "query_id": case.case_id,
        "configuration": result["config"],
        "configuration_name": result.get("config_name", ""),
        "repetition": rep,
        "query_type": case.complexity_tier,
        "domain": case.domain,
        "question": case.question,
        "raw_route": result.get("raw_route", result.get("route", "")),
        "repaired_route": result.get("route", ""),
        "route_repair_reason": result.get("route_repair", ""),
        "response": result["response"],
        "gold_sources": case.gold_sources,
        "retrieved_sources": result["retrieved_sources"],
        "source_recall": result.get("source_recall", 0.0),
        "source_ap": result.get("source_ap", 0.0),
        "fact_coverage": result.get("fact_coverage", 0.0),
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0),
        "tool_calls": result.get("tool_calls", 0),
        "llm_calls": result.get("llm_calls", 0),
        "latency_ms": result.get("latency_ms", 0.0),
        "reference_answer": case.reference_answer,
        "required_facts": case.required_facts,
    }


async def run_experiment(
    cases: list[ScenarioCase],
    configs: list[str],
    services: dict,
    reps: int,
    output_dir: Path,
):
    """Run all configurations on all cases with repetitions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "results.jsonl"
    total = len(cases) * len(configs) * reps
    completed = 0

    existing_keys = set()
    if log_path.exists():
        with log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        r = json.loads(line)
                        if "query_id" in r and "configuration" in r and "error" not in r:
                            existing_keys.add((r["configuration"], r["query_id"], r.get("repetition", 1)))
                    except Exception:
                        pass
        logger.info("Found %d completed records in %s, skipping them.", len(existing_keys), log_path)

    logger.info(
        "Starting V13 experiment: %d cases × %d configs × %d reps = %d runs",
        len(cases), len(configs), reps, total,
    )

    for config in configs:
        for rep in range(1, reps + 1):
            for case in cases:
                if (config, case.case_id, rep) in existing_keys:
                    completed += 1
                    continue
                try:
                    await asyncio.sleep(0.05)  # Yield CPU and reduce thermal spikes
                    result = await run_config(config, case, services)
                    evaluated = evaluate_run(case, result)
                    record = build_run_record(case, evaluated, rep)

                    with log_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")

                    completed += 1
                    if completed % 10 == 0 or completed == total:
                        logger.info(
                            "Progress: %d/%d (%.1f%%) — config=%s rep=%d",
                            completed, total, 100 * completed / total,
                            config, rep,
                        )
                except Exception as exc:
                    logger.error(
                        "FAILED config=%s case=%s rep=%d: %s",
                        config, case.case_id, rep, exc,
                    )
                    error_record = {
                        "query_id": case.case_id,
                        "configuration": config,
                        "repetition": rep,
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    }
                    with log_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(error_record, ensure_ascii=False) + "\n")
                    completed += 1

    logger.info("Experiment complete. Results: %s", log_path)
    return log_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V13 Architecture Experiment Runner")
    parser.add_argument(
        "--scenario", choices=["s1", "s2", "both"], default="both",
        help="Which scenario to run (s1=architecture comparison, s2=ablation, both=all)",
    )
    parser.add_argument(
        "--configs", nargs="*", default=None,
        help="Specific configs to run (e.g., S1-A S1-C). Overrides --scenario.",
    )
    parser.add_argument(
        "--reps", type=int, default=3,
        help="Repetitions per query per config (default: 3)",
    )
    parser.add_argument(
        "--dataset", type=str, default=str(HELDOUT_DATASET),
        help="Path to held-out dataset",
    )
    parser.add_argument(
        "--project", type=str, default=None,
        help="Google Cloud project ID",
    )
    parser.add_argument(
        "--arithmetic-only", action="store_true",
        help="For S2-A4, only run on arithmetic-query subset",
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Path to output directory (for resuming an existing run)",
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    project = configure_vertex(SERVICE_ACCOUNT, args.project)
    logger.info("Using Vertex AI project: %s", project)

    # Load cases
    dataset_path = Path(args.dataset)
    cases = load_cases(dataset_path)
    logger.info("Loaded %d cases from %s", len(cases), dataset_path)

    # Determine configs
    if args.configs:
        configs = args.configs
    elif args.scenario == "s1":
        configs = list(SCENARIO_1_CONFIGS)
    elif args.scenario == "s2":
        configs = list(SCENARIO_2_CONFIGS)
    else:
        # 'both': run S1 + S2 (S2-A0 reuses S1-C data, S2-A1 reuses S1-B)
        configs = ["S1-A", "S1-B", "S1-C", "S2-A2", "S2-A3", "S2-A4", "S2-A5"]

    # For S2-A4, filter to arithmetic cases only
    if args.arithmetic_only and "S2-A4" in configs:
        arith_cases = [c for c in cases if any(
            kw in normalize_text(c.question) for kw in ("tinh tien", "bao nhieu tien", "tinh hoc phi", "mien giam")
        )]
        logger.info("Arithmetic subset: %d/%d cases", len(arith_cases), len(cases))
        # Run non-A4 configs on full cases, A4 on arithmetic subset
        # For simplicity, just filter when A4 is the only config
        if configs == ["S2-A4"]:
            cases = arith_cases

    # Init services
    logger.info("Initializing services...")
    services = init_services()
    logger.info("Services initialized.")

    # Output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
        timestamp = output_dir.name.replace("run_", "")
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_dir = LOG_ROOT / f"run_{timestamp}"

    # Save experiment metadata
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "timestamp": timestamp,
        "model": MODEL,
        "temperature": TEMPERATURE,
        "top_k": TOP_K,
        "reps": args.reps,
        "configs": configs,
        "dataset": str(dataset_path),
        "dataset_size": len(cases),
        "scenario": args.scenario,
        "project": project,
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Run
    log_path = await run_experiment(cases, configs, services, args.reps, output_dir)

    # Summary
    logger.info("=" * 60)
    logger.info("V13 Experiment Complete")
    logger.info("Results: %s", log_path)
    logger.info("Metadata: %s", output_dir / "metadata.json")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
