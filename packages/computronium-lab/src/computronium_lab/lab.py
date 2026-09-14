"""Lab — compose, train, compare, and report ontology coordinates."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, TypedDict

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
    from pathlib import Path

    from computronium_lab.adaptation import (
        AdaptationMode,
        AdaptationResult,
        TaskBoundary,
    )
    from computronium_lab.deployment import ExportResult
    from computronium_lab.research.continual import ContinualReport
    from computronium_lab.research.evolution import (
        EvolutionPlan,
        EvolutionReport,
        EvolutionSpec,
    )
    from computronium_lab.research.substrate import TransferReport
    from computronium_lab.sequential import SequenceTrainingResult
    from computronium_lab.state_prediction import (
        StatePredictionResult as StatePredictionResult,
    )
    from computronium_lab.state_prediction import (
        TransitionTask as StatePredictionTask,
    )
    from computronium_lab.synthesis.engine import ParetoOption, SynthesisResult

PSI_ONLY = "psi_only"


class _HardTaskParams(TypedDict):
    """Difficulty overrides for the flat_classification_hard generator."""

    scale: float
    noise: float


# flat_classification_hard operating point (TODO25 D.2): dims ride the
# registered spec defaults (64 x 8); the measured calibration sweep
# (scripts/probes/todo25_hard_task.json) pins the same scale/noise as the
# flat tier — hardness comes from dims/classes, which clears saturation at
# 20ep (top row 0.984, no row >= 0.995) while weak rules separate.
HARD_TASK_PARAMS: _HardTaskParams = {"scale": 1.2, "noise": 1.5}


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
    *,
    scale: float = 1.2,
    noise: float = 1.5,
) -> tuple[DataLoader[tuple[Tensor, ...]], DataLoader[tuple[Tensor, ...]]]:
    """Deterministic gaussian-blob classification task (quick mode).

    Calibrated difficulty (scale=1.2, noise=1.5): strong gradient-trained
    mechanisms land ~0.90 at 20 epochs while weaker credit rules separate
    below — see the difficulty-sweep note in the body. The
    ``flat_classification_hard`` corpus class (TODO25 D.2) passes harder
    ``scale``/``noise`` via ``HARD_TASK_PARAMS`` so 20 epochs no longer
    saturates.
    """
    gen = torch.Generator().manual_seed(seed)
    # (1.2, 1.5) is the calibrated difficulty operating point (2026-09-13
    # difficulty sweep, TODO23 §12): the old (2.0, 0.5) task saturated at
    # 1.0 for every gradient-trained mechanism, so accuracy metadata
    # stopped discriminating. At (1.2, 1.5) backprop lands ~0.90 @ 20ep
    # while weaker credit rules separate below it.
    x, y = gaussian_blobs(
        n, input_dim, num_classes, scale=scale, noise=noise, generator=gen
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

    def synthesize(
        self, spec: ProblemSpec, *, include_evolved: bool = False
    ) -> SynthesisResult:
        """Spec → best valid mechanism coordinate with provenance (T23.1.5).

        ``include_evolved`` (TODO24 T24.2.6) folds archived *measured*
        accuracies from the frontier archive into selection; off by
        default so TODO23 behavior is unchanged.
        """
        from computronium_lab.synthesis.engine import synthesize as _synthesize

        frontier = None
        if include_evolved:
            from computronium_lab.research.evolution import FrontierArchive

            frontier = FrontierArchive(spec).measured_accuracy()
        result = _synthesize(spec, campaigns_run=self._campaigns, frontier=frontier)
        if result.exploratory:
            self._record_exploratory(result, spec)
        return result

    def plan_evolution(
        self, spec: ProblemSpec, evolution: EvolutionSpec
    ) -> EvolutionPlan:
        """Dry-run evolution plan: genomes, checks, budgets. No training."""
        from computronium_lab.research.evolution import plan_evolution

        return plan_evolution(spec, evolution)

    def run_evolution(self, plan: EvolutionPlan) -> EvolutionReport:
        """Execute an evolution plan end-to-end (T24.2.3)."""
        from computronium_lab.research.evolution import run_evolution

        return run_evolution(self, plan)

    def benchmark_continual(
        self,
        mechanism: str = "temporal_psi_task_switcher",
        curriculum: str = "two_task_switch",
        modes: tuple[str, ...] = ("temporal", "role_split", "conflict_adaptive"),
        controls: tuple[str, ...] = (
            "frozen_no_psi",
            "theta_finetune_matched_compute",
        ),
        seeds: tuple[int, ...] = (0, 1, 2),
    ) -> ContinualReport:
        """ψ-mode benchmark against matched controls (T24.4.4)."""
        from computronium_lab.research.continual import benchmark_continual

        return benchmark_continual(
            self,
            mechanism=mechanism,
            curriculum=curriculum,
            modes=modes,
            controls=controls,
            seeds=seeds,
        )

    def benchmark_substrate_transfer(
        self,
        mechanism: str = "backprop_mlp",
        source_substrate: str = "digital",
        target_constraints: tuple[str, ...] = ("int8", "ternary", "memristive"),
        seeds: tuple[int, ...] = (0, 1, 2),
    ) -> TransferReport:
        """Deployment transfer robustness campaign (T24.5.1)."""
        from computronium_lab.research.substrate import benchmark_substrate_transfer

        return benchmark_substrate_transfer(
            self,
            mechanism=mechanism,
            source_substrate=source_substrate,
            target_constraints=target_constraints,
            seeds=seeds,
        )

    def _research_report_ledger(self, report: dict, path: str | None) -> None:
        import pathlib

        with self.ledger_session(role="main") as sess:
            markdown, data = sess.render()
        report["ledger"] = {"markdown": markdown, **data}
        if path is not None:
            out_dir = pathlib.Path(path)
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "ledger_report.md").write_text(markdown, encoding="utf-8")
            import json

            (out_dir / "ledger_report.json").write_text(
                json.dumps(data, indent=2, sort_keys=True, default=str),
                encoding="utf-8",
            )

    def ledger_session(self, *, role: str = "campaign"):
        """Session bound to ``record_ledger`` + the Computronium profile."""
        from ceec.profile import LedgerRole
        from ceec.session import ledger

        from computronium_lab.ceec_profile import COMPUTRONIUM_PROFILE

        if not self.record_ledger:
            raise ValueError("ledger_session requires record_ledger on Lab(...)")
        return ledger(self.record_ledger, COMPUTRONIUM_PROFILE, role=LedgerRole(role))

    def _record_exploratory(self, result: SynthesisResult, spec: ProblemSpec) -> None:
        """Opt-in CEEC artifact for an exploratory synthesis (T23.1.7)."""
        if not self.record_ledger:
            return
        with self.ledger_session(role="main") as sess:
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
            artifact = sess.artifact(
                payload.encode(),
                "exploratory_synthesis",
                {
                    "source": "computronium_lab.synthesize",
                    "mechanism": result.name,
                    "exploratory": True,
                },
            )
            sess.evidence(
                _lab_scope(spec),
                artifact_refs=[artifact.id],
                predicted_viability=result.predicted_viability,
                notes="exploratory synthesis (T23.1.7): campaign pending",
            )

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
        train_data: object | None = None,
    ) -> TrainingResult:
        """Train with opt-in guarantees; returns a TrainingResult (T23.2.1).

        ``train_data`` (TODO25 F1) supplies an explicit training loader,
        bypassing the default synthetic task — permuted controls, task
        streams, and any runner that already holds its loader pass it
        here instead of calling ``train_with_certificates`` directly.
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
        if train_data is not None:
            return train_with_certificates(
                system,
                train_data,
                device=self.device,
                seed=self.seed,
                epochs=epochs,
                batch_size=batch_size,
                spec=spec,
                options=opts,
                record_ledger=self.record_ledger,
            )
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

    def research_report(
        self,
        spec: ProblemSpec | str | None = None,
        *,
        tier: str = "quick",
        path: str | Path | None = None,
    ) -> dict[str, object]:
        """One call per practitioner question (TODO25 C.3 + D.3).

        Dry-run only: synthesis, an evolution plan, the corpus arm plan
        (trainable vs expected measurement blocks), and the ledger rollup.
        ``spec`` is a ``ProblemSpec`` or its ``key()`` string; ``tier`` is
        a lab budget tier. ``path`` writes the ledger report
        (``ledger_report.md`` + ``.json``) into that directory.
        """

        from computronium_lab.research.corpus import CLASS_BY_NAME
        from computronium_lab.research.evolution import (
            EvolutionBudget,
            EvolutionSpec,
            plan_evolution,
        )
        from computronium_lab.research.schema import BudgetTier
        from computronium_lab.synthesis.catalog import CATALOG

        resolved = self._spec_from_key(spec) if isinstance(spec, str) else spec
        tier_budget = {
            BudgetTier.SMOKE: EvolutionBudget.smoke,
            BudgetTier.QUICK: EvolutionBudget.quick,
            BudgetTier.CERTIFIED: EvolutionBudget.certified,
        }[BudgetTier(tier)]

        report: dict[str, object] = {"tier": tier}
        if resolved is not None:
            trainable = tuple(
                c.name for c in CATALOG if c.trainable_on_task(resolved.task)
            )
            blocked = ()
            if resolved.task in CLASS_BY_NAME:
                blocked = tuple(
                    c.name for c in CATALOG if not c.trainable_on_task(resolved.task)
                )
            synthesis = self.synthesize(resolved)
            evolution = EvolutionSpec(
                seed_candidates=trainable[:4] or ("backprop_mlp",),
                budget=tier_budget(),
                tier=BudgetTier(tier),
            )
            plan = plan_evolution(resolved, evolution)
            report.update({
                "spec_key": resolved.key(),
                "synthesis": {
                    "mechanism": synthesis.name,
                    "coordinate": synthesis.coordinate,
                    "predicted_viability": synthesis.predicted_viability,
                    "provenance": list(synthesis.provenance),
                },
                "evolution_plan": {
                    "seed_candidates": list(evolution.seed_candidates),
                    "genomes": [g.mechanism for g in plan.genomes],
                    "admission": [
                        {"mechanism": m, "admitted": ok, "reason": reason}
                        for m, ok, reason in plan.admission
                    ],
                    "expected_campaigns": plan.expected_campaigns,
                    "expected_epochs": plan.expected_epochs,
                },
                "corpus_arms": {
                    "problem_class": resolved.task,
                    "trainable": trainable,
                    "expected_blocks": blocked,
                    "dims": {
                        "input_dim": resolved.input_dim,
                        "num_classes": resolved.num_classes,
                    },
                },
            })

        if self.record_ledger:
            self._research_report_ledger(report, path)
        return report

    def _spec_from_key(self, key: str) -> ProblemSpec:
        """Rebuild a ProblemSpec from its ``key()`` string."""
        import re

        parts = key.split("/")
        if len(parts) != 7:
            raise ValueError(f"not a ProblemSpec key: {key!r}")
        task, dataset, substrate, precision, continual, local, dims = parts
        cont = re.fullmatch(r"continual=(\w+)", continual)
        loc = re.fullmatch(r"local=(\w+)", local)
        dim = re.fullmatch(r"dims=(\d+)x(\d+)", dims)
        if not (cont and loc and dim):
            raise ValueError(f"not a ProblemSpec key: {key!r}")
        return ProblemSpec(
            task=task,
            dataset=dataset,
            constraints=Constraints(
                substrate=substrate,
                precision=precision,
                continual=cont.group(1) == "True",
                local_credit=loc.group(1) == "True",
            ),
            input_dim=int(dim.group(1)),
            num_classes=int(dim.group(2)),
        )

    def _record_ceec(self, results: list[ComparisonResult]) -> None:
        """Opt-in CEEC-Core evidence recording for a comparison run."""
        if not self.record_ledger:
            return
        with self.ledger_session(role="main") as sess:
            artifact = sess.artifact(
                json_summary(results).encode(),
                "lab_comparison",
                {"source": "computronium_lab.compare", "status": "ok"},
            )
            sess.evidence(
                _lab_scope(None),
                artifact_refs=[artifact.id],
                seeds=1,
                matched_control=False,
                notes="computronium-lab compare summary",
            )


def json_summary(results: list[ComparisonResult]) -> str:
    from computronium_lab.report import result_json

    return result_json(results)


def _lab_scope(spec: ProblemSpec | None):
    from ceec.models import Scope

    substrate = spec.constraints.substrate if spec is not None else "digital"
    return Scope.of(domain="lab", substrate=substrate, budget="quick")
