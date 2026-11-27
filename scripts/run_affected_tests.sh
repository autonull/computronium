#!/usr/bin/env bash
# The affected tier: the test files a working-tree change reaches, bounded by
# the fast suite's own prices. A file the change reaches but the fast suite
# does not run is a long learnability/capability test, so it is named and left
# to the fast or release tier instead of making this one slow.
#
# Pass `--rev <rev>` to select a commit's change instead of the working tree.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

# shellcheck source=scripts/_gpu_idle.sh
source "$SCRIPT_DIR/_gpu_idle.sh"
warn_foreign_gpu_allocations

export UV_LINK_MODE=copy
export TORCHINDUCTOR_CACHE_DIR="${TORCHINDUCTOR_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/computronium/torchinductor}"
mkdir -p "$TORCHINDUCTOR_CACHE_DIR"

tmp="${TMPDIR:-/tmp}/computronium-affected"
mkdir -p "$tmp"

selected=()
heavy=0
while IFS= read -r path; do
    [ -z "$path" ] && continue
    case "$path" in
        tests/acceptance/* | */test_demo_*.py)
            heavy=$((heavy + 1))
            ;;
        *)
            selected+=("$path")
            ;;
    esac
done <<< "$(uv run python scripts/select_affected_tests.py "$@")"

printf '%s\n' "${selected[@]}" | sort -u > "$tmp/affected"
sort -u configs/fast_suite.txt > "$tmp/fast"
comm -12 "$tmp/affected" "$tmp/fast" > "$tmp/run"

count=$(wc -l < "$tmp/run")
priced=$(( ${#selected[@]} - count ))
printf 'affected: %d priced files, %d outside the fast suite, %d release-only\n' \
    "$count" "$priced" "$heavy"

if [ "$count" -eq 0 ]; then
    printf 'affected: nothing priced to run; take the fast suite\n'
    exit 0
fi

# Two workers, not four: the device is one 9.66 GiB GPU and the memory-binding
# property tests allocate large batches, so four workers overflowed it and nine
# tests failed with CUDA OOM (measured). Two keep them inside the device.
# shellcheck disable=SC2046  # one path per line, no spaces
uv run python -m pytest $(cat "$tmp/run") -q -rf --tb=line -n 2
