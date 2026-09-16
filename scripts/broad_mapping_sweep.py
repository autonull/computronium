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

    nohup uv run python scripts/broad_mapping_sweep.py \
        --sample-size 500 --epochs 1 \
        --root artifacts/broad_map > logs/broad_map.log 2>&1 &
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import time
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.autoscientist.bridge import ExperimentProposal
from computronium.autoscientist.campaign import AutoScientistCampaign
from computronium.autoscientist.proposer import (
    GRID_CREDITS,
    GRID_DYNAMICS,
    GRID_TOPOLOGIES,
    GRID_UPDATES,
    cell_key,
)
from computronium.utils import seed_everything

if TYPE_CHECKING:
    from computronium.knowledge import KnowledgeBase
    from computronium.ontology import GeometryConfig

logger = logging.getLogger("broad_map")


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
        viable: frozenset[str] | None = None,
    ) -> None:
        # Sampling RNG, not security-sensitive (S311).
        self.rng = random.Random(seed)  # ruff: ignore[suspicious-non-cryptographic-random-usage] (sampling RNG, not security)
        self.task = task
        self.cells = cells
        self.epochs = epochs
        self.depth = depth
        self.hidden_dim = hidden_dim
        self.param_budget = param_budget
        self.credit_trace = credit_trace
        self.viable = viable
        self.seen: set[str] = set()
        self._reload_covered(kb_path)
        # Balance tracked per (dynamics, credit, update) triple
        self.balance: dict[tuple[str, str, str], int] = {}
        for d in GRID_DYNAMICS:
            for c in GRID_CREDITS:
                for u in GRID_UPDATES:
                    self.balance[d, c, u] = 0

    def _reload_covered(self, kb_path: Path) -> None:
        """Seed the seen-set from the KB coverage matrix (structural voids
        included: a void is covered — it can never execute)."""
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
            topology = self.rng.choice(GRID_TOPOLOGIES)
            key = cell_key(dynamics, credit, update, topology)
            if key in self.seen or (self.viable is not None and key not in self.viable):
                continue
            self.seen.add(key)
            self.balance[dynamics, credit, update] += 1
            proposals.append(
                ExperimentProposal(
                    hypothesis=(
                        f"Broad-map cell {key}: uniform random draw, "
                        "stratified by dynamics×credit×update"
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
                    },
                    justification="broad-map stratified random cell (TODO28)",
                    expected_outcome="measured cell in the atlas",
                    priority=0.5,
                    tags=["autoscientist", "broad_map", key],
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
    """Campaign that appends dry-run-rejected cells to ``structural_voids.jsonl``.

    Void logging stays outside the CEEC ledger: a void is a boundary finding
    about the ontology's compatible region, not a measured experiment.
    """

    def __init__(self, *args: object, voids_path: Path, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.voids_path = voids_path

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-size", type=int, default=500)
    parser.add_argument("--cells-per-iter", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--task", default="mnist")
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--root", type=Path, default=Path("artifacts/broad_map"))
    parser.add_argument(
        "--hidden-dim", type=int, default=64, help="Geometry width for all cells"
    )
    parser.add_argument(
        "--depth", type=int, default=2, help="Geometry depth for all cells"
    )
    parser.add_argument(
        "--param-budget",
        type=int,
        default=25000,
        help="Geometry parameter budget per cell (0 = no rematch). One "
        "hidden_dim rescale per cell brings topologies within ~25%% of the "
        "budget — fixed depth/hidden spans a ~400x param spread.",
    )
    parser.add_argument(
        "--credit-trace",
        action="store_true",
        help="Capture per-cell BP-gradient alignment (credit_trace "
        "instrument: settle phases + split-half + BP reference on one "
        "batch). Adds settle overhead per cell.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    (args.root / "campaign").mkdir(parents=True, exist_ok=True)

    seed_everything(args.seed, deterministic=False)
    viable = enumerate_constraint_voids(
        args.root / "kb.sqlite",
        args.root / "structural_voids.jsonl",
        task=args.task,
    )
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
        viable=frozenset(viable),
    )
    campaign = BroadMappingCampaign(
        knowledge_base=None,
        output_dir=str(args.root / "campaign"),
        db_path=args.root / "campaign" / "campaign.db",
        branch_name="broad_mapping_sweep",
        ceec_ledger_path=args.root / "ledger.sqlite",
        voids_path=args.root / "structural_voids.jsonl",
    )
    campaign.knowledge_base = driver_seeded_kb(args.root / "kb.sqlite")
    campaign.proposer = driver  # type: ignore[assignment]

    completed = 0
    for iteration in range(1, args.max_iterations + 1):
        started = time.time()
        results = campaign.run_iteration(n_experiments=args.cells_per_iter)
        done = sum(1 for r in results if r.get("status") == "completed")
        completed += done
        logger.info(
            "Iteration %d: %d completed / %d proposed (%.0fs); total %d/%d",
            iteration,
            done,
            len(results),
            time.time() - started,
            completed,
            args.sample_size,
        )
        if completed >= args.sample_size:
            logger.info("Sample size reached. Campaign ends.")
            break

    voids = args.root / "structural_voids.jsonl"
    n_voids = sum(1 for _ in voids.open(encoding="utf-8")) if voids.exists() else 0
    logger.info(
        "Broad map finished: %d measured cells, %d structural voids",
        completed,
        n_voids,
    )


def driver_seeded_kb(kb_path: Path) -> KnowledgeBase:
    """Shared KB so gate rejections mark coordinates covered across resumes."""
    from computronium.knowledge import KnowledgeBase

    return KnowledgeBase(kb_path)


if __name__ == "__main__":
    main()
