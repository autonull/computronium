"""Surface report generation from the record store (WP7).

The one report from the store alone (R85-R88). Parquet/JSON export bundles
for R73 round-trip.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record

from computronium.experiment.evidence.claims import (
    Alert,
    check_all_alerts,
    filter_promoted,
)

__all__ = [
    "ExportBundle",
    "ReportGenerator",
    "RunSummary",
    "export_to_json",
    "export_to_parquet",
    "generate_run_report",
    "load_export_bundle",
]


@dataclass(frozen=True, slots=True)
class RunSummary:
    """Summary of a single run from the store."""

    run_id: str
    spec: dict[str, Any] | None
    spec_version: int
    status: str
    budget_consumed_s: float | None
    replay_hash: str | None
    started_at: datetime
    finished_at: datetime | None
    record_count: int
    claim_eligible_count: int
    promoted_count: int


@dataclass(frozen=True, slots=True)
class ExportBundle:
    """Export bundle containing records, artifacts, and metadata for round-trip."""

    records: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    runs: list[dict[str, Any]]
    vector_index: list[dict[str, Any]]
    metadata: dict[str, Any]


class ReportGenerator:
    """Generate reports directly from the record store.

    All queries run against DuckDB; no external files required.
    """

    def __init__(self, store: RecordStore) -> None:
        self._store = store

    def run_summary(self, run_id: str) -> RunSummary | None:
        """Get summary for a single run."""
        if self._store._conn is None:
            raise RuntimeError("Store not initialized")

        row = self._store._conn.execute(
            "SELECT * FROM runs WHERE run_id = ?", [run_id]
        ).fetchone()
        if row is None:
            return None

        record_count = self._store.count_records(run_id)
        claim_eligible_records = self._store.claim_eligible_prefilter()
        claim_eligible_count = sum(
            1 for r in claim_eligible_records if r.run_id == run_id
        )
        promoted_records = filter_promoted(claim_eligible_records)
        promoted_count = sum(1 for r in promoted_records if r.run_id == run_id)

        return RunSummary(
            run_id=row[0],
            spec=json.loads(row[1]) if row[1] else None,
            spec_version=row[2],
            status=row[3],
            budget_consumed_s=row[4],
            replay_hash=row[5],
            started_at=row[6],
            finished_at=row[7],
            record_count=record_count,
            claim_eligible_count=claim_eligible_count,
            promoted_count=promoted_count,
        )

    def list_runs(self) -> list[RunSummary]:
        """List all runs with summaries."""
        if self._store._conn is None:
            raise RuntimeError("Store not initialized")

        rows = self._store._conn.execute(
            "SELECT run_id FROM runs ORDER BY started_at DESC"
        ).fetchall()
        results: list[RunSummary] = []
        for row in rows:
            summary = self.run_summary(row[0])
            if summary is not None:
                results.append(summary)
        return results

    def claim_eligible_records(self, run_id: str | None = None) -> list[Record]:
        """Get all claim-eligible records, optionally filtered by run."""
        records = self._store.claim_eligible_prefilter()
        if run_id:
            records = [r for r in records if r.run_id == run_id]
        return records

    def promoted_records(self, run_id: str | None = None) -> list[Record]:
        """Get all promoted records, optionally filtered by run."""
        eligible = self.claim_eligible_records(run_id)
        return filter_promoted(eligible)

    def records_with_alerts(
        self, run_id: str | None = None
    ) -> list[tuple[Record, list[Alert]]]:
        """Get records with their alert status."""
        if self._store._conn is None:
            raise RuntimeError("Store not initialized")

        conditions = []
        params = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT * FROM records{where_clause} ORDER BY seq"  # noqa: S608 - parameterized query
        rows = self._store._conn.execute(query, params).fetchall()

        results = []
        for row in rows:
            record = self._store._row_to_record(row)
            alerts = check_all_alerts(record)
            if alerts:
                results.append((record, alerts))
        return results

    def pareto_frontier(
        self,
        run_id: str | None = None,
        objectives: tuple[str, str] = ("accuracy", "param_count"),
        maximize: tuple[bool, bool] = (True, False),
    ) -> list[dict[str, Any]]:
        """Compute Pareto frontier from store records.

        Args:
            run_id: Optional run filter
            objectives: Tuple of (primary, secondary) objective keys from payload
            maximize: Tuple of (maximize_primary, maximize_secondary)

        Returns:
            List of dicts with record_id, coordinate, and objective values
        """
        if self._store._conn is None:
            raise RuntimeError("Store not initialized")

        eligible = self.claim_eligible_records(run_id)
        if not eligible:
            return []

        # Extract objective values
        points = []
        for record in eligible:
            try:
                primary_val = record.payload.get(objectives[0])
                secondary_val = record.payload.get(objectives[1])
                if primary_val is None or secondary_val is None:
                    continue
                points.append({
                    "record_id": record.record_id,
                    "cell_key": record.cell_key,
                    "primary": float(primary_val),
                    "secondary": float(secondary_val),
                    "coordinate": {
                        "substrate": record.substrate,
                        "geometry": record.geometry,
                        "dynamics": record.dynamics,
                        "plasticity": record.plasticity,
                        "credit": record.credit,
                        "update": record.update,
                    },
                })
            except ValueError, TypeError:
                continue

        if not points:
            return []

        # Simple Pareto filtering
        primary_key, secondary_key = "primary", "secondary"

        def _is_dominated(p: dict[str, Any], q: dict[str, Any]) -> bool:
            """Check if point p is dominated by point q."""
            primary_better = (
                q[primary_key] > p[primary_key]
                if maximize[0]
                else q[primary_key] < p[primary_key]
            )
            secondary_better = (
                q[secondary_key] > p[secondary_key]
                if maximize[1]
                else q[secondary_key] < p[secondary_key]
            )
            primary_equal = q[primary_key] == p[primary_key]
            secondary_equal = q[secondary_key] == p[secondary_key]

            return (
                (primary_better or primary_equal)
                and (secondary_better or secondary_equal)
                and (primary_better or secondary_better)
            )

        pareto = []
        for i, p in enumerate(points):
            dominated = any(_is_dominated(p, q) for j, q in enumerate(points) if i != j)
            if not dominated:
                pareto.append(p)

        return pareto

    def maturity_distribution(self, run_id: str | None = None) -> dict[str, int]:
        """Count records by maturity level."""
        if self._store._conn is None:
            raise RuntimeError("Store not initialized")

        conditions = []
        params = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = (
            f"SELECT status.maturity, COUNT(*) FROM records{where_clause} "  # noqa: S608
            "GROUP BY status.maturity"
        )
        rows = self._store._conn.execute(query, params).fetchall()
        return {row[0]: row[1] for row in rows}

    def gate_verdict_distribution(self, run_id: str | None = None) -> dict[str, int]:
        """Count records by gate verdict."""
        if self._store._conn is None:
            raise RuntimeError("Store not initialized")

        conditions = []
        params = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = (
            f"SELECT status.gate_verdict, COUNT(*) FROM records{where_clause} "  # noqa: S608
            "GROUP BY status.gate_verdict"
        )
        rows = self._store._conn.execute(query, params).fetchall()
        return {row[0]: row[1] for row in rows}

    def coordinate_coverage(self, run_id: str | None = None) -> dict[str, int]:
        """Count unique coordinates (cell_keys) and their seed replication."""
        if self._store._conn is None:
            raise RuntimeError("Store not initialized")

        conditions = []
        params = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"""
            SELECT cell_key, COUNT(*) as n_seeds
            FROM records{where_clause}
            GROUP BY cell_key
        """  # noqa: S608 - parameterized query
        rows = self._store._conn.execute(query, params).fetchall()
        return {row[0]: row[1] for row in rows}


def generate_run_report(store: RecordStore, run_id: str) -> str:
    """Generate a human-readable report for a single run."""
    generator = ReportGenerator(store)
    summary = generator.run_summary(run_id)
    if summary is None:
        return f"Run {run_id} not found"

    lines = [
        f"Run Report: {run_id}",
        "=" * 60,
        f"Status: {summary.status}",
        f"Started: {summary.started_at}",
        f"Finished: {summary.finished_at or 'N/A'}",
        f"Budget Consumed: {summary.budget_consumed_s or 0:.1f}s",
        f"Replay Hash: {summary.replay_hash or 'N/A'}",
        f"Spec Version: {summary.spec_version}",
        "",
        "Record Statistics:",
        f"  Total Records: {summary.record_count}",
        f"  Claim Eligible: {summary.claim_eligible_count}",
        f"  Promoted: {summary.promoted_count}",
        "",
        "Maturity Distribution:",
    ]

    maturity_dist = generator.maturity_distribution(run_id)
    for maturity, count in sorted(maturity_dist.items()):
        lines.append(f"  {maturity}: {count}")

    lines.append("")
    lines.append("Gate Verdict Distribution:")
    verdict_dist = generator.gate_verdict_distribution(run_id)
    for verdict, count in sorted(verdict_dist.items()):
        lines.append(f"  {verdict}: {count}")

    lines.append("")
    lines.append("Coordinate Coverage (unique cell_keys with seed counts):")
    coverage = generator.coordinate_coverage(run_id)
    for cell_key, n_seeds in sorted(coverage.items()):
        lines.append(f"  {cell_key[:16]}...: {n_seeds} seeds")

    lines.append("")
    lines.append("Pareto Frontier (accuracy vs param_count):")
    pareto = generator.pareto_frontier(run_id)
    if pareto:
        for p in pareto[:10]:
            lines.append(
                f"  {p['record_id'][:16]}... acc={p['primary']:.4f} params={p['secondary']:.0f} "
                f"[{p['coordinate']['dynamics']}/{p['coordinate']['credit']}/{p['coordinate']['update']}]"
            )
    else:
        lines.append("  (no claim-eligible records)")

    lines.append("")
    lines.append("Records with Alerts:")
    alerted = generator.records_with_alerts(run_id)
    if alerted:
        for record, alerts in alerted[:20]:
            alert_str = ", ".join(f"{a.alert_type}:{a.severity}" for a in alerts)
            lines.append(f"  {record.record_id[:16]}... [{alert_str}]")
    else:
        lines.append("  (no alerts)")

    return "\n".join(lines)


def export_to_parquet(
    store: RecordStore,
    output_dir: str | Path,
    run_id: str | None = None,
) -> Path:
    """Export store data to Parquet files for analysis round-trip.

    Creates:
    - records.parquet
    - artifacts.parquet
    - runs.parquet
    - vector_index.parquet
    - metadata.json
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas required for Parquet export. Install with: uv add pandas"
        )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if store._conn is None:
        raise RuntimeError("Store not initialized")

    # Export records
    where = "WHERE run_id = ?" if run_id else ""
    params = [run_id] if run_id else []

    records_df = pd.read_sql_query(
        f"SELECT * FROM records {where} ORDER BY seq",  # noqa: S608
        store._conn,
        params=params,
    )
    records_df.to_parquet(output_path / "records.parquet", index=False)

    # Export artifacts
    artifacts_where = (
        f"WHERE record_id IN (SELECT record_id FROM records {where})"  # noqa: S608
        if run_id
        else ""
    )
    artifacts_df = pd.read_sql_query(
        f"SELECT * FROM artifacts {artifacts_where} ORDER BY created_at",  # noqa: S608
        store._conn,
        params=params,
    )
    artifacts_df.to_parquet(output_path / "artifacts.parquet", index=False)

    # Export runs
    runs_df = pd.read_sql_query(
        f"SELECT * FROM runs {where} ORDER BY started_at",  # noqa: S608
        store._conn,
        params=params,
    )
    runs_df.to_parquet(output_path / "runs.parquet", index=False)

    # Export vector index
    vi_where = (
        f"WHERE record_id IN (SELECT record_id FROM records {where})"  # noqa: S608
        if run_id
        else ""
    )
    vi_df = pd.read_sql_query(
        f"SELECT * FROM vector_index {vi_where}",  # noqa: S608
        store._conn,
        params=params,
    )
    vi_df.to_parquet(output_path / "vector_index.parquet", index=False)

    # Export metadata
    metadata = {
        "exported_at": datetime.now().isoformat(),
        "run_id": run_id,
        "record_count": len(records_df),
        "artifact_count": len(artifacts_df),
        "run_count": len(runs_df),
        "vector_index_count": len(vi_df),
        "schema_version": 1,
    }
    with Path(output_path / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return output_path


def export_to_json(  # noqa: PLR0914
    store: RecordStore,
    output_path: str | Path,
    run_id: str | None = None,
) -> Path:
    """Export store data to a single JSON file for round-trip."""
    output_file = Path(output_path)

    if store._conn is None:
        raise RuntimeError("Store not initialized")

    params = [run_id] if run_id else []
    records_query = (
        "SELECT * FROM records WHERE run_id = ? ORDER BY seq"
        if run_id
        else "SELECT * FROM records ORDER BY seq"
    )

    # Records
    records_rows = store._conn.execute(records_query, params).fetchall()
    records = []
    for row in records_rows:
        record = store._row_to_record(row)
        records.append({
            "record_id": record.record_id,
            "seq": record.seq,
            "run_id": record.run_id,
            "schema_version": record.schema_version,
            "cell_key": record.cell_key,
            "measurement_key": record.measurement_key,
            "substrate": record.substrate,
            "geometry": record.geometry,
            "dynamics": record.dynamics,
            "plasticity": record.plasticity,
            "credit": record.credit,
            "update": record.update,
            "params": record.params,
            "schedule": {
                "fidelity": record.schedule.fidelity,
                "seed": record.schedule.seed,
                "n_seeds": record.schedule.n_seeds,
                "epochs": record.schedule.epochs,
                "batch_limit": record.schedule.batch_limit,
                "budget_id": record.schedule.budget_id,
            },
            "provenance": record.provenance.to_dict(),
            "status": {
                "gate_verdict": record.status.gate_verdict.value,
                "defect": record.status.defect,
                "cause": record.status.cause.value,
                "severity": record.status.severity.value,
                "quarantine": record.status.quarantine,
                "maturity": record.status.maturity.value,
                "uncertainty": record.status.uncertainty,
                "reproducibility": record.status.reproducibility.value,
                "assessment_procedure_version": record.status.assessment_procedure_version,
                "ceec_link": record.status.ceec_link,
            },
            "payload": record.payload,
            "unknown": record.unknown,
        })

    # Artifacts
    artifacts_query = (
        "SELECT * FROM artifacts WHERE record_id IN (SELECT record_id FROM records WHERE run_id = ?)"
        if run_id
        else "SELECT * FROM artifacts"
    )
    artifacts_rows = store._conn.execute(artifacts_query, params).fetchall()
    artifacts = [
        {
            "digest": row[0],
            "role": row[2],
            "record_id": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
            "external_uri": row[5],
            "external_size": row[6],
            "external_checksum": row[7],
        }
        for row in artifacts_rows
    ]

    # Runs
    runs_query = (
        "SELECT * FROM runs WHERE run_id = ? ORDER BY started_at"
        if run_id
        else "SELECT * FROM runs ORDER BY started_at"
    )
    runs_rows = store._conn.execute(runs_query, params).fetchall()
    runs = [
        {
            "run_id": row[0],
            "spec": json.loads(row[1]) if row[1] else None,
            "spec_version": row[2],
            "status": row[3],
            "budget_consumed_s": row[4],
            "replay_hash": row[5],
            "started_at": row[6].isoformat() if row[6] else None,
            "finished_at": row[7].isoformat() if row[7] else None,
        }
        for row in runs_rows
    ]

    # Vector index
    vi_query = (
        "SELECT * FROM vector_index WHERE record_id IN (SELECT record_id FROM records WHERE run_id = ?)"
        if run_id
        else "SELECT * FROM vector_index"
    )
    vi_rows = store._conn.execute(vi_query, params).fetchall()
    vector_index = [
        {
            "record_id": row[0],
            "embedding": list(row[1]),
            "embedding_version": row[2],
        }
        for row in vi_rows
    ]

    bundle = ExportBundle(
        records=records,
        artifacts=artifacts,
        runs=runs,
        vector_index=vector_index,
        metadata={
            "exported_at": datetime.now().isoformat(),
            "run_id": run_id,
            "record_count": len(records),
            "artifact_count": len(artifacts),
            "run_count": len(runs),
            "vector_index_count": len(vector_index),
            "schema_version": 1,
        },
    )

    # Custom JSON encoder for datetime
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)

    with Path(output_file).open("w", encoding="utf-8") as f:
        json.dump(bundle.__dict__, f, cls=DateTimeEncoder, indent=2)

    return output_file


def load_export_bundle(path: str | Path) -> ExportBundle:
    """Load an export bundle from JSON."""
    with Path(path).open(encoding="utf-8") as f:
        data = json.load(f)
    return ExportBundle(**data)
