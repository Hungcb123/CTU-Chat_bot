import json
import logging
import os
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
import redis.asyncio as redis
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.models.pydantic import ChatRequest, ChatResponse
from app.tools.scholarship import tinh_tien_hoc_bong
from app.tools.tuition import tinh_toan_hoc_phi

# Imports cho PostgreSQL
from app.core.database import AsyncSessionLocal
from app.models.schema import ChatSession, ChatMessage, User, generate_uuid
from sqlalchemy.sql import func
from app.api.auth import get_current_user
from app.services.query_intent import (
    QueryIntent,
    build_answer_instruction,
    build_retrieval_lanes,
    classify_query_intent,
    should_rewrite_query,
    validate_rewritten_query,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def _deduplicate_documents(documents):
    unique = []
    seen = set()
    for doc in documents:
        key = doc.metadata.get("doc_id") or (
            doc.metadata.get("source"),
            doc.page_content,
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(doc)
    return unique

async def save_message_to_postgres(session_id: str, human_query: str, ai_response: str, user_id: str):
    try:
        async with AsyncSessionLocal() as db:
            session = await db.get(ChatSession, session_id)
            if not session:
                title = human_query[:50] + ("..." if len(human_query) > 50 else "")
                session = ChatSession(id=session_id, user_id=user_id, title=title)
                db.add(session)
            else:
                session.updated_at = func.now()
                
            # Lưu 2 dòng tin nhắn
            hm = ChatMessage(session_id=session_id, role="human", content=human_query)
            am = ChatMessage(session_id=session_id, role="ai", content=ai_response)
            db.add_all([hm, am])
            await db.commit()
    except Exception as e:
        logger.error(f"Lỗi khi lưu DB dài hạn: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, fast_req: Request, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    redis_client: redis.Redis = fast_req.app.state.redis_client
    engine = fast_req.app.state.engine
    llm = fast_req.app.state.llm
    rewrite_llm = fast_req.app.state.rewrite_llm
    chat_prompt = fast_req.app.state.chat_prompt
    llm_with_tools = fast_req.app.state.llm_with_tools
    tuition_catalog = fast_req.app.state.tuition_catalog
    
    if request.session_id:
        session_id = request.session_id
    else:
        session_id = generate_uuid()
        
    history_key = f"user:{current_user.id}:session:{session_id}:history"
    
    try:
        # --- BƯỚC 1: TRUY XUẤT 5 TIN NHẮN GẦN NHẤT ---
        raw_history = await redis_client.lrange(history_key, -5, -1)
        
        chat_history = []
        for msg_str in raw_history:
            msg_dict = json.loads(msg_str)
            if msg_dict["role"] == "human":
                chat_history.append(HumanMessage(content=msg_dict["content"]))
            elif msg_dict["role"] == "ai":
                chat_history.append(AIMessage(content=msg_dict["content"]))
                
        logger.info(f"Đã nạp {len(chat_history)} tin nhắn lịch sử từ Redis.")

        # --- BƯỚC 1.5: CHỈ LÀM RÕ FOLLOW-UP THẬT SỰ MƠ HỒ ---
        # Câu hỏi rõ được giữ nguyên. Không đưa câu trả lời AI vào rewriter vì
        # nội dung sinh trước đó có thể truyền thêm thực thể sai sang retrieval.
        previous_user_query = next(
            (
                message.content
                for message in reversed(chat_history)
                if isinstance(message, HumanMessage)
            ),
            None,
        )
        search_query = request.query
        rewrite_status = "skipped"
        rewrite_reason = "clear_original_query"

        if should_rewrite_query(request.query, previous_user_query):
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
                    "question": request.query,
                })
                candidate = candidate.strip().strip('"').strip("'")
                accepted, rewrite_reason = validate_rewritten_query(
                    original_query=request.query,
                    rewritten_query=candidate,
                    previous_user_query=previous_user_query,
                )
                if accepted:
                    search_query = candidate
                    rewrite_status = "accepted"
                else:
                    rewrite_status = "rejected"
            except Exception as rewrite_error:
                rewrite_status = "rejected"
                rewrite_reason = f"rewriter_error:{type(rewrite_error).__name__}"
                logger.warning(
                    "Query rewriter lỗi; fallback về câu gốc (%s)",
                    type(rewrite_error).__name__,
                )

        logger.info(
            "Query rewrite status=%s reason=%s original=%r search=%r",
            rewrite_status,
            rewrite_reason,
            request.query,
            search_query,
        )

        # --- BƯỚC 2: ĐỊNH TUYẾN Ý ĐỊNH & RÚT TRÍCH TÀI LIỆU ---
        routing_decision = classify_query_intent(request.query, search_query)
        metadata_filter_enabled = _env_flag("RAG_METADATA_FILTER_ENABLED", default=False)
        no_result_response = None
        missing_lanes = []
        structured_context_blocks = []

        lookup_result = None
        if routing_decision.intent in {
            QueryIntent.ACTUAL_TUITION,
            QueryIntent.CALCULATION,
            QueryIntent.BOTH,
            QueryIntent.AMBIGUOUS_TUITION,
        }:
            lookup_result = tuition_catalog.lookup(request.query)
            lookup_source = "original"
            if (
                lookup_result.status in {"needs_clarification", "not_found"}
                and search_query.strip() != request.query.strip()
                and tuition_catalog.rewrite_is_safe_for_lookup(request.query, search_query)
            ):
                rewritten_lookup = tuition_catalog.lookup(search_query)
                if rewritten_lookup.status == "found":
                    lookup_result = rewritten_lookup
                    lookup_source = "rewrite"
            if lookup_result.status == "found":
                structured_context_blocks.append(lookup_result.message)
                logger.info(
                    "Tra cứu học phí cấu trúc thành công source=%s records=%d",
                    lookup_source,
                    len(lookup_result.records),
                )
            elif (
                lookup_result.status in {"needs_clarification", "not_found"}
                and routing_decision.intent is QueryIntent.ACTUAL_TUITION
            ):
                no_result_response = lookup_result.message

        if no_result_response is not None:
            docs = []
            retrieval_instruction = build_answer_instruction(routing_decision)
        elif (
            lookup_result is not None
            and lookup_result.status == "found"
            and routing_decision.intent is QueryIntent.ACTUAL_TUITION
        ):
            # Exact monetary lookup is authoritative and must not be diluted by
            # semantically similar table/rule chunks, even during a rollout
            # where metadata filtering is temporarily disabled.
            docs = []
            retrieval_instruction = build_answer_instruction(routing_decision)
        elif metadata_filter_enabled:
            docs = []
            for lane in build_retrieval_lanes(routing_decision):
                if lane.name == "actual_tuition" and lookup_result is not None and lookup_result.status == "found":
                    continue
                lane_docs = engine.retrieve(
                    search_query,
                    lane=lane.name,
                    fee_kind=lane.fee_kind,
                    content_kind=lane.content_kind,
                    domain=lane.domain,
                    academic_year=routing_decision.academic_year,
                    top_n=lane.top_n,
                    metadata_filter_enabled=True,
                )
                if not lane_docs:
                    missing_lanes.append(lane.name)
                for doc in lane_docs:
                    doc.metadata = dict(doc.metadata)
                    doc.metadata["retrieval_lane"] = lane.name
                docs.extend(lane_docs)
            docs = _deduplicate_documents(docs)
            retrieval_instruction = build_answer_instruction(routing_decision)
            lane_labels = {
                "actual_tuition": "học phí thực tế",
                "exemption_basis": "mức làm cơ sở tính miễn, giảm",
                "exemption_policy": "chính sách miễn, giảm",
                "scholarship": "tài liệu học bổng",
                "student_loan": "tài liệu vay vốn sinh viên",
                "default": "tài liệu phù hợp",
            }
            if missing_lanes:
                missing_text = ", ".join(
                    lane_labels.get(name, name) for name in missing_lanes
                )
                year_text = (
                    f" cho năm học {routing_decision.academic_year}"
                    if routing_decision.academic_year
                    else ""
                )
                retrieval_instruction += (
                    f" Hệ thống không tìm thấy {missing_text}{year_text}; "
                    "phải nói rõ là không tìm thấy và không dùng loại khác thay thế."
                )
            if not docs and not structured_context_blocks:
                year_text = (
                    f" cho năm học {routing_decision.academic_year}"
                    if routing_decision.academic_year
                    else ""
                )
                requested_text = ", ".join(
                    lane_labels.get(name, name) for name in missing_lanes
                ) or "tài liệu phù hợp"
                no_result_response = (
                    f"Không tìm thấy {requested_text}{year_text} trong kho tài liệu đang hoạt động."
                )
        else:
            docs = engine.retriever.invoke(search_query)
            retrieval_instruction = (
                "Metadata filter đang tắt trong giai đoạn rollout; trả lời theo ngữ cảnh và "
                "vẫn phải phân biệt học phí thực tế với cơ sở tính miễn giảm."
            )

        logger.info(
            "Định tuyến query intent=%s source=%s year=%s metadata_filter=%s docs=%s",
            routing_decision.intent.value,
            routing_decision.classified_from,
            routing_decision.academic_year,
            metadata_filter_enabled,
            len(docs),
        )
        
        # --- DEBUG LOG: Ghi lại 6 Parent Documents được Reranker chọn ---
        try:
            import os
            from datetime import datetime
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "retrieved_docs.log")
            
            log_lines = []
            log_lines.append(f"\n{'='*80}")
            log_lines.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] QUERY GỐC: {request.query}")
            log_lines.append(f"[REWRITE STATUS]: {rewrite_status} ({rewrite_reason})")
            log_lines.append(f"[SEARCH QUERY]: {search_query}")
            log_lines.append(f"[SỐ LƯỢNG DOCS TRẢ VỀ]: {len(docs)}")
            log_lines.append(f"{'-'*80}")
            
            for i, doc in enumerate(docs):
                source = doc.metadata.get('source', 'N/A')
                headers = {k: v for k, v in doc.metadata.items() if k.startswith("Header_")}
                effective_date = doc.metadata.get('effective_date', 'N/A')
                preview = doc.page_content[:1200].replace('\n', ' ')
                
                log_lines.append(
                    f"  [{i+1}] Source: {source} | Date: {effective_date} | "
                    f"FeeKind: {doc.metadata.get('fee_kind', 'N/A')} | "
                    f"Lane: {doc.metadata.get('retrieval_lane', 'default')} | "
                    f"Index: {doc.metadata.get('index_version', 'N/A')}"
                )
                log_lines.append(f"      Headers: {headers}")
                log_lines.append(f"      Preview: {preview}...")
                log_lines.append(f"      Length: {len(doc.page_content)} chars")
                log_lines.append("")
                
            log_lines.append(f"{'='*80}\n")
            log_text = "\n".join(log_lines)
            
            # Ghi ra console log
            logger.info(f"📄 Retrieved {len(docs)} Parent Docs cho query: '{request.query}'")
            for i, doc in enumerate(docs):
                logger.info(f"  Doc [{i+1}]: {doc.metadata.get('source', '?')} | {doc.page_content[:120]}...")
            
            # Ghi ra file (append mode)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_text)
        except Exception as debug_err:
            logger.warning(f"⚠️ Debug log ghi thất bại (không ảnh hưởng hệ thống): {debug_err}")
        
        # Ghép nội dung và tiêm lại Header từ Metadata để LLM không bị mất bối cảnh ở các đoạn bị cắt ngang
        context_blocks = list(structured_context_blocks)
        for doc in docs:
            headers = [str(v) for k, v in doc.metadata.items() if k.startswith("Header_")]
            header_prefix = "Chuyên mục: " + " > ".join(headers) + "\n" if headers else ""
            fee_kind_label = {
                "actual_tuition": "HỌC PHÍ THỰC TẾ",
                "exemption_basis": "CƠ SỞ TÍNH MIỄN GIẢM",
                "not_applicable": "KHÔNG ÁP DỤNG LOẠI HỌC PHÍ",
            }.get(doc.metadata.get("fee_kind"), "KHÔNG PHÂN LOẠI")
            metadata_prefix = (
                f"[LOẠI: {fee_kind_label} | "
                f"NĂM HỌC: {doc.metadata.get('academic_year') or 'không xác định'} | "
                f"NGUỒN: {doc.metadata.get('source', 'Tài liệu')}]\n"
            )
            context_blocks.append(f"{metadata_prefix}{header_prefix}{doc.page_content}")
        if metadata_filter_enabled:
            missing_context_labels = {
                "actual_tuition": "HỌC PHÍ THỰC TẾ",
                "exemption_basis": "CƠ SỞ TÍNH MIỄN GIẢM",
                "exemption_policy": "CHÍNH SÁCH MIỄN GIẢM",
                "scholarship": "HỌC BỔNG",
                "student_loan": "VAY VỐN SINH VIÊN",
                "default": "TÀI LIỆU PHÙ HỢP",
            }
            for lane_name in missing_lanes:
                context_blocks.append(
                    f"[LOẠI: {missing_context_labels.get(lane_name, lane_name)} | "
                    f"NĂM HỌC: {routing_decision.academic_year or 'không xác định'}]\n"
                    "KHÔNG TÌM THẤY DỮ LIỆU ĐÚNG LANE/NĂM HỌC."
                )
            
        context_str = "\n\n---\n\n".join(context_blocks)

        # --- BƯỚC 3: GỌI LLM GEMINI VÀ XỬ LÝ TOOL ---
        chain_input = {
            "context": context_str,
            "retrieval_instruction": retrieval_instruction,
            "chat_history": chat_history,
            "question": request.query # Lưu ý: Vẫn giữ lại câu hỏi gốc cho Gemini để nó phản hồi tự nhiên hơn
        }
        
        response_msg = None
        if no_result_response is None:
            rag_chain = chat_prompt | llm_with_tools
            response_msg = await rag_chain.ainvoke(chain_input)

        if no_result_response is not None:
            ai_response = no_result_response
        elif response_msg.tool_calls:
            logger.info(f"Gemini đã kích hoạt Tool: {response_msg.tool_calls}")
            
            prompt_value = await chat_prompt.ainvoke(chain_input)
            messages = prompt_value.to_messages()
            messages.append(response_msg) 
            
            for tool_call in response_msg.tool_calls:
                if tool_call["name"] == "tinh_tien_hoc_bong":
                    tool_result_str = tinh_tien_hoc_bong.invoke(tool_call["args"])
                    messages.append(ToolMessage(
                        content=tool_result_str,
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"]
                    ))
                elif tool_call["name"] == "tinh_toan_hoc_phi":
                    tool_result_str = tinh_toan_hoc_phi.invoke(tool_call["args"])
                    messages.append(ToolMessage(
                        content=tool_result_str,
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"]
                    ))
                else:
                    messages.append(ToolMessage(
                        content="Lỗi: Không tìm thấy công cụ này.",
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"]
                    ))
            
            final_response = await llm.ainvoke(messages)
            
            if isinstance(final_response.content, list):
                ai_response = " ".join(block.get("text", "") for block in final_response.content if isinstance(block, dict) and block.get("type") == "text")
            else:
                ai_response = str(final_response.content)
                
            if not ai_response.strip():
                ai_response = "Hệ thống đã tính toán xong nhưng gặp lỗi khi diễn đạt."
        else:
            if isinstance(response_msg.content, list):
                ai_response = " ".join(block.get("text", "") for block in response_msg.content if isinstance(block, dict) and block.get("type") == "text")
            else:
                ai_response = str(response_msg.content)

        # --- BƯỚC 4: LƯU LỊCH SỬ ---
        human_msg = json.dumps({"role": "human", "content": request.query})
        ai_msg = json.dumps({"role": "ai", "content": ai_response})
        
        await redis_client.rpush(history_key, human_msg, ai_msg)
        await redis_client.ltrim(history_key, -50, -1)

        # Lưu vào PostgreSQL (Dài hạn) ở chế độ chạy ngầm
        background_tasks.add_task(save_message_to_postgres, session_id, request.query, ai_response, current_user.id)

        return ChatResponse(answer=ai_response, session_id=session_id)

    except redis.RedisError as re:
        logger.error(f"Lỗi thao tác trên Redis: {str(re)}", exc_info=True)
        raise HTTPException(status_code=502, detail="Hệ thống cache tạm thời gián đoạn.")
    except Exception as e:
        logger.error(f"Lỗi hệ thống khi sinh câu trả lời: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra trong quá trình xử lý câu hỏi.")
