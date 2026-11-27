#!/usr/bin/env bash
# The fast suite: the test files that buy the most line coverage per second
# (measured 2026-11-27, TODO108 W60). It is the iteration gate, not the
# release: primitives, the demo artifacts and the serial acceptance steps stay
# in scripts/run_local_gates.sh.
#
# The list in configs/fast_suite.txt is a measurement, not a rule. A renamed or
# deleted file is dropped with a warning (regenerate with
# scripts/probes/probe_fast_suite.py) instead of failing the gate on a move.
#
# Pass `--cov=computronium --cov-report=term` to measure this suite alone.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

# shellcheck source=scripts/_gpu_idle.sh
source "$SCRIPT_DIR/_gpu_idle.sh"
warn_foreign_gpu_allocations

export UV_LINK_MODE=copy
export TORCHINDUCTOR_CACHE_DIR="${TORCHINDUCTOR_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/computronium/torchinductor}"
mkdir -p "$TORCHINDUCTOR_CACHE_DIR"

run() {
    printf '\n=== %s ===\n' "$*"
    "$@"
}

files=()
while IFS= read -r path; do
    [ -z "$path" ] && continue
    if [ -f "$path" ]; then
        files+=("$path")
    else
        printf 'fast suite: %s is gone; regenerate configs/fast_suite.txt\n' "$path" >&2
    fi
done < configs/fast_suite.txt
if [ "${#files[@]}" -eq 0 ]; then
    printf 'fast suite: configs/fast_suite.txt names no existing test file\n' >&2
    exit 1
fi

run uv run python -m pytest "${files[@]}" -q -rf --tb=line "$@"
