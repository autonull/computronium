# TODO58 — Experiment System Hardening & Generalization

**Status: PLANNING — to be started in fresh session**

**Carries forward from TODO57:**
- 1h gate run `exp_todo57_1h_v3` complete: 2070 cells, failure rate <1%, 6/6 axes covered
- All K1–K4 fixes landed in commit `d80bc54b`
- Property locks passing (60+ tests)
- Device placement, numerical failures, width mismatches, task-geometry compat: **RESOLVED**

**Remaining from TODO57 (minor):**
- 3 "numerical" failures are actually energy-clamping warnings (misclassified)
- 17 runtime_error need root-cause analysis (likely void rejections at eval time)
- Failure taxonomy pollution needs fixing before next gate run

---

## A. Immediate Fixes (P0 — This Session)

### A1. Fix Failure Taxonomy Pollution
**File:** `computronium/experiment/execution/evaluate.py`
**Problem:** `EnergyMinimizationDynamics.compute_energy` clamps energy at ±1e6 and logs warning; this gets counted as "numerical" failure.
**Fix:** Distinguish warning from failure in telemetry collection.
```python
# In _free_settle_metrics / _nudged_settle_metrics:
try:
    energy = dynamics.compute_energy(...)
except NumericalError as e:
    metrics["energy_error"] = str(e)  # REAL failure
    metrics["failure_class"] = "critical"
else:
    if abs(energy) >= 1e6:  # Clamped
        metrics["energy_clamped"] = True  # WARNING, not failure
        metrics["failure_class"] = "warning"
```

### A2. Root-Cause 17 Runtime Errors
**Action:** Parse experiment DB, group by defect message, identify pattern.
**Likely causes:**
- Void constraint rejections that pass screening but fail at evaluation
- Substrate-dynamics incompatibilities not in CONSTRAINTS_REGISTRY
- Missing params for specific geometry (e.g., graph edge_index)
**Deliverable:** List of defect patterns → new void constraints or search space fixes.

---

## B. Multi-Task Coverage (P1 — High Impact)

### B1. Geometry-Coverage Profile
**Goal:** Exercise ALL 11 geometries by running multiple tasks.
**Tasks & their geometry coverage:**
| Task | Geometries Exercised |
|------|---------------------|
| `digits` | feedforward, recurrent, conv, tile, tile_mesh |
| `sequential_mnist` | recurrent, causal_transformer, ntm, nca |
| `copy_task` | attention, recurrent, ntm |
| `graph_classification` | graph, spatial_lattice |

**Profile:** `profiles/geometry-coverage.yaml`
```yaml
name: "geometry-coverage"
tasks: ["digits", "sequential_mnist", "copy_task", "graph_classification"]
budget_seconds: 7200  # 2h total
policy: "round_robin_grid"  # per task
gates: [dry_run, property_locks]
reporters: [html, json, sqlite]
```

### B2. Task Registry Extension
**File:** `computronium/experiment/schema/seed_registries.py`
- Add `sequential_mnist`, `copy_task`, `graph_classification` to `TASK_REGISTRY`
- Define input/output shapes, data loaders
- Add task-geometry compatibility constraints (extend D1)

---

## C. Experiment Types Beyond Showcase (P1 — Scientific Utility)

### C1. Ablation Runner
**Purpose:** Compare single axis while holding others fixed.
```python
# Usage: uv run python -m computronium.experiment.runners.ablation \
#   --vary update --fix geometry=feedforward dynamics=instantaneous \
#   --budget 1h --seeds 5
```
**Config:**
```python
@dataclass(frozen=True)
class AblationSpec:
    vary: StructuralAxis
    fix: dict[StructuralAxis, str]
    n_seeds: int = 5
    budget_seconds: float = 3600
    metric: str = "validation_accuracy"
```

### C2. Scaling Runner
**Purpose:** Sweep depth, width, param_budget, settle_horizon.
```python
@dataclass(frozen=True)
class ScalingSpec:
    vary: list[str]  # e.g., ["hidden_dims", "param_budget", "settle_horizon"]
    log_scale: bool = True
    n_points_per_dim: int = 4
    base_config: Coordinate
```

### C3. Comparison Runner (A/B Testing)
**Purpose:** Statistical comparison of two configurations.
```python
@dataclass(frozen=True)
class ComparisonSpec:
    arm_a: Coordinate
    arm_b: Coordinate
    n_seeds: int = 10
    metric: str = "validation_accuracy"
    test: str = "mann_whitney_u"  # or t_test, bootstrap
```

### C4. Replay/Regression Runner
**Purpose:** Re-run known-good cells from previous experiment DB.
```python
@dataclass(frozen=True)
class ReplaySpec:
    source_db: str  # path to experiment.db
    check_metrics: list[str] = ["validation_accuracy", "walltime_total"]
    tolerance: float = 0.02  # 2% regression threshold
```

---

## D. Search Space Intelligence (P2 — Efficiency)

### D1. Bayesian Optimization Strategy
Replace `round_robin_grid` with BO that:
- Uses previous run DB as prior
- Learns void regions (GP classifier on legality)
- Targets Pareto frontier (multi-objective EI)
- Can accept coverage targets: "hit all geometries at least once"

**File:** `computronium/experiment/execution/search_space.py` → add `BayesianSearchStrategy`

### D2. Void Region Caching
Persist void combinations across runs:
```python
# In search_space.py
class VoidCache:
    def __init__(self, db_path: str):
        self.void_combos: set[Coordinate] = load_from_db(db_path)
    
    def is_known_void(self, coord: Coordinate) -> bool:
        return coord in self.void_combos
    
    def record_void(self, coord: Coordinate):
        self.void_combos.add(coord)
        persist_to_db(coord)
```

---

## E. Rich Reporting & Visualization (P2 — Usability)

### E1. Enhanced HTML Reporter
**Artifacts to generate:**
1. **Pareto frontiers** — accuracy vs latency vs params (interactive Plotly)
2. **Axis coverage heatmaps** — geometry × dynamics × credit (measured/void/failed)
3. **Failure mode clustering** — UMAP on defect embeddings, colored by failure class
4. **Convergence curves** — per-cell training curves (not just final metrics)
5. **Resource scaling laws** — flops/step vs params, memory vs depth
6. **Seed stability** — variance across seeds per configuration

**File:** `computronium/experiment/reporters/html.py`

### E2. Structured JSON Output
Machine-readable for downstream analysis:
```json
{
  "run_id": "exp_abc123",
  "profile": "geometry-coverage",
  "cells": [
    {
      "coordinate": {...},
      "metrics": {...},
      "status": "measured|void|failed",
      "failure_class": "critical|degraded|warning|void",
      "defect": "..." | null,
      "seed": 42,
      "walltime_s": 12.3
    }
  ],
  "pareto_frontier": [...],
  "axis_coverage": {...}
}
```

---

## F. Property Test ↔ Experiment Integration (P3 — Regression Safety)

### F1. Experiment-Aware Property Tests
```python
# tests/property/test_experiment_invariants.py
@pytest.mark.experiment
def test_all_measured_cells_satisfy_width_contract(experiment_db):
    for record in experiment_db.measured_cells():
        coord = record.coordinate
        config = compose_configs(coord, ...)
        assert check_width_contract(config)

@pytest.mark.experiment  
def test_no_critical_failures_in_measured_cells(experiment_db):
    critical = [r for r in experiment_db.records() 
                if r.failure_class == "critical"]
    assert len(critical) == 0, f"Critical failures: {critical}"

@pytest.mark.experiment
def test_coverage_targets_met(experiment_db):
    """At least one measured cell per geometry/update/credit."""
    for axis in [StructuralAxis.GEOMETRY, StructuralAxis.UPDATE, ...]:
        measured = {r.coordinate[axis] for r in experiment_db.measured_cells()}
        available = PRIMITIVES_REGISTRY[axis].keys()
        missing = available - measured
        assert not missing, f"Axis {axis}: missing {missing}"
```

### F2. CI Integration
- Run property tests against latest experiment DB on PR merge
- Fail if critical failures introduced
- Track coverage regression over time

---

## G. Declarative Experiment Specification (P3 — Composability)

### G1. Unified ExperimentSpec
**File:** `computronium/experiment/schema/experiment_spec.py`
```python
from dataclasses import dataclass
from computronium.experiment.schema.coordinate import StructuralAxis

@dataclass(frozen=True)
class ExperimentSpec:
    name: str
    # Profile OR inline definition
    profile: str | None = None
    tasks: list[str] = field(default_factory=lambda: ["digits"])
    
    # Axes control
    vary: list[StructuralAxis] = field(default_factory=list)
    fix: dict[StructuralAxis, str] = field(default_factory=dict)
    
    # Search strategy
    search: SearchStrategy = SearchStrategy.GRID
    search_params: dict = field(default_factory=dict)
    
    # Budget
    budget: Budget = field(default_factory=Budget.default)
    
    # Gates (must pass before/during/after)
    gates: list[Gate] = field(default_factory=lambda: [
        Gate.DRY_RUN, Gate.PROPERTY_LOCKS
    ])
    
    # Output
    reporters: list[Reporter] = field(default_factory=lambda: [
        Reporter.HTML, Reporter.JSON, Reporter.SQLITE
    ])
    
    # Seeds
    seeds: int | list[int] = 1
```

### G2. CLI Unification
```bash
# Single entry point for all experiment types
uv run python -m computronium.experiment.cli run \
  --spec experiment_specs/ablation_update.yaml \
  --device auto

# Or inline
uv run python -m computronium.experiment.cli run \
  --type ablation --vary update --fix geometry=feedforward \
  --budget 1h --seeds 5
```

---

## H. Shared Infrastructure Refactor (P2 — Maintainability)

### H1. Kernel/Runner/Reporter Separation
```
computronium/experiment/
├── kernel/              # SHARED CORE (no experiment-type logic)
│   ├── search_space.py  # Composition, legality, void constraints
│   ├── evaluate.py      # Cell evaluation, metrics, stability
│   ├── compose.py       # Config → System composition
│   ├── resources.py     # GPU, memory, flops tracking
│   └── database.py      # SQLite persistence
├── runners/             # EXPERIMENT TYPE IMPLEMENTATIONS
│   ├── __init__.py
│   ├── showcase.py      # Current production-map (legacy)
│   ├── ablation.py      # Single-axis sweeps
│   ├── scaling.py       # Depth/width/budget sweeps
│   ├── comparison.py    # A/B arms
│   ├── replay.py        # Regression from DB
│   └── multi_task.py    # Multi-task coverage
├── profiles/            # YAML/TOML profile definitions
│   ├── production-map.yaml
│   ├── geometry-coverage.yaml
│   ├── stress-test.yaml
│   └── ablation-*.yaml
├── reporters/           # OUTPUT FORMATS
│   ├── __init__.py
│   ├── html.py          # Rich interactive reports
│   ├── json.py          # Machine-readable
│   ├── sqlite.py        # Persistent DB
│   └── tensorboard.py   # Optional
├── schema/
│   ├── experiment_spec.py  # Unified ExperimentSpec
│   ├── coordinate.py
│   ├── primitives.py
│   ├── run_spec.py
│   └── seed_registries.py
└── cli.py               # Unified entry point
```

### H2. Database Schema for Experiment Persistence
```sql
-- experiments table
CREATE TABLE experiments (
    run_id TEXT PRIMARY KEY,
    spec_json TEXT NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT,  -- running, completed, failed, killed
    budget_seconds REAL,
    cells_planned INTEGER,
    cells_measured INTEGER
);

-- cells table (one row per evaluated cell)
CREATE TABLE cells (
    id INTEGER PRIMARY KEY,
    run_id TEXT REFERENCES experiments(run_id),
    coordinate_json TEXT NOT NULL,
    task_id TEXT NOT NULL,
    seed INTEGER,
    status TEXT,  -- measured, void, failed
    failure_class TEXT,  -- critical, degraded, warning, void
    defect TEXT,
    metrics_json TEXT,
    walltime_s REAL,
    created_at TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_cells_run_status ON cells(run_id, status);
CREATE INDEX idx_cells_coordinate ON cells(run_id, coordinate_json);
```

---

## I. Implementation Roadmap

### Week 1: Foundation
- [ ] A1: Fix failure taxonomy (warnings vs failures)
- [ ] A2: Root-cause 17 runtime errors → add void constraints
- [ ] B1: Create `geometry-coverage` profile with 4 tasks
- [ ] B2: Add 3 new tasks to TASK_REGISTRY

### Week 2: Experiment Types
- [ ] C1: Implement `AblationRunner`
- [ ] C2: Implement `ComparisonRunner` (A/B)
- [ ] C3: Implement `ReplayRunner` (regression)
- [ ] G1: Create `ExperimentSpec` schema + CLI

### Week 3: Intelligence & Reporting
- [ ] D1: Bayesian search strategy (or at least void caching)
- [ ] E1: Enhanced HTML reporter (Pareto, heatmaps, clustering)
- [ ] E2: Structured JSON output
- [ ] F1: Experiment-aware property tests

### Week 4: Polish & Integration
- [ ] H1: Refactor into kernel/runners/reporters structure
- [ ] H2: SQLite persistence schema + migration
- [ ] CI integration for property tests on experiment DB
- [ ] Documentation: experiment types guide, profile authoring

---

## J. Success Criteria for TODO58

| Metric | Target |
|--------|--------|
| Failure taxonomy accuracy | 0 false "numerical" from energy clamping |
| Geometry coverage | 11/11 geometries measured across tasks |
| Experiment types | 4 runnable types (showcase, ablation, scaling, comparison) |
| Search efficiency | >50% measured/void ratio (vs ~20% in v2) |
| Report richness | Pareto plots, heatmaps, clustering, curves |
| Regression safety | Property tests run on experiment DB in CI |
| Configurability | Declarative YAML spec for all experiment types |

---

## K. Notes & Open Questions

1. **Task implementation effort** — `sequential_mnist`, `copy_task`, `graph_classification` need data loaders and task shapes. May need to implement or import from existing benchmarks.

2. **Bayesian optimization dependency** — Would need `botorch`/`gpytorch` or lighter alternative (`scikit-optimize`). Keep optional.

3. **HTML reporter dependencies** — `plotly` for interactive charts. Consider static matplotlib + JSON for zero-dep fallback.

4. **Multi-seed evaluation** — Current `evaluate_cell` runs single seed. Ablation/comparison need multi-seed aggregation (mean ± std).

5. **Resource accounting** — `Budget` class should track GPU-hours, not just walltime, for fair comparison across devices.

6. **Experiment naming** — Use deterministic IDs: `{profile}_{timestamp}_{git_short_hash}` for reproducibility.

7. **Backward compatibility** — Existing `production-map` profile and `scripts/run_experiment.py` should continue working during refactor.

---

## L. First Session Scope (When We Start)

**Session 1 goals:**
1. Fix failure taxonomy (A1) — 30 min
2. Analyze 17 runtime errors from v3 run (A2) — 30 min  
3. Create `geometry-coverage` profile + add 3 tasks (B1, B2) — 2h
4. Run 30min geometry-coverage experiment to validate — 30 min
5. Draft `ExperimentSpec` schema (G1) — 1h

**Total: ~4.5h** — achievable in one focused session.

---

## M. Reference: Key Files to Modify

| Area | Files |
|------|-------|
| Failure taxonomy | `evaluate.py:_free_settle_metrics`, `_nudged_settle_metrics` |
| Void constraints | `seed_registries.py:CONSTRAINTS_REGISTRY` |
| Task registry | `seed_registries.py:TASK_REGISTRY`, `evaluate.py:task_shape` |
| Search space | `search_space.py:SearchStrategy`, `iter_candidates` |
| Reporters | `reporters/html.py`, `reporters/json.py`, `reporters/sqlite.py` |
| Runners | `runners/ablation.py`, `runners/comparison.py`, `runners/replay.py` |
| Schema | `schema/experiment_spec.py`, `schema/coordinate.py` |
| CLI | `cli.py` |
| Property tests | `tests/property/test_experiment_invariants.py` (new) |
| Database | `kernel/database.py` (new) |

---

**Next session starts here.** Priority order: A1 → A2 → B1/B2 → G1 → C1.