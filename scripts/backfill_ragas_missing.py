"""Backfill missing RAGAS cells from the Scenario 1/2 checkpoint.

This script never reruns retrieval or answer generation. It derives work from
missing/non-finite cells, evaluates only those metrics, merges successful cells,
and saves the checkpoint atomically after every batch.
"""

import json
import logging
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path


os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

ROOT = Path("/mnt/d/Project/Chatbot")
sys.path.insert(0, str(ROOT))

CHECKPOINT_PATH = ROOT / "logs/scenario12/20260916T075823Z/checkpoint.json"
DATASET_PATH = ROOT / "data/scenario12_heldout_100.jsonl"
LOG_PATH = ROOT / "logs/scenario12/backfill_ragas_missing.log"
COVERAGE_PATH = ROOT / "logs/scenario12/ragas_coverage.json"

BATCH_SIZE = 6
MAX_WORKERS = 6
MAX_PASSES = 5
RETRY_DELAY_SECONDS = 5
REQUIRED_METRICS = ("AR", "CR", "CP", "AC", "Faith")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_PATH), mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("backfill_ragas_missing")


def is_valid_score(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def missing_signature(values):
    return tuple(metric for metric in REQUIRED_METRICS if not is_valid_score(values.get(metric)))


def save_json_atomic(path, payload):
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, path)


def configure_vertex():
    configured_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    candidates = [
        Path(configured_path) if configured_path else None,
        ROOT / "gen-lang-client-0656432358-9a6fb12696b2.json",
        ROOT.parent / "gen-lang-client-0656432358-9a6fb12696b2.json",
    ]
    service_account_path = next((path for path in candidates if path and path.exists()), None)
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if service_account_path:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(service_account_path.resolve())
        metadata = json.loads(service_account_path.read_text(encoding="utf-8"))
        project = project or metadata.get("project_id")
    if not project:
        raise RuntimeError("Cannot determine GCP project")
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project
    return project


def main():
    from datasets import Dataset
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_google_genai import ChatGoogleGenerativeAI
    from ragas import evaluate
    from ragas.metrics import (
        answer_correctness,
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )
    from ragas.prompt import pydantic_prompt as ragas_pydantic_prompt
    from ragas.run_config import RunConfig

    def sanitize_json_escapes(s: str) -> str:
        return re.sub(r'\\([^"\\/bfnrtu])', r'\1', s)

    orig_extract_json = ragas_pydantic_prompt.extract_json

    def safe_extract_json(text: str) -> str:
        extracted = orig_extract_json(text)
        return sanitize_json_escapes(extracted)

    ragas_pydantic_prompt.extract_json = safe_extract_json

    async def generate_repair_as_raw_json(
        llm, data, temperature=None, stop=None, callbacks=None, retries_left=3
    ):
        """Accept Gemini's corrected target JSON without requiring a text wrapper."""
        prompt_value = ragas_pydantic_prompt.PromptValue(
            text=ragas_pydantic_prompt.fix_output_format_prompt.to_string(data)
        )
        response = await llm.generate(
            prompt_value,
            n=1,
            temperature=temperature,
            stop=stop,
            callbacks=callbacks or [],
        )
        raw_output = response.generations[0][0].text
        try:
            extracted = ragas_pydantic_prompt.extract_json(raw_output)
            try:
                parsed = json.loads(extracted)
            except (TypeError, ValueError):
                parsed = json.loads(sanitize_json_escapes(extracted))

            if isinstance(parsed, dict) and set(parsed) == {"text"}:
                inner = ragas_pydantic_prompt.extract_json(parsed["text"])
                try:
                    parsed = json.loads(inner)
                except (TypeError, ValueError):
                    parsed = json.loads(sanitize_json_escapes(inner))

            raw_output = json.dumps(parsed, ensure_ascii=False)
        except (TypeError, ValueError):
            pass
        return ragas_pydantic_prompt.StringIO(text=raw_output)

    ragas_pydantic_prompt.fix_output_format_prompt.generate = generate_repair_as_raw_json

    project = configure_vertex()
    logger.info("Using VertexAI project: %s", project)

    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as handle:
        checkpoint = json.load(handle)

    case_data = {}
    with open(DATASET_PATH, "r", encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            case_data[item["id"]] = item

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        vertexai=True,
        project=project,
        location="us-central1",
        temperature=0,
        request_timeout=120,
    )
    logger.info("Loading embeddings for metrics that require them")
    embeddings = HuggingFaceEmbeddings(
        model_name=str(ROOT / "models/vietnamese-bi-encoder")
    )
    embeddings.embed_query("warmup")
    logger.info("Embeddings ready")

    answer_relevancy.strictness = 1
    metric_catalog = {
        "AR": (answer_relevancy, "answer_relevancy"),
        "CR": (context_recall, "context_recall"),
        "CP": (context_precision, "context_precision"),
        "AC": (answer_correctness, "answer_correctness"),
        "Faith": (faithfulness, "faithfulness"),
    }

    for pass_number in range(1, MAX_PASSES + 1):
        groups = defaultdict(list)
        for key, values in checkpoint["ragas"].items():
            signature = missing_signature(values)
            if signature:
                groups[signature].append(key)

        remaining_cells = sum(len(signature) * len(keys) for signature, keys in groups.items())
        remaining_keys = sum(len(keys) for keys in groups.values())
        logger.info(
            "Pass %d/%d: remaining keys=%d cells=%d groups=%d",
            pass_number,
            MAX_PASSES,
            remaining_keys,
            remaining_cells,
            len(groups),
        )
        if not groups:
            break

        cells_filled_this_pass = 0
        for signature in sorted(groups, key=lambda item: (len(item), item)):
            keys = sorted(groups[signature])
            selected_metrics = [metric_catalog[name][0] for name in signature]
            logger.info("Metric group %s: %d keys", ",".join(signature), len(keys))

            for offset in range(0, len(keys), BATCH_SIZE):
                batch_keys = keys[offset : offset + BATCH_SIZE]
                rows = {"question": [], "answer": [], "contexts": [], "ground_truth": []}
                for key in batch_keys:
                    _, case_id, config = key.split(":")
                    case = case_data[case_id]
                    contexts = checkpoint["retrieval"][case_id]["configs"][config]["contexts"]
                    rows["question"].append(case["question"])
                    rows["answer"].append(checkpoint["answers"][key]["answer"])
                    rows["contexts"].append([item["text"] for item in contexts])
                    rows["ground_truth"].append(case["reference_answer"])

                logger.info(
                    "Evaluating %s batch %d-%d/%d with %d workers",
                    ",".join(signature),
                    offset,
                    offset + len(batch_keys),
                    len(keys),
                    MAX_WORKERS,
                )
                try:
                    result = evaluate(
                        Dataset.from_dict(rows),
                        metrics=selected_metrics,
                        llm=llm,
                        embeddings=embeddings,
                        run_config=RunConfig(
                            timeout=180,
                            max_retries=2,
                            max_wait=30,
                            max_workers=MAX_WORKERS,
                            seed=42,
                        ),
                        raise_exceptions=False,
                        show_progress=True,
                    )
                    frame = result.to_pandas()
                except Exception as exc:
                    logger.error("Batch failed: %s", exc)
                else:
                    for index, key in enumerate(batch_keys):
                        for metric_name in signature:
                            column_name = metric_catalog[metric_name][1]
                            value = frame.iloc[index].get(column_name)
                            if is_valid_score(value):
                                checkpoint["ragas"][key][metric_name] = float(value)
                                cells_filled_this_pass += 1
                            else:
                                logger.warning("Still missing %s for %s", metric_name, key)

                save_json_atomic(CHECKPOINT_PATH, checkpoint)
                logger.info("Checkpoint saved; filled cells this pass=%d", cells_filled_this_pass)

        if cells_filled_this_pass == 0 and pass_number < MAX_PASSES:
            logger.warning("No progress this pass; retrying after %ds", RETRY_DELAY_SECONDS)
            time.sleep(RETRY_DELAY_SECONDS)

    missing_by_metric = {metric: [] for metric in REQUIRED_METRICS}
    invalid_by_metric = {metric: [] for metric in REQUIRED_METRICS}
    for key, values in checkpoint["ragas"].items():
        for metric in REQUIRED_METRICS:
            value = values.get(metric)
            if value is None:
                missing_by_metric[metric].append(key)
            elif not is_valid_score(value):
                invalid_by_metric[metric].append(key)

    coverage = {
        "checkpoint": str(CHECKPOINT_PATH),
        "total_keys": len(checkpoint["ragas"]),
        "required_metrics": list(REQUIRED_METRICS),
        "missing_by_metric": missing_by_metric,
        "invalid_by_metric": invalid_by_metric,
        "complete": not any(missing_by_metric.values()) and not any(invalid_by_metric.values()),
    }
    save_json_atomic(COVERAGE_PATH, coverage)
    logger.info(
        "Coverage complete=%s missing=%s invalid=%s",
        coverage["complete"],
        {name: len(keys) for name, keys in missing_by_metric.items()},
        {name: len(keys) for name, keys in invalid_by_metric.items()},
    )
    if not coverage["complete"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
