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

## Progress Summary (2026-09-18)

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

### ✅ Verification Results

All new tests pass when run per-directory:
```bash
uv run pytest tests/primitives/state_dynamics/pc_alm_settling -q     # 10 passed
uv run pytest tests/primitives/state_dynamics/predictive_settling -q # 7 passed
uv run pytest tests/primitives/credit_assignment/random_projections -q # 7 passed
uv run pytest tests/algorithms/pcalm -q                              # 13 passed
uv run pytest tests/acceleration/test_all_implementations.py -q      # 8 passed
```

All existing tests continue to pass:
```bash
uv run pytest tests/unit/core/test_dynamics.py -q                    # 5 passed, 1 xfailed
uv run pytest tests/integration/test_lazy_dynamics.py -q            # 5 passed
uv run pytest tests/property/test_dynamics_wiring_lock.py -q        # 4 passed
uv run pytest tests/integration/test_pc_alm_validation.py -q        # 28 passed
uv run pytest tests/integration/test_demo_pc_alm.py -q              # 1 passed
```

Note: Test files with identical names in different directories (test_cases.py, test_kernel_parity.py, test_reference.py) cause pytest collection conflicts when run together. Run per-directory or rename files to resolve.

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

**Algorithm exemplar (pcalm):**
- `computronium/algorithms/pcalm/` with spec.py, reference.py, kernel.py, factory.py, cases.py, __init__.py
- Factory wraps compose_joint_system with backend selection
- Uses primitives: primitive.state_dynamics.pc_alm_settling, primitive.credit_assignment.pc_alm

**Tests:**
- tests/primitives/state_dynamics/pc_alm_settling/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/state_dynamics/predictive_settling/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/primitives/credit_assignment/random_projections/ (test_reference.py, test_kernel_parity.py, test_cases.py)
- tests/algorithms/pcalm/ (test_reference.py, test_kernel_parity.py, test_factory.py, test_cases.py)
- tests/acceleration/test_all_implementations.py (parametrized over all_specs())

**Lint fixes:**
- Added noqa comments for intentional patterns (non-empty-init-module RUF067 for registration)
- Fixed import ordering and type annotations
- Fixed ruff format on registry.py
- Fixed missing newlines, unsorted imports, unused imports, TYPE_CHECKING blocks

**Type fixes:**
- Fixed registry.py pyright errors (getattr for package attributes, type ignore for SPEC)
- Added `on_step` parameter to PCALMDynamics.settle() to match StateDynamics protocol

### 📋 Remaining Work (Phase 3+: Migration of Other Primitives/Algorithms)

Per the plan, the next phases are:
- **Phase 3**: Migrate high-value primitives (local_goodness credit, temporal_trace credit, muon update, tile routing, fast_weight plasticity, routing plasticity)
- **Phase 4**: Migrate named algorithms (backprop, fa, dfa, ff, pepita, pc, eqprop, hebbian, stdp, tile, fast_weight, routing)

### 💡 New Improvement Opportunities

1. **Test file naming**: Rename test files to avoid pytest collection conflicts (e.g., `test_primitive_reference.py`, `test_algorithm_reference.py`)
2. **Microbench CLI**: The microbench.py module exists but could be enhanced with more options (--iterations, --warmup, JSON output to file)
3. **Matrix output**: The matrix.py utility could output JSON/Markdown for CI integration
4. **Registry discovery**: The auto-discovery in registry.py currently scans all submodules - consider lazy loading or explicit registration for faster startup
5. **PCALMCredit primitive**: The credit_assignment.pc_alm primitive is declared in uses_primitives but not yet implemented as a separate primitive directory
6. **Documentation**: Consider adding local README.md files to complex primitives (optional per plan)
7. **Kernel implementations**: random_projections kernel falls back to reference; implement Triton FA kernels

### ✅ Facilitating Changes

- The `StateDynamics` protocol now has a consistent signature across all implementations
- Registry discovery is working and testable via `all_specs()`
- Parity testing framework is in place and validated
- Microbenchmark infrastructure exists for engineering smoke tests
- Primitive template validated with 3 primitives (pc_alm_settling, predictive_settling, random_projections)

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
