# TODO84 — Stabilize, Validate, Evidence (Post-TODO83)

**Status:** Supersedes TODO83.md. Incorporates all fixes from 2026-11-06/07 + GPU/CPU behavior characterization.
**Machine:** 16 cores, RTX 3080 10 GB, 31 GB RAM, Linux 7.3.1-1-cachyos
**Codebase:** computronium main (commit `646f2457` → latest)

> **Key insight:** CPU parallel (spawn) is stable; CUDA multi-worker hangs on forkserver. Search space validation and Jacobian numerics are the main blockers to claim-grade evidence.

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

## 🔧 PRE-EXISTING BLOCKERS (Must Fix Before Full Runs)

### 1. Search Space Validation — Invalid Combos Crash Workers
**File:** `computronium/ontology/system.py` (~line 1044)
**Error:** `ValueError: Neuromorphic substrate requires temporal dynamics (spike_integration, energy_minimization, or diffusion), got 'error_predictive_coding'`
**Impact:** ~10-20% of sampled cells crash at validation (worker dies, pool restarts)
**Fix:** Filter invalid substrate×dynamics combos at search space level, not at validation time.

### 2. Jacobian SVD Numerical Instability
**File:** `computronium/packages/stability/src/stability/jacobian.py:118`
**Error:** `torch._C._LinAlgError: linalg.svd: The algorithm failed to converge because the input matrix contained non-finite values.`
**Impact:** Crashes during stability metrics computation for certain dynamics/geometry combos
**Fix:** Add NaN/Inf guards, fallback to approximate methods, or skip metrics for problematic configs.

### 3. Shell Script Timeout Kills Experiments Early
**File:** `experiment_shallow.sh` (line ~450)
**Issue:** `timeout 2400` wrapper kills process at 40 min regardless of Python budget enforcement
**Fix:** Remove external timeout; rely on Python's `budget_seconds` + 10 min grace only.

### 4. Multiprocessing Worker Crashes
**Symptom:** `Error: A process in the process pool was terminated abruptly while the future was running or pending.`
**Root cause:** Likely OOM or CUDA context issues in forked workers (even with spawn)
**Fix:** Add worker health monitoring, restart pool on crash, limit worker memory.

---

## 🎯 IMMEDIATE NEXT SESSION: Stabilization Sprint

| ID | Task | Time | Command / Action | Success Criteria |
|---|---|---|---|---|
| **S1** | Filter invalid substrate×dynamics in search space | 30 min | Edit `kernel/search_space.py` `iter_candidates()` to skip neuromorphic + non-temporal | 0 validation crashes in 100 random samples |
| **S2** | Guard Jacobian SVD against non-finite | 30 min | Edit `packages/stability/src/stability/jacobian.py` add `torch.isfinite` check + fallback | 0 SVD crashes in 100 cells |
| **S3** | Remove shell `timeout` wrapper | 15 min | Edit `experiment_shallow.sh` remove `timeout` command | 0.5h experiment runs to completion |
| **S4** | Verify stabilized run | 30 min | `./experiment_shallow.sh 0.5 --policy tpe --device cpu --workers 6` | Completes 0.5h budget, >30 PASS cells |

---

## 🧪 HYPOTHESIS TRIAGE (Week 2 — After Stabilization)

| ID | Experiment | Command | Success Criteria |
|---|---|---|---|
| **H1** | Credit × Update on digits | `./experiment_shallow.sh 0.5 --policy tpe --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","mean_norm","muon","elastic_consolidation","natural_gradient"]}' --device cpu` | 6+ cells at L1/L2, verdicts with `power_achieved` |
| **H2** | Dynamics × Substrate on digits | `./experiment_shallow.sh 0.5 --policy tpe --axes '{"dynamics":["instantaneous","energy_minimization","lazy","error_predictive_coding"],"substrate":["digital","memristive","optical"]}' --device cpu` | 6+ cells at L1/L2 |
| **H3** | Plasticity × Credit on digits | `./experiment_shallow.sh 0.5 --policy tpe --axes '{"plasticity":["null","temporal_psi","rule_state","fast_weights"],"credit":["gradient","homeostatic","pc_alm","target_inversion"]}' --device cpu` | 6+ cells at L1/L2 |
| **L2** | Fidelity ladder (claim-grade) | `./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu` | L1/L2 cells with 3/5 seed replication, claim-eligible > 0 |

> **Run sequentially on CPU (--device cpu --workers 6).** GPU single-worker OK for quick tests: `--device cuda --max-workers 1`

---

## 📊 GPU/CPU BEHAVIOR MATRIX (Measured 2026-11-07)

| Config | Workers | Result | Notes |
|--------|---------|--------|-------|
| `--device cuda` | 1 | ✅ Works | 3 cells/61s, CUDA 12.3, RTX 3080 |
| `--device cuda` | 2+ | ❌ Hangs | forkserver + CUDA context deadlock |
| `--device cpu` | 1-6 | ✅ Works | spawn method, ~50-60s/cell |
| `--device auto` | auto | ⚠️ Mixed | diagnostics was broken (fixed) |

**Rule:** CPU for parallel (multi-worker), GPU for single-worker only.

---

## 🔬 TECHNICAL DEBT & INSIGHTS

### Search Space Pruning
- Current: 5 substrates × 6 geometries × 7 dynamics × 7 plasticities × 7 credits × 7 updates = ~72k combos
- ~30% invalid (neuromorphic + non-temporal, quantum + classical-only, etc.)
- **Fix:** Add `valid_combinations()` filter in `search_space.py` using ontology compatibility matrix.

### Numerical Hygiene
- Jacobian SVD fails on ill-conditioned matrices from certain dynamics (error_predictive_coding, diffusion)
- Step size warnings: per-element-displacement updates (lion, muon, elastic_consolidation) get gradient-relative LR values
- **Fix:** Add `torch.nan_to_num` or skip metrics with `torch.isfinite(all) == False`.

### Multiprocessing Architecture
- `spawn` + `mp_context=mp.get_context("spawn")` works for CPU
- CUDA requires `torch.multiprocessing.set_start_method('spawn')` + explicit device assignment per worker
- **Future:** Consider `torch.distributed` for GPU multi-worker, or stick to CPU parallel.

### Budget Enforcement
- Python `budget_seconds` in `run_waves()` is the source of truth
- Shell `timeout` is redundant and harmful (kills mid-cell)
- **Fix:** Remove shell timeout entirely; add 10 min grace in Python if needed.

---

## 📋 WEEK 3-4: SAMPLER COMPARISON + ARTIFACTS (After H1-H3)

| ID | Task | Dependency | Time |
|---|---|---|---|
| **S1** | Static vs TPE identical budget | H1 done | 30 min |
| **A1** | Publish credit_vs_update comparison | H1 done | 30 min |
| **B5** | Gate calibration spec | — | 1 hr |
| **B6** | Drift detection alert | — | 30 min |
| **B7** | Metric coverage warnings | — | 30 min |
| **B8** | `capabilities` command | — | 30 min |
| **B9** | Sampler arc: delete `propose()` | — | 1 hr |
| **B10** | Validation codegen from registries | — | 2 hr |

---

## 📦 RELEASE 1.1 PREP (Week 5)

| ID | Task | Time |
|---|---|---|
| **R1** | `CONTRIBUTING.md` with run gates | 30 min |
| **R2** | Release notes (from `cf9356c5`..HEAD) | 30 min |
| **R3** | Tag `v1.1.0` | 5 min |
| **R4** | Clean checkout demo: `uv run comp run demo` | 10 min |

---

## 🚀 QUICK START FOR NEXT SESSION

```bash
# 1. Check ladder test (if still running)
uv run comp status --store /tmp/test_ladder2.duckdb

# 2. Fix validation crash (S1)
# Edit computronium/experiment/kernel/search_space.py
# Add filter for neuromorphic + non-temporal dynamics

# 3. Fix SVD crash (S2)  
# Edit packages/stability/src/stability/jacobian.py
# Add torch.isfinite guard before svdvals()

# 4. Remove shell timeout (S3)
# Edit experiment_shallow.sh: remove 'timeout' from cmd wrapper

# 5. Verify stabilized 0.5h run (S4)
./experiment_shallow.sh 0.5 --policy tpe --device cpu --workers 6 --axes '{"credit":["gradient","homeostatic"],"update":["euclidean","lion"]}'

# 6. When stable, run H1/H2/H3 sequentially
./experiment_shallow.sh 0.5 --policy tpe --device cpu --workers 6 --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","mean_norm","muon","elastic_consolidation","natural_gradient"]}'
# ... wait for completion ...
./experiment_shallow.sh 0.5 --policy tpe --device cpu --workers 6 --axes '{"dynamics":["instantaneous","energy_minimization","lazy","error_predictive_coding"],"substrate":["digital","memristive","optical"]}'
# ... wait for completion ...
./experiment_shallow.sh 0.5 --policy tpe --device cpu --workers 6 --axes '{"plasticity":["null","temporal_psi","rule_state","fast_weights"],"credit":["gradient","homeostatic","pc_alm","target_inversion"]}'
```

---

## 📝 COMMIT HISTORY (This Sprint)

| Commit | Message |
|--------|---------|
| `64d42708` | Fix fidelity ladder promotion + claim eligibility query |
| `4e8a3563` | Move magic numbers to constants in wave.py |
| `9c37e25a` | Fix ProcessPoolExecutor start method to 'spawn' |
| `646f2457` | Update TODO83.md: ladder test running, H1/H2/H3 queued for CPU |
| `338` | Fix diagnostics default device = "auto" |
| `339` | Fix diagnostics CUDA check for auto device |

*Generated 2026-11-07 from TODO83 fixes + GPU/CPU characterization. Supersedes TODO83.md.*