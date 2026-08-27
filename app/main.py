import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import redis.asyncio as redis

# 1. Cấu hình Hệ thống Logging Doanh nghiệp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Import các module AI chuyên dụng
from app.services.rag_engine import AdvancedChunkingEngine
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.tools.scholarship import tinh_tien_hoc_bong
from app.tools.tuition import tinh_toan_hoc_phi
from app.tools.academic_program import (
    tra_cuu_nganh, so_sanh_nganh, tim_nganh,
    xem_chuoi_tien_quyet, mon_chung_giua_nganh, tim_nganh_co_mon,
    set_graph_service,
)
from app.services.tuition_catalog import TuitionRateCatalog
from app.services.graph_service import AcademicGraphService
from app.agents.graph import build_agent_graph

# Import controllers
from app.api.chat import router as chat_router
from app.api.history import router as history_router
from app.api.auth import router as auth_router
from app.api.document import router as document_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    if "GOOGLE_API_KEY" not in os.environ:
        logger.error("Không tìm thấy GOOGLE_API_KEY trong biến môi trường.")
        raise RuntimeError("Hệ thống thiếu API Key của Gemini.")
        
    try:
        logger.info("📡 Đang kết nối tới Redis Server...")
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        app.state.redis_client = redis.from_url(redis_url, decode_responses=True)
        await app.state.redis_client.ping()
        logger.info("✅ Kết nối Redis thành công!")

        logger.info("📡 Đang khởi tạo CSDL PostgreSQL...")
        from app.core.database import engine as async_pg_engine
        from app.models.schema import Base
        async with async_pg_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tạo bảng PostgreSQL thành công!")

        logger.info("🤖 Khởi tạo Vector DB và LLM Gemini + Qwen Local...")
        app.state.engine = AdvancedChunkingEngine(persist_dir=os.path.join(PROJECT_ROOT, "qdrant_storage"))
        app.state.tuition_catalog = TuitionRateCatalog.load()
        logger.info(
            "✅ Đã nạp %d mức học phí có cấu trúc.",
            len(app.state.tuition_catalog.records),
        )

        # KHỞI TẠO NEO4J GRAPH SERVICE
        logger.info("📡 Đang kết nối tới Neo4j Graph Database...")
        neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
        neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")
        app.state.graph_service = AcademicGraphService(
            uri=neo4j_uri, user=neo4j_user, password=neo4j_password,
        )
        app.state.graph_service.ensure_data_loaded()
        set_graph_service(app.state.graph_service)
        logger.info("✅ Neo4j Graph Service sẵn sàng!")
        
        # LLM CHÍNH (GEMINI): Dùng để sinh câu trả lời và sử dụng Tool
        app.state.llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
        
        # LLM PHỤ (GEMINI): Dùng để viết lại câu hỏi (Rewriter) siêu tốc
        app.state.rewrite_llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite",
            temperature=0.0,
        )
        
        # --- CẤU HÌNH MULTI-AGENT GRAPH (LangGraph) ---
        academic_tools = [
            tra_cuu_nganh, so_sanh_nganh, tim_nganh,
            xem_chuoi_tien_quyet, mon_chung_giua_nganh, tim_nganh_co_mon,
        ]
        financial_tools = [tinh_toan_hoc_phi]
        scholarship_tools = [tinh_tien_hoc_bong]

        app.state.agent_graph = build_agent_graph(
            llm=app.state.llm,
            rewrite_llm=app.state.rewrite_llm,
            engine=app.state.engine,
            tuition_catalog=app.state.tuition_catalog,
            academic_tools=academic_tools,
            financial_tools=financial_tools,
            scholarship_tools=scholarship_tools,
        )
        logger.info("✅ Multi-Agent Graph sẵn sàng!")
        
        logger.info("🚀 Toàn bộ Engine đã sẵn sàng tiếp nhận Request!")
        yield
        
    except redis.RedisError as re:
        logger.critical(f"Không thể kết nối đến Redis Docker: {str(re)}")
        raise re
    except Exception as e:
        logger.critical(f"Lỗi khởi tạo hệ thống: {str(e)}")
        raise e
    finally:
        if hasattr(app.state, "graph_service"):
            app.state.graph_service.close()
            logger.info("🔒 Đã đóng kết nối Neo4j an toàn.")
        if hasattr(app.state, "redis_client"):
            await app.state.redis_client.close()
            logger.info("🔒 Đã đóng kết nối Redis an toàn.")

app = FastAPI(title="CTU Scholarship Chatbot V2 - Khắc phục mất Context", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Đăng ký các API routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(document_router)

static_dir = os.path.join(PROJECT_ROOT, "frontend")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Khởi động máy chủ Uvicorn tại cổng 8000...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
