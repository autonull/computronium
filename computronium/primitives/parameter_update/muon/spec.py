"""Specification for Muon Update primitive."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.muon",
    kind="primitive",
    name="Muon (Riemannian Orthogonal Update)",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.muon.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.muon.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    summary="Orthogonal parameter updates via Riemannian optimization on Stiefel manifold.",
    equations="""
    ΔW = -lr · polar(μ·buf + g)  for matrices
    ΔW = -lr · g                 for vectors (biases)
    polar(M) = U @ Vh where M = U @ S @ Vh (SVD)
    buf ← μ·buf + g  (momentum buffer)
    """,
    invariants=(
        "orthogonal updates preserve Frobenius norm of weight matrices",
        "momentum accumulates signal before orthogonalization",
        "vectors (biases) ride plain SGD",
        "deterministic under fixed seed",
    ),
    notes="Uses exact SVD polar factor (ortho_steps=0) for full-spectrum whitening. Newton-Schulz iteration available as opt-in.",
    tags=("muon", "orthogonal_update", "riemannian_optimization"),
)
