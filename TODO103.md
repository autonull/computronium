# TODO103 — Self-Improving System: Rung 3 Claims, Hardcoded Removal & Competitive Runs

**Status:** 2026-11-24. Phase 6.4 (serial full competitive run) complete: 23/75 viable, 1 claim, 21 coordinates. **Defects it exposed are now tracked in [`TODO104.md`](TODO104.md)** (settle recompile crash, timeout thread leak, meta-SEC invalid objective/seed floor, registration box mismatch, lost-result durability, remaining hardcoded defaults).

**Superseded:** the open work lives in [`TODO104.md`](TODO104.md) (Phases 1–8,
progress log). This file stays as the record of what the run established; its
consolidated checklist in §E is historical, not the live queue.

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
- [x] **1.1** `GeometryConfig.causal_transformer`: Remove `image_hw`, `in_channels` defaults; make required
- [x] **1.2** `GeometryConfig.conv`: Remove `in_channels`, `input_hw`, `pool_hw` defaults; make required
- [x] **1.3** `GeometryConfig.nca`: Remove `grid_hw` default; make required
- [x] **1.4** Update `_geometry_builders.py` to error if required params missing (no silent defaults)
- [x] **1.5** Run capability gate: verify 75/75 still pass (now using task-derived params)
  - ✅ conv, nca, causal_transformer pass on MNIST with task-derived params
  - ✅ feedforward, recurrent, graph, tile, tile_mesh, ntm, attention, spatial_lattice, routing pass
  - ✅ instantaneous, energy_minimization, spike_integration, pc_alm, predictive_settling, error_predictive_coding pass
  - ⚠️ lazy, diffusion timeout (pre-existing, not related to our changes)
  - ✅ 73/75 pass (2 known timeouts: lazy, diffusion; rtrl_reference runs but slow)

### Phase 2: Enrich BASE_BOXES (Single Source of Truth)
- [x] **2.1** Add `geometry.input_hw=(28,28)`, `geometry.in_channels=1` to `vision` base_coordinate
- [x] **2.2** Add spatial params to `sequence`, `neuromorphic`, `photonic`, `quantum`, `scientific` base_coordinate
- [x] **2.3** Add `geometry.edge_index` from task to `graph` base_coordinate (via `TaskShape`) — not needed (graph uses own task)
- [x] **2.4** Run SEC screen: verify refusal rate drops (spatial compatibility no longer missing)

### Phase 3: Verify Fallback Paths
- [x] **3.1** `screen_coordinate`: Passes `shape` to `_coordinate` → `_params_for` — verified
- [x] **3.2** `_fallback_coordinate`: Ensure it passes `shape` to `_coordinate` — fixed via `screen_coordinate` fallback
- [x] **3.3** `_iter_legal_coordinates`: Verify `shape` threaded through to `_coordinate` — verified (passed to `_coordinate`)
- [x] **3.4** Test: Run capability gate with fallback path — verified (conv, nca, causal_transformer pass)

### Phase 4: Rung 3 Claims (Competitive Evidence)
- [x] **4.1** Geometry: Run Rung 3 (paired n=5) on 8 viable MNIST primitives + 4 iris primitives
  - ✅ MNIST: feedforward, nca, gradient, pepita, euclidean, adam, lion, muon (4 credit, 2 geometry, 2 update)
  - ✅ Iris: adam, euclidean, lion, muon (4 update) - muon claims d>0.8
  - ✅ MNIST additional: local_goodness, random_projections (claim)
  - ⏭️ Skipped: forward_tangent (too slow, estimator_samples), thermodynamic_contrast (void constraint)
- [x] **4.2** Plasticity: temporal_psi Rung 2 ladder → Rung 3 (coordinate)
- [x] **4.3** Substrate: Rung 3 on specialized tasks
  - ✅ spiking_mnist: neuromorphic substrate (coordinate)
  - ✅ memristor_simulation: memristive substrate (coordinate)
  - ⏭️ optical_mnist: no base family
- [x] **4.4** Auto-register claims: Script reads best ladder point → writes `configs/preregistrations/sec_*.json`
  - ✅ Created sec_primitive_parameter_update_muon_iris.json (min_d=0.5)
  - ✅ Created sec_primitive_credit_assignment_random_projections_mnist.json (min_d=0.8)

### Phase 5: Track C Completion (Recursive Loop)
- [x] **5.1** **C.3** Gap→primitive pipeline:
  - ✅ temporal_psi: Rung 3 complete (trace_decay, coordinate)
  - ✅ causal_transformer: Capability test passes on MNIST (vision)
  - ✅ conv: Capability test passes on MNIST with auto-derived params
  - ⏭️ Output: Primitive proposals in `registry.py` with `unavailable_reason="proposed"`
- [x] **5.2** **C.4** Budget allocation policy:
  - ✅ Query `cells.jsonl`: 579 measured cells with walltime
  - ✅ Fit linear regression: `walltime_s` ~ `log(param_count) + geometry + dynamics + credit + update`
  - ✅ R² = 0.29, model saved to `configs/cost_model.pkl`
  - ⏭️ Replace static `ADAPTIVE_L0_SHARE` with per-primitive cost model
  - ⏭️ Validate on held-out wave

### Phase 6: Meta-SEC Production Run
- [x] **6.1** Run `meta_sec.py` with 5 trials on full `cells.jsonl` (1388 cells)
  - Best params: 4 ladder points (log-spaced -1.1 to 1.5), 3 claim seeds, L0_L2 fidelity, semaphore=8
  - Family-specific min_d: vision=1.09, tabular=0.55, neuromorphic=0.55, etc.
- [x] **6.2** Apply best params: saved to `configs/meta_sec_best.json`
- [x] **6.3** Run `learn_void_rules.py` on full dataset → `configs/void_rules_learned.py`
  - 20 ADD rules (e.g., neuromorphic substrate void constraints)
  - 20+ REMOVE rules (e.g., spectral_constrained update no longer void)
- [x] **6.4** Full SEC competitive run with learned void rules + meta-SEC params
  - ✅ Learned void rules applied (20 ADD, 20+ REMOVE rules registered)
  - ✅ Meta-SEC best params loaded (4 ladder points log-spaced -1.1→1.5, L0_L2, per-family min_d)
  - ✅ Rung 1 ladder at L0 (1 epoch); Rung 2 paired comparison at 5 seeds (pre-registration floor)
  - ✅ Scripts: `scripts/run_full_sec_competitive.py` + `scripts/run_sec_axes_serial.sh`
  - 📊 Baseline concurrent run (semaphore≥2, one process): 6/75 viable, 4 coords, 0 claims, **133 rung timeouts** — concurrency thrashes dynamo on one GPU (infrastructure artifact, not a mechanism verdict)
  - 📊 **Serial authoritative run** (one process per axis, semaphore=1): `results/sec/serial/`
    - credit: 5/19 viable, 4 coords
    - dynamics: 1/8 viable, **1 claim** (`energy_minimization` on MNIST: d=31.1, CI [0.0151, 0.0158], p=0.0076)
    - geometry: 5/12 viable, 5 coords
    - update: **8/18 viable, 8 coords** (was 0/18 all timeout)
    - plasticity: 1/8 viable, 1 coord
    - substrate: 3/10 viable, 3 coords
    - **TOTAL: 23/75 viable, 1 claim, 21 coords, 0 defects**
  - 🐞 Defects found (named, not mechanism verdicts):
    - neuromorphic/quantum/sequence/continual settle kernel: `_eqprop_settle_chunk` recompiles past dynamo limit → leaked semaphore, process dies (skip list; re-run after fix)
    - `adafactor`/`natural_gradient` on MNIST: hang past the per-primitive watchdog (settle/SVD path)
    - update primitives with unavailable knobs (`mean_norm`, `role_split`, `orthogonal`) refuse as "inactive hyperparameters" — box-builder supplies knobs the primitive does not accept

---

## 📈 Success Metrics (Consolidated)

| Metric | Baseline (TODO102) | Target (TODO103) | Measurement |
|--------|-------------------|------------------|-------------|
| Rung 3 claims | 0 | 18+ | serial run: **1** (`energy_minimization` MNIST d=31.1) |
| Rung 3 claims achieved | 2 (muon on iris, random_projections on MNIST) | 1 new (energy_minimization MNIST) | `results/sec/serial/` |
| Serial viable primitives | 6/75 (concurrent baseline) | 23/75 | `results/sec/serial/full_competitive_results.json` |
| Coordinate results | 4 | 21 | serial summary |
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

## 📋 Consolidated Checklist — regenerated 2026-11-25

`TODO104.md` §E is the live checklist; this regenerates TODO103's own items
against the measured evidence, each row naming where its verdict lives.

| TODO103 item | Verdict | Evidence |
|---|---|---|
| 1.1 `causal_transformer` factory defaults (`image_hw`, `in_channels`) | ✅ | the factory takes `image_hw=None`; a cell derives it from the task's shape (`_apply_task_spatial`, `sec_loop.py`) |
| 1.2 `conv` factory defaults | ✅ | `in_channels`/`input_hw` are required; `_derive_conv_params` reads `channel_count`/`spatial_extent` |
| 1.3 `nca` `grid_hw` default | ✅ | required; `_derive_nca_params` derives the grid from the task's shape |
| 1.4 builders error on a missing structural fact | ✅ | `build_spatial_lattice_config`/`build_graph_config` raise by name; lock `test_geometry_shape_source_lock.py` |
| 1.5 "75/75 pass" | ⚠️ restated | the map is 52/75 viable+blind (`results/sec/serial3`); `comp gate breadth` PASSes (17/17 error-aware credits on ≥2 families) |
| 2.1 vision `base_coordinate` spatial params | ✅ | declared; a non-base task in the family now overrides them with its own shape (A10) |
| 2.2 sequence/neuromorphic/photonic/quantum/scientific spatial params | ✅ | stale mnist extents removed from `sequence`/`scientific`; every other row derives from its task |
| 2.3 graph `base_coordinate.edge_index` | ❌ rejected | connectivity is the task's data; `compose_configs` extracts it and the builder refuses a cell that declares none (B5) |
| 2.4 refusal rate <5% | ❌ unmet | 41 refused of 229 serial rungs (17.9%), each with a named reason (`natural_gradient` L0 cost, void rules) |
| 3.1–3.3 `screen_coordinate`/fallbacks thread the task's shape | ✅ | `_params_for`/`screen_coordinate` apply `_apply_task_spatial`; lock `test_params_for_reads_the_tasks_extent` |
| 3.4 fallback-path test | ✅ | same lock; probe `scripts/probes/todo104_non_mnist_shape.py` trains usps/conv and digits/nca |
| 4.1–4.4 Rung 3 claims from the TODO103 run | ❌ artifact | every 2026-11-24 rung-2 pair ran one seed (A11), so its 21 coordinates and 1 claim carry no power statement |
| 5.1 gap→primitive pipeline | ✅ | `temporal_psi`/`causal_transformer`/`conv` are live primitives |
| 5.2 cost model (`R²=0.29`, saved pkl) | ✅ replaced | the offline `configs/cost_model.pkl` had no reader and is deleted; the wave prices from the fidelity's measured cells and the positive control |
| 6.1–6.3 meta-SEC + void rules | ✅ | `meta_sec_best.json` = 3.589, `valid=true`, `claim_seeds=7` (was 0.0) |
| 6.4 serial competitive run | ✅ re-measured | `results/sec/serial3`: 52/75 viable+blind, 1 claim, 21 coordinates; the claim is `dynamics/energy_minimization` on MNIST |

TODO103's success table (18+ claims, 12/12 MNIST geometries, claims/GPU-hour
≥3) is superseded by TODO104 §D: the binding constraint is A22 — a claim needs
`d - 1.96/√n > min_d`, and the declared vision minimum 0.916 needs n≈9800
pairs at the measured effect — not the number of viable primitives.
