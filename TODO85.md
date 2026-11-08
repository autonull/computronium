# TODO85 — Fix & Perfect System Through Experiments (Post-TODO84)

**Status:** Supersedes TODO84. All blockers fixed, all tests pass (883/883).
**Strategy:** Run experiments → find what breaks → fix it → repeat. No publishing, no figures, no overhead.

---

## 🔄 THE LOOP (≤30 min per iteration)

```bash
# 1. RUN experiment (ladder, 0.2-0.5h, TPE, CPU, 4-6 workers)
./experiment_shallow.sh 0.3 --ladder --policy tpe --device cpu -w 4 --tasks digits \
  --axes '{"credit":["gradient","homeostatic","pc_alm"],"update":["euclidean","lion"],"substrate":["digital","ternary"],"plasticity":["null","rule_state"]}' \
  --skip-doctor

# 2. ANALYZE (30 sec) — look for:
#    - Worker crashes / timeouts
#    - Gate failures (which combos fail and why)
#    - Poor performance (which combos underperform)
#    - Missing combos (search space gaps)
uv run comp report --store experiments/experiment_$(ls -t experiments/*.duckdb | head -1).duckdb --format text
uv run comp coverage report --store experiments/experiment_$(ls -t experiments/*.duckdb | head -1).duckdb

# 3. FIX whatever broke (≤15 min)
#    - Worker crash → add deadline/timeout in wave.py
#    - Gate failure → fix compatibility / validation bug
#    - Poor performance → add hyperparam sweep / LR scaling
#    - Missing combos → fix search space filter

# 4. VERIFY fix with quick re-run (0.05h dry-run)
./experiment_shallow.sh 0.05 --ladder --policy tpe --device cpu -w 2 --tasks digits --skip-doctor --dry-run

# 5. COMMIT fix + experiment log
# 6. REPEAT with different axes
```

---

## 🎯 AXES TO ROTATE (Pick 2-4 per run)

| Category | Primitives | Why |
|----------|------------|-----|
| **Credit** | gradient, homeostatic, pc_alm, target_inversion, thermodynamic_contrast | Core learning signal |
| **Update** | euclidean, lion, muon, natural_gradient, mean_norm, elastic_consolidation | Optimization |
| **Substrate** | digital, ternary, memristive, optical | Hardware target |
| **Plasticity** | null, rule_state, temporal_psi, fast_weights | Adaptation |
| **Dynamics** | instantaneous, energy_minimization, lazy, error_predictive_coding, diffusion | State evolution |
| **Geometry** | feedforward, conv, spatial_lattice_3d, tile_mesh, ntm | Architecture |
| **Task** | digits, fashion, mnist, cifar | Benchmark |

**Rule:** Rotate to cover all combinations over time. Prioritize combos that failed last run.

---

## 🛠️ COMMON FIXES (Keep This List Updated)

| Symptom | Fix | File |
|---------|-----|------|
| Worker crash mid-cell | Add per-cell timeout + deadline check | `wave.py` |
| Ternary fails gate | LR scaling by weight_bits; straight-through estimator | `substrate.py`, `update.py` |
| Neuromorphic + non-temporal crashes | Compatibility filter in search space | `search_space.py` |
| Jacobian SVD NaN | isfinite guard + fallback | `jacobian.py` |
| Search space too large | Filter incompatible at harvest | `search_space.py` |
| TPE stuck on one combo | min_samples_per_combo=3 | `policy.py` |
| Planner yields 0 cells | Clear `_seen` between startup/wave | `learning_survey.py` |
| Gate false negative | Fix validation logic | `system.py` |
| CUDA multi-worker hang | Spawn + single GPU context | `wave.py` |

---

## 📝 EXPERIMENT LOG (Append Each Iteration)

| Run | Axes | Walltime | Crashes | Gate Failures | Worst Combo | Fix Applied |
|-----|------|----------|---------|---------------|-------------|-------------|
| 1 | credit: gradient,homeostatic; update: euclidean,lion; substrate: digital; plasticity: null | 223s | 0 | 0 | nca/instantaneous/gradient/euclidean (0.89) | Fixed geometry-task compatibility filter in search_space.py |
| 2 | credit: gradient,homeostatic; update: euclidean,lion; substrate: digital,ternary; plasticity: null,rule_state | 131s | 0 | 8 (ternary combos) | ternary/recurrent/instantaneous/rule_state | Added JointSystem __call__, training mode support |
| 3 | credit: gradient,thermodynamic_contrast; update: euclidean,lion; substrate: digital; plasticity: null; dynamics: instantaneous,energy_minimization | 124s | 0 | 0 | nca/instantaneous/gradient/euclidean (0.95) | 8 workers default, SKIP_DOCTOR=1 |
| 4 | credit: gradient,target_inversion,pepita; update: euclidean,muon; substrate: digital; plasticity: null; geometry: feedforward,recurrent,conv | 97s | 0 | 0 | feedforward/instantaneous/gradient/muon (0.99) | Muon update, spike_integration dynamics work |
| 5 | credit: gradient,temporal_trace; update: euclidean,lion; substrate: digital,neuromorphic; plasticity: null; dynamics: instantaneous,spike_integration | 61s | 0 | 0 | neuromorphic/feedforward/spike_integration/temporal_trace (0.16) | Neuromorphic + spike_integration works |

---

## 🚫 NO

- Paper figures
- Publishing artifacts
- Hypothesis backlogs
- Track A/B/C
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min

---

## 📦 BASELINE (TODO84 Complete)

| Commit | Fix |
|--------|-----|
| `3adf259e` | Planner _seen cleared between startup/wave |
| `3744b6da` | experiment_shallow.sh --skip-doctor |
| `9f07a70d` | All pre-existing test failures fixed |
| `3f51e370` | TPE min_samples_per_combo=3 |
| `131b528b` | Registry exports fixed |
| `60fe60cd` | Integration test regex |
| `d91cdfe9` | DiverseRandomPolicy test fixture |
| `eee8bc91` | Priors registry test expectation |

---

**Start:** Run experiment with 2-4 axes. Fix what breaks. Repeat.