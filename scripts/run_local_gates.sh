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
    tests/integration/test_gallery_lock.py::test_figure_lock -q -rf --tb=line \
    --ignore=tests/property/test_experiment_invariants.py

# The experiment-invariant class reads a real campaign store, and the
# property shard has none: fifteen tests used to skip on a flag the release
# never passed, and eight of them were `pytest.skip` stubs with no body
# (W45). The 40-record readiness campaign is the store, and building it
# costs 11 s.
READINESS_STORE="${TMPDIR:-/tmp}/computronium_release_readiness.duckdb"
rm -f "$READINESS_STORE"
run uv run comp run --spec configs/readiness_campaign.yaml \
    --store "$READINESS_STORE" --device cpu --max-workers 1
run uv run python -m pytest tests/property/test_experiment_invariants.py \
    --experiment-db "$READINESS_STORE" -q -rf --tb=line

run uv run python -m pytest tests/primitives -q -rf --tb=line
run uv run python -m pytest tests/acceleration -q -rf --tb=line
run uv run python -m pytest tests/unit -q -rf --tb=line
run uv run python -m pytest tests/integration -m demo -q -rf --tb=line
# The campaign fixtures build one 450-record campaign that four gates read.
# In a four-way shard the host is the ruler: a loaded host cuts cells before
# their first epoch, the store keeps the artifact, and all fifteen gates fail
# on it (W38). They run serially on their own store, as the plan's step 5 does;
# the shard runs the gates that do not read it.
#
# The from-scratch loop fixture is the same class (W40): its 54 s stage budget
# is a wall clock, a four-way shard cuts cells before their second seed, and
# the credits that promote change (serial: thermodynamic_contrast,
# forward_tangent; shard: homeostatic, zeroth_order). It runs serially too.
run uv run python -m pytest \
    tests/acceptance/test_todo63_scientific_validation.py::TestFromScratchTest \
    -q -rf --tb=line -n 1
run uv run python -m pytest tests/acceptance/test_campaign_lock.py \
    tests/acceptance/test_campaign_evidence_lock.py -q -rf --tb=line -n 1
run uv run python -m pytest tests/acceptance -q -rf --tb=line \
    --ignore=tests/acceptance/test_campaign_lock.py \
    --ignore=tests/acceptance/test_campaign_evidence_lock.py \
    --deselect=tests/acceptance/test_todo63_scientific_validation.py::TestFromScratchTest

run uv run pip-audit
run uv run python -m build
run uv run python scripts/generate_docs.py --all --check

printf '\nlocal gates: PASS\n'
