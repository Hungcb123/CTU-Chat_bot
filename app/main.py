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
from langchain_groq import ChatGroq
from app.tools.scholarship import tinh_tien_hoc_bong

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
        
        # LLM CHÍNH (GEMINI): Dùng để sinh câu trả lời và sử dụng Tool
        app.state.llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.4)
        
        # LLM PHỤ (GROQ Llama): Dùng để viết lại câu hỏi (Rewriter) siêu tốc
        app.state.rewrite_llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.0, # Không cần sáng tạo, chỉ cần dịch đúng
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # --- CẤU HÌNH TOOL CALLING TÍCH HỢP ---
        app.state.tools = [tinh_tien_hoc_bong]
        app.state.llm_with_tools = app.state.llm.bind_tools(app.state.tools)
        
        app.state.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một trợ lý thông minh của Trường Đại học Cần Thơ.
            Bạn CHỈ ĐƯỢC PHÉP hỗ trợ và trả lời các câu hỏi liên quan đến: Học bổng khuyến khích, miễn giảm học phí, trợ cấp xã hội, vay vốn.
            Nếu người dùng hỏi về bất kỳ chủ đề nào khác nằm ngoài phạm vi này, hãy từ chối và trả lời: "Tôi chỉ hỗ trợ giải đáp về các chế độ chính sách (học bổng, miễn giảm học phí, trợ cấp, vay vốn). Xin lỗi vì không thể hỗ trợ câu hỏi này của bạn."
            
            Hãy sử dụng các đoạn ngữ cảnh (Context) sau đây HOẶC kết quả từ các Công cụ (Tools) để trả lời câu hỏi của người dùng.
            Nếu trong Context và kết quả Công cụ đều không có thông tin, hãy trả lời là "Tôi không tìm thấy thông tin này trong tài liệu", tuyệt đối không bịa đặt.
            
            LUẬT QUAN TRỌNG:
            - Trả lời ngắn gọn, súc tích, đi thẳng vào trọng tâm.
            - NẾU người dùng nhắc đến điểm GPA, điểm rèn luyện hoặc hỏi số tiền học bổng: BẮT BUỘC gọi công cụ (tool) để tính toán. Dựa trực tiếp vào KẾT QUẢ CỦA CÔNG CỤ ĐỂ TRẢ LỜI NGƯỜI DÙNG, tuyệt đối không được nói là không tìm thấy thông tin nếu công cụ đã trả về kết quả.
            
            Context:
            {context}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        logger.info("🚀 Toàn bộ Engine đã sẵn sàng tiếp nhận Request!")
        yield
        
    except redis.RedisError as re:
        logger.critical(f"Không thể kết nối đến Redis Docker: {str(re)}")
        raise re
    except Exception as e:
        logger.critical(f"Lỗi khởi tạo hệ thống: {str(e)}")
        raise e
    finally:
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
