"""P0.2/P0.3 instrument self-check + deliberate NaN-path exercise.

TODO27.md §Phase 0 acceptance: every instrument passes its self-check
(backprop credit must read ≈BP's own gradient — cos >= 0.9, the
GradientCredit identity-card gate), and a NaN/failure path is exercised
once on purpose (NaN input must surface as NaN in the instrument reading,
never zero-filled silence).

Also reports the EqProp (thermodynamic-contrast) family's BP-alignment
attenuation profile by depth — an instrument reading, not a verdict.

Run: uv run python scripts/probes/instrument_selfcheck.py
Walltime: < 1 min (CPU, tiny systems).
"""

import json
import math

import torch

from computronium.analysis.instruments import (
    BP_COSINE_GATE,
    credit_trace,
    settle_horizon,
)
from computronium.models.native import (
    create_native_backprop_mlp,
    create_native_eqprop_mlp,
)

__all__ = ["main"]

DEPTH_ATTENUATION = (1, 2, 4, 8)


def main() -> None:
    torch.manual_seed(0)
    x = torch.randn(32, 20)
    y = torch.randint(0, 5, (32,))
    report: dict[str, object] = {}

    bp = create_native_backprop_mlp(20, 32, 5, num_layers=2)
    trace = credit_trace(bp, x, y, bp_reference=True)
    min_cos = trace["bp_min_cosine"]
    assert isinstance(min_cos, float)
    assert min_cos >= BP_COSINE_GATE, (
        f"instrument self-check FAILED: backprop credit read BP gradient "
        f"at cos {min_cos:.4f} < gate {BP_COSINE_GATE}"
    )
    report["backprop_selfcheck"] = {"bp_min_cosine": min_cos, "gate": BP_COSINE_GATE}
    print(f"PASS backprop self-check: bp_min_cosine={min_cos:.4f}")

    eq = create_native_eqprop_mlp(20, 32, 5, num_layers=2)
    eq_trace = credit_trace(eq, x, y, bp_reference=True)
    assert isinstance(eq_trace["bp_cosine"], dict)
    report["eqprop_bp_alignment"] = eq_trace["bp_cosine"]
    print(
        "eqprop BP alignment (attenuation profile):",
        {k: round(v, 3) for k, v in eq_trace["bp_cosine"].items()},
    )

    deep = create_native_eqprop_mlp(20, 32, 5, num_layers=8)
    report["eqprop_depth8_settle_horizon"] = settle_horizon(deep, x, y)
    print("eqprop depth-8 settle horizon:", report["eqprop_depth8_settle_horizon"])

    nan_x = x.clone()
    nan_x[0] = float("nan")
    nan_trace = credit_trace(eq, nan_x, y)
    norms = nan_trace["layer_norms"]
    assert isinstance(norms, dict)
    nan_surfaced = any(math.isnan(v) for v in norms.values())
    assert nan_surfaced, (
        "NaN-path exercise FAILED: a NaN input was absorbed silently — "
        "the instrument must surface the failure, not zero-fill it"
    )
    report["nan_path"] = "surfaced (loud), not zero-filled"
    print("PASS NaN-path exercise: NaN surfaced in credit norms")

    out = json.dumps(report, indent=2, default=str)
    print(out)


if __name__ == "__main__":
    main()
