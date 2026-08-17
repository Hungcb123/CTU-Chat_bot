import argparse
import json
import os
import time
from pathlib import Path
from datetime import datetime
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness,
)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas.run_config import RunConfig
import asyncio

class RateLimitedChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    """Wrapper để giới hạn chính xác 15 RPM (1 request / 4s) cho toàn bộ script"""
    _rate_limit_lock = asyncio.Lock()
    
    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        kwargs.pop("n", None) # Xóa tham số n để tránh lỗi 400 Multiple candidates
        async with self._rate_limit_lock:
            await asyncio.sleep(4.1) # 4.1s đảm bảo < 15 req / phút
            return await super()._agenerate(messages, stop, run_manager, **kwargs)
            
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        kwargs.pop("n", None) # Xóa tham số n để tránh lỗi 400 Multiple candidates
        import time
        time.sleep(4.1)
        return super()._generate(messages, stop, run_manager, **kwargs)

from dotenv import load_dotenv

load_dotenv()

# Setup internal RAG components
from app.services.rag_engine import AdvancedChunkingEngine
from app.services.tuition_catalog import TuitionRateCatalog
from app.services.query_intent import classify_query_intent, build_retrieval_lanes
from scripts.evaluate_chat_dataset import parse_dataset

DEFAULT_DATASET = Path("data/dataset.md")

async def run_evaluation(args):
    dataset_path = args.dataset.resolve()
    cases = parse_dataset(dataset_path)
    if args.limit:
        cases = cases[:args.limit]
        
    print(f"Bắt đầu đánh giá Ragas cho {len(cases)} câu hỏi...")
    
    # Initialize Engine to get Contexts and Answer
    engine = AdvancedChunkingEngine()
    
    llm = RateLimitedChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)
    
    ragas_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }
    
    for i, case in enumerate(cases):
        print(f"Đang xử lý [{i+1}/{len(cases)}]: {case.question}")
        
        # 1. Intent & Routing (Simplified version of chat.py)
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
            
        # Append to Ragas Dataset
        ragas_data["question"].append(case.question)
        ragas_data["answer"].append(answer)
        ragas_data["contexts"].append(contexts)
        ragas_data["ground_truth"].append(case.expected_answer)
        
        time.sleep(1) # Rate limit protection

    # Convert to HuggingFace Dataset
    hf_dataset = Dataset.from_dict(ragas_data)
    
    print("\nĐang chạy Ragas Evaluator (LLM-as-a-judge)...")
    
    # Configure Ragas judge models
    judge_llm = RateLimitedChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    judge_embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # Config rate limit
    run_config = RunConfig(timeout=120, max_retries=10, max_workers=1, max_wait=4)
    
    result = evaluate(
        hf_dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness,
        ],
        llm=judge_llm,
        embeddings=judge_embeddings,
        run_config=run_config,
        raise_exceptions=False
    )
    
    df = result.to_pandas()
    
    # Output markdown report
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("logs/dataset_evaluation")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"ragas_eval_{stamp}.md"
    
    # Calculate averages
    avg_faithfulness = df["faithfulness"].mean() if "faithfulness" in df else 0.0
    avg_relevancy = df["answer_relevancy"].mean() if "answer_relevancy" in df else 0.0
    avg_precision = df["context_precision"].mean() if "context_precision" in df else 0.0
    avg_recall = df["context_recall"].mean() if "context_recall" in df else 0.0
    avg_correctness = df["answer_correctness"].mean() if "answer_correctness" in df else 0.0
    
    md = [
        "# Báo cáo đánh giá RAGAS (End-to-End)",
        f"- Thời gian: `{datetime.now().isoformat()}`",
        f"- Số lượng test: **{len(ragas_data['question'])} câu**",
        "",
        "## Chỉ số trung bình (Metrics)",
        f"- **Faithfulness (Chống ảo giác):** {avg_faithfulness:.4f}",
        f"- **Answer Relevancy (Đúng trọng tâm):** {avg_relevancy:.4f}",
        f"- **Context Precision (Xếp hạng tài liệu):** {avg_precision:.4f}",
        f"- **Context Recall (Bao phủ thông tin):** {avg_recall:.4f}",
        f"- **Answer Correctness (Độ chính xác):** {avg_correctness:.4f}",
        "",
        "## Chi tiết từng câu",
    ]
    
    for i, row in df.iterrows():
        md.extend([
            f"### Câu {i+1}",
            f"- **Question:** {row.get('question', '')}",
            f"- **Ground Truth:** {row.get('ground_truth', '')}",
            f"- **Answer:** {row.get('answer', '')}",
            "",
            "**Điểm Ragas:**",
            f"- Faithfulness: `{row.get('faithfulness', 0)}`",
            f"- Answer Relevancy: `{row.get('answer_relevancy', 0)}`",
            f"- Context Precision: `{row.get('context_precision', 0)}`",
            f"- Context Recall: `{row.get('context_recall', 0)}`",
            f"- Answer Correctness: `{row.get('answer_correctness', 0)}`",
            "---"
        ])
        
    report_path.write_text("\n".join(md), encoding="utf-8")
    print(f"\n✅ Đã lưu báo cáo tại: {report_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit("Lỗi: Cần cấu hình biến môi trường GOOGLE_API_KEY")
        
    asyncio.run(run_evaluation(args))

if __name__ == "__main__":
    main()
