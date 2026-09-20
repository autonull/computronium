"""Lazy State Dynamics Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.lazy_state_dynamics",
    kind="primitive",
    name="Lazy State Dynamics",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.lazy_state_dynamics.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.state_dynamics.lazy_state_dynamics.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Sequential (Gauss-Seidel) EqProp settle with lazy per-layer activation",
    equations="""
Gauss-Seidel sweep: a_l^{t+1} = f(a_l^t, a_{l-1}^{t+1}, a_{l+1}^t)
    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "Gauss-Seidel converges to same fixed point as Jacobi",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "state_dynamics",
        "lazy",
        "gauss_seidel",
        "eqprop",
    ),
)
