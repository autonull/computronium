"""Continual adaptation benchmark (TODO24 Phase 4): ψ-only adaptation
measured against matched controls.

The benchmark runs the ``continual_switch`` corpus class across ψ modes
and controls at equal pass budgets, with θ bitwise-invariance proofs and
a mutable-state inventory per ψ arm. A capacity-matched recurrent control
is included where constructible; otherwise a measurement block records
why not.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium_lab.lab import Lab
    from computronium_lab.research.corpus import ArmSummary
    from computronium_lab.synthesis.spec import ProblemSpec

from computronium_lab.research.paths import results_dir, write_manifest
from computronium_lab.research.schema import (
    BudgetTier,
    MeasurementBlock,
    ProblemClassProtocol,
    StatisticalSummary,
)

__all__ = [
    "CURRICULA",
    "ContinualReport",
    "CurriculumSpec",
    "benchmark_continual",
    "register_curriculum",
]

_CAPACITY_MECHANISM = "ntm_classifier"


class _ContinualClass(ProblemClassProtocol, Protocol):
    """Problem class with a θ-invariance proof surface (continual_switch)."""

    last_proof: dict[str, object] | None


@dataclass(frozen=True, slots=True)
class CurriculumSpec:
    """Task-stream generator: task A → task B with a boundary."""

    name: str = "two_task_switch"
    task_a_offset: int = 0
    task_b_offset: int = 5000
    threshold: float = 0.5
    max_episodes: int = 10
    description: str = "gaussian-blob task A, fresh-seed task B, fixed threshold"


CURRICULA: dict[str, CurriculumSpec] = {
    "two_task_switch": CurriculumSpec(),
}


def register_curriculum(spec: CurriculumSpec) -> None:
    """Plug a new task-stream curriculum into the benchmark (TODO24 §14).

    The continual benchmark resolves a curriculum name through this
    registry, so new A→B streams (offsets, thresholds, episode budgets)
    need no benchmark-code changes.
    """
    if spec.name in CURRICULA:
        raise ValueError(f"curriculum {spec.name!r} is already registered")
    CURRICULA[spec.name] = spec


@dataclass(frozen=True, slots=True)
class ContinualComparison:
    """Paired comparison of one ψ mode against one control."""

    mode: str
    control: str
    mean_diff: float
    paired_p: float | None
    effect_size: float | None


@dataclass(frozen=True, slots=True)
class ContinualReport:
    """Per-mode metrics, controls, statistics, proofs, ledger references."""

    mechanism: str
    curriculum: str
    modes: tuple[str, ...]
    controls: tuple[str, ...]
    seeds: tuple[int, ...]
    arms: tuple[ArmSummary, ...]
    comparisons: tuple[ContinualComparison, ...]
    invariance_proofs: dict[str, list[dict[str, object]]]
    state_inventory: tuple[str, ...]
    capacity_control: str | None
    blocks: tuple[MeasurementBlock, ...]
    cookbook_drafts: tuple[dict[str, object], ...]
    manifest_paths: tuple[str, ...]
    ledger: dict[str, object]


def _state_inventory() -> tuple[str, ...]:
    return (
        "theta: bitwise digest before/after every arm (adaptation.theta_digest)",
        "psi arms: FrozenThetaAudit persistent-state report attached to proof",
        "optimizer state: none carried (closed-form ridge plasticity, no optimizer)",
        "dataloaders: fresh deterministic loaders per seed; val split held out",
        "buffers: frozen backbone buffers; psi is the sole writable state",
    )


def benchmark_continual(
    lab: Lab,
    mechanism: str = "temporal_psi_task_switcher",
    curriculum: str | CurriculumSpec = "two_task_switch",
    modes: Sequence[str] = ("temporal", "role_split", "conflict_adaptive"),
    controls: Sequence[str] = ("frozen_no_psi", "theta_finetune_matched_compute"),
    seeds: Sequence[int] = (0, 1, 2),
) -> ContinualReport:
    """A/B benchmark: ψ modes vs frozen and θ-update matched controls."""
    spec = lab.specify("continual_switch", "two_task_stream")
    if isinstance(curriculum, str):
        if curriculum not in CURRICULA:
            raise ValueError(f"unknown curriculum {curriculum!r}")
        resolved = CURRICULA[curriculum]
    else:
        resolved = curriculum
    if isinstance(curriculum, str) and curriculum not in CURRICULA:
        raise ValueError(f"unknown curriculum {curriculum!r}")
    runner = _BenchmarkRunner(lab, spec, mechanism, resolved, seeds)
    return runner.execute(modes, controls)


class _BenchmarkRunner:
    def __init__(
        self,
        lab: Lab,
        spec: ProblemSpec,
        mechanism: str,
        curriculum: CurriculumSpec,
        seeds: Sequence[int],
    ) -> None:
        self.lab = lab
        self.spec = spec
        self.mechanism = mechanism
        self.curriculum = curriculum
        self.seeds = tuple(seeds)
        self.proofs: dict[str, list[dict[str, object]]] = {}
        self.blocks: list[MeasurementBlock] = []
        self.manifests: list[str] = []

    def execute(self, modes: Sequence[str], controls: Sequence[str]) -> ContinualReport:
        from computronium_lab.research.corpus import CLASS_BY_NAME

        cls = cast(
            "_ContinualClass",
            CLASS_BY_NAME["continual_switch"](
                self.spec,
                mechanism=self.mechanism,
                stream_offset=self.curriculum.task_b_offset
                - self.curriculum.task_a_offset,
                threshold=self.curriculum.threshold,
            ),
        )
        values: dict[str, dict[str, list[float]]] = {}
        arms = (*modes, *controls)
        for arm in arms:
            values[arm] = self._run_arm(cls, arm)
        capacity = self._run_capacity_control()
        if capacity is not None:
            values["capacity_matched_recurrent"] = capacity
        summaries = self._summarize(values)
        comparisons = self._compare(values, modes, controls)
        ledger: dict[str, object] = {"ledger": self.lab.record_ledger, "manifests": []}
        report = ContinualReport(
            mechanism=self.mechanism,
            curriculum=self.curriculum.name,
            modes=tuple(modes),
            controls=tuple(controls),
            seeds=self.seeds,
            arms=tuple(summaries),
            comparisons=tuple(comparisons),
            invariance_proofs=dict(self.proofs),
            state_inventory=_state_inventory(),
            capacity_control=(
                "capacity_matched_recurrent"
                if "capacity_matched_recurrent" in values
                else None
            ),
            blocks=tuple(self.blocks),
            cookbook_drafts=_drafts(values, comparisons, self.curriculum),
            manifest_paths=(),
            ledger=ledger,
        )
        self._write_manifests(report)
        self._record_ledger(report)
        from dataclasses import replace

        return replace(
            report,
            manifest_paths=tuple(self.manifests),
            ledger={
                "ledger": self.lab.record_ledger,
                "manifests": list(self.manifests),
            },
        )

    def _run_arm(self, cls: _ContinualClass, arm: str) -> dict[str, list[float]]:
        collected: dict[str, list[float]] = {}
        for seed in self.seeds:
            shifted = seed + self.curriculum.task_a_offset
            try:
                metrics = cls.run_arm(
                    self.lab, arm, shifted, epochs=self.curriculum.max_episodes
                )
            except Exception as exc:
                self.blocks.append(
                    MeasurementBlock(
                        problem_class="continual_switch",
                        mechanism=f"{self.mechanism}/{arm}",
                        reason=f"arm failed at seed {seed}: {type(exc).__name__}",
                        tier=BudgetTier.QUICK.value,
                        detail=str(exc)[:500],
                    )
                )
                continue
            for metric, value in metrics.items():
                collected.setdefault(metric, []).append(float(value))
        proof = cls.last_proof
        if proof is not None:
            self.proofs.setdefault(arm, []).append(proof)
        return collected

    def _run_capacity_control(self) -> dict[str, list[float]] | None:
        from computronium_lab.research.corpus import CLASS_BY_NAME

        try:
            cls = cast(
                "_ContinualClass",
                CLASS_BY_NAME["continual_switch"](
                    self.spec,
                    mechanism=_CAPACITY_MECHANISM,
                    stream_offset=(
                        self.curriculum.task_b_offset - self.curriculum.task_a_offset
                    ),
                    threshold=self.curriculum.threshold,
                ),
            )
            probe = cls.run_arm(
                self.lab,
                "theta_finetune_matched_compute",
                self.curriculum.task_a_offset,
                epochs=1,
            )
        except Exception as exc:
            self.blocks.append(
                MeasurementBlock(
                    problem_class="continual_switch",
                    mechanism=_CAPACITY_MECHANISM,
                    reason="capacity-matched recurrent control not constructible",
                    tier=BudgetTier.QUICK.value,
                    detail=f"{type(exc).__name__}: {str(exc)[:300]}",
                )
            )
            return None
        del probe
        return self._run_arm(cls, "theta_finetune_matched_compute")

    def _summarize(self, values: dict[str, dict[str, list[float]]]) -> list[ArmSummary]:
        from computronium_lab.research.corpus import ArmSummary
        from computronium_lab.research.schema import StatisticalSummary

        summaries = []
        for arm, metrics in values.items():
            arm_summaries: dict[str, StatisticalSummary] = {}
            for metric, samples in metrics.items():
                summary = StatisticalSummary.from_samples(metric, samples)
                frozen = values.get("frozen_no_psi", {}).get(metric, ())
                if frozen and len(frozen) == len(samples) and arm != "frozen_no_psi":
                    summary = summary.with_paired(samples, list(frozen))
                arm_summaries[metric] = summary
            summaries.append(
                ArmSummary(
                    arm=arm,
                    metric_values={
                        metric: tuple(samples) for metric, samples in metrics.items()
                    },
                    summaries=arm_summaries,
                    control_values={},
                    seeds=self.seeds,
                )
            )
        return summaries

    def _compare(
        self,
        values: dict[str, dict[str, list[float]]],
        modes: Sequence[str],
        controls: Sequence[str],
    ) -> list[ContinualComparison]:
        from computronium.validation.statistics import permutation_test_p

        comparisons = []
        for mode in modes:
            treated = values.get(mode, {}).get("accuracy", ())
            for control in controls:
                baseline = values.get(control, {}).get("accuracy", ())
                if len(treated) != len(baseline) or not treated:
                    continue
                diffs = [t - c for t, c in zip(treated, baseline)]
                mean_diff = sum(diffs) / len(diffs)
                comparisons.append(
                    ContinualComparison(
                        mode=mode,
                        control=control,
                        mean_diff=mean_diff,
                        paired_p=permutation_test_p(
                            list(treated), list(baseline), n_perm=2000
                        ),
                        effect_size=mean_diff,
                    )
                )
        return comparisons

    def _write_manifests(self, report: ContinualReport) -> None:
        for seed in self.seeds:
            run_dir = results_dir(
                "continual_switch", seed, timestamp=_run_stamp(report)
            )
            payload = {
                "problem_class": "continual_switch",
                "mechanism": report.mechanism,
                "curriculum": report.curriculum,
                "tier": BudgetTier.QUICK.value,
                "seed": seed,
                "modes": list(report.modes),
                "comparisons": [
                    {
                        "mode": c.mode,
                        "control": c.control,
                        "mean_diff": c.mean_diff,
                        "paired_p": c.paired_p,
                    }
                    for c in report.comparisons
                ],
            }
            self.manifests.append(str(write_manifest(run_dir, payload)))

    def _record_ledger(self, report: ContinualReport) -> None:
        import json as _json

        from computronium_lab.research.adapters import LabRecorder
        from computronium_lab.research.evidence import vector_evidence

        store = LabRecorder(self.lab).store()
        if store is None:
            return
        try:
            from ceec.models import Scope

            scope = Scope(
                domain="research",
                substrate=("digital",),
                budget=BudgetTier.QUICK.value,
                extra={"problem_class": "continual_switch"},
            )
            artifact = store.ingest_artifact(
                _json.dumps(
                    {
                        "mechanism": report.mechanism,
                        "curriculum": report.curriculum,
                        "comparisons": len(report.comparisons),
                    },
                    sort_keys=True,
                ).encode(),
                "research_corpus_summary",
                {"problem_class": "continual_switch"},
            )
            store.record_derived(
                type_="benchmark_summary",
                operator="continual_protocol_v1",
                inputs={"a": [artifact.id]},
                scope=scope,
                value={
                    "mechanism": report.mechanism,
                    "curriculum": report.curriculum,
                    "comparisons": len(report.comparisons),
                },
            )
            for arm in report.arms:
                accuracy = arm.metric_values.get("accuracy", ())
                if accuracy:
                    vector_evidence(
                        store,
                        scope,
                        axes=["seed"],
                        values=list(accuracy),
                        values_ref=f"continual/{report.curriculum}/{arm.arm}",
                        quality={"seeds": len(accuracy), "matched_control": True},
                        notes=f"continual {arm.arm}",
                    )
            for block in report.blocks:
                block.record(store, scope)
            store._conn.commit()
        finally:
            store.close()


def _run_stamp(report: ContinualReport) -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _drafts(
    values: dict[str, dict[str, list[float]]],
    comparisons: list[ContinualComparison],
    curriculum: CurriculumSpec,
) -> tuple[dict[str, object], ...]:
    drafts = []
    for comparison in comparisons:
        drafts.append({
            "mode": comparison.mode,
            "control": comparison.control,
            "curriculum": curriculum.name,
            "mean_diff": comparison.mean_diff,
            "paired_p": comparison.paired_p,
            "status": "draft",
        })
    return tuple(drafts)
