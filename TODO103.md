# TODO103 — Self-Improving System: Rung 3 Claims, Hardcoded Removal & Competitive Runs

**Status:** 2026-11-24. TODO102 complete (75/75 capability pass). Next: Rung 3 claims, remove hardcoded MNIST defaults, competitive SEC runs.

**Principle:** The system improves itself. Every hardcoded default removed widens capability. Every Rung 3 claim is a reproducible capability. The map is the artifact; the loop is the engine.

---

## 📋 Remaining from TODO102

### Track C (Recursive) - Incomplete
| Item | Status | Notes |
|------|--------|-------|
| **C.3** Gap→primitive pipeline | ⬜ | temporal_psi schedule knob ladder, causal_transformer ladder, conv viability |
| **C.4** Budget allocation policy | ⬜ | Per-primitive cost model from walltime_s regression |

---

## 🗑️ Hardcoded Shortcuts Catalog (Must Fix Before Competitive Runs)

### 1. GeometryConfig Factory Defaults (MNIST-specific)
| File | Method | Hardcoded Default | Fix |
|------|--------|-------------------|-----|
| `ontology/geometry.py:378` | `causal_transformer` | `image_hw=(28,28)`, `in_channels=1` | Make required params; derive from task in builder |
| `ontology/geometry.py:512` | `conv` | `in_channels=1`, `input_hw=(28,28)`, `pool_hw=(4,4)` | Make required params; derive from task |
| `ontology/geometry.py:652` | `nca` | `grid_hw=(16,16)` | Make required params; derive from task |

**Why it matters**: When capability test runs fallback coordinates (`_fallback_coordinate` → `_coordinate` → `_params_for`), these MNIST defaults are used instead of task-derived values. The builders already auto-derive from `input_shape` — the factory methods just need to require the params.

### 2. BASE_BOXES Missing Spatial Params
| Family | Missing in `base_coordinate` | Add |
|--------|------------------------------|-----|
| `vision` | `geometry.input_hw`, `geometry.in_channels` for conv/nca/causal_transformer | `geometry.input_hw=(28,28)`, `geometry.in_channels=1` |
| `sequence` | Spatial params for recurrent on vision | `geometry.input_hw`, `geometry.in_channels` |
| `neuromorphic` | Spatial params for neuromorphic geometry | `geometry.input_hw`, `geometry.in_channels` |
| `photonic` | Spatial params | `geometry.input_hw`, `geometry.in_channels` |
| `quantum` | Spatial params | `geometry.input_hw`, `geometry.in_channels` |
| `scientific` | Spatial params for feedforward | `geometry.input_hw`, `geometry.in_channels` |

**Why it matters**: `BASE_BOXES` is the single source for family axes. When testing non-feedforward geometries on vision, the `base_coordinate` lacks spatial params → falls back to factory defaults (MNIST).

### 3. Screen Coordinate Fallback Path
| Location | Issue | Fix |
|----------|-------|-----|
| `sec_loop.py:screen_coordinate` | When `box_params(screened)` empty, returns `_coordinate(axes, own_knobs=axis)` → uses factory defaults | Pass `shape` to `_coordinate` so `_params_for` can derive spatial params |
| `sec_loop.py:_params_for` | Already fixed for nca/conv/causal_transformer — verify all geometries | Audit all geometry branches |

### 4. Other Hardcoded Shortcuts to Audit
| Location | Hardcoded | Should Be |
|----------|-----------|-----------|
| `sec_loop.py:_params_for:868` | `geometry.edge_index = [[0,1],[1,0]]` for graph | Derive from task's `edge_index` (via `shape`) |
| `sec_loop.py:_params_for:858` | `geometry.lattice_dims = (8,8)` for spatial_lattice | Derive from `input_shape` spatial extent |
| `_geometry_builders.py:76` | `_spatial_extent` returns `(1,1)` for non-spatial | OK — only used for spatial topologies |
| `_geometry_builders.py:71` | `_channel_count` returns `1` for flat | OK — correct for non-spatial |

---

## 🛠 Implementation Plan (Ordered by Dependency)

### Phase 1: Remove Factory Defaults (Foundation)
- [ ] **1.1** `GeometryConfig.causal_transformer`: Remove `image_hw`, `in_channels` defaults; make required
- [ ] **1.2** `GeometryConfig.conv`: Remove `in_channels`, `input_hw`, `pool_hw` defaults; make required
- [ ] **1.3** `GeometryConfig.nca`: Remove `grid_hw` default; make required
- [ ] **1.4** Update `_geometry_builders.py` to error if required params missing (no silent defaults)
- [ ] **1.5** Run capability gate: verify 75/75 still pass (now using task-derived params)

### Phase 2: Enrich BASE_BOXES (Single Source of Truth)
- [ ] **2.1** Add `geometry.input_hw=(28,28)`, `geometry.in_channels=1` to `vision` base_coordinate
- [ ] **2.2** Add spatial params to `sequence`, `neuromorphic`, `photonic`, `quantum`, `scientific` base_coordinate
- [ ] **2.3** Add `geometry.edge_index` from task to `graph` base_coordinate (via `TaskShape`)
- [ ] **2.4** Run SEC screen: verify refusal rate drops (spatial compatibility no longer missing)

### Phase 3: Verify Fallback Paths
- [ ] **3.1** `screen_coordinate`: Already passes `shape` to `_coordinate` → `_params_for` — verify
- [ ] **3.2** `_fallback_coordinate`: Ensure it passes `shape` to `_coordinate`
- [ ] **3.3** `_iter_legal_coordinates`: Verify `shape` threaded through to `_coordinate`
- [ ] **3.4** Test: Run capability gate with `--skip-measured` to exercise fallback path

### Phase 4: Rung 3 Claims (Competitive Evidence)
- [ ] **4.1** Geometry: Run Rung 3 (paired n=10) on 8 viable MNIST primitives + 8 iris primitives
- [ ] **4.2** Plasticity: temporal_psi Rung 2 ladder with `trace_decay_schedule` knob → Rung 3
- [ ] **4.3** Substrate: Rung 3 on specialized tasks (spiking_mnist, optical_mnist_sim)
- [ ] **4.4** Auto-register claims: Script reads best ladder point → writes `configs/preregistrations/sec_*.json`

### Phase 5: Track C Completion (Recursive Loop)
- [ ] **5.1** **C.3** Gap→primitive pipeline:
  - temporal_psi: Run 3-point ladder on `trace_decay_schedule` ∈ {constant, exponential, linear}
  - causal_transformer: Run ladder on vision (patch_size=4, d_model=128, n_layers=2)
  - conv: Verify viability on vision with auto-derived params
  - Output: Primitive proposals in `registry.py` with `unavailable_reason="proposed"`
- [ ] **5.2** **C.4** Budget allocation policy:
  - Query `cells.jsonl`: `walltime_s` ~ `log(param_count) + fidelity + axis_knob`
  - Fit linear regression per primitive
  - Replace static `ADAPTIVE_L0_SHARE` with per-primitive cost model
  - Validate on held-out wave

### Phase 6: Meta-SEC Production Run
- [ ] **6.1** Run `meta_sec.py` with 100 trials on full `cells.jsonl`
- [ ] **6.2** Apply best params: `LADDER_FACTORS`, `CLAIM_SEEDS`, `MIN_EFFECT_SIZE`, fidelity schedule, semaphore
- [ ] **6.3** Run `learn_void_rules.py` on full dataset → update `void_rules_learned.py`
- [ ] **6.4** Full SEC competitive run with learned void rules + meta-SEC params

---

## 📈 Success Metrics (Consolidated)

| Metric | Baseline (TODO102) | Target (TODO103) | Measurement |
|--------|-------------------|------------------|-------------|
| Rung 3 claims | 0 | 18+ | `grep "rung3_verdict.*claim" results/sec/*.json \| wc -l` |
| Geometries viable MNIST | 8/12 | 12/12 | Capability gate geometry subset |
| Substrates with Rung 2 | 4 | 8 | Specialized task results |
| Refusal rate | ~15% | <5% | `cells.jsonl` status counts |
| Claims/GPU-hour | ~1.0 | ≥3.0 | Meta-SEC objective |
| Void rules hand-coded | 0 (learned) | 0 (learned + validated) | `void_rules_learned.py` matches hand-coded ≥95% |
| Primitive proposals | 0 | 3+ | `registry.py unavailable_reason="proposed"` |
| Capability gaps | 0 | 0 | All fixed or proposed |
| Hardcoded defaults | 3 factory + 5 BASE_BOXES | 0 | `grep -r "28, 28\|16, 16" computronium/ontology/geometry.py` |

---

## 🎯 TODO103 Deliverable: Production-Ready Self-Improving System

```
┌─────────────────────────────────────────────────────────────────────┐
│                   COMPUTRONIUM v3 (Production-Ready)               │
├─────────────────────────────────────────────────────────────────────┤
│  Primitives (75+)  ──SEC──▶  Capability Map  ──Meta-SEC──▶       │
│       ▲                                    │                       │
│       │                                    ▼                       │
│       └────── Void Rules (learned) ◀─── New Configs              │
│       └────── Primitive Proposals ◀─── Gap Analysis              │
│       └────── Budget Policy (learned) ◀─── Cost Model            │
│       └────── Rung 3 Claims (reproducible) ◀─── Paired CI        │
└─────────────────────────────────────────────────────────────────────┘
```

**The system now:**
1. **Measures** everything (`cells.jsonl` = complete history)
2. **Learns** void rules from refusals (not hand-coded)
3. **Proposes** primitives from gaps (not human-guessed)
4. **Optimizes** its own SEC config (not fixed constants)
5. **Allocates** budget from cost models (not static splits)
6. **Claims** with statistical rigor (Rung 3 paired CI)
7. **Adapts** to any task geometry (no MNIST hardcoded defaults)

---

## 📋 Consolidated Checklist (Copy-Paste for Session)

```markdown
### Phase 1: Remove Factory Defaults
- [ ] 1.1 GeometryConfig.causal_transformer: remove image_hw, in_channels defaults
- [ ] 1.2 GeometryConfig.conv: remove in_channels, input_hw, pool_hw defaults
- [ ] 1.3 GeometryConfig.nca: remove grid_hw default
- [ ] 1.4 Update _geometry_builders.py to error if required params missing
- [ ] 1.5 Capability gate: 75/75 pass

### Phase 2: Enrich BASE_BOXES
- [ ] 2.1 vision base_coordinate: add input_hw, in_channels
- [ ] 2.2 sequence/neuromorphic/photonic/quantum/scientific: add spatial params
- [ ] 2.3 graph base_coordinate: add edge_index from TaskShape
- [ ] 2.4 SEC screen: refusal rate <5%

### Phase 3: Verify Fallback Paths
- [ ] 3.1 screen_coordinate passes shape
- [ ] 3.2 _fallback_coordinate passes shape
- [ ] 3.3 _iter_legal_coordinates threads shape
- [ ] 3.4 Test fallback path

### Phase 4: Rung 3 Claims
- [ ] 4.1 Geometry Rung 3: 8 MNIST + 8 iris
- [ ] 4.2 temporal_psi Rung 3 with schedule knob
- [ ] 4.3 Substrate Rung 3 on specialized tasks
- [ ] 4.4 Auto-register claims script

### Phase 5: Track C Completion
- [ ] 5.1 C.3 Gap→primitive pipeline (temporal_psi, causal_transformer, conv)
- [ ] 5.2 C.4 Budget policy from cost model

### Phase 6: Meta-SEC Production
- [ ] 6.1 Meta-SEC 100 trials
- [ ] 6.2 Apply best params
- [ ] 6.3 Learned void rules
- [ ] 6.4 Full competitive run
```