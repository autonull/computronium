"""The dashboard's write actions (TODO68).

The drawer used to carry three disabled buttons. They are now real: the
dashboard can measure the seeds a cell still owes, register the protocol a
confirming run must meet, and adopt an unmeasured cell as a question. These
tests pin what each verb does, and the honesty rule that keeps a
registration written after a run started from confirming that run.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from computronium.experiment.execution.campaign_queue import CampaignQueue
from computronium.experiment.execution.dashboard.actions import (
    KIND_CONFIRMATION,
    KIND_QUEST,
    CellTarget,
    cell_spec,
    claim_sentence,
    measurement_budget,
    registration_name,
    registration_payload,
    write_registration,
)
from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)
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
from computronium.experiment.schema.seed_registries import seed_all_registries

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
    """The registries the actions read through."""
    seed_all_registries()


def _spec(n_seeds: int = 5) -> RunSpec:
    return RunSpec(
        profile="demo",
        task="digits",
        objectives=("validation_accuracy",),
        fidelity="L1",
        n_seeds=n_seeds,
        epochs=1,
        budget_seconds=120.0,
    )


def _record(run_id: str, val_acc: float, seed: int, walltime: float = 3.0) -> Record:
    return Record.create(
        run_id=run_id,
        coordinate=Coordinate(**COORDINATE, params={}),
        schedule=Schedule(
            fidelity="L1",
            seed=seed,
            n_seeds=1,
            epochs=1,
            batch_limit=0,
            budget_id="dashboard-test",
            task_id="digits",
            param_budget=0,
        ),
        provenance=Provenance(
            env={"python": "3.14", "platform": "linux"},
            dataset="digits",
            dataset_version="1.0",
            code_sha="dashboard-test",
            policy="dashboard-test",
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
        payload={"val_acc": val_acc, "walltime_s": walltime, "param_count": 1024},
    )


@pytest.fixture
def store_with_run(tmp_path: Path):
    """A store holding one run with five measured seeds of one cell."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    path = tmp_path / "run.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=_spec())
        for seed in range(5):
            store.append(_record(run_id, 0.40 + 0.02 * seed, seed))
    return path, run_id


class TestReplication:
    """The replication is the run's own declaration, narrowed and grown."""

    def test_the_plan_grows_and_the_axes_are_pinned(self) -> None:
        from computronium.experiment.schema.axis import StructuralAxis

        source = _spec(n_seeds=5)
        target = CellTarget(run_id="run-1", coordinate=COORDINATE)

        spec = cell_spec(source, target, seeds=63, budget_seconds=300.0)

        assert spec.n_seeds == 63
        assert spec.selected_primitives(StructuralAxis.CREDIT) == ("gradient",)
        assert spec.selected_primitives(StructuralAxis.GEOMETRY) == ("feedforward",)
        assert spec.budget_seconds == 300.0
        assert spec.task_names == ("digits",)

    def test_the_budget_covers_the_missing_work(self) -> None:
        """Three seconds a seed, fifty-eight seeds, and room to be slower."""
        assert measurement_budget(3.0, 58) == pytest.approx(261.0)

    def test_the_budget_is_never_zero(self) -> None:
        assert measurement_budget(0.0, 0) >= 1.0


class TestRegistration:
    """A registration is the system's own contract, written down."""

    def test_the_payload_carries_the_contract(self) -> None:
        target = CellTarget(run_id="run-1", coordinate=COORDINATE)

        payload = registration_payload(
            target,
            claim="the cell beats chance",
            metric="val_acc",
            threshold=0.3,
            alpha=0.05,
            min_seeds=63,
            kind=KIND_CONFIRMATION,
        )

        assert payload["claim"] == "the cell beats chance"
        assert payload["metric"] == "val_acc"
        assert payload["threshold"] == 0.3
        assert payload["alpha"] == 0.05
        assert payload["min_seeds"] == 63
        assert payload["created"]
        assert payload["registered_at"]
        assert payload["coordinate"] == COORDINATE
        assert payload["run_id"] == "run-1"

    def test_writing_leaves_an_identical_registration_alone(
        self, tmp_path: Path
    ) -> None:
        target = CellTarget(run_id="run-1", coordinate=COORDINATE)
        payload = registration_payload(
            target,
            claim="the cell beats chance",
            metric="val_acc",
            threshold=0.3,
            alpha=0.05,
            min_seeds=63,
            kind=KIND_CONFIRMATION,
        )

        path, written = write_registration(tmp_path, payload, name="reg")
        again, rewritten = write_registration(tmp_path, payload, name="reg")

        assert written is True
        assert rewritten is False
        assert again == path
        assert json.loads(path.read_text(encoding="utf-8"))["metric"] == "val_acc"

    def test_a_different_registration_is_refused(self, tmp_path: Path) -> None:
        target = CellTarget(run_id="run-1", coordinate=COORDINATE)
        first = registration_payload(
            target,
            claim="the cell beats chance",
            metric="val_acc",
            threshold=0.3,
            alpha=0.05,
            min_seeds=63,
            kind=KIND_CONFIRMATION,
        )
        second = registration_payload(
            target,
            claim="the cell beats chance twice",
            metric="val_acc",
            threshold=0.4,
            alpha=0.05,
            min_seeds=63,
            kind=KIND_CONFIRMATION,
        )

        write_registration(tmp_path, first, name="reg")

        with pytest.raises(FileExistsError):
            write_registration(tmp_path, second, name="reg")

    def test_the_claim_states_the_absolute_target(self) -> None:
        target = CellTarget(run_id="run-1", coordinate=COORDINATE)

        sentence = claim_sentence(
            target,
            metric="val_acc",
            task="digits",
            chance=0.1,
            threshold=0.344,
            min_seeds=63,
            kind=KIND_CONFIRMATION,
        )

        assert "0.444 val_acc" in sentence
        assert "0.100 plus 0.344" in sentence
        assert "63 seeds" in sentence

    def test_the_name_says_which_cell(self) -> None:
        target = CellTarget(run_id="run-1", coordinate=COORDINATE)

        name = registration_name(target, KIND_QUEST)

        assert name.startswith("run-1_quest_")
        assert "credit-gradient" in name


def _dashboard(
    store_path: Path,
    queue: CampaignQueue | None,
    registration_dir: Path | None = None,
) -> WebDashboard:
    """A dashboard over one store, with the queue it acts through."""
    return WebDashboard(
        DashboardConfig(
            store_path=str(store_path),
            campaign_queue=queue,
            registration_dir=registration_dir,
            enable_websockets=False,
        )
    )


class TestEndpoints:
    """The three verbs, as the drawer calls them."""

    def test_queue_rest_measures_the_seeds_the_cell_owes(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        path, run_id = store_with_run
        queue = CampaignQueue(max_concurrent=0)
        dashboard = _dashboard(path, queue)

        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/replicate",
                json={"coordinate": COORDINATE},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["run_id"] == run_id
        assert body["campaign_id"]
        assert body["measurements"] == 58
        assert body["plan"] == 63

        queued = queue._queue[0]
        assert queued.spec.runs[0].run_id == run_id
        assert queued.spec.runs[0].spec_file is not None

    def test_queue_rest_without_a_queue_is_refused(
        self,
        store_with_run: tuple[Path, str],
    ) -> None:
        path, run_id = store_with_run
        dashboard = _dashboard(path, None)

        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/replicate",
                json={"coordinate": COORDINATE},
            )

        assert response.status_code == 409
        assert "queue" in response.json()["error"]

    def test_queue_rest_for_an_unknown_run_is_refused(self, tmp_path: Path) -> None:
        path = tmp_path / "empty.duckdb"
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        with RecordStore(StoreConfig(path=path)):
            pass
        dashboard = _dashboard(path, CampaignQueue(max_concurrent=0))

        with TestClient(dashboard.app) as client:
            response = client.post(
                "/api/cells/nope/replicate",
                json={"coordinate": COORDINATE},
            )

        assert response.status_code == 409
        assert "not in the store" in response.json()["error"]

    def test_preregister_registers_the_effect_the_cell_showed(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        path, run_id = store_with_run
        registry = tmp_path / "preregistrations"
        dashboard = _dashboard(path, None, registration_dir=registry)

        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/preregister",
                json={"coordinate": COORDINATE},
            )

        assert response.status_code == 200
        body = response.json()
        registration = body["registration"]
        assert registration["metric"] == "val_acc"
        assert registration["threshold"] == pytest.approx(0.44 - 0.1)
        assert registration["min_seeds"] == 63
        assert registration["alpha"] == 0.05
        assert body["written"] is True
        assert (
            registry
            / f"{registration_name(CellTarget(run_id, COORDINATE), KIND_CONFIRMATION)}.json"
        ).exists()

    def test_preregister_refuses_a_cell_with_no_measurement(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        path, run_id = store_with_run
        dashboard = _dashboard(path, None, registration_dir=tmp_path / "regs")

        other = {**COORDINATE, "credit": "pepita"}
        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/preregister",
                json={"coordinate": other},
            )

        assert response.status_code == 409
        assert "quest" in response.json()["error"]

    def test_quest_registers_the_question_an_unmeasured_cell_answers(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        path, run_id = store_with_run
        registry = tmp_path / "preregistrations"
        dashboard = _dashboard(path, None, registration_dir=registry)

        other = {**COORDINATE, "credit": "pepita"}
        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/quest",
                json={"coordinate": other},
            )

        assert response.status_code == 200
        registration = response.json()["registration"]
        assert registration["kind"] == KIND_QUEST
        assert registration["threshold"] > 0.0
        assert registration["min_seeds"] == 63
        assert "before any measurement" in registration["claim"]

    def test_quest_refuses_a_cell_that_is_already_measured(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        path, run_id = store_with_run
        dashboard = _dashboard(path, None, registration_dir=tmp_path / "regs")

        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/quest",
                json={"coordinate": COORDINATE},
            )

        assert response.status_code == 409
        assert "preregister" in response.json()["error"]


class TestTheQuestIsAnswered:
    """A question with no run behind it is a note, not a question."""

    def _quest(
        self,
        store_path: Path,
        run_id: str,
        registry: Path,
        queue: CampaignQueue | None,
    ) -> dict:
        dashboard = _dashboard(store_path, queue, registration_dir=registry)
        other = {**COORDINATE, "credit": "pepita"}
        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/quest",
                json={"coordinate": other},
            )
        assert response.status_code == 200
        return response.json()

    def test_the_quest_queues_the_run_that_would_answer_it(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        path, run_id = store_with_run
        queue = CampaignQueue(max_concurrent=0)

        body = self._quest(path, run_id, tmp_path / "regs", queue)

        assert body["scheduled"] is True
        assert body["campaign_id"]
        assert body["measurements"] == 63
        assert body["plan"] == 63
        assert body["budget_seconds"] > 0.0

        queued = queue._queue[0]
        assert queued.spec.runs[0].run_id is None
        assert queued.spec.runs[0].spec_file is not None

    def test_the_answering_run_is_a_new_one(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        """A threshold written now cannot confirm a run that has begun."""
        path, run_id = store_with_run
        queue = CampaignQueue(max_concurrent=0)

        self._quest(path, run_id, tmp_path / "regs", queue)

        assert queue._queue[0].spec.runs[0].run_id is None

    def test_the_budget_is_measured_from_the_run(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        """The run's own seeds say what a measurement costs."""
        path, run_id = store_with_run
        queue = CampaignQueue(max_concurrent=0)

        body = self._quest(path, run_id, tmp_path / "regs", queue)

        # Three seconds a seed, sixty-three seeds, and room to be slower.
        assert body["budget_seconds"] == pytest.approx(3.0 * 63 * 1.5)

    def test_without_a_queue_the_question_is_registered_and_nothing_is_scheduled(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        path, run_id = store_with_run
        registry = tmp_path / "regs"

        body = self._quest(path, run_id, registry, None)

        assert body["scheduled"] is False
        assert body["campaign_id"] is None
        assert "queue" in body["note"]
        assert body["written"] is True
        assert list(registry.glob("*.json"))

    def test_the_registration_says_the_cell_and_the_seeds(
        self,
        store_with_run: tuple[Path, str],
        tmp_path: Path,
    ) -> None:
        path, run_id = store_with_run
        registry = tmp_path / "regs"

        body = self._quest(path, run_id, registry, None)

        registration = body["registration"]
        assert registration["kind"] == KIND_QUEST
        assert registration["min_seeds"] == 63
        assert registration["coordinate"]["credit"] == "pepita"
        assert "before any measurement" in registration["claim"]


class TestRunContinuity:
    """A replication continues its run, so the seeds join its evidence."""

    def test_the_store_records_the_changed_declaration(self, tmp_path: Path) -> None:
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        path = tmp_path / "run.duckdb"
        with RecordStore(StoreConfig(path=path)) as store:
            run_id = store.create_run(spec=_spec(n_seeds=5))
            store.update_run_spec(run_id, _spec(n_seeds=63))

            info = store.query_run(run_id)

        assert info is not None
        assert info.spec is not None
        assert info.spec.n_seeds == 63

    def test_updating_an_unknown_run_is_refused(self, tmp_path: Path) -> None:
        from computronium.experiment.evidence.store import (
            RecordStore,
            StoreConfig,
            StoreError,
        )

        path = tmp_path / "run.duckdb"
        with RecordStore(StoreConfig(path=path)) as store, pytest.raises(StoreError):
            store.update_run_spec("nope", _spec())

    @pytest.mark.asyncio
    async def test_the_campaign_yaml_carries_the_run(self) -> None:
        from computronium.experiment.execution.campaign import (
            CampaignRun,
            CampaignSpec,
            load_campaign,
        )
        from computronium.experiment.execution.campaign_queue import (
            CampaignQueue,
            CampaignQueueEntry,
        )

        spec = CampaignSpec(
            name="replicate",
            runs=[
                CampaignRun(
                    name="rest",
                    spec_file="declaration.json",
                    store="experiment.duckdb",
                    run_id="run-7",
                )
            ],
            store="experiment.duckdb",
        )
        queue = CampaignQueue()
        entry = CampaignQueueEntry(campaign_id="c1", spec=spec)

        path = await queue._write_campaign_yaml(entry)
        loaded = load_campaign(path)

        assert loaded.runs[0].run_id == "run-7"
        assert loaded.runs[0].spec_file == "declaration.json"


class TestConfirmationHonesty:
    """A threshold written after a run began cannot confirm that run."""

    def test_a_registration_written_later_does_not_confirm_the_run(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from datetime import datetime, timedelta

        from computronium.experiment.surface import report

        started = datetime(2026, 1, 1, 9, 0, 0)
        written = started + timedelta(hours=1)
        (tmp_path / "reg.json").write_text(
            json.dumps({
                "metric": "val_acc",
                "registered_at": written.isoformat(),
                "created": written.date().isoformat(),
            }),
            encoding="utf-8",
        )
        monkeypatch.setattr(report, "PREREGISTRATION_ROOT", tmp_path)
        report.registrations.cache_clear()

        try:
            assert "val_acc" not in report.preregistered_metrics(started, frozenset())
            assert "val_acc" in report.preregistered_metrics(
                written + timedelta(seconds=1),
                frozenset(),
            )
        finally:
            report.registrations.cache_clear()
