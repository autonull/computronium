"""Specification for the VON rule (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.parameter_update.bayesian_online",
    kind="primitive",
    name="Bayesian Online Update",
    axis="parameter_update",
    reference_entrypoint="computronium.primitives.parameter_update.bayesian_online.reference.step",
    kernel_entrypoint="computronium.primitives.parameter_update.bayesian_online.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="An online diagonal Gaussian posterior per parameter.",
    equations="""
    μ ← μ − α·σ²·g;  σ² ← max(min_var, σ²·(1 − α·σ²·g²))
    """,
    invariants=("the variance falls on a constant gradient", "the variance floors at its declared minimum"),
    notes="The reference wraps BayesianOnlineUpdate; the kernel falls back to it until a fused device path lands.",
    tags=("bayesian_online", "von", "posterior", "parameter_update"),
)
