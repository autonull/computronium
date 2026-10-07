"""The round loop's mechanisms, verified without training a cell (TODO48b R1).

Four of the defects D3 found inside its own blast radius were found by *training
cells to check plumbing*: a budget that nothing charged, a decision read back as
a constant, a policy that re-proposed what the store held, a rejection nobody
classified. Each cost 17-26 s to assert and none of them was about learning.

So the plumbing is asserted here against an injected backend
(``tests/property/_fake_backend.py``), where the whole file runs in seconds, and
the last test ties that tier to reality: the same declaration through the fake
and through a real ``LocalBackend`` must store an identical set of
``measurement_key``s. That test is the honesty requirement — a fake that skipped
the dedup, or the legality screen, would make the two sets differ, and a lock
that cannot go red is a comment.
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import StratifiedRandomPolicy
from computronium.experiment.execution.search_space import (
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.execution.stage import Proposal
from computronium.experiment.schema import RunSpec, seed_all_registries

from ._fake_backend import SYNTHETIC_WALLTIME_S, FakeBackend
from ._specs import mechanism_spec

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from pathlib import Path

    from computronium.experiment.execution.backends import ExecutionBackend
    from computronium.experiment.execution.search_space import SearchSpace

pytestmark = pytest.mark.timeout(300)

# The most rounds a run may spin while measuring nothing, before it concludes.
MAX_FRUITLESS_ROUNDS = 3


@pytest.fixture(scope="module", autouse=True)
def _seed_registries() -> None:
    seed_all_registries()


def _space(spec: RunSpec) -> SearchSpace:
    """The space this spec resolves to, as the runner builds it."""
    return search_space_from_spec(spec, tasks=spec.task_names)


def _config(
    run_id: str,
    spec: RunSpec,
    *,
    backend: ExecutionBackend,
    rounds: int = 3,
    budget: Budget | None = None,
) -> PipelineConfig:
    return PipelineConfig(
        run_id=run_id,
        run_spec=spec,
        budget=budget or Budget.from_duration("10m"),
        cost_model=SimpleCostModel(),
        backend=backend,
        policy=StratifiedRandomPolicy(seed=42),
        seed=spec.seed,
        max_rounds=rounds,
        min_rounds=1,
    )


@contextlib.contextmanager
def _launches(
    tmp_path: Path,
    name: str,
    *,
    spec: RunSpec | None = None,
    backend_factory: Callable[[], ExecutionBackend] | None = None,
    rounds: int = 3,
    budget: Budget | None = None,
    launches: int = 1,
) -> Generator[tuple[list[str], PipelineRunner, RecordStore]]:
    """Run one declaration ``launches`` times over one store; yield its ledger.

    Every launch builds a fresh backend, because a backend that remembers its
    submissions is exactly what the resume test must not be able to lean on.
    """
    spec = spec or mechanism_spec()
    with RecordStore(StoreConfig(path=tmp_path / f"{name}.duckdb")) as store:
        run_id = store.create_run(spec=spec)
        runner: PipelineRunner | None = None
        for launch in range(launches):
            runner = PipelineRunner(
                _config(
                    run_id,
                    spec,
                    backend=(backend_factory or FakeBackend)(),
                    rounds=rounds,
                    budget=replace(budget, started_at=0.0) if budget else None,
                ),
                store,
            )
            asyncio.run(runner.run())
            store.finish_run(
                run_id, "interrupted" if launch < launches - 1 else "completed"
            )
        assert runner is not None
        yield (
            [r.measurement_key for r in store.query_records(run_id=run_id)],
            runner,
            store,
        )


def test_a_relaunched_run_measures_nothing_twice_and_says_why(tmp_path: Path) -> None:
    """The store is the checkpoint: a relaunch adds no key and loses none.

    Falsifiable by removing ``_resume_completed_measurements``: every
    already-measured cell is then re-proposed, re-measured and refused by the
    store, which is a PERSISTENCE_ERROR rejection per seed — a measurement spent
    to learn nothing.
    """
    with _launches(tmp_path, "relaunch", launches=2) as (keys, runner, _store):
        assert keys, "the fixture measured nothing"
        assert len(keys) == len(set(keys)), "a launch duplicated a measurement"
        assert not [
            r for r in runner.rejections if r.get("cause") == "PERSISTENCE_ERROR"
        ]
        backend = runner._config.backend
        assert isinstance(backend, FakeBackend)
        assert backend.submitted == [], (
            "the second launch re-measured the first's cells"
        )


def test_a_batch_of_measured_cells_measures_nothing_and_says_so(
    tmp_path: Path,
) -> None:
    """Exhaustion is a signal the round loop reads, not a hang.

    The all-seen batch is what distinguishes "the policy has nothing left" from
    "the cells this round proposed failed": the first ends the run, the second
    is retried a bounded number of times. Falsifiable by dropping the flag —
    the loop then spins to its round limit on a space it has finished.
    """
    spec = mechanism_spec()
    with _launches(tmp_path, "exhausted", rounds=5) as (keys, runner, _store):
        assert keys, "the fixture measured nothing"
        assert len(keys) == len(set(keys)), "a round duplicated a measurement"
        proposals = list(iter_candidates(spec, _space(spec), shape=task_shape))
        measured = asyncio.run(
            runner._execute_batch_with_isolation([
                Proposal(coordinate=c, schedule=s, rationale="exhaustion")
                for c, s in proposals
            ])
        )
        assert measured == [], "a batch of measured cells was measured again"
        assert runner._state.last_batch_was_all_seen, (
            "the exhaustion signal the round loop reads was never raised"
        )


def test_a_policy_with_nothing_left_ends_the_run_in_bounded_rounds(
    tmp_path: Path,
) -> None:
    """The loop concludes a finished space rather than running out the clock.

    A policy whose stream is empty proposes nothing at all, so the all-seen
    batch never forms; the fruitless-round bound is what ends the run instead.
    Both paths terminate, and neither may cost the round limit.
    """
    with _launches(tmp_path, "bounded", rounds=20) as (keys, runner, _store):
        assert keys
        assert runner._state.current_round < 20, (
            "the run ran out its round limit instead of concluding"
        )


def test_the_budget_is_charged_for_exactly_what_the_run_stored(tmp_path: Path) -> None:
    """A declared budget binds, because the run charges what it stored.

    Falsifiable by dropping the ``_charge_budget`` call: ``target_cells`` then
    compares against a counter nothing advances, every cell looks affordable,
    and a campaign declared to stop measures its whole space instead.
    """
    with _launches(
        tmp_path, "charged", budget=Budget.from_duration("10m", target_cells=4)
    ) as (keys, runner, _store):
        budget = runner._state.budget
        assert budget is not None
        assert budget.target_reached(), "the declared cell budget never bound"
        assert budget.done == len(keys) > 3, (
            f"the cell budget did not bind: {len(keys)} keys"
        )
        assert budget.cost_consumed == pytest.approx(
            len(keys) * SYNTHETIC_WALLTIME_S, rel=1e-6
        )


def test_an_exhausted_budget_is_read_as_a_decision_not_as_a_clock(
    tmp_path: Path,
) -> None:
    """S10's termination reaches the round loop as a decision.

    Falsifiable by returning ``continue_round`` unconditionally — the shape D3
    found: the decision was built and then read back as a constant, so the only
    stopping condition left was the round limit.
    """
    with _launches(
        tmp_path,
        "decided",
        rounds=8,
        budget=Budget.from_duration("10m", target_cells=3),
    ) as (_keys, runner, _store):
        decision = runner._state.last_decision
        assert decision is not None, "no stage ever decided"
        assert decision.transition.value == "complete"
        assert decision.rationale == "Budget exhausted"
        assert runner._state.current_round < 8, (
            "the round limit stopped it, not the budget"
        )


def test_a_rejected_cell_is_classified_and_its_siblings_still_store(
    tmp_path: Path,
) -> None:
    """Failure isolation: one refused cell costs one cell, not the batch.

    Falsifiable by letting the exception escape ``submit_batch``: every
    sibling in the round is lost with it.
    """
    rejected = "gradient"

    def rejects(coordinate, schedule) -> str | None:
        _ = schedule
        return "no" if coordinate.credit == rejected else None

    with _launches(
        tmp_path,
        "isolated",
        backend_factory=lambda: FakeBackend(rejects=rejects),
        rounds=2,
    ) as (keys, runner, store):
        causes = {r.get("cause") for r in runner.rejections}
        assert keys, "the whole batch died with the rejected cell"
        assert "invalid_config" in causes, f"the rejection was not classified: {causes}"
        credits = {record.credit for record in store.query_records()}
        assert credits == {"random_projections"}, (
            f"a refused cell was stored anyway: {credits}"
        )


def test_the_fake_tier_and_a_real_backend_store_the_same_measurements(
    tmp_path: Path,
) -> None:
    """The synchronization lock: the fast tier may not drift from reality.

    One declaration, two backends, two stores, one expected answer: the set of
    ``measurement_key``s the run measured. A fake that skipped the dedup, the
    legality screen or the per-seed split would store a different set, and this
    goes red naming which side moved.
    """
    with _launches(tmp_path, "sync_fake") as (fake_keys, _fake, _store):
        pass
    with _launches(tmp_path, "sync_real", backend_factory=LocalBackend) as (
        real_keys,
        _real,
        _store,
    ):
        pass

    assert fake_keys, "the fake measured nothing, so it agrees with nothing"
    assert set(fake_keys) == set(real_keys), (
        f"fake-only: {sorted(set(fake_keys) - set(real_keys))}; "
        f"real-only: {sorted(set(real_keys) - set(fake_keys))}"
    )
