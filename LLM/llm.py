import os
import sys

# Bước 1: Thêm thư mục gốc vào biến môi trường hệ thống để Python có thể tìm thấy thư mục Chunking
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Bước 2: BÂY GIỜ MỚI IMPORT ĐƯỢC Engine từ file sematic_chunking.py
from Chunking.sematic_chunking import AdvancedChunkingEngine

from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

if __name__ == "__main__":
    # Bước 3: Khởi tạo lại Engine để lấy cấu hình kết nối DB (Qdrant & Vector)
    engine = AdvancedChunkingEngine(persist_dir=os.path.join(PROJECT_ROOT, "qdrant_storage"))
    
    # Bước 4: Kiểm tra và khởi tạo LLM (API Key đã được load từ biến môi trường qua start_env.sh)
    if "GOOGLE_API_KEY" not in os.environ:
        print("❌ Lỗi: Chưa tìm thấy GOOGLE_API_KEY. Vui lòng kiểm tra file .env và chạy qua start_env.sh!")
        sys.exit(1)
        
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

    # Bước 5: Gắn engine.retriever vào chuỗi xử lý
    rag_chain = (
        {"context": engine.retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("\n" + "="*50)
    print("🤖 CHATBOT ĐÃ SẴN SÀNG! (Gõ 'exit' hoặc 'quit' để thoát)")
    print("="*50 + "\n")
    
    while True:
        try:
            query = input("🧑 Bạn: ")
            if query.lower() in ['exit', 'quit']:
                print("🤖 Tạm biệt!")
                break
                
            if not query.strip():
                continue
                
            response = rag_chain.invoke(query)
            print(f"🤖 Trả lời:\n{response}\n")
            print("-" * 50)
        except KeyboardInterrupt:
            print("\n🤖 Tạm biệt!")
            break