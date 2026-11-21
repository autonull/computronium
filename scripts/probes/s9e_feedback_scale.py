"""S9e probe: does ``credit.feedback_scale`` move a credit's pseudo-gradient?

The ladder measured the same val_acc at 0.001/0.01/0.1 for
``thermodynamic_contrast`` and ``local_goodness`` (S9b), and published both as
"tuned at x0.1" before the tie rule caught it. A tie at the accuracy ruler can
be a plateau or an inert knob; this probe asks the cheaper question directly —
one pseudo-gradient per scale, at the primitive's own micro-case — so the ladder
records a mechanism, not a plateau.

Measured 2026-11-20: the norm is bit-identical across scales for both credits,
so ``feedback_scale`` is inert at their boxes (thermodynamic contrast is exact —
no feedback matrix — and local goodness runs ``local_objective="ff"``, whose
pseudo-gradient is the autograd derivative of the goodness contrast). The
ladder therefore withdraws the knob for a credit whose law declares it unread.

Run: ``uv run python scripts/probes/s9e_feedback_scale.py``
"""

from __future__ import annotations

from dataclasses import replace

from computronium.primitives.cases import _credit_step, build_case, cell_config
from computronium.primitives.registry import get_primitive_spec

SCALES = (0.001, 0.01, 0.1)
CREDITS = ("thermodynamic_contrast", "local_goodness")


def main() -> int:
    inert = True
    for credit in CREDITS:
        spec = get_primitive_spec(f"primitive.credit_assignment.{credit}")
        assert spec is not None
        cell = cell_config(spec, "mnist")
        case = build_case(spec, "mnist")
        norms = []
        for scale in SCALES:
            scaled = replace(cell, credit=replace(cell.credit, feedback_scale=scale))
            norms.append(_credit_step(scaled, case).metrics["pseudo_gradient_norm"])
        same = len(set(norms)) == 1
        inert &= same
        print(
            f"{credit}: pseudo-gradient norm {norms} -> {'inert' if same else 'binds'}"
        )
    return 0 if inert else 1


if __name__ == "__main__":
    raise SystemExit(main())
