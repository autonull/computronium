"""Lock: I(C,U) trains on the campaign's measurements, and holds out honestly.

TODO51 §4's acceptance criterion is a held-out accuracy, and the model could
not reach one: `ICUModel.load_from_store` reads records the model itself wrote
(`payload["icu"]`), so the only records it could ever learn from were its own
output. Nothing connected a campaign's `val_acc` to a feature vector, which is
why §4 read "PENDING CAMPAIGN DATA" with the ingestion half missing too.

Two locks:

* **the path exists** — a campaign's records reach the model, features from the
  coordinate and the metric from the payload;
* **the split is inherited, not chosen** — the train/evaluate boundary comes
  from each record's own `provenance.data_origin`. If ingestion picked the
  moment to split, a caller could train on its held-out set; the leakage guard
  would still report clean because it reads the same tag.
"""

from __future__ import annotations

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.learning.icu import DataOrigin, ICUModel
from computronium.experiment.schema.coordinate import (
    Coordinate,
    Provenance,
    Schedule,
)
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)

_RUN = "icu-ingest"


def _provenance(origin: DataOrigin) -> Provenance:
    return Provenance(
        env={},
        dataset="digits",
        dataset_version="1.0",
        code_sha="test",
        policy="test",
        links={},
        data_origin=origin,
    )


def _status() -> Status:
    return Status(
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
    )


def _record(
    credit: str,
    update: str,
    origin: DataOrigin,
    accuracy: float,
    seed: int,
) -> Record:
    return Record.create(
        run_id=_RUN,
        coordinate=Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit=credit,
            update=update,
            params={"hidden_dim": 64},
        ),
        schedule=Schedule(
            fidelity="L0",
            seed=seed,
            n_seeds=1,
            epochs=1,
            batch_limit=1,
            budget_id="test",
        ),
        provenance=_provenance(origin),
        status=_status(),
        payload={
            "val_acc": accuracy,
            "val_loss": 1.0 - accuracy,
            "param_count": 4096,
            "walltime_s": 1.5,
        },
    )


_TRAINING = (
    ("gradient", 0.80),
    ("thermodynamic_contrast", 0.60),
    ("pepita", 0.70),
    ("random_projections", 0.50),
)
_EVALUATION = (
    ("gradient", 0.82),
    ("thermodynamic_contrast", 0.58),
    ("pepita", 0.72),
    ("random_projections", 0.52),
)


@pytest.fixture
def campaign_path(tmp_path):
    """A closed store holding exploration- and calibration-origin records."""
    path = tmp_path / "icu.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        store.create_run(_RUN, None)
        for seed in range(4):
            for credit, accuracy in _TRAINING:
                store.append(
                    _record(credit, "euclidean", DataOrigin.EXPLORATION, accuracy, seed)
                )
            for credit, accuracy in _EVALUATION:
                store.append(
                    _record(credit, "adam", DataOrigin.CALIBRATION, accuracy, seed)
                )
    return path


def test_a_campaigns_measurements_reach_the_model(campaign_path) -> None:
    model = ICUModel()
    with RecordStore(StoreConfig(path=campaign_path)) as store:
        model.ingest_measurements(store, _RUN)
    ingested = model.n_records

    assert ingested == 32, "every measured record carries val_acc"
    assert model.n_records == ingested
    features = {r.feature_vector.interaction_key for r in model._records}
    assert "gradient|euclidean" in features
    assert "gradient|adam" in features
    assert "pepita|euclidean" in features


def test_the_split_is_inherited_from_each_records_origin(campaign_path) -> None:
    model = ICUModel()
    with RecordStore(StoreConfig(path=campaign_path)) as store:
        model.ingest_measurements(store, _RUN)

    assert len(model.training_records) == 16, "exploration origin trains"
    assert len(model.evaluation_records) == 16, "calibration origin evaluates"
    for record in model.training_records:
        assert record.data_origin is DataOrigin.EXPLORATION
    for record in model.evaluation_records:
        assert record.data_origin is DataOrigin.CALIBRATION


def test_a_records_missing_the_metric_is_skipped_not_defaulted(campaign_path) -> None:
    """A substituted 0.0 would train the model on a measurement nobody took."""
    with RecordStore(StoreConfig(path=campaign_path)) as store:
        blind = Record.create(
            run_id=_RUN,
            coordinate=Coordinate(
                substrate="digital",
                geometry="feedforward",
                dynamics="instantaneous",
                plasticity="null",
                credit="muon",
                update="adam",
                params={},
            ),
            schedule=Schedule(
                fidelity="L0",
                seed=0,
                n_seeds=1,
                epochs=1,
                batch_limit=1,
                budget_id="test",
            ),
            provenance=_provenance(DataOrigin.EXPLORATION),
            status=_status(),
            payload={"status": "evaluated"},
        )
        store.append(blind)
        model = ICUModel()
        ingested = model.ingest_measurements(store, _RUN)

    assert ingested == 32, "the val_acc-less record contributes nothing"
    assert "muon|adam" not in {r.feature_vector.interaction_key for r in model._records}


def test_the_leakage_guard_sees_the_ingested_split(campaign_path) -> None:
    """The guard reads the same tag ingestion wrote, so it cannot be bypassed."""
    model = ICUModel()
    with RecordStore(StoreConfig(path=campaign_path)) as store:
        model.ingest_measurements(store, _RUN)
    audit = model.check_leakage()

    assert audit["training_origins"] == [DataOrigin.EXPLORATION.value]
    assert audit["evaluation_origins"] == [DataOrigin.CALIBRATION.value]
    assert audit["total_records"] == 32
    assert audit["leakage_detected"] is False


def test_held_out_accuracy_reports_on_evaluation_origins_only(campaign_path) -> None:
    model = ICUModel()
    with RecordStore(StoreConfig(path=campaign_path)) as store:
        model.ingest_measurements(store, _RUN)
    report = model.held_out_accuracy()

    assert report["status"] == "ok"
    assert report["n"] == 16, "the evaluation origins, not all 32"
    assert 0.0 <= report["exact_match_rate"] <= 1.0
    assert report["mean_absolute_error"] >= 0.0
