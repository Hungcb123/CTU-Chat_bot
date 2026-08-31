from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base
import uuid
import uuid6

def generate_uuid():
    return str(uuid6.uuid7())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="student")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Quan hệ 1-N với ChatSession
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False) # 'human' or 'ai'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")

class ParentDocument(Base):
    """Bảng dùng làm DocStore cho RAG, thay thế cho LocalShelveStore"""
    __tablename__ = "parent_documents"

    id = Column(String, primary_key=True) # ID mapping với vector Qdrant
    content = Column(Text, nullable=False) # Nội dung văn bản
    metadata_json = Column(JSONB, nullable=True) # JSONB siêu nhanh của Postgres
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DocumentMetadataRecord(Base):
    """Bảng lưu trữ business metadata của tài liệu RAG trong PostgreSQL.

    Mỗi row ứng với 1 file .md trong corpus. Dữ liệu gốc nằm trong
    document_metadata.json và được đồng bộ vào bảng này khi re-ingest
    hoặc upload tài liệu mới.
    """
    __tablename__ = "document_metadata"

    id = Column(String, primary_key=True, default=generate_uuid)
    source = Column(String, unique=True, nullable=False, index=True)  # Tên file .md
    domain = Column(String, nullable=False)          # tuition, scholarship, student_loan, ...
    content_kind = Column(String, nullable=False)    # rate_table, policy, announcement, ...
    fee_kind = Column(String, nullable=False)        # actual_tuition, exemption_basis, not_applicable
    academic_year = Column(String, nullable=True)    # 2025-2026 format
    status = Column(String, nullable=False, default="active")  # active / inactive
    original_filename = Column(String, nullable=True)  # Tên file PDF gốc (chỉ uploaded docs)
    uploaded_by = Column(String, nullable=True)        # Username admin đã upload
    uploaded_at = Column(DateTime(timezone=True), nullable=True)  # Thời điểm upload
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
