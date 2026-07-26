"""Evaluate ``data/dataset.md`` through the real authenticated ``/chat`` API.

The evaluator uses Llama-3.3-70B via Groq as an LLM judge to evaluate answers, then writes both JSONL evidence and a human-readable Markdown report.

Examples (run while FastAPI is already listening on port 8000):

    python scripts/evaluate_chat_dataset.py --username hung --password hung --limit 5
    python scripts/evaluate_chat_dataset.py --username hung --password hung
    python scripts/evaluate_chat_dataset.py --dry-run
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "dataset.md"
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs" / "dataset_evaluation"
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class DatasetCase:
    case_id: int
    category: str
    question: str
    expected_answer: str
    expected_sources: tuple[str, ...]


class ScoreResult(BaseModel):
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Score from 0.0 to 1.0 based on how well the actual answer matches the expected answer.",
    )
    passed: bool = Field(description="True if the answer is considered correct and accurate, False otherwise.")
    reasoning: str = Field(description="Brief reasoning for the score and pass/fail decision.")


SECTION_RE = re.compile(r"(?m)^\s*\d+\.\s*Ngữ cảnh:\s*(.+?)\s*$")
QUESTION_RE = re.compile(
    r"(?ms)^\s*Câu hỏi\s+(\d+):\s*(.*?)\s*"
    r"Câu trả lời mong đợi:\s*(.*?)\s*\n\s*\.\s*Tên file gốc:\s*"
    r"(.*?)(?=^\s*Câu hỏi\s+\d+:|^\s*\d+\.\s*Ngữ cảnh:|\Z)"
)


def score_answer(
    expected: str,
    actual: str,
    *,
    llm: Any,
    threshold: float = 0.55,
) -> ScoreResult:
    prompt = PromptTemplate.from_template(
        """You are an expert judge evaluating an AI chatbot's response in Vietnamese.

Expected Answer:
{expected}

Actual Answer:
{actual}

Evaluate the actual answer against the expected answer.
Determine a score between 0.0 and 1.0 based on accuracy.
Set passed to true only when the score is at least {threshold} and the answer
captures the essential expected facts correctly.
Output ONLY a valid JSON object with keys: 'score', 'passed', and 'reasoning'."""
    )
    chain = prompt | llm.with_structured_output(ScoreResult)
    try:
        judgement = chain.invoke(
            {
                "expected": expected,
                "actual": actual,
                "threshold": threshold,
            }
        )
        return ScoreResult(
            score=judgement.score,
            passed=bool(judgement.passed and judgement.score >= threshold),
            reasoning=judgement.reasoning,
        )
    except Exception as e:
        return ScoreResult(score=0.0, passed=False, reasoning=f"Error evaluating: {e}")


def parse_dataset(path: Path) -> list[DatasetCase]:
    text = path.read_text(encoding="utf-8")
    sections = [(match.start(), match.group(1).strip()) for match in SECTION_RE.finditer(text)]
    if not sections:
        raise ValueError(f"No 'Ngữ cảnh' sections found in {path}")

    cases: list[DatasetCase] = []
    seen_ids: set[int] = set()
    for match in QUESTION_RE.finditer(text):
        case_id = int(match.group(1))
        if case_id in seen_ids:
            raise ValueError(f"Duplicate question id {case_id}")
        seen_ids.add(case_id)
        category = next(
            (name for position, name in reversed(sections) if position < match.start()),
            "Không phân loại",
        )
        source_text = re.sub(r"\s+", " ", match.group(4)).strip().rstrip(".")
        sources = tuple(part.strip() for part in source_text.split(",") if part.strip())
        cases.append(
            DatasetCase(
                case_id=case_id,
                category=category,
                question=re.sub(r"\s+", " ", match.group(2)).strip(),
                expected_answer=re.sub(r"\s+", " ", match.group(3)).strip(),
                expected_sources=sources,
            )
        )

    if not cases:
        raise ValueError(f"No questions found in {path}")
    expected_ids = list(range(min(seen_ids), max(seen_ids) + 1))
    actual_ids = sorted(seen_ids)
    if actual_ids != expected_ids:
        missing = sorted(set(expected_ids) - seen_ids)
        raise ValueError(f"Question ids are not contiguous; missing {missing}")
    return sorted(cases, key=lambda case: case.case_id)


def _open_json(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    payload: dict[str, Any],
    timeout: float,
) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"detail": raw or str(exc)}
        return exc.code, body


def _write_markdown_report(
    path: Path,
    *,
    records: list[dict[str, Any]],
    dataset_path: Path,
    base_url: str,
    threshold: float,
    started_at: str,
) -> None:
    total = len(records)
    passed = sum(bool(record.get("passed")) for record in records)
    accuracy = passed / total if total else 0.0
    average_score = (
        sum(float(record.get("score", 0.0)) for record in records) / total
        if total
        else 0.0
    )
    category_rows: list[str] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["category"])].append(record)
    for category, items in grouped.items():
        category_passed = sum(bool(item.get("passed")) for item in items)
        category_rows.append(
            f"| {category} | {category_passed}/{len(items)} | "
            f"{category_passed / len(items) * 100:.2f}% |"
        )

    lines = [
        "# Báo cáo đánh giá `/chat`",
        "",
        f"- Thời điểm bắt đầu: `{started_at}`",
        f"- Dataset: `{dataset_path}`",
        f"- API: `{base_url.rstrip('/')}/chat`",
        f"- Số câu đã chạy: **{total}**",
        f"- Số câu đạt: **{passed}**",
        f"- Số lỗi HTTP/API: **{sum(bool(record.get('error')) for record in records)}**",
        f"- Accuracy LLM-as-a-judge: **{accuracy * 100:.2f}%**",
        f"- Điểm trung bình: **{average_score * 100:.2f}%**",
        f"- Ngưỡng pass: `{threshold}`",
        "",
        "> Cách chấm: Sử dụng Llama-3.3-70B-Versatile (via Groq) làm giám khảo (LLM-as-a-judge).",
        "",
        "## Kết quả theo lĩnh vực",
        "",
        "| Lĩnh vực | Đạt | Accuracy |",
        "|---|---:|---:|",
        *category_rows,
        "",
        "## Chi tiết từng câu",
        "",
    ]
    for record in records:
        marker = "PASS" if record.get("passed") else "FAIL"
        lines.extend(
            [
                f"### Câu {record['case_id']} · {marker} · score={float(record.get('score', 0)):.4f}",
                "",
                f"- Lĩnh vực: {record['category']}",
                f"- HTTP: `{record.get('http_status')}` · Thời gian: `{float(record.get('duration_seconds', 0)):.2f}s`",
                f"- Nguồn kỳ vọng: `{', '.join(record.get('expected_sources', []))}`",
                f"- Lý do (Reasoning): {record.get('reasoning', '')}",
                "",
                "**Câu hỏi**",
                "",
                f"> {record['question']}",
                "",
                "**Câu trả lời mong đợi**",
                "",
                f"> {str(record['expected_answer']).replace(chr(10), '<br>')}",
                "",
                "**Câu trả lời thực tế**",
                "",
                f"> {str(record.get('actual_answer') or record.get('error') or '').replace(chr(10), '<br>')}",
                "",
                "---",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _filter_cases(cases: Iterable[DatasetCase], args: argparse.Namespace) -> list[DatasetCase]:
    selected = [
        case
        for case in cases
        if (args.from_id is None or case.case_id >= args.from_id)
        and (args.to_id is None or case.case_id <= args.to_id)
        and (args.category is None or args.category.casefold() in case.category.casefold())
    ]
    if args.limit is not None:
        selected = selected[: args.limit]
    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--username", default=os.getenv("CHATBOT_TEST_USERNAME", "hung"))
    parser.add_argument("--password", default=os.getenv("CHATBOT_TEST_PASSWORD"))
    parser.add_argument("--timeout", type=float, default=240.0)
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between /chat calls")
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--from-id", type=int)
    parser.add_argument("--to-id", type=int)
    parser.add_argument("--category", help="Case-insensitive category substring")
    parser.add_argument("--limit", type=int, help="Run only the first N selected cases")
    parser.add_argument("--shared-session", action="store_true", help="Reuse one chat session; default isolates every case")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Parse and list cases without API calls")
    parser.add_argument(
        "--rescore-jsonl",
        type=Path,
        help="Recompute scores from an existing JSONL without calling the API",
    )
    parser.add_argument("--fail-under", type=float, default=0.0, help="Exit non-zero if accuracy is below this 0..1 value")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 0 <= args.threshold <= 1:
        raise SystemExit("--threshold must be between 0 and 1")
    if not 0 <= args.fail_under <= 1:
        raise SystemExit("--fail-under must be between 0 and 1")
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be at least 1")
    if not args.dry_run and not os.getenv("GROQ_API_KEY"):
        raise SystemExit("GROQ_API_KEY is not set in the environment or project .env")

    dataset_path = args.dataset.resolve()
    if args.rescore_jsonl:
        source_path = args.rescore_jsonl.resolve()
        records = [
            json.loads(line)
            for line in source_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        for record in records:
            scoring = score_answer(
                str(record.get("expected_answer", "")),
                str(record.get("actual_answer", "")),
                llm=llm,
                threshold=args.threshold,
            )
            record.update(scoring.model_dump())

        args.output_dir.mkdir(parents=True, exist_ok=True)
        started = datetime.now().astimezone()
        stamp = started.strftime("%Y%m%d_%H%M%S")
        stem = f"{source_path.stem}_rescored_{stamp}"
        jsonl_path = args.output_dir / f"{stem}.jsonl"
        report_path = args.output_dir / f"{stem}.md"
        with jsonl_path.open("w", encoding="utf-8") as jsonl:
            for record in records:
                jsonl.write(json.dumps(record, ensure_ascii=False) + "\n")
        _write_markdown_report(
            report_path,
            records=records,
            dataset_path=dataset_path,
            base_url=args.base_url,
            threshold=args.threshold,
            started_at=started.isoformat(),
        )
        passed = sum(bool(record.get("passed")) for record in records)
        average = sum(float(record.get("score", 0)) for record in records) / len(records)
        print(f"Rescored {len(records)} records from {source_path}")
        print(f"Completed: {passed}/{len(records)} passed; average={average * 100:.2f}%")
        print(f"JSONL evidence: {jsonl_path}")
        print(f"Markdown report: {report_path}")
        return 0

    cases = _filter_cases(parse_dataset(dataset_path), args)
    if not cases:
        raise SystemExit("No dataset cases matched the selected filters")
    dataset_hash = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    print(f"Parsed {len(cases)} cases from {dataset_path}")
    print(f"Dataset SHA256: {dataset_hash}")
    for case in cases if args.dry_run else []:
        print(f"[{case.case_id:02d}] {case.category}: {case.question}")
    if args.dry_run:
        print("Dry-run complete; no HTTP request was made.")
        return 0

    password = args.password or getpass.getpass(f"Password for {args.username}: ")
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    base_url = args.base_url.rstrip("/") + "/"
    login_status, login_body = _open_json(
        opener,
        urljoin(base_url, "auth/login"),
        payload={"username": args.username, "password": password},
        timeout=args.timeout,
    )
    if login_status < 200 or login_status >= 300:
        print(f"Login failed ({login_status}): {login_body}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now().astimezone()
    stamp = started.strftime("%Y%m%d_%H%M%S")
    jsonl_path = args.output_dir / f"chat_eval_{stamp}.jsonl"
    report_path = args.output_dir / f"chat_eval_{stamp}.md"
    records: list[dict[str, Any]] = []
    shared_session_id: str | None = None

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    print(f"Authenticated as {args.username}; running {len(cases)} /chat requests")
    print(f"JSONL evidence: {jsonl_path}")
    try:
        with jsonl_path.open("w", encoding="utf-8") as jsonl:
            for position, case in enumerate(cases, start=1):
                payload: dict[str, Any] = {"query": case.question}
                if args.shared_session and shared_session_id:
                    payload["session_id"] = shared_session_id
                started_case = time.perf_counter()
                error: str | None = None
                actual_answer = ""
                response_session_id: str | None = None
                try:
                    status, body = _open_json(
                        opener,
                        urljoin(base_url, "chat"),
                        payload=payload,
                        timeout=args.timeout,
                    )
                    if 200 <= status < 300:
                        actual_answer = str(body.get("answer", ""))
                        response_session_id = body.get("session_id")
                        if args.shared_session:
                            shared_session_id = response_session_id or shared_session_id
                    else:
                        error = str(body.get("detail", body))
                except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                    status = 0
                    error = f"{type(exc).__name__}: {exc}"

                scoring = score_answer(
                    case.expected_answer,
                    actual_answer,
                    llm=llm,
                    threshold=args.threshold,
                ) if actual_answer else ScoreResult(
                    score=0.0,
                    passed=False,
                    reasoning="No actual answer was provided or an error occurred."
                )
                record = {
                    "case_id": case.case_id,
                    "category": case.category,
                    "question": case.question,
                    "expected_answer": case.expected_answer,
                    "actual_answer": actual_answer,
                    "expected_sources": list(case.expected_sources),
                    "http_status": status,
                    "session_id": response_session_id,
                    "duration_seconds": round(time.perf_counter() - started_case, 3),
                    "error": error,
                    **scoring.model_dump(),
                }
                records.append(record)
                jsonl.write(json.dumps(record, ensure_ascii=False) + "\n")
                jsonl.flush()
                verdict = "PASS" if scoring.passed else "FAIL"
                print(
                    f"[{position:02d}/{len(cases):02d}] case={case.case_id:02d} "
                    f"{verdict} score={scoring.score:.3f} time={record['duration_seconds']:.1f}s"
                )
                if position < len(cases) and args.delay > 0:
                    time.sleep(args.delay)
    except KeyboardInterrupt:
        print("\nInterrupted; writing a partial report for completed cases.", file=sys.stderr)

    _write_markdown_report(
        report_path,
        records=records,
        dataset_path=dataset_path,
        base_url=base_url,
        threshold=args.threshold,
        started_at=started.isoformat(),
    )
    total = len(records)
    passed = sum(record["passed"] for record in records)
    api_errors = sum(bool(record.get("error")) for record in records)
    accuracy = passed / total if total else 0.0
    print(
        f"Completed: {passed}/{total} passed; accuracy={accuracy * 100:.2f}%; "
        f"api_errors={api_errors}"
    )
    print(f"Markdown report: {report_path}")
    if total == 0 or api_errors:
        return 2
    return 1 if accuracy < args.fail_under else 0


if __name__ == "__main__":
    raise SystemExit(main())
