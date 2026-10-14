#!/usr/bin/env bash
# Autonomous discoveries: maturation + ablation in one script
# Run on watchdog-free environment (bare metal / VM / different CI)

set -euo pipefail

cd /home/me/computronium

echo "============================================================"
echo "AUTONOMOUS DISCOVERIES: MATURATION + ABLATION"
echo "============================================================"
echo ""

# Phase 1: Maturation (2h)
echo ">>> PHASE 1: Maturation (2h, L1, 10 epochs, 5 seeds, full training)"
echo "    Top 5 configs from autonomous search:"
echo "    1. sparse/feedforward/instantaneous/gradient/ortho_adam/substrate_coupled (98.06%)"
echo "    2. sparse/feedforward/error_predictive_coding/thermodynamic_contrast/ortho_adam/fast_weights (95.0%)"
echo "    3. sparse/feedforward/instantaneous/pepita/ortho_adam/substrate_coupled (90.8%)"
echo "    4. complex/feedforward/error_predictive_coding/thermodynamic_contrast/riemannian_orthogonal/temporal_psi (90.3%)"
echo "    5. complex/recurrent/energy_minimization/gradient/riemannian_orthogonal/routing (90.3%)"
echo ""

uv run python scripts/run_experiment.py \
  --hours 2 --profile production-map --device cuda \
  --fidelity L1 --epochs 10 --n-seeds 5 --batch-limit 0 \
  --substrates sparse,complex \
  --geometries feedforward,recurrent \
  --dynamics instantaneous,error_predictive_coding,lazy,energy_minimization \
  --credits gradient,thermodynamic_contrast,pepita \
  --updates ortho_adam,riemannian_orthogonal \
  --plasticities substrate_coupled,fast_weights,temporal_psi,routing,rule_state \
  --store experiments/exp_autonomous_maturation.duckdb \
  --verbose

echo ""
echo ">>> Maturation complete. Starting ablation..."
echo ""

# Phase 2: Ablation (30min)
echo ">>> PHASE 2: Targeted ablation (30min, L0, broad subspace)"
echo ""

uv run python scripts/run_experiment.py \
  --hours 0.5 --profile production-map --device cuda \
  --substrates sparse,complex,digital,optical,analog,ternary,memristive \
  --geometries feedforward,recurrent,tile,tile_mesh \
  --dynamics instantaneous,error_predictive_coding,lazy,energy_minimization,spike_integration,predictive_settling \
  --credits gradient,thermodynamic_contrast,pepita,target_inversion,local_goodness,random_projections \
  --updates ortho_adam,riemannian_orthogonal,muon,natural_gradient,local_adam,euclidean,lion,mean_norm \
  --plasticities substrate_coupled,fast_weights,temporal_psi,routing,rule_state,null,conflict_adaptive \
  --store experiments/exp_autonomous_ablation.duckdb \
  --verbose

echo ""
echo "============================================================"
echo "BOTH PHASES COMPLETE"
echo "============================================================"
echo ""
echo "Generate reports:"
echo "  uv run python -m computronium.experiment.surface.cli report \\"
echo "    --store experiments/exp_autonomous_maturation.duckdb --format html \\"
echo "    --output experiments/exp_autonomous_maturation.html"
echo ""
echo "  uv run python -m computronium.experiment.surface.cli report \\"
echo "    --store experiments/exp_autonomous_ablation.duckdb --format html \\"
echo "    --output experiments/exp_autonomous_ablation.html"