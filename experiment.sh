#!/usr/bin/env bash
# experiment.sh - Run TODO61 Full Maturation + Ablation + Reports (2.5h)
#
# This script runs the complete experiment pipeline:
#   Phase B: Full maturation of 2 confirmed Pareto configurations (L1, 5 seeds, 10 epochs)
#   Phase C: Targeted ablation (30min, production-map L0, subspace filter)
#   Phase D: Generate HTML/JSON reports
#
# Usage: ./experiment.sh [--device auto|cpu|cuda] [--maturation-hours 2] [--ablation-hours 0.5]
#        ./experiment.sh --help
#
# Prerequisites:
#   - uv sync --dev --all-extras (run once before first execution)
#   - Run on bare metal/VM without 6-minute process watchdog

set -euo pipefail

# ============================================================
# Configuration - FULL MATURATION RUN (2h + 30min)
# ============================================================
DEVICE="cuda"
MATURATION_HOURS=2
ABLATION_HOURS=0.5
MATURATION_STORE="experiments/exp_todo61_maturation.duckdb"
ABLATION_STORE="experiments/exp_todo61_ablation.duckdb"
LOG_DIR="logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MAIN_LOG="${LOG_DIR}/experiment_${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# The 5 Pareto configurations from 1h production-map run
# (TODO61 §2.2 - run maturation on THESE, not broad search)
# ============================================================
# 1. optical/tile_mesh/energy_minimization/thermodynamic_contrast/ortho_adam/conflict_adaptive (64% outlier)
# 2. memristive/tile_mesh/instantaneous/target_inversion/mean_norm/routing (30%)
# 3. digital/tile/energy_minimization/temporal_trace/lion/rule_state (23%, lower params)
# 4. sparse/tile/energy_minimization/pc_alm/local_adam/null (23%)
# 5. complex/tile/energy_minimization/target_inversion/muon/rule_state (23%)

# ============================================================
# Helper Functions
# ============================================================
log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} [${level}] ${msg}" | tee -a "${MAIN_LOG}"
}

info() { log "INFO" "${BLUE}$*${NC}"; }
warn() { log "WARN" "${YELLOW}$*${NC}"; }
error() { log "ERROR" "${RED}$*${NC}"; }
success() { log "SUCCESS" "${GREEN}$*${NC}"; }

run_cmd() {
    local cmd="$*"
    info "Running: ${cmd}"
    eval "${cmd}" 2>&1 | tee -a "${MAIN_LOG}"
    local exit_code=${PIPESTATUS[0]}
    if [[ ${exit_code} -ne 0 ]]; then
        error "Command failed with exit code ${exit_code}: ${cmd}"
        return ${exit_code}
    fi
    success "Command completed: ${cmd}"
    return 0
}

check_env() {
    info "Checking environment..."
    if ! command -v uv &> /dev/null; then
        error "uv not found. Please install uv first."
        exit 1
    fi

    if uv run python -c "import optuna, scipy, torchvision, pytest" 2>&1 | grep -q "ModuleNotFoundError"; then
        warn "Some dev packages may be missing. Run: uv sync --dev --all-extras"
    else
        success "Dev environment OK"
    fi

    mkdir -p experiments logs
    success "Directories ready: experiments/, logs/"
}

# ============================================================
# Phase B: FULL Targeted Maturation Experiment
# ============================================================
run_maturation() {
    info "========================================"
    info "PHASE B: Full Targeted Maturation (${MATURATION_HOURS}h)"
    info "========================================"
    info "Re-running 2 CONFIRMED Pareto configurations at L1 fidelity"
    info "Seeds: 5, Epochs: 10, Batch limit: 0 (full training)"
    info "Policy: model_based (exploit known good regions)"
    info "Objectives: validation_accuracy, walltime_total, param_count"
    info "Store: ${MATURATION_STORE}"
    info ""
    info "Target configurations (CONFIRMED at 89% L1 in quick run):"
    info "  1. optical/tile_mesh/energy_minimization/thermodynamic_contrast/ortho_adam/conflict_adaptive (89.2%)"
    info "  2. memristive/tile_mesh/instantaneous/target_inversion/mean_norm/routing (88.9%)"

    local start_time=$(date +%s)

    # Run targeted production-map with ONLY the 2 confirmed Pareto configurations
    run_cmd "uv run python scripts/run_experiment.py \
        --hours ${MATURATION_HOURS} \
        --profile production-map \
        --device ${DEVICE} \
        --fidelity L1 \
        --epochs 10 \
        --n-seeds 5 \
        --batch-limit 0 \
        --substrates optical,memristive \
        --geometries tile_mesh \
        --dynamics energy_minimization,instantaneous \
        --credits thermodynamic_contrast,target_inversion \
        --updates ortho_adam,mean_norm \
        --plasticities conflict_adaptive,routing \
        --store ${MATURATION_STORE} \
        --verbose"

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    success "Phase B completed in $((duration / 60))m $((duration % 60))s"
}

# ============================================================
# Phase C: QUICK Targeted Ablation
# ============================================================
run_ablation() {
    info "========================================"
    info "PHASE C: Quick Targeted Ablation (${ABLATION_HOURS}h = ~1 min)"
    info "========================================"
    info "Profile: production-map (L0 fidelity, 1 epoch, batch_limit=2)"
    info "Subspace filter matching Pareto subspace for fast screening"
    info "Store: ${ABLATION_STORE}"

    local start_time=$(date +%s)

    run_cmd "uv run python scripts/run_experiment.py \
        --hours ${ABLATION_HOURS} \
        --profile production-map \
        --device ${DEVICE} \
        --substrates optical,memristive,digital,sparse,complex \
        --geometries tile_mesh,tile \
        --dynamics energy_minimization,instantaneous \
        --credits thermodynamic_contrast,target_inversion,temporal_trace,pc_alm \
        --updates ortho_adam,muon,euclidean,natural_gradient,lion,local_adam,mean_norm \
        --plasticities conflict_adaptive,rule_state,routing,null \
        --store ${ABLATION_STORE} \
        --verbose"

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    success "Phase C completed in $((duration / 60))m $((duration % 60))s"
}

# ============================================================
# Phase D: Report Generation
# ============================================================
generate_reports() {
    info "========================================"
    info "PHASE D: Report Generation"
    info "========================================"

    # Maturation reports
    if [[ -f "${MATURATION_STORE}" ]]; then
        info "Generating maturation reports..."
        run_cmd "uv run python -m computronium.experiment.surface.cli report \
            --store ${MATURATION_STORE} \
            --format html \
            --output experiments/exp_todo61_maturation.html"

        run_cmd "uv run python -m computronium.experiment.surface.cli report \
            --store ${MATURATION_STORE} \
            --format json \
            --output experiments/exp_todo61_maturation.json"

        success "Maturation reports generated:"
        info "  HTML: experiments/exp_todo61_maturation.html"
        info "  JSON: experiments/exp_todo61_maturation.json"
    else
        warn "Maturation store not found: ${MATURATION_STORE}"
    fi

    # Ablation reports
    if [[ -f "${ABLATION_STORE}" ]]; then
        info "Generating ablation reports..."
        run_cmd "uv run python -m computronium.experiment.surface.cli report \
            --store ${ABLATION_STORE} \
            --format html \
            --output experiments/exp_todo61_ablation.html"

        run_cmd "uv run python -m computronium.experiment.surface.cli report \
            --store ${ABLATION_STORE} \
            --format json \
            --output experiments/exp_todo61_ablation.json"

        success "Ablation reports generated:"
        info "  HTML: experiments/exp_todo61_ablation.html"
        info "  JSON: experiments/exp_todo61_ablation.json"
    else
        warn "Ablation store not found: ${ABLATION_STORE}"
    fi
}

# ============================================================
# Summary
# ============================================================
print_summary() {
    info "========================================"
    info "EXPERIMENT COMPLETE - SUMMARY"
    info "========================================"
    info "Main log: ${MAIN_LOG}"
    info ""
    info "Outputs:"
    if [[ -f "experiments/exp_todo61_maturation.html" ]]; then
        info "  ✓ Maturation HTML: experiments/exp_todo61_maturation.html"
    fi
    if [[ -f "experiments/exp_todo61_maturation.json" ]]; then
        info "  ✓ Maturation JSON: experiments/exp_todo61_maturation.json"
    fi
    if [[ -f "experiments/exp_todo61_ablation.html" ]]; then
        info "  ✓ Ablation HTML: experiments/exp_todo61_ablation.html"
    fi
    if [[ -f "experiments/exp_todo61_ablation.json" ]]; then
        info "  ✓ Ablation JSON: experiments/exp_todo61_ablation.json"
    fi
    info ""
    info "Stores (for re-analysis):"
    if [[ -f "${MATURATION_STORE}" ]]; then
        info "  ✓ ${MATURATION_STORE}"
    fi
    if [[ -f "${ABLATION_STORE}" ]]; then
        info "  ✓ ${ABLATION_STORE}"
    fi
    info ""
    info "SUCCESS CRITERIA (TODO61 §5):"
    info "  • Maturation top accuracy ≥ 85% (vs 64% L0 outlier)"
    info "  • All maturation cells have convergence_curve (learning curves)"
    info "  • Stability metrics valid: spectral_radius ∈ [0.5, 1.5]"
    info "  • Failure rate < 1%"
    info "  • GradientCredit compatibility: 0 shape mismatch failures"
    info "  • Pareto frontier quality: ≥ 5 distinct architectures"
    info ""
    info "Next steps:"
    info "  1. Open HTML reports to review learning curves, Pareto frontiers"
    info "  2. Check JSON for convergence_curve data (per-epoch metrics)"
    info "  3. Verify stability metrics: spectral_radius ∈ [0.5, 1.5]"
    info "  4. Compare maturation top accuracy vs 64% L0 outlier (target ≥ 85%)"
}

# ============================================================
# Signal Handling
# ============================================================
cleanup() {
    warn "Interrupted! Cleaning up..."
    pkill -P $$ 2>/dev/null || true
    exit 130
}
trap cleanup SIGINT SIGTERM

# ============================================================
# Argument Parsing
# ============================================================
usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Run TODO61 Full Maturation + Ablation + Reports (~2.5h)

Options:
    --device DEVICE           Device to use: auto, cpu, cuda (default: cuda)
    --maturation-hours HOURS  Maturation run duration in hours (default: 2)
    --ablation-hours HOURS    Ablation run duration in hours (default: 0.5)
    --maturation-store PATH   DuckDB store for maturation (default: experiments/exp_todo61_maturation.duckdb)
    --ablation-store PATH     DuckDB store for ablation (default: experiments/exp_todo61_ablation.duckdb)
    --skip-maturation         Skip Phase B (maturation)
    --skip-ablation           Skip Phase C (ablation)
    --skip-reports            Skip Phase D (report generation)
    --check-env-only          Only check environment, don't run experiments
    -h, --help                Show this help

Environment:
    UV_LINK_MODE=copy         Recommended for this filesystem (avoids hardlink warnings)

Example:
    $0 --device cuda

Note: Run on bare metal/VM without 6-minute process watchdog.
      This script will take ~2.5 hours total.
      Phase B targets EXACTLY 2 confirmed Pareto configs (not broad search).
      For quick 10-min test: $0 --maturation-hours 0.15 --ablation-hours 0.02
EOF
}

SKIP_MATURATION=false
SKIP_ABLATION=false
SKIP_REPORTS=false
CHECK_ENV_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --device)
            DEVICE="$2"
            shift 2
            ;;
        --maturation-hours)
            MATURATION_HOURS="$2"
            shift 2
            ;;
        --ablation-hours)
            ABLATION_HOURS="$2"
            shift 2
            ;;
        --maturation-store)
            MATURATION_STORE="$2"
            shift 2
            ;;
        --ablation-store)
            ABLATION_STORE="$2"
            shift 2
            ;;
        --skip-maturation)
            SKIP_MATURATION=true
            shift
            ;;
        --skip-ablation)
            SKIP_ABLATION=true
            shift
            ;;
        --skip-reports)
            SKIP_REPORTS=true
            shift
            ;;
        --check-env-only)
            CHECK_ENV_ONLY=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# ============================================================
# Main
# ============================================================
main() {
    info "========================================"
    info "TODO61 Experiment Runner - TARGETED MATURATION"
    info "========================================"
    info "Timestamp: ${TIMESTAMP}"
    info "Device: ${DEVICE}"
    info "Maturation: ${MATURATION_HOURS}h (${SKIP_MATURATION:-false})"
    info "Ablation: ${ABLATION_HOURS}h (${SKIP_ABLATION:-false})"
    info "Reports: ${SKIP_REPORTS:-false}"
    info "Log: ${MAIN_LOG}"
    info "========================================"

    check_env

    if [[ "${CHECK_ENV_ONLY}" == "true" ]]; then
        success "Environment check complete. Exiting."
        exit 0
    fi

    local overall_start=$(date +%s)

    # Phase B: Targeted Maturation
    if [[ "${SKIP_MATURATION}" != "true" ]]; then
        run_maturation
    else
        warn "Skipping Phase B (maturation)"
    fi

    # Phase C: Ablation
    if [[ "${SKIP_ABLATION}" != "true" ]]; then
        run_ablation
    else
        warn "Skipping Phase C (ablation)"
    fi

    # Phase D: Reports
    if [[ "${SKIP_REPORTS}" != "true" ]]; then
        generate_reports
    else
        warn "Skipping Phase D (reports)"
    fi

    local overall_end=$(date +%s)
    local total_duration=$((overall_end - overall_start))
    info "========================================"
    success "Total experiment time: $((total_duration / 3600))h $(((total_duration % 3600) / 60))m $((total_duration % 60))s"
    print_summary
}

# Run main
main "$@"