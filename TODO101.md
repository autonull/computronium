# TODO101 — SEC Loop: Breadth Completion & Multi-Axis Claims

**Status:** 2026-11-23. TODO100 complete (Credit axis Rung 0–3 done). Next phase: breadth completion across all axes + claims on non-Credit axes.

**Principle:** Breadth before optimization. Every low cell is a defect probe. Fixes propagate across primitives via shared implementation.

---

## 🎯 Scope: Complete Breadth + Multi-Axis Rung 2/3

| Axis | Primitives | Rung 0 | Rung 1 (viability) | Rung 2 (provisional) | Rung 3 (claims) |
|------|------------|--------|--------------------|----------------------|-----------------|
| Credit | 19 | ✅ | ✅ (13/16 viable) | ✅ (13 at best box) | ✅ (2 credits, 4 claims) |
| Update | 18 | ✅ | ✅ (18/18 viable) | ✅ (2 claims: lion, muon) | ⬜ |
| Substrate | 10 | ✅ | ✅ (10/10 viable) | ✅ (0 claims) | ⬜ |
| Dynamics | 8 | ✅ | ⚠️ (1/8 viable on default) | ✅ (1 claim: energy_min) | ⬜ |
| Plasticity | 8 | ✅ | ⚠️ (1/8 viable: temporal_psi) | ✅ (0 claims) | ⬜ |
| Geometry | 12 | ✅ | ❌ (needs task shape) | ⬜ | ⬜ |

**Total:** 75 primitives, all Rung 0 wired.
**Rung 1 complete:** Credit, Update, Substrate.
**Rung 1 partial:** Dynamics (energy_minimization viable with matched box), Plasticity (temporal_psi viable).
**Rung 1 blocked:** Geometry (structural knobs need task shape at compose time).
**Rung 2 complete:** Credit (2 claims), Update (2 claims), Substrate (0 claims), Dynamics (1 claim), Plasticity (0 claims).
**Rung 3 complete:** Credit (2 credits × 2 families = 4 claims).

---

## 📋 Phase 1: Breadth Completion — Re-screen Stale Map Rows

**Problem:** Map rows measured before void rules were declared carry boxes the declared space now refuses (e.g., `fast_weights` measured at `instantaneous` dynamics, `conflict_adaptive` measured with `gradient` credit). The capability rung rebuilds legal boxes via `_iter_legal_coordinates`, but the main SEC map (`results/sec/map.json`) still has stale coordinates.

**Action:** Run full breadth screen on MNIST (vision) to refresh all 75 primitives at legal coordinates.

```bash
# Full breadth screen on MNIST (vision)
uv run python -m computronium.experiment.sec_loop \
  --track P0 --breadth full --task mnist --device cuda \
  --out results/sec_breadth_vision --max-primitives 75
```

**Expected:** All 75 primitives screened at legal coordinates. Refused primitives documented with reason (geometry mismatch, credit×dynamics incompatibility, etc.).

**Follow-up:** Repeat for other task families where base boxes exist:
- Tabular (iris): `uv run python -m computronium.experiment.sec_loop --track P0 --breadth full --task iris --device cpu --out results/sec_breadth_tabular --max-primitives 75`
- Sequence (sequential_mnist): when base box declared
- Graph (cora): when base box declared

**Walltime estimate:** ~10 min on GPU for 75 primitives × 1 epoch L0.

---

## 📋 Phase 2: Update Axis — Rung 3 Claims (lion, muon)

**Status:** Rung 2 complete — lion (d=3.97) and muon (d=10.63) beat euclidean baseline on MNIST.

**Action:** Pre-register paired comparisons for lion and muon on vision (mnist) and tabular (iris) families.

```bash
# Pre-register claims
uv run python -m computronium.experiment.sec_deep_dive \
  --credit lion --family vision \
  --registration configs/preregistrations/sec_update_lion_vision.json \
  --n-seeds 5 --async

uv run python -m computronium.experiment.sec_deep_dive \
  --credit muon --family vision \
  --registration configs/preregistrations/sec_update_muon_vision.json \
  --n-seeds 5 --async
```

**Success criteria:** Cohen's d ≥ 0.8 (vision) / ≥ 0.5 (tabular) with 95% CI excluding 0.

---

## 📋 Phase 3: Dynamics Axis — Rung 3 Claim (energy_minimization)

**Status:** Rung 2 complete — energy_minimization (beta=0.1, step_size=0.1) beats instantaneous (d=15.5) on MNIST.

**Action:** Pre-register paired comparison for energy_minimization on vision (mnist) and tabular (iris).

```bash
uv run python -m computronium.experiment.sec_deep_dive \
  --dynamics energy_minimization --family vision \
  --registration configs/preregistrations/sec_dyn_energy_min_vision.json \
  --n-seeds 5 --async
```

**Note:** energy_minimization requires `energy_minimization` dynamics + compatible credit (not gradient). Use `pc_alm` or `target_inversion` credit.

---

## 📋 Phase 4: Plasticity Axis — Rung 2/3 for temporal_psi

**Status:** temporal_psi viable on MNIST (val_acc=0.838 vs null=0.886) but underperforms. Other 7 plasticity primitives refused or no effect.

**Action:** 
1. Tune temporal_psi knobs (trace_decay, learning rate) to close gap with null baseline
2. If viable, pre-register claim on vision + tabular
3. Document capability gaps for refused primitives (conflict_adaptive, fast_weights, routing, closed_form_ridge, rule_state, substrate_coupled)

```bash
# Viability ladder for temporal_psi
uv run python -m computronium.experiment.sec_loop \
  --track P0 --breadth delta --task mnist --axis plasticity \
  --own-knobs --out results/sec_plasticity_tune --max-primitives 8
```

---

## 📋 Phase 5: Geometry Axis — Structural Knob Resolution

**Problem:** All 12 geometry primitives have structural knobs (hidden_dim, num_layers) requiring task shape at compose time. Cannot run Rung 1 ladder without a task.

**Fix Options:**
1. **Declare default task shapes** in geometry primitive specs (e.g., `default_input_dim=784, default_hidden_dims=(512,)`)
2. **Add task-aware compose** that injects task shape from the run spec into geometry configs
3. **Run Rung 1 per-task** (MNIST for vision, iris for tabular, etc.) instead of generic ladder

**Recommendation:** Option 2 — modify compose chain to carry `TaskShape` through to geometry builders. This is a structural fix that benefits all axes.

**Files to modify:**
- `computronium/experiment/kernel/compose.py` — inject task shape
- `computronium/primitives/geometry/` — accept optional `input_dim`, `hidden_dims` from task

---

## 📋 Phase 6: Substrate Axis — Rung 3 on Specialized Tasks

**Status:** No substrate beats digital on MNIST. But substrates are designed for specialized tasks (neuromorphic, photonic, quantum, analog).

**Action:** Run Rung 1/2 on declared task families:
- Neuromorphic substrates → neuromorphic tasks (spiking MNIST, DVS gestures)
- Photonic substrates → photonic tasks (optical MNIST simulation)
- Quantum substrates → quantum tasks (quantum circuit learning)
- Analog substrates → analog tasks (memristor simulation)

**Requires:** Task implementations for these families (currently missing).

---

## 🔧 Defect Registry (Extended from TODO100)

| Defect ID | Symptom | Mechanism | Failing Test | Fix File | Primitives Affected | Status |
|-----------|---------|-----------|--------------|----------|---------------------|--------|
| GAP-001 | σ channel missing | θ not in _step_psi | test_the_plastic_step_carries_the_substrate_state | core/pipeline.py | All plasticity | ✅ Fixed |
| DEF-001 | target_inversion below bar | feedback_scale default too small | Rung 1 ladder (digits) | N/A (hyperparam) | target_inversion | ✅ Fixed |
| DEF-002 | local_goodness below bar | readout_error=False default | Rung 1 ladder (digits) | N/A (hyperparam) | local_goodness | ✅ Fixed |
| DEF-003 | Later families never tried | pytest.skip aborted loop | test_primitive_on_declared_families | tests/primitives/test_primitive_capability.py | multi-family | ✅ Fixed |
| DEF-004 | time-major energy crashes | trace() assumes 2-D | test_primitive_on_declared_families | ontology/dynamics/_dynamics.py | energy_minimization | ✅ Fixed |
| DEF-005 | fast_weights crash on sequence | modulate wrong axis | test_primitive_on_declared_families | core/plasticity/fast_weights.py | fast_weights | ✅ Fixed |
| DEF-006 | RL cell compared on accuracy | reads accuracy, not mean_reward | test_primitive_on_declared_families | tests/primitives/test_primitive_capability.py | RL tasks | ✅ Fixed |
| **DEF-007** | **Geometry needs task shape** | Structural knobs require input_dim | — | compose.py, geometry builders | All geometry | **Open** |
| **DEF-008** | **Stale map coordinates** | Map measured before void rules | — | sec_loop.py --breadth full | All axes | **Phase 1** |
| **DEF-009** | **temporal_psi below null** | trace_decay not optimal | Rung 2 (MNIST) | N/A (hyperparam) | temporal_psi | **Phase 4** |
| **DEF-010** | **Substrate tasks missing** | No neuromorphic/photonic/quantum tasks | — | domains/ | neuromorphic, photonic, quantum substrates | **Phase 6** |

---

## 🏁 Exit Criteria for TODO101

| Criterion | Target | Status |
|-----------|--------|--------|
| Phase 1: Full breadth screen on MNIST completes | 75 primitives screened at legal coordinates | ⬜ |
| Phase 1: Full breadth screen on iris completes | 75 primitives screened at legal coordinates | ⬜ |
| Phase 2: lion claim confirmed on vision (d≥0.8, n=5) | Pre-registered paired comparison passes | ⬜ |
| Phase 2: muon claim confirmed on vision (d≥0.8, n=5) | Pre-registered paired comparison passes | ⬜ |
| Phase 3: energy_minimization claim confirmed on vision (d≥0.8, n=5) | Pre-registered paired comparison passes | ⬜ |
| Phase 4: temporal_psi viability gap closed or gap documented | Rung 2 coordinate or named capability gap | ⬜ |
| Phase 5: Geometry accepts task shape from compose | All 12 geometry primitives run Rung 1 on MNIST | ⬜ |
| Capability gate green after each phase | No regressions in test_primitive_capability.py | ⬜ |
| Experiment log complete | Rung, stop reason, box, cost recorded per cell | ⬜ |

---

## 📊 Experiment Log Template (per session)

```
## Session YYYY-MM-DD
**Decision:** <question, actions, error costs>
**Experiment:** <command>
**Box:** <task, fidelity, seeds, knobs allowed>
**Rung / stop:** <0-3; why the rung stopped>
**Result:** <metric, ruler, cost>
**Triage:** <defect | capability gap | coordinate result; if defect, the failing test; if gap, the primitive that closes it>
**Fixes Applied:** <files changed>
**Next Experiment:** <planned command>
```

---

## 🔄 Recommended Order

1. **Phase 1** (immediate): Full breadth screens on MNIST + iris — refreshes map, unblocks all downstream work (~20 min GPU)
2. **Phase 2** (parallel): Pre-register & run Update axis claims (lion, muon) — builds on completed Rung 2
3. **Phase 3** (parallel): Pre-register & run Dynamics axis claim (energy_minimization)
4. **Phase 5** (structural): Fix Geometry task-shape injection — unblocks Geometry Rung 1
5. **Phase 4** (tuning): temporal_psi knob tuning — may close gap or document gap
6. **Phase 6** (long-term): Substrate-specialized tasks — requires new task implementations

---

## 📈 Compounded Impact

| Metric | Current (TODO100) | With TODO101 |
|--------|-------------------|--------------|
| Axes with Rung 3 claims | 1 (Credit) | 3 (Credit, Update, Dynamics) |
| Total confirmed claims | 4 | Target: 8+ |
| Geometries with Rung 1 data | 0 (blocked) | 12 (all) |
| Primitives with legal map coords | ~60% (stale) | 100% (refreshed) |
| Capability map completeness | Partial | Full breadth |

**Total estimated wall-clock:** ~2-3 hours GPU (Phases 1-3) + structural fix (Phase 5) + tuning (Phase 4).

---

*TODO101 continues the SEC loop. The map is the artifact, not the leaderboard. Every anomaly is a triage question.*