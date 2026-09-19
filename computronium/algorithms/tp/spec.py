"""Target Propagation (TP) Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.tp",
    kind="algorithm",
    name="Target Propagation",
    family="target_propagation",
    reference_entrypoint="computronium.algorithms.tp.reference.step",
    kernel_entrypoint="computronium.algorithms.tp.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    uses_primitives=(
        "primitive.state_dynamics.predictive_settling",
        "primitive.credit_assignment.target_inversion",
        "primitive.parameter_update.euclidean",
    ),
    summary="Target Propagation with transpose feedback and predictive settling.",
    equations="""
    t_L = one_hot(y)                           # output target
    t_l = t_{l+1} @ W_{l+1}^T                   # propagated targets via transpose
    ΔW_l = (a_l - t_l)^T @ a_{l-1} / batch     # layer-local pseudo-gradient
    """,
    invariants=(
        "targets propagated via transpose of forward weights",
        "output target is one-hot label",
        "pseudo-gradients use local layer activations and targets",
        "deterministic under fixed seed",
    ),
    notes="Kernel may accelerate the target propagation and pseudo-gradient computation.",
    tags=("target_propagation", "transpose_feedback", "predictive_coding"),
)
