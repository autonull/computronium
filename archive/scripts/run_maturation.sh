#!/usr/bin/env bash
# TODO61 Phase B: Maturation run for autonomous-discovered top configs
# Run on watchdog-free environment (bare metal / VM / different CI)

set -euo pipefail

cd /home/me/computronium

echo "=== Maturation: 2h, L1, 10 epochs, 5 seeds, full training ==="

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