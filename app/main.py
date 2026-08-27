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
from app.services.llm_classifier import LLMIntentClassifier
from app.services.graph_service import AcademicGraphService

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
        
        # --- CẤU HÌNH TOOL CALLING TÍCH HỢP ---
        app.state.tools = [
            tinh_tien_hoc_bong, tinh_toan_hoc_phi,
            tra_cuu_nganh, so_sanh_nganh, tim_nganh,
            xem_chuoi_tien_quyet, mon_chung_giua_nganh, tim_nganh_co_mon,
        ]
        app.state.llm_with_tools = app.state.llm.bind_tools(app.state.tools)
        
        # --- LLM CLASSIFIER (Primary: LLM, Fallback: Rule-base) ---
        app.state.llm_classifier = LLMIntentClassifier(
            llm=app.state.rewrite_llm,  # Dùng chung Gemini Flash Lite
            confidence_threshold=float(os.environ.get("LLM_CLASSIFIER_THRESHOLD", "0.8")),
            timeout_seconds=float(os.environ.get("LLM_CLASSIFIER_TIMEOUT", "5.0")),
        )
        logger.info(
            "✅ LLM Classifier initialized (threshold=%.2f, timeout=%.1fs)",
            app.state.llm_classifier.confidence_threshold,
            app.state.llm_classifier.timeout_seconds,
        )
        
        app.state.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một trợ lý thông minh của Trường Đại học Cần Thơ.
            Chuyên môn của bạn là giải đáp các vấn đề về: Tài chính Sinh viên (học phí, học bổng, miễn giảm, trợ cấp, vay vốn), Chương trình đào tạo các ngành, và Quy chế học vụ.
            Nếu người dùng hỏi những chủ đề hoàn toàn không liên quan (ví dụ: nấu ăn, giải trí, chính trị...), hãy từ chối khéo léo.
            
            Hãy sử dụng các đoạn ngữ cảnh (Context) sau đây HOẶC kết quả từ các Công cụ (Tools) để trả lời câu hỏi của người dùng.
            Nếu trong Context và kết quả Công cụ đều không có thông tin, hãy trả lời là "Tôi không tìm thấy thông tin này trong tài liệu", tuyệt đối không bịa đặt.
            
            LUẬT QUAN TRỌNG:
            - Trả lời ngắn gọn, súc tích, đi thẳng vào trọng tâm.
            - NẾU người dùng CHỦ ĐỘNG cung cấp điểm GPA, điểm rèn luyện (ĐRL) và nhờ tính toán xem đạt học bổng loại gì, số tiền bao nhiêu: BẮT BUỘC gọi công cụ `tinh_tien_hoc_bong`.
            - NẾU người dùng CHỈ HỎI TRA CỨU thông tin chung (ví dụ: "Học bổng loại Khá khối Kinh doanh là bao nhiêu?", "Học bổng xuất sắc được bao nhiêu tiền?"): HÃY TÌM TRONG NGỮ CẢNH VÀ TRẢ LỜI TRỰC TIẾP, KHÔNG gọi công cụ tính toán.
            - NẾU người dùng yêu cầu TÍNH SỐ TIỀN PHẢI ĐÓNG SAU MIỄN GIẢM HOẶC SỐ TIỀN ĐƯỢC GIẢM (ví dụ hỏi sinh viên thuộc diện X thì còn đóng hoặc được giảm bao nhiêu tiền): BẮT BUỘC thực hiện 4 bước:
              Bước 1: Tìm "Mức học phí thực tế" của 1 tín chỉ (Dựa vào Ngành hoặc Học phần và Khóa học, trong file quy định mức học phí).
              Bước 2: Tìm "Mức học phí làm cơ sở tính miễn giảm" (Mức trần) của Khối ngành hoặc Học phần đại cương chung đó (trong file cơ sở tính miễn, giảm).
              Bước 3: Tìm "% được giảm" dựa vào diện đối tượng sinh viên.
              Bước 4: Gọi công cụ `tinh_toan_hoc_phi` với 3 con số vừa tìm được. Dựa trực tiếp vào kết quả của công cụ để trả lời.
            - NẾU người dùng CHỈ HỎI TRA CỨU thông tin (ví dụ: "Mức học phí làm cơ sở tính miễn giảm của môn X là bao nhiêu?", "Học phí của môn Y là bao nhiêu?"): HÃY TÌM TRONG NGỮ CẢNH VÀ TRẢ LỜI TRỰC TIẾP, không gọi công cụ tính toán. 
              + CHÚ Ý CỰC KỲ QUAN TRỌNG: "Mức học phí thực tế" và "Mức học phí làm cơ sở tính miễn giảm" là 2 bảng giá hoàn toàn KHÁC NHAU. 
              + NẾU câu hỏi nhắc đến "miễn giảm", TUYỆT ĐỐI CHỈ lấy số liệu từ tài liệu có tiêu đề "Mức học phí làm cơ sở để tính miễn, giảm". (Ví dụ: môn Giáo dục quốc phòng và an ninh có mức cơ sở miễn giảm là 451.000 đồng/tín chỉ, KHÔNG PHẢI 695.000 đồng).
            - Nếu Context có nhãn `KẾT QUẢ TRA CỨU HỌC PHÍ CẤU TRÚC - NGUỒN ƯU TIÊN`, phải dùng đúng các mức trong khối đó. Không được thay bằng mức từ vector search.
            - NẾU người dùng HỎI VỀ NGÀNH HỌC, CHƯƠNG TRÌNH ĐÀO TẠO, MÔN HỌC CỦA NGÀNH: Gọi công cụ `tra_cuu_nganh` để tra cứu. Nếu cần so sánh 2 ngành, gọi `so_sanh_nganh`. Nếu cần tìm ngành theo tiêu chí, gọi `tim_nganh`.
            - NẾU người dùng HỎI VỀ CHUỖI TIÊN QUYẾT ("muốn học môn X cần học gì trước?"): Gọi công cụ `xem_chuoi_tien_quyet` với mã hoặc tên môn.
            - NẾU người dùng HỎI VỀ MÔN CHUNG GIỮA 2 NGÀNH: Gọi công cụ `mon_chung_giua_nganh`.
            - NẾU người dùng HỎI "ngành nào có môn X?" hoặc "môn X thuộc ngành nào?": Gọi công cụ `tim_nganh_co_mon`.

            CHỈ DẪN ĐỊNH TUYẾN CHO CÂU HỎI HIỆN TẠI:
            {retrieval_instruction}
            
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
