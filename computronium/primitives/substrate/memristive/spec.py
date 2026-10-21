"""Memristive Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.memristive",
    kind="primitive",
    name="Memristive",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.memristive.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.substrate.memristive.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Memristive substrate with IR-drop and conductance bounds.",
    equations="""
V = IR; dG/dt = f(V, G)
    """,
    invariants=(
        "deterministic under fixed seed",
        "conductance stays within bounds",
    ),
    notes="Reference wraps MemristiveSubstrate; kernel falls back to reference",
    tags=(
        "substrate",
        "memristive",
        "ir-drop",
        "conductance",
    ),
)
