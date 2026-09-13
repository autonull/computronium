"""Lab — compose, train, compare, and report ontology coordinates."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

import torch
from torch import Tensor
from torch.utils.data import DataLoader, TensorDataset

from computronium.experiments.joint.tasks import gaussian_blobs
from computronium_lab.presets import PRESETS, build_system_preset
from computronium_lab.recipes import RECIPES, build_recipe
from computronium_lab.synthesis.spec import Constraints, ProblemSpec
from computronium_lab.training import (
    TrainingResult,
    TrainOptions,
    train_with_certificates,
)

if TYPE_CHECKING:
    from computronium_lab.adaptation import (
        AdaptationMode,
        AdaptationResult,
        TaskBoundary,
    )
    from computronium_lab.deployment import ExportResult
    from computronium_lab.sequential import SequenceTrainingResult
    from computronium_lab.state_prediction import (
        StatePredictionResult as StatePredictionResult,
    )
    from computronium_lab.state_prediction import (
        TransitionTask as StatePredictionTask,
    )
    from computronium_lab.synthesis.engine import ParetoOption, SynthesisResult

PSI_ONLY = "psi_only"


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
    """Deterministic gaussian-blob classification task (quick mode).

    Calibrated difficulty (scale=1.2, noise=1.5): strong gradient-trained
    mechanisms land ~0.90 at 20 epochs while weaker credit rules separate
    below — see the difficulty-sweep note in the body.
    """
    gen = torch.Generator().manual_seed(seed)
    # (1.2, 1.5) is the calibrated difficulty operating point (2026-09-13
    # difficulty sweep, TODO23 §12): the old (2.0, 0.5) task saturated at
    # 1.0 for every gradient-trained mechanism, so accuracy metadata
    # stopped discriminating. At (1.2, 1.5) backprop lands ~0.90 @ 20ep
    # while weaker credit rules separate below it.
    x, y = gaussian_blobs(
        n, input_dim, num_classes, scale=1.2, noise=1.5, generator=gen
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
        self._campaigns: dict[str, int] = {}

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

    def synthesize(self, spec: ProblemSpec) -> SynthesisResult:
        """Spec → best valid mechanism coordinate with provenance (T23.1.5)."""
        from computronium_lab.synthesis.engine import synthesize as _synthesize

        result = _synthesize(spec, campaigns_run=self._campaigns)
        if result.exploratory:
            self._record_exploratory(result, spec)
        return result

    def _record_exploratory(self, result: SynthesisResult, spec: ProblemSpec) -> None:
        """Opt-in CEEC artifact for an exploratory synthesis (T23.1.7)."""
        from pathlib import Path

        from ceec.models import Scope
        from ceec.store import CEECStore

        if not self.record_ledger:
            return
        db = Path(self.record_ledger)
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
        with CEECStore(db, db.parent / "artifacts") as store:
            artifact = store.ingest_artifact(
                payload.encode(),
                "exploratory_synthesis",
                {
                    "source": "computronium_lab.synthesize",
                    "mechanism": result.name,
                    "exploratory": True,
                },
            )
            store.record_evidence(
                kind="scalar",
                scope=Scope(
                    domain="lab",
                    substrate=(spec.constraints.substrate,),
                    budget="quick",
                ),
                artifact_refs=[artifact.id],
                quality={"predicted_viability": result.predicted_viability},
                defects=[],
                notes="exploratory synthesis (T23.1.7): campaign pending",
            )
            store._conn.commit()

    def explore(self, spec: ProblemSpec) -> list[ParetoOption]:
        """Pareto frontier of constraint-satisfying mechanisms (T23.1.6)."""
        from computronium_lab.synthesis.engine import explore as _explore

        return _explore(spec)

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
        *,
        spec: ProblemSpec | None = None,
        options: TrainOptions | None = None,
        val_data: object | None = None,
    ) -> TrainingResult:
        """Train with opt-in guarantees; returns a TrainingResult (T23.2.1).

        ``val_data`` (or ``TrainOptions.val_data``) wires a validation
        loader through to the trainer: per-epoch best-snapshot selection
        when harvest_mode="best_snapshot", and val_loss/val_acc in
        ``TrainingResult.metrics``.
        """
        if task != "synthetic":
            raise ValueError(
                f"task {task!r} not wired; Lab quick mode ships 'synthetic'"
            )
        opts = options or TrainOptions()
        if val_data is not None and opts.val_data is None:
            opts = replace(opts, val_data=val_data)
        torch.manual_seed(self.seed)
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

    def train_sequence(
        self,
        system: object,
        task: str = "last_symbol",
        *,
        epochs: int = 60,
        lr: float = 0.1,
        batch_size: int = 32,
        seq_len: int = 8,
        input_dim: int = 8,
        seed: int | None = None,
    ) -> SequenceTrainingResult:
        """BPTT classification on a sequence task (TODO23 sequence tier)."""
        from computronium_lab.sequential import train_sequence as _train

        return _train(
            system,
            task,
            epochs=epochs,
            lr=lr,
            batch_size=batch_size,
            seq_len=seq_len,
            input_dim=input_dim,
            seed=self.seed if seed is None else seed,
        )

    def train_state_prediction(
        self,
        system: object,
        task: StatePredictionTask | None = None,
        *,
        epochs: int = 300,
        lr: float = 0.02,
        batch_size: int = 32,
        steps: int = 3,
        seed: int | None = None,
    ) -> StatePredictionResult:
        """State-prediction training on the grid tier (TODO23 §12)."""
        from computronium_lab.state_prediction import (
            grid_transition_task,
        )
        from computronium_lab.state_prediction import (
            train_state_prediction as _train,
        )

        if task is None:
            task = grid_transition_task(self.seed if seed is None else seed)
        return _train(
            system,
            task,
            epochs=epochs,
            lr=lr,
            batch_size=batch_size,
            steps=steps,
            seed=self.seed if seed is None else seed,
        )

    def adapt(
        self,
        system: object,
        task_data: object,
        mode: AdaptationMode | str = PSI_ONLY,
        *,
        episodes: int = 10,
        boundary: TaskBoundary | None = None,
        stability_check: bool = False,
        psi_step: str = "final",
    ) -> AdaptationResult:
        """ψ-only continual adaptation on frozen θ (TODO23 Phase 3).

        ``psi_step="every_timestep"`` accumulates ψ statistics across
        sequence timesteps (see ``adaptation.adapt``).
        """
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
        )

    def export(
        self,
        system: object,
        out_dir: str = "exports",
        *,
        spec: ProblemSpec | None = None,
        target: str = "onnx",
        quantization: str | None = None,
        input_shape: tuple[int, ...] = (1, 32),
        sample_input: Tensor | None = None,
    ) -> ExportResult:
        """Compile → constrain → quantize → export with substrate report (T23.4)."""
        from computronium_lab.deployment import export_system

        return export_system(
            system,
            out_dir,
            constraints=spec.constraints if spec is not None else None,
            target=target,
            quantization=quantization,  # type: ignore[arg-type]
            input_shape=input_shape,
            sample_input=sample_input,
        )

    def serve(
        self,
        system: object,
        *,
        spec: ProblemSpec | None = None,
        host: str = "127.0.0.1",
        port: int = 8000,
        input_shape: tuple[int, ...] = (1, 32),
    ) -> None:
        """Run the FastAPI edge runtime against a composed system (T23.4.4)."""
        from computronium_lab.deployment import serve_system

        serve_system(
            system,
            constraints=spec.constraints if spec is not None else None,
            host=host,
            port=port,
            input_shape=input_shape,
        )

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
