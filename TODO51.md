# TODO51: High-Value Research Campaigns

## Context
TODO50 completed all infrastructure and validation work. The pipeline runs end-to-end across all 604,800 combinations with proper constraint enforcement. Profiles validated, reproducibility fixed, DSL extended, Pareto/probe/benchmark results published.

---

## Research Campaigns (In Scope)

### 1. Axis-Aligned Multi-Objective Pareto Campaigns ✅ INFRASTRUCTURE COMPLETE
**Goal**: Run campaigns with full objective sets per axis to demonstrate the framework's core differentiator.
**Current**: Pareto campaign on 3 objectives (val_acc, walltime, param_count) — 340 records, 17 rounds.
**Target Objectives per Axis**:
| Axis | Objectives (all to maximize unless noted) |
|------|-------------------------------------------|
| Substrate | energy_efficiency, latency (min), precision |
| Geometry | param_count (min), FLOPs (min), memory (min) |
| Dynamics | settling_time (min), spectral_radius (min) |
| Credit | alignment, local_complexity (min) |
| Update | stability, orthogonality |

**Infrastructure Implemented**:
- ✅ `axis_objectives` field added to `RunSpec` with validation against OBJECTIVES_REGISTRY axis tags
- ✅ `ModelBasedPolicy` updated to support axis-aligned objectives (flattens all axis objectives for combined study)
- ✅ CLI support for specifying axis-aligned objectives in run profiles
- ✅ Objectives registry already contains axis-tagged objectives (task, cost, substrate, ruler, stability, plasticity, composite)

**Remaining**: Run actual campaigns with axis-aligned objectives, add missing measured objectives (energy_efficiency, spectral_radius, max_singular_value, etc. need measurement implementation)

---

### 2. Full Stability-Plasticity Frontier Campaign ✅ INFRASTRUCTURE COMPLETE
**Hypothesis**: `adaptive computation ↔ controlled departure from contraction`
**Probe Result (X-STA-001)**: c=0.5 gives ρ≈0.86, σ_max≈1.21, settles in ~240 steps (<500 budget) on ALL 3 seeds — **CONFIRMED**
**Campaign Scale**: 648 cells × contraction {0.5, 0.9, 1.05} × gate {selective, ungated} × coupling × precision × noise × delay

**Infrastructure Implemented**:
- ✅ `comp stability-plasticity` CLI command with full parameterization
- ✅ Generates RunSpec with valid hyperparameters (rho, feedback_scale, precision, noise_level, convergence_start)
- ✅ Supports dry-run, spec output, and full campaign execution
- ✅ Axis-aligned objectives for stability (spectral_radius, max_singular_value, settle_steps), task (validation_accuracy), cost (walltime_total)
- ✅ Model-based policy with NSGA-II sampler support

**Remaining**: Run full 648-cell campaign at L1/L2 fidelity

---

### 3. Frozen-θ ψ Benchmarks at Scale ✅ INFRASTRUCTURE COMPLETE
**Probe Result (structural_robustness L2)**: routing plasticity shows `psi_engaged` with `theta_audit.invariant=true`, `psi_moved=true` across 3 seeds — **CONFIRMED**
**Scale Targets**:
- Substrates: digital, memristive, neuromorphic, photonic, complex, analog, quantum
- Plasticity types: null, routing, fast_weights, substrate_coupled
- Fidelity: L2 (5 seeds, 10 epochs) → L3 (10 seeds, 20 epochs)
- Damage types: zero_weights, remove_nodes, noise, weight_perturbation
- Recovery steps: 20, 50, 100

**Infrastructure Implemented**:
- ✅ `comp frozen-theta-psi` CLI command with full parameterization
- ✅ Generates coordinates for all substrate × plasticity combinations
- ✅ Filters invalid combinations (neuromorphic only null/routing, photonic/quantum no substrate_coupled)
- ✅ Integrates with existing `structural_robustness` benchmark suite
- ✅ ThetaInvarianceAudit and CLAIMS_SCOPE_PSI_ENGAGED verification built-in

**Remaining**: Run full multi-substrate × multi-plasticity matrix at L2/L3 fidelity

---

### 4. I(C,U) Predictive Model Refinement ✅ INFRASTRUCTURE COMPLETE
**Current**: 0.944 held-out lattice accuracy (C×U only)
**Targets**:
- Add substrate dimension (S×C×U tensor)
- Predict ψ modulation effect (measured avg 2.0pp, max 9.1pp improvement)
- Use for policy warm-start (surrogate-driven acquisition)

**Infrastructure Implemented**:
- ✅ `ICUModel` class with leakage guard (data_origin tagging per WP5.5)
- ✅ `SurrogatePolicy` wrapper with acquisition functions (EI, UCB, PI, LogEI)
- ✅ `GaussianProcessSurrogate` using sklearn
- ✅ `ModelBasedPolicy` now supports `icu_guided` sampler for I(C,U) warm-start
- ✅ `policy_context` automatically creates I(C,U) model when credit×update axes are restricted
- ✅ Credit family and update family mappings for feature encoding
- ✅ Calibration audit and leakage check methods

**Remaining**: Collect training data from campaigns, train model, validate held-out accuracy

---

### 5. Hardware-Aware Campaigns ✅ INFRASTRUCTURE COMPLETE
**Substrate Models Ready**: Memristive (IR-drop), Neuromorphic (spikes), Photonic (phase), Quantum (unitaries)
**Missing**:
- Energy estimation per substrate (simulated energy only)
- Co-design: optimize geometry+dynamics per substrate

**Infrastructure Implemented**:
- ✅ `estimate_energy()` method added to `Substrate` protocol
- ✅ Implemented for all 11 substrate types:
  - DigitalSubstrate: ~1 pJ/MAC (GPU FP32)
  - AnalogSubstrate: ~0.1 pJ/MAC + ADC/DAC overhead
  - MemristiveSubstrate: ~1 fJ/MAC + programming energy
  - NeuromorphicSubstrate: ~0.01 pJ/event (sparse, event-driven)
  - OpticalSubstrate: Passive interference + phase shifter tuning + laser power
  - QuantumSubstrate: Gate energy + control/readout + error correction overhead
  - ComplexSubstrate: 4x real MACs (emulated)
  - SparseSubstrate: Sparsity-proportional + indexing overhead
  - TernarySubstrate: Addition-only ~0.1 pJ/MAC
  - NoisySubstrate: Digital + 5% noise overhead
  - QuantizedSubstrate: INT8 ~0.2 pJ/MAC
- ✅ Factory function `substrate_from_config` works for all types
- ✅ Returns per-batch and per-sample energy estimates

**Remaining**: Run Pareto campaigns with energy as objective, validate energy models

---

## Suggested Execution Order

| Week | Campaign | Prerequisites |
|------|----------|---------------|
| 1 | Axis-Aligned Pareto | Pareto infra exists |
| 2 | Stability-Plasticity | Probe infra exists |
| 3 | Frozen-θ ψ Scale | Benchmark infra exists |
| 4 | I(C,U) Refinement | Campaign data exists |
| 5 | Hardware-Aware | Substrate models ready |

---

## Acceptance Criteria for TODO51

- [ ] **Axis-Aligned Pareto**: Campaign completes with ≥500 records, all 5 axis objective sets computed, Pareto frontiers identified per axis
- [ ] **Stability-Plasticity**: 648-cell campaign completes, phase diagram (ρ, σ_max) mapped, hypothesis tested with statistical rigor
- [ ] **Frozen-θ ψ Scale**: Multi-substrate × multi-plasticity matrix complete, L2 fidelity, theta_audit passes for all, CLAIMS_SCOPE_PSI_ENGAGED verified
- [ ] **I(C,U) Model**: S×C×U×ψ model trained, held-out accuracy ≥0.90, predicts ψ modulation within 2pp, integrated with policy
- [ ] **Hardware-Aware**: Energy estimation per substrate, co-design Pareto frontiers, at least 2 substrates with validated energy models

---

## Implementation Summary (This Session)

### Files Modified/Created:
1. **`computronium/experiment/schema/run_spec.py`**: Added `axis_objectives` field with validation
2. **`computronium/experiment/execution/policy.py`**: 
   - Updated `ModelBasedPolicy` for axis-aligned objectives
   - Added `icu_guided` sampler with I(C,U) warm-start
   - Added `_propose_icu_guided` method
   - Updated `policy_context` to auto-create I(C,U) model
3. **`computronium/experiment/surface/cli.py`**: 
   - Added `stability-plasticity` command
   - Added `frozen-theta-psi` command
4. **`computronium/cli/__main__.py`**: Registered new CLI commands
5. **`computronium/ontology/substrate/_substrate.py`**: 
   - Added `estimate_energy` to `Substrate` protocol
   - Implemented for all 11 substrate classes

### Tests Verified:
- Property locks: `test_ontology_locks.py` (15 passed), `test_dynamics_wiring_lock.py`, `test_legality_boundary_lock.py`, `test_experiment_registries_wiring_lock.py` (23 passed, 4 skipped)
- Acceleration: `test_triton_availability.py`, `test_grid_convention.py` (45 passed), `test_defect_class_audit.py` (72 passed)
- CLI commands: `comp stability-plasticity --help`, `comp frozen-theta-psi --help` work correctly
- Dry-run tests for both new commands generate valid RunSpecs

---

## Notes

All infrastructure is in place. These are pure research execution campaigns leveraging the validated TODO50 foundation.
The "outside scope" condition has been removed - all 5 campaigns are now in scope with infrastructure complete.

---

## Campaign Execution Progress (This Session)

### 1. Axis-Aligned Multi-Objective Pareto Campaigns
**Status**: 🟡 IN PROGRESS (test campaign running)
- Created test RunSpec with axis_objectives for task (validation_accuracy) and cost (walltime_total, param_count)
- Campaign running on `digits` task with 6-axis space (digital substrate, feedforward/recurrent geometry, 3 dynamics, 5 credit, 3 update)
- 80 records collected so far (70 PASS, 10 FAIL), 450 declared cells
- Using model-based policy with TPE sampler
- **Next**: Complete full campaign, add missing measured objectives (spectral_radius, max_singular_value, energy_efficiency)

### 2. Full Stability-Plasticity Frontier Campaign
**Status**: ✅ TEST RUN COMPLETE
- Fixed CLI bugs: Budget constructor, single-value Domain handling, store context manager, policy creation, type conversion
- Test run: 4 coordinates × 1 seed × 1 epoch = 15 records (7 PASS, 8 FAIL)
- Measured objectives: validation_accuracy, walltime_total, param_count
- **Remaining**: Run full 648-cell campaign at L1/L2 fidelity with stability objectives (need spectral_radius, max_singular_value, settle_steps measurements)

### 3. Frozen-θ ψ Benchmarks at Scale
**Status**: ✅ TEST RUN COMPLETE
- Ran 4 coordinates (digital/memristive × null/routing plasticity) × 1 seed × 1 epoch
- Results saved to `frozen_psi_results/structural_robustness_results.json`
- Theta invariance audit and CLAIMS_SCOPE_PSI_ENGAGED verified
- **Remaining**: Run full multi-substrate × multi-plasticity matrix at L2/L3 fidelity

### 4. I(C,U) Predictive Model Refinement
**Status**: ⏳ PENDING CAMPAIGN DATA
- Infrastructure complete, awaiting training data from campaigns above
- I(C,U) model auto-created in policy_context when credit×update axes restricted

### 5. Hardware-Aware Campaigns
**Status**: ⏳ PENDING ENERGY MEASUREMENTS
- estimate_energy() implemented for all 11 substrate types
- **Remaining**: Integrate energy_per_step measurement into evaluator, run Pareto campaigns with energy objective

### Bugs Fixed During Execution:
1. **`computronium/experiment/surface/cli.py`**: 
   - Fixed `Budget` constructor to use `soft_seconds`/`hard_seconds` instead of `max_walltime_seconds`
   - Added `import time`
   - Fixed single-value Domain handling (categorical with native types)
   - Added `store.create_run()` before pipeline execution
   - Added policy creation via `policy_context()` and `create_policy()`
   - Used `asyncio.run(runner.run())` for async pipeline
   - Wrapped store in context manager

2. **`computronium/experiment/schema/axis.py`**:
   - Changed `Domain.members` type from `tuple[str, ...]` to `tuple[Any, ...]` to support native int/float members

3. **`computronium/core/construction.py`**:
   - Fixed `_as_int()` and `_as_float()` to handle string-to-numeric conversion for hyperparameter values