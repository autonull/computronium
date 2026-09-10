import shutil

import pytest

from computronium.ceec import CEECStore, models


@pytest.fixture
def store(tmp_path):
    with CEECStore(tmp_path / "ceec.sqlite3", tmp_path / "artifacts") as s:
        yield s


@pytest.fixture
def scope():
    return models.Scope(domain="probe", substrate=("digital",), budget="quick")


@pytest.fixture
def evidence(store, scope):
    artifact = store.ingest_artifact(b"probe-output", "result", {"probe": "test"})
    return store.record_evidence(
        "vector",
        scope,
        [artifact.id],
        axes=["seed", "metric"],
        values_ref=artifact.uri,
        quality={"verification_level": 4},
    )


def link_belief(store, scope, evidence, belief_id="B-T1"):
    store.create_belief(
        "test hypothesis",
        "mechanism",
        scope,
        id_=belief_id,
        evidence_refs=[evidence.id],
    )
    store.update_belief(
        belief_id,
        models.Probability(low=0.2, high=0.6),
        "high",
        "low",
        "narrow",
        "open",
        "bootstrap",
    )
    return belief_id


shutil  # re-exported for tests that clean artifact dirs
