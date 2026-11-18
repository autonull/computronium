"""Neuromorphic Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.neuromorphic",
    kind="primitive",
    name="Neuromorphic",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.neuromorphic.reference.make_substrate"
    ),
    kernel_entrypoint=(
        "computronium.primitives.substrate.neuromorphic.kernel.make_substrate"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
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
    task_families=('neuromorphic', 'vision'),
    available=True,
    capability_card="Neuromorphic substrate; event-driven; spiking; low power",
)
