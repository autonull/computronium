"""Complex Substrate Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.complex",
    kind="primitive",
    name="Complex Substrate",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.complex.reference.make_substrate"
    ),
    kernel_entrypoint=(
        "computronium.primitives.substrate.complex.kernel.make_substrate"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Digital substrate with complex-valued state space for holomorphic/phase-based computation.",
    equations="""
    x = x_real + i * x_imag
    x' = W @ x + b  (complex matmul)
    """,
    invariants=(
        "deterministic under fixed seed",
        "complex dtype preserved",
        "finite state",
        "conjugate symmetry for real outputs",
    ),
    notes="Reference implementation delegates to ComplexSubstrate. Kernel falls back to reference (Triton TODO).",
    tags=("substrate", "digital", "complex", "holomorphic", "phase"),
)
