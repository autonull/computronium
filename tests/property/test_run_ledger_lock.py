"""TODO47 locks for a run's own ledger: §3.7 gates 5 (resume), 6 (replay hash), 7 (two policies over one store).

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

Gate 7 asks whether a second policy can measure over the same store and produce
records the first one can be compared with. Two properties, one falsifiable: the
model-based trial sequence must *differ* from the random one for the same seed
(a policy that quietly replays the other one is not a policy comparison), and a
measurement identity must be a function of the coordinate alone, so records from
two policies are comparable at all.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import (
    ModelBasedPolicy,
    Policy,
    StratifiedRandomPolicy,
)
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import (
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    AxisSelection,
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
    """A *narrow* space, so a second round can reach a cell the first did not.

    An unrestricted run declares hundreds of thousands of cells and a
    deterministic policy re-proposes its own first round, so "the resume added
    coverage" and "the extra round diverged" both became unobservable — the
    fixture, not the mechanism, was what the lock was silently testing.

    More legal cells than a round proposes (10) is the requirement: a space one
    round exhausts cannot show a resume adding coverage, nor a third round
    diverging from a second. The file then runs in ~17 s instead of 6 min.
    """
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
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(
                axis=StructuralAxis.GEOMETRY,
                primitives=("feedforward", "recurrent"),
            ),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS,
                primitives=(
                    "energy_minimization",
                    "lazy",
                    "predictive_settling",
                    "instantaneous",
                ),
            ),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("fast_weights",)),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=("thermodynamic_contrast", "gradient", "random_projections"),
            ),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
        ),
    )


def _config(
    run_id: str,
    spec: RunSpec,
    rounds: int,
    policy: Policy | None = None,
) -> PipelineConfig:
    return PipelineConfig(
        run_id=run_id,
        run_spec=spec,
        budget=Budget.from_duration(f"{int(spec.budget_seconds or 0)}s"),
        cost_model=SimpleCostModel(),
        backend=LocalBackend(),
        policy=policy or StratifiedRandomPolicy(seed=42),
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


def test_relaunching_a_run_never_duplicates_or_loses_a_measurement(
    tmp_path: Path,
) -> None:
    """Re-launching measures nothing twice; it may continue the coverage.

    The old form asserted ``second == first``, which is only true of a policy
    that forgets: the runner now hands the policy the store's completed count so
    a resume continues rather than replaying. The invariant that matters is the
    store's — no repeated key, and no cell spent on a measurement the store
    refuses.
    """
    spec = _run_spec()
    store_path = tmp_path / "resume_noop.duckdb"

    with RecordStore(StoreConfig(path=store_path)) as store:
        run_id = store.create_run(spec=spec)
        asyncio.run(PipelineRunner(_config(run_id, spec, rounds=2), store).run())
        first = set(_keys(store, run_id))
        runner = PipelineRunner(_config(run_id, spec, rounds=2), store)
        asyncio.run(runner.run())
        second = _keys(store, run_id)
        rejections = runner.rejections

    assert first
    assert set(first) <= set(second), "the relaunch lost a measurement"
    assert len(second) == len(set(second)), "the relaunch duplicated a measurement"
    assert not [r for r in rejections if r.get("cause") == "PERSISTENCE_ERROR"], (
        "the relaunch spent a measurement the store refused"
    )


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


def _two_policy_runs(tmp_path: Path) -> tuple[list[str], list[str]]:
    """Run random then model-based over one store; return both key sequences."""
    spec = _run_spec()
    store_path = tmp_path / "two_policies.duckdb"
    sequences: list[list[str]] = []

    for name, policy in (
        ("random", StratifiedRandomPolicy(seed=42)),
        ("model_based", ModelBasedPolicy(sampler="tpe", seed=42, n_startup_trials=5)),
    ):
        with RecordStore(StoreConfig(path=store_path)) as store:
            run_id = store.create_run(spec=spec)
            asyncio.run(PipelineRunner(_config(run_id, spec, 2, policy), store).run())
            store.finish_run(run_id, "completed")
            sequences.append(_keys(store, run_id))

    return sequences[0], sequences[1]


def test_two_policies_over_one_store_measure_different_trials(tmp_path: Path) -> None:
    """Same seed, same store, same task — and a different trial sequence.

    Per session 7's honesty note: a model-based policy that proposed the random
    policy's trials would be indistinguishable from it in the store.
    """
    random_keys, model_keys = _two_policy_runs(tmp_path)

    assert random_keys, "the random policy measured nothing"
    assert model_keys, "the model-based policy measured nothing"
    assert random_keys != model_keys


def test_measurement_identity_is_the_coordinate_alone(tmp_path: Path) -> None:
    """A record's key recomputes from its own coordinate — whichever policy wrote it."""
    from computronium.experiment.schema.coordinate import Coordinate

    random_keys, model_keys = _two_policy_runs(tmp_path)

    with RecordStore(StoreConfig(path=tmp_path / "two_policies.duckdb")) as store:
        records = [
            record
            for keys in (random_keys, model_keys)
            for record in store.query_records()
            if record.measurement_key in set(keys)
        ]

    assert records
    schema_versions = {record.schema_version for record in records}
    assert len(schema_versions) == 1, "two policies wrote two record schemas"
    for record in records:
        coordinate = Coordinate.from_record(record)
        assert coordinate.measurement_key(record.schedule) == record.measurement_key
