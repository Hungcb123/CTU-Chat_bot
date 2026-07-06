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
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

# TÍCH HỢP GROQ CHO REWRITER
from langchain_groq import ChatGroq

# Import Tool tính toán học bổng
from Tools.scholarship_tool import tinh_tien_hoc_bong

@asynccontextmanager
async def lifespan(app: FastAPI):
    if "GOOGLE_API_KEY" not in os.environ:
        logger.error("Không tìm thấy GOOGLE_API_KEY trong biến môi trường.")
        raise RuntimeError("Hệ thống thiếu API Key của Gemini.")
        
    try:
        logger.info("📡 Đang kết nối tới Redis Server...")
        app.state.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
        await app.state.redis_client.ping()
        logger.info("✅ Kết nối Redis thành công!")

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
        if hasattr(app.state, "redis_client"):
            await app.state.redis_client.close()
            logger.info("🔒 Đã đóng kết nối Redis an toàn.")

app = FastAPI(title="CTU Scholarship Chatbot V2 - Khắc phục mất Context", lifespan=lifespan)
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
    
    history_key = "single_user:chat_history"
    
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

        # --- BƯỚC 1.5: ĐỊNH HÌNH LẠI CÂU HỎI BẰNG Llama LOCAL ---
        # Chỉ tốn thời gian gọi mô hình Rewriter nếu như ĐÃ CÓ lịch sử chat
        if chat_history:
            # Chuyển đổi chat_history thành chuỗi văn bản để ép Llama không được đóng vai chatbot
            history_text = "\n".join([f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}" for m in chat_history])
            
            rewrite_prompt = ChatPromptTemplate.from_messages([
                ("system", "Bạn là một công cụ phân tích ngôn ngữ. Nhiệm vụ DUY NHẤT của bạn là ĐỊNH DẠNG LẠI câu hỏi.\n"
                 "TUYỆT ĐỐI KHÔNG TRẢ LỜI CÂU HỎI. TUYỆT ĐỐI KHÔNG GIẢI THÍCH.\n"
                 "Nếu câu hỏi của người dùng bị thiếu ngữ cảnh (chủ ngữ, đối tượng), hãy tìm thông tin từ Lịch sử Chat để đắp vào câu hỏi cho đầy đủ ý nghĩa.\n"
                 "Ví dụ Lịch sử: Đang nói về Học bổng SCIC của Khoa CNTT.\n"
                 "Ví dụ Câu hỏi: Điều kiện điểm số là bao nhiêu?\n"
                 "Ví dụ Output chuẩn: Điều kiện điểm số để nhận học bổng SCIC của Khoa CNTT là bao nhiêu?\n"
                 "CHỈ IN RA ĐÚNG 1 CÂU VIẾT LẠI, KHÔNG THÊM DẤU NGOẶC KÉP."),
                ("human", "Lịch sử Chat:\n{history_text}\n\nCâu hỏi cần viết lại: {question}")
            ])
            rewrite_chain = rewrite_prompt | rewrite_llm | StrOutputParser()
            search_query = await rewrite_chain.ainvoke({
                "history_text": history_text,
                "question": request.query
            })
            logger.info(f"🔍 Groq Llama viết lại: '{request.query}' -> '{search_query}'")
        else:
            # Nếu là câu hỏi đầu tiên, dùng luôn câu gốc (Tối ưu tốc độ)
            search_query = request.query

        # --- BƯỚC 2: RÚT TRÍCH TÀI LIỆU TỪ VECTOR DB ---
        docs = engine.retriever.invoke(search_query)
        context_str = "\n\n".join(doc.page_content for doc in docs)

        # --- BƯỚC 3: GỌI LLM GEMINI VÀ XỬ LÝ TOOL ---
        chain_input = {
            "context": context_str,
            "chat_history": chat_history,
            "question": request.query # Lưu ý: Vẫn giữ lại câu hỏi gốc cho Gemini để nó phản hồi tự nhiên hơn
        }
        
        rag_chain = app.state.chat_prompt | app.state.llm_with_tools
        response_msg = await rag_chain.ainvoke(chain_input)
        
        if response_msg.tool_calls:
            logger.info(f"Gemini đã kích hoạt Tool: {response_msg.tool_calls}")
            
            prompt_value = await app.state.chat_prompt.ainvoke(chain_input)
            messages = prompt_value.to_messages()
            messages.append(response_msg) 
            
            from langchain_core.messages import ToolMessage
            
            for tool_call in response_msg.tool_calls:
                if tool_call["name"] == "tinh_tien_hoc_bong":
                    tool_result_str = tinh_tien_hoc_bong.invoke(tool_call["args"])
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
            
            final_response = await app.state.llm.ainvoke(messages)
            
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

        return ChatResponse(answer=ai_response)

    except redis.RedisError as re:
        logger.error(f"Lỗi thao tác trên Redis: {str(re)}", exc_info=True)
        raise HTTPException(status_code=502, detail="Hệ thống cache tạm thời gián đoạn.")
    except Exception as e:
        logger.error(f"Lỗi hệ thống khi sinh câu trả lời: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra trong quá trình xử lý câu hỏi.")

@app.post("/new-chat")
async def new_chat_endpoint(fast_req: Request):
    redis_client: redis.Redis = fast_req.app.state.redis_client
    history_key = "single_user:chat_history"
    try:
        await redis_client.delete(history_key)
        logger.info("🗑️ Đã bắt đầu phiên chat mới (API /new-chat).")
        return {"status": "success", "message": "Bắt đầu chat mới thành công"}
    except Exception as e:
        logger.error(f"Lỗi khi xóa lịch sử trên Redis: {str(e)}")
        raise HTTPException(status_code=500, detail="Không thể tạo chat mới.")

@app.post("/clear-history")
async def clear_history_endpoint(fast_req: Request):
    redis_client: redis.Redis = fast_req.app.state.redis_client
    history_key = "single_user:chat_history"
    try:
        await redis_client.delete(history_key)
        logger.info("🗑️ Đã xóa trắng lịch sử trò chuyện (New Chat).")
        return {"status": "success", "message": "Đã xóa lịch sử thành công"}
    except Exception as e:
        logger.error(f"Lỗi khi xóa lịch sử trên Redis: {str(e)}")
        raise HTTPException(status_code=500, detail="Không thể xóa lịch sử.")

static_dir = os.path.join(PROJECT_ROOT, "UI", "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Khởi động máy chủ Uvicorn tại cổng 8000...")
    uvicorn.run("UI.app_qwen_rewriter:app", host="0.0.0.0", port=8000, reload=True)
