"""Direct Feedback Alignment (DFA) Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.dfa",
    kind="algorithm",
    name="Direct Feedback Alignment",
    family="random_feedback",
    reference_entrypoint="computronium.algorithms.dfa.reference.step",
    kernel_entrypoint="computronium.algorithms.dfa.kernel.step",
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
        "primitive.credit_assignment.random_projections",
        "primitive.parameter_update.euclidean",
    ),
    summary="Direct Feedback Alignment with output-to-all-layers fixed random feedback.",
    equations="""
    δ_L = ∂L/∂a_L                             # output error via autograd
    δ_l = δ_L @ B_l                            # direct feedback from output
    ΔW_l = δ_l @ a_{l-1}^T / batch             # layer-local weight update
    where B_l are fixed random matrices (not W^T)
    """,
    invariants=(
        "feedback matrices are fixed and not transposes",
        "all hidden layers receive feedback directly from output layer",
        "pseudo-gradients align with reference gradients over time",
        "deterministic under fixed seed",
    ),
    notes="DFA uses direct feedback from output to each layer. Kernel may accelerate the random projection credit computation.",
    tags=("direct_feedback_alignment", "random_feedback", "local_learning"),
)
