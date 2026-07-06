from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Auth Schemas ---
class UserAuth(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    role: str

# --- Chat Schemas ---
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str

# --- History Schemas ---
class SessionResponse(BaseModel):
    id: str
    title: str
    updated_at: datetime

class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]

class MessageResponse(BaseModel):
    role: str
    content: str

class MessageListResponse(BaseModel):
    messages: List[MessageResponse]

class SessionUpdate(BaseModel):
    title: str
