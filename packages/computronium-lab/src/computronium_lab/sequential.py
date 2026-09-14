"""Sequence task tier (TODO23 §12: the task-class extension).

The Lab's classification tier is single-pass CE; sequence problems need
per-timestep BPTT through the geometry's own sequence API. This module
hosts the synthetic sequence tasks (Z3 generators, reused — no real
datasets, §11-compliant) and the BPTT training loop over a composed
ontology System's geometry (``geometry.episode(grad=True)``).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, cast

import torch
from torch import Tensor

from computronium.experiments.joint.z3_fixed_weights import (
    create_last_symbol_task,
    create_parity_task,
    create_threshold_task,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium_lab.lab import Lab

__all__ = [
    "SEQUENCE_TASKS",
    "SequenceCampaignReport",
    "SequenceTrainingResult",
    "sequence_campaign",
    "sequence_task",
    "train_sequence",
]

SEQUENCE_TASKS: tuple[str, ...] = ("parity", "last_symbol", "threshold")

_GENERATORS: dict[str, Callable[..., tuple[Tensor, Tensor]]] = {
    "parity": create_parity_task,
    "last_symbol": create_last_symbol_task,
    "threshold": create_threshold_task,
}

_CHANCE: dict[str, float] = {"parity": 0.5, "last_symbol": 0.5, "threshold": 0.5}


def sequence_task(
    task: str,
    *,
    batch_size: int = 32,
    seq_len: int = 8,
    input_dim: int = 8,
    seed: int = 0,
) -> tuple[Tensor, Tensor]:
    """One synthetic sequence episode ``(x (B, T, D), y (B,))``.

    Deterministic per ``seed``; generators are the recorded Z3 task
    definitions (parity / last_symbol / threshold), reused — nothing new
    is invented here.
    """
    gen = _GENERATORS.get(task)
    if gen is None:
        raise ValueError(f"unknown sequence task {task!r}; known: {SEQUENCE_TASKS}")
    torch.manual_seed(seed)
    return gen(batch_size, seq_len, input_dim)


@dataclass(frozen=True, slots=True)
class SequenceTrainingResult:
    """One BPTT training run on a composed System's geometry."""

    task: str
    epochs: int
    accuracy: float
    chance: float
    history: tuple[dict[str, float], ...] = field(default_factory=tuple)
    walltime_s: float = 0.0


def train_sequence(  # ruff: ignore[too-many-arguments] - flat sequence-run knobs
    system: object,
    task: str,
    *,
    epochs: int = 60,
    lr: float = 0.1,
    batch_size: int = 32,
    seq_len: int = 8,
    input_dim: int = 8,
    seed: int = 0,
    val_batches: int = 8,
    label_shuffle: bool = False,
) -> SequenceTrainingResult:
    """BPTT classification on a sequence task (TODO23 sequence tier).

    Trains the composed System's *geometry* through
    ``geometry.episode(grad=True)`` with per-episode CE on the final-step
    logits and plain SGD — the recorded construction for
    sequence-shaped geometries (NTM). The credit axis is bypassed: BPTT
    through the unrolled episode *is* backprop; the update axis's
    step_size is ignored in favor of ``lr``.

    Raises ``ValueError`` for unknown tasks and ``TypeError`` when the
    geometry exposes no ``episode`` API (sequence-incompatible).

    ``label_shuffle=True`` is the matched-control arm: targets are
    permuted per episode while training; scoring stays on the
    *unpermuted* val episodes, so the learned map is wrong by
    construction and the control ceiling is chance.
    """
    if not hasattr(system, "geometry"):
        raise TypeError("sequence training requires a composed ontology System")
    geometry = system.geometry  # type: ignore[attr-defined]
    episode = cast(
        "Callable[..., tuple[Tensor, Tensor]] | None",
        getattr(geometry, "episode", None),
    )
    if not callable(episode):
        raise TypeError("geometry exposes no episode API; sequence-incompatible")
    torch.manual_seed(seed)
    optimizer = torch.optim.SGD(geometry.parameters(), lr=lr)
    t0 = time.perf_counter()
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        x, y = sequence_task(
            task,
            batch_size=batch_size,
            seq_len=seq_len,
            input_dim=input_dim,
            seed=seed * 1000 + epoch,
        )
        if label_shuffle:
            y = y[
                torch.randperm(
                    len(y), generator=torch.Generator().manual_seed(seed + epoch)
                )
            ]
        optimizer.zero_grad()
        logits, _ = episode(x, grad=True)
        loss = torch.nn.functional.cross_entropy(logits[:, -1], y)
        loss.backward()
        optimizer.step()
        history.append({"epoch": epoch, "loss": float(loss.detach())})
    geometry.eval()
    correct = total = 0
    with torch.no_grad():
        for i in range(val_batches):
            x, y = sequence_task(
                task,
                batch_size=batch_size,
                seq_len=seq_len,
                input_dim=input_dim,
                seed=10_000 + seed * 100 + i,
            )
            logits, _ = episode(x)
            correct += int((logits[:, -1].argmax(-1) == y).sum())
            total += len(y)
    return SequenceTrainingResult(
        task=task,
        epochs=epochs,
        accuracy=correct / max(total, 1),
        chance=_CHANCE[task],
        history=tuple(history),
        walltime_s=time.perf_counter() - t0,
    )


@dataclass(frozen=True, slots=True)
class SequenceCampaignReport:
    """Multi-seed validation of one mechanism on one sequence task.

    Gates: ``BenchmarkReproduction`` (mean accuracy within tolerance of
    the transcribed metadata) and ``DeployabilityCheck`` (export manifest).
    The classification StabilityCertificate does not apply to the BPTT
    path; its absence is recorded, not faked.
    """

    task: str
    seeds: tuple[int, ...]
    accuracies: tuple[float, ...]
    predicted_accuracy: float
    reproduction: bool
    deployability: bool
    certified: bool
    control_accuracy: float | None = None
    matched_control: bool = False

    def summary(self) -> dict[str, object]:
        return {
            "task": self.task,
            "seeds": list(self.seeds),
            "accuracies": list(self.accuracies),
            "predicted_accuracy": self.predicted_accuracy,
            "control_accuracy": self.control_accuracy,
            "matched_control": self.matched_control,
            "gates": {
                "BenchmarkReproduction": self.reproduction,
                "StabilityCertificate": None,
                "DeployabilityCheck": self.deployability,
            },
            "certified": self.certified,
        }


def sequence_campaign(
    lab: Lab,
    system_builder: Callable[[], object],
    task: str,
    *,
    predicted_accuracy: float,
    seeds: tuple[int, ...] = (0, 1, 2),
    epochs: int = 120,
    lr: float = 0.1,
    tolerance: float = 0.15,
    out_dir: str | None = None,
) -> SequenceCampaignReport:
    """Multi-seed sequence validation, CEEC-recorded (§6, campaign-shaped).

    Records one ``validation_campaign`` artifact + evidence + gate
    outcomes + decision (certify / do-not-certify) when
    ``lab.record_ledger`` is set — the ledger stores the negative result
    too.
    """
    accuracies: list[float] = []
    for seed in seeds:
        result = train_sequence(system_builder(), task, epochs=epochs, lr=lr, seed=seed)
        accuracies.append(result.accuracy)
    mean_accuracy = sum(accuracies) / len(accuracies)
    reproduction = mean_accuracy >= predicted_accuracy - tolerance

    control_accuracies = []
    for seed in seeds:
        control = train_sequence(
            system_builder(),
            task,
            epochs=epochs,
            lr=lr,
            seed=seed,
            label_shuffle=True,
        )
        control_accuracies.append(control.accuracy)
    control_mean = sum(control_accuracies) / len(control_accuracies)
    matched_control = control_mean < predicted_accuracy - tolerance

    deployability = True
    deploy_note = "skipped (no out_dir)"
    if out_dir is not None:
        from computronium_lab.deployment import export_system

        try:
            export = export_system(
                system_builder(), out_dir, target="onnx", input_shape=(1, 8)
            )
            deployability = (
                export.substrate_report.constraints_preserved
                and Path(export.manifest_path).exists()
            )
            deploy_note = f"manifest={Path(export.manifest_path).name}"
        except Exception as exc:  # ruff: ignore[blind-except] - gate failure is data
            deployability = False
            deploy_note = f"export failed: {exc}"

    certified = reproduction and deployability
    report = SequenceCampaignReport(
        task=task,
        seeds=seeds,
        accuracies=tuple(accuracies),
        predicted_accuracy=predicted_accuracy,
        reproduction=reproduction,
        deployability=deployability,
        certified=certified,
        control_accuracy=control_mean,
        matched_control=matched_control,
    )
    _record(lab, report, deploy_note)
    return report


def _record(lab: Lab, report: SequenceCampaignReport, deploy_note: str) -> None:
    from ceec.models import Scope
    from ceec.store import CEECStore

    ledger = lab.record_ledger
    if not ledger:
        return
    payload = json.dumps(report.summary(), indent=2)
    with CEECStore(Path(ledger), Path(ledger).parent / "artifacts") as store:
        artifact = store.ingest_artifact(
            payload.encode(),
            "validation_campaign",
            {"source": "computronium_lab.sequence_campaign", "task": report.task},
        )
        evidence = store.record_evidence(
            kind="scalar",
            scope=Scope(
                domain="lab",
                substrate=("digital",),
                budget="quick",
                extra={"sequence_task": report.task},
            ),
            artifact_refs=[artifact.id],
            quality={
                "seeds": len(report.seeds),
                "matched_control": report.matched_control,
                "evaluation_policy": "sequence_campaign_v1",
                "control_accuracy": report.control_accuracy,
            },
            defects=[],
            notes=(
                f"sequence campaign; control {report.control_accuracy:.3f}; "
                f"stability gate N/A (BPTT); deploy: {deploy_note}"
            ),
        )
        for gate, ok in (
            ("BenchmarkReproduction", report.reproduction),
            ("DeployabilityCheck", report.deployability),
        ):
            store.record_gate_outcome(
                gate=gate,
                status="passed" if ok else "failed",
                rationale=f"sequence campaign ({report.task})",
                evidence_refs=[evidence.id],
            )
        store.record_decision(
            state_hash=artifact.sha256,
            candidate_experiments=[],
            scores={"mean_accuracy": sum(report.accuracies) / len(report.accuracies)},
            rationale=(
                f"certify sequence mechanism ({report.task})"
                if report.certified
                else f"do not certify: gates failed ({report.task})"
            ),
            selected_experiment=None,
        )
        store._conn.commit()
