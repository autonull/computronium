"""Hebbian/STDP Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.hebbian",
    kind="algorithm",
    name="Hebbian/STDP",
    reference_entrypoint="computronium.algorithms.hebbian.reference.step",
    kernel_entrypoint="computronium.algorithms.hebbian.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_verified",
    uses_primitives=(
        "primitive.state_dynamics.instantaneous_pass",
        "primitive.credit_assignment.temporal_trace",
        "primitive.parameter_update.euclidean",
    ),
    summary="Hebbian/STDP learning: neurons that fire together, wire together.",
    equations="""
    ΔW_l ∝ h_l h_{l-1}^T  # Hebbian
    ΔW_l ∝ (h_l - ⟨h_l⟩)(h_{l-1} - ⟨h_{l-1}⟩)^T  # Covariance
    ΔW_l ∝ a_plus·postᵀ·pre_trace − a_minus·post_traceᵀ·pre  # STDP
    """,
    invariants=(
        "local weight updates only",
        "no global error signal required",
        "deterministic under fixed seed",
        "spike-timing dependent plasticity (STDP) mechanism",
    ),
    notes="Uses TemporalTraceCredit for STDP-based credit assignment.",
    tags=("hebbian", "stdp", "local_learning", "correlation", "temporal_trace"),
)
