import logging
import json
from fastapi import APIRouter, HTTPException, Request, Depends
import redis.asyncio as redis
from app.api.auth import get_current_user
from app.models.schema import User, ChatSession, ChatMessage
from app.core.database import AsyncSessionLocal
from sqlalchemy import select, desc
from app.models.pydantic import SessionResponse, SessionListResponse, MessageResponse, MessageListResponse, SessionUpdate

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/sessions", response_model=SessionListResponse)
async def get_sessions(current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == current_user.id)
            .order_by(desc(ChatSession.updated_at))
        )
        sessions = result.scalars().all()
        return SessionListResponse(sessions=[
            SessionResponse(id=s.id, title=s.title, updated_at=s.updated_at) for s in sessions
        ])

@router.get("/sessions/{session_id}/messages", response_model=MessageListResponse)
async def get_session_messages(session_id: str, fast_req: Request, current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as db:
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
            
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        messages = result.scalars().all()
        
        if messages:
            redis_client: redis.Redis = fast_req.app.state.redis_client
            history_key = f"user:{current_user.id}:session:{session_id}:history"
            await redis_client.delete(history_key)
            recent_msgs = messages[-50:]
            redis_msgs = []
            for m in recent_msgs:
                redis_msgs.append(json.dumps({"role": m.role, "content": m.content}))
            if redis_msgs:
                await redis_client.rpush(history_key, *redis_msgs)
                
        return MessageListResponse(messages=[
            MessageResponse(id=m.id, role=m.role, content=m.content, created_at=m.created_at) for m in messages
        ])

@router.put("/sessions/{session_id}")
async def update_session_title(session_id: str, update_data: SessionUpdate, current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as db:
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
            
        session.title = update_data.title
        await db.commit()
        return {"status": "success", "message": "Đã đổi tên thành công"}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, fast_req: Request, current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as db:
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
            
        await db.delete(session)
        await db.commit()
        
        redis_client: redis.Redis = fast_req.app.state.redis_client
        history_key = f"user:{current_user.id}:session:{session_id}:history"
        await redis_client.delete(history_key)
        
        return {"status": "success", "message": "Đã xóa phiên chat"}
