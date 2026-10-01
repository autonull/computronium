# TODO33: Deprecated/Legacy Code Cleanup

**Status**: **COMPLETED** — All 7 items completed.

## Summary of Completed Work

All deprecated/legacy code shims have been removed after migrating internal consumers:

1. ✅ **CEEC Shim** (`computronium/ceec/`) — Migrated ~40 test/script files to direct `ceec` imports, deleted entire shim directory
2. ✅ **Deployments `_DEPRECATED_ATTRS`** (`computronium/models/deployments/deployment.py`) — Updated test file, removed shim dict and `__getattr__`
3. ✅ **Legacy ModelConfig** (`computronium/config/unified.py`) — Moved to `computronium/models/deployments/config.py`, updated 6 deployment files
4. ✅ **Core Legacy Exports** (`computronium/core/__init__.py`) — Removed `LayerRole`, `ModelConfig`, `compute_hidden_dims`, `resolve_hidden_dims` from `_LAZY`
5. ✅ **Config Legacy OmegaConf Exports** (`computronium/config/__init__.py`) — Deleted 12 `Legacy*Config` re-exports, cleaned up docstring
6. ✅ **Experiments Legacy Imports** (`computronium/experiments/__init__.py`) — Deleted try/except block for 7 legacy experiment modules
7. ✅ **Acceleration Legacy Exports** (`computronium/acceleration/__init__.py`) — Kept minimal exports for CLI, removed 200+ lines of contrastive kernel exports

---

## Summary

Since there are **no external users**, all backward-compat shims can be removed after migrating internal consumers. This document catalogs every shim, its internal uses, and the migration required.

---

## 1. `computronium/ceec/__init__.py` — CEEC Shim (HIGH IMPACT) ✅ **COMPLETED**

**What it was**: Thin re-export of `packages/ceec-core` (`ceec` package) with deprecation warning. Also had shim modules in `computronium/ceec/*.py`.

**Internal consumers**: ~40 test files + scripts in `tests/ceec/`, `scripts/probes/`, `scripts/*.py`

**Migration done**: Replaced all `from computronium.ceec import X` → `from ceec import X` (and `from computronium.ceec.*` → `from ceec.*`) using sed. Deleted entire `computronium/ceec/` directory.

**Files updated**:
- `tests/ceec/test_*.py` (12 files)
- `scripts/probes/x_*.py` (10+ files)
- `scripts/b_h3_scope_gate.py`

**Effort**: ~30 min ✅ Done

---

## 2. `computronium/models/deployments/deployment.py` — `_DEPRECATED_ATTRS` (MEDIUM IMPACT) ✅ **COMPLETED**

**What it was**: Lazy `__getattr__` shim for 27 old class names (ConvTileNet, RLTileNet, etc.) emitting `DeprecationWarning`.

**Internal consumers**: 1 test file + deployments package itself
- `tests/integration/test_equitile_domains.py` — imports deprecated attrs directly
- `computronium/models/deployments/*.py` (vision, rl, timeseries, graph, base) — use new factories internally but shim exists for backward compat

**Migration done**:
1. Updated `test_equitile_domains.py` to use new imports from vision and rl modules directly
2. Deleted `_DEPRECATED_ATTRS` dict and `__getattr__` shim from deployment.py
3. Removed unused `warnings` import

**Effort**: ~15 min ✅ Done

---

## 3. `computronium/config/unified.py` — Legacy `ModelConfig` (MEDIUM IMPACT) ✅ **COMPLETED**

**What it was**: Old `@dataclass` ModelConfig (lines 130-190) kept for deployments package.

**Internal consumers**: 6 files in `computronium/models/deployments/`

**Migration done**: Moved legacy ModelConfig, LayerRole, _build_model_config, resolve_hidden_dims, compute_hidden_dims, and config_to_dict to `computronium/models/deployments/config.py`. Updated all 6 deployment files to import from the new location. Removed legacy exports from config/unified.py and core/__init__.py.

**Effort**: ~30 min ✅ Done

---

## 4. `computronium/core/__init__.py` — Legacy `BioModel` & `ModelConfig` Exports (LOW IMPACT) ✅ **COMPLETED**

**What it was**: Lazy exports for `BioModel` and legacy `ModelConfig` from `computronium.config.unified`

**Internal consumers**: Same 6 deployment files (import via `from computronium.core.model import BioModel` and `from computronium.config.unified import ModelConfig`)

**Migration done**: Removed `LayerRole`, `ModelConfig`, `compute_hidden_dims`, `resolve_hidden_dims` from `_LAZY` dict in `core/__init__.py` after deployments migrated.

**Effort**: ~5 min ✅ Done

---

## 5. `computronium/config/__init__.py` — Legacy OmegaConf Exports (LOW IMPACT) ✅ **COMPLETED**

**What it was**: 12 `Legacy*Config` re-exports from `computronium.config.omegaconf` (lines 29-57, 85-98)

**Internal consumers**: **Zero** — grep confirms no active code imports these

**Action taken**: Deleted all legacy imports and removed from `__all__`. Cleaned up docstring and removed outdated comment block.

**Files removed from `__all__` and imports**:
- `LegacyDatasetConfig`, `LegacyDomainConfig`, `LegacyExperimentConfig`
- `LegacyLightningConfig`, `LegacyModelConfig`, `LegacyOptimizerConfig`
- `LegacyPropagatorConfig`, `LegacyScientistConfig`, `LegacySparsityConfig`
- `LegacyTrainingConfig`
- `get_default_config`, `validate_config`

**Effort**: ~5 min ✅ Done

---

## 6. `computronium/experiments/__init__.py` — Legacy Experiment Imports (LOW IMPACT) ✅ **COMPLETED**

**What it was**: Try/except imports for 7 legacy experiment modules (lines 18-32)

**Internal consumers**: **Zero** — these are only invoked via `comp` CLI commands, not imported

**Action taken**: Deleted the legacy try/except block and removed legacy entries from `__all__`. Kept only the joint architecture experiments.

**Effort**: ~5 min ✅ Done

---

## 7. `computronium/acceleration/__init__.py` — Legacy Kernel Exports (MEDIUM IMPACT) ✅ **COMPLETED**

**What it was**: 200+ lines exporting old kernel backend classes, contrastive kernels, utilities (lines 16-256)

**Internal consumers**: 2 CLI files + 1 test
- `computronium/cli/export_kernel.py` — imports `AlgorithmFamily`, `HardwareTarget`, `KernelConfig`, `KernelRegistry`, `get_algorithm_kernels`
- `computronium/cli/export_trained_kernel.py` — same imports
- `tests/unit/test_verify_backend.py` — imports `kernels` module

**Migration done**: Kept minimal exports needed by CLI files in acceleration/__init__.py:
- `AlgorithmFamily`, `HardwareTarget`, `KernelConfig`, `KernelRegistry`, `LocalityLevel`, `infer_algorithm_family` (from kernel_backend.py)
- `get_algorithm_kernels()` function (kept for CLI registry population)
- `HAS_CUPY`, `HAS_TRITON`, `AutoDispatcher`, etc. (from backends module)
- `compile_model`, `compile_settling_loop` (from compile module)
- Removed all contrastive kernel exports (BaseContrastiveKernel, ContrastiveConfig, ContrastiveKernel, FAContrastiveKernel, etc.)
- Removed contrastive primitives exports (batched_outer_product, conductance_matmul, etc.)

**Effort**: ~30 min ✅ Done

---

## 9. `computronium/core/joint/transition.py` — `LegacyDynamicsAsCoupledTransition` (KEEP)

**Status**: **DO NOT REMOVE** — explicitly named compatibility wrapper, tested in:
- `tests/property/joint/test_adapter_projections.py`
- `tests/property/joint/test_coupled_transition_protocol.py`

This is intentional zero-cost compatibility for 5-D → 6-D transition.

---

## 10. Old Kernel Implementation Files (KEEP)

**Status**: **DO NOT REMOVE** — these are the actual kernel implementations referenced by new registry specs:

| File | Role |
|------|------|
| `kernels.py` | Reference EqProp kernels |
| `triton_kernels.py` | Triton ops (EqProp, MEP) |
| `fa_kernels.py` | FA kernels (used by random_projections, local_goodness kernels) |
| `pc_kernels.py`, `hebbian_kernels.py`, `snn_kernels.py`, `ff_kernels.py`, `tp_kernels.py`, `tile_kernels.py`, `mep_kernels.py`, `backprop_kernels.py`, `contrastive_kernels.py`, `pcalm_kernels.py` | Algorithm-specific kernels |

The new `acceleration/registry.py` points to these via `reference_entrypoint`/`kernel_entrypoint`. They are **active implementations**, not legacy code.

---

## 11. Duplicate Strategy Files (INVESTIGATE)

**Observation**: Both `mep/optimizers/strategies/` and `core/optimization/strategies/` have `gradient.py`, `update.py`, `constraint.py`, `feedback.py`, `base.py`

**Analysis**: 
- `mep/optimizers/strategies/` — MEP-specific extensions (EP gradients, CUDA Muon, Dion, Fisher)
- `core/optimization/strategies/` — Generic strategies (Backprop, FA, TP, Hebbian gradients; Plain/Muon updates)

**Relationship**: MEP imports from core (`from computronium.core.optimization.strategies import ...`). Not duplicates — intentional layering.

**Action**: Keep both. Document the relationship in `mep/optimizers/strategies/__init__.py`.

---

## Execution Order

```
1. config/__init__.py — Delete legacy OmegaConf exports (no deps)           [5 min]
2. experiments/__init__.py — Delete legacy experiment imports (no deps)     [5 min]
3. ceec/__init__.py — Migrate ~40 test/script files to `ceec` direct imports [30 min]
4. deployments/deployment.py — Migrate test_equitile_domains.py, delete shim [15 min]
5. config/unified.py + core/__init__.py — Migrate deployments to new ModelConfig [30 min]
6. acceleration/__init__.py — Migrate 2 CLI files to new registry API       [30 min]
```

**Total**: ~1 hour 55 min

---

## Verification After Each Step

```bash
# After each migration:
uv run python -m pytest tests/ -q --tb=short  # Full suite must pass
uv run pyright .                              # Type checking clean
uv run ruff check .                           # Lint clean
```

---

## Notes

- **No external users** = no deprecation period needed. Direct migration → removal.
- **CEEC shim** is highest impact (most files) but mechanical (sed replacement).
- **Deployments package** is the blocker for items 3, 4, 5 — migrate it first or in parallel.
- **Kernel files** are NOT legacy — they're the implementation backend for the new registry.