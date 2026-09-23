"""Broad mapping sweep (TODO28 Phase 1) — stratified random atlas sampling.

The G1 coverage sweep walks registry product order and stays trapped in one
dynamics slice. This campaign instead samples **uniformly at random** across
the full dynamics × credit × update × topology grid, stratified so every
dynamics family receives an equal share of proposals — the data shape a
high-dimensional visualization (UMAP/t-SNE) needs.

Epistemic rule (TODO28 §1): dry-run-rejected cells are **structural voids**,
not experiments. They are recorded to ``structural_voids.jsonl`` (and marked
covered in the KB) but never pre-registered in the CEEC ledger. Every cell
that passes the gate is pre-registered, executed, and ledgered as usual.

Usage::

    nohup uv run comp continuous --budget 5m \
        --root artifacts/broad_map > logs/broad_map.log 2>&1 &

or via the thin wrapper::

    nohup uv run python scripts/broad_mapping_sweep.py \
        --sample-size 500 --epochs 1 \
        --root artifacts/broad_map > logs/broad_map.log 2>&1 &
"""

from __future__ import annotations

import json
import logging
import random
import re
import time
import traceback
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Protocol

from computronium.autoscientist.bridge import ExperimentProposal
from computronium.autoscientist.campaign import AutoScientistCampaign
from computronium.autoscientist.defects import (
    DefectRecord,
    append_defect,
    defect_id,
    quarantined_cells,
    read_defects,
)
from computronium.autoscientist.objectives import (
    DEFAULT_OBJECTIVES,
    ObjectiveSpec,
)
from computronium.autoscientist.proposer import (
    GRID_CREDITS,
    GRID_DYNAMICS,
    GRID_TOPOLOGIES,
    GRID_UPDATES,
    cell_key,
)
from computronium.utils import seed_everything

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable
    from pathlib import Path

    from computronium.knowledge import KnowledgeBase
    from computronium.ontology import GeometryConfig

logger = logging.getLogger("broad_map")

_DURATION_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([smh]?)\s*$", re.IGNORECASE)
_DURATION_SCALES: dict[str, float] = {"": 1.0, "s": 1.0, "m": 60.0, "h": 3600.0}


@dataclass(frozen=True, slots=True)
class ContinuousBudget:
    """Budget for one burst of continuous discovery (TODO29 Phase 3).

    Frozen value object: ``advance``/``advance_by`` return fresh instances.
    ``target_cells`` is a hard cap on completed cells; ``soft_seconds`` stops
    *starting* new cells past the anchor; ``hard_seconds`` is the stricter
    between-cells ceiling for loop drivers.
    """

    started_at: float  # time.monotonic() anchor
    soft_seconds: float | None = None
    hard_seconds: float | None = None
    target_cells: int | None = None
    done: int = 0

    @classmethod
    def parse(cls, spec: str, *, started_at: float | None = None) -> ContinuousBudget:
        """Parse ``"5m"``/``"90s"``/``"1h"``/``"3600"`` into a soft+hard
        budget anchored at ``started_at`` (default: now, monotonic)."""
        match = _DURATION_RE.match(spec)
        if match is None:
            raise ValueError(
                f"invalid budget {spec!r}: expected '<n><s|m|h>' (e.g. 5m, 90s, 1h)"
            )
        seconds = float(match.group(1)) * _DURATION_SCALES[match.group(2).lower()]
        return cls(
            started_at=time.monotonic() if started_at is None else started_at,
            soft_seconds=seconds,
            hard_seconds=seconds,
        )

    def soft_expired(self, now: float) -> bool:
        return (
            self.soft_seconds is not None and now - self.started_at >= self.soft_seconds
        )

    def hard_expired(self, now: float) -> bool:
        return (
            self.hard_seconds is not None and now - self.started_at >= self.hard_seconds
        )

    def target_reached(self) -> bool:
        return self.target_cells is not None and self.done >= self.target_cells

    def advance(self) -> ContinuousBudget:
        return self.advance_by(1)

    def advance_by(self, n: int) -> ContinuousBudget:
        return replace(self, done=self.done + n)


def enumerate_constraint_voids(
    kb_path: Path, voids_path: Path, *, task: str
) -> set[str]:
    """Walk the full grid product through ``SystemConfig.validate()``.

    Constraint rejections are structural voids (TODO28): enumerate every
    dynamics × credit × update × topology combination cheaply — no GPU,
    no training — writing each rejection to ``structural_voids.jsonl`` and
    returning the viable cell keys. The sampler then draws only viable
    cells, so governed budget is never spent proposing known-rejected
    coordinates.
    """
    from computronium.ontology import (
        CreditAssignmentConfig,
        DigitalSubstrate,
        ParameterUpdateConfig,
        StateDynamicsConfig,
    )
    from computronium.ontology.system import SystemConfig

    substrate = DigitalSubstrate().config
    viable: set[str] = set()
    fresh_rows: list[str] = []
    known = (
        {
            (r["dynamics"], r["credit"], r["update"], r["topology"])
            for r in (
                json.loads(line)
                for line in voids_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        }
        if voids_path.exists()
        else set()
    )
    for dynamics in GRID_DYNAMICS:
        dcfg = getattr(StateDynamicsConfig, dynamics)()
        for credit in GRID_CREDITS:
            ccfg = getattr(CreditAssignmentConfig, credit)()
            for update in GRID_UPDATES:
                try:
                    ucfg = getattr(ParameterUpdateConfig, update)()
                except TypeError:
                    continue
                for topology in GRID_TOPOLOGIES:
                    if (dynamics, credit, update, topology) in known:
                        continue
                    try:
                        SystemConfig(
                            substrate=substrate,
                            geometry=_geometry_for(topology),
                            dynamics=dcfg,
                            credit=ccfg,
                            update=ucfg,
                        ).validate()
                    except ValueError as exc:
                        fresh_rows.append(
                            json.dumps({
                                "timestamp": time.time(),
                                "task": task,
                                "dynamics": dynamics,
                                "credit": credit,
                                "update": update,
                                "topology": topology,
                                "category": classify_void(str(exc)),
                                "error": str(exc)[:300],
                            })
                            + "\n"
                        )
                    else:
                        viable.add(cell_key(dynamics, credit, update, topology))
    if fresh_rows:
        voids_path.parent.mkdir(parents=True, exist_ok=True)
        with voids_path.open("a", encoding="utf-8") as fh:
            fh.writelines(fresh_rows)
    logger.info(
        "Constraint enumeration: %d viable / %d void cells (%d new)",
        len(viable),
        len(fresh_rows),
        len(fresh_rows),
    )
    return viable


def _geometry_for(topology: str) -> GeometryConfig:
    from computronium.autoscientist.compose import build_geometry_config

    return build_geometry_config(
        {"topology_type": topology, "depth": 2, "hidden_dim": 64},
        input_dim=256,
        output_dim=10,
    )


class StratifiedRandomDriver:
    """Propose uniformly random grid cells, stratified evenly by dynamics.

    Fulfills the campaign's ``propose_batch`` contract. Novelty is the
    in-process cell-key set seeded from the KB coverage matrix, so a resumed
    run does not re-measure cells the G1 sweep already covered.

    Improvement: balances (dynamics, credit, update) triples so no river axis
    starves at small sample sizes (TODO28 improvement opportunity 1).

    Phase 2 (TODO31): Accepts ``objectives`` for objective-space exploration
    bias — prefers cells in under-explored regions of the Pareto front.
    """

    def __init__(  # ruff: ignore[too-many-arguments] (driver mirrors sweep axes)
        self,
        kb_path: Path,
        *,
        task: str,
        cells: int,
        epochs: int,
        seed: int,
        depth: int = 2,
        hidden_dim: int = 64,
        param_budget: int = 0,
        credit_trace: bool = False,
        limit_batches: int = 0,
        viable: frozenset[str] | None = None,
        defects_path: Path | None = None,
        burst_tag: str | None = None,
        objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
    ) -> None:
        # Sampling RNG, not security-sensitive (S311).
        self.rng = random.Random(seed)  # ruff: ignore[suspicious-non-cryptographic-random-usage] (sampling, not crypto)
        self.task = task
        self.cells = cells
        self.epochs = epochs
        self.depth = depth
        self.hidden_dim = hidden_dim
        self.param_budget = param_budget
        self.credit_trace = credit_trace
        self.limit_batches = limit_batches
        self.viable = viable
        self.defects_path = defects_path
        self.burst_tag = burst_tag
        self.objectives = objectives
        self.seen: set[str] = set()
        self.quarantined: frozenset[str] = frozenset()
        self._reload_covered(kb_path)
        # Balance tracked per (dynamics, credit, update) triple
        self.balance: dict[tuple[str, str, str], int] = {}
        for d in GRID_DYNAMICS:
            for c in GRID_CREDITS:
                for u in GRID_UPDATES:
                    self.balance[d, c, u] = 0
        # Objective-space coverage tracking (Phase 2)
        self._objective_bins: dict[str, int] = {}
        self._obj_min: list[float] = []
        self._obj_max: list[float] = []
        self._load_objective_coverage(kb_path)

    def _load_objective_coverage(self, kb_path: Path) -> None:
        """Seed objective-space bins from existing KB measurements."""
        if not kb_path.exists() or len(self.objectives) < 2:
            return
        import numpy as np

        from computronium.knowledge import KnowledgeBase

        kb = KnowledgeBase(kb_path)
        obj_names = [o.name.value for o in self.objectives]
        points: list[list[float]] = []
        for entry in kb.query():
            if not str(entry.topic).startswith("experiment:"):
                continue
            metrics = entry.metrics
            pt = []
            for name in obj_names:
                val = metrics.get(name)
                if isinstance(val, int | float):
                    pt.append(float(val))
                else:
                    break
            else:
                points.append(pt)
        if not points:
            return
        arr = np.array(points)
        # Simple binning: quantile-based bins per objective
        self._obj_min = arr.min(axis=0).tolist()
        self._obj_max = arr.max(axis=0).tolist()
        for pt in points:
            bin_key = self._bin_point(pt)
            self._objective_bins[bin_key] = self._objective_bins.get(bin_key, 0) + 1
        logger.info(
            "Objective-space coverage: %d bins populated", len(self._objective_bins)
        )

    def _bin_point(self, pt: list[float]) -> str:
        """Quantize a point in objective space to a bin key."""
        bins_per_dim = 5
        coords = []
        for i, val in enumerate(pt):
            lo, hi = self._obj_min[i], self._obj_max[i]
            if hi <= lo:
                coords.append(0)
            else:
                normalized = (val - lo) / (hi - lo)
                coords.append(min(bins_per_dim - 1, int(normalized * bins_per_dim)))
        return ",".join(str(c) for c in coords)

    def _score_proposal(
        self, dynamics: str, credit: str, update: str, topology: str
    ) -> float:
        """Score a proposal by how under-explored its predicted objective region is.

        Returns a score where higher = more under-explored (preferred).
        """
        if not self._objective_bins or len(self.objectives) < 2:
            return self.rng.random()  # No bias if no objective data
        # Predict objective values based on (dynamics, credit, update) family
        # For now, use family averages from KB; fallback to random
        # We don't have a predictor yet, so use balance as proxy
        # Cells from under-sampled strata are more likely to be in novel objective regions
        stratum_count = self.balance.get((dynamics, credit, update), 0)
        return 1.0 / (1.0 + stratum_count) + self.rng.random() * 0.1

    def _reload_covered(self, kb_path: Path) -> None:
        """Seed the seen-set from the KB coverage matrix (structural voids
        included: a void is covered — it can never execute) and the
        quarantine set from the defect stream (TODO29: cells with an open
        defect are skipped until the code changes)."""
        if self.defects_path is not None:
            self.quarantined = quarantined_cells(read_defects(self.defects_path))
            if self.quarantined:
                logger.info(
                    "Quarantine seed: %d cells with open defects",
                    len(self.quarantined),
                )
        if not kb_path.exists():
            return
        from computronium.knowledge import KnowledgeBase

        kb = KnowledgeBase(kb_path)
        for entry in kb.query():
            hp = entry.hyperparameters
            if not (hp.get("dynamics") and hp.get("credit") and hp.get("update")):
                continue
            geometry = hp.get("geometry") or {}
            if not isinstance(geometry, dict):
                continue
            self.seen.add(
                cell_key(
                    str(hp["dynamics"]),
                    str(hp["credit"]),
                    str(hp["update"]),
                    str(geometry.get("topology_type", "feedforward")),
                )
            )
        logger.info("Coverage seed: %d known cells", len(self.seen))

    def has_novel(self) -> bool:
        """Random sampling over a large grid: novel cells effectively always
        remain; the caller's sample-size/iteration caps end the campaign."""
        return True

    def propose_batch(
        self, n_proposals: int, recent_results: list[dict[str, object]] | None = None
    ) -> list[ExperimentProposal]:
        proposals: list[ExperimentProposal] = []
        attempts = 0
        while len(proposals) < min(n_proposals, self.cells) and attempts < 200:
            attempts += 1
            # Stratification: the least-proposed (dynamics, credit, update) triple is next.
            (dynamics, credit, update) = min(
                self.balance, key=lambda k: (self.balance[k], self.rng.random())
            )
            # Objective-space bias: sample multiple topologies, prefer under-explored bins
            best_topology = None
            best_score = -1.0
            for topology in self.rng.choices(
                GRID_TOPOLOGIES, k=min(3, len(GRID_TOPOLOGIES))
            ):
                key = cell_key(dynamics, credit, update, topology)
                if (
                    key in self.seen
                    or key in self.quarantined
                    or (self.viable is not None and key not in self.viable)
                ):
                    continue
                score = self._score_proposal(dynamics, credit, update, topology)
                if score > best_score:
                    best_score = score
                    best_topology = topology
            if best_topology is None:
                continue
            topology = best_topology
            key = cell_key(dynamics, credit, update, topology)
            self.seen.add(key)
            stratum_count = self.balance[dynamics, credit, update]
            self.balance[dynamics, credit, update] += 1
            maturity_tags = ["maturity:l0"]
            if self.burst_tag is not None:
                maturity_tags.append(self.burst_tag)
            proposals.append(
                ExperimentProposal(
                    hypothesis=(
                        f"Broad-map cell {key}: stratified by dynamics×credit×update, "
                        f"objective-space score={best_score:.2f}"
                    ),
                    model="eqprop",
                    task=self.task,
                    geometry={
                        "topology_type": topology,
                        "depth": self.depth,
                        "hidden_dim": self.hidden_dim,
                        "init_scheme": "default",
                    },
                    dynamics=dynamics,
                    credit=credit,
                    update=update,
                    hyperparams={
                        "epochs": self.epochs,
                        "param_budget": self.param_budget,
                        "credit_trace": self.credit_trace,
                        "limit_batches": self.limit_batches,
                    },
                    justification=(
                        f"Balancing under-sampled triple "
                        f"{dynamics} × {credit} × {update} — stratum "
                        f"count {stratum_count} before this proposal; "
                        f"topology {topology} chosen by objective-space bias "
                        f"(score={best_score:.2f})"
                    ),
                    expected_outcome="measured cell in the atlas",
                    priority=0.5,
                    tags=["autoscientist", "broad_map", *maturity_tags, key],
                )
            )
        logger.info(
            "Broad-map driver: %d novel cells (%d attempts, balance sample %s)",
            len(proposals),
            attempts,
            dict(list(self.balance.items())[:5]),
        )
        return proposals


_VOID_CATEGORIES: tuple[tuple[str, str], ...] = (
    # Settle→route shape-contract crashes: non-layered geometries assume
    # settle-state shapes; these are implementation boundaries, not ontology
    # physics (TODO28 audit 2026-09-15).
    ("requires a linear-stack geometry", "geometry_constraint"),
    ("layered geometry", "geometry_constraint"),
    ("layer-structured geometry", "geometry_constraint"),
    ("does not support recurrent geometry", "geometry_constraint"),
    ("requires energy-based or instantaneous dynamics", "geometry_constraint"),
    ("state-shape contract", "geometry_constraint"),
    ("non-differentiable settled", "geometry_constraint"),
    ("requires thermodynamic_contrast, local_goodness", "geometry_constraint"),
    ("Tile mesh geometry requires", "geometry_constraint"),
    ("Spike integration dynamics requires temporal trace", "geometry_constraint"),
    ("Thermodynamic contrast credit", "geometry_constraint"),
    ("dynamics requires thermodynamic_contrast", "geometry_constraint"),
    ("one_hot is only applicable", "geometry_constraint"),
    ("is invalid for input of size", "geometry_constraint"),
    ("expects states", "geometry_constraint"),
    ("not enough values to unpack", "settle_route_shape"),
    ("must match the size of tensor", "settle_route_shape"),
    ("normalized_shape", "settle_route_shape"),
    ("does not require grad", "autograd_break"),
)


def classify_void(error: str) -> str:
    """Distinguish ontology voids from implementation-boundary crashes."""
    for needle, category in _VOID_CATEGORIES:
        if needle in error:
            return category
    return "unclassified"


class BroadMappingCampaign(AutoScientistCampaign):
    """Campaign with the two side-channel ledgers (TODO29):

    - dry-run-rejected cells → ``structural_voids.jsonl`` (ontology
      boundaries; never ledgered);
    - gate-passing runtime crashes → ``runtime_defects.jsonl``
      (implementation defects; CEEC-failed by the base class, cell
      quarantined until the code changes).

    Void/defect logging stays outside the CEEC ledger: neither is a
    measured experiment.
    """

    def __init__(
        self,
        *args: object,
        voids_path: Path,
        defects_path: Path | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.voids_path = voids_path
        self.defects_path = defects_path

    def _execute_proposal(
        self, proposal: ExperimentProposal, dry_run: bool = False
    ) -> dict[str, object]:
        try:
            return super()._execute_proposal(proposal, dry_run)
        except Exception as e:  # noqa: BLE001 (base class contracts broad failure)
            if not dry_run and self.defects_path is not None:
                self._record_defect(proposal, e)
            raise

    def _record_defect(self, proposal: ExperimentProposal, error: Exception) -> None:
        """Append one DefectRecord *before* the base class closes the CEEC
        trace — the defect stream is a side-channel, never a ledger path."""
        defects_path = self.defects_path
        if defects_path is None:
            return
        geometry = proposal.geometry or {}
        cell = (
            cell_key(
                str(proposal.dynamics or ""),
                str(proposal.credit or ""),
                str(proposal.update or ""),
                str(geometry.get("topology_type", "feedforward")),
            )
            if proposal.dynamics and proposal.credit and proposal.update
            else f"{proposal.model}:{proposal.task}"
        )
        did = defect_id(type(error).__name__, str(error))
        append_defect(
            defects_path,
            DefectRecord(
                defect_id=did,
                timestamp=time.time(),
                task=proposal.task,
                cell=cell,
                error_class=type(error).__name__,
                message=str(error),
                traceback_tail="\n".join(traceback.format_exc().splitlines()[-15:]),
                status="open",
            ),
        )
        logger.error("Runtime defect %s quarantines cell %s", did, cell)

    def _record_incompatible(self, proposal: ExperimentProposal, error: str) -> None:
        super()._record_incompatible(proposal, error)
        geometry = proposal.geometry or {}
        row = {
            "timestamp": time.time(),
            "task": proposal.task,
            "dynamics": proposal.dynamics,
            "credit": proposal.credit,
            "update": proposal.update,
            "topology": geometry.get("topology_type"),
            "category": classify_void(error),
            "error": error[:300],
        }
        with self.voids_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        logger.info(
            "Structural void: %s|%s|%s|%s",
            proposal.dynamics,
            proposal.credit,
            proposal.update,
            geometry.get("topology_type"),
        )


def driver_seeded_kb(kb_path: Path) -> KnowledgeBase:
    """Shared KB so gate rejections mark coordinates covered across resumes."""
    from computronium.knowledge import KnowledgeBase

    return KnowledgeBase(kb_path)


def build_sweep(
    args: argparse.Namespace,
) -> tuple[BroadMappingCampaign, StratifiedRandomDriver]:
    """Shared construction used by the sweep script and ``comp continuous``:
    void enumeration, stratified driver, defect-wired campaign."""
    from computronium.autoscientist.objectives import parse_objectives

    viable = enumerate_constraint_voids(
        args.root / "kb.sqlite",
        args.root / "structural_voids.jsonl",
        task=args.task,
    )
    obj_spec = getattr(args, "objectives", "accuracy,walltime_s")
    objectives = parse_objectives(obj_spec)
    driver = StratifiedRandomDriver(
        args.root / "kb.sqlite",
        task=args.task,
        cells=args.cells_per_iter,
        epochs=args.epochs,
        seed=args.seed,
        depth=args.depth,
        hidden_dim=args.hidden_dim,
        param_budget=args.param_budget,
        credit_trace=args.credit_trace,
        limit_batches=getattr(args, "limit_batches", 0) or 0,
        viable=frozenset(viable),
        defects_path=args.root / "runtime_defects.jsonl",
        burst_tag=next_burst_tag(args.root / "kb.sqlite"),
        objectives=objectives,
    )
    campaign = BroadMappingCampaign(
        knowledge_base=None,
        output_dir=str(args.root / "campaign"),
        db_path=args.root / "campaign" / "campaign.db",
        branch_name="broad_mapping_sweep",
        ceec_ledger_path=args.root / "ledger.sqlite",
        voids_path=args.root / "structural_voids.jsonl",
        defects_path=args.root / "runtime_defects.jsonl",
    )
    campaign.knowledge_base = driver_seeded_kb(args.root / "kb.sqlite")
    campaign.proposer = driver  # type: ignore[assignment]
    return campaign, driver


class BurstDriver(Protocol):
    """Minimal driver surface ``run_burst`` depends on (the daemon wraps the
    concrete ``StratifiedRandomDriver`` to observe the propose phase)."""

    cells: int

    def propose_batch(
        self, n_proposals: int, recent_results: list[dict[str, object]] | None = None
    ) -> list[ExperimentProposal]: ...

    def has_novel(self) -> bool: ...


_BURST_STOP_REASONS: dict[str, str] = {
    "target": "target cell count reached",
    "soft": "soft budget expired (current cell finished, no new starts)",
    "hard": "hard budget expired",
    "exhausted": "no novel cells left (grid exhausted or all quarantined)",
    "max_iterations": "max iterations reached",
    "paused": "pause requested (in-flight batch finished)",
    "stopped": "graceful stop requested",
}


def budget_from_args(args: argparse.Namespace) -> ContinuousBudget:
    """Burst budget from the shared CLI flags (``--budget``/``--target-cells``)."""
    budget = (
        ContinuousBudget.parse(args.budget)
        if args.budget
        else ContinuousBudget(started_at=time.monotonic())
    )
    if args.target_cells is not None:
        budget = replace(budget, target_cells=args.target_cells)
    return budget


def _absorb_results(
    results: list[dict[str, object]],
    walltime_by_family: dict[str, list[float]],
) -> tuple[int, int]:
    """Fold one iteration's result rows into (completed, failed) counts and
    the per-family walltime accumulator."""
    completed = 0
    failed = 0
    for row in results:
        if row.get("status") == "completed":
            completed += 1
            proposal = row.get("proposal")
            family = (
                str(proposal.get("dynamics", "unknown"))
                if isinstance(proposal, dict)
                else "unknown"
            )
            raw = row.get("walltime_s")
            if isinstance(raw, int | float):
                walltime_by_family.setdefault(family, []).append(float(raw))
        elif row.get("status") == "failed":
            failed += 1
    return completed, failed


def _burst_stop(
    budget: ContinuousBudget,
    gate: Callable[[], str | None] | None,
    now: float,
) -> str | None:
    """Boundary checks in priority order: budget, then lifecycle gate."""
    if budget.target_reached():
        return "target"
    if budget.hard_expired(now):
        return "hard"
    if budget.soft_expired(now):
        return "soft"
    return gate() if gate is not None else None


def run_burst(
    campaign: BroadMappingCampaign,
    driver: BurstDriver,
    budget: ContinuousBudget,
    *,
    max_iterations: int,
    gate: Callable[[], str | None] | None = None,
    on_cell_complete: Callable[[int], None] | None = None,
) -> dict[str, object]:
    """One budgeted burst (TODO29 Phase 3): sweep loop extracted from
    ``broad_mapping_sweep.main``.

    Budget checks happen at proposal boundaries only — ``run_iteration`` is
    never interrupted mid-``train_step``. Each cell is KB-flushed on
    completion, so a stop degrades by the granularity of the in-flight
    batch and never by corruption. On stop the campaign is checkpointed;
    the KB coverage seed makes the next burst resume-safe by construction.

    Returns:
        Summary dict: ``completed``, ``failed``, ``done``, ``stop_reason``
        and per-family mean ``walltime_s`` (the Phase 1 instrument).
    """
    completed = 0
    failed = 0
    empty_streak = 0
    walltime_by_family: dict[str, list[float]] = {}
    stop_reason = "max_iterations"
    for iteration in range(1, max_iterations + 1):
        if (reason := _burst_stop(budget, gate, time.monotonic())) is not None:
            stop_reason = reason
            break
        started = time.time()
        # Trim the batch at the target boundary: --target-cells is a hard
        # cap, so the last iteration never overshoots by a partial batch.
        n_proposals = driver.cells
        if budget.target_cells is not None:
            n_proposals = min(n_proposals, budget.target_cells - budget.done)
        results = campaign.run_iteration(n_experiments=n_proposals)
        if not results:
            # An empty iteration means either a fully gate-rejected batch
            # (transient: rejected cells are KB-covered, so the next batch
            # proposes elsewhere) or a truly exhausted/quarantined grid.
            empty_streak += 1
            if empty_streak >= 3:
                stop_reason = "exhausted"
                break
            continue
        empty_streak = 0
        done, batch_failed = _absorb_results(results, walltime_by_family)
        completed += done
        failed += batch_failed
        if on_cell_complete is not None:
            for _ in range(done):
                on_cell_complete(budget.done + _ + 1)
        budget = budget.advance_by(done)
        logger.info(
            "Burst iteration %d: %d completed / %d proposed (%.0fs); total %d%s",
            iteration,
            done,
            len(results),
            time.time() - started,
            budget.done,
            f"/{budget.target_cells}" if budget.target_cells is not None else "",
        )
    campaign.save_checkpoint()
    means = {
        family: round(sum(times) / len(times), 3)
        for family, times in walltime_by_family.items()
    }
    if means:
        logger.info("Mean walltime by dynamics family: %s", means)
    logger.info(
        "Burst stop (%s): %d measured cells, %d failed runs, %d structural voids, %d defects",
        _BURST_STOP_REASONS[stop_reason],
        completed,
        failed,
        _count_lines(campaign.voids_path),
        len(
            read_defects(campaign.defects_path)
            if campaign.defects_path is not None
            else []
        ),
    )
    return {
        "completed": completed,
        "failed": failed,
        "done": budget.done,
        "stop_reason": stop_reason,
        "walltime_mean_by_family": means,
    }
    if means:
        logger.info("Mean walltime by dynamics family: %s", means)
    logger.info(
        "Burst stop (%s): %d measured cells, %d failed runs, %d structural voids, %d defects",
        _BURST_STOP_REASONS[stop_reason],
        completed,
        failed,
        _count_lines(campaign.voids_path),
        len(
            read_defects(campaign.defects_path)
            if campaign.defects_path is not None
            else []
        ),
    )
    return {
        "completed": completed,
        "failed": failed,
        "done": budget.done,
        "stop_reason": stop_reason,
        "walltime_mean_by_family": means,
    }


def _count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as fh:
        return sum(1 for _ in fh)


# --- Epistemic maturation (TODO29 Phase 4): Spark → Survivor → Claim ------


@dataclass(frozen=True, slots=True)
class _CellRow:
    """One measured KB entry with its maturity/burst provenance."""

    key: str
    task: str
    dynamics: str
    credit: str
    update: str
    topology: str
    geometry: dict[str, object]
    accuracy: float
    walltime: float
    param_budget: int
    nan_loss: bool
    bursts: tuple[str, ...]
    levels: tuple[str, ...]
    # NEW — multi-objective fields (TODO31 Phase 1)
    flops: float = 0.0
    memory_mb: float = 0.0
    energy_per_step: float = 0.0
    latency_ms: float = 0.0
    # Ruler-relative
    bp_deficit: float = 0.0
    ruler_walltime_ratio: float = 0.0
    ruler_energy_ratio: float = 0.0
    # Stability instruments
    spectral_radius: float = 0.0
    lyapunov_exponent: float = 0.0
    max_singular_value: float = 0.0
    # Credit instruments
    credit_alignment: float = 0.0
    feedback_path_length: float = 0.0
    trace_variance: float = 0.0
    # Plasticity
    psi_capacity: float = 0.0
    consolidation_cost: float = 0.0
    rewrite_rate: float = 0.0
    # Settle
    settle_steps_used: int = 0
    free_energy_final: float = 0.0
    settle_horizon: float = 0.0
    stability_plasticity_ratio: float = 0.0
    credit_efficiency: float = 0.0


@dataclass(frozen=True, slots=True)
class _Candidate:
    """A promotion candidate shared by the L1 and L2 tiers."""

    key: str
    task: str
    dynamics: str
    credit: str
    update: str
    topology: str
    geometry: dict[str, object]
    param_budget: int
    accuracy: float
    bursts_seen: int = 0
    front_bursts: int = 0


def next_burst_tag(kb_path: Path) -> str:
    """``burst:<utc-date>-<seq>`` for the next burst, derived from the tags
    already recorded in the KB (append-safe across resumes)."""
    from datetime import UTC, datetime

    from computronium.knowledge import KnowledgeBase

    date = datetime.now(UTC).strftime("%Y-%m-%d")
    seq = 0
    if kb_path.exists():
        for entry in KnowledgeBase(kb_path).query():
            for tag in entry.tags:
                if not tag.startswith("burst:"):
                    continue
                day, _, s = tag.split(":", 1)[1].rpartition("-")
                if day == date and s.isdigit():
                    seq = max(seq, int(s))
    return f"burst:{date}-{seq + 1}"


def _load_measured_cells(kb_path: Path, task: str | None = None) -> list[_CellRow]:
    """Measured cells with their maturity/burst provenance (mtime-cached)."""
    from computronium.visualization.atlas import kb_load_cached

    return kb_load_cached(
        kb_path,
        lambda: _load_measured_cells_uncached(kb_path, task),
        list,
        key_extra=("measured", task),
    )


def _load_measured_cells_uncached(kb_path: Path, task: str | None) -> list[_CellRow]:
    from computronium.knowledge import KnowledgeBase
    from computronium.visualization.atlas import UNBOUNDED_ROWS

    rows: list[_CellRow] = []
    if not kb_path.exists():
        return rows
    # auto_embed=False + unbounded limit: full-campaign read without vector init;
    # query() defaults to the newest 100 rows, which truncated dashboard stats.
    for entry in KnowledgeBase(kb_path, auto_embed=False).query(limit=UNBOUNDED_ROWS):
        topic = str(entry.topic)
        if not topic.startswith("experiment:"):
            continue
        entry_task = topic.split(":", 1)[1]
        if task is not None and entry_task != task:
            continue
        hp = entry.hyperparameters
        if not (hp.get("dynamics") and hp.get("credit") and hp.get("update")):
            continue
        geometry = hp.get("geometry") or {}
        if not isinstance(geometry, dict):
            continue
        tags = [str(t) for t in entry.tags]
        budget_raw = hp.get("param_budget", 0)
        metrics = entry.metrics
        rows.append(
            _CellRow(
                key=cell_key(
                    str(hp["dynamics"]),
                    str(hp["credit"]),
                    str(hp["update"]),
                    str(geometry.get("topology_type", "feedforward")),
                ),
                task=entry_task,
                dynamics=str(hp["dynamics"]),
                credit=str(hp["credit"]),
                update=str(hp["update"]),
                topology=str(geometry.get("topology_type", "feedforward")),
                geometry=dict(geometry),
                accuracy=float(metrics.get("final_accuracy", 0.0)),
                walltime=float(metrics.get("walltime_s", 0.0)),
                param_budget=int(budget_raw)
                if isinstance(budget_raw, int | float)
                else 0,
                nan_loss=bool(metrics.get("nan_loss")),
                bursts=tuple(
                    t.split(":", 1)[1] for t in tags if t.startswith("burst:")
                ),
                levels=tuple(
                    t.split(":", 1)[1] for t in tags if t.startswith("maturity:")
                ),
                # NEW — multi-objective fields from KB metrics (TODO31)
                flops=float(metrics.get("flops", 0.0)),
                memory_mb=float(metrics.get("memory_mb", 0.0)),
                energy_per_step=float(metrics.get("energy_per_step", 0.0)),
                latency_ms=float(metrics.get("latency_ms", 0.0)),
                bp_deficit=float(metrics.get("bp_deficit", 0.0)),
                ruler_walltime_ratio=float(metrics.get("ruler_walltime_ratio", 0.0)),
                ruler_energy_ratio=float(metrics.get("ruler_energy_ratio", 0.0)),
                spectral_radius=float(metrics.get("spectral_radius", 0.0)),
                lyapunov_exponent=float(metrics.get("lyapunov_exponent", 0.0)),
                max_singular_value=float(metrics.get("max_singular_value", 0.0)),
                credit_alignment=float(metrics.get("credit_alignment", 0.0)),
                feedback_path_length=float(metrics.get("feedback_path_length", 0.0)),
                trace_variance=float(metrics.get("trace_variance", 0.0)),
                psi_capacity=float(metrics.get("psi_capacity", 0.0)),
                consolidation_cost=float(metrics.get("consolidation_cost", 0.0)),
                rewrite_rate=float(metrics.get("rewrite_rate", 0.0)),
                settle_steps_used=int(metrics.get("settle_steps_used", 0)),
                free_energy_final=float(metrics.get("free_energy_final", 0.0)),
                settle_horizon=float(
                    metrics.get("settle_horizon", metrics.get("settle_steps_used", 0))
                ),
                stability_plasticity_ratio=float(
                    metrics.get("stability_plasticity_ratio", 0.0)
                ),
                credit_efficiency=float(metrics.get("credit_efficiency", 0.0)),
            )
        )
    return rows


def _void_keys(voids_path: Path) -> frozenset[str]:
    if not voids_path.exists():
        return frozenset()
    keys = set()
    for line in voids_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("dynamics") and r.get("credit") and r.get("update"):
            keys.add(
                cell_key(
                    str(r["dynamics"]),
                    str(r["credit"]),
                    str(r["update"]),
                    str(r["topology"]),
                )
            )
    return frozenset(keys)


def promote_candidates(
    kb_path: Path,
    voids_path: Path,
    k: int,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
) -> list[_Candidate]:
    """Promotion query (TODO29 Phase 4 / TODO31 Phase 1): cells on the burst
    Pareto front (``atlas.pareto_top`` over configurable objectives) that have
    no ``maturity:l1`` row yet. Void-covered keys are excluded. Up to ``k``
    candidates, best on primary objective first."""
    import pandas as pd

    from computronium.visualization.atlas import pareto_top

    rows = _load_measured_cells(kb_path)
    by_key: dict[str, list[_CellRow]] = {}
    for row in rows:
        by_key.setdefault(row.key, []).append(row)
    if not by_key or k <= 0:
        return []

    # Build per-cell best metrics for all configured objectives
    obj_names = [o.name.value for o in objectives]

    per_cell: list[dict[str, float]] = []
    for key, group in by_key.items():
        if any(r.nan_loss for r in group):
            continue
        cell_data = {"key": key}
        for obj_name in obj_names:
            vals = [getattr(r, obj_name, 0.0) for r in group]
            if vals:
                obj_spec = next(o for o in objectives if o.name.value == obj_name)
                cell_data[obj_name] = (
                    max(vals) if obj_spec.direction == "maximize" else min(vals)
                )
            else:
                cell_data[obj_name] = 0.0
        per_cell.append(cell_data)

    if not per_cell:
        return []
    front = pareto_top(pd.DataFrame(per_cell), k=len(per_cell), objectives=objectives)
    void_keys = _void_keys(voids_path)
    candidates: list[_Candidate] = []
    for key in (str(v) for v in front["key"]):
        group = by_key[key]
        if any(lvl in {"l1", "l2"} for r in group for lvl in r.levels):
            continue
        if key in void_keys:
            continue
        first = group[0]
        candidates.append(
            _Candidate(
                key=key,
                task=first.task,
                dynamics=first.dynamics,
                credit=first.credit,
                update=first.update,
                topology=first.topology,
                geometry=first.geometry,
                param_budget=first.param_budget,
                accuracy=max(r.accuracy for r in group),
                bursts_seen=len({b for r in group for b in r.bursts}),
            )
        )
        if len(candidates) >= k:
            break
    return candidates


def _deep_tier_candidates(
    kb_path: Path,
    top: int,
    task: str | None = None,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
) -> list[_Candidate]:
    """Cells on a per-burst Pareto front in ≥ 2 distinct bursts (L2 gate).
    Uses configurable objectives for multi-objective Pareto front."""
    import pandas as pd

    from computronium.visualization.atlas import pareto_top

    rows = [r for r in _load_measured_cells(kb_path, task) if "l2" not in r.levels]
    by_key: dict[str, list[_CellRow]] = {}
    burst_rows: dict[str, list[_CellRow]] = {}
    for row in rows:
        by_key.setdefault(row.key, []).append(row)
        for burst in row.bursts:
            burst_rows.setdefault(burst, []).append(row)

    obj_names = [o.name.value for o in objectives]

    front_bursts: dict[str, set[str]] = {}
    for burst, group in burst_rows.items():
        per_cell: list[dict[str, float]] = []
        for r in group:
            if r.nan_loss:
                continue
            cell_data = {"key": r.key}
            for obj_name in obj_names:
                val = getattr(r, obj_name, 0.0)
                cell_data[obj_name] = val
            per_cell.append(cell_data)
        if not per_cell:
            continue
        df = pd.DataFrame(per_cell)
        front = pareto_top(df, k=len(group), objectives=objectives)
        for key in (str(v) for v in front["key"]):
            front_bursts.setdefault(key, set()).add(burst)

    candidates = [
        _Candidate(
            key=key,
            task=group[0].task,
            dynamics=group[0].dynamics,
            credit=group[0].credit,
            update=group[0].update,
            topology=group[0].topology,
            geometry=group[0].geometry,
            param_budget=group[0].param_budget,
            accuracy=max(r.accuracy for r in group),
            front_bursts=len(front_bursts[key]),
        )
        for key, group in by_key.items()
        if len(front_bursts.get(key, ())) >= 2
    ]
    # Sort by primary objective
    primary_obj = obj_names[0] if obj_names else "accuracy"
    candidates.sort(key=lambda c: getattr(c, primary_obj, 0.0), reverse=True)
    return candidates[:top]


def _seed_sensitivity_flags(
    rows: list[_CellRow], *, threshold: float = 0.2
) -> list[dict[str, object]]:
    """Cells measured in ≥ 2 bursts whose accuracy spread exceeds the
    threshold: contradictions become findings (seed_sensitivity)."""
    by_key: dict[str, list[_CellRow]] = {}
    for row in rows:
        by_key.setdefault(row.key, []).append(row)
    flags: list[dict[str, object]] = []
    for key, group in by_key.items():
        bursts = {b for r in group for b in r.bursts}
        if len(bursts) < 2:
            continue
        accs = [r.accuracy for r in group]
        spread = max(accs) - min(accs)
        if spread > threshold:
            flags.append({
                "cell": key,
                "bursts": sorted(bursts),
                "spread": round(spread, 4),
                "accuracies": accs,
            })
    return flags


def _append_maturation(path: Path, row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


class _FixedProposer:
    """Replays explicit maturation proposals through the governed pipeline."""

    def __init__(self, proposals: list[ExperimentProposal]) -> None:
        self._proposals = proposals

    def propose_batch(
        self, n_proposals: int, recent_results: list[dict[str, object]] | None = None
    ) -> list[ExperimentProposal]:
        return self._proposals[:n_proposals]

    def has_novel(self) -> bool:
        return bool(self._proposals)


def _maturation_proposal(
    candidate: _Candidate,
    *,
    level: str,
    epochs: int,
    burst_tag: str | None = None,
) -> ExperimentProposal:
    """Same cell key, fresh execution at the promotion tier's epochs."""
    tags = ["autoscientist", "broad_map", f"maturity:{level}"]
    if burst_tag is not None:
        tags.append(burst_tag)
    tags.append(candidate.key)
    geometry = dict(candidate.geometry)
    geometry.setdefault("init_scheme", "default")
    return ExperimentProposal(
        hypothesis=f"Maturation {level} re-run of {candidate.key} at epochs={epochs}",
        model="eqprop",
        task=candidate.task,
        geometry=geometry,
        dynamics=candidate.dynamics,
        credit=candidate.credit,
        update=candidate.update,
        hyperparams={"epochs": epochs, "param_budget": candidate.param_budget},
        justification=f"maturation promotion to {level} (TODO29 Phase 4)",
        expected_outcome="claim-grade evidence at the promoted tier",
        priority=0.6,
        tags=tags,
    )


def run_l1_maturation(
    args: argparse.Namespace,
    campaign: BroadMappingCampaign,
    burst_tag: str | None = None,
) -> list[dict[str, object]]:
    """``--maturation N``: after a burst, promote up to N front cells to an
    epochs=3 re-run (``maturity:l1``) through the governed pipeline."""
    from computronium.autoscientist.benchmark import (
        benchmark_inference_from_campaign_result,
    )
    from computronium.autoscientist.objectives import parse_objectives

    obj_spec = getattr(args, "objectives", "accuracy,walltime_s")
    objectives = parse_objectives(obj_spec)
    candidates = promote_candidates(
        args.root / "kb.sqlite",
        args.root / "structural_voids.jsonl",
        args.maturation,
        objectives=objectives,
    )
    if not candidates:
        logger.info("Maturation: no promotion candidates on the burst front.")
        return []
    proposals = [
        _maturation_proposal(c, level="l1", epochs=3, burst_tag=burst_tag)
        for c in candidates
    ]
    campaign.proposer = _FixedProposer(proposals)  # type: ignore[assignment]
    results = campaign.run_iteration(n_experiments=len(proposals))
    written: list[dict[str, object]] = []
    for proposal, result in zip(proposals, results, strict=False):
        if result.get("status") != "completed":
            continue
        # Inference benchmark for L1+ promotion (TODO31 Phase 3.3)
        inf_metrics = benchmark_inference_from_campaign_result(result)
        latency_ms = inf_metrics.latency_ms if inf_metrics else 0.0
        row: dict[str, object] = {
            "maturity": "l1",
            "cell": proposal.tags[-1],
            "task": proposal.task,
            "epochs": 3,
            "burst": burst_tag,
            "accuracy": result.get("final_accuracy"),
            "walltime_s": result.get("walltime_s"),
            "latency_ms": latency_ms,
            "timestamp": time.time(),
        }
        _append_maturation(args.root / "maturation.jsonl", row)
        written.append(row)
    logger.info("Maturation L1: %d re-runs recorded", len(written))
    return written


def run_deep_tier(
    root: Path,
    campaign: BroadMappingCampaign,
    *,
    task: str | None,
    top: int,
    epochs: int,
    seeds: int,
    seed: int,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
) -> list[dict[str, object]]:
    """L2 deep tier: cells front-stable across ≥ 2 bursts, re-executed at
    ``--epochs`` for ``--seeds`` fresh seeds — each seed a separately
    pre-registered CEEC experiment. Rows land in ``maturation.jsonl``."""
    from computronium.autoscientist.benchmark import (
        benchmark_inference_from_campaign_result,
    )

    candidates = _deep_tier_candidates(
        root / "kb.sqlite", top, task, objectives=objectives
    )
    for flag in _seed_sensitivity_flags(_load_measured_cells(root / "kb.sqlite", task)):
        _append_maturation(
            root / "maturation.jsonl",
            {"kind": "seed_sensitivity", **flag, "timestamp": time.time()},
        )
    if not candidates:
        logger.info("Deep tier: no cells are front-stable across ≥ 2 bursts yet.")
        return []
    written: list[dict[str, object]] = []
    for candidate in candidates:
        accuracies: list[float] = []
        latencies: list[float] = []
        for i in range(seeds):
            seed_everything(seed + i, deterministic=False)
            proposal = _maturation_proposal(candidate, level="l2", epochs=epochs)
            campaign.proposer = _FixedProposer([proposal])  # type: ignore[assignment]
            for r in campaign.run_iteration(n_experiments=1):
                if r.get("status") == "completed":
                    acc = r.get("final_accuracy")
                    if isinstance(acc, int | float):
                        accuracies.append(float(acc))
                    # Inference benchmark for L2 promotion (TODO31 Phase 3.3)
                    inf_metrics = benchmark_inference_from_campaign_result(r)
                    if inf_metrics:
                        latencies.append(inf_metrics.latency_ms)
        if not accuracies:
            continue
        mean_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
        row: dict[str, object] = {
            "maturity": "l2",
            "cell": candidate.key,
            "task": candidate.task,
            "epochs": epochs,
            "seeds": len(accuracies),
            "accuracies": accuracies,
            "mean": round(sum(accuracies) / len(accuracies), 4),
            "spread": round(max(accuracies) - min(accuracies), 4),
            "front_bursts": candidate.front_bursts,
            "latency_ms": mean_latency,
            # Verification-level aspiration: Level 4 quality (seeds, matched
            # controls pending) — claims still require human review per CEEC.
            "quality": {"seeds": len(accuracies), "matched_control": False},
            "timestamp": time.time(),
        }
        _append_maturation(root / "maturation.jsonl", row)
        written.append(row)
    logger.info("Deep tier: %d claim-grade cells recorded", len(written))
    return written


def main(args: argparse.Namespace) -> None:
    """Run the sweep loop with the parsed CLI arguments."""
    logging.basicConfig(level=logging.INFO)
    (args.root / "campaign").mkdir(parents=True, exist_ok=True)

    seed_everything(args.seed, deterministic=False)
    campaign, driver = build_sweep(args)
    budget = ContinuousBudget(
        started_at=time.monotonic(),
        target_cells=args.sample_size,
    )
    summary = run_burst(campaign, driver, budget, max_iterations=args.max_iterations)
    logger.info(
        "Broad map finished: %d measured cells this run",
        int(summary["completed"]),  # type: ignore[arg-type]
    )
