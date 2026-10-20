"""What the dashboard says about itself (TODO69).

The narration is the dashboard's account of itself, in sentences. These tests
pin the *rules* it must obey — it speaks in words rather than figures, it
keeps an account, an agent can read it without a browser — and not the exact
wording, which is expected to move as the phrasing is tuned.
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

import pytest
from fastapi.testclient import TestClient

from computronium.experiment.execution.dashboard.narration import (
    Narration,
    best_cell,
    event_sentence,
    state_sentences,
)
from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)

if TYPE_CHECKING:
    from pathlib import Path

COORDINATE = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}


@pytest.fixture(autouse=True)
def _registries() -> None:
    """The registries the dashboard reads through."""
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()


def _record(credit: str, val_acc: float, seed: int) -> dict[str, Any]:
    """One record, as the API serves it."""
    return {
        "record_id": f"r{seed}",
        "coordinate": {**COORDINATE, "credit": credit},
        "payload": {"val_acc": val_acc, "walltime_s": 1.0},
    }


def _event(stage: str, message: str, **kwargs: Any):
    from computronium.experiment.execution.events import PipelineEvent

    return PipelineEvent(stage=stage, message=message, **kwargs)


def _metrics() -> dict[str, Any]:
    """The metrics payload of a run that measured two arms."""
    return {
        "records": [
            _record("gradient", 0.40, 0),
            _record("gradient", 0.44, 1),
            _record("pepita", 0.51, 0),
        ],
        "run": {
            "run_id": "run-1",
            "profile": "demo",
            "tasks": ["digits"],
            "fidelity": "L1",
            "mode": "EXPLORATORY",
            "status": "running",
            "declared_cells": 4,
        },
        "chance": 0.1,
        "required_seeds": 63,
        "resources": {"seeds_per_arm": 5, "records": 3},
        "store": {"source": "live"},
    }


class TestItSpeaksInWords:
    """A voice-over that recites numbers is worse than one that does not."""

    @pytest.mark.parametrize(
        "event",
        [
            _event("s6_train", "train cells: 4 proposals", detail={"proposals": 4}),
            _event(
                "s7_measure",
                "gradient/feedforward/instantaneous seed 3: val_acc 0.412",
                detail={
                    "cell": "gradient/feedforward/instantaneous",
                    "seed": 3,
                    "val_acc": 0.412,
                },
            ),
            _event("campaign", "queued quest-abc"),
            _event("s4_gate", "gate proposals", detail={"proposals": 2}),
        ],
    )
    def test_a_sentence_reads_no_figures(self, event: Any) -> None:
        sentence = event_sentence(event)

        assert sentence
        assert sentence.endswith(".")
        assert not any(character.isdigit() for character in sentence)

    def test_the_state_reads_no_figures(self) -> None:
        for sentence in state_sentences(_metrics(), {"running": 1, "queued": 2}):
            for figure in ("0.51", "0.40", "63", "0.10"):
                assert figure not in sentence


class TestItSaysWhatItFound:
    """The narration knows which cell leads."""

    def test_the_best_cell_is_the_one_that_scored_highest(self) -> None:
        records = [
            _record("gradient", 0.40, 0),
            _record("gradient", 0.44, 1),
            _record("pepita", 0.51, 0),
            _record("pepita", 0.53, 1),
        ]

        best = best_cell(records)
        assert best is not None
        name, mean, spread, seeds = best

        assert name == "pepita"
        assert mean == pytest.approx(0.52)
        assert spread == pytest.approx(0.0141421, abs=1e-6)
        assert seeds == 2

    def test_no_records_is_no_best_cell(self) -> None:
        assert best_cell([]) is None

    def test_the_state_is_two_sentences(self) -> None:
        sentences = state_sentences(_metrics(), {"running": 1, "queued": 2})

        assert len(sentences) == 2
        assert all(sentence.endswith(".") for sentence in sentences)

    def test_a_dashboard_with_nothing_to_say_says_so(self) -> None:
        sentences = state_sentences({})

        assert len(sentences) == 2
        assert all(sentence for sentence in sentences)


class TestTheAccount:
    """The account keeps the moments and the present."""

    def test_an_event_becomes_a_line(self) -> None:
        narration = Narration()

        line = narration.event(_event("campaign", "queued quest-abc"))

        assert line.text
        assert narration.latest() is line
        assert len(narration.lines()) == 1

    def test_the_script_is_the_present_then_the_history(self) -> None:
        narration = Narration()
        narration.state(("The demo run is exploratory.", "Two cells measured."))
        narration.event(_event("campaign", "queued quest-abc"))

        script = narration.script()

        assert script.startswith("The demo run is exploratory. Two cells measured.")
        assert len(script.splitlines()) == 2

    def test_the_account_remembers_only_what_it_can_hold(self) -> None:
        narration = Narration(history=3)

        for index in range(5):
            narration.event(_event("campaign", f"queued quest-{index}"))

        assert len(narration.lines()) == 3


class TestTheEndpoint:
    """A reader without a browser can ask what is happening."""

    def test_the_endpoint_answers_with_the_account(self, tmp_path: Path) -> None:
        from computronium.experiment.evidence.store import RecordStore, StoreConfig
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
        from computronium.experiment.schema.run_spec import RunSpec

        path = tmp_path / "run.duckdb"
        spec = RunSpec(
            profile="demo",
            task="digits",
            objectives=("validation_accuracy",),
            fidelity="L1",
            n_seeds=2,
            epochs=1,
        )
        with RecordStore(StoreConfig(path=path)) as store:
            run_id = store.create_run(spec=spec)
            for seed in range(2):
                store.append(
                    Record.create(
                        run_id=run_id,
                        coordinate=Coordinate(**COORDINATE, params={}),
                        schedule=Schedule(
                            fidelity="L1",
                            seed=seed,
                            n_seeds=1,
                            epochs=1,
                            batch_limit=0,
                            budget_id="narration-test",
                            task_id="digits",
                            param_budget=0,
                        ),
                        provenance=Provenance(
                            env={"python": "3.14", "platform": "linux"},
                            dataset="digits",
                            dataset_version="1.0",
                            code_sha="narration-test",
                            policy="narration-test",
                            links={"run_id": run_id},
                        ),
                        status=Status(
                            gate_verdict=GateVerdict.PASS_,
                            defect="",
                            cause=FailureCause.UNKNOWN,
                            severity=Severity.LOW,
                            quarantine=False,
                            maturity=Maturity.L1,
                            uncertainty={},
                            reproducibility=ReproducibilityClass.REPLAYABLE,
                            assessment_procedure_version="1.0",
                            ceec_link=None,
                        ),
                        payload={"val_acc": 0.4 + 0.02 * seed, "walltime_s": 1.0},
                    )
                )

        dashboard = WebDashboard(DashboardConfig(store_path=str(path)))
        with TestClient(dashboard.app) as client:
            response = client.get("/api/narration")

        assert response.status_code == 200
        body = response.json()
        assert "state" in body
        assert "lines" in body
        assert "script" in body
        assert json.dumps(body)


class TestARunThatHasNotMeasuredYet:
    """The dashboard shows the run it is watching, before the evidence.

    A dashboard that shows nothing until the work is done has forgotten the
    run it is watching: the run's declaration is enough to draw its space,
    and the absence of evidence is the truth about it.
    """

    def _empty_run(self, tmp_path: Path) -> tuple[Path, str]:
        """A store holding a run that has measured nothing yet."""
        from computronium.experiment.evidence.store import RecordStore, StoreConfig
        from computronium.experiment.schema.run_spec import RunSpec

        path = tmp_path / "empty.duckdb"
        spec = RunSpec(
            profile="demo",
            task="digits",
            objectives=("validation_accuracy",),
            fidelity="L1",
            n_seeds=2,
            epochs=1,
        )
        with RecordStore(StoreConfig(path=path)) as store:
            return path, store.create_run(spec=spec)

    def test_the_run_still_names_itself(self, tmp_path: Path) -> None:
        path, run_id = self._empty_run(tmp_path)
        dashboard = WebDashboard(DashboardConfig(store_path=str(path)))

        metrics = asyncio.run(dashboard._get_campaign_metrics_detailed(run_id))

        assert metrics["records"] == []
        assert metrics["run"]["run_id"] == run_id
        assert metrics["run"]["profile"] == "demo"
        assert metrics["run"]["mode"] == "EXPLORATORY"
        assert metrics["resources"]["records"] == 0

    def test_the_narration_says_it_has_measured_nothing(self, tmp_path: Path) -> None:
        path, run_id = self._empty_run(tmp_path)
        dashboard = WebDashboard(DashboardConfig(store_path=str(path)))

        metrics = asyncio.run(dashboard._get_campaign_metrics_detailed(run_id))
        sentences = state_sentences(metrics, None)

        assert "nothing yet" in sentences[0]
        assert all(sentence.endswith(".") for sentence in sentences)
