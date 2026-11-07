# TODO84 — Stabilize, Validate, Evidence (Post-TODO83)

**Status:** Supersedes TODO83.md. Incorporates all fixes from 2026-11-06/07 + GPU/CPU behavior characterization.
**Machine:** 16 cores, RTX 3080 10 GB, 31 GB RAM, Linux 7.3.1-1-cachyos
**Codebase:** computronium main (commit `7b2a0534` → latest)

> **Key insight:** CPU parallel (spawn) is stable; CUDA multi-worker hangs on forkserver. Two worker-crashing bugs block claim-grade evidence: search space validation (neuromorphic + non-temporal) and Jacobian SVD (non-finite values).

---

## ✅ COMPLETED (TODO83 Fixes)

| Fix | File | Commit |
|-----|------|--------|
| Claim eligibility query: `normalized_val_acc` → `normalized_metric` | `evidence/store/_queries.py:251` | `64d42708` |
| Ladder promotion expands to n_seeds replicates (L1=3, L2=5) | `wave.py:_run_ladder_promotion` | `64d42708` |
| Budget calculation accounts for replication factor | `wave.py:946` | `64d42708` |
| ProcessPoolExecutor forced to 'spawn' start method | `wave.py:739-748` | `9c37e25a` |
| Magic numbers → constants (`MAX_PROMOTE_CELLS=20`, `MAX_WAVE_CELLS=64`) | `wave.py:53-54` | `4e8a3563` |
| Diagnostics default device = "auto" (was "cpu") | `environment/diagnostics.py:241` | `338` |

---

## 🔧 BLOCKERS (Fix First — Both Crash Workers) ✅ FIXED

| ID | Bug | File | Fix | Test |
|---|---|---|---|---|
| **B1** | Validation crash: neuromorphic + non-temporal dynamics | `computronium/experiment/kernel/search_space.py` `iter_candidates()` | Added `_is_substrate_dynamics_compatible()` + `_is_geometry_dynamics_compatible()` defense-in-depth filters | Dry-run confirms neuromorphic+instantaneous filtered out |
| **B2** | Jacobian SVD: non-finite values | `packages/stability/src/stability/jacobian.py` | `torch.isfinite` guard on all SVD/eigenvalue paths; returns NaN metrics | Unit test: NaN/Inf Jacobians return NaN without crashing |
| **B3** | Shell `timeout` kills experiments mid-cell | `experiment_shallow.sh` line ~500 | Removed `timeout` wrapper; Python budget is source of truth | Dry-run completes without timeout interference |

> All three blockers fixed. Session 1 complete.

---

## 🎯 SESSION 1: Stabilize (1.5h) ✅ COMPLETE

```bash
# 1. Remove shell timeout (B3) — 15 min ✅
# Edit experiment_shallow.sh: remove 'timeout' from cmd wrapper

# 2. Fix validation crash (B1) + SVD crash (B2) — 1h ✅
# Edit computronium/experiment/kernel/search_space.py: add compatibility filter
# Edit packages/stability/src/stability/jacobian.py: add isfinite guard

# 3. Verify stabilized run — 15 min ✅
./experiment_shallow.sh 0.1 --policy tpe --device cpu --workers 6 \
  --axes '{"credit":["gradient","homeostatic"],"update":["euclidean","lion"]}'
# Expect: 0 worker crashes, completes 0.1h budget
```

---

## 🧪 SESSION 2: Hypothesis Triage with Ladder (3h) ✅ COMPLETE

**Run all hypothesis axes WITH ladder promotion (--ladder) to get L1/L2 claim-grade data in one pass.**

```bash
# H1: Credit × Update on digits (5×6 = 30 combos, ladder: L0→L1→L2) ✅ DONE
./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu --workers 6 \
  --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","mean_norm","muon","elastic_consolidation","natural_gradient"]}'
# Result: 62 cells evaluated (48 L0 + 9 L1 + 5 L2), 46 passed, 16 failed, ladder promotion worked, exit code 0

# H2: Dynamics × Substrate on digits (4×3 = 12 combos) ✅ COMPLETE
./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu --workers 6 \
  --axes '{"dynamics":["instantaneous","energy_minimization","lazy","error_predictive_coding"],"substrate":["digital","memristive","optical"]}'
# Fixed neuromorphic validation bug in system.py (_validate_neuromorphic_substrate_dynamics)
# Fixed budget enforcement in wave.py: added deadline cancellation of pending futures + per-cell timeouts
# Result: 78 cells evaluated (29 L0 + 48 L1 + 1 L2), 59 passed, 19 failed, 20 skipped, exit code 0, walltime 978s

# H3: Plasticity × Credit on digits (4×4 = 16 combos) ✅ COMPLETE
./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu --workers 6 \
  --axes '{"plasticity":["null","temporal_psi","rule_state","fast_weights"],"credit":["gradient","homeostatic","pc_alm","target_inversion"]}'
# Worker crash fixed by budget enforcement + per-cell timeouts in wave.py
# Result: 70 cells evaluated (13 L0 + 27 L1 + 30 L2), 66 passed, 4 failed, 30 skipped, exit code 0, walltime 396s
```

**Success criteria per run:** 6+ cells reach L1/L2 with 3/5 seed replication, `power_achieved` verdicts, claim-eligible > 0.

---

## 📊 GPU/CPU RULE (Measured 2026-11-07)

| Config | Workers | Result | Use For |
|--------|---------|--------|---------|
| `--device cuda` | 1 | ✅ Works | Quick single-worker tests |
| `--device cuda` | 2+ | ❌ Hangs | Never |
| `--device cpu` | 1-6 | ✅ Works | All parallel runs |

---

## 📋 WEEK 3-4: Sampler Comparison + Artifacts ✅ COMPLETE

| ID | Task | Dependency | Time | Status |
|---|---|---|---|---|
| **S1** | Static vs TPE identical budget | H1 done | 30 min | ✅ Done |
| **A1** | Publish credit_vs_update comparison | H1 done | 30 min | ✅ Done |
| **B5** | Gate calibration spec | — | 1 hr | ✅ Done |
| **B6** | Drift detection alert | — | 30 min | ✅ Done |
| **B7** | Metric coverage warnings | — | 30 min | ✅ Done |
| **B8** | `capabilities` command | — | 30 min | ✅ Done |
| **B9** | Sampler arc: delete `propose()` | — | 1 hr | ✅ Done |
| **B10** | Validation codegen from registries | — | 2 hr | ✅ Done |

> S1/A1 artifacts in `docs/artifacts/credit_vs_update_comparison.md`  
> B5 spec in `docs/specs/gate_calibration.md`  
> B6/B7 alerts in `computronium/experiment/monitoring/alerts.py`  
> B8 command: `comp capabilities {list,verify,matrix}`  
> B9: Planner protocol uses `__iter__` instead of `propose()`  
> B10 artifacts in `docs/generated/` via `python -m computronium.experiment.validation.generate`

---

## 📦 RELEASE 1.1 PREP (Week 5)

| ID | Task | Time |
|---|---|---|
| **R1** | `CONTRIBUTING.md` with run gates | 30 min |
| **R2** | Release notes (`cf9356c5`..HEAD) | 30 min |
| **R3** | Tag `v1.1.0` | 5 min |
| **R4** | Clean checkout demo | 10 min |

---

## 🔬 TECHNICAL DEBT (Defer Until Post-Evidence)

- Search space pruning: 72k combos → filter invalid at proposal (B1 partially addresses)
- Jacobian numerics: fallback SVD methods (B2 partially addresses)
- Worker pool restart on crash: lower priority after B1/B2
- CUDA multi-worker: requires `torch.distributed` rewrite

---

## 📝 COMMIT HISTORY

| Commit | Message |
|--------|---------|
| `HEAD` | B10: Validation codegen from registries |
| `05f8f620` | B10: Validation codegen from registries |
| `1d6b0c5f` | B9: Sampler arc - replace propose() with iterator protocol |
| `96f6dd79` | B6/B7/B8: Monitoring alerts + capabilities command |
| `4e29258e` | B5: Gate calibration spec from H1/H2/H3 failure analysis |
| `e62f3434` | S1+A1 complete: Static vs TPE comparison + credit_vs_update artifact |
| `088052cc` | Session 2 complete: All three hypothesis experiments (H1, H2, H3) pass with ladder promotion |
| `f3152134` | Fix budget enforcement in wave.py: deadline cancellation + per-cell timeouts |
| `ef12224e` | Fix neuromorphic substrate validation bug in _validate_neuromorphic_substrate_dynamics |
| `8f90baa5` | Fix B1/B2/B3: substrate-dynamics compat filter, Jacobian isfinite guards, remove shell timeout |
| `64d42708` | Fix fidelity ladder promotion + claim eligibility query |
| `4e8a3563` | Move magic numbers to constants in wave.py |
| `9c37e25a` | Fix ProcessPoolExecutor start method to 'spawn' |
| `646f2457` | Update TODO83.md |
| `338` | Fix diagnostics default device = "auto" |
| `339` | Fix diagnostics CUDA check for auto device |
| `7b2a0534` | Add TODO84.md |

*Generated 2026-11-07. Supersedes TODO83.md.*