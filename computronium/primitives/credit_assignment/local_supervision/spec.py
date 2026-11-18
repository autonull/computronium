"""Specification for the local-supervision estimator (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.local_supervision",
    kind="primitive",
    name="Local Supervision Credit",
    axis="credit_assignment",
    reference_entrypoint="computronium.primitives.credit_assignment.local_supervision.reference.step",
    kernel_entrypoint="computronium.primitives.credit_assignment.local_supervision.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Deep local credit: one auxiliary supervised head per hidden layer.",
    equations="""
    ĝ_ℓ = ∇_{W_ℓ} CE(s·A_ℓ φ(W_ℓ x_{ℓ−1}), y)
    """,
    invariants=("no gradient crosses a layer boundary", "the auxiliary head is one fixed orthonormalized projection", "the readout keeps the exact task gradient"),
    notes="The reference wraps LocalSupervisionCredit; the kernel falls back to it until a fused device path lands.",
    tags=("local_supervision", "layerwise", "auxiliary_head", "credit"),
    task_families=("continual", "vision"),
    available=True,
    capability_card="Local credit with auxiliary heads; stable at batch 1; compatible with EWC",
)
