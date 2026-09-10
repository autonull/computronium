import pytest
from pydantic import ValidationError

from computronium.ceec import models


class TestProbability:
    def test_valid_interval(self):
        p = models.Probability(low=0.2, high=0.6, point=0.4, method="mid")
        assert p.point == 0.4

    def test_inverted_interval_rejected(self):
        with pytest.raises(ValidationError, match="inverted"):
            models.Probability(low=0.7, high=0.3)

    def test_point_outside_interval_rejected(self):
        with pytest.raises(ValidationError, match="outside interval"):
            models.Probability(low=0.2, high=0.6, point=0.9)


class TestEvidence:
    def test_structured_kind_requires_axes_and_ref(self, scope):
        with pytest.raises(ValidationError, match="structured"):
            models.Evidence(
                id="E-1", kind="tensor", scope=scope, created_at="2026-01-01"
            )

    def test_structured_kind_valid(self, scope):
        ev = models.Evidence(
            id="E-1",
            kind="curve",
            scope=scope,
            axes=["t"],
            values_ref="ceec/artifacts/x",
            created_at="2026-01-01",
        )
        assert ev.axes == ["t"]

    def test_inert_requires_notes(self, scope):
        with pytest.raises(ValidationError, match="notes"):
            models.Evidence(
                id="E-1", kind="inert", scope=scope, created_at="2026-01-01"
            )

    def test_missing_requires_notes(self, scope):
        with pytest.raises(ValidationError, match="notes"):
            models.Evidence(
                id="E-1", kind="missing", scope=scope, created_at="2026-01-01"
            )

    def test_invalid_id_prefix_rejected(self, scope):
        with pytest.raises(ValidationError, match="expected prefix"):
            models.Evidence(
                id="X-1", kind="scalar", scope=scope, created_at="2026-01-01"
            )


class TestStatusChange:
    def test_promotion_requires_gate_refs(self, scope):
        with pytest.raises(ValidationError, match="gate refs"):
            models.StatusChange(
                id="SC-1",
                belief_id="B-1",
                from_status="open",
                to_status="promoted",
                reason="r",
                created_at="2026-01-01",
            )

    def test_reopen_requires_trigger(self):
        with pytest.raises(ValidationError, match="trigger"):
            models.StatusChange(
                id="SC-1",
                belief_id="B-1",
                from_status="boundary",
                to_status="open",
                reason="r",
                created_at="2026-01-01",
            )

    def test_reopen_with_trigger_valid(self):
        sc = models.StatusChange(
            id="SC-1",
            belief_id="B-1",
            from_status="boundary",
            to_status="open",
            reason="r",
            trigger="strong_untested_mechanism",
            created_at="2026-01-01",
        )
        assert sc.trigger == "strong_untested_mechanism"


class TestCalibration:
    def test_brier_requires_point_probability(self):
        with pytest.raises(ValidationError, match="point probability"):
            models.CalibrationRecord(
                id="CAL-1", prediction="p", brier_score=0.1, created_at="2026-01-01"
            )

    def test_outcome_requires_predicted_probability(self):
        with pytest.raises(ValidationError, match="predicted probability"):
            models.CalibrationRecord(
                id="CAL-1",
                prediction="p",
                outcome_boolean=True,
                created_at="2026-01-01",
            )
