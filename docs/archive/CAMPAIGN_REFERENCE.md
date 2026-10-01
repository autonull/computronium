# Campaign Reference — Quick-Lookup Tables

**Status**: Append-only reference. Updated when new void categories, fix patterns, or file mappings are discovered.

---

## 1. Void Categories (from `classify_void`)

| Category | Meaning | Triggering Error Pattern | Action |
|----------|---------|-------------------------|--------|
| `geometry_constraint` | Geometry doesn't support dynamics' state shape | `requires a linear-stack geometry`, `layered geometry`, `state-shape contract` | Doc here; not a bug |
| `credit_geometry` | Credit requires specific geometry | `LocalContrastive requires feedforward`, `spike_integration.*route()` | Doc here |
| `dynamics_credit` | Credit incompatible with dynamics | `FA on recurrent energy_min`, `thermodynamic_contrast requires energy_minimization` | Doc here |
| `diffusion_noise` | Stochastic dynamics requires substrate noise > 0 | `Diffusion dynamics requires substrate noise_level > 0` | Add `noise_level` to substrate config for that dynamics |
| `substrate_mismatch` | Substrate precision/sparsity incompatible with geometry | `spatial_lattice works best with neuromorphic substrate` | Doc or auto-configure |

---

## 2. Common Fix Patterns

### 2.1 Substrate-Aware Configuration
```python
# In autoscientist/compose.py: _build_substrate_config()
def _build_substrate_config(substrate_name: str, dynamics: str):
    factory = factory_map.get(name_lower, SubstrateConfig.digital)
    # Add noise for stochastic dynamics
    if dynamics in {"diffusion", "spike_integration"}:
        return factory(noise_level=0.05 if dynamics == "diffusion" else 0.01)
    return factory()
```

### 2.2 Geometry Budget Respect
```python
# In autoscientist/compose.py: build_geometry_config()
# Any geometry with size parameters should auto-size from param_budget
if topology in {"tile_mesh", "spatial_lattice", ...} and param_budget > 0:
    # Constrain geometry size params from budget
    if topology == "tile_mesh":
        # Example: scale neurons_per_tile / tiles_per_layer
        pass
    elif topology == "spatial_lattice":
        # Constrain lattice_dims from budget
        lattice_dims = _constrain_spatial_lattice_dims(lattice_dims, param_budget, ...)
    # Add more geometry types as needed...
```

### 2.3 Step Size Overrides
```python
# In ontology/update.py: _STEP_SIZE_OVERRIDES
_STEP_SIZE_OVERRIDES = {
    ("energy_minimization", "random_projections"): 0.1,
    ("energy_minimization", "gradient"): 0.5,
    ("diffusion", "random_projections"): 0.05,
    ("diffusion", "spectral_constrained"): 0.1,
    ("diffusion", "homeostatic"): 0.1,
    # Add more from campaign data...
}
```

### 2.4 Beta Auto-Propagation
```python
# In autoscientist/compose.py: compose_cell_system()
if dcfg.dynamics_type == "energy_minimization" and ccfg.credit_type == "thermodynamic_contrast":
    ccfg = CreditAssignmentConfig.thermodynamic_contrast(beta=dcfg.beta)
elif dcfg.dynamics_type == "pc_alm" and ccfg.credit_type in {"pc_alm", "thermodynamic_contrast"}:
    ccfg = CreditAssignmentConfig(
        credit_type=ccfg.credit_type,
        beta=dcfg.beta,
        feedback_matrix=ccfg.feedback_matrix,
        local_objective=ccfg.local_objective,
        orthogonal_init=ccfg.orthogonal_init,
        feedback_scale=ccfg.feedback_scale,
        credit_norm=ccfg.credit_norm,
    )
```

### 2.5 Energy Clamp Tracking
```python
# In ontology/dynamics/_dynamics.py: _SettleTelemetry
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

## 3. File Locations for Quick Fixes

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
| Tile mesh weight init | `ontology/geometry.py` | `TileGeometry._build_tile_params()` |
| Spectral radius probe | `autoscientist/campaign.py` | `probe_spectral_radius()` |
| Diff validation | `ontology/system.py` | `validate()`, `_validate_diffusion_dynamics_geometry()` |

---

## 4. Campaign Artifact Locations

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

## 5. Key Log Line Patterns

| Pattern | Meaning | File to Fix |
|---------|---------|-------------|
| `Energy clamped: <val> -> <val>` | step_size too high | `ontology/update.py` `_STEP_SIZE_OVERRIDES` |
| `Structural void: <type>` | Ontology boundary | This file (void categories) |
| `<dynamics> dynamics requires substrate noise_level > 0` | Substrate mismatch | `autoscientist/compose.py` `_build_substrate_config()` |
| `CEEC ledger: X-XXXXX completed` | Success | — |
| `Runtime defect: <TypeError>: <msg>` | Gate-passing crash | Quarantine → fix code → unquarantine |

---

## 6. Target Metrics Quick Reference

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Energy clamp rate | <5% | 5–20% | >20% |
| Spectral radius | <0.5 | 0.5–1.0 | >1.0 |
| Param count / budget | 0.8–1.2x | 1.2–2.0x | >2.0x |
| Median L0 accuracy | >25% | 15–25% | <15% |
| Pareto front spread | >40% | 20–40% | <20% |
| L2 cells / maturation | ≥1 | 0 | 0 |

---

## 7. Anti-Patterns Quick Reference

| Don't | Do Instead |
|-------|------------|
| `--limit-batches 0` in broad mapping | `--limit-batches 30` |
| Ignore clamp warnings | Treat as config bugs |
| Single burst only | Always maturation + deep-tier |
| Skip KB report | `comp campaign kb-report` every run |
| Hardcode `hidden_dim=64` | Read `param_budget` in geometry config |
| Digital substrate for **stochastic dynamics** | Auto-set `noise_level` by dynamics type |

---

## 8. One-Liner Debug Commands

```bash
# Check clamp rates from KB
uv run python -c "
import sqlite3, json
conn = sqlite3.connect('artifacts/broad_map/mnist/kb.sqlite')
for row in conn.execute('SELECT id, metrics FROM knowledge WHERE source=\"experiment\"'):
    m = json.loads(row[1])
    if m.get('energy_clamp_count', 0) > 0:
        print(row[0], m['energy_clamp_count'])
"

# Find worst Pareto cells
uv run python -c "
import sqlite3, json
conn = sqlite3.connect('artifacts/broad_map/mnist/kb.sqlite')
cells = []
for row in conn.execute('SELECT id, metrics FROM knowledge WHERE source=\"experiment\"'):
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

# Spectral radius by dynamics
uv run python -c "
import sqlite3, json
conn = sqlite3.connect('artifacts/broad_map/mnist/kb.sqlite')
from collections import defaultdict
d = defaultdict(list)
for row in conn.execute('SELECT id, metrics FROM knowledge WHERE source=\"experiment\"'):
    m = json.loads(row[1])
    hp = json.loads(row[2]) if row[2] else {}
    dyn = hp.get('dynamics', 'unknown')
    sr = m.get('spectral_radius', 0)
    if sr > 0: d[dyn].append(sr)
for k, v in d.items():
    print(f'{k}: max={max(v):.4f} avg={sum(v)/len(v):.4f} n={len(v)}')
"

# Spectral radius check for stochastic dynamics (should be < 1.0 after probe fix)
uv run python -c "
import sqlite3, json
conn = sqlite3.connect('artifacts/broad_map/mnist/kb.sqlite')
for row in conn.execute('SELECT id, metrics, hyperparameters FROM knowledge WHERE source=\"experiment\"'):
    m = json.loads(row[1]) if row[1] else {}
    hp = json.loads(row[2]) if row[2] else {}
    if hp.get('dynamics') in {'diffusion', 'spike_integration'}:
        sr = m.get('spectral_radius', 0)
        status = '✅' if sr < 1.0 else '❌'
        print(f'{status} {row[0]}: dyn={hp.get(\"dynamics\")} sr={sr:.4f}')
"
```

---

*End of CAMPAIGN_REFERENCE.md — update when new patterns emerge.*