"""``comp continuous`` — the budgeted burst runner (TODO29 Phase 3).

Continuous discovery in time-boxed bursts: each burst samples viable grid
cells through the stratified driver, harvests gate rejections as structural
voids and runtime crashes as quarantined defects, and flushes the KB per
cell — every burst is resume-safe by construction.

Single-daemon assumption: do not point two bursts at one ``--root``
(SQLite write contention).

Usage::

    comp continuous --budget 5m --root artifacts/broad_map --credit-trace
    comp continuous --target-cells 100 --loop --sleep 10
    comp continuous unquarantine --defect a1b2c3d4e5f6 --root artifacts/broad_map
"""

from __future__ import annotations

import argparse
import logging
import signal
import time
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.autoscientist.broad_map import (
    BroadMappingCampaign,
    budget_from_args,
    build_sweep,
    driver_seeded_kb,
    run_burst,
    run_deep_tier,
    run_l1_maturation,
)
from computronium.autoscientist.defects import resolve_defect
from computronium.utils import seed_everything

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger("continuous")

_DEFECTS_NAME = "runtime_defects.jsonl"


def _add_common_flags(parser: argparse.ArgumentParser) -> None:
    """Flags shared by ``comp continuous`` and ``comp daemon``."""
    parser.add_argument(
        "--budget",
        type=str,
        default=None,
        help="soft time cap per burst (e.g. 5m, 90s, 1h)",
    )
    parser.add_argument(
        "--target-cells", type=int, default=None, help="hard cap on completed cells"
    )
    parser.add_argument(
        "--objectives",
        type=str,
        default="accuracy,walltime_s",
        help="comma-separated objectives for multi-objective optimization "
        "(e.g. accuracy,walltime_s,param_count). "
        "Available: accuracy, walltime_s, param_count, flops, memory_mb, "
        "energy_per_step, latency_ms, bp_deficit, ruler_walltime_ratio, "
        "ruler_energy_ratio, spectral_radius, lyapunov_exponent, "
        "max_singular_value, psi_capacity, consolidation_cost, rewrite_rate, "
        "credit_alignment, feedback_path_length, trace_variance",
    )
    parser.add_argument(
        "--maturation",
        type=int,
        default=0,
        help="reserve up to N cells of each burst for an epochs=3 promotion re-run (maturity:l1)",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="run bursts forever (fresh budget per burst) instead of one burst",
    )
    parser.add_argument(
        "--sleep", type=float, default=10.0, help="seconds between --loop bursts"
    )
    parser.add_argument("--root", type=Path, default=Path("artifacts/broad_map"))
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="also tee the burst log here (the comp dashboard ticker reads it)",
    )
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--cells-per-iter", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--task", default="mnist")
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--param-budget", type=int, default=25000)
    parser.add_argument(
        "--limit-batches",
        type=int,
        default=0,
        help="cap training batches per epoch (0 = full epoch); shorter cells "
        "trade per-cell fidelity for coverage — right for L0 mapping",
    )
    parser.add_argument(
        "--credit-trace",
        action="store_true",
        help="capture per-cell BP-gradient alignment (adds settle overhead per cell)",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="comp continuous", description=__doc__)
    _add_common_flags(parser)
    sub = parser.add_subparsers(dest="command")
    unquarantine = sub.add_parser(
        "unquarantine", help="release cells quarantined by a resolved defect"
    )
    unquarantine.add_argument("--defect", required=True, help="defect id (sha256[:12])")
    unquarantine.add_argument("--root", type=Path, default=Path("artifacts/broad_map"))
    deep_tier = sub.add_parser(
        "deep-tier",
        help="promote front-stable cells to claim-grade L2 re-runs (seeds × epochs)",
    )
    deep_tier.add_argument("--top", type=int, default=5, help="max cells to promote")
    deep_tier.add_argument("--epochs", type=int, default=10, help="epochs per L2 run")
    deep_tier.add_argument("--seeds", type=int, default=3, help="fresh seeds per cell")
    deep_tier.add_argument("--task", default=None, help="filter candidates by task")
    deep_tier.add_argument("--root", type=Path, default=Path("artifacts/broad_map"))
    deep_tier.add_argument(
        "--seed", type=int, default=20260915, help="base seed (seed i = base + i)"
    )
    deep_tier.add_argument(
        "--dry-run",
        action="store_true",
        help="show the promotion plan without executing",
    )
    return parser


def _burst_once(args: argparse.Namespace, campaign, driver) -> str:
    summary = run_burst(
        campaign,
        driver,
        budget_from_args(args),
        max_iterations=args.max_iterations,
    )
    return str(summary["stop_reason"])


def _loop_bursts(args: argparse.Namespace, campaign, driver) -> None:
    while True:
        summary = _burst_once(args, campaign, driver)
        if summary == "exhausted":
            logger.info("Grid exhausted: continuous loop ends.")
            return
        logger.info("Sleeping %.0fs until the next burst", args.sleep)
        time.sleep(args.sleep)


def _install_sigterm(handler: Callable[[], object] | None = None) -> None:
    def _terminate(signum: int, frame: object) -> None:
        if handler is not None:
            handler()
            return
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _terminate)


def _run_forever(args: argparse.Namespace, campaign, driver) -> int:  # noqa: ANN001 (internal, typed by build_sweep)
    _install_sigterm()
    try:
        _loop_bursts(args, campaign, driver)
    except KeyboardInterrupt, SystemExit:
        # Graceful flush path — never a finally block (PEP 765). The KB is
        # flushed per cell and the last burst checkpointed on stop.
        logger.info("Interrupted: state flushed; resume with the same --root.")
    return 0


def _tee_log(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )
    # Root handler: modules log under computronium.* names; named
    # loggers ("broad_map") would never see them.
    logging.getLogger().addHandler(handler)


def _burst(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO)
    _install_sigterm()
    if args.log_path is not None:
        _tee_log(args.log_path)
    try:
        _run_burst(args)
    except KeyboardInterrupt, SystemExit:
        logger.info("Interrupted: state flushed; resume with the same --root.")
    return 0


def _run_burst(args: argparse.Namespace) -> None:
    (args.root / "campaign").mkdir(parents=True, exist_ok=True)
    seed_everything(args.seed, deterministic=False)
    campaign, driver = build_sweep(args)
    if args.loop:
        _run_forever(args, campaign, driver)
        return
    run_burst(
        campaign, driver, budget_from_args(args), max_iterations=args.max_iterations
    )
    if args.maturation:
        run_l1_maturation(args, campaign, driver.burst_tag)


def _deep_tier(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO)
    root: Path = args.root
    from computronium.autoscientist.objectives import parse_objectives

    obj_spec = getattr(args, "objectives", "accuracy,walltime_s")
    objectives = parse_objectives(obj_spec)
    if args.dry_run:
        from computronium.autoscientist.broad_map import _deep_tier_candidates

        plan = _deep_tier_candidates(root / "kb.sqlite", args.top, args.task, objectives=objectives)
        for candidate in plan:
            print(
                f"{candidate.key}  acc={candidate.accuracy:.3f}  "
                f"front_bursts={candidate.front_bursts}  "
                f"planned: {args.seeds} seeds × {args.epochs} epochs"
            )
        print(f"{len(plan)} candidate(s); {len(plan) * args.seeds} CEEC experiments")
        return 0
    campaign = BroadMappingCampaign(
        knowledge_base=driver_seeded_kb(root / "kb.sqlite"),
        output_dir=str(root / "campaign"),
        db_path=root / "campaign" / "campaign.db",
        branch_name="deep_tier",
        ceec_ledger_path=root / "ledger.sqlite",
        voids_path=root / "structural_voids.jsonl",
        defects_path=root / "runtime_defects.jsonl",
    )
    (root / "campaign").mkdir(parents=True, exist_ok=True)
    rows = run_deep_tier(
        root,
        campaign,
        task=args.task,
        top=args.top,
        epochs=args.epochs,
        seeds=args.seeds,
        seed=args.seed,
        objectives=objectives,
    )
    print(f"deep-tier: {len(rows)} claim-grade row(s) in {root / 'maturation.jsonl'}")
    return 0


def _unquarantine(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO)
    resolved = resolve_defect(args.root / _DEFECTS_NAME, args.defect)
    if resolved == 0:
        print(f"defect {args.defect} not found (or already resolved)", flush=True)
        return 1
    print(f"defect {args.defect} resolved; affected cells re-open for the next burst")
    return 0


def main() -> int:
    args = _build_parser().parse_args()
    if args.command == "unquarantine":
        return _unquarantine(args)
    if args.command == "deep-tier":
        return _deep_tier(args)
    return _burst(args)


if __name__ == "__main__":
    raise SystemExit(main())
