#!/usr/bin/env bash
# experiment_shallow.sh — Run survey-24h profile with a time limit (hours)
#
# Usage:
#   ./experiment_shallow.sh <hours> [--dry-run] [--device auto|cpu|cuda] [--max-workers N]
#
# Examples:
#   ./experiment_shallow.sh 1                    # 1 hour
#   ./experiment_shallow.sh 0.5                  # 30 minutes
#   ./experiment_shallow.sh 2 --max-workers 2    # 2 hours, 2 workers
#   ./experiment_shallow.sh 1 --dry-run          # Show plan without executing

set -euo pipefail

# Defaults
HOURS="${1:-}"
DRY_RUN=false
DEVICE="auto"
MAX_WORKERS=""
EXTRA_ARGS=()

# Parse arguments
shift 1 || true
while [[ $# -gt 0 ]]; do
    case "$1" in
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
        --help|-h)
            echo "Usage: $0 <hours> [--dry-run] [--device auto|cpu|cuda] [--max-workers N]"
            echo ""
            echo "Runs the 'survey-24h' profile with a time budget in hours."
            echo "Results stored in experiment_<N>h.duckdb"
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
    echo "Usage: $0 <hours> [--dry-run] [--device auto|cpu|cuda] [--max-workers N]" >&2
    exit 1
fi

# Check uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' not found in PATH. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check we're in the right directory (has pyproject.toml)
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Not in project root (pyproject.toml not found). Run from computronium directory."
    exit 1
fi

# Convert hours to seconds (float arithmetic)
BUDGET_SECONDS=$(python3 -c "print(int(float('${HOURS}') * 3600))")

# Store path with hours in name
STORE_PATH="experiment_${HOURS}h.duckdb"

# Build command
CMD=(
    uv run comp run survey-24h
    --store "${STORE_PATH}"
    --device "${DEVICE}"
    --overrides "{\"budget_seconds\": ${BUDGET_SECONDS}}"
)

if [[ -n "${MAX_WORKERS}" ]]; then
    CMD+=(--max-workers "${MAX_WORKERS}")
fi

if [[ "${DRY_RUN}" == true ]]; then
    CMD+=(--dry-run)
fi

CMD+=("${EXTRA_ARGS[@]}")

# Log configuration
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  survey-24h Experiment (shallow/broad mapping)              ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Time limit:     ${HOURS} hour(s) (${BUDGET_SECONDS} seconds)"
echo "║  Store:          ${STORE_PATH}"
echo "║  Device:         ${DEVICE}"
[[ -n "${MAX_WORKERS}" ]] && echo "║  Max workers:    ${MAX_WORKERS}"
[[ "${DRY_RUN}" == true ]] && echo "║  Mode:           DRY RUN (plan only)"
echo "║  Profile:        survey-24h (all 6 axes, L0/L1, no settlement)"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Environment check
echo "🔍 Environment check..."

# Write check script to temp file (works in any POSIX shell)
ENV_CHECK=$(cat << 'PYEOF'
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
)

# Execute via temp file to avoid heredoc shell compat issues
TMP_CHECK=$(mktemp --suffix=.py)
echo "$ENV_CHECK" > "$TMP_CHECK"
if ! uv run python "$TMP_CHECK"; then
    rm -f "$TMP_CHECK"
    echo "❌ Environment check failed — see error above"
    echo "   Fix: uv sync --dev --all-extras"
    exit 1
fi
rm -f "$TMP_CHECK"

echo ""
echo "🚀 Executing: ${CMD[*]}"
echo ""

# Run with timeout (add 5 min grace)
GRACE_SECONDS=300
TOTAL_TIMEOUT=$((BUDGET_SECONDS + GRACE_SECONDS))

if [[ "${DRY_RUN}" == true ]]; then
    "${CMD[@]}"
else
    # Use a background process so we can capture output properly
    timeout "${TOTAL_TIMEOUT}" "${CMD[@]}" 2>&1
    EXIT_CODE=$?
    if [[ $EXIT_CODE -eq 124 ]]; then
        echo ""
        echo "⏱️  Experiment timed out after ${TOTAL_TIMEOUT}s (budget + grace)"
        echo "   This is expected — the pipeline enforces soft deadline at ${BUDGET_SECONDS}s"
    elif [[ $EXIT_CODE -ne 0 ]]; then
        echo ""
        echo "❌ Experiment failed with exit code ${EXIT_CODE}"
        echo "   Check the output above for errors."
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