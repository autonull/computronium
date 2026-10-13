# TODO62: Improvements from Quick Maturation Findings

**Source:** Quick maturation run (10 min, L1 fidelity, 3 epochs, 1 seed) on 5 Pareto configs from 1h production-map run.

**Key Finding:** 2/5 Pareto configs confirmed at **89% L1 accuracy** (vs 64%/30% L0):
1. `optical/tile_mesh/energy_minimization/thermodynamic_contrast/ortho_adam/conflict_adaptive` — 89.2%
2. `memristive/tile_mesh/instantaneous/target_inversion/mean_norm/routing` — 88.9%

3 false positives: 13-15% at L1 (different plasticity: rule_state, null).

---

## 1. Search Space Priors & Pruning (High Impact, Low Effort)

### 1.1 Add Tile Mesh + Plasticity Priors
**File:** `computronium/experiment/surface/cli.py` → `RUN_PROFILES`
- Add `tile_mesh` as primary geometry for maturation/claim profiles
- Add `conflict_adaptive`, `routing` as primary plasticities
- Add `optical`, `memristive` as primary substrates
- Add `energy_minimization`, `instantaneous` as primary dynamics for tile_mesh

### 1.2 Compatibility Matrix in RunSpec
**File:** `computronium/experiment/schema/run_spec.py`
- Add `compatibility_matrix: dict[str, list[str]]` field
- Encode known invalid combos:
  - `instantaneous` + geometries with separate output_proj (attention, causal_transformer, spatial_lattice, tile, tile_mesh, conv) + `gradient` credit
  - `predictive_settling` + non-layered geometries
- Use in `ModelBasedPolicy` for smart sampling

### 1.3 Prune Quick-Verify Profile
**File:** `computronium/experiment/surface/cli.py`
- Focus quick-verify on `tile_mesh` × `{conflict_adaptive, routing}` × `{optical, memristive}`
- Reduce from 450 → ~50 cells, faster feedback

---

## 2. Stability Metrics Enhancement (Medium Impact)

### 2.1 Basin Stability Estimation
**File:** `computronium/experiment/kernel/evaluate.py`
- Multi-start perturbation: run settle from N random initial states
- Measure fraction converging to same fixed point
- Add `basin_stability` to payload

### 2.2 Transient Amplification Tracking
**File:** `computronium/experiment/execution/settle_operator.py`
- Track `||J_F^k||_2` during settle iterations
- Add `max_transient_amplification` to payload
- Correlate with generalization gap

### 2.3 Condition Number of Step Jacobian
**File:** `computronium/experiment/kernel/evaluate.py`
- Compute `κ(J_F) = σ_max / σ_min` at settled state
- Add `jacobian_condition_number` to payload

---

## 3. Predictive Settling Robustness (Medium Impact)

### 3.1 Adaptive Step Size from Lipschitz Constant
**File:** `computronium/ontology/dynamics/_dynamics.py`
- Estimate local Lipschitz constant during settle
- `step_size = min(0.5, 1.0 / L_local)` instead of fixed clamp
- Add gradient clipping for error correction step

### 3.2 Convergence Monitoring
- Add `settle_convergence_rate` metric
- Early exit if `||x_{t+1} - x_t|| < ε`

---

## 4. Convergence Curve Analysis (High Impact)

### 4.1 Early Stopping Detection
**File:** `computronium/experiment/kernel/evaluate.py`
- Detect plateau: `val_acc` change < 0.1% for 3 epochs
- Add `early_stopped_at_epoch` to payload
- Save compute on converged runs

### 4.2 Plateau Detection for Adaptive Epoch Budget
- If converged by epoch 3, don't run epochs 4-10
- Dynamic `batch_limit` based on convergence speed

### 4.3 Generalization Gap Tracking
- Track `train_acc - val_acc` per epoch
- Flag runs where gap > 10% (overfitting)

---

## 5. Bug Fixes (Critical)

### 5.1 JSON Report Generator Bug
**File:** `computronium/experiment/reporters/json.py` or report CLI
- Ablation JSON export shows `val_acc: 0%` for all records
- DB has correct values (e.g., 48.4%), export is broken
- Root cause: payload field mapping issue

### 5.2 Convergence Curve Schema
- Curve entries missing `epoch` field (only has train/val loss/acc)
- Fix serializer to include epoch number

---

## 6. Experiment Infrastructure (Medium Impact)

### 6.1 Default Maturation to Confirmed Configs
**File:** `experiment.sh` (DONE in TODO61)
- Default `--maturation-hours 2` targets 2 confirmed configs
- Quick test: `--maturation-hours 0.15 --ablation-hours 0.02`

### 6.2 Claim-Grade Profile Automation
**File:** `computronium/experiment/surface/cli.py`
- Add `--claim` flag: auto-run confirmed configs at 10 seeds × 20 epochs
- CEEC governance integration

### 6.3 Pareto Frontier Export
**File:** `computronium/experiment/surface/cli.py report`
- Export top-N configs as CSV/JSON for downstream use
- Include: coordinate, mean/std accuracy, walltime, params, ρ, learning curve summary

---

## 7. Physical Substrate Validation (Future)

### 7.1 Memristive Hardware Mapping
- Map `ortho_adam` update to memristive conductance updates
- IR-drop noise model validation

### 7.2 Optical Phase Encoding
- Map `tile_mesh` to optical phase/amplitude
- Coherent interference benefits

---

## Priority Order for Implementation

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| **P0** | Fix JSON report val_acc bug | 1h | Critical |
| **P0** | Add search priors to RUN_PROFILES | 30m | High |
| **P0** | Prune quick-verify profile | 30m | High |
| **P1** | Compatibility matrix in RunSpec | 2h | High |
| **P1** | Convergence curve early stopping | 2h | High |
| **P2** | Basin stability estimation | 4h | Medium |
| **P2** | Adaptive step_size predictive settling | 4h | Medium |
| **P2** | Pareto CSV/JSON export | 2h | Medium |
| **P3** | Claim-grade automation | 4h | Medium |
| **P3** | Memristive/optical hardware mapping | 1w | Future |

---

## Success Criteria for TODO62

| Criterion | Target |
|-----------|--------|
| Quick-verify runs in <30s | 50 cells → <30s wall |
| Search space pruned by 10x | 450 → 50 cells |
| JSON reports show correct val_acc | 0% bug fixed |
| Early stopping saves 30% compute | Converged runs stop at epoch 3-5 |
| Compatibility matrix blocks invalid combos | 0 GradientCredit shape mismatches |
| Pareto export works | CSV/JSON with top-N configs |

---

## Notes

- Full 2h maturation run (`./experiment.sh` on bare metal) will provide statistical rigor (5 seeds × 10 epochs)
- The improvements above can be implemented **in parallel** with the full run
- After TODO62, the system will be optimized for the confirmed winning configurations
- Physical substrate validation remains future work (requires hardware access)