"""Forward-Forward (FF) Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.ff",
    kind="algorithm",
    name="Forward-Forward",
    family="local_goodness",
    reference_entrypoint="computronium.algorithms.ff.reference.step",
    kernel_entrypoint="computronium.algorithms.ff.kernel.step",
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
    summary="Forward-Forward: layer-local objectives, no backward pass.",
    equations="""
    Positive pass:  h_l = σ(W_l h_{l-1} + y_l)
    Negative pass:  h_l = σ(W_l h_{l-1} + y'_l)

    L_l = softplus(-g_l^pos + θ) + softplus(g_l^neg - θ)
    where g_l = ||h_l||^2 is the goodness
    """,
    invariants=(
        "no backward pass through the network",
        "layer-local losses and optimizers",
        "deterministic under fixed seed",
    ),
    notes="Custom train_step with per-layer optimizers. Kernel may accelerate layer-wise operations.",
    tags=("forward_forward", "local_learning", "no_backprop", "goodness"),
)
