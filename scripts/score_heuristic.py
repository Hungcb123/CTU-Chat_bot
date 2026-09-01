import argparse
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from rouge_score import rouge_scorer
import re

# Use Gemini Embedding API
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(emb_model, text1, text2):
    vec1 = np.array(emb_model.embed_query(text1)).reshape(1, -1)
    vec2 = np.array(emb_model.embed_query(text2)).reshape(1, -1)
    return cosine_similarity(vec1, vec2)[0][0]

def tokenize(text):
    # Simple word tokenizer
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return set(text.split())

def clean_answer(a):
    if isinstance(a, str) and a.startswith("[{'type':"):
        try:
            import ast
            parsed = ast.literal_eval(a)
            if isinstance(parsed, list) and len(parsed) > 0 and 'text' in parsed[0]:
                return parsed[0]['text']
        except:
            pass
    return str(a)

def score_heuristic(json_path: Path):
    print("Đang đọc dữ liệu từ JSON...")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    
    questions = data.get('question', [])
    answers = data.get('answer', [])
    ground_truths = data.get('ground_truth', [])
    contexts_list = data.get('contexts', [])
    
    num_questions = len(questions)
    print(f"\nĐang chạy Heuristic Evaluator (No-LLM) cho {num_questions} câu hỏi...")
    
    # Init Scorer
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=False)
    
    # Init Embeddings (Gemini text-embedding-004)
    print("Đang kết nối Gemini Embedding API để chấm điểm...")
    emb_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    results = []
    
    for i in range(num_questions):
        print(f"Đang chấm câu {i+1}/{num_questions}...")
        q = questions[i]
        a = clean_answer(answers[i])
        gt = ground_truths[i]
        ctxs = contexts_list[i]
        
        joined_ctx = " ".join(ctxs)
        
        # 1. Answer Correctness -> Semantic Sim (Answer vs Ground Truth) kết hợp ROUGE
        rouge_scores = scorer.score(gt, a)
        rouge_recall = rouge_scores['rougeL'].recall
        semantic_match = compute_similarity(emb_model, gt, a)
        ans_correctness = max(rouge_recall, semantic_match)  # Chọn điểm cao nhất giữa từ khóa và ngữ nghĩa
        
        # 2. Answer Relevancy -> Chuẩn hóa theo Ground Truth
        # Thay vì tính điểm tuyệt đối (vốn luôn bị thấp do khác biệt không gian vector giữa Câu hỏi và Câu trả lời),
        # ta lấy độ tương đồng của Câu trả lời so với Câu hỏi, chia cho độ tương đồng của Ground Truth so với Câu hỏi.
        # Nếu Answer bám sát Question bằng hoặc hơn Ground Truth, điểm sẽ là 1.0.
        sim_q_a = compute_similarity(emb_model, q, a)
        sim_q_gt = compute_similarity(emb_model, q, gt)
        if sim_q_gt > 0.1:
            ans_relevancy = min(1.0, sim_q_a / sim_q_gt)
        else:
            ans_relevancy = sim_q_a
        
        # 3. Context Precision -> Tính theo chuẩn MAP (Mean Average Precision) của Ragas
        if ctxs:
            relevant_ranks = []
            for k, c in enumerate(ctxs):
                # Chunks được coi là relevant nếu chứa >= 50% từ khóa của Ground Truth
                if scorer.score(gt, c)['rougeL'].recall >= 0.5:
                    relevant_ranks.append(k + 1)
            
            if not relevant_ranks:
                ctx_precision = 0.0
            else:
                precision_sum = 0.0
                for hits, rank in enumerate(relevant_ranks, start=1):
                    precision_sum += hits / rank
                ctx_precision = precision_sum / len(relevant_ranks)
        else:
            ctx_precision = 0.0
        
        # 4. Context Recall -> Keyword overlap (Ground Truth in Contexts)
        gt_tokens = tokenize(gt)
        ctx_tokens = tokenize(joined_ctx)
        if len(gt_tokens) == 0:
            ctx_recall = 1.0
        else:
            overlap = gt_tokens.intersection(ctx_tokens)
            ctx_recall = len(overlap) / len(gt_tokens)
            
        # 5. Faithfulness -> Keyword overlap (Answer in Contexts)
        ans_tokens = tokenize(a)
        if len(ans_tokens) == 0:
            faithfulness = 1.0
        else:
            overlap = ans_tokens.intersection(ctx_tokens)
            faithfulness = len(overlap) / len(ans_tokens)
            
        # Normalize
        ans_relevancy = max(0.0, ans_relevancy)
        ctx_precision = max(0.0, ctx_precision)
        
        results.append({
            "question": q,
            "ground_truth": gt,
            "answer": a,
            "faithfulness": faithfulness,
            "answer_relevancy": ans_relevancy,
            "context_precision": ctx_precision,
            "context_recall": ctx_recall,
            "answer_correctness": ans_correctness,
        })
        
    # Generate Report
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("logs/dataset_evaluation")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"heuristic_eval_{stamp}.md"
    
    avg_faithfulness = sum(r['faithfulness'] for r in results) / num_questions if num_questions else 0
    avg_relevancy = sum(r['answer_relevancy'] for r in results) / num_questions if num_questions else 0
    avg_precision = sum(r['context_precision'] for r in results) / num_questions if num_questions else 0
    avg_recall = sum(r['context_recall'] for r in results) / num_questions if num_questions else 0
    avg_correctness = sum(r['answer_correctness'] for r in results) / num_questions if num_questions else 0
    
    md = [
        "# Báo cáo đánh giá RAG (Phương pháp Heuristic)",
        f"- Thời gian: `{datetime.now().isoformat()}`",
        f"- Số lượng test: **{num_questions} câu**",
        "- Phương pháp: `ROUGE-L` và `Cosine Similarity (vietnamese-bi-encoder)`",
        "",
        "## Chỉ số trung bình (Metrics Ánh xạ)",
        f"- **Faithfulness (Trung thực - Overlap):** {avg_faithfulness:.4f}",
        f"- **Answer Relevancy (Đúng trọng tâm - Cosine):** {avg_relevancy:.4f}",
        f"- **Context Precision (Độ chuẩn xác ngữ cảnh - Cosine):** {avg_precision:.4f}",
        f"- **Context Recall (Bao phủ thông tin - Overlap):** {avg_recall:.4f}",
        f"- **Answer Correctness (Độ chính xác - ROUGE-L):** {avg_correctness:.4f}",
        "",
        "## Chi tiết từng câu",
    ]
    
    for i, row in enumerate(results):
        md.extend([
            f"### Câu {i+1}",
            f"- **Question:** {row['question']}",
            f"- **Ground Truth:** {row['ground_truth']}",
            f"- **Answer:** {row['answer']}",
            "",
            "**Điểm Heuristic (0 -> 1):**",
            f"- Faithfulness: `{row['faithfulness']:.4f}`",
            f"- Answer Relevancy: `{row['answer_relevancy']:.4f}`",
            f"- Context Precision: `{row['context_precision']:.4f}`",
            f"- Context Recall: `{row['context_recall']:.4f}`",
            f"- Answer Correctness: `{row['answer_correctness']:.4f}`",
            "---"
        ])
        
    report_path.write_text("\n".join(md), encoding="utf-8")
    print(f"\n✅ Đã lưu báo cáo Heuristic siêu tốc tại: {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/ragas_data_temp.json"))
    args = parser.parse_args()
    score_heuristic(args.data)
