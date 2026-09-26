"""The settle-loop driver is the only place a settle loop may be written.

TODO34 §5.1 collapsed ten hand-written ``for step in range(max_steps)`` loops
across six dynamics classes into one driver. The duplication was the bug
factory: the dead-early-stop defect of ``ff6528fb`` existed in four of those
copies at once, because it travelled with the copy-paste.

Two claims are tested here:

* the driver's *semantics* — horizon, early stop, executed-step count — since
  the driver is now load-bearing for every dynamics class, and
* the *uniqueness* of the driver — an AST scan over the dynamics package that
  fails if a new loop is written by hand. A lock that only checks behaviour
  cannot stop the duplication returning; this is the same shape as the
  geometry wiring lock corrected in ``ff6528fb`` (§0.6): assert against the
  code that exists, never against a hand-maintained list.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import cast

from computronium.ontology.dynamics._settle_driver import (
    SettleIterate,
    checkpointed_every,
    run_settle_loop,
)

PACKAGE = Path(__file__).resolve().parents[2] / "computronium" / "ontology" / "dynamics"
DRIVER = "_settle_driver.py"


def _horizon_loops(path: Path) -> list[int]:
    """Line numbers of loops iterating a settle horizon, by AST."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    loops = [
        (node.lineno, node.iter if isinstance(node, ast.For) else node.test)
        for node in ast.walk(tree)
        if isinstance(node, ast.For | ast.While)
    ]
    return [
        lineno
        for lineno, iterable in loops
        if any(
            (isinstance(child, ast.Attribute) and child.attr == "max_steps")
            or (isinstance(child, ast.Name) and child.id == "max_steps")
            for child in ast.walk(iterable)
        )
    ]


class TestRunSettleLoop:
    """Horizon and early-stop semantics, independent of any dynamics class."""

    def test_runs_the_full_horizon_without_an_observer(self) -> None:
        seen: list[int] = []
        assert run_settle_loop(seen.append, max_steps=5) == 5
        assert seen == [0, 1, 2, 3, 4]

    def test_observer_stops_the_loop_and_counts_executed_steps(self) -> None:
        seen: list[int] = []
        steps = run_settle_loop(seen.append, max_steps=10, after_step=lambda s: s >= 2)
        assert steps == 3
        assert seen == [0, 1, 2]

    def test_step_runs_before_the_observer_may_stop_it(self) -> None:
        """The 0.2 defect, restated: nothing may be consulted in place of
        the step itself, or a settle silently becomes a single pass."""
        order: list[str] = []
        run_settle_loop(
            lambda s: order.append(f"step{s}"),
            max_steps=2,
            after_step=lambda s: order.append(f"observe{s}") or True,
        )
        assert order == ["step0", "observe0"]

    def test_zero_horizon_executes_nothing(self) -> None:
        seen: list[int] = []
        assert run_settle_loop(seen.append, max_steps=0) == 0
        assert seen == []


class TestSettleIterate:
    def test_carries_the_rebound_value(self) -> None:
        box: SettleIterate[int] = SettleIterate(1)
        box.value = 2
        assert box.value == 2


class TestCheckpointedEvery:
    def test_skips_step_zero_and_wraps_the_rest(self, monkeypatch) -> None:
        from torch.utils import checkpoint

        calls: list[int] = []

        def _fake(fn, *args, use_reentrant):
            calls.append(args[0])
            return fn(*args)

        monkeypatch.setattr(checkpoint, "checkpoint", _fake)
        every = 3
        advance = checkpointed_every(lambda step: step * 2, every)
        assert [advance(step) for step in range(7)] == [0, 2, 4, 6, 8, 10, 12]
        assert calls == [3, 6]


class TestDriverUniquenessLock:
    """No settle loop may be hand-written outside the driver."""

    def test_no_hand_written_horizon_loop_in_the_dynamics_package(self) -> None:
        offenders = {
            path.name: _horizon_loops(path)
            for path in sorted(PACKAGE.glob("*.py"))
            if path.name != DRIVER and _horizon_loops(path)
        }
        assert offenders == {}, (
            "settle loops belong to run_settle_loop; call it with a step_fn "
            f"(TODO34 §5.1): {offenders}"
        )

    def test_the_driver_itself_still_has_its_own_loop(self) -> None:
        """Probe-the-probe: a scan that sees nothing proves nothing."""
        assert _horizon_loops(PACKAGE / DRIVER)

    def test_every_dynamics_class_reports_its_horizon(self) -> None:
        """Telemetry coverage: a settle that runs steps but never records the
        count is indistinguishable from a single pass to the instruments.
        ``InstantaneousDynamics`` runs one pass and says so. The count is
        not bounded by ``max_steps``: ``SpikeIntegrationDynamics``'s layered
        path integrates every layer against its own drive, so a settle
        executes ``max_steps`` per layer and the horizon counts them all."""
        import torch

        from computronium.ontology.dynamics import DYNAMICS_REGISTRY
        from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
        from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
        from computronium.state import CompositeState

        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=8, hidden_dims=(16, 16), output_dim=4)
        )
        substrate = DigitalSubstrate(SubstrateConfig.digital())

        for dynamics_type in DYNAMICS_REGISTRY:
            dynamics = DYNAMICS_REGISTRY[dynamics_type]()
            state = CompositeState(
                activity={"x": torch.randn(2, 8)}, plastic={}, substrate={}
            )
            with torch.no_grad():
                dynamics.settle(state, geometry, substrate, target=None)
            horizon = cast("int", getattr(dynamics, "_settle_steps_used"))
            assert horizon > 0, f"{dynamics_type} ran a settle, recorded no horizon"
