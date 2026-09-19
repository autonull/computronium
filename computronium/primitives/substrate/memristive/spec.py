"""Memristive Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
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
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
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
