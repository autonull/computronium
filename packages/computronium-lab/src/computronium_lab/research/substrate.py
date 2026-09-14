"""Substrate robustness benchmark (TODO24 Phase 5): deployment transfer
measured, not described.

Trains on the source substrate, transfers to INT8 / ternary / memristive
constraints, and records accuracy delta, fidelity, export success, energy
estimates, and constraint preservation per target. Substrate models remain
simulated: energy values carry their tier label, never a hardware claim.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium_lab.lab import Lab
    from computronium_lab.synthesis.catalog import MechanismCandidate
    from computronium_lab.synthesis.spec import ProblemSpec

from computronium_lab.research.paths import results_dir, write_manifest
from computronium_lab.research.schema import (
    BudgetTier,
    MeasurementBlock,
    ProblemClassProtocol,
)

__all__ = [
    "TransferReport",
    "TransferScore",
    "benchmark_substrate_transfer",
]

_TARGET_CONSTRAINTS: dict[str, dict[str, object]] = {
    "digital": {"quantization": None, "substrate": "digital"},
    "int8": {"quantization": "int8", "substrate": "digital"},
    "ternary": {"quantization": "ternary", "substrate": "digital"},
    "memristive": {"quantization": None, "substrate": "memristive"},
}


@dataclass(frozen=True, slots=True)
class TransferScore:
    """Composite transfer record for one (target, seed)."""

    mechanism: str
    target: str
    seed: int
    accuracy: float
    accuracy_delta: float
    fidelity: float
    export_success: bool
    energy_j: float
    energy_tier: str
    constraints_preserved: bool


@dataclass(frozen=True, slots=True)
class TransferReport:
    """Transfer robustness across mechanisms and constraint sets."""

    mechanism: str
    source_substrate: str
    targets: tuple[str, ...]
    seeds: tuple[int, ...]
    scores: tuple[TransferScore, ...]
    ranking: tuple[str, ...]
    blocks: tuple[MeasurementBlock, ...]
    cookbook_drafts: tuple[dict[str, object], ...]
    manifest_paths: tuple[str, ...]
    ledger: dict[str, object]


def benchmark_substrate_transfer(
    lab: Lab,
    mechanism: str = "backprop_mlp",
    source_substrate: str = "digital",
    target_constraints: Sequence[str] = ("int8", "ternary", "memristive"),
    seeds: Sequence[int] = (0, 1, 2),
) -> TransferReport:
    """Train-once-transfer-many robustness campaign (T24.5.1/5.2)."""
    from computronium_lab.research.corpus import CLASS_BY_NAME

    for target in target_constraints:
        if target not in _TARGET_CONSTRAINTS:
            raise ValueError(f"unknown transfer target {target!r}")
    spec = lab.specify("substrate_transfer", "gaussian_blob")
    cls = CLASS_BY_NAME["substrate_transfer"](spec, mechanism=mechanism)
    runner = _TransferRunner(lab, spec, cls, mechanism, source_substrate, seeds)
    return runner.execute(tuple(target_constraints))


class _TransferRunner:
    def __init__(
        self,
        lab: Lab,
        spec: ProblemSpec,
        cls: ProblemClassProtocol,
        mechanism: str,
        source_substrate: str,
        seeds: Sequence[int],
    ) -> None:
        self.lab = lab
        self.spec = spec
        self.cls = cls
        self.mechanism = mechanism
        self.source_substrate = source_substrate
        self.seeds = tuple(seeds)
        self.blocks: list[MeasurementBlock] = []
        self.manifests: list[str] = []

    def execute(self, targets: tuple[str, ...]) -> TransferReport:
        scores: list[TransferScore] = []
        with tempfile.TemporaryDirectory(prefix="transfer_") as scratch:
            for seed in self.seeds:
                baseline = self._run_arm("digital", seed)
                if baseline is None:
                    continue
                for target in targets:
                    score = self._run_target(target, seed, baseline, scratch)
                    if score is not None:
                        scores.append(score)
        ranking = _rank(targets, scores)
        report = TransferReport(
            mechanism=self.mechanism,
            source_substrate=self.source_substrate,
            targets=targets,
            seeds=self.seeds,
            scores=tuple(scores),
            ranking=ranking,
            blocks=tuple(self.blocks),
            cookbook_drafts=_drafts(self.mechanism, targets, scores),
            manifest_paths=tuple(self.manifests),
            ledger={"ledger": self.lab.record_ledger, "manifests": []},
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

    def _run_arm(self, arm: str, seed: int) -> dict[str, float] | None:
        try:
            return self.cls.run_arm(self.lab, arm, seed, epochs=5)
        except Exception as exc:
            self.blocks.append(
                MeasurementBlock(
                    problem_class="substrate_transfer",
                    mechanism=f"{self.mechanism}/{arm}",
                    reason=f"transfer arm failed at seed {seed}: {type(exc).__name__}",
                    tier=BudgetTier.QUICK.value,
                    detail=str(exc)[:500],
                )
            )
            return None

    def _run_target(
        self, target: str, seed: int, baseline: dict[str, float], scratch: str
    ) -> TransferScore | None:
        metrics = self._run_arm(target, seed)
        if metrics is None:
            return None
        export_success, preserved = self._export_probe(target, seed, scratch)
        return TransferScore(
            mechanism=self.mechanism,
            target=target,
            seed=seed,
            accuracy=metrics["accuracy"],
            accuracy_delta=metrics["accuracy"] - baseline["accuracy"],
            fidelity=metrics["fidelity"],
            export_success=export_success,
            energy_j=metrics["energy_j"],
            energy_tier="simulated",
            constraints_preserved=preserved,
        )

    def _export_probe(self, target: str, seed: int, scratch: str) -> tuple[bool, bool]:
        from pathlib import Path as _Path

        from computronium_lab.deployment import export_system
        from computronium_lab.synthesis.spec import Constraints

        config = _TARGET_CONSTRAINTS[target]
        out_dir = _Path(scratch) / f"{target}_{seed}"
        try:
            self.lab.seed = seed
            system = _row(self.mechanism).build(self.spec)
            export = export_system(
                system,
                str(out_dir),
                constraints=Constraints(substrate=str(config["substrate"])),
                target="onnx",
                quantization=config["quantization"],  # type: ignore[arg-type]
            )
            manifest_ok = _Path(export.manifest_path).exists()
            return True, bool(
                export.substrate_report.constraints_preserved and manifest_ok
            )
        except Exception as exc:
            self.blocks.append(
                MeasurementBlock(
                    problem_class="substrate_transfer",
                    mechanism=f"{self.mechanism}/{target}",
                    reason=f"export failed at seed {seed}: {type(exc).__name__}",
                    tier=BudgetTier.QUICK.value,
                    detail=str(exc)[:500],
                )
            )
            return False, False

    def _write_manifests(self, report: TransferReport) -> None:
        for seed in self.seeds:
            run_dir = results_dir(
                "substrate_transfer",
                seed,
                timestamp=datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
            )
            payload = {
                "problem_class": "substrate_transfer",
                "mechanism": report.mechanism,
                "source_substrate": report.source_substrate,
                "tier": BudgetTier.QUICK.value,
                "seed": seed,
                "ranking": list(report.ranking),
                "scores": [
                    {
                        "target": s.target,
                        "accuracy": s.accuracy,
                        "accuracy_delta": s.accuracy_delta,
                        "fidelity": s.fidelity,
                        "export_success": s.export_success,
                        "energy_j": s.energy_j,
                        "energy_tier": s.energy_tier,
                    }
                    for s in report.scores
                    if s.seed == seed
                ],
            }
            self.manifests.append(str(write_manifest(run_dir, payload)))

    def _record_ledger(self, report: TransferReport) -> None:
        import json as _json

        from computronium_lab.research.adapters import LabRecorder
        from computronium_lab.research.evidence import (
            frontier_evidence,
            vector_evidence,
        )

        store = LabRecorder(self.lab).store()
        if store is None:
            return
        try:
            from ceec.models import Scope

            scope = Scope(
                domain="research",
                substrate=(self.source_substrate,),
                budget=BudgetTier.QUICK.value,
                extra={"problem_class": "substrate_transfer"},
            )
            artifact = store.ingest_artifact(
                _json.dumps(
                    {
                        "mechanism": report.mechanism,
                        "ranking": list(report.ranking),
                    },
                    sort_keys=True,
                ).encode(),
                "research_corpus_summary",
                {"problem_class": "substrate_transfer"},
            )
            store.record_derived(
                type_="transfer_summary",
                operator="transfer_protocol_v1",
                inputs={"a": [artifact.id]},
                scope=scope,
                value={
                    "mechanism": report.mechanism,
                    "ranking": list(report.ranking),
                },
            )
            for target in report.targets:
                deltas = [s.accuracy_delta for s in report.scores if s.target == target]
                if deltas:
                    vector_evidence(
                        store,
                        scope,
                        axes=["seed"],
                        values=deltas,
                        values_ref=f"transfer/{report.mechanism}/{target}",
                        quality={"seeds": len(deltas), "matched_control": True},
                        notes=f"transfer accuracy delta {target}",
                    )
            points = [
                {"accuracy": s.accuracy, "energy_j": s.energy_j} for s in report.scores
            ]
            if points:
                frontier_evidence(
                    store,
                    scope,
                    points=points,
                    axes=["accuracy", "energy_j"],
                    values_ref=f"transfer/{report.mechanism}/frontier",
                    quality={"tier": "simulated"},
                    notes="accuracy-energy transfer frontier (simulated energy)",
                )
            for block in report.blocks:
                block.record(store, scope)
            store._conn.commit()
        finally:
            store.close()


def _row(name: str) -> MechanismCandidate:
    from computronium_lab.synthesis.catalog import CATALOG

    for candidate in CATALOG:
        if candidate.name == name:
            return candidate
    raise ValueError(f"{name!r} is not cataloged")


def _rank(targets: tuple[str, ...], scores: Sequence[TransferScore]) -> tuple[str, ...]:
    """Robustness order: export success, accuracy delta, fidelity."""

    def _key(target: str) -> tuple[float, float, float]:
        rows = [s for s in scores if s.target == target]
        if not rows:
            return (0.0, float("-inf"), float("inf"))
        success = sum(1.0 for s in rows if s.export_success) / len(rows)
        delta = sum(s.accuracy_delta for s in rows) / len(rows)
        fidelity = sum(s.fidelity for s in rows) / len(rows)
        return (success, delta, -fidelity)

    return tuple(sorted(targets, key=_key, reverse=True))


def _drafts(
    mechanism: str, targets: tuple[str, ...], scores: Sequence[TransferScore]
) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "mechanism": mechanism,
            "target": target,
            "mean_accuracy_delta": (
                sum(s.accuracy_delta for s in scores if s.target == target)
                / max(1, sum(1 for s in scores if s.target == target))
            ),
            "status": "draft",
        }
        for target in targets
    )
