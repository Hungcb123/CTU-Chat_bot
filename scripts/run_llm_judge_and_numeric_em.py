#!/usr/bin/env python3
"""LLM-as-a-Judge & Numeric Exact Match Evaluator for Scenario 1 (S1-A, S1-B, S1-C).

Directly addresses reviewer feedback:
1. LLM-as-a-Judge (semantic accuracy / rubric) replacing flawed substring containment.
2. Numeric Exact Match for financial / tuition fee queries.
"""

from __future__ import annotations

import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

SERVICE_ACCOUNT_KEY = ROOT / "gen-lang-client-0656432358-9a6fb12696b2.json"
RESULTS_JSONL = ROOT / "logs" / "v13_architecture" / "run_20260923_155602" / "results.jsonl"
CHECKPOINT_PATH = ROOT / "logs" / "v13_architecture" / "run_20260923_155602" / "llm_judge_eval.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("judge_eval")


def extract_numbers_and_currencies(text: str) -> set[str]:
    """Extract normalized financial numbers (e.g. 40.000.000, 192.183.000, 40 triệu, 50%)."""
    normalized = text.lower()
    # Normalize 'triệu' -> e.g. 40 triệu -> 40000000 or keep standard forms
    tokens = set()
    # Match currency patterns like 40.000.000, 192,183,000, 451.000
    for match in re.findall(r"\b\d{1,3}(?:[.,]\d{3})+(?:\s*(?:đ|vnđ|đồng))?\b", normalized):
        cleaned = re.sub(r"[^\d]", "", match)
        if cleaned:
            tokens.add(cleaned)
    # Match patterns like 40 triệu, 10 triệu, 50%
    for match in re.findall(r"\b\d+(?:[.,]\d+)?\s*(?:triệu|nghìn|ngàn|tỷ|%)\b", normalized):
        tokens.add(re.sub(r"\s+", "", match))
    return tokens


def compute_numeric_exact_match(reference: str, response: str) -> float:
    """Strict numeric check: all key financial figures in reference must be present in response."""
    ref_nums = extract_numbers_and_currencies(reference)
    if not ref_nums:
        return 1.0  # No numeric claim to check
    resp_nums = extract_numbers_and_currencies(response)
    matched = ref_nums.intersection(resp_nums)
    return 1.0 if len(matched) == len(ref_nums) else (len(matched) / len(ref_nums))


JUDGE_RUBRIC = """Bạn là Thẩm định viên Khoa học AI (LLM-as-a-Judge) độc lập, đánh giá chất lượng câu trả lời của Chatbot tư vấn đại học (CTU-Chat).
Nhiệm vụ của bạn là đánh giá câu trả lời của hệ thống (Generated Response) so với câu hỏi và sự thật nền (Ground Truth / Reference Answer).

HÃY ĐÁNH GIÁ THEO 2 THƯỚC ĐO:

1. AC (Answer Correctness / Semantic Accuracy) [thang điểm từ 0.0 đến 1.0]:
- 1.0: Câu trả lời hoàn toàn chính xác về mặt sự thật, logic, số liệu và điều kiện so với Ground Truth.
- 0.7 - 0.9: Đúng trọng tâm, đúng sự thật cốt lõi nhưng thiếu một số chi tiết phụ không ảnh hưởng lớn đến kết luận.
- 0.4 - 0.6: Trả lời đúng một phần nhưng bỏ sót ý quan trọng hoặc có điểm mơ hồ.
- 0.1 - 0.3: SAI DỮ KIỆN QUAN TRỌNG:
  * Nếu tính sai con số học phí, số tiền miễn giảm, số tín chỉ cốt lõi.
  * Nếu nhầm lẫn đối tượng áp dụng (cohort, ngành, diện chính sách).
  * Chú ý: Dù câu trả lời có chứa từ khóa của Ground Truth nhưng đặt trong ngữ cảnh sai hoặc kết quả tính toán cuối cùng sai -> BẮT BUỘC chấm AC <= 0.3.
- 0.0: Hoàn toàn sai, lạc đề hoặc bịa đặt (hallucination).

2. AR (Answer Relevancy) [thang điểm từ 0.0 đến 1.0]:
- Mức độ câu trả lời giải quyết trực tiếp và đầy đủ câu hỏi của sinh viên.
- 1.0: Đi thẳng vào câu hỏi, mạch lạc, súc tích.
- 0.5: Trả lời lan man hoặc chỉ giải quyết một góc nhỏ của câu hỏi.
- 0.0: Không trả lời câu hỏi.

=== CÂU HỎI CỦA SINH VIÊN ===
{question}

=== SỰ THẬT NỀN (GROUND TRUTH / REFERENCE ANSWER) ===
{reference_answer}

=== CÂU TRẢ LỜI CỦA HỆ THỐNG (GENERATED RESPONSE) ===
{response}

Hãy trả về DUY NHẤT một chuỗi JSON hợp lệ với cấu trúc sau:
{{"AC": <float từ 0.0 đến 1.0>, "AR": <float từ 0.0 đến 1.0>, "reason": "<giải thích ngắn gọn trong 1-2 câu>"}}
"""


class JudgeEvaluator:
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        self.model_name = model_name
        if SERVICE_ACCOUNT_KEY.exists():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(SERVICE_ACCOUNT_KEY.resolve())
            sa_data = json.loads(SERVICE_ACCOUNT_KEY.read_text(encoding="utf-8"))
            project = sa_data.get("project_id", "gen-lang-client-0656432358")
            self.client = genai.Client(vertexai=True, project=project, location="us-central1")
            logger.info("Initialized Vertex AI client for Judge (%s, project=%s)", model_name, project)
        else:
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            logger.info("Initialized Google AI Studio client for Judge (%s)", model_name)

    def evaluate_one(self, record: dict[str, Any]) -> dict[str, Any]:
        question = record.get("question", "")
        reference = record.get("reference_answer", "")
        response = record.get("response", "")
        domain = record.get("domain", "")

        # 1. Numeric exact match for financial
        is_financial = "financial" in domain or any(k in question.lower() for k in ("học phí", "miễn giảm", "tiền", "đồng", "triệu"))
        num_em = compute_numeric_exact_match(reference, response) if is_financial else None

        # 2. LLM Judge
        prompt = JUDGE_RUBRIC.format(
            question=question,
            reference_answer=reference,
            response=response if response.strip() else "(Hệ thống không đưa ra câu trả lời)",
        )

        ac = 0.0
        ar = 0.0
        reason = ""

        if not response.strip():
            return {
                "AC": 0.0,
                "AR": 0.0,
                "Pass_50": 0,
                "Pass_75": 0,
                "Num_EM": 0.0 if is_financial else None,
                "is_financial": is_financial,
                "reason": "Empty response",
            }

        for attempt in range(3):
            try:
                res = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                txt = res.text.strip()
                if "```json" in txt:
                    txt = txt.split("```json")[1].split("```")[0].strip()
                elif "```" in txt:
                    txt = txt.split("```")[1].split("```")[0].strip()
                data = json.loads(txt)
                ac = float(data.get("AC", 0.0))
                ar = float(data.get("AR", 0.0))
                reason = str(data.get("reason", ""))
                break
            except Exception as e:
                logger.warning("Judge attempt %d/3 failed for query %s: %s", attempt + 1, record.get("query_id"), e)
                time.sleep(1.0 * (attempt + 1))

        ac = min(1.0, max(0.0, ac))
        ar = min(1.0, max(0.0, ar))

        return {
            "AC": ac,
            "AR": ar,
            "Pass_50": 1 if ac >= 0.50 else 0,
            "Pass_75": 1 if ac >= 0.75 else 0,
            "Num_EM": num_em,
            "is_financial": is_financial,
            "reason": reason,
        }


def main():
    parser = argparse.ArgumentParser(description="Evaluate Scenario 1 with LLM-as-a-Judge & Num-EM")
    parser.add_argument("--workers", type=int, default=8, help="Number of concurrent judge threads")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of queries per config for quick test")
    parser.add_argument("--configs", nargs="+", default=["S1-A", "S1-B", "S1-C"], help="Configurations to evaluate")
    args = parser.parse_args()

    if not RESULTS_JSONL.exists():
        logger.error("Results file not found: %s", RESULTS_JSONL)
        sys.exit(1)

    # Load existing checkpoint if available
    checkpoint: dict[str, Any] = {}
    if CHECKPOINT_PATH.exists():
        try:
            checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
            logger.info("Loaded checkpoint with %d existing judgements", len(checkpoint))
        except Exception as e:
            logger.warning("Could not read checkpoint: %s", e)

    # Load target records
    records_to_run = []
    with RESULTS_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            cfg = rec.get("configuration")
            if cfg in args.configs:
                key = f"{cfg}:{rec.get('query_id')}"
                if key not in checkpoint:
                    records_to_run.append((key, rec))

    if args.limit:
        records_to_run = records_to_run[: args.limit * len(args.configs)]

    logger.info("Total records to evaluate: %d (already done: %d)", len(records_to_run), len(checkpoint))

    judge = JudgeEvaluator()

    # Run evaluations concurrently
    if records_to_run:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_key = {
                executor.submit(judge.evaluate_one, rec): (key, rec)
                for key, rec in records_to_run
            }

            count = 0
            for future in as_completed(future_to_key):
                key, rec = future_to_key[future]
                try:
                    result = future.result()
                    checkpoint[key] = {
                        "config": rec.get("configuration"),
                        "query_id": rec.get("query_id"),
                        "domain": rec.get("domain"),
                        **result,
                    }
                    count += 1
                    if count % 10 == 0 or count == len(records_to_run):
                        logger.info("Evaluated [%d/%d] queries...", count, len(records_to_run))
                        CHECKPOINT_PATH.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
                except Exception as e:
                    logger.error("Evaluation error for %s: %s", key, e)

        CHECKPOINT_PATH.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Saved all judgements to %s", CHECKPOINT_PATH)

    # Summary Statistics
    print("\n" + "=" * 80)
    print("SCENARIO 1: LLM-AS-A-JUDGE & NUMERIC EXACT MATCH SUMMARY (N=100)")
    print("=" * 80)
    print(f"{'Configuration':<22} | {'Pass(AC>=.50)':<13} | {'Pass(AC>=.75)':<13} | {'Mean AC':<9} | {'Mean AR':<9} | {'Num-EM (Fin)':<13}")
    print("-" * 88)

    summary_stats = {}
    for cfg in args.configs:
        cfg_items = [v for k, v in checkpoint.items() if v.get("config") == cfg]
        if not cfg_items:
            continue
        n = len(cfg_items)
        pass_50 = sum(v["Pass_50"] for v in cfg_items) / n * 100
        pass_75 = sum(v["Pass_75"] for v in cfg_items) / n * 100
        mean_ac = sum(v["AC"] for v in cfg_items) / n * 100
        mean_ar = sum(v["AR"] for v in cfg_items) / n * 100

        fin_items = [v for v in cfg_items if v.get("Num_EM") is not None]
        num_em = (sum(v["Num_EM"] for v in fin_items) / len(fin_items) * 100) if fin_items else 0.0

        summary_stats[cfg] = {
            "n": n,
            "pass_50": pass_50,
            "pass_75": pass_75,
            "mean_ac": mean_ac,
            "mean_ar": mean_ar,
            "num_em": num_em,
            "n_fin": len(fin_items),
        }
        print(f"{cfg:<22} | {pass_50:>11.1f}% | {pass_75:>11.1f}% | {mean_ac:>7.2f}% | {mean_ar:>7.2f}% | {num_em:>11.1f}%")

    print("=" * 88)

    # Compare CTU-Chat (S1-C) vs Single Agent (S1-A)
    if "S1-C" in summary_stats and "S1-A" in summary_stats:
        delta_p50 = summary_stats["S1-C"]["pass_50"] - summary_stats["S1-A"]["pass_50"]
        delta_ac = summary_stats["S1-C"]["mean_ac"] - summary_stats["S1-A"]["mean_ac"]
        delta_em = summary_stats["S1-C"]["num_em"] - summary_stats["S1-A"]["num_em"]
        print(f"\nDelta (CTU-Chat S1-C vs Single Agent S1-A):")
        print(f"  Δ Pass (AC >= 0.50): {delta_p50:+.1f} pp")
        print(f"  Δ Answer Correctness: {delta_ac:+.2f} pp")
        print(f"  Δ Numeric Exact Match (Financial): {delta_em:+.1f} pp")


if __name__ == "__main__":
    main()
