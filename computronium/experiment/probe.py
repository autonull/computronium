"""Probe submission and normalization (architecture §6.2, §6.4).

A **probe** is one ``(model, task, config, seed)`` training run. The layer's
:class:`ProbeDriver` is a thin adapter over the existing training path
(default :class:`CoreTrainerDriver`, which composes a learning rule's system
and trains it through :class:`~computronium.core.system_trainer.SystemTrainer`);
:func:`run_probe` is the single point where a probe's per-seed record is
normalized once into a :class:`ProbeResult`.

``run_verify`` (existing in ``cli/run.py``) already emits per-seed JSONL with
CI/effect-size metadata; this module consumes that record shape rather than
re-implementing a training loop.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

# Whether probes persist results to the knowledge layer (KnowledgeBase /
# FailureTracker) by default. Environment-controllable so tests can isolate.
_DEFAULT_RECORD = os.environ.get("COMPUTRONIUM_RECORD_RESULTS", "1") != "0"

__all__ = [
    "CoreTrainerDriver",
    "ProbeDriver",
    "ProbeResult",
    "config_key",
    "run_probe",
]

_EXCLUDED_CONFIG_KEYS = frozenset({
    "epochs",
    "batch_size",
    "tier",
    "is_verification",
    "verified_trial_id",
    "seed",
})


def config_key(config: dict[str, object]) -> str:
    """Return a content hash of a config for idempotence.

    Excludes run-control keys (epochs/seed/batch) so the same architecture
    config across two runs maps to the same key — the resume index matches on
    it. The key is order-independent.
    """
    canonical = {k: config[k] for k in config if k not in _EXCLUDED_CONFIG_KEYS}
    blob = json.dumps(canonical, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def _dominant_training_path(
    paths: object,
) -> str:
    """Return the most-frequent credit-assignment path observed, or ``""``.

    ``paths`` is the per-epoch ``training_paths`` dict the trainer records
    (route name → step count). The dominant route is the probe headline; the
    full map is preserved separately as ``training_paths``.
    """
    if not isinstance(paths, dict) or not paths:
        return ""
    return max(paths.items(), key=lambda kv: int(kv[1]))[0]


@dataclass(frozen=True, slots=True)
class ProbeResult:
    """Normalized per-probe metrics record (architecture §6.2)."""

    model: str
    task: str
    config: dict[str, object]
    config_key: str
    seed: int
    status: str  # "ok" | "error"
    final_acc: float = 0.0
    final_train_loss: float = 0.0
    epoch_time_s: float = 0.0
    param_count: int = 0
    forward_flops: int = 0
    backward_flops: int = 0
    peak_memory_mb: float = 0.0
    wall_time_s: float = 0.0
    training_path: str = ""
    error: str = ""

    def to_dict(self) -> dict[str, object]:
        """Serialize to a plain dict for JSONL output."""
        return field_to_dict(self)


def field_to_dict(result: ProbeResult) -> dict[str, object]:
    """Serialize a :class:`ProbeResult` to a JSON-compatible dict."""
    config = dict(result.config)
    return {
        "model": result.model,
        "task": result.task,
        "config": config,
        "config_key": result.config_key,
        "seed": result.seed,
        "status": result.status,
        "final_acc": result.final_acc,
        "final_train_loss": result.final_train_loss,
        "epoch_time_s": result.epoch_time_s,
        "param_count": result.param_count,
        "forward_flops": result.forward_flops,
        "backward_flops": result.backward_flops,
        "peak_memory_mb": result.peak_memory_mb,
        "wall_time_s": result.wall_time_s,
        "training_path": result.training_path,
        "error": result.error,
    }


@runtime_checkable
class ProbeDriver(Protocol):
    """Narrow adapter over the existing training path (architecture §6.4)."""

    def train(  # ruff: ignore[too-many-locals]
        self,
        *,
        model: str,
        task: str,
        config: dict[str, object],
        seed: int,
        epochs: int,
        device: str,
        propagator: str | None = None,
    ) -> dict[str, object]: ...


class CoreTrainerDriver:
    """Drives a probe through the System path (the existing training path).

    Compute settings (batch size, tracking toggles, the per-epoch time
    budget) come from the campaign's ``compute`` block and are threaded into
    every :class:`~computronium.core.system_trainer.SystemTrainerConfig` so a
    probe respects the operator's declared resource budget.

    The driver used to reach training through ``CoreTrainer``, removed in
    Sprint 7.6.10, so every call raised ``ImportError`` and the three sweep
    scripts that construct it had no working path. It now composes the named
    learning rule's system and trains it, which also removes the silent-BPTT
    hazard the old path carried: a rule system has exactly one credit
    assignment, and :func:`~computronium.core.system_trainer.EpochRecord`'s
    ``training_paths`` says which one actually ran.
    """

    def __init__(  # driver constructor captures all campaign compute settings at once  # ruff: ignore[too-many-arguments]
        self,
        *,
        num_workers: int = 0,
        batch_size: int = 64,
        track_energy: bool = False,
        track_flops: bool = True,
        track_memory: bool = True,
        batches_per_epoch: int | None = None,
        record_results: bool = _DEFAULT_RECORD,
        target_hardware: str | None = None,
        max_epoch_time: float = 0.0,
    ) -> None:
        self.num_workers = num_workers
        self.batch_size = batch_size
        self.track_energy = track_energy
        self.track_flops = track_flops
        self.track_memory = track_memory
        self.batches_per_epoch = batches_per_epoch
        self.record_results = record_results
        self.target_hardware = target_hardware
        self.max_epoch_time = max_epoch_time

    def train(  # ruff: ignore[too-many-locals]
        self,
        *,
        model: str,
        task: str,
        config: dict[str, object],
        seed: int,
        epochs: int,
        device: str,
        propagator: str | None = None,
    ) -> dict[str, object]:
        """Train one probe and return aggregated metrics.

        The arm is an MLP over the task's flattened input whose credit
        assignment is the named learning rule, so the sweep varies the rule
        and holds the geometry. ``propagator`` overrides the rule the model
        name implies, which is how a family is forced onto a rule its native
        arm would not otherwise use.

        Args:
            model: Zoo model name or rule name, per
                :func:`~computronium.core.rules.rule_for_name`.
            task: Task name understood by
                :func:`~computronium.domains.factory.create_task`.
            config: Sampled architecture config (``hidden_dim``, ``num_layers``,
                ``learning_rate``; anything else is reported as a phantom knob).
            seed: Master seed.
            epochs: Training epochs.
            device: Target device.
            propagator: Learning rule to force, when the model name's own rule
                is not the one under test.

        Returns:
            A metrics dict with ``final_acc``, ``epoch_time_s``, flops, memory,
            and the ``training_path`` the probe actually took.

        Raises:
            KeyError: The model or propagator names no known learning rule.
            RuntimeError: If training raises or returns no history.
        """
        from computronium.core.exceptions import NumericalInstabilityError
        from computronium.core.rules import rule_for_name, rule_system_from_config
        from computronium.core.system_trainer import (
            SystemTrainer,
            SystemTrainerConfig,
            TaskBatches,
            flat_input_dim,
        )
        from computronium.domains.factory import create_task
        from computronium.experiment.param_estimator import (
            estimate_param_count,
            phantom_knobs,
            resolve_native_model,
        )
        from computronium.utils import seed_everything

        seed_everything(seed, device)
        rule = rule_for_name(propagator or model)
        handle = create_task(
            task, device=device, quick_mode=False, num_workers=self.num_workers
        )
        input_dim = flat_input_dim(handle.input_dim, handle.name)
        system, phantom = rule_system_from_config(
            rule, input_dim, handle.output_dim, config, device=device
        )
        # Phantom-drift diagnosis: sampled knobs the arm could not consume,
        # from both namespaces -- the zoo model's own signature and the rule
        # system's. Surfaced by the sweep instead of silently ignored.
        with contextlib.suppress(KeyError, ValueError, TypeError):
            phantom = sorted(
                set(phantom)
                | set(
                    phantom_knobs(
                        resolve_native_model(model),
                        config,
                        input_dim=input_dim,
                        output_dim=handle.output_dim,
                        model_name=model,
                    )
                )
            )
        try:
            param_count = estimate_param_count(
                model, config, input_dim=input_dim, output_dim=handle.output_dim
            )
        except Exception:  # defensive: counting must never break a probe
            param_count = 0

        handle.setup()
        trainer_config = SystemTrainerConfig(
            max_epochs=epochs,
            batch_size=self.batch_size,
            val_batch_size=self.batch_size,
            device=device,
            track_energy=self.track_energy,
            track_flops=self.track_flops,
            track_memory=self.track_memory,
            seed=seed,
            max_epoch_time=self.max_epoch_time,
        )
        try:
            trainer = SystemTrainer(
                system=system,
                config=trainer_config,
                train_data=TaskBatches(
                    handle, "train", self.batch_size, self.batches_per_epoch
                ),
                val_data=TaskBatches(
                    handle, "val", self.batch_size, self.batches_per_epoch
                ),
            )
            history = trainer.fit()
        except NumericalInstabilityError as exc:
            self._record(
                model=model,
                task=task,
                config=config,
                status="error",
                extra={"error": str(exc), "defect": "nan_divergence"},
                seed=seed,
                device=device,
            )
            raise RuntimeError(f"probe {model}/{task} diverged: {exc}") from exc
        except Exception as exc:  # broad: a broken model must not kill the gate
            self._record(
                model=model,
                task=task,
                config=config,
                status="error",
                extra={"error": str(exc)},
                seed=seed,
                device=device,
            )
            raise RuntimeError(  # descriptive message is the public API
                f"probe {model}/{task} failed: {exc}"
            ) from exc
        if not history:
            self._record(
                model=model,
                task=task,
                config=config,
                status="error",
                extra={"error": "no history"},
                seed=seed,
                device=device,
            )
            raise RuntimeError(  # descriptive message is the public API
                f"probe {model}/{task} returned no history"
            )

        last = history[-1]
        cost = trainer.epoch_resources[-1] if trainer.epoch_resources else None
        total_time = sum(c.epoch_time_s for c in trainer.epoch_resources)
        paths = dict(cost.training_paths) if cost else {}
        accs = [float(m["train_acc"]) for m in history if m.get("train_acc")]
        half_idx = max(1, len(accs) // 2) if accs else 0
        unavailable = sorted(
            name
            for name in ("forward_flops", "backward_flops", "peak_memory_mb")
            if cost is None or getattr(cost, name) is None
        )
        metrics: dict[str, object] = {
            "final_acc": float(last.get("train_acc") or last.get("val_acc") or 0.0),
            "final_train_loss": float(last.get("train_loss") or 0.0),
            "epoch_time_s": total_time,
            "param_count": param_count,
            "forward_flops": int(cost.forward_flops or 0) if cost else 0,
            "backward_flops": int(cost.backward_flops or 0) if cost else 0,
            "peak_memory_mb": float(cost.peak_memory_mb or 0.0) if cost else 0.0,
            # peak_memory_mb is CUDA-only and flops need a settle model, so a
            # metric the trainer could not measure is listed here rather than
            # being indistinguishable from a measured zero.
            "resource_metrics_unavailable": unavailable,
            # peak_memory_mb is CUDA-only; wall_time_s is not populated on CPU,
            # so fall back to the summed epoch time so the parity contract's
            # `matched_by.reported: [wall_time_s]` is real.
            "wall_time_s": total_time,
            "best_epoch_acc": max(accs)
            if accs
            else float(last.get("train_acc") or 0.0),
            "acc_at_half": float(accs[half_idx - 1])
            if accs and half_idx
            else float(last.get("train_acc") or 0.0),
            "loss_epoch_0": float(history[0].get("train_loss") or 0.0),
            "loss_epoch_final": float(last.get("train_loss") or 0.0),
            # Self-diagnosis: the credit-assignment route this probe actually
            # used. A bio-family probe reporting "bptt" is a silent-fallback
            # defect surfaced without human audit; a rule system has no such
            # route, so the name is the rule that ran.
            "training_paths": paths,
            "training_path": _dominant_training_path(paths),
            # Epoch-time truncation: if any epoch was cut short by the
            # ``max_epoch_time`` budget, the run's resource metrics are over a
            # partial epoch -- not comparable to full-epoch runs. The sweep
            # must prune (flag as defect) such a run.
            "epoch_time_budget_stopped": any(
                c.budget_stopped for c in trainer.epoch_resources
            ),
            # Phantom-drift diagnosis: sampled tuning knobs this probe could
            # not deliver. Flagged by the sweep as a defect.
            "phantom_knobs": phantom,
            # Requested substrate facade. The System path composes its own
            # substrate and has no facade to swap, so this is reported as
            # requested rather than as applied.
            "target_hardware": self.target_hardware,
        }
        self._record(
            model=model,
            task=task,
            config=config,
            status="completed",
            metrics=metrics,
            seed=seed,
            device=device,
        )
        return metrics

    def _record(
        self,
        *,
        model: str,
        task: str,
        config: dict[str, object],
        status: str,
        metrics: dict[str, object] | None = None,
        extra: dict[str, object] | None = None,
        seed: int = 0,
        device: str = "cpu",
    ) -> None:
        """Persist a probe outcome to the knowledge layer (best-effort).

        Recording must never break a probe: a DB/embedding failure is logged
        and swallowed. Gated by ``record_results`` so tests can disable it.
        """
        if not self.record_results:
            return
        try:
            from computronium.experiment.result_sink import record_experiment_result

            record_experiment_result(
                model=model,
                task=task,
                config=config,
                metrics=metrics,
                status=status,
                seed=seed,
                device=device,
                extra=extra,
            )
        except Exception as exc:  # pragma: no cover  # best-effort persistence
            from computronium.core.logging import get_logger

            get_logger().error(
                "result_sink recording failed for %s/%s: %s", model, task, exc
            )


def run_probe(
    driver: ProbeDriver,
    *,
    model: str,
    task: str,
    config: dict[str, object],
    seed: int,
    epochs: int,
    device: str,
    param_count: int = 0,
    propagator: str | None = None,
) -> ProbeResult:
    """Run one probe and normalize the outcome into a :class:`ProbeResult`.

    This is the single normalization point for the layer: every probe —
    scheduled by the producer, executed by the driver — becomes a
    :class:`ProbeResult`. Parameter count comes from
    ``experiment.param_estimator`` (passed in by the scheduler).

    Args:
        driver: The :class:`ProbeDriver` to execute training.
        model: Registered model name.
        task: Registered task name.
        config: Architecture config.
        seed: Seed for this probe.
        epochs: Training epochs.
        device: Target device.
        param_count: Static parameter count (from the estimator).
        propagator: Registered learning-rule propagator for bio-rule probes.

    Returns:
        A normalized :class:`ProbeResult` (status ``"ok"`` or ``"error"``).
    """
    try:
        call_kwargs: dict[str, object] = {
            "model": model,
            "task": task,
            "config": config,
            "seed": seed,
            "epochs": epochs,
            "device": device,
        }
        # ``propagator`` is an optional learning-rule override: only forward it
        # when set, so drivers that represent the default (no-rule) probe path
        # do not need to declare a keyword they never use.
        if propagator is not None:
            call_kwargs["propagator"] = propagator
        metrics = driver.train(**call_kwargs)
        return ProbeResult(
            model=model,
            task=task,
            config=config,
            config_key=config_key(config),
            seed=seed,
            status="ok",
            final_acc=float(metrics.get("final_acc", 0.0)),
            final_train_loss=float(metrics.get("final_train_loss", 0.0)),
            epoch_time_s=float(metrics.get("epoch_time_s", 0.0)),
            param_count=param_count,
            forward_flops=int(metrics.get("forward_flops", 0)),
            backward_flops=int(metrics.get("backward_flops", 0)),
            peak_memory_mb=float(metrics.get("peak_memory_mb", 0.0)),
            wall_time_s=float(metrics.get("wall_time_s", 0.0)),
            training_path=str(metrics.get("training_path", "")),
        )
    except Exception as exc:  # broad: normalize any probe failure
        return ProbeResult(
            model=model,
            task=task,
            config=config,
            config_key=config_key(config),
            seed=seed,
            status="error",
            error=str(exc),
        )
