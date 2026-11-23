# TODO102 — Self-Improving System: Consolidated Hygiene, Specialized Tasks & Recursive Optimization

**Status:** 2026-11-23. TODO101 complete (breadth + 8 Rung 3 claims). Next: hygiene, specialized tasks, recursive self-improvement.

**Principle:** The system improves itself. Every defect fixed widens capability. Every measurement feeds the next rung. The map is the artifact; the loop is the engine.

---

## 🎯 Consolidated Scope: 3 Tracks, Not 9 Phases

| Track | Focus | Duration | Dependencies |
|-------|-------|----------|--------------|
| **A: Foundation** | Hygiene + Specialized Tasks | Week 1-2 | None (parallel) |
| **B: Depth** | Geometry/Plasticity/Substrate Rung 2/3 | Week 2-3 | Track A |
| **C: Recursive** | Meta-SEC + Gap Closure | Week 3-4 | Track B |

**Key Insight:** Tracks A and B are the *work*; Track C is the *engine* that makes future work cheaper. Run C's instrumentation *during* A/B, not after.

---

## 📋 Track A: Foundation (Week 1-2, Parallel)

### A.1: Hygiene — 2 Fixes, 1 File Each
| Defect | Fix | File | Test |
|--------|-----|------|------|
| DEF-012 | Tile void constraint | `legality/void_rules.py:allow_tile_gradient()` | `pytest -k "tile" -n 1` |
| DEF-013 | Routing credit incompatibility | `kernel/search_space.py:routing_compatible_credits` | `pytest -k "routing" -n 1` |

**Efficiency:** Both are single-function edits. Run tests in parallel.

### A.2: Specialized Substrate Tasks — 4 Tasks, 1 Pattern
**Pattern:** Each task = 1 file in `domains/<family>.py` with `@register_task` decorator.

| Family | Tasks | File | Base Template |
|--------|-------|------|---------------|
| neuromorphic | spiking_mnist, dvs_gestures | `domains/neuromorphic.py` | `domains/vision.py` |
| photonic | optical_mnist_sim | `domains/photonic.py` | `domains/vision.py` |
| quantum | quantum_circuit_learning | `domains/quantum.py` | `domains/scientific.py` |
| analog | memristor_simulation | `domains/analog.py` | `domains/scientific.py` |

**Low-Effort Win:** Copy `domains/vision.py` → modify `input_shape`, `domain`, `geometry_hint`, `pass_bar`. 15 min/task.

**Parallelization:** All 4 independent. Assign to subagents.

### A.3: Instrumentation for Track C (Free, During A/B)
Add to every SEC run (already in `sec_loop.py`, `sec_all_axes.py`):
```python
# Already captured: walltime_s, replay_hash, box params, refusal reason
# Add to cell record: primitive_signature = hash(primitive + knob + task)
```
No code change — data already flows. Track C reads `cells.jsonl`.

**Track A Exit Criteria:**
- [x] DEF-012, DEF-013 fixed → tile + instantaneous + gradient allowed; routing_compatible_credits() returns 13 credits
- [x] 4 specialized tasks registered → neuromorphic (2), photonic (1), quantum (1), analog (1)
- [ ] All 12 geometries Rung 1 viable on MNIST (pending capability test run)

---

## 📋 Track B: Depth (Week 2-3, After A)

### B.1: Geometry Rung 2/3 — 7 Primitives, Batched
**Viable on MNIST:** attention, feedforward, recurrent, ntm, tile_mesh, spatial_lattice, nca

**Batch Command:**
```bash
# Rung 2 ladders (parallel, 7 primitives × 2 tasks)
uv run python -m computronium.experiment.sec_all_axes --axis geometry --rung both --task mnist --semaphore 3
uv run python -m computronium.experiment.sec_all_axes --axis geometry --rung both --task iris --semaphore 3
```

**Auto-Register Claims:** Script reads best ladder point → writes `configs/preregistrations/sec_geometry_<prim>.json`.

### B.2: Plasticity Rung 3 — temporal_psi Only
**Gap:** -0.47pp vs null. Fix: add `trace_decay_schedule` hyperparam (exponential/linear).

**Action:**
1. Add `trace_decay_schedule` to `TemporalPsiConfig.hyperparameters()` (domain: ["constant", "exponential", "linear"])
2. Run Rung 2 with schedule as knob (vs constant baseline)
3. If viable → Rung 3 claim

### B.3: Substrate Rung 2/3 — On Specialized Tasks
Run on tasks from Track A.2:
```bash
uv run python -m computronium.experiment.sec_all_axes --axis substrate --rung both --task spiking_mnist --semaphore 2
uv run python -m computronium.experiment.sec_all_axes --axis substrate --rung both --task optical_mnist_sim --semaphore 2
# ... etc
```

**Track B Exit Criteria:**
- [ ] 6+ Geometry Rung 3 claims (d ≥ 0.8 vision)
- [ ] temporal_psi Rung 3 claim or documented gap with fix primitive
- [ ] 4 Substrate Rung 2 coordinates on specialized tasks

---

## 📋 Track C: Recursive Meta-SEC (Week 3-4, Continuous)

### C.1: Meta-SEC Engine (1 File: `computronium/experiment/meta_sec.py`)
**Reads:** `results/sec/cells.jsonl` + `results/sec/map.json`
**Optimizes:**
| Parameter | Current | Search Space |
|-----------|---------|--------------|
| LADDER_FACTORS | (0.1, 1.0, 10.0) | 3-5 points, log-spaced |
| CLAIM_SEEDS | 5 | 3, 5, 7, 10 |
| MIN_EFFECT_SIZE | 0.8/0.5 | 0.5-1.2 per family |
| Fidelity schedule | L0→L1→L2 | L0 only, L0→L1, L0→L2 |
| semaphore_limit | 2 | 1, 2, 4, 8 |

**Method:** Bayesian optimization (TPE) on meta-objective: `claims_per_gpu_hour`.

### C.2: Search Space Pruning (From Data, Not Code)
**Current:** Hand-coded void rules in `legality/void_rules.py`
**New:** Learn from `cells.jsonl` refusals:
```python
# For each (geometry, credit, dynamics) tuple: count refused vs measured
# If refused_rate > 0.8 and measured_count > 5 → add void rule
# If measured_count > 10 and all viable → remove void rule
```
**Output:** Auto-generated `void_rules_learned.py` → reviewed → replaces hand-coded.

### C.3: Primitive Proposals (From Gaps)
**Input:** Capability gaps from Track B (temporal_psi, causal_transformer, conv)
**Output:** New primitive configs in `primitives/registry.py` with `available=False, unavailable_reason="proposed"`.
**Validation:** Rung 0 (wiring) auto-run on proposal.

### C.4: Budget Allocation Policy
**Current:** Static `ADAPTIVE_L0_SHARE = 0.3` (spaces <1000) / `0.5`
**Learned:** Per-primitive cost model from `walltime_s` → `n_wave = budget / (pred_cost × seed_plan)`
**Model:** Linear regression on `log(walltime) ~ log(param_count) + fidelity + axis_knob`

**Track C Exit Criteria:**
- [ ] Meta-SEC runs → improves `claims_per_gpu_hour` by ≥ 2×
- [ ] Learned void rules match hand-coded ≥ 90% + find 2+ new
- [ ] 3+ primitive proposals auto-generated, 1+ clears Rung 0
- [ ] Budget policy beats static split on held-out wave

---

## 🔄 Consolidated Execution Graph

```
                    ┌─────────────────────┐
                    │   START (TODO101)   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │  A.1 Hygiene │ │ A.2 Tasks   │ │ A.3 Instrument│
       │  (2 fixes)   │ │ (4 files)   │ │ (free)      │
       └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    ┌─────────────────┐
                    │  CAPABILITY     │
                    │  GATE 56/56     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │ B.1 Geometry│ │ B.2 Plastic │ │ B.3 Substrate│
       │ Rung 2/3    │ │ temporal_psi│ │ Specialized │
       └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    ┌─────────────────┐
                    │  CLAIMS + GAPS  │
                    │  (data for C)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │ C.1 Meta-SEC│ │ C.2 Prune   │ │ C.3 Propose │
       │ Optimize    │ │ Void Rules  │ │ Primitives  │
       └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    ┌─────────────────┐
                    │  TODO103 READY  │
                    │  (Self-Improving)│
                    └─────────────────┘
```

**Parallelization:**
- A.1 + A.2 + A.3: Fully parallel (Week 1)
- B.1 + B.2 + B.3: Parallel after A (Week 2)
- C.1-4: Continuous during A/B; full run after B (Week 3-4)

---

## 📊 Low-Effort High-Impact Capabilities (Achieved During A/B)

| Capability | Effort | When | Value |
|------------|--------|------|-------|
| **Auto-claim registration** | 1 script | B.1 | No manual JSON writing |
| **Cost model per primitive** | 1 query | A.3 (free) | Optimal wave sizing |
| **Refusal taxonomy** | 1 query | A.3 (free) | Debug via `grep "refused" cells.jsonl` |
| **Primitive signature hashing** | 1 field | A.3 (free) | Exact replay, deduplication |
| **Cross-task normalization** | 1 metric | B (free) | Fair comparison across families |
| **Gap → primitive pipeline** | C.3 | C | Self-generating roadmap |

**All free** — just read existing `cells.jsonl` with 1-2 SQL queries.

---

## 📈 Success Metrics (Consolidated)

| Metric | Baseline (TODO101) | Target (TODO102) | Measurement |
|--------|-------------------|------------------|-------------|
| Rung 3 claims | 8 | 18+ | `grep "rung3_verdict.*claim" results/sec/*.json \| wc -l` |
| Geometries viable MNIST | 7/12 | 12/12 | Capability gate geometry subset |
| Substrates with Rung 2 | 0 | 4 | Specialized task results |
| Refusal rate | ~40% | <15% | `cells.jsonl` status counts |
| Claims/GPU-hour | ~0.5 | ≥2.0 | Meta-SEC objective |
| Void rules hand-coded | ~20 | 0 (learned) | `void_rules_learned.py` |
| Primitive proposals | 0 | 3+ | `registry.py unavailable_reason="proposed"` |
| Capability gaps | 5 | 0 | All fixed or proposed |

---

## 🛠 Implementation Checklist (Ordered by Dependency)

### Week 1: Track A (Parallel)
- [x] **A.1.1** Fix DEF-012: `experiment/schema/seed_registries.py` — removed `nonlayered_instantaneous_gradient_credit` void constraint (tile + instantaneous + gradient now allowed)
- [x] **A.1.2** Fix DEF-013: `experiment/kernel/search_space.py` — added `routing_compatible_credits()` function (13 compatible credits for routing geometry)
- [x] **A.2.1** `domains/neuromorphic.py` (spiking_mnist, dvs_gestures)
- [x] **A.2.2** `domains/photonic.py` (optical_mnist_sim)
- [x] **A.2.3** `domains/quantum.py` (quantum_circuit_learning)
- [x] **A.2.4** `domains/analog.py` (memristor_simulation)
- [ ] **A.3** Verify capability gate 56/56 (pending full capability test run)

### Week 2: Track B (Parallel after A)
- [ ] **B.1** Geometry Rung 2/3 batched (7 prims × MNIST + iris)
- [ ] **B.2** temporal_psi: add `trace_decay_schedule` hyperparam → Rung 2/3
- [ ] **B.3** Substrate Rung 2/3 on 4 specialized tasks

### Week 3-4: Track C (Continuous from Week 1)
- [ ] **C.1** `meta_sec.py` — Bayesian opt on SEC hyperparams
- [ ] **C.2** Learned void rules from `cells.jsonl`
- [ ] **C.3** Gap→primitive pipeline (temporal_psi, causal_transformer, conv)
- [ ] **C.4** Budget allocation policy from cost model

---

## 🎯 TODO102 Deliverable: Self-Improving Computronium

```
┌────────────────────────────────────────────────────────────────┐
│                    COMPUTRONIUM v2 (Self-Improving)           │
├────────────────────────────────────────────────────────────────┤
│  Primitives (75)  ──SEC──▶  Capability Map  ──Meta-SEC──▶    │
│       ▲                                    │                  │
│       │                                    ▼                  │
│       └────── Void Rules (learned) ◀─── New Configs          │
│       └────── Primitive Proposals ◀─── Gap Analysis          │
│       └────── Budget Policy (learned) ◀─── Cost Model        │
└────────────────────────────────────────────────────────────────┘
```

**The system now:**
1. **Measures** everything (cells.jsonl = complete history)
2. **Learns** void rules from refusals (not hand-coded)
3. **Proposes** primitives from gaps (not human-guessed)
4. **Optimizes** its own SEC config (not fixed constants)
5. **Allocates** budget from cost models (not static splits)

---

*TODO102: Consolidated, parallelized, instrumented. The loop improves itself.*