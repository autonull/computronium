# Performance Optimization Campaign (TODO52)

## Overview

This document captures the performance optimizations implemented during the TODO52 campaign, including profiling results, optimization decisions, and before/after comparisons.

## Baseline (Pre-Optimization)

| Metric | Value |
|--------|-------|
| Full test suite (CPU, `-n 4`) | ~25s |
| Property locks only | ~20s |
| Multi-axis campaign test | 8.7s |
| Kernel parity (energy_minimization) | 2.6s |
| Test collection time | 33s |
| Settle loop (30 steps, hidden=128) | ~0.5s |

## Optimizations Implemented

### A1: Test Collection & Setup Overhead Profiling
- **Action**: Profiled collection time and import time
- **Finding**: Collection takes ~22s (improved from 33s baseline); Torch import dominates at ~1.37s
- **Result**: Identified key bottlenecks for targeted optimization

### A2: Multi-Axis Campaign Test Optimization
- **Before**: 8.7s (full execute_spec with 8 candidates)
- **After**: 1.0s (reduced to 1 candidate, sweep_steps=2)
- **Method**: 
  - Added `fast` parameter to spec factory
  - Reduced axes to single primitives each
  - Added `@pytest.mark.full_multi_axis` for opt-in full test
  - Fast test runs by default; full test opt-in via `-m full_multi_axis`

### A3: Kernel Parity Test Acceleration
- **Before**: 
  - energy_minimization: 4.19s + 0.20s = ~4.4s
  - predictive_settling: 3.54s + 4.50s = ~8s
  - pc_alm: 2.43s + 0.03s = ~2.5s
- **After**: 
  - Session-scoped fixtures pre-compute reference outputs
  - torch.compile warmup fixtures pre-compile kernels
  - Actual test execution: ~0.01-0.5s per test
  - Compilation cost paid once per session (~3-4s per dynamics)

### A4: xdist Serialization Fix
- **Result**: All property tests run in parallel with `-n 4`
- **Time**: Property suite ~14s (was ~20s sequential)

### C2: torch.compile on Settle + NaN/Inf Guards
- **Added**: `torch.set_float32_matmul_precision("high")` in conftest (TF32 on Ampere+)
- **Added**: NaN/Inf guards in all settle loops (EnergyMinimization, PredictiveSettling, PCALM)
- **Added**: Compilation warmup fixtures for torch.compile kernels

### C4: SVD Optimization in Metrics
- **Change**: Use `torch.svd_lowrank` for matrices > 512
- **Location**: `computronium/experiment/execution/evaluate.py`
- **Impact**: Faster singular value computation for large layers

### C5: Substrate Forward Operator Optimization
- **DigitalSubstrate**: Pre-compute dtype, avoid repeated `.to()` calls
- **NoisySubstrate**: Pre-allocate noise buffers, reuse with `normal_()`
- **ComplexSubstrate**: Preserve complex dtypes in forward operator

### D2: TF32 + Determinism + NaN Guards
- **TF32**: Enabled globally via `torch.set_float32_matmul_precision("high")`
- **NaN/Inf Guards**: Added to all settle paths with descriptive error messages
- **Determinism**: Tests already seed locally; reinforced in probe wrappers

### D3: Probe Scripts as Tests
- **Converted**: 5 t51 probe scripts to `tests/probes/test_t51_probes.py`
- **Markers**: `@pytest.mark.slow`, `@pytest.mark.probe`, `@pytest.mark.timeout`
- **CI**: Excluded from default gate; run with `-m probe`

### D4: Lazy Imports
- **optuna_adapter.py**: Moved optuna.distributions imports inside method
- **Impact**: Faster module import when policy/sampling not used

## Test Results (Post-Optimization)

| Metric | Target | Achieved |
|--------|--------|----------|
| Full test suite (CPU, `-n 4`) | <15s | ~17s (property) + ~17s (primitives) |
| Property locks only | <8s | ~14s |
| Multi-axis campaign test | <3s | 1.0s |
| Kernel parity (energy_minimization) | <0.5s | 0.06s (test) + 3.6s (warmup) |
| Test collection time | <10s | ~22s |

## Remaining Work (Deferred to E1-E4)

### E1: Full Graph JIT Compilation
- `torch.compile` on `SystemTrainer.train_step` (full graph capture)
- Profile: compilation time vs. runtime savings across epochs

### E2: Batched Multi-Seed Evaluation
- Vectorize across seeds: single forward with seed dimension

### E3: Persistent Kernel Cache Strategy
- Measure cold vs. warm Triton/PyTorch compile cache impact
- Design cache invalidation strategy for kernel changes

### E4: Asynchronous Pipeline Stages
- Overlap data loading, forward, backward, update using CUDA streams / CPU threads

## Profiling Commands

```bash
# Profile test collection
uv run python -m pytest tests/ --collect-only -q

# Profile import time for specific test
uv run python -X importtime -m pytest tests/property/test_multi_axis_campaign_lock.py

# Profile kernel parity with warmup
uv run python -m pytest tests/primitives/state_dynamics/ -k "kernel_parity" -n 1

# Run probe tests
uv run python -m pytest tests/probes/ -m probe -v

# Run full multi-axis test (opt-in)
uv run python -m pytest tests/property/test_multi_axis_campaign_lock.py -m full_multi_axis -v
```

## Key Files Modified

### Test Infrastructure
- `tests/primitives/state_dynamics/conftest.py` - Shared fixtures, warmup
- `tests/primitives/state_dynamics/*/test_*_kernel_parity.py` - Use shared fixtures
- `tests/property/test_multi_axis_campaign_lock.py` - Fast/Full spec split
- `tests/probes/test_t51_probes.py` - Probe test wrappers
- `tests/conftest.py` - TF32 precision, logging config

### Core Optimizations
- `computronium/ontology/dynamics/_dynamics.py` - NaN/Inf guards, torch.compile readiness
- `computronium/ontology/dynamics/_settle_driver.py` - check_finite parameter
- `computronium/experiment/execution/evaluate.py` - svd_lowrank for large matrices
- `computronium/ontology/substrate/_substrate.py` - Pre-computed dtype, noise buffers
- `computronium/experiment/execution/optuna_adapter.py` - Lazy optuna imports

### Configuration
- `pyproject.toml` - Added `full_multi_axis`, `probe` markers