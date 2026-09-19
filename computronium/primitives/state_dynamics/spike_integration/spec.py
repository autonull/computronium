"""Spike Integration Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.spike_integration",
    kind="primitive",
    name="Spike Integration",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.spike_integration.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.state_dynamics.spike_integration.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Spike integration dynamics (LIF/Izhikevich).",
    equations="""
tau * dv/dt = -v + I; v = v + dt/tau * (-v + I)
    """,
    invariants=(
        "state remains finite",
        "deterministic under fixed seed",
        "spike times are deterministic",
    ),
    notes="Reference wraps SpikeIntegrationDynamics; kernel falls back to reference (Triton TODO in snn_kernels.py)",
    tags=(
        "spiking",
        "lif",
        "izhikevich",
        "settling",
    ),
)
