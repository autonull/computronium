import json

import pytest
from pydantic import ValidationError

from computronium.ceec import StoreError, models
from computronium.ceec.migrate import todo18_records
from computronium.ceec.probe_adapter import ingest_verdict, record_probe_result


class TestStructuredEvidence:
    def test_curve_result_cannot_be_scalar_only(self, store, scope):
        with pytest.raises(ValidationError, match="structured"):
            store.record_evidence("curve", scope, no_artifact_justification="trust me")

    def test_tensor_result_preserves_axes(self, store, scope):
        artifact = store.ingest_artifact(b"tensor", "result")
        ev = store.record_evidence(
            "tensor",
            scope,
            [artifact.id],
            axes=["depth", "seed"],
            values_ref=artifact.uri,
        )
        assert store.get_evidence(ev.id).axes == ["depth", "seed"]

    def test_invalid_coordinate_produces_inert(self, store):
        output = {
            "status": "inert",
            "kind": "scalar",
            "scope": {"domain": "probe"},
            "values": None,
            "notes": "invalid coordinate: recurrent geometry needs energy dynamics",
        }
        result = record_probe_result(store, output, "probe-x")
        assert result.evidence.kind == "inert"
        assert result.evidence.notes

    def test_infrastructure_failure_produces_missing(self, store):
        output = {
            "status": "missing",
            "kind": "scalar",
            "scope": {"domain": "probe"},
            "values": None,
        }
        output["notes"] = "OOM during execution"
        result = record_probe_result(store, output, "probe-y")
        assert result.evidence.kind == "missing"

    def test_missing_artifact_justification_required(self, store, scope):
        with pytest.raises(StoreError, match="no_artifact_justification"):
            store.record_evidence("scalar", scope)

    def test_inert_auto_documents_notes(self, store):
        output = {
            "status": "inert",
            "kind": "scalar",
            "scope": {"domain": "probe"},
            "values": None,
        }
        result = record_probe_result(store, output, "probe-z")
        assert "inert" in result.evidence.notes
        assert result.evidence.kind == "inert"

    def test_structured_probe_preserves_kind_and_axes(self, store):
        output = {
            "status": "ok",
            "kind": "curve",
            "scope": {"domain": "probe", "substrate": ["digital"]},
            "axes": ["step"],
            "values": {"loss": [1.0, 0.9, 0.8]},
            "quality": {"seeds": 3, "matched_control": True},
            "summary": {"final_loss": 0.8},
        }
        result = record_probe_result(store, output, "probe-curve")
        assert result.evidence.kind == "curve"
        assert result.evidence.axes == ["step"]
        assert result.derived is not None
        assert result.derived.value == {"final_loss": 0.8}
        artifacts = store.evidence_artifacts(result.evidence.id)
        assert artifacts == [result.artifact.id]

    def test_summary_becomes_derived_not_primary(self, store):
        output = {
            "status": "ok",
            "kind": "tensor",
            "scope": {"domain": "probe"},
            "axes": ["a", "b"],
            "values": [[1.0]],
            "summary": {"mean": 1.0},
            "summary_operator": "mean",
        }
        result = record_probe_result(store, output, "probe-tensor")
        assert result.derived is not None
        assert result.derived.operator == "mean"
        assert result.evidence.kind == "tensor"


class TestTodo18Migration:
    def test_claim_records_migrated_as_artifact_evidence_derived(
        self, store, tmp_path, monkeypatch
    ):
        fake = tmp_path / "claim_record.json"
        fake.write_text(json.dumps({"claim": "slice works", "status": "verified"}))
        monkeypatch.setattr(
            todo18_records,
            "TODO18_CLAIM_RECORDS",
            [(str(fake), "test_campaign")],
        )
        ids = todo18_records.migrate_claim_records(store)
        assert len(ids) == 1
        ev = store.get_evidence(ids[0])
        assert ev.quality["migrated"] is True
        artifacts = store.evidence_artifacts(ev.id)
        assert len(artifacts) == 1

    def test_corrections_migrated(self, store, tmp_path, monkeypatch):
        (tmp_path / "docs").mkdir()
        corrections = tmp_path / "docs" / "CORRECTIONS.md"
        corrections.write_text("# Corrections\n- defect: aliasing bug fixed")
        monkeypatch.setattr(todo18_records, "_repo_root", lambda: tmp_path)
        evidence_id = todo18_records.migrate_corrections_log(store)
        assert evidence_id is not None
        ev = store.get_evidence(evidence_id)
        assert ev.kind == "event"

    def test_missing_files_skipped(self, store, tmp_path, monkeypatch):
        monkeypatch.setattr(todo18_records, "_repo_root", lambda: tmp_path)
        result = todo18_records.migrate_all(store)
        assert result["claim_records"] == []
        assert result["corrections"] is None


class TestIngestVerdict:
    def _belief(self, store, scope):
        artifact = store.ingest_artifact(b"bootstrap", "config")
        return store.create_belief(
            "temporal psi credit",
            "mechanism",
            scope,
            evidence_refs=[
                store.record_evidence(
                    "vector", scope, [artifact.id], axes=["a"], values_ref=artifact.uri
                ).id
            ],
        ).id

    def test_governance_loop_links_updates_and_audits(self, store, scope):
        belief_id = self._belief(store, scope)
        store.pre_register_experiment(
            models.Experiment(
                id="X-T-001",
                question="q",
                rationale="r",
                scope=scope,
                target_beliefs=[belief_id],
                target_goals=[],
                design={"seed_plan": "3", "evaluation_policy": "e"},
                prediction="temporal credit helps",
                controls=["frozen_null"],
                metrics=["b_final"],
                budget="quick",
                falsification_criterion="no gain",
                overturn_criterion="closed-form matches return",
                hard_gates=["coordinate_valid"],
                created_at="2026-09-10",
            )
        )
        verdict = ingest_verdict(
            store,
            probe_name="X-T-001",
            probe_output={
                "status": "ok",
                "kind": "tensor",
                "axes": ["arm", "seed"],
                "values": {"temporal": [0.1, 0.2]},
                "quality": {"seeds": 3, "verification_level": 4},
            },
            belief_id=belief_id,
            new_interval=(0.30, 0.60),
            rationale="probe verdict",
            outcome="supported",
            outcome_boolean=True,
            notes="test",
        )
        assert verdict.probe.derived is None
        assert store.latest_revision(belief_id).probability.low == 0.30
        assert verdict.calibration is None  # no pre-registered probability
        assert verdict.violations == []
        assert [r.gate for r in verdict.evaluation.results]
