"""Noisy Substrate Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.noisy",
    kind="primitive",
    name="Noisy Substrate",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.noisy.reference.make_substrate"
    ),
    kernel_entrypoint=("computronium.primitives.substrate.noisy.kernel.make_substrate"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Digital substrate with configurable additive Gaussian noise for robustness testing.",
    equations="""
    x' = x + N(0, σ²)
    """,
    invariants=(
        "deterministic under fixed seed",
        "noise level matches config",
        "finite state",
        "zero noise recovers digital substrate",
    ),
    notes="Reference implementation delegates to NoisySubstrate. Kernel falls back to reference (Triton TODO).",
    tags=("substrate", "digital", "noise", "robustness"),
)
