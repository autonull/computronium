"""Local Contrastive Credit Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.local_contrastive",
    kind="primitive",
    name="Local Contrastive Credit",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.local_contrastive.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.local_contrastive.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Per-layer recomputed goodness contrast read from a label-augmented input channel.",
    equations="""
x_aug = [x | onehot(y)];  a_pos, a_neg from label roll
ΔW_hidden ∝ gate(a_pos) − gate(a_neg), EMA-normalized
    """,
    invariants=(
        "deterministic under fixed seed",
        "requires label-augmented inputs of width input_dim + label_dim",
        "readout trains on local CE with raw magnitude",
    ),
    notes="O(1)-peak-memory class: each layer's graph is built and released inside the credit.",
    tags=(
        "credit",
        "contrastive",
        "forward_forward",
        "label_channel",
    ),
    task_families=('vision',),
    available=True,
    capability_card="Local contrastive credit; positive/negative samples per layer; no global loss",
)
