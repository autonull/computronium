# TODO59: Experiment System — Run, Report, Iterate

**Goal:** Run experiments of arbitrary length (1h+), produce meaningful reports, fix bugs in the process. Continuously improve the experiment process.

**Anti-goals:** No new infrastructure, no refactoring for its own sake, no duplicate database layers.

---

## Current State (Post-Session 4)

| Component | Status |
|-----------|--------|
| 4 runners (ablation, scaling, comparison, replay) | Implemented, import errors in execution/ backends |
| geometry-coverage profile | Created, 3 tasks × 2 geometries × 2 dynamics |
| VoidCache | Working, persists across runs |
| HTML/JSON reporters | Working |
| Kernel (compose, evaluate, search_space, resources) | Moved to `kernel/`, exports OK |
| DuckDB RecordStore | Exists at `evidence/store.py` (1800 lines), production-ready |
| SQLite database | **Deleted** — was a bad decision |

**Broken:** `execution/` backends/pipeline still import from old `execution.evaluate`/`execution.compose` paths. Runners fail at composition.

---

## Phase 1: Fix Imports & Run Validation Experiment (30 min)

- [ ] Fix remaining `execution.evaluate` → `kernel.evaluate` imports in:
  - `execution/backends.py` (cell_record)
  - `execution/pipeline.py` (task_shape)
  - `execution/pricing.py` (task_shape)
  - `execution/campaign.py` (task_shape)
  - `surface/cli.py` (task_shape)
  - `probe.py` (task_shape)
- [ ] Fix `execution.compose` → `kernel.compose` imports in same files
- [ ] Run ablation on `digits` (60s budget) — verify end-to-end
- [ ] Run comparison A/B — verify end-to-end
- [ ] Run geometry-coverage via CLI — verify HTML/JSON output

---

## Phase 2: 1-Hour Experiment + Report (1h)

- [ ] Run `geometry-coverage` profile for 1 hour on CPU
- [ ] Verify HTML report: Pareto frontier, heatmaps, scaling curves render
- [ ] Verify JSON report: cells, Pareto, axis coverage, summary stats
- [ ] Document any failures (void, crash, timeout) in report
- [ ] Commit report artifacts to `experiments/geometry-coverage-<timestamp>/`

---

## Phase 3: Bug Fixes from 1h Run (30 min)

- [ ] Fix any task/geometry/dynamics compatibility issues found
- [ ] Add void constraints for newly discovered invalid combos
- [ ] Fix any metric computation errors
- [ ] Re-run 1h to confirm fixes

---

## Phase 4: Longer Experiments & Iteration (Ongoing)

| Duration | Profile | Goal |
|----------|---------|------|
| 2h | geometry-coverage | Full 11 geometries × 3 tasks |
| 4h | stress-test (new) | Push param_budget, epochs, seeds |
| 8h+ | production-map | Publication-ready results |

**Per cycle:**
1. Run experiment
2. Analyze report for anomalies
3. Fix top 3 bugs
4. Extend duration

---

## Carried Forward from TODO58 (Week 4 Items)

| Item | Status | Notes |
|------|--------|-------|
| GraphClassificationTask + GraphGeometry | ❌ Open | TUDataset batches multiple graphs; GraphGeometry expects single static graph. Need `GraphClassificationGeometry` or batched graph support. |
| GraphTask DataLoader | ❌ Open | Returns `None` (full-graph training). Trainer expects iterable DataLoader. Need wrapper or full-graph mode. |
| Task-geometry void constraints | ❌ Open | Add constraints: graph geometry → graph task with edge_index; recurrent geometry + gradient credit → settling dynamics. |
| Multi-seed aggregation | 🟡 Partial | Ablation/Comparison runners support n_seeds; verify mean±std in reports. |
| Resource accounting (GPU-hours) | ❌ Open | `Budget`/`CostTracker` track GPU-hours/energy/carbon; integrate into reports. |
| Experiment naming | ❌ Open | Use `{profile}_{timestamp}_{git_short_hash}` for reproducibility. |
| Documentation | ❌ Open | Experiment types guide, profile authoring, CLI reference. |
| CI integration | ❌ Open | GitHub Actions workflow for experiment DB property tests. |

**Non-goals (explicitly dropped):**
- ❌ Bayesian optimization (D1) — void cache sufficient
- ❌ SQLite database (H2) — DuckDB `RecordStore` exists at `evidence/store.py`
- ❌ Kernel refactor (H1) — **DONE** in this session

---

## Concrete Commands

```bash
# Phase 1 validation
uv run python -m computronium.experiment.cli run \
  --type ablation --vary geometry \
  --fix dynamics=instantaneous,credit=gradient,update=euclidean,plasticity=null,substrate=digital \
  --task digits --budget 60s --seeds 1 --device cpu

# Phase 2 1-hour run
uv run python -m computronium.experiment.cli run \
  --spec computronium/experiment/profiles/geometry-coverage.yaml \
  --budget 1h --device cpu

# View results
open experiments/geometry-coverage-<timestamp>/report.html
cat experiments/geometry-coverage-<timestamp>/report.json | jq .
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| End-to-end ablation | Runs without import errors |
| 1h geometry-coverage | >50% cells measured (not void/failed) |
| HTML report | Opens, shows Pareto + heatmap |
| JSON report | Valid schema, all cells present |
| Zero SQLite | Confirmed absent |

---

## Explicit Non-Goals

- ❌ New database schema (DuckDB exists)
- ❌ Kernel/refactor restructuring (done)
- ❌ Bayesian optimization (D1) — void cache is enough for now
- ❌ New tasks — 3 tasks sufficient for validation
- ❌ New runners — 4 cover the space
- ❌ CI integration — manual runs first

---

## Files to Touch (Only)

```
computronium/experiment/execution/backends.py
computronium/experiment/execution/pipeline.py
computronium/experiment/execution/pricing.py
computronium/experiment/execution/campaign.py
computronium/experiment/surface/cli.py
computronium/experiment/probe.py
```

That's it. Everything else works.