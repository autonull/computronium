"""The store's mirror: a live dashboard in another terminal (TODO68).

DuckDB's lock on a store is exclusive, so a dashboard in another process
cannot open a store a campaign is writing, and a campaign cannot open a store
a dashboard holds. The writer publishes a *mirror* — a consistent copy, swapped
in atomically — and a reader that cannot open the original reads the mirror.

These tests pin that contract in the two processes it is about: the writer
publishes, the reader reads, and neither waits for the other to finish.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence.mirror import (
    mirror_path,
    readable_store,
)
from computronium.experiment.evidence.store import (
    RecordStore,
    StoreConfig,
    StoreError,
)
from tests.unit.experiment.dashboard_store import demo_record, demo_spec

if TYPE_CHECKING:
    from pathlib import Path

# A reader in its own process: it reports where its picture came from.
READER = """
import json, sys
from pathlib import Path
from computronium.experiment.evidence.mirror import readable_store

with readable_store(Path(sys.argv[1])) as view:
    records = list(view.store.query_records())
    print(json.dumps({
        "source": view.source,
        "records": len(records),
        "published": view.published_at.isoformat() if view.published_at else None,
    }))
"""

# A reader that holds the file open, so the writer has to wait for it.
HOLDER = """
import sys, time
from pathlib import Path
from computronium.experiment.evidence.store import RecordStore, StoreConfig

with RecordStore(StoreConfig(path=Path(sys.argv[1]), read_only=True)):
    print("holding", flush=True)
    time.sleep(float(sys.argv[2]))
"""


def _read_in_another_process(path: Path) -> dict[str, object]:
    """What a reader in another process sees of the store."""
    result = subprocess.run(
        [sys.executable, "-c", READER, str(path)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


@pytest.fixture
def store_path(tmp_path: Path) -> Path:
    """A store path with no store on it yet."""
    return tmp_path / "run.duckdb"


class TestTheMirror:
    """What the writer publishes."""

    def test_the_writer_publishes_a_mirror(self, store_path: Path) -> None:
        target = mirror_path(store_path)

        with RecordStore(
            StoreConfig(path=store_path, mirror_path=target, mirror_interval=0.0)
        ) as store:
            run_id = store.create_run(spec=demo_spec())
            store.append(demo_record(run_id, 0.4, 0))

            assert target.exists()

    def test_the_mirror_holds_the_records_the_store_holds(
        self, store_path: Path
    ) -> None:
        target = mirror_path(store_path)

        with RecordStore(
            StoreConfig(path=store_path, mirror_path=target, mirror_interval=0.0)
        ) as store:
            run_id = store.create_run(spec=demo_spec())
            for seed in range(3):
                store.append(demo_record(run_id, 0.4 + 0.01 * seed, seed))

        with RecordStore(StoreConfig(path=target, read_only=True)) as mirror:
            assert len(list(mirror.query_records())) == 3

    def test_the_mirror_holds_the_record_that_was_just_appended(
        self, store_path: Path
    ) -> None:
        """A mirror that lags is a picture that lies about the run.

        The publish happens after every append, and the copy DuckDB makes on
        its own can fail: it copies the tables in an order of its own
        choosing, and the foreign key between the records and the runs
        refuses a copy that puts the records first. A failed publish leaves
        the mirror holding the picture before the last append.
        """
        target = mirror_path(store_path)

        with RecordStore(
            StoreConfig(path=store_path, mirror_path=target, mirror_interval=0.0)
        ) as store:
            run_id = store.create_run(spec=demo_spec())
            for seed in range(3):
                store.append(demo_record(run_id, 0.4 + 0.01 * seed, seed))
                with RecordStore(StoreConfig(path=target, read_only=True)) as mirror:
                    assert mirror.count_records() == seed + 1

    def test_a_store_that_publishes_nothing_writes_no_mirror(
        self, store_path: Path
    ) -> None:
        with RecordStore(StoreConfig(path=store_path)) as store:
            run_id = store.create_run(spec=demo_spec())
            store.append(demo_record(run_id, 0.4, 0))

        assert not mirror_path(store_path).exists()


class TestTheReader:
    """What a reader in another process sees."""

    def test_a_reader_reads_the_mirror_while_the_writer_writes(
        self, store_path: Path
    ) -> None:
        """The dashboard in the other terminal: the run, as of the last publish."""
        target = mirror_path(store_path)

        with RecordStore(
            StoreConfig(path=store_path, mirror_path=target, mirror_interval=0.0)
        ) as store:
            run_id = store.create_run(spec=demo_spec())
            for seed in range(3):
                store.append(demo_record(run_id, 0.4, seed))

            seen = _read_in_another_process(store_path)

        assert seen["source"] == "snapshot"
        assert seen["records"] == 3
        assert seen["published"]

    def test_a_reader_prefers_the_live_store_when_it_can_open_it(
        self, store_path: Path
    ) -> None:
        target = mirror_path(store_path)

        with RecordStore(
            StoreConfig(path=store_path, mirror_path=target, mirror_interval=0.0)
        ) as store:
            run_id = store.create_run(spec=demo_spec())
            store.append(demo_record(run_id, 0.4, 0))

        seen = _read_in_another_process(store_path)

        assert seen["source"] == "live"
        assert seen["records"] == 1

    def test_a_reader_with_nothing_to_read_is_told_so(self, store_path: Path) -> None:
        with (
            pytest.raises(StoreError, match="no mirror was published"),
            readable_store(store_path),
        ):
            pass


class TestTheWriterWaits:
    """A reader that holds the file must not stop a campaign."""

    def test_the_writer_waits_a_reader_out(self, store_path: Path) -> None:
        with RecordStore(StoreConfig(path=store_path)):
            pass

        holder = subprocess.Popen(
            [sys.executable, "-c", HOLDER, str(store_path), "2"],
            stdout=subprocess.PIPE,
            text=True,
        )
        try:
            assert holder.stdout is not None
            assert holder.stdout.readline().strip() == "holding"
            started = time.monotonic()
            with RecordStore(StoreConfig(path=store_path)) as store:
                run_id = store.create_run(spec=demo_spec())
                store.append(demo_record(run_id, 0.4, 0))
            waited = time.monotonic() - started
        finally:
            holder.wait(timeout=30)

        assert waited > 0.5
