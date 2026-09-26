#!/bin/bash
# Per-tier suite runner: one process per tier so a crashing tier cannot take
# the rest down, xdist to bound memory (the monolith was OOM-killed), and
# --durations to surface the slowest tests for cost reduction.
#
# addopts deselects `-m slow`, so the eight tiers below are the fast profile
# and the demo suite (test_demo_ntm_local 231s, test_demo_update_ladder 183s,
# measured 2026-09-25) is invisible here. The SLOW pass is what keeps that
# from being a silent skip: the gallery run records and manifest pin are
# verified by tests that live behind the marker. Run it before a round closes;
# skip it for an inner-loop gate.
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

if [ "$1" = "--with-slow" ]; then
  start=$SECONDS
  echo "=== TIER slow (start $start) ==="
  uv run python -m pytest tests -q -n 4 -p no:cacheprovider -m slow \
      --durations=20 > "logs/tiers/slow.log" 2>&1
  code=$?
  echo "=== TIER slow exit=$code walltime=$((SECONDS - start))s ==="
  tail -3 "logs/tiers/slow.log" | grep -E "passed|failed|error" || true
fi

echo "=== ALL TIERS DONE ==="
