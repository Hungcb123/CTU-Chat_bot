#!/usr/bin/env bash
set -e
cd /mnt/d/Project/Chatbot
export PYTHONUNBUFFERED=1

echo ">>> Resuming V13 experiment at $(date)..."
wsl_venv/bin/python scripts/run_v13_architecture_experiment.py \
    --scenario both \
    --reps 1 \
    --dataset data/scenario12_heldout_100.jsonl \
    --output-dir logs/v13_architecture/run_20260923_155602 \
    2>&1 | tee -a logs/v13_pipeline_20260923_155430/scenario12.log

echo ">>> Experiment completed! Running Auto-Summary..."
wsl_venv/bin/python scripts/summarize_v13_results.py logs/v13_architecture/run_20260923_155602 --latex 2>&1 | tee logs/v13_pipeline_20260923_155430/summary.log
echo ">>> Auto-Summary completed!"
