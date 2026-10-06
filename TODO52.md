# TODO52: Performance Profiling & Optimization Campaign

## Context

TODO51 delivered P0 (Ruff/Pyright clean) and verified P1 smoke tests. Test suite baseline established:
- **Property locks**: 96 tests, ~20s (multi-axis campaign: 8.7s, stability/energy: 4.5s)
- **Primitives**: 419 tests, 12.6s (kernel parity: 2.6s each for energy_minimization, predictive_settling, pc_alm)
- **Algorithms**: 258 tests, 9.7s (all <0.1s each)
- **Acceleration**: 372 tests, 28.5s (defect audit: 4.6s setup; kernel parity: up to 2.6s)
- **Total fast suite**: ~71s sequential, ~25s with `-n 4`

GPU tests: 81 skipped in acceleration (require CUDA). Local GPU available for profiling.

## Goals

1. **Profile test hotspots** — identify slowest tests and their root causes
2. **Low-hanging fruit optimizations** — minimal complexity, maximal speedup
3. **GPU-local acceleration** — verify kernels run on CUDA, measure speedup
4. **System-level performance** — optimize hot paths in ontology/experiment pipelines
5. **Concurrent enhancements** — fix pre-existing issues, improve DX, harden correctness

---

## Part A — Test Profiling & Quick Wins (Week 1)

### A1. Profile Test Collection & Setup Overhead
**Problem**: `test_defect_class_audit.py` has 4.6s setup (census import). `test_multi_axis_campaign` 8.7s (full pipeline). Collection takes 33s.
**Actions**:
```bash
# Profile collection time
uv run python -m pytest tests/ --collect-only -q 2>&1 | tail -5
# Profile import time
uv run python -X importtime -m pytest tests/property/test_multi_axis_campaign_lock.py 2>&1 | head -50
# Profile test runtime with pytest-profiling
uv run pip install pytest-profiling && uv run pytest tests/property/test_multi_axis_campaign_lock.py --profile
```
**Targets**: Collection 33s → <10s; multi-axis setup 8.7s → <3s.

### A2. Optimize Slowest Property Tests
| Test | Current | Target | Approach |
|------|---------|--------|----------|
| `test_multi_axis_campaign_run_completes_and_closes` | 8.7s | <3s | Reduce cells/epochs; mock backend; fixture reuse |
| `test_stability_metrics_cover_dynamics_family` (8×) | 0.2-0.5s | <0.1s | Shared settle; reuse Jacobian; reduce hidden_dim |
| `test_defect_class_audit.py::test_the_twin_census_is_a_fixed_list` | 4.6s setup | <1s | Move census to module-level fixture (session scope) |

### A3. Accelerate Kernel Parity Tests (Local)
**Problem**: 15+ kernel parity tests at 0.5-2.6s each (energy_minimization 2.6s, predictive_settling 2.5s, pc_alm 1.4s).
**Root cause**: Full settle + Triton kernel + autograd comparison per test.
**Fixes**:
- **Shared fixtures**: Create session-scoped `settled_state` fixture per dynamics type (reuse across parity tests)
- **Reduced dimensions**: Test parity at hidden_dim=32 (not 128) for fast suite; full dim opt-in via `--full-parity`
- **Batch comparisons**: Compare multiple kernels in single test invocation
- **Triton cache**: Set `TRITON_CACHE_DIR` locally; verify warm vs cold runs

### A4. Parallelize Slow Test Files (Local xdist)
Current: `-n 4` in addopts but some files run sequentially due to fixtures.
**Action**: Audit `pytest-xdist` compatibility; mark truly serial tests with `@pytest.mark.serial`; enable `-n auto` locally; target 25s → <15s for full fast suite.

---

## Part B — GPU-Local Acceleration & Verification (Week 1-2)

### B1. Local GPU Verification (No CI)
**Current**: 81 tests skipped (`@pytest.mark.gpu_only` / `gpu`).
**Action**: If local CUDA available:
```bash
uv pip install cupy-cuda12x triton[torch]
uv run pytest tests/acceleration/ -m "gpu" -q --tb=short
```
**Target**: Run GPU parity tests locally; verify numerical parity (cosine ≥ 0.999) vs CPU; measure speedup.

### B2. Triton Kernel Warmup Fixture (Reusable)
**Problem**: First Triton run includes JIT compilation (~2-5s).
**Fix** (in `tests/conftest.py`):
```python
@pytest.fixture(scope="session", autouse=True)
def triton_warmup():
    if torch.cuda.is_available():
        from computronium.acceleration import get_available_kernels
        for k in get_available_kernels():
            k.warmup()  # Run dummy forward/backward
```
**Also**: Add CPU warmup for Triton CPU fallback kernels.

### B3. GPU Memory Profiling (Local)
Use `torch.cuda.memory_allocated()`, `torch.cuda.max_memory_allocated()` in tests:
```python
def test_gpu_memory_profile():
    peak = torch.cuda.max_memory_allocated() / 1e9  # GB
    assert peak < 2.0  # Sanity threshold
```

---

## Part C — System-Level Performance Hot Paths (Week 2)

### C1. Profile Core Pipeline Hot Paths
```bash
# Profile training step (CPU)
uv run python -m cProfile -o train.prof -m computronium.experiment.surface.cli stability-plasticity --dry-run --max-cells 1
uv run snakeviz train.prof

# Profile with PyTorch profiler
uv run python -c "
import torch.profiler as profiler
with profiler.profile(activities=[profiler.ProfilerActivity.CPU], record_shapes=True) as p:
    run_training_step()
print(p.key_averages().table(sort_by='cpu_time_total', row_limit=20))
"
```

**Expected hot spots**:
1. `StateDynamics.settle()` — Jacobian computation, autograd graph
2. `CreditAssignment.compute_pseudo_gradient()` — backward passes
3. `ParameterUpdate.step()` — optimizer step + momentum
4. `Substrate.forward_operator()` — matmul + noise injection
5. `SearchSpace.iter_candidates()` — coordinate generation

### C2. Optimize Settle Loop (Highest Impact)
**Current**: 30 steps × autograd Jacobian per step = 30 backward passes.
**Optimizations** (in order of ROI):
| Technique | Est. Speedup | Complexity | File |
|-----------|--------------|------------|------|
| `torch.compile(mode="reduce-overhead")` on settle | 2-3× | Low (decorator) | `_dynamics.py` |
| Cache Jacobian from settle for metrics | 2× | Low | `evaluate.py` |
| Gradient checkpointing every N steps | 1.5× | Low (config) | `_dynamics.py` |
| Batched multi-seed settle | 3× | Medium | `_dynamics.py` |

**Immediate**: Add `torch.compile` to `EnergyMinimizationDynamics.settle` and `PredictiveSettlingDynamics.settle` behind config flag.

### C3. Optimize Search Space Iteration
**Current**: `iter_candidates` generates all coordinates upfront (cartesian product).
**Fixes** in `computronium/experiment/execution/search_space.py`:
- Lazy generator with early filtering (yield valid coords only)
- Cache axis validity per spec (memoize `_filter_axes_for_validity`)
- Prune impossible combinations before Cartesian product

### C4. Optimize Energy/Metrics Computation
**Current**: Per-layer energy + full Jacobian SVD per evaluation.
**Fixes** in `computronium/experiment/execution/evaluate.py`:
- Cache Jacobian from settle (already computed for stability) → reuse for SVD
- Use `torch.linalg.svdvals` (faster than full SVD when only singular values needed)
- Randomized SVD for large layers (>512): `torch.svd_lowrank`

### C5. Optimize Substrate Forward Operators
**Current**: Each substrate re-validates shapes, computes energy separately.
**Fixes** in `computronium/ontology/substrate/_substrate.py`:
- Move shape validation to `__init__` or factory (once per layer, not per forward)
- Fused energy estimation: compute MACs + energy in single pass
- Pre-allocate noise buffers for stochastic substrates

---

## Part D — Concurrent Enhancements (Same Time, High Value)

### D1. Fix Pre-existing Test Failures (Blockers for Green Suite)
| Failure | Location | Fix |
|---------|----------|-----|
| 6 sampler failures | `test_sampler_lock.py` | Update `step_size`→`settle_step`, `icu_guided`→`tpe`, RunSpec validation |
| 344 pyright errors | `computronium/core/` legacy | Deferred, but fix `continual/`, `tile/`, `substrates/` incrementally |

### D2. Harden Numerical Correctness
- **Add `torch.set_float32_matmul_precision('high')`** in conftest for TensorFloat-32 on Ampere+
- **Verify determinism**: Run each property test 3× with different seeds, assert bitwise equality
- **NaN/Inf guards**: Add `torch.isfinite()` checks in settle loop, credit assignment, update step

### D3. Improve Developer Experience
- **Faster test iteration**: Add `--lf` (last failed) and `--ff` (failed first) support; fix pytest cache corruption
- **Better test output**: Custom pytest plugin for structured JSON output (for profiling/analysis)
- **Probe scripts as tests**: Convert `scripts/probes/t51_*.py` to `tests/probes/` with pytest markers for CI inclusion

### D4. Optimize Data Structures & Memory
- **Frozen dataclasses**: Ensure all config objects use `frozen=True, slots=True` (already mostly done)
- **Tensor reuse**: In settle loop, reuse activation buffers instead of allocating per step
- **Lazy imports**: Move heavy imports (triton, cupy, optuna) inside functions, not module level

### D5. Documentation & Knowledge Capture
- **Performance notes**: Add `docs/performance/` with profiling outputs, optimization decisions
- **Benchmark scripts**: Create `scripts/benchmarks/` for reproducible microbenchmarks
- **Architecture decision records**: Document why certain optimizations were chosen/rejected

---

## Part E — Larger Optimizations (Investigate, Deferred)

### E1. Full Graph JIT Compilation
- `torch.compile` on `SystemTrainer.train_step` (full graph capture)
- Profile: compilation time vs. runtime savings across epochs

### E2. Batched Multi-Seed Evaluation
Vectorize across seeds: single forward with seed dimension instead of sequential runs.

### E3. Persistent Kernel Cache Strategy
- Measure cold vs. warm Triton/PyTorch compile cache impact locally
- Design cache invalidation strategy for kernel changes

### E4. Asynchronous Pipeline Stages
Overlap data loading, forward, backward, update using CUDA streams / CPU threads.

---

## Success Criteria (Measurable, Local)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Full test suite (CPU, `-n 4`) | ~25s | <15s | `uv run pytest tests/property/ tests/primitives/ tests/algorithms/ tests/acceleration/ -n 4` |
| Property locks only | ~20s | <8s | `uv run pytest tests/property/ -n 4` |
| Multi-axis campaign test | 8.7s | <3s | Single test duration |
| Kernel parity (energy_minimization) | 2.6s | <0.5s | Per-test duration |
| Test collection time | 33s | <10s | `uv run pytest --collect-only` |
| Settle loop (30 steps, hidden=128) | ~0.5s | <0.2s | Microbenchmark |
| GPU kernel parity (if CUDA) | N/A | <0.3s | Local run |

---

## Execution Order

```
Week 1 (Test & Kernel Focus):
  □ A1: Profile collection & setup (1h)
  □ A2: Optimize slowest property tests (2h)
  □ A3: Accelerate kernel parity tests — shared fixtures, reduced dims (3h)
  □ A4: Fix xdist serialization, enable -n auto locally (1h)
  □ B1: Local GPU verification (if CUDA) (1h)
  □ B2: Triton warmup fixture (1h)
  □ B3: GPU memory profiling (1h)

Week 2 (System Hot Paths):
  □ C1: Profile core pipeline with cProfile/PyTorch profiler (2h)
  □ C2: torch.compile on settle kernels + Jacobian caching (3h)
  □ C3: Lazy search space iteration (1h)
  □ C4: SVD optimization in metrics (1h)
  □ C5: Substrate forward operator optimization (2h)

Concurrent (D1-D5) — sprinkle throughout:
  □ D1: Fix 6 sampler failures
  □ D2: TF32 + determinism + NaN guards
  □ D3: Faster test iteration, probe-as-tests
  □ D4: Tensor reuse, lazy imports
  □ D5: Performance docs + benchmark scripts

Ongoing (E1-E4) — investigate when time permits
```

---

## Notes

- **No new runtime dependencies** — profiling tools (`pytest-profiling`, `snakeviz`, `pytest-benchmark`) dev-only
- **Preserve correctness** — all optimizations must pass existing property locks
- **GPU optional** — if no local CUDA, skip B1-B3; CPU optimizations still deliver 2-3×
- **Document findings** — `docs/performance/` with profiling outputs, before/after comparisons
- **TODO51 pre-existing issues**: 6 sampler failures, 344 pyright in core/ — D1 addresses sampler; pyright incremental

---

## References

- `scripts/probes/t51_*` — probe patterns for measurement
- `tests/property/test_stability_energy_metrics_lock.py` — settle profiling pattern
- `computronium/acceleration/` — Triton kernel registry
- `computronium/experiment/execution/pipeline.py` — round loop hot path
- `computronium/ontology/dynamics/_dynamics.py` — settle implementations
- `computronium/ontology/substrate/_substrate.py` — substrate forward operators
- `computronium/experiment/execution/evaluate.py` — metrics computation