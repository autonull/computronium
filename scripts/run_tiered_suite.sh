#!/bin/bash
# Per-tier suite runner: one process per tier so a crashing tier cannot take
# the rest down, xdist to bound memory (the monolith was OOM-killed), and
# --durations to surface the slowest tests for cost reduction.
#
# addopts deselects `-m slow`, so the tiers below are the fast profile
# and the demo suite (test_demo_ntm_local 231s, test_demo_update_ladder 183s,
# measured 2026-09-25) is invisible here. The SLOW pass is what keeps that
# from being a silent skip: the gallery run records and manifest pin are
# verified by tests that live behind the marker. Run it before a round closes;
# skip it for an inner-loop gate.
cd "$(dirname "$(readlink -f "$0")")/.." || exit 1
mkdir -p logs/tiers
# Derived, not hand-listed: a hand list is a silent skip the day a test
# directory is added (TODO35 §1.1 — `acceleration` was missing for a whole
# pass, which meant the entire Triton/FA kernel suite never ran at round close).
# tests/slow is excluded because it is the marker pass below, not a tier.
TIERS=$(find tests -mindepth 1 -maxdepth 1 -type d -not -name 'slow' \
          -not -name '__pycache__' -printf '%f\n' | sort)
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

  # Re-verify the locks that the slow pass invalidates. The gallery lock lives
  # in the integration tier, which runs BEFORE slow — so the pass that
  # re-emits seven of the records it compares against has already happened by
  # the time this runs, and the tier-order result was taken against
  # pre-slow-pass records (TODO35 §11.6-1; this staleness went unnoticed for
  # a round and was §11.2's finding). Provenance is the same shape for the
  # same reason: re-emitted records must be re-read against the environment.
  start=$SECONDS
  echo "=== POST-SLOW RE-PIN VERIFY (start $start) ==="
  uv run python -m pytest tests/integration/test_gallery_lock.py \
      tests/property/test_gallery_provenance_lock.py \
      tests/property/test_claim_ownership_lock.py \
      tests/property/test_determinism_thread_lock.py \
      -q -p no:cacheprovider > "logs/tiers/post_slow_verify.log" 2>&1
  code=$?
  echo "=== POST-SLOW RE-PIN VERIFY exit=$code walltime=$((SECONDS - start))s ==="
  tail -3 "logs/tiers/post_slow_verify.log" | grep -E "passed|failed|error" || true
  if [ "$code" -ne 0 ]; then
    echo "=== A record moved under a stale pin: re-pin docs/figures/manifest.json"
    echo "=== and commit it; this failure is the order bug's own detector."
  fi
fi

echo "=== ALL TIERS DONE ==="
