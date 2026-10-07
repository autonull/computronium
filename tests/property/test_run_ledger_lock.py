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
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.execution import (
    LocalBackend,
    Budget,
    SimpleCostModel,
    PipelineConfig,
    PipelineRunner,
    ModelBasedPolicy,
    Policy,
    StratifiedRandomPolicy,
    ProposalContext,
    search_space_from_spec,
    task_shape,
)
from computronium.experiment.schema import (
    StructuralAxis,
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    AxisSelection,
    RunSpec,
    seed_all_registries,
)

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
    diverging from a second. Using only fast dynamics/credits keeps the test
    focused on ledger mechanics (not dynamics correctness) while staying quick.
    """
    return RunSpec(
        profile="resume-lock",
        task="digits",
        objectives=("validation_accuracy", "walltime_total"),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        # An ample wall clock: this fixture's subject is measurement identity,
        # and a budget that expires on a loaded machine truncates the run at a
        # different cell than on an idle one — a real limit, and the wrong
        # variable for a hash lock to depend on.
        budget_seconds=600.0,
        param_budget=MEASURED_PARAM_BUDGET,
        batch_limit=MEASURED_BATCH_LIMIT,
        axes=(
            AxisSelection(
                axis=StructuralAxis.SUBSTRATE, primitives=("digital", "sparse", "analog")),
            AxisSelection(
                axis=StructuralAxis.GEOMETRY,
                primitives=("feedforward", "recurrent"),
            ),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS,
                primitives=("instantaneous",),
            ),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("fast_weights", "null")),
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
        asyncio.run(PipelineRunner(_config(run_id, spec, rounds=1), store).run())
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
    from computronium.experiment.schema import Coordinate

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


def _campaign_spec() -> RunSpec:
    """The narrow fixture widened to three substrates: one launch is one *batch*.

    ``_run_spec`` declares 15 cells and a round proposes ~8 of them, so two
    launches always finish any space of that size and a third has nothing to do.
    Thirty cells is the smallest widening where budget exhaustion interrupts the
    campaign twice and the last launch still owes it a round — the shape D3's
    claim needs. Measured: 30 declared, launches of 10/20/30, 13 s.
    """
    base = _run_spec()
    return base.model_copy(
        update={
            "axes": (
                AxisSelection(
                    axis=StructuralAxis.SUBSTRATE,
                    primitives=("digital", "sparse", "analog"),
                ),
                *(
                    selection
                    for selection in base.axes
                    if selection.axis != StructuralAxis.SUBSTRATE
                ),
            )
        }
    )


def _declared_keys(spec: RunSpec) -> set[str]:
    """Every measurement identity the declaration owes, from the same stream.

    Read through ``ProposalContext`` with no evidence, so "the space" and "the
    work left" are one implementation rather than two that can disagree.
    """
    from computronium.experiment.execution import (
        task_shape,
        ProposalContext,
        search_space_from_spec,
    )

    ctx = ProposalContext(
        search_space=search_space_from_spec(spec, tasks=spec.task_names),
        spec=spec,
        run_id="declared",
        budget=Budget.from_duration(f"{int(spec.budget_seconds or 0)}s"),
        cost_model=SimpleCostModel(),
        shape=task_shape,
    )
    return {
        coordinate.measurement_key(seed)
        for coordinate, schedule in ctx.cells()
        for seed in schedule.seed_plan
    }


def test_three_launches_complete_the_declared_space_with_no_duplicate_and_no_gap(
    tmp_path: Path,
) -> None:
    """TODO48 D3 at campaign scale: interrupt, resume, interrupt, resume, done.

    The interruption is a *budget*, not a timer: each of the first two launches
    is declared to stop at six measurements, so where it stops is arithmetic
    rather than a race with the machine clock — the fixture cannot be flaky
    about which cells a launch reached. What a killed process leaves behind is
    the same store, and a relaunch reads the same history.

    The two weaker claims above (nothing duplicated, nothing lost) both survive a
    resume that measures *nothing new at all*. This one is the campaign-scale
    statement: the third launch finishes the space the declaration names — every
    legal cell, every seed, no repeats — which is the only way a long campaign's
    numbers can be read as coverage rather than as a prefix.
    """
    spec = _campaign_spec()
    declared = _declared_keys(spec)
    store_path = tmp_path / "campaign_resume.duckdb"
    sizes: list[int] = []

    with RecordStore(StoreConfig(path=store_path)) as store:
        run_id = store.create_run(spec=spec)
        for launch, budgeted in enumerate((True, True, False)):
            config = _config(run_id, spec, rounds=3)
            if budgeted:
                # Budget exhaustion is the campaign's own stopping condition, and
                # the store is the checkpoint it leaves behind.
                config = replace(
                    config, budget=Budget.from_duration("10m", target_cells=6)
                )
            runner = PipelineRunner(config, store)
            asyncio.run(runner.run())
            status = "interrupted" if launch < 2 else "completed"
            store.finish_run(run_id, status)
            sizes.append(len(_keys(store, run_id)))
            assert not [
                r for r in runner.rejections if r.get("cause") == "PERSISTENCE_ERROR"
            ], f"launch {launch + 1} spent a measurement the store refused"

    with RecordStore(StoreConfig(path=store_path)) as store:
        stored_keys = _keys(store, run_id)

    assert declared, "the declaration owes nothing; the fixture is empty"
    assert sizes[0] < len(declared), (
        "the first launch finished the space, so no resume was exercised"
    )
    assert sizes[0] < len(declared), f"the first launch ignored its budget: {sizes}"
    assert sizes[0] < sizes[1], f"the first resume measured nothing new: {sizes}"
    assert sizes[1] < sizes[2], f"the second resume measured nothing new: {sizes}"
    assert len(stored_keys) == len(set(stored_keys)), "a launch duplicated a cell"
    assert set(stored_keys) == declared, (
        f"{len(declared - set(stored_keys))} declared cell(s) unmeasured, "
        f"{len(set(stored_keys) - declared)} measured outside the declaration"
    )


def test_every_policy_resumes_within_the_runs_own_store(tmp_path: Path) -> None:
    """Resume is not a per-policy courtesy: the stream every policy walks is filtered.

    D3's second half. Only two of the eight policies used to remember a cursor,
    and the other six re-proposed their first round into cells already measured —
    the round then stored nothing, and the run concluded the space was exhausted
    while two thirds of it was untouched. The mechanism is therefore singular
    (``ProposalContext.cells`` skips what the store holds) and this walks every
    catalog entry over one real store to prove no policy escapes it.
    """
    from computronium.experiment.execution import (
        task_shape,
        POLICY_CATALOG,
        ProposalContext,
        create_policy,
        policy_context,
        search_space_from_spec,
    )

    spec = _campaign_spec()
    store_path = tmp_path / "policy_resume.duckdb"
    with RecordStore(StoreConfig(path=store_path)) as store:
        run_id = store.create_run(spec=spec)
        config = _config(run_id, spec, rounds=2)
        # One round's batch, then stop: half the space, so a resume is visible.
        asyncio.run(
            PipelineRunner(
                replace(config, budget=Budget.from_duration("10m", target_cells=4)),
                store,
            ).run()
        )
        store.finish_run(run_id, "interrupted")
        measured = frozenset(_keys(store, run_id))

        assert 0 < len(measured) < len(_declared_keys(spec)), (
            "the fixture measured nothing, or everything; a resume is unobservable"
        )

        for name in POLICY_CATALOG:
            policy = create_policy(name, **policy_context(spec, name, shape=task_shape))
            ctx = ProposalContext(
                search_space=search_space_from_spec(spec, tasks=spec.task_names),
                spec=spec,
                run_id=run_id,
                budget=Budget.from_duration(f"{int(spec.budget_seconds or 0)}s"),
                cost_model=SimpleCostModel(),
                evidence=store,
                shape=task_shape,
            )
            proposals = list(policy.propose(ctx))

            assert proposals, f"{name} proposed nothing to resume"
            stale = [
                proposal.coordinate.measurement_key(seed)
                for proposal in proposals
                for seed in proposal.schedule.seed_plan
                if proposal.coordinate.measurement_key(seed) in measured
            ]
            assert not stale, f"{name} re-proposed {len(stale)} measured measurement(s)"
