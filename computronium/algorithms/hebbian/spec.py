"""Hebbian/STDP Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.hebbian",
    kind="algorithm",
    name="Hebbian/STDP",
    family="hebbian",
    reference_entrypoint="computronium.algorithms.hebbian.reference.step",
    kernel_entrypoint="computronium.algorithms.hebbian.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    uses_primitives=(
        "primitive.state_dynamics.instantaneous",
        "primitive.credit_assignment.local_goodness",
        "primitive.parameter_update.euclidean",
    ),
    summary="Hebbian learning: neurons that fire together, wire together.",
    equations="""
    ΔW_l ∝ h_l h_{l-1}^T  # Hebbian
    ΔW_l ∝ (h_l - ⟨h_l⟩)(h_{l-1} - ⟨h_{l-1}⟩)^T  # Covariance
    """,
    invariants=(
        "local weight updates only",
        "no global error signal required",
        "deterministic under fixed seed",
    ),
    notes="Uses LocalGoodnessCredit as a proxy for Hebbian correlation.",
    tags=("hebbian", "stdp", "local_learning", "correlation"),
)
