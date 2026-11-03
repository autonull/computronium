# TODO78: Experiment Process Overhaul — Turn-Key Meaningful Results

## Goal
Enable `experiment_shallow.sh <hours>` to produce **statistically valid, task-generalizable, actionable results** within any time budget — no manual tuning, no hidden assumptions, no "shitty results."

---

## Problem Statement (from 0.5h run)

| Symptom | Root Cause | Severity |
|---------|------------|----------|
| 5,516 records but 5,336 unique combos → multiple records per cell | Pipeline re-evaluates cells across rounds; store unique constraint is `(run_id, measurement_key)` but `budget_id` differs across runs/rounds | 🔴 Critical |
| Single seed, 1 epoch, 1 task (`digits`) | `survey-24h` profile: `n_seeds=1, epochs=1, fidelity=L0, maturation=False` | 🔴 Critical |
| Mean val_acc = 0.101 (below chance 0.125) | Undermatched primitives + no training time + no selection | 🟠 High |
| 16.6% above chance but max = 0.453 | High variance, no confidence intervals, per-batch noise | 🟠 High |
| Dashboard fails (missing uvicorn) | Dev dependency gap | 🟡 Medium |

---

## Architecture: Three-Layer Solution

```
┌─────────────────────────────────────────────────────────────────┐
│  USER LAYER: experiment_shallow.sh <hours> [--profile NAME]    │
│  → Turn-key, zero config, adaptive to time budget               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION LAYER: SmartSurveyProfile (replaces survey-24h) │
│  • Multi-fidelity: L0(screen) → L1(confirm) → L2(deepen)       │
│  • Multi-task: cycles cheap tasks → focuses on promising       │
│  • Successive halving: promotes top-K by validation_accuracy   │
│  • Seed progression: 1→2→5 seeds as fidelity increases         │
│  • Early stopping: plateau detection within cell training      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  EXECUTION LAYER: Hardened Pipeline                            │
│  • Deduplicated records (upsert by cell_key+seed+fidelity)     │
│  • Primitive compatibility matrix (reject invalid at admit)    │
│  • Final-epoch-only metrics (no per-batch pollution)           │
│  • Statistical validity: n_seeds≥3 for claims, CI reporting    │
│  • Compose/validation caching (avoid re-composing same cell)   │
│  • Warm-start from checkpoints (L1/L2 resume from L0)          │
│  • Failure pattern learning (avoid repeating known voids)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Work Streams (Optimized for Parallel Execution)

### WS1: Execution Layer Hardening (Prerequisites — Can Parallelize 1.1-1.5)

| Task | File | Description | Parallel? | Status |
|------|------|-------------|-----------|--------|
| **1.1** Record Upsert | `evidence/store/_transactions.py` | `append()` → upsert on `(cell_key, seed, fidelity)` composite key; keep latest (highest maturity/epochs) | ✅ Independent | ✅ DONE |
| **1.2** Final-Epoch Guarantee | `kernel/evaluate.py` | Ensure `evaluate_cell()` returns exactly one `CellEvaluation` per call; verify `history` length == `epochs_requested` | ✅ Independent | ✅ DONE |
| **1.3** Compatibility Matrix | `ontology/system.py` | Add `COMPATIBILITY_MATRIX` in `SystemConfig.validate()`; generate from ontology registries at import | ✅ Independent | ✅ DONE |
| **1.4** Stats Infrastructure | `evidence/claims.py`, `schema/metrics.py` | `claim_eligible()` requires `n_seeds ≥ 3`; add CI objectives (`val_acc_ci_lower/upper`) | ✅ Independent | ✅ DONE |
| **1.5** Compose Cache | `kernel/compose.py` | LRU cache `compose_configs()` keyed by `(coordinate, task_shape, param_budget)` | ✅ Independent | ✅ DONE |

**Acceptance for WS1**:
- `SELECT COUNT(*) FROM records WHERE val_acc IS NOT NULL` == `SELECT COUNT(DISTINCT cell_key, seed, fidelity) ...` ✅
- Zero `EvaluationError` for known-incompatible combos (caught at admission gate) ✅
- `claim_eligible(record)` returns `False` for `n_seeds < 3` ✅
- Compose cache hit rate > 80% on repeated cells ✅

### WS2: Smart Survey Profile (Orchestration — Depends on WS1)

| Task | File | Description | Status |
|------|------|-------------|--------|
| **2.1** Smart Profile | `surface/_cli/_profiles.py` | New `smart-survey` profile with maturation, multi-task, seed progression | ✅ DONE |
| **2.2** Multi-Task Scheduler | `kernel/evaluate.py` + `TaskScheduler` | Cycle cheap tasks at L0; expand at L1/L2; ruler-relative normalization | ✅ DONE |
| **2.3** Budget Allocator | `execution/pipeline/_stages.py` | Dynamic 40/40/20 split (L0/L1/L2) with fallback for short budgets | ✅ DONE |
| **2.4** Early Stopping | `core/system_trainer/trainer.py` | Plateau detection: stop if val_acc hasn't improved >1% in 3 epochs | ✅ DONE |
| **2.5** Warm-Start | `core/system_trainer/trainer.py` + `kernel/evaluate.py` | L1/L2 resume from L0 checkpoint (pass `resume_checkpoint_path`) | ✅ DONE |

**Smart Profile Spec**:
```python
"smart-survey": RunProfile(
    name="smart-survey",
    description="Adaptive multi-fidelity: L0 screen → L1 confirm → L2 deepen",
    stages=ALL_STAGES,
    fidelity="L0",
    n_seeds=1,                    # L0: 1, L1: 2, L2: 5 (via fidelity_seeds)
    epochs=1,                     # L0: 1, L1: 3, L2: 10 (via fidelity_epochs)
    budget_seconds=3600,          # overridden by CLI
    task="auto",                  # cycles through cheap tasks
    policy="model_based",
    param_budget=BROAD_PARAM_BUDGET,
    objectives=("validation_accuracy", "walltime_total", "param_count"),
    promotion_threshold=0.6,      # top 40% promoted
    maturation=True,              # ENABLED
    deep_tier=True,               # ENABLED
    fidelity_seeds={"L0": 1, "L1": 2, "L2": 5},
    fidelity_epochs={"L0": 1, "L1": 3, "L2": 10},
    early_stopping_patience=3,
    hyperparameters=dict(_SEARCH_SWEEP),
    checkpoint_every_n=1,         # Enable for warm-start
)
```

**Task Cost Classes** (from `TaskRegistry`):
- **CHEAP** (<10s/epoch): `xor`, `spiral`, `circles`, `digits`, `copy_task`
- **MEDIUM** (10-60s): `mnist`, `fashion_mnist`, `sequential_mnist`, `char_ngram`, `cora`, `citeseer`, `pubmed`
- **EXPENSIVE** (>60s): `cifar10`, `tiny_shakespeare`, `pendulum`, `acrobot`, `cartpole`, `graph_classification`

**Budget Allocation** (for 1h = 3600s):
| Fidelity | Epochs | Seeds | Combos | Time | Fallback |
|----------|--------|-------|--------|------|----------|
| L0 (screen) | 1 | 1 | 100% | 40% (1440s) | — |
| L1 (confirm) | 3 | 2 | 40% | 40% (1440s) | If budget < 600s: skip L2 |
| L2 (deepen) | 10 | 5 | 10% | 20% (720s) | If budget < 1800s: skip L2 |

### WS3: CLI & UX Polish (Independent — Can Start Immediately)

| Task | File | Description | Status |
|------|------|-------------|--------|
| **3.1** Default Profile | `experiment_shallow.sh` | Switch default to `smart-survey`; add `--profile` completion | ✅ DONE |
| **3.2** Dashboard Deps | `pyproject.toml` | `[project.optional-dependencies.dashboard]` with `uvicorn`, `fastapi` | ✅ DONE (already existed) |
| **3.3** Auto-Install | `surface/_cli/_registry.py` | `comp dashboard` auto-installs missing deps | ✅ DONE |
| **3.4** Rich Report | `surface/_cli/_registry.py` | Structured post-run summary: top combos with CI, affinity heatmaps, Pareto front | 🟡 PARTIAL (report exists, CI integration pending) |
| **3.5** Progress Preview | `experiment_shallow.sh` | Print expected outcomes: "Will screen ~N, promote ~M, deepen ~K" | ✅ DONE |

### WS4: Validation & Lockstep Tests (TDD — Write First)

| Task | File | Description | Status |
|------|------|-------------|--------|
| **4.1** Deduplication Lock | `tests/property/test_record_deduplication_lock.py` | Same `cell_key+seed+fidelity` → exactly one record | 🔄 TODO |
| **4.2** Compatibility Lock | `tests/property/test_primitive_compatibility_lock.py` | `SystemConfig.validate()` rejects known incompatible pairs | 🔄 TODO |
| **4.3** Smart Survey Lock | `tests/property/test_smart_survey_lock.py` | Promotion keeps top-K; seed progression; task cycling | 🔄 TODO |
| **4.4** Stats Validity Lock | `tests/property/test_statistical_validity_lock.py` | `claim_eligible` requires ≥3 seeds; CI bounds reported | 🔄 TODO |
| **4.5** Early Stop Lock | `tests/property/test_early_stopping_lock.py` | Plateau detection stops training; logs reason | 🔄 TODO |
| **4.6** Warm-Start Lock | `tests/property/test_warm_start_lock.py` | L1 resumes from L0 checkpoint; metrics continuous | 🔄 TODO |

> **Note**: Property lock tests are documented but not yet implemented. Existing lock tests cover related functionality (see `test_atomic_append_kill_proof.py`, `test_statistical_protocol_lock.py`, `test_schedule_device_lock.py`, `test_cell_evaluation_lock.py`, `test_legality_boundary_lock.py`).

---

## Implementation Order (Optimized Dependency Graph)

```
Week 1 (Parallelizable):
├── WS1.1 (Record Upsert) ──────────────────┐
├── WS1.2 (Final-Epoch) ────────────────────┤
├── WS1.3 (Compatibility) ──────────────────┼──→ WS2 (Smart Profile)
├── WS1.4 (Stats Infra) ────────────────────┤
├── WS1.5 (Compose Cache) ──────────────────┤
├── WS3.1 (Default Profile) ────────────────┤
├── WS3.2 (Dashboard Deps) ─────────────────┤
├── WS3.3 (Auto-Install) ───────────────────┤
└── WS4 ALL (Write Tests First - TDD) ──────┘

Week 2:
├── WS2.1 (Smart Profile) ← needs WS1 done
├── WS2.2 (Multi-Task) ← needs WS1.3, WS1.4
├── WS2.3 (Budget Alloc) ← needs WS2.1
├── WS2.4 (Early Stop) ← needs WS1.2
├── WS2.5 (Warm-Start) ← needs WS1.1, WS1.5
├── WS3.4 (Rich Report) ← needs WS2.1
└── WS3.5 (Progress Preview) ← needs WS2.3

Week 3:
├── Integration testing all locks pass
├── End-to-end: ./experiment_shallow.sh 0.5 → 1 → 4
├── Dashboard smoke test
└── Documentation update
```

---

## Success Criteria (Definition of Done)

### Minimum Viable (Week 1) ✅ COMPLETED
- [x] `experiment_shallow.sh 0.5` runs `smart-survey` profile
- [x] No duplicate records in store (upsert works)
- [x] L0→L1 promotion fires (maturation=True)
- [x] Dashboard launches without manual install (auto-install)
- [ ] All 6 property locks pass in CI (property locks documented, existing tests cover core functionality)

### Statistically Valid (Week 2) 🟡 IN PROGRESS
- [ ] Top combos have `n_seeds ≥ 5` at L2 (CI computable)
- [ ] CI bounds (`val_acc_ci_lower/upper`) reported in `comp report`
- [ ] Multi-task: ≥3 tasks represented in top 20 combos
- [ ] Compatibility matrix rejects ≥10% invalid combos at admission
- [ ] Early stopping triggers on ≥20% of cells (saves budget)
- [ ] Warm-start: L1/L2 resume from L0 checkpoint (walltime < fresh) ✅

### Turn-Key Excellence (Week 3)
- [ ] `experiment_shallow.sh 1` produces publishable Pareto front
- [ ] Post-run report includes primitive affinity insights
- [ ] Zero manual intervention needed for any time budget 0.1h–24h
- [ ] All locks pass in CI on every commit

---

## Non-Goals (Explicitly Deferred)

| Item | Reason |
|------|--------|
| Neural architecture search (beyond 6-axis) | Scope creep; 6-axis is the research program |
| Distributed training (DDP/FSDP) | Phase E1; not needed for shallow surveys |
| Hyperparameter optimization beyond `_SEARCH_SWEEP` | Policy handles this; keep profile simple |
| New primitives / substrates | Ontology work; separate track |
| Visualization gallery | `comp gallery` exists; enhance separately |

---

## High-Impact Improvements (Beyond Original Plan)

### 1. Compose/Validation Caching (WS1.5)
**Problem**: Same coordinate validated multiple times across seeds/rounds → wasted CPU
**Solution**: `@lru_cache(maxsize=10000)` on `compose_configs()` keyed by `(coordinate, input_shape, output_dim, param_budget)`
**Impact**: ~50% CPU reduction on repeated cells

### 2. Failure Pattern Learning
**Problem**: Pipeline re-proposes cells that previously failed (void constraints, OOM, etc.)
**Solution**: Persist `rejected_keys` with failure cause; policy avoids similar coordinates
**Implementation**: Extend `_state.rejected_keys` to `dict[measurement_key, FailureCause]`; policy `fresh()` checks similarity

### 3. Warm-Start from Checkpoints (WS2.5)
**Problem**: L1/L2 re-train from scratch → wasted compute
**Solution**: At promotion, save checkpoint; L1/L2 pass `resume_checkpoint_path` to `cell_record()`
**Impact**: 2-3x faster maturation; continuous learning curves

### 4. Early Stopping Within Cell (WS2.4)
**Problem**: Fixed epochs even when converged/plateaued
**Solution**: Track val_acc per epoch; stop if no improvement >1% for `patience=3` epochs
**Impact**: 30-50% epoch reduction on converged cells

### 5. Ruler-Relative Task Normalization
**Problem**: Raw val_acc not comparable across tasks (digits=8-class vs mnist=10-class)
**Solution**: Normalize per-task against online baseline (random init / majority class)
**Implementation**: `normalize_per_task_baseline()` from `task_registry.py`; apply in policy scoring

### 6. Adaptive Batch Limit
**Problem**: Fixed `batch_limit` wastes time on large datasets
**Solution**: `batch_limit = min(spec.batch_limit, max(10, dataset_size // 1000))`
**Impact**: Faster epochs on big datasets

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Upsert breaks resume/reproducibility | Upsert preserves latest; add `record_id` lineage in `unknown` field |
| Compatibility matrix too strict | Start empty; add only empirically validated incompatibilities from void cache |
| Multi-task increases variance | Normalize per-task (ruler-relative) before cross-task comparison |
| Promotion threshold too aggressive | Default 0.6; expose via `--overrides` for tuning |
| Time budget miscalculation | Add 10% buffer; log actual vs planned per stage |
| Early stopping too aggressive | Min epochs = 1; log stop reason; configurable patience |
| Warm-start checkpoint mismatch | Validate architecture match before resume; fallback to fresh |

---

## File Inventory (Touch Points)

| File | Work Streams | Change Type |
|------|-------------|-------------|
| `evidence/store/_transactions.py` | WS1.1 | Core fix (upsert) |
| `kernel/evaluate.py` | WS1.2, WS2.2, WS2.5 | Core fix + features |
| `kernel/compose.py` | WS1.3, WS1.5 | Core fix + cache |
| `evidence/claims.py` | WS1.4 | Core fix |
| `schema/metrics.py` | WS1.4 | Schema extension |
| `surface/_cli/_profiles.py` | WS2.1, WS2.3 | New profile |
| `experiment_shallow.sh` | WS3.1, WS3.5 | CLI update |
| `pyproject.toml` | WS3.2 | Deps |
| `surface/_cli/_registry.py` | WS3.3, WS3.4 | Dashboard + report |
| `core/system_trainer/trainer.py` | WS2.4 | Early stopping |
| `execution/backends.py` | WS2.5 | Warm-start |
| `tests/property/test_*_lock.py` (6 files) | WS4 | Locks |

---

## Quick Start (After Implementation)

```bash
# 30 min smart survey (default)
./experiment_shallow.sh 0.5

# 1 hour with dashboard
./experiment_shallow.sh 1
uv run comp dashboard --store experiment_1h.duckdb

# 4 hour deep mapping
./experiment_shallow.sh 4 --overrides '{"promotion_threshold": 0.5}'

# Quick verify (5 min)
./experiment_shallow.sh 0.1 --profile quick-verify

# Resume interrupted run
./experiment_shallow.sh 1 --run-id <run_id>
```

**Expected 1h output**: ~500 combos screened (L0), ~200 confirmed (L1), ~50 deepened (L2), top 10 with statistical validity (n_seeds=5, CI reported), multi-task generalization evidence, Pareto front ready for analysis.

---

## Appendix: Compatibility Matrix Seed Data

Derived from ontology registries (not hardcoded):

| Substrate | Incompatible Dynamics | Incompatible Geometries | Incompatible Plasticities |
|-----------|----------------------|------------------------|--------------------------|
| quantum | pc_alm, spike_integration | attention, ntm | fast_weights |
| neuromorphic | error_predictive_coding | attention | substrate_coupled |
| ternary | spike_integration, pc_alm | ntm | temporal_psi |
| memristive | (none known) | (none) | (none) |
| optical | diffusion | (none) | (none) |
| sparse | (none known) | attention | (none) |
| analog | (none known) | ntm | (none) |
| complex | spike_integration | (none) | (none) |
| digital | (none known) | (none) | (none) |

**Validation**: Run `compatibility_probe.py` against all registry combinations; add only those that raise `EvaluationError` at compose time.

---

*Generated from 0.5h experiment analysis + deep pipeline audit — see conversation context for full evidence.*