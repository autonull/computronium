"""Riemannian Orthogonal Update Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.riemannian_orthogonal",
    kind="primitive",
    name="Riemannian Orthogonal Update",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.riemannian_orthogonal.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.riemannian_orthogonal.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Muon-class polar-factor whitening of the momentum matrix.",
    equations="""
v <- mu*v + g;  Delta theta = -lr * polar(v)  (exact SVD at ortho_steps=0)
    """,
    invariants=(
        "deterministic under fixed seed",
        "full-spectrum whitening at ortho_steps=0",
        "Newton-Schulz iteration only when ortho_steps > 0",
    ),
    notes="The coordinate registered as `muon` delegates to this same class; the two coordinates differ in their update_type and therefore in the dispatch key, not in the executed rule.",
    tags=(
        "muon",
        "riemannian",
        "orthogonal",
        "parameter_update",
    ),
)
