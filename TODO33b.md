# TODO33b: Additional Cleanup/Refactoring Plan (REVISED)

**Status**: Phase 1 COMPLETE — Type Safety Fixes Done

---

## 🎯 HIGH VALUE: Type Safety Fixes (Real Bugs) ✅ COMPLETED

### 1. `computronium/ontology/dynamics/_dynamics.py` — 24 LSP Errors ✅ FIXED
| Error | Location | Issue | Fix Applied |
|-------|----------|-------|-------------|
| `ActivityValue \| None` → `list[Tensor] \| None` | Line 96, 103 | Return type mismatch in protocol methods | Fixed return type annotations in `_get_state_dual_vars`, `_get_state_activity` |
| `Mapping[str, ActivityValue]` → `dict[str, ActivityValue] \| None` | Line 103 | Mapping vs dict covariance | Changed return type to `Mapping[str, ActivityValue] \| None` |
| `list[list[Tensor]]` → `ActivityValue` | Line 177 | Nested list assignment to union type | Store `spike_rasters` under `_spike_rasters` key with type ignore |
| `object` → `Tensor` | Line 743 | Unknown return type | Added `cast("Tensor", ...)` for `tile_energy` call |
| `object \| list[Tensor]` → `Sized` | Line 904, 981 | `len()` on untyped object | Added explicit `list[Tensor]` type annotations for `all_acts` |
| `__getitem__` missing on `object` | Line 908, 910, 929, 943, 945, 1003, 1047 | Untyped dict/list access | Fixed by typing `all_acts` as `list[Tensor]` |
| `CompositeState` attribute assignment | Line 1056-1059 | `free_state`/`nudged_state`/`activations` type mismatch | Added explicit `list[Tensor]` type for `acts` variable |
| `list[float] \| None` → `list[float]` | Line 1214 | Nullable vs non-nullable | Changed type annotation to `list[float] \| None` |
| `object` not callable | Lines 1762, 1803, 1808, 1897 | `op` typed as `object` | Added `ForwardOp` type alias and used it |
| `1 + rho` with `rho: float \| None` | Line 1911 | Operator issue | Use `current_rho` which is non-nullable |
| `geometry.substrate` unknown | Line 1928 | Attribute access issue | Use `getattr(geometry, "substrate", None)` |
| `dual_vars` type mismatch | Line 1949 | ActivityValue vs list[Tensor] | Added proper type checking with `isinstance` |
| `CompositeState.dual_vars` unknown | Line 1717 | Attribute access issue | Use `setattr` for SystemState, `set_activity` for CompositeState |

### 2. `computronium/acceleration/compile.py` — 7 LSP Errors ✅ FIXED
| Error | Location | Issue | Fix Applied |
|-------|----------|-------|-------------|
| `_FnWrapper` → `Module` in `_select_compile_mode` | Line 141 | Wrapper type not accepted | Moved `_FnWrapper` to module level, updated type hints |
| `_FnWrapper` → `Module` in `_should_use_dynamic_shapes` | Line 145 | Same | Same fix |
| `Tensor` not callable | Line 338, 343, 467, 469, 474, 476 | `model.settle`/`get_activations` unknown | Added `_EqPropModel` Protocol with required methods |
| Return type `Module \| Callable` → `Module` | Line 572 | Function wrapper return | Added cast in `compile_model_with_preset` |

---

## 🎯 HIGH VALUE: Complexity in Hot Paths

### 3. Core Acceleration (User-Facing)
| Function | File | Complexity | Priority |
|----------|------|------------|----------|
| `compile_settling_loop` | compile.py:501 | C901=13 | HIGH — training hot path |
| `compile_model_with_preset` | compile.py:543 | C901=12 | HIGH — user API |
| `get_compile_config` | compile.py:564 | C901=11 | MED — config helper |
| `FAKernelBackend.kernel_train_step` | fa_kernels.py | C901/PLR0915 | HIGH — FA backend |
| `PCKernelBackend.kernel_train_step` | pc_kernels.py | C901/PLR0915 | HIGH — PC backend |
| `SNNKernelBackend.kernel_train_step` | snn_kernels.py | C901/PLR0915 | MED — SNN backend |

### 4. Core Ontology (System Configuration)
| Function | File | Complexity | Priority |
|----------|------|------------|----------|
| `SystemConfig.validate()` | system.py:251 | C901=44, PLR0912=43, PLR0915=70 | CRITICAL — every run |
| `Coordinate.valid_combinations()` | system.py:627 | C901=19, PLR0912=18 | HIGH — AutoScientist |
| `EnergyMinimizationDynamics.settle()` | _dynamics.py:864 | C901=26, PLR0912=29 | CRITICAL — EqProp hot path |
| `PredictiveSettlingDynamics.settle()` | _dynamics.py:1612 | PLR0912=13 | HIGH — PC hot path |
| `_eager_relaxation()` | _dynamics.py:1725 | C901=21, PLR0912=14 | HIGH — internal helper |
| `TileGeometry.forward()` | geometry.py:1172 | C901=11 | HIGH — tile routing |
| `TileGeometry.update_params()` | geometry.py:1302 | C901=12 | MED — param updates |
| `geometry_from_config()` | geometry.py:2861 | C901=12 | MED — factory |

---

## 📋 MEDIUM VALUE: Complexity in Active Modules

### 5. Execution Engine (Used in Training)
| Function | File | Complexity | Notes |
|----------|------|------------|-------|
| `Strategy._analyze_failures()` | strategy.py:779 | C901=23, PLR0912=22 | Failure classifier pipeline |
| `Strategy._analyze_saturation()` | strategy.py:862 | C901=15, PLR0912=14 | Saturation detection |
| `Strategy._generate_standard_candidates()` | strategy.py:418 | C901=13 | Candidate generation |
| `Synthesizer._get_trials_df()` | synthesizer.py:136 | C901=17 | Optuna query |
| `Synthesizer.rescue_metadata()` | synthesizer.py:196 | C901=13, PLR0912=16 | Metadata repair |
| `Synthesizer._analyze_efficiency()` | synthesizer.py:411 | C901=13, PLR0912=13 | Pareto analysis |

### 6. Hyperopt (Experimental but Active)
| Function | File | Complexity | Notes |
|----------|------|------------|-------|
| `encode_configs()` | analysis.py:41 | C901=19, PLR0912=19, PLR0915=51 | Config encoding |
| `run_single_trial_task()` | experiment.py:403 | C901=17, PLR0912=20, PLR0915=63 | Trial runner |
| `get_search_space_for_model()` | hyperparameter_metamodel.py:268 | C901=35, PLR0912=35, PLR0915=85 | Space composition |
| `create_optuna_space()` | optuna_bridge.py:83 | C901=43, PLR0912=42, PLR0915=87 | Optuna bridge |

---

## ⚠️ LOW VALUE: Defer/Ignore (Experimental or Throwaway)

| Category | Files | Reason |
|----------|-------|--------|
| **Joint experiments** | `experiments/joint/*.py` (4 funcs) | One-off eval, not production |
| **Validation tracks** | `validation/tracks/*.py` (4 funcs) | One-off validation, low churn |
| **Audit scripts** | `scripts/audit_*.py` (9 funcs) | Throwaway probes, run once |
| **Analysis scripts** | `scripts/b2_*.py`, `contrastive_profile.py` | Profiling tools, not library code |
| **Ontology explorer** | `scripts/ontology_explorer.py` | CLI tool, not imported |
| **Test files** | `tests/unit/test_verify_backend.py`, `test_smoke_all_tasks.py`, `test_determinism_extended.py` | Only run in CI |
| **External packages** | `packages/ceec-core/`, `packages/stability/` | Separate repos, fix upstream |

---

## 📅 Execution Phases (Revised Priority)

### Phase 1: Type Safety (CRITICAL - Real Bugs) ✅ COMPLETED
```bash
# Fix _dynamics.py LSP errors ✅
# Fix compile.py LSP errors ✅
uv run pyright computronium/ontology/dynamics/_dynamics.py  # 0 errors
uv run pyright computronium/acceleration/compile.py         # 0 errors
```

**Verification:**
- ✅ Core tests pass: `tests/unit/core/test_config_unified.py tests/integration/test_equitile_domains.py` (39 passed)
- ✅ Type checking clean on both modules
- ✅ No new complexity issues introduced in compile.py

### Phase 2: Hot Path Complexity (HIGH - User Impact)
```bash
# Core acceleration
uv run ruff check --select=C901 computronium/acceleration/compile.py
uv run ruff check --select=C901 computronium/acceleration/fa_kernels.py
uv run ruff check --select=C901 computronium/acceleration/pc_kernels.py

# Core ontology
uv run ruff check --select=C901 computronium/ontology/system.py
uv run ruff check --select=C901 computronium/ontology/dynamics/_dynamics.py
uv run ruff check --select=C901 computronium/ontology/geometry.py
```

### Phase 3: Active Module Complexity (MEDIUM)
```bash
# Execution engine
uv run ruff check --select=C901 computronium/execution/strategy.py
uv run ruff check --select=C901 computronium/execution/synthesizer.py

# Hyperopt (if still used)
uv run ruff check --select=C901 computronium/hyperopt/
```

### Phase 4: Protocols & Contracts (QUALITY)
- Add property tests for `StateDynamics.settle()` / `compute_energy()` contracts
- Document protocol invariants in `ontology/` (activation layout, free/nudged semantics)
- Run dead code detection: `search_graph(max_degree=0)` via codebase-memory-mcp

---

## ✅ Verification Gates (Per Phase)
```bash
# Core tests must pass
uv run python -m pytest tests/unit/core/test_config_unified.py tests/integration/test_equitile_domains.py -q

# Type checking on modified modules
uv run pyright <modified_module>

# Complexity check on modified modules
uv run ruff check --select=C901,PLR0912,PLR0915 <modified_module>
```

---

## 📝 Phase 1 Notes & Improvement Opportunities

### Completed Work Summary
- **All 31 LSP errors fixed** across 2 critical modules (`_dynamics.py`: 24, `compile.py`: 7)
- **Root causes addressed**: Missing type annotations, untyped duck-typing helpers, Protocol mismatches, covariance issues
- **Patterns established**: `StateLike` type alias, `ForwardOp` type alias, `_EqPropModel` Protocol, proper casting

### Improvement Opportunities (for future passes)
1. **`_compute_hopfield_energy`** (C901=14, PLR0912=16) — Extract tile energy dispatch, weight/bias extraction, and energy computation into private helpers
2. **`EnergyMinimizationDynamics.settle`** (C901=26, PLR0912=29) — Split into: compiled path, checkpointed path, eager path, convergence checking
3. **`PredictiveSettlingDynamics.settle`** (PLR0912=18) — Extract tile/layered/recurrent paths into separate methods
4. **`PCALMDynamics._eager_relaxation`** (C901=21, PLR0912=14) — Extract constraint computation, dual update, primal update into helpers
5. **`LazyStateDynamics.settle`** (C901=11) — Minor: extract output layer update

### Remaining Phase 1 Follow-ups
- [ ] Run full test suite to catch any edge cases
- [ ] Consider adding `spike_rasters` to `ActivityValue` type in `computronium/state/composite.py` for cleaner typing
- [ ] Consider adding `dual_vars` field to `CompositeState` for consistency with `SystemState`

### Phase 2+ Readiness
The type system is now clean for the hot-path modules. Complexity refactoring (Phase 2) can proceed with confidence that type signatures are stable and correct.

---

## 🔑 Key Principle
**Fix type errors first** — they're real bugs. **Refactor complexity only in hot paths** — complexity in experimental/throwaway code has negative ROI.