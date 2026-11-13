"""Photonic Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.optical",
    kind="primitive",
    name="Optical",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.optical.reference.make_substrate"
    ),
    kernel_entrypoint=(
        "computronium.primitives.substrate.optical.kernel.make_substrate"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
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
        "optical",
        "phase",
    ),
)
