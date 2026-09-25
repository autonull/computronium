#!/bin/bash
# Per-tier suite runner: one process per tier so a crashing tier cannot take
# the rest down, xdist to bound memory (the monolith was OOM-killed), and
# --durations to surface the slowest tests for cost reduction.
cd /home/me/computronium || exit 1
mkdir -p logs/tiers
TIERS="unit primitives algorithms graph ceec platform property integration"
for tier in $TIERS; do
  start=$SECONDS
  echo "=== TIER $tier (start $start) ==="
  uv run python -m pytest "tests/$tier" -q -n 4 -p no:cacheprovider \
      --durations=20 > "logs/tiers/$tier.log" 2>&1
  code=$?
  echo "=== TIER $tier exit=$code walltime=$((SECONDS - start))s ==="
  tail -3 "logs/tiers/$tier.log" | grep -E "passed|failed|error" || true
done
echo "=== ALL TIERS DONE ==="
