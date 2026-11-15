"""TODO92 §3.10 rung 0: which live substrate can carry the credit × substrate 2×2?

The interaction is `(PEPITA − gradient)_substrate − (PEPITA − gradient)_digital`
on feedforward geometry, where PEPITA is legal. Before spending the claim-grade
run, each candidate substrate needs the AGENTS viability gate's first questions
answered cheaply:

1. does the cell compose at all (a declared legal completion);
2. does the credit move the parameters (a non-zero update); and
3. does the substrate change the computation the credit drives? A substrate
   that returns the digital cell bit-for-bit makes the 2×2 mechanically zero — a
   defect/refusal, not a null result.

Method: one seeded ``train_step`` at the digits task shape, fingerprinting the
post-step geometry parameters (the §3.9 ruler). Every arm starts from the same
pre-step weights, copied from the digital baseline, so differences are the
substrate's or the credit's. ``complex`` is excluded by
``complex_substrate_real_compute``; ``neuromorphic`` refuses instantaneous
dynamics (``neuromorphic_substrate_dynamics``), so it is probed against a
``digital + energy_minimization`` baseline and reported with that baseline.

A substrate passing rung 0 is a *candidate* for the 2×2, not a result: the
viability ladder (3-point primary knob, one confirmation seed) and the
pre-registered n≥5 interaction remain.

Run: uv run python scripts/probes/t92_credit_substrate_rung0.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import torch

from computronium.experiment.evidence.liveness import (
    CANONICAL,
    one_step_fingerprint,
    same_fingerprint,
)
from computronium.experiment.schema.seed_registries import seed_all_registries

__all__ = ["main"]

TASK = "digits"
CREDIT = "pepita"
SUBSTRATES: tuple[tuple[str, str], ...] = (
    ("digital", "instantaneous"),
    ("analog", "instantaneous"),
    ("memristive", "instantaneous"),
    ("optical", "instantaneous"),
    ("quantum", "instantaneous"),
    ("sparse", "instantaneous"),
    ("ternary", "instantaneous"),
    ("neuromorphic", "energy_minimization"),
)


@dataclass(frozen=True, slots=True)
class Arm:
    """One one-step measurement."""

    outcome: str
    detail: str
    wall_s: float


@dataclass(frozen=True, slots=True)
class Baseline:
    """The digital cell a substrate row is compared against."""

    initial: dict[str, torch.Tensor]
    gradient: dict[str, torch.Tensor]
    pepita: dict[str, torch.Tensor]


def _delta(before: dict[str, torch.Tensor], after: dict[str, torch.Tensor]) -> float:
    return max((after[name] - before[name]).abs().max().item() for name in before)


def _arm(
    selection: dict[str, str], initial=None
) -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor], Arm]:
    started = time.perf_counter()
    try:
        before, after, _count = one_step_fingerprint(TASK, selection, initial=initial)
    except Exception as exc:  # ruff: ignore[blind-except] - the probe reports the cause
        return (
            {},
            {},
            Arm("error", f"{type(exc).__name__}: {exc}", time.perf_counter() - started),
        )
    moved = _delta(before, after)
    finite = all(torch.isfinite(t).all().item() for t in after.values())
    outcome = "ok" if finite and moved > 0.0 else "inert"
    return (
        before,
        after,
        Arm(
            outcome,
            f"delta={moved:.3e} finite={finite}",
            time.perf_counter() - started,
        ),
    )


def _digital_baseline(dynamics: str) -> Baseline | None:
    selection = dict(CANONICAL, dynamics=dynamics)
    before, after_gradient, gradient = _arm(selection)
    if gradient.outcome != "ok":
        return None
    _same, after_pepita, pepita = _arm(dict(selection, credit=CREDIT), initial=before)
    if pepita.outcome != "ok":
        return None
    return Baseline(before, after_gradient, after_pepita)


def _probe_row(
    substrate: str, dynamics: str, baseline: Baseline
) -> tuple[str, bool, bool]:
    selection = dict(CANONICAL, substrate=substrate, dynamics=dynamics)
    _before, after_gradient, gradient = _arm(selection, initial=baseline.initial)
    if gradient.outcome != "ok":
        return f"gradient: {gradient.outcome} ({gradient.detail})", False, False
    _same, after_pepita, pepita = _arm(
        dict(selection, credit=CREDIT), initial=baseline.initial
    )
    if pepita.outcome != "ok":
        return f"{CREDIT}: {pepita.outcome} ({pepita.detail})", False, False
    credit_live = not same_fingerprint(after_pepita, after_gradient)
    substrate_live = not same_fingerprint(after_pepita, baseline.pepita)
    substrate_delta = max(
        (after_pepita[name] - baseline.pepita[name]).abs().max().item()
        for name in baseline.pepita
    )
    detail = (
        f"gradient {gradient.detail} ({gradient.wall_s:.2f}s); "
        f"{CREDIT} {pepita.detail} ({pepita.wall_s:.2f}s); "
        f"credit {'LIVE' if credit_live else 'INERT'}; "
        f"substrate {'LIVE' if substrate_live else 'INERT'} "
        f"(vs digital {substrate_delta:.3e})"
    )
    return detail, credit_live, substrate_live


def main() -> int:
    seed_all_registries()
    baselines = {
        dynamics: _digital_baseline(dynamics)
        for dynamics in ("instantaneous", "energy_minimization")
    }
    if any(baseline is None for baseline in baselines.values()):
        print(f"digital baseline failed: {baselines}")
        return 1
    print(f"{'substrate':14} {'dynamics':21} outcome")
    candidates: list[str] = []
    for substrate, dynamics in SUBSTRATES:
        baseline = baselines[dynamics]
        assert baseline is not None  # checked above
        started = time.perf_counter()
        detail, credit_live, substrate_live = _probe_row(substrate, dynamics, baseline)
        wall = time.perf_counter() - started
        print(f"{substrate:14} {dynamics:21} {detail}  [{wall:.2f}s]")
        if credit_live and substrate_live:
            candidates.append(substrate)
    print("=" * 100)
    print(f"candidates for the 2x2: {candidates or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
