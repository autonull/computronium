---

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

---

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

---

## 🛠️ Kernel Development Workflow

Tooling to promote kernels through the ladder with parity + microbench evidence at each rung.

### `scaffold_kernel.py` — Generate Kernel Stubs

```bash
# Torch.compile rung (default first rung for StateDynamics primitives)
uv run python scripts/scaffold_kernel.py \
    --primitive primitive.state_dynamics.energy_minimization \
    --technology compile

# Triton rung (for credit primitives, or where compile insufficient)
uv run python scripts/scaffold_kernel.py \
    --primitive primitive.credit_assignment.random_projections \
    --technology triton
```

Generates `kernel.py` with:
- `is_available()` — runtime capability check
- `step(case)` — kernel entrypoint delegating to reference when unavailable
- Parity tolerance pulled from spec's `ParityTolerance`

### `kernel_dev.py` — Watch & Re-test

```bash
# Watch mode: re-runs parity on file change (polling, no deps)
uv run python scripts/kernel_dev.py \
    --primitive primitive.credit_assignment.random_projections \
    --watch

# Single run
uv run python scripts/kernel_dev.py \
    --primitive primitive.credit_assignment.random_projections \
    --once
```

### `validate_composition.py` — Algorithm Dependency Audit

```bash
# Validate all 21 algorithm specs
uv run python scripts/validate_composition.py --all-algorithms

# Validate single algorithm
uv run python scripts/validate_composition.py --algorithm algorithm.backprop
```

Static check: each algorithm's `uses_primitives ⊆ actually-imported primitives`. Wired into CI (`.github/workflows/ci.yml`).

---

## 📚 Documentation & Bench Tools from Specs

### `generate_docs.py` — Render Spec Metadata

```bash
# Generate all docs + implementation matrix
uv run python scripts/generate_docs.py --all --output docs/generated/

# Single implementation
uv run python scripts/generate_docs.py --id primitive.state_dynamics.energy_minimization
```

Outputs:
- `docs/generated/primitives/<axis>/<name>.md` — Purpose, Mathematics (equations), Invariants, Reference, Kernel, Parity tolerance, Status, Tags
- `docs/generated/algorithms/<name>.md`
- `docs/generated/IMPLEMENTATION_MATRIX.md` — from `matrix.py --format github-markdown`

### `generate_property_tests.py` — Hypothesis Tests from Invariants

```bash
uv run python scripts/generate_property_tests.py --all --output tests/property/generated/
```

Generates 73 tests for 48 specs (excludes geometry/substrate with different interfaces):
- **Deterministic seed**: same seed → bitwise-equal outputs
- **Finite state**: no NaN/Inf in outputs (covers `state remains finite`, `activations remain finite`, `parameters remain finite`, etc.)

### `bench_dashboard.py` — Latency/Memory vs Commit

```bash
# Generate dashboard plots from microbench JSONL artifacts
uv run python scripts/bench_dashboard.py --input artifacts/benchmarks/ --png artifacts/bench_dashboard.png

# Text summary only
uv run python scripts/bench_dashboard.py --input artifacts/benchmarks/ --summary-only

# Filter to specific spec
uv run python scripts/bench_dashboard.py --input artifacts/benchmarks/ --spec primitive.state_dynamics.energy_minimization
```

Plots median/p95 latency and peak memory across git commits from microbench JSONL (which embeds git SHA via `--tag`).

---

## 🧪 Enhanced CLI Tools

### `microbench.py` — Microbenchmark Runner

```bash
# Single implementation with full options
uv run python -m computronium.acceleration.microbench \
    --id primitive.state_dynamics.energy_minimization \
    --backend kernel \
    --device cuda \
    --steps 10 \
    --dtype float32 \
    --seed 42 \
    --warmup 3 \
    --iterations 10 \
    --format jsonl \
    --output artifacts/benchmarks/energy_minimization.jsonl \
    --tag $(git rev-parse HEAD)

# All implementations (CI-friendly)
uv run python -m computronium.acceleration.microbench --all --format csv --output bench.csv
```

**New flags**:
- `--iterations` / `--warmup` — statistical measurement
- `--output bench.jsonl` — resumable JSONL artifact (one line per iteration)
- `--format csv` — summary CSV (median, p95, throughput, peak_mem_mb)
- `--tag` — git SHA stamped into each row for regression tracking
- Peak memory capture: `torch.cuda.max_memory_allocated` / CPU RSS delta

### `matrix.py` — Implementation Matrix

```bash
# GitHub-flavored markdown (renders in PR comments)
uv run python -m computronium.acceleration.matrix --format github-markdown

# Composable filters for CI subsets
uv run python -m computronium.acceleration.matrix \
    --filter axis=state_dynamics,kind=primitive,status=kernel_unverified \
    --format json
```

---

## 🧪 Registry Integrity Locks (Extended Verification Framework)

These locks protect the 64-spec registry from silent drift — extending TODO32's `test_dynamics_wiring_lock.py` doctrine.

| Lock | File | Purpose |
|------|------|---------|
| **Completeness** | `tests/property/test_registry_completeness_lock.py` | Every ontology class ↔ exactly one primitive spec; every spec resolves to live class (13 tests) |
| **Scaffolder round-trip** | Template rendering verified | `scaffold_primitive.py`/`scaffold_algorithm.py` output passes own tests |
| **Structural equivalence** | Geometry/Substrate primitives | Factory determinism: same config → bitwise-equal state tensors; spec round-trip |
| **Promotion rule** | `tests/property/test_kernel_verified_promotion_rule.py` | `kernel_verified` requires: (a) parity on CPU+GPU, (b) microbench JSONL evidence, (c) dispatch `auto` routes to kernel (25 tests) |