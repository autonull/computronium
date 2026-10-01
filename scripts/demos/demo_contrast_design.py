"""Demo: WP18 ContrastDesign — OFAT DOE + DataOrigin, known effect recovered.

Expected: an OFAT design over hidden_dim/num_layers identifies the known
optimum of a deterministic scoring function, with matched contrast groups
and explicit DataOrigin provenance labels.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from computronium.experiment.execution.contrast_design import (
    Factor,
    create_ofat_design,
)
from computronium.experiment.schema.coordinate import DataOrigin


def _score(params: dict[str, int]) -> float:
    """Known effect: 64 hidden units is optimal; depth 2 is optimal."""
    h, d = params["hidden_dim"], params["num_layers"]
    return -(abs(h - 64) / 64) - 0.1 * abs(d - 2)


def main() -> int:
    factors = (
        Factor(name="hidden_dim", levels=(32, 64, 128)),
        Factor(name="num_layers", levels=(1, 2, 4)),
    )
    design = create_ofat_design(
        factors=list(factors),
        base_levels={"hidden_dim": 32, "num_layers": 1},
        seed=42,
    )
    print(f"design: {design.design_kind.value}, runs: {design.n_runs}")

    by_group: dict[str, list] = {}
    for a in design.assignments:
        by_group.setdefault(a.matched_group, []).append(a)
    for group, arms in by_group.items():
        arms.sort(
            key=lambda a: _score({
                "hidden_dim": a.factor_assignments.get("hidden_dim", 64),
                "num_layers": a.factor_assignments.get("num_layers", 2),
            }),
            reverse=True,
        )
        best_arm = arms[0]
        print(f"group {group}: best = {best_arm.factor_assignments}")

    hidden_arms = by_group["ofat_hidden_dim"]
    assert hidden_arms[0].factor_assignments["hidden_dim"] == 64
    layer_arms = by_group["ofat_num_layers"]
    assert layer_arms[0].factor_assignments["num_layers"] == 2
    for origin in (DataOrigin.CONTROL, DataOrigin.CONTRAST):
        print(f"data_origin label: {origin.value}")
    print("Contrast-design demo: OK (known effect recovered)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
