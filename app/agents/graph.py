"""
Multi-Agent Graph sử dụng LangGraph.
Kiến trúc: Supervisor Pattern với 4 Agent chuyên môn.

Flow:
  START → supervisor → (routing) → [retrieval?] → agent → END
"""

from __future__ import annotations

import logging
import operator
from typing import Annotated, Any, Literal, Sequence

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from app.agents.prompts import (
    ACADEMIC_PROMPT,
    FINANCIAL_PROMPT,
    GENERAL_PROMPT,
    SCHOLARSHIP_PROMPT,
    SUPERVISOR_PROMPT,
)
from app.services.query_intent import (
    QueryIntent,
    QueryRoutingDecision,
    build_answer_instruction,
    build_retrieval_lanes,
    should_rewrite_query,
    validate_rewritten_query,
)

logger = logging.getLogger(__name__)

def _parse_llm_content(content: Any) -> str:
    """Helper to parse Gemini list content format into a single string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            block.get("text", "") for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)

# ─────────────────────────────────────────────────────────────────────
# 1. STATE DEFINITION
# ─────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """Trạng thái chia sẻ giữa các nodes trong graph."""
    # Input gốc
    query: str                           # Câu hỏi gốc
    chat_history: list[BaseMessage]      # Lịch sử hội thoại

    # Supervisor output
    search_query: str                    # Câu hỏi đã rewrite
    next_agent: str                      # academic | financial | scholarship | general
    routing_decision: Any                # QueryRoutingDecision (cho retrieval)

    # Retrieval output
    context: str                         # Context từ RAG
    retrieval_instruction: str           # Hướng dẫn cho agent

    # Final output
    response: str                        # Câu trả lời cuối cùng


# ─────────────────────────────────────────────────────────────────────
# 2. SUPERVISOR ROUTING SCHEMA
# ─────────────────────────────────────────────────────────────────────

class RouteDecision(BaseModel):
    """Structured output cho Supervisor routing — agent + intent."""
    next_agent: Literal["academic", "financial", "scholarship", "general"] = Field(
        description="Tên agent chuyên môn sẽ xử lý câu hỏi này"
    )
    intent: Literal[
        "actual_tuition", "exemption_basis", "exemption_policy",
        "calculation", "both", "ambiguous_tuition",
        "scholarship",
        "student_loan", "social_support",
        "academic_program", "academic_rules", "quy_che_general",
        "other",
    ] = Field(
        description="Phân loại chi tiết nội dung câu hỏi để chọn đúng loại tài liệu retrieval"
    )


# Mapping intent string → QueryIntent enum
_INTENT_MAP: dict[str, QueryIntent] = {e.value: e for e in QueryIntent}


# ─────────────────────────────────────────────────────────────────────
# 4. BUILD GRAPH FUNCTION
# ─────────────────────────────────────────────────────────────────────

def build_agent_graph(
    llm,
    rewrite_llm,
    engine,
    tuition_catalog,
    graph_service,
    academic_tools: list,
    financial_tools: list,
    scholarship_tools: list,
):
    """Xây dựng LangGraph StateGraph cho Multi-Agent System.

    Args:
        llm: LLM chính (Gemini) dùng cho tất cả agents.
        rewrite_llm: LLM phụ dùng cho query rewrite.
        engine: RAG engine (Qdrant + BM25).
        tuition_catalog: Catalog tra cứu học phí cấu trúc.
        graph_service: AcademicGraphService instance (Neo4j).
        academic_tools: Danh sách tools cho Academic Agent.
        financial_tools: Danh sách tools cho Financial Agent.
        scholarship_tools: Danh sách tools cho Scholarship Agent.
    """

    # --- Structured LLM cho Supervisor routing ---
    supervisor_llm = llm.with_structured_output(RouteDecision)

    # --- ReAct Agents ---
    academic_agent = create_react_agent(
        model=llm,
        tools=academic_tools,
        prompt=ACADEMIC_PROMPT,
    )

    # ─────────────────────────────────────────────────────────────
    # NODE: supervisor
    # ─────────────────────────────────────────────────────────────
    async def supervisor_node(state: AgentState) -> dict:
        """Supervisor: Query Rewrite → Phân tích Intent → Chọn Agent."""
        query = state["query"]
        chat_history = state.get("chat_history", [])

        # ── Query Rewrite ──
        previous_user_query = next(
            (m.content for m in reversed(chat_history) if isinstance(m, HumanMessage)),
            None,
        )
        search_query = query

        if should_rewrite_query(query, previous_user_query):
            rewrite_prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "Bạn chỉ làm rõ đại từ hoặc phần bị lược bỏ trong câu hỏi hiện tại "
                    "bằng câu hỏi trước đó của người dùng. Không thêm ngân hàng, học bổng, "
                    "chương trình đào tạo, ngành, khóa, năm học, chính sách, con số hoặc "
                    "điều kiện không có trong hai câu. Không trả lời. Chỉ in một câu truy vấn.",
                ),
                (
                    "human",
                    "Câu hỏi trước của người dùng: {previous_user_query}\n"
                    "Câu hỏi hiện tại: {question}\n"
                    "Câu truy vấn độc lập:",
                ),
            ])
            rewrite_chain = rewrite_prompt | rewrite_llm | StrOutputParser()
            try:
                candidate = await rewrite_chain.ainvoke({
                    "previous_user_query": previous_user_query,
                    "question": query,
                })
                candidate = candidate.strip().strip('"').strip("'")
                accepted, reason = validate_rewritten_query(
                    original_query=query,
                    rewritten_query=candidate,
                    previous_user_query=previous_user_query,
                )
                if accepted:
                    search_query = candidate
                    logger.info("Query rewrite status=accepted search=%r", search_query)
                else:
                    logger.info("Query rewrite status=rejected reason=%s", reason)
            except Exception as e:
                logger.warning("Query rewriter lỗi: %s", type(e).__name__)

        # ── Routing Decision ──
        messages = [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=query),
        ]
        try:
            route: RouteDecision = await supervisor_llm.ainvoke(messages)
            next_agent = route.next_agent
        except Exception as e:
            logger.warning("Supervisor routing lỗi, fallback general: %s", e)
            next_agent = "general"

        # ── Intent (từ LLM structured output) → QueryRoutingDecision ──
        intent = _INTENT_MAP.get(route.intent, QueryIntent.OTHER)
        routing_decision = QueryRoutingDecision(intent=intent)

        logger.info(
            "🎯 Supervisor: query=%r → agent=%s (intent=%s)",
            query, next_agent, intent.value,
        )

        return {
            "search_query": search_query,
            "next_agent": next_agent,
            "routing_decision": routing_decision,
        }

    # ─────────────────────────────────────────────────────────────
    # NODE: retrieval (cho financial, scholarship, general)
    # ─────────────────────────────────────────────────────────────
    async def retrieval_node(state: AgentState) -> dict:
        """RAG Retrieval: Qdrant + BM25 hybrid search."""
        search_query = state["search_query"]
        query = state["query"]
        routing_decision = state["routing_decision"]
        next_agent = state["next_agent"]

        docs = []
        structured_context_blocks = []
        missing_lanes = []
        retrieval_instruction = build_answer_instruction(routing_decision)

        # ── Tra cứu học phí cấu trúc (nếu financial) ──
        # Ưu tiên: Neo4j graph → JSON TuitionRateCatalog fallback
        lookup_result = None
        graph_found = False
        if next_agent == "financial" and graph_service is not None:
            try:
                graph_results = graph_service.lookup_tuition(query)
                if not graph_results and search_query.strip() != query.strip():
                    graph_results = graph_service.lookup_tuition(search_query)
                if graph_results:
                    from app.tools.tuition_graph import _format_graph_results
                    structured_context_blocks.append(_format_graph_results(graph_results))
                    logger.info("Tra cứu học phí từ graph thành công: %d kết quả", len(graph_results))
                    graph_found = True
            except Exception as e:
                logger.warning("Graph tuition lookup lỗi, fallback JSON: %s", e)

        # Fallback: JSON TuitionRateCatalog nếu graph không tìm thấy
        if next_agent == "financial" and not graph_found:
            lookup_result = tuition_catalog.lookup(query)
            if (
                lookup_result.status in {"needs_clarification", "not_found"}
                and search_query.strip() != query.strip()
                and tuition_catalog.rewrite_is_safe_for_lookup(query, search_query)
            ):
                rewritten_lookup = tuition_catalog.lookup(search_query)
                if rewritten_lookup.status == "found":
                    lookup_result = rewritten_lookup
            if lookup_result.status == "found":
                structured_context_blocks.append(lookup_result.message)
                logger.info("Tra cứu học phí từ JSON fallback thành công records=%d", len(lookup_result.records))

        # ── RAG Retrieval ──
        lanes = build_retrieval_lanes(routing_decision)
        for lane in lanes:
            if lane.name == "actual_tuition" and lookup_result and lookup_result.status == "found":
                continue
            lane_docs = engine.retrieve(
                search_query,
                lane=lane.name,
                fee_kind=lane.fee_kind,
                content_kind=lane.content_kind,
                domain=lane.domain,
                top_n=lane.top_n,
                metadata_filter_enabled=True,
            )
            if not lane_docs:
                missing_lanes.append(lane.name)
            for doc in lane_docs:
                doc.metadata = dict(doc.metadata)
                doc.metadata["retrieval_lane"] = lane.name
            docs.extend(lane_docs)

        # ── Deduplicate ──
        seen = set()
        unique_docs = []
        for doc in docs:
            key = doc.metadata.get("doc_id") or (doc.metadata.get("source"), doc.page_content)
            if key not in seen:
                seen.add(key)
                unique_docs.append(doc)
        docs = unique_docs

        # ── Build context string ──
        context_blocks = list(structured_context_blocks)
        for doc in docs:
            headers = [str(v) for k, v in doc.metadata.items() if k.startswith("Header_")]
            header_prefix = "Chuyên mục: " + " > ".join(headers) + "\n" if headers else ""
            fee_kind_label = {
                "actual_tuition": "HỌC PHÍ THỰC TẾ",
                "exemption_basis": "CƠ SỞ TÍNH MIỄN GIẢM",
            }.get(doc.metadata.get("fee_kind"), "")
            metadata_prefix = (
                f"[LOẠI: {fee_kind_label} | "
                f"NĂM HỌC: {doc.metadata.get('academic_year', 'không xác định')} | "
                f"NGUỒN: {doc.metadata.get('source', 'Tài liệu')}]\n"
            )
            context_blocks.append(f"{metadata_prefix}{header_prefix}{doc.page_content}")

        # ── Missing lanes warning ──
        lane_labels = {
            "actual_tuition": "học phí thực tế",
            "exemption_basis": "mức làm cơ sở tính miễn, giảm",
            "exemption_policy": "chính sách miễn, giảm",
            "scholarship": "tài liệu học bổng",
            "student_loan": "tài liệu vay vốn sinh viên",
            "default": "tài liệu phù hợp",
        }
        if missing_lanes:
            missing_text = ", ".join(lane_labels.get(n, n) for n in missing_lanes)
            retrieval_instruction += (
                f" Hệ thống không tìm thấy {missing_text}; "
                "phải nói rõ là không tìm thấy và không dùng loại khác thay thế."
            )

        context_str = "\n\n---\n\n".join(context_blocks) if context_blocks else "Không có tài liệu liên quan."

        # ── Logging ──
        source_icons = {"vector": "🔵", "bm25": "🟢", "vector+bm25": "🟡"}
        logger.info("📄 Retrieved %d docs cho query: '%s'", len(docs), search_query)
        src_counts: dict = {}
        for doc in docs:
            rs = doc.metadata.get("retrieval_source", "unknown")
            src_counts[rs] = src_counts.get(rs, 0) + 1
        src_summary = " | ".join(
            f"{source_icons.get(s, '⚪')}{s}: {c}" for s, c in src_counts.items()
        )
        logger.info("📊 Nguồn retrieval: %s", src_summary)

        return {
            "context": context_str,
            "retrieval_instruction": retrieval_instruction,
        }

    # ─────────────────────────────────────────────────────────────
    # NODE: academic_agent
    # ─────────────────────────────────────────────────────────────
    async def academic_agent_node(state: AgentState) -> dict:
        """Academic Agent: ReAct loop với Neo4j graph tools."""
        query = state["query"]
        chat_history = state.get("chat_history", [])

        result = await academic_agent.ainvoke({
            "messages": [*chat_history, HumanMessage(content=query)],
        })

        # Lấy message cuối cùng từ ReAct agent
        final_msg = result["messages"][-1]
        response = _parse_llm_content(final_msg.content)

        logger.info("🔵 Academic Agent hoàn thành: %d chars", len(response))
        return {"response": response}

    # ─────────────────────────────────────────────────────────────
    # NODE: financial_agent
    # ─────────────────────────────────────────────────────────────
    async def financial_agent_node(state: AgentState) -> dict:
        """Financial Agent: RAG context + calc tools."""
        query = state["query"]
        context = state.get("context", "")
        retrieval_instruction = state.get("retrieval_instruction", "")
        chat_history = state.get("chat_history", [])

        prompt = FINANCIAL_PROMPT.format(
            context=context,
            retrieval_instruction=retrieval_instruction,
        )
        financial_agent = create_react_agent(
            model=llm,
            tools=financial_tools,
            prompt=prompt,
        )
        result = await financial_agent.ainvoke({
            "messages": [*chat_history, HumanMessage(content=query)],
        })

        final_msg = result["messages"][-1]
        response = _parse_llm_content(final_msg.content)

        logger.info("🟡 Financial Agent hoàn thành: %d chars", len(response))
        return {"response": response}

    # ─────────────────────────────────────────────────────────────
    # NODE: scholarship_agent
    # ─────────────────────────────────────────────────────────────
    async def scholarship_agent_node(state: AgentState) -> dict:
        """Scholarship Agent: RAG context + scholarship calc tool."""
        query = state["query"]
        context = state.get("context", "")
        retrieval_instruction = state.get("retrieval_instruction", "")
        chat_history = state.get("chat_history", [])

        prompt = SCHOLARSHIP_PROMPT.format(
            context=context,
            retrieval_instruction=retrieval_instruction,
        )
        scholarship_agent = create_react_agent(
            model=llm,
            tools=scholarship_tools,
            prompt=prompt,
        )
        result = await scholarship_agent.ainvoke({
            "messages": [*chat_history, HumanMessage(content=query)],
        })

        final_msg = result["messages"][-1]
        response = _parse_llm_content(final_msg.content)

        logger.info("🟣 Scholarship Agent hoàn thành: %d chars", len(response))
        return {"response": response}

    # ─────────────────────────────────────────────────────────────
    # NODE: general_agent
    # ─────────────────────────────────────────────────────────────
    async def general_agent_node(state: AgentState) -> dict:
        """General Agent: RAG context, no tools."""
        query = state["query"]
        context = state.get("context", "")
        retrieval_instruction = state.get("retrieval_instruction", "")
        chat_history = state.get("chat_history", [])

        prompt = ChatPromptTemplate.from_messages([
            ("system", GENERAL_PROMPT.format(
                context=context,
                retrieval_instruction=retrieval_instruction,
            )),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])
        chain = prompt | llm | StrOutputParser()
        response = await chain.ainvoke({
            "chat_history": chat_history,
            "question": query,
        })
        response = _parse_llm_content(response)

        logger.info("🟠 General Agent hoàn thành: %d chars", len(response))
        return {"response": response}

    # ─────────────────────────────────────────────────────────────
    # 5. ROUTING FUNCTIONS
    # ─────────────────────────────────────────────────────────────
    def route_after_supervisor(state: AgentState) -> str:
        """Quyết định node tiếp theo sau Supervisor."""
        next_agent = state["next_agent"]
        if next_agent == "academic":
            return "academic_agent"
        # financial, scholarship, general đều cần retrieval trước
        return "retrieval"

    def route_after_retrieval(state: AgentState) -> str:
        """Sau retrieval, chuyển đến agent chuyên môn."""
        next_agent = state["next_agent"]
        return f"{next_agent}_agent"

    # ─────────────────────────────────────────────────────────────
    # 6. BUILD GRAPH
    # ─────────────────────────────────────────────────────────────
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("academic_agent", academic_agent_node)
    graph.add_node("financial_agent", financial_agent_node)
    graph.add_node("scholarship_agent", scholarship_agent_node)
    graph.add_node("general_agent", general_agent_node)

    # Add edges
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route_after_supervisor, {
        "academic_agent": "academic_agent",
        "retrieval": "retrieval",
    })
    graph.add_conditional_edges("retrieval", route_after_retrieval, {
        "financial_agent": "financial_agent",
        "scholarship_agent": "scholarship_agent",
        "general_agent": "general_agent",
    })
    graph.add_edge("academic_agent", END)
    graph.add_edge("financial_agent", END)
    graph.add_edge("scholarship_agent", END)
    graph.add_edge("general_agent", END)

    compiled = graph.compile()
    logger.info("✅ Multi-Agent Graph compiled: 6 nodes, Supervisor pattern")
    return compiled
