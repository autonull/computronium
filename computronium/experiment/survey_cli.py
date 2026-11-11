"""The survey entry point: one CLI for both experiment engines.

``LearningSurvey`` and ``SimpleSurvey`` share a spec builder, evaluator, wave
executor, store and report; only the planner differs. Their CLIs differed by
copy-paste, so this module owns the one argument surface, the one banner and
the one post-run check. Bash wrappers are gone: every branch that used to live
in shell (device resolution, store defaults, budget arithmetic) is now typed
Python.
"""

from __future__ import annotations

import os
import sys


def _disable_cuda_for_cpu(argv: list[str]) -> None:
    """Hide CUDA before any torch import when the caller asked for CPU."""
    if "--device" not in argv:
        return
    try:
        index = argv.index("--device")
    except ValueError:
        return
    if index + 1 < len(argv) and argv[index + 1] == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""


_disable_cuda_for_cpu(sys.argv[1:])

import argparse  # ruff: ignore[module-import-not-at-top-of-file]
import json  # ruff: ignore[module-import-not-at-top-of-file]
import logging  # ruff: ignore[module-import-not-at-top-of-file]
from pathlib import Path  # ruff: ignore[module-import-not-at-top-of-file]
from typing import Any  # ruff: ignore[module-import-not-at-top-of-file]

from computronium.core.logging import get_logger  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.core.utils.device import get_device  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.learning_survey import run_learning_survey  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.simple_survey import run_simple_survey  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.wave import (  # ruff: ignore[module-import-not-at-top-of-file]
    CostModel,
    _axis_overrides,
    _default_store_path,
    _format_error,
    _pretty_print_dry_run,
    _run_self_test,
)

logger = get_logger(__name__)

ENGINES = {"learn": "LearningSurvey (PolicyPlanner)", "static": "SimpleSurvey"}
POLICIES = ("tpe", "nsga2", "random")
LADDER_SEEDS = {"L0": 1, "L1": 3, "L2": 5}
LADDER_EPOCHS = {"L0": 1, "L1": 5, "L2": 20}
LADDER_SPLIT = {"L0": 0.6, "L1": 0.3, "L2": 0.1}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="survey",
        description="Run a LearningSurvey (adaptive) or SimpleSurvey (static) experiment.",
    )
    parser.add_argument(
        "hours",
        type=float,
        nargs="?",
        help="Time budget in hours (required unless --doctor)",
    )
    parser.add_argument(
        "--mode",
        choices=ENGINES,
        default="learn",
        help="Engine: learn (policy-driven) or static (fixed plan)",
    )
    parser.add_argument("--fidelity", default="L0", choices=["L0", "L1", "L2"])
    parser.add_argument("--tasks", default="", help="Comma-separated task names")
    parser.add_argument(
        "--store",
        default=None,
        help="DuckDB store path (default: experiments/experiment_<ts>.duckdb)",
    )
    parser.add_argument("--promote-from", default=None)
    parser.add_argument("--promote-top", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--dry-run-format", choices=["json", "table", "summary"], default="table"
    )
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--param-budget", type=int, default=0)
    parser.add_argument(
        "--n-seeds", type=int, default=None, help="Seeds per cell (default: ladder)"
    )
    parser.add_argument(
        "--epochs", type=int, default=None, help="Epochs per cell (default: ladder)"
    )
    parser.add_argument("--batch-limit", type=int, default=0)
    parser.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="Cells evaluated concurrently within a wave (1 = serial)",
    )
    parser.add_argument(
        "--log-steps",
        type=int,
        default=0,
        help="Trainer steps between progress logs (0 = epoch only)",
    )
    parser.add_argument("--axes", default="", help="JSON: axis -> [primitives]")
    parser.add_argument(
        "--digital", action="store_true", help="Restrict to digital substrate only"
    )
    parser.add_argument("--hyperparameters", default="", help="JSON: hyperparameters")
    parser.add_argument("--objectives", default="", help="Comma-separated objectives")
    parser.add_argument(
        "--axis-objectives", default="", help="JSON: axis -> [objectives]"
    )
    parser.add_argument("--policy", default="tpe", choices=POLICIES)
    parser.add_argument(
        "--ladder", action="store_true", help="Run L0 -> L1 -> L2 in one invocation"
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--quiet", "-q", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--doctor", action="store_true")
    return parser


def _banner(args: argparse.Namespace, device: str, store_path: str) -> None:
    depth = f"fixed ({args.fidelity})"
    if args.ladder:
        depth = "fidelity ladder (L0=1x1, L1=3x5, L2=5x20)"
    elif args.n_seeds is not None or args.epochs is not None:
        depth = (
            f"fixed ({args.fidelity}, n_seeds={args.n_seeds or 'ladder'}, "
            f"epochs={args.epochs or 'ladder'})"
        )
    sampler = args.policy if args.mode == "learn" else "N/A"
    print("=" * 64)
    print(f"  Survey :: {ENGINES[args.mode]}")
    print("=" * 64)
    print(f"  Sampler:      {sampler}")
    print(f"  Depth:        {depth}")
    print(f"  Time limit:   {args.hours:g} hour(s)")
    print(f"  Store:        {store_path}")
    print(f"  Device:       {device} (resolved from {args.device})")
    print(f"  Seed:         {args.seed}")
    if args.tasks:
        print(f"  Tasks:        {args.tasks}")
    for flag in ("promote_from", "ladder", "resume", "dry_run"):
        value = getattr(args, flag)
        if value:
            print(f"  {flag.replace('_', ' ').title():<13} {value}")
    if args.max_workers > 1:
        print(f"  {'Max workers':<13} {args.max_workers}")
    if args.log_steps:
        print(f"  {'Log steps':<13} {args.log_steps}")
    print("=" * 64)
    print()


def _print_ladder_dry_run(result: dict[str, Any], hours: float) -> None:
    cells = result.get("cells", [])
    split = result.get("budget_split", LADDER_SPLIT)
    print("\n=== Ladder Dry-Run ===")
    print(
        f"Budget: {hours:g}h ({int(hours * 3600)}s) | Tasks: "
        f"{', '.join(result.get('tasks', []))}"
    )
    print(
        f"Split: L0={split.get('L0', 0.6) * 100:.0f}% "
        f"L1={split.get('L1', 0.3) * 100:.0f}% L2={split.get('L2', 0.1) * 100:.0f}%"
    )
    for fidelity in ("L0", "L1", "L2"):
        count = max(1, int(result.get("n", 0) * split.get(fidelity, 0.0)))
        print(
            f"--- {fidelity} ({count} cells, n_seeds={LADDER_SEEDS[fidelity]}, "
            f"epochs={LADDER_EPOCHS[fidelity]}) ---"
        )
        for index, (coord, _schedule) in enumerate(cells[:5], 1):
            print(
                f"  {index}  {coord.substrate:<15} {coord.geometry:<15} "
                f"{coord.dynamics:<20} {coord.plasticity:<15} "
                f"{coord.credit:<20} {coord.update:<15}"
            )
        if count > 5:
            print(f"  ... {count - 5} more cells")


def _print_dry_run(result: dict[str, Any], args: argparse.Namespace) -> None:
    if args.dry_run_format == "json":
        print(json.dumps(result, default=str, indent=2))
        return
    if args.dry_run_format == "summary":
        model: CostModel = result["model"]
        n = result.get("n", 0)
        total = model.startup_s + n * model.cost_per_cell_s
        split = result.get("budget_split")
        split_text = (
            f" | split: L0={split.get('L0', 0.6) * 100:.0f}% "
            f"L1={split.get('L1', 0.3) * 100:.0f}% L2={split.get('L2', 0.1) * 100:.0f}%"
            if split
            else ""
        )
        print(
            f"Dry-run: {n} cells | {args.fidelity} | "
            f"{', '.join(result.get('tasks', []))} | "
            f"~{model.cost_per_cell_s:.1f}s/cell ({model.source}) | "
            f"~{total:.0f}s total{split_text}"
        )
        return
    if args.mode == "learn" and result.get("ladder"):
        _print_ladder_dry_run(result, args.hours)
        return
    _pretty_print_dry_run(
        result, hours=args.hours, fidelity=args.fidelity, model=result["model"]
    )


def _manifest_summary(store_path: str) -> dict[str, Any]:
    """The run manifest written at close, or an empty dict if there is none."""
    manifest_path = Path(store_path).with_suffix(".run.json")
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {}


def _post_run_checks(store_path: str, hours: float) -> None:
    """Report where the evidence is and whether the budget was spent."""
    print("\nPost-run analysis:")
    for command in (
        f"uv run comp coverage report --store {store_path}",
        f"uv run comp report --store {store_path} --format text",
        f"uv run comp dashboard --store {store_path}",
    ):
        print(f"  {command}")

    manifest = _manifest_summary(store_path)
    if not manifest:
        return
    walltime = float(manifest.get("walltime_s") or 0.0)
    budget = hours * 3600
    if budget > 0 and walltime < 0.8 * budget:
        print(f"  warning: walltime {walltime:.0f}s < 80% of budget {budget:.0f}s")
    planned = int(manifest.get("cells_planned") or 0)
    measured = int(manifest.get("cells_evaluated") or 0)
    if planned > 0 and measured < 0.8 * planned:
        print(f"  warning: measured {measured} cells < 80% of planned {planned}")


def _hint(error: str) -> str | None:
    lowered = error.lower()
    match True:
        case _ if "cuda" in lowered:
            return "Try --device cpu or export CUDA_VISIBLE_DEVICES=''"
        case _ if "search space" in lowered or "no cells" in lowered:
            return "Try --fidelity L0 --device cpu, or check --axes constraints"
        case _ if "import" in lowered or "module" in lowered:
            return "Run: uv sync --dev --all-extras"
        case _ if "permission" in lowered:
            return "Check file permissions for the store path"
        case _ if "no space" in lowered or "disk" in lowered:
            return "Free disk space or use --store with a different path"
    return None


def _run_doctor() -> int:
    from computronium.experiment.environment.diagnostics import (
        print_diagnostics,
        run_diagnostics,
    )

    print_diagnostics(run_diagnostics(device="cpu", hours=0.001))
    return 0


def _resolve_device(device: str) -> str:
    resolved = get_device(device).type
    if resolved == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
    return resolved


def _dispatch(
    args: argparse.Namespace,
    *,
    device: str,
    store_path: str,
    verbose: bool,
    tasks: list[str] | None,
    axes: dict[str, tuple[str, ...]] | None,
    hyperparameters: dict[str, Any] | None,
    objectives: tuple[str, ...],
    axis_objectives: dict[str, tuple[str, ...]] | None,
) -> dict[str, Any]:
    """Run the engine the CLI asked for; both accept the same core arguments."""
    common: dict[str, Any] = {
        "hours": args.hours,
        "fidelity": args.fidelity,
        "tasks": tasks,
        "store_path": store_path,
        "promote_from": args.promote_from,
        "promote_top": args.promote_top,
        "seed": args.seed,
        "dry_run": args.dry_run,
        "device": device,
        "param_budget": args.param_budget,
        "n_seeds": args.n_seeds,
        "epochs": args.epochs,
        "batch_limit": args.batch_limit,
        "axes": axes,
        "hyperparameters": hyperparameters,
        "objectives": objectives,
        "verbose": verbose,
        "cpu_threads": 1,
        "resume": args.resume,
        "ladder": args.ladder,
        "policy": args.policy,
        "max_workers": args.max_workers,
        "log_steps": args.log_steps,
    }
    if args.mode == "learn":
        return run_learning_survey(**common, axis_objectives=axis_objectives)
    return run_simple_survey(**common)


def _report(result: dict[str, Any], args: argparse.Namespace, store_path: str) -> None:
    """Render a dry-run preview, or the run result plus its post-run checks."""
    if args.dry_run:
        _print_dry_run(result, args)
        return
    print(json.dumps(result, default=str, indent=2))
    _post_run_checks(store_path, args.hours)


def main(argv: list[str] | None = None) -> None:
    """Parse one argument surface and dispatch to the chosen engine."""
    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)

    args = _parser().parse_args(argv)

    if args.doctor:
        sys.exit(_run_doctor())
    if args.hours is None:
        print("Error: hours argument required (unless --doctor)", file=sys.stderr)
        sys.exit(2)

    device = _resolve_device(args.device)
    # Auto-limit max_workers for CUDA to avoid GPU contention
    if device.startswith("cuda") and args.max_workers > 1:
        logger.warning(
            "max_workers=%d on CUDA device causes severe GPU contention; "
            "limiting to 1. Use --max-workers=1 explicitly if intentional.",
            args.max_workers,
        )
        args.max_workers = 1
    if args.self_test and not _run_self_test(device):
        print(_format_error("Self-test failed", "Try --device cpu"), file=sys.stderr)
        sys.exit(1)

    store_path = args.store or _default_store_path()
    verbose = args.verbose or (not args.quiet and sys.stdout.isatty())
    tasks = args.tasks.split(",") if args.tasks else None
    axes = _axis_overrides(args.axes, digital=args.digital)
    hyperparameters = json.loads(args.hyperparameters) if args.hyperparameters else None
    objectives = tuple(args.objectives.split(",")) if args.objectives else ()
    axis_objectives = json.loads(args.axis_objectives) if args.axis_objectives else None

    _banner(args, device, store_path)

    try:
        result = _dispatch(
            args,
            device=device,
            store_path=store_path,
            verbose=verbose,
            tasks=tasks,
            axes=axes,
            hyperparameters=hyperparameters,
            objectives=objectives,
            axis_objectives=axis_objectives,
        )
        _report(result, args, store_path)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as exc:  # ruff: ignore[blind-except] - CLI boundary renders every failure
        print(_format_error(str(exc), _hint(str(exc))), file=sys.stderr)
        if verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
