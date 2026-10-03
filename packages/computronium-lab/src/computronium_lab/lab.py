"""Lab — compose, train, compare, and report ontology coordinates.

Survivors (R78): lab, training, synthesis, adaptation.
Retired: presets, recipes, campaign, deployment, ecosystem, sequential,
state_prediction, research/.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, TypedDict

import torch
from torch import Tensor
from torch.utils.data import DataLoader, TensorDataset

from computronium.benchmarks.joint.tasks import gaussian_blobs
from computronium_lab.synthesis.spec import Constraints, ProblemSpec
from computronium_lab.training import (
    TrainingResult,
    TrainOptions,
    train_with_certificates,
)

# Minimal CEEC profile for exploratory synthesis recording (T23.1.7)
try:
    from ceec.constraints import ConstraintResult
    from ceec.profile import CORE_CONSTRAINTS, CORE_QUALITY, Constraint, Profile
    from ceec.session import ledger
    from ceec.profile import LedgerRole

    def _frozen_theta_audit(
        store, experiment, _profile
    ) -> ConstraintResult:
        design = experiment.design
        ok = not design.get("psi_only") or "frozen_theta_audit" in experiment.hard_gates
        return ConstraintResult(
            "frozen_theta_audit_for_psi_only_claims",
            ok,
            f"psi_only={design.get('psi_only')}, "
            f"frozen_theta_audit gate={'frozen_theta_audit' in experiment.hard_gates}",
        )

    def _identity_card(
        store, experiment, _profile
    ) -> ConstraintResult:
        design = experiment.design
        ok = not design.get("new_primitive") or bool(design.get("identity_card_ref"))
        return ConstraintResult(
            "identity_card_for_new_primitive",
            ok,
            f"new_primitive={design.get('new_primitive')}, card="
            f"{design.get('identity_card_ref')!r}",
        )

    COMPUTRONIUM_PROFILE = Profile(
        name="computronium-lab",
        policy_version="26.0",
        scope_dimensions={
            "domain": str,
            "task": str,
            "run_id": str,
            "substrate": str,
            "geometry": str,
            "credit": str,
            "budget": str,
        },
        budget_tiers=("quick", "standard", "nightly"),
        tier_budget={"smoke": "quick", "quick": "standard", "certified": "nightly"},
        default_cost={"quick": 1.0, "standard": 4.0, "nightly": 16.0},
        constraints=(
            *CORE_CONSTRAINTS,
            Constraint("frozen_theta_audit_for_psi_only_claims", _frozen_theta_audit),
            Constraint("identity_card_for_new_primitive", _identity_card),
        ),
        quality=CORE_QUALITY,
    )
except ImportError:
    COMPUTRONIUM_PROFILE = None
    ledger = None
    LedgerRole = None

if TYPE_CHECKING:
    from pathlib import Path

    from computronium_lab.adaptation import (
        AdaptationMode,
        AdaptationResult,
        TaskBoundary,
    )
    from computronium_lab.synthesis.engine import ParetoOption, SynthesisResult
    from computronium_lab.synthesis.predictor import (
        ViabilityPredictor as ViabilityPredictor,
    )


# flat_classification_hard operating point (TODO25 D.2): dims ride the
# registered spec defaults (64 x 8); the measured calibration sweep
# (scripts/probes/todo25_hard_task.json) pins the same scale/noise as the
# flat tier — hardness comes from dims/classes, which clears saturation at
# 20ep (top row 0.984, no row >= 0.995) while weak rules separate.
HARD_TASK_PARAMS: _HardTaskParams = {"scale": 1.2, "noise": 1.5}


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    """One preset's quick training outcome."""

    preset: str
    final_loss: float
    final_accuracy: float
    walltime_s: float
    history: list[dict[str, float]] = field(default_factory=list)


class _HardTaskParams(TypedDict):
    """Difficulty overrides for the flat_classification_hard generator."""

    scale: float
    noise: float


def synthetic_task(
    seed: int = 0,
    n: int = 256,
    input_dim: int = 32,
    num_classes: int = 4,
    batch_size: int = 32,
    *,
    scale: float = 1.2,
    noise: float = 1.5,
) -> tuple[DataLoader[tuple[Tensor, ...]], DataLoader[tuple[Tensor, ...]]]:
    """Deterministic gaussian-blob classification task (quick mode).

    Calibrated difficulty (scale=1.2, noise=1.5): strong gradient-trained
    mechanisms land ~0.90 at 20 epochs while weaker credit rules separate
    below — see the difficulty-sweep note in the body. The
    ``flat_classification_hard`` corpus class (TODO25 D.2) passes harder
    ``scale``/``noise`` via ``HARD_TASK_PARAMS`` so 20 epochs no longer
    saturates.
    """
    gen = torch.Generator().manual_seed(seed)
    # (1.2, 1.5) is the calibrated difficulty operating point (2026-09-13
    # difficulty sweep, TODO23 §12): the old (2.0, 0.5) task saturated at
    # 1.0 for every gradient-trained mechanism, so accuracy metadata
    # stopped discriminating. At (1.2, 1.5) backprop lands ~0.90 @ 20ep
    # while weaker credit rules separate below it.
    x, y = gaussian_blobs(
        n, input_dim, num_classes, scale=scale, noise=noise, generator=gen
    )
    split = int(n * 0.75)
    train = DataLoader(
        TensorDataset(x[:split], y[:split]), batch_size=batch_size, shuffle=True
    )
    val = DataLoader(TensorDataset(x[split:], y[split:]), batch_size=batch_size)
    return train, val


class Lab:
    """High-level interface to the Computronium ontology.

    Wraps existing validated factories and trainers only; no new ontology
    semantics. CEEC evidence recording is opt-in via ``record_ledger``.
    """

    def __init__(
        self,
        device: str = "cpu",
        seed: int = 0,
        quick: bool = True,
        record_ledger: str | None = None,
    ) -> None:
        self.device = device
        self.seed = seed
        self.quick = quick
        self.record_ledger = record_ledger
        self.last_results: list[ComparisonResult] = []

    def specify(
        self,
        task: str,
        dataset: str,
        constraints: Constraints | None = None,
        objectives: tuple[str, ...] = ("accuracy",),
        exploration_budget: int = 3,
        **dims: int,
    ) -> ProblemSpec:
        """Specify the problem — the input to synthesize() (TODO23 T23.1.1)."""
        spec = ProblemSpec(
            task=task,
            dataset=dataset,
            constraints=constraints or Constraints(),
            objectives=objectives,
            exploration_budget=exploration_budget,
            input_dim=int(dims.get("input_dim", 32)),
            num_classes=int(dims.get("num_classes", 4)),
        )
        return spec

    def synthesize(
        self,
        spec: ProblemSpec,
        *,
        model: ViabilityPredictor | None = None,
        include_evolved: bool = False,
    ) -> SynthesisResult:
        """Spec → best valid mechanism coordinate with provenance (T23.1.5).

        ``model`` overrides the shared fitted viability predictor — a test
        or caller may pin predictions instead of inheriting the fit's drift.
        ``include_evolved`` folds archived *measured* accuracies from the
        frontier archive into selection; off by default.
        """
        from computronium_lab.synthesis.engine import synthesize as _synthesize

        result = _synthesize(spec, model=model, campaigns_run={})
        if result.exploratory:
            self._record_exploratory(result, spec)
        return result

    def ledger_session(self, *, role: str = "campaign"):
        """Session bound to ``record_ledger`` + the Computronium profile."""
        if not self.record_ledger:
            raise ValueError("ledger_session requires record_ledger on Lab(...)")
        if COMPUTRONIUM_PROFILE is None or ledger is None:
            raise ImportError("CEEC not available")
        return ledger(self.record_ledger, COMPUTRONIUM_PROFILE, role=LedgerRole(role))

    def _record_exploratory(self, result: SynthesisResult, spec: ProblemSpec) -> None:
        """Opt-in CEEC artifact for an exploratory synthesis (T23.1.7)."""
        if not self.record_ledger or COMPUTRONIUM_PROFILE is None or ledger is None:
            return
        with self.ledger_session(role="main") as sess:
            payload = json.dumps(
                {
                    "mechanism": result.name,
                    "coordinate": result.coordinate,
                    "predicted_viability": result.predicted_viability,
                    "spec": spec.key(),
                    "provenance": list(result.provenance),
                },
                indent=2,
            )
            artifact = sess.artifact(
                payload.encode(),
                "exploratory_synthesis",
                {
                    "source": "computronium_lab.synthesize",
                    "mechanism": result.name,
                    "exploratory": True,
                },
            )
            sess.evidence(
                _lab_scope(spec),
                artifact_refs=[artifact.id],
                predicted_viability=result.predicted_viability,
                notes="exploratory synthesis (T23.1.7): campaign pending",
            )

    def explore(self, spec: ProblemSpec) -> list[ParetoOption]:
        """Pareto frontier of constraint-satisfying mechanisms (T23.1.6)."""
        from computronium_lab.synthesis.engine import explore as _explore

        return _explore(spec)

    def compose(self, coordinate: object) -> object:
        """One-line system composition from a 6-axis coordinate."""
        from computronium.core.system_trainer import compose_joint_system

        if hasattr(coordinate, "__dict__"):
            # Assume it's a coordinate object with substrate, geometry, etc.
            kwargs = coordinate.__dict__
            return compose_joint_system(**kwargs)
        raise ValueError("compose() expects a coordinate object with axis attributes")

    def train(
        self,
        system: object,
        task: str = "synthetic",
        epochs: int = 1,
        batch_size: int = 32,
        *,
        spec: ProblemSpec | None = None,
        options: TrainOptions | None = None,
        val_data: object | None = None,
        train_data: object | None = None,
    ) -> TrainingResult:
        """Train with opt-in guarantees; returns a TrainingResult (T23.2.1)."""
        if task != "synthetic":
            raise ValueError(
                f"task {task!r} not wired; Lab quick mode ships 'synthetic'"
            )
        opts = options or TrainOptions()
        if val_data is not None and opts.val_data is None:
            opts = replace(opts, val_data=val_data)
        torch.manual_seed(self.seed)
        if train_data is not None:
            return train_with_certificates(
                system,
                train_data,
                device=self.device,
                seed=self.seed,
                epochs=epochs,
                batch_size=batch_size,
                spec=spec,
                options=opts,
                record_ledger=self.record_ledger,
            )
        train_loader, _ = synthetic_task(
            seed=self.seed,
            batch_size=batch_size,
            input_dim=spec.input_dim if spec is not None else 32,
            num_classes=spec.num_classes if spec is not None else 4,
        )
        return train_with_certificates(
            system,
            train_loader,
            device=self.device,
            seed=self.seed,
            epochs=epochs,
            batch_size=batch_size,
            spec=spec,
            options=opts,
            record_ledger=self.record_ledger,
        )

    def adapt(
        self,
        system: object,
        task_data: object,
        mode: AdaptationMode | str = "psi_only",
        *,
        episodes: int = 10,
        boundary: TaskBoundary | None = None,
        stability_check: bool = False,
        psi_step: str = "final",
        psi: dict | None = None,
    ) -> AdaptationResult:
        """ψ-only continual adaptation on frozen θ (T23 Phase 3)."""
        from computronium_lab.adaptation import adapt as _adapt

        torch.manual_seed(self.seed)
        return _adapt(
            system,
            task_data,
            mode,
            episodes=episodes,
            boundary=boundary,
            stability_check=stability_check,
            psi_step=psi_step,
            psi=psi,
        )

    def compare(
        self,
        systems: list[tuple[str, object]],
        task: str = "synthetic",
        epochs: int = 1,
    ) -> list[ComparisonResult]:
        """Train each (name, system) pair; keep results for report()."""
        results: list[ComparisonResult] = []
        for name, system in systems:
            t0 = time.perf_counter()
            metrics = self.train(system, task=task, epochs=epochs).metrics
            walltime = time.perf_counter() - t0
            results.append(
                ComparisonResult(
                    preset=name,
                    final_loss=metrics["loss"],
                    final_accuracy=metrics["accuracy"],
                    walltime_s=walltime,
                )
            )
        self.last_results = results
        return results

    def report(self, path: str) -> str:
        """Write a markdown report of the last compare() call."""
        if not self.last_results:
            raise ValueError("nothing to report; run compare() first")
        from computronium_lab.report import write_report

        return write_report(self.last_results, path)


def _lab_scope(spec: ProblemSpec | None):
    from ceec.models import Scope

    substrate = spec.constraints.substrate if spec is not None else "digital"
    return Scope.of(domain="lab", substrate=substrate, budget="quick")