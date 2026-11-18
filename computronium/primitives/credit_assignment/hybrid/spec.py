"""Hybrid Credit Assignment Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.hybrid",
    kind="primitive",
    name="Hybrid lockstep trunk + exact head",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.hybrid.reference.step"
    ),
    kernel_entrypoint=("computtronium.primitives.credit_assignment.hybrid.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="kernel_unverified",
    summary=(
        "Lockstep-local PEPITA trunk + 2-layer backprop head: the head's "
        "autograd graph is the only stored activation set."
    ),
    equations="""
    1. h = f_trunk(x) under no_grad; h = h.detach().requires_grad_()
    2. logits = f_head(h); L = CE(logits, y)
    3. δ, ∇W_head = autograd.grad(L, [h, W_head])  # true head gradients
    4. x̃ = x + γ·δBᵀ; ΔW_trunk,l = (mod_postᵀ mod_pre − std_postᵀ std_pre)/B
    """,
    invariants=(
        "trunk pass runs under no_grad; only the head graph is retained",
        "trunk and head gradients use the same pre-update weights",
        "the split lands on a Linear (a residual skip never straddles it)",
        "lockstep trunk ≡ store-all hybrid at atol=0 on a seeded fixture",
        "trunk activation set flat in depth",
    ),
    notes=(
        "Distinct from PEPITA: the trunk's error is the head's input "
        "gradient, not the output-layer target error. Distinct from "
        "backprop: the trunk never builds an autograd graph."
    ),
    tags=("hybrid", "local_learning", "lockstep", "random_feedback", "autograd"),
    task_families=("vision", "sequence"),
    available=True,
    capability_card="Hybrid local+backprop; lockstep trunk with exact head gradients; reduced activation memory",
)
