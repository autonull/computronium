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
    from computronium.experiment.schema.run_spec import RunSpec

from computronium.experiment.evidence.claims import (
    Alert,
    AxisImpact,
    Claim,
    check_all_alerts,
    derive_claims,
    filter_promoted,
    replication_key,
    strongest_axis,
)
from computronium.experiment.evidence.limitations import (
    Limitation,
    derive_limitations,
    replication_keys_of,
)
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.metrics import (
    objective_metric,
    objective_name,
    optimizes,
)
from computronium.experiment.schema.record import GateVerdict

__all__ = [
    "AxisImpact",
    "Claim",
    "ExportBundle",
    "Limitation",
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
    spec: RunSpec | None
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


def _maximizes(metric_key: str) -> bool:
    """Whether a payload key is maximized, per the objective that measures it.

    An unclaimed key (a cost the study never declared) is minimized: a front
    treats it as a cost rather than silently reading a bigger number as better.
    """
    name = objective_name(metric_key)
    return optimizes(name) if name is not None else False


def _directions(objectives: tuple[str, str]) -> tuple[bool, bool]:
    """Whether each of a front's two payload keys is maximized."""
    primary, secondary = objectives
    return _maximizes(primary), _maximizes(secondary)


class ReportGenerator:  # ruff: ignore[too-many-public-methods] - one read method per report section, by design
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
        eligible = self.claim_eligible_records(run_id)
        claim_eligible_count = len(eligible)
        promoted_count = len(filter_promoted(eligible))

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

    def claim_eligible_records(self, run_id: str) -> list[Record]:
        """The records of every cell that achieved the claim-grade seed count.

        Eligibility is decided per *cell*, by achieved passing seeds: the
        executor writes one record per seed, so a record-level filter cannot
        see a replication group. One definition, read by every consumer here.
        """
        cells = set(self._store.claim_eligible_replication_keys(run_id))
        return [
            record
            for record in self._store.query_records(run_id=run_id)
            if replication_key(record) in cells
        ]

    def promoted_records(self, run_id: str) -> list[Record]:
        """Get the promoted records of a run."""
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
        run_id: str,
        objectives: tuple[str, str] | None = None,
        maximize: tuple[bool, bool] | None = None,
    ) -> list[dict[str, Any]]:
        """Compute the Pareto frontier over a run's claim-eligible cells.

        Args:
            run_id: Run filter.
            objectives: Primary and secondary payload keys. Defaults to the
                run's own first two measured objectives — a front over a key no
                measurement emits is an empty section, not a finding.
            maximize: Tuple of (maximize_primary, maximize_secondary). Read
                from each objective's declared direction when omitted, because a
                front that maximizes accuracy and walltime together is empty.

        Returns:
            List of dicts with record_id, coordinate, and objective values.
        """
        objectives = objectives or self.front_objectives(run_id)
        maximize = maximize or _directions(objectives)
        return self._pareto_subset(
            self.claim_eligible_records(run_id), objectives, maximize
        )

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
            axis.value: self._store.count_by_axis(axis, run_id)
            for axis in StructuralAxis
        }

    def achieved_seeds(self, run_id: str | None = None) -> dict[str, int]:
        """Achieved passing seeds per replication key — one query per cell."""
        keys = replication_keys_of(self._store.query_records(run_id=run_id))
        return {
            key: self._store.count_achieved_seeds(replication_key=key, run_id=run_id)
            for key in keys
        }

    def claims(self, run_id: str) -> tuple[Claim, ...]:
        """The claims a run makes, each with n and variance (R35/R64).

        One claim family per *measured* declared objective: a run that measured
        two things can say which axis mattered for each, and reporting only the
        first is half an answer. A run whose objectives nothing measures makes
        no claim.
        """
        metrics = self.claim_metrics(run_id)
        if not metrics:
            return ()
        spec = self._spec(run_id)
        return derive_claims(
            self._store.query_records(run_id=run_id),
            metrics=metrics,
            achieved=self.achieved_seeds(run_id),
            min_seeds=spec.n_seeds if spec else 5,
        )

    def limitations(self, run_id: str) -> tuple[Limitation, ...]:
        """Every limitation derivable from the run's records, none asserted."""
        spec = self._spec(run_id)
        return derive_limitations(
            self._store.query_records(run_id=run_id),
            achieved=self.achieved_seeds(run_id),
            n_seeds=spec.n_seeds if spec else None,
            fidelity=spec.fidelity if spec else None,
            objectives=spec.objectives if spec else (),
            claim_count=len(self.claims(run_id)),
        )

    def _spec(self, run_id: str) -> RunSpec | None:
        """The run's persisted spec, or None when the run is unknown."""
        info = self._store.query_run(run_id)
        return info.spec if info is not None else None

    def front_objectives(self, run_id: str) -> tuple[str, str]:
        """The two payload keys a Pareto front defaults to.

        The run's first two *measured* objectives. Parameter count is the
        fallback for a run that measured only one thing, because a front needs
        two axes; it is not the second axis by default, since comparing an
        outcome against size when the run declared a second outcome discards the
        outcome.
        """
        metrics = self.claim_metrics(run_id)
        if len(metrics) >= 2:
            return metrics[0], metrics[1]
        return (metrics[0] if metrics else "param_count", "param_count")

    def claim_metrics(self, run_id: str) -> tuple[str, ...]:
        """The payload keys the run's measured objectives resolve to, in order."""
        spec = self._spec(run_id)
        if spec is None:
            return ()
        metrics: list[str] = []
        for name in spec.objectives:
            try:
                metrics.append(objective_metric(name))
            except LookupError:
                continue
        return tuple(dict.fromkeys(metrics))

    def failures_by_cause(self, run_id: str | None = None) -> dict[str, int]:
        """Count failed records grouped by recorded failure cause."""
        return self._store.count_by_failure_cause(run_id)

    def budget_consumption(self, run_id: str | None = None) -> list[dict[str, Any]]:
        """Budget consumed per run (declared vs consumed when available)."""
        results = []
        for info in self._store.query_runs(run_id=run_id):
            declared = info.spec.budget_seconds if info.spec else None
            results.append({
                "run_id": info.run_id,
                "status": info.status,
                "declared_budget_s": declared,
                "consumed_s": info.budget_consumed_s,
            })
        return results

    def fronts_by_fidelity(
        self,
        run_id: str,
        objectives: tuple[str, str] | None = None,
        maximize: tuple[bool, bool] | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Pareto frontier per fidelity level (R86 fronts-by-fidelity)."""
        objectives = objectives or self.front_objectives(run_id)
        maximize = maximize or _directions(objectives)
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

    def promotion_history(self, run_id: str) -> list[dict[str, Any]]:
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

    def claim_eligible_table(self, run_id: str) -> list[dict[str, Any]]:
        """Flat claim-eligible table rows for reporting (R85)."""
        rows = []
        for r in self.claim_eligible_records(run_id):
            rows.append({
                "record_id": r.record_id,
                "cell_key": r.cell_key,
                "replication_key": replication_key(r),
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


def _section(title: str) -> list[str]:
    """A report section heading."""
    return ["", title]


def _claims_section(generator: ReportGenerator, run_id: str) -> list[str]:
    """Claims, each with n and variance, and which axis mattered most."""
    lines = _section(
        "Claims (n and variance are mandatory; a claim line is not prose):"
    )
    claims = generator.claims(run_id)
    if not claims:
        return [*lines, "  (none — see Limitations)"]
    impact = strongest_axis(claims)
    if impact is not None:
        lines.append(f"  {impact.render()}")
    lines.extend(f"  {claim.render()}" for claim in claims)
    return lines


def _limitations_section(generator: ReportGenerator, run_id: str) -> list[str]:
    """Limitations, each naming the filter that re-derives it."""
    lines = _section("Limitations (every line re-derivable from a record):")
    limitations = generator.limitations(run_id)
    if not limitations:
        return [*lines, "  (none)"]
    for limitation in limitations:
        lines.append(f"  [{limitation.kind}] {limitation.detail}")
        lines.append(f"      evidence: {limitation.evidence}")
    return lines


def _distribution_section(
    title: str, distribution: dict[str, int], indent: str = "  "
) -> list[str]:
    """One count-by-value section."""
    return _section(title) + [
        f"{indent}{name}: {count}" for name, count in sorted(distribution.items())
    ]


def _pareto_section(generator: ReportGenerator, run_id: str) -> list[str]:
    """The claim-eligible Pareto front, or why there is none."""
    primary, secondary = generator.front_objectives(run_id)
    lines = _section(f"Pareto Frontier ({primary} vs {secondary}):")
    pareto = generator.pareto_frontier(run_id)
    if not pareto:
        return [*lines, "  (no claim-eligible records)"]
    return [
        *lines,
        *(
            f"  {point['record_id'][:16]}... {primary}={point['primary']:.4f} "
            f"{secondary}={point['secondary']:.4f} "
            f"[{point['coordinate']['dynamics']}/{point['coordinate']['credit']}/"
            f"{point['coordinate']['update']}]"
            for point in pareto[:10]
        ),
    ]


def _alerts_section(generator: ReportGenerator, run_id: str) -> list[str]:
    """Records carrying an alert, with the alert kinds."""
    lines = _section("Records with Alerts:")
    alerted = generator.records_with_alerts(run_id)
    if not alerted:
        return [*lines, "  (no alerts)"]
    return [
        *lines,
        *(
            f"  {record.record_id[:16]}... ["
            f"{', '.join(f'{a.alert_type}:{a.severity}' for a in alerts)}]"
            for record, alerts in alerted[:20]
        ),
    ]


def _coverage_section(generator: ReportGenerator, run_id: str) -> list[str]:
    """Unique cells with their seed counts."""
    lines = _section("Coordinate Coverage (unique cell_keys with seed counts):")
    return [
        *lines,
        *(
            f"  {cell_key[:16]}...: {n_seeds} seeds"
            for cell_key, n_seeds in sorted(
                generator.coordinate_coverage(run_id).items()
            )
        ),
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
        *_distribution_section(
            "Maturity Distribution:", generator.maturity_distribution(run_id)
        ),
        *_distribution_section(
            "Gate Verdict Distribution:", generator.gate_verdict_distribution(run_id)
        ),
        *_coverage_section(generator, run_id),
        *_claims_section(generator, run_id),
        *_limitations_section(generator, run_id),
        *_pareto_section(generator, run_id),
        *_alerts_section(generator, run_id),
    ]
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
