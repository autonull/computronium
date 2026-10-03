# TODO49: Complete End-to-End Experiment Pipeline for All Axes

## Goal
Make the experiment pipeline run `comp run quick-verify` (and other profiles) across **all 604,800 declared combinations** end-to-end, producing valid PASS records for every compatible cell, with proper legality enforcement and reporting.

---

## Current State (from TODO48 investigation)

**Working:** Minimal subset (1 substrate × 1 geometry × 1 dynamics × 1 plasticity × 1 credit × 1 update = 1 cell)
- `digital/feedforward/instantaneous/null/gradient/euclidean` → 50 PASS records on digits L0

**Blocked for full space:**
1. **Axis filtering is hardcoded** — `known_valid_by_axis` in `_filter_axes_for_validity` only covers ~6 primitives/axis
2. **Void constraints incomplete** — 8 registered vs 25+ checks in `SystemConfig.validate()`
3. **Resource constraints deferred** — `max_hidden_dim` etc. need hyperparams only at compose time
4. **GateStage filter incomplete** — only 5/8 void constraints enforced at gate
5. **Search strategy inefficient** — Cartesian product still checks invalid combos first
6. **No systematic validity map** — no single source of truth for "which axis combos work"

---

## Plan: 5 Phases

### Phase 1: Complete Void Constraint Registry (Week 1) ✅ COMPLETED
**Objective:** Make `CONSTRAINTS_REGISTRY` void constraints 1:1 with `SystemConfig.validate()` cross-axis checks.

**Actions:**
- [x] Audit `SystemConfig.validate()` for all cross-axis `raise ValueError` checks (Geometry↔Dynamics, Credit↔Dynamics, Substrate↔Dynamics, Substrate↔Geometry, Credit↔Geometry, Substrate↔Credit, etc.)
- [x] For each check, add a `ConstraintSpec` to `CONSTRAINTS` in `seed_registries.py` using proper AST builders (`not_`, `and_`, `or_`, `in_`, `not_in`, `has_key`)
- [x] Include `task` context for task-fence constraints (classification, language_modeling)
- [x] Target: 24 void constraints matching every `if ...: raise ValueError` in `SystemConfig.validate()` (the "25+" in plan was an estimate including a duplicate)

**Files Modified:**
- `computronium/experiment/schema/seed_registries.py` — added 21 new ConstraintSpec entries
- `computronium/experiment/legality/dsl.py` — added `has_key` builder (already existed)

**Verification:**
```python
# After Phase 1: every SystemConfig.validate() cross-axis check has a registry counterpart
from computronium.experiment.schema.registries import CONSTRAINTS_REGISTRY
void_count = len([c for c in CONSTRAINTS_REGISTRY.values() if c.kind.value == "void"])
assert void_count >= 24  # 24 hard checks (warnings excluded)
```

**New Void Constraints Added:**
- `recurrent_geometry_dynamics` — recurrent geometry requires energy/PC-family/diffusion/instantaneous dynamics
- `nonlayered_geometry_dynamics` — attention/spatial_lattice/graph/conv/nca/ntm/causal_transformer require instantaneous
- `tile_mesh_dynamics` — tile/tile_mesh need energy_minimization/pc_alm/instantaneous
- `nca_ntm_geometry` — nca/ntm need instantaneous
- `diffusion_dynamics_credit` — diffusion blocks gradient/backprop
- `diffusion_dynamics_geometry` — diffusion needs recurrent geometry
- `spike_integration_credit` — spike_integration needs temporal_trace/spiking/target_inversion/target_prop
- `predictive_settling_credit` — predictive_settling/error_predictive_coding need thermodynamic_contrast/equilibrium/local_goodness/forward_only
- `pc_alm_dynamics` — pc_alm needs pc_alm/thermodynamic_contrast credit AND layered geometry
- `residual_connections` — residual=True requires feedforward geometry
- `thermodynamic_contrast_dynamics` — thermodynamic_contrast/equilibrium need energy/PC-family/lazy/pc_alm
- `neuromorphic_substrate_dynamics` — neuromorphic substrate needs temporal dynamics
- `quantum_substrate_dynamics` — quantum substrate needs energy_minimization/instantaneous/diffusion
- `local_contrastive_geometry` — local_goodness/forward_only/pepita/local_contrastive need feedforward geometry
- `attention_geometry_compatibility` — attention geometry incompatible with pepita/local_goodness/local_contrastive/forward_only
- `gradient_credit_beta_clamp` — gradient/backprop with beta >= 1.0 has zero pseudo-gradient

---

### Phase 2: Replace Hardcoded Axis Filtering with SAT/Constraint Solver (Week 1-2) ✅ COMPLETED
**Objective:** Compute valid axis combinations automatically from void constraints, not hardcoded lists.

**Actions:**
- [x] Build a **constraint satisfaction layer** in `_filter_axes_for_validity` that:
  - Takes all primitives per axis (from spec selection)
  - Evaluates all void constraints (as predicates over axis values)
  - Computes the set of valid 6-tuples that satisfy all void constraints
  - Derives per-axis `valid_primitives` from the valid tuples
- [x] Replace `_filter_axes_for_validity` with this computed filter
- [x] Remove `known_valid_by_axis` hardcoded map
- [x] Filter out constraints referencing `params.*` at search space time (evaluated at compose time instead)
- [x] Update `iter_candidates` to use all void constraints (not hardcoded allowlist)
- [x] Increase `_PRICE_SCAN` from 24 to 5000 in `pricing.py` to handle full space

**Files Modified:**
- `computronium/experiment/execution/search_space.py` — new constraint satisfaction logic in `_filter_axes_for_validity` and `iter_candidates`
- `computronium/experiment/execution/pricing.py` — increased `_PRICE_SCAN` to 5000

**Verification:**
```python
# After Phase 2: search space primitives match exactly what SystemConfig.validate() accepts
from computronium.experiment.execution.search_space import search_space_from_spec, iter_candidates
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.execution.evaluate import task_shape

spec = RunSpec(task='digits', fidelity='L1', seed=42, n_seeds=1, epochs=3, param_budget=10000, objectives=('validation_accuracy',), device='cpu')
space = search_space_from_spec(spec)
count = sum(1 for _ in iter_candidates(spec, space, shape=task_shape, max_scan=10000))
assert count > 100  # Should find many valid cells quickly
# Result: 880 valid cells found with full axes
```

---

### Phase 3: Two-Stage Legality (Gate + Compose) (Week 2) 🔄 IN PROGRESS
**Objective:** Enforce all constraints at the right stage — cross-axis at S4 (gate), resource at S5 (compose).

**Actions:**
- [x] **GateStage (S4):** Enforce ALL void constraints (cross-axis compatibility)
  - Use full `CONSTRAINTS_REGISTRY` void predicates
  - Removed `CROSS_AXIS_CONSTRAINT_NAMES` allowlist
  - Filter out constraints referencing `params.*` (evaluated at compose time)
- [ ] **ComposeStage (S5) / TrainStage (S6):** Enforce resource constraints
  - `max_hidden_dim`, `max_layers`, `max_steps` need `coordinate.params` (hyperparameters)
  - These are checked inside `_composable` / `compose_configs` → `SystemConfig.validate()`
  - GateStage should NOT evaluate them (they return None/TypeError without params)
- [x] Unify: `iter_candidates` pre-filters void constraints; `_composable` catches resource constraints
- [ ] Add `ConstraintEnforcement.S5_COMPOSE` for resource constraints if needed

**Files Modified:**
- `computronium/experiment/execution/stages_impl.py` — GateStage: removed allowlist, added params filter
- `computronium/experiment/execution/search_space.py` — iter_candidates: void pre-filter with params filter

**Verification:**
```bash
# Gate correctly rejects invalid cells, passes valid ones
# 20 void constraints usable at gate (4 reference params.* and are deferred to compose)
# Valid cell passes all gate constraints!
# Invalid cell correctly rejected by: nonlayered_geometry_dynamics
```

---

### Phase 4: Hyperparameter Space Integration (Week 2-3) ⏳ PENDING
**Objective:** Properly sweep hyperparameters within valid structural combinations.

**Current issue:** `_walk` does Cartesian product over structural axes × hyperparameter ladders. For valid structural combos, this works. But:
- Some hyperparameters are only valid for specific structural choices (e.g., `num_heads` only for attention)
- `harvest_schema().active(coordinate)` already handles this — but `_composable` re-validates

**Actions:**
- [ ] Verify `harvest_schema().active(coordinate)` correctly narrows hyperparameters per structural selection
- [ ] Ensure `_cell_params` only assigns swept values that `active.for_axis()` permits
- [ ] The `_composable` cache key must include relevant hyperparameters that affect validity
  - Currently: only structural axes + task + param_budget
  - Add: any hyperparameter that `SystemConfig.validate()` checks (e.g., `hidden_dim`, `num_layers`)
- [ ] Consider: for each valid structural combo, what's the valid hyperparameter subspace?

**Files:**
- `computronium/experiment/execution/search_space.py` — `_composable` cache key, `_cell_params`, `_walk`

**Verification:**
```python
# Structural combo + hyperparameter sweep should not produce invalid configs
for coord, sched in iter_candidates(spec, space, shape=task_shape, max_scan=1000):
    assert _composable(coord, sched.task_id, task_shape, sched.param_budget)
```

---

### Phase 5: Full Profile Validation & Reporting (Week 3) ⏳ PENDING
**Objective:** Run all 4 profiles end-to-end with reporting.

**Profiles to validate:**
| Profile | Fidelity | Seeds | Epochs | Budget | Expected Cells |
|---------|----------|-------|--------|--------|----------------|
| quick-verify | L1 | 1 | 3 | 300s | ~50-200 |
| production-map | L0→L1→L2 | 1→5→10 | 1→10→20 | 3600s | ~500-2000 |
| maturation | L2 | 5 | 10 | 7200s | Front cells only |
| claim | L2 | 10 | 20 | ∞ | Claim-grade |

**Actions:**
- [ ] Run `quick-verify` to completion (60s budget) — verify 50+ PASS records
- [ ] Run `production-map` with budget — verify maturation + promotion works
- [ ] Run `maturation` on production-map front cells — verify L2 re-runs
- [ ] Run `claim` — verify CEEC governance + uncertainty computation
- [ ] Generate reports: `comp report`, `comp conformance`, `comp status`
- [ ] Verify replay hash matches across runs

**Files:**
- `computronium/experiment/surface/cli.py` — profile definitions (may need budget tuning)
- `computronium/experiment/execution/promotion.py` — promotion logic
- `computronium/experiment/evidence/claims.py` — uncertainty computation

**Verification:**
```bash
# Quick-verify
comp run quick-verify --store /tmp/qv.duckdb --dry-run  # Shows valid cells
comp run quick-verify --store /tmp/qv.duckdb  # ~60s, 50+ PASS
comp report --store /tmp/qv.duckdb

# Production-map (longer)
comp run production-map --store /tmp/pm.duckdb --dry-run
comp run production-map --store /tmp/pm.duckdb  # ~1hr
comp report --store /tmp/pm.duckdb --format json
```

---

## Technical Debt to Address Alongside

| Debt | Location | Fix |
|------|----------|-----|
| `expr_from_string` still used for non-void constraints | `seed_registries.py` hard constraints | Convert all to AST builders |
| ~~`_PRICE_SCAN=24` too small for full space~~ | `pricing.py` | **FIXED**: Increased to 5000 |
| `_MAX_SCAN=10000` may cut off valid cells | `search_space.py` | Increase or make adaptive |
| Warning spam from `SystemConfig.validate()` | `ontology/system.py` | Downgrade to debug or aggregate |
| No progress indicator for long runs | `pipeline.py` | Add tqdm/rich progress bar |

---

## Success Criteria (Definition of Done)

1. **`comp run quick-verify --store /tmp/test.duckdb`** completes in <60s with **>50 PASS records** across multiple valid axis combinations
2. **All 4 profiles** execute without crashes, producing valid records
3. **`comp report`** shows meaningful coverage across axes (not just 1 primitive per axis)
4. **`comp conformance`** passes for required capabilities
5. **Replay hash** matches for resumed runs
6. **Zero gate rejections** for cross-axis compatibility (all caught at search space time)
7. **Resource constraint failures** only at compose time, properly classified

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SAT solving 604k combos too slow | Simple iteration with DSL eval is ~0.5ms/combo = 5min; cache per spec; precompute at S2 |
| Hyperparameter space explodes valid combos | `param_budget` + fairness constraint already limits; `_composable` caches by structural axes only |
| `SystemConfig.validate()` has implicit rules not in registry | Phase 1 audit must be exhaustive; add test: every `raise ValueError` in validate() has registry entry |
| Promotion/maturation logic untested at scale | Run production-map with small budget first; verify promotion criteria |

---

## Dependencies

- **Phase 1 → Phase 2:** Void constraints must be complete before computing valid combos ✅
- **Phase 2 → Phase 3:** Valid combos from Phase 2 feed gate filtering ✅
- **Phase 3 → Phase 4:** Two-stage legality enables proper hyperparameter sweep 🔄
- **Phase 4 → Phase 5:** Full sweep needed for meaningful profiles ⏳

---

## Timeline Estimate

| Phase | Duration | Cumulative |
|-------|----------|------------|
| 1: Complete Void Constraints | 3 days | 3 days |
| 2: SAT/Constraint Solver | 5 days | 8 days |
| 3: Two-Stage Legality | 3 days | 11 days |
| 4: Hyperparameter Integration | 4 days | 15 days |
| 5: Profile Validation | 3 days | 18 days |
| **Buffer** | 5 days | **23 days** |

**Actual Progress:** Phases 1-2 complete, Phase 3 partially complete (gate side done, compose side pending)

---

## Appendix: SystemConfig.validate() Cross-Axis Checks Checklist

From `computronium/ontology/system.py:379-425`:

**Geometry-Dynamics:**
- [x] `_validate_recurrent_geometry_dynamics` — recurrent needs energy/PC/diffusion/instantaneous
- [x] `_validate_nonlayered_geometry_dynamics` — attention/spatial_lattice/graph/conv/nca/ntm/causal_transformer need instantaneous
- [x] `_validate_tile_mesh_dynamics` — tile/tile_mesh need energy_minimization/pc_alm/instantaneous
- [x] `_validate_nca_ntm_geometry` — nca/ntm need instantaneous

**Dynamics-Credit:**
- [x] `_validate_diffusion_dynamics_credit` — diffusion blocks gradient/backprop
- [x] `_validate_spike_integration_credit` — spike_integration needs temporal_trace/spiking/target_inversion/target_prop
- [x] `_validate_predictive_settling_credit` — predictive_settling/error_predictive_coding needs thermodynamic_contrast/equilibrium/local_goodness/forward_only

**Dynamics-Geometry:**
- [x] `_validate_diffusion_dynamics_geometry` — diffusion needs recurrent

**Credit-Geometry:**
- [x] `_validate_local_contrastive_geometry` — local_contrastive needs layered geometry
- [x] `_validate_attention_geometry_compatibility` — attention geometry needs compatible credit

**Credit-Dynamics:**
- [x] `_validate_thermodynamic_contrast_dynamics` — thermodynamic_contrast needs energy/PC-family

**Substrate-Dynamics:**
- [x] `_validate_neuromorphic_substrate_dynamics`
- [ ] `_validate_analog_substrate_noise` (warning only)
- [ ] `_validate_complex_substrate_credit` (warning only)
- [x] `_validate_quantum_substrate_dynamics`
- [ ] `_validate_sparse_substrate_update` (warning only)
- [ ] `_validate_ternary_substrate_credit` (warning only)
- [ ] `_validate_diffusion_substrate_noise` (warning only)

**Geometry-Substrate:**
- [ ] `_validate_spatial_neuromorphic_geometry_substrate` (warning only)
- [ ] `_validate_tile_mesh_sparse_substrate` (warning only)

**Special:**
- [x] `_validate_gradient_credit_beta_clamp`
- [ ] `_validate_per_element_displacement_step_size` (warning only)
- [ ] `_validate_energy_minimization_momentum_update` (warning only)

**Total: 16 hard cross-axis checks + 3 resource + 2 task fence + 3 original = 24 void constraints registered**

---

## Notes for Remaining Work

1. **Phase 3 Compose Stage**: Need to ensure resource constraints (max_hidden_dim, max_layers, max_steps) are properly enforced at S5 compose time. Currently they're checked in `_composable` but not in the GateStage. The `compose_configs` function calls `SystemConfig.validate()` which will catch them.

2. **Phase 4 Hyperparameters**: The `_composable` cache key currently only includes structural axes + task + param_budget. Need to add hyperparameters that affect validity (hidden_dim, num_layers, max_steps, beta). This ensures a cell that passes gate but fails compose due to hyperparameter values is properly cached.

3. **Phase 5 Full Profiles**: The quick-verify profile currently declares ALL primitives (no axis restrictions). This produces 604,800 declared combinations. With the new constraint satisfaction, only ~24+ are legal. The budget of 300s may not be enough to measure all legal cells. Consider adding axis restrictions to the quick-verify profile or increasing budget.

4. **Reproducibility Issue**: During testing, a cell failed replay validation ("replay did not reproduce the claimed metrics within tolerance 0.25"). This is a pre-existing issue unrelated to the constraint changes, but should be investigated before full profile runs.

5. **Performance**: The constraint satisfaction in `_filter_axes_for_validity` evaluates all combinations (up to 604,800) with DSL predicates. For the full space this takes ~2-3 seconds. Caching per RunSpec is already implemented via the search space snapshot.

6. **Remaining Void Constraints**: 4 constraints reference `params.*` and are deferred to compose time:
   - `residual_connections` (checks `params.residual`)
   - `gradient_credit_beta_clamp` (checks `params.beta`)
   - `max_hidden_dim` (checks `params.hidden_dim`)
   - `max_layers` (checks `params.num_layers`)
   - `max_steps` (checks `params.max_steps`)
   These should be enforced at S5 ComposeStage when hyperparameters are available.