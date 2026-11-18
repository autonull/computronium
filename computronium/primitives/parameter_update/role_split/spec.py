"""Role-Split Update Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.role_split",
    kind="primitive",
    name="Role-Split Update",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.role_split.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.role_split.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Per-name dispatcher: one rule on the named role, another everywhere else.",
    equations="""
Delta theta_n = on_role.step(g_n) if n in role_names else other.step(g_n)
    """,
    invariants=(
        "deterministic under fixed seed",
        "each parameter name is stepped exactly once",
        "momentum buffers kept per sub-rule",
    ),
    notes="Default split is Riemannian-orthogonal on the readout and Euclidean elsewhere.",
    tags=(
        "role_split",
        "dispatch",
        "hybrid",
        "parameter_update",
    ),
    task_families=('vision',),
    available=True,
    capability_card="Role-split update; separates feature/readout learning rates",
)
