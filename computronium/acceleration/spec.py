"""Implementation Specification for Primitives and Algorithms.

Defines metadata for implementations including parity tolerances,
registry keys, and self-documentation fields.
"""

from dataclasses import dataclass
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
    """Tolerance thresholds for parity comparison between reference and kernel outputs."""

    max_abs_diff: float = 1e-4
    max_rel_diff: float = 1e-3
    min_cosine: float = 0.999


@dataclass(frozen=True, slots=True)
class ImplementationSpec:
    """Complete specification for a primitive or algorithm implementation.

    The `id` field should be stable and machine-readable.
    Recommended ID conventions:
        primitive.state_dynamics.predictive_settling
        primitive.credit_assignment.random_projections
        primitive.parameter_update.muon
        primitive.plasticity.fast_weight
        algorithm.backprop
        algorithm.fa
        algorithm.pcalm
        algorithm.eqprop
    """

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
