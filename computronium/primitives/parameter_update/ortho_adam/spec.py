"""OrthoAdam Update Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.ortho_adam",
    kind="primitive",
    name="OrthoAdam Update",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.ortho_adam.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.ortho_adam.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Adam moments whose matrix directions are orthogonalized to the Adam step magnitude.",
    equations="""
m, v <- Adam moments
Delta theta_matrix = -ortho_lr * polar(m_hat) * |m_hat|/sqrt(v_hat);  vectors stay Adam
    """,
    invariants=(
        "deterministic under fixed seed",
        "vector parameters keep plain Adam steps",
        "matrix directions orthogonalized by the exact polar factor at ortho_steps=0",
    ),
    notes="Hybrid of the Adam and Muon families; two learning rates, one per parameter shape.",
    tags=(
        "adam",
        "orthogonal",
        "muon",
        "parameter_update",
    ),
    task_families=('vision', 'sequence'),
    available=True,
    capability_card="Orthogonal Adam; maintains weight orthogonality; stability",
)
