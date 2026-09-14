# TODO24 Baseline Freeze (T24.0.1)

**Frozen:** 2026-09-13 (TODO24 Phase 0). This document pins the TODO23
operating point that all TODO24 measurements compare against.

## Catalog hash

`sha256(packages/computronium-lab/src/computronium_lab/synthesis/catalog.py)[:16]` = `844c9658149301ee`

12 catalog rows at freeze time, in definition order:

`backprop_mlp, role_split_muon_readout, temporal_psi_task_switcher, ff_mlp,
fa_mlp, epc_deep, eqprop_mlp, spatial_lattice_bp, ntm_classifier,
ntm_sequence, nca_predictor, pepita_mlp`

## Predictor corpus hash

`sha256(data/icu_measurements.csv)[:16]` = `9a504e8fedd3797d`
(predictor module: `sha256(.../synthesis/predictor.py)[:16]` = `b9d5d1faf2a20004`)

The `I(C,U,P)` viability model (`ViabilityModel.fit(depth_max=2)`) is
trained on this corpus; held-out geometry accuracy 0.944 (recorded in the
D22 mechanism-explorer demo record).

## Calibrated task parameters (quick tier)

| Task | Calibration |
|---|---|
| flat classification (gaussian blob) | scale 1.2, noise 1.5, 75/25 train/val split, `input_dim=32`, `num_classes=4` |
| sequence last_symbol | `seq_len=8`, `input_dim=8`, 120 epochs (0.918–0.922 recorded) |
| sequence threshold | 120 epochs, ~0.65 recorded ceiling |
| sequence parity | at chance at the recorded budget (inherited TODO23 limitation) |
| NCA state prediction | `grid_transition_task`, 3-step rollout, 300 epochs default (certifies at 100) |
| continual ψ adaptation | `Lab.adapt`, frozen-θ ψ episodes; θ bitwise invariance audited |

## Known campaign budgets

- `run_campaign`: seeds `(0, 1, 2)`, reproduction tolerance 0.15 vs catalog Pareto accuracy.
- `promote_mechanism`: one spec per campaign; label-permuted matched control at equal compute; CEEC §18 gates (`promote` threshold 0.95, multi-seed ≥ 3).
- Exploratory synthesis: `exploration_budget=3` campaigns per spec key (default).
- 10-epoch flat-classification runs are cross-process nondeterministic and honestly refuse promotion; reproduction operating point is 0.896 @ 20 ep (3 seeds).

## Known limitations at freeze

- `sequence_parity` does not train above chance at recorded budgets — recorded limitation, not a budget problem.
- Substrate models (memristive/neuromorphic/…) are simulated; energy values are `simulated`/`estimated` tier, never hardware-measured.
- Lab campaign evidence is historically scalar-only (CEEC §27 anti-pattern); TODO24 retires this via structured-kind helpers (T24.0.6).
- `GateStatus` vocabulary reconciled to the METHODOLOGY §15 spec vocabulary (`passed`/`failed`/`unknown`/`waived_with_justification`) in T24.0.6.
- `role_split_mlp` does not exist; the catalog row is `role_split_muon_readout`.

## Budget tiers (T24.0.3, RESEARCH3 E-1 ladder)

| Tier | max_campaigns | max_epochs_per_campaign | max_seeds | Allowed outcomes |
|---|---|---|---|---|
| smoke | 2 | 1 | 1 | pass/fail only |
| quick | 8 | 20 | 3 | frontier hints, exploratory notes |
| certified | 24 | task operating point | 3 | cookbook, belief promotion, publication-grade reports |
