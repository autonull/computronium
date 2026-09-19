"""Substrate Coupled Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.plasticity.substrate_coupled",
    kind="primitive",
    name="Substrate Coupled",
    axis="plasticity",
    reference_entrypoint=(
        "computronium.primitives.plasticity.substrate_coupled.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.plasticity.substrate_coupled.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Substrate-coupled plasticity.",
    equations="""
Plasticity coupled to substrate physics (e.g., memristive conductance).
    """,
    invariants=(
        "deterministic under fixed seed",
        "substrate state evolves with plasticity",
    ),
    notes="Reference wraps SubstrateCoupledPlasticity; kernel falls back to reference",
    tags=(
        "plasticity",
        "substrate",
        "coupled",
        "memristive",
    ),
)
