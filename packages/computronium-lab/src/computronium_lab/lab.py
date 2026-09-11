"""Lab — compose, train, compare, and report ontology coordinates."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import torch
from torch import Tensor
from torch.utils.data import DataLoader, TensorDataset

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.trainer import SystemTrainer
from computronium_lab.presets import PRESETS, build_system_preset
from computronium_lab.recipes import RECIPES, build_recipe


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    """One preset's quick training outcome."""

    preset: str
    final_loss: float
    final_accuracy: float
    walltime_s: float
    history: list[dict[str, float]] = field(default_factory=list)


def synthetic_task(
    seed: int = 0,
    n: int = 256,
    input_dim: int = 32,
    num_classes: int = 4,
    batch_size: int = 32,
) -> tuple[DataLoader[tuple[Tensor, ...]], DataLoader[tuple[Tensor, ...]]]:
    """Deterministic gaussian-blob classification task (quick mode)."""
    gen = torch.Generator().manual_seed(seed)
    centers = torch.randn(num_classes, input_dim, generator=gen) * 2.0
    labels = torch.randint(0, num_classes, (n,), generator=gen)
    x = centers[labels] + torch.randn(n, input_dim, generator=gen) * 0.5
    y = labels
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

    def compose(self, preset: str, **kwargs: object) -> object:
        """One-line system composition from a registered preset."""
        entry = PRESETS.get(preset)
        if entry is None:
            raise ValueError(f"unknown preset {preset!r}; known: {sorted(PRESETS)}")
        if entry.kind == "mechanism" and entry.recipe_name:
            raise ValueError(
                f"preset {preset!r} is a mechanism recipe — use "
                f"lab.recipe({entry.recipe_name!r})"
            )
        merged = {**({"seed": self.seed} if self.seed else {}), **kwargs}
        torch.manual_seed(self.seed)
        return build_system_preset(preset, **merged)

    def train(
        self,
        system: object,
        task: str = "synthetic",
        epochs: int = 1,
        batch_size: int = 32,
    ) -> dict[str, float]:
        """Quick-train a composed system; returns final train metrics."""
        if task != "synthetic":
            raise ValueError(
                f"task {task!r} not wired; Lab quick mode ships 'synthetic'"
            )
        torch.manual_seed(self.seed)
        train_loader, _ = synthetic_task(seed=self.seed, batch_size=batch_size)
        trainer = SystemTrainer(
            system=system,  # type: ignore[arg-type]
            config=SystemTrainerConfig(
                max_epochs=epochs,
                batch_size=batch_size,
                device=self.device,
                seed=self.seed,
                deterministic=True,
            ),
            train_data=train_loader,
        )
        history = trainer.fit()
        final = history[-1] if history else {}
        return {
            "loss": float(final.get("train_loss", final.get("loss", 0.0))),
            "accuracy": float(final.get("train_acc", final.get("free_accuracy", 0.0))),
        }

    def compare(
        self,
        presets: list[str],
        task: str = "synthetic",
        epochs: int = 1,
        **kwargs: object,
    ) -> list[ComparisonResult]:
        """Compose + train each preset; keep results for report()."""
        results: list[ComparisonResult] = []
        for name in presets:
            system = self.compose(name, **kwargs)
            t0 = time.perf_counter()
            metrics = self.train(system, task=task, epochs=epochs)
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
        if self.record_ledger:
            self._record_ceec(results)
        return results

    def recipe(self, name: str, **kwargs: object) -> object:
        """Instantiate a validated mechanism recipe."""
        if name not in RECIPES:
            raise ValueError(f"unknown recipe {name!r}; known: {sorted(RECIPES)}")
        return build_recipe(name, **kwargs)

    def report(self, path: str) -> str:
        """Write a markdown report of the last compare() call."""
        if not self.last_results:
            raise ValueError("nothing to report; run compare() first")
        from computronium_lab.report import write_report

        return write_report(self.last_results, path)

    def _record_ceec(self, results: list[ComparisonResult]) -> None:
        """Opt-in CEEC-Core evidence recording for a comparison run."""
        from pathlib import Path

        from ceec.models import Scope
        from ceec.store import CEECStore

        if not self.record_ledger:
            return
        db = Path(self.record_ledger)
        with CEECStore(db, db.parent / "artifacts") as store:
            artifact = store.ingest_artifact(
                json_summary(results).encode(),
                "lab_comparison",
                {"source": "computronium_lab.compare", "status": "ok"},
            )
            store.record_evidence(
                kind="scalar",
                scope=Scope(
                    domain="lab",
                    substrate=("digital",),
                    budget="quick",
                ),
                artifact_refs=[artifact.id],
                quality={"seeds": 1, "matched_control": False},
                defects=[],
                notes="computronium-lab compare summary",
            )
            store._conn.commit()


def json_summary(results: list[ComparisonResult]) -> str:
    from computronium_lab.report import result_json

    return result_json(results)
