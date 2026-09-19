"""NTM Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.ntm",
    kind="primitive",
    name="NTM Geometry",
    axis="geometry",
    reference_entrypoint=("computronium.primitives.geometry.ntm.reference.forward"),
    kernel_entrypoint=("computronium.primitives.geometry.ntm.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Neural Turing Machine with LSTM controller and content-addressed memory.",
    equations="""
Controller: h_t = LSTM([x_t; r_{t-1}])
Read: r_t = Σ_s softmax(β cos(m_s, k_r)) m_s
Write: m_s ← m_s ⊙ (1 - w_s ⊙ e) + w_s ⊙ a
""",
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "memory slots maintain identity",
    ),
    notes="Reference implementation delegates to NtmGeometry.",
    tags=(
        "geometry",
        "ntm",
        "external_memory",
        "content_addressing",
    ),
)
