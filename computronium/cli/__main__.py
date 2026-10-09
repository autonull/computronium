"""Computronium CLI dispatcher (``comp``).

Single public command surface over the Kernel and Library adapters. Every top-level
command maps to one module ``main``; the console-script table in
``pyproject.toml`` points at this entry point so the public API boundary stays
one place.

Usage::

        comp <command> [args]

    where ``command`` is a parity/repro/validate/benchmark adapter or one of
    the kernel surface's own subcommands (``run``, ``report``, ``export``,
    ``conformance``, ``status``), promoted to the top level so a run is one
    command rather than two.
"""

from __future__ import annotations

import argparse
import sys
import warnings
from typing import TYPE_CHECKING

# Suppress informational UserWarnings (geometry/substrate hints, etc.)
warnings.filterwarnings("ignore", category=UserWarning)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_SURFACE = "computronium.experiment.surface.cli"

# command -> (module, attribute, argv prefix). Resolved lazily to keep the
# import graph shallow: the dispatcher itself must not drag in the zoo/execution
# layer. The surface's own subcommands are promoted with their name as the
# prefix, so ``comp run`` and ``comp run run`` reach the same parser and there
# is no second command tree to keep in step.
_SUBCOMMANDS: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "run": (_SURFACE, "main", ("run",)),
    "report": (_SURFACE, "main", ("report",)),
    "export": (_SURFACE, "main", ("export",)),
    "import": (_SURFACE, "main", ("import",)),
    "conformance": (_SURFACE, "main", ("conformance",)),
    "status": (_SURFACE, "main", ("status",)),
    "gallery": (_SURFACE, "main", ("gallery",)),
    "hypothesis-campaign": (_SURFACE, "main", ("hypothesis-campaign",)),
    "stability-plasticity": (_SURFACE, "main", ("stability-plasticity",)),
    "frozen-theta-psi": (_SURFACE, "main", ("frozen-theta-psi",)),
    "parity": ("computronium.cli.parity", "main", ()),
    "repro": (_SURFACE, "main", ("repro",)),
    "validate": ("computronium.cli.validate", "main", ()),
    "joint-validate": ("computronium.cli.joint_validate", "main", ()),
    "benchmark": ("computronium.cli.benchmark", "main", ()),
    "stats": (_SURFACE, "main", ("stats",)),
    "pareto": (_SURFACE, "main", ("pareto",)),
    "diff": (_SURFACE, "main", ("diff",)),
    "campaign": (_SURFACE, "main", ("campaign",)),
    "schema": (_SURFACE, "main", ("schema",)),
    "power-analysis": (_SURFACE, "main", ("power-analysis",)),
    "stability-analysis": (_SURFACE, "main", ("stability-analysis",)),
}

_SUMMARIES: dict[str, str] = {
    "run": "Execute a run profile (dry-run with --dry-run)",
    "report": "Generate report from store",
    "export": "Export store data for round-trip",
    "import": "Import store data from export (round-trip)",
    "conformance": "Check capability conformance",
    "status": "Show run/store status",
    "gallery": "Render gallery figures from demo records",
    "hypothesis-campaign": "Run hypothesis templates over campaign records",
    "stability-plasticity": "Generate and run stability-plasticity frontier campaign",
    "frozen-theta-psi": "Run frozen-θ ψ benchmarks at scale (multi-substrate, multi-plasticity)",
    "parity": "Check library-vs-kernel parity for an axis",
    "repro": "Replay a recorded run and diff it",
    "validate": "Validate a config or record against the schema",
    "joint-validate": "Validate a composed multi-axis system",
    "benchmark": "Run kernel benchmarks and emit a verdict",
    "stats": "Compute summary statistics for run metrics (machine-readable)",
    "pareto": "Export Pareto frontier for plotting (machine-readable)",
    "diff": "Statistical run comparison with effect sizes",
    "campaign": "Run declarative multi-run YAML campaigns",
    "schema": "Dump JSON schemas for RunSpec/Coordinate/Objectives",
    "power-analysis": "Compute statistical power for experiment design (machine-readable)",
    "stability-analysis": "Run dynamical stability analysis "
    "(Lyapunov spectra, basin stability, settling trajectories)",
}


def _build_parser() -> argparse.ArgumentParser:
    """Build the top-level help tree.

    Returns:
        Parser whose subparsers mirror :data:`_SUBCOMMANDS`; each subcommand
        forwards its remainder to the owning module's parser.
    """
    parser = argparse.ArgumentParser(
        prog="comp",
        description="Computronium — experiment surface over the Kernel and Library.",
        epilog="Run 'comp <command> --help' for that command's own options.",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    for name in _SUBCOMMANDS:
        sub.add_parser(name, help=_SUMMARIES[name], add_help=False)
    return parser


def _load(command: str) -> Callable[[], int]:
    module_name, attr, _ = _SUBCOMMANDS[command]
    module = __import__(module_name, fromlist=[attr])
    return getattr(module, attr)


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch to the sub-command's module ``main``.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``). The first element
            selects the command; the remainder are forwarded unchanged so each
            adapter parses its own flags.

    Returns:
        The adapter's exit code (``0`` when it returns ``None``).
    """
    # Use threading backend for joblib to avoid loky semaphore leaks
    # This must be done before any joblib.Parallel usage (e.g., in sklearn)
    import joblib

    joblib.parallel.DEFAULT_BACKEND = "threading"

    args = list(sys.argv[1:] if argv is None else argv)
    parser = _build_parser()
    if not args:
        parser.print_help(sys.stderr)
        return 1
    if args[0] in {"-h", "--help"}:
        parser.print_help()
        return 0

    command, rest = args[0], args[1:]
    if command not in _SUBCOMMANDS:
        print(
            f"comp: unknown command {command!r}",
            file=sys.stderr,
        )
        parser.print_usage(sys.stderr)
        return 2

    # Each adapter's argparse reads sys.argv[1:] when called with no explicit
    # argv, so rewrite it to look like the command was invoked directly — with
    # the promoted surface subcommand's own name in front of the remainder.
    prefix = _SUBCOMMANDS[command][2]
    sys.argv = [f"comp {command}", *prefix, *rest]
    try:
        return int(_load(command)() or 0)
    except SystemExit as exc:
        return int(exc.code or 0)
    finally:
        # Shutdown joblib's reusable loky executor to avoid semaphore leaks
        try:
            from joblib.externals.loky import get_reusable_executor

            executor = get_reusable_executor()
            executor.shutdown(wait=True)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
