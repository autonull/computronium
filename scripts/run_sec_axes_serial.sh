#!/usr/bin/env bash
# Serial per-axis SEC competitive driver.
#
# One process per axis: fresh torch.compile state and one GPU training at a
# time (semaphore=1). Concurrency inside one process thrashes dynamo and
# times out rungs on the single GPU, so axes are run strictly sequentially.
#
# Usage: scripts/run_sec_axes_serial.sh [axis ...]
#   default axes: credit dynamics geometry update plasticity substrate
set -u

cd "$(dirname "$0")/.." || exit 1

AXES=("$@")
if [ ${#AXES[@]} -eq 0 ]; then
  AXES=(credit dynamics geometry update plasticity substrate)
fi

OUT_ROOT="results/sec/serial"
mkdir -p "$OUT_ROOT"
STAMP=$(date +%Y%m%d_%H%M%S)
LOG_ROOT="logs/serial_$STAMP"
mkdir -p "$LOG_ROOT"

for axis in "${AXES[@]}"; do
  echo "=== [$(date +%H:%M:%S)] axis $axis ==="
  SEC_AXES="$axis" \
  SEC_SEMAPHORE=1 \
  SEC_RUNG_TIMEOUT=180 \
  SEC_RESULTS_DIR="$OUT_ROOT/$axis" \
  PYTHONUNBUFFERED=1 \
    uv run python scripts/run_full_sec_competitive.py \
      > "$LOG_ROOT/$axis.log" 2>&1
  echo "=== [$(date +%H:%M:%S)] axis $axis done (exit $?) ==="
done

echo "ALL AXES DONE -> $OUT_ROOT  (logs: $LOG_ROOT)"
