"""Neuromorphic Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.neuromorphic",
    kind="primitive",
    name="Neuromorphic",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.neuromorphic.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.substrate.neuromorphic.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Neuromorphic substrate with async spikes.",
    equations="""
Spike-based computation with event-driven updates.
    """,
    invariants=(
        "deterministic under fixed seed",
        "spike timing is deterministic",
    ),
    notes="Reference wraps NeuromorphicSubstrate; kernel falls back to reference",
    tags=(
        "substrate",
        "neuromorphic",
        "spikes",
        "async",
    ),
)
