import pytest

from computronium.ceec import StoreError, gates


def make_instrument_chain(store, scope):
    instrument = store.create_belief(
        "instrument works", "instrument", scope, id_="I-TEST", evidence_refs=[]
    )
    evidence = store.ingest_artifact(b"chain", "result")
    ev = store.record_evidence(
        "scalar", scope, [evidence.id], notes="direct observation"
    )
    mid = store.create_belief(
        "depends on instrument", "mechanism", scope, id_="B-MID", evidence_refs=[ev.id]
    )
    leaf = store.create_belief(
        "depends on mid", "mechanism", scope, id_="B-LEAF", evidence_refs=[ev.id]
    )
    store._conn.executemany(
        "INSERT INTO belief_dependencies VALUES (?, ?)",
        [(mid.id, instrument.id), (leaf.id, mid.id)],
    )
    store._conn.commit()
    return instrument, mid, leaf


class TestQuarantinePropagation:
    def test_unknown_trigger_rejected(self, store, scope):
        instrument, _, _ = make_instrument_chain(store, scope)
        with pytest.raises(StoreError, match="unknown quarantine trigger"):
            gates.quarantine(store, instrument.id, "suspicion", "no evidence")

    def test_propagates_transitively(self, store, scope):
        instrument, mid, leaf = make_instrument_chain(store, scope)
        changes = gates.quarantine(
            store, instrument.id, "estimator_mislabeled", "bad label source"
        )
        assert len(changes) == 3
        assert store.current_status(instrument.id) == "quarantined"
        assert store.current_status(mid.id) == "quarantined"
        assert store.current_status(leaf.id) == "quarantined"
        assert "propagated quarantine from I-TEST" in changes[-1].reason
        assert changes[0].belief_id == instrument.id

    def test_idempotent_requarantine(self, store, scope):
        instrument, _, _ = make_instrument_chain(store, scope)
        gates.quarantine(store, instrument.id, "audit_incomplete", "gap")
        changes = gates.quarantine(
            store, instrument.id, "config_provenance_mismatch", "second defect"
        )
        assert changes == []

    def test_dependent_blocked_while_quarantined(self, store, scope):
        instrument, mid, leaf = make_instrument_chain(store, scope)
        gates.quarantine(
            store, instrument.id, "known_defect_affects_measurement", "defect"
        )
        assert gates.effective_status(store, mid.id).effective == "quarantined"
        assert gates.effective_status(store, leaf.id).effective == "quarantined"
        lifted = gates.unquarantine(store, instrument.id, "audit completed, no defect")
        assert len(lifted) == 3
        assert gates.effective_status(store, mid.id).effective == "open"
        assert gates.effective_status(store, leaf.id).effective == "open"

    def test_unquarantine_requires_quarantined(self, store, scope):
        _, mid, _ = make_instrument_chain(store, scope)
        with pytest.raises(StoreError, match="not quarantined"):
            gates.unquarantine(store, mid.id, "nothing to lift")

    def test_material_scope_only_direct_quarantine(self, store, scope):
        instrument, mid, _ = make_instrument_chain(store, scope)
        gates.quarantine(store, instrument.id, "live_patch_unverified", "unverified")
        assert gates.effective_status(store, mid.id).quarantined_by == (instrument.id,)


class TestStaleDependencies:
    def test_content_change_marks_stale(self, store, scope):
        from computronium.ceec import models

        instrument, mid, _ = make_instrument_chain(store, scope)
        artifact = store.ingest_artifact(b"instr-ev", "result")
        ev = store.record_evidence(
            "vector", scope, [artifact.id], axes=["seed"], values_ref=artifact.uri
        )
        store._link(
            store._conn,
            "belief_evidence",
            "belief_id",
            instrument.id,
            "evidence_id",
            [ev.id],
        )
        store._conn.commit()
        store.update_belief(
            instrument.id,
            models.Probability(low=0.2, high=0.5),
            "high",
            "low",
            "narrow",
            "open",
            "initial calibration",
        )
        store.update_belief(
            mid.id,
            models.Probability(low=0.3, high=0.6),
            "medium",
            "low",
            "narrow",
            "open",
            "revision based on instrument content A",
        )
        store.update_belief(
            instrument.id,
            models.Probability(low=0.5, high=0.9),
            "medium",
            "medium",
            "narrow",
            "open",
            "instrument recalibrated",
        )
        eff = gates.effective_status(store, mid.id)
        assert instrument.id in eff.stale_by

    def test_status_flip_alone_not_stale(self, store, scope):
        instrument, mid, _ = make_instrument_chain(store, scope)
        gates.quarantine(store, instrument.id, "audit_incomplete", "gap")
        gates.unquarantine(store, instrument.id, "resolved later")
        assert gates.effective_status(store, mid.id).stale_by == ()
