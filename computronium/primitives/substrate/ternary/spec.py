"""Ternary Substrate Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.ternary",
    kind="primitive",
    name="Ternary Substrate",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.ternary.reference.make_substrate"
    ),
    kernel_entrypoint=(
        "computronium.primitives.substrate.ternary.kernel.make_substrate"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Digital substrate with ternary weight quantization {-α, 0, +α} for efficient inference.",
    equations="""
    w_ternary = sign(w) * max(|w|)
    x' = w_ternary @ x + b
    """,
    invariants=(
        "deterministic under fixed seed",
        "weights constrained to ternary values",
        "finite state",
        "STE gradient for training",
    ),
    notes="Reference implementation delegates to TernarySubstrate. Kernel falls back to reference (Triton TODO).",
    tags=("substrate", "digital", "ternary", "quantization", "inference"),
)
