"""
Re-evaluate RAGAS scores for 29 Cat-C cases whose reference_answer was rewritten.
Reuses existing retrieval + generation from checkpoint.json.
The initial pass evaluated all five metrics. Resumed backfill runs evaluate only
Faithfulness for records that failed its output parser, preserving the other
four completed scores.
Saves checkpoint incrementally after each batch and supports resuming.
"""
import json, logging, os, sys, time
from pathlib import Path

os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

ROOT = Path("/mnt/d/Project/Chatbot")
sys.path.insert(0, str(ROOT))

LOG_PATH = ROOT / "logs/scenario12/reeval_cat_c.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_PATH), mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("reevaluate_ragas")

CP_PATH = ROOT / "logs/scenario12/20260916T075823Z/checkpoint.json"
DATASET_PATH = ROOT / "data/scenario12_heldout_100.jsonl"
SA_PATH = Path("/mnt/d/Project/gen-lang-client-0656432358-9a6fb12696b2.json")
PROGRESS_PATH = ROOT / "logs/scenario12/reeval_cat_c_progress.json"

CAT_C = [
    "HOUT-COMP-03", "HOUT-COMP-05", "HOUT-DIR-ACAD-01", "HOUT-DIR-ACAD-03",
    "HOUT-DIR-ACAD-05", "HOUT-DIR-ACAD-06", "HOUT-DIR-ACAD-07", "HOUT-DIR-ACAD-08",
    "HOUT-DIR-ACAD-09", "HOUT-DIR-ACAD-10", "HOUT-DIR-FIN-07", "HOUT-DIR-FIN-08",
    "HOUT-DIR-GEN-02", "HOUT-DIR-GEN-06", "HOUT-DIR-GEN-10", "HOUT-DIR-SCH-01",
    "HOUT-DIR-SCH-02", "HOUT-DIR-SCH-04", "HOUT-DIR-SCH-05", "HOUT-DIR-SCH-08",
    "HOUT-DIR-SCH-10", "HOUT-MHOP-FIN-04", "HOUT-MHOP-GEN-03", "HOUT-MHOP-SCH-04",
    "HOUT-TEMP-05", "HOUT-XDOM-07", "HOUT-XDOM-08", "HOUT-XDOM-10", "HOUT-XDOM-16",
]

BATCH_SIZE = 2
MAX_WORKERS = 1
MAX_SHARD_ATTEMPTS = 5
RETRY_DELAY_SECONDS = 5

def configure_vertex():
    """Setup VertexAI credentials."""
    if SA_PATH.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(SA_PATH.resolve())
        metadata = json.loads(SA_PATH.read_text(encoding="utf-8"))
        project = metadata.get("project_id")
    else:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise RuntimeError("Cannot determine GCP project")
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project
    return project

def main():
    from datasets import Dataset
    from langchain_google_genai import ChatGoogleGenerativeAI
    from ragas import evaluate
    from ragas.metrics import faithfulness
    from ragas.prompt import pydantic_prompt as ragas_pydantic_prompt
    from ragas.run_config import RunConfig

    async def generate_repair_as_raw_json(
        llm, data, temperature=None, stop=None, callbacks=None, retries_left=3
    ):
        """Accept Gemini's corrected JSON directly during RAGAS parse repair."""
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
            parsed = json.loads(ragas_pydantic_prompt.extract_json(raw_output))
            if isinstance(parsed, dict) and set(parsed) == {"text"}:
                raw_output = parsed["text"]
                parsed = json.loads(ragas_pydantic_prompt.extract_json(raw_output))
            raw_output = json.dumps(parsed, ensure_ascii=False)
        except (TypeError, ValueError):
            pass
        return ragas_pydantic_prompt.StringIO(text=raw_output)

    # RAGAS's repair prompt asks Gemini to wrap corrected JSON in {"text": ...}.
    # Gemini commonly returns the corrected target object directly, which is valid
    # but the stock repair parser rejects it before the target parser sees it.
    ragas_pydantic_prompt.fix_output_format_prompt.generate = generate_repair_as_raw_json

    project = configure_vertex()
    logger.info("Using VertexAI project: %s", project)

    # Load checkpoint
    logger.info("Loading checkpoint from %s...", CP_PATH)
    with open(CP_PATH, 'r', encoding='utf-8') as f:
        cp = json.load(f)

    # Load updated dataset
    case_data = {}
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            case_data[item['id']] = item

    # Find all RAGAS keys for Cat-C cases
    keys_to_reevaluate = []
    for key in cp['ragas']:
        parts = key.split(':')
        case_id = parts[1]
        if case_id in CAT_C:
            keys_to_reevaluate.append(key)

    # Sort for deterministic order
    keys_to_reevaluate.sort()
    logger.info("Total Cat-C keys to re-evaluate: %d", len(keys_to_reevaluate))

    # Check progress file if resuming
    completed_keys = set()
    if PROGRESS_PATH.exists():
        try:
            with open(PROGRESS_PATH, 'r', encoding='utf-8') as f:
                completed_keys = set(json.load(f).get("completed_keys", []))
            logger.info("Found progress file: %d keys already completed.", len(completed_keys))
        except Exception as e:
            logger.warning("Could not load progress file: %s", e)

    remaining_keys = [k for k in keys_to_reevaluate if k not in completed_keys]
    logger.info("Remaining keys to evaluate: %d / %d", len(remaining_keys), len(keys_to_reevaluate))

    if not remaining_keys:
        logger.info("All Cat-C keys already completed!")
        return

    # Setup LLM. Faithfulness does not use embeddings.
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        vertexai=True,
        project=project,
        location="us-central1",
        temperature=0,
        request_timeout=120,
    )
    columns = {
        "faithfulness": "Faith",
    }
    required_metrics = ("AR", "CR", "CP", "AC", "Faith")

    total_done = len(completed_keys)
    start_time = time.time()

    for offset in range(0, len(remaining_keys), BATCH_SIZE):
        shard_keys = remaining_keys[offset:offset + BATCH_SIZE]
        logger.info(
            "Evaluating shard %d-%d / %d (Total done: %d / %d) ...",
            offset, offset + len(shard_keys), len(remaining_keys),
            total_done, len(keys_to_reevaluate)
        )

        shard_start = time.time()
        shard_pending = list(shard_keys)
        for attempt in range(1, MAX_SHARD_ATTEMPTS + 1):
            rows = {"question": [], "answer": [], "contexts": [], "ground_truth": []}
            for key in shard_pending:
                parts = key.split(':')
                case_id = parts[1]
                config = parts[2]
                answer_record = cp['answers'][key]
                case = case_data[case_id]
                contexts = cp['retrieval'][case_id]['configs'][config]['contexts']
                rows["question"].append(case['question'])
                rows["answer"].append(answer_record['answer'])
                rows["contexts"].append([item["text"] for item in contexts])
                rows["ground_truth"].append(case['reference_answer'])

            logger.info(
                "Shard attempt %d/%d: records=%d workers=%d metrics=%s",
                attempt, MAX_SHARD_ATTEMPTS, len(shard_pending), MAX_WORKERS,
                ",".join(columns.values()),
            )
            try:
                result = evaluate(
                    Dataset.from_dict(rows),
                    metrics=[faithfulness],
                    llm=llm,
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
                logger.error("Shard attempt %d failed: %s", attempt, exc)
            else:
                retry_keys = []
                for index, key in enumerate(shard_pending):
                    new_metrics = {}
                    missing_metrics = []
                    for source_name, target_name in columns.items():
                        value = frame.iloc[index].get(source_name)
                        if value is None or value != value:
                            missing_metrics.append(target_name)
                        else:
                            new_metrics[target_name] = float(value)
                    if missing_metrics:
                        logger.warning(
                            "Not checkpointing %s; missing metrics: %s",
                            key, ",".join(missing_metrics),
                        )
                        retry_keys.append(key)
                        continue
                    metrics = dict(cp['ragas'].get(key, {}))
                    metrics.update(new_metrics)
                    missing_after_merge = [
                        name for name in required_metrics
                        if metrics.get(name) is None or metrics.get(name) != metrics.get(name)
                    ]
                    if missing_after_merge:
                        logger.warning(
                            "Not checkpointing %s; still missing after merge: %s",
                            key, ",".join(missing_after_merge),
                        )
                        retry_keys.append(key)
                        continue
                    cp['ragas'][key] = metrics
                    completed_keys.add(key)
                shard_pending = retry_keys
                if not shard_pending:
                    break

            if attempt < MAX_SHARD_ATTEMPTS:
                logger.warning(
                    "Retrying %d incomplete records in %ds",
                    len(shard_pending), RETRY_DELAY_SECONDS,
                )
                time.sleep(RETRY_DELAY_SECONDS)

        total_done = len(completed_keys)
        shard_duration = time.time() - shard_start
        logger.info(
            "Shard done in %.2fs. Total progress: %d/%d (%.1f%%); incomplete=%d",
            shard_duration, total_done, len(keys_to_reevaluate),
            (total_done / len(keys_to_reevaluate)) * 100, len(shard_pending),
        )

        # Save checkpoint after each shard
        with open(CP_PATH, 'w', encoding='utf-8') as f:
            json.dump(cp, f, ensure_ascii=False)

        # Save progress
        with open(PROGRESS_PATH, 'w', encoding='utf-8') as f:
            json.dump({"completed_keys": list(completed_keys)}, f)

        logger.info("Checkpoint & progress saved.")

    logger.info("=== RE-EVALUATION COMPLETE ===")
    logger.info("Total completed: %d / %d", total_done, len(keys_to_reevaluate))
    incomplete_count = len(keys_to_reevaluate) - len(completed_keys)
    if incomplete_count:
        logger.error(
            "Re-evaluation incomplete: %d records remain. Resume the script to retry them.",
            incomplete_count,
        )

    # Final summary for T4
    t4_metrics = {"AR": [], "CR": [], "CP": [], "AC": [], "Faith": []}
    for key, vals in cp['ragas'].items():
        if key.split(':')[2] == 'T4':
            for m in t4_metrics:
                v = vals.get(m)
                if v is not None:
                    t4_metrics[m].append(v)

    print("\n=== UPDATED T4 Metrics ===")
    for m, vals in t4_metrics.items():
        print(f"  {m}: {sum(vals)/len(vals):.4f} (N={len(vals)})")

if __name__ == "__main__":
    main()
