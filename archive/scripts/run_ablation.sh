#!/usr/bin/env bash
# TODO61 Phase C: Targeted ablation around autonomous discoveries
# 30 min, production-map L0, broader subspace

set -euo pipefail

cd /home/me/computronium

echo "=== Ablation: 30min, L0, broad subspace around top configs ==="

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