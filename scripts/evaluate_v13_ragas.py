#!/usr/bin/env python3
"""V13 Ragas Evaluator — Compute AC, Faith, CR, CP metrics via Ragas.

Reads results.jsonl from a V13 experiment run, evaluates each response
with Ragas metrics, and writes enriched results back.

Usage:
  python scripts/evaluate_v13_ragas.py logs/v13_architecture/run_YYYYMMDD_HHMMSS/
  python scripts/evaluate_v13_ragas.py logs/v13_architecture/run_YYYYMMDD_HHMMSS/ --batch-size 10
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

SERVICE_ACCOUNT = ROOT / "gen-lang-client-0656432358-9a6fb12696b2.json"


def configure_vertex(credentials: Path, project: str | None) -> str:
    if credentials.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials.resolve())
        metadata = json.loads(credentials.read_text(encoding="utf-8"))
        project = project or metadata.get("project_id")
    if not project:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise RuntimeError("Cannot determine Google Cloud project")
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project
    return project


def load_results(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def evaluate_batch(records: list[dict[str, Any]], batch_size: int = 10) -> list[dict[str, Any]]:
    """Evaluate records with Ragas metrics in batches."""
    import ragas
    from ragas import evaluate
    from ragas.metrics import (
        answer_correctness,
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )
    from datasets import Dataset

    metrics = [
        answer_correctness,
        answer_relevancy,
        faithfulness,
        context_recall,
        context_precision,
    ]

    enriched = []
    total = len(records)

    for i in range(0, total, batch_size):
        batch = records[i : i + batch_size]
        print(f"  Evaluating batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}...")

        # Build Ragas dataset
        data = {
            "question": [],
            "answer": [],
            "contexts": [],
            "ground_truth": [],
        }

        for record in batch:
            if "error" in record:
                enriched.append(record)
                continue

            data["question"].append(record.get("question", ""))
            data["answer"].append(record.get("response", ""))

            # Contexts from retrieved sources (use response text if no contexts available)
            contexts = record.get("retrieved_contexts", [])
            if not contexts:
                contexts = [record.get("response", "")]
            data["contexts"].append(contexts)

            data["ground_truth"].append(record.get("reference_answer", ""))

        if not data["question"]:
            continue

        try:
            dataset = Dataset.from_dict(data)
            result = evaluate(dataset, metrics=metrics)
            result_df = result.to_pandas()

            valid_idx = 0
            for record in batch:
                if "error" in record:
                    continue

                row = result_df.iloc[valid_idx]
                record["ragas_answer_correctness"] = float(row.get("answer_correctness", 0.0))
                record["ragas_answer_relevancy"] = float(row.get("answer_relevancy", 0.0))
                record["ragas_faithfulness"] = float(row.get("faithfulness", 0.0))
                record["ragas_context_recall"] = float(row.get("context_recall", 0.0))
                record["ragas_context_precision"] = float(row.get("context_precision", 0.0))
                enriched.append(record)
                valid_idx += 1

        except Exception as exc:
            print(f"  WARNING: Ragas evaluation failed for batch: {exc}")
            for record in batch:
                record["ragas_error"] = str(exc)
                enriched.append(record)

        # Rate limiting
        time.sleep(1.0)

    return enriched


def main():
    parser = argparse.ArgumentParser(description="V13 Ragas Evaluator")
    parser.add_argument("run_dir", type=str, help="Path to experiment run directory")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for Ragas evaluation")
    parser.add_argument("--project", type=str, default=None, help="Google Cloud project ID")
    parser.add_argument("--output", type=str, default=None, help="Output file (default: results_ragas.jsonl)")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    results_path = run_dir / "results.jsonl"

    if not results_path.exists():
        print(f"ERROR: {results_path} not found")
        sys.exit(1)

    project = configure_vertex(SERVICE_ACCOUNT, args.project)
    print(f"Using Vertex AI project: {project}")

    records = load_results(results_path)
    print(f"Loaded {len(records)} records")

    # Filter out error records for evaluation
    valid = [r for r in records if "error" not in r]
    errors = [r for r in records if "error" in r]
    print(f"Valid for evaluation: {len(valid)}, errors: {len(errors)}")

    enriched = evaluate_batch(valid, batch_size=args.batch_size)
    enriched.extend(errors)

    output_path = Path(args.output) if args.output else (run_dir / "results_ragas.jsonl")
    with output_path.open("w", encoding="utf-8") as f:
        for record in enriched:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Enriched results written to: {output_path}")

    # Quick summary
    ragas_records = [r for r in enriched if "ragas_answer_correctness" in r]
    if ragas_records:
        from collections import defaultdict
        import numpy as np

        by_config = defaultdict(list)
        for r in ragas_records:
            by_config[r["configuration"]].append(r)

        print("\nRagas Summary:")
        print(f"{'Config':<25} {'AC':>7} {'AR':>7} {'Faith':>7} {'CR':>7} {'CP':>7}")
        print("-" * 65)
        for config in sorted(by_config.keys()):
            recs = by_config[config]
            ac = np.mean([r["ragas_answer_correctness"] for r in recs])
            ar = np.mean([r["ragas_answer_relevancy"] for r in recs])
            faith = np.mean([r["ragas_faithfulness"] for r in recs])
            cr = np.mean([r["ragas_context_recall"] for r in recs])
            cp = np.mean([r["ragas_context_precision"] for r in recs])
            print(f"{config:<25} {ac:>7.3f} {ar:>7.3f} {faith:>7.3f} {cr:>7.3f} {cp:>7.3f}")


if __name__ == "__main__":
    main()
