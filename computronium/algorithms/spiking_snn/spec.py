"""Spiking SNN Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.spiking_snn",
    kind="algorithm",
    name="Spiking SNN (STDP)",
    family="spiking",
    reference_entrypoint="computronium.algorithms.spiking_snn.reference.step",
    kernel_entrypoint="computronium.algorithms.spiking_snn.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    uses_primitives=(
        "primitive.state_dynamics.spike_integration",
        "primitive.credit_assignment.temporal_trace",
        "primitive.parameter_update.euclidean",
    ),
    summary="Spiking Neural Network: LIF neurons with STDP credit assignment.",
    equations="""
    LIF: τ_m dv/dt = -v + I_syn,  spike if v > θ
    STDP: ΔW ∝ Σ_{t_pre, t_post} F(t_post - t_pre)
    """,
    invariants=(
        "spike timing determines weight updates",
        "membrane potential dynamics are deterministic",
        "deterministic under fixed seed",
    ),
    notes="Kernel may accelerate spike integration and STDP computation.",
    tags=("spiking", "snn", "stdp", "lif", "temporal"),
)
