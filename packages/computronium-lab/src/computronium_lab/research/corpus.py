"""Certified Research Corpus v1 (TODO24 Phase 3): persistent problem
classes, measurement-protocol execution, statistics, and re-measurement.

Every class implements ``ProblemClassProtocol``: a deterministic task
generator, default metrics, an arm runner, and a matched control. The
``MeasurementRunner`` executes multi-seed, equal-compute, val-split
campaigns, records ``research_corpus_summary`` artifacts with vector
evidence and ``Derived`` statistics, appends measured points to the
frontier archive, and files unmeasurable rows as measurement blocks.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Protocol, cast, runtime_checkable

import torch

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from ceec.models import Scope
    from ceec.store import CEECStore
    from torch import Tensor
    from torch.utils.data import DataLoader

    from computronium_lab.lab import Lab
    from computronium_lab.synthesis.catalog import MechanismCandidate
    from computronium_lab.synthesis.spec import ProblemSpec

from computronium_lab.research.paths import results_dir, write_manifest
from computronium_lab.research.schema import (
    BudgetTier,
    MeasurementBlock,
    ProblemClassProtocol,
    StatisticalSummary,
)

__all__ = [
    "CLASS_BY_NAME",
    "CorpusReport",
    "MeasurementRunner",
    "problem_class_defaults",
    "register_problem_class",
    "remeasure_catalog",
]


@runtime_checkable
class _EvalSystem(Protocol):
    """Structural surface needed to score a trained system on a loader."""

    def eval(self) -> object: ...
    def __call__(self, x: Tensor) -> Tensor: ...


class _SystemWithGeometry(Protocol):
    """Structural surface for substrate transfer (geometry fork + export)."""

    geometry: torch.nn.Module


def _score_accuracy(system: object, loader: DataLoader) -> float:
    """Val accuracy for a composed system (eval + __call__ surface)."""
    if not isinstance(system, _EvalSystem):
        raise TypeError("composed system lacks eval/__call__")
    system.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in loader:
            total += len(y)
            correct += int((system(x).argmax(-1) == y).sum())
    return correct / total if total else 0.0


def _row(name: str) -> MechanismCandidate:
    from computronium_lab.synthesis.catalog import CATALOG

    for candidate in CATALOG:
        if candidate.name == name:
            return candidate
    raise ValueError(f"{name!r} is not cataloged")


class _FlatClassification:
    """Calibrated gaussian-blob quick tier (TODO23 reproduction 0.896 @ 20ep)."""

    name = "flat_classification"
    task = "flat_classification"
    dataset = "gaussian_blob"

    def __init__(self, spec: ProblemSpec, scratch: Path | None = None) -> None:
        self.spec = spec

    def generate_task(self, seed: int) -> object:
        from computronium_lab.lab import synthetic_task

        return synthetic_task(
            seed=seed,
            input_dim=self.spec.input_dim,
            num_classes=self.spec.num_classes,
        )

    def default_metrics(self) -> tuple[str, ...]:
        return ("accuracy",)

    def control_arm(self, arm: str) -> str | None:
        if arm.endswith("::permuted"):
            return None
        return f"{arm}::permuted"

    def run_arm(
        self, lab: Lab, arm: str, seed: int, *, epochs: int
    ) -> dict[str, float]:
        from computronium_lab.lab import synthetic_task
        from computronium_lab.training import StabilityGuardKill, TrainOptions

        mechanism, _, control = arm.partition("::")
        lab.seed = seed
        system = _row(mechanism).build(self.spec)
        train_loader, val_loader = synthetic_task(
            seed=seed,
            input_dim=self.spec.input_dim,
            num_classes=self.spec.num_classes,
        )
        if control == "permuted":
            from torch.utils.data import DataLoader, TensorDataset

            gen = torch.Generator().manual_seed(seed + 9999)
            dataset = train_loader.dataset
            if not isinstance(dataset, TensorDataset):
                raise TypeError("synthetic task dataset is not a TensorDataset")
            x, y = dataset.tensors
            permuted = DataLoader(
                TensorDataset(x, y[torch.randperm(len(y), generator=gen)].clone()),
                batch_size=train_loader.batch_size or 32,
            )
            lab.train(
                system,
                epochs=epochs,
                spec=self.spec,
                train_data=permuted,
            )
            return {"accuracy": _score_accuracy(system, val_loader)}
        try:
            result = lab.train(
                system,
                task="synthetic",
                epochs=epochs,
                spec=self.spec,
                options=TrainOptions(stability_guard=True),
                val_data=val_loader,
            )
        except StabilityGuardKill:
            return {"accuracy": 0.0}
        metrics = result.metrics
        return {"accuracy": float(metrics.get("val_acc", metrics.get("accuracy", 0.0)))}


class _FlatClassificationHard:
    """Non-saturating flat variant (TODO25 D.2): higher dims + stronger
    noise so 20 epochs does not saturate — rank-based hypothesis tests
    (H24.2) stay decisive where ``flat_classification`` censors."""

    name = "flat_classification_hard"
    task = "flat_classification_hard"
    dataset = "gaussian_blob_hard"

    def __init__(self, spec: ProblemSpec, scratch: Path | None = None) -> None:
        self.spec = spec

    def generate_task(self, seed: int) -> object:
        from computronium_lab.lab import HARD_TASK_PARAMS, synthetic_task

        return synthetic_task(
            seed=seed,
            input_dim=self.spec.input_dim,
            num_classes=self.spec.num_classes,
            **HARD_TASK_PARAMS,
        )

    def default_metrics(self) -> tuple[str, ...]:
        return ("accuracy",)

    def control_arm(self, arm: str) -> str | None:
        if arm.endswith("::permuted"):
            return None
        return f"{arm}::permuted"

    def run_arm(
        self, lab: Lab, arm: str, seed: int, *, epochs: int
    ) -> dict[str, float]:
        from computronium_lab.lab import HARD_TASK_PARAMS, synthetic_task
        from computronium_lab.training import StabilityGuardKill, TrainOptions

        mechanism, _, control = arm.partition("::")
        lab.seed = seed
        system = _row(mechanism).build(self.spec)
        train_loader, val_loader = synthetic_task(
            seed=seed,
            input_dim=self.spec.input_dim,
            num_classes=self.spec.num_classes,
            **HARD_TASK_PARAMS,
        )
        if control == "permuted":
            from torch.utils.data import DataLoader, TensorDataset

            gen = torch.Generator().manual_seed(seed + 9999)
            dataset = train_loader.dataset
            if not isinstance(dataset, TensorDataset):
                raise TypeError("synthetic task dataset is not a TensorDataset")
            x, y = dataset.tensors
            permuted = DataLoader(
                TensorDataset(x, y[torch.randperm(len(y), generator=gen)].clone()),
                batch_size=train_loader.batch_size or 32,
            )
            lab.train(
                system,
                epochs=epochs,
                spec=self.spec,
                train_data=permuted,
            )
            return {"accuracy": _score_accuracy(system, val_loader)}
        try:
            result = lab.train(
                system,
                task="synthetic",
                epochs=epochs,
                spec=self.spec,
                options=TrainOptions(stability_guard=True),
                val_data=val_loader,
                train_data=train_loader,
            )
        except StabilityGuardKill:
            return {"accuracy": 0.0}
        metrics = result.metrics
        return {"accuracy": float(metrics.get("val_acc", metrics.get("accuracy", 0.0)))}


class _SequenceClass:
    """NTM sequence tier; one class per recorded Z3 task."""

    def __init__(
        self,
        spec: ProblemSpec,
        scratch: Path | None = None,
        *,
        seq_task: str = "last_symbol",
    ) -> None:
        self.spec = spec
        self.seq_task = seq_task

    @property
    def name(self) -> str:
        return f"sequence_{self.seq_task}"

    @property
    def task(self) -> str:
        return f"sequence_{self.seq_task}"

    @property
    def dataset(self) -> str:
        return "synthetic_sequences"

    def generate_task(self, seed: int) -> object:
        from computronium_lab.sequential import sequence_task

        return sequence_task(self.seq_task, seed=seed)

    def default_metrics(self) -> tuple[str, ...]:
        return ("accuracy",)

    def control_arm(self, arm: str) -> str | None:
        if arm.endswith("::shuffled"):
            return None
        return f"{arm}::shuffled"

    def run_arm(
        self, lab: Lab, arm: str, seed: int, *, epochs: int
    ) -> dict[str, float]:
        from computronium_lab.sequential import train_sequence

        mechanism, _, control = arm.partition("::")
        lab.seed = seed
        system = _row(mechanism).build(self.spec)
        result = train_sequence(
            system,
            self.seq_task,
            epochs=epochs,
            seed=seed,
            label_shuffle=(control == "shuffled"),
        )
        return {"accuracy": float(result.accuracy), "chance": float(result.chance)}


class _NcaStatePrediction:
    """K-step rollout task (avoids the one-step degeneracy)."""

    name = "nca_state_prediction"
    task = "nca_state_prediction"
    dataset = "grid_transitions"

    def __init__(self, spec: ProblemSpec, scratch: Path | None = None) -> None:
        self.spec = spec

    def generate_task(self, seed: int) -> object:
        from computronium_lab.state_prediction import grid_transition_task

        return grid_transition_task(seed)

    def default_metrics(self) -> tuple[str, ...]:
        return ("cell_accuracy",)

    def control_arm(self, arm: str) -> str | None:
        if arm.endswith("::shuffled"):
            return None
        return f"{arm}::shuffled"

    def run_arm(
        self, lab: Lab, arm: str, seed: int, *, epochs: int
    ) -> dict[str, float]:
        from dataclasses import replace

        from computronium_lab.state_prediction import TransitionTask

        mechanism, _, control = arm.partition("::")
        lab.seed = seed
        system = _row(mechanism).build(self.spec)
        task = self.generate_task(seed)
        if not isinstance(task, TransitionTask):
            raise TypeError("NCA task generator must return a TransitionTask")
        if control == "shuffled":
            gen = torch.Generator().manual_seed(seed + 9999)
            perm = torch.randperm(task.train_next.shape[0], generator=gen)
            task = replace(task, train_next=task.train_next[perm].clone())
        result = lab.train_state_prediction(system, task=task, epochs=epochs, seed=seed)
        return {
            "cell_accuracy": float(result.cell_accuracy),
            "mse": float(result.mse),
            "chance": float(result.chance),
        }


class _ContinualSwitch:
    """Synthetic task stream with a boundary (ψ modes vs controls)."""

    name = "continual_switch"
    task = "continual_switch"
    dataset = "two_task_stream"

    MODES: tuple[str, ...] = (
        "temporal",
        "role_split",
        "conflict_adaptive",
        "frozen_no_psi",
        "theta_finetune_matched_compute",
    )

    def __init__(
        self,
        spec: ProblemSpec,
        scratch: Path | None = None,
        *,
        mechanism: str = "backprop_mlp",
        stream_offset: int = 5000,
        threshold: float = 0.5,
    ) -> None:
        self.spec = spec
        self.mechanism = mechanism
        self.stream_offset = stream_offset
        self.threshold = threshold
        self.last_proof: dict[str, object] | None = None

    def generate_task(self, seed: int) -> object:
        from computronium_lab.lab import synthetic_task

        task_a = synthetic_task(
            seed=seed,
            input_dim=self.spec.input_dim,
            num_classes=self.spec.num_classes,
        )
        task_b = synthetic_task(
            seed=seed + self.stream_offset,
            input_dim=self.spec.input_dim,
            num_classes=self.spec.num_classes,
        )
        return (task_a, task_b)

    def default_metrics(self) -> tuple[str, ...]:
        return ("accuracy",)

    def control_arm(self, arm: str) -> str | None:
        if arm in {"frozen_no_psi", "theta_finetune_matched_compute"}:
            return None
        return "frozen_no_psi"

    def run_arm(
        self, lab: Lab, arm: str, seed: int, *, epochs: int
    ) -> dict[str, float]:
        from computronium_lab.adaptation import theta_digest
        from computronium_lab.training import StabilityGuardKill, TrainOptions

        lab.seed = seed
        system = _row(self.mechanism).build(self.spec)
        streams = self.generate_task(seed)
        if not (isinstance(streams, tuple) and len(streams) == 2):
            raise TypeError("continual stream must be a (task_a, task_b) pair")
        (train_a, _), (train_b, val_b) = streams
        try:
            lab.train(
                system,
                epochs=epochs,
                spec=self.spec,
                options=TrainOptions(stability_guard=True),
                train_data=train_a,
            )
        except StabilityGuardKill:
            self.last_proof = {"stability_kill": True}
            return {
                "accuracy": 0.0,
                "episodes": 0.0,
                "threshold_reached": 0.0,
                "theta_invariant": 0.0,
                "psi_updated": 0.0,
                "stability": 0.0,
            }
        digest_before = theta_digest(system)
        if arm == "frozen_no_psi":
            accuracy, episodes_used, reached, psi_changed = self._probe(
                lab, system, val_b, arm
            )
            invariant, psi_updated, audit_note = True, False, None
        elif arm == "theta_finetune_matched_compute":
            lab.train(
                system,
                epochs=epochs,
                spec=self.spec,
                train_data=train_b,
            )
            accuracy = _score_accuracy(system, val_b)
            episodes_used, reached = epochs, accuracy >= self.threshold
            invariant = theta_digest(system) == digest_before
            psi_updated, psi_changed, audit_note = False, False, None
        else:
            accuracy, episodes_used, reached, invariant, psi_updated, psi_changed = (
                self._adapt_tracked(lab, system, train_b, val_b, arm, epochs)
            )
            audit_note = self.last_proof.get("audit") if self.last_proof else None
        digest_after = theta_digest(system)
        if arm not in {"frozen_no_psi", "theta_finetune_matched_compute"}:
            invariant = digest_after == digest_before
        self.last_proof = {
            "theta_before": digest_before,
            "theta_after": digest_after,
            "invariant": invariant,
            "psi_changed": psi_changed,
            "audit": audit_note,
        }
        return {
            "accuracy": accuracy,
            "episodes": float(episodes_used),
            "threshold_reached": 1.0 if reached else 0.0,
            "theta_invariant": 1.0 if invariant else 0.0,
            "psi_updated": 1.0 if psi_updated else 0.0,
            "stability": 1.0,
        }

    def _probe(
        self, lab: Lab, system: object, val_b: object, arm: str
    ) -> tuple[float, int, bool, bool]:
        """Zero-episode probe: val accuracy under current ψ, no state change.

        The probe always runs in the ``temporal`` mode: with zero episodes
        no adaptation occurs whatever the mode, and ``temporal`` is a valid
        mode name (arm names such as ``frozen_no_psi`` are not modes).
        """
        probe = lab.adapt(system, val_b, mode="temporal", episodes=0)
        accuracy = float(
            probe.metrics.get("psi_accuracy", probe.metrics.get("accuracy", 0.0))
        )
        return accuracy, 0, accuracy >= self.threshold, False

    def _adapt_tracked(
        self,
        lab: Lab,
        system: object,
        train_b: object,
        val_b: object,
        arm: str,
        budget: int,
    ) -> tuple[float, int, bool, bool, bool, bool]:
        """Episode loop with val probes; returns accuracy, episodes used,
        threshold flag, digest invariance, ψ update flag, ψ change flag."""
        from computronium.core.frozen_theta import FrozenThetaAudit
        from computronium_lab.adaptation import theta_digest

        digest_before = theta_digest(system)
        first_sha: str | None = None
        last_sha: str | None = None
        accuracy, episodes_used, reached, psi_updated = 0.0, budget, False, False
        psi_state: dict[str, Tensor] | None = None
        with FrozenThetaAudit(system) as audit_ctx:
            for episode in range(1, budget + 1):
                result = lab.adapt(system, train_b, mode=arm, episodes=1, psi=psi_state)
                psi_state = result.psi
                psi_updated = psi_updated or bool(result.psi_updated)
                probe = lab.adapt(system, val_b, mode=arm, episodes=0, psi=psi_state)
                accuracy = float(
                    probe.metrics.get(
                        "psi_accuracy", probe.metrics.get("accuracy", 0.0)
                    )
                )
                if first_sha is None:
                    first_sha = probe.psi_sha
                last_sha = probe.psi_sha
                episodes_used = episode
                if accuracy >= self.threshold:
                    reached = True
                    break
        report = audit_ctx.report
        audit_note = report.summary() if report is not None else None
        psi_changed = first_sha is not None and first_sha != last_sha
        invariant = theta_digest(system) == digest_before
        self.last_proof = {"audit": audit_note}
        return accuracy, episodes_used, reached, invariant, psi_updated, psi_changed


class _SubstrateTransfer:
    """Digital-trained model evaluated under substrate constraints."""

    name = "substrate_transfer"
    task = "substrate_transfer"
    dataset = "gaussian_blob"

    TARGETS: tuple[str, ...] = ("digital", "int8", "ternary", "memristive")

    def __init__(
        self,
        spec: ProblemSpec,
        scratch: Path | None = None,
        *,
        mechanism: str = "backprop_mlp",
    ) -> None:
        self.spec = spec
        self.mechanism = mechanism
        self.scratch = scratch

    def generate_task(self, seed: int) -> object:
        from computronium_lab.lab import synthetic_task

        return synthetic_task(
            seed=seed,
            input_dim=self.spec.input_dim,
            num_classes=self.spec.num_classes,
        )

    def default_metrics(self) -> tuple[str, ...]:
        return ("accuracy",)

    def control_arm(self, arm: str) -> str | None:
        return None

    def run_arm(
        self, lab: Lab, arm: str, seed: int, *, epochs: int
    ) -> dict[str, float]:
        from computronium_lab.deployment import (
            compile_substrate,
            estimate_energy,
            substrate_report,
        )
        from computronium_lab.lab import synthetic_task
        from computronium_lab.synthesis.spec import Constraints

        lab.seed = seed
        system = cast("_SystemWithGeometry", _row(self.mechanism).build(self.spec))
        lab.train(system, task="synthetic", epochs=epochs, spec=self.spec)
        _, val_loader = synthetic_task(
            seed=seed,
            input_dim=self.spec.input_dim,
            num_classes=self.spec.num_classes,
        )
        sample = next(iter(val_loader))[0]
        if arm == "digital":
            return {
                "accuracy": _score_accuracy(system, val_loader),
                "fidelity": 0.0,
                "energy_j": estimate_energy(
                    system.geometry,
                    compile_substrate(self.spec.constraints),
                ).joules,
                "export_success": 1.0,
            }
        fork = copy.deepcopy(system)
        geometry = fork.geometry
        spec = compile_substrate(Constraints(substrate="memristive"))
        if arm in {"int8", "ternary"}:
            from computronium.deployment import (
                quantize_model_dynamic_int8,
                quantize_model_ternary_inplace,
            )

            constrained = (
                quantize_model_dynamic_int8(geometry)
                if arm == "int8"
                else quantize_model_ternary_inplace(geometry)
            )
            with torch.no_grad():
                baseline = geometry(sample)
                fidelity = float((baseline - constrained(sample)).abs().max())
        elif arm == "memristive":
            from computronium.ontology.substrate.spec import make_substrate
            from computronium_lab.deployment import apply_substrate_constraints

            apply_substrate_constraints(geometry, make_substrate(spec))
            fidelity = substrate_report(geometry, spec, sample).fidelity_max_abs_diff
        else:
            raise ValueError(f"unknown transfer target {arm!r}")
        return {
            "accuracy": _score_accuracy(fork, val_loader),
            "fidelity": fidelity,
            "energy_j": estimate_energy(geometry, spec).joules,
            "export_success": 1.0,
        }


def _sequence_class(seq_task: str) -> type[_SequenceClass]:
    return type(
        f"_Sequence{seq_task.title().replace('_', '')}",
        (_SequenceClass,),
        {
            "__init__": lambda self, spec, scratch=None: _SequenceClass.__init__(
                self, spec, scratch, seq_task=seq_task
            )
        },
    )


CLASS_BY_NAME: dict[str, Callable[..., ProblemClassProtocol]] = {
    "flat_classification": _FlatClassification,
    "flat_classification_hard": _FlatClassificationHard,
    "sequence_last_symbol": _sequence_class("last_symbol"),
    "sequence_threshold": _sequence_class("threshold"),
    "sequence_parity": _sequence_class("parity"),
    "nca_state_prediction": _NcaStatePrediction,
    "continual_switch": _ContinualSwitch,
    "substrate_transfer": _SubstrateTransfer,
}

_SPEC_DEFAULTS: dict[str, dict[str, object]] = {
    "flat_classification": {
        "task": "flat_classification",
        "dataset": "gaussian_blob",
    },
    "flat_classification_hard": {
        "task": "flat_classification_hard",
        "dataset": "gaussian_blob_hard",
        "input_dim": 64,
        "num_classes": 8,
    },
    "sequence_last_symbol": {
        "task": "sequence_last_symbol",
        "dataset": "synthetic_sequences",
        "input_dim": 8,
        "num_classes": 2,
    },
    "sequence_threshold": {
        "task": "sequence_threshold",
        "dataset": "synthetic_sequences",
        "input_dim": 8,
        "num_classes": 2,
    },
    "sequence_parity": {
        "task": "sequence_parity",
        "dataset": "synthetic_sequences",
        "input_dim": 8,
        "num_classes": 2,
    },
    "nca_state_prediction": {
        "task": "nca_state_prediction",
        "dataset": "grid_transitions",
    },
    "continual_switch": {
        "task": "continual_switch",
        "dataset": "two_task_stream",
    },
    "substrate_transfer": {
        "task": "substrate_transfer",
        "dataset": "gaussian_blob",
    },
}


def register_problem_class(
    name: str,
    factory: Callable[..., ProblemClassProtocol],
    *,
    task: str,
    dataset: str,
    input_dim: int | None = None,
    num_classes: int | None = None,
) -> None:
    """Plug a new problem class into the corpus (TODO24 §14).

    The factory must return a ``ProblemClassProtocol`` from a
    ``ProblemSpec`` (``factory(spec)``); ``task``/``dataset``/dims declare
    how ``MeasurementRunner`` builds that spec. No core evolution changes
    required; ``remeasure_catalog`` and the frontier archive consume the
    new class generically.
    """
    if name in CLASS_BY_NAME:
        raise ValueError(f"problem class {name!r} is already registered")
    CLASS_BY_NAME[name] = factory
    defaults: dict[str, object] = {"task": task, "dataset": dataset}
    if input_dim is not None:
        defaults["input_dim"] = input_dim
    if num_classes is not None:
        defaults["num_classes"] = num_classes
    _SPEC_DEFAULTS[name] = defaults


def problem_class_defaults(name: str) -> dict[str, object]:
    """Spec config for a registered problem class (task/dataset/dims).

    This is the public read side of ``register_problem_class``:
    ``MeasurementRunner`` builds the class's ``ProblemSpec`` from it.
    """
    return dict(_SPEC_DEFAULTS[name])


@dataclass(frozen=True, slots=True)
class ArmSummary:
    """Per-arm metrics, statistics, and control comparison."""

    arm: str
    metric_values: dict[str, tuple[float, ...]]
    summaries: dict[str, StatisticalSummary]
    control_values: dict[str, tuple[float, ...]]
    seeds: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CorpusReport:
    """Regenerable corpus result for one problem class."""

    spec_key: str
    problem_class: str
    tier: str
    run_id: str
    arms: tuple[ArmSummary, ...]
    blocks: tuple[MeasurementBlock, ...]
    manifest_paths: tuple[str, ...]
    ledger: dict[str, object]


@dataclass
class _CorpusState:
    lab: Lab
    problem_class: ProblemClassProtocol
    spec: ProblemSpec
    arms: tuple[str, ...]
    seeds: tuple[int, ...]
    epochs: int
    tier: BudgetTier
    run_id: str
    store: CEECStore | None
    scope: Scope | None
    values: dict[str, dict[str, list[float]]]
    controls: dict[str, dict[str, list[float]]]
    blocks: list[MeasurementBlock]
    manifests: list[str]


class MeasurementRunner:
    """Multi-seed, equal-compute, val-split, matched-control execution."""

    def __init__(self, lab: Lab, *, tier: BudgetTier = BudgetTier.QUICK) -> None:
        self.lab = lab
        self.tier = tier

    def run(
        self,
        problem_class: str,
        arms: Sequence[str],
        *,
        seeds: Sequence[int] = (0, 1, 2),
        epochs: int = 1,
        run_id: str | None = None,
    ) -> CorpusReport:

        if problem_class not in CLASS_BY_NAME:
            raise ValueError(f"unknown problem class {problem_class!r}")
        resolved_run_id = run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        dims = _dims_of(problem_class)
        spec = self.lab.specify(
            _task_of(problem_class),
            _dataset_of(problem_class),
            input_dim=dims.get("input_dim", 32),
            num_classes=dims.get("num_classes", 4),
        )
        instance = CLASS_BY_NAME[problem_class](spec)
        state = _CorpusState(
            lab=self.lab,
            problem_class=instance,
            spec=spec,
            arms=tuple(arms),
            seeds=tuple(seeds),
            epochs=epochs,
            tier=self.tier,
            run_id=resolved_run_id,
            store=_open_store(self.lab),
            scope=None,
            values={arm: {} for arm in arms},
            controls={},
            blocks=[],
            manifests=[],
        )
        if state.store is not None:
            from ceec.models import Scope

            state.scope = Scope(
                domain="research",
                substrate=(spec.constraints.substrate,),
                budget=self.tier.value,
                extra={"run_id": resolved_run_id, "problem_class": problem_class},
            )
        try:
            for arm in state.arms:
                self._run_arm_seeds(state, arm)
            self._write_manifests(state)
            self._record_ledger(state)
            self._append_frontier(state)
            return self._assemble(state)
        finally:
            if state.store is not None:
                state.store.commit()
                state.store.close()

    def _trainability_block(self, state: _CorpusState, arm: str) -> str | None:
        """Trainable_on consult (TODO25 D.1): resolve the arm's mechanism
        and return a block reason when the construction path has no
        training path for this problem class — before any build."""
        mechanism = arm.partition("::")[0]
        try:
            row = _row(mechanism)
        except ValueError:
            return None
        if state.problem_class.name in row.trainable_on:
            return None
        return (
            f"{mechanism} has no training path for {state.problem_class.name} "
            f"(trainable_on={sorted(row.trainable_on)})"
        )

    def _run_arm_seeds(self, state: _CorpusState, arm: str) -> None:
        blocked = self._trainability_block(state, arm)
        if blocked is not None:
            state.blocks.append(
                MeasurementBlock(
                    problem_class=state.problem_class.name,
                    mechanism=arm,
                    reason=blocked,
                    tier=state.tier.value,
                )
            )
            return
        for seed in state.seeds:
            try:
                metrics = state.problem_class.run_arm(
                    state.lab, arm, seed, epochs=state.epochs
                )
            except Exception as exc:
                state.blocks.append(
                    MeasurementBlock(
                        problem_class=state.problem_class.name,
                        mechanism=arm,
                        reason=f"arm failed at seed {seed}: {type(exc).__name__}",
                        tier=state.tier.value,
                        detail=str(exc)[:500],
                    )
                )
                continue
            for metric, value in metrics.items():
                state.values[arm].setdefault(metric, []).append(float(value))
        control = state.problem_class.control_arm(arm)
        if control is not None:
            for seed in state.seeds:
                try:
                    metrics = state.problem_class.run_arm(
                        state.lab, control, seed, epochs=state.epochs
                    )
                except Exception as exc:
                    state.blocks.append(
                        MeasurementBlock(
                            problem_class=state.problem_class.name,
                            mechanism=control,
                            reason=f"control failed at seed {seed}: {type(exc).__name__}",
                            tier=state.tier.value,
                            detail=str(exc)[:500],
                        )
                    )
                    continue
                for metric, value in metrics.items():
                    state.controls.setdefault(control, {}).setdefault(
                        metric, []
                    ).append(float(value))

    def _write_manifests(self, state: _CorpusState) -> None:
        for seed in state.seeds:
            run_dir = results_dir(
                state.problem_class.name, seed, timestamp=state.run_id
            )
            payload = {
                "problem_class": state.problem_class.name,
                "spec_key": state.spec.key(),
                "tier": state.tier.value,
                "run_id": state.run_id,
                "seed": seed,
                "epochs": state.epochs,
                "arms": {
                    arm: {
                        metric: values[state.seeds.index(seed)]
                        if seed in state.seeds and len(values) > state.seeds.index(seed)
                        else None
                        for metric, values in metrics.items()
                    }
                    for arm, metrics in state.values.items()
                },
            }
            state.manifests.append(str(write_manifest(run_dir, payload)))

    def _record_ledger(self, state: _CorpusState) -> None:

        if state.store is None or state.scope is None:
            return
        summary_payload = {
            "problem_class": state.problem_class.name,
            "spec_key": state.spec.key(),
            "tier": state.tier.value,
            "run_id": state.run_id,
            "arms": sorted(state.values),
            "blocks": len(state.blocks),
        }
        artifact = state.store.ingest_artifact(
            json.dumps(summary_payload, sort_keys=True).encode(),
            "research_corpus_summary",
            {"problem_class": state.problem_class.name, "run_id": state.run_id},
        )
        state.store.record_derived(
            type_="corpus_summary",
            operator="measurement_protocol_v1",
            inputs={"a": [artifact.id]},
            scope=state.scope,
            value=summary_payload,
        )

    def _append_frontier(self, state: _CorpusState) -> None:
        from computronium_lab.research.autopoiesis import (
            CandidateEvaluation,
            CoordinateGenome,
        )
        from computronium_lab.research.evolution import FrontierArchive

        archive = FrontierArchive(state.spec)
        evaluations = []
        for arm, metrics in state.values.items():
            mechanism = arm.split("::")[0]
            try:
                genome = CoordinateGenome.seed(mechanism, state.spec)
            except ValueError:
                continue
            accuracy = _first(metrics, ("accuracy", "cell_accuracy"))
            if accuracy is None:
                continue
            evaluations.append(
                CandidateEvaluation(
                    genome_digest=genome.digest,
                    mechanism=mechanism,
                    objectives={
                        "accuracy": accuracy,
                        "stability": 1.0,
                        "adaptation_speed": 0.0,
                        "latency": 0.0,
                        "memory": 0.0,
                    },
                    metric_sources={"accuracy": "corpus_protocol_v1"},
                    seeds=state.seeds,
                    per_seed_accuracy=tuple(
                        metrics.get("accuracy", metrics.get("cell_accuracy", []))
                    ),
                    reproduction=True,
                    stability=None,
                    certified=False,
                    gate_outcomes={
                        "BenchmarkReproduction": None,
                        "StabilityCertificate": None,
                        "DeployabilityCheck": None,
                    },
                )
            )
        archive.add(evaluations, tier=state.tier.value, run_id=state.run_id)

    def _assemble(self, state: _CorpusState) -> CorpusReport:
        from computronium_lab.research.schema import StatisticalSummary

        summaries = []
        for arm, metrics in state.values.items():
            arm_summaries: dict[str, StatisticalSummary] = {}
            for metric, values in metrics.items():
                summary = StatisticalSummary.from_samples(metric, values)
                control = state.problem_class.control_arm(arm)
                control_values = (
                    state.controls.get(control, {}).get(metric, ()) if control else ()
                )
                if control_values and len(control_values) == len(values):
                    summary = summary.with_paired(values, list(control_values))
                arm_summaries[metric] = summary
            control = state.problem_class.control_arm(arm)
            summaries.append(
                ArmSummary(
                    arm=arm,
                    metric_values={
                        metric: tuple(values) for metric, values in metrics.items()
                    },
                    summaries=arm_summaries,
                    control_values={
                        metric: tuple(values)
                        for metric, values in state.controls.get(
                            control or "", {}
                        ).items()
                    },
                    seeds=state.seeds,
                )
            )
        return CorpusReport(
            spec_key=state.spec.key(),
            problem_class=state.problem_class.name,
            tier=state.tier.value,
            run_id=state.run_id,
            arms=tuple(summaries),
            blocks=tuple(state.blocks),
            manifest_paths=tuple(state.manifests),
            ledger={
                "ledger": state.lab.record_ledger,
                "manifests": list(state.manifests),
            },
        )


def _first(metrics: dict[str, list[float]], keys: Sequence[str]) -> float | None:
    for key in keys:
        if metrics.get(key):
            values = metrics[key]
            return sum(values) / len(values)
    return None


def _task_of(problem_class: str) -> str:
    return str(_SPEC_DEFAULTS[problem_class]["task"])


def _dataset_of(problem_class: str) -> str:
    return str(_SPEC_DEFAULTS[problem_class]["dataset"])


def _dims_of(problem_class: str) -> dict[str, int]:
    defaults = _SPEC_DEFAULTS[problem_class]
    return {
        key: int(cast("int", defaults[key]))
        for key in ("input_dim", "num_classes")
        if key in defaults
    }


def _open_store(lab: Lab) -> CEECStore | None:
    from computronium_lab.research.adapters import LabRecorder

    return LabRecorder(lab).store()


def remeasure_catalog(
    lab: Lab,
    problem_classes: Sequence[str],
    *,
    mechanisms: Sequence[str] | None = None,
    seeds: Sequence[int] = (0, 1, 2),
    epochs: int = 1,
    tier: BudgetTier = BudgetTier.QUICK,
    run_id: str | None = None,
) -> dict[str, CorpusReport]:
    """Re-measure catalog rows on corpus tasks (T24.3.4).

    Rows without a valid construction path for a class fail into
    measurement blocks — the corpus records them, never forces them.
    """
    from computronium_lab.synthesis.catalog import CATALOG

    resolved_run_id = run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    rows = [c.name for c in CATALOG if mechanisms is None or c.name in mechanisms]
    reports: dict[str, CorpusReport] = {}
    for problem_class in problem_classes:
        runner = MeasurementRunner(lab, tier=tier)
        reports[problem_class] = runner.run(
            problem_class,
            rows,
            seeds=seeds,
            epochs=epochs,
            run_id=f"{resolved_run_id}-{problem_class}",
        )
    return reports
