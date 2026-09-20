"""Photonic Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.photonic",
    kind="primitive",
    name="Photonic",
    axis="substrate",
    reference_entrypoint=("computronium.primitives.substrate.photonic.reference.step"),
    kernel_entrypoint=("computronium.primitives.substrate.photonic.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Optical/photonic substrate with phase/amplitude encoding",
    equations="""
Complex-valued operations via phase interference
    """,
    invariants=(
        "deterministic under fixed seed",
        "complex-valued operations",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "substrate",
        "photonic",
        "optical",
        "phase",
    ),
)
