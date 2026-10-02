"""Lock: a policy generates cells; it is never handed a list to choose from.

plan3 §5 names this the *Canonical SearchSpace/Proposal lock (WP14)*, and calls
it a guarded regression: nothing else stops the architecture from reverting to
a candidate list. Before (TODO46 §3.3/§3.4) every policy took
``propose(candidates, records, budget, cost_model)`` and only ever tuned the
hyperparameters inside a cell stream the caller had enumerated — so a
model-based run could not choose a topology, and no lock noticed.

Two claims, and the second is the guard:

* every policy, given the axes snapshot, the constraints, one task, a Budget and
  an empty store, proposes cells — legal ones, from that snapshot, for that task
* no policy's ``propose`` accepts a candidate list, which is what makes the first
  claim true tomorrow rather than today
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.compose import compose_configs
from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.execution.policy import (
    POLICY_CATALOG,
    EvolutionPolicy,
    ModelBasedPolicy,
    Policy,
    ProposalContext,
    RoundRobinGridPolicy,
    StrategyProgressionPolicy,
    StratifiedRandomPolicy,
    SynthesisPolicy,
    TrainerDrivenPolicy,
    UniformRandomPolicy,
)
from computronium.experiment.execution.search_space import search_space_from_spec
from computronium.experiment.schema.axis import Domain, Scale, StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection, RunSpec

_TASK = "digits"


def _spec(**overrides: Any) -> RunSpec:
    fields: dict[str, Any] = {
        "profile": "lock",
        "task": _TASK,
        "objectives": ("validation_accuracy",),
        "fidelity": "L0",
        "n_seeds": 1,
        "epochs": 2,
        "seed": 7,
        "hyperparameters": {"step_size": Domain(lo=1e-4, hi=1e-1, scale=Scale.LOG)},
        "axes": (
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
        ),
    }
    fields.update(overrides)
    return RunSpec(**fields)


_SPEC = _spec()

# One instance per catalog entry, so the lock runs over the shipped policies
# rather than over a stand-in that shares their names.
_POLICIES: dict[str, Policy] = {
    "evolution": EvolutionPolicy(seed=0),
    "model_based": ModelBasedPolicy(
        seed=0, objectives=("validation_accuracy",), spec=_SPEC
    ),
    "round_robin_grid": RoundRobinGridPolicy(seed=0),
    "stratified_random": StratifiedRandomPolicy(seed=0),
    "strategy_progression": StrategyProgressionPolicy(
        stages=[(UniformRandomPolicy(seed=0), 1.0)]
    ),
    "trainer_driven": TrainerDrivenPolicy(),
    "uniform_random": UniformRandomPolicy(seed=0),
}
_POLICIES["synthesis"] = SynthesisPolicy(list(_POLICIES.values()))


def _policy(name: str) -> Policy:
    return _POLICIES[name]


def _context(spec: RunSpec | None = None) -> ProposalContext:
    """One task, a budget, and an empty store. No candidate list exists."""
    declaration = spec or _SPEC
    return ProposalContext(
        search_space=search_space_from_spec(declaration, tasks=[_TASK]),
        spec=declaration,
        run_id="wp14",
        budget=Budget(started_at=0.0, target_cells=None, target_cost=None),
        cost_model=SimpleCostModel(),
        task=_TASK,
        shape=task_shape,
        n_propose=5,
    )


@pytest.mark.parametrize("name", sorted(POLICY_CATALOG))
def test_a_policy_with_no_candidates_and_no_records_still_proposes(name: str) -> None:
    ctx = _context()
    assert ctx.records() == [], "the lock only means something from an empty store"

    proposals = list(_policy(name).propose(ctx))

    assert proposals, f"{name} proposed nothing from an empty run"
    assert len(proposals) <= ctx.n_propose


@pytest.mark.parametrize("name", sorted(POLICY_CATALOG))
def test_every_proposal_is_a_cell_the_run_declared(name: str) -> None:
    ctx = _context()
    space = ctx.search_space
    for proposal in _policy(name).propose(ctx):
        for axis in StructuralAxis:
            assert getattr(proposal.coordinate, axis.value) in space.primitives(axis), (
                f"{name} proposed {getattr(proposal.coordinate, axis.value)} on "
                f"{axis.value}, which the spec does not permit"
            )
        assert proposal.schedule.task_id == _TASK
        assert proposal.schedule.fidelity == ctx.spec.fidelity


@pytest.mark.parametrize("name", sorted(POLICY_CATALOG))
def test_every_proposal_composes_for_the_task(name: str) -> None:
    """A cell nobody could compose is discovered by training, which is expensive."""
    shape = task_shape(_TASK)
    for proposal in _policy(name).propose(_context()):
        compose_configs(
            coordinate=proposal.coordinate,
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=proposal.schedule.param_budget,
        )


@pytest.mark.parametrize("name", sorted(POLICY_CATALOG))
def test_no_policy_takes_a_candidate_list(name: str) -> None:
    """The guarded regression: the architecture may not come back."""
    parameters = list(inspect.signature(POLICY_CATALOG[name].propose).parameters)
    assert parameters == ["self", "ctx"], (
        f"{name}.propose takes {parameters}; a policy that is handed candidates "
        "can only choose among them, which is the architecture WP14 forbids"
    )


def test_a_trainer_that_says_nothing_hands_over_to_the_fallback() -> None:
    class Silent:
        def propose(self, ctx: ProposalContext) -> Any:
            return []

    policy = TrainerDrivenPolicy(trainer=Silent(), fallback=UniformRandomPolicy(seed=0))

    assert list(policy.propose(_context()))


def test_a_space_with_nothing_on_an_axis_proposes_nothing() -> None:
    """No cells is a fact about the spec, not a policy failure."""
    ctx = _context(
        _spec(
            axes=(AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=()),),
        )
    )

    assert list(_policy("uniform_random").propose(ctx)) == []
