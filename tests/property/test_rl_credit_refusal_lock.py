"""Lock: an RL cell cannot claim a credit the lane never applies (TODO92 §3.3b).

DDPG optimises ``system.geometry.params`` and never calls the composed credit,
so six credits measured one value (-126.4 at 30 episodes). The declared space
now refuses the error-aware credits on RL tasks: only the two rows that declare
``error_blind=True`` compose. Falsified by deleting the constraint: the
pendulum space proposes ``gradient``/``target_inversion`` again.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from computronium.core.system_trainer.spec import error_blind_credit
from computronium.experiment.kernel.search_space import (
    _compiled_void_constraints,
    search_space_from_spec,
)
from computronium.experiment.schema import (
    AxisSelection,
    RunSpec,
    StructuralAxis,
)
from computronium.experiment.schema.axis import AXES_REGISTRIES
from computronium.experiment.schema.seed_registries import seed_all_registries

type Rule = Callable[[tuple[str, ...]], object]

_RULE = "rl_credit_must_be_error_blind"
_ORDER = list(StructuralAxis)


def _error_blind() -> set[str]:
    """The credits whose implementation declares no error signal.

    Reads the declaration the constraint reads, not a test-local list.
    """
    seed_all_registries()
    credits = {
        spec.name
        for spec in AXES_REGISTRIES[StructuralAxis.CREDIT]
        if error_blind_credit(spec.name)
    }
    assert credits, "no credit declares error_blind=True"
    return credits


def _selection(task: str, credit: str) -> tuple[str, ...]:
    values = {
        "substrate": "digital",
        "geometry": "feedforward",
        "dynamics": "instantaneous",
        "plasticity": "null",
        "credit": credit,
        "update": "adam",
        "task": task,
    }
    return (*tuple(values[axis.value] for axis in _ORDER), task)


def _rule() -> Rule:
    seed_all_registries()
    _, task_dependent = _compiled_void_constraints()
    rules = dict(task_dependent)
    return cast("Rule", rules[_RULE])


def test_rl_refuses_error_aware_credits() -> None:
    rule = _rule()
    for credit in ("gradient", "target_inversion", "random_projections", "pc_alm"):
        assert not rule(_selection("pendulum", credit)), credit


def test_rl_keeps_the_error_blind_credits() -> None:
    rule = _rule()
    for credit in sorted(_error_blind()):
        assert rule(_selection("pendulum", credit)), credit


def test_the_rule_is_task_scoped() -> None:
    """The same error-aware credit stays legal off the RL lane."""
    rule = _rule()
    assert rule(_selection("mnist", "gradient"))
    assert rule(_selection("cora", "target_inversion"))


def test_the_pendulum_space_drops_error_aware_credits() -> None:
    spec = RunSpec(
        profile="rl-credit-lock",
        task="pendulum",
        objectives=("mean_reward", "walltime_total"),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=300.0,
        param_budget=100_000,
        batch_limit=32,
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
            AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=("instantaneous",)),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=("gradient", "homeostatic", "temporal_trace"),
            ),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("adam",)),
        ),
    )
    space = search_space_from_spec(spec, tasks=spec.task_names)
    assert set(space.primitives(StructuralAxis.CREDIT)) == _error_blind()
