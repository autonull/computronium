"""CEEC link: proposals are pre-registrations (TODO27 Phase 2.1/2.4).

One trace per governed proposal: pre-register (prediction + threshold +
scope) → execute → ``ProbeResult`` → ``Session.record_result`` (decision,
artifact, evidence, calibration, gate evaluation in one ledger row).
Failures are recorded too — never limbo.
"""

import contextlib
from typing import TYPE_CHECKING

from ceec.probe_adapter import record_probe_result

from computronium.autoscientist.bridge import ExperimentProposal
from computronium.autoscientist.proposer import cell_key
from computronium.core.logging import get_logger

if TYPE_CHECKING:
    from ceec.models import Experiment
    from ceec.run import ExperimentRun
    from ceec.session import Session

__all__ = ["CEECLink", "logger"]

logger = get_logger(__name__)


class CEECLink:
    """Governed execution channel between the campaign and a CEEC ledger."""

    def __init__(self, ledger_path: str, profile: object | None = None):
        from ceec.profile import DEFAULT_PROFILE
        from ceec.session import ledger

        self.ledger_path = ledger_path
        self.session: Session = ledger(
            ledger_path,
            profile or DEFAULT_PROFILE,  # type: ignore[arg-type]
        )

    @staticmethod
    def _cell(proposal: ExperimentProposal) -> str:
        if proposal.dynamics and proposal.credit and proposal.update:
            topology = "feedforward"
            if proposal.geometry:
                topology = str(proposal.geometry.get("topology_type", topology))
            return cell_key(
                proposal.dynamics, proposal.credit, proposal.update, topology
            )
        return f"{proposal.model}|{proposal.propagator or 'native'}"

    def pre_register(self, proposal: ExperimentProposal) -> Experiment:
        """Write the proposal's prediction + threshold + scope before execution."""
        threshold = proposal.hyperparams.get("threshold")
        falsifier = f"final_accuracy < {threshold}" if threshold is not None else None
        from ceec.models import Scope

        return self.session.experiment(
            question=proposal.hypothesis,
            prediction=proposal.expected_outcome or "measured cell in the atlas",
            scope=Scope.of(
                domain="probe",
                task=proposal.task,
                model=proposal.model,
                cell=self._cell(proposal),
                branch=self._branch(proposal),
            ),
            rationale=proposal.justification or "autoscientist proposal",
            design={
                "cell": self._cell(proposal),
                "geometry": proposal.geometry or {},
                "dynamics": proposal.dynamics,
                "credit": proposal.credit,
                "update": proposal.update,
                "optimizer": proposal.optimizer,
                "priority": proposal.priority,
                "tags": list(proposal.tags),
            },
            falsification_criterion=falsifier,
        )

    @staticmethod
    def _branch(proposal: ExperimentProposal) -> str:
        for tag in proposal.tags:
            if tag.startswith("campaign:"):
                return tag.split(":", 1)[1]
        return "main"

    def record(
        self,
        experiment: Experiment,
        proposal: ExperimentProposal,
        result: dict[str, object],
    ) -> ExperimentRun:
        """Ingest a completed execution through the shared governance loop."""
        from ceec.run import ProbeResult

        accuracy_raw = result.get("final_accuracy")
        accuracy = float(accuracy_raw) if isinstance(accuracy_raw, int | float) else 0.0
        threshold = proposal.hyperparams.get("threshold")
        outcome_boolean = (
            accuracy >= float(threshold)
            if isinstance(threshold, int | float)
            else accuracy > 0.0
        )
        run = self.session.record_result(
            experiment,
            ProbeResult(
                label="completed",
                outcome_boolean=bool(outcome_boolean),
                payload={
                    "final_accuracy": accuracy,
                    "final_loss": result.get("final_loss"),
                    "train_accuracy": result.get("train_accuracy"),
                    "epochs_completed": result.get("epochs_completed"),
                    "cell": self._cell(proposal),
                },
                axes=("final_accuracy",),
                values=(accuracy,),
                quality={"seeds": 1, "matched_control": False},
                notes=proposal.hypothesis[:120],
            ),
        )
        logger.info(
            "CEEC ledger: %s %s (gate=%s)", run.experiment_id, run.status, run.outcome
        )
        return run

    def record_failure(
        self, experiment: Experiment, proposal: ExperimentProposal, error: str
    ) -> None:
        """Close the trace on a failed execution — the proposal never limbo."""
        from ceec.store import StoreError

        try:
            store = self.session.store
            with contextlib.suppress(StoreError):
                store.pre_register_experiment(experiment)
            store.set_experiment_status(experiment.id, "failed")
            # Failure evidence enters the ledger as a "missing" probe output
            # (infrastructure/execution failure per the E.1 contract).
            record_probe_result(
                store,
                {
                    "status": "missing",
                    "scope": {"domain": "probe", "task": proposal.task},
                    "values": {"error": error, "cell": self._cell(proposal)},
                    "quality": {"seeds": 0, "matched_control": False},
                    "notes": f"execution failed: {error[:160]}",
                },
                f"campaign_failure:{self._cell(proposal)}",
            )
        except StoreError as exc:
            logger.error("CEEC ledger: failure ingest rejected: %s", exc)
