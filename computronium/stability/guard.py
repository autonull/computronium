"""Adapter: the standalone stability package is the single source (Rule 6)."""

from stability.guard import (
    DEFAULT_TAU,
    CalibrationReport,
    DisagreementReport,
    GuardDecision,
    GuardHandle,
    ProbeSpec,
    StabilityGuard,
    StabilityVerdict,
    attach,
    calibrate_threshold,
    measure_guard_overhead,
    quantify_proxy_disagreement,
)

__all__ = [
    "DEFAULT_TAU",
    "CalibrationReport",
    "DisagreementReport",
    "GuardDecision",
    "GuardHandle",
    "ProbeSpec",
    "StabilityGuard",
    "StabilityVerdict",
    "attach",
    "calibrate_threshold",
    "measure_guard_overhead",
    "quantify_proxy_disagreement",
]
