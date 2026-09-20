"""Quantum Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.quantum",
    kind="primitive",
    name="Quantum",
    axis="substrate",
    reference_entrypoint=("computronium.primitives.substrate.quantum.reference.step"),
    kernel_entrypoint=("computronium.primitives.substrate.quantum.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Quantum substrate with unitary gate operations",
    equations="""
Unitary evolution: U = exp(-iHt)
    """,
    invariants=(
        "deterministic under fixed seed",
        "unitary operations preserve norm",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "substrate",
        "quantum",
        "unitary",
    ),
)
