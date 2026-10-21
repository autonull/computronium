"""Spike Integration Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
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
