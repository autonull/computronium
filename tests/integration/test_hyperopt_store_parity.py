"""T21.3A.9 parity lock: HyperoptStorage on the ceec sqlite toolkit.

Schema parity with the hand-rolled original (tables, columns, trial
round-trip) plus toolkit behavior (user_version, in-place reopen).
"""

from __future__ import annotations

import sqlite3

import pytest

from computronium.hyperopt.storage import HyperoptStorage


@pytest.fixture
def store(tmp_path):
    return HyperoptStorage(str(tmp_path / "hyperopt.db"))


def test_schema_tables_and_version(store: HyperoptStorage) -> None:
    tables = {
        r[0]
        for r in store.conn.execute("select name from sqlite_master where type='table'")
    }
    assert {"hyperopt_logs", "training_trajectories", "training_checkpoints"} <= tables
    assert store.schema_version == 2
    columns = {r[1] for r in store.conn.execute("pragma table_info(hyperopt_logs)")}
    assert {
        "trial_id",
        "model_name",
        "config_json",
        "status",
        "timestamp",
        "is_pareto",
    } <= columns


def test_trial_round_trip(store: HyperoptStorage) -> None:
    trial_id = store.create_trial("model", {"lr": 0.1})
    store.update_trial(trial_id, status="done", final_loss=0.5)
    row = store.conn.execute(
        "select model_name, status, final_loss, config_json from hyperopt_logs"
        " where trial_id = ?",
        (trial_id,),
    ).fetchone()
    assert dict(row) == {
        "model_name": "model",
        "status": "done",
        "final_loss": 0.5,
        "config_json": '{"lr": 0.1}',
    }


def test_in_place_reopen(tmp_path) -> None:
    path = str(tmp_path / "reopen.db")
    first = HyperoptStorage(path)
    first.create_trial("m", {})
    first.conn.close()
    second = HyperoptStorage(path)
    assert second.schema_version == 2
    rows = second.conn.execute("select count(*) from hyperopt_logs").fetchone()
    assert rows[0] == 1


def test_unknown_schema_version_refused(tmp_path) -> None:
    from ceec.sqlite_toolkit import SchemaVersionError

    path = str(tmp_path / "future.db")
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA user_version = 99;")
    conn.commit()
    conn.close()
    with pytest.raises(SchemaVersionError, match="v99"):
        HyperoptStorage(path)
