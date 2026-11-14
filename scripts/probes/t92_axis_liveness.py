"""TODO92 §3.9: classify every declared axis value as refused, live, or inert.

Method. Read the declared space for ``digits`` (the canonical task) and
``cora`` (the graph task). For one axis value at a time, take the declared-legal
completion closest to the canonical stack (digital / feedforward /
instantaneous / null / gradient / adam), compose it, run **one** ``train_step``
on a seeded synthetic batch, and fingerprint the post-step geometry parameters.
The reference is the same completion with the axis set to the canonical value
(or the nearest declared value when the canonical one is refused). Bit-identical
parameters mean inert; a difference means live.

Why parameters, not ``train_loss``: the trainer reports the loss *before* the
update, so a one-step loss comparison cannot see a credit or update rule. It
also cannot separate Lion from Adam, whose first steps are both sign-like
(measured: ``train_loss`` identical, parameter delta 6.3e-06). The parameter
fingerprint is the sensitive one-step ruler; the mechanics live in
``computronium.experiment.evidence.liveness``.

Why several completions: a mechanism can need a partner axis to be exercised.
``conflict_adaptive`` is readout-replacing, so the gradient credit is refused
and the closest legal completion uses an error-blind credit that never writes
the replacement readout; the row is inert there but live with
``local_goodness``/``target_inversion``/``random_projections``. The probe tries a
bounded set of completions before calling a row inert.

Special cases. ``complex`` is refused on every task by
``complex_substrate_real_compute``. ``graph`` is not reachable on ``digits``
(the geometry x task-shape rule), so it is probed on Cora against a flat
feedforward reference. ``rule_state`` and ``substrate_coupled`` are inert in the
standard step (the former has no ``modulate``; the latter is a documented no-op
at the plasticity protocol level) and are declared unavailable with their
reversal triggers in ``seed_registries._UNAVAILABLE``.

Measured 2026-11-14 (CPU, digits 8x8 + Cora): 57 declared values = 6 canonical
references + 48 live + 1 refused (`complex`) + 2 unavailable (`rule_state`,
`substrate_coupled`); 0 undeclared inert. Walltime printed, never recorded.

Run: uv run python scripts/probes/t92_axis_liveness.py
"""

from __future__ import annotations

import time
from collections import Counter
from typing import cast

import torch

from computronium.experiment.evidence.liveness import (
    CANONICAL,
    describe,
    one_step_fingerprint,
    same_fingerprint,
)
from computronium.experiment.legality.dsl import CoordinateContext, evaluate
from computronium.experiment.legality.engine import void_rules
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.schema.seed_registries import (
    _UNAVAILABLE,
    seed_all_registries,
)
from computronium.experiment.surface.combinations import (
    AXIS_ORDER,
    declared_space,
)

__all__ = ["main"]

type Fingerprint = tuple[dict[str, torch.Tensor], dict[str, torch.Tensor], int]

#: Cheapest-first tie-break for a completion's dynamics.
DYNAMICS_COST = {
    "instantaneous": 0,
    "lazy": 1,
    "spike_integration": 2,
    "error_predictive_coding": 3,
    "energy_minimization": 4,
    "predictive_settling": 5,
    "pc_alm": 6,
    "diffusion": 7,
}
MAX_COMPLETIONS = 12


def _axes() -> dict[str, tuple[str, ...]]:
    return {axis.value: tuple(AXES_REGISTRIES[axis].keys()) for axis in StructuralAxis}


def _available(axis: str, value: str) -> bool:
    return AXES_REGISTRIES[StructuralAxis[axis.upper()]][value].available


def _unavailable_reason(axis: str, value: str) -> str | None:
    return _UNAVAILABLE.get((StructuralAxis[axis.upper()], value))


def _selection(cell: tuple[str, ...]) -> dict[str, str]:
    return dict(zip(AXIS_ORDER, cell, strict=True))


def _refusal(selection: dict[str, str], task: str | None) -> str | None:
    ctx = CoordinateContext(Coordinate(**selection, params={}), task=task)
    for rule in void_rules():
        if not evaluate(rule.predicate, ctx):
            return rule.name
    return None


def _completions(
    space, axis: str, value: str, limit: int = MAX_COMPLETIONS
) -> list[tuple[str, ...]]:
    index = AXIS_ORDER.index(axis)

    def order(cell: tuple[str, ...]) -> tuple[int, int, tuple[str, ...]]:
        distance = sum(
            1
            for name, chosen in zip(AXIS_ORDER, cell, strict=True)
            if chosen != CANONICAL[name]
        )
        return distance, DYNAMICS_COST.get(cell[index], 9), cell

    candidates = sorted(
        (cell for cell in space.cells if cell[index] == value), key=order
    )
    return candidates[:limit]


def _reference_values(space, axis: str) -> list[str]:
    index = AXIS_ORDER.index(axis)
    values = [CANONICAL[axis]]
    values.extend(sorted({candidate[index] for candidate in space.cells} - set(values)))
    return values


def _run_one(
    task: str,
    selection: dict[str, str],
    started: float,
    *,
    initial=None,
    joint_null: bool = False,
) -> tuple[str, Fingerprint | str, str]:
    try:
        before, after, count = one_step_fingerprint(
            task, selection, initial=initial, joint_null=joint_null
        )
    except Exception as exc:  # ruff: ignore[blind-except] - the probe reports the cause
        return (
            "error",
            f"{type(exc).__name__}: {exc}",
            f"{time.perf_counter() - started:.2f}s",
        )
    return (
        "ok",
        (before, after, count),
        f"{time.perf_counter() - started:.2f}s",
    )


def _compare_completion(
    space, axis: str, value: str, selection: dict[str, str]
) -> tuple[str, str, str, str]:
    """Run one completion against its first working reference."""
    started = time.perf_counter()
    status, payload, wall = _run_one("digits", selection, started)
    if status != "ok":
        return "error", str(payload), "—", wall
    before, after, count = cast("Fingerprint", payload)
    for ref_value in _reference_values(space, axis):
        if ref_value == value:
            continue
        reference = dict(selection, **{axis: ref_value})
        started = time.perf_counter()
        ref_status, ref_payload, ref_wall = _run_one(
            "digits",
            reference,
            started,
            initial=before,
            joint_null=axis == "plasticity",
        )
        if ref_status != "ok":
            continue
        _ref_before, ref_after, ref_count = cast("Fingerprint", ref_payload)
        detail = f"{describe(selection)} vs {ref_value} (pn {count}/{ref_count})"
        verdict = "live" if not same_fingerprint(after, ref_after) else "inert"
        return verdict, detail, ref_value, f"{wall}/{ref_wall}"
    return "error", f"{describe(selection)}: no legal reference", "—", wall


def _probe_value(space, axis: str, value: str) -> tuple[str, str, str, str]:
    """Classify one value; returns verdict, detail, reference, wall."""
    if axis == "geometry" and value == "graph":
        return _probe_graph()
    completions = _completions(space, axis, value)
    if not completions:
        selection = dict(CANONICAL, **{axis: value})
        return (
            "refused",
            _refusal(selection, "digits") or "no declared cell",
            "—",
            "0.00s",
        )

    inert: tuple[str, str, str] | None = None
    errors: list[str] = []
    for cell in completions:
        verdict, detail, reference, wall = _compare_completion(
            space, axis, value, _selection(cell)
        )
        if verdict == "live":
            return verdict, detail, reference, wall
        if verdict == "inert":
            inert = (detail, reference, wall)
        else:
            errors.append(detail)
    if inert is not None:
        return "inert", inert[0], inert[1], inert[2]
    return "error", "; ".join(errors) or "no legal reference", "—", "0.00s"


def _probe_graph() -> tuple[str, str, str, str]:
    selection = dict(CANONICAL, geometry="graph")
    reference = dict(CANONICAL, geometry="feedforward")
    started = time.perf_counter()
    status, payload, wall = _run_one("cora", selection, started)
    if status != "ok":
        return "error", str(payload), "—", wall
    before, after, count = cast("Fingerprint", payload)
    started = time.perf_counter()
    ref_status, ref_payload, ref_wall = _run_one(
        "cora", reference, started, initial=before
    )
    if ref_status != "ok":
        return "error", str(ref_payload), "—", f"{wall}/{ref_wall}"
    _ref_before, ref_after, ref_count = cast("Fingerprint", ref_payload)
    verdict = "live" if not same_fingerprint(after, ref_after) else "inert"
    return verdict, f"cora, pn {count}/{ref_count}", "feedforward", f"{wall}/{ref_wall}"


def main() -> int:
    seed_all_registries()
    space = declared_space("digits")
    names = _axes()
    results: list[tuple[str, str, str, str, str, str]] = []
    print(f"{'axis':11} {'value':24} {'verdict':11} {'wall':13} detail")
    for axis in AXIS_ORDER:
        for value in names[axis]:
            if value == CANONICAL[axis]:
                results.append((axis, value, "reference", "—", "—", "0.00s"))
                continue
            declared_unavailable = not _available(axis, value)
            verdict, detail, reference, wall = _probe_value(space, axis, value)
            if declared_unavailable:
                reason = _unavailable_reason(axis, value) or "declared unavailable"
                if verdict == "inert":
                    verdict, detail = "unavailable", f"inert; {reason}"
                elif verdict == "live":
                    verdict = "stale-unavailable"
                    detail = f"LIVE (reversal trigger fired); {detail}"
            print(f"{axis:11} {value:24} {verdict:11} {wall:13} {detail}")
            results.append((axis, value, verdict, reference, detail, wall))
    counts = Counter(row[2] for row in results)
    print("=" * 80)
    print(f"axis values: {len(results)}; {dict(sorted(counts.items()))}")
    failures = [
        row for row in results if row[2] in {"inert", "stale-unavailable", "error"}
    ]
    if failures:
        print("UNRESOLVED (fix, park, or declare unavailable):")
        for row in failures:
            print(f"  {row[0]}={row[1]} [{row[2]}]: {row[4]}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
