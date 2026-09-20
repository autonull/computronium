"""Feedback Alignment (FA) Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.fa",
    kind="algorithm",
    name="Feedback Alignment",
    family="random_feedback",
    reference_entrypoint="computronium.algorithms.fa.reference.step",
    kernel_entrypoint="computronium.algorithms.fa.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    uses_primitives=(
        "primitive.state_dynamics.instantaneous_pass",
        "primitive.credit_assignment.random_projections",
        "primitive.parameter_update.euclidean",
    ),
    summary="Feedback Alignment with fixed random feedback matrices.",
    equations="""
    δ_l = B_{l+1} δ_{l+1} ⊙ σ'(z_l)
    ΔW_l = -η δ_l a_{l-1}^T
    where B are fixed random matrices (not W^T)
    """,
    invariants=(
        "feedback matrices are fixed and not transposes",
        "pseudo-gradients align with reference gradients over time",
        "deterministic under fixed seed",
    ),
    notes="Kernel may accelerate the random projection credit computation.",
    tags=("feedback_alignment", "random_feedback", "local_learning"),
)
