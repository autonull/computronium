#!/usr/bin/env bash
# run_continuous.sh — ONE entry point for continuous experiments.
#
# Runs the self-driving controller: propose → run → analyze → narrow → repeat,
# until the budget is exhausted or the process is killed. Resumable: re-run to
# continue from experiments/continuous/state.json.
#
# Live artifacts (experiments/continuous/):
#   report.md      human-readable summary (best, top cells, history, defects)
#   ledger.jsonl   per-cycle structured record
#   defects.jsonl  defect signatures + suggested fixes
#
# Usage:
#   ./run_continuous.sh                 # 8h on cuda
#   HOURS=24 DEVICE=cuda ./run_continuous.sh
#   CYCLES=3 ./run_continuous.sh        # smoke test
#
# Recommended (bare metal, survives the shell):
#   nohup ./run_continuous.sh > logs/continuous_main.log 2>&1 &
set -euo pipefail

cd "$(dirname "$0")"

HOURS="${HOURS:-8}"
DEVICE="${DEVICE:-cuda}"
CYCLES="${CYCLES:-0}"

echo "=== continuous experiments: ${HOURS}h on ${DEVICE} (cycles=${CYCLES}) ==="

exec uv run python scripts/continuous_experiment.py \
  --hours "${HOURS}" \
  --device "${DEVICE}" \
  --cycles "${CYCLES}"
