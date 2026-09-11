"""``stability`` command-line interface.

Successor to computronium's ``comp stability`` report surface for the
framework-free package capabilities: attach-and-check against a synthetic
linear map, and a quick self-contained ROC calibration over the Ginibre
harvest.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import TYPE_CHECKING

import torch

from stability.calibration import (
    GINIBRE_DIM,
    STATISTIC_KINDS,
    calibrate_ginibre_harvest,
    ginibre_run,
)
from stability.guard import DEFAULT_TAU, StabilityGuard, attach

if TYPE_CHECKING:
    from collections.abc import Sequence


def _cmd_check(args: argparse.Namespace) -> int:
    dim = GINIBRE_DIM
    generator = torch.Generator().manual_seed(args.seed)
    weight = torch.randn(dim, dim, generator=generator) * (args.gain / dim**0.5)

    model = torch.nn.Linear(dim, dim, bias=False)
    with torch.no_grad():
        model.weight.copy_(weight)
    guard = attach(model, threshold=args.tau, window=args.window)

    killed_at: int | None = None
    for step in range(args.steps):
        x = torch.randn(args.batch, dim, generator=generator)
        verdict = guard.check({"x": x}, step=step)
        if verdict.kill:
            killed_at = step
            break

    result = {
        "gain": args.gain,
        "tau": args.tau,
        "killed_at": killed_at,
        "max_statistic": verdict.max_statistic,
    }
    print(json.dumps(result, indent=2))
    return 0 if killed_at is None else 1


def _cmd_calibrate(args: argparse.Namespace) -> int:
    record = calibrate_ginibre_harvest(
        dim=args.dim,
        good_gains=tuple(args.good_gains),
        bad_gains=tuple(args.bad_gains),
        seeds_per_gain=args.seeds,
    )
    print(json.dumps(record.to_dict(), indent=2))
    return 0


def _cmd_statistic(args: argparse.Namespace) -> int:
    transition, state = ginibre_run(args.gain, args.seed, dim=args.dim)
    guard = StabilityGuard(threshold=args.tau, statistic=args.kind, window=args.window)
    value = guard.probe(transition, state, None)  # type: ignore[arg-type]
    decision = guard.decide(value, args.kind)
    print(
        json.dumps(
            {
                "kind": args.kind,
                "statistic": decision.statistic,
                "threshold": decision.threshold,
                "kill": decision.kill,
            },
            indent=2,
        )
    )
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stability", description="Calibrated stability guard CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Attach the guard to a linear map and run")
    check.add_argument("--gain", type=float, default=1.2)
    check.add_argument("--tau", type=float, default=DEFAULT_TAU)
    check.add_argument("--steps", type=int, default=100)
    check.add_argument("--batch", type=int, default=8)
    check.add_argument("--dim", type=int, default=GINIBRE_DIM)
    check.add_argument("--window", type=int, default=10)
    check.add_argument("--seed", type=int, default=0)
    check.set_defaults(func=_cmd_check)

    calib = sub.add_parser("calibrate", help="Quick Ginibre ROC calibration")
    calib.add_argument("--dim", type=int, default=GINIBRE_DIM)
    calib.add_argument("--good-gains", nargs="+", type=float, default=[0.5, 0.7, 0.9])
    calib.add_argument("--bad-gains", nargs="+", type=float, default=[1.1, 1.2, 1.4])
    calib.add_argument("--seeds", type=int, default=3)
    calib.set_defaults(func=_cmd_calibrate)

    stat = sub.add_parser("statistic", help="Probe one statistic on a Ginibre run")
    stat.add_argument("--kind", choices=STATISTIC_KINDS, default="windowed_growth")
    stat.add_argument("--gain", type=float, default=1.2)
    stat.add_argument("--tau", type=float, default=DEFAULT_TAU)
    stat.add_argument("--window", type=int, default=10)
    stat.add_argument("--dim", type=int, default=GINIBRE_DIM)
    stat.add_argument("--seed", type=int, default=0)
    stat.set_defaults(func=_cmd_statistic)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
