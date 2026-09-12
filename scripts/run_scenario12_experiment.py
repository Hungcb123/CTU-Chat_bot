#!/usr/bin/env python3
"""Reproducible Scenario 1--2 runner with held-out gating and provenance logs."""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

from scripts.scenario12_common import (  # noqa: E402
    ScenarioCase,
    load_cases,
    mean,
    normalize_text,
    retrieve_configurations,
    sha256_file,
    sha256_text,
    source_from_document,
    source_metrics,
    stddev,
)

MODEL = "gemini-2.5-flash-lite"
TOP_K = 7
METRIC_K = 10
TEMPERATURE = 0.0
GENERATION_PROMPT_VERSION = "scenario12_grounded_complete_answer_v2"
RAGAS_RUBRIC_VERSION = "ragas-0.4-default-ar-cr-cp-ac-v1"
DEV_DATASET = ROOT / "data" / "scenario12_dev.jsonl"
HELDOUT_DATASET = ROOT / "data" / "scenario12_heldout.jsonl"
LOG_ROOT = ROOT / "logs" / "scenario12"
SERVICE_ACCOUNT = ROOT / "gen-lang-client-0656432358-9a6fb12696b2.json"
CONFIGS_S1 = ("E1", "E2", "E3", "E4", "E5")
CONFIGS_S2 = ("T1", "T2", "T3", "T4", "T5", "T6", "T7")

GENERATION_PROMPT = """Bạn là trợ lý tư vấn học vụ và học phí của Trường Đại học Cần Thơ (CTU).
Chỉ dùng evidence được cung cấp. Hãy trả lời câu hỏi bằng câu hoàn chỉnh, rõ ràng, nêu rõ chủ thể được hỏi (tên ngành, khóa, hệ đào tạo, học bổng hoặc thủ tục tương ứng) kèm dữ kiện số liệu hoặc quy định chính xác.
Nếu evidence chỉ hỗ trợ một phần, trả lời phần biết được và nêu phần còn thiếu.
Chỉ nói không tìm thấy khi toàn bộ evidence không có dữ kiện liên quan.

EVIDENCE:
{contexts}

QUESTION: {question}
ANSWER:"""


def json_dump(path: Path, payload: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def append_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def configure_vertex(credentials: Path, project: str | None) -> str:
    if credentials.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials.resolve())
        metadata = json.loads(credentials.read_text(encoding="utf-8"))
        project = project or metadata.get("project_id")
    if not project:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise RuntimeError("Không xác định được Google Cloud project cho Vertex AI")
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project
    return project


def signature(dataset: Path, args: argparse.Namespace) -> dict[str, Any]:
    import ragas

    tracked = [
        ROOT / "scripts" / "scenario12_common.py",
        Path(__file__),
        ROOT / "app" / "services" / "graph_service.py",
        ROOT / "Graph_DB" / "app" / "ingest_tuition.py",
    ]
    graph_data = sorted((ROOT / "Graph_DB" / "data").glob("**/*"))
    graph_data = [path for path in graph_data if path.is_file()]
    catalog = ROOT / "data" / "tuition_rates.json"
    return {
        "dataset_sha256": sha256_file(dataset),
        "code_sha256": sha256_text("".join(sha256_file(path) for path in tracked)),
        "prompt_sha256": sha256_text(GENERATION_PROMPT),
        "judge_rubric_sha256": sha256_text(RAGAS_RUBRIC_VERSION),
        "graph_data_sha256": sha256_text("".join(sha256_file(path) for path in graph_data)),
        "catalog_sha256": sha256_file(catalog),
        "model": args.model,
        "ragas_version": ragas.__version__,
        "top_k": TOP_K,
        "metric_k": METRIC_K,
        "scenario": args.scenario,
        "split": args.split,
        "limit": args.limit,
        "configurations": list(CONFIGS_S1 + CONFIGS_S2),
        "generation": {
            "temperature": TEMPERATURE,
            "repetitions": args.repetitions,
            "embedding_model": args.embedding_model,
            "embedding_backend": args.embedding_backend,
            "location": args.location,
        },
    }


def latest_resumable_run(expected: dict[str, Any]) -> Path | None:
    if not LOG_ROOT.exists():
        return None
    for directory in sorted((p for p in LOG_ROOT.iterdir() if p.is_dir()), reverse=True):
        checkpoint = directory / "checkpoint.json"
        if checkpoint.exists():
            try:
                if json.loads(checkpoint.read_text(encoding="utf-8")).get("signature") == expected:
                    return directory
            except (OSError, json.JSONDecodeError):
                continue
    return None


def create_run_dir(expected: dict[str, Any], resume: bool) -> tuple[Path, dict[str, Any]]:
    if resume:
        found = latest_resumable_run(expected)
        if not found:
            raise RuntimeError("Không có checkpoint nào có chữ ký khớp hoàn toàn để resume")
        return found, json.loads((found / "checkpoint.json").read_text(encoding="utf-8"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = LOG_ROOT / stamp
    suffix = 1
    while run_dir.exists():
        run_dir = LOG_ROOT / f"{stamp}-{suffix}"
        suffix += 1
    run_dir.mkdir(parents=True)
    checkpoint = {"signature": expected, "retrieval": {}, "answers": {}, "ragas": {}}
    json_dump(run_dir / "checkpoint.json", checkpoint)
    return run_dir, checkpoint


def setup_logging(run_dir: Path) -> logging.Logger:
    logger = logging.getLogger("scenario12")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    for handler in (logging.StreamHandler(), logging.FileHandler(run_dir / "run.log", encoding="utf-8")):
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def retrieval_metrics(sources: list[str], gold: list[str]) -> dict[str, float]:
    sources = list(dict.fromkeys(source for source in sources if source))
    gold_set = set(gold)
    ranks = [index + 1 for index, source in enumerate(sources[:METRIC_K]) if source in gold_set]
    top5_hits = sum(1 for source in sources[:5] if source in gold_set)
    return {
        "hit_at_1": float(any(rank <= 1 for rank in ranks)),
        "hit_at_3": float(any(rank <= 3 for rank in ranks)),
        "precision_at_5": top5_hits / 5,
        "recall_at_5": top5_hits / len(gold_set) if gold_set else 1.0,
        "mrr_at_10": 1 / ranks[0] if ranks else 0.0,
    }


def factual_exact_match(case: ScenarioCase, answer: str) -> float:
    facts = case.required_facts
    if not facts:
        facts = list(dict.fromkeys(
            token for token in __import__("re").findall(r"\b[\d][\d.,/%-]*\b", case.reference_answer)
        ))
    if not facts:
        return float(bool(normalize_text(answer)))
    normalized_answer = normalize_text(answer)
    return sum(normalize_text(fact) in normalized_answer for fact in facts) / len(facts)


def document_payload(document: Any) -> dict[str, Any]:
    metadata = dict(getattr(document, "metadata", {}) or {})
    return {
        "text": getattr(document, "page_content", ""),
        "source": source_from_document(document),
        "backend": metadata.get("backend", "document"),
        "evidence_lane": metadata.get("evidence_lane", "document"),
        "metadata": {
            key: value for key, value in metadata.items()
            if key not in {"credential", "api_key", "password"}
        },
    }


def initialize_retrieval() -> tuple[Any, Any, Any, Any]:
    from app.services.graph_service import AcademicGraphService
    from app.services.rag_engine import AdvancedChunkingEngine, TemporalCrossEncoderReranker
    from app.services.tuition_catalog import TuitionRateCatalog

    engine = AdvancedChunkingEngine()
    compressor = None
    if engine.cross_encoder is not None:
        compressor = TemporalCrossEncoderReranker(
            model=engine.cross_encoder, top_n=METRIC_K, score_tolerance=0.05,
        )
    catalog = TuitionRateCatalog.load()
    graph = AcademicGraphService(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password"),
    )
    return engine, graph, catalog, compressor


def run_retrieval(
    cases: list[ScenarioCase], checkpoint: dict[str, Any], checkpoint_path: Path,
    logger: logging.Logger,
) -> None:
    engine, graph, catalog, compressor = initialize_retrieval()
    try:
        for index, case in enumerate(cases, start=1):
            if case.case_id in checkpoint["retrieval"]:
                continue
            started = time.perf_counter()
            trace = retrieve_configurations(
                case, engine, graph, catalog, compressor, top_k=TOP_K, metric_k=METRIC_K,
            )
            configs: dict[str, Any] = {}
            for config, documents in trace.configs.items():
                payloads = [document_payload(document) for document in documents]
                sources = [payload["source"] for payload in payloads]
                config_payload: dict[str, Any] = {
                    "contexts": payloads,
                    "latency_ms": trace.latency_ms[config],
                }
                if config in CONFIGS_S1:
                    config_payload["metrics"] = retrieval_metrics(sources, case.gold_sources)
                if config in CONFIGS_S2:
                    config_payload["diagnostics"] = source_metrics(
                        sources, case.gold_sources, top_k=TOP_K,
                        source_relation=case.source_relation,
                    )
                configs[config] = config_payload
            checkpoint["retrieval"][case.case_id] = {
                "configs": configs,
                "graph_hit": trace.graph_hit,
                "catalog_fallback": trace.catalog_fallback,
                "active_lanes": trace.active_lanes,
                "gate_reasons": trace.gate_reasons,
                "wall_latency_ms": (time.perf_counter() - started) * 1000,
            }
            json_dump(checkpoint_path, checkpoint)
            logger.info("retrieval [%d/%d] %s graph=%s fallback=%s", index, len(cases), case.case_id, trace.graph_hit, trace.catalog_fallback)
    finally:
        graph.close()


def create_llm(args: argparse.Namespace, project: str) -> Any:
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=args.model,
        temperature=TEMPERATURE,
        vertexai=True,
        project=project,
        location=args.location,
        retries=args.max_retries,
        request_timeout=args.timeout,
    )


def generate_one(llm: Any, prompt: str, args: argparse.Namespace) -> tuple[str, float, str | None]:
    started = time.perf_counter()
    for attempt in range(args.max_retries + 1):
        try:
            response = llm.invoke(prompt)
            content = response.content
            if isinstance(content, list):
                content = "".join(str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in content)
            return str(content).strip(), (time.perf_counter() - started) * 1000, None
        except Exception as exc:
            if attempt >= args.max_retries:
                return "", (time.perf_counter() - started) * 1000, f"{type(exc).__name__}: {exc}"
            time.sleep(min(30.0, 2.0 ** attempt + random.random()))
    raise AssertionError("unreachable")


def run_generation(
    cases: list[ScenarioCase], checkpoint: dict[str, Any], checkpoint_path: Path,
    llm: Any, args: argparse.Namespace, logger: logging.Logger,
) -> None:
    jobs = []
    for repetition in range(1, args.repetitions + 1):
        for case in cases:
            for config in CONFIGS_S2:
                key = f"r{repetition}:{case.case_id}:{config}"
                if key in checkpoint["answers"]:
                    continue
                contexts = checkpoint["retrieval"][case.case_id]["configs"][config]["contexts"]
                context_text = "\n\n---\n\n".join(item["text"] for item in contexts)
                prompt = GENERATION_PROMPT.format(contexts=context_text or "(không có evidence)", question=case.question)
                jobs.append((key, case, config, repetition, prompt))
    logger.info("generation tasks=%d workers=%d", len(jobs), args.workers)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(generate_one, llm, prompt, args): (key, case, config, repetition)
            for key, case, config, repetition, prompt in jobs
        }
        for index, future in enumerate(as_completed(futures), start=1):
            key, case, config, repetition = futures[future]
            answer, latency, error = future.result()
            checkpoint["answers"][key] = {
                "case_id": case.case_id,
                "config": config,
                "repetition": repetition,
                "answer": answer,
                "latency_ms": latency,
                "error": error,
                "factual_exact_match": factual_exact_match(case, answer),
            }
            json_dump(checkpoint_path, checkpoint)
            if index % 10 == 0 or index == len(jobs):
                logger.info("generation [%d/%d] last=%s/%s/r%d error=%s", index, len(jobs), case.case_id, config, repetition, bool(error))


def run_ragas(
    cases: list[ScenarioCase], checkpoint: dict[str, Any], checkpoint_path: Path,
    llm: Any, args: argparse.Namespace, logger: logging.Logger,
) -> None:
    from datasets import Dataset
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from ragas import evaluate
    from ragas.metrics import answer_correctness, answer_relevancy, context_precision, context_recall
    from ragas.run_config import RunConfig

    case_map = {case.case_id: case for case in cases}
    missing_keys = [key for key in checkpoint["answers"] if key not in checkpoint["ragas"]]
    if not missing_keys:
        logger.info("ragas: no missing records")
        return
    if args.embedding_backend == "local":
        embeddings = HuggingFaceEmbeddings(model_name=args.embedding_model)
    else:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=args.embedding_model,
            vertexai=True,
            project=args.project_resolved,
            location=args.location,
        )
    # The runner already supplies three independent repetitions. Keeping the
    # internal reverse-question strictness at one avoids silently requesting
    # three candidates from a Vertex wrapper that returns one candidate.
    answer_relevancy.strictness = 1
    columns = {
        "answer_relevancy": "AR",
        "context_recall": "CR",
        "context_precision": "CP",
        "answer_correctness": "AC",
    }
    logger.info("ragas records=%d workers=%d shard=%d", len(missing_keys), args.workers, args.ragas_batch_size)
    for offset in range(0, len(missing_keys), args.ragas_batch_size):
        shard_keys = missing_keys[offset:offset + args.ragas_batch_size]
        rows = {"question": [], "answer": [], "contexts": [], "ground_truth": []}
        for key in shard_keys:
            answer_record = checkpoint["answers"][key]
            case = case_map[answer_record["case_id"]]
            contexts = checkpoint["retrieval"][case.case_id]["configs"][answer_record["config"]]["contexts"]
            rows["question"].append(case.question)
            rows["answer"].append(answer_record["answer"])
            rows["contexts"].append([item["text"] for item in contexts])
            rows["ground_truth"].append(case.reference_answer)
        result = evaluate(
            Dataset.from_dict(rows),
            metrics=[answer_relevancy, context_recall, context_precision, answer_correctness],
            llm=llm,
            embeddings=embeddings,
            run_config=RunConfig(
                timeout=args.timeout, max_retries=args.max_retries,
                max_wait=30, max_workers=args.workers, seed=42,
            ),
            raise_exceptions=False,
            show_progress=True,
        )
        frame = result.to_pandas()
        for index, key in enumerate(shard_keys):
            metrics: dict[str, float | None] = {}
            for source_name, target_name in columns.items():
                value = frame.iloc[index].get(source_name)
                metrics[target_name] = None if value is None or value != value else float(value)
            checkpoint["ragas"][key] = metrics
        json_dump(checkpoint_path, checkpoint)
        logger.info("ragas [%d/%d] checkpointed", min(offset + len(shard_keys), len(missing_keys)), len(missing_keys))


def bootstrap_ci(values: list[float], *, samples: int = 10000) -> list[float]:
    if not values:
        return [0.0, 0.0]
    rng = random.Random(42)
    means = sorted(mean([values[rng.randrange(len(values))] for _ in values]) for _ in range(samples))
    return [means[int(0.025 * (samples - 1))], means[int(0.975 * (samples - 1))]]


def aggregate(cases: list[ScenarioCase], checkpoint: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    summary: dict[str, Any] = {"scenario1": {}, "scenario2": {}, "paired_differences": {}}
    if args.scenario in {"1", "all"}:
        for config in CONFIGS_S1:
            rows = [checkpoint["retrieval"][case.case_id]["configs"][config] for case in cases]
            metric_names = ("hit_at_1", "hit_at_3", "precision_at_5", "recall_at_5", "mrr_at_10")
            summary["scenario1"][config] = {
                name: mean([row["metrics"][name] for row in rows]) for name in metric_names
            }
            summary["scenario1"][config]["latency_ms"] = mean([row["latency_ms"] for row in rows])
    if args.scenario in {"2", "all"}:
        for config in CONFIGS_S2:
            config_summary: dict[str, Any] = {}
            keys = [
                f"r{rep}:{case.case_id}:{config}"
                for rep in range(1, args.repetitions + 1) for case in cases
            ]
            for metric in ("AR", "CR", "CP", "AC"):
                values = [checkpoint["ragas"][key][metric] for key in keys if checkpoint["ragas"].get(key, {}).get(metric) is not None]
                config_summary[metric] = {
                    "mean": mean(values), "sd": stddev(values), "ci95": bootstrap_ci(values), "n": len(values),
                }
            diagnostics = [checkpoint["retrieval"][case.case_id]["configs"][config]["diagnostics"] for case in cases]
            config_summary["source_recall"] = mean([row["source_recall"] for row in diagnostics])
            config_summary["source_ap"] = mean([row["source_ap"] for row in diagnostics])
            answer_rows = [checkpoint["answers"][key] for key in keys if key in checkpoint["answers"]]
            config_summary["factual_exact_match"] = mean([row["factual_exact_match"] for row in answer_rows])
            summary["scenario2"][config] = config_summary
        for ablation in ("T5", "T6", "T7"):
            summary["paired_differences"][f"T4-{ablation}"] = {}
            for metric in ("AR", "CR", "CP", "AC"):
                differences = []
                for rep in range(1, args.repetitions + 1):
                    for case in cases:
                        left = checkpoint["ragas"].get(f"r{rep}:{case.case_id}:T4", {}).get(metric)
                        right = checkpoint["ragas"].get(f"r{rep}:{case.case_id}:{ablation}", {}).get(metric)
                        if left is not None and right is not None:
                            differences.append(left - right)
                summary["paired_differences"][f"T4-{ablation}"][metric] = {
                    "mean": mean(differences), "ci95": bootstrap_ci(differences), "n": len(differences),
                }
    return summary


def write_reports(run_dir: Path, cases: list[ScenarioCase], checkpoint: dict[str, Any], summary: dict[str, Any], manifest: dict[str, Any]) -> None:
    records = []
    for case in cases:
        retrieval = checkpoint["retrieval"][case.case_id]
        for config, data in retrieval["configs"].items():
            base = {
                "case_id": case.case_id, "category": case.category, "question": case.question,
                "config": config, "reference_answer": case.reference_answer,
                "gold_sources": case.gold_sources, "source_relation": case.source_relation,
                "contexts": data["contexts"], "retrieval_latency_ms": data["latency_ms"],
                "graph_hit": retrieval["graph_hit"], "catalog_fallback": retrieval["catalog_fallback"],
                "gate_reasons": retrieval["gate_reasons"],
            }
            if config in CONFIGS_S1:
                records.append({**base, "scenario": 1, "metrics": data["metrics"]})
            if config in CONFIGS_S2:
                for repetition in range(1, manifest["repetitions"] + 1):
                    key = f"r{repetition}:{case.case_id}:{config}"
                    records.append({
                        **base, "scenario": 2, "repetition": repetition,
                        **checkpoint["answers"].get(key, {}), "metrics": checkpoint["ragas"].get(key, {}),
                        "diagnostics": data["diagnostics"],
                    })
    (run_dir / "records.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    json_dump(run_dir / "summary.json", summary)
    failures = [row for row in records if row.get("error") or any(value is None for value in row.get("metrics", {}).values())]
    failure_lines = ["# Failures", "", f"Total: {len(failures)}", ""]
    failure_lines.extend(f"- `{row['case_id']}` / `{row['config']}`: {row.get('error') or 'missing metric'}" for row in failures)
    (run_dir / "failures.md").write_text("\n".join(failure_lines) + "\n", encoding="utf-8")
    comparison = ["# Scenario 1–2 comparison", "", f"- Split: `{manifest['split']}`", f"- Cases: {manifest['case_count']}", ""]
    if summary["scenario1"]:
        comparison.extend(["## Scenario 1", "", "| Config | H@1 | H@3 | P@5 | R@5 | MRR@10 | Latency ms |", "|---|---:|---:|---:|---:|---:|---:|"])
        for config, row in summary["scenario1"].items():
            comparison.append(f"| {config} | {row['hit_at_1']:.4f} | {row['hit_at_3']:.4f} | {row['precision_at_5']:.4f} | {row['recall_at_5']:.4f} | {row['mrr_at_10']:.4f} | {row['latency_ms']:.2f} |")
    if summary["scenario2"]:
        comparison.extend(["", "## Scenario 2", "", "| Config | AR | CR | CP | AC | Source recall | Source AP | Fact EM |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
        for config, row in summary["scenario2"].items():
            comparison.append(f"| {config} | {row['AR']['mean']:.4f} ± {row['AR']['sd']:.4f} | {row['CR']['mean']:.4f} ± {row['CR']['sd']:.4f} | {row['CP']['mean']:.4f} ± {row['CP']['sd']:.4f} | {row['AC']['mean']:.4f} ± {row['AC']['sd']:.4f} | {row['source_recall']:.4f} | {row['source_ap']:.4f} | {row['factual_exact_match']:.4f} |")
    (run_dir / "comparison.md").write_text("\n".join(comparison) + "\n", encoding="utf-8")
    artifacts = {}
    for name in ("records.jsonl", "summary.json", "comparison.md", "failures.md", "checkpoint.json", "run.log"):
        path = run_dir / name
        if path.exists():
            artifacts[name] = sha256_file(path)
    manifest["artifact_sha256"] = artifacts
    json_dump(run_dir / "manifest.json", manifest)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("1", "2", "all"), default="all")
    parser.add_argument("--split", choices=("dev", "heldout"), default="dev")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--repetitions", type=int, default=3)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fresh", action="store_true")
    mode.add_argument("--resume", action="store_true")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--embedding-model", default=str(ROOT / "models" / "vietnamese-bi-encoder"))
    parser.add_argument("--embedding-backend", choices=("local", "vertex"), default="local")
    parser.add_argument("--credentials", type=Path, default=SERVICE_ACCOUNT)
    parser.add_argument("--project")
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--ragas-batch-size", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = (args.dataset or (DEV_DATASET if args.split == "dev" else HELDOUT_DATASET)).resolve()
    cases = load_cases(dataset, require_approved=args.split == "heldout")
    if args.limit:
        cases = cases[:args.limit]
    args.project_resolved = configure_vertex(args.credentials, args.project)
    expected = signature(dataset, args)
    run_dir, checkpoint = create_run_dir(expected, args.resume)
    logger = setup_logging(run_dir)
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "split": args.split, "dataset": str(dataset), "case_count": len(cases),
        "scenario": args.scenario, "model": args.model, "embedding_model": args.embedding_model,
        "temperature": TEMPERATURE, "workers": args.workers, "repetitions": args.repetitions,
        "signature": expected,
    }
    json_dump(run_dir / "manifest.json", manifest)
    logger.info("run=%s split=%s cases=%d scenario=%s", run_dir, args.split, len(cases), args.scenario)
    run_retrieval(cases, checkpoint, run_dir / "checkpoint.json", logger)
    if args.scenario in {"2", "all"}:
        llm = create_llm(args, args.project_resolved)
        run_generation(cases, checkpoint, run_dir / "checkpoint.json", llm, args, logger)
        judge_llm = create_llm(args, args.project_resolved)
        run_ragas(cases, checkpoint, run_dir / "checkpoint.json", judge_llm, args, logger)
    summary = aggregate(cases, checkpoint, args)
    write_reports(run_dir, cases, checkpoint, summary, manifest)
    logger.info("complete: %s", run_dir)


if __name__ == "__main__":
    main()
