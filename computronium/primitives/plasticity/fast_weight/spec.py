"""Fast Weight Plasticity Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.plasticity.fast_weight",
    kind="primitive",
    name="Fast Weight Plasticity",
    axis="plasticity",
    reference_entrypoint=(
        "computronium.primitives.plasticity.fast_weight.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.plasticity.fast_weight.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_verified",
    summary="Episode-local associative memory via Hebbian outer-product with random projection.",
    equations="""
    A_{t+1} = decay * A_t + lr * Proj(outer(pre_t, post_t))
    pre = settled input x, post = settled output y (F3-audit fix)
    """,
    invariants=(
        "fast weights remain bounded",
        "deterministic under fixed seed",
        "projection is non-expansive (||P v|| <= ||v||)",
    ),
    notes="Accelerated kernel could fuse Hebbian update with projection.",
    tags=("fast_weights", "hebbian", "associative_memory", "episode_local"),
)
