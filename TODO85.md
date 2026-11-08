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
| Ternary + energy_minimization crashes | TWN ternary thresholding (0.7*E[|W|]); energy uses kernel.effective_weights() | `substrate.py`, `_dynamics.py` |
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
| 6 | credit: gradient,homeostatic; update: euclidean,lion; substrate: digital; plasticity: null | 130s | 0 | 0 | nca/instantaneous/gradient/euclid (0.96) | Fixed tile/NTM/attention input flattening; geometry coverage 5→9/11 |
| 7 | credit: gradient,thermodynamic_contrast,pepita; update: euclidean,muon,lion; substrate: digital,ternary; plasticity: null; dynamics: instantaneous,energy_minimization | 124s | 6 | 6 (ternary+energy_min+thermo/pepita) | ternary/recur/energy_min/thermo/lion | Ternary substrate validation needs work |
| 8 | credit: gradient,thermodynamic_contrast; update: euclidean,muon; substrate: digital; plasticity: null,rule_state; dynamics: instantaneous,energy_minimization | 174s | 0 | 0 | recur/energy_min/rule_state/grad/muon (0.97) | rule_state + muon works |
| 9 | credit: gradient,thermodynamic_contrast,pepita; update: euclidean,lion,muon; substrate: digital,ternary; plasticity: null; dynamics: instantaneous,energy_minimization | 385s | 0 | 0 | ternary/feedforward/energy_min/thermo/euclid (0.11) | Fixed ternary STE quantization (TWN scaling) + energy computation with effective weights |
| 10 | credit: gradient,thermodynamic_contrast,temporal_trace; update: euclidean,lion; substrate: digital,neuromorphic; plasticity: null,rule_state; dynamics: instantaneous,spike_integration | 170s | 0 | 0 | neuromorphic/feedforward/spike_integration/temporal_trace (0.09) | Neuromorphic + rule_state + spike_integration works |
| 11 | credit: gradient,homeostatic,pc_alm; update: euclidean,lion; substrate: digital,ternary; plasticity: null,rule_state; dynamics: instantaneous,energy_minimization | 334s | 0 | 0 | ternary/recurrent/energy_min/pc_alm/euclid (0.10) | Homeostatic + PC-ALM credit with ternary/energy_minimization works |
| 12 | credit: gradient,homeostatic,pc_alm; update: euclidean,lion; substrate: digital,ternary,neuromorphic,memristive; plasticity: null,rule_state; dynamics: instantaneous,energy_minimization,spike_integration; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca | 269s | 0 | 0 | ntm/grad/lion (0.97) | Memristive + neuromorphic work; conv/attention/tile_mesh/ntm covered; spike_integration filtered (needs temporal_trace/target_inversion credit) |
| 13 | credit: temporal_trace,target_inversion; update: euclidean,lion; substrate: neuromorphic,memristive; plasticity: null,rule_state; dynamics: spike_integration,energy_minimization,instantaneous; geometry: feedforward,recurrent | 161s | 0 | 0 | memristive/feedforward/spike_integration/null/target_inversion/lion (0.49) | Neuromorphic + spike_integration works with temporal_trace/target_inversion credit |
| 14 | credit: gradient,thermodynamic_contrast,pepita; update: euclidean,muon,lion; substrate: digital,ternary; plasticity: null,rule_state; dynamics: instantaneous,energy_minimization; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca | 315s | 0 | 0 | feedforward/grad/muon (0.99) | Muon works; pepita works; ternary+energy_min+thermo/pepita works |
| 15 | credit: gradient,homeostatic,pc_alm,temporal_trace,target_inversion,pepita,thermodynamic_contrast; update: euclidean,muon,lion; substrate: digital,ternary,neuromorphic,memristive; plasticity: null,rule_state; dynamics: instantaneous,energy_minimization,spike_integration; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca | 423s | 0 | 0 | feedforward/grad/muon (0.98) | All 4 substrates + spike_integration + 7 credits work; coverage: 70% credit, 44% substrate, 55% geometry |
| 16 | credit: gradient,temporal_trace,target_inversion,local_goodness,local_contrastive,random_projections; update: euclidean,muon,lion,adam,natural_gradient; substrate: digital,ternary,analog,optical,sparse,complex,quantum; plasticity: null,rule_state,fast_weights,temporal_psi; dynamics: instantaneous,energy_minimization,spike_integration,diffusion,predictive_settling,error_predictive_coding,lazy; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca,graph,spatial_lattice,causal_transformer | 333s | 1 | 0 | sparse/feedforward/energy_minimization/rule_state/local_goodness/adam (numerical) | 7/9 substrates work; sparse+energy_min+rule_state+local_goodness+adam numerical instability (passed on retry) |
| 17 | credit: gradient,homeostatic,pc_alm,pepita,thermodynamic_contrast; update: euclidean,muon,lion; substrate: digital,ternary,memristive,neuromorphic; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization,spike_integration; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca; tasks: digits,fashion_mnist | 399s | 0 | 0 | memristive/feedforward/grad/muon (0.98) | fast_weights + thermodynamic_contrast works; neuromorphic+energy_min+pepita works; 2 tasks |
| 18 | credit: gradient,homeostatic,pc_alm,pepita,thermodynamic_contrast,target_inversion,temporal_trace; update: euclidean,muon,lion,adam,natural_gradient,mean_norm,elastic_consolidation; substrate: digital,ternary,memristive,neuromorphic,analog,optical; plasticity: null,rule_state,fast_weights,temporal_psi; dynamics: instantaneous,energy_minimization,spike_integration,lazy; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca | 391s | 1 | 0 | digital/nca/instantaneous/temporal_psi/gradient/adam (tensor size mismatch) | 6 substrates work; temporal_psi + NCA + adam tensor size bug |
| 19 | credit: gradient,pepita; update: euclidean,muon,lion; substrate: digital,ternary,memristive; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca | 210s | 0 | 0 | digital/feedforward/instantaneous/rule_state/gradient/muon (0.99) | fast_weights + pepita works; param_count shown; L0→L1→L2 complete |
| 20 | credit: gradient,pepita,thermodynamic_contrast; update: euclidean,muon,lion; substrate: digital,ternary,memristive; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca; tasks: digits,fashion_mnist | 343s | 0 | 0 | digital/feedforward/instantaneous/rule_state/gradient/muon (0.98) | 2 tasks declared; all cells on digits (budget); fast_weights + thermo works |

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

---

## 🔍 FIXABLE vs FILTERED (From Runs 1-9)

| Combo | Status | Fix Type | Notes |
|-------|--------|----------|-------|
| Tile/Tile_mesh + vision | **FIXED** | Input flattening (3 lines) | Works now, 0.96 accuracy |
| NTM + vision | **FIXED** | Input flattening in forward_with_intermediates | Works now |
| Attention + vision | **FIXED** | Input flattening in forward_with_intermediates | Works now |
| Graph + vision | Filtered | No edge_index from vision data | Needs k-NN graph construction or patch-graph |
| Causal_transformer + vision | Filtered | Expects 1D tokens, gets 3D images | Needs ViT-style patch embedding |
| Ternary + energy_minimization + thermodynamic_contrast/pepita | **FIXED** | TWN ternary quantization + substrate-effective energy | Was: straight-through estimator broke energy_minimization settle. Fix: proper ternary thresholding (0.7*E[|W|]) + energy uses kernel.effective_weights() |

**Priority for next session:** Test neuromorphic + spike_integration, memristive substrate, and rule_state plasticity. Expand geometry coverage (conv, attention, tile_mesh).