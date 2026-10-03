"""The price oracle's numbers are the numbers the run produces (TODO48b R2).

Every guess a session made about a campaign's size — "will ``target_cells=6``
stop after seven records?", "how many cells does this space declare?", "is this
fixture big enough to need three launches?" — was answered by launching it. The
oracle answers them from the declaration before anything is spent, which makes
it falsifiable in the only way that matters: the run it priced stores exactly
the cells it counted, and its measured seconds land inside the published
tolerance of the projection.

The last test locks the reason the oracle exists. A declaration can name a
primitive that composes for nothing, and the space screens that silently: the
first draft of this fixture had one legal cell out of two declared axes and
nothing said so until a run measured it. ``unreachable`` is the report line that
would have said it.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import StratifiedRandomPolicy
from computronium.experiment.execution.pricing import price_plan
from computronium.experiment.execution.search_space import search_space_from_spec
from computronium.experiment.schema.registries import (
    FIXED_RUN_COST_SECONDS,
    MEASURED_CELL_SECONDS,
)
from computronium.experiment.schema.seed_registries import seed_all_registries

from ._specs import mechanism_spec, unreachable_spec

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.execution.pricing import PricePlan
    from computronium.experiment.schema.run_spec import RunSpec

pytestmark = pytest.mark.timeout(300)

# A projection is a plan, not a stopwatch: the table was measured on 16 CPU
# cores and a loaded box (or a GPU one) moves both directions. The band is
# published so a projection that is *structurally* wrong — the wrong cell count,
# an order of magnitude off — goes red without a slow machine going red.
_PROJECTION_BAND = (0.2, 4.0)


@pytest.fixture(scope="module", autouse=True)
def _seed_registries() -> None:
    seed_all_registries()


def _plan(spec: RunSpec) -> PricePlan:
    return price_plan(spec, search_space_from_spec(spec, tasks=spec.task_names))


def test_the_oracle_prices_every_primitive_it_can_measure() -> None:
    """The per-dynamics prices are the registry's, and every one is used.

    Falsifiable by inventing a number here: the sums would no longer be the
    registry's, so the projection would drift from the table the next session
    re-measures.
    """
    plan = _plan(mechanism_spec())

    assert set(plan.per_dynamics_seconds) <= set(MEASURED_CELL_SECONDS)
    assert sum(plan.per_dynamics_seconds.values()) == pytest.approx(
        plan.projected_seconds, rel=1e-9
    )


def test_a_declaration_that_names_an_unreachable_primitive_says_so() -> None:
    """Opportunity 3, made loud: an axis member no legal cell offers is named.

    Falsifiable by dropping ``_unreachable``: the report would call a one-cell
    axis a declared one and the run would read as a campaign that chose a single
    credit rule.
    """
    spec = unreachable_spec()
    plan = _plan(spec)

    assert plan.legal_cells < plan.declared_cells, (
        "the fixture is not exercising the gap it exists for"
    )
    # ``instantaneous`` is the unreachable member here, not the credit rule: the
    # credit axis composes with energy-based dynamics and the dynamics axis is
    # what collapses. Which primitive it is does not matter — that *some*
    # declared member is named does.
    assert plan.unreachable == (("dynamics", "instantaneous"),)
    assert "dynamics=instantaneous" in plan.render()


def test_a_declared_budget_stops_the_plan_where_the_run_would_stop() -> None:
    """The stop point is arithmetic, so a lock can depend on it.

    Falsifiable by overstating the price: the stop index would land earlier than
    the cells a budget that size actually pays for.
    """
    spec = mechanism_spec()
    budget = 3 * MEASURED_CELL_SECONDS["energy_minimization"]
    plan = _plan(spec.model_copy(update={"budget_seconds": budget}))

    stop = plan.budget_stop_cell
    assert stop is not None, "a budget the space overruns never stopped the plan"
    assert sum(plan.cell_seconds[: stop - 1]) <= budget, (
        "the stop is before the money ran out"
    )
    assert sum(plan.cell_seconds[:stop]) > budget, "the stop is after the money ran out"
    assert "stops at cell" in plan.render()


def test_the_projected_space_is_exactly_the_space_the_run_measures(
    tmp_path: Path,
) -> None:
    """Declared == stored, key for key, on a real backend.

    Falsifiable by overstating the cell count, which is the oracle's own
    assertion: the run stores fewer records than the plan promised and this goes
    red.
    """
    spec = mechanism_spec()
    plan = _plan(spec)
    started = time.perf_counter()
    with RecordStore(StoreConfig(path=tmp_path / "priced.duckdb")) as store:
        run_id = store.create_run(spec=spec)
        runner = PipelineRunner(
            PipelineConfig(
                run_id=run_id,
                run_spec=spec,
                budget=Budget.from_duration("10m"),
                cost_model=SimpleCostModel(),
                backend=LocalBackend(),
                policy=StratifiedRandomPolicy(seed=42),
                seed=spec.seed,
                max_rounds=4,
                min_rounds=1,
            ),
            store,
        )
        asyncio.run(runner.run())
        store.finish_run(run_id, "completed")
        stored = store.query_records(run_id=run_id)
    measured = time.perf_counter() - started

    assert plan.legal_cells == len(stored), (
        f"the oracle promised {plan.legal_cells} cell(s); the run stored {len(stored)}"
    )
    assert len({record.measurement_key for record in stored}) == len(stored)
    assert measured < plan.projected_seconds + FIXED_RUN_COST_SECONDS, (
        f"the run took {measured:.1f}s, more than its cells' "
        f"{plan.projected_seconds:.1f}s projection plus fixed cost"
    )
    timed = sum(float(record.payload.get("walltime_s", 0.0)) for record in stored)
    ratio = timed / plan.projected_seconds
    assert _PROJECTION_BAND[0] <= ratio <= _PROJECTION_BAND[1], (
        f"the cells timed {timed:.1f}s against a {plan.projected_seconds:.1f}s "
        f"projection ({ratio:.2f}x)"
    )
