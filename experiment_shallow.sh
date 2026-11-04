#!/usr/bin/env bash
# experiment_shallow.sh — Run a SimpleSurvey experiment with a time limit (hours)
#
# Usage:
#   ./experiment_shallow.sh <hours> [--fidelity L0|L1|L2] [--tasks auto|list]
#                          [--workers N] [--store PATH] [--promote-from PATH]
#                          [--promote-top N] [--seed N] [--dry-run] [--device auto|cpu|cuda]
#
# Examples:
#   ./experiment_shallow.sh 0.5 --fidelity L0                    # 30 min L0 screen
#   ./experiment_shallow.sh 0.5 --fidelity L1 --promote-from L0.duckdb  # Promote top 20 from L0
#   ./experiment_shallow.sh 1 --fidelity L2 --promote-from L1.duckdb --promote-top 5  # Deepen top 5
#   ./experiment_shallow.sh 0.01 --dry-run                       # Dry run (generation only)

set -euo pipefail

# Defaults
HOURS=""
FIDELITY="L0"
TASKS="auto"
MAX_WORKERS=4
STORE_PATH=""
PROMOTE_FROM=""
PROMOTE_TOP=20
SEED=42
DRY_RUN=false
DEVICE="auto"
PARAM_BUDGET=0
N_SEEDS=1
EPOCHS=1
BATCH_LIMIT=0
AXES=""
HYPERPARAMETERS=""
OBJECTIVES=""
VERBOSE=false

# Handle --help/-h immediately
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    cat <<'EOF'
Usage: experiment_shallow.sh <hours> [--fidelity L0|L1|L2] [--tasks auto|list] [--workers N] [--store PATH] [--promote-from PATH] [--promote-top N] [--seed N] [--dry-run] [--device auto|cpu|cuda] [--verbose]

Runs a SimpleSurvey experiment with a time budget in hours.
Results stored in <store>.duckdb

Options:
  --fidelity L0|L1|L2     Fidelity level (default: L0)
  --tasks auto|list       Comma-separated task names or "auto" (default: auto)
  --workers N             Max concurrent workers (default: 4)
  --store PATH            DuckDB store path (default: experiment_<hours>h.duckdb)
  --promote-from PATH     Prior store path for importance sampling
  --promote-top N         Number of top cells to promote (default: 20)
  --seed N                Random seed (default: 42)
  --dry-run               Generate cells only, no training
  --device auto|cpu|cuda  Device (default: auto)
  --param-budget N        Parameter budget ceiling (default: 0 = unconstrained)
  --n-seeds N             Seeds per cell (default: 1)
  --epochs N              Epochs per cell (default: 1)
  --batch-limit N         Batch limit (default: 0 = full dataset)
  --axes JSON             JSON: {"axis": ["primitives"]}
  --hyperparams JSON      JSON: hyperparameter domains
  --objectives LIST       Comma-separated objectives
  --verbose, -v           Verbose progress output
  --help, -h              Show this help

Examples:
  experiment_shallow.sh 0.5 --fidelity L0
  experiment_shallow.sh 0.5 --fidelity L1 --promote-from L0.duckdb
  experiment_shallow.sh 1 --fidelity L2 --promote-from L1.duckdb --promote-top 5
  experiment_shallow.sh 0.01 --dry-run
  experiment_shallow.sh 0.1 --fidelity L0 --verbose
EOF
    exit 0
fi

# First positional argument is required hours
HOURS="${1:-}"
shift 1 || true

if [[ -z "${HOURS}" ]]; then
    echo "Error: Hours argument required" >&2
    echo "Usage: $0 <hours> [options]" >&2
    exit 1
fi

# Parse remaining arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --fidelity)
            FIDELITY="${2:-L0}"
            shift 2
            ;;
        --tasks)
            TASKS="${2:-auto}"
            shift 2
            ;;
        --workers)
            MAX_WORKERS="${2:-4}"
            shift 2
            ;;
        --store)
            STORE_PATH="${2:-}"
            shift 2
            ;;
        --promote-from)
            PROMOTE_FROM="${2:-}"
            shift 2
            ;;
        --promote-top)
            PROMOTE_TOP="${2:-20}"
            shift 2
            ;;
        --seed)
            SEED="${2:-42}"
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
        --param-budget)
            PARAM_BUDGET="${2:-0}"
            shift 2
            ;;
        --n-seeds)
            N_SEEDS="${2:-1}"
            shift 2
            ;;
        --epochs)
            EPOCHS="${2:-1}"
            shift 2
            ;;
        --batch-limit)
            BATCH_LIMIT="${2:-0}"
            shift 2
            ;;
        --axes)
            AXES="${2:-}"
            shift 2
            ;;
        --hyperparams)
            HYPERPARAMETERS="${2:-}"
            shift 2
            ;;
        --objectives)
            OBJECTIVES="${2:-}"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Check uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' not found in PATH." >&2
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

# Find project root
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
    echo "❌ Could not find project root (pyproject.toml not found)." >&2
    exit 1
fi

cd "$PROJECT_ROOT"

# Default store path
if [[ -z "${STORE_PATH}" ]]; then
    STORE_PATH="experiment_${HOURS}h.duckdb"
fi

# Build command
CMD=(
    uv run python -m computronium.experiment.simple_survey
    "${HOURS}"
    --fidelity "${FIDELITY}"
    --max-workers "${MAX_WORKERS}"
    --store "${STORE_PATH}"
    --seed "${SEED}"
    --device "${DEVICE}"
    --param-budget "${PARAM_BUDGET}"
    --n-seeds "${N_SEEDS}"
    --epochs "${EPOCHS}"
    --batch-limit "${BATCH_LIMIT}"
)

if [[ "${TASKS}" != "auto" ]]; then
    CMD+=(--tasks "${TASKS}")
fi

if [[ -n "${PROMOTE_FROM}" ]]; then
    CMD+=(--promote-from "${PROMOTE_FROM}")
    CMD+=(--promote-top "${PROMOTE_TOP}")
fi

if [[ -n "${AXES}" ]]; then
    CMD+=(--axes "${AXES}")
fi

if [[ -n "${HYPERPARAMETERS}" ]]; then
    CMD+=(--hyperparameters "${HYPERPARAMETERS}")
fi

if [[ -n "${OBJECTIVES}" ]]; then
    CMD+=(--objectives "${OBJECTIVES}")
fi

if [[ "${DRY_RUN}" == true ]]; then
    CMD+=(--dry-run)
fi

if [[ "${VERBOSE}" == true ]]; then
    CMD+=(--verbose)
fi

# Print configuration
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              SimpleSurvey Experiment                         ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║ Time limit:     %-45s ║\n" "${HOURS} hour(s)"
printf "║ Fidelity:       %-45s ║\n" "${FIDELITY}"
printf "║ Store:          %-45s ║\n" "${STORE_PATH}"
printf "║ Device:         %-45s ║\n" "${DEVICE}"
printf "║ Max workers:    %-45s ║\n" "${MAX_WORKERS}"
printf "║ Seed:           %-45s ║\n" "${SEED}"
[[ -n "${PROMOTE_FROM}" ]] && printf "║ Promote from:   %-45s ║\n" "${PROMOTE_FROM}"
[[ -n "${PROMOTE_FROM}" ]] && printf "║ Promote top:    %-45s ║\n" "${PROMOTE_TOP}"
[[ "${DRY_RUN}" == true ]] && printf "║ Mode:           %-45s ║\n" "DRY RUN (generation only)"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Executing: ${CMD[*]}"
echo ""

# Run with timeout (add 5 min grace)
GRACE_SECONDS=300
BUDGET_SECONDS=$(python3 -c "print(int(float('${HOURS}') * 3600))" 2>/dev/null || awk -v h="${HOURS}" 'BEGIN {print int(h * 3600)}')
TOTAL_TIMEOUT=$((BUDGET_SECONDS + GRACE_SECONDS))

if command -v timeout &> /dev/null; then
    TIMEOUT_CMD=(timeout "${TOTAL_TIMEOUT}")
else
    TIMEOUT_CMD=()
    echo "⚠️  'timeout' command not found; running without hard timeout"
fi

if [[ "${DRY_RUN}" == true ]]; then
    "${CMD[@]}"
else
    if [[ ${#TIMEOUT_CMD[@]} -gt 0 ]]; then
        "${TIMEOUT_CMD[@]}" "${CMD[@]}" 2>&1
    else
        "${CMD[@]}" 2>&1
    fi
    EXIT_CODE=$?

    if [[ $EXIT_CODE -eq 124 ]]; then
        echo ""
        echo "⏱️  Experiment timed out after ${TOTAL_TIMEOUT}s (budget + grace)"
    elif [[ $EXIT_CODE -eq 127 ]]; then
        echo ""
        echo "❌ Command not found. Ensure 'uv' is available." >&2
        exit 127
    elif [[ $EXIT_CODE -ne 0 ]]; then
        echo ""
        echo "❌ Experiment failed with exit code ${EXIT_CODE}" >&2
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