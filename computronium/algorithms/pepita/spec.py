"""PEPITA Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.pepita",
    kind="algorithm",
    name="PEPITA",
    family="local_goodness",
    reference_entrypoint="computronium.algorithms.pepita.reference.step",
    kernel_entrypoint="computronium.algorithms.pepita.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_verified",
    uses_primitives=(
        "primitive.state_dynamics.instantaneous_pass",
        "primitive.credit_assignment.local_goodness",
        "primitive.parameter_update.euclidean",
    ),
    summary="PEPITA: fixed random B, error-modulated second forward pass, autograd update.",
    equations="""
    h_l = σ(W_l h_{l-1})
    h_l^e = σ(W_l h_{l-1} + B_l e)  # error-modulated pass

    ΔW_l ∝ (h_l^e - h_l) h_{l-1}^T
    """,
    invariants=(
        "single fixed random feedback matrix B",
        "error modulation in second forward pass",
        "autograd update on perturbed states",
        "deterministic under fixed seed",
    ),
    notes="Distinct from Forward-Forward: uses error signal, not label injection.",
    tags=("pepita", "local_learning", "error_modulated", "random_feedback"),
)
