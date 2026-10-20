"""What the dashboard says about itself (TODO69).

The narration is the dashboard's account of itself, in sentences: what just
happened, and what the state of the system is. These tests pin the sentences
and the endpoint, because a sentence a reader cannot check against the panels
is a decoration, not a narration.
"""

from __future__ import annotations

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


class TestTheSentences:
    """Every sentence names a thing a reader can check."""

    def test_a_stage_says_what_it_did_and_how_many(self) -> None:
        sentence = event_sentence(
            _event("s6_train", "train cells: 4 proposals", detail={"proposals": 4})
        )

        assert sentence == "Stage 6 — train cells: 4 proposals."

    def test_a_measurement_names_the_cell_the_seed_and_the_number(self) -> None:
        sentence = event_sentence(
            _event(
                "s7_measure",
                "gradient/feedforward/instantaneous seed 3: val_acc 0.412",
                detail={
                    "cell": "gradient/feedforward/instantaneous",
                    "seed": 3,
                    "val_acc": 0.412,
                },
            )
        )

        assert sentence == (
            "Measured gradient/feedforward/instantaneous, seed 3: val_acc 0.412."
        )

    def test_a_measurement_carries_the_chance_it_is_read_against(self) -> None:
        sentence = event_sentence(
            _event(
                "s7_measure",
                "gradient/feedforward/instantaneous seed 0: val_acc 0.412",
                detail={
                    "cell": "gradient/feedforward/instantaneous",
                    "seed": 0,
                    "val_acc": 0.412,
                },
            ),
            chance=0.1,
        )

        assert "chance 0.10" in sentence

    def test_a_campaign_says_what_happened_to_it(self) -> None:
        sentence = event_sentence(_event("campaign", "queued quest-abc"))

        assert sentence == "Campaign queued quest-abc."

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

    def test_a_cell_with_one_seed_has_no_spread(self) -> None:
        best = best_cell([_record("gradient", 0.4, 0)])
        assert best is not None
        name, mean, spread, seeds = best

        assert name == "gradient"
        assert mean == pytest.approx(0.4)
        assert spread == 0.0
        assert seeds == 1


class TestTheState:
    """The summary says which run this is and what it holds."""

    def _metrics(self) -> dict[str, Any]:
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
            },
            "chance": 0.1,
            "required_seeds": 63,
            "resources": {"seeds_per_arm": 5, "records": 3},
            "store": {"source": "live"},
        }

    def test_the_first_sentence_names_the_run_and_what_it_holds(self) -> None:
        first, _ = state_sentences(self._metrics())

        assert "demo" in first
        assert "digits" in first
        assert "EXPLORATORY" in first
        assert "2 cells measured" in first
        assert "3 records" in first

    def test_the_second_sentence_says_what_the_numbers_mean(self) -> None:
        _, second = state_sentences(self._metrics(), {"running": 1, "queued": 2})

        assert "Best cell: pepita" in second
        assert "0.510" in second
        assert "Chance 0.10" in second
        assert "58 more seeds needed for a claim" in second
        assert "1 running" in second
        assert "Picture: live" in second

    def test_a_dashboard_with_nothing_to_say_says_so(self) -> None:
        first, second = state_sentences({})

        assert "No run" in first
        assert second


class TestTheAccount:
    """The account keeps the moments and the present."""

    def test_an_event_becomes_a_line(self) -> None:
        narration = Narration()

        line = narration.event(_event("campaign", "queued quest-abc"))

        assert line.text == "Campaign queued quest-abc."
        assert narration.latest() is line
        assert len(narration.lines()) == 1

    def test_the_script_is_the_present_then_the_history(self) -> None:
        narration = Narration()
        narration.state(("Run demo — EXPLORATORY.", "Two cells measured."))
        narration.event(_event("campaign", "queued quest-abc"))

        script = narration.script()

        assert script.startswith("Run demo — EXPLORATORY. Two cells measured.")
        assert "Campaign queued quest-abc." in script

    def test_the_account_remembers_only_what_it_can_hold(self) -> None:
        narration = Narration(history=3)

        for index in range(5):
            narration.event(_event("campaign", f"queued quest-{index}"))

        assert len(narration.lines()) == 3
        assert narration.lines()[-1].text == "Campaign queued quest-4."


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
