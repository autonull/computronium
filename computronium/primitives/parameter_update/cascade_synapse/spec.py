"""Specification for the Benna-Fusi cascade rule (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.parameter_update.cascade_synapse",
    kind="primitive",
    name="Cascade Synapse Plasticity",
    axis="parameter_update",
    reference_entrypoint="computronium.primitives.parameter_update.cascade_synapse.reference.step",
    kernel_entrypoint="computronium.primitives.parameter_update.cascade_synapse.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="A metaplastic multi-level state per parameter.",
    equations="""
    Δθ = −lr·g·(1 + c);  c ← c + up on a sign flip
    """,
    invariants=("the cascade saturates at its level count", "a repeated direction decays the cascade"),
    notes="The reference wraps CascadeSynapsePlasticity; the kernel falls back to it until a fused device path lands.",
    tags=("cascade_synapse", "metaplastic", "parameter_update"),
)
