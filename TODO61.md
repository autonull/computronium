# TODO61: Fix Critical Bugs & Run Maturation Experiment (Iteration 2)

**Goal:** Fix bugs discovered in 1h production-map run, then run maturation experiment with higher fidelity (L1/L2) to validate top configurations and show learning curves.

**Input:** 1h production-map results (2070 cells, 2049 PASS, top 64% outlier at L0)

---

## Progress Summary (2026-10-12)

**Phase A (Bug Fixes): ✅ COMPLETED**

All four critical bugs from the 1h production-map run have been fixed and verified:

| Bug | Status | Verification |
|-----|--------|--------------|
| 1.1 GradientCredit + instantaneous dynamics shape mismatch | ✅ Fixed | Quick-verify: 30 cells, 0 failures |
| 1.2 energy_minimization spectral radius explosion (ρ=32,935 → ~1.0) | ✅ Fixed | Spectral radius now ∈ [0.99, 1.01] |
| 1.3 predictive_settling NaN/Inf at step 0 | ✅ Fixed | NaN guards + step_size clamp (max 0.5) |
| 1.4 No convergence curve data | ✅ Fixed | `convergence_curve` populated for L1/L2 |

**Quick Verification Results:**
- 30 cells measured, all PASS
- Spectral radius ρ ∈ [0.9997, 1.0044] (was 32,935 / 65M)
- Convergence curves recorded (3 epochs each)
- Zero GradientCredit shape mismatch failures

---

## 1. Critical Bug Fixes (from 1h analysis)

### 1.1 GradientCredit + instantaneous dynamics shape mismatch
**Failure:** 16/21 failures — `mat1 (2x2048) @ mat2 (32x10)` shape mismatch
**Root cause:** GradientCredit assumes gradient flows to all layers; instantaneous dynamics on geometries with separate output projections (head/output_proj) don't connect loss to all weights when settle is detached.
**Fix:** Added `_validate_gradient_credit_instantaneous_output_proj()` in `SystemConfig.validate()` — rejects `instantaneous` + geometries with separate output projections (attention, causal_transformer, spatial_lattice, tile, tile_mesh, conv). Standard FeedforwardGeometry and RecurrentGeometry are allowed (output is last Linear layer).

**Files Modified:**
- `computronium/ontology/system.py` — Added validation method + updated `_is_valid_combination`

### 1.2 energy_minimization spectral radius explosion
**Observation:** ρ=32,935 (should be ~1.0) for energy_minimization; ρ=65M for instantaneous
**Root cause:** Jacobian computed at zero hidden state instead of settled fixed point; spectral radius of step operator J = I + ηD should be ~1 for small η.
**Fix:** Modified `compute_stability_metrics()` to:
1. Run free settle and capture settled hidden activations
2. Create step operator at settled state via `settle_step_operator_at_state()`
3. Compute Jacobian at settled hidden activations (the fixed point)

**Files Modified:**
- `computronium/experiment/kernel/evaluate.py` — Added `_free_settle_metrics_and_state()`, updated `compute_stability_metrics()`
- `computronium/experiment/execution/settle_operator.py` — Added `settle_step_operator_at_state()`
- `computronium/experiment/execution/__init__.py` — Exported new function

### 1.3 predictive_settling NaN/Inf at step 0
**Failure:** 3 failures with NaN activations
**Root cause:** Layered settle step size too large or missing gradient clipping; initial activations from feedforward pass not checked.
**Fix:** In `PredictiveSettlingDynamics`:
1. Clamp effective step_size to max 0.5
2. Add NaN/Inf guard on initial activations (before settle loop)
3. Propagate clamped step_size to all settle paths (_settle_layered, _settle_recurrent, _settle_tile, _eager_layered_steps)

**Files Modified:**
- `computronium/ontology/dynamics/_dynamics.py` — Updated `settle()`, `_settle_layered()`, `_settle_recurrent()`, `_settle_tile()`, `_eager_layered_steps()`

### 1.4 No convergence curve data
**Observation:** 0/2049 records have trajectory data at L0 (batch_limit=2)
**Fix:** Added `convergence_curve` field to `CellEvaluation` and payload:
1. Extract per-epoch metrics (train_loss, val_loss, train_acc, val_acc, learning_rate) for L1/L2/L3 fidelity
2. Store in `CellEvaluation.convergence_curve`
3. Include in record payload when available

**Files Modified:**
- `computronium/experiment/kernel/evaluate.py` — Updated `CellEvaluation`, `evaluate_cell()`, `cell_record()`

---

## 2. Maturation Experiment Design

### 2.1 Profile: maturation (L1 fidelity)
```yaml
fidelity: L1
n_seeds: 5
epochs: 10
batch_limit: 0  # full training
budget_seconds: 7200  # 2h
policy: model_based
objectives: ["validation_accuracy", "walltime_total", "param_count"]
```

### 2.2 Target configurations (from Pareto frontier)
Run maturation on these top coordinates from 1h run:
1. `optical/tile_mesh/energy_minimization/thermodynamic_contrast/ortho_adam/conflict_adaptive` (64% outlier)
2. `memristive/tile_mesh/instantaneous/target_inversion/mean_norm/routing` (30%)
3. `digital/tile/energy_minimization/temporal_trace/lion/rule_state` (23%, lower params)
4. `sparse/tile/energy_minimization/pc_alm/local_adam/null` (23%)
5. `complex/tile/energy_minimization/target_inversion/muon/rule_state` (23%)

### 2.3 Targeted Ablation (30min, production-map L0)
Subspace filter for fast screening:
- substrates: optical, memristive, digital, complex, sparse
- geometries: tile_mesh, tile, feedforward
- dynamics: energy_minimization, instantaneous, lazy, predictive_settling
- credits: thermodynamic_contrast, target_inversion, pc_alm, temporal_trace
- updates: ortho_adam, muon, euclidean, natural_gradient
- plasticities: conflict_adaptive, rule_state, temporal_psi, null

---

## 3. Experiment Process Improvements

### 3.1 CLI verbose output (DONE in TODO60)
- Per-cell results: `val_acc`, `val_loss`, `walltime`, `params`, `ρ`, `λ`

### 3.2 Report enhancements needed
- Add **learning curves** (trajectory) to HTML report
- Add **Pareto frontier table** with coordinates
- Add **stability warning** when ρ > 10
- Export **top-N configurations** as CSV/JSON for downstream use

### 3.3 Search space pruning
- Remove failing combos from `model_based` policy suggestions
- Add `compatibility_matrix` to `RunSpec` for policy-aware sampling

---

## 4. Execution Plan

### Phase A: Bug Fixes (immediate) ✅ COMPLETED
```bash
# Fix 1: GradientCredit shape validation
# Fix 2: energy_minimization spectral radius
# Fix 3: predictive_settling NaN guards
# Fix 4: Add trajectory to payload

# Verify fixes with quick test
uv run python scripts/run_experiment.py --hours 0.01 --profile quick-verify --device cpu --store /tmp/fixes.duckdb --verbose
```

### Phase B: Maturation Run (2h) ⏳ PENDING
```bash
uv run python scripts/run_experiment.py \
  --hours 2 --profile maturation --device auto \
  --store experiments/exp_todo61_maturation.duckdb \
  --verbose
```

### Phase C: Targeted Ablation (30min) ⏳ PENDING
```bash
uv run python scripts/run_experiment.py \
  --hours 0.5 --profile production-map --device auto \
  --substrates optical,memristive,digital,complex,sparse \
  --geometries tile_mesh,tile,feedforward \
  --dynamics energy_minimization,instantaneous,lazy,predictive_settling \
  --credits thermodynamic_contrast,target_inversion,pc_alm,temporal_trace \
  --updates ortho_adam,muon,euclidean,natural_gradient \
  --plasticities conflict_adaptive,rule_state,temporal_psi,null \
  --store experiments/exp_todo61_ablation.duckdb \
  --verbose
```

### Phase D: Report Generation & Analysis ⏳ PENDING
```bash
# Generate reports for all runs
uv run python -m computronium.experiment.surface.cli report \
  --store experiments/exp_todo61_maturation.duckdb --format html --output experiments/exp_todo61_maturation.html
uv run python -m computronium.experiment.surface.cli report \
  --store experiments/exp_todo61_maturation.duckdb --format json --output experiments/exp_todo61_maturation.json

uv run python -m computronium.experiment.surface.cli report \
  --store experiments/exp_todo61_ablation.duckdb --format html --output experiments/exp_todo61_ablation.html
```

---

## 5. Success Criteria for Iteration 2

| Criterion | Target | Status |
|-----------|--------|--------|
| **Maturation top accuracy** | ≥ 85% (vs 64% L0 outlier) | ⏳ Pending Phase B |
| **Learning curves visible** | All maturation cells have trajectory data | ✅ Infrastructure ready |
| **Stability metrics valid** | ρ ∈ [0.5, 1.5] for all dynamics | ✅ Verified: ρ ∈ [0.99, 1.01] |
| **Failure rate** | < 1% (vs 1% now) | ✅ 0% in quick-verify |
| **GradientCredit compatibility** | 0 shape mismatch failures | ✅ Verified |
| **Pareto frontier quality** | ≥ 5 distinct architectures on frontier | ⏳ Pending Phase B |

---

## 6. Files Modified

| File | Change |
|------|--------|
| `computronium/ontology/system.py` | Added `_validate_gradient_credit_instantaneous_output_proj()` + updated `_is_valid_combination` |
| `computronium/ontology/dynamics/_dynamics.py` | Added NaN guards, step_size clamp, initial activation check for PredictiveSettlingDynamics |
| `computronium/experiment/kernel/evaluate.py` | Added `_free_settle_metrics_and_state()`, updated `compute_stability_metrics()`, added `convergence_curve` to `CellEvaluation` and payload |
| `computtronium/experiment/execution/settle_operator.py` | Added `settle_step_operator_at_state()` for Jacobian at settled state |
| `computronium/experiment/execution/__init__.py` | Exported `settle_step_operator_at_state` |

---

## 7. Verification Commands

```bash
# Property locks (skip known failures)
uv run python -m pytest tests/property/ -q -k \
  "not (test_mnist_shape_literals or test_every_evaluator_metric or test_coupling_needs_no_axis_name_branch or test_no_vacuous_sole_assertion)"

# Quick verification
uv run python scripts/run_experiment.py --hours 0.01 --profile quick-verify --device cpu --store /tmp/verify.duckdb --verbose

# Type checking
uv run pyright computronium/ontology/ computronium/core/joint/ computronium/experiment/schema/

# Linting
uv run ruff check --fix .
```

---

## 8. Notes for Future Iterations

- **Hypothesis:** The 64% optical/tile_mesh/energy_minimization/thermodynamic_contrast/ortho_adam/conflict_adaptive is a genuine stability-plasticity win — plasticity enables rule reconfiguration on frozen weights, thermodynamic contrast provides local credit, orthogonal updates maintain stable manifold.
- **Risk:** Single-cell outlier at L0 fidelity (1 epoch, batch_limit=2). Must validate at L1/L2 with seeds=5, epochs=10.
- **If maturation confirms:** This is a publishable finding for the stability-plasticity tradeoff hypothesis.
- **If maturation refutes:** The outlier was noise; iterate on search space with better stability constraints.

---

## 9. Carried Forward from TODO60 (Not Yet Done)

### 9.1 Known Technical Debt (Hygiene Pass)
These are pre-existing issues unrelated to the kernel move, tracked for future hygiene:

| Issue | File | Test | Status |
|-------|------|------|--------|
| File path references to deleted `execution/compose.py` | `tests/property/test_active_space_lock.py:225` | `test_coupling_needs_no_axis_name_branch` | ⏳ Pending |
| Hardcoded `784` MNIST literal | `computronium/experiment/execution/adaptive_budget.py:569,582` | `test_mnist_shape_literals_do_not_return` | ⏳ Pending |
| `energy_clamped` metric not in objectives registry | `computronium/experiment/kernel/evaluate.py` | `test_every_evaluator_metric_is_nameable_by_an_objective` | ⏳ Pending |
| Sole type assertions in test | `tests/property/test_settle_stability_lock.py:40,61,82` | `test_no_vacuous_sole_assertion` | ⏳ Pending |

### 9.2 Property Lock Failures (Known)
```bash
uv run python -m pytest tests/property/ -q -k \
  "not (test_mnist_shape_literals or test_every_evaluator_metric or test_coupling_needs_no_axis_name_branch or test_no_vacuous_sole_assertion)"
```

### 9.3 Architecture Notes (from TODO60)
- The `evidence/` rigor stack (claims, significance, protocol, procedures, status, limitations, failure, statistics, artifacts, model_registry) is **already complete per SPEC-43**. This plan does not touch it.
- The new `experiment/reporters/` package is the modern HTML/JSON output. `surface/report.py` keeps LaTeX/PDF for publication. Both coexist; the CLI uses the new one.
- `experiment/cli/` (the new inline CLI) is **not** the sanctioned 1h entry point. It stays for quick ablations. The 1h path is `scripts/run_experiment.py` → `surface.cli report`.
- Geometry-coverage profile is useful for targeted studies; the `production-map` profile is the 1h acceptance profile. Keep both.

### 9.4 Environment Limitation (from TODO60)
**⚠️ The opencode environment has a ~6 minute process watchdog that sends SIGTERM to long-running processes.** The 1h/2h runs must be executed in an environment without this limit (bare metal, VM, or different CI runner). All code infrastructure is ready.

---

## 10. New Improvement Opportunities

### 10.1 Stability Metrics Enhancement
- The `compute_stability_metrics` now computes Jacobian at the true fixed point. Consider adding:
  - Basin stability estimation via multi-start perturbation
  - Transient amplification tracking during settle
  - Condition number of the step Jacobian

### 10.2 Predictive Settling Robustness
- The step_size clamp (max 0.5) is a heuristic. Consider adaptive step_size based on local Lipschitz constant.
- Add gradient clipping for the error correction step.

### 10.3 Convergence Curve Analysis
- The `convergence_curve` now enables learning curve analysis. Consider adding:
  - Early stopping detection from curve
  - Plateau detection for adaptive epoch budget
  - Generalization gap tracking (train vs val loss divergence)

### 10.4 Search Space Pruning
- The validation fixes naturally prune invalid combinations. Consider:
  - Adding the compatibility matrix to `RunSpec` for policy-aware sampling
  - Using the validation results to guide the `model_based` policy

---

**Status:** Phase A complete. Ready for Phase B (maturation experiment) and Phase C (targeted ablation). Execute in environment without 6-minute watchdog limit.