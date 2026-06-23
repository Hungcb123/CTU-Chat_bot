import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Bước 1: Setup paths để import được Chunking
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Load biến môi trường từ file .env
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from Chunking.sematic_chunking import AdvancedChunkingEngine
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Biến toàn cục lưu trữ engine và chain
engine = None
rag_chain = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine, rag_chain
    if "GOOGLE_API_KEY" not in os.environ:
        print("❌ Lỗi: Chưa tìm thấy GOOGLE_API_KEY. Vui lòng kiểm tra file .env!")
        
    engine = AdvancedChunkingEngine(persist_dir=os.path.join(PROJECT_ROOT, "qdrant_storage"))
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    
    prompt_template = """
    Bạn là một trợ lý thông minh của Trường Đại học Cần Thơ. 
    Hãy sử dụng các ngữ cảnh (Context) sau đây để trả lời câu hỏi của người dùng. 
    Nếu trong Context không có thông tin, hãy trả lời là "Tôi không tìm thấy thông tin này trong tài liệu", tuyệt đối không bịa đặt.
    
    Context:
    {context}
    
    Câu hỏi: {question}
    
    Câu trả lời:
    """
    prompt = PromptTemplate.from_template(prompt_template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": engine.retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("🤖 Chatbot Engine Initialized!")
    yield

app = FastAPI(title="CTU Scholarship Chatbot API", lifespan=lifespan)

# Khởi tạo thư mục static (sẽ được mount ở cuối file)
static_dir = os.path.join(PROJECT_ROOT, "UI", "static")
os.makedirs(static_dir, exist_ok=True)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str



@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    try:
        response = rag_chain.invoke(request.query)
        return ChatResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Phục vụ thư mục static ở root (phải đặt ở cuối cùng để không đè lên các route API)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Khởi động server tại: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
