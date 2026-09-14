"""State-prediction task tier (TODO23 §12): grid→grid regression.

The NCA problem class is state prediction (recorded verdict, TODO23
§12): ``NcaGeometry.forward`` is one CA ``step`` over ``(B, C, H, W)``
states, so the honest tier is a grid→grid MSE task, not classification.

Synthetic task (§11-compliant, nothing invented): hidden-teacher
transition prediction. A fixed random NCA (teacher, deterministic per
seed, full mask) defines the one-step map; the student NCA trains by
direct autograd MSE through ``geometry.forward`` — the credit axis is
bypassed because one-step MSE through the geometry IS backprop (the
same honest framing as ``sequential.train_sequence``).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

import torch
import torch.nn.functional as F  # noqa: N812
from torch import Tensor

from computronium import GeometryConfig, NcaGeometry
from computronium.ontology.geometry import geometry_from_config

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium_lab.lab import Lab

__all__ = [
    "StatePredictionCampaignReport",
    "StatePredictionResult",
    "grid_transition_task",
    "state_prediction_campaign",
    "train_state_prediction",
]


@dataclass(frozen=True, slots=True)
class TransitionTask:
    """One hidden-teacher transition dataset with a held-out val split."""

    train_states: Tensor
    train_next: Tensor
    val_states: Tensor
    val_next: Tensor
    channels: int


def _teacher(seed: int, grid: int, channels: int) -> NcaGeometry:
    torch.manual_seed(seed)
    geometry = geometry_from_config(
        GeometryConfig.nca(channels=channels, grid_hw=(grid, grid), label_channels=0)
    )
    for param in geometry.parameters():  # type: ignore[attr-defined]
        param.requires_grad_(False)
    return cast("NcaGeometry", geometry)


def _sample(
    teacher: NcaGeometry,
    seed: int,
    grid: int,
    channels: int,
    batch_size: int,
    steps: int,
) -> tuple[Tensor, Tensor]:
    gen = torch.Generator().manual_seed(seed)
    ids = torch.randint(0, channels, (batch_size, grid, grid), generator=gen)
    states = F.one_hot(ids, channels).permute(0, 3, 1, 2).float()
    with torch.no_grad():
        nxt = teacher.rollout(states, steps)
    return states, nxt


def grid_transition_task(
    seed: int,
    *,
    grid: int = 10,
    channels: int = 4,
    steps: int = 3,
    n_train: int = 256,
    n_val: int = 64,
) -> TransitionTask:
    """Hidden-teacher rollout pairs (states, teacher.rollout(states, steps)).

    The teacher rule is fixed per ``seed`` (full mask inside ``step`` —
    the deterministic per-step map); inputs are one-hot channel grids.
    ``steps`` must exceed 1: the one-step map degenerates to identity
    (small tanh deltas, next≈states — measured: trained AND permuted
    control both at cell_acc 1.0). Deterministic per seed.
    """
    teacher = _teacher(seed, grid, channels)
    train_states, train_next = _sample(teacher, seed, grid, channels, n_train, steps)
    val_states, val_next = _sample(teacher, seed + 7777, grid, channels, n_val, steps)
    return TransitionTask(
        train_states=train_states,
        train_next=train_next,
        val_states=val_states,
        val_next=val_next,
        channels=channels,
    )


@dataclass(frozen=True, slots=True)
class StatePredictionResult:
    """One state-prediction training run on a composed NCA System."""

    epochs: int
    mse: float
    cell_accuracy: float
    chance: float
    history: tuple[dict[str, float], ...]
    walltime_s: float


def train_state_prediction(  # noqa: PLR0913 - flat state-prediction knobs
    system: object,
    task: TransitionTask,
    *,
    epochs: int = 300,
    lr: float = 0.02,
    batch_size: int = 32,
    steps: int = 3,
    seed: int = 0,
    label_shuffle: bool = False,
) -> StatePredictionResult:
    """Direct-autograd MSE training on the state-prediction tier.

    The credit axis is bypassed: BPTT through
    ``geometry.rollout(grad=True)`` with rollout-target MSE IS backprop
    (the same honest framing as ``sequential.train_sequence``); the
    update axis's step_size is ignored in favor of ``lr``. Raises
    ``TypeError`` for geometries that are not CA grids (forward must
    accept ``(B, C, H, W)`` states and return the same shape).

    ``label_shuffle=True`` is the matched-control arm: train targets are
    permuted across samples (wrong map by construction), scoring stays
    on the unpermuted val split.
    """
    if not hasattr(system, "geometry"):
        raise TypeError("state prediction requires a composed ontology System")
    geometry = system.geometry  # type: ignore[attr-defined]
    if not isinstance(geometry, NcaGeometry):
        raise TypeError(
            "state-prediction training requires an NCA geometry "
            "(forward over (B, C, H, W) state grids)"
        )
    torch.manual_seed(seed)
    optimizer = torch.optim.Adam(geometry.parameters(), lr=lr)
    train_x, train_y = task.train_states, task.train_next
    if label_shuffle:
        perm = torch.randperm(
            len(train_y), generator=torch.Generator().manual_seed(seed + 99)
        )
        train_y = train_y[perm].clone()
    history: list[dict[str, float]] = []
    t0 = time.perf_counter()
    for epoch in range(epochs):
        order = torch.randperm(
            len(train_x), generator=torch.Generator().manual_seed(seed * 1000 + epoch)
        )
        epoch_loss = 0.0
        n_batches = 0
        for start in range(0, len(order), batch_size):
            idx = order[start : start + batch_size]
            optimizer.zero_grad()
            pred = geometry.rollout(train_x[idx], steps, grad=True)
            loss = F.mse_loss(pred, train_y[idx])
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.detach())
            n_batches += 1
        history.append({"epoch": epoch, "loss": epoch_loss / max(n_batches, 1)})
    geometry.eval()
    with torch.no_grad():
        pred = geometry.rollout(task.val_states, steps)
        mse = float(F.mse_loss(pred, task.val_next))
        cell_acc = float((pred.argmax(1) == task.val_next.argmax(1)).float().mean())
    return StatePredictionResult(
        epochs=epochs,
        mse=mse,
        cell_accuracy=cell_acc,
        chance=1.0 / task.channels,
        history=tuple(history),
        walltime_s=time.perf_counter() - t0,
    )


@dataclass(frozen=True, slots=True)
class StatePredictionCampaignReport:
    """Multi-seed validation of one NCA mechanism on the state tier.

    Gates: ``BenchmarkReproduction`` (mean val cell-accuracy within
    tolerance of the catalog metadata), ``StabilityCertificate`` absent
    by construction is recorded as None (the direct-autograd path bypasses
    the classification guard convention), and ``DeployabilityCheck``
    (export manifest).
    """

    seeds: tuple[int, ...]
    accuracies: tuple[float, ...]
    mse: tuple[float, ...]
    predicted_accuracy: float
    reproduction: bool
    deployability: bool
    certified: bool
    control_accuracy: float | None = None
    matched_control: bool = False

    def summary(self) -> dict[str, object]:
        return {
            "task": "grid_transition",
            "seeds": list(self.seeds),
            "accuracies": list(self.accuracies),
            "mse": list(self.mse),
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


def state_prediction_campaign(
    lab: Lab,
    system_builder: Callable[[], object],
    *,
    predicted_accuracy: float,
    seeds: tuple[int, ...] = (0, 1, 2),
    epochs: int = 300,
    lr: float = 0.02,
    tolerance: float = 0.15,
    out_dir: str | None = None,
) -> StatePredictionCampaignReport:
    """Multi-seed state-prediction validation, CEEC-recorded (§6).

    Records one ``validation_campaign`` artifact + evidence + gate
    outcomes + decision when ``lab.record_ledger`` is set; the negative
    result is stored too.
    """
    accuracies: list[float] = []
    mses: list[float] = []
    for seed in seeds:
        task = grid_transition_task(seed)
        result = train_state_prediction(
            system_builder(), task, epochs=epochs, lr=lr, seed=seed
        )
        accuracies.append(result.cell_accuracy)
        mses.append(result.mse)
    mean_accuracy = sum(accuracies) / len(accuracies)
    reproduction = mean_accuracy >= predicted_accuracy - tolerance

    control_accuracies = []
    for seed in seeds:
        control = train_state_prediction(
            system_builder(),
            grid_transition_task(seed),
            epochs=epochs,
            lr=lr,
            seed=seed,
            label_shuffle=True,
        )
        control_accuracies.append(control.cell_accuracy)
    control_mean = sum(control_accuracies) / len(control_accuracies)
    matched_control = control_mean < predicted_accuracy - tolerance

    deployability = True
    deploy_note = "skipped (no out_dir)"
    if out_dir is not None:
        from computronium_lab.deployment import export_system

        try:
            export = export_system(
                system_builder(), out_dir, target="onnx", input_shape=(1, 4, 10, 10)
            )
            deployability = (
                export.substrate_report.constraints_preserved
                and Path(export.manifest_path).exists()
            )
            deploy_note = f"manifest={Path(export.manifest_path).name}"
        except Exception as exc:  # noqa: BLE001 - gate failure is data
            deployability = False
            deploy_note = f"export failed: {exc}"

    certified = reproduction and deployability
    report = StatePredictionCampaignReport(
        seeds=seeds,
        accuracies=tuple(accuracies),
        mse=tuple(mses),
        predicted_accuracy=predicted_accuracy,
        reproduction=reproduction,
        deployability=deployability,
        certified=certified,
        control_accuracy=control_mean,
        matched_control=matched_control,
    )
    _record(lab, report, deploy_note)
    return report


def _record(lab: Lab, report: StatePredictionCampaignReport, deploy_note: str) -> None:
    from ceec.models import Scope
    from ceec.store import CEECStore

    ledger = lab.record_ledger
    if not ledger:
        return
    payload = json.dumps(report.summary(), indent=2)
    db = Path(str(ledger))
    with CEECStore(db, db.parent / "artifacts") as store:
        artifact = store.ingest_artifact(
            payload.encode(),
            "validation_campaign",
            {
                "source": "computronium_lab.state_prediction",
                "task": "grid_transition",
            },
        )
        evidence = store.record_evidence(
            kind="scalar",
            scope=Scope.of(domain="lab", substrate=("digital",), budget="quick"),
            artifact_refs=[artifact.id],
            quality={
                "seeds": len(report.seeds),
                "matched_control": report.matched_control,
            },
            defects=[],
            notes=f"state-prediction campaign; deploy: {deploy_note}",
        )
        for gate, ok in (
            ("BenchmarkReproduction", report.reproduction),
            ("DeployabilityCheck", report.deployability),
        ):
            store.record_gate_outcome(
                gate=gate,
                status="passed" if ok else "failed",
                rationale="state-prediction tier campaign (grid_transition)",
                evidence_refs=[evidence.id],
            )
        store.record_decision(
            state_hash=artifact.sha256,
            candidate_experiments=[],
            scores={"mean_accuracy": sum(report.accuracies) / len(report.accuracies)},
            rationale=(
                "certify NCA state-prediction mechanism"
                if report.certified
                else "do not certify: gates failed"
            ),
            selected_experiment=None,
        )
        store._conn.commit()
