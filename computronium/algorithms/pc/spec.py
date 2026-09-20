"""Predictive Coding (PC) Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.pc",
    kind="algorithm",
    name="Predictive Coding",
    family="predictive_coding",
    reference_entrypoint="computronium.algorithms.pc.reference.step",
    kernel_entrypoint="computronium.algorithms.pc.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_verified",
    uses_primitives=(
        "primitive.state_dynamics.predictive_settling",
        "primitive.credit_assignment.local_goodness",
        "primitive.parameter_update.euclidean",
    ),
    summary="Predictive Coding: hierarchical prediction error minimization.",
    equations="""
    ε_l = h_l - f_θ_l(h_{l+1})  # prediction error
    h_l ← h_l - η (∂ε_l/∂h_l + ∂ε_{l-1}/∂h_l)  # state update

    Δθ_l ∝ -ε_l ∂f_θ_l/∂θ_l  # weight update
    """,
    invariants=(
        "prediction errors decrease during settling",
        "hierarchical error propagation",
        "deterministic under fixed seed",
    ),
    notes="Kernel may accelerate the predictive settling dynamics.",
    tags=("predictive_coding", "hierarchical", "error_minimization", "settling"),
)
