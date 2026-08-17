import argparse
import json
import os
import time
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Setup internal RAG components
from app.services.rag_engine import AdvancedChunkingEngine
from app.services.query_intent import classify_query_intent, build_retrieval_lanes
from scripts.evaluate_chat_dataset import parse_dataset

async def run_generation(dataset_path: Path, limit: int = None):
    cases = parse_dataset(dataset_path)
    if limit:
        cases = cases[:limit]
        
    print(f"Bắt đầu lấy ngữ cảnh và sinh câu trả lời cho {len(cases)} câu hỏi...")
    
    engine = AdvancedChunkingEngine()
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)
    
    ragas_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }
    
    for i, case in enumerate(cases):
        print(f"Đang xử lý [{i+1}/{len(cases)}]: {case.question}")
        
        # 1. Intent & Routing
        decision = classify_query_intent(case.question)
        lanes = build_retrieval_lanes(decision)
        
        # 2. Retrieval
        all_docs = []
        for lane in lanes:
            if lane.name == "not_applicable": continue
            docs = engine.retrieve(
                query=case.question,
                lane=lane.name,
                fee_kind=lane.fee_kind,
                content_kind=lane.content_kind,
                domain=lane.domain,
                academic_year=decision.academic_year,
                top_n=lane.top_n
            )
            all_docs.extend(docs)
            
        # Deduplicate
        unique_docs = []
        seen = set()
        for doc in all_docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_docs.append(doc)
                
        contexts = [doc.page_content for doc in unique_docs]
        
        # 3. Generation
        context_str = "\n\n---\n\n".join(contexts)
        prompt = f"Ngữ cảnh:\n{context_str}\n\nCâu hỏi: {case.question}\n\nHãy trả lời câu hỏi dựa vào ngữ cảnh trên một cách ngắn gọn, súc tích."
        
        if not contexts:
            answer = "Hệ thống không tìm thấy tài liệu phù hợp."
        else:
            try:
                ai_msg = await llm.ainvoke(prompt)
                answer = str(ai_msg.content)
            except Exception as e:
                answer = f"Error: {e}"
            
        ragas_data["question"].append(case.question)
        ragas_data["answer"].append(answer)
        ragas_data["contexts"].append(contexts)
        ragas_data["ground_truth"].append(case.expected_answer)
        
        time.sleep(1) # Rate limit protection
        time.sleep(4)

    out_path = Path("data/ragas_data_temp.json")
    out_path.write_text(json.dumps(ragas_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ Đã lưu data để Ragas chấm điểm tại: {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("data/dataset.md"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    asyncio.run(run_generation(args.dataset, args.limit))
