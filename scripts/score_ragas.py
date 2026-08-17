import argparse
import json
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
from ragas.run_config import RunConfig
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import asyncio
from dotenv import load_dotenv

class RateLimitedChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    """Wrapper để giới hạn chính xác 15 RPM (1 request / 4s) cho toàn bộ script"""
    _rate_limit_lock = asyncio.Lock()
    
    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        kwargs.pop("n", None) # Xóa tham số n để tránh lỗi 400 Multiple candidates
        async with self._rate_limit_lock:
            await asyncio.sleep(4.1)
            return await super()._agenerate(messages, stop, run_manager, **kwargs)
            
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        kwargs.pop("n", None) # Xóa tham số n để tránh lỗi 400 Multiple candidates
        import time
        time.sleep(4.1)
        return super()._generate(messages, stop, run_manager, **kwargs)

load_dotenv()

def score_data(json_path: Path):
    print("Đang đọc dữ liệu từ JSON...")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    
    hf_dataset = Dataset.from_dict(data)
    
    print(f"\nĐang chạy Ragas Evaluator (LLM-as-a-judge) cho {len(data['question'])} câu hỏi...")
    
    # Configure Ragas judge models
    judge_llm = RateLimitedChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    judge_embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # Rate limit configuration cho Ragas để tránh limit 15 RPM của bản free
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
    
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("logs/dataset_evaluation")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"ragas_eval_{stamp}.md"
    
    avg_faithfulness = df["faithfulness"].mean() if "faithfulness" in df else 0.0
    avg_relevancy = df["answer_relevancy"].mean() if "answer_relevancy" in df else 0.0
    avg_precision = df["context_precision"].mean() if "context_precision" in df else 0.0
    avg_recall = df["context_recall"].mean() if "context_recall" in df else 0.0
    avg_correctness = df["answer_correctness"].mean() if "answer_correctness" in df else 0.0
    
    md = [
        "# Báo cáo đánh giá RAGAS (End-to-End)",
        f"- Thời gian: `{datetime.now().isoformat()}`",
        f"- Số lượng test: **{len(data['question'])} câu**",
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/ragas_data_temp.json"))
    args = parser.parse_args()
    score_data(args.data)
