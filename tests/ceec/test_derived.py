"""Derived operator registry + recomputation lock (TODO26 T26.F.1)."""

import pytest
from ceec.derived import OPERATORS, compute_derived
from ceec.profile import CORE_CONSTRAINTS, Profile
from ceec.session import ledger

from ceec import models

PROFILE = Profile(name="t", policy_version="26.0", constraints=CORE_CONSTRAINTS)


def _session(tmp_path):
    return ledger(tmp_path / "d.sqlite3", PROFILE)


def _evidence(sess, values):
    payload = (
        "{" + '"rows": [' + ", ".join(str(v) for v in values) + "]" + "}"
    ).encode()
    artifact = sess.store.ingest_artifact(payload, "evidence_payload")
    scope = models.Scope.of(domain="test")
    return sess.store.record_evidence(
        "vector",
        scope,
        artifact_refs=[artifact.id],
        axes=["trial"],
        values_ref=f"artifact:{artifact.id}",
    )


def test_mean_recomputes_byte_identically(tmp_path):
    with _session(tmp_path) as sess:
        ev = _evidence(sess, [0.1, 0.2, 0.3])
        derived = compute_derived(
            sess.store, "mean", {"a": [ev.id]}, scope=models.Scope.of(domain="test")
        )
        again = compute_derived(
            sess.store, "mean", {"a": [ev.id]}, scope=models.Scope.of(domain="test")
        )
        assert derived.value == again.value
        assert derived.value == pytest.approx(0.2)
        assert derived.provenance["recomputable"] is True


def test_contrast_relation(tmp_path):
    with _session(tmp_path) as sess:
        left = _evidence(sess, [0.9, 0.8])
        right = _evidence(sess, [0.4, 0.4])
        derived = compute_derived(
            sess.store,
            "contrast",
            {"left": [left.id], "right": [right.id]},
            scope=models.Scope.of(domain="test"),
        )
        assert derived.value == pytest.approx((0.9 + 0.8) / 2 - 0.4)


def test_chance_band_operator(tmp_path):
    with _session(tmp_path) as sess:
        ev = _evidence(sess, [0.501, 0.499, 0.5])
        derived = compute_derived(
            sess.store,
            "chance_band",
            {"accs": [ev.id]},
            scope=models.Scope.of(domain="test"),
            parameters={"n_eval": 100, "chance": 0.5},
        )
        assert derived.value is True


def test_registry_surface():
    for name in (
        "mean",
        "median",
        "spread",
        "contrast",
        "slope",
        "dominance",
        "replication",
        "chance_band",
    ):
        assert name in OPERATORS
        assert OPERATORS[name].kind in {"summary", "relation"}
