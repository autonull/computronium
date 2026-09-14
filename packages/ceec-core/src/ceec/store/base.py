"""Store base: connection lifecycle and shared internals."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Self

from ceec.profile import LedgerRole, Profile
from ceec.store.schema import _APPEND_ONLY, _SCHEMA, StoreError, _additive_migrate

if TYPE_CHECKING:
    from collections.abc import Iterator


class StoreBase:
    """Connection, identity allocation, and row access internals."""

    db_path: Path
    artifacts_dir: Path
    role: LedgerRole
    profile: Profile | None
    _conn: sqlite3.Connection

    def __init__(
        self,
        db_path: Path | str,
        artifacts_dir: Path | str,
        *,
        role: LedgerRole | str = LedgerRole.MAIN,
        profile: Profile | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.artifacts_dir = Path(artifacts_dir)
        self.role = LedgerRole(role)
        self.profile = profile
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        _additive_migrate(self._conn)
        for table in _APPEND_ONLY:
            for action in ("UPDATE", "DELETE"):
                self._conn.execute(
                    f"CREATE TRIGGER IF NOT EXISTS {table}_no_{action.lower()} "
                    f"BEFORE {action} ON {table} BEGIN "
                    f"SELECT RAISE(ABORT, '{table} is append-only'); END"
                )
        self._conn.execute(
            "INSERT OR IGNORE INTO ledger_meta VALUES ('role', ?)", (self.role.value,)
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def commit(self) -> None:
        """Flush pending writes (public flush for multi-call ingest blocks)."""
        self._conn.commit()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        self.close()

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def _next_id(self, kind: str, table: str, explicit: str | None) -> str:
        from ceec.ids import prefix_for

        if explicit is not None:
            return explicit
        sql = f"SELECT COUNT(*) AS n FROM {table}"  # noqa: S608  internal prefix map
        row = self._conn.execute(sql).fetchone()
        return f"{prefix_for(kind)}-{row['n'] + 1:06d}"

    def _fetch(self, table: str, id_: str) -> sqlite3.Row:
        row = self._conn.execute(
            f"SELECT * FROM {table} WHERE id = ?",  # noqa: S608  internal
            (id_,),
        ).fetchone()
        if row is None:
            raise StoreError(
                f"{table[:-1] if table.endswith('s') else table} {id_!r} not found"
            )
        return row

    def _require(self, table: str, id_: str | None) -> None:
        if id_ is None:
            raise StoreError(f"missing required reference into {table}")
        row = self._conn.execute(
            f"SELECT 1 FROM {table} WHERE id = ?",  # noqa: S608  internal
            (id_,),
        ).fetchone()
        if row is None:
            raise StoreError(f"referenced row missing in {table}: {id_!r}")

    def _has_links(self, belief_id: str, *link_tables: tuple[str, str]) -> bool:
        for table, col in link_tables:
            row = self._conn.execute(
                f"SELECT 1 FROM {table} WHERE belief_id = ? LIMIT 1",  # noqa: S608
                (belief_id,),
            ).fetchone()
            if row is not None:
                return True
        return False

    @staticmethod
    def _link(
        conn: sqlite3.Connection,
        table: str,
        left_col: str,
        left_id: str,
        right_col: str,
        right_ids: list[str] | None,
    ) -> None:
        if not right_ids:
            return
        sql = f"INSERT OR IGNORE INTO {table} ({left_col}, {right_col}) VALUES (?, ?)"  # noqa: S608  internal
        conn.executemany(sql, [(left_id, rid) for rid in right_ids])
