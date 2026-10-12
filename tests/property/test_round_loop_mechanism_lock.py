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

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.execution import (
    Budget,
    LocalBackend,
    PipelineConfig,
    PipelineRunner,
    Proposal,
    SimpleCostModel,
    StratifiedRandomPolicy,
    iter_candidates,
    search_space_from_spec,
    task_shape,
)
from computronium.experiment.schema import RunSpec, seed_all_registries

from ._fake_backend import FakeBackend
from ._specs import mechanism_spec

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from pathlib import Path

    from computronium.experiment.execution.backends import ExecutionBackend
    from computronium.experiment.kernel.search_space import SearchSpace

pytestmark = pytest.mark.timeout(300)


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


def test_a_measured_batch_measures_nothing_and_the_stream_says_so(
    tmp_path: Path,
) -> None:
    """Exhaustion is a signal the round loop reads, not a hang.

    Once every declared cell is stored the stream reports itself exhausted, so
    the loop concludes the finite space instead of spinning. Falsifiable by
    dropping the exhaustion flag: the loop then re-proposes measured cells
    (which the store refuses one at a time) until the round limit.
    """
    spec = mechanism_spec()
    with _launches(tmp_path, "exhausted", rounds=20) as (keys, runner, _store):
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
        stream = runner._state.cell_stream
        assert stream is not None and stream.is_exhausted, (
            "the exhaustion signal the round loop reads was never raised"
        )


def test_a_finished_space_ends_the_run_without_the_round_limit(
    tmp_path: Path,
) -> None:
    """The loop concludes a finished space rather than running out the clock.

    A stream with nothing left proposes nothing at all; the exhaustion check is
    what ends the run instead of the round limit.
    """
    with _launches(tmp_path, "bounded", rounds=20) as (keys, runner, _store):
        assert keys
        assert runner._state.current_round < 20, (
            "the run ran out its round limit instead of concluding"
        )


def test_the_run_charges_measured_cell_time_for_budget_sizing(tmp_path: Path) -> None:
    """The sizer reads measured walltime, so the run must charge it.

    ``BatchSizer.n_propose`` divides the remaining budget by the median cell
    time; falsifiable by dropping the charge: the sizer then never sees a
    median and every round proposes the cold-start maximum.
    """
    with _launches(tmp_path, "charged", rounds=20) as (keys, runner, _store):
        assert keys, "the fixture measured nothing"
        timing = runner._state.cell_timing
        assert timing.cell_count > 0, "no cell time was ever recorded"
        assert timing.median_cell_time() is not None, "the sizer has no median"


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
