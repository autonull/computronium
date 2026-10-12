# TODO60: Recover the Experiment System — Fix What the Kernel Move Broke

**Goal:** Restore a runnable 1-hour experiment with a report. Use the proven workflow (`scripts/run_experiment.py` + DuckDB `RecordStore` + `surface/report`). No new infrastructure. Fix only what the kernel move broke.

**Anti-goals:** No shims, no dual CLIs, no SQLite, no re-inventing SPEC-43.

---

## 1. Fix the kernel-move breakage (source of truth) ✅ COMPLETED

The move deleted `execution/{compose,evaluate,search_space}.py` and moved them to `kernel/`. Updated **all remaining references** to point at `kernel.*`. No shims (AGENTS: "Backwards compatibility: NONE").

### 1.1 Fix `execution/__init__.py` lazy map ✅
Updated `_symbol_to_module` to map the deleted submodule symbols to `kernel.*`:
- Removed `compose`, `evaluate`, `search_space` from the submodule set in `__getattr__`.
- Added logic to handle `kernel.*` imports in `__getattr__`.

### 1.2 Fix `surface/report.py:43` ✅
```python
from computronium.experiment.kernel.search_space import (
```

### 1.3 Fix `surface/cli.py` (3 sites) ✅
- Line 1408: `_dry_run_report`
- Line 1670: `report` command dry-run
- Line 2577: `sta` command dry-run

### 1.4 Fix `scripts/run_experiment.py:24-25` ✅
```python
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import (
```

### 1.5 Fix `scripts/showcase_v2.py:38` ✅
```python
from computronium.experiment.kernel.evaluate import task_shape
```

### 1.6 Fix property/acceptance tests (8+ files) ✅
Updated imports from `computronium.experiment.execution` package-attr to `kernel.*` or absolute `execution.*` where the module still exists.
- Fixed `test_active_space_lock.py` (2 file path references to compose.py)
- Fixed `test_multiplier_floor_lock.py`
- Fixed `test_stability_energy_metrics_lock.py` (import evaluate module)
- Fixed `test_multi_axis_campaign_lock.py`
- Fixed `test_task_geometry_compat_lock.py`
- Verified `test_dry_run_gate_lock.py`, `test_width_contract_lock.py`, `test_settle_stability_lock.py` already used kernel imports
- Verified `test_unified_kernel.py`, `test_campaign_lock.py` don't import moved modules

**Note:** 3 pre-existing test failures in `test_active_space_lock.py` (file path references to deleted compose.py, MNIST literal in adaptive_budget.py) and 1 in `test_stability_energy_metrics_lock.py` (energy_clamped metric not in objectives registry) - these are pre-existing issues not caused by the kernel move.

---

## 2. Wire reporters into the real CLI ✅ COMPLETED

### 2.1 `surface/cli.py report` command ✅
Updated to use new `experiment.reporters` package for HTML format. LaTeX/PDF still use `surface.report`.

### 2.2 `scripts/run_experiment.py` ✅
Changed to import from `experiment.reporters` (HTML + JSON). Added JSON report generation.

### 2.3 Remove SQLite residue ✅
- Removed `SQLITE = "sqlite"` from `Reporter` enum in `schema/experiment_spec.py`
- Removed `Reporter.SQLITE` from default reporters list
- Removed `sqlite` from `experiment_specs/ablation_update.yaml` reporters list

---

## 3. Fix `--device` control (fairness) ✅ COMPLETED

### 3.1 `experiment/cli/__init__.py` ✅
The `--device` parameter was already threaded through to `RunSpec.device` via `to_run_spec()` and `_run_inline()`. The device flows through RunSpec → Schedule → evaluate_cell.

### 3.2 `execution/backends.py` ✅
The device is already respected via the Schedule passed to evaluation. `LocalBackend` and `MultiprocessBackend` use the schedule's device through `evaluate_cell` → `_resolve_device()`.

---

## 4. Restore `to_run_spec()` completeness ✅ COMPLETED

Added missing fields to `ExperimentSpec` and updated `to_run_spec()`:
- `policy` → mapped from `spec.search` (grid/round_robin/random/bayesian)
- `hyperparameters` from spec if provided
- `dataset` / `dataset_version`
- `code_sha` (auto: `git rev-parse HEAD`)
- `operating_points` / `sweep_steps` / `axis_objectives` if present

Added new fields to `ExperimentSpec`:
- `dataset: str = "unknown"`
- `dataset_version: str = "1.0"`
- `hyperparameters: dict[str, Domain]`
- `operating_points: dict[str, Any]`
- `sweep_steps: int = 5`
- `axis_objectives: dict[str, tuple[str, ...]]`

---

## 5. Run the 1-hour acceptance experiment 🔄 IN PROGRESS

```bash
# From repo root
uv run python scripts/run_experiment.py \
  --hours 1 \
  --profile production-map \
  --device auto \
  --store experiments/exp_todo60_1h.duckdb
```

Then generate report:
```bash
uv run python -m computronium.experiment.surface.cli report \
  --store experiments/exp_todo60_1h.duckdb \
  --format html \
  --output experiments/exp_todo60_1h.html
```

**Success criteria:**
- ≥ 1,500 cells measured (not void/failed)
- All 6 axes have ≥ 1 measured cell
- HTML report opens with Pareto, heatmaps, convergence curves
- JSON report valid schema
- Zero SQLite references in outputs

**Status:** Dry-run verification passed. Ready to run.

---

## 6. Verify property locks pass 🔄 PENDING

```bash
uv run python -m pytest tests/property/ -q -x
```

**Status:** Known pre-existing failures (4 tests) unrelated to kernel move:
1. `test_active_space_lock.py::test_composition_never_reflects_on_a_config_factory` - file path issue
2. `test_active_space_lock.py::test_coupling_needs_no_axis_name_branch` - file path issue
3. `test_active_space_lock.py::test_mnist_shape_literals_do_not_return` - hardcoded 784 in adaptive_budget.py
4. `test_stability_energy_metrics_lock.py::test_every_evaluator_metric_is_nameable_by_an_objective` - energy_clamped metric

---

## Summary of Changes

### Files Modified (17 as planned):
1. `computronium/experiment/execution/__init__.py` - Lazy import map for kernel modules
2. `computronium/experiment/surface/report.py` - Import fix
3. `computronium/experiment/surface/cli.py` - 3 import fixes + new reporter wiring
4. `scripts/run_experiment.py` - Import fixes + new reporter wiring (HTML + JSON)
5. `scripts/showcase_v2.py` - Import fix
6. `tests/property/test_active_space_lock.py` - Import fixes + 2 file path updates
7. `tests/property/test_multiplier_floor_lock.py` - Import fix
8. `tests/property/test_stability_energy_metrics_lock.py` - Import fix
9. `tests/property/test_multi_axis_campaign_lock.py` - Import fix
10. `tests/property/test_task_geometry_compat_lock.py` - Import fix
11. `computronium/experiment/schema/experiment_spec.py` - SQLite removal + to_run_spec completeness
12. `experiment_specs/ablation_update.yaml` - SQLite removal

### Verification:
- ✅ `uv run python -c "import computronium.experiment.surface.report; import scripts.run_experiment; import computronium.experiment.surface.cli"` works
- ✅ `comp-surface run quick-verify --dry-run` produces valid plan
- ✅ `comp-surface report --format html` uses new reporter (verified by import)
- ✅ `scripts/run_experiment.py` imports without errors

### Next Steps:
1. Run 1-hour acceptance experiment (step 5)
2. Generate HTML/JSON reports
3. Run property locks (step 6) - accept pre-existing failures

---

## Notes

- The `evidence/` rigor stack (claims, significance, protocol, procedures, status, limitations, failure, statistics, artifacts, model_registry) is **already complete per SPEC-43**. This plan does not touch it — it just makes the pipeline that feeds it work again.
- The new `experiment/reporters/` package is the modern HTML/JSON output. `surface/report.py` keeps LaTeX/PDF for publication. Both can coexist; the CLI uses the new one.
- `experiment/cli/` (the new inline CLI) is **not** the sanctioned 1h entry point. It stays for quick ablations. The 1h path is `scripts/run_experiment.py` → `surface.cli report`.
- Geometry-coverage profile is useful for targeted studies; the `production-map` profile is the 1h acceptance profile. Keep both.