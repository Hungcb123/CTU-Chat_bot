#!/usr/bin/env python3
"""Build the normalized development set and author-reviewable held-out set."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from scripts.scenario12_common import canonical_source, normalize_text  # noqa: E402

SOURCE_CSV = ROOT / "data" / "150_NATURAL_NO_APPENDIX.csv"
DEV_OUTPUT = ROOT / "data" / "scenario12_dev.jsonl"
HELDOUT_OUTPUT = ROOT / "data" / "scenario12_heldout.jsonl"
REVIEW_OUTPUT = ROOT / "data" / "scenario12_heldout_review.md"
SERVICE_ACCOUNT = ROOT / "gen-lang-client-0656432358-9a6fb12696b2.json"
MODEL = "gemini-2.5-flash-lite"

QUOTAS = {
    "actual_tuition": 20,
    "academic_rules": 6,
    "scholarship": 5,
    "student_loan": 4,
    "social_support": 4,
    "other": 4,
    "academic_program": 3,
    "exemption_policy": 2,
    "exemption_basis": 2,
}

SOURCE_POOLS = {
    "academic_rules": [
        "QD2457_Quy_dinh_xet_mien_va_cong_nhan_diem_HP_hinh_thuc_CQ_nam_2024_llp.md",
        "quychehocvu.md", "QD1813_QD_ban_hanh_Quy_dinh_cong_tac_hoc_vu_2021.md",
        "3_don_xin_hoc_lai_llp.md", "5_don_xin_tam_nghi_hoc_llp.md", "7_don_de_nghi_chuyen_ctdt_llp.md",
    ],
    "scholarship": [
        "HB_K51_2026.md", "HB_TanSinhVien_K52.md", "HB_Vallet_Chi_Tiet.md",
        "HB_SCIC_2026.md", "Tài liệu phân bổ quỹ học bổng.md",
    ],
    "student_loan": [
        "VayVonSinhVien2022.md", "VayVonVoiNhomNganhKThuat - Copy.md",
        "VayVonMuaMayTinh.md", "HuongDanXacNhanVayVon.md",
    ],
    "social_support": ["Ho_tro.md", "HoTroCp.md", "Tro_cap_XH.md", "TCXH.md"],
    "other": [
        "Noi quy KTX nam 2016_llp.md", "SoTay.md", "qt_cap_bangdiem_TV_TA_llp.md",
        "Phieu_De_nghi_cap_ban_sao_cap_lai_chinh_sua_NDVB_llp.md",
    ],
    "academic_program": [
        "108_7480107_TriTueNhanTao.md", "61_7510605_LogisticsVaQuanLyChuoiCungUng.md",
        "114_7540106_DamBaoChatLuongVaAnToanTthucPham.md",
    ],
    "exemption_policy": ["mghp.md", "12_don_de_nghi_mien_giam_hoc_phi_llp.md"],
    "exemption_basis": ["MucHocPhi_2526_MienGiam.md", "MucHocPhi_2526_MienGiam.md"],
}

FOCUS_HINTS = {
    ("exemption_basis", 1): "Chọn mức cơ sở của Khối ngành IV.",
    ("exemption_basis", 2): "Chọn riêng mức cơ sở của học phần Giáo dục quốc phòng và An ninh; không dùng Khối ngành IV.",
}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def parse_sources(value: str) -> list[str]:
    return list(dict.fromkeys(canonical_source(item) for item in re.split(r"[,;]", value or "") if item.strip()))


def build_dev() -> list[dict[str, Any]]:
    with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    rows = []
    for index, row in enumerate(source_rows, start=1):
        question = (row.get("Master Question") or row.get("Question") or "").strip()
        if not question:
            continue
        case_id = str(row.get("Original ID") or index)
        rows.append({
            "id": case_id,
            "category": (row.get("Category") or "").strip(),
            "question": question,
            "reference_answer": (row.get("Answer") or row.get("Ground Truth") or "").strip(),
            "raw_evidence": (row.get("Ground Truth") or row.get("Answer") or "").strip(),
            "gold_sources": parse_sources(row.get("Source") or ""),
            "source_relation": (row.get("source_relation") or "single").strip(),
            "required_facts": [],
            "query_family": f"dev-{case_id}",
            "is_composite": case_id.startswith("CDICT"),
            "review_status": "development",
        })
    if len(rows) != 150:
        raise ValueError(f"Development set phải có 150 câu, nhận {len(rows)}")
    write_jsonl(DEV_OUTPUT, rows)
    return rows


def select_tuition_records(count: int) -> list[dict[str, Any]]:
    payload = json.loads((ROOT / "data" / "tuition_rates.json").read_text(encoding="utf-8"))
    candidates = [
        row for row in payload["records"]
        if row.get("major_name") and row.get("cohort_min") == row.get("cohort_max")
    ]
    candidates.sort(key=lambda row: (
        row.get("program_type", ""), row.get("major_name", ""), row.get("cohort_min", 0), row.get("rate_type", ""),
    ))
    selected: list[dict[str, Any]] = []
    seen_major: Counter[str] = Counter()
    seen_program: Counter[str] = Counter()
    for row in sorted(candidates, key=lambda item: (seen_program[item["program_type"]], seen_major[item["major_name"]], item["id"])):
        if seen_major[row["major_name"]] >= 2:
            continue
        selected.append(row)
        seen_major[row["major_name"]] += 1
        seen_program[row["program_type"]] += 1
        if len(selected) == count:
            break
    if len(selected) != count:
        raise ValueError("Không đủ tuition records khác nhau để tạo held-out")
    return selected


def tuition_cases() -> list[dict[str, Any]]:
    program_labels = {"standard": "chương trình chuẩn", "high_quality": "chương trình chất lượng cao", "advanced": "chương trình tiên tiến"}
    rate_labels = {"per_academic_year": "mỗi năm học", "per_full_course": "toàn khóa", "per_credit": "mỗi tín chỉ"}
    rows = []
    for index, record in enumerate(select_tuition_records(QUOTAS["actual_tuition"]), start=1):
        cohort = record["cohort_min"]
        amount = int(record["amount_vnd"])
        program = program_labels.get(record["program_type"], record["program_type"])
        unit = rate_labels.get(record["rate_type"], record["rate_type"])
        question = f"Cho mình xin đúng mức thu {unit} của ngành {record['major_name']}, {program}, khóa {cohort} trong năm học {record['academic_year']}?"
        amount_text = f"{amount:,}".replace(",", ".")
        answer = f"Mức thu của ngành {record['major_name']}, {program}, khóa {cohort}, năm học {record['academic_year']} là {amount_text} đồng {unit}."
        rows.append({
            "id": f"HOUT-TUI-{index:02d}", "category": "actual_tuition", "question": question,
            "reference_answer": answer,
            "raw_evidence": f"{record['source_section']} | {record.get('source_table', '')} | {answer}",
            "gold_sources": [canonical_source(record["source"])], "source_relation": "single",
            "required_facts": [record["major_name"], str(cohort), str(amount), record["academic_year"]],
            "query_family": f"heldout-tuition-{record['id']}", "is_composite": False,
            "review_status": "pending", "source_section": record["source_section"],
            "source_table": record.get("source_table"),
        })
    return rows


def source_excerpt(path: Path, max_chars: int = 18000) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) <= max_chars:
        return text
    third = max_chars // 3
    return text[:third] + "\n...[TRUNCATED]...\n" + text[len(text) // 2:len(text) // 2 + third] + "\n...[TRUNCATED]...\n" + text[-third:]


def parse_json_response(content: Any) -> dict[str, Any]:
    if isinstance(content, list):
        content = "".join(str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in content)
    text = str(content).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("LLM output không phải JSON object")
    return payload


async def generate_case(llm: Any, category: str, source_name: str, index: int, semaphore: asyncio.Semaphore) -> dict[str, Any]:
    source_path = ROOT / "data" / "markdown" / source_name
    excerpt = source_excerpt(source_path)
    focus_hint = FOCUS_HINTS.get((category, index), "Tự chọn một fact cụ thể phù hợp category.")
    prompt = f"""Từ DUY NHẤT tài liệu CTU chính thống bên dưới, tạo đúng một test case tiếng Việt cho category `{category}`.
Câu hỏi phải tự nhiên, tự đủ nghĩa, kiểm tra một fact cụ thể chưa cần suy đoán. Không hỏi ngày hiện tại.
Đáp án phải hoàn toàn suy ra được từ trích đoạn. required_facts là 1--5 chuỗi bắt buộc phải có trong đáp án đúng.
Không đưa tên file vào câu hỏi. Trả về duy nhất JSON object với keys: question, reference_answer, required_facts, evidence_excerpt, is_composite.
evidence_excerpt phải là đoạn nguyên văn ngắn nhất trong tài liệu đủ chứng minh đáp án (tối đa 900 ký tự).

SOURCE FILE: {source_name}
CANDIDATE POSITION: {index} (nếu cùng source được dùng lại, bắt buộc chọn một fact khác theo vị trí này)
FOCUS: {focus_hint}
DOCUMENT:
{excerpt}
"""
    async with semaphore:
        response = await llm.ainvoke(prompt)
    payload = parse_json_response(response.content)
    required = [str(item).strip() for item in payload.get("required_facts", []) if str(item).strip()]
    if not payload.get("question") or not payload.get("reference_answer") or not required or not payload.get("evidence_excerpt"):
        raise ValueError(f"Case {category}/{source_name} thiếu trường bắt buộc")
    return {
        "id": f"HOUT-{category.upper().replace('_', '-')}-{index:02d}",
        "category": category,
        "question": str(payload["question"]).strip(),
        "reference_answer": str(payload["reference_answer"]).strip(),
        "raw_evidence": str(payload["evidence_excerpt"]).strip(),
        "gold_sources": [source_name],
        "source_relation": "single",
        "required_facts": required,
        "query_family": f"heldout-{category}-{Path(source_name).stem}-{index}",
        "is_composite": bool(payload.get("is_composite", False)),
        "review_status": "pending",
    }


async def generate_non_tuition(project: str, location: str, workers: int) -> list[dict[str, Any]]:
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model=MODEL, temperature=0.0, vertexai=True, project=project, location=location,
        response_mime_type="application/json", retries=6, request_timeout=180,
    )
    semaphore = asyncio.Semaphore(workers)
    tasks = []
    for category, quota in QUOTAS.items():
        if category == "actual_tuition":
            continue
        sources = SOURCE_POOLS[category]
        if len(sources) != quota:
            raise ValueError(f"SOURCE_POOLS[{category}] phải có đúng {quota} file")
        tasks.extend(generate_case(llm, category, source, index, semaphore) for index, source in enumerate(sources, start=1))
    return list(await asyncio.gather(*tasks))


def ngram_set(text: str, n: int = 5) -> set[tuple[str, ...]]:
    tokens = normalize_text(text).split()
    return {tuple(tokens[index:index + n]) for index in range(max(0, len(tokens) - n + 1))}


def jaccard(left: set[Any], right: set[Any]) -> float:
    return len(left & right) / len(left | right) if left or right else 1.0


def embedding_novelty(dev_questions: list[str], heldout_questions: list[str]) -> list[float]:
    from sentence_transformers import SentenceTransformer

    model_path = ROOT / "models" / "vietnamese-bi-encoder"
    model = SentenceTransformer(str(model_path) if model_path.exists() else "bkai-foundation-models/vietnamese-bi-encoder")
    vectors = model.encode(dev_questions + heldout_questions, normalize_embeddings=True, show_progress_bar=True)
    dev_vectors = vectors[:len(dev_questions)]
    heldout_vectors = vectors[len(dev_questions):]
    return [float(max(vector @ dev_vector for dev_vector in dev_vectors)) for vector in heldout_vectors]


def validate_novelty(dev: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> None:
    dev_questions = [row["question"] for row in dev]
    heldout_questions = [row["question"] for row in heldout]
    normalized_dev = {normalize_text(question) for question in dev_questions}
    dev_ngrams = [ngram_set(question) for question in dev_questions]
    max_embedding = embedding_novelty(dev_questions, heldout_questions)
    failures = []
    for index, row in enumerate(heldout):
        exact = normalize_text(row["question"]) in normalized_dev
        max_ngram = max(jaccard(ngram_set(row["question"]), grams) for grams in dev_ngrams)
        internal_exact = any(
            normalize_text(row["question"]) == normalize_text(previous["question"])
            for previous in heldout[:index]
        )
        internal_ngram = max(
            (jaccard(ngram_set(row["question"]), ngram_set(previous["question"])) for previous in heldout[:index]),
            default=0.0,
        )
        row["novelty"] = {
            "normalized_exact_duplicate": exact,
            "max_fivegram_jaccard": round(max_ngram, 6),
            "max_embedding_cosine": round(max_embedding[index], 6),
            "heldout_exact_duplicate": internal_exact,
            "heldout_max_fivegram_jaccard": round(internal_ngram, 6),
        }
        if exact or internal_exact or max_ngram >= 0.80 or internal_ngram >= 0.80 or max_embedding[index] >= 0.985:
            failures.append((row["id"], exact, internal_exact, max_ngram, internal_ngram, max_embedding[index]))
    if failures:
        raise ValueError(f"Held-out có case quá giống development: {failures}")


def validate(rows: list[dict[str, Any]]) -> None:
    if len(rows) != 50:
        raise ValueError(f"Held-out phải có 50 case, nhận {len(rows)}")
    counts = Counter(row["category"] for row in rows)
    if counts != Counter(QUOTAS):
        raise ValueError(f"Quota sai: {dict(counts)}")
    ids = [row["id"] for row in rows]
    families = [row["query_family"] for row in rows]
    if len(ids) != len(set(ids)) or len(families) != len(set(families)):
        raise ValueError("ID hoặc query_family bị trùng")
    for row in rows:
        for key in ("question", "reference_answer", "raw_evidence", "gold_sources", "required_facts"):
            if not row.get(key):
                raise ValueError(f"{row['id']} thiếu {key}")


def render_review(rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Scenario 1–2 held-out review", "",
        "> Bộ này là **author-reviewed held-out set**, không phải independent annotation.",
        "> Kiểm tra từng case rồi đổi `[ ] Approved` thành `[x] Approved`. Sau đó chạy",
        "> `wsl_venv/bin/python scripts/prepare_scenario12_datasets.py --apply-review`.", "",
        "## Quota", "",
    ]
    counts = Counter(row["category"] for row in rows)
    lines.extend(f"- `{category}`: {counts[category]}" for category in QUOTAS)
    for row in rows:
        novelty = row.get("novelty", {})
        lines.extend([
            "", f"## {row['id']} — {row['category']}", "",
            "- [ ] Approved", "- [ ] Question đúng và tự đủ nghĩa", "- [ ] Answer được source chứng minh", "- [ ] Required facts đầy đủ", "- [ ] Gold source đúng", "",
            f"**Question:** {row['question']}", "",
            f"**Reference answer:** {row['reference_answer']}", "",
            f"**Required facts:** `{json.dumps(row['required_facts'], ensure_ascii=False)}`", "",
            f"**Gold source:** `{', '.join(row['gold_sources'])}`", "",
            f"**Evidence excerpt:** {row['raw_evidence']}", "",
            f"**Novelty:** exact=`{novelty.get('normalized_exact_duplicate')}`, 5-gram=`{novelty.get('max_fivegram_jaccard')}`, embedding=`{novelty.get('max_embedding_cosine')}`",
        ])
    REVIEW_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply_review() -> None:
    rows = [json.loads(line) for line in HELDOUT_OUTPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    review = REVIEW_OUTPUT.read_text(encoding="utf-8")
    approved = set()
    for section in re.split(r"(?m)^## ", review)[1:]:
        first_line, _, body = section.partition("\n")
        case_id = first_line.split(" — ", 1)[0].strip()
        if re.search(r"(?mi)^- \[x\] Approved\s*$", body):
            approved.add(case_id)
    for row in rows:
        row["review_status"] = "approved" if row["id"] in approved else "pending"
    write_jsonl(HELDOUT_OUTPUT, rows)
    print(f"Applied review: {len(approved)}/{len(rows)} approved")
    if len(approved) != len(rows):
        raise SystemExit(2)


def configure_project(credentials: Path, project: str | None) -> str:
    if credentials.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials.resolve())
        project = project or json.loads(credentials.read_text(encoding="utf-8")).get("project_id")
    project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise RuntimeError("Thiếu Google Cloud project")
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    return project


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-review", action="store_true")
    parser.add_argument("--credentials", type=Path, default=SERVICE_ACCOUNT)
    parser.add_argument("--project")
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    if args.apply_review:
        apply_review()
        return
    dev = build_dev()
    project = configure_project(args.credentials, args.project)
    heldout = tuition_cases() + asyncio.run(generate_non_tuition(project, args.location, args.workers))
    validate(heldout)
    validate_novelty(dev, heldout)
    write_jsonl(HELDOUT_OUTPUT, heldout)
    render_review(heldout)
    print(f"Wrote {len(dev)} dev cases: {DEV_OUTPUT}")
    print(f"Wrote {len(heldout)} pending held-out cases: {HELDOUT_OUTPUT}")
    print(f"Review checklist: {REVIEW_OUTPUT}")


if __name__ == "__main__":
    main()
