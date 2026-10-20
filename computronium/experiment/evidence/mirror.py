"""A consistent copy of the store, for readers that cannot open the original.

DuckDB's lock on a database file is exclusive, whichever way round it is taken:
a reader in another process cannot open a store a writer holds, and a writer
cannot open a store a reader holds. A live dashboard and a running campaign in
two terminals therefore see nothing of each other at all — the dashboard polls
an empty file, and the campaign cannot even start while the dashboard holds the
file open.

The writer is the only party that can take a consistent picture of the store
while it writes, so the writer publishes one. A *mirror* is a copy of the whole
database, taken inside a transaction and swapped in atomically: a reader sees
either the previous mirror or the new one, never half of either. A reader that
cannot open the original opens the mirror, and sees the run as of the last
publish.

The mirror is a copy, not a second truth: it holds the records the store holds,
and the store remains the record of account. A reader that can open the
original always prefers it.
"""

from __future__ import annotations

import contextlib
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Generator

    import duckdb

    from computronium.experiment.evidence.store import RecordStore

logger = logging.getLogger(__name__)

# The two ways a connection can be refused because somebody else holds the
# file. The first is another process; the second is this process, where DuckDB
# shares one instance per path and refuses a second configuration.
LOCK_HELD_ELSEWHERE = "conflicting lock"
CONFIGURATION_MISMATCH = "different configuration"


def mirror_path(path: Path) -> Path:
    """Where the mirror of a store lives.

    Args:
        path: The store's own path.

    Returns:
        The path the store's mirror is published to.
    """
    return path.with_name(f"{path.stem}.mirror{path.suffix}")


def is_lock_conflict(error: BaseException | None) -> bool:
    """Whether the error says somebody else holds the file.

    Both ways of being refused are a conflict: another process holds the lock,
    or this process holds it in the other configuration.
    """
    if error is None:
        return False
    message = str(error).lower()
    return LOCK_HELD_ELSEWHERE in message or CONFIGURATION_MISMATCH in message


def held_in_another_process(error: BaseException | None) -> bool:
    """Whether the error says another *process* holds the file.

    A configuration mismatch is this process: DuckDB shares one instance per
    path, and a read-only connection cannot join a read-write one.
    """
    if error is None:
        return False
    return LOCK_HELD_ELSEWHERE in str(error).lower()


def publish_mirror(conn: duckdb.DuckDBPyConnection, path: Path) -> None:
    """Publish a consistent copy of the database at ``path``.

    The copy is taken by DuckDB itself, inside the writer's own connection, so
    it is a consistent picture of the committed data and never a torn file. It
    is written beside the target and moved into place, so a reader never opens
    a half-written mirror.

    Args:
        conn: The writer's connection.
        path: Where the mirror is published.

    Raises:
        RuntimeError: The database could not be copied.
    """
    row = conn.execute("SELECT current_database()").fetchone()
    if row is None:
        msg = "the database did not name itself"
        raise RuntimeError(msg)
    source = str(row[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    staged = path.with_name(f"{path.name}.staged-{os.getpid()}")
    for stale in (staged, Path(f"{staged}.wal")):
        stale.unlink(missing_ok=True)

    conn.execute(f"ATTACH '{_quoted(str(staged))}' AS mirror (READ_WRITE)")
    try:
        conn.execute(f'COPY FROM DATABASE "{_quoted(source)}" TO mirror')
    finally:
        conn.execute("DETACH mirror")

    staged.replace(path)
    for stale in (Path(f"{staged}.wal"), Path(f"{path}.wal")):
        stale.unlink(missing_ok=True)


def _quoted(name: str) -> str:
    """A name safe to splice into a statement."""
    return name.replace("'", "''")


@dataclass(frozen=True, slots=True)
class StoreView:
    """A store opened for reading, and where it came from.

    The source is part of the answer: a picture taken from a snapshot says so,
    and says when the snapshot was taken.
    """

    store: RecordStore
    source: Literal["live", "snapshot"]
    published_at: datetime | None = None


@contextlib.contextmanager
def readable_store(path: Path) -> Generator[StoreView]:
    """Open a store for reading: the original, or the mirror its writer published.

    The original is preferred whenever it can be opened. A writer in another
    process holds the file for the whole run, so the mirror is the only picture
    available while it runs; a writer in this process cannot be joined by a
    read-only connection at all, and the read-write connection is the one that
    sees the run as it happens.

    Args:
        path: The store's path.

    Yields:
        The store, opened for reading, and where it came from.

    Raises:
        StoreError: The store could not be opened, and no mirror was published.
    """
    from computronium.experiment.evidence.store import (
        RecordStore,
        StoreConfig,
        StoreError,
    )

    live: RecordStore | None = None
    failure: Exception | None = None
    try:
        candidate = RecordStore(StoreConfig(path=path, read_only=True))
        candidate.__enter__()
    except Exception as exc:  # ruff: ignore[blind-except] - the reason decides what to try next
        failure = exc
    else:
        live = candidate

    if live is not None:
        try:
            yield StoreView(store=live, source="live")
        finally:
            live.__exit__(None, None, None)
        return

    if path.exists() and not held_in_another_process(failure):
        # The writer is this process: DuckDB shares one instance per path and
        # refuses a read-only connection to a path a read-write one holds.
        writer_here: RecordStore | None = None
        try:
            writer_here = RecordStore(StoreConfig(path=path, read_only=False))
            writer_here.__enter__()
        except Exception as exc:  # ruff: ignore[blind-except] - the mirror may still answer
            logger.debug("Store %s could not be opened read-write: %s", path, exc)
            writer_here = None
        if writer_here is not None:
            try:
                yield StoreView(store=writer_here, source="live")
            finally:
                writer_here.__exit__(None, None, None)
            return

    mirror = mirror_path(path)
    if mirror.exists():
        store = RecordStore(StoreConfig(path=mirror, read_only=True))
        with store:
            yield StoreView(
                store=store,
                source="snapshot",
                published_at=datetime.fromtimestamp(mirror.stat().st_mtime),
            )
        return

    msg = f"store {path} could not be opened and no mirror was published: {failure}"
    raise StoreError(msg)


__all__ = [
    "CONFIGURATION_MISMATCH",
    "LOCK_HELD_ELSEWHERE",
    "StoreView",
    "held_in_another_process",
    "is_lock_conflict",
    "mirror_path",
    "publish_mirror",
    "readable_store",
]
