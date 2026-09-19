# Primitive/Algorithm Structure with a Shared Acceleration Layer

This plan restructures Computronium so that:

```text
acceleration/ is a shared utility layer for backends, kernels, parity, dispatch, and microbenchmarking
primitives/ contains reusable axis-level mechanisms
algorithms/ contains named compositions of primitives
```

The structure is designed to make future additions obvious, testable, and acceleratable without requiring global documentation or a new conceptual “absorption” layer.

The core doctrine is:

```text
Reference implementations define mathematical meaning.
Kernel implementations provide accelerated execution.
Parity tests protect the meaning.
Microbenchmarks expose engineering value.
The registry makes implementation status explicit.
```

---

## Progress Summary (2026-09-19)

### ✅ Completed Steps

| Step | Description | Status |
|------|-------------|--------|
| 1 | Create missing acceleration contracts (spec.py, parity.py, microbench.py, matrix.py) | ✅ Done |
| 1b | Adapt existing: KernelRegistry → registry.py, AutoDispatcher → dispatch.py | ✅ Done |
| 2 | Create primitive exemplar (pc_alm_settling) | ✅ Done |
| 3 | Add primitive tests | ✅ Done |
| 4 | Create algorithm exemplar (pcalm) | ✅ Done |
| 5 | Add algorithm tests | ✅ Done |
| 6 | Add central registry test | ✅ Done |
| 7 | Update old acceleration imports | ✅ Done (pcalm_kernels.py already delegates) |
| 8 | Run repository health checks | ✅ Done |
| 9 | Fix lint issues in new files (RUF067, format) | ✅ Done |
| 10 | Fix pyright type issues (registry, PCALMDynamics settle signature) | ✅ Done |
| 11 | Create predictive_settling primitive (state_dynamics) | ✅ Done |
| 12 | Add predictive_settling tests | ✅ Done |
| 13 | Create random_projections primitive (credit_assignment) | ✅ Done |
| 14 | Add random_projections tests | ✅ Done |
| 15 | Create local_goodness primitive (credit_assignment) | ✅ Done |
| 16 | Add local_goodness tests | ✅ Done |
| 17 | Create temporal_trace primitive (credit_assignment) | ✅ Done |
| 18 | Add temporal_trace tests | ✅ Done |
| 19 | Create muon primitive (parameter_update) | ✅ Done |
| 20 | Add muon tests | ✅ Done |
| 21 | Create tile_mesh primitive (geometry) | ✅ Done |
| 22 | Add tile_mesh tests | ✅ Done |
| 23 | Create fast_weight primitive (plasticity) | ✅ Done |
| 24 | Add fast_weight tests | ✅ Done |
| 25 | Create routing primitive (plasticity) | ✅ Done |
| 26 | Add routing tests | ✅ Done |

### ✅ Verification Results

All new tests pass when run per-directory (and now globally with renamed test files):
```bash
uv run pytest tests/primitives/state_dynamics/pc_alm_settling -q     # 10 passed
uv run pytest tests/primitives/state_dynamics/predictive_settling -q # 7 passed
uv run pytest tests/primitives/state_dynamics/energy_minimization -q # 9 passed
uv run pytest tests/primitives/state_dynamics/spike_integration -q   # 9 passed
uv run pytest tests/primitives/credit_assignment/random_projections -q # 7 passed
uv run pytest tests/primitives/credit_assignment/local_goodness -q   # 8 passed
uv run pytest tests/primitives/credit_assignment/temporal_trace -q   # 7 passed
uv run pytest tests/primitives/credit_assignment/pc_alm -q           # 8 passed
uv run pytest tests/primitives/credit_assignment/thermodynamic_contrast -q # 7 passed
uv run pytest tests/primitives/credit_assignment/reverse_mode -q     # 9 passed
uv run pytest tests/primitives/parameter_update/muon -q              # 7 passed
uv run pytest tests/primitives/parameter_update/euclidean -q         # 9 passed
uv run pytest tests/primitives/parameter_update/spectral_constrained -q # 9 passed
uv run pytest tests/primitives/geometry/tile_mesh -q                 # 10 passed
uv run pytest tests/primitives/geometry/feedforward_dag -q           # 10 passed
uv run pytest tests/primitives/geometry/recurrent_attractor -q       # 10 passed
uv run pytest tests/primitives/plasticity/fast_weight -q             # 12 passed
uv run pytest tests/primitives/plasticity/routing -q                 # 13 passed
uv run pytest tests/primitives/plasticity/null -q                    # 9 passed
uv run pytest tests/primitives/plasticity/substrate_coupled -q       # 9 passed
uv run pytest tests/primitives/substrate/digital -q                  # 10 passed
uv run pytest tests/primitives/substrate/memristive -q               # 10 passed
uv run pytest tests/primitives/substrate/neuromorphic -q             # 10 passed
uv run pytest tests/algorithms/pcalm -q                              # 13 passed
uv run pytest tests/algorithms/backprop -q                           # 13 passed
uv run pytest tests/algorithms/fa -q                                 # 13 passed
uv run pytest tests/algorithms/eqprop -q                             # 13 passed
uv run pytest tests/algorithms/ff -q                                 # 13 passed
uv run pytest tests/algorithms/pepita -q                             # 13 passed
uv run pytest tests/algorithms/pc -q                                 # 13 passed
uv run pytest tests/algorithms/hebbian -q                            # 13 passed
uv run pytest tests/algorithms/tile -q                               # 13 passed
uv run pytest tests/algorithms/routing -q                            # 13 passed
uv run pytest tests/algorithms/fast_weight -q                        # 13 passed
uv run pytest tests/algorithms/spiking_snn -q                        # 13 passed
uv run pytest tests/algorithms/tp -q                                 # 9 passed
uv run pytest tests/algorithms/dfa -q                                # 9 passed
uv run pytest tests/acceleration/test_all_implementations.py -q      # 62 passed
```

All existing tests continue to pass:
```bash
uv run pytest tests/unit/core/test_dynamics.py -q                    # 5 passed, 1 xfailed
uv run pytest tests/integration/test_lazy_dynamics.py -q            # 5 passed
uv run pytest tests/property/test_dynamics_wiring_lock.py -q        # 4 passed
uv run pytest tests/integration/test_pc_alm_validation.py -q        # 28 passed
uv run pytest tests/integration/test_demo_pc_alm.py -q              # 1 passed
```

Note: Test files renamed to `test_<name>_*.py` pattern to avoid pytest collection conflicts. `pytest tests/` now works globally.

### 🔧 Changes Made

**New acceleration layer contracts:**
- `computronium/acceleration/spec.py` - ImplementationSpec, ParityTolerance
- `computronium/acceleration/parity.py` - compare(), assert_parity()
- `computronium/acceleration/microbench.py` - CLI smoke benchmark runner
- `computronium/acceleration/matrix.py` - Registry → implementation matrix
- `computronium/acceleration/registry.py` - Auto-discovery registry with get_spec/all_specs
- `computronium/acceleration/dispatch.py` - select_backend(spec, requested)

**Primitive exemplar (pc_alm_settling):**
- `computronium/primitives/state_dynamics/pc_alm_settling/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps PCALMDynamics; kernel delegates to pcalm_kernels._compiled_pcalm_settle
- Deterministic RNG handling for parity testing

**Primitive (predictive_settling):**
- `computronium/primitives/state_dynamics/predictive_settling/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps PredictiveSettlingDynamics; kernel delegates to _compiled_layered_settle (torch.compile)
- Deterministic RNG handling for parity testing

**Primitive (random_projections):**
- `computronium/primitives/credit_assignment/random_projections/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps RandomProjectionsCredit; kernel falls back to reference (Triton TODO)
- Deterministic RNG handling for parity testing

**Primitive (local_goodness):**
- `computronium/primitives/credit_assignment/local_goodness/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps LocalGoodnessCredit (FF/LEMMA variants); kernel falls back to reference
- Deterministic RNG handling for parity testing

**Primitive (temporal_trace):**
- `computronium/primitives/credit_assignment/temporal_trace/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps TemporalTraceCredit; kernel falls back to reference (Triton TODO)
- Deterministic RNG handling for parity testing

**Primitive (muon):**
- `computronium/primitives/parameter_update/muon/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps RiemannianOrthogonalUpdate (Muon); kernel falls back to reference
- Deterministic RNG handling for parity testing

**Primitive (tile_mesh):**
- `computronium/primitives/geometry/tile_mesh/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps TileGeometry; kernel falls back to reference (Triton TODO in tile_kernels.py)
- Deterministic RNG handling for parity testing

**Primitive (fast_weight):**
- `computronium/primitives/plasticity/fast_weight/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps FastWeightPlasticity; kernel falls back to reference
- Deterministic RNG handling for parity testing

**Primitive (routing):**
- `computronium/primitives/plasticity/routing/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps RoutingPlasticity; kernel falls back to reference
- Deterministic RNG handling for parity testing

**Primitive (energy_minimization) — NEW THIS SESSION:**
- `computronium/primitives/state_dynamics/energy_minimization/` with spec.py, reference.py, kernel.py, cases.py, __init__.py
- Reference wraps EnergyMinimizationDynamics; kernel falls back to reference (torch.compile path)
- Deterministic RNG handling for parity testing

**Scaffolding & Test Generation — NEW THIS SESSION:**
- `scripts/scaffold_primitive.py` — Jinja2-based scaffolding for new primitives
- `scripts/templates/primitive/` — Templates for __init__.py, spec.py, reference.py, kernel.py, cases.py, and tests
- `tests/generate_tests.py` — Generates test files from ImplementationSpec
- `scripts/rename_test_files.py` — Renames test files to avoid pytest conflicts

**CI & Registry — NEW THIS SESSION:**
- `.github/workflows/ci.yml` — Added parity gate, matrix output, microbenchmark smoke
- `computronium/acceleration/matrix.py` — Added --format json/markdown support
- `computronium/acceleration/microbench.py` -- Added --all and --format json support
- `computronium/primitives/__init__.py` — Lazy loading via __getattr__
- `computronium/algorithms/__init__.py` — Lazy loading via __getattr__

**Test File Renaming — NEW THIS SESSION:**
- All primitive tests renamed to `test_<primitive_name>_*.py`
- All algorithm tests renamed to `test_<algorithm_name>_*.py`
- Enables global `pytest tests/` without collection conflicts

**Algorithm exemplar (pcalm):**
- `computronium/algorithms/pcalm/` with spec.py, reference.py, kernel.py, factory.py, cases.py, __init__.py
- Factory wraps compose_joint_system with backend selection
- Uses primitives: primitive.state_dynamics.pc_alm_settling, primitive.credit_assignment.pc_alm

**Phase 4 Algorithms (11 algorithms):**
- `computronium/algorithms/backprop/` - Standard backpropagation with autograd
- `computronium/algorithms/fa/` - Feedback Alignment with fixed random feedback
- `computronium/algorithms/eqprop/` - Equilibrium Propagation with energy minimization
- `computronium/algorithms/ff/` - Forward-Forward with layer-local goodness
- `computronium/algorithms/pepita/` - PEPITA with error-modulated forward passes
- `computronium/algorithms/pc/` - Predictive Coding with hierarchical error minimization
- `computronium/algorithms/hebbian/` - Hebbian/STDP with local correlation
- `computronium/algorithms/tile/` - TileNet with modular tile geometry
- `computronium/algorithms/routing/` - 6-D Joint with RoutingPlasticity
- `computronium/algorithms/fast_weight/` - 6-D Joint with FastWeightPlasticity
- `computronium/algorithms/spiking_snn/` - Spiking NN with LIF + STDP
- Each algorithm has spec.py, reference.py, kernel.py, factory.py, cases.py, __init__.py
- Tests for each algorithm under tests/algorithms/<name>/

**Tests:**
- tests/primitives/state_dynamics/pc_alm_settling/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/state_dynamics/predictive_settling/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/credit_assignment/random_projections/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/credit_assignment/local_goodness/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/credit_assignment/temporal_trace/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/parameter_update/muon/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/geometry/tile_mesh/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/plasticity/fast_weight/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/plasticity/routing/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/algorithms/pcalm/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/backprop/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/fa/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/eqprop/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/ff/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/pepita/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/pc/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/hebbian/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/tile/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/routing/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/fast_weight/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/algorithms/spiking_snn/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/acceleration/test_all_implementations.py (parametrized over all_specs())

**Lint fixes:**
- Added noqa comments for intentional patterns (non-empty-init-module RUF067 for registration)
- Fixed import ordering and type annotations
- Fixed ruff format on all new files
- Fixed missing newlines, unsorted imports, unused imports, TYPE_CHECKING blocks

**Type fixes:**
- Fixed registry.py pyright errors (getattr for package attributes, type ignore for SPEC)
- Added `on_step` parameter to PCALMDynamics.settle() to match StateDynamics protocol

### ✅ Completed Steps (Phase 4: Migration of Named Algorithms)

| Step | Description | Status |
|------|-------------|--------|
| 27 | Create backprop algorithm (algorithm.backprop) | ✅ Done |
| 28 | Create fa algorithm (algorithm.fa) | ✅ Done |
| 29 | Create eqprop algorithm (algorithm.eqprop) | ✅ Done |
| 30 | Create ff algorithm (algorithm.ff) | ✅ Done |
| 31 | Create pepita algorithm (algorithm.pepita) | ✅ Done |
| 32 | Create pc algorithm (algorithm.pc) | ✅ Done |
| 33 | Create hebbian algorithm (algorithm.hebbian) | ✅ Done |
| 34 | Create tile algorithm (algorithm.tile) | ✅ Done |
| 35 | Create routing algorithm (algorithm.routing) | ✅ Done |
| 36 | Create fast_weight algorithm (algorithm.fast_weight) | ✅ Done |
| 37 | Create spiking_snn algorithm (algorithm.spiking_snn) | ✅ Done |
| 38 | Add tests for all Phase 4 algorithms | ✅ Done |
| 39 | Run repository health checks | ✅ Done |

### ✅ Completed Steps (Phase 5: Missing Primitives & Algorithms)

| Step | Description | Status |
|------|-------------|--------|
| 40 | Create PCALMCredit primitive (primitive.credit_assignment.pc_alm) | ✅ Done |
| 41 | Add PCALMCredit primitive tests | ✅ Done |
| 42 | Create target_prop algorithm (algorithm.tp) | ✅ Done |
| 43 | Add target_prop algorithm tests | ✅ Done |
| 44 | Create dfa algorithm (algorithm.dfa) | ✅ Done |
| 45 | Add dfa algorithm tests | ✅ Done |
| 46 | Run repository health checks | ✅ Done |

### ✅ Completed Steps (This Session: 2026-09-19 — Complete)

| Step | Description | Status |
|------|-------------|--------|
| 47 | Fix RUF067 lint in __init__.py registration (dfa, tp, pc_alm credit) | ✅ Done |
| 48 | Fix pyright type errors: add `on_step` to InstantaneousDynamics & SpikeIntegrationDynamics | ✅ Done |
| 49 | Fix ruff format on 4 primitive files | ✅ Done |
| 50 | Verify all new tests pass (per-directory due to pytest collection conflicts) | ✅ Done |
| 51 | Verify all existing integration/property tests pass | ✅ Done |
| 52 | Verify central registry test (48 tests) passes | ✅ Done |
| 53 | Fix all lint issues in new primitives/algorithms (noqa-comments, rule-codes-in-suppression-comments) | ✅ Done |
| 54 | Run pyright type checking on new modules | ✅ Done |
| 55 | Run repository health checks (ruff format, ruff check, pyright) | ✅ Done |

### ✅ Completed Steps (This Session: 2026-09-19 — Continued)

| Step | Description | Status |
|------|-------------|--------|
| 56 | Create scaffolding script (`scripts/scaffold_primitive.py`) with Jinja2 templates | ✅ Done |
| 57 | Create test generator (`tests/generate_tests.py`) from specs | ✅ Done |
| 58 | Add CI parity gate (`.github/workflows/ci.yml` matrix + parity step) | ✅ Done |
| 59 | Fix test file naming (rename `test_*.py` → `test_<name>_*.py`) | ✅ Done |
| 60 | Scaffold `energy_minimization` primitive (Phase 6, first high-priority) | ✅ Done |
| 61 | Add lazy registry loading (`computronium/primitives/__init__.py` `__getattr__`) | ✅ Done |
| 62 | Run repository health checks (ruff format, ruff check, pyright) | ✅ Done |

### ✅ Completed Steps (This Session: 2026-09-19 — Phase 6 Primitives)

| Step | Description | Status |
|------|-------------|--------|
| 63 | Create `thermodynamic_contrast` primitive (credit_assignment, high priority) | ✅ Done |
| 64 | Create `euclidean` primitive (parameter_update, high priority) | ✅ Done |
| 65 | Create `null` primitive (plasticity, high priority) | ✅ Done |
| 66 | Fix parity.py to handle empty tensor comparison | ✅ Done |
| 67 | Fix test file naming conflicts (test_<name>_*.py pattern) | ✅ Done |
| 68 | Run all primitive/algorithm/registry tests | ✅ Done (299 passed) |
| 69 | Run integration/property tests | ✅ Done |
| 70 | Run repository health checks (ruff format, ruff check, pyright) | ✅ Done |

### ✅ Completed Steps (This Session: 2026-09-19 — Lint & Type Fixes)

| Step | Description | Status |
|------|-------------|--------|
| 71 | Fix ruff rule codes in pyproject.toml for ruff 0.15.9 (E501, PLR2004, PLR6301, ARG001, N806, RSE102, TRY003, RUF001-3, PLR0133, RUF069, ERA001, RUF100, RUF103) | ✅ Done |
| 72 | Fix noqa comments in all primitive/algorithm __init__.py files (RUF067, PLE0605, I001, INP001) | ✅ Done |
| 73 | Add missing test dependencies (matplotlib, plotly) | ✅ Done |
| 74 | Run ruff format on all new files | ✅ Done |
| 75 | Run ruff check on primitives/algorithms — all clean | ✅ Done |
| 76 | Run pyright on primitives/algorithms — 0 errors, 2 warnings (dynamic __all__) | ✅ Done |
| 77 | Run full primitive/algorithm/acceleration test suite (355 tests) | ✅ Done |
| 78 | Run integration/property tests (38 tests) | ✅ Done |

### ✅ Completed Steps (This Session: 2026-09-19 — Phase 6 feedforward_dag)

| Step | Description | Status |
|------|-------------|--------|
| 79 | Create `feedforward_dag` primitive (geometry, high priority) | ✅ Done |
| 80 | Add feedforward_dag to lazy registry loading (primitives/__init__.py, primitives/geometry/__init__.py) | ✅ Done |
| 81 | Add feedforward_dag tests (10 tests: reference, kernel_parity, cases) | ✅ Done |
| 82 | Run ruff format, ruff check, pyright on new primitive | ✅ Done |
| 83 | Run all primitive/algorithm/acceleration tests | ✅ Done (203 tests passed) |
| 84 | Run integration/property tests | ✅ Done |

### ✅ Completed Steps (This Session: 2026-09-19 — Phase 6 recurrent_attractor + digital)

| Step | Description | Status |
|------|-------------|--------|
| 85 | Create `recurrent_attractor` primitive (geometry, high priority) | ✅ Done |
| 86 | Add recurrent_attractor to lazy registry loading (primitives/__init__.py, primitives/geometry/__init__.py) | ✅ Done |
| 87 | Add recurrent_attractor tests (10 tests: reference, kernel_parity, cases) | ✅ Done |
| 88 | Create `digital` primitive (substrate, high priority) with make_substrate factory pattern | ✅ Done |
| 89 | Add digital to lazy registry loading (primitives/__init__.py, primitives/substrate/__init__.py) | ✅ Done |
| 90 | Add digital tests (12 tests: reference, kernel_parity, cases) | ✅ Done |
| 91 | Fix central registry test to skip geometry/substrate primitives | ✅ Done |
| 92 | Run ruff format, ruff check, pyright on new primitives | ✅ Done |
| 93 | Run all primitive/algorithm/acceleration tests (384 passed, 8 skipped) | ✅ Done |
| 94 | Run integration/property tests (43 passed) | ✅ Done |

### ✅ Completed Steps (This Session: 2026-09-19 — Phase 6 Week 2 Primitives)

| Step | Description | Status |
|------|-------------|--------|
| 95 | Create `spike_integration` primitive (state_dynamics, high priority) | ✅ Done |
| 96 | Create `reverse_mode` primitive (credit_assignment, high priority) with GradientCredit | ✅ Done |
| 97 | Create `spectral_constrained` primitive (parameter_update, medium priority) | ✅ Done |
| 98 | Create `substrate_coupled` primitive (plasticity, medium priority) | ✅ Done |
| 99 | Create `memristive` primitive (substrate, medium priority) with factory pattern | ✅ Done |
| 100 | Create `neuromorphic` primitive (substrate, medium priority) with factory pattern | ✅ Done |
| 101 | Fix test file naming to `test_<name>_*.py` pattern for all new primitives | ✅ Done |
| 102 | Fix central registry test to use separate cases for reference/kernel (autograd safety) | ✅ Done |
| 103 | Run ruff format, ruff check, pyright on all new primitives | ✅ Done |
| 104 | Run all primitive/algorithm/acceleration tests (448 passed, 12 skipped) | ✅ Done |
| 105 | Run integration/property tests (38 passed) | ✅ Done |

### ✅ Completed Steps (This Session: 2026-09-19 — Phase 6 Week 3 Primitives)

| Step | Description | Status |
|------|-------------|--------|
| 106 | Create `instantaneous_pass` primitive (state_dynamics, medium priority) | ✅ Done |
| 107 | Create `target_inversion` primitive (credit_assignment, medium priority) | ✅ Done |
| 108 | Create `closed_form_ridge` primitive (plasticity, medium priority) | ✅ Done |
| 109 | Create `temporal_psi` primitive (plasticity, medium priority) | ✅ Done |
| 110 | Create `fabric_pc` primitive (geometry, medium priority) using GraphGeometry | ✅ Done |
| 111 | Create `ntm` primitive (geometry, medium priority) with NtmGeometry | ✅ Done |
| 112 | Create `nca` primitive (geometry, medium priority) with NcaGeometry | ✅ Done |
| 113 | Fix test file naming to `test_<name>_*.py` pattern for all new primitives | ✅ Done |
| 114 | Run ruff format, ruff check, pyright on all new primitives | ✅ Done |
| 115 | Run all primitive/algorithm/acceleration tests (519 passed, 18 skipped) | ✅ Done |
| 116 | Run integration/property tests (10 passed) | ✅ Done |
| 117 | Update TODO32.md with Week 3 completion status | ✅ Done |

### 📋 Remaining Work

Per the plan, future phases include:

#### Phase 6: Remaining Primitives (6 Axes × ~5 each = ~30 primitives)

Each primitive follows the 6-file template (`spec.py`, `reference.py`, `kernel.py`, `cases.py`, `__init__.py`, tests). Reference delegates to ontology class; kernel starts as reference fallback, Triton added later.

**Use scaffolding**: `uv run python scripts/scaffold_primitive.py --axis <axis> --name <name> ...` (see Force Multipliers)

| Axis | Primitive | Ontology Class | Priority | Dependencies | Scaffold Command |
|------|-----------|----------------|----------|--------------|------------------|
| **state_dynamics** | ✅ `energy_minimization` | `EnergyMinimizationDynamics` | **High** | - | `--axis state_dynamics --name energy_minimization --ontology-class EnergyMinimizationDynamics --ontology-module computronium.ontology.dynamics --config StateDynamicsConfig.energy_minimization` |
| | ✅ `spike_integration` | `SpikeIntegrationDynamics` | **High** | - | `--axis state_dynamics --name spike_integration --ontology-class SpikeIntegrationDynamics --ontology-module computronium.ontology.dynamics --config StateDynamicsConfig.spike_integration` |
| | ✅ `instantaneous_pass` | `InstantaneousDynamics` | Medium | - | `--axis state_dynamics --name instantaneous_pass --ontology-class InstantaneousDynamics --ontology-module computronium.ontology.dynamics --config StateDynamicsConfig.instantaneous` |
| | `lazy_state_dynamics` | `LazyStateDynamics` | Low | - | `--axis state_dynamics --name lazy_state_dynamics --ontology-class LazyStateDynamics --ontology-module computronium.ontology.dynamics --config StateDynamicsConfig.lazy_state_dynamics` |
| | `diffusion` | `DiffusionDynamics` | Low | - | `--axis state_dynamics --name diffusion --ontology-class DiffusionDynamics --ontology-module computronium.ontology.dynamics --config StateDynamicsConfig.diffusion` |
| **credit_assignment** | ✅ `reverse_mode` | `GradientCredit` | **High** | - | `--axis credit_assignment --name reverse_mode --ontology-class GradientCredit --ontology-module computronium.ontology.credit --config CreditAssignmentConfig.gradient` |
| | ✅ `thermodynamic_contrast` | `ThermodynamicContrast` | **High** | - | `--axis credit_assignment --name thermodynamic_contrast --ontology-class ThermodynamicContrast --ontology-module computronium.ontology.credit --config CreditAssignmentConfig.thermodynamic_contrast` |
| | ✅ `target_inversion` | `TargetInversionCredit` | Medium | - | `--axis credit_assignment --name target_inversion --ontology-class TargetInversionCredit --ontology-module computronium.ontology.credit --config CreditAssignmentConfig.target_inversion` |
| | `homeostatic` | `HomeostaticCredit` | Low | - | `--axis credit_assignment --name homeostatic --ontology-class HomeostaticCredit --ontology-module computronium.ontology.credit --config CreditAssignmentConfig.homeostatic` |
| **parameter_update** | `euclidean` | `EuclideanUpdate` | **High** | - | `--axis parameter_update --name euclidean --ontology-class EuclideanUpdate --ontology-module computronium.ontology.update --config ParameterUpdateConfig.euclidean` |
| | ✅ `spectral_constrained` | `SpectralConstrainedUpdate` | Medium | - | `--axis parameter_update --name spectral_constrained --ontology-class SpectralConstrainedUpdate --ontology-module computronium.ontology.update --config ParameterUpdateConfig.spectral_constrained` |
| | `natural_gradient` | `NaturalGradientUpdate` | Low | - | `--axis parameter_update --name natural_gradient --ontology-class NaturalGradientUpdate --ontology-module computronium.ontology.update --config ParameterUpdateConfig.natural_gradient` |
| | `elastic_consolidation` | `ElasticConsolidationUpdate` | Low | - | `--axis parameter_update --name elastic_consolidation --ontology-class ElasticConsolidationUpdate --ontology-module computronium.ontology.update --config ParameterUpdateConfig.elastic_consolidation` |
| **plasticity** | `null` | `NullPlasticity` | **High** | - | `--axis plasticity --name null --ontology-class NullPlasticity --ontology-module computronium.ontology.plasticity --config PlasticityConfig.null` |
| | ✅ `substrate_coupled` | `SubstrateCoupledPlasticity` | Medium | substrate primitives | `--axis plasticity --name substrate_coupled --ontology-class SubstrateCoupledPlasticity --ontology-module computronium.ontology.plasticity --config PlasticityConfig.substrate_coupled` |
| | `rule_state` | `RuleStatePlasticity` | Low | - | `--axis plasticity --name rule_state --ontology-class RuleStatePlasticity --ontology-module computronium.ontology.plasticity --config PlasticityConfig.rule_state` |
| | ✅ `closed_form_ridge` | `ClosedFormRidgePlasticity` | Medium | - | `--axis plasticity --name closed_form_ridge --ontology-class ClosedFormRidgePlasticity --ontology-module computronium.ontology.plasticity --config PlasticityConfig.closed_form_ridge` |
| | ✅ `temporal_psi` | `TemporalPsiPlasticity` | Medium | - | `--axis plasticity --name temporal_psi --ontology-class TemporalPsiPlasticity --ontology-module computronium.ontology.plasticity --config PlasticityConfig.temporal_psi` |
| **geometry** | ✅ `feedforward_dag` | `FeedforwardGeometry` | **High** | - | `--axis geometry --name feedforward_dag --ontology-class FeedforwardGeometry --ontology-module computronium.ontology.geometry --config GeometryConfig.feedforward` |
| | ✅ `recurrent_attractor` | `RecurrentGeometry` | **High** | - | `--axis geometry --name recurrent_attractor --ontology-class RecurrentGeometry --ontology-module computronium.ontology.geometry --config GeometryConfig.recurrent` |
| | ✅ `fabric_pc` | `GraphGeometry` | Medium | - | `--axis geometry --name fabric_pc --ontology-class GraphGeometry --ontology-module computronium.ontology.geometry --config GeometryConfig.graph` |
| | `spatial_lattice_3d` | `SpatialLattice3DGeometry` | Low | - | `--axis geometry --name spatial_lattice_3d --ontology-class SpatialLattice3DGeometry --ontology-module computronium.ontology.geometry --config GeometryConfig.spatial_lattice_3d` |
| | ✅ `ntm` | `NtmGeometry` | Medium | - | `--axis geometry --name ntm --ontology-class NtmGeometry --ontology-module computronium.ontology.geometry --config GeometryConfig.ntm` |
| | ✅ `nca` | `NcaGeometry` | Medium | - | `--axis geometry --name nca --ontology-class NcaGeometry --ontology-module computronium.ontology.geometry --config GeometryConfig.nca` |
| **substrate** | ✅ `digital` | `DigitalSubstrate` | **High** | - | `--axis substrate --name digital --ontology-class DigitalSubstrate --ontology-module computronium.ontology.substrate --config SubstrateConfig.digital` |
| | ✅ `memristive` | `MemristiveSubstrate` | Medium | - | `--axis substrate --name memristive --ontology-class MemristiveSubstrate --ontology-module computronium.ontology.substrate --config SubstrateConfig.memristive` |
| | ✅ `neuromorphic` | `NeuromorphicSubstrate` | Medium | - | `--axis substrate --name neuromorphic --ontology-class NeuromorphicSubstrate --ontology-module computronium.ontology.substrate --config SubstrateConfig.neuromorphic` |
| | `photonic` | `PhotonicSubstrate` | Low | - | `--axis substrate --name photonic --ontology-class PhotonicSubstrate --ontology-module computronium.ontology.substrate --config SubstrateConfig.photonic` |
| | `quantum` | `QuantumSubstrate` | Low | - | `--axis substrate --name quantum --ontology-class QuantumSubstrate --ontology-module computronium.ontology.substrate --config SubstrateConfig.quantum` |
| | `noisy` | `NoisySubstrate` | Low | - | `--axis substrate --name noisy --ontology-class NoisySubstrate --ontology-module computronium.ontology.substrate --config SubstrateConfig.noisy` |
| | `sparse` | `SparseSubstrate` | Low | - | `--axis substrate --name sparse --ontology-class SparseSubstrate --ontology-module computronium.ontology.substrate --config SubstrateConfig.sparse` |
| | `complex` | `ComplexSubstrate` | Low | - | `--axis substrate --name complex --ontology-class ComplexSubstrate --ontology-module computronium.ontology.substrate --config SubstrateConfig.complex` |
| | `ternary` | `TernarySubstrate` | Low | - | `--axis substrate --name ternary --ontology-class TernarySubstrate --ontology-module computronium.ontology.substrate --config SubstrateConfig.ternary` |

**Substrate/Geometry Note**: These are structural primitives. Their `reference.py` exposes `make_substrate()` / `make_geometry()` factories, not `step(case)`. Parity tests verify structural equivalence via integration tests, not `assert_parity`. See Force Multiplier #6.

### Phase 6 Execution Order (Dependency-Aware)

1. **Week 1**: ✅ `energy_minimization`, ✅ `thermodynamic_contrast`, ✅ `euclidean`, ✅ `null`, ✅ `feedforward_dag`, ✅ `recurrent_attractor`, ✅ `digital` (7 primitives, unblocks most algorithms)
2. **Week 2**: ✅ `spike_integration`, ✅ `reverse_mode`, ✅ `spectral_constrained`, ✅ `substrate_coupled`, ✅ `memristive`, ✅ `neuromorphic` (6 primitives)
3. **Week 3**: ✅ `instantaneous_pass`, ✅ `target_inversion`, ✅ `closed_form_ridge`, ✅ `temporal_psi`, ✅ `fabric_pc`, ✅ `ntm`, ✅ `nca` (7 primitives)
4. **Week 4**: `lazy_state_dynamics`, `diffusion`, `homeostatic`, `natural_gradient`, `elastic_consolidation`, `rule_state`, `spatial_lattice_3d`, `photonic`, `quantum`, `noisy`, `sparse`, `complex`, `ternary` (13 primitives, low priority)

### Phase 7: Additional Algorithms (beyond current 14)

| Algorithm | Coordinate (S×G×D×P×C×U) | Primitives Used | Priority | Scaffold Command |
|-----------|--------------------------|-----------------|----------|------------------|
| `directed_ep` | Digital × Recurrent × EnergyMin × Null × RandomProj × Euclidean | energy_minimization, random_projections, euclidean | Medium | `--name directed_ep --family equilibrium_propagation --primitives energy_minimization,random_projections,euclidean --factory create_directed_ep_mlp` |
| `finite_nudge_ep` | Digital × Recurrent × EnergyMin(β≥1) × Null × ThermoContrast × Euclidean | energy_minimization, thermodynamic_contrast, euclidean | Medium | `--name finite_nudge_ep --family equilibrium_propagation --primitives energy_minimization,thermodynamic_contrast,euclidean --factory create_finite_nudge_ep_mlp` |
| `ternary_eqprop` | Ternary × Recurrent × EnergyMin × Null × ThermoContrast × Euclidean | energy_minimization, thermodynamic_contrast, euclidean, ternary substrate | Low | `--name ternary_eqprop --family equilibrium_propagation --primitives energy_minimization,thermodynamic_contrast,euclidean,ternary --factory create_ternary_eqprop_mlp` |
| `momentum_eqprop` | Digital × Recurrent × EnergyMin(momentum) × Null × ThermoContrast × Euclidean | energy_minimization(momentum), thermodynamic_contrast, euclidean | Low | `--name momentum_eqprop --family equilibrium_propagation --primitives energy_minimization,thermodynamic_contrast,euclidean --factory create_momentum_eqprop_mlp` |
| `sparse_eqprop` | Sparse × Recurrent × EnergyMin × Null × ThermoContrast × Euclidean | energy_minimization, thermodynamic_contrast, euclidean, sparse substrate | Low | `--name sparse_eqprop --family equilibrium_propagation --primitives energy_minimization,thermodynamic_contrast,euclidean,sparse --factory create_sparse_eqprop_mlp` |
| `diffusion_eqprop` | Digital × Recurrent × Diffusion × Null × ThermoContrast × Euclidean | diffusion, thermodynamic_contrast, euclidean | Low | `--name diffusion_eqprop --family equilibrium_propagation --primitives diffusion,thermodynamic_contrast,euclidean --factory create_diffusion_eqprop_mlp` |
| `holomorphic_ep` | Quantum × Recurrent × EnergyMin × Null × ThermoContrast × Euclidean | energy_minimization, thermodynamic_contrast, euclidean, quantum substrate | Low | `--name holomorphic_ep --family equilibrium_propagation --primitives energy_minimization,thermodynamic_contrast,euclidean,quantum --factory create_holomorphic_ep_mlp` |

**Algorithm Scaffolding**: `uv run python scripts/scaffold_algorithm.py ...` generates factory + reference + kernel + cases + tests.

#### Phase 8: Triton Kernel Implementation

Primitives currently falling back to reference; need Triton kernels:

| Primitive | Current Fallback | Target Kernel | Effort | Depends On |
|-----------|-----------------|---------------|--------|------------|
| `predictive_settling` | `torch.compile` | Triton fused layered settle | Medium | Phase 6: energy_minimization |
| `random_projections` | reference | Triton batched matmul + projection | Medium | - |
| `local_goodness` | reference | Triton layer-local goodness | Medium | - |
| `temporal_trace` | reference | Triton STDP trace update | Medium | - |
| `muon` | reference | Triton orthogonalization (Newton-Schulz) | High | - |
| `fast_weight` | reference | Triton fast-weight outer product | Medium | - |
| `routing` | reference | Triton gating/routing | Medium | Phase 6: substrate_coupled |
| `tile_mesh` | reference | Triton tile routing | Medium | - |
| `energy_minimization` | reference | Triton energy gradient + settle | Medium | Phase 6 |
| `spike_integration` | reference | Triton LIF/Izhikevich step | Medium | Phase 6 |
| `thermodynamic_contrast` | reference | Triton free/nudged contrast | Medium | Phase 6 |
| `target_inversion` | reference | Triton inverse mapping | Medium | Phase 6 |
| `spectral_constrained` | reference | Triton spectral norm projection | Medium | Phase 6 |

**Kernel Development Order** (maximizes reuse):
1. `random_projections` → reusable batched matmul primitive
2. `local_goodness` → reusable layer-wise reduction
3. `energy_minimization` → reusable gradient + settle loop
4. `thermodynamic_contrast` → reuses energy_minimization kernels
5. `fast_weight` / `routing` → outer product + gating
6. `muon` → standalone Newton-Schulz
7. `tile_mesh` → sparse routing
8. `spike_integration` → LIF step
9. `target_inversion` → inverse mapping
10. `spectral_constrained` → spectral norm
11. `temporal_trace` → STDP trace
12. `predictive_settling` → layered settle (depends on energy_minimization)

### 🎯 Immediate Next Steps (Do This Week) — ✅ ALL COMPLETE

| Step | Task | Command/Action | Done When |
|------|------|----------------|-----------|
| 1 | Create scaffolding script | `scripts/scaffold_primitive.py` with Jinja2 templates | ✅ Generates working primitive |
| 2 | Create test generator | `tests/generate_tests.py` from spec + case | ✅ Generates 3 test files |
| 3 | Add CI parity gate | `.github/workflows/ci.yml` matrix + parity step | ✅ PR shows matrix comment |
| 4 | Fix test file naming | Rename `test_*.py` → `test_<name>_*.py` | ✅ `pytest tests/` works globally |
| 5 | Scaffold first Phase 6 primitive | `energy_minimization` (high priority, unblocks eqprop kernels) | ✅ Primitive + tests pass |
| 6 | Add lazy registry loading | `computronium/primitives/__init__.py` `__getattr__` | ✅ Import time ~5ms |

### 💡 New Improvement Opportunities

1. **Test file naming**: ✅ DONE - Renamed to `test_<name>_reference.py`, `test_<name>_kernel_parity.py`, `test_<name>_cases.py` pattern. `pytest tests/` now works globally.

2. **Microbench CLI**: The microbench.py module exists but could be enhanced with more options (`--iterations`, `--warmup`, JSON output to file, `--device` selection, CSV summary).

3. **Microbench CLI**: The microbench.py module exists but could be enhanced with more options (`--iterations`, `--warmup`, JSON output to file, `--device` selection, CSV summary).

4. **Matrix output**: The matrix.py utility now outputs JSON/Markdown for CI integration (GitHub Actions table, PR comments).

5. **Registry discovery**: ✅ DONE - Lazy loading implemented in `computronium/primitives/__init__.py` and `computronium/algorithms/__init__.py` via `__getattr__`. Import time ~5ms.

6. **Documentation**: Consider adding local README.md files to complex primitives (optional per plan). Template: Purpose, Mathematics, Axes, Reference, Kernel, Parity, Status, Known Issues.

7. **Documentation**: Consider adding local README.md files to complex primitives (optional per plan). Template: Purpose, Mathematics, Axes, Reference, Kernel, Parity, Status, Known Issues.

8. **Pre-existing lint debt**: Old `acceleration/` modules (fa_kernels.py, triton_kernels.py, pc_kernels.py, ff_kernels.py, hebbian_kernels.py, snn_kernels.py, tp_kernels.py, tile_kernels.py, mep_kernels.py, backprop_kernels.py, contrastive_kernels.py, pcalm_kernels.py, eqprop_kernel_backend.py, compile.py, kernels.py, kernel_backend.py, backends.py) have invalid `# noqa` directives (missing comma-separated codes). These are legacy files not part of the new primitives/algorithms structure. Fix when touched.

9. **Ruff rule code drift**: Ruff 0.15.9 changed rule codes (e.g., `line-too-long` → `E501`, `non-empty-init-module` → `RUF067`, `invalid-all-format` → `PLE0605`). The new primitives/algorithms code uses correct codes; legacy code may need updates during Register C hygiene pass.

### 🚀 Leverage New Architecture: Force Multipliers for Future Work

The new `primitives/` + `algorithms/` + `acceleration/` structure enables several force multipliers that dramatically reduce effort for future additions:

#### 1. Code Generation / Scaffolding (NEW: `scripts/scaffold_primitive.py`, `scripts/scaffold_algorithm.py`)

**Problem**: Creating a new primitive requires 6 files + 3 test files with repetitive boilerplate.

**Solution**: CLI scaffolding that generates complete, working primitive/algorithm from a spec:

```bash
# Generate primitive from minimal spec
uv run python scripts/scaffold_primitive.py \
    --axis state_dynamics \
    --name energy_minimization \
    --ontology-class EnergyMinimizationDynamics \
    --ontology-module computronium.ontology.dynamics \
    --config-class StateDynamicsConfig.energy_minimization

# Generate algorithm from primitive list
uv run python scripts/scaffold_algorithm.py \
    --name directed_ep \
    --family equilibrium_propagation \
    --primitives energy_minimization,random_projections,euclidean \
    --factory create_directed_ep_mlp
```

**Outputs**: All 6 primitive files + 3 test files + registry registration, ready to edit.

**Effort reduction**: ~90% boilerplate eliminated. New primitive in 30 seconds vs 30 minutes.

#### 2. Test Generation from Specs (NEW: `tests/generate_tests.py`)

**Problem**: Test files (`test_reference.py`, `test_kernel_parity.py`, `test_cases.py`) are nearly identical across primitives.

**Solution**: Generate tests from the `ImplementationSpec` + `Case` dataclass:

```python
# In spec.py, add:
TEST_CONFIG = {
    "reference_tests": ["deterministic", "different_seeds", "returns_expected_type"],
    "parity_tests": ["default_tolerance", "different_seeds"],
    "case_tests": ["deterministic", "config_structure"],
}

# Generate:
uv run python tests/generate_tests.py --spec primitive.state_dynamics.energy_minimization
```

**Benefits**: Tests stay in sync with spec changes; new primitives get tests automatically.

#### 3. CI Integration: Parity Gates & Matrix Reports

**Add to CI pipeline** (`.github/workflows/ci.yml`):

```yaml
- name: Parity Gate
  run: |
    uv run python -m computronium.acceleration.matrix --format json > matrix.json
    uv run python -m computronium.acceleration.microbench --all --format json > bench.json
    uv run pytest tests/acceleration/test_all_implementations.py -q

- name: Comment PR with Matrix
  uses: actions/github-script@v7
  with:
    script: |
      const matrix = require('./matrix.json');
      // Post formatted table as PR comment
```

**Artifacts**: Matrix table, parity reports, microbench results as CI artifacts for regression tracking.

#### 4. Kernel Development Workflow (NEW: `scripts/kernel_dev.py`)

**Problem**: Writing Triton kernels is error-prone; parity testing is manual.

**Solution**: Scaffold + guided development:

```bash
# 1. Scaffold kernel with parity harness
uv run python scripts/scaffold_kernel.py \
    --primitive primitive.state_dynamics.energy_minimization \
    --technology triton

# 2. Run parity in watch mode during development
uv run python scripts/kernel_dev.py \
    --primitive primitive.state_dynamics.energy_minimization \
    --watch  # re-runs parity on file change

# 3. Microbench comparison
uv run python -m computronium.acceleration.microbench \
    --id primitive.state_dynamics.energy_minimization \
    --backend reference,kernel \
    --device cpu,cuda \
    --iterations 100
```

**Template includes**: Triton kernel stub, reference delegate, `is_available()`, parity tolerance from spec.

#### 5. Algorithm Composition Validation (NEW: `scripts/validate_composition.py`)

**Problem**: `uses_primitives` in algorithm spec may drift from actual imports.

**Solution**: Static validation:

```python
# In algorithm spec.py:
USES_PRIMITIVES = (
    "primitive.state_dynamics.energy_minimization",
    "primitive.credit_assignment.thermodynamic_contrast",
    "primitive.parameter_update.euclidean",
)

# Validation script checks:
# 1. All listed primitives exist in registry
# 2. Algorithm reference.py imports only from listed primitives (+ ontology)
# 3. No undeclared primitive dependencies
```

Run in CI: `uv run python scripts/validate_composition.py --all-algorithms`

#### 6. Substrate/Geometry: Structural Primitives (Special Handling)

Substrate and Geometry primitives differ from computational axes:
- **No `step(case)` interface** - they construct system topology/state space
- **Factory-style**: `make_substrate(spec)`, `make_geometry(config)`
- **Kernel = JIT/compile optimization** (e.g., sparse matmul, IR-drop solver)

**Template adjustment** for substrate/geometry:
```python
# substrate/digital/spec.py
SPEC = ImplementationSpec(
    id="primitive.substrate.digital",
    kind="primitive",
    axis="substrate",
    reference_entrypoint="computronium.primitives.substrate.digital.reference.make_substrate",
    kernel_entrypoint="computronium.primitives.substrate.digital.kernel.make_substrate",
    # No parity.test - structural equivalence verified by integration tests
)
```

#### 7. Documentation Generation from Specs (NEW: `scripts/generate_docs.py`)

Specs carry rich metadata: `summary`, `equations`, `invariants`, `notes`, `tags`, `evidence_ids`.

**Generate**:
- `docs/primitives/<axis>/<name>.md` - per-primitive docs
- `docs/algorithms/<name>.md` - per-algorithm docs
- `docs/IDENTITY_CARDS.md` - algorithm identity cards (already exists)
- `docs/IMPLEMENTATION_MATRIX.md` - from `matrix.py`

```bash
uv run python scripts/generate_docs.py --all --output docs/generated/
```

#### 8. Registry: Lazy Loading + Explicit Registration

Current: eager import scans all submodules (~2s startup).

**Option A**: Lazy loading with `__getattr__` in `computronium.primitives` + `computronium.algorithms`
**Option B**: Explicit registration via `pyproject.toml` entry points (faster, explicit)

```toml
# pyproject.toml
[project.entry-points."computronium.primitives"]
state_dynamics = "computronium.primitives.state_dynamics:register_all"
credit_assignment = "computronium.primitives.credit_assignment:register_all"
# ...
```

#### 9. Benchmark Harness: Comparative Regression Tracking

Extend microbench to track performance over time:

```bash
# Store results with git SHA
uv run python -m computronium.acceleration.microbench \
    --id primitive.state_dynamics.pc_alm_settling \
    --backend kernel \
    --device cuda \
    --output benchmarks/pcalm_settling_${GIT_SHA}.json
```

**Dashboard**: `scripts/bench_dashboard.py` plots latency/memory over commits.

#### 10. Property Tests from Spec Invariants

Spec `invariants` tuple can generate Hypothesis property tests:

```python
# spec.py
invariants=(
    "settling residual decreases or remains bounded",
    "state remains finite",
    "deterministic under fixed seed",
)

# scripts/invariant_to_property.py generates:
@given(data=st.data())
def test_settling_residual_decreases(data):
    case = make_case(seed=data.draw(st.integers(0, 1000)))
    output = reference_step(case)
    # Check residual decreased...
```

### 🔧 Facilitating Changes (for next sessions)

- The `StateDynamics` protocol now has a consistent signature across all implementations (including `on_step` callback)
- Registry discovery is working and testable via `all_specs()`
- Parity testing framework is in place and validated
- Microbenchmark infrastructure exists for engineering smoke tests
- Primitive template validated with 10 primitives (pc_alm_settling, predictive_settling, random_projections, local_goodness, temporal_trace, muon, tile_mesh, fast_weight, routing, pc_alm)
- Phase 3 (high-value primitives migration) complete: geometry/tile_mesh, plasticity/fast_weight, plasticity/routing
- Phase 4 (named algorithms migration) complete: 11 algorithms migrated with full test coverage (backprop, fa, eqprop, ff, pepita, pc, hebbian, tile, fast_weight, routing, spiking_snn)
- Phase 5 (missing primitives & algorithms) complete: PCALMCredit primitive, target_prop (tp), dfa algorithms
- Algorithm template validated with 14 algorithms (pcalm + 11 Phase 4 algorithms + tp + dfa)
- All 174 algorithm tests pass (13 tests × 11 Phase 4 algorithms + 13 pcalm tests + 9 tp tests + 9 dfa tests) when run per-directory
- All 125 primitive tests pass (10+7+7+8+7+7+10+12+13+8+10+16+10+4+10) when run per-directory
- All 56 central registry tests pass (2 tests × 28 implementations)
- All existing integration/property tests continue to pass (test_lazy_dynamics, test_pc_alm_validation, test_demo_pc_alm, test_dynamics_wiring_lock)
- All lint checks pass for new primitives/algorithms code (ruff format, ruff check with correct rule codes)
- All pyright type checks pass for new primitives/algorithms code (0 errors, 2 warnings for dynamic `__all__`)
- **Note**: `algorithm.hebbian` covers STDP using LocalGoodnessCredit as proxy; separate `algorithm.stdp` not needed per current design
- **Session complete**: All Phase 1-5 work done. 14 primitives + 14 algorithms registered, 355 tests pass (125 primitive + 174 algorithm + 56 registry), all existing tests pass.
- **This session**: Fixed ruff 0.15.9 rule code drift in pyproject.toml and all __init__.py files; added matplotlib/plotly test dependencies; verified full test suite.

---

# 1. Goals

This refactor should achieve the following:

1. Make algorithm and primitive implementations explicit.
2. Separate mathematical reference implementations from accelerated kernels.
3. Make parity testing a first-class part of the system.
4. Enable lightweight microbenchmarking without running large experiments.
5. Keep the system algorithm-agnostic.
6. Avoid betting on any single algorithm.
7. Enable future absorption of new methods without making absorption itself the goal.
8. Prepare the codebase for implementation dominance across many methods.
9. Keep existing tests working through gradual migration.
10. Prefer self-documenting source code over global documentation.

---

# 2. Non-Goals

This refactor explicitly avoids:

1. A global API rewrite.
2. A large-bang file move.
3. A new top-level “absorption” concept.
4. Long-running experiments.
5. Scientific claim generation.
6. Choosing a flagship algorithm.
7. Building a general-purpose kernel DSL.
8. Adding large numbers of global Markdown documents.

---

# 3. Architectural Doctrine

## 3.1 Primitive

A primitive is a reusable axis-level mechanism.

Examples:

```text
predictive settling
energy minimization
spike integration
random projection credit
local goodness credit
temporal trace credit
fast-weight plasticity
routing plasticity
Muon update
spectral constrained update
tile routing
NTM memory addressing
NCA state transition
```

A primitive usually corresponds to one or more of the six axes:

```text
Substrate
Geometry
StateDynamics
Plasticity
CreditAssignment
ParameterUpdate
```

A primitive may not be a complete trainable algorithm by itself.

---

## 3.2 Algorithm

An algorithm is a named composition of primitives into a usable learning system or method.

Examples:

```text
Backprop
FA
DFA
FF
PEPITA
Predictive Coding
PC-ALM
EqProp
Hebbian learning
STDP
TileNet
Fast-weight method
Routing method
Target Propagation
```

An algorithm composes primitives and may also define its own fused hot path.

---

## 3.3 Acceleration Layer

The acceleration layer is shared infrastructure.

It must not become the home of algorithm-specific mathematics.

It provides:

```text
backend definitions
implementation specs
registry discovery
parity comparison
microbenchmarking
dispatch policy
kernel availability
Triton utilities
profiling hooks
```

---

# 4. Target Source Layout

The target structure is:

```text
computronium/
    acceleration/
        __init__.py
        backends.py
        spec.py
        registry.py
        parity.py
        microbench.py
        dispatch.py
        matrix.py
        triton_utils.py

    primitives/
        __init__.py

        state_dynamics/
            __init__.py
            predictive_settling/
            pc_alm_settling/
            energy_minimization/
            spike_integration/
            instantaneous_pass/
            lazy_state_dynamics/
            diffusion/

        credit_assignment/
            __init__.py
            reverse_mode/
            random_projections/
            local_goodness/
            thermodynamic_contrast/
            temporal_trace/
            target_inversion/
            homeostatic/

        parameter_update/
            __init__.py
            euclidean/
            muon/
            spectral_constrained/
            natural_gradient/
            elastic_consolidation/

        plasticity/
            __init__.py
            null/
            routing/
            fast_weight/
            substrate_coupled/
            rule_state/
            closed_form_ridge/
            temporal_psi/

        geometry/
            __init__.py
            feedforward_dag/
            recurrent_attractor/
            tile_mesh/
            fabric_pc/
            spatial_lattice_3d/
            ntm/
            nca/

        substrate/
            __init__.py
            digital/
            memristive/
            neuromorphic/
            photonic/
            quantum/
            noisy/
            sparse/
            complex/
            ternary/

    algorithms/
        __init__.py

        backprop/
        fa/
        dfa/
        ff/
        pepita/
        pc/
        pcalm/
        eqprop/
        hebbian/
        stdp/
        target_prop/
        tile/
        fast_weight/
        routing/
        snn/
```

Not all directories need to exist immediately.

The structure should grow as primitives and algorithms are migrated.

---

# 5. Dependency Rules

The dependency direction must remain clean.

```text
acceleration/
    may depend only on standard library, torch, and generic utilities
    must not depend on primitive or algorithm internals

primitives/
    may depend on acceleration/
    may depend on core ontology types
    must not depend on algorithms/

algorithms/
    may depend on primitives/
    may depend on acceleration/
    may depend on core system composition utilities

tests/
    may depend on everything
```

This prevents circular imports and keeps the shared layer truly shared.

---

# 6. Shared Acceleration Layer

The acceleration layer becomes the implementation contract layer.

## 6.1 `backends.py`

Purpose:

```text
Define backend names and availability.
```

Recommended content:

```python
from typing import Literal

Backend = Literal[
    "reference",
    "kernel",
]

KernelTechnology = Literal[
    "triton",
    "cuda",
    "torch_compile",
    "cupy",
    "numpy",
]


def kernel_available(technology: KernelTechnology) -> bool:
    """
    Return True if the given kernel technology is usable in the current environment.
    """
    if technology == "triton":
        try:
            import triton  # noqa: F401
            import torch

            return torch.cuda.is_available()
        except Exception:
            return False

    if technology == "cuda":
        import torch

        return torch.cuda.is_available()

    if technology == "torch_compile":
        import torch

        return hasattr(torch, "compile")

    if technology == "cupy":
        try:
            import cupy  # noqa: F401

            return True
        except Exception:
            return False

    if technology == "numpy":
        return True

    return False
```

The important distinction is:

```text
"reference" means the clear Python/PyTorch implementation.
"kernel" means the accelerated implementation exposed by kernel.py.
```

The actual technology used by `kernel.py` is recorded separately, usually as `"triton"`.

---

## 6.2 `spec.py`

Purpose:

```text
Define implementation metadata.
```

Recommended content:

```python
from dataclasses import dataclass, field
from typing import Literal

from computronium.acceleration.backends import Backend, KernelTechnology


ImplementationKind = Literal[
    "primitive",
    "algorithm",
]


ImplementationStatus = Literal[
    "missing",
    "reference_only",
    "kernel_unverified",
    "kernel_verified",
    "microbenched",
    "campaign_ready",
    "deprecated",
]


Axis = Literal[
    "substrate",
    "geometry",
    "state_dynamics",
    "plasticity",
    "credit_assignment",
    "parameter_update",
]


@dataclass(frozen=True, slots=True)
class ParityTolerance:
    max_abs_diff: float = 1e-4
    max_rel_diff: float = 1e-3
    min_cosine: float = 0.999


@dataclass(frozen=True, slots=True)
class ImplementationSpec:
    id: str
    kind: ImplementationKind
    name: str
    reference_entrypoint: str
    kernel_entrypoint: str | None = None
    kernel_technology: KernelTechnology | None = None
    supported_backends: tuple[Backend, ...] = ("reference",)
    parity: ParityTolerance = ParityTolerance()
    status: ImplementationStatus = "reference_only"

    # Primitive metadata
    axis: Axis | None = None

    # Algorithm metadata
    family: str | None = None
    uses_primitives: tuple[str, ...] = ()

    # Self-documentation
    summary: str = ""
    equations: str = ""
    invariants: tuple[str, ...] = ()
    notes: str = ""

    # Future hooks
    tags: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
```

The `id` field should be stable and machine-readable.

Recommended ID conventions:

```text
primitive.state_dynamics.predictive_settling
primitive.credit_assignment.random_projections
primitive.parameter_update.muon
primitive.plasticity.fast_weight
algorithm.backprop
algorithm.fa
algorithm.pcalm
algorithm.eqprop
```

---

## 6.3 `registry.py`

Purpose:

```text
Register and discover implementations.
```

Recommended content:

```python
from computronium.acceleration.spec import ImplementationSpec

_REGISTRY: dict[str, ImplementationSpec] = {}


def register(spec: ImplementationSpec) -> None:
    if spec.id in _REGISTRY:
        raise ValueError(f"implementation already registered: {spec.id}")
    _REGISTRY[spec.id] = spec


def get(implementation_id: str) -> ImplementationSpec:
    return _REGISTRY[implementation_id]


def all_specs() -> tuple[ImplementationSpec, ...]:
    return tuple(_REGISTRY.values())


def primitives() -> tuple[ImplementationSpec, ...]:
    return tuple(spec for spec in _REGISTRY.values() if spec.kind == "primitive")


def algorithms() -> tuple[ImplementationSpec, ...]:
    return tuple(spec for spec in _REGISTRY.values() if spec.kind == "algorithm")
```

For now, registration can be explicit.

Later, discovery can scan:

```text
computronium.primitives
computronium.algorithms
```

and import modules that expose `SPEC`.

---

## 6.4 `parity.py`

Purpose:

```text
Compare reference and kernel outputs.
```

Recommended content:

```python
from typing import Any

import torch

from computronium.acceleration.spec import ParityTolerance


def _flatten(value: Any) -> torch.Tensor:
    if isinstance(value, torch.Tensor):
        return value.detach().reshape(-1).float()

    if isinstance(value, dict):
        parts = [_flatten(v) for v in value.values()]
        return torch.cat(parts) if parts else torch.tensor([])

    if isinstance(value, tuple | list):
        parts = [_flatten(v) for v in value]
        return torch.cat(parts) if parts else torch.tensor([])

    return torch.as_tensor(value).detach().reshape(-1).float()


def compare(reference: Any, kernel: Any) -> dict[str, float]:
    ref = _flatten(reference)
    acc = _flatten(kernel)

    abs_diff = torch.abs(ref - acc)
    max_abs_diff = abs_diff.max().item()

    rel_diff = abs_diff / (torch.abs(ref) + 1e-8)
    max_rel_diff = rel_diff.max().item()

    if ref.numel() == 0:
        cosine = 1.0
    else:
        cosine = torch.nn.functional.cosine_similarity(
            ref.unsqueeze(0),
            acc.unsqueeze(0),
        ).item()

    return {
        "max_abs_diff": max_abs_diff,
        "max_rel_diff": max_rel_diff,
        "cosine": cosine,
    }


def assert_parity(reference: Any, kernel: Any, tolerance: ParityTolerance) -> dict[str, float]:
    report = compare(reference, kernel)

    assert report["max_abs_diff"] <= tolerance.max_abs_diff, report
    assert report["max_rel_diff"] <= tolerance.max_rel_diff, report
    assert report["cosine"] >= tolerance.min_cosine, report

    return report
```

This utility should remain generic.

It must not know about specific algorithms.

---

## 6.5 `microbench.py`

Purpose:

```text
Run tiny, non-scientific benchmark smoke tests.
```

Recommended command form:

```bash
uv run python -m computronium.acceleration.microbench \
    --id primitive.state_dynamics.pc_alm_settling \
    --backend reference,kernel \
    --device cpu \
    --steps 3
```

The microbenchmark runner should:

1. Load the implementation module.
2. Call its `make_case()`.
3. Run the selected backend.
4. Measure wall time.
5. Print JSON to stdout.
6. Avoid making scientific claims.
7. Use tiny shapes by default.

Example output:

```json
{
  "id": "primitive.state_dynamics.pc_alm_settling",
  "backend": "kernel",
  "device": "cpu",
  "steps": 3,
  "wall_time_s": 0.004,
  "status": "ok"
}
```

Microbenchmarking is for engineering smoke tests, not campaign evidence.

---

## 6.6 `dispatch.py`

Purpose:

```text
Select a backend safely.
```

Recommended policy:

```python
def select_backend(spec: ImplementationSpec, requested: str = "auto") -> str:
    if requested == "reference":
        return "reference"

    if requested == "kernel":
        if "kernel" not in spec.supported_backends:
            raise ValueError(f"no kernel backend for {spec.id}")
        return "kernel"

    if requested == "auto":
        if (
            "kernel" in spec.supported_backends
            and spec.status in {"kernel_verified", "microbenched", "campaign_ready"}
        ):
            return "kernel"
        return "reference"

    raise ValueError(f"unknown backend request: {requested}")
```

This allows future callers to use:

```text
auto
reference
kernel
```

without knowing implementation details.

---

## 6.7 `matrix.py`

Purpose:

```text
Generate an implementation matrix from the registry.
```

This replaces the need for a global Markdown implementation matrix.

Recommended command:

```bash
uv run python -m computronium.acceleration.matrix
```

Example output:

```text
ID                                                    KIND       AXIS                BACKENDS          STATUS
primitive.state_dynamics.predictive_settling          primitive  state_dynamics      reference,kernel  kernel_verified
primitive.credit_assignment.random_projections        primitive  credit_assignment   reference,kernel  kernel_verified
primitive.parameter_update.muon                       primitive  parameter_update    reference         reference_only
algorithm.backprop                                    algorithm                      reference,kernel  kernel_verified
algorithm.pcalm                                       algorithm                      reference,kernel  kernel_verified
```

This keeps the source of truth in code.

---

# 7. Primitive Package Template

Every primitive package **wraps an existing ontology class** from `computronium.ontology.*` with the uniform template (`spec.py`, `reference.py`, `kernel.py`, `cases.py`). The primitive directory does not contain the mathematical implementation — it delegates to the ontology class.

Example:

```text
computronium/primitives/state_dynamics/pc_alm_settling/
    __init__.py
    spec.py
    reference.py      # delegates to PCALMDynamics
    kernel.py         # delegates to pcalm_kernels
    cases.py
    README.md         # optional
```

`README.md` is optional. Prefer docstrings unless the mathematics needs extra explanation.

---

## 7.1 Primitive `__init__.py`

Example:

```python
"""
PC-ALM settling primitive.

This primitive implements the primal-dual settling dynamics used by
Augmented Lagrangian Predictive Coding.

Reference implementation:
    computronium.primitives.state_dynamics.pc_alm_settling.reference

Accelerated kernel:
    computronium.primitives.state_dynamics.pc_alm_settling.kernel
"""

from computronium.acceleration.registry import register

from .spec import SPEC
from .reference import step as reference_step
from .kernel import step as kernel_step
from .cases import make_case

register(SPEC)

__all__ = [
    "SPEC",
    "reference_step",
    "kernel_step",
    "make_case",
]
```

If the kernel is optional or unavailable, `kernel.py` should still import safely and expose availability information.

---

## 7.2 Primitive `spec.py`

Example:

```python
from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.pc_alm_settling",
    kind="primitive",
    name="PC-ALM Settling",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.pc_alm_settling.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.state_dynamics.pc_alm_settling.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    summary="Primal-dual settling dynamics for PC-ALM.",
    equations="""
    x_{t+1} = ...
    lambda_{t+1} = ...
    """,
    invariants=(
        "settling residual decreases or remains bounded",
        "state remains finite",
        "deterministic under fixed seed",
    ),
    notes="Accelerated kernel should preserve the settled state within tolerance.",
    tags=("predictive_coding", "augmented_lagrangian", "settling"),
)
```

---

## 7.3 Primitive `reference.py`

Example (wraps existing ontology class):

```python
"""
Reference implementation for PC-ALM settling.

Delegates to computronium.ontology.dynamics.PCALMDynamics (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from computronium.ontology.dynamics import PCALMDynamics, StateDynamicsConfig
from computronium.ontology.system import SystemState


def step(case: Any) -> Any:
    """
    Execute one reference step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.
    """
    config = StateDynamicsConfig.pc_alm(
        max_steps=case.config["steps"],
        step_size=case.config.get("step_size", 0.1),
        rho=case.config.get("rho", 1.0),
        beta=case.config.get("beta", 0.5),
    )
    dynamics = PCALMDynamics(config)
    # Convert case to SystemState, run settle, return result
    state = _case_to_system_state(case)
    return dynamics.settle(state, case.config.get("target"))
```

The reference implementation should:

1. Be readable — thin wrapper around ontology class.
2. Be deterministic — same seed, same output.
3. Avoid clever optimizations — ontology class is the reference.
4. Avoid backend-specific logic — pure Python/PyTorch.
5. Be close to the mathematics — ontology class defines the math.

---

## 7.4 Primitive `kernel.py`

Example (delegates to existing acceleration kernels):

```python
"""
Accelerated kernel for PC-ALM settling.

Delegates to computronium.acceleration.pcalm_kernels.fused_dual_primal_update
and _compiled_pcalm_settle. Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.acceleration.pcalm_kernels import (
    fused_dual_primal_update,
    _compiled_pcalm_settle,
    HAS_TRITON_PCALM,
)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and HAS_TRITON_PCALM


def step(case: Any) -> Any:
    """
    Execute one accelerated step using the opaque case object.
    """
    if not is_available():
        from .reference import step as reference_step
        return reference_step(case)

    # Use compiled settle loop or fused Triton kernels
    return _compiled_pcalm_settle(...)
```

The file is named `kernel.py`, not `triton.py`.

The backend technology is recorded in the spec and inside the module.

If multiple kernel technologies are needed later, `kernel.py` can expose:

```python
BACKENDS = {
    "triton": triton_step,
    "cuda": cuda_step,
}

DEFAULT_BACKEND = "triton"


def step(case):
    return BACKENDS[DEFAULT_BACKEND](case)
```

But the initial template should remain simple.

---

## 7.5 Primitive `cases.py`

Purpose:

```text
Provide tiny deterministic cases for parity tests and microbenchmarks.
```

Example:

```python
"""
Deterministic test cases for PC-ALM settling.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    prediction: torch.Tensor
    multiplier: torch.Tensor
    config: dict[str, Any]


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    state = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)
    prediction = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)
    multiplier = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)

    config = {
        "steps": 3,
        "rho": 0.1,
        "tol": 1e-4,
    }

    return Case(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config=config,
    )
```

Every primitive and algorithm should provide such a case factory.

This makes parity and microbenchmarking uniform.

---

# 8. Algorithm Package Template

An algorithm package composes primitives into a named method.

Example:

```text
computronium/algorithms/pcalm/
    __init__.py
    spec.py
    reference.py
    kernel.py
    factory.py
    cases.py
    README.md
```

---

## 8.1 Algorithm `__init__.py`

Example (wraps existing factory, composes primitives):

```python
"""
PC-ALM algorithm.

Composes primitives into a named method. Wraps
computronium.create_pc_alm_mlp factory.

Reference implementation:
    computronium.algorithms.pcalm.reference

Accelerated kernel:
    computronium.algorithms.pcalm.kernel
"""

from computronium.acceleration.registry import register

from .spec import SPEC
from .reference import step as reference_step
from .kernel import step as kernel_step
from .cases import make_case
from .factory import create_pc_alm_mlp

register(SPEC)

__all__ = [
    "SPEC",
    "reference_step",
    "kernel_step",
    "make_case",
    "create_pc_alm_mlp",
]
```

---

## 8.2 Algorithm `spec.py`

Example:

```python
from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.pcalm",
    kind="algorithm",
    name="PC-ALM",
    family="predictive_coding",
    reference_entrypoint="computronium.algorithms.pcalm.reference.step",
    kernel_entrypoint="computronium.algorithms.pcalm.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    uses_primitives=(
        "primitive.state_dynamics.pc_alm_settling",
        "primitive.credit_assignment.pc_alm",
    ),
    summary="Augmented Lagrangian Predictive Coding.",
    equations="""
    ...
    """,
    invariants=(
        "local error signals remain bounded",
        "settling dynamics are deterministic under fixed seed",
        "slow parameters are not mutated during intra-episode steps",
    ),
    notes="Kernel should fuse the primal-dual settle loop where possible.",
    tags=("predictive_coding", "augmented_lagrangian", "local_learning"),
)
```

---

## 8.3 Algorithm `factory.py`

Example (thin wrapper over existing factory):

```python
"""
Public factory for PC-ALM systems.

Wraps computronium.create_pc_alm_mlp, adding backend selection.
"""

from typing import Any

from computronium import create_pc_alm_mlp as _create_pc_alm_mlp
from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get


def create_pc_alm_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
) -> Any:
    """
    Create a PC-ALM MLP system.

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.pcalm")
    backend = select_backend(spec, backend)
    # Pass backend to underlying system composition
    return _create_pc_alm_mlp(
        input_dim, hidden_dims, output_dim, lr=lr, device=device, backend=backend
    )
```

The factory should not hardcode backend selection.

It should allow:

```text
backend="auto"
backend="reference"
backend="kernel"
```

---

# 9. Testing Strategy

Tests should mirror the source structure.

Recommended layout:

```text
tests/
    acceleration/
        test_backends.py
        test_registry.py
        test_parity.py
        test_microbench.py
        test_dispatch.py

    primitives/
        state_dynamics/
            pc_alm_settling/
                test_reference.py
                test_kernel_parity.py
                test_cases.py

        credit_assignment/
            random_projections/
                test_reference.py
                test_kernel_parity.py

    algorithms/
        pcalm/
            test_reference.py
            test_kernel_parity.py
            test_factory.py
            test_cases.py
```

In addition, provide one central parameterized test:

```text
tests/acceleration/test_all_implementations.py
```

Its purpose is to iterate over the registry and verify that each implementation obeys the basic contract.

Example:

```python
import importlib

import pytest

from computronium.acceleration.registry import all_specs


@pytest.mark.parametrize("spec", all_specs())
def test_reference_smoke(spec):
    module = importlib.import_module(spec.reference_entrypoint.rsplit(".", 1)[0])
    case_module = importlib.import_module(
        spec.reference_entrypoint.rsplit(".", 1)[0].rsplit(".", 1)[0] + ".cases"
    )

    case = case_module.make_case()
    output = module.step(case)

    assert output is not None


@pytest.mark.parametrize("spec", all_specs())
def test_kernel_parity(spec):
    if "kernel" not in spec.supported_backends:
        pytest.skip("no kernel backend")

    base = spec.reference_entrypoint.rsplit(".", 2)[0]

    reference_module = importlib.import_module(f"{base}.reference")
    kernel_module = importlib.import_module(f"{base}.kernel")
    case_module = importlib.import_module(f"{base}.cases")

    if not kernel_module.is_available():
        pytest.skip("kernel not available")

    case = case_module.make_case()

    reference_output = reference_module.step(case)
    kernel_output = kernel_module.step(case)

    from computronium.acceleration.parity import assert_parity

    assert_parity(reference_output, kernel_output, spec.parity)
```

This gives you a structural safety net across the entire system.

---

# 10. Property Locks

Parity tests do not replace property locks.

Property locks remain responsible for mathematical and ontological invariants.

Examples:

```text
energy decreases
fixed points are stable
locality constraints hold
feedback matrices are not transposes
pseudo-gradients align with reference gradients
persistent theta is not mutated during intra-episode steps
fast plastic variables update only through plasticity projection
```

For each primitive or algorithm, invariant information should be recorded in the spec:

```python
invariants=(
    "energy decreases",
    "state remains bounded",
)
```

But executable property tests should remain in the test suite.

---

# 11. Microbenchmark Policy

Microbenchmarks are not scientific campaigns.

They exist to answer engineering questions:

```text
Does the kernel run?
Is it dramatically slower or faster than the reference?
Does it allocate excessive memory?
Is it safe to benchmark later?
```

Default microbenchmarks should use tiny shapes:

```text
batch: 2 or 4
sequence: 4 or 8
hidden: 32 or 64
steps: 1 to 5
```

This keeps compute requirements minimal.

Microbenchmark outputs should be JSON.

They may be printed to stdout or written under:

```text
scratch/
```

They should not be treated as CEEC evidence unless explicitly promoted later.

---

# 12. Migration Strategy

The migration should be gradual.

Do not move all files at once.

Use a strangler pattern.

**No backwards compatibility** (AGENTS.md: "Backwards compatibility: NONE"). Old imports are updated in-place; no shims.

---

## 12.1 Phase 0: Create missing acceleration contracts

Existing `backends.py` and `kernel_backend.py` provide ~70% of the acceleration layer. Add only the missing pieces:

```text
computronium/acceleration/spec.py          # ImplementationSpec, ParityTolerance
computronium/acceleration/parity.py        # compare(), assert_parity()
computronium/acceleration/microbench.py    # CLI smoke benchmark runner
computronium/acceleration/matrix.py        # Registry → implementation matrix
```

Adapt existing:
- `KernelRegistry` (kernel_backend.py) → serves as `registry.py` (add `get_spec`, `all_specs` returning ImplementationSpec)
- `AutoDispatcher` + `get_optimal_backend` (backends.py) → serves as `dispatch.py` (add `select_backend(spec, requested)`)

Keep changes small and testable.

Definition of done:

```text
ImplementationSpec can be created
KernelRegistry can register/retrieve specs
parity utility compares tensors
dispatch selects reference/kernel via spec
microbench skeleton runs
matrix utility prints registry table
```

---

## 12.2 Phase 1: Create one primitive exemplar

Create one primitive directory.

Recommended first candidate:

```text
computronium/primitives/state_dynamics/pc_alm_settling/
```

Reason:

```text
PC-ALM is recent, relevant, and already demonstrates kernel value.
```

This does not make PC-ALM the strategic flagship.

It only validates the template.

Definition of done:

```text
primitive package exists
SPEC is registered
reference_step exists
kernel_step exists or safely reports unavailable
make_case exists
parity test passes or skips cleanly
microbench smoke runs
```

---

## 12.3 Phase 2: Create one algorithm exemplar

Create:

```text
computronium/algorithms/pcalm/
```

This algorithm package should compose or wrap the primitive.

Definition of done:

```text
algorithm SPEC is registered
algorithm reference_step exists
algorithm kernel_step exists or delegates to primitive kernels
factory exists or is stubbed
parity test passes or skips cleanly
microbench smoke runs
```

---

## 12.3 Phase 3: Migrate high-value primitives

Wrap existing ontology primitives into the new `primitives/` structure. Each primitive directory wraps an existing class from `ontology/` with the template (`spec.py`, `reference.py`, `kernel.py`, `cases.py`).

Prioritize primitives that are reusable and kernel-heavy.

Suggested order:

```text
1. predictive settling / PC-style dynamics     → PCALMDynamics, PredictiveSettlingDynamics
2. random projection credit assignment         → RandomProjectionsCredit
3. local goodness credit assignment            → LocalGoodnessCredit (FF/LEMMA)
4. Hebbian / STDP trace updates                → TemporalTraceCredit
5. Muon / orthogonal parameter updates         → RiemannianOrthogonalUpdate (Muon)
6. tile routing / tile updates                 → TileGeometry + routing kernels
7. fast-weight plasticity                      → FastWeightPlasticity
8. routing plasticity                          → RoutingPlasticity
```

For each one:

```text
create primitive directory under computronium/primitives/<axis>/<name>/
add __init__.py registering SPEC
add spec.py with ImplementationSpec (id, axis, entrypoints, parity, status)
add reference.py delegating to ontology class
add kernel.py delegating to acceleration kernel (or eager fallback)
add cases.py with make_case() for parity/microbench
add tests under tests/primitives/<axis>/<name>/
register spec in __init__.py
update old acceleration/*_kernels.py imports to point to new primitive
```

---

## 12.4 Phase 4: Migrate named algorithms

After primitives are in place, migrate algorithms:

```text
backprop
fa
ff
pepita
pc
pcalm
eqprop
hebbian
stdp
tile
fast_weight
routing
```

Each algorithm should declare which primitives it uses:

```python
uses_primitives=(
    "primitive.credit_assignment.random_projections",
    "primitive.parameter_update.euclidean",
)
```

This makes the 6-axis composition explicit.

---

# 13. Mapping Existing Code to the New Structure

Use this rule:

```text
If code is backend plumbing, it belongs in acceleration/.
If code is a reusable axis mechanism, it belongs in primitives/.
If code is a named method or recipe, it belongs in algorithms/.
```

Likely mapping (wrappers around existing ontology classes):

```text
acceleration/backends.py
    stays in acceleration/ (add select_backend)

acceleration/kernel_backend.py
    stays in acceleration/ (KernelRegistry → registry; add get_spec/all_specs)

acceleration/triton_kernels.py
    → acceleration/triton_utils.py (generic Triton utilities only)

acceleration/fa_kernels.py
    → primitives/credit_assignment/random_projections/kernel.py
    wraps RandomProjectionsCredit (ontology/credit.py)

acceleration/pc_kernels.py
    → primitives/state_dynamics/predictive_settling/kernel.py
    wraps PredictiveSettlingDynamics (ontology/dynamics/_dynamics.py)
    → primitives/state_dynamics/pc_alm_settling/kernel.py
    wraps PCALMDynamics + pcalm_kernels.py fused kernels

acceleration/hebbian_kernels.py
    → primitives/credit_assignment/temporal_trace/kernel.py
    wraps TemporalTraceCredit (ontology/credit.py)

acceleration/snn_kernels.py
    → primitives/state_dynamics/spike_integration/kernel.py
    wraps SpikeIntegrationDynamics (ontology/dynamics/_dynamics.py)

acceleration/ff_kernels.py
    → primitives/credit_assignment/local_goodness/kernel.py
    wraps LocalGoodnessCredit (ontology/credit.py)

acceleration/tp_kernels.py
    → primitives/credit_assignment/target_inversion/kernel.py
    wraps TargetInversionCredit (ontology/credit.py)

acceleration/tile_kernels.py
    → primitives/geometry/tile_mesh/kernel.py
    wraps TileGeometry (ontology/geometry.py)

acceleration/mep_kernels.py
    → primitives/parameter_update/muon/kernel.py
    wraps RiemannianOrthogonalUpdate (ontology/update.py)
    → primitives/parameter_update/spectral_constrained/kernel.py
    wraps SpectralConstrainedUpdate (ontology/update.py)

acceleration/backprop_kernels.py
    → algorithms/backprop/kernel.py (or reference-only)
    wraps BackpropCredit (ontology/credit.py) + EuclideanUpdate

acceleration/contrastive_kernels.py
    → primitives/credit_assignment/thermodynamic_contrast/kernel.py
    wraps ThermodynamicContrast (ontology/credit.py)

acceleration/pcalm_kernels.py
    → primitives/state_dynamics/pc_alm_settling/kernel.py
    wraps PCALMDynamics + fused_dual_primal_update + _compiled_pcalm_settle

acceleration/eqprop_kernel_backend.py
    → primitives/state_dynamics/energy_minimization/kernel.py
    wraps EnergyMinimizationDynamics (ontology/dynamics/_dynamics.py)

acceleration/compile.py
    → acceleration/triton_utils.py (torch.compile helpers)
```

Do not rush this mapping.

Wrap first, move later. Each primitive directory wraps its ontology class; kernel.py delegates to existing acceleration kernels.

---

# 14. Self-Documentation Requirements

Avoid global documentation.

Instead, require self-documenting source.

Every package should have a module docstring.

Every spec should include:

```python
summary
equations
invariants
notes
tags
```

Every reference module should explain:

```text
what mathematical operation it implements
why it is considered the reference
what assumptions it makes
```

Every kernel module should explain:

```text
what reference implementation it accelerates
what kernel technology it uses
what numerical tolerances it targets
what limitations it has
```

Local `README.md` files are allowed only when the mathematics or migration history needs more space than docstrings reasonably support.

Preferred local README sections:

```text
Purpose
Mathematics
Axes
Reference implementation
Kernel implementation
Parity expectations
Status
Known issues
```

But if a README merely repeats the spec, omit it.

---

# 15. Future Addition Template

The structure must make future additions mechanical.

## 15.1 Adding a new primitive

To add a new primitive:

```text
1. Choose the axis.
2. Create computronium/primitives/<axis>/<primitive_name>/.
3. Add __init__.py.
4. Add spec.py.
5. Add reference.py.
6. Add cases.py.
7. Add tests.
8. Add kernel.py when an accelerated implementation exists.
9. Register the spec.
10. Run parity and microbench smoke tests.
```

The primitive is not considered complete until:

```text
reference exists
case exists
reference smoke test passes
kernel exists or is explicitly absent
parity passes if kernel exists
spec is registered
```

---

## 15.2 Adding a new algorithm

To add a new algorithm:

```text
1. Identify the primitives it uses.
2. Create computronium/algorithms/<algorithm_name>/.
3. Add __init__.py.
4. Add spec.py.
5. Add reference.py.
6. Add cases.py.
7. Add factory.py.
8. Add kernel.py if there is a fused algorithm-specific hot path.
9. Add tests.
10. Register the spec.
11. Run parity and microbench smoke tests.
```

If the algorithm is purely compositional and has no unique fused kernel, `kernel.py` may delegate to primitive kernels.

It should still expose the same contract.

---

# 16. Backend Selection Contract

All implementations should support the same conceptual backend choices:

```text
auto
reference
kernel
```

Meaning:

```text
auto:
    use kernel if available and verified, otherwise use reference

reference:
    force the reference implementation

kernel:
    force the accelerated kernel
```

This contract should eventually be honored by factories, trainers, and benchmarking utilities.

For now, it only needs to exist at the primitive/algorithm seam.

---

# 17. Status Model

Each implementation has a status:

```text
missing
reference_only
kernel_unverified
kernel_verified
microbenched
campaign_ready
deprecated
```

Meaning:

```text
missing:
    planned but not implemented

reference_only:
    reference implementation exists

kernel_unverified:
    kernel exists but parity is not verified

kernel_verified:
    kernel exists and parity tests pass

microbenched:
    kernel parity passes and microbenchmark smoke runs

campaign_ready:
    implementation is stable enough for larger campaigns

deprecated:
    implementation is retained for compatibility but should not be used
```

The status should be updated as tests and benchmarks pass.

Eventually, some of this can be inferred automatically.

Initially, manual status is acceptable.

---

# 18. Relationship to Existing Property Tests

Existing property tests remain important.

The new structure does not replace them.

The relationship is:

```text
property tests:
    verify mathematical and ontological invariants

parity tests:
    verify that accelerated kernels preserve reference behavior

microbenchmarks:
    verify engineering performance smoke tests

campaigns:
    produce scientific evidence
```

The new structure makes all four easier to run.

---

# 19. Relationship to CEEC

CEEC remains separate but benefits from this structure.

Implementation specs can later be linked to CEEC evidence:

```python
evidence_ids=(
    "E-000123",
)
```

Parity reports and microbench outputs can later be promoted into CEEC artifacts if desired.

For now, keep CEEC integration minimal.

The immediate goal is implementation clarity, not evidence harvesting.

---

# 20. Immediate Implementation Plan

This is the concrete sequence to execute.

## Step 1: Create missing acceleration contracts

Create new files:

```text
computronium/acceleration/spec.py
computronium/acceleration/parity.py
computronium/acceleration/microbench.py
computronium/acceleration/matrix.py
```

Adapt existing (add to `kernel_backend.py` and `backends.py`):
- `KernelRegistry.get_spec(id)`, `KernelRegistry.all_specs()` → return `ImplementationSpec`
- `select_backend(spec, requested)` in `backends.py`

Definition of done:

```text
ImplementationSpec can be created
KernelRegistry registers/retrieves specs
parity utility compares tensors
dispatch selects reference/kernel via spec
microbench skeleton runs
matrix utility prints registry table
```

---

## Step 2: Create one primitive exemplar

Create:

```text
computronium/primitives/state_dynamics/pc_alm_settling/
```

Add:

```text
__init__.py (registers SPEC)
spec.py (ImplementationSpec for primitive.state_dynamics.pc_alm_settling)
reference.py (delegates to PCALMDynamics)
kernel.py (delegates to pcalm_kernels._compiled_pcalm_settle / fused_dual_primal_update)
cases.py (make_case for parity/microbench)
```

Definition of done:

```text
SPEC is registered
make_case creates a tiny deterministic case
reference_step runs (wraps PCALMDynamics)
kernel_step runs or skips cleanly (delegates to pcalm_kernels)
```

---

## Step 3: Add primitive tests

Create:

```text
tests/primitives/state_dynamics/pc_alm_settling/
    test_reference.py
    test_kernel_parity.py
    test_cases.py
```

Definition of done:

```bash
uv run pytest tests/primitives/state_dynamics/pc_alm_settling -q
```

passes.

---

## Step 4: Create one algorithm exemplar

Create:

```text
computronium/algorithms/pcalm/
```

Add:

```text
__init__.py (registers SPEC)
spec.py (ImplementationSpec for algorithm.pcalm, uses_primitives declared)
reference.py (wraps PC-ALM system composition)
kernel.py (delegates to primitive kernels)
factory.py (thin wrapper over create_pc_alm_mlp with backend selection)
cases.py (make_case for algorithm-level parity)
```

Definition of done:

```text
SPEC is registered
algorithm step can run a tiny case
factory exists (wraps create_pc_alm_mlp)
kernel step delegates to primitive kernels
```

---

## Step 5: Add algorithm tests

Create:

```text
tests/algorithms/pcalm/
    test_reference.py
    test_kernel_parity.py
    test_factory.py
    test_cases.py
```

Definition of done:

```bash
uv run pytest tests/algorithms/pcalm -q
```

passes.

---

## Step 6: Add central registry test

Create:

```text
tests/acceleration/test_all_implementations.py
```

Definition of done:

```bash
uv run pytest tests/acceleration/test_all_implementations.py -q
```

passes.

---

## Step 7: Update old acceleration imports

For each migrated primitive, update the old `acceleration/*_kernels.py` to import from the new primitive location.

Example:

```python
# computronium/acceleration/pcalm_kernels.py
from computronium.primitives.state_dynamics.pc_alm_settling.kernel import step  # noqa: F401
```

Definition of done:

```text
old imports updated to new locations
existing tests still pass
```

---

## Step 8: Run repository health checks

Run:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright .
uv run pytest tests/acceleration tests/primitives tests/algorithms -q
```

Definition of done:

```text
no new lint errors
no new type errors
new tests pass
old tests remain green or failures are pre-existing and documented
```

---

## Step 9: Run repository health checks

Run:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright .
uv run pytest tests/acceleration tests/primitives tests/algorithms -q
```

Definition of done:

```text
no new lint errors
no new type errors
new tests pass
old tests remain green or failures are pre-existing and documented
```

---

# 21. Definition of Done for the Initial Refactor

The initial refactor is complete when:

```text
acceleration/ contains shared backend utilities only (spec, parity, microbench, matrix, registry, dispatch)
ImplementationSpec exists
registry exists (KernelRegistry extended with get_spec/all_specs)
parity utility exists
microbench utility exists
matrix utility exists
one primitive follows the new structure (wraps ontology class)
one algorithm follows the new structure (wraps factory, composes primitives)
each has reference, kernel, cases, and spec
parity tests pass or skip cleanly
microbench smoke runs
old imports updated to new primitive/algorithm locations
no global documentation is required
the structure clearly templates future additions
```

---

# 22. Future Extension Example

Suppose someone later wants to add a new local-learning algorithm.

The path is obvious:

```text
computronium/algorithms/new_method/
    __init__.py
    spec.py
    reference.py
    kernel.py
    factory.py
    cases.py
```

If it needs a new credit rule:

```text
computronium/primitives/credit_assignment/new_credit_rule/
    __init__.py
    spec.py
    reference.py
    kernel.py
    cases.py
```

If it needs a new settling dynamic:

```text
computronium/primitives/state_dynamics/new_settling_rule/
    __init__.py
    spec.py
    reference.py
    kernel.py
    cases.py
```

The process is the same:

```text
write reference
write case
write tests
write kernel
prove parity
run microbench
register spec
```

That is the desired property.

---

# 23. Principles Embedded in the Structure

This structure enforces the following principles automatically:

## Reference-first

Every primitive and algorithm must have a clear reference implementation.

## Kernel acceleration without semantic drift

Kernel implementations must pass parity tests.

## Self-documentation

Specs carry summaries, equations, invariants, notes, and tags.

## Machine-readable implementation status

The registry knows what exists and what state it is in.

## Lightweight benchmarking

Microbenchmarks are smoke tests, not campaigns.

## Low-compute safety

Default cases are tiny and deterministic.

## Algorithm neutrality

No algorithm is structurally privileged.

## Reuse through primitives

Shared mechanisms live in primitives, not duplicated inside algorithms.

## Gradual migration

Old code can remain available through shims.

## Future automation

The registry, specs, cases, parity, and microbench seams give the AutoScientist clean handles for future exploration.

---

# 24. Final Recommendation

Adopt this structure as the target architecture.

Begin with:

```text
acceleration contracts
one primitive exemplar
one algorithm exemplar
parity tests
microbench smoke
registry matrix
```

Then migrate existing code incrementally.

The result is a codebase where every primitive and algorithm is:

```text
explicit
testable
benchmarkable
acceleratable
self-documenting
machine-discoverable
```

That is the right foundation for implementation dominance without forcing a premature commitment to any single algorithm.
