# TODO79: SimpleSurvey — Minimal Adaptive Experiment System

> **Core Idea**: Replace the complex multi-stage pipeline with a **single parallel evaluation script** that leverages 90% of existing code. Adaptivity comes from *offline* importance sampling using prior runs, not *online* policy optimization.

---

## The Problem with Current Architecture

| Current | Issue |
|---------|-------|
| 11-stage pipeline (S1-S11) | 3370 rounds in 0.5h for 8 records |
| Policy (Optuna TPE/NSGA-II) | Loky semaphore leaks, complexity |
| Multi-fidelity promotion | Warm-start bugs, checkpoint mismatches |
| Allocator + deadline enforcer | Doesn't work reliably |
| Cell stream + re-proposing | Exhausts after ~5 valid cells |

**Root cause**: Online adaptation is the wrong abstraction for shallow surveys.

---

## Solution: SimpleSurvey

```
┌─────────────────────────────────────────────────────────────┐
│  experiment_shallow.sh <hours> [--fidelity L0|L1|L2]       │
│         [--cells N] [--tasks auto|list] [--workers N]      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  1. GENERATE: Sample N valid cells from pre-filtered space  │
│     - iter_candidates + check_compatibility_matrix (fast)   │
│     - Optional: bias toward prior run top performers        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. EVALUATE: Parallel map (ProcessPoolExecutor)            │
│     - cell_record(coord, schedule) → metrics                │
│     - No rounds, no policy, no promotion, no checkpoints    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. AGGREGATE: Store → report (CI, Pareto, heatmaps)        │
└─────────────────────────────────────────────────────────────┘
```

---

## What This Eliminates (3000+ lines)

| Component | Lines | Replaced By |
|-----------|-------|-------------|
| Pipeline stages, budget, deadline | ~1500 | `ProcessPoolExecutor` + `timeout` |
| Policy (Optuna, samplers) | ~800 | Random/grid/sobol + importance sampling |
| Promotion/warm-start | ~400 | Separate fidelity runs |
| Allocator | ~300 | `estimate_cell_counts(budget_s)[fidelity]` |
| Cell stream + re-proposing | ~500 | Pre-generated cell list |

**Net: Remove ~3000 lines, add ~200 lines (`simple_survey.py`).**

---

## What We Keep (All Valuable Code)

| Component | Purpose |
|-----------|---------|
| `iter_candidates` | Cell generation |
| `check_compatibility_matrix` | Fast invalid combo rejection (50%+) |
| `compose_configs` (LRU cached) | Compose acceleration |
| `cell_record` / `evaluate_cell` | Training + metrics |
| `TaskScheduler` | Task cycling, ruler-relative normalization |
| `RecordStore` | Persistence, upsert deduplication |
| `estimate_cell_counts` | Budget → cell count |
| `_promotion.py` normalization | Reusable for importance scoring |
| `report.py` | Heatmaps, CI, Pareto front |
| All 171 property locks | Regression tests |

---

## Adaptivity Without Online Policy

```python
# simple_survey.py — Importance sampling from prior runs

def _generate_valid_cells(n, fidelity, tasks, seed, prior_store=None):
    cells = []
    
    # 1. Exploitation: bias toward prior winners (if prior run exists)
    if prior_store:
        top = prior_store.query_top(fidelity=fidelity, k=10, metric="val_acc")
        cells.extend(_mutate_around(top, n // 2, fidelity, tasks))
    
    # 2. Exploration: random valid cells
    cells.extend(_random_explore(n - len(cells), fidelity, tasks, seed))
    
    return cells[:n]

def _mutate_around(top_coords, n, fidelity, tasks):
    """Mutate 1-2 axes of top performers to explore neighborhood."""
    for coord in top_coords:
        for _ in range(n // len(top_coords)):
            mutated = _mutate_axes(coord, k=2)  # Change 1-2 axes
            if check_compatibility_matrix(mutated):
                yield mutated

def _random_explore(n, fidelity, tasks, seed):
    """Random valid cells from iter_candidates."""
    import random; random.seed(seed)
    for task in cycle(tasks):
        spec = RunSpec(fidelity=fidelity, task=task, ...)
        for coord, sched in iter_candidates(spec, max_scan=50000):
            if check_compatibility_matrix(coord):
                yield (coord, sched)
                if len(cells) >= n: return
```

**No Optuna. No rounds. No promotion logic.**

---

## Multi-Fidelity via Separate Commands

```bash
# Screen (cheap, many cells)
./experiment_shallow.sh 0.5 --fidelity L0 --out L0.duckdb

# Confirm (promote top 20 from L0)
./experiment_shallow.sh 0.5 --fidelity L1 --in L0.duckdb --promote-top 20

# Deepen (promote top 5 from L1)
./experiment_shallow.sh 1 --fidelity L2 --in L1.duckdb --promote-top 5
```

Each run is **independent, simple, parallel**. User controls promotion explicitly.

---

## Dry-Run Driven Development

### Core Principle: **Every feature testable via `--dry-run` in <5 seconds**

```bash
# Dry-run tests (no training, just generation + validation)
./experiment_shallow.sh 0.01 --dry-run --fidelity L0      # Cell generation
./experiment_shallow.sh 0.01 --dry-run --fidelity L1 --in L0.duckdb  # Promotion
./experiment_shallow.sh 0.01 --dry-run --fidelity L2 --in L1.duckdb  # Deepen

# Unit tests via pytest (also fast, no GPU)
uv run pytest tests/unit/test_simple_survey.py -v
```

### Test Categories

| Test | Method | Time |
|------|--------|------|
| Cell generation validity | `--dry-run` + inspect output | 2s |
| Compatibility filtering | `--dry-run` + count rejected | 2s |
| Task cycling per fidelity | `--dry-run` + inspect tasks | 2s |
| Importance sampling bias | pytest + mock prior store | 1s |
| Parallel evaluate (mock) | pytest + mock cell_record | 5s |
| Report generation | pytest + temp store | 3s |
| **Full integration (0.02h)** | `./experiment_shallow.sh 0.02` | 30s |

**No 0.5h runs during development.** Only final validation.

---

## Implementation Plan

### Phase 1: Core SimpleSurvey ✅ COMPLETE

```python
# experiment/simple_survey.py
def run_simple_survey(
    hours: float,
    fidelity: str = "L0",
    tasks: list[str] = None,
    max_workers: int = 4,
    store_path: str = "experiment.duckdb",
    promote_from: str = None,      # Prior store path
    promote_top: int = 20,         # How many to promote
    seed: int = 42,
    dry_run: bool = False,
) -> dict:
    # 1. Budget → cell count
    budget_s = int(hours * 3600)
    n_cells = estimate_cell_counts(budget_s)[fidelity]
    
    # 2. Generate cells (with importance sampling)
    cells = _generate_valid_cells(n_cells, fidelity, tasks, seed, promote_from, promote_top)
    
    if dry_run:
        return {"cells": cells, "n": len(cells), "tasks": _extract_tasks(cells)}
    
    # 3. Parallel evaluate
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_evaluate_one, c, fidelity, store_path) for c in cells]
        results = [f.result() for f in as_completed(futures)]
    
    # 4. Store & report
    store = RecordStore(store_path)
    run_id = store.create_run(...)
    store.append_many(results)
    return generate_report(store, run_id)
```

**Tests**: `test_simple_survey.py` with `--dry-run` assertions. ✅ PASSED

### Phase 2: CLI Integration ✅ COMPLETE

```bash
# experiment_shallow.sh — thin wrapper
#!/bin/bash
# ... parse args ...
uv run python -m experiment.simple_survey \
    --hours "$HOURS" \
    --fidelity "$FIDELITY" \
    --workers "$MAX_WORKERS" \
    --store "$STORE_PATH" \
    ${PROMOTE_FROM:+--promote-from "$PROMOTE_FROM"} \
    ${PROMOTE_TOP:+--promote-top "$PROMOTE_TOP"} \
    ${DRY_RUN:+--dry-run}
```

**Tests**: `--dry-run` output validation. ✅ PASSED

### Phase 3: Report Integration ✅ COMPLETE

Reuse existing `report.py` — just call `generate_report(store, run_id)`.

**Tests**: Report structure validation. ✅ PASSED

### Phase 4: Validation Runs (IN PROGRESS)

```bash
# Quick validation (30s each)
./experiment_shallow.sh 0.02 --dry-run        # Generation test ✅
./experiment_shallow.sh 0.02 --fidelity L0    # L0 integration ✅
./experiment_shallow.sh 0.02 --fidelity L1 --in L0.duckdb  # Promotion test ✅

# Full validation (5 min)
./experiment_shallow.sh 0.1 --fidelity L0     # 50 cells, real training (PENDING)
```

---

## Success Criteria (Measurable)

| Metric | Target | Measurement | Status |
|--------|--------|-------------|--------|
| **Throughput** | ≥50 unique cells / 0.5h | `records count / fidelity` | Pending |
| **L1 Validity** | val_acc > 0.0 | `payload.val_acc` on L1 records | Pending |
| **Multi-task** | ≥3 tasks in top 10 | Report heatmap | Pending |
| **Dry-run speed** | <5s | `time ./experiment_shallow.sh 0.01 --dry-run` | ✅ ~2s |
| **Code size** | <500 lines new | `wc -l simple_survey.py` | ✅ ~400 |
| **Lock compliance** | 171/171 pass | `pytest tests/property/` | ✅ PASSED |

---

## Files Created/Modified

| File | Action | Lines | Status |
|------|--------|-------|--------|
| `computronium/experiment/simple_survey.py` | **NEW** — Core implementation | ~400 | ✅ |
| `experiment_shallow.sh` | **REWRITE** — Thin wrapper | ~150 | ✅ |
| `tests/unit/test_simple_survey.py` | **NEW** — Dry-run tests | ~120 | ✅ |

**No changes to**: `search_space.py`, `evaluate.py`, `compose.py`, `policy.py`, `_promotion.py`, `backends.py`, pipeline stages.

---

## Migration Path

| Step | Action | Status |
|------|--------|--------|
| 1 | Build `simple_survey.py` + tests (dry-run driven) | ✅ |
| 2 | Replace `experiment_shallow.sh` wrapper | ✅ |
| 3 | Validate 0.1h runs produce ≥20 cells | 🔄 |
| 4 | **Archive complex pipeline** → `experiment/deep_pipeline/` | ⏳ |
| 5 | Update docs/README | ⏳ |

**Rollback**: Complex pipeline preserved in `experiment/deep_pipeline/` for NAS campaigns.

---

## Quick-Start for Next Session

```bash
# 1. Create simple_survey.py skeleton
cat > experiment/simple_survey.py << 'EOF'
# ... scaffold with run_simple_survey() ...
EOF

# 2. Write dry-run tests first (TDD)
cat > tests/unit/test_simple_survey.py << 'EOF'
def test_dry_run_generates_valid_cells():
    result = run_simple_survey(0.01, fidelity="L0", dry_run=True)
    assert result["n"] > 0
    for coord, sched in result["cells"]:
        assert check_compatibility_matrix(coord) == (True, None)
EOF

# 3. Run tests (should fail initially)
uv run pytest tests/unit/test_simple_survey.py -v

# 4. Implement until tests pass
# 5. Test CLI integration
./experiment_shallow.sh 0.01 --dry-run
```

---

## Appendix: Why This Works

| Concern | Answer |
|---------|--------|
| "No policy = bad search" | Random/grid/sobol + importance sampling from prior runs is competitive for low-dimensional discrete spaces (6 axes × ~10 values) |
| "No warm-start = slow" | Fresh L1 training (3 epochs) < warm-start resume + validation overhead |
| "No promotion = manual work" | User controls promotion explicitly — clearer, fewer bugs |
| "No deadline enforcer" | `timeout` at shell level + process pool is sufficient |
| "Existing locks break" | Locks test *invariants* (deduplication, compatibility, stats) — all preserved |

**The complex pipeline solves problems that don't exist for shallow surveys.**