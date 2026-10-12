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

**Phase A+ (Hyperparameter-Flow Refactor): ✅ COMPLETED — done as a single source of truth**

The `params={}` mystery (§11) is fixed permanently, not patched. See §11 for the
full root cause and the design. In short:

- A hyperparameter's **identity is `(axis, name)`** and its **name is the config
  field the component reads**. The canonical key is `"{axis}.{name}"`.
- **Both alias tables are deleted** (`CONFIG_FIELD_ALIASES`, `GEOMETRY_ALIASES`).
  The geometry normalizer now reads `num_layers`/`hidden_dim` directly; the
  dynamics/credit/update declarations were renamed to their config fields
  (`step_size`, `beta`, `momentum`). `step_size` is shared by dynamics and update
  and each resolves independently under its axis.
- **`AxisSpec.accepted_params` is the one authority** for "what a primitive
  reads"; composition and the search space both go through
  `ActiveSpace.for_axis`. A new `geometry_keys.py` is the single vocabulary the
  schema and composer share, so drift is impossible by construction.
- Also fixed: log-spaced **integer** domains (`"log_int"` scale) so widths sweep
  as integers, and `max_hidden_dim` sizing now uses the **flattened** input width.

**Verification:** `quick-verify` 40 cells, all PASS, ~41s wall, params displayed
(`[geometry.hidden_dim=33]`) and stored, ρ ∈ [0.97, 1.007], zero failures. The
property tier is 1719 passed; the residual failures are pre-existing (§9.2).

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

### 9.2 Property Lock Failures (Known — pre-existing, verified on the prior commit)
```bash
uv run python -m pytest tests/property/ -q -k \
  "not (test_mnist_shape_literals or test_every_evaluator_metric or test_no_vacuous_sole_assertion)"
```
After the §11 refactor the property tier is **1719 passed / 24 skipped** with the
following **pre-existing** failures (each reproduced on the prior commit with
this work stashed, so none is a regression here):

| Test | Nature |
|------|--------|
| `test_active_space_lock::test_mnist_shape_literals_do_not_return` | `784` literal in `execution/adaptive_budget.py` |
| `test_assertion_quality_lock::test_no_vacuous_sole_assertion` | sole type-assert test |
| `test_stability_energy_metrics_lock::test_every_evaluator_metric...` | `energy_clamped` not in objectives registry |
| `test_undefined_name_lock::test_no_undefined_names_in_tree` | `pd` F821 in `reporters/html.py` |
| `test_lazy_export_lock[execution]` (×3) | `BatchSizer`/`CellStream` map rows not in `__all__`; `compose`/`search_space` stale submodule refs |
| `test_dry_run_gate_lock`, `test_price_oracle_lock`, `test_task_geometry_compat_lock`, `test_width_contract_lock`, `test_settle_stability_lock`, `test_run_ledger_lock`, `test_state_algebra_lock`, `test_readme_build_lock`, `test_lint_count_ratchet` | kernel-move + report/build residuals |


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

### 10.5 Hyperparameter-Flow Follow-ups (post §11 refactor)
- `_TOPOLOGY_KEYS` still lists composer-only keys the harvest never declares
  (`edge_index`, `in_channels`, `pool_hw`, …). Harmless — `for_axis` intersects
  with declared specs — but a `topology → declared-keys` view would make the
  vocabulary auditable against the harvest directly.
- `active.for_axis` is recomputed per cell in `_cell_params` and again in
  `compose_configs`; the dry-run gate already caches composition, but the active
  space itself is not memoised. A per-coordinate cache would cut L0 scan cost
  (the `quick-verify` smoke scanned ~75s of dry-runs for 40 measured cells).
- The property tier still carries pre-existing failures unrelated to this work
  (see §9.2); a hygiene pass should close them before Phase B is treated as a
  clean gate.

---

## 11. Hyperparameter Flow — Root Cause & Design (✅ FIXED, done permanently)

### 11.1 What was actually wrong

The symptom was `coord.params == {}` for every cell, even budgeted runs whose
`spec.hyperparameters` non-empty (the auto-narrowed `hidden_dim`). The plan's
first hypothesis — "availability predicate parsing" — was **wrong**:
availability evaluated fine.

The real defect: **"which swept values does this cell read?" was answered in
three places that had drifted apart.**

1. `HyperparameterSpec.availability` — predicates said a knob is *active*.
2. `AxisSpec.accepted_params` — the config **factory signature** (config field
   names) said a knob is *accepted*.
3. The composer's own geometry key-sets (`_COMMON_GEOMETRY_KEYS`,
   `_TOPOLOGY_KEYS`) + `_GEOMETRY_ALIASES` said what geometry *actually reads*.

`_cell_params` filtered by (2); composition read geometry through (3). For every
axis but geometry those agree. Geometry is built by a **normalizer**, not a
factory: its harvested names were bridged to composer keys (`num_layers` →
`depth`, `hidden_dim` → *passthrough*), so `accepted_params` — the factory
signature `hidden_dims` — named **nothing** a swept width reached. Every swept
`hidden_dim` was therefore dropped, silently, and records lost the width they
trained at. `CONFIG_FIELD_ALIASES` was the same disease on the other axes
(`settle_step`→`step_size`, …): a hand-maintained rename layer over the field a
config reads, forced by a flat, globally-unique hyperparameter namespace.

### 11.2 The permanent design (single source of truth)

**A hyperparameter's identity is `(axis, name)`; its name is the config field
the component reads; the canonical key is `"{axis}.{name}"`.** No translation
layer exists anywhere.

- **Declarations** (`GeometryConfig`, `StateDynamicsConfig`,
  `CreditAssignmentConfig`, `ParameterUpdateConfig`, `PlasticityConfig`
  `.hyperparameters()`) declare each knob under the exact name it consumes.
  Dynamics/credit/update were renamed to their fields (`step_size`, `beta`,
  `momentum`); the geometry normalizer now reads `num_layers` (not `depth`).
- **`AxisSpec.accepted_params` is the one authority** for "what a primitive
  reads". Non-geometry: the factory signature (now matching the declared names).
  Geometry: `geometry_accepted_params(topology)` from the new
  `computronium/experiment/schema/geometry_keys.py`, the one vocabulary the
  schema, composer, and search space share.
- **`ActiveSpace.for_axis(axis, primitive)` is the one filter.** Composition
  (`compose_configs`) and the search space (`_cell_params`) both read it, so a
  carried value is exactly one composition applies.
- **Names may repeat across axes** (`step_size` on dynamics *and* update) — the
  schema no longer forbids it; `step_size` resolves independently per axis.
- Deleted: `CONFIG_FIELD_ALIASES`, `config_field_name`, `GEOMETRY_ALIASES`,
  `_GEOMETRY_ALIASES`. Added: `qualified_name`, `geometry_keys.py`.

### 11.3 Correlated fixes made on the way

- **`"log_int"` domain scale** (`harvest._domain_and_kind`): a log-spaced
  **integer** domain. `hidden_dim` was declared `(8, 4096, "log")` → parsed
  CONTINUOUS → the sweep emitted fractional widths (`34.068…`). It is now
  `(8, 4096, "log_int")` → integer ladder.
- **`max_hidden_dim` sizing** (`RunSpec._max_hidden_dim_for_budget`, `_swept`)
  used `input_shape[-1]` (8 for digits) instead of the flattened `input_dim`
  (64), over-estimating the fitting width ~3.5×. Now uses `TaskShape.input_dim`.

### 11.4 Files (this refactor)

| File | Change |
|------|--------|
| `computronium/experiment/schema/geometry_keys.py` | **NEW** — the composer key vocabulary + `geometry_accepted_params` / `geometry_consumes_name` |
| `computronium/experiment/schema/harvest.py` | `qualified_name`; canonical-keyed `ActiveSpace.values`/`by_name`; deleted alias map; log_int |
| `computronium/experiment/schema/run_spec.py` | canonical keys; auto-narrow `geometry.hidden_dim`; flattened input width |
| `computronium/experiment/schema/seed_registries.py` | `_accepted_params` uses the geometry vocabulary |
| `computronium/experiment/schema/coordinate.py` | rate check strips the axis prefix |
| `computronium/experiment/schema/registries.py` | `RATE_PARAMETERS` = fields (`step_size`, `beta`, …) |
| `computronium/experiment/kernel/search_space.py` | `_swept`/`_cell_params` canonical-keyed; composition parity |
| `computronium/experiment/kernel/compose.py` | geometry reads `num_layers`; `_geometry_mapping` via `for_axis`; no alias |
| `computronium/experiment/execution/optuna_adapter.py` | distributions keyed canonically |
| `computronium/experiment/learning/benchmark.py` | encoder reads canonical keys |
| `computronium/ontology/{geometry,dynamics/_dynamics,credit,update}.py` | declarations renamed to config fields; `log_int` |
| `examples/learning-rules-and-geometry-digits.yaml` | canonical hyperparameter keys |
| `tests/property/test_hyperparameter_flow_lock.py` | **NEW** — real flow lock (no mock injection) |

### 11.5 Locks

- `tests/property/test_hyperparameter_flow_lock.py` — a swept width reaches
  every cell it can size and composition honours it; a knob a topology cannot
  size is dropped, not carried.
- `tests/property/test_hyperparameter_display_lock.py` — rewritten to drive the
  **real** search space (no injected params), so it can fail.
- `test_active_space_lock`, `test_schema_seam_lock` — now assert identity is
  `(axis, name)`, names are the config fields, and no translation exists.

**Success criteria (§11 prior text): MET** — cells display and store their
hyperparameters; `test_hyperparameter_flow_lock` passes (the display shows the
axis-qualified key, e.g. `[geometry.hidden_dim=33]`).

---

**Status:** Phase A **and** Phase A+ complete — the experiment system runs
end-to-end with populated, identity-carrying records. Next: Phase B (maturation)
and Phase C (ablation), which still require an environment without the ~6-minute
watchdog (§9.4).
