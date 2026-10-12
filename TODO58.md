# TODO58 — Experiment System Hardening & Generalization

**Status: IN PROGRESS — Session 2 complete**

**Carries forward from TODO57:**
- 1h gate run `exp_todo57_1h_v3` complete: 2070 cells, failure rate <1%, 6/6 axes covered
- All K1–K4 fixes landed in commit `d80bc54b`
- Property locks passing (60+ tests)
- Device placement, numerical failures, width mismatches, task-geometry compat: **RESOLVED**

**Remaining from TODO57 (minor):**
- ~~3 "numerical" failures are actually energy-clamping warnings (misclassified)~~ **FIXED** (A1)
- ~~17 runtime_error need root-cause analysis (likely void rejections at eval time)~~ **FIXED** (A2 - found 320 errors, all from recurrent+instantaneous+gradient, added void constraint)
- ~~Failure taxonomy pollution needs fixing before next gate run~~ **FIXED** (A1 + A2)

---

## A. Immediate Fixes (P0 — This Session) ✅ **COMPLETE**

### A1. Fix Failure Taxonomy Pollution ✅ **DONE**
**File:** `computronium/experiment/execution/evaluate.py` (`_record_family_energy`)
**Problem:** `EnergyMinimizationDynamics.compute_energy` clamps energy at ±1e6 (configurable `max_energy`) and logs warning; this was being misclassified as "numerical" failure.
**Fix:** Detect energy clamping by comparing returned energy against `max_energy * 0.999` threshold and record `energy_clamped: True` in metrics as a warning flag, not a failure.
```python
# In _record_family_energy:
max_energy = getattr(getattr(dynamics, "config", None), "max_energy", 1e6)
if abs(energy_val) >= max_energy * 0.999:  # Near clamp boundary
    metrics["energy_clamped"] = True  # WARNING, not failure
```
**Verified:** Test with `max_energy=1e-10` correctly sets `energy_clamped: True`.

### A2. Root-Cause Runtime Errors ✅ **DONE**
**Analysis:** Parsed experiment DB (`experiment.duckdb`), found 320 runtime errors (not 17) — all from the combination `recurrent` geometry + `instantaneous` dynamics + `gradient` credit.
**Root cause:** Instantaneous dynamics on recurrent geometry doesn't settle recurrent connections, leaving some weights disconnected from the loss graph → "GradientCredit: no gradient reached ['4.weight']".
**Fix:** Added void constraint `recurrent_instantaneous_gradient_credit` in `seed_registries.py:CONSTRAINTS` to suppress this invalid combination at search space level.
```python
ConstraintSpec(
    name="recurrent_instantaneous_gradient_credit",
    kind=ConstraintKind.VOID,
    description="Recurrent geometry with instantaneous dynamics incompatible with gradient/backprop credit (weights disconnected from loss)",
    predicate=not_(and_(eq(var("geometry"), const("recurrent")),
                        eq(var("dynamics"), const("instantaneous")),
                        in_(var("credit"), const(["gradient", "backprop"])))),
    proof_kind=ProofKind.TYPE_MISMATCH,
    origin="DECLARED",
)
```
**Verified:** All property locks pass; legality engine now voids this combination.

---

## B. Multi-Task Coverage (P1 — High Impact) ✅ **COMPLETE (Tasks & Profile)**

### B1. Geometry-Coverage Profile ✅ **DONE**
**File:** `profiles/geometry-coverage.yaml`
**Created:** Profile exercising 4 tasks to cover all 11 geometries:
```yaml
name: "geometry-coverage"
tasks: ["digits", "sequential_mnist", "copy_task", "graph_classification"]
budget_seconds: 7200  # 2h total
policy: "round_robin_grid"
gates: [dry_run, property_locks]
reporters: [html, json, sqlite]
```
**Task-geometry coverage:**
| Task | Geometries Exercised |
|------|---------------------|
| `digits` | feedforward, recurrent, conv, tile, tile_mesh |
| `sequential_mnist` | recurrent, causal_transformer, ntm, nca |
| `copy_task` | attention, recurrent, ntm |
| `graph_classification` | graph, spatial_lattice |

### B2. Task Registry Extension ✅ **DONE**
**Files:** `computronium/domains/registry.py`, `computronium/domains/factory.py`
- Added `sequential_mnist`, `copy_task`, `graph_classification` to `SUPPORTED_TASKS`
- Implemented all three tasks as `DomainTask` subclasses with proper data loaders:
  - **SequentialMNISTTask**: MNIST pixels as 784-step sequence (input_dim=784, output_dim=10)
  - **CopyTask**: Synthetic sequence copy task (input_dim=2*seq_len+1, output_dim=vocab_size)
  - **GraphClassificationTask**: TUDataset-based graph classification (MUTAG default, input_dim=7, output_dim=2)
- All tasks inherit from `DomainTask` base class with `evaluate()`, `get_dataloader()`, `get_batch()` methods
**Verified:** RunSpec validation passes for all 4 tasks; task_shape() returns correct dimensions.

---

## C. Experiment Types Beyond Showcase (P1 — Scientific Utility) ✅ **SESSION 2 COMPLETE**

### C1. Ablation Runner ✅ **DONE**
**File:** `computronium/experiment/runners/ablation.py`
**Purpose:** Compare single axis while holding others fixed.
```bash
# Usage: uv run python -m computronium.experiment.runners.ablation \
#   --vary update --fix geometry=feedforward dynamics=instantaneous \
#   --budget 1h --seeds 5
```
**Config:**
```python
@dataclass(frozen=True, slots=True)
class AblationSpec:
    vary: StructuralAxis
    fix: dict[StructuralAxis, str]
    n_seeds: int = 5
    budget_seconds: float = 3600
    metric: str = "validation_accuracy"
    task: str | None = None
```
**Verified:** Runs ablation on `update` axis with 3 seeds, produces statistical summary (mean ± std) across update primitives.

### C2. Scaling Runner
**Purpose:** Sweep depth, width, param_budget, settle_horizon.
```python
@dataclass(frozen=True, slots=True)
class ScalingSpec:
    vary: list[str]  # e.g., ["hidden_dims", "param_budget", "settle_horizon"]
    log_scale: bool = True
    n_points_per_dim: int = 4
    base_config: Coordinate
```

### C3. Comparison Runner (A/B Testing) ✅ **DONE**
**File:** `computronium/experiment/runners/comparison.py`
**Purpose:** Statistical comparison of two configurations.
```bash
# Usage: uv run python -m computronium.experiment.runners.comparison \
#   --arm-a geometry=feedforward,dynamics=instantaneous,credit=gradient,update=euclidean \
#   --arm-b geometry=feedforward,dynamics=instantaneous,credit=gradient,update=adam \
#   --seeds 1 --budget 60
```
**Config:**
```python
@dataclass(frozen=True, slots=True)
class ComparisonSpec:
    arm_a: dict[StructuralAxis, str]
    arm_b: dict[StructuralAxis, str]
    n_seeds: int = 10
    budget_seconds: float = 3600
    metric: str = "validation_accuracy"
    test: str = "mann_whitney_u"  # or t_test, bootstrap
    task: str | None = None
```
**Verified:** Runs A/B comparison with Mann-Whitney U test, reports p-value and significance.

### C4. Replay/Regression Runner ✅ **DONE**
**File:** `computronium/experiment/runners/replay.py`
**Purpose:** Re-run known-good cells from previous experiment DB.
```python
@dataclass(frozen=True, slots=True)
class ReplaySpec:
    source_db: str
    check_metrics: list[str] = field(default_factory=lambda: ["validation_accuracy", "walltime_total"])
    tolerance: float = 0.02
    budget_seconds: float = 3600
    task: str | None = None
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

## G. Declarative Experiment Specification (P3 — Composability) ✅ **SESSION 2 COMPLETE**

### G1. Unified ExperimentSpec ✅ **DONE**
**File:** `computronium/experiment/schema/experiment_spec.py`
Declarative YAML/JSON spec for all experiment types:
```yaml
name: "ablation_update"
type: "ablation"
tasks: ["digits"]
ablation:
  vary: "update"
  fix:
    geometry: "feedforward"
    dynamics: "instantaneous"
    credit: "gradient"
    substrate: "digital"
    plasticity: "null"
  n_seeds: 3
  metric: "validation_accuracy"
budget:
  seconds: 600
gates: ["dry_run", "property_locks"]
reporters: ["json", "sqlite"]
```

### G2. CLI Unification ✅ **DONE**
**File:** `computronium/experiment/cli/__init__.py`, `computronium/experiment/cli/__main__.py`
Single entry point for all experiment types:
```bash
# From spec file
uv run python -m computronium.experiment.cli run \
  --spec experiment_specs/ablation_update.yaml \
  --device auto

# Or inline
uv run python -m computronium.experiment.cli run \
  --type ablation --vary update \
  --fix geometry=feedforward --fix dynamics=instantaneous \
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

### Week 1: Foundation ✅ **COMPLETE**
- [x] A1: Fix failure taxonomy (warnings vs failures)
- [x] A2: Root-cause runtime errors → add void constraint for recurrent+instantaneous+gradient
- [x] B1: Create `geometry-coverage` profile with 4 tasks
- [x] B2: Add 3 new tasks (sequential_mnist, copy_task, graph_classification)

### Week 2: Experiment Types
- [x] C1: Implement `AblationRunner`
- [x] C2: Implement `ComparisonRunner` (A/B)
- [x] C3: Implement `ReplayRunner` (regression)
- [x] G1: Create `ExperimentSpec` schema + CLI

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

## L. First Session Scope (When We Start) ✅ **COMPLETE**

**Session 1 goals:**
1. ✅ Fix failure taxonomy (A1) — 30 min
2. ✅ Analyze runtime errors from v3 run (A2) — 30 min  
3. ✅ Create `geometry-coverage` profile + add 3 tasks (B1, B2) — 2h
4. ✅ Validate tasks with RunSpec and evaluate_cell — 30 min
5. ✅ Draft notes for `ExperimentSpec` schema (G1) — 30 min

**Total: ~4h** — completed in one focused session.

---

## L2. Next Session Scope (Session 2) ✅ **COMPLETE**

**Session 2 goals:**
1. ✅ Implement `AblationRunner` (C1) — 2h
2. ✅ Implement `ComparisonRunner` (C3) — 1.5h
3. ✅ Create `ExperimentSpec` schema + CLI (G1) — 2h
4. ✅ Run ablation experiment to validate — 30 min

**Total: ~6h** — completed in one focused session.

---

## L3. Session 1 Notes & Open Issues

**Completed:**
- Energy clamping detection: Added `energy_clamped` flag in `_record_family_energy()` (evaluate.py:336-340). Clamped energies no longer pollute "numerical" failure counts.
- Void constraint for `recurrent` + `instantaneous` + `gradient`/`backprop`: Added `recurrent_instantaneous_gradient_credit` constraint (seed_registries.py:1101-1118). Catches 320 invalid combinations at search space level.
- Three new tasks implemented and registered:
  - `sequential_mnist`: Sequential MNIST (784-step sequence) — exercises recurrent, causal_transformer, NTM, NCA
  - `copy_task`: Synthetic sequence copy — exercises attention, recurrent, NTM
  - `graph_classification`: TUDataset graph classification (MUTAG) — exercises graph, spatial_lattice
- `geometry-coverage` profile created at `profiles/geometry-coverage.yaml` with 4 tasks, 2h budget, round-robin grid policy.

**Known Issues / Follow-up Needed:**
1. **Graph geometry + graph_classification task**: The graph geometry requires `edge_index` which is provided by the task data, but the compose system doesn't automatically pass it. Need to modify `compose.py` to extract graph data from the task and pass it to geometry config.
2. **CopyTask output dimension mismatch**: CopyTask uses `vocab_size` as output_dim (default 8), but energy_minimization dynamics expects output_dim matching the target one-hot size. Need to either adjust dynamics or task to align dimensions.
3. **Sequential MNIST with recurrent geometry**: Works with instantaneous dynamics but needs settling dynamics (energy_minimization, etc.) for proper recurrent behavior. Current profile includes all dynamics but some combinations may fail validation.
4. **Task-geometry compatibility constraints**: Should add constraints to void invalid combinations (e.g., graph geometry requires graph task data with edge_index).

**Files Modified:**
- `computronium/experiment/execution/evaluate.py` — energy clamping detection
- `computronium/experiment/schema/seed_registries.py` — void constraint for recurrent+instantaneous+gradient
- `computronium/domains/registry.py` — added 3 tasks to SUPPORTED_TASKS
- `computronium/domains/factory.py` — implemented 3 DomainTask subclasses
- `profiles/geometry-coverage.yaml` — new profile (new file)

**Tests Passing:**
- All property locks (dynamics_wiring_lock, experiment_registries_wiring_lock, legality_boundary_lock)
- Unit tests (test_ontology.py)
- RunSpec validation for all 4 tasks
- evaluate_cell works for sequential_mnist with feedforward/instantaneous/gradient/euclidean

---

## M. Reference: Key Files to Modify

| Area | Files |
|------|-------|
| Failure taxonomy | `evaluate.py:_record_family_energy` ✅ |
| Void constraints | `seed_registries.py:CONSTRAINTS` ✅ (added `recurrent_instantaneous_gradient_credit`) |
| Task registry | `domains/registry.py:SUPPORTED_TASKS` ✅, `domains/factory.py` ✅ (3 new DomainTask subclasses) |
| Search space | `search_space.py:SearchStrategy`, `iter_candidates` |
| Reporters | `reporters/html.py`, `reporters/json.py`, `reporters/sqlite.py` |
| Runners | `runners/ablation.py` ✅, `runners/comparison.py` ✅, `runners/replay.py` ✅ |
| Schema | `schema/experiment_spec.py` ✅, `schema/coordinate.py` |
| CLI | `cli.py` ✅ |
| Property tests | `tests/property/test_experiment_invariants.py` (new) |
| Database | `kernel/database.py` (new) |
| Profiles | `profiles/geometry-coverage.yaml` ✅ (new) |
| Compose | `execution/compose.py` (graph edge_index passthrough needed) |

---

## N. Session 2 Summary

**Completed:** All Session 2 goals achieved. Ablation, Comparison, and Replay runners implemented with full store integration. ExperimentSpec schema and unified CLI operational. Validation runs successful.

**Next:** Session 3 starts with ScalingRunner (C2), void caching (D2), and experiment-aware property tests (F1).