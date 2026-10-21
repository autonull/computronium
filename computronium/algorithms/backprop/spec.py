"""Backprop Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="algorithm.backprop",
    kind="algorithm",
    name="Backpropagation",
    reference_entrypoint="computronium.algorithms.backprop.reference.step",
    kernel_entrypoint="computronium.algorithms.backprop.kernel.step",
    kernel_technology="torch_compile",
    supported_backends=("reference", "kernel"),
    status="kernel_verified",
    uses_primitives=(
        "primitive.state_dynamics.instantaneous_pass",
        "primitive.credit_assignment.reverse_mode",
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
