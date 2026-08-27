import json
import logging
import os
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
import redis.asyncio as redis
from langchain_core.messages import HumanMessage, AIMessage
from app.models.pydantic import ChatRequest, ChatResponse

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
    agent_graph = fast_req.app.state.agent_graph
    
    if request.session_id:
        session_id = request.session_id
    else:
        session_id = generate_uuid()
        
    history_key = f"user:{current_user.id}:session:{session_id}:history"
    
    try:
        # --- BƯỚC 1: TRUY XUẤT LỊCH SỬ TỪ REDIS ---
        raw_history = await redis_client.lrange(history_key, -5, -1)
        
        chat_history = []
        for msg_str in raw_history:
            msg_dict = json.loads(msg_str)
            if msg_dict["role"] == "human":
                chat_history.append(HumanMessage(content=msg_dict["content"]))
            elif msg_dict["role"] == "ai":
                chat_history.append(AIMessage(content=msg_dict["content"]))
                
        logger.info(f"Đã nạp {len(chat_history)} tin nhắn lịch sử từ Redis.")

        # --- BƯỚC 2: GỌI MULTI-AGENT GRAPH ---
        result = await agent_graph.ainvoke({
            "query": request.query,
            "chat_history": chat_history,
            # Khởi tạo state mặc định
            "search_query": "",
            "next_agent": "",
            "routing_decision": None,
            "context": "",
            "retrieval_instruction": "",
            "response": "",
        })
        
        ai_response = result.get("response", "")
        
        if not ai_response or not ai_response.strip():
            logger.warning("⚠️ Agent graph trả về response rỗng")
            ai_response = "Xin lỗi, tôi không thể xử lý câu hỏi này lúc này."

        # --- BƯỚC 3: LƯU LỊCH SỬ ---
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
