"""Reverse Mode Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.reverse_mode",
    kind="primitive",
    name="Reverse Mode",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.reverse_mode.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.reverse_mode.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
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
