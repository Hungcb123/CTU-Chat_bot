import re
from pathlib import Path

path = Path("/mnt/d/Project/Chatbot/scripts/evaluate_chat_dataset.py")
content = path.read_text(encoding="utf-8")

# 1. Imports
content = content.replace(
    "from collections import defaultdict\nfrom dataclasses import asdict, dataclass",
    "from collections import defaultdict\nfrom pydantic import BaseModel, Field\nfrom langchain_groq import ChatGroq\nfrom langchain_core.prompts import PromptTemplate"
)

# 2. Docstring
content = content.replace(
    "The evaluator deliberately does not use another LLM as a judge.  It computes a\ndeterministic score from expected numeric facts and Vietnamese content-token\nrecall",
    "The evaluator uses Llama-3.3-70B via Groq as an LLM judge to evaluate answers"
)

# 3. ScoreResult
content = re.sub(
    r"@dataclass\(frozen=True\)\nclass ScoreResult:.*?missing_facts: tuple\[str, \.\.\.\]\n",
    'class ScoreResult(BaseModel):\n'
    '    score: float = Field(description="Score from 0.0 to 1.0 based on how well the actual answer matches the expected answer.")\n'
    '    passed: bool = Field(description="True if the answer is considered correct and accurate, False otherwise.")\n'
    '    reasoning: str = Field(description="Brief reasoning for the score and pass/fail decision.")\n',
    content,
    flags=re.DOTALL
)

# 4. Remove heuristics and update score_answer
heuristics_pattern = r"VIETNAMESE_STOPWORDS = \{.*?def score_answer\(expected: str, actual: str, \*, threshold: float = 0\.55\) -> ScoreResult:.*?missing_facts=tuple\(sorted\(missing_facts\)\),\n    \)"

new_score_answer = '''def score_answer(expected: str, actual: str, llm: ChatGroq) -> ScoreResult:
    prompt = PromptTemplate.from_template(
        "You are an expert judge evaluating an AI chatbot's response in Vietnamese.\\n"
        "Expected Answer:\\n{expected}\\n\\n"
        "Actual Answer:\\n{actual}\\n\\n"
        "Evaluate the actual answer against the expected answer.\\n"
        "Determine a score between 0.0 and 1.0 based on accuracy, and set passed to true if it captures the essential expected facts correctly.\\n"
        "Output ONLY a valid JSON object with keys: 'score', 'passed', and 'reasoning'."
    )
    chain = prompt | llm.with_structured_output(ScoreResult)
    try:
        return chain.invoke({"expected": expected, "actual": actual})
    except Exception as e:
        return ScoreResult(score=0.0, passed=False, reasoning=f"Error evaluating: {e}")'''

content = re.sub(heuristics_pattern, new_score_answer, content, flags=re.DOTALL)


# 5. _write_markdown_report updates
content = content.replace(
    "> Cách chấm không gọi thêm LLM: 60% độ đúng dữ kiện số/ngày/%, \"\n        \"40% độ bao phủ từ nội dung. Với câu không có số, điểm bằng content recall. \"\n        \"Câu trả lời từ chối/không tìm thấy thông tin bị trừ 75% điểm và không được pass.",
    "> Cách chấm: Sử dụng Llama-3.3-70B-Versatile (via Groq) làm giám khảo (LLM-as-a-judge)."
)
content = content.replace(
    "- Accuracy heuristic:",
    "- Accuracy LLM-as-a-judge:"
)
content = re.sub(
    r"f\"- Numeric recall.*?f\"- Dữ kiện số còn thiếu: `\{',\ '\.join\(record\.get\('missing_facts', \[\]\)\) or 'không'\}`\",",
    'f"- Lý do (Reasoning): {record.get(\'reasoning\', \'\')}",',
    content,
    flags=re.DOTALL
)

# 6. Rescore logic
content = content.replace(
    "            scoring = score_answer(\n                str(record.get(\"expected_answer\", \"\")),\n                str(record.get(\"actual_answer\", \"\")),\n                threshold=args.threshold,\n            )\n            record.update(asdict(scoring))",
    '            import os\n            llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, api_key=os.getenv("GROQ_API_KEY"))\n'
    '            scoring = score_answer(\n                str(record.get("expected_answer", "")),\n                str(record.get("actual_answer", "")),\n                llm=llm\n            )\n            record.update(scoring.dict())'
)

# 7. Main loop logic
content = content.replace(
    "                scoring = score_answer(\n                    case.expected_answer,\n                    actual_answer,\n                    threshold=args.threshold,\n                ) if actual_answer else ScoreResult(\n                    score=0.0,\n                    passed=False,\n                    abstained=False,\n                    content_recall=0.0,\n                    numeric_recall=0.0,\n                    expected_facts=tuple(sorted(_numeric_facts(case.expected_answer))),\n                    matched_facts=(),\n                    missing_facts=tuple(sorted(_numeric_facts(case.expected_answer))),\n                )",
    '                scoring = score_answer(\n                    case.expected_answer,\n                    actual_answer,\n                    llm=llm\n                ) if actual_answer else ScoreResult(\n                    score=0.0,\n                    passed=False,\n                    reasoning="No actual answer was provided or an error occurred."\n                )'
)

# 8. Add LLM initialization in main
content = content.replace(
    '    shared_session_id: str | None = None\n\n    print(f"Authenticated as {args.username}; running {len(cases)} /chat requests")',
    '    shared_session_id: str | None = None\n\n'
    '    import os\n'
    '    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, api_key=os.getenv("GROQ_API_KEY"))\n\n'
    '    print(f"Authenticated as {args.username}; running {len(cases)} /chat requests")'
)

# 9. Dictionary update
content = content.replace(
    '                    "error": error,\n                    **asdict(scoring),\n                }',
    '                    "error": error,\n                    **scoring.dict(),\n                }'
)

path.write_text(content, encoding="utf-8")
print("Refactoring complete.")
