"""Specification for the schedule-free AdamW rule (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.parameter_update.schedule_free",
    kind="primitive",
    name="Schedule Free Update",
    axis="parameter_update",
    reference_entrypoint="computronium.primitives.parameter_update.schedule_free.reference.step",
    kernel_entrypoint="computronium.primitives.parameter_update.schedule_free.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="The averaged sequence iterate is the evaluation point.",
    equations="""
    z ← z − lr·g/√v;  x ← (1 − c)x + c·z,  c = 1/(t + 1)
    """,
    invariants=("no decreasing learning-rate schedule is read", "the evaluation point is the running average"),
    notes="The reference wraps ScheduleFreeUpdate; the kernel falls back to it until a fused device path lands.",
    tags=("schedule_free", "averaging", "parameter_update"),
)
