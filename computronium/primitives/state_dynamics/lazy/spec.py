"""Lazy State Dynamics Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.lazy",
    kind="primitive",
    name="Lazy Dynamics",
    axis="state_dynamics",
    reference_entrypoint=("computronium.primitives.state_dynamics.lazy.reference.step"),
    kernel_entrypoint=("computronium.primitives.state_dynamics.lazy.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
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
    task_families=('vision',),
    available=True,
    capability_card="Lazy dynamics; deferred computation; sparse updates",
)
