"""Surface report generation from the record store (WP7).

The one report from the store alone (R85-R88). Parquet/JSON export bundles
for R73 round-trip.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
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
from computronium.experiment.schema.record import GateVerdict

__all__ = [
    "ExportBundle",
    "ReportGenerator",
    "RunSummary",
    "export_to_json",
    "export_to_parquet",
    "generate_run_report",
    "load_export_bundle",
    "narrative_handoff_summary",
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
        info = self._store.query_run(run_id)
        if info is None:
            return None

        record_count = self._store.count_records(run_id)
        claim_eligible_records = self._store.claim_eligible_prefilter()
        claim_eligible_count = sum(
            1 for r in claim_eligible_records if r.run_id == run_id
        )
        promoted_records = filter_promoted(claim_eligible_records)
        promoted_count = sum(1 for r in promoted_records if r.run_id == run_id)

        return RunSummary(
            run_id=info.run_id,
            spec=info.spec,
            spec_version=info.spec_version,
            status=info.status,
            budget_consumed_s=info.budget_consumed_s,
            replay_hash=info.replay_hash,
            started_at=info.started_at,
            finished_at=info.finished_at,
            record_count=record_count,
            claim_eligible_count=claim_eligible_count,
            promoted_count=promoted_count,
        )

    def list_runs(self) -> list[RunSummary]:
        """List all runs with summaries."""
        results: list[RunSummary] = []
        for info in self._store.query_runs():
            summary = self.run_summary(info.run_id)
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
        results = []
        for record in self._store.query_records(run_id=run_id):
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
        return self._store.count_by_status_field("maturity", run_id)

    def gate_verdict_distribution(self, run_id: str | None = None) -> dict[str, int]:
        """Count records by gate verdict."""
        return self._store.count_by_status_field("gate_verdict", run_id)

    def coordinate_coverage(self, run_id: str | None = None) -> dict[str, int]:
        """Count unique coordinates (cell_keys) and their seed replication."""
        return self._store.cell_seed_counts(run_id)

    def axis_coverage(self, run_id: str | None = None) -> dict[str, dict[str, int]]:
        """Per-axis stratification of records (R18 axis-coverage section)."""
        return {
            axis: self._store.count_by_axis(axis, run_id)  # type: ignore[arg-type]
            for axis in (
                "substrate",
                "geometry",
                "dynamics",
                "plasticity",
                "credit",
                "update",
            )
        }

    def failures_by_cause(self, run_id: str | None = None) -> dict[str, int]:
        """Count failed records grouped by recorded failure cause."""
        return self._store.count_by_failure_cause(run_id)

    def budget_consumption(self, run_id: str | None = None) -> list[dict[str, Any]]:
        """Budget consumed per run (declared vs consumed when available)."""
        results = []
        for info in self._store.query_runs(run_id=run_id):
            declared = (info.spec or {}).get("budget_seconds")
            results.append({
                "run_id": info.run_id,
                "status": info.status,
                "declared_budget_s": declared,
                "consumed_s": info.budget_consumed_s,
            })
        return results

    def fronts_by_fidelity(
        self,
        run_id: str | None = None,
        objectives: tuple[str, str] = ("accuracy", "param_count"),
        maximize: tuple[bool, bool] = (True, False),
    ) -> dict[str, list[dict[str, Any]]]:
        """Pareto frontier per fidelity level (R86 fronts-by-fidelity)."""
        records = self._store.query_records(run_id=run_id)
        by_fidelity: dict[str, list[Any]] = {}
        for record in records:
            by_fidelity.setdefault(record.schedule.fidelity, []).append(record)

        fronts: dict[str, list[dict[str, Any]]] = {}
        for fidelity, fidelity_records in sorted(by_fidelity.items()):
            # Reuse the Pareto filter by feeding claim-shaped subsets.
            eligible = [
                r
                for r in fidelity_records
                if r.status.gate_verdict == GateVerdict.PASS_
                and not r.status.quarantine
            ]
            fronts[fidelity] = self._pareto_subset(eligible, objectives, maximize)
        return fronts

    def promotion_history(self, run_id: str | None = None) -> list[dict[str, Any]]:
        """Promoted records in persistence (seq) order — promotion history."""
        promoted = filter_promoted(self.claim_eligible_records(run_id))
        promoted.sort(key=lambda r: r.seq)
        return [
            {
                "seq": r.seq,
                "record_id": r.record_id,
                "cell_key": r.cell_key,
                "fidelity": r.schedule.fidelity,
                "seed": r.schedule.seed,
                "maturity": r.status.maturity.value,
            }
            for r in promoted
        ]

    def claim_eligible_table(self, run_id: str | None = None) -> list[dict[str, Any]]:
        """Flat claim-eligible table rows for reporting (R85)."""
        rows = []
        for r in self.claim_eligible_records(run_id):
            replication_key = (
                f"{r.cell_key}|{r.schedule.fidelity}|{r.schedule.n_seeds}|"
                f"{r.schedule.epochs}|{r.schedule.batch_limit}|{r.schedule.budget_id}"
            )
            rows.append({
                "record_id": r.record_id,
                "cell_key": r.cell_key,
                "replication_key": replication_key,
                "coordinate": f"{r.substrate}/{r.geometry}/{r.dynamics}/"
                f"{r.plasticity}/{r.credit}/{r.update}",
                "fidelity": r.schedule.fidelity,
                "seed": r.schedule.seed,
                "n_seeds": r.schedule.n_seeds,
                "maturity": r.status.maturity.value,
            })
        return rows

    def campaign_diff(self, run_a: str, run_b: str) -> dict[str, Any]:
        """Cross-run campaign diff (C78): coverage and outcome deltas."""
        diff: dict[str, Any] = {"run_a": run_a, "run_b": run_b}
        for label, run in (("a", run_a), ("b", run_b)):
            diff[f"summary_{label}"] = self.run_summary(run)
            diff[f"coverage_{label}"] = self.coordinate_coverage(run)
            diff[f"maturity_{label}"] = self.maturity_distribution(run)
        cov_a = diff["coverage_a"]
        cov_b = diff["coverage_b"]
        diff["cells_only_in_a"] = sorted(set(cov_a) - set(cov_b))
        diff["cells_only_in_b"] = sorted(set(cov_b) - set(cov_a))
        diff["shared_cells"] = len(set(cov_a) & set(cov_b))
        return diff

    def _pareto_subset(
        self,
        records: list[Record],
        objectives: tuple[str, str],
        maximize: tuple[bool, bool],
    ) -> list[dict[str, Any]]:
        """Pareto filter over a record subset (shared by frontier methods)."""
        points: list[dict[str, Any]] = []
        for record in records:
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

        def _is_dominated(p: dict[str, Any], q: dict[str, Any]) -> bool:
            primary_better = (
                q["primary"] > p["primary"]
                if maximize[0]
                else q["primary"] < p["primary"]
            )
            secondary_better = (
                q["secondary"] > p["secondary"]
                if maximize[1]
                else q["secondary"] < p["secondary"]
            )
            primary_equal = q["primary"] == p["primary"]
            secondary_equal = q["secondary"] == p["secondary"]
            return (
                (primary_better or primary_equal)
                and (secondary_better or secondary_equal)
                and (primary_better or secondary_better)
            )

        return [
            p
            for i, p in enumerate(points)
            if not any(_is_dominated(p, q) for j, q in enumerate(points) if i != j)
        ]


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

    snapshot = store.export_snapshot(run_id)

    def _flatten(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        flat: list[dict[str, Any]] = []
        for row in rows:
            flat.append({
                key: json.dumps(value, default=str)
                if isinstance(value, dict | list)
                else value
                for key, value in row.items()
            })
        return flat

    records_df = pd.DataFrame(_flatten(snapshot["records"]))
    artifacts_df = pd.DataFrame(snapshot["artifacts"])
    runs_df = pd.DataFrame(_flatten(snapshot["runs"]))
    vi_df = pd.DataFrame(_flatten(snapshot["vector_index"]))
    records_df.to_parquet(output_path / "records.parquet", index=False)
    artifacts_df.to_parquet(output_path / "artifacts.parquet", index=False)
    runs_df.to_parquet(output_path / "runs.parquet", index=False)
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

    snapshot = store.export_snapshot(run_id)
    records = snapshot["records"]
    artifacts = snapshot["artifacts"]
    runs = snapshot["runs"]
    vector_index = snapshot["vector_index"]

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
        json.dump(asdict(bundle), f, cls=DateTimeEncoder, indent=2)

    return output_file


def narrative_handoff_summary(store: RecordStore, run_id: str) -> str:
    """Narrative handoff summary for operator review (R88).

    One screen: run state, evidence counts, claim-eligible cells, open
    alerts, promotion history tail, budget, and operator intents.
    """
    generator = ReportGenerator(store)
    summary = generator.run_summary(run_id)
    if summary is None:
        return f"Run {run_id} not found"
    eligible = generator.claim_eligible_table(run_id)
    alerted = generator.records_with_alerts(run_id)
    history = generator.promotion_history(run_id)
    budgets = generator.budget_consumption(run_id)
    intents = store.query_intent_records(run_id)
    lines = [
        f"Handoff: run {run_id} [{summary.status}]",
        f"Records: {summary.record_count} total, "
        f"{summary.claim_eligible_count} claim-eligible, "
        f"{summary.promoted_count} promoted.",
    ]
    if eligible:
        lines.append("Claim-eligible cells (first 5):")
        for row in eligible[:5]:
            lines.append(
                f"  {row['coordinate']} fidelity={row['fidelity']} "
                f"seeds={row['seed']}/{row['n_seeds']} maturity={row['maturity']}"
            )
    else:
        lines.append("No claim-eligible cells yet.")
    if alerted:
        lines.append(f"Open alerts: {len(alerted)} record(s) flagged:")
        for record, alerts in alerted[:5]:
            kinds = ", ".join(a.alert_type for a in alerts)
            lines.append(f"  {record.record_id[:12]} [{kinds}]")
    else:
        lines.append("Open alerts: none.")
    if history:
        lines.append(
            f"Latest promotion: seq={history[-1]['seq']} "
            f"cell={history[-1]['cell_key'][:12]}"
        )
    if budgets:
        consumed = budgets[0].get("consumed_s")
        declared = budgets[0].get("declared_budget_s")
        lines.append(f"Budget: consumed={consumed}s declared={declared}s")
    lines.append(f"Operator intents on record: {len(intents)}")
    for intent_record in intents[-3:]:
        payload = intent_record.payload
        lines.append(
            f"  {payload.get('intent_kind')} by {payload.get('operator')} "
            f"at {payload.get('timestamp')}"
        )
    return "\n".join(lines)


def load_export_bundle(path: str | Path) -> ExportBundle:
    """Load an export bundle from JSON."""
    with Path(path).open(encoding="utf-8") as f:
        data = json.load(f)
    return ExportBundle(**data)
