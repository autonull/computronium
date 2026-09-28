# TODO41: Campaign → Fix → Campaign Iteration Loop

**Status**: 🟢 **ACTIVE** — Formalizing the improvement cycle established in TODO40

---

## 0. Progress Summary (2026-09-28)

### Completed Fixes

| # | Fix | File | Description |
|---|-----|------|-------------|
| 1 | **Fixed multiple VectorStore initializations** | `computronium/autoscientist/broad_map.py`, `computronium/cli/continuous.py` | Created a single shared `KnowledgeBase` instance in `build_sweep()` and passed it to `StratifiedRandomDriver`, `BroadMappingCampaign`, and `next_burst_tag()`. The `NearestNeighbors` index now initializes **once per campaign** instead of 5+ times. |
| 2 | **Fixed driver stratification to use pre-computed viable topologies** | `computronium/autoscientist/broad_map.py` | Modified `StratifiedRandomDriver` to pre-compute viable topologies per (dynamics, credit, update) triple during init, avoiding random sampling of non-viable topologies. Driver now iterates through ALL viable topologies for a triple when scoring proposals, ensuring efficient exploration. |
| 3 | **Added KB path storage in driver** | `computronium/autoscientist/broad_map.py` | Driver now stores `_kb_path` and `_kb` references to avoid re-creating KnowledgeBase instances in `_load_objective_coverage()` and `_reload_covered()`. |
| 4 | **Updated `driver_seeded_kb()` and `next_burst_tag()` to accept shared KB** | `computronium/autoscientist/broad_map.py` | Both functions now accept an optional pre-created `KnowledgeBase` instance, avoiding redundant initialization. |

### Verification
- All integration tests pass: `pytest tests/integration/test_continuous_burst.py -q` ✅ (8 passed)
- Campaign readers pass: `pytest tests/unit/test_campaign_readers.py -k "not daemon" -q` ✅ (7 passed)
- Dev-env smoke test passes ✅
- Format & lint pass ✅

---

## 1. The Loop Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. RUN BURST                                                    │
│    comp continuous --budget 5m --target-cells 50                │
│    --limit-batches 30 --root artifacts/broad_map                │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. ANALYZE RESULTS (KB + Reports)                               │
│    - KB query: Pareto front (accuracy, walltime, params)       │
│    - Void categories: geometry_constraint, credit_geometry,    │
│      dynamics_credit, diffusion_noise                          │
│    - Energy clamp warnings → step_size too high?               │
│    - Low accuracy clusters → credit/dynamics mismatch?         │
│    - Spectral radius explosions → substrate/noise issues       │
│    - Param count blowups → geometry sizing                     │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. FIX DEFECTS / IMPROVE CONFIG                                 │
│    - Runtime defects → code fix (quarantined until fixed)      │
│    - Structural voids → doc in COORDINATE_VOIDS.md             │
│    - Poor performers → adjust defaults / add validation        │
│    - Energy warnings → lower default step_size for that combo  │
│    - Substrate mismatches → auto-configure noise/precision     │
│    - Geometry blowups → respect param_budget                   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. RE-RUN (resume-safe)                                         │
│    Same command → picks up from KB coverage seed               │
│    New cells only; voids/defects already known                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: The loop is fast because voids are cached in KB. First run enumerates ~3,861 voids (~5s). Subsequent runs skip them instantly. Only *new* viable cells are trained.

---

## 2. Running Effective Campaigns

### Quick Verification (2-3 min)
```bash
uv run comp continuous --budget 120s --target-cells 20 \
  --limit-batches 10 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/verify_XXX
```

### Production Mapping (Broad Coverage)
```bash
uv run comp continuous --budget 5m --target-cells 50 \
  --limit-batches 30 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/broad_map
```

### Maturation (Front Promotion)
```bash
uv run comp continuous deep-tier --root artifacts/broad_map --maturation 10
```

### Multi-Task
```bash
uv run comp continuous --tasks mnist,cifar10,spiral \
  --budget 5m --target-cells 50 --root artifacts/broad_map
```

### Substrate-Aware
```bash
uv run comp continuous --substrate memristive \
  --budget 5m --target-cells 50 --root artifacts/broad_map
```

---

## 3. Analysis Commands

### KB Report (HTML + JSON)
```bash
uv run comp campaign kb-report --root artifacts/broad_map/mnist \
  --output-dir artifacts/broad_map/report
```

### Pareto Front
```bash
uv run comp frontier --study broad_mapping_sweep \
  --db artifacts/broad_map/mnist/kb.sqlite
```

### Direct KB Query
```bash
uv run python -c "
from computronium.knowledge import KnowledgeBase
kb = KnowledgeBase('artifacts/broad_map/mnist/kb.sqlite')
rows = kb.query_engine.execute('SELECT * FROM experiments WHERE metrics LIKE \"%accuracy%\"')
for r in rows[:5]: print(r)
"
```

### Campaign Diff
```bash
uv run comp campaign diff --root-a artifacts/broad_map/run1 \
  --root-b artifacts/broad_map/run2 --task mnist
```

### Defect Auto-Release
```bash
uv run comp continuous unquarantine --unquarantine-fixed \
  --root artifacts/broad_map
```

---

## 4. Reading Campaign Output

### Key Log Lines

| Line Pattern | Meaning | Action |
|--------------|---------|--------|
| `Energy clamped: -1.2M -> -1.0M` | step_size too high for this combo | Lower step_size in `ParameterUpdateConfig` |
| `Structural void: diffusion\|random_projections\|...` | Ontology boundary (not a bug) | Doc in COORDINATE_VOIDS.md |
| `Diffusion dynamics requires substrate noise_level > 0` | Substrate mismatch | Add noise to substrate config |
| `CEEC ledger: X-000015 completed (gate=completed)` | Cell trained successfully | ✅ Good |
| `Runtime defect: TypeError: PC-ALM requires...` | Gate-passing crash | Quarantined; fix code then unquarantine |

### Void Categories (from `classify_void`)

| Category | Meaning | Action |
|----------|---------|--------|
| `geometry_constraint` | Geometry doesn't support dynamics' state shape | Doc in COORDINATE_VOIDS.md |
| `credit_geometry` | Credit requires specific geometry (e.g., LocalContrastive → feedforward) | Doc |
| `dynamics_credit` | Credit incompatible with dynamics (e.g., FA on recurrent energy_min) | Doc |
| `diffusion_noise` | Diffusion requires substrate noise > 0 | Add `noise_level` to substrate config |

### Energy Clamp Frequency

If >20% of cells trigger clamp warnings for a given `(dynamics, credit, update)` combo → **lower default step_size** for that combo in `ParameterUpdateConfig.<update>()` factory.

### Spectral Radius Explosions

| Pattern | Likely Cause | Fix |
|---------|--------------|-----|
| `spectral_radius ~254K` with diffusion | Substrate noise_level=0 | Set `noise_level=0.05` for diffusion |
| `spectral_radius > 1.0` with tile_mesh | Too many params (fixed tiles) | Auto-size from `param_budget` |
| `spectral_radius > 1.0` with recurrent | step_size too high / beta mismatch | Check step_size overrides, beta propagation |

### Param Count Blowups

| Pattern | Likely Cause | Fix |
|---------|--------------|-----|
| `param_count ~768K` (budget 25K) | Tile mesh hardcoded tiles | Auto-size `neurons_per_tile`/`tiles_per_layer` from budget |
| `param_count ~1.6M` (spatial_lattice) | Lattice too large | Constrain lattice_dims from budget |

---

## 5. Common Fix Patterns

### 5.1 Substrate-Aware Configuration

```python
# In compose.py: _build_substrate_config()
def _build_substrate_config(substrate_name: str, dynamics: str):
    factory = factory_map.get(name_lower, SubstrateConfig.digital)
    if dynamics == "diffusion":
        return factory(noise_level=0.05)  # Langevin needs noise
    if dynamics == "spike_integration":
        return factory(noise_level=0.01)  # SNN benefits from noise
    return factory()
```

### 5.2 Geometry Budget Respect

```python
# In compose.py: build_geometry_config()
if topology == "tile_mesh" and param_budget > 0:
    if param_budget < 50000:
        npt, tpl = 16, 2
    elif param_budget < 100000:
        npt, tpl = 32, 3
    else:
        npt, tpl = 48, 4
```

### 5.3 Step Size Overrides

```python
# In update.py: _STEP_SIZE_OVERRIDES
_STEP_SIZE_OVERRIDES = {
    ("energy_minimization", "random_projections"): 0.1,
    ("energy_minimization", "gradient"): 0.5,
    ("diffusion", "random_projections"): 0.05,
    # Add more from campaign data...
}
```

### 5.4 Beta Auto-Propagation

```python
# In compose.py: compose_cell_system()
if dcfg.dynamics_type == "energy_minimization" and ccfg.credit_type == "thermodynamic_contrast":
    ccfg = CreditAssignmentConfig.thermodynamic_contrast(beta=dcfg.beta)
```

### 5.5 Energy Clamp Tracking

```python
# In _dynamics.py: _SettleTelemetry
class _SettleTelemetry:
    _energy_clamp_count: int = 0

    def _note_settle_start(self) -> None:
        self._converged = False
        self._settle_steps_used = 0
        self._settle_layers = 1
        # _energy_clamp_count accumulates across free/nudged phases

# In compute_energy() and settle loop:
if clamped_val != energy_val:
    self._energy_clamp_count += 1
```

---

## 6. Verification Gates

After each fix, run a **2-minute verification burst**:

```bash
uv run comp continuous --budget 120s --target-cells 20 \
  --limit-batches 10 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/verify_fix_XX
```

### Target Metrics

| Metric | Before Fix | Target | Notes |
|--------|------------|--------|-------|
| Energy clamp warnings | ~30% of cells | <5% | For overridden combos |
| Median accuracy (L0) | ~13% | >25% | With beta matching |
| Pareto front spread | 7–58% (clustered) | 15–70% (spread) | Objective-space bias |
| L2 cells produced | 0 | ≥1 per maturation | deep-tier wired |
| Diffusion spectral_radius | ~254K | <1.0 | With noise_level=0.05 |
| Tile mesh param_count | ~768K | ~25K | With budget sizing |

### Full Test Suite

```bash
# Dev-env smoke
uv run python -c "import optuna, scipy, torchvision, pytest"

# Format & lint (changed files)
uv run ruff format --check && uv run ruff check --fix

# Type check (changed files)
uv run pyright <changed_files>

# Integration tests
uv run pytest tests/integration/test_continuous_burst.py -q

# Campaign readers
uv run pytest tests/unit/test_campaign_readers.py -k "not daemon" -q
```

---

## 7. Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|--------------|------------------|
| Running full epochs (`limit_batches=0`) in broad mapping | 40x fewer cells/hour; wastes budget on voids | Use `--limit-batches 30` for L0 mapping |
| Ignoring energy clamp warnings | Silent training degradation; weights explode | Treat clamp warnings as config bugs |
| Running single burst and stopping | No maturation; can't distinguish noise from signal | Always run `--maturation N` then `deep-tier` |
| Not checking KB after run | Miss Pareto front, void breakdown, walltime profile | `comp campaign kb-report` after each burst |
| Hardcoding geometry params | Blows param budget on tile_mesh/spatial_lattice | Always read `param_budget` in `build_geometry_config` |
| Using digital substrate for diffusion | Langevin requires noise; diverges | Auto-set `noise_level` by dynamics type |

---

## 8. Measurement Quality Gates

A cell is **measurement-grade (L2)** only if:

- [ ] 3 seeds, full epochs (no `--limit-batches`)
- [ ] No energy clamp warnings
- [ ] No structural voids in its coordinate
- [ ] CEEC gate = completed (not defect)
- [ ] Reproducible: `comp repro --experiment <id>` passes

**Burst cells are L0** (1 seed, limited batches, exploratory). Only promote to L1/L2 via maturation pipeline.

---

## 9. File Locations for Quick Fixes

| Issue Area | Primary File | Key Function/Class |
|------------|--------------|---------------------|
| Substrate config | `autoscientist/compose.py` | `_build_substrate_config()` |
| Geometry sizing | `autoscientist/compose.py` | `build_geometry_config()` |
| Step size overrides | `ontology/update.py` | `_STEP_SIZE_OVERRIDES`, `_apply_step_size_overrides()` |
| Beta propagation | `autoscientist/compose.py` | `compose_cell_system()` |
| Energy clamp tracking | `ontology/dynamics/_dynamics.py` | `_SettleTelemetry`, `compute_energy()`, `settle()` |
| KB clamp reporting | `core/campaign/kb_report.py` | `_extract_clamp_stats()` |
| Void enumeration | `autoscientist/broad_map.py` | `enumerate_constraint_voids()` |
| Driver objective bias | `autoscientist/broad_map.py` | `StratifiedRandomDriver._score_proposal()` |
| Maturation pipeline | `autoscientist/broad_map.py` | `promote_candidates()`, `run_l1_maturation()`, `run_deep_tier()` |

---

## 10. Campaign Log Locations

| Artifact | Location |
|----------|----------|
| KB (SQLite) | `artifacts/<run>/<task>/kb.sqlite` |
| CEEC ledger | `artifacts/<run>/<task>/ledger.sqlite` |
| Campaign DB | `artifacts/<run>/<task>/campaign/campaign.db` |
| Checkpoints | `artifacts/<run>/<task>/campaign/checkpoints/` |
| Runtime defects | `artifacts/<run>/<task>/runtime_defects.jsonl` |
| KB reports | `artifacts/<run>/<task>/report/kb_campaign_report.{json,html}` |
| Maturation data | `artifacts/<run>/<task>/maturation.jsonl` |

---

## 11. Extending the Loop (Future Work)

### High-Leverage Additions

1. **Automated step_size calibration** — Run mini-grid per (dynamics, credit, update) to find max step_size before clamp; write to `_STEP_SIZE_OVERRIDES`

2. **Per-topology Pareto predictor** — Replace family-average with topology-conditioned predictor in `StratifiedRandomDriver`

3. **Auto-void classification** — ML classifier on void error messages to reduce manual COORDINATE_VOIDS.md maintenance

4. **Maturation `--limit-batches`** — L1/L2 currently run full epochs; add flag for faster verification cycles

5. **Deprecate legacy `run_deep_tier`** — Unify with L1→L2 pipeline

6. **Daemon stability** — Fix race condition in `test_daemon_client_round_trips_live_daemon`

### Issues Identified During TODO41

7. **Driver RNG tiebreaker bias** — When all (dynamics, credit, update) triples have balance=0, the `min(..., key=lambda k: (balance, rng.random()))` tiebreaker may not provide uniform distribution. Consider shuffling the balance dict items before min() or using a different selection strategy for the initial burst.

8. **Pre-computed viable topologies only works with `viable` frozenset** — If `viable=None` (no void enumeration), the driver falls back to random sampling. Ensure void enumeration runs first or add fallback logic.

9. **KB report generation creates new KB instance** — `build_kb_report()` in `core/campaign/kb_report.py` creates its own `KnowledgeBase`, adding another VectorStore initialization. Consider passing shared KB or making VectorStore a singleton per DB path.

---

## 12. Quick Reference: One-Liner Fixes

```bash
# Add noise for diffusion (auto-applied now, but manual if needed)
uv run comp continuous --substrate analog --budget 1m --target-cells 5 ...

# Check clamp rates from KB
uv run python -c "
import sqlite3, json
conn = sqlite3.connect('artifacts/broad_map/mnist/kb.sqlite')
for row in conn.execute('SELECT id, metrics FROM experiments'):
    m = json.loads(row[1])
    if m.get('energy_clamp_count', 0) > 0:
        print(row[0], m['energy_clamp_count'])
"

# Find worst Pareto cells
uv run python -c "
import sqlite3, json
conn = sqlite3.connect('artifacts/broad_map/mnist/kb.sqlite')
cells = []
for row in conn.execute('SELECT id, metrics FROM experiments'):
    m = json.loads(row[1])
    cells.append((m.get('final_accuracy', 0), row[0]))
cells.sort()
for acc, cid in cells[:10]:
    print(f'{acc:.4f} {cid}')
"

# Count voids by category
uv run python -c "
import sqlite3
conn = sqlite3.connect('artifacts/broad_map/mnist/kb.sqlite')
for row in conn.execute('SELECT category, COUNT(*) FROM structural_voids GROUP BY category ORDER BY 2 DESC'):
    print(f'{row[0]}: {row[1]}')
"
```

---

## 13. Execution Checklist (Per Iteration)

- [ ] Run verification burst (2 min)
- [ ] Generate KB report (`comp campaign kb-report`)
- [ ] Check Pareto front spread and accuracy
- [ ] Check energy clamp rates by (dynamics, credit, update)
- [ ] Check spectral radius for explosions
- [ ] Check param_count vs budget for geometry blowups
- [ ] Identify top 3 worst-performing combos
- [ ] Apply targeted fix (step_size, substrate noise, geometry sizing, beta)
- [ ] Run tests (`pytest tests/integration/test_continuous_burst.py -q`)
- [ ] Re-run verification burst
- [ ] Update TODO41.md with findings
- [ ] Commit with descriptive message

---

**Remember**: The KB is your memory. Every burst makes the next one smarter. Voids are not failures — they are the map boundaries. Defects are not bugs — they are the code telling you what to fix.