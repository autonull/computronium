# Release Notes — v1.1.0

**Date:** 2026-11-07  
**Base:** `cf9356c5` → `238d2efa` (14 commits)  
**Theme:** Stabilize, Validate, Evidence

---

## Summary

This release completes the post-TODO83 stabilization sprint and delivers claim-grade experimental evidence across three hypothesis axes (H1, H2, H3) with fidelity ladder promotion (L0→L1→L2). All worker-crashing blockers are fixed. Week 3-4 artifacts (sampler comparison, gate calibration, monitoring alerts, capabilities command, validation codegen) are complete.

---

## 🎯 Major Accomplishments

### Session 1: Stabilization (Complete)
Fixed three worker-crashing bugs that blocked claim-grade evidence:
- **B1**: Validation crash on neuromorphic + non-temporal dynamics — added defense-in-depth compatibility filters in `search_space.py`
- **B2**: Jacobian SVD non-finite values — added `torch.isfinite` guards in `stability/jacobian.py`
- **B3**: Shell `timeout` killing experiments mid-cell — removed timeout wrapper, Python budget is now source of truth

Additional fixes:
- ProcessPoolExecutor forced to `spawn` start method (fixes CUDA forkserver hangs)
- Fidelity ladder promotion now expands to n_seeds replicates (L1=3, L2=5)
- Budget calculation accounts for replication factor
- Magic numbers → constants (`MAX_PROMOTE_CELLS=20`, `MAX_WAVE_CELLS=64`)
- Diagnostics default device = "auto"

### Session 2: Hypothesis Triage with Ladder (Complete)
All three hypothesis axes executed with ladder promotion (L0→L1→L2) in single passes:

| Experiment | Axis | Combos | Cells (L0/L1/L2) | Passed | Failed | Skipped | Walltime |
|------------|------|--------|------------------|--------|--------|---------|----------|
| **H1** | Credit × Update | 5×6=30 | 48/9/5 = 62 | 46 | 16 | — | ~1200s |
| **H2** | Dynamics × Substrate | 4×3=12 | 29/48/1 = 78 | 59 | 19 | 20 | 978s |
| **H3** | Plasticity × Credit | 4×4=16 | 13/27/30 = 70 | 66 | 4 | 30 | 396s |

**Key Finding (H1):** Only `gradient × euclidean` reaches claim grade (L2, 5 seeds, 1.0000 mean val_acc). All other 29 combos fail to reach L2 within 0.5h budget.

### Week 3-4: Artifacts & Infrastructure (Complete)

| ID | Deliverable | Location |
|----|-------------|----------|
| **S1** | Static vs TPE identical budget comparison | `docs/artifacts/credit_vs_update_comparison.md` |
| **A1** | Credit × Update comparison artifact | `docs/artifacts/credit_vs_update_comparison.md` |
| **B5** | Gate calibration specification | `docs/specs/gate_calibration.md` |
| **B6** | Drift detection alerts | `computronium/experiment/monitoring/alerts.py` |
| **B7** | Metric coverage warnings | `computronium/experiment/monitoring/alerts.py` |
| **B8** | `comp capabilities {list,verify,matrix}` command | `computronium/cli/commands/capabilities.py` |
| **B9** | Sampler arc: `propose()` → `__iter__` protocol | `computronium/experiment/wave.py` |
| **B10** | Validation codegen from registries | `docs/generated/` |

---

## 🔧 Bug Fixes

| Commit | Fix |
|--------|-----|
| `8f90baa5` | B1/B2/B3: substrate-dynamics compat filter, Jacobian isfinite guards, remove shell timeout |
| `ef12224e` | Neuromorphic substrate validation bug in `_validate_neuromorphic_substrate_dynamics` |
| `f3152134` | Budget enforcement: deadline cancellation + per-cell timeouts in `wave.py` |
| `9c37e25a` | ProcessPoolExecutor start method = 'spawn' |
| `64d42708` | Fidelity ladder promotion + claim eligibility query |
| `4e8a3563` | Magic numbers → constants in `wave.py` |
| `338` / `339` | Diagnostics default device = "auto", CUDA check for auto |

---

## 📦 New Features

### `comp capabilities` Command (B8)
```bash
uv run comp capabilities list           # List all registered capabilities
uv run comp capabilities list --kind substrate --stage gate1
uv run comp capabilities verify         # Verify coverage per stage
uv run comp capabilities matrix         # Kind × Stage matrix
```

### Monitoring Alerts (B6/B7)
```bash
# Run-time and post-run alerting for:
# - Gate verdict drift (FAIL rate > 25%)
# - Metric coverage degradation (non-finite > 5%)
# - Dtype mismatch detection (BFloat16/Float, Bool tensors)
# - Budget enforcement violations
uv run python -m computronium.experiment.monitoring.alerts <store_path> [run_id]
```

### Validation Codegen (B10)
Generates machine-readable validation artifacts from registries:
```
docs/generated/
├── availability_predicates.json
├── credit_update_compat.json
├── geometry_dynamics_compat.json
├── substrate_dynamics_compat.json
├── capabilities.json/md
├── axes.json/md
├── objectives.json/md
├── stages.json/md
├── policies.json
├── priors.json
├── constraints.json
├── void_constraints.json
├── cli_flag_tables.json
├── compatibility_matrix.json
├── IMPLEMENTATION_MATRIX.md
└── validation_types.ts
```
Run: `uv run python -m computronium.experiment.validation.generate`

### Sampler Protocol Modernization (B9)
- Planner protocol now uses `__iter__` instead of `propose(n)`
- `StaticPlanner` and `PolicyPlanner` implement `__iter__` yielding `(Coordinate, Schedule)`
- Legacy `propose()` retained for backward compatibility
- Wave loop uses `iter(planner)` with `_set_wave_size(n)` to control yield count
- Enables continuous streaming proposals instead of batch requests

---

## 📊 Experimental Evidence

### GPU/CPU Rule (Measured)
| Config | Workers | Result | Use For |
|--------|---------|--------|---------|
| `--device cuda` | 1 | ✅ Works | Quick single-worker tests |
| `--device cuda` | 2+ | ❌ Hangs | Never |
| `--device cpu` | 1-6 | ✅ Works | All parallel runs |

### Claim-Grade Baseline
**`gradient × euclidean`** is the only combination with replicated L2 evidence (5 seeds, 1.0000 mean val_acc). Use as reference for all future comparisons.

### Known Failure Modes (from Gate Calibration B5)
- **Numerical failures** (~70%): Step size overshoot on `per_element_displacement` rules + substrate issues
- **Dtype mismatches** (~15%): BFloat16/Float mixing in homeostatic/target_inversion credit
- **Bool tensor ops** (~10%): Boolean masks used in matmul without float conversion
- **Type cast errors**: Output type mismatch in `elastic_consolidation` update

---

## 📝 Documentation Updates

- `CONTRIBUTING.md` — Added with run gates, development workflow, testing tiers
- `docs/artifacts/credit_vs_update_comparison.md` — H1 ladder + S1 static vs TPE comparison
- `docs/specs/gate_calibration.md` — Failure taxonomy, thresholds, calibration actions
- `docs/generated/` — 18 validation artifacts from registries
- `TODO84.md` — Updated to track progress through Release 1.1 prep

---

## 🔬 Technical Debt (Deferred)

- Search space pruning: 72k combos → filter invalid at proposal (B1 partially addresses)
- Jacobian numerics: fallback SVD methods (B2 partially addresses)
- Worker pool restart on crash: lower priority after B1/B2
- CUDA multi-worker: requires `torch.distributed` rewrite

---

## 📋 Migration Notes

### Breaking Changes
None. All changes are backward-compatible:
- Sampler `propose()` retained as legacy wrapper
- New alerts are opt-in
- Validation codegen is additive

### Deprecations
- `Planner.propose(n)` → use `iter(planner)` with `planner._set_wave_size(n)`

---

## ✅ Verification

```bash
# Gate 0: Environment sanity
uv run comp doctor
uv run comp run demo --dry-run

# Gate 1: Ladder smoke test (~2 min)
./experiment_shallow.sh 0.05 --ladder --device cpu --workers 2 \
  --axes '{"credit":["gradient"],"update":["euclidean"]}'

# Gate 2: Single-axis sweep (~15 min)
./experiment_shallow.sh 0.2 --ladder --device cpu --workers 4 \
  --axes '{"credit":["gradient","homeostatic"],"update":["euclidean","lion"]}'
```

---

## 👥 Contributors

Automated stabilization & evidence collection pipeline.

---

*Generated from commits `cf9356c5`..`238d2efa`*