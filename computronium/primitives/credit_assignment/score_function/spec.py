"""Score-function estimator primitive specification."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.score_function",
    kind="primitive",
    name="Score Function Credit",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.score_function.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.score_function.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Unbiased score-function gradient of an expected task loss.",
    equations="""
    a ~ Categorical(softmax(logits))
    R(a) = 1[a = y]
    ĝ = (1/n) Σ ∇_θ log π(a_i) (R(a_i) − b), b = mean R
    """,
    invariants=(
        "deterministic under fixed seed",
        "unbiased for the expected reward",
        "variance falls as 1/√n samples",
    ),
    notes=(
        "Reference wraps ScoreFunctionCredit; the kernel falls back to it "
        "until a fused sample/backprop path lands."
    ),
    tags=("score_function", "reinforce", "policy_gradient", "unbiased", "estimator"),
    task_families=('vision',),
    available=True,
    capability_card="Score function (REINFORCE) credit; high variance; baseline for comparison",
)
