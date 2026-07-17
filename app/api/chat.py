import json
import logging
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

logger = logging.getLogger(__name__)

router = APIRouter()

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

        # --- BƯỚC 1.5: ĐỊNH HÌNH LẠI CÂU HỎI VÀ MỞ RỘNG TRUY VẤN (QUERY EXPANSION) BẰNG Llama ---
        # Luôn chạy để đảm bảo các câu hỏi chung chung được mở rộng từ khóa, giúp Vector Search bắt trúng tài liệu
        history_text = "Không có lịch sử."
        if chat_history:
            history_text = "\n".join([f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}" for m in chat_history])
            
        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một chuyên gia ngôn ngữ học và kỹ sư tối ưu tìm kiếm (Prompt Engineer). Nhiệm vụ của bạn là VIẾT LẠI câu hỏi của người dùng cho rõ nghĩa hơn và MỞ RỘNG TỪ KHÓA (Query Expansion) để hệ thống Vector Search tìm được tài liệu chính xác nhất.
Quy tắc BẮT BUỘC:
1. [NGỮ CẢNH ĐỘC QUYỀN]: Tất cả ngữ cảnh đều thuộc về "Trường Đại học Cần Thơ" (CTU). TUYỆT ĐỐI KHÔNG tự bịa đặt, suy diễn thêm tên các trường đại học khác (ví dụ: ĐHQGHN, Bách Khoa...).
2. [BỔ SUNG NGỮ CẢNH]: Nếu câu hỏi bị cụt (ví dụ: "vậy còn ngành CNTT thì sao?"), hãy lấy ngữ cảnh từ Lịch sử Chat đắp vào.
3. [MỞ RỘNG VAY VỐN]: Nếu người dùng hỏi chung chung về "vay vốn", "vay tiền học", "gia đình khó khăn", "thu nhập trung bình"... mà không nói rõ ngân hàng nào, BẮT BUỘC phải viết lại câu hỏi có chứa cụm từ: "vay vốn qua Ngân hàng Chính sách xã hội (NHCSXH) và vay tiền đóng học phí qua Ngân hàng thương mại VietinBank".
4. [MỞ RỘNG HỌC BỔNG]: Nếu hỏi chung chung về "học bổng", hãy viết lại có chứa cụm từ: "Học bổng khuyến khích học tập (ngân sách nhà nước) và Học bổng tài trợ từ doanh nghiệp bên ngoài".
5. Nếu câu hỏi đã nhắc đích danh một tên cụ thể (như VietinBank, học bổng Vallet), thì chỉ làm rõ câu hỏi, không cần nhét thêm các nguồn khác.
6. [MỞ RỘNG KHÓA VÀ HỆ ĐÀO TẠO]: Nếu câu hỏi liên quan đến học phí, BẮT BUỘC phải làm rõ thông tin về "Khóa" (VD: K45 -> Khóa 45, K52 -> Khóa 52). Quan trọng:
   - Nếu người dùng KHÔNG nhắc đến chữ "chất lượng cao", "clc", "tiên tiến", hãy BỔ SUNG cụm từ "Đại trà" vào truy vấn để tránh bị nhầm với hệ CLC.
7. [MỞ RỘNG MIỄN GIẢM]: Nếu câu hỏi nhắc đến "miễn giảm", "trừ tiền học", "cơ sở tính miễn giảm", BẮT BUỘC phải BỔ SUNG cụm từ "làm cơ sở để tính miễn, giảm học phí" vào truy vấn.
8. TUYỆT ĐỐI KHÔNG trả lời câu hỏi. CHỈ in ra 1 câu duy nhất là câu truy vấn đã được tối ưu.
9. KHÔNG giải thích, KHÔNG nhắc đến các ví dụ trong hướng dẫn này."""),
            ("human", "Lịch sử Chat:\n{history_text}\n\nCâu hỏi hiện tại: {question}\n\nViết lại và tối ưu câu truy vấn cho Đại học Cần Thơ:")
        ])
        
        rewrite_chain = rewrite_prompt | rewrite_llm | StrOutputParser()
        search_query = await rewrite_chain.ainvoke({
            "history_text": history_text,
            "question": request.query
        })
        
        # Llama 3 hay bị "ảo tưởng" đang là chatbot nên hay trả lời từ chối
        search_query_clean = search_query.strip().replace('"', '').replace("'", "")
        bad_phrases = ["tôi không", "xin lỗi", "không thể", "không có", "không rõ", "là một ai"]
        
        if any(phrase in search_query_clean.lower() for phrase in bad_phrases):
            logger.warning(f"⚠️ Llama viết lại thất bại ('{search_query}'). Fallback về câu gốc.")
            search_query = request.query
        else:
            logger.info(f"🔍 Groq Llama đã viết lại (Query Expansion): '{request.query}' -> '{search_query}'")

        # --- BƯỚC 2: RÚT TRÍCH TÀI LIỆU TỪ VECTOR DB ---
        docs = engine.retriever.invoke(search_query)
        
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
            log_lines.append(f"[SEARCH QUERY (sau Rewrite)]: {search_query}")
            log_lines.append(f"[SỐ LƯỢNG DOCS TRẢ VỀ]: {len(docs)}")
            log_lines.append(f"{'-'*80}")
            
            for i, doc in enumerate(docs):
                source = doc.metadata.get('source', 'N/A')
                headers = {k: v for k, v in doc.metadata.items() if k.startswith("Header_")}
                effective_date = doc.metadata.get('effective_date', 'N/A')
                preview = doc.page_content[:700].replace('\n', ' ')
                
                log_lines.append(f"  [{i+1}] Source: {source} | Date: {effective_date}")
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
        context_blocks = []
        for doc in docs:
            headers = [str(v) for k, v in doc.metadata.items() if k.startswith("Header_")]
            header_prefix = "Chuyên mục: " + " > ".join(headers) + "\n" if headers else ""
            context_blocks.append(f"[{doc.metadata.get('source', 'Tài liệu')}]\n{header_prefix}{doc.page_content}")
            
        context_str = "\n\n---\n\n".join(context_blocks)

        # --- BƯỚC 3: GỌI LLM GEMINI VÀ XỬ LÝ TOOL ---
        chain_input = {
            "context": context_str,
            "chat_history": chat_history,
            "question": request.query # Lưu ý: Vẫn giữ lại câu hỏi gốc cho Gemini để nó phản hồi tự nhiên hơn
        }
        
        rag_chain = chat_prompt | llm_with_tools
        response_msg = await rag_chain.ainvoke(chain_input)
        
        if response_msg.tool_calls:
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
