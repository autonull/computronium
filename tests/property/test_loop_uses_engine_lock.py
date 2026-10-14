"""Lock: the loop drives the engine, it does not re-implement it (TODO63 Phase 1).

TODO62 realized the closed loop as a parallel mini-system
(``scripts/continuous_experiment.py``): a ~400-line re-implementation of
proposal, promotion, and reporting, with hardcoded ``KNOWN_GOOD`` seeds and a
``FIX_HINTS`` table. TODO63 retires it and drives the engine that already
exists. This lock is the tripwire: a bespoke proposal/promotion/report path
reappearing beside ``experiment/execution/*`` fails here.

Two claims:

* the loop's entry point (``cli._cmd_loop``) carries none of the retired
  helpers, so the mini-system cannot be reborn inside the CLI;
* the driver calls the engine's own seams — the pipeline, the promotion ladder,
  the baseline registry, and the multi-objective frontier — rather than any
  private duplicate.

Falsifiable by reintroducing ``propose_axes`` / ``merge_top`` / ``FIX_HINTS``
or by having the driver sort cells by ``best_acc`` instead of computing a
Pareto frontier.
"""

from __future__ import annotations

import inspect

from computronium.cli import __main__ as dispatcher
from computronium.experiment.registry import loop as loop_module
from computronium.experiment.surface import cli as surface

# Names the retired parallel mini-system used; each is a re-implementation the
# engine already owns (proposal, promotion, reporting, "known-good" seeds).
_RETIRED = (
    "propose_axes",
    "classify_cycle_log",
    "load_best_from_store",
    "merge_top",
    "FIX_HINTS",
    "KNOWN_GOOD",
)


def test_the_loop_command_drives_the_driver() -> None:
    """``_cmd_loop`` is a wrapper: it constructs and runs ``LoopDriver``."""
    source = inspect.getsource(surface._cmd_loop)
    assert "LoopDriver" in source
    assert "LoopConfig" in source


def test_the_loop_command_carries_none_of_the_retired_helpers() -> None:
    """The mini-system's helpers do not reappear inside the CLI."""
    source = inspect.getsource(surface._cmd_loop)
    present = [name for name in _RETIRED if name in source]
    assert not present, f"retired loop helpers returned to _cmd_loop: {present}"


def test_the_driver_calls_the_engine_seams() -> None:
    """The driver composes the engine; it does not rebuild these stages."""
    source = inspect.getsource(loop_module)
    for seam in (
        "PipelineRunner",
        "promote_with_stats",
        "BaselineRegistry",
        "compute_pareto_frontier",
    ):
        assert seam in source, f"driver does not call the engine seam {seam}"
    present = [name for name in _RETIRED if name in source]
    assert not present, f"retired helpers returned to the driver: {present}"


def test_the_loop_command_is_reachable_through_the_surface() -> None:
    """``comp loop`` is dispatched, so the loop is a command, not a module call."""
    assert "loop" in dispatcher._SUBCOMMANDS
    assert "loop" in dispatcher._SUMMARIES
