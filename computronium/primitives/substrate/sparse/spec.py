"""Sparse Substrate Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.sparse",
    kind="primitive",
    name="Sparse Substrate",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.sparse.reference.make_substrate"
    ),
    kernel_entrypoint=(
        "computronium.primitives.substrate.sparse.kernel.make_substrate"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Digital substrate with configurable sparsity constraints for efficient computation.",
    equations="""
    W_sparse = W_dense * mask
    x' = W_sparse @ x + b
    """,
    invariants=(
        "deterministic under fixed seed",
        "sparsity level matches config",
        "finite state",
        "zero sparsity recovers dense digital substrate",
    ),
    notes="Reference implementation delegates to SparseSubstrate. Kernel falls back to reference (Triton TODO).",
    tags=("substrate", "digital", "sparse", "efficiency"),
)
