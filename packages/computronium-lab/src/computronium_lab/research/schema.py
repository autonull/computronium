"""Research schema (TODO24 Phase 0): durable abstractions for the Certified
Research Corpus.

Every measurement maps onto CEEC-Core objects: a ``MeasurementProtocol``
pre-registers as a ceec ``Experiment`` (``ceec.bootstrap.experiment_from_config``
shape), a ``StatisticalSummary`` records as a ceec ``Derived``, and a
``MeasurementBlock`` records as a lab artifact with ``inert``/``missing``
evidence (notes mandatory). Budget tiers follow the RESEARCH3 E-1 ladder:
smoke → smoke, quick → pilot, certified → full; only ``certified`` supports
cookbook entries or belief promotion, and "certified" is shorthand for
"campaign gates passed", never a belief status.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ceec.models import Scope
    from ceec.store import CEECStore

    from computronium_lab.lab import Lab

from computronium_lab.research.evidence import record_block

__all__ = [
    "BUDGET_CAPS",
    "BudgetCap",
    "BudgetTier",
    "CorpusSpec",
    "MeasurementBlock",
    "MeasurementProtocol",
    "ProblemClassProtocol",
    "StatisticalSummary",
]


class BudgetTier(StrEnum):
    """Measurement budget tier (RESEARCH3 E-1 ladder)."""

    SMOKE = "smoke"
    QUICK = "quick"
    CERTIFIED = "certified"


@dataclass(frozen=True, slots=True)
class BudgetCap:
    """Hard caps for one budget tier; ``None`` epochs inherits the task's
    certified operating point."""

    max_campaigns: int
    max_epochs_per_campaign: int | None
    max_seeds: int


BUDGET_CAPS: Mapping[str, BudgetCap] = {
    BudgetTier.SMOKE: BudgetCap(2, 1, 1),
    BudgetTier.QUICK: BudgetCap(8, 20, 3),
    BudgetTier.CERTIFIED: BudgetCap(24, None, 3),
}

CERTIFIED_OUTCOMES: Mapping[str, frozenset[str]] = {
    BudgetTier.SMOKE: frozenset({"pass_fail"}),
    BudgetTier.QUICK: frozenset({"frontier_hints", "exploratory_notes"}),
    BudgetTier.CERTIFIED: frozenset({
        "cookbook",
        "belief_promotion",
        "publication_reports",
    }),
}


@runtime_checkable
class ProblemClassProtocol(Protocol):
    """A standardized, extensible research problem class (TODO24 §14).

    Implementations are pure protocol plugs — no core evolution changes are
    required to add one. ``task`` must be deterministic for a fixed seed.
    """

    @property
    def name(self) -> str:
        """Registry key (also the class's measurement-block namespace)."""
        ...

    def generate_task(self, seed: int) -> object:
        """Deterministic task data for the given seed."""
        ...

    def default_metrics(self) -> tuple[str, ...]:
        """Metric names this class reports per arm."""
        ...

    def run_arm(
        self,
        lab: Lab,
        arm: str,
        seed: int,
        *,
        epochs: int,
    ) -> dict[str, float]:
        """Train/adapt one arm and return its metric values."""
        ...

    def control_arm(self, arm: str) -> str | None:
        """The matched control for ``arm`` (label-permutation family), if any."""
        ...


@dataclass(frozen=True, slots=True)
class MeasurementProtocol:
    """Pre-registerable measurement design for one problem class."""

    problem_class: str
    seeds: tuple[int, ...]
    epochs: int
    controls: tuple[str, ...] = ()
    tier: str = BudgetTier.QUICK
    val_split: float = 0.25
    equal_compute: bool = True
    evidence_kind: str = "vector"
    extra: dict[str, object] = field(default_factory=dict)

    def experiment_config(self, *, question: str, prediction: str) -> dict[str, object]:
        """CEEC ``Experiment``-shaped config (``ceec.bootstrap`` compatible)."""
        return {
            "id": f"X-R24-{self.problem_class.upper().replace('-', '')}-001",
            "question": question,
            "rationale": f"corpus measurement of {self.problem_class} at tier {self.tier}",
            "design": {
                "seeds": list(self.seeds),
                "epochs": self.epochs,
                "equal_compute": self.equal_compute,
                "controls": list(self.controls),
                "evidence_kind": self.evidence_kind,
                **dict(self.extra),
            },
            "metrics": ["accuracy"],
            "hard_gates": ["BenchmarkReproduction", "StabilityCertificate"],
            "prediction": prediction,
            "prediction_probability": {"low": 0.6, "high": 0.9, "method": "prior"},
            "budget": "quick",
            "falsification_criterion": (
                "control arm matches or beats the treated arm on val accuracy"
            ),
            "overturn_criterion": (
                "a seed-paired permutation test finds no treated advantage"
            ),
        }


@dataclass(frozen=True, slots=True)
class StatisticalSummary:
    """Seed-level statistics for one arm; built on the RESEARCH3 PR-4 kit
    (``computronium.validation.statistics``), never a parallel stack."""

    metric: str
    n: int
    mean: float
    std: float
    ci_low: float
    ci_high: float
    paired_statistic: float | None = None
    paired_p: float | None = None
    effect_size: float | None = None

    @classmethod
    def from_samples(
        cls,
        metric: str,
        samples: Sequence[float],
        *,
        seed: int = 0,
        alpha: float = 0.05,
    ) -> StatisticalSummary:
        """Bootstrap CI over the seed sample (percentile method)."""
        import numpy as np

        from computronium.validation.statistics import bootstrap_ci

        arr = np.asarray(samples, dtype=float)
        lo, hi = bootstrap_ci(list(samples), n_boot=2000, alpha=alpha, seed=seed)
        return cls(
            metric=metric,
            n=int(arr.size),
            mean=float(arr.mean()) if arr.size else 0.0,
            std=float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
            ci_low=lo,
            ci_high=hi,
        )

    def with_paired(
        self, treated: Sequence[float], control: Sequence[float]
    ) -> StatisticalSummary:
        """Attach a paired permutation comparison against the control arm."""
        from computronium.validation.statistics import permutation_test_p

        diffs = [t - c for t, c in zip(treated, control, strict=False)]
        p = permutation_test_p(list(treated), list(control), n_perm=2000)
        effect = sum(diffs) / len(diffs) if diffs else None
        return StatisticalSummary(
            metric=self.metric,
            n=self.n,
            mean=self.mean,
            std=self.std,
            ci_low=self.ci_low,
            ci_high=self.ci_high,
            paired_statistic=effect,
            paired_p=p,
            effect_size=effect,
        )


@dataclass(frozen=True, slots=True)
class MeasurementBlock:
    """A blocked or impossible measurement (TODO24 §11 terminology: a lab
    ``measurement_block`` artifact, never a CEEC boundary belief)."""

    problem_class: str
    mechanism: str
    reason: str
    tier: str = BudgetTier.QUICK
    detail: str = ""

    def record(self, store: CEECStore, scope: Scope) -> str:
        """Persist as a ``measurement_block`` artifact with ``missing``
        evidence; notes are mandatory by construction."""
        import json

        payload = {
            "problem_class": self.problem_class,
            "mechanism": self.mechanism,
            "reason": self.reason,
            "tier": self.tier,
            "detail": self.detail,
        }
        artifact = store.ingest_artifact(
            json.dumps(payload, sort_keys=True).encode(),
            "measurement_block",
            {"problem_class": self.problem_class, "mechanism": self.mechanism},
        )
        evidence = record_block(
            store,
            scope,
            artifact_refs=[artifact.id],
            notes=f"{self.reason}: {self.detail}".strip(": "),
        )
        return evidence.id


CorpusTaskFactory = Callable[[int], object]


@dataclass(frozen=True, slots=True)
class CorpusSpec:
    """Persistent corpus declaration: problem classes, seeds, tier."""

    name: str
    problem_classes: tuple[str, ...]
    seeds: tuple[int, ...] = (0, 1, 2)
    tier: str = BudgetTier.QUICK
    description: str = ""

    def protocol_for(self, problem_class: str) -> MeasurementProtocol:
        return MeasurementProtocol(
            problem_class=problem_class,
            seeds=self.seeds,
            epochs=1 if self.tier == BudgetTier.SMOKE else 20,
            tier=self.tier,
        )
