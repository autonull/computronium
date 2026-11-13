"""Reverse Mode Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.gradient",
    kind="primitive",
    name="Gradient Credit",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.gradient.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.gradient.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Reverse-mode autograd credit (backprop baseline).",
    equations="""
∂L/∂W via torch.autograd.grad
    """,
    invariants=(
        "deterministic under fixed seed",
        "exact gradient match with autograd",
    ),
    notes="Reference wraps GradientCredit; kernel falls back to reference",
    tags=(
        "backprop",
        "gradient",
        "autograd",
        "baseline",
    ),
)
