"""Store-level tests: append-only guarantees and artifact hash stability."""

from __future__ import annotations

import sqlite3

import pytest

from ceec import CEECStore, StoreError, models


@pytest.fixture()
def store():
    import tempfile
    from pathlib import Path

    with (
        tempfile.TemporaryDirectory() as tmp,
        CEECStore(Path(tmp) / "ceec.sqlite3", Path(tmp) / "artifacts") as s,
    ):
        yield s


def test_append_only_tables_reject_mutation(store: CEECStore) -> None:
    store.ingest_artifact(b"payload", "blob")
    db = sqlite3.connect(store.db_path)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE artifacts SET type = 'tampered'")


def test_artifact_hash_stable(store: CEECStore) -> None:
    import hashlib

    artifact = store.ingest_artifact(b"payload", "blob")
    assert artifact.sha256 == hashlib.sha256(b"payload").hexdigest()


def test_duplicate_id_rejected(store: CEECStore) -> None:
    store.ingest_artifact(b"payload-a", "blob", id_="A-000001")
    with pytest.raises(sqlite3.IntegrityError):
        store.ingest_artifact(b"payload-b", "blob", id_="A-000001")


def test_invalid_reference_rejected(store: CEECStore) -> None:
    scope = models.Scope(domain="credit", credit=("gradient",))
    with pytest.raises(StoreError):
        store.record_evidence(
            kind="vector",
            scope=scope,
            artifact_refs=["A-999999"],
            axes=["a"],
            values_ref="A-999999",
        )
