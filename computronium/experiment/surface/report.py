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
    from collections.abc import Mapping, Sequence

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec

from computronium.experiment.evidence.claims import (
    DEFAULT_MIN_SEEDS,
    Alert,
    AxisImpact,
    Claim,
    cell_metrics_by_axis_value,
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
from computronium.experiment.evidence.significance import (
    Significance,
    paired_significance,
)
from computronium.experiment.execution.search_space import (
    declared_cell_count,
    search_space_from_spec,
)
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import DataOrigin
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
    "Significance",
    "export_to_json",
    "export_to_parquet",
    "generate_html_report",
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
    declared_cells: int


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


def _numeric_vector(
    record: Record, objectives: tuple[str, ...]
) -> dict[str, float] | None:
    """A record's objective values as floats, or ``None`` if it lacks one.

    ``None`` rather than a default: a record missing an objective cannot be
    placed on that front, and a substituted zero would place it there wrongly.
    """
    values: dict[str, float] = {}
    for key in objectives:
        raw = record.payload.get(key)
        if raw is None:
            return None
        try:
            values[key] = float(raw)
        except ValueError, TypeError:
            return None
    return values


def _directions(objectives: tuple[str, ...]) -> tuple[bool, ...]:
    """Whether each of a front's payload keys is maximized, in order.

    Read per objective from its declared direction, because a front that
    maximizes accuracy and minimizes walltime needs to know which is which
    before it can say what dominates what.
    """
    return tuple(_maximizes(key) for key in objectives)


def non_dominated(
    points: Sequence[Mapping[str, float]],
    axes: Sequence[str],
    maximize: Sequence[bool],
) -> list[int]:
    """Indices of the points no other point dominates, over any arity.

    A point is dominated when another is at least as good on every axis and
    strictly better on one. Two objectives is the special case a two-axis front
    needs; six is the case TODO51\'s stability axis needs. A two-objective filter
    silently projected that six-name set onto its first two, so the front it
    reported was a front over (rho, sigma_max) with the other four unconstrained.

    Args:
        points: Candidates, each mapping axis name to value.
        axes: The axis names, in the order ``maximize`` describes them. Named
            explicitly rather than read from the first point, because a point
            carries bookkeeping fields that are not axes.
        maximize: Per axis, whether larger is better.

    Returns:
        Indices into ``points``, ascending.
    """
    if len(axes) != len(maximize):
        msg = f"{len(axes)} axes but {len(maximize)} directions"
        raise ValueError(msg)

    def _better(candidate: float, incumbent: float, axis: int) -> bool:
        return candidate > incumbent if maximize[axis] else candidate < incumbent

    vectors = [[point[axis] for axis in axes] for point in points]
    keep: list[int] = []
    for i, vector in enumerate(vectors):
        dominated = False
        for j, rival in enumerate(vectors):
            if i == j:
                continue
            at_least_as_good = all(
                _better(rival[a], vector[a], a) or rival[a] == vector[a]
                for a in range(len(axes))
            )
            strictly_better = any(
                _better(rival[a], vector[a], a) for a in range(len(axes))
            )
            if at_least_as_good and strictly_better:
                dominated = True
                break
        if not dominated:
            keep.append(i)
    return keep


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

        # Calculate declared cells from the spec
        declared_cells = 0
        if info.spec is not None:
            space = search_space_from_spec(info.spec)
            declared_cells = declared_cell_count(info.spec, space)

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
            declared_cells=declared_cells,
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
        objectives: tuple[str, ...] | None = None,
        maximize: tuple[bool, ...] | None = None,
    ) -> list[dict[str, Any]]:
        """Compute the Pareto frontier over a run's claim-eligible cells.

        Args:
            run_id: Run filter.
            objectives: Payload keys, one per front axis. Defaults to the run's
                own first two measured objectives — a front over a key no
                measurement emits is an empty section, not a finding.
            maximize: Per axis, whether larger is better. Read from each
                objective's declared direction when omitted, because a front that
                maximizes accuracy and walltime together is empty.

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
        return derive_claims(
            self._store.query_records(run_id=run_id),
            metrics=metrics,
            achieved=self.achieved_seeds(run_id),
            min_seeds=self._min_seeds(run_id),
        )

    def significance(self, run_id: str) -> Significance | None:
        """Whether the axis that mattered most mattered *significantly* (E2).

        Tested on the widest axis' best and worst values, paired over the cells
        those two values share. ``None`` when there is no spread to test (a
        single-valued axis); too little shared coverage is an
        :class:`Significance` of its own, not a missing one.
        """
        claims = self.claims(run_id)
        pair = self._pair_under_test(claims)
        if pair is None:
            return None
        axis_name, metric, best_value, worst_value = pair
        by_value = cell_metrics_by_axis_value(
            self._store.query_records(run_id=run_id),
            axis=StructuralAxis(axis_name),
            metric=metric,
            achieved=self.achieved_seeds(run_id),
            min_seeds=self._min_seeds(run_id),
        )
        return paired_significance(
            by_value.get(best_value, {}),
            by_value.get(worst_value, {}),
            axis=axis_name,
            metric=metric,
            best_value=best_value,
            worst_value=worst_value,
        )

    @staticmethod
    def _pair_under_test(claims: tuple[Claim, ...]) -> tuple[str, str, str, str] | None:
        """The (axis, metric, best, worst) the significance test compares.

        The widest axis when one spread — that is where a reader looks first.
        Failing that, the first axis with two values at all: a run whose arms
        tie still gets its null tested, because silence is indistinguishable
        from a test that was never run.
        """
        by_axis: dict[tuple[str, str], dict[str, Claim]] = {}
        for claim in claims:
            by_axis.setdefault((claim.metric, claim.axis), {})[claim.value] = claim
        impact = strongest_axis(claims)
        if impact is not None:
            return (
                impact.axis,
                impact.metric,
                impact.best_value,
                impact.worst_value,
            )
        for (metric, axis), values in sorted(by_axis.items()):
            if len(values) < 2:
                continue
            ordered = sorted(values.values(), key=lambda c: (c.mean, c.value))
            return axis, metric, ordered[-1].value, ordered[0].value
        return None

    def data_origin_distribution(self, run_id: str) -> dict[str, int]:
        """Records per provenance data origin — the design's own allocation."""
        counts: dict[str, int] = {}
        for record in self._store.query_records(run_id=run_id):
            origin = record.provenance.data_origin.value
            counts[origin] = counts.get(origin, 0) + 1
        return counts

    def control_records(self, run_id: str) -> tuple[Record, ...]:
        """The records S1 stamped as the design's control.

        Derived from the store alone: a control is a record whose provenance
        says so, so the report names one without asking the scheduler. A run
        whose design stamped nothing returns none, and the report says so
        rather than substituting an exploration cell for a control it is not.
        """
        return tuple(
            r
            for r in self._store.query_records(run_id=run_id)
            if r.provenance.data_origin == DataOrigin.CONTROL
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

    def _min_seeds(self, run_id: str) -> int:
        """The seed floor every claim-side derivation agrees on."""
        spec = self._spec(run_id)
        return spec.n_seeds if spec else DEFAULT_MIN_SEEDS

    def front_objectives(self, run_id: str, limit: int = 2) -> tuple[str, ...]:
        """The payload keys a whole-run front defaults to.

        The run's first *limit* measured objectives. Parameter count is the
        fallback for a run that measured only one thing, because a front needs
        two axes; it is not the second axis by default, since comparing an
        outcome against size when the run declared a second outcome discards the
        outcome.
        """
        metrics = self.claim_metrics(run_id)
        if len(metrics) >= limit:
            return metrics[:limit]
        return (metrics[0] if metrics else "param_count",) * limit

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
        objectives: tuple[str, ...] | None = None,
        maximize: tuple[bool, ...] | None = None,
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
        objectives: tuple[str, ...],
        maximize: tuple[bool, ...],
    ) -> list[dict[str, Any]]:
        """Pareto filter over a record subset, at the arity asked for.

        Any number of axes: an axis-aligned front has as many as its axis
        declares. A record missing one of them cannot be placed on the front at
        all, so it is dropped rather than scored against a default.
        """
        points: list[dict[str, Any]] = []
        for record in records:
            values = _numeric_vector(record, objectives)
            if values is None:
                continue
            points.append({
                "record_id": record.record_id,
                "cell_key": record.cell_key,
                "objectives": values,
                "coordinate": {
                    "substrate": record.substrate,
                    "geometry": record.geometry,
                    "dynamics": record.dynamics,
                    "plasticity": record.plasticity,
                    "credit": record.credit,
                    "update": record.update,
                },
            })

        if not points:
            return []
        vectors = [point["objectives"] for point in points]
        return [points[i] for i in non_dominated(vectors, objectives, maximize)]

    def axis_frontiers(self, run_id: str) -> dict[str, list[dict[str, Any]]]:
        """One Pareto front per structural axis, from the run's own declaration.

        The axis-aligned campaign declares a full objective set per axis — six
        objectives for stability, three for cost. Reporting one front over the
        run's first two objectives instead answers a question nobody asked: the
        stability axis is defined by rho, sigma_max and the four other names
        that constrain them jointly, and a two-axis filter leaves those four
        unconstrained while calling the result a front.

        Returns:
            Axis name to its front. An axis with no claim-eligible cell
            carrying every one of its objectives is absent, not empty.
        """
        spec = self._spec(run_id)
        declared = dict(spec.axis_objectives) if spec else {}
        if not declared:
            return {}
        eligible = self.claim_eligible_records(run_id)
        return {
            axis: self._pareto_subset(eligible, tuple(names), _directions(names))
            for axis, names in declared.items()
            if names
        }


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
    significance = generator.significance(run_id)
    if significance is not None:
        lines.append(f"  {significance.render()}")
    return lines


def _contrast_section(generator: ReportGenerator, run_id: str) -> list[str]:
    """The contrast design's allocation, and the control cell by name (E3).

    The control is what every contrast is measured against, so a report that
    compares cells without naming it has no reference point. It is read from
    the records' own provenance: a design that stamped nothing is reported as
    absent, never as an unnamed control.
    """
    lines = _section("Contrast Design (data-origin allocation):")
    distribution = generator.data_origin_distribution(run_id)
    if not distribution:
        return [*lines, "  (no records — no design to report)"]
    lines.extend(
        f"  {origin}: {count} record(s)"
        for origin, count in sorted(distribution.items())
    )

    controls = generator.control_records(run_id)
    if not controls:
        lines.append("  Control: none — this run's design stamped no control record")
        return lines
    cell_keys = sorted({r.cell_key for r in controls})
    lines.append(f"  Control ({len(controls)} record(s), {len(cell_keys)} cell(s)):")
    for key in cell_keys:
        seeds = sorted(r.schedule.seed for r in controls if r.cell_key == key)
        lines.append(f"    cell_key: {key}")
        lines.append(f"    seeds: {seeds}")
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
            f"  {point['record_id'][:16]}... "
            + " ".join(
                f"{key}={value:.4g}" for key, value in point["objectives"].items()
            )
            + f" [{point['coordinate']['dynamics']}/{point['coordinate']['credit']}/"
            f"{point['coordinate']['update']}]"
            for point in pareto[:10]
        ),
    ]


def _axis_frontiers_section(generator: ReportGenerator, run_id: str) -> list[str]:
    """One front per declared structural axis, over that axis's full objective set."""
    fronts = generator.axis_frontiers(run_id)
    if not fronts:
        return []
    lines = _section("Axis-Aligned Pareto Frontiers:")
    for axis in sorted(fronts):
        names = ", ".join(fronts[axis][0]["objectives"]) if fronts[axis] else "-"
        lines.append(f"  {axis} ({names}): {len(fronts[axis])} non-dominated")
        for point in fronts[axis][:5]:
            cell = point["coordinate"]
            values = " ".join(
                f"{key}={value:.4g}" for key, value in point["objectives"].items()
            )
            lines.append(
                f"    {cell['dynamics']}/{cell['credit']}/{cell['update']} {values}"
            )
    return lines


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


def _economics_section(generator: ReportGenerator, run_id: str) -> list[str]:
    """Campaign economics: cost per record, projected completion."""
    summary = generator.run_summary(run_id)
    if summary is None:
        return []

    lines = _section("Campaign Economics:")
    if summary.record_count > 0 and summary.budget_consumed_s is not None:
        cost_per_record = summary.budget_consumed_s / summary.record_count
        lines.append(f"  Cost per Record: {cost_per_record:.3f}s")

        if summary.declared_cells > 0:
            projected_total = cost_per_record * summary.declared_cells
            remaining_cells = summary.declared_cells - summary.record_count
            projected_remaining = cost_per_record * remaining_cells
            lines.append(
                f"  Projected Total: {projected_total:.1f}s ({projected_total / 60:.1f}m)"
            )
            lines.append(
                f"  Remaining: {projected_remaining:.1f}s ({projected_remaining / 60:.1f}m)"
            )
            progress = (summary.record_count / summary.declared_cells) * 100
            lines.append(
                f"  Progress: {progress:.1f}% ({summary.record_count}/{summary.declared_cells})"
            )
    elif summary.declared_cells > 0:
        lines.append(f"  Declared Cells: {summary.declared_cells}")
        lines.append(f"  Records Measured: {summary.record_count}")
        lines.append("  Cost per Record: N/A (no budget consumed yet)")
    else:
        lines.append("  No declared cells or records measured")
    return lines


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
        f"  Declared Cells: {summary.declared_cells}",
        *_economics_section(generator, run_id),
        *_distribution_section(
            "Maturity Distribution:", generator.maturity_distribution(run_id)
        ),
        *_distribution_section(
            "Gate Verdict Distribution:", generator.gate_verdict_distribution(run_id)
        ),
        *_coverage_section(generator, run_id),
        *_contrast_section(generator, run_id),
        *_claims_section(generator, run_id),
        *_limitations_section(generator, run_id),
        *_pareto_section(generator, run_id),
        *_axis_frontiers_section(generator, run_id),
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


def _load_training_history(store: RecordStore, run_id: str) -> dict[str, list[dict]]:
    """Load training history from checkpoint artifacts for all records in a run.

    Returns:
        Dict mapping cell_key to list of epoch history dicts.
    """
    import io

    import torch

    history_data: dict[str, list[dict]] = {}
    records = store.query_records(run_id=run_id)
    for record in records:
        artifacts = store.artifacts.get_for_record(record.record_id)
        for artifact in artifacts:
            if artifact.role.value == "model_checkpoint":
                ckpt_bytes = store.artifacts.get(artifact.digest)
                if ckpt_bytes:
                    try:
                        ckpt = torch.load(
                            io.BytesIO(ckpt_bytes),
                            map_location="cpu",
                            weights_only=False,
                        )
                        if "history" in ckpt:
                            history_data[record.cell_key] = ckpt["history"]
                    except Exception:
                        pass  # Skip corrupted checkpoints
    return history_data


def _compute_ablation_table(
    records: list,
    fixed_axes: dict[str, str],
    varying_axis: str,
    metric: str,
) -> list[dict]:
    """Compute ablation table: metric mean/std per value of varying_axis.

    Args:
        records: List of records to analyze.
        fixed_axes: Dict of axis -> value to filter on (e.g., {"substrate": "digital"}).
        varying_axis: Axis to ablate over (e.g., "credit").
        metric: Payload key to aggregate (e.g., "val_acc").

    Returns:
        List of dicts with axis value, mean, std, count.
    """
    import statistics
    from collections import defaultdict

    # Filter records matching fixed axes
    filtered = []
    for r in records:
        match = True
        for axis, value in fixed_axes.items():
            if getattr(r, axis) != value:
                match = False
                break
        if match:
            filtered.append(r)

    # Group by varying axis
    groups: dict[str, list[float]] = defaultdict(list)
    for r in filtered:
        val = r.payload.get(metric)
        if val is not None:
            groups[getattr(r, varying_axis)].append(float(val))

    # Compute statistics
    result = []
    for axis_val, vals in sorted(groups.items()):
        if vals:
            result.append({
                varying_axis: axis_val,
                "mean": statistics.mean(vals),
                "std": statistics.stdev(vals) if len(vals) > 1 else 0.0,
                "count": len(vals),
                "min": min(vals),
                "max": max(vals),
            })
    return result


def generate_html_report(
    store: RecordStore,
    run_id: str,
    output_path: str | Path | None = None,
) -> Path:
    """Generate a comprehensive interactive HTML report for a run.

    Includes:
    - Multiple Pareto frontiers (accuracy vs walltime, accuracy vs params, stability vs plasticity)
    - Convergence curves (loss/accuracy per epoch, per seed)
    - Objective distributions
    - Credit vs Update performance heatmap
    - Substrate comparison
    - Per-axis ablation tables

    Args:
        store: Record store containing the run data.
        run_id: Run ID to generate report for.
        output_path: Optional output file path. Defaults to {run_id}_report.html.

    Returns:
        Path to the generated HTML file.
    """
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        raise ImportError(
            "plotly required for HTML report. Install with: uv add plotly"
        )

    generator = ReportGenerator(store)
    summary = generator.run_summary(run_id)
    if summary is None:
        raise ValueError(f"Run {run_id} not found")

    # Get claim-eligible records for Pareto analysis
    eligible_records = generator.claim_eligible_records(run_id)
    # Fallback to all records if no claim-eligible records
    if not eligible_records:
        eligible_records = generator._store.query_records(run_id=run_id)
    if not eligible_records:
        raise ValueError(f"No records for run {run_id}")

    # Get objectives for this run
    objectives = generator.claim_metrics(run_id)
    if len(objectives) < 2:
        objectives = generator.front_objectives(run_id)

    # Prepare data for plotting
    plot_data = []
    for record in eligible_records:
        row = {
            "record_id": record.record_id[:12],
            "cell_key": record.cell_key[:12],
            "dynamics": record.dynamics,
            "credit": record.credit,
            "update": record.update,
            "substrate": record.substrate,
            "geometry": record.geometry,
            "plasticity": record.plasticity,
            "seed": record.schedule.seed,
        }
        for obj in objectives:
            row[obj] = record.payload.get(obj)
        # Add all available metrics for ablation analysis
        for key, value in record.payload.items():
            if isinstance(value, int | float) and not isinstance(value, bool):
                if key not in row:
                    row[key] = value
        plot_data.append(row)

    if not plot_data:
        raise ValueError("No valid data for plotting")

    # Load training history from checkpoints
    history_data = _load_training_history(store, run_id)

    # Filter records with primary objectives present
    obj_x, obj_y = objectives[0], objectives[1]
    plot_data = [
        r for r in plot_data if r.get(obj_x) is not None and r.get(obj_y) is not None
    ]

    # Create comprehensive dashboard with 3 rows x 3 cols
    fig = make_subplots(
        rows=3,
        cols=3,
        subplot_titles=(
            f"Pareto: {obj_x.replace('_', ' ').title()} vs {obj_y.replace('_', ' ').title()}",
            "Pareto: Validation Accuracy vs Params",
            "Pareto: Spectral Radius vs Plasticity Capacity",
            "Convergence: Train/Val Loss per Epoch",
            "Convergence: Train/Val Accuracy per Epoch",
            "Objective Distributions",
            "Credit vs Update Heatmap",
            "Substrate Comparison",
            "Stability Metrics: ρ(J) vs σ_max",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}, {"type": "box"}],
            [{"type": "heatmap"}, {"type": "scatter"}, {"type": "scatter"}],
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.06,
    )

    # ===== ROW 1: PARETO FRONTIERS =====

    # Plot 1: Primary Pareto frontier
    x_vals = [r[obj_x] for r in plot_data]
    y_vals = [r[obj_y] for r in plot_data]

    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            name="All Cells",
            marker=dict(size=8, opacity=0.6, color="lightblue"),
            text=[
                f"{r['cell_key']}<br>{r['dynamics']}/{r['credit']}/{r['update']}"
                for r in plot_data
            ],
            hovertemplate="%{text}<br>%{xaxis_title}: %{x:.4g}<br>%{yaxis_title}: %{y:.4g}<extra></extra>",
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    pareto_points = generator.pareto_frontier(run_id, (obj_x, obj_y))
    if pareto_points:
        pareto_x = [p["objectives"][obj_x] for p in pareto_points]
        pareto_y = [p["objectives"][obj_y] for p in pareto_points]
        fig.add_trace(
            go.Scatter(
                x=pareto_x,
                y=pareto_y,
                mode="markers+lines",
                name="Pareto Frontier",
                marker=dict(size=12, color="red", symbol="diamond"),
                line=dict(color="red", dash="dot"),
                text=[
                    f"{p['cell_key']}<br>{p['coordinate']['dynamics']}/{p['coordinate']['credit']}/{p['coordinate']['update']}"
                    for p in pareto_points
                ],
                hovertemplate="%{text}<br>%{xaxis_title}: %{x:.4g}<br>%{yaxis_title}: %{y:.4g}<extra></extra>",
                showlegend=True,
            ),
            row=1,
            col=1,
        )

    fig.update_xaxes(title_text=obj_x.replace("_", " ").title(), row=1, col=1)
    fig.update_yaxes(title_text=obj_y.replace("_", " ").title(), row=1, col=1)

    # Plot 2: Accuracy vs Params Pareto
    if "val_acc" in objectives and "param_count" in objectives:
        acc_vals = [r["val_acc"] for r in plot_data if r.get("val_acc") is not None]
        param_vals = [
            r["param_count"] for r in plot_data if r.get("param_count") is not None
        ]
        if acc_vals and param_vals:
            # Match records with both metrics
            valid_records = [
                r
                for r in plot_data
                if r.get("val_acc") is not None and r.get("param_count") is not None
            ]
            if valid_records:
                fig.add_trace(
                    go.Scatter(
                        x=[r["param_count"] for r in valid_records],
                        y=[r["val_acc"] for r in valid_records],
                        mode="markers",
                        name="Acc vs Params",
                        marker=dict(size=8, opacity=0.6, color="lightgreen"),
                        text=[
                            f"{r['cell_key']}<br>{r['dynamics']}/{r['credit']}/{r['update']}"
                            for r in valid_records
                        ],
                        hovertemplate="%{text}<br>Params: %{x:.0f}<br>Val Acc: %{y:.4g}<extra></extra>",
                        showlegend=False,
                    ),
                    row=1,
                    col=2,
                )
                pareto_acc_param = generator.pareto_frontier(
                    run_id, ("param_count", "val_acc")
                )
                if pareto_acc_param:
                    pareto_x = [
                        p["objectives"]["param_count"] for p in pareto_acc_param
                    ]
                    pareto_y = [p["objectives"]["val_acc"] for p in pareto_acc_param]
                    fig.add_trace(
                        go.Scatter(
                            x=pareto_x,
                            y=pareto_y,
                            mode="markers+lines",
                            name="Acc-Params Frontier",
                            marker=dict(size=12, color="darkgreen", symbol="diamond"),
                            line=dict(color="darkgreen", dash="dot"),
                            showlegend=False,
                        ),
                        row=1,
                        col=2,
                    )
    fig.update_xaxes(title_text="Param Count", type="log", row=1, col=2)
    fig.update_yaxes(title_text="Validation Accuracy", row=1, col=2)

    # Plot 3: Stability vs Plasticity Pareto (ρ(J) vs psi_capacity)
    if "spectral_radius" in objectives and "psi_capacity" in objectives:
        valid_records = [
            r
            for r in plot_data
            if r.get("spectral_radius") is not None
            and r.get("psi_capacity") is not None
        ]
        if valid_records:
            fig.add_trace(
                go.Scatter(
                    x=[r["psi_capacity"] for r in valid_records],
                    y=[r["spectral_radius"] for r in valid_records],
                    mode="markers",
                    name="Stability vs Plasticity",
                    marker=dict(size=8, opacity=0.6, color="orange"),
                    text=[
                        f"{r['cell_key']}<br>{r['dynamics']}/{r['credit']}/{r['update']}/{r['plasticity']}"
                        for r in valid_records
                    ],
                    hovertemplate="%{text}<br>Psi Capacity: %{x:.0f}<br>ρ(J): %{y:.4g}<extra></extra>",
                    showlegend=False,
                ),
                row=1,
                col=3,
            )
    fig.update_xaxes(title_text="Psi Capacity", row=1, col=3)
    fig.update_yaxes(title_text="Spectral Radius ρ(J)", row=1, col=3)

    # ===== ROW 2: CONVERGENCE CURVES =====

    # Plot 4: Convergence - Loss per epoch
    has_history = len(history_data) > 0
    if has_history:
        for cell_key, history in list(history_data.items())[
            :10
        ]:  # Limit to 10 cells for readability
            epochs = [h["epoch"] for h in history]
            train_loss = [h.get("train_loss", 0) for h in history]
            val_loss = [h.get("val_loss", 0) for h in history]
            fig.add_trace(
                go.Scatter(
                    x=epochs,
                    y=train_loss,
                    mode="lines+markers",
                    name=f"{cell_key[:8]} train",
                    line=dict(width=1),
                    marker=dict(size=4),
                    opacity=0.7,
                    showlegend=False,
                    legendgroup=cell_key,
                ),
                row=2,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=epochs,
                    y=val_loss,
                    mode="lines+markers",
                    name=f"{cell_key[:8]} val",
                    line=dict(width=1, dash="dot"),
                    marker=dict(size=4),
                    opacity=0.7,
                    showlegend=False,
                    legendgroup=cell_key,
                ),
                row=2,
                col=1,
            )
    else:
        fig.add_annotation(
            text="No checkpoint history available",
            xref="x4",
            yref="y4",
            x=0.5,
            y=0.5,
            showarrow=False,
            row=2,
            col=1,
        )
    fig.update_xaxes(title_text="Epoch", row=2, col=1)
    fig.update_yaxes(title_text="Loss", row=2, col=1)

    # Plot 5: Convergence - Accuracy per epoch
    if has_history:
        for cell_key, history in list(history_data.items())[:10]:
            epochs = [h["epoch"] for h in history]
            train_acc = [h.get("train_acc", 0) for h in history]
            val_acc = [h.get("val_acc", 0) for h in history]
            fig.add_trace(
                go.Scatter(
                    x=epochs,
                    y=train_acc,
                    mode="lines+markers",
                    name=f"{cell_key[:8]} train",
                    line=dict(width=1),
                    marker=dict(size=4),
                    opacity=0.7,
                    showlegend=False,
                    legendgroup=f"{cell_key}_acc",
                ),
                row=2,
                col=2,
            )
            fig.add_trace(
                go.Scatter(
                    x=epochs,
                    y=val_acc,
                    mode="lines+markers",
                    name=f"{cell_key[:8]} val",
                    line=dict(width=1, dash="dot"),
                    marker=dict(size=4),
                    opacity=0.7,
                    showlegend=False,
                    legendgroup=f"{cell_key}_acc",
                ),
                row=2,
                col=2,
            )
    else:
        fig.add_annotation(
            text="No checkpoint history available",
            xref="x5",
            yref="y5",
            x=0.5,
            y=0.5,
            showarrow=False,
            row=2,
            col=2,
        )
    fig.update_xaxes(title_text="Epoch", row=2, col=2)
    fig.update_yaxes(title_text="Accuracy", row=2, col=2)

    # Plot 6: Objective distributions (box plots)
    for obj in objectives[:6]:
        vals = [r[obj] for r in plot_data if r.get(obj) is not None]
        if vals:
            fig.add_trace(
                go.Box(
                    y=vals,
                    name=obj.replace("_", " ").title(),
                    boxmean=True,
                    showlegend=False,
                ),
                row=2,
                col=3,
            )
    fig.update_yaxes(title_text="Value", row=2, col=3)

    # ===== ROW 3: ABLATION & COMPARISON =====

    # Plot 7: Credit vs Update heatmap (mean val_acc)
    credit_vals = sorted(set(r["credit"] for r in plot_data))
    update_vals = sorted(set(r["update"] for r in plot_data))
    if credit_vals and update_vals and "val_acc" in objectives:
        heatmap_data = []
        heatmap_text = []
        for credit in credit_vals:
            row_vals = []
            row_text = []
            for update in update_vals:
                subset = [
                    r
                    for r in plot_data
                    if r["credit"] == credit
                    and r["update"] == update
                    and r.get("val_acc") is not None
                ]
                if subset:
                    mean_acc = sum(r["val_acc"] for r in subset) / len(subset)
                    row_vals.append(mean_acc)
                    row_text.append(
                        f"{credit}/{update}<br>acc={mean_acc:.3f}<br>n={len(subset)}"
                    )
                else:
                    row_vals.append(None)
                    row_text.append("")
            heatmap_data.append(row_vals)
            heatmap_text.append(row_text)

        fig.add_trace(
            go.Heatmap(
                z=heatmap_data,
                x=update_vals,
                y=credit_vals,
                text=heatmap_text,
                texttemplate="%{text}",
                colorscale="Viridis",
                colorbar=dict(title="Val Acc"),
                showscale=True,
                hoverongaps=False,
            ),
            row=3,
            col=1,
        )
    fig.update_xaxes(title_text="Update", row=3, col=1)
    fig.update_yaxes(title_text="Credit", row=3, col=1)

    # Plot 8: Substrate comparison
    substrates = sorted(set(r["substrate"] for r in plot_data))
    for substrate in substrates:
        sub_data = [
            r
            for r in plot_data
            if r["substrate"] == substrate
            and r.get(obj_x) is not None
            and r.get(obj_y) is not None
        ]
        if sub_data:
            fig.add_trace(
                go.Scatter(
                    x=[r[obj_x] for r in sub_data],
                    y=[r[obj_y] for r in sub_data],
                    mode="markers",
                    name=f"Substrate: {substrate}",
                    marker=dict(size=8),
                    text=[
                        f"{r['dynamics']}/{r['credit']}/{r['update']}" for r in sub_data
                    ],
                    hovertemplate="%{text}<br>%{xaxis_title}: %{x:.4g}<br>%{yaxis_title}: %{y:.4g}<extra></extra>",
                    showlegend=False,
                ),
                row=3,
                col=2,
            )
    fig.update_xaxes(title_text=obj_x.replace("_", " ").title(), row=3, col=2)
    fig.update_yaxes(title_text=obj_y.replace("_", " ").title(), row=3, col=2)

    # Plot 9: Stability metrics scatter (ρ(J) vs σ_max)
    stability_records = [
        r
        for r in plot_data
        if r.get("spectral_radius") is not None
        and r.get("max_singular_value") is not None
    ]
    if stability_records:
        fig.add_trace(
            go.Scatter(
                x=[r["spectral_radius"] for r in stability_records],
                y=[r["max_singular_value"] for r in stability_records],
                mode="markers",
                name="Stability",
                marker=dict(
                    size=10,
                    color=[r.get("val_acc", 0) for r in stability_records],
                    colorscale="RdYlGn",
                    showscale=True,
                    colorbar=dict(title="Val Acc"),
                ),
                text=[
                    f"{r['cell_key']}<br>{r['dynamics']}/{r['credit']}/{r['update']}<br>ρ={r['spectral_radius']:.4f}<br>σ_max={r['max_singular_value']:.4f}"
                    for r in stability_records
                ],
                hovertemplate="%{text}<extra></extra>",
                showlegend=False,
            ),
            row=3,
            col=3,
        )
        # Add diagonal line y=x (where σ_max = ρ)
        max_val = max(
            max(r["spectral_radius"] for r in stability_records),
            max(r["max_singular_value"] for r in stability_records),
        )
        fig.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode="lines",
                name="σ_max = ρ(J)",
                line=dict(color="gray", dash="dash", width=1),
                showlegend=False,
            ),
            row=3,
            col=3,
        )
    fig.update_xaxes(title_text="Spectral Radius ρ(J)", row=3, col=3)
    fig.update_yaxes(title_text="Max Singular Value σ_max", row=3, col=3)

    # Update layout
    fig.update_layout(
        title=f"Run Report: {run_id} (Status: {summary.status})",
        height=1400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        margin=dict(t=100, b=50, l=50, r=50),
    )

    # Generate HTML
    output_file = Path(output_path) if output_path else Path(f"{run_id}_report.html")
    output_file.write_text(fig.to_html(include_plotlyjs="cdn"), encoding="utf-8")

    return output_file


def export_to_json(  # ruff: ignore[too-many-locals]
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


def _generate_latex_report(
    store: RecordStore,
    run_id: str,
    output_path: str | Path,
) -> Path:
    """Generate a LaTeX report for a run.

    Args:
        store: Record store containing the run data.
        run_id: Run ID to generate report for.
        output_path: Output file path for .tex file.

    Returns:
        Path to the generated LaTeX file.
    """
    generator = ReportGenerator(store)
    summary = generator.run_summary(run_id)
    if summary is None:
        raise ValueError(f"Run {run_id} not found")

    eligible = generator.claim_eligible_records(run_id)
    claims = generator.claims(run_id)
    limitations = generator.limitations(run_id)
    pareto = generator.pareto_frontier(run_id)
    axis_frontiers = generator.axis_frontiers(run_id)
    significance = generator.significance(run_id)

    # Escape LaTeX special characters
    def escape_latex(text: str) -> str:
        replacements = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
            "\\": r"\textbackslash{}",
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    lines = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\usepackage{geometry}",
        r"\geometry{margin=1in}",
        r"\usepackage{hyperref}",
        r"\usepackage{graphicx}",
        r"\usepackage{amsmath}",
        r"\usepackage{amssymb}",
        r"\title{Computronium Run Report: " + escape_latex(run_id) + "}",
        r"\author{Generated by \texttt{comp report}}",
        r"\date{" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "}",
        r"\begin{document}",
        r"\maketitle",
        "",
        r"\section{Run Summary}",
        r"\begin{tabular}{ll}",
        r"  Status & " + escape_latex(summary.status) + r" \\",
        r"  Started & " + escape_latex(str(summary.started_at)) + r" \\",
        r"  Finished & " + escape_latex(str(summary.finished_at or "N/A")) + r" \\",
        r"  Budget Consumed (s) & " + f"{summary.budget_consumed_s or 0:.1f}" + r" \\",
        r"  Replay Hash & " + escape_latex(summary.replay_hash or "N/A") + r" \\",
        r"  Spec Version & " + str(summary.spec_version) + r" \\",
        r"\end{tabular}",
        "",
        r"\section{Record Statistics}",
        r"\begin{tabular}{lr}",
        r"  \textbf{Metric} & \textbf{Value} \\",
        r"  \midrule",
        f"  Total Records & {summary.record_count} \\",
        f"  Claim Eligible & {summary.claim_eligible_count} \\",
        f"  Promoted & {summary.promoted_count} \\",
        f"  Declared Cells & {summary.declared_cells} \\",
        r"\end{tabular}",
        "",
    ]

    # Economics
    if summary.record_count > 0 and summary.budget_consumed_s is not None:
        cost_per_record = summary.budget_consumed_s / summary.record_count
        lines.extend([
            r"\section{Campaign Economics}",
            r"\begin{tabular}{lr}",
            r"  \textbf{Metric} & \textbf{Value} \\",
            r"  \midrule",
            f"  Cost per Record (s) & {cost_per_record:.3f} \\",
        ])
        if summary.declared_cells > 0:
            projected_total = cost_per_record * summary.declared_cells
            remaining_cells = summary.declared_cells - summary.record_count
            projected_remaining = cost_per_record * remaining_cells
            progress = (summary.record_count / summary.declared_cells) * 100
            lines.extend([
                f"  Projected Total (s) & {projected_total:.1f} \\",
                f"  Remaining (s) & {projected_remaining:.1f} \\",
                f"  Progress \\% & {progress:.1f} \\\\",
            ])
        lines.extend([r"\end{tabular}", ""])

    # Claims
    if claims:
        lines.extend([
            r"\section{Claims}",
            r"\begin{longtable}{llllll}",
            r"  \textbf{Metric} & \textbf{Axis} & \textbf{Value} & \textbf{Mean} & \textbf{Std} & \textbf{n} \\",
            r"  \midrule",
            r"  \endhead",
        ])
        for claim in claims:
            lines.append(
                f"  {escape_latex(claim.metric)} & {escape_latex(claim.axis)} & "
                f"{escape_latex(claim.value)} & {claim.mean:.4g} & {claim.std:.4g} & {claim.n_seeds} \\"
            )
        lines.extend([r"\end{longtable}", ""])

        if significance is not None:
            lines.extend([
                r"\subsection{Significance Test}",
                f"  Axis: {escape_latex(significance.axis)}, Metric: {escape_latex(significance.metric)} \\",
                f"  Best: {escape_latex(significance.best_value)} (n={significance.n_best}), "
                f"Worst: {escape_latex(significance.worst_value)} (n={significance.n_worst}) \\",
                f"  Test: {escape_latex(significance.test)}, p-value: {significance.p_value:.4g} \\",
                f"  Effect size: {significance.effect_size:.4g}, Significant: {significance.significant} \\",
                "",
            ])

    # Limitations
    if limitations:
        lines.extend([
            r"\section{Limitations}",
            r"\begin{itemize}",
        ])
        for lim in limitations:
            lines.append(
                r"  \item ["
                + escape_latex(f"[{lim.kind}]")
                + r"] "
                + escape_latex(lim.detail)
                + r" \\ Evidence: "
                + escape_latex(lim.evidence)
            )
        lines.extend([r"\end{itemize}", ""])

    # Pareto Frontier
    if pareto:
        obj_names = list(pareto[0]["objectives"].keys()) if pareto else []
        lines.extend([
            r"\section{Pareto Frontier}",
            f"  Objectives: {', '.join(escape_latex(o) for o in obj_names)} \\",
            r"\begin{longtable}{llllll}",
            r"  \textbf{Record} & \textbf{Cell} & "
            + " & ".join(escape_latex(o.replace("_", " ").title()) for o in obj_names)
            + r" & \textbf{Coordinate} \\",
            r"  \midrule",
            r"  \endhead",
        ])
        for point in pareto[:20]:
            coord = point["coordinate"]
            coord_str = f"{coord['dynamics']}/{coord['credit']}/{coord['update']}"
            obj_vals = " & ".join(f"{point['objectives'][o]:.4g}" for o in obj_names)
            lines.append(
                f"  {escape_latex(point['record_id'][:12])} & {escape_latex(point['cell_key'][:12])} "
                f"& {obj_vals} & {escape_latex(coord_str)} \\"
            )
        lines.extend([r"\end{longtable}", ""])

    # Axis Frontiers
    if axis_frontiers:
        lines.extend([r"\section{Axis-Aligned Pareto Frontiers}", ""])
        for axis, front in axis_frontiers.items():
            if not front:
                continue
            obj_names = list(front[0]["objectives"].keys())
            lines.extend([
                r"\subsection{" + escape_latex(axis) + "}",
                f"  Objectives: {', '.join(escape_latex(o) for o in obj_names)} \\",
                r"\begin{longtable}{lllll}",
                r"  \textbf{Record} & \textbf{Cell} & "
                + " & ".join(
                    escape_latex(o.replace("_", " ").title()) for o in obj_names
                )
                + r" & \textbf{Coordinate} \\",
                r"  \midrule",
                r"  \endhead",
            ])
            for point in front[:10]:
                coord = point["coordinate"]
                coord_str = f"{coord['dynamics']}/{coord['credit']}/{coord['update']}"
                obj_vals = " & ".join(
                    f"{point['objectives'][o]:.4g}" for o in obj_names
                )
                lines.append(
                    f"  {escape_latex(point['record_id'][:12])} & {escape_latex(point['cell_key'][:12])} "
                    f"& {obj_vals} & {escape_latex(coord_str)} \\"
                )
            lines.extend([r"\end{longtable}", ""])

    # Distribution tables
    for title, dist in [
        ("Maturity Distribution", generator.maturity_distribution(run_id)),
        ("Gate Verdict Distribution", generator.gate_verdict_distribution(run_id)),
    ]:
        if dist:
            lines.extend([
                r"\section{" + escape_latex(title) + "}",
                r"\begin{tabular}{lr}",
                r"  \textbf{Category} & \textbf{Count} \\",
                r"  \midrule",
            ])
            for cat, count in sorted(dist.items()):
                lines.append(f"  {escape_latex(cat)} & {count} \\")
            lines.extend([r"\end{tabular}", ""])

    lines.append(r"\end{document}")

    output_file = Path(output_path)
    output_file.write_text("\n".join(lines), encoding="utf-8")
    return output_file


def generate_latex_report(
    store: RecordStore,
    run_id: str,
    output_path: str | Path | None = None,
) -> Path:
    """Generate a LaTeX report for a run.

    Args:
        store: Record store containing the run data.
        run_id: Run ID to generate report for.
        output_path: Optional output file path. Defaults to {run_id}_report.tex.

    Returns:
        Path to the generated LaTeX file.
    """
    output_file = Path(output_path) if output_path else Path(f"{run_id}_report.tex")
    return _generate_latex_report(store, run_id, output_file)


def generate_pdf_report(
    store: RecordStore,
    run_id: str,
    output_path: str | Path | None = None,
    keep_tex: bool = False,
) -> Path:
    """Generate a PDF report via pandoc from LaTeX.

    Requires pandoc to be installed: https://pandoc.org/installing.html

    Args:
        store: Record store containing the run data.
        run_id: Run ID to generate report for.
        output_path: Optional output file path. Defaults to {run_id}_report.pdf.
        keep_tex: If True, keep the intermediate .tex file.

    Returns:
        Path to the generated PDF file.

    Raises:
        RuntimeError: If pandoc is not available or conversion fails.
    """
    import shutil
    import subprocess

    # Check if pandoc is available
    if not shutil.which("pandoc"):
        raise RuntimeError(
            "pandoc not found in PATH. Install pandoc to generate PDF reports: "
            "https://pandoc.org/installing.html"
        )

    output_file = Path(output_path) if output_path else Path(f"{run_id}_report.pdf")
    tex_file = output_file.with_suffix(".tex")

    # Generate LaTeX first
    _generate_latex_report(store, run_id, tex_file)

    # Convert to PDF via pandoc
    try:
        result = subprocess.run(
            [
                "pandoc",
                str(tex_file),
                "-o",
                str(output_file),
                "--pdf-engine=xelatex",
                "-V",
                "geometry:margin=1in",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pandoc failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("pandoc timed out after 120 seconds")
    except Exception as e:
        raise RuntimeError(f"PDF generation failed: {e}")

    # Clean up .tex file unless requested to keep
    if not keep_tex and tex_file.exists():
        tex_file.unlink()

    return output_file
