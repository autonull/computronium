"""Shared sqlite-store plumbing (TODO21 T21.3A.9 toolkit).

Single source for the schema-versioned store pattern that
``computronium.core.campaign.campaign_store`` pioneered (frozen
``MIGRATIONS`` map applied via ``user_version``) and the transaction
contextmanager ``ceec.store`` ships. Stores migrate onto this base
store-by-store with parity locks; prefixed-id generation (``ceec.store``)
stays opt-in and is NOT imposed here.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from ceec.store import StoreError

if TYPE_CHECKING:
    from collections.abc import Generator

__all__ = ["SchemaVersionError", "SqliteStore"]


class SchemaVersionError(StoreError):
    """The database's schema version is not in the store's migration map."""


class SqliteStore:
    """Schema-versioned sqlite store base.

    Subclasses declare a frozen ``MIGRATIONS`` map ``{version: DDL}``;
    version 1 creates the initial schema and later versions mutate it.
    ``user_version`` records the applied version, so existing databases
    migrate in place.
    """

    MIGRATIONS: ClassVar[dict[int, str]] = {}
    JOURNAL_MODE: ClassVar[str] = "WAL"

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        if self.JOURNAL_MODE:
            self.conn.execute(f"PRAGMA journal_mode={self.JOURNAL_MODE};")
        self._apply_migrations()

    def _apply_migrations(self) -> None:
        if not self.MIGRATIONS:
            raise SchemaVersionError(
                f"{type(self).__name__} declares no MIGRATIONS map"
            )
        current = self.schema_version
        if current and current not in self.MIGRATIONS:
            raise SchemaVersionError(
                f"database schema v{current} unknown to "
                f"{type(self).__name__} (known: {sorted(self.MIGRATIONS)})"
            )
        for version in sorted(self.MIGRATIONS):
            if version > current:
                self.conn.executescript(self.MIGRATIONS[version])
                self.conn.execute(f"PRAGMA user_version = {version};")
                self.conn.commit()

    @property
    def schema_version(self) -> int:
        """Applied schema version of the connected database."""
        return int(self.conn.execute("PRAGMA user_version;").fetchone()[0])

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection]:
        """Commit on success, roll back on error."""
        try:
            yield self.conn
            self.conn.commit()
        except BaseException:
            self.conn.rollback()
            raise
