"""How the mirror is published, and why the copy cannot fail (TODO69).

``COPY FROM DATABASE`` copies the tables in an order DuckDB chooses, and
when the ``records`` table is copied before the ``runs`` table, the
foreign key between them refuses the copy: the mirror keeps the picture
it had, and a reader in another process sees a run one record behind.
This probe measures that failure and measures the copy that replaced it.

Run: uv run python scripts/probes/todo69_mirror_probe.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from computronium.experiment.evidence.mirror import mirror_path  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.evidence.store import RecordStore, StoreConfig  # ruff: ignore[module-import-not-at-top-of-file]
from tests.unit.experiment.dashboard_store import demo_record, demo_spec  # ruff: ignore[module-import-not-at-top-of-file]

RECORDS = 3
TRIALS = 12


def build(path: Path, records: int) -> str:
    """A store with one run and a few records."""
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=demo_spec())
        for seed in range(records):
            store.append(demo_record(run_id, 0.4 + 0.01 * seed, seed))
    return run_id


def copy_from_database(conn, staged: Path) -> None:
    """The copy DuckDB does on its own: the one that fails."""
    source = str(conn.execute("SELECT current_database()").fetchone()[0])
    conn.execute(f"ATTACH '{staged}' AS mirror (READ_WRITE)")
    try:
        conn.execute(f'COPY FROM DATABASE "{source}" TO mirror')
    finally:
        conn.execute("DETACH mirror")


def publish(conn, staged: Path) -> None:
    """The copy the mirror makes now: table by table, in the order the keys allow."""
    from computronium.experiment.evidence.mirror import _copy_database

    conn.execute(f"ATTACH '{staged}' AS mirror (READ_WRITE)")
    try:
        _copy_database(conn)
    finally:
        conn.execute("DETACH mirror")


def attempt(path: Path, copier, records: int) -> tuple[int, str]:
    """One store, published after every append; return the mirror's count."""
    target = mirror_path(path)
    if target.exists():
        target.unlink()
    failures: list[str] = []
    with RecordStore(
        StoreConfig(path=path, mirror_path=target, mirror_interval=0.0)
    ) as store:
        run_id = store.create_run(spec=demo_spec())
        for seed in range(records):
            store.append(demo_record(run_id, 0.4 + 0.01 * seed, seed))
        conn = store._conn  # ruff: ignore[private-member-access]  - the probe is the writer's own connection
        for _ in range(3):
            staged = target.with_name(f"{target.name}.staged")
            if staged.exists():
                staged.unlink()
            try:
                copier(conn, staged)
                staged.replace(target)
            except Exception as exc:  # ruff: ignore[blind-except]  - the probe reports what happened
                failures.append(str(exc).splitlines()[0])
    with RecordStore(StoreConfig(path=target, read_only=True)) as mirror:
        return mirror.count_records(), failures[0] if failures else ""


def main() -> int:
    """Publish a mirror a few times over, with each way of copying."""
    for name, copier in (
        ("copy-from-database", copy_from_database),
        ("table-by-table", publish),
    ):
        misses = 0
        errors = 0
        with tempfile.TemporaryDirectory() as directory:
            for trial in range(TRIALS):
                path = Path(directory) / f"probe-{trial}.duckdb"
                held, error = attempt(path, copier, RECORDS)
                misses += held != RECORDS
                errors += bool(error)
                if error and trial == 0:
                    print(f"[{name}] {error}")
        print(
            f"[{name}] the mirror missed a record {misses} times out of {TRIALS} "
            f"({errors} publishes failed)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
