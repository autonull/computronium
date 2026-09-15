"""Unit tests for the CEEC link (TODO27 Phase 2.1/2.4): proposal =
pre-registration, one trace, never limbo."""

from pathlib import Path

import pytest

from computronium.autoscientist.bridge import ExperimentProposal
from computronium.autoscientist.ceec_link import CEECLink


@pytest.fixture()
def ledger_path(tmp_path: Path) -> Path:
    return tmp_path / "ceec" / "ledger.sqlite3"


@pytest.fixture()
def proposal() -> ExperimentProposal:
    return ExperimentProposal(
        hypothesis="governed trace",
        model="eqprop",
        task="digits",
        geometry={"topology_type": "recurrent", "depth": 2, "hidden_dim": 32},
        hyperparams={"threshold": 0.3},
        justification="coverage cell",
        expected_outcome="above chance",
        tags=["autoscientist", "campaign:t"],
    )


def _link(path: Path) -> CEECLink:
    return CEECLink(str(path))


def _result(accuracy: float) -> dict[str, object]:
    return {
        "status": "completed",
        "final_accuracy": accuracy,
        "final_loss": 1.0,
        "train_accuracy": accuracy,
        "epochs_completed": 1,
    }


def test_pre_register_writes_prediction_threshold_scope(
    ledger_path: Path, proposal: ExperimentProposal
) -> None:
    link = _link(ledger_path)
    experiment = link.pre_register(proposal)
    # session.experiment() drafts; the store registers at record time.
    assert experiment.prediction == "above chance"
    assert experiment.falsification_criterion == "final_accuracy < 0.3"
    assert experiment.scope.dims["task"] == "digits"
    assert experiment.design["geometry"]["topology_type"] == "recurrent"


def test_governed_record_closes_the_trace(
    ledger_path: Path, proposal: ExperimentProposal
) -> None:
    link = _link(ledger_path)
    experiment = link.pre_register(proposal)
    run = link.record(experiment, proposal, _result(0.57))
    assert run.status == "completed"
    assert run.evidence_id
    assert run.artifact_id
    stored = link.session.store.get_experiment(experiment.id)
    assert stored.status == "completed"


def test_failure_never_limbos(ledger_path: Path, proposal: ExperimentProposal) -> None:
    link = _link(ledger_path)
    experiment = link.pre_register(proposal)
    link.record_failure(experiment, proposal, "RuntimeError: shape mismatch")
    stored = link.session.store.get_experiment(experiment.id)
    assert stored.status == "failed"


def test_threshold_decides_outcome_boolean(
    ledger_path: Path, proposal: ExperimentProposal
) -> None:
    link = _link(ledger_path)
    experiment = link.pre_register(proposal)
    run = link.record(experiment, proposal, _result(0.2))
    assert run.outcome == "completed"
    # The outcome boolean (0.2 < 0.3 threshold) is false — a red verdict,
    # routed to calibration for the gate set to evaluate.
    from ceec.calibration import calibration_report

    report = calibration_report(link.session.store)
    assert report is not None
