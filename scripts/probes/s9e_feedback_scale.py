"""S9e probe: does the knob the ladder sweeps move a credit's pseudo-gradient?

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

S9e follow-up (same day): the two credits S9b also swept still laddered the
withdrawn knob, so this probe now measures the knob each law declares it reads.
``beta`` binds for ``thermodynamic_contrast`` (the nudge strength), ``fd_step``
binds for ``zeroth_order``, and ``feedback_scale`` binds for
``target_inversion`` — its accuracy ruler still ties at chance, which is a
plateau on an unimplemented row, not an inert knob.

Run: ``uv run python scripts/probes/s9e_feedback_scale.py``
"""

from __future__ import annotations

from dataclasses import replace

from computronium.primitives.cases import _credit_step, build_case, cell_config
from computronium.primitives.registry import get_primitive_spec

SCALES = (0.1, 1.0, 10.0)
#: Each credit and the config field the ladder sweeps (``None``: the law
#: declares the field unread, and the ladder withdraws the knob).
CASES = (
    ("thermodynamic_contrast", "beta"),
    ("local_goodness", "feedback_scale"),
    ("target_inversion", "feedback_scale"),
    ("zeroth_order", "fd_step"),
)


def _norm(credit: str, field: str, factor: float) -> float:
    spec = get_primitive_spec(f"primitive.credit_assignment.{credit}")
    assert spec is not None
    cell = cell_config(spec, "mnist")
    case = build_case(spec, "mnist")
    default = getattr(cell.credit, field)
    scaled = replace(cell, credit=replace(cell.credit, **{field: default * factor}))
    return float(_credit_step(scaled, case).metrics["pseudo_gradient_norm"])


def main() -> int:
    for credit, field in CASES:
        norms = [round(_norm(credit, field, factor), 6) for factor in SCALES]
        same = len(set(norms)) == 1
        print(
            f"{credit}.{field}: pseudo-gradient norm {norms} -> "
            f"{'inert' if same else 'binds'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
