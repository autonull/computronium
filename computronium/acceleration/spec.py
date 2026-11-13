"""Implementation Specification for Primitives and Algorithms.

Defines metadata for implementations including parity tolerances,
registry keys, and self-documentation fields.
"""

from dataclasses import dataclass
from typing import Final, Literal

Backend = Literal[
    "reference",
    "kernel",
]

KernelTechnology = Literal[
    "torch",
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


#: The runtime axis segment each spec axis names (TODO91 S1b).
#:
#: A spec ID *is* its runtime coordinate: ``primitive.<axis>.<name>`` selects
#: ``<name>`` on ``<axis>``. Three axes spell their segment differently from the
#: spec's historical axis label; the rest are identity, which is why the map is
#: two entries and a fallthrough rather than six rows.
AXIS_SEGMENT: Final[dict[str, str]] = {
    "state_dynamics": "dynamics",
    "credit_assignment": "credit",
    "parameter_update": "update",
}


def axis_segment(axis: str) -> str:
    """The runtime axis segment a spec axis names.

    Args:
        axis: A spec axis label, e.g. ``"state_dynamics"``.

    Returns:
        The runtime segment, e.g. ``"dynamics"``.
    """
    return AXIS_SEGMENT.get(axis, axis)


def coordinate_of_id(spec_id: str) -> tuple[str, str] | None:
    """The ``(runtime axis, runtime coordinate)`` a primitive spec ID names.

    Args:
        spec_id: A primitive spec ID of the form
            ``primitive.<axis>.<name>``.

    Returns:
        The pair, or ``None`` when the ID has another shape.
    """
    parts = spec_id.split(".")
    if len(parts) != 3 or parts[0] != "primitive":
        return None
    return axis_segment(parts[1]), parts[2]


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
        primitive.plasticity.fast_weights
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
    uses_primitives: tuple[str, ...] = ()

    # Self-documentation
    summary: str = ""
    equations: str = ""
    invariants: tuple[str, ...] = ()
    notes: str = ""

    # Future hooks
    tags: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
