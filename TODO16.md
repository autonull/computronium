# Computronium: Unified Execution Plan — Final

## Guiding Doctrine

- **Composition before invention.** No new primitives. Compose existing ones across untouched axes.
- **Prediction before measurement.** Every cell gets a pre-registered prediction derived from the I(C,U) law.
- **Autopsy before training.** ≤5-min pure-tensor diagnostics on frozen weights precede any training run.
- **Harvest, don't train-longer.** EMA/best-snapshot evaluation is the default instrument.
- **Checkpoint first, diagnose second.** Never retrain to re-run a diagnostic.
- **Exploit discovered principles.** Transport graph, peak-then-memorize, weight-sharing law, mask-entropy law — these are design tools now.
- **Recorded-source verdicts count.** If a measurement exists in a log, cite it. Do not re-run.
- **Feasibility-isolation ladder before any training.** Representation → Wiring → Horizon → Optimizer.
- **CPU-only.** GPU is ~3× slower at probe scale (kernel-launch bound per §11.6).

---

## Cost-Reduction Principles

| Strategy | Savings |
|---|---|
| Parse existing logs for I(C,U) table. Zero new compute. | ~2h eliminated |
| Cite recorded measurements (PEPITA×Muon 0.306, LEMMA alignment, etc.). | ~30 min eliminated |
| Probe-free EMA harvest (`--probe-free`) as default instrument. | 40% per-cell |
| Shorter budgets where peak is known. Depth-100 peaks at batch 30 → run 40 batches. NTM recall peaks by 4800 → cap there. | 60% on deep cells |
| 1 seed for screens; 3 seeds only for promotion. | 3× on screens |
| Background anything >5 min. `nohup … > logs/<name>.log 2>&1 &`, poll ≤2 min. | Unblocks depth-100, NTM 8000 |
| Parallelize. OMP_NUM_THREADS=2 per process; max 3 concurrent. | 2–3× walltime |
| Distill-init for recurrent/iterative substrates. 5s init replaces from-scratch. | 10–100× |
| Pre-registered lr tables instead of screens. | Avoids 3× screen overhead |
| Assert `batches_seen ≥ budget` inside every training loop. | Prevents silent truncation |

---

## Phase 0 — Infrastructure Lock (Session 1, ~45 min)

### 0.1 Promote Harvest Instrument into `SystemTrainer` (~15 min)

**What:** Add `harvest_mode: Literal["ema", "best_snapshot", None]` to `SystemTrainerConfig`.

**Implementation:**
- `harvest_mode="ema"`: streaming EMA of weights (decay 0.99), evaluated once at end.
- `harvest_mode="best_snapshot"`: track best val metric every N batches; restore best at end.
- Default: `None` (backward-compatible).

**Test:** `tests/integration/test_harvest_trainer.py` — depth-32, 150 batches, assert EMA final ≥ max-snapshot. Assert `harvest_mode=None` produces identical results to current behavior. **~2 min.**

### 0.2 I(C,U) Data Extraction Script (~10 min)

**What:** `scripts/analysis/harvest_icu_table.py` parses existing logs into `data/icu_measurements.csv`.

**Sources (all existing, zero new compute):**
- `logs/w1_credit_ladder*.log` — MLP: bp/ff/pepita/rp × euclid/muon/ortho/lion
- `logs/w1_lattice_ladder.log` — lattice: bp/ff/pepita × euclid/muon/ortho
- `logs/w8_nca_verdict.log` — NCA: bptt/local × euclid/muon
- `logs/w8_ortho_screen.log` — NCA: local × ortho_adam
- `logs/w8_ntm_promo.log` — NTM: local × adam/muon
- `logs/w9_family_depth_grid.log` — EqProp/FF depth profiles
- `pepita_faithful_replication` outputs — PEPITA × adam/muon
- `d50_autopsy` outputs — depth 20–100 under harvest
- `w7_stdp_muon.py` output — STDP × muon
- `w0_tf_local_optimizers` logs — transformer: local_contrastive × 5 optimizers

**Output schema:**
```python
@dataclass
class ICURecord:
    credit: str          # "fa", "pepita", "ff", "local_contrastive", "lemma", "stdp", "thermo"
    update: str          # "euclid", "adam", "muon", "ortho_adam", "lion"
    geometry: str        # "mlp", "transformer", "lattice", "nca", "ntm"
    depth: int
    width: int
    task: str            # "mnist", "fashion", "lm", "copy", "recall", "ordinary"
    seed: int
    accuracy: float
    interaction_i: float
    mechanism_class: str  # "exact_gradient", "projected_pseudo", "goodness_contrast", "hebbian"
    plasticity: str      # "null", "routing", "fast_weight"
    status: str          # "promoted", "boundary", "open", "reopened"
```

**Estimated rows:** ~150–200.

### 0.3 Recipe-Card Registry + Inertness Guard (~15 min)

**What (recipe cards):** `computronium/analysis/recipe_cards.py` — static dict from existing findings:

```python
RECIPE_CARDS = {
    ("fa_family", "muon"): {"status": "rescue", "delta": +0.46, "geometries": ["mlp", "lattice"]},
    ("fa_family", "ortho_adam"): {"status": "rescue_sharp", "delta": +0.36, "edge": "1e-4 to 1e-3"},
    ("pepita", "adam"): {"status": "home", "parity": 0.884, "boundary": "classification_only"},
    ("pepita", "muon"): {"status": "harm", "delta": -0.14},
    ("lemma", "*"): {"status": "closed", "mechanism": "alignment_noise"},
    ("stdp", "*"): {"status": "closed", "mechanism": "no_error_term"},
    ("local_contrastive", "muon"): {"status": "boundary", "mechanism": "gate_shutdown"},
    ("eqprop", "*"): {"status": "peak_collapse", "harvest_required": True},
    ("ff", "*"): {"status": "depth_wall_d2", "harvest_limited": True},
}
```

**What (inertness guard):** Add 5-line warning to `RandomProjectionsCredit.compute_pseudo_gradient` when the layered FA contract returns all-zeros (prevents silent no-op runs; §7 Session 7 queued item). ~5 min.

**Register C note:** Geometry-is-not-family-portable documentation and per-family constructor registry deferred to post-sprint unless a cross-family grid is attempted.

---

## Phase 1 — Ship Proven Results (Session 1–2, ~35 min)

### 1.1 Depth Headline Demo (Gallery Row D18) (~5 min)

**What:** Wrap existing `d50_autopsy.py --probe-free` as gallery demo D18.

**How:** `tests/integration/test_demo_depth_harvest.py`
- Arms: depth-{32, 50} × {final_step, ema_harvest}
- Architecture: 784→128×N→10, mupc init, residual, OrthoAdam
- Budget: 150 batches, probe-free EMA
- Assert: EMA ≥ final for all depths; depth-50 EMA ≥ 0.75
- Gallery lock re-pinned (24 figures)

**Cost:** ~3 min (2 cells × 150 batches × ~150s each, parallel with OMP=2).

### 1.2 NTM Local-Credit Demo (Gallery Row D19) (~5 min)

**What:** Wrap existing `w8_ntm_copy.py` as gallery demo D19.

**How:** `tests/integration/test_demo_ntm_local.py`
- Arms: bptt control + local3 (r6 recipe), 3000 steps, width 16
- Assert: local ≥ 0.84, bptt ≥ 0.97
- Frame: transport graph > memory machinery (§17.9)

**Cost:** ~5 min (2 cells × 2.5 min, parallel).

### 1.3 PEPITA Breadth (~4 min/cell, background)

**What:** PEPITA on CIFAR-10 (flattened 3072→256→10) and Cora (1433→64→7).

**How:** `pepita_faithful_replication.py --task=cifar10` and `--task=cora`. 3 seeds each.

**Pre-registered:**
- CIFAR-10: PEPITA ≥ 0.55 (fixed-input classification; modulation works)
- Cora: PEPITA ≥ 0.65 (fixed-input node features; modulation works)
- If either fails: boundary is "high-dimensional input," not "autoregressive." Record mechanism.

**Cost:** ~3 min/cell × 6 cells = ~18 min total. **Background** (3 parallel pairs, OMP=2).

### 1.4 NTM Copy 3-Seed @ 8000 (~5 min/cell, background)

**What:** Firm the 0.958 single-seed result (§17.3).

**How:** `w8_ntm_copy.py --arm=local3 --steps=8000 --width=16 --seed={0,1,2}`.

**Pre-registered:** mean ≥ 0.93, all seeds ≥ 0.90. If any seed < 0.85: record as seed-sensitive, not boundary.

**Cost:** ~5 min/cell × 3 = **background**, poll every 2 min.

### 1.5 LSTM-Alone No-Memory Control (~2 min/cell, background)

**What:** §17.11 prerequisite. Run `w8_ordinary_task.py --arm=lstm` (already implemented) on the ordinary-task baseline to gate transport-graph claims.

**Pre-registered:** LSTM-alone ≈ bptt ≈ hebbian on MNIST rows (memory superfluous). If LSTM-alone < 0.80: memory IS needed on this task; re-interpret §17.9.

**Cost:** ~2 min/cell × 3 seeds = ~6 min. **Background.**

---

## Phase 2 — P-Axis Frontier Probes (Session 2–3, ~45 min)

All four probes run in parallel (OMP=2, 2 at a time).

### 2.1 FastWeightPlasticity × NTM Ordinary Task (~3 min/cell)

**What:** ψ = fast-weight matrix modulating NTM controller hidden activity on the §17.5 ordinary-task baseline.

**Critical design decision:** The FastWeight arm **keeps the autograd graph through h into ψ** (bptt variant, matched to §17.9's Hebbian arm). Zero-history FastWeight is a separate, harder cell deferred. This is NOT a local-credit rescue — it tests whether learned ψ projections add value over fixed Hebbian writes when the transport graph is intact.

**How:** Extend `w8_ordinary_task.py` with `--arm=fastweight`:
- ψ modulates controller hidden: `h_mod = h + ψ @ h`
- ψ written by Hebbian rule: `ψ ← 0.95·ψ + lr·outer(h_pre, h_post)`
- ψ decays at episode boundary (lifecycle: `fast_plastic`)
- Autograd graph preserved through h into ψ

**Pre-registered prediction:** FastWeight ≥ 0.897 (bptt baseline) because ψ provides learned read/write projections the fixed random projections lack.

**Falsification:** If FastWeight ≤ 0.897 at matched budget → the learned/fixed-write distinction is empty even with credit. P-axis contribution to ordinary-task memory is closed.

**I(C,U,P) extension:** Run under {Adam, Muon} to test whether ψ changes the interaction surface.

**Cost:** ~3 min × 2 updates × 3 seeds = ~18 min total. **Background** (3 parallel pairs).

### 2.2 RoutingPlasticity × Depth-32 (~3 min/cell)

**What:** Add `RoutingPlasticity` (gate_dim=32) to the depth-32 recipe. Compare: Null×d32 vs Routing×d32 vs Routing×d50.

**How:** Extend `d50_autopsy.py` with `--routing --gate-dim=32`. Probe-free EMA.

**Pre-registered prediction (softened per evaluation):** Routing×d50 ≥ Null×d32 × 0.90 (within 10% of the depth-32 frontier, i.e., ≥ 0.83). If Routing×d50 < 0.83: the depth boundary is representation-limited, not compute-limited. Routing does not solve peak-then-memorize.

**Falsification:** If Routing×d50 < 0.83 → routing does not prevent late-layer memorization.

**Cost:** ~3 min × 3 configs × 3 seeds = ~27 min total. **Background** (3 parallel).

### 2.3 Z3 Toy Feasibility (~3 min/cell)

**What:** Frozen θ, two tasks (parity, last-symbol), ψ selects operators. Assert exact θ invariance.

**Implementation prerequisite (~30 min, separate from execution):**
- Implement operator callables: {Identity, Parity, LastSymbol} as fixed functions on hidden state. Reuse D17 multi-ψ infrastructure (frozen backbone pattern).
- ψ: one-hot selector vector (3,), written by closed-form ridge on operator outputs.
- Architecture: 32→16→4 MLP, trained on parity to convergence via distill-init, then frozen (SHA-asserted).

**Execution:** `scripts/probes/z3_toy.py`
- Task A: parity (ψ selects Parity operator). Task B: last-symbol (ψ selects LastSymbol).
- Assert: `‖θ_after − θ_before‖ == 0` bitwise. Both tasks ≥ 0.90.

**Pre-registered prediction:** ψ-mediated operator selection achieves ≥ 0.90 on both tasks with exact θ invariance.

**Falsification:** If ψ cannot select without degrading task A → Z3 mechanism closed at toy scale.

**Critical distinction from Flagship B:** Z3 uses ψ to *select computation* (discrete routing), not to *correct representations* (continuous affine). The mask-entropy law does not apply.

**Cost:** Implementation ~30 min (Phase 2 prerequisite). Execution ~3 min × 3 seeds = ~9 min. **Foreground** (each cell ≤3 min).

### 2.4 RoutingPlasticity × NCA (Stability-Plasticity Test) (~2 min/cell)

**What:** First empirical test of the stability-plasticity hypothesis: "useful rule reconfiguration may require temporarily sacrificing contraction margin."

**How:** Extend `w8_nca_local.py` with `--routing`:
- Per-site gate: `g = sigmoid(W_gate @ neighborhood_features)`
- Effective delta: `Δstate = g * Δ + (1-g) * 0` (gated growth)
- Track: ρ(J_F) via power iteration, settling time, basin stability (perturbation recovery)
- Distill-init matched. 300 eps.

**Pre-registered prediction:** Routing reduces compute (fewer active sites) at ≤5% stability margin loss. If routing destabilizes the fixed point → boundary condition for the hypothesis.

**Cost:** ~2 min × 3 seeds = ~6 min. **Foreground.**

### Phase 2 Stop-Loss

If **all four** probes (2.1–2.4) falsify: P-axis closed at probe scale. Record boundaries. Return to NTM ladder and PEPITA breadth. Do not theorize. Do not escalate.

---

## Phase 3 — Escalation (Session 3–4, gated by Phase 2 survival)

### 3A. If Z3 Toy Alive → Z3 Full Experiment (~3 min/cell)

**What:** Expand to 8 operators: {Identity, Threshold, Accumulate, LastSymbol, Parity, SparseTopKRoute, SignFlip, Delay}. Tasks: parity, last-symbol, threshold, cumulative-sum.

**Key metrics:** Adaptation time (episodes to switch), parameter invariance (exact), operator diversity.

**Connection to Benchmark Level 3.5 (Algorithm Migration):** This IS the algorithm migration experiment. ψ switches strategy A₀→A₁ without changing θ.

**Cost:** ~3 min × 4 tasks × 3 seeds = ~36 min. **Background.**

### 3B. If Routing×Depth Alive → Depth-64/100 (~6 min/cell, background)

**Critical cost correction:** Depth-100 at 150 batches takes ~24 min/seed (§13.6). At 40 batches (peak at 30): ~6.4 min. **This exceeds 5 min. MUST be backgrounded.**

**How:** `d50_autopsy.py --depth {64,100} --batches 40 --harvest --routing --probe-free`

**Pre-registered:** If Routing×depth-64 ≥ Null×depth-32 × 0.90 → the frontier is compute-limited, not representation-limited.

**Cost:** ~6 min × 2 depths × 3 seeds = ~36 min. **Background**, poll ≤2 min, pre-registered kill at 8 min.

### 3C. If FastWeight×NTM Alive → FastWeight×Depth (~3 min/cell)

**What:** FastWeightPlasticity on depth-32/50 MLPs. Probe-free EMA.

**Pre-registered:** FastWeight×depth-50 EMA ≥ Null×depth-50 EMA + 0.03. Two-timescale adaptation flattens the memorization tail.

**Cost:** ~3 min × 2 depths × 3 seeds = ~18 min. **Background.**

### 3D. If Routing×NCA Alive → Stability Measurement (~2 min)

**What:** Full stability-plasticity measurement on trained checkpoints.

**How:** `comp stability --model nca_routing --task growth` — measurement only, no training.

**Metrics:** ρ(J_F), local Lyapunov exponent, settling time, basin stability.

**Cost:** ~2 min.

---

## Phase 4 — Flagship C: Predictive I(C,U,P) Model (Session 4–5, ~35 min)

### 4.1 Aggregate Data (~5 min)

Run §0.2 extraction script. **Zero new compute.**

### 4.2 Fit Predictive Model (~10 min — the 10-min exception)

**Model:** `sklearn.tree.DecisionTreeClassifier` (interpretable) + `sklearn.linear_model.LogisticRegression` (calibrated). Target: binary viable/not-viable.

**Validation strategy:** 5-fold cross-validation with stratified splits. Report mean ± std accuracy. If CV accuracy < 70%: add mechanism_class and task_type as features before refitting.

**Feature space:**

| Feature Class | Features |
|---|---|
| Credit mechanism | exact_gradient / projected_pseudo / goodness_contrast / hebbian / no_error_term |
| Optimizer geometry | orthogonalizing / per_coordinate / sign_based / euclidean |
| Architecture | depth, width, geometry_class (stack/iterative/memory) |
| Task type | fixed_input / autoregressive / retrieval_demanding |
| Plasticity | null / routing / fast_weight |

### 4.3 Prediction-Before-Measurement Validation (~4 min)

**What:** Hold out one geometry (lattice). Predict its I(C,U) profile from {MLP, NCA, NTM}. Compare.

**Additional held-out predictions (3 cells, ~4 min total):**
1. PEPITA × Lion on classification (~1 min). Prediction: Lion hurts (sign-blind on exact-modulation), but less severely than Muon.
2. FA × OrthoAdam on NTM (~2 min). Prediction: rescue transfers from MLP.
3. FastWeightPlasticity × Muon on ordinary task (~1 min). Prediction: optimizer matters less (ψ is not credit-shaped).

### 4.4 Ship Report (~5 min)

`comp frontier --study icu_law` → HTML report with:
- I(C,U) interaction heatmap (credit × update, colored by Δ)
- P-axis modulation plot (how plasticity changes the interaction surface)
- Recipe-card table (queryable)
- Predictive model accuracy + held-out validation results
- Failure manifold clustering (via `computronium/analysis/genealogy.py`)

---

## Phase 5 — Benchmark Hierarchy (Session 5–6, ~30 min)

### 5.0 Feasibility Check (~2 min)

Before running any benchmark level: `comp benchmark run --suite adaptation_efficiency --dry-run` (or equivalent) to verify task generators produce valid data. If it fails: defer that level, run the next.

### 5.1 Level 1: Adaptation Efficiency (~5 min)

**What:** Distribution-switch task (Phase A: y=f_A(x), Phase B: y=f_B(x)). Compare Null vs FastWeight vs Routing on adaptation time and energy.

**Connection:** Directly tests P-axis under distribution shift. If Phase 2 showed FastWeight alive, this validates it at benchmark scale.

**Cost:** ~5 min (3 configs × 3 seeds × ~30s, parallel).

### 5.2 Level 3.5: Algorithm Migration (~5 min)

**What:** Cumulative sum → Last symbol. Assert ‖θ_after − θ_before‖ = 0.

**Connection:** This IS Z3 if Phase 3A is alive. Reuse Z3 infrastructure.

**Cost:** ~5 min.

### 5.3 Level 3: Structural Robustness (~5 min)

**What:** Zero weights, remove nodes, dead channels. Null vs Routing vs SubstrateCoupled recovery.

**Connection:** RoutingPlasticity's recovery capability (from Phase 2.2/3B) is the mechanism under test.

**Cost:** ~5 min.

### 5.4 NTM Associative Recall (~4 min/cell, background)

**What:** Execute §17.10 queued levers in specified order:
1. **First:** Run levers (a) writer loss re-weighting AND (b) value-channel supervision through live `hc` at cued-read step, **combined**. 4800 steps cap.
2. **If combined (a)+(b) pushes acc_given_hit ≥ 0.85:** recall is solved.
3. **If not:** Run lever (c) extended budget at 12000 steps, **background**.

**Pre-registered:** If (a)+(b) combined ≥ 0.85 → value binding solved. If not → value binding is a structural limit of zero-history factorization.

**Cost:** ~4 min × 4 configs × 3 seeds = ~48 min. **Background.**

---

## Phase 6 — Transport Graph Mapping (Session 6–7, ~35 min)

### 6.1 Transport Graph Spectrum on Retrieval Tasks (~3 min/cell)

**What:** Map the dense↔sparse spectrum on retrieval-demanding tasks only (§17.11: memory value is only measurable on retrieval-demanding tasks).

| Memory Type | Write Rule | Read Rule |
|---|---|---|
| Dense fast weights (Hebbian) | Fixed outer-product | Linear projection |
| Sparse addressed (NTM) | Learned heads | Softmax content |
| Slot-capped fast weights | Fixed + slot mask | Slot-indexed |
| Linear-transformer read | Fixed | Linear attention |

**Tasks:** copy + associative recall (the retrieval-demanding rungs).

**Question:** At what retrieval-demand does learned addressing reassert itself over fixed writes?

**Cost:** 4 types × 2 tasks × 3 seeds = 24 cells × ~2.5 min = ~60 min. **Background** (3 parallel).

**Reduced version (if time-constrained):** 4 types × 1 task (recall) × 3 seeds = 12 cells × ~2.5 min = ~30 min background.

### 6.2 Minimal Transport Graph Credit Rule (Design Only)

**What:** Design doc for a new `CreditAssignment` primitive that optimizes the gradient path through memory directly, without learned addressing.

**Status:** Design only. No implementation until §6.1 shows transport graph is the binding constraint. **Cost: 0 min compute.**

### 6.3 I(C,U,P) Three-Way Interaction Report (~5 min)

**What:** Combine Phase 4 model + Phase 2/3 P-axis data + Phase 5 benchmark data.

**Key question answered:** Does ψ change the credit-optimizer interaction surface, or is it a passive passenger?

**Ship as:** Extension of §4.4 report + `comp stability` output.

---

## Phase 7 — AutoScientist Campaigns (Session 7+, background)

### 7.1 First 6-D Joint Campaign (~2 min/cell, background)

```yaml
campaign: p_axis_credit_update_sweep
fixed: {S: Digital, G: FeedforwardDAG, D: InstantaneousPass}
varied: P × C × U = 3 × 4 × 2 = 24 cells × 3 seeds = 72 cells
budget_per_cell: 150 batches MNIST (~2 min)
hypothesis: "P-axis modulates the I(C,U) interaction surface"
```

**Cost:** 72 × 2 min = ~144 min. **Background** (3 parallel, OMP=2). Poll every 2 min.

### 7.2 Stability-Plasticity Campaign (~2 min/cell, background)

```yaml
campaign: stability_plasticity_frontier
fixed: {S: Digital, G: NcaGeometry, D: InstantaneousPass, C: LocalGoodnessCredit}
varied: P × U × ρ constraint = 2 × 2 × 4 = 16 cells × 3 seeds = 48 cells
budget_per_cell: 300 eps NCA (~2 min)
hypothesis: "useful rule reconfiguration requires controlled departure from contraction"
```

**Cost:** 48 × 2 min = ~96 min. **Background.**

---

## Anti-Stack (Explicit Deferrals)

| Direction | Reason |
|---|---|
| Substrate exploration (memristive, optical, quantum, photonic) | Excluded by constraint |
| W0 transformer local credit revival | Boundary with full mechanism map; gate shutdown structural |
| LEMMA redemption | Closed with measurement (alignment ≈ 0) |
| Mask-ψ / piecewise-ψ | Mask-entropy law confirmed cross-geometry |
| PEPITA on LM / autoregressive tasks | Label-copying attractor structural |
| STDP modulation (W7.3b) | No error term; structural closure. Keep killed. |
| Depth > 32 without P-axis mechanism | Extends peak-then-memorize without new capability |
| W8.6 cellular-computer moonshot | Requires P-axis + NTM + NCA composition; defer to Phase 7+ |
| Per-site FA primitive (lattice) | Requires invention; composition before invention |
| New credit/update primitives | Composition before invention |
| Breadth for breadth's sake | Depth on alive axes, not width on dead ones |
| 3-seed promotion rounds within a sprint | Single-seed reopen sufficient to change status; promotion deferred |

---

## Per-Cell Time Budget (Hard Limits)

| Cell Type | Budget | Method |
|---|---|---|
| Probe-free EMA harvest (depth ≤ 50) | ≤3 min | `--probe-free`, 150 batches |
| Depth-64 harvest | ≤5 min | `--batches 40` (peak at ~30) |
| Depth-100 harvest | ≤7 min | `--batches 40`, **background** |
| NTM copy/recall @4800 | ≤4 min | Width 16, parallel |
| NTM copy @8000 | ≤5 min | Background if >5 |
| NCA finetune | ≤2 min | Distill-init, 300–800 eps |
| Z3 toy | ≤3 min | Frozen θ, closed-form ψ |
| PEPITA classification | ≤3 min | 150 batches |
| FastWeight × NTM ordinary | ≤3 min | 600 steps |
| Routing × depth-32 | ≤3 min | Probe-free EMA |
| Predictive model fit | ≤10 min | **10-min exception** |
| Benchmark Level 1/3/3.5 | ≤5 min | Toy tasks, parallel |
| AutoScientist campaign cells | ≤2 min | Background, parallel |

**Any cell exceeding 5 min MUST be backgrounded.** No exceptions.

---

## Success Criteria

| Criterion | Met When |
|---|---|
| Depth ≥ 50 headline shipped | Gallery demo D18 passes lock test |
| NTM local-credit capability shipped | Gallery demo D19 passes lock test |
| I(C,U) law is predictive | Held-out prediction accuracy ≥ 80% |
| P-axis produces new capability | ≥1 Phase 2 probe alive AND Phase 3 succeeds |
| Benchmark hierarchy exercised | Levels 1, 3.5, 3 produce FrontierRecords |
| Stability-plasticity measured | ρ(J_F) reported for ≥2 P-axis configs |
| Transport graph quantified | ≥3 memory types on ≥1 retrieval task |
| Recipe cards queryable | `comp frontier --study icu_law` renders HTML |
| LSTM-alone control measured | §17.11 prerequisite satisfied |
| Inertness guard live | RandomProjectionsCredit warns on all-zero pseudo-gradients |

---

## Execution Rules

1. Every cell pre-registers: question, mechanism, prediction, control, budget, metric, falsification criterion.
2. Every negative gets §17 defect-hunt before boundary.
3. Every positive gets 3-seed + matched control before promotion.
4. **Background anything >5 min.** Poll ≤2 min. Pre-register kill time.
5. OMP_NUM_THREADS=2 for parallel launches. Max 3 concurrent.
6. Assert `batches_seen ≥ budget` inside every training loop.
7. EMA harvest is default. Probe-free unless peak STEP is the datum.
8. No new ontology primitives without Phase 2 survival + user confirmation.
9. Reactive ratchet only. Lock defects encountered, not hypothetical.
10. **Stop-loss honored.** All Phase 2 falsify → write boundaries, pivot.
11. **Recorded-source verdicts count.** If a measurement exists in a log, cite it. Do not re-run.
12. **Feasibility-isolation ladder before any training.** Representation → Wiring → Horizon → Optimizer.
13. **Checkpoint first, diagnose second.** Never retrain to re-run a diagnostic.

---

## Total Estimated Compute

| Phase | Foreground | Background | Total |
|---|---|---|---|
| 0: Infrastructure | ~40 min | 0 | ~40 min |
| 1: Ship | ~10 min | ~25 min | ~35 min |
| 2: P-Axis Probes | ~15 min | ~45 min | ~60 min |
| 3: Escalation | ~5 min | ~90 min | ~95 min |
| 4: Flagship C | ~25 min | 0 | ~25 min |
| 5: Benchmarks | ~17 min | ~50 min | ~67 min |
| 6: Transport Graph | ~5 min | ~35 min | ~40 min |
| 7: AutoScientist | 0 | ~240 min | ~240 min |
| **Total** | **~117 min** | **~485 min** | **~602 min** |

**Foreground time (active attention): ~2 hours across 7 sessions.**
**Background time (unattended): ~8 hours.**
**Maximum single foreground cell: 10 min** (predictive model fit only).

---

## Session Map

| Session | Focus | Foreground | Background Launched |
|---|---|---|---|
| 1 | Phase 0 + Phase 1.1–1.2 | ~50 min | PEPITA breadth, NTM 3-seed, LSTM control |
| 2 | Phase 1.3–1.5 results + Phase 2 probes | ~30 min | FastWeight×NTM, Routing×depth |
| 3 | Phase 2.3 Z3 + Phase 2.4 NCA | ~45 min | Z3 full (if alive), depth-64/100 (if alive) |
| 4 | Phase 3 results + Phase 4.1–4.2 | ~35 min | — |
| 5 | Phase 4.3–4.4 + Phase 5 | ~35 min | NTM recall, transport graph |
| 6 | Phase 5 results + Phase 6 | ~25 min | AutoScientist campaigns |
| 7 | Phase 7 results + final report | ~15 min | — |
