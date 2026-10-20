"""Schema creation under a catalog conflict (TODO68).

A dashboard reading a store a campaign is writing opens a second connection
to the same file. When the store is fresh, both connections try to create its
schema and one of them loses the race with a catalog write-write conflict.
The loser must wait and try again — the store's DDL is all ``IF NOT EXISTS``,
so the retry converges.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import duckdb
import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig

if TYPE_CHECKING:
    from pathlib import Path


def test_a_second_connection_to_a_fresh_store_both_open(tmp_path: Path) -> None:
    """Two connections to the same new store: the second finds the schema."""
    path = tmp_path / "fresh.duckdb"

    with RecordStore(StoreConfig(path=path)) as first:
        assert first.is_open
        with RecordStore(StoreConfig(path=path)) as second:
            assert second.is_open


def test_schema_creation_survives_a_catalog_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The connection that loses the race waits and creates the schema."""
    attempts = {"count": 0}
    original = RecordStore._create_schema_objects

    def flaky(self: RecordStore) -> None:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise duckdb.TransactionException("Catalog write-write conflict")
        original(self)

    monkeypatch.setattr(RecordStore, "_create_schema_objects", flaky)

    with RecordStore(StoreConfig(path=tmp_path / "raced.duckdb")) as store:
        assert store.is_open
        assert attempts["count"] == 2


def test_a_conflict_that_never_clears_is_raised(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A store that cannot be created fails loudly instead of hanging."""

    def always_conflicts(self: RecordStore) -> None:
        raise duckdb.TransactionException("Catalog write-write conflict")

    monkeypatch.setattr(RecordStore, "_create_schema_objects", always_conflicts)

    with (
        pytest.raises(duckdb.TransactionException),
        RecordStore(StoreConfig(path=tmp_path / "never.duckdb")),
    ):
        pass
