"""Thermodynamic Contrast Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.thermodynamic_contrast",
    kind="primitive",
    name="Thermodynamic Contrast",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.thermodynamic_contrast.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.thermodynamic_contrast.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Equilibrium Propagation contrastive credit assignment using free/nudged phase difference.",
    equations="""
    ΔW_l = (free_pre_lᵀ free_post_l − nudged_pre_lᵀ nudged_post_l)ᵀ / (β·batch)
    ε_l = (free_post_l − nudged_post_l) / β
    """,
    invariants=(
        "deterministic under fixed seed",
        "pseudo-gradients finite",
        "energy non-increasing on symmetric topology",
    ),
    notes="Reference implementation delegates to ThermodynamicContrast ontology class. Kernel acceleration targets contrastive Hebbian computation.",
    tags=("equilibrium_propagation", "contrastive", "local_learning"),
)
