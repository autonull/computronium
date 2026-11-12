"""Lock: a plan that comes back short says which rule pruned it (N2/G16).

An empty or short plan is a measurement of the space, and the space already
knows why: a void constraint, a compatibility rule, a compose failure or the
dry-run gate. The reasons used to be discarded, so a run reported "No more
cells to evaluate" over a declaration that was void on its face, and a
compatibility rule that the search space did not know about dropped a quarter
of the declared-legal space in silence.

Falsified by removing the sink: the counters stay empty and every assertion
below fails on an empty summary.
"""

from __future__ import annotations

from collections import Counter

from computronium.experiment.execution.policy import (
    ProposalContext,
    UniformRandomPolicy,
)
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import (
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema import (
    AxisSelection,
    RunSpec,
    StructuralAxis,
)
from computronium.experiment.wave import PolicyPlanner, StaticPlanner
from computronium.ontology.system import check_compatibility_matrix


def _spec(
    *,
    substrate: str = "digital",
    geometry: str = "recurrent",
    dynamics: str = "instantaneous",
    plasticity: str | tuple[str, ...] = "null",
    credit: str = "gradient",
    update: str = "adam",
) -> RunSpec:
    plasticity_values = (plasticity,) if isinstance(plasticity, str) else plasticity
    return RunSpec(
        task="mnist",
        fidelity="L1",
        n_seeds=1,
        epochs=1,
        budget_seconds=600.0,
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=(substrate,)),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=(geometry,)),
            AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=(dynamics,)),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=plasticity_values),
            AxisSelection(axis=StructuralAxis.CREDIT, primitives=(credit,)),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=(update,)),
        ),
    )


def test_a_void_declaration_names_its_constraint() -> None:
    """Gradient credit cannot compute recurrent weight grads (declared void)."""
    spec = _spec()
    space = search_space_from_spec(spec, tasks=("mnist",))
    rejections: Counter[str] = Counter()
    cells = list(
        iter_candidates(
            spec,
            space,
            shape=task_shape,
            rejections=rejections,
            page_size=50,
            use_void_cache=False,
        )
    )

    assert cells == []
    assert "void constraint: recurrent_instantaneous_gradient_credit" in rejections


def test_the_planner_summary_carries_the_cause() -> None:
    """The planner a run actually uses reads the same sink."""
    spec = _spec(plasticity=("null", "routing"))
    space = search_space_from_spec(spec, tasks=("mnist",))

    for planner in (
        StaticPlanner(
            spec=spec, fidelity="L1", tasks=("mnist",), seed=42, search_space=space
        ),
        PolicyPlanner(
            spec=spec,
            fidelity="L1",
            tasks=("mnist",),
            seed=42,
            search_space=space,
            policy="random",
        ),
    ):
        assert planner.propose(4, seen=set()) == []
        assert "void constraint: recurrent_instantaneous_gradient_credit" in (
            planner.rejection_summary()
        )


def test_a_flat_rule_drop_is_counted_too() -> None:
    """The planner's own compatibility matrix is a filter, not a silent gate.

    ``ternary`` x ``temporal_psi`` passes every declared constraint, so the
    search space proposes it; the flat matrix refuses it at the planner. That
    second filter has to report itself, or the two sources of truth can drift
    without a trace.
    """
    spec = _spec(
        substrate="ternary",
        geometry="feedforward",
        plasticity="temporal_psi",
    )
    space = search_space_from_spec(spec, tasks=("mnist",))
    rejections: Counter[str] = Counter()
    ctx = ProposalContext(
        search_space=space,
        spec=spec,
        run_id="lock",
        n_propose=4,
        shape=task_shape,
        rejections=rejections,
    )

    assert list(UniformRandomPolicy(seed=42).propose(ctx))
    planner = PolicyPlanner(
        spec=spec,
        fidelity="L1",
        tasks=("mnist",),
        seed=42,
        search_space=space,
        policy="random",
    )
    planner.propose(4, seen=set())
    assert "ternary' incompatible with plasticity 'temporal_psi" in (
        planner.rejection_summary()
    )


def test_stale_stdp_rule_stays_deleted() -> None:
    """STDP on instantaneous dynamics is a declared-legal cell, not a void.

    The flat matrix carried ``temporal_trace`` x ``instantaneous`` as
    incompatible while the declared space and the compiled ``hebbian`` rung
    both admit it. That disagreement made a whole quarter of the declared space
    vanish at the planner. The credit is error-blind by contract, so it measures
    chance on a supervised task; that is a result, not an illegal coordinate.
    """
    coordinate = (
        "digital",
        "recurrent",
        "instantaneous",
        "null",
        "temporal_trace",
        "adam",
    )
    assert check_compatibility_matrix(*coordinate) == []

    spec = _spec(credit="temporal_trace", plasticity=("null", "routing"))
    space = search_space_from_spec(spec, tasks=("mnist",))
    cells = list(iter_candidates(spec, space, shape=task_shape, page_size=50))
    assert cells
    assert {coordinate.plasticity for coordinate, _ in cells} == {"null", "routing"}
