"""UI state store — append-only sqlite sidecar (M2.2).

Replay from events reconstructs identical badges/quests/records.
Rebuildable via `comp dashboard --rebuild-ui-state`.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.ui.recognition.projector import RecognitionEvent, RecognitionState

_STATE_STORE_PATH = "ui_state.sqlite"
_SCHEMA_VERSION = 1


def get_state_store(root: Path | None = None) -> RecognitionStateStore:
    """Get or create the state store for a campaign root."""
    if root is None:
        root = Path("artifacts/broad_map")
    db_path = root / _STATE_STORE_PATH
    return RecognitionStateStore(db_path)


class RecognitionStateStore:
    """Append-only sqlite store for recognition state.

    Schema:
    - events: event log (kind, timestamp, payload_json, event_hash)
    - badges: earned badges (badge_id, earned_at, evidence_ref)
    - quests: quest progress (quest_id, opted_in, progress, completed_at)
    - records: personal bests (record_id, objective, value, cell_key, timestamp, scope)
    - fog_regions: charted regions (region, charted_at)
    - metadata: schema version, last_rebuild_at
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    payload_json TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    UNIQUE(event_hash)
                );

                CREATE TABLE IF NOT EXISTS badges (
                    badge_id TEXT PRIMARY KEY,
                    earned_at REAL NOT NULL,
                    evidence_ref TEXT
                );

                CREATE TABLE IF NOT EXISTS quests (
                    quest_id TEXT PRIMARY KEY,
                    opted_in INTEGER NOT NULL DEFAULT 0,
                    progress_current INTEGER NOT NULL DEFAULT 0,
                    completed_at REAL
                );

                CREATE TABLE IF NOT EXISTS records (
                    record_id TEXT PRIMARY KEY,
                    objective TEXT NOT NULL,
                    value REAL NOT NULL,
                    cell_key TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    scope TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS fog_regions (
                    region TEXT PRIMARY KEY,
                    charted_at REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_events_kind ON events(kind);
                CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_badges_earned_at ON badges(earned_at);
                CREATE INDEX IF NOT EXISTS idx_records_objective ON records(objective);
            """
            )
            # Set schema version
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("schema_version", str(_SCHEMA_VERSION)),
            )

    @contextmanager
    def _conn(self):
        """Thread-safe connection context manager."""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    # ──────────────────────────────────────────────────────────────────────────
    # Event log (append-only, idempotent by event_hash)
    # ──────────────────────────────────────────────────────────────────────────

    def append_event(self, event: RecognitionEvent) -> bool:
        """Append an event to the log.

        Returns True if inserted, False if duplicate (idempotent).
        """
        import hashlib

        payload_json = json.dumps(event.payload, sort_keys=True)
        event_hash = hashlib.sha256(f"{event.kind}{payload_json}".encode()).hexdigest()[
            :16
        ]

        with self._conn() as conn:
            try:
                conn.execute(
                    "INSERT INTO events (kind, timestamp, payload_json, event_hash) VALUES (?, ?, ?, ?)",
                    (event.kind, event.timestamp, payload_json, event_hash),
                )
            except sqlite3.IntegrityError:
                # Duplicate event_hash — idempotent
                return False
            else:
                return True

    def get_all_events(self) -> list[RecognitionEvent]:
        """Get all events in timestamp order."""
        from computronium.ui.recognition.projector import RecognitionEvent

        with self._conn() as conn:
            rows = conn.execute(
                "SELECT kind, timestamp, payload_json FROM events ORDER BY timestamp"
            ).fetchall()
            return [
                RecognitionEvent(
                    kind=row["kind"],
                    timestamp=row["timestamp"],
                    payload=json.loads(row["payload_json"]),
                )
                for row in rows
            ]

    def clear_events(self) -> None:
        """Clear all events (for rebuild)."""
        with self._conn() as conn:
            conn.execute("DELETE FROM events")

    # ──────────────────────────────────────────────────────────────────────────
    # Badges
    # ──────────────────────────────────────────────────────────────────────────

    def upsert_badge(
        self, badge_id: str, earned_at: float, evidence_ref: str | None = None
    ) -> None:
        """Insert or update a badge."""
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO badges (badge_id, earned_at, evidence_ref) VALUES (?, ?, ?)",
                (badge_id, earned_at, evidence_ref),
            )

    def get_badges(self) -> list[dict]:
        """Get all earned badges."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT badge_id, earned_at, evidence_ref FROM badges ORDER BY earned_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def clear_badges(self) -> None:
        """Clear all badges (for rebuild)."""
        with self._conn() as conn:
            conn.execute("DELETE FROM badges")

    # ──────────────────────────────────────────────────────────────────────────
    # Quests
    # ──────────────────────────────────────────────────────────────────────────

    def upsert_quest(
        self,
        quest_id: str,
        opted_in: bool,
        progress_current: int,
        completed_at: float | None = None,
    ) -> None:
        """Insert or update quest progress."""
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO quests (quest_id, opted_in, progress_current, completed_at) VALUES (?, ?, ?, ?)",
                (quest_id, 1 if opted_in else 0, progress_current, completed_at),
            )

    def get_quests(self) -> list[dict]:
        """Get all quest progress."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT quest_id, opted_in, progress_current, completed_at FROM quests"
            ).fetchall()
            return [
                {
                    "quest_id": row["quest_id"],
                    "opted_in": bool(row["opted_in"]),
                    "progress_current": row["progress_current"],
                    "completed_at": row["completed_at"],
                }
                for row in rows
            ]

    def clear_quests(self) -> None:
        """Clear all quests (for rebuild)."""
        with self._conn() as conn:
            conn.execute("DELETE FROM quests")

    # ──────────────────────────────────────────────────────────────────────────
    # Records
    # ──────────────────────────────────────────────────────────────────────────

    def upsert_record(
        self,
        record_id: str,
        objective: str,
        value: float,
        cell_key: str,
        timestamp: float,
        scope: str,
    ) -> None:
        """Insert or update a personal best record."""
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO records (record_id, objective, value, cell_key, timestamp, scope) VALUES (?, ?, ?, ?, ?, ?)",
                (record_id, objective, value, cell_key, timestamp, scope),
            )

    def get_records(self) -> list[dict]:
        """Get all records."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT record_id, objective, value, cell_key, timestamp, scope FROM records ORDER BY timestamp DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def clear_records(self) -> None:
        """Clear all records (for rebuild)."""
        with self._conn() as conn:
            conn.execute("DELETE FROM records")

    # ──────────────────────────────────────────────────────────────────────────
    # Fog regions
    # ──────────────────────────────────────────────────────────────────────────

    def upsert_fog_region(self, region: str, charted_at: float) -> None:
        """Mark a region as charted."""
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO fog_regions (region, charted_at) VALUES (?, ?)",
                (region, charted_at),
            )

    def get_fog_regions(self) -> list[str]:
        """Get all charted regions."""
        with self._conn() as conn:
            rows = conn.execute("SELECT region FROM fog_regions").fetchall()
            return [row["region"] for row in rows]

    def clear_fog_regions(self) -> None:
        """Clear all fog regions (for rebuild)."""
        with self._conn() as conn:
            conn.execute("DELETE FROM fog_regions")

    # ──────────────────────────────────────────────────────────────────────────
    # Rebuild from event log
    # ──────────────────────────────────────────────────────────────────────────

    def rebuild_from_events(self) -> RecognitionState:
        """Reconstruct recognition state from event log (pure replay)."""
        from computronium.ui.recognition.projector import fold

        events = self.get_all_events()
        return fold(events)

    def persist_state(self, state: RecognitionState) -> None:
        """Persist a complete recognition state to the store."""
        import time

        now = time.time()

        # Clear and rebuild
        self.clear_badges()
        self.clear_quests()
        self.clear_records()
        self.clear_fog_regions()

        for badge in state.badges:
            self.upsert_badge(badge.id, now)

        for quest in state.quests:
            self.upsert_quest(
                quest.id,
                quest.opted_in,
                quest.progress_current,
                quest.completed_at if hasattr(quest, "completed_at") else None,
            )

        for record in state.records:
            self.upsert_record(
                record.id,
                record.objective,
                record.value,
                record.cell_key,
                record.timestamp,
                record.scope,
            )

        for region in state.fog_regions_charted:
            self.upsert_fog_region(region, now)

        # Update rebuild timestamp
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("last_rebuild_at", str(now)),
            )

    def get_last_rebuild_at(self) -> float | None:
        """Get the last rebuild timestamp."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT value FROM metadata WHERE key = 'last_rebuild_at'"
            ).fetchone()
            return float(row["value"]) if row else None
