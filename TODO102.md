# TODO102 — Self-Improving System: Hygiene, Specialized Tasks & Recursive Optimization

**Status:** 2026-11-23. TODO101 complete (breadth + 8 Rung 3 claims). Next: hygiene pass, specialized tasks, recursive self-improvement.

**Principle:** The system improves itself. Every defect fixed widens capability. Every measurement feeds the next rung. The map is the artifact; the loop is the engine.

---

## 🎯 Scope: From Breadth → Depth → Self-Improvement

| Phase | Focus | Deliverable |
|-------|-------|-------------|
| **Hygiene** | Fix DEF-012, DEF-013 | All 12 geometries viable on MNIST |
| **Phase 6** | Specialized substrate tasks | Neuromorphic/photonic/quantum Rung 1 |
| **Phase 7** | Geometry Rung 2/3 claims | 6+ geometry claims at matched boxes |
| **Phase 8** | Recursive SEC | System runs SEC on itself (meta-learning) |
| **Phase 9** | Capability gap closure | temporal_psi, causal_transformer, conv, routing, tile |

---

## 📋 Phase H: Hygiene Pass (Immediate — unblocks Geometry claims)

### DEF-012: Tile void constraint
**Problem:** `tile` + `instantaneous` + `gradient` refused by `nonlayered_instantaneous_gradient_credit` void rule.
**Root Cause:** Tile geometry is non-layered (modular), but void rule expects layered geometry for gradient credit.
**Fix:** Update void rule in `legality/void_rules.py` to allow tile/tile_mesh with gradient when `num_layers ≥ 2`.
**Test:** `pytest tests/primitives/test_primitive_capability.py -k "tile" -n 1`

### DEF-013: Routing credit defect
**Problem:** `routing` geometry fails with `gradient` credit: "no gradient reached target indices".
**Root Cause:** Mixture-of-experts routing detaches gradients; gradient credit requires full graph connectivity.
**Fix:** Update `kernel/search_space.py` compatibility matrix: routing geometry incompatible with gradient credit; declare compatible credits (pc_alm, target_inversion, random_projections).
**Test:** `pytest tests/primitives/test_primitive_capability.py -k "routing" -n 1`

**Hygiene Exit Criteria:**
- [ ] DEF-012 fixed: tile, tile_mesh viable on MNIST with gradient
- [ ] DEF-013 fixed: routing viable on MNIST with compatible credit
- [ ] All 12 geometries Rung 1 viable on MNIST (no refused except task-family)
- [ ] Capability gate: 56/56 pass (geometry + plasticity + dynamics + update + substrate)

---

## 📋 Phase 6: Substrate Specialized Tasks (Unblocks Substrate Rung 3)

**Status:** DEF-010 — No task implementations for neuromorphic, photonic, quantum, analog families.

| Substrate | Target Task Family | Task Needed | Status |
|-----------|-------------------|-------------|--------|
| neuromorphic | neuromorphic | spiking_mnist, dvs_gestures | ⬜ |
| photonic | photonic | optical_mnist_sim | ⬜ |
| quantum | quantum | quantum_circuit_learning | ⬜ |
| analog/memristive | analog | memristor_simulation | ⬜ |
| ternary | neuromorphic | spiking_mnist | ⬜ |
| sparse | vision/tabular | (existing MNIST/iris work) | ✅ |

**Implementation Pattern** (per `domains/factory.py`):
```python
# domains/neuromorphic.py
@register_task
def spiking_mnist() -> TaskSpecEnriched:
    return TaskSpecEnriched(
        name="spiking_mnist",
        domain=DomainType.NEUROMORPHIC,
        task_families=("neuromorphic",),
        input_shape=(2, 28, 28, 20),  # (polarity, H, W, time_bins)
        output_dim=10,
        primary_objective="validation_accuracy",
        pass_bar=0.10,  # chance = 1/10
        resolution=10_000,
        geometry_hint="neuromorphic",
        cost_class=CostClass.EXPENSIVE,
    )
```

**Phase 6 Exit Criteria:**
- [ ] 4+ specialized tasks implemented (one per substrate family)
- [ ] Each substrate runs Rung 1 on its declared family
- [ ] Substrate Rung 2/3 claims on specialized tasks

---

## 📋 Phase 7: Geometry Rung 2/3 Claims (Depth on Viable Primitives)

**Viable Geometries on MNIST (from TODO101):** attention (0.910), feedforward (0.913), recurrent (0.913), ntm (0.872), tile_mesh (0.898), spatial_lattice (0.908), nca (0.893)

**Action per primitive:**
1. Run Rung 2 ladder (hidden_dim, num_layers) on MNIST + iris
2. Pre-register paired comparison vs feedforward baseline
3. Run Rung 3 (n=5 seeds, paired CI)

**Priority Order:**
| Geometry | MNIST Best | Iris Best | Claim Target |
|----------|------------|-----------|--------------|
| attention | 0.910 | 0.933 | vision ≥ 0.8 |
| recurrent | 0.913 | 0.933 | sequence ≥ 0.8 |
| feedforward | 0.913 | 1.0 | baseline (no claim) |
| spatial_lattice | 0.908 | 0.967 | vision ≥ 0.8 |
| tile_mesh | 0.898 | 0.967 | vision ≥ 0.8 |
| nca | 0.893 | — | vision ≥ 0.8 |
| ntm | 0.872 | 0.867 | sequence ≥ 0.8 |

**Phase 7 Exit Criteria:**
- [ ] 6+ geometry Rung 2 coordinates
- [ ] 4+ geometry Rung 3 claims (d ≥ 0.8 vision, d ≥ 0.5 tabular)
- [ ] Claims recorded in `configs/preregistrations/sec_geometry_*.json`

---

## 📋 Phase 8: Recursive SEC — System Runs SEC on Itself (Meta-Learning)

**Core Idea:** The SEC loop is a fixed point. The system should optimize its own SEC configuration.

### 8.1: Meta-Parameter Optimization
Optimize SEC hyperparameters via SEC itself:
- `LADDER_FACTORS` (currently 0.1, 1.0, 10.0)
- `CLAIM_SEEDS` (currently 5)
- `MIN_EFFECT_SIZE_BY_FAMILY` (currently 0.8 vision, 0.5 tabular)
- `semaphore_limit` (concurrency)
- Fidelity schedule (L0→L1→L2 promotion rules)

### 8.2: Search Space Auto-Tuning
- Use SEC results to prune void regions of search space
- Learn compatibility rules from measured refusals (not hand-coded)
- Auto-generate `void_rules.py` from empirical data

### 8.3: Primitive Generation
- System proposes new primitive configurations from gaps
- Example: "temporal_psi fails on vision → propose trace_decay schedule primitive"
- Validate via Rung 0→1 before human review

### 8.4: Budget Allocation Learning
- Learn per-primitive cost models from walltime measurements
- Optimize wave sizing: `n_wave = budget / (measured_cost × seed_plan)`
- Replace static `ADAPTIVE_L0_SHARE` with learned policy

**Phase 8 Exit Criteria:**
- [ ] SEC hyperparameters tuned via SEC (meta-Rung 1)
- [ ] Search space pruning reduces refused cells by ≥ 50%
- [ ] Budget allocation policy beats static 30/50% L0 split
- [ ] At least 1 auto-generated primitive clears Rung 1

---

## 📋 Phase 9: Capability Gap Closure (From Measurements)

| Gap | Primitive | Root Cause | Proposed Fix |
|-----|-----------|------------|--------------|
| temporal_psi -0.47pp vs null | temporal_psi | trace_decay static; needs schedule | Add `trace_decay_schedule` hyperparam (exponential/linear decay) |
| causal_transformer on lm | causal_transformer | No embedding layer for token indices | Add `embedding_dim` to causal_transformer factory; declare `reads_tokens=True` |
| conv below bar (0.319) | conv | Flattened MNIST (784) not spatial; needs `input_hw=(28,28)` | Fix own_knob_params to pass `input_hw` from task shape |
| routing gradient defect | routing | MoE detaches gradients | Already in DEF-013 (hygiene) |
| tile void constraint | tile | Non-layered + gradient refused | Already in DEF-012 (hygiene) |

**Phase 9 Exit Criteria:**
- [ ] temporal_psi closes gap or documents as capability gap with fix primitive
- [ ] causal_transformer viable on lm (with embedding)
- [ ] conv viable on MNIST (with spatial shape)
- [ ] All gaps have named mechanism + failing test or documented fix primitive

---

## 📊 Compounded Impact Projection

| Metric | TODO101 (Current) | TODO102 Target | TODO103 (Recursive) |
|--------|-------------------|----------------|---------------------|
| Rung 3 claims | 8 | 18+ | 30+ (auto) |
| Geometries viable | 7/12 MNIST | 12/12 MNIST | 12/12 all families |
| Substrates with claims | 0 | 4 (specialized) | 6+ |
| Search space efficiency | ~40% refused | <20% refused | <5% refused (learned) |
| Capability gaps | 5 documented | 0 (fixed or primitive) | Self-identified |
| SEC meta-parameters | Fixed | Tuned via SEC | Self-optimizing |

---

## 🔄 Self-Improvement Loop Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPUTRONIUM SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Primitives │───▶│  SEC Loop   │───▶│ Capability  │     │
│  │  (75 axes)  │    │  (map)      │    │  Map        │     │
│  └─────────────┘    └──────┬──────┘    └──────┬──────┘     │
│                            │                    │            │
│                            ▼                    ▼            │
│                   ┌──────────────────────────────────┐      │
│                   │      META-SEC (Phase 8)          │      │
│                   │  • Tunes SEC hyperparams         │      │
│                   │  • Prunes search space           │      │
│                   │  • Proposes new primitives       │      │
│                   │  • Learns budget allocation      │      │
│                   └──────────────────────────────────┘      │
│                            │                    │            │
│                            ▼                    ▼            │
│                   ┌─────────────┐    ┌─────────────┐         │
│                   │ New Config  │    │ New Primitive│        │
│                   │ (SEC.yaml)  │    │ (auto-gen)  │        │
│                   └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

**Implementation:** `computronium/experiment/meta_sec.py`
- Reads `results/sec/map.json` + `results/sec/cells.jsonl`
- Runs SEC on SEC configuration space
- Outputs: updated `sec_all_axes.py` params, new void rules, primitive proposals

---

## 📋 Execution Order (Dependency-Aware)

```
Hygiene (H) ──▶ Phase 6 ──▶ Phase 7 ──▶ Phase 8 ──▶ Phase 9
   │            │           │           │           │
   │            │           │           │           └── Requires H, 7
   │            │           │           └───────────── Requires 6, 7
   │            │           └──────────────────────── Requires H
   │            └───────────────────────────────────── Independent
   └────────────────────────────────────────────────── Independent
```

**Parallelizable:** H + Phase 6 (independent)
**Sequential:** Phase 7 needs H; Phase 8 needs 6+7; Phase 9 needs H+7

---

## 🛠 Implementation Checklist

### Hygiene (Week 1)
- [ ] Fix DEF-012: `legality/void_rules.py` — allow tile/tile_mesh with gradient when layered
- [ ] Fix DEF-013: `kernel/search_space.py` — routing incompatible with gradient credit
- [ ] Run capability gate: 56/56 pass

### Phase 6 (Week 2-3)
- [ ] Implement `domains/neuromorphic.py` (spiking_mnist, dvs_gestures)
- [ ] Implement `domains/photonic.py` (optical_mnist_sim)
- [ ] Implement `domains/quantum.py` (quantum_circuit_learning)
- [ ] Implement `domains/analog.py` (memristor_simulation)
- [ ] Run substrate Rung 1 on each specialized task

### Phase 7 (Week 3-4)
- [ ] Run geometry Rung 2 ladders (7 primitives × 2 tasks)
- [ ] Pre-register 7 claims in `configs/preregistrations/`
- [ ] Run Rung 3 paired comparisons (n=5)

### Phase 8 (Week 4-6)
- [ ] Implement `computronium/experiment/meta_sec.py`
- [ ] Define SEC meta-search space (LADDER_FACTORS, CLAIM_SEEDS, MIN_EFFECT_SIZE, etc.)
- [ ] Run meta-Rung 1 on SEC config space
- [ ] Implement search space pruning from empirical refusals
- [ ] Implement primitive proposal from gap analysis

### Phase 9 (Week 5-6)
- [ ] Fix temporal_psi: add `trace_decay_schedule` hyperparam
- [ ] Fix causal_transformer: add embedding layer + `reads_tokens=True`
- [ ] Fix conv: pass `input_hw` from task shape in own_knob_params
- [ ] Verify all gaps closed or documented with fix primitives

---

## 📈 Success Metrics (Per Phase)

| Phase | Metric | Target |
|-------|--------|--------|
| H | Capability gate pass rate | 56/56 |
| 6 | Substrates with Rung 1 data | 4/4 specialized families |
| 7 | Geometry Rung 3 claims | ≥4 (d ≥ 0.8 vision) |
| 8 | Meta-SEC improves walltime | ≥2× cells/budget |
| 8 | Search space refusal rate | <20% |
| 9 | Capability gaps remaining | 0 |

---

*TODO102 continues the SEC loop. The system improves itself. Every measurement feeds the next rung. The map is the artifact; the loop is the engine.*