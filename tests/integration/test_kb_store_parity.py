"""T21.3A.9 parity lock: KnowledgeBase on the ceec sqlite toolkit.

Schema parity with the hand-rolled original (tables, columns, entry
round-trip) plus toolkit behavior (user_version, in-place reopen).
"""

from __future__ import annotations

import sqlite3
from json import loads as json_loads

import pytest

from computronium.knowledge.entries import KnowledgeEntry
from computronium.knowledge.kb import KnowledgeBase, KnowledgeBaseConfig


@pytest.fixture
def store(tmp_path):
    return KnowledgeBase(
        KnowledgeBaseConfig(db_path=str(tmp_path / "kb.db"), auto_embed=False)
    )


def _entry(entry_id: str = "KB-T1") -> KnowledgeEntry:
    return KnowledgeEntry(
        id=entry_id,
        topic="Scaling",
        model_family="eqprop",
        finding="O(1) memory scaling",
        details="details",
        confidence=0.9,
        tags=["memory"],
        source="literature",
        metrics={"acc": 0.9},
        hyperparameters={"lr": 0.1},
        extra={"k": "v"},
    )


def test_schema_tables_and_version(store: KnowledgeBase) -> None:
    tables = {
        r[0]
        for r in store.conn.execute("select name from sqlite_master where type='table'")
    }
    assert {"knowledge", "experiments", "surrogates"} <= tables
    assert store.schema_version == 1
    columns = {r[1] for r in store.conn.execute("pragma table_info(knowledge)")}
    assert {
        "id",
        "topic",
        "model_family",
        "finding",
        "confidence",
        "tags",
        "timestamp",
        "source",
        "experiment_id",
        "metrics",
    } <= columns


def test_entry_round_trip(store: KnowledgeBase) -> None:
    store.add_entry(_entry())
    row = store.conn.execute(
        "select topic, model_family, confidence, tags, metrics from knowledge"
        " where id = 'KB-T1'"
    ).fetchone()
    assert dict(row) == {
        "topic": "Scaling",
        "model_family": "eqprop",
        "confidence": 0.9,
        "tags": '["memory"]',
        "metrics": '{"acc": 0.9}',
    }
    fetched = store.get_by_id("KB-T1")
    assert fetched is not None
    assert fetched.finding == "O(1) memory scaling"
    assert fetched.tags == ["memory"]


def test_experiment_round_trip(store: KnowledgeBase) -> None:
    experiment_id = store.add_experiment(
        name="n",
        model_family="eqprop",
        task="mnist",
        config={"lr": 0.1},
        metrics={"acc": 0.88},
    )
    experiment = store.get_experiment(experiment_id)
    assert experiment is not None
    assert experiment["model_family"] == "eqprop"
    assert json_loads(str(experiment["metrics"])) == {"acc": 0.88}
    assert (
        store.conn.execute(
            "select count(*) from knowledge where experiment_id = ?", (experiment_id,)
        ).fetchone()[0]
        == 1
    )


def test_in_place_reopen(tmp_path) -> None:
    path = str(tmp_path / "reopen.db")
    first = KnowledgeBase(KnowledgeBaseConfig(db_path=path, auto_embed=False))
    first.add_entry(_entry())
    first.close()
    second = KnowledgeBase(KnowledgeBaseConfig(db_path=path, auto_embed=False))
    assert second.schema_version == 1
    # 3 seed entries (loaded into the empty db by the first instance)
    # + the explicit entry; seed load skipped on reopen.
    assert second.conn.execute("select count(*) from knowledge").fetchone()[0] == 4


def test_unknown_schema_version_refused(tmp_path) -> None:
    from ceec.sqlite_toolkit import SchemaVersionError

    path = str(tmp_path / "future.db")
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA user_version = 99;")
    conn.commit()
    conn.close()
    with pytest.raises(SchemaVersionError, match="v99"):
        KnowledgeBase(KnowledgeBaseConfig(db_path=path, auto_embed=False))
