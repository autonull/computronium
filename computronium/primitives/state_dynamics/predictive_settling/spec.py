"""Predictive Settling Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.predictive_settling",
    kind="primitive",
    name="Predictive Settling",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.predictive_settling.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.state_dynamics.predictive_settling.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    summary="Predictive coding settling dynamics (PCN).",
    equations="""
    μ_0 = x                    # input clamped
    μ_l ← μ_l - η · (μ_l - f(μ_{l-1} W_{l-1} + b_{l-1}))  # prediction error minimization
    """,
    invariants=(
        "prediction errors decrease or remain bounded",
        "state remains finite",
        "deterministic under fixed seed",
    ),
    notes="Accelerated kernel should preserve the settled state within tolerance.",
    tags=("predictive_coding", "pcn", "settling"),
)
