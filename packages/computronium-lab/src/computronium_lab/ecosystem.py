"""Ecosystem adapters (TODO23 Phase 5): HuggingFace + Lightning callbacks and
the quick-tier benchmark suite.

Both callbacks lazy-import their frameworks and degrade to a clear
RuntimeError, keeping ``computronium-lab`` installable without ecosystem
extras. The benchmark suite reuses ``Lab.compare`` — measured rows only,
no synthetic metadata (anti-probe-farm rule, TODO23 §11).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from computronium_lab.lab import Lab

__all__ = [
    "BenchmarkReport",
    "BenchmarkRow",
    "HuggingFaceCallback",
    "LightningStabilityCallback",
    "report_json",
    "run_benchmark",
]


class HuggingFaceCallback:
    """``transformers.TrainerCallback`` that records per-epoch loss history.

    The compat layer requires a ``system`` attribute on the wrapped model
    (``Trainer.model_wrapped.system``) only when ``stability_guard`` is
    enabled; plain loss tracking needs nothing extra.
    """

    def __init__(
        self,
        *,
        stability_guard: bool = False,
        evidence_path: str | None = None,
    ) -> None:
        try:
            from transformers import TrainerCallback
        except ModuleNotFoundError as exc:  # pragma: no cover - env-dependent
            raise RuntimeError(
                "HuggingFaceCallback requires transformers; install with "
                "'uv add transformers'"
            ) from exc
        self._base = TrainerCallback()
        self.stability_guard = stability_guard
        self.evidence_path = evidence_path
        self.history: list[dict[str, float]] = []
        self.t0 = 0.0

    def on_train_begin(
        self, args: object, state: object, control: object, **kw: object
    ) -> object:
        self.t0 = time.perf_counter()
        return control

    def on_epoch_end(
        self, args: object, state: object, control: object, **kw: object
    ) -> object:
        logs = kw.get("logs") or {}
        if not isinstance(logs, dict):
            logs = {}
        self.history.append({
            "loss": float(logs.get("loss", 0.0)),
            "epoch": float(getattr(state, "epoch", 0) or 0),
        })
        return control

    def on_train_end(
        self, args: object, state: object, control: object, **kw: object
    ) -> object:
        if self.evidence_path:
            Path(self.evidence_path).write_text(
                json.dumps(
                    {
                        "walltime_s": time.perf_counter() - self.t0,
                        "epochs": len(self.history),
                        "history": self.history,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        return control


class LightningStabilityCallback:
    """Lightning callback: calibrated stability guard over the composed system.

    Requires the ``LightningModule`` to expose a ``system`` attribute (the
    computronium System); probes the system's geometry each epoch with the
    fast-proxy statistic and raises :class:`StabilityGuardKill` on a kill
    verdict — same semantics as ``Lab.train(stability_guard=True)``.
    """

    def __init__(self, probe_batch: dict[str, object] | None = None) -> None:
        try:
            import lightning.pytorch as _pl  # type: ignore[import-not-found]

            del _pl
        except ModuleNotFoundError as exc:  # pragma: no cover - env-dependent
            raise RuntimeError(
                "LightningStabilityCallback requires lightning; install with "
                "'uv add lightning'"
            ) from exc
        self._probe_batch = probe_batch
        self.handle: object | None = None
        self._system: object | None = None

    def on_train_start(self, trainer: object, pl_module: object) -> None:
        from computronium_lab.training import _attach_guard

        system = getattr(pl_module, "system", None)
        if system is None or getattr(system, "geometry", None) is None:
            raise ValueError(
                "LightningStabilityCallback needs pl_module.system.geometry"
            )
        if self._probe_batch is None:
            loader = pl_module.train_dataloader()  # type: ignore[attr-defined]
            from computronium_lab.training import _probe_batch

            self._probe_batch = _probe_batch(loader, "cpu")
        self.handle = _attach_guard(system.geometry)
        self._system = system

    def on_train_epoch_end(self, trainer: object, pl_module: object) -> None:
        from computronium_lab.training import StabilityGuardKill as _Kill

        if self.handle is None or self._probe_batch is None:
            return
        verdict = self.handle.check_external(  # type: ignore[attr-defined]
            dict(self._probe_batch),
            lambda s: {**s, "y": self._forward(s)},
            step=int(getattr(trainer, "current_epoch", 0)),
        )
        if verdict.kill:
            raise _Kill(
                f"stability guard kill at epoch {getattr(trainer, 'current_epoch', '?')}: "
                f"statistic={verdict.max_statistic} > τ={verdict.threshold}"
            )

    def _forward(self, state: dict[str, object]) -> object:
        import torch

        if self._system is None:
            raise RuntimeError("on_train_start has not run; no system attached")
        with torch.no_grad():
            return self._system.geometry(state["x"])  # type: ignore[attr-defined]


@dataclass(frozen=True, slots=True)
class BenchmarkRow:
    """One measured preset row (quick-tier benchmark, T23.5.3)."""

    preset: str
    loss: float
    accuracy: float
    walltime_s: float


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    """Measured benchmark rows + non-dominated frontier over (accuracy↑, walltime↓)."""

    rows: tuple[BenchmarkRow, ...]
    frontier: tuple[str, ...]
    walltime_s: float
    history: list[dict[str, float]] = field(default_factory=list)


def run_benchmark(
    presets: list[str],
    *,
    epochs: int = 1,
    seed: int = 0,
    batch_size: int = 32,
    device: str = "cpu",
) -> BenchmarkReport:
    """Quick-tier benchmark: measured loss/accuracy/walltime per preset (T23.5.3).

    Every row is a real ``Lab.compare`` training run on the deterministic
    synthetic task; the frontier is non-dominated over (accuracy↑, walltime↓).
    """
    lab = Lab(device=device, seed=seed)
    t0 = time.perf_counter()
    results = lab.compare(presets, task="synthetic", epochs=epochs)
    walltime = time.perf_counter() - t0

    rows = tuple(
        BenchmarkRow(
            preset=r.preset,
            loss=r.final_loss,
            accuracy=r.final_accuracy,
            walltime_s=r.walltime_s,
        )
        for r in results
    )

    def dominates(a: BenchmarkRow, b: BenchmarkRow) -> bool:
        better_eq = a.accuracy >= b.accuracy and a.walltime_s <= b.walltime_s
        strictly = a.accuracy > b.accuracy or a.walltime_s < b.walltime_s
        return better_eq and strictly

    frontier = tuple(
        r.preset for r in rows if not any(dominates(w, r) for w in rows if w is not r)
    )
    return BenchmarkReport(
        rows=rows,
        frontier=frontier,
        walltime_s=walltime,
        history=[h for r in results for h in r.history],
    )


def report_json(report: BenchmarkReport, path: str) -> str:
    """Write the benchmark report as JSON; returns the payload."""
    payload = json.dumps(
        {
            "walltime_s": report.walltime_s,
            "frontier": list(report.frontier),
            "rows": [
                {
                    "preset": r.preset,
                    "loss": r.loss,
                    "accuracy": r.accuracy,
                    "walltime_s": r.walltime_s,
                }
                for r in report.rows
            ],
        },
        indent=2,
    )
    Path(path).write_text(payload, encoding="utf-8")
    return payload
