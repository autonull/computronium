"""Routing Plasticity Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.plasticity.routing",
    kind="primitive",
    name="Routing Plasticity",
    axis="plasticity",
    reference_entrypoint=("computronium.primitives.plasticity.routing.reference.step"),
    kernel_entrypoint=("computronium.primitives.plasticity.routing.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    summary="State-dependent pathway gating with Gumbel-Softmax routing and per-unit modulation.",
    equations="""
    gate_logits_{t+1} = decay * gate_logits_t + lr * (x @ G)
    active_routes = GumbelSoftmax(gate_logits, temperature)  # training
              = top_k(gate_logits)                          # eval
    mask_ℓ = sigmoid(gate_logits @ U_ℓ)  # per-layer modulation
    """,
    invariants=(
        "gate logits remain bounded",
        "active routes sum to 1 per sample (training) or match top_k (eval)",
        "deterministic under fixed seed",
    ),
    notes="Accelerated kernel could fuse gate logit update with routing selection.",
    tags=("routing", "gating", "sparse_routing", "conditional_computation", "moe"),
)
