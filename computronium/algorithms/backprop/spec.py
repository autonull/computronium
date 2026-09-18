"""Backprop Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.backprop",
    kind="algorithm",
    name="Backpropagation",
    family="gradient_descent",
    reference_entrypoint="computronium.algorithms.backprop.reference.step",
    kernel_entrypoint="computronium.algorithms.backprop.kernel.step",
    kernel_technology="torch_compile",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_verified",
    uses_primitives=(
        "primitive.state_dynamics.instantaneous",
        "primitive.credit_assignment.backprop",
        "primitive.parameter_update.euclidean",
    ),
    summary="Standard backpropagation with automatic differentiation.",
    equations="""
    L = loss(f_θ(x), y)
    Δθ = -η ∇_θ L
    """,
    invariants=(
        "gradient matches autograd reference",
        "deterministic under fixed seed",
        "parameters updated via optimizer step",
    ),
    notes="Reference implementation uses PyTorch autograd. Kernel may use torch.compile.",
    tags=("backprop", "autograd", "baseline"),
)
