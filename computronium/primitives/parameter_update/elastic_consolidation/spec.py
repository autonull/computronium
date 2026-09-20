"""Elastic Consolidation Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.elastic_consolidation",
    kind="primitive",
    name="Elastic Consolidation",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.elastic_consolidation.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.elastic_consolidation.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Elastic Weight Consolidation (EWC) with Fisher information",
    equations="""
Δθ = -η(∇L + λΣ F_i(θ_i - θ_i^*))
    """,
    invariants=(
        "deterministic under fixed seed",
        "parameters remain finite",
        "EWC regularization applied",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "parameter_update",
        "elastic_consolidation",
        "ewc",
        "fisher",
    ),
)
