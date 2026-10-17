
## ⚡ Hardware Acceleration (`computronium/acceleration/`)

| Module | Purpose |
|--------|---------|
| `kernels.py` | Pure NumPy/CuPy reference for correctness |
| `triton_kernels.py` | Triton JIT fused ops for EqProp/MEP |
| `fa_kernels.py` | Fused feedback projection, activation derivative, batched outer product |
| `pc_kernels.py` | Fused prediction, error update, contrastive update (Predictive Coding) |
| `hebbian_kernels.py` | Hebbian/Oja's rule, 3-factor, contrastive Hebbian |
| `snn_kernels.py` | LIF step, STDP, contrastive STDP |
| `ff_kernels.py` | Goodness threshold, contrastive FF/PEPITA updates |
| `tp_kernels.py` | Target propagation inverse + target computation |
| `tile_kernels.py` | Complete TileNet suite: 6 algorithms activity/weight update, routing (top-k/random/learned), multi-GPU NCCL sharding |
| `mep_kernels.py` | Muon orthogonalization, Dion SVD, Fisher whitening, EP settle |
| `backprop_kernels.py` | Fused BPTT baseline |
| `contrastive_kernels.py` | Memory-efficient contrastive primitives (no stored activations; 10 algorithm families) |
| `backends.py` | Auto-dispatch (TRITON > CUDA > CuPy > CPU > NumPy), `AutoDispatcher`, `KernelProfiler` |
| `compile.py` | `torch.compile` integration: custom `EqPropFunction`/`EqPropTritonFunction` autograd, dynamic shapes, compile presets |
| `kernel_backend.py` | `KernelRegistry` with shape-specific auto-tuning cache |

- ⚡ Triton kernels for all tile algorithms + MEP + FA + PC + Hebbian + SNN + FF + TP
- 🔄 Auto-dispatch with profile-guided backend selection
- 🚀 Custom EqProp autograd Function enabling `torch.compile` on settle loops (2–3× speedup)
- 🌐 Multi-GPU tile sharding support for large TileNet models
- ✅ Gradient equivalence CI gate (Triton vs CuPy vs PyTorch on every commit)


## 🚀 Shared Acceleration Layer (`computronium/acceleration/` — Registry & Dispatch)

The acceleration layer now provides a **unified registry** of **64 implementations** (43 primitives + 21 algorithms) across all 6 ontology axes, with a common `ImplementationSpec` metadata structure enabling automated tooling.

### Registry Structure

| Axis | Primitives | Algorithms | Total |
|------|-----------|-----------|-------|
| **Substrate** | 9 | — | 9 |
| **Geometry** | 7 | — | 7 |
| **StateDynamics** | 8 | — | 8 |
| **Plasticity** | 7 | — | 7 |
| **CreditAssignment** | 6 | — | 6 |
| **ParameterUpdate** | 6 | — | 6 |
| **Algorithms** | — | 21 | 21 |
| **Total** | **43** | **21** | **64** |

Each `ImplementationSpec` carries:
- **Identity**: `id`, `name`, `axis`, `kind` (primitive/algorithm)
- **Mathematics**: `summary`, `equations`, `invariants`, `notes`, `evidence_ids`, `tags`
- **Kernel**: `supported_backends`, `kernel_technology` (compile/triton), `status` (reference_only/kernel_unverified/kernel_verified), `parity` tolerance
- **Entrypoints**: `reference_entrypoint`, `kernel_entrypoint`, `cases_entrypoint`

### Auto-Dispatch & Status Ladder

```python
from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get

spec = get("primitive.state_dynamics.energy_minimization")
backend = select_backend(
    spec, "auto"
)  # Returns "kernel" if status=kernel_verified, else "reference"
```

**Status ladder** (each rung requires evidence before promotion):
1. `reference_only` — Pure Python/NumPy/CuPy reference implementation
2. `kernel_unverified` — Kernel exists (`kernel.py`), parity not yet validated
3. `kernel_verified` — Parity passes (max_abs_diff < tolerance), microbench evidence recorded, `dispatch.select_backend(spec, "auto")` routes to kernel

**Current status**: 25 specs `kernel_verified` (11 primitives + 14 algorithms), up from 1 at TODO32 start. The kernel ladder promotes through `reference → torch.compile → Triton` (credit primitives skip compile rung due to autograd incompatibility).

### Registry API

```python
from computronium.acceleration.registry import (
    all_specs,
    algorithms,
    primitives,
    get,
    list_by_axis,
)

all_specs()  # → tuple[ImplementationSpec, ...] (all 64)
algorithms()  # → 21 algorithm specs
primitives()  # → 43 primitive specs
get("primitive.credit_assignment.random_projections")
list_by_axis()  # → {axis: [spec_ids]} dict for CLI/docs filtering
```
