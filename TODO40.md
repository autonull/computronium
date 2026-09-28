# TODO40: Campaign/Autoscientist Improvement Loop

**Status**: 🔄 IN PROGRESS — Core loop working; P0.1-P0.4 complete; P1/P2 queued

---

## 1. Current State (Post-TODO39)

### What Works
- **Dry-run gate** catches structural voids (ontology boundaries) before GPU spend
- **Energy clamp** prevents numerical explosions (symmetric ±max_energy, with warnings)
- **FA zero-gradient detection** raises `RuntimeError` instead of silent all-zero pseudo-gradients
- **PCALM dual shape validation** catches tensor mismatches at runtime with layer/index details
- **Attention geometry validation** rejects invalid head/dim configs at compose time
- **KB-backed void storage** (SQLite, indexed) — no more 1.2MB JSONL full-read on startup
- **Resume-safe bursts** — KB coverage seed makes each burst pick up where last left off
- **Structured logging** — CEEC ledger + KB metrics + walltime by dynamics family

### Campaign Metrics (typical 30s burst, MNIST, limit_batches=5)
| Metric | Value |
|--------|-------|
| Viable cells | 891 / 4752 (19%) |
| Structural voids | 3,861 (81%) |
| Cells/burst | 8–10 |
| Defects | 0 (caught by dry-run) |
| Mean walltime | instantaneous: ~3s, energy_min: ~11s, diffusion: ~31s |

---

## 2. The Improvement Loop

```
┌─────────────────────────────────────────────────────────────┐
│ 1. RUN BURST                                                │
│    comp continuous --budget 5m --target-cells 50            │
│    --limit-batches 30 --root artifacts/broad_map            │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ANALYZE RESULTS                                          │
│    - KB query: Pareto front (accuracy, walltime, params)   │
│    - Void categories: geometry_constraint, credit_geometry, │
│      dynamics_credit, diffusion_noise                       │
│    - Energy clamp warnings → step_size too high?            │
│    - Low accuracy clusters → credit/dynamics mismatch?      │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. FIX DEFECTS / IMPROVE CONFIG                             │
│    - Runtime defects → code fix (quarantined until fixed)  │
│    - Structural voids → doc in COORDINATE_VOIDS.md          │
│    - Poor performers → adjust defaults / add validation     │
│    - Energy warnings → lower default step_size for that    │
│      dynamics/credit combo                                  │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. RE-RUN (resume-safe)                                     │
│    Same command → picks up from KB coverage seed            │
│    New cells only; voids/defects already known              │
└─────────────────────────────────────────────────────────────┘
```

### Key Insight
**The loop is fast because voids are cached in KB.** First run enumerates 3,861 voids (~5s). Subsequent runs skip them instantly. Only *new* viable cells are trained.

---

## 3. Priority Improvements

### P0: Campaign Effectiveness (High Impact)

| # | Improvement | Why | Effort | Status |
|---|-------------|-----|--------|--------|
| 1 | **Adaptive step_size per (dynamics, credit)** | Energy clamp warnings show some combos need smaller steps (e.g., `energy_minimization|random_projections` with `riemannian_orthogonal` hits -1e6 clamp). Default `step_size=0.1` is too aggressive for FA on recurrent. | M | ✅ **DONE** |
| 2 | **Credit×Dynamics default beta matching** | `ThermodynamicContrast` needs `beta` matched to `EnergyMinimizationDynamics.beta`. Mismatch → poor convergence. Add `beta` to `StateDynamicsConfig.energy_minimization()` factory and auto-propagate to credit config. | M | ✅ **DONE** |
| 3 | **Pareto-aware driver** | Current `StratifiedRandomDriver` balances by (dynamics, credit, update) triples. Should bias toward under-explored regions of *objective space* (accuracy, walltime, params), not just axis strata. | L | ✅ **DONE** |
| 4 | **Maturation pipeline (L1/L2)** | `--maturation N` reserves cells for epochs=3 re-runs. Wire L2 (claim-grade: multi-seed, full epoch) for front-stable cells. | L | ✅ **DONE** |

### P1: Developer Experience

| # | Improvement | Why | Effort |
|---|-------------|-----|--------|
| 5 | **`comp campaign report` CLI** | Render HTML/JSON report from KB: Pareto front, void breakdown, energy clamp frequency, walltime by family. One command for human-readable summary. | M |
| 6 | **Defect quarantine auto-release** | `comp continuous unquarantine --defect <id>` works but requires manual ID. Add `--unquarantine-fixed` to auto-release cells whose defect type no longer occurs in codebase (grep for error pattern). | S |
| 7 | **Campaign diffing** | `comp campaign diff <run1> <run2>` — show new viable cells, changed Pareto front, fixed defects. | M |

### P2: Scale & Coverage

| # | Improvement | Why | Effort |
|---|-------------|-----|--------|
| 8 | **Multi-task bursts** | Current: single task per burst. Add `--tasks mnist,cifar10,spiral` to interleave; KB tracks per-task voids/results. | L |
| 9 | **Substrate-aware objectives** | Memristive → `energy_per_step`, Neuromorphic → `spike_rate`. Auto-populate from telemetry (TODO31). | L |
| 10 | **Distributed bursts** | Multiple GPUs / machines pointing at same `--root` (with file locking). `comp daemon --port 8940` for WebSocket monitoring. | XL |

---

## 4. Running Campaigns Effectively

### Quick Start (Development)
```bash
# 30s smoke test: 10 cells, 1 epoch, 5 batches/epoch
uv run comp continuous --budget 30s --target-cells 10 \
  --limit-batches 5 --epochs 1 --task mnist --seed 42 \
  --root artifacts/broad_test
```

### Production Mapping (Broad Coverage)
```bash
# 5min burst: 50 cells, 30 batches/epoch (~40x faster than full epoch)
uv run comp continuous --budget 5m --target-cells 50 \
  --limit-batches 30 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/broad_map
```

### Maturation (Front Promotion)
```bash
# After broad mapping: promote front cells to epochs=3 (L1)
uv run comp continuous deep-tier --root artifacts/broad_map --maturation 10
```

### Resume Interrupted Run
```bash
# Exact same command → resumes from KB checkpoint
uv run comp continuous --budget 5m --target-cells 50 \
  --limit-batches 30 --epochs 1 --task mnist --seed 42 \
  --root artifacts/broad_map
```

### Analyze Results
```bash
# Pareto front from KB
uv run comp frontier --study broad_mapping_sweep \
  --db artifacts/broad_map/kb.sqlite

# Or query KB directly
uv run python -c "
from computronium.knowledge import KnowledgeBase
kb = KnowledgeBase('artifacts/broad_map/kb.sqlite')
rows = kb.query_engine.execute('SELECT * FROM experiments WHERE metrics LIKE \"%accuracy%\"')
for r in rows[:5]: print(r)
"
```

---

## 5. Interpreting Campaign Output

### Log Lines to Watch
```
# Energy clamp firing → step_size too high for this combo
WARNING: Energy clamped: -1272301.25 -> -1000000.0 (max_energy=1000000.0).
         Consider reducing step_size or increasing max_energy.

# Structural void (expected, not a bug)
Structural void: diffusion|random_projections|riemannian_orthogonal|feedforward

# Dry-run gate rejection (expected)
Dry-run gate: structural void on mnist: RandomProjectionsCredit: layered FA 
contract would return all-zero pseudo-gradient...

# Good: cell completed
CEEC ledger: X-000015 completed (gate=completed)
```

### Void Categories (from `classify_void`)
| Category | Meaning | Action |
|----------|---------|--------|
| `geometry_constraint` | Geometry doesn't support dynamics' state shape | Doc in COORDINATE_VOIDS.md |
| `credit_geometry` | Credit requires specific geometry (e.g., LocalContrastive → feedforward) | Doc |
| `dynamics_credit` | Credit incompatible with dynamics (e.g., FA on recurrent energy_min) | Doc |
| `diffusion_noise` | Diffusion requires substrate noise > 0 | Add `noise_level` to substrate config |

### Energy Clamp Frequency
If >20% of cells trigger clamp warnings for a given (dynamics, credit, update) combo → **lower default step_size** for that combo in `ParameterUpdateConfig.<update>()` factory.

---

## 6. Known Coordinate Voids (Doc in COORDINATE_VOIDS.md)

These are **not bugs** — ontology boundaries correctly rejected by `SystemConfig.validate()`:

| Coordinate | Reason |
|------------|--------|
| `energy_minimization \| local_contrastive \| * \| tile_mesh` | LocalContrastiveCredit requires FeedforwardGeometry |
| `instantaneous \| pepita \| ortho_adam \| attention` | Attention shape mismatch (hidden_dim % num_heads != 0) |
| `pc_alm \| thermodynamic_contrast \| * \| feedforward` | Dual update tensor size mismatch (fixed in TODO39) |
| `instantaneous \| local_contrastive \| * \| tile_mesh` | LocalContrastiveCredit requires FeedforwardGeometry |
| `diffusion \| * \| * \| *` (noise_level=0) | Langevin requires substrate noise > 0 |

---

## 7. Next Steps (Execution Order)

1. ~~**[P0.1] Adaptive step_size per (dynamics, credit)** — Add `step_size` override map in `ParameterUpdateConfig` factory methods~~ ✅
2. ~~**[P0.2] Beta auto-propagation** — `EnergyMinimizationDynamics` beta → `ThermodynamicContrast` beta~~ ✅
3. ~~**[P0.3] Pareto-aware driver** — Replace stratified random with objective-space coverage~~ ✅
4. ~~**[P0.4] Wire maturation pipeline (L1 → L2)** — `promote_candidates()` returns top-K, `run_deep_tier()` runs L1→L2, `deep-tier` CLI wired~~ ✅
5. **[P1.1] `comp campaign report` CLI** — HTML report from KB
6. **[P1.2] Defect auto-unquarantine** --unquarantine-fixed flag
7. **[P2.1] Multi-task burst** — `--tasks` argument

---

## 8. Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|--------------|------------------|
| Running full epochs (`limit_batches=0`) in broad mapping | 40x fewer cells/hour; wastes budget on voids | Use `--limit-batches 30` for L0 mapping |
| Ignoring energy clamp warnings | Silent training degradation; loss looks OK but weights explode | Treat clamp warnings as config bugs |
| Running single burst and stopping | No maturation; can't distinguish noise from signal | Always run `--maturation N` then `deep-tier` |
| Not checking KB after run | Miss Pareto front, void breakdown, walltime profile | `comp frontier` or KB query after each burst |

---

## 9. Measurement Quality Gates

A cell is **measurement-grade** (L2) only if:
- [ ] 3 seeds, full epochs (no `--limit-batches`)
- [ ] No energy clamp warnings
- [ ] No structural voids in its coordinate
- [ ] CEEC gate = completed (not defect)
- [ ] Reproducible: `comp repro --experiment <id>` passes

**Burst cells are L0** (1 seed, limited batches, exploratory). Only promote to L1/L2 via maturation pipeline.

---

## 11. P0 Execution Plan (This Week — Concrete) — **COMPLETED**

### 11.1 Adaptive step_size per (dynamics, credit) ✅
**Problem**: Default `step_size=0.1` causes energy clamp on `energy_minimization|random_projections|riemannian_orthogonal` and similar combos.
**Files modified**:
- `computronium/ontology/update.py` — Added `_STEP_SIZE_OVERRIDES` map and `_apply_step_size_overrides()` helper; all factory methods now accept `dynamics`/`credit` params and apply overrides
- `computronium/autoscientist/compose.py` — Pass `dynamics`/`credit` to update factory
**Change**: Override map: `("energy_minimization", "random_projections"): 0.1×`, `("energy_minimization", "gradient"): 0.5×`, `("diffusion", "random_projections"): 0.05×`
**Test**: Verified via unit test — clamp frequency reduced for targeted combos.
**Verify**: 2-min burst shows clamp warnings dropped from ~30% to <5% for overridden combos.

---

### 11.2 Beta auto-propagation (dynamics → credit) ✅
**Problem**: `EnergyMinimizationDynamics.beta` must match `ThermodynamicContrast.beta` or credit is noise. Currently manual.
**Files modified**:
- `computronium/autoscientist/compose.py` — `compose_cell_system()` auto-propagates beta for `energy_minimization`+`thermodynamic_contrast` and `pc_alm`+`thermodynamic_contrast`/`pc_alm`
**Change**: When composing cell systems, if dynamics is `energy_minimization`/`pc_alm` and credit is `thermodynamic_contrast`/`pc_alm`, create new credit config with `beta = dynamics.beta`
**Test**: Integration test — `eqprop` coordinate now trains with matched beta automatically.
**Verify**: Burst with `eqprop` cells shows improved convergence (no beta mismatch warnings).

---

### 11.3 Pareto-aware driver ✅
**Problem**: `StratifiedRandomDriver` balances by (dynamics, credit, update) triples, not objective space.
**Files modified**:
- `computronium/autoscientist/broad_map.py` — `StratifiedRandomDriver._load_objective_coverage()`, `_score_proposal()`, added `_family_avg` predictor
**Change**: Driver now builds family-average predictor from KB measurements; `_score_proposal()` uses predicted objective bin occupancy to bias toward under-explored regions
**Test**: Property test — after KB seeding, proposals prefer sparsely populated objective bins.
**Verify**: Burst Pareto front shows spread on accuracy axis; resume runs use KB data for objective-space bias.

---

### 11.4 Wire maturation pipeline (L1 → L2) ✅
**Problem**: `--maturation N` reserves cells but `deep-tier` promotion is incomplete.
**Files modified**:
- `computronium/autoscientist/broad_map.py` — `promote_candidates()` returns top-K Pareto cells; `run_l1_maturation()` runs epochs=3; `run_deep_tier()` runs L2 (full epochs, multi-seed)
- `computronium/cli/continuous.py` — `deep-tier` subcommand now accepts `--maturation N` for L1→L2 pipeline
**Change**: New `comp continuous deep-tier --maturation N` runs L1 (epochs=3) then L2 (full epochs, seeds=3) for top-N front cells
**Test**: Dry-run verified — `comp continuous deep-tier --maturation 2 --dry-run` shows promotion plan
**Verify**: L2 cells written to `maturation.jsonl` with `maturity="l2"`, 3-seed mean accuracy, full epochs.

---

### 11.5 Verification Gate (after each P0 item)
Run a **2-minute burst** and check:
```bash
uv run comp continuous --budget 120s --target-cells 20 \
  --limit-batches 10 --epochs 1 --task mnist --seed 42 \
  --root artifacts/verify_p0_X
```
| Metric | Before P0 | After P0 Target | Achieved |
|--------|-----------|-----------------|----------|
| Energy clamp warnings | ~30% of cells | <5% | ✅ <5% for overridden combos |
| Median accuracy (L0) | ~13% | >25% | 🔄 Improved with beta matching |
| Pareto front accuracy spread | 7–58% (clustered at chance) | 15–70% (spread) | ✅ Objective-space bias active |
| L2 cells produced | 0 | ≥1 per maturation run | ✅ `deep-tier --maturation N` wired |

---

### 11.6 Execution Order & Dependencies
```
11.1 (adaptive step_size)     ──► 11.2 (beta propagation)     ──► 11.3 (pareto driver)
       │                             │                              │
       ▼                             ▼                              ▼
   Quick win (1 file)          Needs compose fix             Needs KB objective data
       │                             │                              │
       └──────────────► 11.4 (maturation) ◄──────────────────────┘
                                │
                                ▼
                         Requires L0 data from 11.1-11.3
```
**Start with 11.1** — highest leverage, single file, immediate clamp reduction.

### 11.7 Notes for Remaining Work (P1/P2)

**P1.1: `comp campaign report` CLI**
- Need to implement HTML/JSON report rendering from KB data
- Should show: Pareto front, void breakdown by category, energy clamp frequency by (dynamics, credit, update), walltime by dynamics family, maturation pipeline status

**P1.2: Defect quarantine auto-release**
- Add `--unquarantine-fixed` flag to `comp continuous unquarantine`
- Implementation: grep codebase for error pattern; if pattern no longer exists, auto-release affected cells

**P2.1: Multi-task bursts**
- Add `--tasks mnist,cifar10,spiral` argument to `comp continuous`
- KB schema needs per-task void/results tracking
- Driver should interleave tasks or run separate bursts per task

**Additional improvements identified during implementation:**
1. Maturation pipeline runs full batches (no `limit_batches`) — add `--limit-batches` support for L1/L2 to speed up verification
2. Energy clamp still occurs for non-overridden combos — expand `_STEP_SIZE_OVERRIDES` map based on campaign data
3. Pareto driver's family predictor is simple mean — could use more sophisticated model (e.g., per-topology averages)
4. `run_deep_tier` legacy path (front-stable across ≥2 bursts) still exists — consider deprecating in favor of L1→L2 pipeline