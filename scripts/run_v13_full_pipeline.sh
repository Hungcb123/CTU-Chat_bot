#!/usr/bin/env bash
# ============================================================
# V13 Full Experiment Pipeline
# ============================================================
# Runs all three experimental scenarios for Paper V13_new:
#   Scenario 1: Architecture-level comparison (S1-A, S1-B, S1-C)
#   Scenario 2: Architectural ablation (S2-A2..A5, reusing S1-B=S2-A1, S1-C=S2-A0)
#   Scenario 3: Tool ambiguity stress test (via existing v6 script)
#
# Usage:
#   bash scripts/run_v13_full_pipeline.sh              # Full run (3 reps)
#   bash scripts/run_v13_full_pipeline.sh --reps 1     # Quick single-rep run
#   bash scripts/run_v13_full_pipeline.sh --scenario s1 # Only Scenario 1
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Activate virtualenv
if [ -d "wsl_venv" ]; then
    source wsl_venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

REPS="${REPS:-3}"
SCENARIO="${SCENARIO:-all}"

# Parse CLI args
while [[ $# -gt 0 ]]; do
    case $1 in
        --reps) REPS="$2"; shift 2 ;;
        --scenario) SCENARIO="$2"; shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
LOG_DIR="logs/v13_pipeline_${TIMESTAMP}"
mkdir -p "$LOG_DIR"

echo "============================================================"
echo "V13 Full Experiment Pipeline"
echo "  Scenario: $SCENARIO"
echo "  Repetitions: $REPS"
echo "  Output: $LOG_DIR"
echo "  Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================================"

# ── Scenario 1 & 2: Architecture comparison and ablation ──
if [[ "$SCENARIO" == "all" || "$SCENARIO" == "s1" || "$SCENARIO" == "s2" || "$SCENARIO" == "both" ]]; then
    echo ""
    echo ">>> Scenario 1 & 2: Architecture & Ablation"
    echo "    Configs: S1-A, S1-B, S1-C + S2-A2, S2-A3, S2-A4, S2-A5"
    echo "    (S1-B = S2-A1, S1-C = S2-A0 — shared runs)"
    echo ""

    python scripts/run_v13_architecture_experiment.py \
        --scenario both \
        --reps "$REPS" \
        --dataset data/scenario12_heldout_100.jsonl \
        2>&1 | tee "$LOG_DIR/scenario12.log"

    echo ">>> Scenario 1 & 2 complete."
fi

# ── Scenario 3: Tool ambiguity stress test ──
if [[ "$SCENARIO" == "all" || "$SCENARIO" == "s3" ]]; then
    echo ""
    echo ">>> Scenario 3: Tool Ambiguity Stress Test"
    echo "    Configs: single_full, single_topk, routed_generic, routed_specialist"
    echo "    Levels: 0 (11 tools), 2 (31 tools), 4 (51 tools)"
    echo ""

    python scripts/run_multi_vs_single_agent_v6_ambiguity.py \
        2>&1 | tee "$LOG_DIR/scenario3.log"

    echo ">>> Scenario 3 complete."
fi

# ── Summary ──
LATEST_RUN=$(ls -td logs/v13_architecture/run_* 2>/dev/null | head -1)
if [ -n "$LATEST_RUN" ]; then
    echo ""
    echo ">>> Auto-summarizing latest run: $LATEST_RUN"
    python scripts/summarize_v13_results.py "$LATEST_RUN" --latex 2>&1 | tee "$LOG_DIR/summary.log"
fi

echo ""
echo "============================================================"
echo "V13 Pipeline Complete"
echo "  Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "  Logs: $LOG_DIR/"
echo ""
echo "Next steps:"
echo "  1. Run Ragas evaluation:"
echo "     python scripts/evaluate_v13_ragas.py $LATEST_RUN"
echo "  2. Fill paper tables with results from $LOG_DIR/summary.log"
echo "============================================================"
