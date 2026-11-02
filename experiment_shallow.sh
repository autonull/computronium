#!/usr/bin/env bash
# experiment_shallow.sh — Run a broad survey profile with a time limit (hours)
#
# Usage:
#   ./experiment_shallow.sh <hours> [--profile NAME] [--dry-run] [--device auto|cpu|cuda] [--max-workers N] [--overrides JSON]
#
# Examples:
#   ./experiment_shallow.sh 1                              # 1 hour, survey-24h profile
#   ./experiment_shallow.sh 0.5 --profile quick-verify     # 30 min, quick verify
#   ./experiment_shallow.sh 2 --max-workers 2              # 2 hours, 2 workers
#   ./experiment_shallow.sh 1 --dry-run                    # Show plan without executing
#   ./experiment_shallow.sh 1 --overrides '{"n_seeds": 2}' # 1 hour, 2 seeds/cell

set -euo pipefail

# Defaults
HOURS="${1:-}"
PROFILE="survey-24h"
DRY_RUN=false
DEVICE="auto"
MAX_WORKERS=""
OVERRIDES_JSON=""
EXTRA_ARGS=()

# Parse arguments
shift 1 || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --profile)
            PROFILE="${2:-survey-24h}"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --device)
            DEVICE="${2:-auto}"
            shift 2
            ;;
        --max-workers)
            MAX_WORKERS="${2:-}"
            shift 2
            ;;
        --overrides)
            OVERRIDES_JSON="${2:-}"
            shift 2
            ;;
        --help|-h)
            cat <<'EOF'
Usage: experiment_shallow.sh <hours> [--profile NAME] [--dry-run] [--device auto|cpu|cuda] [--max-workers N] [--overrides JSON]

Runs a broad survey profile with a time budget in hours.
Results stored in experiment_<N>h.duckdb

Profiles:
  survey-24h      Broad 24h mapping: all 6 axes, L0/L1, 1-2 epochs, no settlement (default)
  quick-verify    Fast sanity check: L0 smoke + L1 evidence on few seeds (~5 min)
  quick-run       Dashboard quick-start: diverse cells in ~30s for Pareto/ablation
  production-map  Full broad mapping: L0→L1→L2 maturation with multi-objective Pareto
  demo            One controlled contrast: four credit rules, five axes fixed

Options:
  --profile NAME       Profile to run (default: survey-24h)
  --dry-run            Print plan without executing
  --device auto|cpu|cuda  Device to run on (default: auto)
  --max-workers N      Max concurrent cell workers
  --overrides JSON     JSON overrides for profile parameters
  --help, -h           Show this help

Examples:
  experiment_shallow.sh 1
  experiment_shallow.sh 0.5 --profile quick-verify
  experiment_shallow.sh 2 --max-workers 2 --device cpu
  experiment_shallow.sh 1 --dry-run
  experiment_shallow.sh 1 --overrides '{"n_seeds": 2, "epochs": 2}'
EOF
            exit 0
            ;;
        *)
            EXTRA_ARGS+=("$1")
            shift
            ;;
    esac
done

# Validate hours argument
if [[ -z "${HOURS}" ]]; then
    echo "Error: Hours argument required" >&2
    echo "Usage: $0 <hours> [--profile NAME] [--dry-run] [--device auto|cpu|cuda] [--max-workers N] [--overrides JSON]" >&2
    exit 1
fi

# Check uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' not found in PATH." >&2
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

# Find project root (directory containing pyproject.toml)
find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/pyproject.toml" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

PROJECT_ROOT="$(find_project_root)"
if [[ -z "${PROJECT_ROOT}" ]]; then
    echo "❌ Could not find project root (pyproject.toml not found in any parent directory)." >&2
    echo "   Run this script from within the computronium repository." >&2
    exit 1
fi

cd "$PROJECT_ROOT"

# Check if uv environment is set up
check_uv_env() {
    if [[ ! -d ".venv" ]] && [[ ! -f "uv.lock" ]]; then
        return 1
    fi
    # Quick check if key packages are importable
    if ! uv run python -c "import torch, optuna, scipy, torchvision, pytest" 2>/dev/null; then
        return 1
    fi
    return 0
}

# Convert hours to seconds (float arithmetic, portable)
BUDGET_SECONDS=$(python3 -c "print(int(float('${HOURS}') * 3600))" 2>/dev/null || \
                 awk -v h="${HOURS}" 'BEGIN {print int(h * 3600)}')

# Store path with hours in name
STORE_PATH="experiment_${HOURS}h.duckdb"

# Build overrides JSON
OVERRIDES="{\"budget_seconds\": ${BUDGET_SECONDS}}"
if [[ -n "${OVERRIDES_JSON}" ]]; then
    # Merge user overrides with budget_seconds
    OVERRIDES=$(python3 -c "
import json, sys
base = json.loads('${OVERRIDES}')
user = json.loads('${OVERRIDES_JSON}')
base.update(user)
print(json.dumps(base))
" 2>/dev/null || echo "${OVERRIDES}")
fi

# Build command
CMD=(
    uv run comp run "${PROFILE}"
    --store "${STORE_PATH}"
    --device "${DEVICE}"
    --overrides "${OVERRIDES}"
)

if [[ -n "${MAX_WORKERS}" ]]; then
    CMD+=(--max-workers "${MAX_WORKERS}")
fi

if [[ "${DRY_RUN}" == true ]]; then
    CMD+=(--dry-run)
fi

CMD+=("${EXTRA_ARGS[@]}")

# Log configuration
print_box() {
    local title="$1"
    shift
    local width=64
    printf "╔%*s╗\n" $((width-1)) | tr ' ' '═'
    printf "║ %-*s ║\n" $((width-4)) "${title}"
    printf "╠%*s╣\n" $((width-1)) | tr ' ' '═'
    for line in "$@"; do
        printf "║ %-*s ║\n" $((width-4)) "${line}"
    done
    printf "╚%*s╝\n" $((width-1)) | tr ' ' '═'
}

print_box "survey-24h Experiment (shallow/broad mapping)" \
    "Time limit:     ${HOURS} hour(s) (${BUDGET_SECONDS} seconds)" \
    "Store:          ${STORE_PATH}" \
    "Device:         ${DEVICE}" \
    "$( [[ -n "${MAX_WORKERS}" ]] && echo "Max workers:    ${MAX_WORKERS}" || true )" \
    "$( [[ "${DRY_RUN}" == true ]] && echo "Mode:           DRY RUN (plan only)" || true )" \
    "Profile:        ${PROFILE}"
echo ""

# Environment check with visible output
echo "🔍 Environment check..."

# Create temp file portably
TMP_CHECK="$(mktemp -t env_check_XXXXXX.py 2>/dev/null || mktemp /tmp/env_check_XXXXXX.py)"
cat > "$TMP_CHECK" << 'PYEOF'
import sys
try:
    import torch, optuna, scipy, torchvision, pytest
except ImportError as e:
    print(f"  Missing dependency: {e}", file=sys.stderr)
    sys.exit(1)

print(f"  CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print(f"  GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
import os, psutil
print(f"  CPU cores: {os.cpu_count()}")
print(f"  System RAM: {psutil.virtual_memory().total / 1e9:.1f} GB")
PYEOF

# Run with visible output (not suppressed)
if ! uv run python "$TMP_CHECK"; then
    EXIT_CODE=$?
    rm -f "$TMP_CHECK"
    echo ""
    echo "❌ Environment check failed (exit code: $EXIT_CODE)" >&2
    echo "   The 'uv run' command above shows the actual error." >&2
    echo ""
    echo "   Common fixes:" >&2
    echo "   1. Run: uv sync --dev --all-extras" >&2
    echo "   2. If on a new machine, ensure uv is installed and try: uv venv && uv sync --dev --all-extras" >&2
    echo "   3. Check that pyproject.toml has all required dependencies" >&2
    exit 1
fi
rm -f "$TMP_CHECK"

echo ""
echo "🚀 Executing: ${CMD[*]}"
echo ""

# Run with timeout (add 5 min grace), portable timeout handling
GRACE_SECONDS=300
TOTAL_TIMEOUT=$((BUDGET_SECONDS + GRACE_SECONDS))

# Check if timeout command exists
if command -v timeout &> /dev/null; then
    TIMEOUT_CMD=(timeout "${TOTAL_TIMEOUT}")
else
    # No timeout command - run without hard timeout (pipeline enforces soft deadline)
    TIMEOUT_CMD=()
    echo "⚠️  'timeout' command not found; relying on pipeline soft deadline only"
fi

if [[ "${DRY_RUN}" == true ]]; then
    "${CMD[@]}"
else
    # Run with output visible
    if [[ ${#TIMEOUT_CMD[@]} -gt 0 ]]; then
        "${TIMEOUT_CMD[@]}" "${CMD[@]}" 2>&1
    else
        "${CMD[@]}" 2>&1
    fi
    EXIT_CODE=$?
    
    if [[ $EXIT_CODE -eq 124 ]]; then
        echo ""
        echo "⏱️  Experiment timed out after ${TOTAL_TIMEOUT}s (budget + grace)"
        echo "   This is expected — the pipeline enforces soft deadline at ${BUDGET_SECONDS}s"
    elif [[ $EXIT_CODE -eq 127 ]]; then
        echo ""
        echo "❌ Command not found. Ensure 'uv' and 'comp' are available." >&2
        exit 127
    elif [[ $EXIT_CODE -ne 0 ]]; then
        echo ""
        echo "❌ Experiment failed with exit code ${EXIT_CODE}" >&2
        echo "   Check the output above for errors." >&2
        exit $EXIT_CODE
    fi
fi

# Post-run summary
if [[ "${DRY_RUN}" != true ]]; then
    echo ""
    echo "📊 Post-run analysis:"
    echo "  uv run comp coverage report --store ${STORE_PATH}"
    echo "  uv run comp report --store ${STORE_PATH} --format text"
    echo "  uv run comp dashboard --store ${STORE_PATH}"
fi