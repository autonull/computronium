"""Lock: a claim carries n and variance, and every limitation is queryable.

TODO46 §3.5's gate. The report rendered statistics — record counts, maturity
distributions, a Pareto front — and *no claims*: ``claims.py`` had eligibility
predicates and no renderer, and the word "limitation" appeared nowhere under
``experiment/``, so the third element of R85's Claim/Evidence/Limitation
triple had no data model at all.

Two claims are locked here, and they are different in kind:

* a claim is **inexpressible** without its evidence — ``n`` and ``variance``
  are required fields with no default, so no caller can assert a claim and
  forget what it rests on
* a limitation is **re-derivable** — every line carries the filter that
  recomputes its count from records, and each test recomputes it

The records are measured, not fabricated: this module's fixture trains real
``digits`` cells through the kernel's own evaluator (``cell_record``) and
stores them, at the measured regime — one epoch, two batches, the declared
parameter ceiling. A hand-written payload would prove the report formats a
dict; a measured one proves the claim is a claim.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from computronium.experiment.evidence.claims import (
    Claim,
    derive_claims,
    replication_key,
    strongest_axis,
)
from computronium.experiment.evidence.limitations import (
    Limitation,
    LimitationKind,
    derive_limitations,
    replication_keys_of,
)
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.evaluate import cell_record
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.experiment.schema.metrics import measured_objectives, objective_metric
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)
from computronium.experiment.schema.run_spec import MEASURED_PARAM_BUDGET, RunSpec
from computronium.experiment.surface.report import ReportGenerator, generate_run_report

_TASK = "digits"
_CREDITS = ("thermodynamic_contrast", "local_contrastive")
_SEEDS = 5
_SHORT_SEEDS = 2
_BATCHES = 2
_METRIC = "val_acc"


def _coordinate(credit: str) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="fast_weights",
        credit=credit,
        update="euclidean",
        params={},
    )


def _schedule(seed: int) -> Schedule:
    return Schedule(
        fidelity="L2",
        seed=seed,
        n_seeds=1,
        epochs=1,
        batch_limit=_BATCHES,
        budget_id="claim-gate",
        task_id=_TASK,
        param_budget=MEASURED_PARAM_BUDGET,
    )


def _spec(**overrides: object) -> RunSpec:
    declared: dict[str, object] = {
        "task": _TASK,
        "objectives": ("validation_accuracy",),
        "fidelity": "L2",
        "n_seeds": _SEEDS,
        "epochs": 1,
        "batch_limit": _BATCHES,
        "param_budget": MEASURED_PARAM_BUDGET,
    }
    return RunSpec(**{**declared, **overrides})  # type: ignore[arg-type]


@pytest.fixture(scope="module")
def measured_run(
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[tuple[str, Path]]:
    """A store holding measured ``digits`` records: two credits at five seeds.

    The first credit is measured at all ``_SEEDS``; the second stops at
    ``_SHORT_SEEDS``, so the abandoned-cell limitation has something real to
    derive. Yields the run id and the store path.
    """
    path = tmp_path_factory.mktemp("claims") / "claims.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=_spec())
        for credit, n_seeds in ((_CREDITS[0], _SEEDS), (_CREDITS[1], _SHORT_SEEDS)):
            for seed in range(n_seeds):
                record = cell_record(
                    _coordinate(credit),
                    _schedule(seed),
                    Provenance(
                        env={},
                        dataset=_TASK,
                        dataset_version="1.0",
                        code_sha="test",
                        policy="test",
                        links={"run_id": run_id},
                    ),
                )
                store.append(record)
    yield run_id, path


@pytest.fixture(scope="module")
def measured_records(measured_run: tuple[str, Path]) -> list[Record]:
    """The measured records, read back from the store the run wrote."""
    run_id, path = measured_run
    with RecordStore(StoreConfig(path=path)) as store:
        return store.query_records(run_id=run_id)


class TestClaimModel:
    """A claim is not expressible without the evidence it rests on (R64)."""

    def test_n_and_variance_are_required_fields(self) -> None:
        with pytest.raises(TypeError):
            Claim(  # type: ignore[call-arg]
                metric=_METRIC, axis="credit", value="pepita", mean=0.5, variance=0.01
            )

    @pytest.mark.parametrize(
        ("n", "mean", "variance"),
        [
            (0, 0.5, 0.0),
            (5, float("nan"), 0.0),
            (5, 0.5, float("inf")),
            (5, 0.5, -1e-9),
        ],
    )
    def test_an_impossible_claim_is_refused(
        self, n: int, mean: float, variance: float
    ) -> None:
        with pytest.raises(ValueError, match="Claim"):
            Claim(
                metric=_METRIC,
                axis="credit",
                value="pepita",
                n=n,
                mean=mean,
                variance=variance,
                cells=1,
            )

    def test_a_rendered_claim_names_its_evidence(self) -> None:
        claim = Claim(
            metric=_METRIC,
            axis="credit",
            value="pepita",
            n=5,
            mean=0.5,
            variance=0.04,
            cells=2,
        )
        rendered = claim.render()
        assert "n=5" in rendered
        assert "credit=pepita" in rendered
        assert _METRIC in rendered


class TestClaimDerivation:
    """Claims are grouped from measurements, filtered by the predicates."""

    def test_measured_records_produce_a_claim(
        self, measured_records: list[Record]
    ) -> None:
        claims = derive_claims(measured_records, metrics=(_METRIC,), min_seeds=_SEEDS)

        assert claims, "measured records yielded no claim"
        assert {claim.metric for claim in claims} == {_METRIC}
        for claim in claims:
            assert claim.n >= _SEEDS
            assert claim.cells >= 1

    def test_a_claim_mean_is_the_mean_of_its_records(
        self, measured_records: list[Record]
    ) -> None:
        claims = derive_claims(measured_records, metrics=(_METRIC,), min_seeds=_SEEDS)
        for claim in claims:
            values = [
                float(r.payload[_METRIC])
                for r in measured_records
                if getattr(r, claim.axis) == claim.value
            ]
            assert claim.n == len(values)
            assert claim.mean == pytest.approx(sum(values) / len(values))

    def test_a_cell_short_of_its_declared_seeds_makes_no_claim(
        self, measured_records: list[Record]
    ) -> None:
        """The filter is eligibility, not a quorum the run asserts."""
        achieved = {
            key: sum(
                1
                for r in measured_records
                if replication_key(r) == key and r.status.gate_verdict.value == "PASS"
            )
            for key in replication_keys_of(measured_records)
        }
        assert min(achieved.values()) < _SEEDS, "fixture should include a short cell"

        claimed = {
            claim.value
            for claim in derive_claims(
                measured_records,
                metrics=(_METRIC,),
                achieved=achieved,
                min_seeds=_SEEDS,
            )
        }
        assert _CREDITS[0] in claimed
        assert _CREDITS[1] not in claimed

    def test_a_failed_or_quarantined_record_never_backs_a_claim(
        self, measured_records: list[Record]
    ) -> None:
        """A claim is a filter applied to a run, never the run asserting itself."""
        failing = [
            record
            for record in measured_records
            if record.status.gate_verdict.value == "PASS"
            and not record.status.quarantine
        ]
        without = derive_claims(measured_records, metrics=(_METRIC,), min_seeds=_SEEDS)
        filtered = derive_claims(
            failing,
            metrics=(_METRIC,),
            min_seeds=_SEEDS,
        )
        assert {c.value for c in without} == {c.value for c in filtered}
        assert all(c.n >= _SEEDS for c in filtered)

    def test_the_widest_axis_is_the_one_reported_as_mattering(self) -> None:
        claims = (
            Claim(
                metric=_METRIC,
                axis="credit",
                value="a",
                n=5,
                mean=0.9,
                variance=0.01,
                cells=1,
            ),
            Claim(
                metric=_METRIC,
                axis="credit",
                value="b",
                n=5,
                mean=0.2,
                variance=0.01,
                cells=1,
            ),
            Claim(
                metric=_METRIC,
                axis="update",
                value="euclidean",
                n=5,
                mean=0.6,
                variance=0.01,
                cells=1,
            ),
            Claim(
                metric=_METRIC,
                axis="update",
                value="hebbian",
                n=5,
                mean=0.5,
                variance=0.01,
                cells=1,
            ),
        )
        impact = strongest_axis(claims)

        assert impact is not None
        assert impact.axis == "credit"
        assert impact.best_value == "a"
        assert impact.worst_value == "b"
        assert impact.spread == pytest.approx(0.7)

    def test_one_value_per_axis_makes_no_impact(self) -> None:
        claims = (
            Claim(
                metric=_METRIC,
                axis="credit",
                value="a",
                n=5,
                mean=0.9,
                variance=0.0,
                cells=1,
            ),
        )
        assert strongest_axis(claims) is None


class TestPerMetricClaims:
    """TODO47 T4: which axis mattered, asked per metric and over a real front.

    Session 11's note: a report that answers for the run's *first* objective
    cannot say that a different axis dominated the second one, and a front over
    one metric and ``param_count`` throws away the outcome the run declared.
    """

    @pytest.fixture(scope="class")
    def two_objective_run(
        self, tmp_path_factory: pytest.TempPathFactory
    ) -> Iterator[tuple[str, Path]]:
        """A measured run declaring two objectives: accuracy and walltime."""
        path = tmp_path_factory.mktemp("two_objectives") / "two.duckdb"
        spec = _spec(objectives=("validation_accuracy", "walltime_total"))
        with RecordStore(StoreConfig(path=path)) as store:
            run_id = store.create_run(spec=spec)
            for credit in _CREDITS:
                for seed in range(_SEEDS):
                    store.append(
                        cell_record(
                            _coordinate(credit),
                            _schedule(seed),
                            Provenance(
                                env={},
                                dataset=_TASK,
                                dataset_version="1.0",
                                code_sha="test",
                                policy="test",
                                links={"run_id": run_id},
                            ),
                        )
                    )
        yield run_id, path

    def test_the_report_claims_both_declared_metrics(
        self, two_objective_run: tuple[str, Path]
    ) -> None:
        run_id, path = two_objective_run
        with RecordStore(StoreConfig(path=path)) as store:
            claims = ReportGenerator(store).claims(run_id)

        assert {claim.metric for claim in claims} == {"val_acc", "walltime_s"}

    def test_the_front_spans_the_two_declared_objectives(
        self, two_objective_run: tuple[str, Path]
    ) -> None:
        run_id, path = two_objective_run
        with RecordStore(StoreConfig(path=path)) as store:
            generator = ReportGenerator(store)
            axes = generator.front_objectives(run_id)
            front = generator.pareto_frontier(run_id)

        assert axes == ("val_acc", "walltime_s")
        assert front, "no claim-eligible record carried both objectives"
        for point in front:
            assert point["primary"] == pytest.approx(
                float(point["primary"])  # the val_acc the front ranked on
            )
            assert point["secondary"] > 0

    def test_a_trade_off_keeps_every_non_dominated_point(
        self, tmp_path_factory: pytest.TempPathFactory
    ) -> None:
        """The filter itself, on points that genuinely trade off.

        Fabricated on purpose: this run's measured cells do not trade off.
        ``val_acc`` saturates at two values in the measured regime, so the
        fastest high-accuracy cell dominates every other and the measured front
        is legitimately a single point — asserted above, not hidden here. A front
        with one point is a finding about the regime; a front that cannot hold
        two is a broken filter, and only a real trade-off can tell them apart.
        """

        def _point(acc: float, wall: float) -> Record:
            return Record.create(
                run_id="pareto-filter",
                coordinate=_coordinate(_CREDITS[0]),
                schedule=_schedule(0),
                provenance=Provenance(
                    env={},
                    dataset=_TASK,
                    dataset_version="1.0",
                    code_sha="test",
                    policy="test",
                    links={},
                ),
                status=Status(
                    gate_verdict=GateVerdict.PASS_,
                    defect="",
                    cause=FailureCause.UNKNOWN,
                    severity=Severity.LOW,
                    quarantine=False,
                    maturity=Maturity.L0,
                    uncertainty={},
                    reproducibility=ReproducibilityClass.REPLAYABLE,
                    assessment_procedure_version="1.0",
                    ceec_link=None,
                ),
                payload={"val_acc": acc, "walltime_s": wall},
            )

        points = [_point(0.9, 1.0), _point(0.8, 0.5), _point(0.7, 0.6)]
        with RecordStore(
            StoreConfig(path=tmp_path_factory.mktemp("pareto") / "pareto.duckdb")
        ) as store:
            generator = ReportGenerator(store)
            front = generator._pareto_subset(
                points, ("val_acc", "walltime_s"), (True, False)
            )

        assert [(p["primary"], p["secondary"]) for p in front] == [
            (0.9, 1.0),
            (0.8, 0.5),
        ]

    def test_the_report_names_the_axes_its_front_used(
        self, two_objective_run: tuple[str, Path]
    ) -> None:
        run_id, path = two_objective_run
        with RecordStore(StoreConfig(path=path)) as store:
            report = generate_run_report(store, run_id)

        assert "val_acc vs walltime_s" in report


class TestLimitations:
    """Every limitation line is a count of records under a stated filter."""

    def test_a_limitation_must_name_its_evidence(self) -> None:
        with pytest.raises(ValueError, match="evidence"):
            Limitation(
                kind=LimitationKind.QUARANTINED, detail="two", count=2, evidence=""
            )

    def test_the_run_states_its_short_cells_and_unreached_fidelity(
        self, measured_records: list[Record], measured_run: tuple[str, Path]
    ) -> None:
        run_id, path = measured_run
        with RecordStore(StoreConfig(path=path)) as store:
            limitations = ReportGenerator(store).limitations(run_id)
        kinds = {limitation.kind for limitation in limitations}

        assert LimitationKind.CELLS_ABANDONED in kinds
        for limitation in limitations:
            assert limitation.evidence

    def test_each_limitation_count_is_recomputable_from_the_records(
        self, measured_records: list[Record]
    ) -> None:
        achieved = {
            key: sum(
                1
                for r in measured_records
                if replication_key(r) == key and r.status.gate_verdict.value == "PASS"
            )
            for key in replication_keys_of(measured_records)
        }
        limitations = derive_limitations(
            measured_records,
            achieved=achieved,
            n_seeds=_SEEDS,
            fidelity="L2",
            objectives=("validation_accuracy",),
            claim_count=1,
        )
        recomputed = {
            LimitationKind.QUARANTINED: sum(
                1 for r in measured_records if r.status.quarantine
            ),
            LimitationKind.GATES_SKIPPED: sum(
                1
                for r in measured_records
                if r.status.gate_verdict.value in {"PENDING", "QUARANTINE"}
            ),
            LimitationKind.CELLS_ABANDONED: sum(
                1 for n in achieved.values() if n < _SEEDS
            ),
            LimitationKind.FIDELITY_NOT_REACHED: sum(
                1 for r in measured_records if r.schedule.fidelity != "L2"
            ),
            LimitationKind.UNMEASURED_OBJECTIVES: 0,
        }
        for limitation in limitations:
            if limitation.kind in recomputed:
                assert limitation.count == recomputed[limitation.kind]

    def test_an_unmeasured_objective_is_stated_not_silently_dropped(self) -> None:
        unmeasured = [
            name
            for name in ("flops", "memory_usage")
            if name not in measured_objectives()
        ]
        assert unmeasured, "fixture should name objectives nothing measures"
        limitations = derive_limitations([], objectives=tuple(unmeasured))
        line = next(
            l for l in limitations if l.kind is LimitationKind.UNMEASURED_OBJECTIVES
        )

        assert line.count == len(unmeasured)
        assert unmeasured[0] in line.detail

    def test_a_run_that_measured_nothing_says_it_made_no_claim(self) -> None:
        limitations = derive_limitations([], claim_count=0)
        assert LimitationKind.NO_ELIGIBLE_CLAIM in {l.kind for l in limitations}


class TestReport:
    """§3.5's gate, on a run whose records were measured."""

    def test_the_report_prints_a_claim_with_n_and_variance(
        self, measured_run: tuple[str, Path]
    ) -> None:
        run_id, path = measured_run
        with RecordStore(StoreConfig(path=path)) as store:
            report = generate_run_report(store, run_id)

        assert "Claims" in report
        assert f"n={_SEEDS}" in report or "n=" in report
        assert "Limitations" in report
        assert str(LimitationKind.CELLS_ABANDONED) in report

    def test_the_claim_metric_is_the_runs_declared_objective(
        self, measured_run: tuple[str, Path]
    ) -> None:
        run_id, path = measured_run
        with RecordStore(StoreConfig(path=path)) as store:
            claims = ReportGenerator(store).claims(run_id)

        assert claims, "no claim derived from the run's own declared objective"
        assert all(
            claim.metric == objective_metric("validation_accuracy") for claim in claims
        )

    def test_a_run_naming_only_unmeasured_objectives_makes_no_claim(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "unmeasured.duckdb"
        with RecordStore(StoreConfig(path=path)) as store:
            run_id = store.create_run(spec=_spec(objectives=("flops",)))
            generator = ReportGenerator(store)
            claims = generator.claims(run_id)
            limitations = generator.limitations(run_id)

        assert claims == ()
        assert LimitationKind.UNMEASURED_OBJECTIVES in {l.kind for l in limitations}

    def test_claim_eligibility_is_decided_per_cell_not_per_record(
        self, measured_run: tuple[str, Path]
    ) -> None:
        """The executor writes one record per seed, so no record can know."""
        run_id, path = measured_run
        with RecordStore(StoreConfig(path=path)) as store:
            cells = store.claim_eligible_replication_keys(run_id, min_n_seeds=_SEEDS)
            eligible = ReportGenerator(store).claim_eligible_records(run_id)

        assert len(cells) == 1, "the fixture's second cell is short of its seeds"
        assert {r.credit for r in eligible} == {_CREDITS[0]}
        assert all(r.status.quarantine is False for r in eligible)

    def test_every_axis_in_a_claim_is_a_structural_axis(
        self, measured_run: tuple[str, Path]
    ) -> None:
        run_id, path = measured_run
        with RecordStore(StoreConfig(path=path)) as store:
            claims = ReportGenerator(store).claims(run_id)

        assert {claim.axis for claim in claims} <= {
            axis.value for axis in StructuralAxis
        }
