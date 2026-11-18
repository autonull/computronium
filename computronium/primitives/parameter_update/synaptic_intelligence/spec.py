"""Specification for the synaptic-intelligence rule (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.parameter_update.synaptic_intelligence",
    kind="primitive",
    name="Synaptic Intelligence Update",
    axis="parameter_update",
    reference_entrypoint="computronium.primitives.parameter_update.synaptic_intelligence.reference.step",
    kernel_entrypoint="computronium.primitives.parameter_update.synaptic_intelligence.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="The SI penalty lifted into an update rule with a task anchor.",
    equations="""
    ΔW = −lr·(g + ξ·Ω̃·(θ − θ*)),  Ω̃ = W/((θ − θ*)² + ε)
    """,
    invariants=("the penalty vanishes at the task anchor", "the path integral lives in the optimizer state"),
    notes="The reference wraps SynapticIntelligenceUpdate; the kernel falls back to it until a fused device path lands.",
    tags=("synaptic_intelligence", "consolidation", "parameter_update"),
    task_families=("continual",),
    available=True,
    capability_card="Synaptic Intelligence for continual learning; path integral importance; task anchor",
)