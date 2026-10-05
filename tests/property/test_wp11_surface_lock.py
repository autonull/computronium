"""WP11 surface locks: intent persistence, exports, profiles, codegen, CLI.

L13 (intent records), L14 (public-API exports), R43 (question-first),
R80 (documented commands), R83 (alert dedup), R88 (handoff), codegen drift.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

from computronium.experiment.evidence.store import (
    DuplicateMeasurementError,
    RecordStore,
    StoreConfig,
)
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.surface import cli
from computronium.experiment.surface.operations import (
    DEFAULT_Q14_ROUTES,
    AlertDedup,
    OperatorIntentKind,
    create_operator_intent,
    default_events_for,
)
from computronium.experiment.surface.profiles import (
    QUESTION_FIRST_STAGES,
    question_first,
)
from computronium.experiment.surface.report import (
    export_to_json,
    narrative_handoff_summary,
)
from computronium.experiment.surface.service import (
    poll_control_file,
    write_control_intent,
)


@pytest.fixture(autouse=True)
def _seed() -> None:
    seed_all_registries()


@pytest.fixture
def _store(tmp_path: Path) -> Iterator[RecordStore]:
    store = RecordStore(StoreConfig(path=tmp_path / "wp11.duckdb"))
    store.__enter__()
    try:
        yield store
    finally:
        store.__exit__(None, None, None)


def _intent_dict(intent_id: str = "intent-1") -> dict[str, object]:
    return {
        "intent_id": intent_id,
        "kind": OperatorIntentKind.PAUSE.value,
        "payload": {},
        "timestamp": "2026-09-30T00:00:00",
        "operator": "test",
        "reason": "lock",
    }


class TestIntentPersistence:
    def test_round_trip(self, _store: RecordStore) -> None:
        run_id = _store.create_run(spec=RunSpec(task="digits", profile="test"))
        record = _store.record_intent(run_id, _intent_dict())
        assert record.payload["kind"] == "operator_intent"
        found = _store.query_intent_records(run_id)
        assert len(found) == 1
        assert found[0].record_id == record.record_id

    def test_redelivery_dedups(self, _store: RecordStore) -> None:
        run_id = _store.create_run(spec=RunSpec(task="digits", profile="test"))
        _store.record_intent(run_id, _intent_dict())
        with pytest.raises(DuplicateMeasurementError):
            _store.record_intent(run_id, _intent_dict())

    def test_run_scoping(self, _store: RecordStore) -> None:
        run_a = _store.create_run(spec=RunSpec(task="digits", profile="a"))
        run_b = _store.create_run(spec=RunSpec(task="digits", profile="b"))
        _store.record_intent(run_a, _intent_dict("intent-a"))
        assert len(_store.query_intent_records(run_a)) == 1
        assert len(_store.query_intent_records(run_b)) == 0
        assert len(_store.query_intent_records()) == 1


class TestPublicExports:
    def test_snapshot_keys_serializable(self, _store: RecordStore) -> None:
        run_id = _store.create_run(spec=RunSpec(task="digits", profile="test"))
        _store.record_intent(run_id, _intent_dict())
        snapshot = _store.export_snapshot(run_id)
        assert set(snapshot) == {"records", "runs", "artifacts", "vector_index"}
        assert len(snapshot["records"]) == 1
        assert len(snapshot["runs"]) == 1
        json.dumps(snapshot, default=str)

    def test_export_json_round_trip(self, _store: RecordStore, tmp_path: Path) -> None:
        run_id = _store.create_run(spec=RunSpec(task="digits", profile="test"))
        _store.record_intent(run_id, _intent_dict())
        out = export_to_json(_store, tmp_path / "bundle.json", run_id)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["metadata"]["record_count"] == 1
        assert data["records"][0]["payload"]["kind"] == "operator_intent"

    def test_handoff_mentions_intents(self, _store: RecordStore) -> None:
        run_id = _store.create_run(spec=RunSpec(task="digits", profile="test"))
        _store.record_intent(run_id, _intent_dict())
        text = narrative_handoff_summary(_store, run_id)
        assert "Operator intents on record: 1" in text
        assert "pause" in text


class TestQuestionFirst:
    def test_spec_shape(self) -> None:
        spec = question_first("validation_accuracy", "digits", {"budget_seconds": 60})
        assert spec.profile == "question_first"
        assert spec.policy == "synthesis"
        assert spec.objectives == ("validation_accuracy",)
        assert spec.stages == QUESTION_FIRST_STAGES
        assert spec.task_names == ("digits",)
        assert spec.budget_seconds == 60.0

    def test_unknown_objective_rejected(self) -> None:
        with pytest.raises(ValueError, match="unknown objective"):
            question_first("not_an_objective", "digits")

    def test_unknown_operating_point_field_rejected(self) -> None:
        with pytest.raises(ValueError, match="unknown field"):
            question_first("validation_accuracy", "digits", {"epochs": 2, "lr": 0.1})

    def test_write_only_keys_are_not_spec_fields(self) -> None:
        # data_origin_allocation and contrast_quota are S3 *stage* params;
        # a spec that carries them is dead config the stages never read.
        with pytest.raises(ValueError, match="data_origin_allocation"):
            RunSpec.model_validate({
                "task": "digits",
                "data_origin_allocation": {"exploration": 0.6},
            })


class TestDocumentedCommands:
    @pytest.mark.parametrize(
        "argv",
        (
            ["run", "--help"],
            ["report", "--help"],
            ["export", "--help"],
            ["conformance", "--help"],
            ["status", "--help"],
        ),
    )
    def test_commands_parse(self, argv: list[str]) -> None:
        with pytest.raises(SystemExit) as exc:
            cli.main(argv)
        assert exc.value.code == 0

    def test_run_profiles_canonical_stages(self) -> None:
        for name, profile in cli.RUN_PROFILES.items():
            assert profile.stages, name
            for stage in profile.stages:
                assert stage in QUESTION_FIRST_STAGES, (name, stage)


class TestAlertsAndControl:
    def test_dedup_window(self) -> None:
        dedup = AlertDedup(window_seconds=3600.0)
        assert dedup.should_fire("divergence", "run-1")
        assert not dedup.should_fire("divergence", "run-1")
        assert dedup.should_fire("divergence", "run-2")
        assert dedup.should_fire("stagnation", "run-1")

    def test_q14_routes_cover_alerts(self) -> None:
        assert set(default_events_for("operator")) >= {"run_completed", "run_failed"}
        for event, groups in DEFAULT_Q14_ROUTES.items():
            assert groups, event

    def test_control_file_round_trip(self, tmp_path: Path) -> None:
        control = tmp_path / "control.jsonl"
        write_control_intent(control, OperatorIntentKind.PAUSE, {}, "op-1", "why")
        intents = poll_control_file(control, "run-1")
        assert len(intents) == 1
        assert intents[0].kind == OperatorIntentKind.PAUSE
        assert intents[0].run_id == "run-1"
        assert poll_control_file(control, "run-1") == []

    def test_operator_intent_factory(self) -> None:
        intent = create_operator_intent("run-1", OperatorIntentKind.SNAPSHOT, {})
        assert intent.run_id == "run-1"
        assert intent.intent_id
