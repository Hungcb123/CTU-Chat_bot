import asyncio
import os
import json
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import random

load_dotenv()

async def generate_questions_from_file(file_path: str, num_questions: int, llm: ChatGoogleGenerativeAI) -> list:
    content = Path(file_path).read_text(encoding="utf-8")
    
    # We chunk the content loosely if it's too big, or just pass it in.
    # 4 files, 100 questions total = ~25 questions per file.
    
    prompt = f"""Dưới đây là nội dung từ một quy chế/văn bản. Hãy sinh ra {num_questions} câu hỏi và câu trả lời TỐT NHẤT có thể dùng để đánh giá hệ thống tư vấn (RAG).
Yêu cầu:
1. Câu hỏi phải đa dạng (có câu hỏi đóng, câu hỏi mở, câu hỏi cần suy luận).
2. Câu trả lời (Expected Answer) phải thật chính xác dựa hoàn toàn vào nội dung được cung cấp.
3. Không bịa đặt nội dung.
4. Trả về đúng định dạng Markdown như sau (KHÔNG dùng code block ```markdown hay json, CHỈ xuất trực tiếp chữ ra):

## 1. <Câu hỏi 1>
- **Expected Answer:** <Câu trả lời 1>

## 2. <Câu hỏi 2>
- **Expected Answer:** <Câu trả lời 2>

... (tiếp tục cho đến hết)

Nội dung văn bản:
{content}
"""

    print(f"Generating {num_questions} questions for {file_path}...")
    try:
        res = await llm.ainvoke(prompt)
        text = res.content.strip()
        
        # Remove any Markdown code blocks if the model wrapped it
        if text.startswith("```markdown"):
            text = text[11:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return text.strip()
    except Exception as e:
        print(f"Error on {file_path}: {e}")
        return ""

async def main():
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7)
    
    files = [
        "data/markdown/CVHT_2025.md",
        "data/markdown/CVHTv2007.md",
        "data/markdown/3hk.md",
        "data/markdown/QD1813_QD_ban_hanh_Quy_dinh_cong_tac_hoc_vu_2021.md"
    ]
    
    target_total = 100
    per_file = target_total // len(files)
    remainder = target_total % len(files)
    
    all_output = []
    all_output.append("# Dataset 100 Questions for RAGAS Evaluation\n")
    
    tasks = []
    counts = [per_file] * len(files)
    for i in range(remainder):
        counts[i] += 1
        
    for f, count in zip(files, counts):
        tasks.append(generate_questions_from_file(f, count, llm))
        
    results = await asyncio.gather(*tasks)
    
    # Re-number everything sequentially
    final_md = ""
    q_num = 1
    
    import re
    
    for res in results:
        # Split by ##
        blocks = re.split(r'##\s*\d+\.\s*', res)
        for block in blocks:
            if not block.strip(): continue
            if "- **Expected Answer:**" in block:
                # Reconstruct
                final_md += f"\n## {q_num}. {block.strip()}\n"
                q_num += 1
                
    out_path = Path("data/ragas_test_dataset.md")
    out_path.write_text(f"# Dataset 100 Questions for RAGAS Evaluation\n{final_md}", encoding="utf-8")
    print(f"\n✅ Đã tạo thành công {q_num - 1} câu hỏi và lưu tại: {out_path}")

if __name__ == "__main__":
    asyncio.run(main())
