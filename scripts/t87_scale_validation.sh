#!/usr/bin/env bash
# TODO87 PHASE 5 — scale validation at L2 depth on one GPU.
#
# C2: digital/feedforward/energy_minimization/null/gradient/adam (2h budget)
# C4: memristive/feedforward/energy_minimization/null/gradient/adam (1.1h budget,
#     n_seeds=1 so one 20-epoch replicate can finish inside the budget —
#     TODO86 measured ~208 s/epoch, so a full L2 seed needs ~70 min).
#
# Run sequentially: one GPU, one store writer.
set -u
cd /home/me/computronium
export UV_LINK_MODE=copy

C2_HOURS=2
C4_HOURS=1

echo "=== C2 start $(date -Is) (budget ${C2_HOURS}h) ==="
timeout $((C2_HOURS * 3600 + 900)) uv run python -m computronium.experiment.survey_cli "$C2_HOURS" \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L2 \
  --store experiments/t87_C2_digital_energy_min.duckdb \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["energy_minimization"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  > logs/t87_C2_digital_energy_min.log 2>&1
echo "=== C2 exit=$? $(date -Is) ==="

echo "=== C4 start $(date -Is) (budget ${C4_HOURS}h) ==="
timeout $((C4_HOURS * 3600 + 900)) uv run python -m computronium.experiment.survey_cli "$C4_HOURS" \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L2 --n-seeds 1 \
  --store experiments/t87_C4_memristive_energy_min.duckdb \
  --axes '{"substrate":["memristive"],"geometry":["feedforward"],"dynamics":["energy_minimization"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  > logs/t87_C4_memristive_energy_min.log 2>&1
echo "=== C4 exit=$? $(date -Is) ==="

echo "=== ALL SCALE RUNS DONE $(date -Is) ==="
