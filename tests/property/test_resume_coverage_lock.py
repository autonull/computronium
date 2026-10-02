"""TODO47 locks for a run's own bookkeeping: §3.7 gate 5 (resume) and gate 6 (replay hash).

The lock reads the store alone. It asserts the two properties a resumed run
must have — no duplicate ``measurement_key`` and no gap in coordinate coverage —
and, crucially, that it can fail. The store's ``UNIQUE(run_id, measurement_key)``
constraint hides re-measurement rather than exposing it, so the falsifiable
statement is the rejection list: with the resume seeding removed from
``PipelineRunner`` every already-measured cell is re-measured, refused by the
store, and classified as a PERSISTENCE_ERROR rejection.

Gate 6 is the same discipline applied to ``runs.replay_hash``: the hash must be
written when the run finishes, must repeat for the same declaration, and must
change when the declaration changes — or it describes nothing.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import StratifiedRandomPolicy
from computronium.experiment.schema.run_spec import (
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    RunSpec,
)
from computronium.experiment.schema.seed_registries import seed_all_registries

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.timeout(300)


@pytest.fixture(scope="module", autouse=True)
def _seed_registries() -> None:
    seed_all_registries()


def _run_spec() -> RunSpec:
    return RunSpec(
        profile="resume-lock",
        task="digits",
        objectives=("validation_accuracy", "walltime_total"),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=60.0,
        param_budget=MEASURED_PARAM_BUDGET,
        batch_limit=MEASURED_BATCH_LIMIT,
    )


def _config(run_id: str, spec: RunSpec, rounds: int) -> PipelineConfig:
    return PipelineConfig(
        run_id=run_id,
        run_spec=spec,
        budget=Budget.from_duration(f"{int(spec.budget_seconds or 0)}s"),
        cost_model=SimpleCostModel(),
        backend=LocalBackend(),
        policy=StratifiedRandomPolicy(seed=42),
        seed=spec.seed,
        max_rounds=rounds,
        min_rounds=1,
    )


def _keys(store: RecordStore, run_id: str) -> list[str]:
    return [r.measurement_key for r in store.query_records(run_id=run_id)]


def test_resume_by_run_id_neither_duplicates_nor_loses_a_measurement(
    tmp_path: Path,
) -> None:
    """Interrupt after the first round, resume by run_id, check the store alone."""
    spec = _run_spec()
    store_path = tmp_path / "resume_lock.duckdb"

    with RecordStore(StoreConfig(path=store_path)) as store:
        run_id = store.create_run(spec=spec)
        asyncio.run(PipelineRunner(_config(run_id, spec, rounds=2), store).run())
        store.finish_run(run_id, "interrupted")
        interrupted = _keys(store, run_id)

    assert interrupted, "the interrupted launch measured nothing to resume from"

    with RecordStore(StoreConfig(path=store_path)) as store:
        runner = PipelineRunner(_config(run_id, spec, rounds=3), store)
        asyncio.run(runner.run())
        store.finish_run(run_id, "completed")
        resumed = _keys(store, run_id)
        rejections = runner.rejections

    # No duplicate measurement_key survived in the store.
    assert len(resumed) == len(set(resumed))

    # No gap: every interrupted measurement is still there, nothing was lost.
    assert set(interrupted) <= set(resumed)

    # And the resume did work rather than re-measuring the same cells.
    assert len(resumed) > len(interrupted)

    # The store's own duplicate constraint is not what saved the run: without
    # resume seeding each re-measured cell reaches the store, is refused, and
    # lands here as a rejection — the measurement is spent and lost.
    assert not [r for r in rejections if r.get("cause") == "PERSISTENCE_ERROR"]


def test_resume_of_an_uninterrupted_run_is_a_no_op(tmp_path: Path) -> None:
    """Re-launching the same run_id re-measures nothing and rejects nothing."""
    spec = _run_spec()
    store_path = tmp_path / "resume_noop.duckdb"

    with RecordStore(StoreConfig(path=store_path)) as store:
        run_id = store.create_run(spec=spec)
        asyncio.run(PipelineRunner(_config(run_id, spec, rounds=2), store).run())
        first = set(_keys(store, run_id))
        runner = PipelineRunner(_config(run_id, spec, rounds=2), store)
        asyncio.run(runner.run())
        second = set(_keys(store, run_id))
        rejections = runner.rejections

    assert first
    assert second == first
    assert not [r for r in rejections if r.get("cause") == "PERSISTENCE_ERROR"]


def _replay_hash_of(tmp_path: Path, name: str, spec: RunSpec, rounds: int = 2) -> str:
    """Run one spec to completion in its own store; return the hash it wrote."""
    with RecordStore(StoreConfig(path=tmp_path / name)) as store:
        run_id = store.create_run(spec=spec)
        runner = PipelineRunner(_config(run_id, spec, rounds=rounds), store)
        asyncio.run(runner.run())
        store.finish_run(run_id, "completed")
        return store.query_runs(run_id=run_id)[0].replay_hash or ""


def test_the_same_spec_run_twice_yields_the_same_replay_hash(tmp_path: Path) -> None:
    """A replayed run is recognisable as the same run."""
    spec = _run_spec()
    first = _replay_hash_of(tmp_path, "replay_a.duckdb", spec)
    second = _replay_hash_of(tmp_path, "replay_b.duckdb", spec)

    assert first, "the run wrote no replay hash"
    assert first == second


def test_one_changed_spec_field_yields_a_different_replay_hash(tmp_path: Path) -> None:
    """A changed declaration is a different run, and the hash says so."""
    base = _run_spec()
    changed = base.model_copy(update={"epochs": base.epochs + 1})

    assert tuple(base.diff(changed)) == ("epochs",)
    assert _replay_hash_of(tmp_path, "replay_c.duckdb", base) != _replay_hash_of(
        tmp_path, "replay_d.duckdb", changed
    )


def test_a_diverged_run_hashes_differently_though_its_spec_did_not(
    tmp_path: Path,
) -> None:
    """A spec-only hash cannot detect a run that measured different cells."""
    spec = _run_spec()
    short = _replay_hash_of(tmp_path, "replay_short.duckdb", spec, rounds=2)
    long = _replay_hash_of(tmp_path, "replay_long.duckdb", spec, rounds=3)

    assert short != long
