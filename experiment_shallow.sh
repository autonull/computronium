#!/usr/bin/env bash
# experiment_shallow.sh — Run a SimpleSurvey or LearningSurvey experiment with a time limit (hours)
#
# Usage:
#   ./experiment_shallow.sh <hours> [--mode static|learn] [--fidelity L0|L1|L2] [--tasks auto|list]
#                          [--workers N] [--store PATH] [--promote-from PATH]
#                          [--promote-top N] [--seed N] [--dry-run] [--device auto|cpu|cuda]
#                          [--verbose] [--self-test] [--doctor] [--resume] [--policy tpe|nsga2|random]
#                          [--ladder] [--cpu-threads N]
#
# Examples:
#   ./experiment_shallow.sh 0.5                                      # learn, TPE, ladder depth
#   ./experiment_shallow.sh 0.5 --policy random                      # sampler control
#   ./experiment_shallow.sh 2 --ladder                               # L0 → L1 → L2 in one run
#   ./experiment_shallow.sh 0.5 --fidelity L1 --promote-from l0.duckdb  # warm start
#   ./experiment_shallow.sh 0.5 --mode static                        # yesterday's exact plan
#   ./experiment_shallow.sh 0.01 --dry-run                           # wave-0 preview

set -euo pipefail

# Defaults (learning mode by default)
HOURS=""
MODE="learn"          # static | learn
POLICY="tpe"          # tpe | nsga2 | random (learn mode only)
FIDELITY="L0"
TASKS="auto"
MAX_WORKERS="auto"
STORE_PATH=""
PROMOTE_FROM=""
PROMOTE_TOP=20
SEED=42
DRY_RUN=false
DEVICE="auto"
PARAM_BUDGET=0
N_SEEDS=""            # empty => fidelity ladder
EPOCHS=""             # empty => fidelity ladder
BATCH_LIMIT=0
AXES=""
HYPERPARAMETERS=""
OBJECTIVES=""
VERBOSE=false
SELF_TEST=false
DOCTOR_MODE=false
RESUME=false
LADDER=false
CPU_THREADS="1"

# Handle --help/-h immediately
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    cat <<'EOF'
Usage: experiment_shallow.sh <hours> [--mode static|learn] [--static] [--learn] [--fidelity L0|L1|L2] [--tasks auto|list] [--workers N] [--store PATH] [--promote-from PATH] [--promote-top N] [--seed N] [--dry-run] [--device auto|cpu|cuda] [--param-budget N] [--n-seeds N] [--epochs N] [--batch-limit N] [--axes JSON] [--hyperparams JSON] [--objectives LIST] [--verbose] [--self-test] [--doctor] [--resume] [--policy tpe|nsga2|random] [--ladder] [--cpu-threads N]

Runs an experiment with a time budget in hours.
Default mode is "learn" (LearningSurvey with TPE sampler and fidelity ladder).
Use --mode static for the original SimpleSurvey deterministic plan.

Options:
  --mode static|learn       Engine: static (SimpleSurvey) or learn (LearningSurvey) (default: learn)
  --static                  Alias for --mode static
  --learn                   Alias for --mode learn
  --policy tpe|nsga2|random Sampler for learn mode (default: tpe)
  --ladder                  Run L0 → L1 → L2 in one invocation, promoting between stages
  --fidelity L0|L1|L2       Fidelity level (default: L0; ignored if --ladder)
  --tasks auto|list         Comma-separated task names or "auto" (default: auto)
  --workers N               Max concurrent workers (default: auto = all cores / GPU count)
  --store PATH              DuckDB store path (default: experiments/experiment_<ts>.duckdb)
  --promote-from PATH       Prior store path for importance sampling / warm start
  --promote-top N           Number of top cells to promote (default: 20)
  --seed N                  Random seed (default: 42)
  --dry-run                 Generate cells only, no training
  --device auto|cpu|cuda    Device (default: auto)
  --param-budget N          Parameter budget ceiling (default: 0 = unconstrained)
  --n-seeds N               Seeds per cell (default: unset = fidelity ladder)
  --epochs N                Epochs per cell (default: unset = fidelity ladder)
  --batch-limit N           Batch limit (default: 0 = full dataset)
  --axes JSON               JSON: {"axis": ["primitives"]}
  --hyperparams JSON        JSON: hyperparameter domains
  --objectives LIST         Comma-separated objectives
  --verbose, -v             Verbose progress output
  --self-test               Run environment self-test before experiment
  --doctor                  Run environment diagnostics only, no experiment
  --resume                  Resume from existing store, skip measured cells (static mode)
  --cpu-threads N           Torch threads per worker (default: 1)
  --help, -h                Show this help

Examples:
  experiment_shallow.sh 0.5
  experiment_shallow.sh 0.5 --policy random
  experiment_shallow.sh 2 --ladder
  experiment_shallow.sh 0.5 --fidelity L1 --promote-from l0.duckdb
  experiment_shallow.sh 0.5 --mode static
  experiment_shallow.sh 0.01 --dry-run
EOF
    exit 0
fi

# First positional argument is required hours (unless --doctor)
if [[ "${1:-}" == "--doctor" ]]; then
    DOCTOR_MODE=true
else
    HOURS="${1:-}"
    shift 1 || true
fi

if [[ "${DOCTOR_MODE}" == false && -z "${HOURS}" ]]; then
    echo "Error: Hours argument required" >&2
    echo "Usage: $0 <hours> [options]" >&2
    exit 1
fi

# Parse remaining arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)
            MODE="${2:-learn}"
            shift 2
            ;;
        --static)
            MODE="static"
            shift
            ;;
        --learn)
            MODE="learn"
            shift
            ;;
        --policy)
            POLICY="${2:-tpe}"
            shift 2
            ;;
        --ladder)
            LADDER=true
            shift
            ;;
        --fidelity)
            FIDELITY="${2:-L0}"
            shift 2
            ;;
        --tasks)
            TASKS="${2:-auto}"
            shift 2
            ;;
        --workers)
            MAX_WORKERS="${2:-auto}"
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
            N_SEEDS="${2:-}"
            shift 2
            ;;
        --epochs)
            EPOCHS="${2:-}"
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
        --self-test)
            SELF_TEST=true
            shift
            ;;
        --doctor)
            DOCTOR_MODE=true
            shift
            ;;
        --resume)
            RESUME=true
            shift
            ;;
        --cpu-threads)
            CPU_THREADS="${2:-1}"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Environment diagnostics function
run_doctor() {
    echo "🔍 Running environment diagnostics via Python module..."
    # Find project root
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/pyproject.toml" ]]; then
            cd "$dir"
            uv run python -m computronium.experiment.environment.diagnostics
            return
        fi
        dir="$(dirname "$dir")"
    done
    echo "❌ Could not find project root (pyproject.toml not found)" >&2
    exit 1
}

if [[ "${DOCTOR_MODE}" == true ]]; then
    run_doctor
    exit 0
fi

# Run doctor automatically if first run to diagnose issues (unless self-test enabled)
if [[ "${SELF_TEST}" == false && -z "${SKIP_DOCTOR:-}" ]]; then
    echo ">>> Running quick diagnostics (use SKIP_DOCTOR=1 to skip)..."
    run_doctor
    echo ""
fi

# Check uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' not found in PATH." >&2
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

# Find project root FIRST (before any PROJECT_ROOT usage)
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
    echo "   Current directory: $PWD" >&2
    exit 1
fi

echo "📁 Project root: ${PROJECT_ROOT}"
cd "$PROJECT_ROOT"

# Test that uv can run the module
echo ">>> Testing uv environment..."
if ! uv run python -c "import sys; print('Python:', sys.version)" 2>&1; then
    echo "⚠️  uv run failed, trying direct python..."
    USE_DIRECT_PYTHON=true
else
    USE_DIRECT_PYTHON=false
fi

# Determine module and default store path from Python layer
if [[ -z "${STORE_PATH}" ]]; then
    if [[ "${USE_DIRECT_PYTHON}" == true ]]; then
        PYTHON_EXE="${PROJECT_ROOT}/.venv/bin/python"
        if [[ ! -f "${PYTHON_EXE}" ]]; then
            PYTHON_EXE="python3"
        fi
        STORE_PATH=$("${PYTHON_EXE}" -c "
import sys
sys.path.insert(0, '.')
from computronium.experiment.simple_survey import _default_store_path
print(_default_store_path())
" 2>&1)
    else
        STORE_PATH=$(uv run python -c "
import sys
sys.path.insert(0, '.')
from computronium.experiment.simple_survey import _default_store_path
print(_default_store_path())
" 2>&1)
    fi
fi

# Select module based on mode
MODULE="computronium.experiment.learning_survey"
[[ "${MODE}" == "static" ]] && MODULE="computronium.experiment.simple_survey"

# Test that the module can be loaded
echo ">>> Testing module import..."
if [[ "${USE_DIRECT_PYTHON}" == true ]]; then
    PYTHON_EXE="${PROJECT_ROOT}/.venv/bin/python"
    if [[ ! -f "${PYTHON_EXE}" ]]; then
        PYTHON_EXE="python3"
    fi
    "${PYTHON_EXE}" -c "import ${MODULE}; print('Module loaded OK')" 2>&1
else
    uv run python -c "import ${MODULE}; print('Module loaded OK')" 2>&1
fi

# Build command
if [[ "${USE_DIRECT_PYTHON}" == true ]]; then
    PYTHON_EXE="${PROJECT_ROOT}/.venv/bin/python"
    if [[ ! -f "${PYTHON_EXE}" ]]; then
        PYTHON_EXE="python3"
    fi
    RUNNER=("${PYTHON_EXE}")
else
    RUNNER=(uv run python)
fi

CMD=( "${RUNNER[@]}" -m "${MODULE}" "${HOURS}"
      --fidelity "${FIDELITY}"
      --max-workers "${MAX_WORKERS}"
      --store "${STORE_PATH}"
      --seed "${SEED}"
      --device "${DEVICE}"
      --param-budget "${PARAM_BUDGET}"
      --batch-limit "${BATCH_LIMIT}"
      --cpu-threads "${CPU_THREADS}" )

# Forward --n-seeds/--epochs only when set (ladder otherwise)
[[ -n "${N_SEEDS}" ]] && CMD+=( --n-seeds "${N_SEEDS}" )
[[ -n "${EPOCHS}"  ]] && CMD+=( --epochs  "${EPOCHS}"  )

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

if [[ "${SELF_TEST}" == true ]]; then
    CMD+=(--self-test)
fi

if [[ "${RESUME}" == true ]]; then
    CMD+=(--resume)
fi

if [[ "${MODE}" == "learn" ]]; then
    CMD+=(--policy "${POLICY}")
fi

if [[ "${LADDER}" == true ]]; then
    CMD+=(--ladder)
fi

# Resolve device and worker count for banner
if [[ "${USE_DIRECT_PYTHON}" == true ]]; then
    PYTHON_EXE="${PROJECT_ROOT}/.venv/bin/python"
    if [[ ! -f "${PYTHON_EXE}" ]]; then
        PYTHON_EXE="python3"
    fi
    RESOLVED_DEVICE=$("${PYTHON_EXE}" -c "
import torch
from computronium.core.utils.device import get_device
d = get_device('${DEVICE}')
print(d.type)
" 2>&1)
    RESOLVED_WORKERS=$("${PYTHON_EXE}" -c "
import torch
import os
try:
    import psutil
    available_gb = psutil.virtual_memory().available / (1024**3)
    max_by_memory = max(1, int(available_gb / 2))
except:
    max_by_memory = 999
if '${MAX_WORKERS}' == 'auto':
    if '${RESOLVED_DEVICE}' == 'cuda':
        print(torch.cuda.device_count() or 1)
    else:
        cores = os.cpu_count() or 4
        print(min(cores, max_by_memory))
else:
    print('${MAX_WORKERS}')
" 2>&1)
else
    RESOLVED_DEVICE=$(uv run python -c "
import torch
from computronium.core.utils.device import get_device
d = get_device('${DEVICE}')
print(d.type)
" 2>&1)
    RESOLVED_WORKERS=$(uv run python -c "
import torch
import os
try:
    import psutil
    available_gb = psutil.virtual_memory().available / (1024**3)
    max_by_memory = max(1, int(available_gb / 2))
except:
    max_by_memory = 999
if '${MAX_WORKERS}' == 'auto':
    if '${RESOLVED_DEVICE}' == 'cuda':
        print(torch.cuda.device_count() or 1)
    else:
        cores = os.cpu_count() or 4
        print(min(cores, max_by_memory))
else:
    print('${MAX_WORKERS}')
" 2>&1)
fi

# Engine and sampler strings for banner
ENGINE_STR="static (SimpleSurvey)"
[[ "${MODE}" == "learn" ]] && ENGINE_STR="learn (PolicyPlanner)"

SAMPLER_STR="N/A"
[[ "${MODE}" == "learn" ]] && SAMPLER_STR="${POLICY} (nsga2 optional)"

DEPTH_STR="fixed (${FIDELITY})"
if [[ "${LADDER}" == true ]]; then
    DEPTH_STR="fidelity ladder (L0=1×1, L1=3×5, L2=5×20)"
elif [[ -n "${N_SEEDS}" || -n "${EPOCHS}" ]]; then
    DEPTH_STR="fixed (${FIDELITY}, n_seeds=${N_SEEDS:-1}, epochs=${EPOCHS:-1})"
fi

# Print banner
echo "╔══════════════════════════════════════════════════════════════╗"
if [[ "${MODE}" == "learn" ]]; then
    echo "║              Experiment (LearningSurvey)                     ║"
else
    echo "║              Experiment (SimpleSurvey)                       ║"
fi
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║ Engine:         %-48s ║\n" "${ENGINE_STR}"
printf "║ Sampler:        %-48s ║\n" "${SAMPLER_STR}"
printf "║ Depth:          %-48s ║\n" "${DEPTH_STR}"
printf "║ Time limit:     %-48s ║\n" "${HOURS} hour(s)"
printf "║ Store:          %-48s ║\n" "${STORE_PATH}"
printf "║ Device:         %-48s ║\n" "${RESOLVED_DEVICE} (resolved from ${DEVICE})"
printf "║ Workers:        %-48s ║\n" "${RESOLVED_WORKERS} (resolved from ${MAX_WORKERS})"
printf "║ Seed:           %-48s ║\n" "${SEED}"
[[ -n "${PROMOTE_FROM}" ]] && printf "║ Promote from:   %-48s ║\n" "${PROMOTE_FROM}"
[[ -n "${PROMOTE_FROM}" ]] && printf "║ Promote top:    %-48s ║\n" "${PROMOTE_TOP}"
[[ "${DRY_RUN}" == true ]] && printf "║ Mode:           %-48s ║\n" "DRY RUN (wave-0 preview)"
[[ "${SELF_TEST}" == true ]] && printf "║ Self-test:      %-48s ║\n" "ENABLED"
[[ "${RESUME}" == true ]] && printf "║ Resume:         %-48s ║\n" "ENABLED"
[[ "${LADDER}" == true ]] && printf "║ Ladder:         %-48s ║\n" "ENABLED"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Executing: ${CMD[*]}"
echo ""

# Run with timeout (add 10 min grace) — Python deadline is the real stop
GRACE_SECONDS=600
BUDGET_SECONDS=$(python3 -c "print(int(float('${HOURS}') * 3600))" 2>/dev/null || awk -v h="${HOURS}" 'BEGIN {print int(h * 3600)}')
TOTAL_TIMEOUT=$((BUDGET_SECONDS + GRACE_SECONDS))

if command -v timeout &> /dev/null; then
    TIMEOUT_CMD=(timeout "${TOTAL_TIMEOUT}")
else
    TIMEOUT_CMD=()
    echo "⚠️  'timeout' command not found; running without hard timeout"
fi

# S1: Wrap execution so the 124 branch, failure hints and post-run summary are reachable under set -e
EXIT_CODE=0

# Run the experiment
if [[ "${DRY_RUN}" == true ]]; then
    echo ">>> Running dry-run..."
    stdbuf -oL -eL "${CMD[@]}" 2>&1
    EXIT_CODE=$?
    echo ">>> Dry-run exit code: $EXIT_CODE"
else
    echo ">>> Starting experiment (timeout: ${TOTAL_TIMEOUT}s, budget enforced by Python)..."
    if [[ ${#TIMEOUT_CMD[@]} -gt 0 ]]; then
        stdbuf -oL -eL "${TIMEOUT_CMD[@]}" "${CMD[@]}" 2>&1
    else
        stdbuf -oL -eL "${CMD[@]}" 2>&1
    fi
    EXIT_CODE=$?
    echo ">>> Experiment exit code: $EXIT_CODE"

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
        echo "   Try running with --doctor to diagnose environment issues"
        exit $EXIT_CODE
    fi
fi

# Post-run summary and checks
if [[ "${DRY_RUN}" != true && $EXIT_CODE -eq 0 ]]; then
    echo ""
    echo "📊 Post-run analysis:"
    echo "  uv run comp coverage report --store ${STORE_PATH}"
    echo "  uv run comp report --store ${STORE_PATH} --format text"
    echo "  uv run comp dashboard --store ${STORE_PATH}"
    
    # S12: Read run.json and warn if under-budget
    RUN_JSON="${STORE_PATH%.duckdb}.run.json"
    if [[ -f "${RUN_JSON}" ]]; then
        WALLTIME=$(python3 -c "
import json, sys
try:
    with open('${RUN_JSON}') as f:
        data = json.load(f)
    print(data.get('walltime_s', 0))
except:
    print(0)
" 2>&1)
        PLANNED=$(python3 -c "
import json, sys
try:
    with open('${RUN_JSON}') as f:
        data = json.load(f)
    print(data.get('cells_planned', 0))
except:
    print(0)
" 2>&1)
        MEASURED=$(python3 -c "
import json, sys
try:
    with open('${RUN_JSON}') as f:
        data = json.load(f)
    print(data.get('cells_evaluated', 0))
except:
    print(0)
" 2>&1)
        
        BUDGET_S=$((HOURS * 3600))
        if (( $(echo "$WALLTIME < 0.8 * $BUDGET_S" | bc -l 2>/dev/null || echo 0) )); then
            echo "⚠️  Warning: walltime ${WALLTIME}s < 80% of budget ${BUDGET_S}s"
        fi
        if (( PLANNED > 0 )) && (( $(echo "$MEASURED < 0.8 * $PLANNED" | bc -l 2>/dev/null || echo 0) )); then
            echo "⚠️  Warning: measured ${MEASURED} cells < 80% of planned ${PLANNED}"
        fi
    fi
fi

exit $EXIT_CODE