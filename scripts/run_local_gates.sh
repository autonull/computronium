#!/usr/bin/env bash
# The local release gate. GitHub Actions is disabled (TODO107 D1); this
# sequence is the release. One pass, fail fast: static ratchets, then the
# property shard, then the cheaper suites.
set -euo pipefail

cd "$(dirname "$0")/.."

export UV_LINK_MODE=copy
# The compile cache outlives a run, so it lives outside the tree: inside it,
# `ruff check .` lints the cache and the lint ratchet counts it (W36).
export TORCHINDUCTOR_CACHE_DIR="${TORCHINDUCTOR_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/computronium/torchinductor}"
mkdir -p "$TORCHINDUCTOR_CACHE_DIR"

run() {
    printf '\n=== %s ===\n' "$*"
    "$@"
}

run uv run ruff format --check .
run uv run python scripts/check_pyright_ratchet.py
run uv run python -m pytest \
    tests/property/test_lint_count_ratchet.py \
    tests/unit/test_github_workflows_disabled.py \
    tests/test_timeout_marker_policy.py -q

# The property shard runs once, first among the test suites: it is the
# largest, so a failure stops the release before the cheaper suites re-pay it.
run uv run python -m pytest tests/property \
    tests/integration/test_gallery_lock.py::test_figure_lock -q -rf --tb=line

run uv run python -m pytest tests/primitives -q -rf --tb=line
run uv run python -m pytest tests/acceleration -q -rf --tb=line
run uv run python -m pytest tests/unit -q -rf --tb=line
run uv run python -m pytest tests/integration -m demo -q -rf --tb=line
# The campaign fixtures build one 450-record campaign that four gates read.
# In a four-way shard the host is the ruler: a loaded host cuts cells before
# their first epoch, the store keeps the artifact, and all fifteen gates fail
# on it (W38). They run serially on their own store, as the plan's step 5 does;
# the shard runs the gates that do not read it.
run uv run python -m pytest tests/acceptance/test_campaign_lock.py \
    tests/acceptance/test_campaign_evidence_lock.py -q -rf --tb=line -n 1
run uv run python -m pytest tests/acceptance -q -rf --tb=line \
    --ignore=tests/acceptance/test_campaign_lock.py \
    --ignore=tests/acceptance/test_campaign_evidence_lock.py

run uv run pip-audit
run uv run python -m build
run uv run python scripts/generate_docs.py --all --check

printf '\nlocal gates: PASS\n'
