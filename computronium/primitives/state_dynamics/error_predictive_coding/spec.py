"""Error Predictive Coding Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.error_predictive_coding",
    kind="primitive",
    name="Error Predictive Coding",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.error_predictive_coding.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.state_dynamics.error_predictive_coding.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Error-parameterized predictive coding: reverse-mode AD carries the loss gradient to every error.",
    equations="""
s_i = ŝ_i + ε_i,  ŝ_i = f_θ_i(s_{i−1})
Δθ_i ∝ (∂ŝ_i/∂θ_i)ᵀ ε_i
    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "settling residual decreases or remains bounded",
    ),
    notes="Not biologically local by design: reverse-mode propagation is the ePC trade-off.",
    tags=(
        "state_dynamics",
        "predictive_coding",
        "epc",
    ),
)
