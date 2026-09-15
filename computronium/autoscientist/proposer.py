"""
ExperimentProposer: Generates intelligent experiment batches.

Takes hypotheses from HypothesisReasoner and converts them into
concrete experiment proposals with configurations.
"""

from collections.abc import Callable
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

from computronium.autoscientist.bridge import AutoScientistBridge, ExperimentProposal
from computronium.autoscientist.reasoner import Hypothesis, HypothesisReasoner
from computronium.core.exceptions import KnowledgeBaseError
from computronium.core.logging import get_logger
from computronium.knowledge import KnowledgeBase
from computronium.ontology import ParameterUpdateConfig
from computronium.ontology.dynamics import DYNAMICS_REGISTRY

if TYPE_CHECKING:
    from computronium.knowledge.entries import ConditionalQuery

__all__ = [
    "ExperimentProposer",
    "ProposalObjective",
    "cell_key",
    "logger",
]
logger = get_logger()

#: Grid axes for coverage-driven proposals (P1.2a). Update names mirror the
#: ``ParameterUpdateConfig`` classmethods; credit names the
#: ``CreditAssignmentConfig`` classmethods; dynamics the ``DYNAMICS_REGISTRY``
#: keys. No preset ranking — the coverage matrix and the KB decide.
GRID_DYNAMICS: tuple[str, ...] = tuple(DYNAMICS_REGISTRY)
GRID_CREDITS: tuple[str, ...] = (
    "thermodynamic_contrast",
    "local_contrastive",
    "random_projections",
    "local_goodness",
    "temporal_trace",
    "target_inversion",
    "homeostatic",
    "pepita",
    "gradient",
)
GRID_UPDATES: tuple[str, ...] = (
    "euclidean",
    "adam",
    "local_adam",
    "muon" if hasattr(ParameterUpdateConfig, "muon") else "unit_rms",
    "mean_norm",
    "spectral_constrained",
    "ortho_adam",
    "lion",
    "role_split",
    "elastic_consolidation",
)
GRID_TOPOLOGIES: tuple[str, ...] = (
    "feedforward",
    "recurrent",
    "tile_mesh",
    "attention",
    "spatial_lattice",
)


def cell_key(dynamics: str, credit: str, update: str, topology: str) -> str:
    """Canonical coverage-matrix key for a grid cell."""
    return f"{dynamics}|{credit}|{update}|{topology}"


class ProposalObjective(StrEnum):
    """What a proposal cycle is explicitly optimizing (bias audit, plan §5 cycle 2).

    Defaulting to ``ACCURACY`` reproduces the historical behavior; choosing a
    non-accuracy objective forces the proposer to rank candidates by a resource
    or robustness axis instead — surfacing whether the engine is biased toward
    accuracy alone.
    """

    ACCURACY = "accuracy"
    MEMORY = "memory"
    SETTLING_SPEED = "settling_speed"
    NOISE_ROBUSTNESS = "noise_robustness"
    STABILITY = "stability"
    ENERGY = "energy"
    LATENCY = "latency"
    PLASTICITY_CAPACITY = "plasticity_capacity"


# Query service shape the proposer depends on (P2 read-half). Injected so the
# flywheel's read path can be unit-tested against a stub, not a live DB.
ConditionalQuerier = Callable[["ConditionalQuery"], list[object]]


class ExperimentProposer:
    """
    Generates experiment batches from hypotheses.

    Supports:
    - Systematic search across model+propagator combinations
    - Targeted experiments based on specific hypotheses
    - Ablation studies (vary one parameter at a time)
    - Curriculum-based progression (easy tasks first)

    P2 (read-half): the proposer can consult prior verified conditionals via an
    injected query service and prune probes the KB has already characterized —
    turning the "knowledge layer is read" claim into a measurable skip.
    """

    def __init__(
        self,
        knowledge_base: KnowledgeBase | None = None,
        reasoner: HypothesisReasoner | None = None,
        conditional_query: ConditionalQuerier | None = None,
    ):
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.reasoner = reasoner or HypothesisReasoner(self.knowledge_base)
        self.bridge = AutoScientistBridge()
        # Dependency injection: the query service defaults to the KB's conditional
        # read, but is swappable for a stub in tests / a remote service in prod.
        self._conditional_query = conditional_query or (
            self.knowledge_base.query_conditionals
        )

    def propose_batch(
        self,
        n_proposals: int = 10,
        objective: ProposalObjective | str = ProposalObjective.ACCURACY,
        recent_results: list[dict[str, object]] | None = None,
    ) -> list[ExperimentProposal]:
        """
        Propose a batch of hypothesis-driven experiments.

        Args:
            n_proposals: Number of proposals to generate.
            objective: The axis to optimize when ranking candidates. Defaults to
                ACCURACY (historical behavior); a non-accuracy objective forces
                the cycle to rank by memory/settling-speed/noise-robustness so
                the engine's bias is explicit and auditable (plan §5 cycle 2).
            recent_results: Recent experiment metrics for the rule-based
                hypothesis generators. Callers with a KnowledgeBase should
                pass their latest experiment records — the generators are
                inert without them.

        Returns:
            List of experiment proposals.
        """
        objective_enum = (
            objective
            if isinstance(objective, ProposalObjective)
            else ProposalObjective(objective)
        )
        proposals = []

        # 1. Generate hypotheses
        hypotheses = self.reasoner.generate_hypotheses(recent_results)

        # 2. Convert hypotheses to proposals
        for h in hypotheses[:n_proposals]:
            proposal = self._hypothesis_to_proposal(h, objective_enum)
            if proposal:
                proposals.append(proposal)

        logger.info(
            "Proposed %d experiments (%d hypothesis-driven) objective=%s",
            len(proposals),
            len(proposals),
            objective_enum.value,
        )
        return proposals

    def _covered_cells(self, limit: int = 2000) -> set[str]:
        """Read the coverage matrix out of the KB's own experiment records.

        A cell is covered iff a prior experiment entry ran its full
        (dynamics, credit, update, topology) key — novelty is measured,
        not assumed.
        """
        kb = self.knowledge_base
        if kb is None:
            return set()
        covered: set[str] = set()
        try:
            entries = kb.query(source="experiment")
        except KnowledgeBaseError, ValueError:  # pragma: no cover - defensive
            return set()
        for entry in entries[:limit]:
            hp = (
                entry.hyperparameters if isinstance(entry.hyperparameters, dict) else {}
            )
            geo = hp.get("geometry")
            topology = geo.get("topology_type") if isinstance(geo, dict) else None
            if hp.get("dynamics") and topology:
                covered.add(
                    cell_key(
                        str(hp["dynamics"]),
                        str(hp.get("credit", "")),
                        str(hp.get("update", "")),
                        str(topology),
                    )
                )
        return covered

    #: Instrument signature → discriminating follow-up (P1.2c). Each rule
    #: proposes the cell that separates hypotheses, not a blind neighbor.
    INSTRUMENT_RULES: ClassVar[tuple[tuple[str, str], ...]] = (
        ("zero_input_credit", "mupc_depth_rescue"),
        ("unreliable_credit", "reliability_recheck"),
    )

    def propose_instrument_triggered(
        self,
        reading: dict[str, object],
        base: ExperimentProposal,
    ) -> list[ExperimentProposal]:
        """Propose targeted follow-ups from an instrument reading (P1.2c).

        Args:
            reading: A ``credit_trace`` dict (``layer_norms``,
                ``split_half_cosine`` — see
                ``computronium.analysis.instruments``).
            base: The cell the reading came from.
        """
        norms = reading.get("layer_norms")
        cosines = reading.get("split_half_cosine")
        signatures: list[str] = []
        if isinstance(norms, dict) and norms:
            first = next(iter(norms.values()))
            if isinstance(first, int | float) and first < 1e-8:
                signatures.append("zero_input_credit")
        if isinstance(cosines, dict) and cosines:
            vals = [v for v in cosines.values() if isinstance(v, int | float)]
            if vals and sum(vals) / len(vals) < 0.2:
                signatures.append("unreliable_credit")

        follow_ups: list[ExperimentProposal] = []
        for signature in signatures:
            geometry = dict(base.geometry or {"topology_type": "feedforward"})
            hyperparams = dict(base.hyperparams)
            match signature:
                case "zero_input_credit":
                    raw_depth = geometry.get("depth", 2)
                    depth = int(raw_depth) if isinstance(raw_depth, int | float) else 2
                    geometry["depth"] = depth + 8
                    geometry["init_scheme"] = "mupc"
                    hypothesis = (
                        f"zero input-layer credit on {self._cell_of(base)}: "
                        "test the depth-scaled-init rescue (μPC)"
                    )
                case "unreliable_credit":
                    raw_batch = hyperparams.get("batch_size", 64)
                    batch = int(raw_batch) if isinstance(raw_batch, int | float) else 64
                    hyperparams["batch_size"] = batch * 2
                    hypothesis = (
                        f"unreliable credit split-half on {self._cell_of(base)}: "
                        "recheck at doubled batch before budget escalation"
                    )
                case _:
                    continue
            follow_ups.append(
                ExperimentProposal(
                    hypothesis=hypothesis,
                    model=base.model,
                    task=base.task,
                    geometry=geometry,
                    dynamics=base.dynamics,
                    credit=base.credit,
                    update=base.update,
                    hyperparams=hyperparams,
                    justification=f"instrument-triggered ({signature})",
                    expected_outcome="signature resolves or boundary records",
                    priority=0.7,
                    tags=["autoscientist", "instrument_triggered", signature],
                )
            )
        return follow_ups

    @staticmethod
    def _cell_of(p: ExperimentProposal) -> str:
        if p.dynamics and p.credit and p.update:
            topology = "feedforward"
            if p.geometry:
                topology = str(p.geometry.get("topology_type", topology))
            return cell_key(p.dynamics, p.credit, p.update, topology)
        return f"{p.model}|{p.task}"

    def propose_coverage_cells(
        self,
        n_proposals: int = 10,
        *,
        task: str = "mnist",
        model: str = "eqprop",
        depth: int = 2,
        hidden_dim: int = 64,
        init_scheme: str = "default",
    ) -> list[ExperimentProposal]:
        """Propose the first coverage-novel grid cells in registry order.

        P1.2(a): the coverage matrix (read from the KB) drives novelty;
        ``conditional_query`` prunes cells the KB has already characterized.
        Iteration order is the registry/product order — the grid re-measures
        structure rather than seeding from any operator's conclusions.
        """
        covered = self._covered_cells()
        proposals: list[ExperimentProposal] = []
        for dynamics in GRID_DYNAMICS:
            for credit in GRID_CREDITS:
                for update in GRID_UPDATES:
                    for topology in GRID_TOPOLOGIES:
                        if len(proposals) >= n_proposals:
                            return proposals
                        key = cell_key(dynamics, credit, update, topology)
                        if key in covered:
                            continue
                        covered.add(key)
                        proposal = ExperimentProposal(
                            hypothesis=(
                                f"Coverage cell {key}: measure the untested "
                                "dynamics x credit x update x topology coordinate"
                            ),
                            model=model,
                            task=task,
                            geometry={
                                "topology_type": topology,
                                "depth": depth,
                                "hidden_dim": hidden_dim,
                                "init_scheme": init_scheme,
                            },
                            dynamics=dynamics,
                            credit=credit,
                            update=update,
                            justification="coverage-novel cell (P1.2a)",
                            expected_outcome="measured cell in the atlas",
                            priority=0.5,
                            tags=["autoscientist", "coverage", key],
                        )
                        kept, _ = self.avoid_characterized([proposal])
                        proposals.extend(kept)
        return proposals

    def _hypothesis_to_proposal(
        self,
        hypothesis: Hypothesis,
        objective: ProposalObjective = ProposalObjective.ACCURACY,
    ) -> ExperimentProposal | None:
        """Convert a hypothesis to an experiment proposal."""
        if not hypothesis.proposed_model and not hypothesis.proposed_propagator:
            return None

        tags = ["autoscientist", hypothesis.source]
        if objective is not ProposalObjective.ACCURACY:
            tags.append(f"objective:{objective.value}")
        return ExperimentProposal(
            hypothesis=hypothesis.statement,
            model=hypothesis.proposed_model or "MLP",
            task=hypothesis.proposed_task or "mnist",
            propagator=hypothesis.proposed_propagator,
            justification=(
                hypothesis.reasoning_chain[0] if hypothesis.reasoning_chain else ""
            ),
            expected_outcome=hypothesis.statement,
            priority=hypothesis.confidence,
            tags=tags,
        )

    def propose_ablation(
        self,
        model: str,
        base_config: dict[str, object],
        parameters: list[str],
        values: list[list[object]],
    ) -> list[ExperimentProposal]:
        """
        Propose ablation studies varying specific parameters.

        Args:
            model: Model name to ablate.
            base_config: Base configuration.
            parameters: Parameter names to vary.
            values: Values to try for each parameter.

        Returns:
            List of ablation proposals.
        """
        proposals = []
        task_raw = base_config.get("task", "mnist")
        task = task_raw if isinstance(task_raw, str) else "mnist"
        for param, vals in zip(parameters, values):
            for v in vals:
                config = dict(base_config)
                config[param] = v
                proposals.append(
                    ExperimentProposal(
                        hypothesis=f"Ablation: effect of {param}={v} on {model}",
                        model=model,
                        task=task,
                        hyperparams={param: v},
                        priority=0.4,
                        tags=["ablation", param],
                    )
                )
        return proposals

    def avoid_characterized(
        self,
        proposals: list[ExperimentProposal],
        *,
        accuracy_target: float = 0.5,
    ) -> tuple[list[ExperimentProposal], list[ExperimentProposal]]:
        """
        Prune proposals whose (model, task) the KB has already characterized.

        P2-lite's turbine-turns signal: a probe is *redundant* if a prior
        verified conditional already answers ``(proposal.model, proposal.task)``
        at or above ``accuracy_target``. Skipping it is the compounding claim
        made measurable — the proposer read the KB and burned no budget on a
        probe it could not improve.

        Args:
            proposals: Candidate proposals.
            accuracy_target: Minimum stored accuracy for a previous conditional
                to count as "already characterized".

        Returns:
            ``(kept, skipped)`` — proposals that remain worth probing, and those
            dropped because a prior conditional already covered them. The paired
            counterfactual (with-KB vs without-KB) is the count of ``skipped``.
        """
        kept: list[ExperimentProposal] = []
        skipped: list[ExperimentProposal] = []
        for p in proposals:
            if not p.model:
                kept.append(p)
                continue
            query: ConditionalQuery = {
                "model": p.model,
                "task": (p.task or "mnist"),
                "accuracy_target": accuracy_target,
                "memory_cap": None,
                "flops_cap": None,
                "substrate": None,
            }
            covered = self._conditional_query(query)
            if covered:
                skipped.append(p)
            else:
                kept.append(p)
        if skipped:
            logger.info(
                "proposer skipped %d already-characterized probe(s)", len(skipped)
            )
        return kept, skipped
