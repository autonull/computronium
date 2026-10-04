# TODO50: Remaining Work & High-Value Opportunities

## Context
TODO49 completed Phases 1-5: end-to-end pipeline works across all 604,800 declared combinations with proper constraint enforcement at S4 (gate) and S5 (compose). quick-verify and production-map profiles validated.

---

## Critical Infrastructure Gaps (Must Fix First)

### 0. Protobuf Version Conflict (Blocks P2P) ✅ COMPLETED
**Error**: `gencode 7.35.1 runtime 6.33.6` — generated protobuf code incompatible with runtime.
**Location**: `computronium/p2p/proto/tile_mesh_pb2.py`
**Fix Applied**: Regenerated protobuf with `python -m grpc_tools.protoc` using current protoc (36.1 / protobuf 7.36.x)
**Status**: P2P tests (`test_dht.py`, `test_grpc_seam.py`) now collect and pass.

### 0b. Missing Triton Kernels (2 algorithms) ✅ DFA COMPLETED, TP PARTIAL
| Algorithm | File | Status |
|-----------|------|--------|
| DFA (Direct Feedback Alignment) | `computronium/algorithms/dfa/kernel.py` | ✅ **IMPLEMENTED** - Parity tests pass |
| TP (Target Propagation) | `computronium/algorithms/tp/kernel.py` | 🟡 **PARTIAL** - Kernel runs but needs settling loop for full parity |

**Details**:
- **DFA**: Created `computronium/acceleration/dfa_kernels.py` with `DFAKernelBackend` + Triton kernels (`dfa_feedback_projection_triton`, `dfa_batched_outer_triton`). Updated `computronium/algorithms/dfa/kernel.py` to use the backend with proper RNG state matching. Parity tests pass with `max_abs_diff=1e-4`, `max_rel_diff=1e-3`, `min_cosine=0.999`.
- **TP**: Created Triton kernels in `computronium/acceleration/tp_kernels.py` (`tp_transpose_feedback_triton`, `tp_batched_outer_triton`). Fixed `TPKernelBackend.train_step` bug. Kernel runs but returns simplified metrics (loss, accuracy) vs pipeline's full metrics (loss, energy, nudged_fit_accuracy, free_loss, free_energy, free_accuracy). Needs PredictiveSettlingDynamics settling loop implementation for full parity.

**Impact**: DFA rung now uses Triton acceleration; TP falls back to reference for full pipeline parity.

---

## Remaining Work (from TODO49)

### 1. Full-Budget Profile Validation
| Profile | Current Status | Needed |
|---------|----------------|--------|
| **maturation** | Runs S4-S10, untested at scale | Run with `budget_seconds=7200`, `n_seeds=5`, `epochs=10`, `fidelity=L2` |
| **claim** | Runs S8-S11 only, needs front cells | Run with `budget_seconds=None`, `n_seeds=10`, `epochs=20`, `fidelity=L2` |

**Action**: 
```bash
# Maturation (2hr)
comp run maturation --store mat.duckdb --overrides '{"budget_seconds": 7200}'

# Claim (needs front cells from production-map first)
comp run production-map --store pm.duckdb --overrides '{"budget_seconds": 3600}'
comp run claim --store pm.duckdb
```

### 2. Reproducibility Investigation
**Problem**: Some cells fail replay validation even with `torch.manual_seed()`. Observed variance: val_acc 0.66 vs 0.51.

**Suspected causes**:
- DataLoader worker non-determinism (multi-worker)
- CUDA non-determinism (even on CPU via cuDNN)
- Training dynamics sensitivity (chaotic regimes)

**Experiments**:
```python
# Test 1: Single-worker DataLoader
# Test 2: torch.use_deterministic_algorithms(True)
# Test 3: CUDA_LAUNCH_BLOCKING=1
# Test 4: Fixed batch ordering via manual seed per epoch
```

**Decision point**: If variance > 0.5 persists, either increase tolerance further or accept Level 4 (sampled numerical) claims only.

### 3. `expr_from_string` → AST Builders (Technical Debt)
**Location**: `computronium/experiment/schema/seed_registries.py`
**Scope**: ~15 non-void constraints (HARD, OPERATING_POINT, FAIRNESS kinds)
**Benefit**: Machine-checkable evaluation, removes string-parsing fragility

---

## High-Value Opportunities

### A. Multi-Objective Pareto Campaigns (Core Value Prop)
**Why**: The framework's differentiator is axis-aligned multi-objective optimization.
**Current**: quick-verify uses 2 objectives (val_acc, walltime). production-map uses 3.
**Opportunity**: Run campaigns with full objective sets per axis:
- Substrate: energy, latency, precision
- Geometry: param_count, FLOPs, memory
- Dynamics: settling_time, spectral_radius
- Credit: alignment, local_complexity
- Update: stability, orthogonality

**Deliverable**: `comp run pareto-campaign --objectives axis_aligned`

### B. Stability-Plasticity Frontier Mapping
**Hypothesis**: `adaptive computation ↔ controlled departure from contraction`
**Metrics to sweep**:
- Spectral radius ρ(J_F) via `spectral_radius_from_jacobian`
- Transient amplification σ_max(J_F) via `dominant_singular_value`
- Lyapunov exponents via QR
- Basin stability via sampling

**Campaign**: 648 cells × contraction {0.5, 0.9, 1.05} × gate {selective, ungated} × coupling × precision × noise × delay
**Status**: Probe-scale done (TODO49 §502-503). Needs full campaign.

### C. Frozen-θ ψ Benchmarks (P-Axis Validation)
**Probes complete** (TODO49 §475-477):
- Kolmogorov compression: 2.66× ratio
- NCA fabric reconfiguration: K patterns, θ SHA-invariant
- NTM tape composition: O(1) depth
- σ_max(J_F) frontier measured

**Next**: Scale to L1/L2 with 3+ seeds, publish as validated claim (Level 4).

### D. I(C,U) Predictive Model Refinement
**Current**: 0.944 held-out lattice accuracy (TODO49 §273)
**Opportunity**: 
- Add substrate dimension (currently C×U only)
- Predict ψ modulation effect (measured avg 2.0pp, max 9.1pp)
- Use for policy warm-start (surrogate-driven acquisition)

### E. Hardware-Aware Campaigns
**Substrate models ready**: Memristive (IR-drop), Neuromorphic (spikes), Photonic (phase), Quantum (unitaries)
**Missing**: 
- Energy estimation per substrate (simulated energy only)
- Hardware-measured validation (future work)
- Co-design: optimize geometry+dynamics per substrate

### F. Distributed / P2P Validation ✅ UNBLOCKED
**Implemented**: gRPC/Kademlia, DDP/FSDP/DeepSpeed, ONNX/TorchScript/INT8 export
**Status**: Protobuf conflict resolved; P2P tests pass
**Untested at scale**: Multi-node campaigns, fault tolerance, P2P gossip cluster

---

## Quick Wins (Low Effort, High Signal)

| Task | Effort | Command/Location | Status |
|------|--------|------------------|--------|
| Fix protobuf version conflict | 30min | Regenerate proto | ✅ Done |
| Implement Triton DFA kernel | 2-4hr | `computronium/algorithms/dfa/kernel.py` | ✅ Done |
| Implement Triton TP kernel | 2-4hr | `computronium/algorithms/tp/kernel.py` | 🟡 Partial |
| Add tqdm progress bar to pipeline | 1hr | `computronium/experiment/execution/pipeline.py` | ⏳ Pending |
| Single-worker DataLoader for determinism | 30min | `computronium/domains/registry.py` task loaders | ⏳ Pending |
| `torch.use_deterministic_algorithms()` flag | 15min | `RunSpec` or `SystemTrainerConfig` | ⏳ Pending |
| Export gallery figures from last run | 30min | `comp report --store X --format json` → `scripts/fidelity_gate_report.py` | ⏳ Pending |
| Add `--axis-coverage` CLI flag to report | 1hr | `computronium/experiment/surface/report.py` | ⏳ Pending |

---

## Suggested Execution Order

1. **Day 1**: ✅ Fix protobuf conflict + implement missing Triton kernels (DFA done, TP partial)
2. **Week 1**: Reproducibility fix + maturation/claim profile runs
3. **Week 2**: Multi-objective Pareto campaign design + first runs
4. **Week 3**: Stability-plasticity campaign (uses existing probe infrastructure)
5. **Week 4**: Frozen-θ ψ benchmark scaling + I(C,U) model refinement
5. **Ongoing**: Hardware-aware campaigns as substrate models mature

---

## Acceptance Criteria for TODO50

- [x] Protobuf version conflict resolved; P2P tests collect and pass
- [x] Triton DFA kernel implemented (parity with reference)
- [ ] Triton TP kernel implemented (parity with reference) - needs settling loop
- [ ] maturation profile completes with ≥50 L2 cells
- [ ] claim profile produces claim-grade evidence (N≥10 seeds)
- [ ] Replay variance < 0.25 tolerance OR documented as Level 4 limitation
- [ ] At least one multi-objective Pareto campaign published
- [ ] Stability-plasticity frontier mapped at campaign scale
- [ ] Frozen-θ ψ benchmarks at L2 with 3+ seeds
- [ ] Progress indicator in pipeline output

---

## Notes for Next Session

### TP Kernel Completion
To complete TP kernel parity:
1. Implement PredictiveSettlingDynamics settling loop in `TPKernelBackend.train_step`
2. Match pipeline output format: loss, energy, nudged_fit_accuracy, free_loss, free_energy, free_accuracy
3. The settling loop runs `max_steps` iterations with beta nudge, converging the state
4. Reference uses `settle_steps=10`, `beta=0.1` from PredictiveSettlingDynamics config

### Key Files Modified
- `computronium/acceleration/dfa_kernels.py` - New DFA kernel backend with Triton
- `computronium/algorithms/dfa/kernel.py` - Updated to use DFA backend with RNG matching
- `computronium/acceleration/tp_kernels.py` - Added Triton kernels, fixed train_step
- `computronium/algorithms/tp/kernel.py` - Updated to use TP backend with RNG matching
- `computronium/p2p/proto/tile_mesh_pb2.py` - Regenerated protobuf
- `computronium/p2p/proto/tile_mesh_pb2_grpc.py` - Regenerated protobuf

### Test Commands
```bash
# DFA parity (passing)
uv run python -m pytest tests/algorithms/dfa/test_dfa_kernel_parity.py -v

# TP parity (failing - needs settling loop)
uv run python -m pytest tests/algorithms/tp/test_tp_kernel_parity.py -v

# P2P tests (passing)
uv run python -m pytest tests/integration/test_grpc_seam.py tests/integration/test_dht.py -v -m slow
```