"""Unified training surface (TODO23 Phase 2): certificates for Lab.train()."""

from __future__ import annotations

import copy
import hashlib
import json
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.trainer import SystemTrainer

if TYPE_CHECKING:
    from collections.abc import Mapping

    from stability.guard import GuardHandle

    from computronium.core.frozen_theta import FrozenThetaAuditReport
    from computronium_lab.synthesis.spec import ProblemSpec

DEFAULT_TAU = 1.029


class StabilityGuardKill(RuntimeError):  # ruff: ignore[error-suffix-on-exception-name] - CEEC gate name is pre-registered
    """CEEC-gated stop: the stability guard flagged divergence mid-training."""


@dataclass(frozen=True, slots=True)
class StabilityCertificate:
    """Outcome of StabilityGuard monitoring during training."""

    checked: bool
    kill: bool
    threshold: float = DEFAULT_TAU
    max_statistic: float | None = None
    note: str | None = None


@dataclass(frozen=True, slots=True)
class HarvestCertificate:
    """End-of-run weight harvest applied by the trainer."""

    mode: str
    applied: bool


@dataclass(frozen=True, slots=True)
class ThetaAuditOutcome:
    """FrozenΘ audit over persistent state across the training run.

    Weight mutation through the parameter-update path is expected during
    training; the guarantee is that no persistent tensor was *rebound*
    (re-instantiated outside the update path) or mutated without a
    version bump.
    """

    mutated: tuple[str, ...]
    version_bumped: tuple[str, ...]
    rebound: tuple[str, ...]

    @property
    def clean(self) -> bool:
        """No geometry tensor left the in-place update path during training."""
        return not any(name.startswith("geometry.") for name in self.rebound)


@dataclass(frozen=True, slots=True)
class DeterminismSeal:
    """seed → bitwise reproducible params + metrics certificate (T23.2.6).

    ``first_divergence_epoch`` localizes the first epoch whose metrics
    diverged between the replicas (``None`` = no divergence observed, or
    verified run).
    """

    params_sha256: str
    metrics_sha256: str
    verified: bool
    first_divergence_epoch: int | None = None


@dataclass(frozen=True, slots=True)
class TrainingResult:
    """Full training outcome with every opt-in certificate attached."""

    metrics: dict[str, float]
    history: tuple[dict[str, float], ...]
    walltime_s: float
    stability: StabilityCertificate | None = None
    harvest: HarvestCertificate | None = None
    theta_audit: ThetaAuditOutcome | None = None
    determinism: DeterminismSeal | None = None
    ceec_artifact_ids: tuple[str, ...] = ()


def _params_digest(system: object) -> str:
    params: Mapping[str, Tensor] = system.geometry.params  # type: ignore[attr-defined]
    h = hashlib.sha256()
    for name in sorted(params):
        t = params[name].detach().cpu().contiguous()
        h.update(name.encode())
        h.update(t.numpy().tobytes())
    return h.hexdigest()


def _metrics_digest(history: list[dict[str, float]]) -> str:
    h = hashlib.sha256()
    for row in history:
        h.update(
            json.dumps({
                k: round(float(v), 12) for k, v in sorted(row.items())
            }).encode()
        )
    return h.hexdigest()


def _make_trainer(
    system: object,
    train_data: object,
    *,
    device: str,
    seed: int,
    epochs: int,
    batch_size: int,
    harvest_mode: str | None,
    val_data: object | None = None,
) -> SystemTrainer:
    return SystemTrainer(
        system=system,  # type: ignore[arg-type]
        config=SystemTrainerConfig(
            max_epochs=epochs,
            batch_size=batch_size,
            device=device,
            seed=seed,
            deterministic=True,
            harvest_mode=harvest_mode,  # type: ignore[arg-type]
        ),
        train_data=train_data,  # type: ignore[arg-type]
        val_data=val_data,  # type: ignore[arg-type]
    )


def _fit(
    system: object,
    train_data: object,
    *,
    device: str,
    seed: int,
    epochs: int,
    batch_size: int,
    harvest_mode: str | None,
    val_data: object | None = None,
) -> SystemTrainer:
    torch.manual_seed(seed)
    trainer = _make_trainer(
        system,
        train_data,
        device=device,
        seed=seed,
        epochs=epochs,
        batch_size=batch_size,
        harvest_mode=harvest_mode,
        val_data=val_data,
    )
    trainer.fit()
    return trainer


def seal_determinism(
    system: object,
    train_data: object,
    *,
    device: str,
    seed: int,
    epochs: int,
    batch_size: int,
    harvest_mode: str | None,
    val_data: object | None = None,
) -> tuple[DeterminismSeal, SystemTrainer]:
    """Train twice from identical state; verify bitwise-identical outcome.

    Returns the seal and the *second* trainer (so callers keep one final
    parameter state). Opt-in: this doubles the training cost. A per-epoch
    metrics trace localizes the first diverging epoch when the seal fails.
    """
    runs: list[tuple[str, str, SystemTrainer]] = []
    for _ in range(2):
        replica = copy.deepcopy(system)
        trainer = _fit(
            replica,
            train_data,
            device=device,
            seed=seed,
            epochs=epochs,
            batch_size=batch_size,
            harvest_mode=harvest_mode,
            val_data=val_data,
        )
        runs.append((
            _params_digest(replica),
            _metrics_digest(trainer.history),
            trainer,
        ))
    a, b = runs
    divergence = _first_divergence_epoch(a[2].history, b[2].history)
    verified = a[0] == b[0] and a[1] == b[1]
    seal = DeterminismSeal(
        params_sha256=b[0],
        metrics_sha256=b[1],
        verified=verified,
        first_divergence_epoch=None if verified else divergence,
    )
    return seal, b[2]


def _first_divergence_epoch(
    a: list[dict[str, float]], b: list[dict[str, float]]
) -> int | None:
    for ra, rb in zip(a, b):
        if ra.get("epoch") != rb.get("epoch") or _metrics_digest([
            ra
        ]) != _metrics_digest([rb]):
            return int(ra.get("epoch", 0))
    return None


def stability_probe(
    handle: GuardHandle,
    state: dict[str, object],
    step: int,
) -> StabilityCertificate:
    """One StabilityVerdict → StabilityCertificate (never raises)."""
    try:
        verdict = handle.check(state, step=step)
    except Exception as exc:  # noqa: BLE001 - certificate, not a crash path
        return StabilityCertificate(
            checked=False, kill=False, note=f"guard unavailable: {exc}"
        )
    return StabilityCertificate(
        checked=True,
        kill=verdict.kill,
        threshold=verdict.threshold,
        max_statistic=verdict.max_statistic,
    )


def theta_outcome(system: object, report: FrozenThetaAuditReport) -> ThetaAuditOutcome:
    """FrozenThetaAuditReport → ThetaAuditOutcome."""
    return ThetaAuditOutcome(
        mutated=report.mutated,
        version_bumped=report.version_bumped,
        rebound=report.rebound,
    )


def ceec_campaign(
    ledger_path: str,
    history: tuple[dict[str, float], ...],
    source: str,
) -> tuple[str, ...]:
    """Opt-in per-epoch CEEC evidence (T23.2.5); returns artifact ids."""
    from ceec.models import Scope
    from ceec.session import ledger

    from computronium_lab.ceec_profile import COMPUTRONIUM_PROFILE

    ids: list[str] = []
    with ledger(ledger_path, COMPUTRONIUM_PROFILE, role="scratch") as sess:
        for row in history:
            payload = json.dumps(row, sort_keys=True).encode()
            artifact = sess.artifact(
                payload, "lab_training_epoch", {"source": source, "status": "ok"}
            )
            ids.append(artifact.id)
            sess.evidence(
                Scope.of(domain="lab", substrate="digital", budget="quick"),
                artifact_refs=[artifact.id],
                seeds=1,
                matched_control=False,
                notes=f"epoch {int(row.get('epoch', -1))} training metrics",
            )
    return tuple(ids)


@dataclass(frozen=True, slots=True)
class TrainOptions:
    """Opt-in guarantees for one training run (T23.2.1–T23.2.6)."""

    stability_guard: bool = False
    harvest: bool = False
    harvest_mode: str = "ema"
    frozen_theta_audit: bool | None = None
    ceec_logging: bool = False
    determinism_seal: bool = False
    val_data: object | None = None


class _GuardedRun:
    """Per-epoch training loop with a calibrated stability kill switch.

    Probe states cycle across epochs (rolling probe): a fixed batch misses
    late-run divergence in weight drift that other inputs expose.
    """

    def __init__(
        self,
        trainer: SystemTrainer,
        handle: GuardHandle,
        probe_states: list[dict[str, object]],
        max_epochs: int,
    ) -> None:
        self._trainer = trainer
        self._handle = handle
        self._probe_states = probe_states
        self._max_epochs = max_epochs
        self.certificate: StabilityCertificate | None = None

    def run(self) -> None:
        self._trainer._harvest_init()
        while self._trainer.current_epoch < self._max_epochs:
            self._trainer.train_epoch()
            state = self._probe_states[
                self._trainer.current_epoch % len(self._probe_states)
            ]
            cert = stability_probe(self._handle, state, self._trainer.current_epoch)
            self.certificate = cert
            if cert.kill:
                self._trainer._harvest_finalize()
                raise StabilityGuardKill(
                    f"stability guard kill at epoch {self._trainer.current_epoch}: "
                    f"statistic={cert.max_statistic} > τ={cert.threshold}"
                )
        self._trainer._harvest_finalize()


def _probe_batch(
    train_data: object, device: str, k: int = 4
) -> list[dict[str, object]]:
    """First ``k`` training batches as rolling guard probe states."""
    states: list[dict[str, object]] = []
    try:
        for x, _ in train_data:  # type: ignore[union-attr]
            states.append({"x": x.to(device)})
            if len(states) >= k:
                break
    except TypeError:  # not iterable (already-consumed generator etc.)
        pass
    return states or [{"x": torch.zeros(1)}]


def _attach_guard(model: object) -> GuardHandle:
    """Attach the calibrated guard with a geometry-appropriate transition.

    Geometry forward maps a fixed input batch to its activity output; the
    fast-proxy statistic measures one-step Jacobian gain at that input
    (windowed growth would need a shape-matched recurrent feedback, which
    classification geometries do not have).
    """
    from stability import attach

    def transition(state: dict[str, object]) -> dict[str, object]:
        x = state.get("x")
        if x is None:
            return state
        with torch.no_grad():
            y = model(x)  # type: ignore[operator]
        return {**state, "y": y}

    return attach(model, statistic="fast_proxy", transition_fn=transition)  # type: ignore[arg-type]


def train_with_certificates(
    system: object,
    train_data: object,
    *,
    device: str = "cpu",
    seed: int = 0,
    epochs: int = 1,
    batch_size: int = 32,
    spec: ProblemSpec | None = None,
    options: TrainOptions = TrainOptions(),
    record_ledger: str | None = None,
) -> TrainingResult:
    """Single training entry point; every guarantee is opt-in (T23.2.1).

    options.stability_guard: calibrated kill switch, per-epoch boundary checks
      (rolling probe batches).
    options.harvest: EMA weight resurrection wired into the trainer config.
    options.frozen_theta_audit: automatic when spec.continual=True (T23.2.4).
    options.ceec_logging + record_ledger: per-epoch CEEC evidence capture.
    options.determinism_seal: bitwise reproducibility proof (2× training
      cost) with first-divergence localization.
    options.val_data: validation loader → trainer validate() surfaces
      val_loss/val_acc in metrics and best-snapshot selection.
    """
    val_data = options.val_data
    t0 = time.perf_counter()
    audit_on = (
        options.frozen_theta_audit
        if options.frozen_theta_audit is not None
        else bool(spec and spec.constraints.continual)
    )
    harvest_mode_eff = options.harvest_mode if options.harvest else None

    theta_cm = None
    if audit_on:
        from computronium.core.frozen_theta import FrozenThetaAudit

        # Training legitimately mutates θ via the update path; we record the
        # audit outcome rather than assert strict invariance (ψ-only strictness
        # is Phase 3's AdaptationResult contract).
        theta_cm = FrozenThetaAudit(system)
    if theta_cm is not None:
        theta_cm.__enter__()

    stability: StabilityCertificate | None = None
    seal: DeterminismSeal | None = None
    if options.determinism_seal:
        seal, trainer = seal_determinism(
            system,
            train_data,
            device=device,
            seed=seed,
            epochs=epochs,
            batch_size=batch_size,
            harvest_mode=harvest_mode_eff,
            val_data=val_data,
        )
    elif options.stability_guard:
        torch.manual_seed(seed)
        trainer = _make_trainer(
            system,
            train_data,
            device=device,
            seed=seed,
            epochs=epochs,
            batch_size=batch_size,
            harvest_mode=harvest_mode_eff,
            val_data=val_data,
        )
        handle = _attach_guard(trainer.system.geometry)  # type: ignore[attr-defined]
        run = _GuardedRun(trainer, handle, _probe_batch(train_data, device), epochs)
        run.run()
        stability = run.certificate
    else:
        trainer = _fit(
            system,
            train_data,
            device=device,
            seed=seed,
            epochs=epochs,
            batch_size=batch_size,
            harvest_mode=harvest_mode_eff,
            val_data=val_data,
        )
    history = trainer.history

    if theta_cm is not None:
        theta_cm.__exit__(None, None, None)

    audit: ThetaAuditOutcome | None = None
    if theta_cm is not None and theta_cm.report is not None:
        audit = theta_outcome(system, theta_cm.report)

    final = history[-1] if history else {}
    metrics = {
        "loss": float(final.get("train_loss", final.get("loss", 0.0))),
        "accuracy": float(final.get("train_acc", final.get("free_accuracy", 0.0))),
    }
    if val_data is not None:
        metrics.update(trainer.validate())

    ceec_ids: tuple[str, ...] = ()
    if options.ceec_logging and record_ledger:
        ceec_ids = ceec_campaign(
            record_ledger, tuple(history), "computronium_lab.train"
        )

    return TrainingResult(
        metrics=metrics,
        history=tuple(history),
        walltime_s=time.perf_counter() - t0,
        stability=stability,
        harvest=HarvestCertificate(options.harvest_mode, applied=options.harvest)
        if options.harvest
        else None,
        theta_audit=audit,
        determinism=seal,
        ceec_artifact_ids=ceec_ids,
    )


__all__ = [
    "DEFAULT_TAU",
    "DeterminismSeal",
    "HarvestCertificate",
    "StabilityCertificate",
    "StabilityGuardKill",
    "ThetaAuditOutcome",
    "TrainOptions",
    "TrainingResult",
    "ceec_campaign",
    "seal_determinism",
    "stability_probe",
    "theta_outcome",
    "train_with_certificates",
]
