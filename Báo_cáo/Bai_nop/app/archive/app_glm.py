import os
import sys
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
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
from Chunking.sematic_chunking_rerank import AdvancedChunkingEngine
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
# Import Tool tính toán học bổng
from Tools.scholarship_tool import tinh_tien_hoc_bong

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan quản lý tập trung tài nguyên hệ thống khi Startup và Shutdown.
    """
    if "ZHIPUAI_API_KEY" not in os.environ:
        logger.error("Không tìm thấy ZHIPUAI_API_KEY trong biến môi trường.")
        raise RuntimeError("Hệ thống thiếu API Key của ZhipuAI (GLM).")
        
    try:
        logger.info("📡 Đang kết nối tới Redis Server...")
        # Sử dụng Connection Pool để tối ưu hiệu năng kết nối của Redis
        app.state.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
        # Ping thử để chắc chắn kết nối sống
        await app.state.redis_client.ping()
        logger.info("✅ Kết nối Redis thành công!")

        logger.info("🤖 Khởi tạo Vector DB và LLM ChatGLM...")
        app.state.engine = AdvancedChunkingEngine(persist_dir=os.path.join(PROJECT_ROOT, "qdrant_storage"))
        
        # LLM chính (GLM-4.5-Air)
        app.state.llm = ChatOpenAI(
            model="glm-4.5-air",
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            api_key=os.environ["ZHIPUAI_API_KEY"],
            temperature=0.8
        )
        # LLM phụ (cũng dùng GLM-4.5-Air cho ổn định)
        app.state.rewrite_llm = ChatOpenAI(
            model="glm-4.5-air",
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            api_key=os.environ["ZHIPUAI_API_KEY"],
            temperature=0.1
        )
        
        # --- CẤU HÌNH TOOL CALLING TÍCH HỢP ---
        app.state.tools = [tinh_tien_hoc_bong]
        # Ép con LLM chính kết nối với Tool
        app.state.llm_with_tools = app.state.llm.bind_tools(app.state.tools)
        
        app.state.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một trợ lý thông minh của Trường Đại học Cần Thơ.
            Hãy sử dụng các đoạn ngữ cảnh (Context) sau đây để trả lời câu hỏi của người dùng.
            Nếu trong Context không có thông tin, hãy trả lời là "Tôi không tìm thấy thông tin này trong tài liệu", tuyệt đối không bịa đặt.
            
            LUẬT QUAN TRỌNG:
            - Trả lời ngắn gọn, súc tích, đi thẳng vào trọng tâm.
            - NẾU người dùng nhắc đến điểm GPA, điểm rèn luyện hoặc hỏi số tiền học bổng: BẮT BUỘC gọi công cụ (tool) để tính toán, tuyệt đối không tự tính.
            
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
        # Giải phóng tài nguyên khi tắt server
        if hasattr(app.state, "redis_client"):
            await app.state.redis_client.close()
            logger.info("🔒 Đã đóng kết nối Redis an toàn.")

app = FastAPI(title="CTU Scholarship Chatbot V2", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, fast_req: Request):
    redis_client: redis.Redis = fast_req.app.state.redis_client
    engine = fast_req.app.state.engine
    llm = fast_req.app.state.llm
    rewrite_llm = fast_req.app.state.rewrite_llm
    chat_prompt = fast_req.app.state.chat_prompt
    
    # Định danh cứng key lưu lịch sử cho luồng test đơn giản này
    history_key = "single_user:chat_history"
    
    try:
        # --- BƯỚC 1: TRUY XUẤT 5 TIN NHẮN GẦN NHẤT (Sliding Window từ Redis) ---
        # Lấy từ chỉ mục -5 đến -1 (5 phần tử cuối cùng của danh sách)
        raw_history = await redis_client.lrange(history_key, -5, -1)
        
        chat_history = []
        for msg_str in raw_history:
            msg_dict = json.loads(msg_str)
            if msg_dict["role"] == "human":
                chat_history.append(HumanMessage(content=msg_dict["content"]))
            elif msg_dict["role"] == "ai":
                chat_history.append(AIMessage(content=msg_dict["content"]))
                
        logger.info(f"Đã tối ưu hóa context: Rút trích {len(chat_history)} tin nhắn gần nhất từ Redis.")

        # --- BƯỚC 1.5: ĐỊNH HÌNH LẠI CÂU HỎI (Query Contextualization & Expansion) ---
        # Phân tích ngữ cảnh từ lịch sử để tạo thành câu hỏi độc lập (standalone query)
        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", """Dựa vào lịch sử trò chuyện (nếu có), hãy viết lại câu hỏi mới nhất của người dùng thành một câu hỏi hoàn toàn độc lập và đầy đủ ý nghĩa để dùng cho hệ thống tìm kiếm tài liệu. 
            KHÔNG được trả lời câu hỏi, CHỈ trả về câu hỏi đã được viết lại.
            
            LUẬT THÉP:
            1. Phải dịch/mở rộng tất cả các từ viết tắt thông dụng trong đại học (VD: DRL -> Điểm rèn luyện, ĐTB/GPA -> Điểm trung bình).
            2. TUYỆT ĐỐI KHÔNG lặp lại câu "Tôi không tìm thấy thông tin này trong tài liệu." từ lịch sử AI. Nhiệm vụ của bạn LÀ VIẾT LẠI CÂU HỎI của người dùng."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        rewrite_chain = rewrite_prompt | rewrite_llm | StrOutputParser()
        search_query = await rewrite_chain.ainvoke({
            "chat_history": chat_history,
            "question": request.query
        })
        logger.info(f"🔍 Câu hỏi gốc: '{request.query}' -> Đã viết lại thành: '{search_query}'")

        # --- BƯỚC 2: RÚT TRÍCH TÀI LIỆU TỪ VECTOR DB (RAG) ---
        # Thực hiện câu lệnh tìm kiếm bằng câu hỏi đã được làm rõ ngữ cảnh
        docs = engine.retriever.invoke(search_query)
        context_str = "\n\n".join(doc.page_content for doc in docs)

        # --- BƯỚC 3: GỌI LLM VÀ XỬ LÝ TOOL (Native Tool Calling) ---
        chain_input = {
            "context": context_str,
            "chat_history": chat_history,
            "question": request.query
        }
        
        # Chạy LCEL Chain với LLM đã được gắn Tool
        rag_chain = app.state.chat_prompt | app.state.llm_with_tools
        response_msg = await rag_chain.ainvoke(chain_input)
        
        # Đánh chặn: Kiểm tra xem Gemini có quyết định dùng Tool hay không
        if response_msg.tool_calls:
            logger.info(f"Gemini đã kích hoạt Tool: {response_msg.tool_calls}")
            tool_call = response_msg.tool_calls[0]
            if tool_call["name"] == "tinh_tien_hoc_bong":
                # Chạy hàm tính toán Python và dùng thẳng kết quả đó làm câu trả lời
                ai_response = tinh_tien_hoc_bong.invoke(tool_call["args"])
            else:
                ai_response = "Đã xảy ra lỗi không xác định khi gọi công cụ."
        else:
            # Nếu không dùng Tool, lấy câu trả lời chữ thông thường (Xử lý lỗi Array Pydantic)
            if isinstance(response_msg.content, list):
                ai_response = " ".join(block.get("text", "") for block in response_msg.content if isinstance(block, dict) and block.get("type") == "text")
            else:
                ai_response = str(response_msg.content)

        # --- BƯỚC 4: LƯU TIN NHẮN MỚI NGƯỢC LẠI REDIS ---
        # Đóng gói dữ liệu tin nhắn mới của cả Human và AI
        human_msg = json.dumps({"role": "human", "content": request.query})
        ai_msg = json.dumps({"role": "ai", "content": ai_response})
        
        # Đẩy đồng thời vào cuối danh sách Redis List
        await redis_client.rpush(history_key, human_msg, ai_msg)
        
        # Tùy chọn: Để tránh Redis List phình to vô hạn theo ngày tháng, 
        # giữ độ dài tối đa của list trong cache khoảng 50 tin nhắn để dự phòng.
        await redis_client.ltrim(history_key, -50, -1)

        return ChatResponse(answer=ai_response)

    except redis.RedisError as re:
        logger.error(f"Lỗi thao tác trên Redis: {str(re)}", exc_info=True)
        raise HTTPException(status_code=502, detail="Hệ thống cache tạm thời gián đoạn.")
    except Exception as e:
        logger.error(f"Lỗi hệ thống khi sinh câu trả lời: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra trong quá trình xử lý câu hỏi.")

# Phục vụ thư mục static chứa giao diện
static_dir = os.path.join(PROJECT_ROOT, "UI", "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Khởi động máy chủ Uvicorn tại cổng 8000...")
    uvicorn.run("UI.app_glm:app", host="0.0.0.0", port=8000, reload=True)