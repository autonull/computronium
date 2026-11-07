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

## 🔧 BLOCKERS (Fix First — Both Crash Workers)

| ID | Bug | File | Fix | Test |
|---|---|---|---|---|
| **B1** | Validation crash: neuromorphic + non-temporal dynamics | `kernel/search_space.py` `iter_candidates()` | Filter invalid substrate×dynamics at proposal time | 0 crashes in 100 random samples |
| **B2** | Jacobian SVD: non-finite values | `packages/stability/src/stability/jacobian.py:118` | `torch.isfinite` guard + fallback/skip | 0 SVD crashes in 100 cells |
| **B3** | Shell `timeout` kills experiments mid-cell | `experiment_shallow.sh` line ~450 | Remove `timeout` wrapper; Python budget is source of truth | 0.5h run completes |

> **Fix B1+B2 together** (both in worker crash path), then B3. Pool restart on crash is lower priority — these fixes eliminate ~95% of crashes.

---

## 🎯 SESSION 1: Stabilize (1.5h)

```bash
# 1. Remove shell timeout (B3) — 15 min
# Edit experiment_shallow.sh: remove 'timeout' from cmd wrapper

# 2. Fix validation crash (B1) + SVD crash (B2) — 1h
# Edit kernel/search_space.py: add compatibility filter
# Edit packages/stability/src/stability/jacobian.py: add isfinite guard

# 3. Verify stabilized run — 15 min
./experiment_shallow.sh 0.1 --policy tpe --device cpu --workers 6 \
  --axes '{"credit":["gradient","homeostatic"],"update":["euclidean","lion"]}'
# Expect: 0 worker crashes, completes 0.1h budget
```

---

## 🧪 SESSION 2: Hypothesis Triage with Ladder (3h)

**Run all hypothesis axes WITH ladder promotion (--ladder) to get L1/L2 claim-grade data in one pass.**

```bash
# H1: Credit × Update on digits (5×6 = 30 combos, ladder: L0→L1→L2)
./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu --workers 6 \
  --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","mean_norm","muon","elastic_consolidation","natural_gradient"]}'

# H2: Dynamics × Substrate on digits (4×3 = 12 combos)
./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu --workers 6 \
  --axes '{"dynamics":["instantaneous","energy_minimization","lazy","error_predictive_coding"],"substrate":["digital","memristive","optical"]}'

# H3: Plasticity × Credit on digits (4×4 = 16 combos)
./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu --workers 6 \
  --axes '{"plasticity":["null","temporal_psi","rule_state","fast_weights"],"credit":["gradient","homeostatic","pc_alm","target_inversion"]}'
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

## 📋 WEEK 3-4: Sampler Comparison + Artifacts

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
| `64d42708` | Fix fidelity ladder promotion + claim eligibility query |
| `4e8a3563` | Move magic numbers to constants in wave.py |
| `9c37e25a` | Fix ProcessPoolExecutor start method to 'spawn' |
| `646f2457` | Update TODO83.md |
| `338` | Fix diagnostics default device = "auto" |
| `339` | Fix diagnostics CUDA check for auto device |
| `7b2a0534` | Add TODO84.md |

*Generated 2026-11-07. Supersedes TODO83.md.*