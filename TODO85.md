# TODO85 — Fix & Perfect System Through Experiments (Post-TODO84)

**Status:** Supersedes TODO84. All blockers fixed, all tests pass (883/883).
**Strategy:** Run experiments → find what breaks → fix it → repeat. No publishing, no figures, no overhead.

## ✅ CURRENT STATE (Run 40)

**Multi-task experiments work end-to-end with full fidelity ladder.** `digits`, `fashion_mnist`, and `mnist` are measured and stored independently at L0→L1→L2.

Fixes landed this session:

| Defect | Fix | File |
|--------|-----|------|
| **Store collapsed tasks: dedup key was `(cell_key, seed, fidelity)`** — same coordinate on 3 tasks kept only the last record. This is why runs looked "all digits". | Task added to dedup key and lookup | `evidence/store/_transactions.py` |
| Task never cycled — planner used `tasks[0]` for the whole wave | Persistent `_task_cycle`/`_task_index` on `PolicyPlanner` | `wave.py` |
| Progress hid tasks — only every ~10th cell logged | Every cell logs `task=<id>` alongside axes | `wave.py` |
| `"digits"` hardcoded in 4 execution paths | Single `RunSpec.scheduled_tasks` property | `run_spec.py`, `wave.py` |
| Budget overrun 400s+ — cancelled cells kept running | Deadline calls `pool.kill_workers()` | `wave.py` |
| NaN auxiliary metric discarded a whole valid cell | Core metrics gate the cell; auxiliary NaNs dropped and reported | `kernel/evaluate.py` |
| **Ladder starved L1/L2 — 0 cells measured** | Stage budget = time actually left (L1 ≤60% of it); cells priced from their own measured walltime × epoch ratio; unaffordable cells/stages skipped instead of started then killed | `wave.py` |
| **energy_minimization 30 settle steps by default** | Default `max_steps=10`, the measured accuracy/cost optimum | `ontology/dynamics/_dynamics.py` |
| Stale neuromorphic sparsity test | Test configures `sparsity=0.95` instead of relying on a default deliberately changed to 0 | `tests/integration/test_energy_invariants.py` |

### Measured evidence (digits, L1 = 8 epochs, 1 seed)

| `max_steps` | walltime | val_acc |
|-------------|----------|---------|
| 5 | 5.0 s | 0.717 |
| **10** | **8.7 s** | **0.803** |
| 20 | 15.8 s | 0.781 |
| 30 | 22.7 s | 0.767 |

More settling costs time and does not improve accuracy. Note: the convergence
residual plateaus at ~1e-3, so the default `convergence_threshold=1e-4` can never
trigger — every settle runs the full `max_steps`. That is why cost is linear in
`max_steps`.

### GPU (RTX 3080, verified this session)

`--device cuda` works end-to-end (mnist cell val_acc 0.95). Every Triton family
compiles (`fa`, `pc`, `pcalm`, `snn`, `ff`, `pepita`, `hebbian`,
`complex_substrate`). But on these tiny cells GPU is **slower**, because the
settle loop is launch/latency-bound, not compute-bound:

| cell (mnist, L0, 1 epoch) | CPU | CUDA |
|---------------------------|-----|------|
| instantaneous | 22.3 s | 20.9 s |
| energy_minimization (30 steps) | 187 s | 299 s |

Use GPU for larger models/batches, not these. The Triton settle-family kernels are
not on the `energy_minimization` path; that path uses `SubstrateSettleKernel`
(plain torch matmuls) plus one GPU sync per settle step for the convergence check.

### Verified ladder (Run 40: 0.36h, 8 workers, 1800s budget)

```
L0: 38 cells in 894s  (7 credits, 5 updates, 8 substrates, 4 plasticities, 4 dynamics, 7 geometries, 3 tasks)
L1: 2 cells × 3 tasks = 6 cells → 6 seed-replicates each, budget 437s
L2: 6 cells × 5 seeds = 30 cells, budget 611s
74 evaluated, 0 failed, 1290s used

Per-task records: digits 44, fashion_mnist 15, mnist 15
```

### Verified ladder (Run 38: 0.12h, 8 workers, 432s budget)

```
L0: 21 cells in 197s
L1: 2 cells → 6 seed-replicates, 6 results, budget 141s   (was 0)
L2: 4 cells → 20 seed-replicates, 20 results, budget 159s (was 0)
47 evaluated, 0 failed, 306s used
```

---

## 🔄 THE LOOP (≤30 min per iteration)

```bash
# 1. RUN experiment (0.3-0.5h, TPE, CPU, 8 workers)
./experiment_shallow.sh 0.3 --policy tpe --device cpu --workers 8 \
  --tasks digits,fashion_mnist,mnist \
  --axes '{"credit":["gradient","homeostatic","pc_alm"],"update":["euclidean","lion"],"substrate":["digital","ternary"],"plasticity":["null","rule_state"]}' \
  --skip-doctor
# Add --ladder only when budget >= 0.5h

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

# 4. VERIFY fix with quick re-run (0.02h, no ladder — ladder starves L1/L2)
./experiment_shallow.sh 0.02 --policy tpe --device cpu --workers 2 --tasks digits,fashion_mnist,mnist --skip-doctor

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
| Only one task appears in results | `task_id` must be in the store dedup key | `evidence/store/_transactions.py` |
| Cell FAILs though training was fine | Gate on core metrics only; drop auxiliary NaNs | `kernel/evaluate.py` |
| Worker crash mid-cell | Add per-cell timeout + deadline check | `wave.py` |
| Run overruns its budget | `pool.kill_workers()` at deadline | `wave.py` |
| L1/L2 measure 0 cells | Size each stage from measured cell cost and time left; skip unaffordable stages | `wave.py` |
| energy_min cells too slow | Default `max_steps=10` (measured optimum), not 30 | `dynamics/_dynamics.py` |
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
| 21 | credit: gradient,pepita,thermodynamic_contrast,target_inversion,temporal_trace; update: euclidean,muon,lion,adam; substrate: digital,ternary,memristive,neuromorphic; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization,spike_integration; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca; tasks: digits,fashion_mnist,mnist | 426s | 0 | 0 | digital/recurrent/energy_min/thermo/muon (0.97) | 3 tasks declared; neuromorphic now works (0.9+); only digits tested (budget) |
| 22 | neuromorphic-focused: credit: gradient,pepita,thermodynamic_contrast,target_inversion,temporal_trace; update: euclidean,muon,lion; substrate: neuromorphic; plasticity: null,rule_state; dynamics: instantaneous,energy_minimization,spike_integration; geometry: feedforward,recurrent | 245s | 0 | 0 | neuromorphic/recurrent/energy_min/thermo/muon (0.97) | Neuromorphic fixed (sparsity 0.95→0); 0.9+ val_acc achieved |
| 23 | credit: gradient,pepita; update: euclidean,muon,lion; substrate: digital,ternary,memristive; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca; tasks: fashion_mnist,mnist | 25s | 0 | 0 | digital/feedforward/instantaneous/pepita/lion (0.84) | fashion_mnist + mnist tested; 0.84/0.95 baseline |
| 24 | credit: gradient,pepita,thermodynamic_contrast,target_inversion,temporal_trace; update: euclidean,muon,lion,adam,natural_gradient; substrate: digital,ternary,memristive,neuromorphic,analog,optical; plasticity: null,rule_state,fast_weights,temporal_psi; dynamics: instantaneous,energy_minimization,spike_integration,lazy; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca | 485s | 1 | 0 | digital/nca/instantaneous/temporal_psi/gradient/natural_gradient (tensor size mismatch) | 6 substrates; NCA+temporal_psi+natural_gradient tensor size bug |
| 25 | credit: gradient,pepita,thermodynamic_contrast; update: euclidean,muon,lion; substrate: digital,ternary,memristive,neuromorphic,analog,optical,sparse,complex; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca | 327s | 0 | 0 | analog/feedforward/instantaneous/pepita/muon (0.97) | 8/9 substrates work (only quantum missing); sparse/complex/analog/optical all pass |
| 26 | credit: gradient,pepita,thermodynamic_contrast; update: euclidean,muon,lion; substrate: digital,ternary,memristive,neuromorphic,analog,optical,sparse,complex; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization; geometry: feedforward,recurrent,tile_mesh | 260s | 0 | 0 | optical/recurrent/energy_min/grad/muon (0.97) | 8/9 substrates; non-layered geoms (conv/attention) require instantaneous; tile_mesh declared but not measured |
| 27 | credit: homeostatic,pc_alm,target_inversion,temporal_trace,random_projections; update: euclidean,muon; substrate: digital,ternary,memristive; plasticity: null,rule_state; dynamics: instantaneous; geometry: conv,attention,tile_mesh | 28s | 0 | 0 | memristive/tile_mesh/instantaneous/rule_state/random_projections/muon (0.80) | Non-layered geoms (conv/attention/tile_mesh) now work with compatible credits (homeostatic, pc_alm, target_inversion, temporal_trace, random_projections) |
| 28 | credit: gradient,thermodynamic_contrast; update: euclidean,muon; substrate: digital,ternary,memristive; plasticity: null,rule_state; dynamics: energy_minimization; geometry: feedforward,recurrent,tile_mesh | 78s | 0 | 0 | digital/feedforward/energy_min/thermo/muon (0.91) | energy_minimization works with layered geoms (feedforward, recurrent, tile_mesh) |
| 29 | credit: gradient,pepita; update: euclidean,muon; substrate: digital,ternary,memristive; plasticity: null,rule_state; dynamics: instantaneous; geometry: feedforward; tasks: fashion_mnist,mnist | 133s | 0 | 0 | digital/feedforward/pepita/muon (0.86) | fashion_mnist tested (0.86); mnist declared but not tested (budget) |
| 30 | credit: gradient,pepita; update: euclidean,muon; substrate: digital,ternary,memristive; plasticity: null,rule_state; dynamics: instantaneous; geometry: feedforward,conv,attention,tile_mesh; task: mnist | 142s | 0 | 0 | memristive/feedforward/grad/muon (0.96) | MNIST tested; non-layered geoms filtered (require compatible credits) |
| 31 | credit: homeostatic,pc_alm,target_inversion,temporal_trace,random_projections; update: euclidean,muon; substrate: digital,ternary,memristive; plasticity: null,rule_state; dynamics: instantaneous; geometry: conv,attention,tile_mesh; task: mnist | 30s | 2 | 0 | digital/tile_mesh/pc_alm/euclidean (0.19) | Non-layered geoms work with compatible credits (pc_alm passes; target_inversion/homeostatic fail on attention) |
| 32 | credit: gradient,pepita,thermodynamic_contrast; update: euclidean,muon,lion; substrate: digital,ternary,memristive; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization; geometry: feedforward,recurrent,tile_mesh; tasks: digits,fashion_mnist,mnist,kmnist | 210s | 0 | 0 | memristive/feedforward/pepita/muon (0.98) | 4 tasks declared; all cells on digits (task cycling issue); fast_weights + thermo works |
| 33 | credit: gradient,pepita,thermodynamic_contrast,target_inversion,temporal_trace; update: euclidean,muon,lion; substrate: digital,ternary,memristive,analog,optical,sparse,complex; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization; geometry: feedforward,recurrent,conv,attention,tile_mesh,nca; tasks: digits,fashion_mnist,mnist | 407s | 0 | 0 | optical/recur/energy_min/fast_weights/thermo/muon (0.94) | 7/9 substrates work; complex/tile_mesh/instant/rule_state/target_inv/lion (0.93); only digits tested (budget); NCA not measured |
| 34 | credit: gradient,pepita,thermodynamic_contrast; update: euclidean,muon; substrate: digital,ternary,memristive; plasticity: null; dynamics: instantaneous,energy_minimization; geometry: feedforward,recurrent; tasks: digits,fashion_mnist,mnist | 663s | 0 | 0 | ternary/feedforward/instant/null/grad/euclid (0.96) | TASK CYCLING FIXED: all 3 tasks evaluated (digits:6, fashion:3, mnist:2); 3 substrates, 2 geometries, 2 dynamics, 3 credits, 2 updates |
| 35 | credit: gradient,homeostatic,pc_alm,target_inversion,temporal_trace; update: euclidean,muon,lion; substrate: digital,ternary,memristive,analog,optical; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization; geometry: feedforward,recurrent,conv,attention,tile_mesh; tasks: digits,fashion_mnist,mnist | 900s | 0 | 1 (aux NaN) | ternary/recurrent/energy_min/rule_state/grad/lion (numerical) | 38/39 cells; tasks split 12 digits / 11 fashion / 10 mnist; found store dedup collapsing tasks + validator hiding the NaN |
| 36 | credit: gradient,pepita; update: euclidean,lion; substrate: ternary,memristive; plasticity: null,rule_state,fast_weights; dynamics: instantaneous,energy_minimization; geometry: feedforward,recurrent,conv; tasks: digits,fashion_mnist,mnist | 431s | 0 | 0 | memristive/feedforward/instant/lion (0.79) | Validator fix verified: 0 failures; energy_min cells ~7 min each (~53s/cell avg) |
| 37 | credit: gradient; update: euclidean; substrate: digital; plasticity: null; dynamics: instantaneous; geometry: feedforward; tasks: digits,fashion_mnist,mnist | 46s | 0 | 0 | same coord on all 3 tasks | Store dedup fix verified: 1 record per task (digits:1, fashion:1, mnist:1) |
| 38 | credit: gradient,pepita; update: euclidean,muon; substrate: digital,ternary; plasticity: null; dynamics: instantaneous,energy_minimization; geometry: feedforward; tasks: digits,fashion_mnist; ladder | 306s | 0 | 0 | digital/ff/energy_min/pepita/muon (0.31 L0) | Ladder fixed: L0 21 cells → L1 6 → L2 20, 0 killed (was 0/0). energy_min max_steps 30→10: 2.6× faster, higher accuracy (0.803 vs 0.767) |
| 39 | GPU check: credit: gradient; update: euclidean,muon; substrate: digital,ternary; plasticity: null; dynamics: instantaneous,energy_minimization; geometry: feedforward; tasks: digits,mnist | 108s | 0 | 0 | mnist digital/ff/instant/grad/euclid (0.950) | `--device cuda` works end-to-end. GPU slower on tiny cells (mnist energy_min 299s vs 187s CPU); all Triton families compile |
| 40 | credit: gradient,homeostatic,pc_alm,target_inversion,temporal_trace,pepita,thermodynamic_contrast; update: euclidean,muon,lion,adam,natural_gradient; substrate: digital,ternary,memristive,neuromorphic,analog,optical,sparse,complex; plasticity: null,rule_state,fast_weights,temporal_psi; dynamics: instantaneous,energy_minimization,spike_integration,lazy; geometry: feedforward,conv,attention,tile_mesh,ntm,recurrent,nca; tasks: digits,fashion_mnist,mnist; ladder | 1290s | 0 | 0 | digital/ff/instant/null/grad/euclid (0.96 L2) | Full ladder with 7 credits, 5 updates, 8 substrates, 4 plasticities, 4 dynamics, 7 geoms, 3 tasks: L0 38 cells → L1 6 (3 task-cycled ×2 cells) → L2 30 (6 cells ×5 seeds). All 3 tasks measured at all fidelities (digits:44, fashion:15, mnist:15 records) |

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

**Start:** Multi-task ladder is live. Run wide axes with `--tasks digits,fashion_mnist,mnist --ladder`. Fix what breaks. Repeat.

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
| Multi-task cycling | **FIXED** | Planner cycle + store dedup key | `PolicyPlanner` assigns tasks from `scheduled_tasks`; `RecordStore` dedup key now includes `task_id` (was collapsing 3 tasks into 1 record) |
| NaN auxiliary metric fails whole cell | **FIXED** | Core-metric gate | Only `loss`/`val_acc`/`train_acc`/`accuracy` NaNs fail a cell; auxiliary NaNs are dropped and reported |

**Priority for next session:**
1. Ladder follow-up: the L0 share is 50% flat. If L0 exhausts its cell space early, the unused time is already available to L1/L2; consider shrinking L0's share for small spaces.
2. energy_minimization: default is now 10 steps. The dead convergence knob (`threshold=1e-4` vs a ~1e-3 residual floor) should either be raised to a reachable value or documented as "step budget only".
3. GPU: only worth it for larger models/batches. The settle loop syncs per step; moving the convergence check off the hot path (or batching the horizon with `compiled=True`) is the prerequisite for GPU speedup. Benchmark a hidden=256, batch=256 cell before claiming any GPU win.
4. Then remaining primitive gaps: neuromorphic + spike_integration, quantum substrate, temporal_psi plasticity, graph/causal_transformer/spatial_lattice/ntm geometries, diffusion/error_predictive_coding/lazy/predictive_settling/pc_alm dynamics, adam/natural_gradient/elastic_consolidation updates.