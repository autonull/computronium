#!/usr/bin/env bash
# run_autonomous.sh — Autonomous experiment loop entry point.
#
# Discovers new high-performing configs via explore/exploit cycles.
# No seeds — pure discovery. Resumable from experiments/autonomous/state.json.
#
# Live artifacts (experiments/autonomous/):
#   report.md      human-readable summary (best, top cells, history, defects)
#   ledger.jsonl   per-cycle structured record
#   defects.jsonl  defect signatures + suggested fixes
#
# Usage:
#   ./run_autonomous.sh                 # 8h on cuda
#   HOURS=24 DEVICE=cuda ./run_autonomous.sh
#   CYCLES=4 ./run_autonomous.sh        # 4 cycles
#
# Recommended (bare metal):
#   nohup ./run_autonomous.sh > logs/autonomous_main.log 2>&1 &
set -euo pipefail

cd "$(dirname "$0")"

HOURS="${HOURS:-8}"
DEVICE="${DEVICE:-cuda}"
CYCLES="${CYCLES:-0}"

echo "=== autonomous experiments: ${HOURS}h on ${DEVICE} (cycles=${CYCLES}) ==="

exec uv run python scripts/run_autonomous.py \
  --hours "${HOURS}" \
  --device "${DEVICE}" \
  --cycles "${CYCLES}"