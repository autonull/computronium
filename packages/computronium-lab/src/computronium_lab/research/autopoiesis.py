"""Autopoiesis kernel (TODO24 Phase 1): concrete implementations of the
TODO23 ``computronium.autopoiesis.protocols``.

The shipped protocols are scalar and minimal; this module preserves scalar
conformance where a scalar view exists (surrogate screens, single-objective
fallbacks) and adds the research-layer extensions — vector fitness,
crowding, hypervolume stagnation — beside them. The TODO23 protocols are
never widened.

Every mutant stays on valid Lab construction paths: row hops point at
catalog rows, size overrides flow into preset builders, and the
constitution test-builds each candidate before any training.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING, cast

from computronium_lab.lab import Lab, synthetic_task
from computronium_lab.synthesis.catalog import CATALOG, MechanismCandidate
from computronium_lab.synthesis.engine import (
    OBJECTIVE_FIELDS,
    card_factor,
    screen_config,
)
from computronium_lab.synthesis.predictor import ViabilityModel
from computronium_lab.synthesis.spec import ProblemSpec
from computronium_lab.training import StabilityGuardKill, TrainOptions

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium_lab.research.schema import BudgetCap

__all__ = [
    "OBJECTIVE_NAMES",
    "CampaignFitness",
    "CandidateEvaluation",
    "CoordinateGenome",
    "ParetoSelection",
    "ResearchConstitution",
    "ResearchStagnationDetector",
    "SafeMutationOperator",
    "SurrogateFitness",
    "crowding_distance",
    "hypervolume",
    "nondominated_sort",
    "objective_names",
]

OBJECTIVE_NAMES: tuple[str, ...] = tuple(OBJECTIVE_FIELDS)


def objective_names() -> tuple[str, ...]:
    """Live objective names (TODO24 §14).

    Unlike the import-time ``OBJECTIVE_NAMES`` snapshot, this reflects
    objectives added later via ``register_objective``.
    """
    return tuple(OBJECTIVE_FIELDS)


_SIZE_MIN = 0.25
_SIZE_MAX = 4.0
_PRECISIONS: tuple[str, ...] = ("float32", "float16")
_QUANTIZATIONS: tuple[str | None, ...] = (None, "int8", "ternary")


@lru_cache(maxsize=1)
def _viability_model() -> ViabilityModel:
    return ViabilityModel().fit()


def _row(name: str) -> MechanismCandidate:
    for candidate in CATALOG:
        if candidate.name == name:
            return candidate
    raise ValueError(f"{name!r} is not a catalog row")


def _nested(payload: Mapping[str, object], *keys: str) -> object:
    """Walk a nested genome-payload mapping; every level must be a mapping."""
    node: object = payload
    for key in keys:
        if not isinstance(node, Mapping):
            raise TypeError(f"genome payload has no mapping at {key!r}")
        node = node[key]
    return node


def _payload_digest(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


@dataclass(slots=True)
class CoordinateGenome:
    """A catalog-rooted mechanism coordinate with search annotations.

    The genome always resolves to a catalog row: row hops mutate the row
    name, size/precision/quantization/substrate mutate the spec or the
    preset build kwargs. ``instantiate`` builds a fresh system — parents
    are never mutated in place.
    """

    mechanism: str
    spec: ProblemSpec
    size_scale: float = 1.0
    precision: str = "float32"
    quantization: str | None = None
    substrate: str | None = None
    lineage: tuple[str, ...] = ()
    mutations: tuple[str, ...] = ()
    notes: list[str] = field(default_factory=list[str])

    @classmethod
    def seed(cls, mechanism: str, spec: ProblemSpec) -> CoordinateGenome:
        return cls(
            mechanism=mechanism,
            spec=spec,
            precision=spec.constraints.precision,
        )

    @property
    def candidate(self) -> MechanismCandidate:
        return _row(self.mechanism)

    @property
    def effective_spec(self) -> ProblemSpec:
        constraints = self.spec.constraints
        if self.substrate is not None or self.precision != constraints.precision:
            from dataclasses import replace

            constraints = replace(
                constraints,
                substrate=self.substrate or constraints.substrate,
                precision=self.precision,
            )
            return replace(self.spec, constraints=constraints)
        return self.spec

    def genome(self) -> dict[str, object]:
        constraints = self.spec.constraints
        return {
            "mechanism": self.mechanism,
            "spec": {
                "task": self.spec.task,
                "dataset": self.spec.dataset,
                "constraints": {
                    "compute_budget": constraints.compute_budget,
                    "latency_ms": constraints.latency_ms,
                    "memory_gb": constraints.memory_gb,
                    "continual": constraints.continual,
                    "local_credit": constraints.local_credit,
                    "precision": self.precision,
                    "substrate": self.substrate or constraints.substrate,
                },
                "objectives": list(self.spec.objectives),
                "exploration_budget": self.spec.exploration_budget,
                "input_dim": self.spec.input_dim,
                "num_classes": self.spec.num_classes,
            },
            "size_scale": self.size_scale,
            "precision": self.precision,
            "quantization": self.quantization,
            "substrate_override": self.substrate,
            "lineage": list(self.lineage),
            "mutations": list(self.mutations),
            "notes": list(self.notes),
        }

    @classmethod
    def _base_spec(cls, raw_spec: Mapping[str, object]) -> ProblemSpec:
        from computronium_lab.synthesis.spec import Constraints

        raw_constraints = raw_spec["constraints"]
        if not isinstance(raw_constraints, Mapping):
            raise TypeError("genome payload requires a constraints mapping")
        constraints = Constraints(
            compute_budget=cast("str | None", raw_constraints.get("compute_budget")),
            latency_ms=cast("float | None", raw_constraints.get("latency_ms")),
            memory_gb=cast("float | None", raw_constraints.get("memory_gb")),
            continual=bool(raw_constraints.get("continual", False)),
            local_credit=bool(raw_constraints.get("local_credit", False)),
            precision=str(raw_constraints.get("precision", "float32")),
            substrate=str(raw_constraints.get("substrate", "digital")),
        )
        return ProblemSpec(
            task=str(raw_spec["task"]),
            dataset=str(raw_spec["dataset"]),
            constraints=constraints,
            objectives=tuple(
                cast("Sequence[str]", raw_spec.get("objectives", ("accuracy",)))
            ),
            exploration_budget=int(cast("int", raw_spec.get("exploration_budget", 3))),
            input_dim=int(cast("int", raw_spec.get("input_dim", 32))),
            num_classes=int(cast("int", raw_spec.get("num_classes", 4))),
        )

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> CoordinateGenome:
        raw_spec = payload["spec"]
        if not isinstance(raw_spec, Mapping):
            raise TypeError("genome payload requires a spec mapping")
        quantization = payload.get("quantization")
        substrate = payload.get("substrate_override")
        return cls(
            mechanism=str(payload["mechanism"]),
            spec=cls._base_spec(raw_spec),
            size_scale=float(cast("float", payload.get("size_scale", 1.0))),
            precision=str(payload.get("precision", "float32")),
            quantization=str(quantization) if quantization is not None else None,
            substrate=str(substrate) if substrate is not None else None,
            lineage=tuple(cast("Sequence[str]", payload.get("lineage", ()))),
            mutations=tuple(cast("Sequence[str]", payload.get("mutations", ()))),
            notes=list(cast("Sequence[str]", payload.get("notes", []))),
        )

    @property
    def digest(self) -> str:
        """Identity of the search coordinate.

        Build ``notes`` are excluded: ``instantiate`` may annotate them
        (partial size-override application) without changing identity.
        """
        payload = self.genome()
        return _payload_digest({k: v for k, v in payload.items() if k != "notes"})

    def _build_preset(self, candidate: MechanismCandidate) -> object:
        from computronium_lab.presets import build_system_preset

        base = {
            "input_dim": self.spec.input_dim,
            "output_dim": self.spec.num_classes,
        }
        width = max(1, round(candidate.width * self.size_scale))
        depth = max(1, round(candidate.depth * self.size_scale))
        attempts = [
            {"width": width, "depth": depth},
            {"width": width},
            {"depth": depth},
            {},
        ]
        errors: list[str] = []
        for extra in attempts:
            try:
                system = build_system_preset(candidate.build_name, **base, **extra)
            except TypeError as exc:
                errors.append(str(exc))
                continue
            if extra != attempts[0]:
                self.notes.append(
                    f"size override partially applied ({extra or 'none'})"
                )
            return system
        raise TypeError(
            f"preset {candidate.build_name!r} rejects size kwargs: {errors[-1]}"
        )

    def instantiate(self) -> object:
        """Build a fresh system on a valid Lab construction path."""
        candidate = self.candidate
        if candidate.build_kind == "preset":
            return self._build_preset(candidate)
        return candidate.build(self.effective_spec)

    def surrogate_vector(self) -> dict[str, float]:
        """Predicted objective vector (screening only, never certification)."""
        candidate = self.candidate
        viability = _viability_model().predict(candidate.features(self.effective_spec))
        factor, _ = card_factor(candidate.credit, candidate.update)
        accuracy = viability * factor
        scale = self.size_scale
        return {
            "accuracy": accuracy,
            "adaptation_speed": candidate.pareto.adaptation_speed,
            "stability": candidate.pareto.stability,
            "latency": candidate.pareto.latency_ms * scale,
            "memory": candidate.pareto.memory_gb * scale,
        }


class SafeMutationOperator:
    """Mutations constrained to valid Lab construction paths (T24.1.2).

    Row hops target catalog rows sharing the current geometry; size,
    precision, quantization, and substrate edits stay on supported paths.
    """

    def __init__(self, *, size_jitter: float = 0.25) -> None:
        self.size_jitter = size_jitter

    def _hop_targets(
        self, row: MechanismCandidate, axis: str
    ) -> list[MechanismCandidate]:
        targets = []
        for candidate in CATALOG:
            if candidate.name == row.name or candidate.geometry != row.geometry:
                continue
            match axis:
                case "credit":
                    hop = candidate.credit != row.credit
                case "update":
                    hop = (
                        candidate.credit == row.credit
                        and candidate.update != row.update
                    )
                case "plasticity":
                    hop = (
                        candidate.credit == row.credit
                        and candidate.plasticity != row.plasticity
                    )
                case _:
                    hop = False
            if hop:
                targets.append(candidate)
        return targets

    def mutate(self, genome: dict[str, object], rng: object) -> dict[str, object]:
        """Return a mutated payload; structurally valid by construction."""
        if not isinstance(rng, random.Random):  # ruff: ignore[suspicious-non-cryptographic-random-usage] - seeded deterministic evolution requires a pseudo-random RNG
            raise TypeError(
                f"mutate requires a random.Random, got {type(rng).__name__}"
            )
        payload = json.loads(json.dumps(genome))
        row = _row(str(payload["mechanism"]))
        ops = [
            "credit_swap",
            "update_swap",
            "plasticity_swap",
            "size_jitter",
            "precision_swap",
            "quantization_cycle",
            "substrate_swap",
        ]
        rng.shuffle(ops)
        for op in ops:
            if self._apply(op, payload, row, rng):
                payload["lineage"] = [*payload.get("lineage", []), row.name]
                payload["mutations"] = [
                    *payload.get("mutations", []),
                    str(payload["_last_mutation"]),
                ]
                del payload["_last_mutation"]
                return payload
        payload["mutations"] = [*payload.get("mutations", []), "identity"]
        payload["lineage"] = [*payload.get("lineage", []), row.name]
        return payload

    _HOP_OPS = frozenset({"credit_swap", "update_swap", "plasticity_swap"})

    def _apply(
        self,
        op: str,
        payload: dict[str, object],
        row: MechanismCandidate,
        rng: random.Random,
    ) -> bool:
        if op in self._HOP_OPS:
            return self._apply_hop(op, payload, row, rng)
        match op:
            case "size_jitter":
                return self._apply_size(payload, rng)
            case "precision_swap":
                return self._apply_precision(payload, rng)
            case "quantization_cycle":
                return self._apply_quantization(payload)
            case "substrate_swap":
                return self._apply_substrate(payload, row, rng)
            case _:
                return False

    def _screen_ok(self, payload: dict[str, object], row: MechanismCandidate) -> bool:
        """A mutation target must pass config validation on the payload's
        effective spec (catalog substrate claims can diverge from
        ``SystemConfig.validate`` — e.g. neuromorphic needs temporal
        dynamics — so targets are screened, not trusted)."""
        try:
            genome = CoordinateGenome.from_payload(payload)
        except KeyError, TypeError, ValueError:
            return False
        if genome.mechanism != row.name:
            try:
                row = _row(genome.mechanism)
            except ValueError:
                return False
        try:
            screen_config(row, genome.effective_spec)
        except Exception:
            return False
        return True

    def _apply_hop(
        self,
        op: str,
        payload: dict[str, object],
        row: MechanismCandidate,
        rng: random.Random,
    ) -> bool:
        targets = [
            target
            for target in self._hop_targets(row, op.removesuffix("_swap"))
            if self._screen_ok({**payload, "mechanism": target.name}, target)
        ]
        if not targets:
            return False
        target = rng.choice(targets)
        payload["mechanism"] = target.name
        payload["_last_mutation"] = f"{op}:{row.name}->{target.name}"
        return True

    def _apply_size(self, payload: dict[str, object], rng: random.Random) -> bool:
        factor = 1.0 + rng.uniform(-self.size_jitter, self.size_jitter)
        scale = min(
            _SIZE_MAX,
            max(
                _SIZE_MIN, float(cast("float", payload.get("size_scale", 1.0))) * factor
            ),
        )
        payload["size_scale"] = scale
        payload["_last_mutation"] = f"size_jitter:x{factor:.2f}"
        return True

    def _apply_precision(self, payload: dict[str, object], rng: random.Random) -> bool:
        current = str(
            payload.get("precision")
            or _nested(payload, "spec", "constraints", "precision")
        )
        options = [p for p in _PRECISIONS if p != current] or [current]
        rng.shuffle(options)
        original = payload.get("precision")
        for chosen in options:
            payload["precision"] = chosen
            row = _row(str(payload["mechanism"]))
            if self._screen_ok(payload, row):
                payload["_last_mutation"] = f"precision_swap:{current}->{chosen}"
                return True
        payload["precision"] = original
        return False

    def _apply_quantization(self, payload: dict[str, object]) -> bool:
        current = payload.get("quantization")
        nxt = _QUANTIZATIONS[(_QUANTIZATIONS.index(current) + 1) % len(_QUANTIZATIONS)]
        payload["quantization"] = nxt
        payload["_last_mutation"] = f"quantization_cycle:{current}->{nxt}"
        return True

    def _apply_substrate(
        self,
        payload: dict[str, object],
        row: MechanismCandidate,
        rng: random.Random,
    ) -> bool:
        current = str(
            payload.get("substrate_override")
            or _nested(payload, "spec", "constraints", "substrate")
        )
        options = [
            s
            for s in row.substrates
            if s != current
            and self._screen_ok({**payload, "substrate_override": s}, row)
        ]
        if not options:
            return False
        chosen = rng.choice(options)
        payload["substrate_override"] = chosen
        payload["_last_mutation"] = f"substrate_swap:{current}->{chosen}"
        return True


class ResearchConstitution:
    """Admits only constructible, constraint-satisfying genomes (T24.1.3).

    Every admitted genome test-builds a fresh system: invalid candidates
    are rejected before any training.
    """

    def __init__(self, spec: ProblemSpec, budget: BudgetCap) -> None:
        self.spec = spec
        self.budget = budget

    def admits(self, genome: dict[str, object]) -> bool:
        return self.evaluate(genome)[0]

    def evaluate(self, genome: dict[str, object]) -> tuple[bool, str]:
        """Admission verdict with a human-readable reason (rejection report)."""
        candidate = self._parse(genome)
        if candidate is None:
            return False, "unparseable genome payload"
        try:
            reason = self._bound_reason(candidate)
        except (KeyError, TypeError, ValueError) as exc:
            return False, f"unknown mechanism: {exc}"
        if reason is not None:
            return False, reason
        if not self._test_build(candidate):
            return False, "construction failed (screen_config or instantiate)"
        return True, "admitted"

    def _parse(self, genome: dict[str, object]) -> CoordinateGenome | None:
        try:
            return CoordinateGenome.from_payload(genome)
        except KeyError, TypeError, ValueError:
            return None

    def _bound_reason(self, candidate: CoordinateGenome) -> str | None:
        if not (_SIZE_MIN <= candidate.size_scale <= _SIZE_MAX):
            return (
                f"size_scale {candidate.size_scale} outside [{_SIZE_MIN}, {_SIZE_MAX}]"
            )
        if candidate.quantization not in {"int8", "ternary", None}:
            return f"quantization {candidate.quantization!r} has no export path"
        row = candidate.candidate
        effective = candidate.effective_spec
        if effective.constraints.substrate not in row.substrates:
            return (
                f"substrate {effective.constraints.substrate!r} "
                f"unsupported by {row.name}"
            )
        if effective.constraints.local_credit and not row.local_credit:
            return f"{row.name} is not local-credit"
        if effective.task not in row.trainable_on:
            return (
                f"{row.name} has no training path for task {effective.task!r} "
                f"(trainable_on={sorted(row.trainable_on)})"
            )
        return self._resource_reason(candidate, row)

    def _resource_reason(
        self, candidate: CoordinateGenome, row: MechanismCandidate
    ) -> str | None:
        limits = candidate.effective_spec.constraints
        if (
            limits.latency_ms is not None
            and row.pareto.latency_ms * candidate.size_scale > limits.latency_ms
        ):
            return f"latency estimate exceeds {limits.latency_ms} ms"
        if (
            limits.memory_gb is not None
            and row.pareto.memory_gb * candidate.size_scale > limits.memory_gb
        ):
            return f"memory estimate exceeds {limits.memory_gb} GB"
        return None

    def _test_build(self, candidate: CoordinateGenome) -> bool:
        from computronium_lab.synthesis.engine import screen_config

        try:
            screen_config(candidate.candidate, candidate.effective_spec)
            candidate.instantiate()
        except Exception:
            return False
        return True


class SurrogateFitness:
    """Cheap predictor + recipe-prior + resource screen (T24.1.4).

    The scalar ``score`` is the protocol view; ``score_vector`` is the
    research-layer extension consumed by Pareto selection.
    """

    def __init__(self, spec: ProblemSpec) -> None:
        self.spec = spec

    def screen(self, genome: CoordinateGenome | Mapping[str, object]) -> float:
        candidate = (
            genome
            if isinstance(genome, CoordinateGenome)
            else CoordinateGenome.from_payload(genome)
        )
        row = candidate.candidate
        viability = _viability_model().predict(row.features(candidate.effective_spec))
        factor, _ = card_factor(row.credit, row.update)
        score = viability * factor
        limits = candidate.effective_spec.constraints
        scale = candidate.size_scale
        if (
            limits.latency_ms is not None
            and row.pareto.latency_ms * scale > limits.latency_ms
        ):
            score *= 0.5
        if (
            limits.memory_gb is not None
            and row.pareto.memory_gb * scale > limits.memory_gb
        ):
            score *= 0.5
        return float(score)

    def score(self, operator: object, batch: object = None) -> float:
        """Protocol view: the surrogate needs no batch."""
        if isinstance(operator, CoordinateGenome):
            return self.screen(operator)
        if isinstance(operator, dict):
            return self.screen(CoordinateGenome.from_payload(operator))
        raise TypeError(f"surrogate cannot score {type(operator).__name__}")

    def score_vector(self, genome: CoordinateGenome) -> dict[str, float]:
        return genome.surrogate_vector()


_SEQ_TASKS = ("sequence_last_symbol", "sequence_threshold", "sequence_parity")
_SEQ_TASK_ARG = {
    "sequence_last_symbol": "last_symbol",
    "sequence_threshold": "threshold",
    "sequence_parity": "parity",
}


@dataclass(frozen=True, slots=True)
class CandidateEvaluation:
    """Standardized campaign-backed objective vector (T24.1.5)."""

    genome_digest: str
    mechanism: str
    objectives: dict[str, float]
    metric_sources: dict[str, str]
    seeds: tuple[int, ...]
    per_seed_accuracy: tuple[float, ...]
    reproduction: bool
    stability: bool | None
    certified: bool
    gate_outcomes: dict[str, bool | None]
    walltime_s: float = 0.0
    notes: tuple[str, ...] = ()


_FLAT_TASKS = ("flat_classification", "flat_classification_hard")


class NotTrainableError(Exception):
    """A row's construction path has no campaign training path for the
    spec task (TODO25 D.1): consult ``MechanismCandidate.trainable_on``
    before building; a mismatch is a measurement block, not a traceback.
    """


class CampaignFitness:
    """Campaign-backed fitness over Lab construction paths (T24.1.5)."""

    def __init__(
        self, spec: ProblemSpec, *, reproduction_tolerance: float = 0.15
    ) -> None:
        self.spec = spec
        self.reproduction_tolerance = reproduction_tolerance

    def evaluate(
        self,
        genome: CoordinateGenome,
        lab: Lab,
        *,
        seeds: Sequence[int],
        epochs: int,
    ) -> CandidateEvaluation:
        """Train one fresh system per seed; never mutate parents in place."""
        import time

        t0 = time.perf_counter()
        row = genome.candidate
        if self.spec.task not in row.trainable_on:
            raise NotTrainableError(
                f"{genome.mechanism} has no campaign training path for "
                f"task {self.spec.task!r} "
                f"(trainable_on={sorted(row.trainable_on)})"
            )
        accuracies: list[float] = []
        stability_ok: bool | None = True
        metric_source = "task_accuracy"
        for seed in seeds:
            lab.seed = seed
            system = genome.instantiate()
            accuracy, guard, source = self._train_arm(lab, genome, system, seed, epochs)
            accuracies.append(accuracy)
            metric_source = source
            if guard is None:
                stability_ok = None if stability_ok is None else stability_ok
            else:
                stability_ok = bool(stability_ok) and guard
        mean_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
        reproduction = (
            mean_accuracy >= row.pareto.accuracy - self.reproduction_tolerance
        )
        stability_gate: bool | None = (
            bool(stability_ok) if stability_ok is not None else None
        )
        certified = bool(reproduction) and (stability_gate is not False)
        if stability_gate is None and self.spec.task in _FLAT_TASKS:
            certified = False
        objectives = {
            "accuracy": mean_accuracy,
            "stability": 1.0 if stability_gate else 0.0,
            "adaptation_speed": row.pareto.adaptation_speed,
            "latency": row.pareto.latency_ms * genome.size_scale,
            "memory": row.pareto.memory_gb * genome.size_scale,
        }
        return CandidateEvaluation(
            genome_digest=genome.digest,
            mechanism=genome.mechanism,
            objectives=objectives,
            metric_sources=dict.fromkeys(("accuracy",), metric_source),
            seeds=tuple(seeds),
            per_seed_accuracy=tuple(accuracies),
            reproduction=bool(reproduction),
            stability=stability_gate,
            certified=bool(certified),
            gate_outcomes={
                "BenchmarkReproduction": bool(reproduction),
                "StabilityCertificate": stability_gate,
                "DeployabilityCheck": None,
            },
            walltime_s=time.perf_counter() - t0,
        )

    def _train_arm(
        self, lab: Lab, genome: CoordinateGenome, system: object, seed: int, epochs: int
    ) -> tuple[float, bool | None, str]:
        task = self.spec.task
        if task in _FLAT_TASKS:
            from computronium_lab.lab import HARD_TASK_PARAMS

            hard = task == "flat_classification_hard"
            if hard:
                train_loader, val_loader = synthetic_task(
                    seed=seed,
                    input_dim=self.spec.input_dim,
                    num_classes=self.spec.num_classes,
                    **HARD_TASK_PARAMS,
                )
            else:
                _, val_loader = synthetic_task(
                    seed=seed,
                    input_dim=self.spec.input_dim,
                    num_classes=self.spec.num_classes,
                )
                train_loader = None
            try:
                result = lab.train(
                    system,
                    task="synthetic",
                    epochs=epochs,
                    spec=genome.effective_spec,
                    options=TrainOptions(stability_guard=True),
                    val_data=val_loader,
                    train_data=train_loader,
                )
            except StabilityGuardKill:
                return 0.0, False, "train_accuracy"
            metrics = result.metrics
            if "val_acc" in metrics:
                accuracy = float(metrics["val_acc"])
                source = "val_accuracy"
            else:
                accuracy = float(metrics.get("accuracy", 0.0))
                source = "train_accuracy"
            guard = result.stability
            ok = (
                (bool(guard.checked) and not bool(guard.kill))
                if guard is not None
                else None
            )
            return accuracy, ok, source
        if task in _SEQ_TASKS:
            result = lab.train_sequence(
                system,
                task=_SEQ_TASK_ARG[task],
                epochs=epochs,
                seed=seed,
            )
            return float(result.accuracy), None, "task_accuracy"
        if task == "nca_state_prediction":
            state_result = lab.train_state_prediction(system, epochs=epochs, seed=seed)
            return float(state_result.cell_accuracy), None, "task_accuracy"
        raise ValueError(f"task {task!r} has no campaign fitness path")


def _dominates(
    a: Mapping[str, float],
    b: Mapping[str, float],
    objectives: Sequence[tuple[str, bool]],
) -> bool:
    better = False
    for name, maximize in objectives:
        delta = a[name] - b[name]
        if not maximize:
            delta = -delta
        if delta < 0:
            return False
        if delta > 0:
            better = True
    return better


def nondominated_sort(
    vectors: Sequence[Mapping[str, float]],
    objectives: Sequence[tuple[str, bool]],
) -> list[list[int]]:
    """Fronts of indices, front 0 first (NSGA-II ordering)."""
    remaining = list(range(len(vectors)))
    fronts: list[list[int]] = []
    while remaining:
        front = [
            i
            for i in remaining
            if not any(
                _dominates(vectors[j], vectors[i], objectives)
                for j in remaining
                if j != i
            )
        ]
        if not front:
            front = remaining[:1]
        fronts.append(front)
        front_set = set(front)
        remaining = [i for i in remaining if i not in front_set]
    return fronts


def crowding_distance(
    vectors: Sequence[Mapping[str, float]],
    objectives: Sequence[tuple[str, bool]],
) -> list[float]:
    """Per-point crowding over the front (boundary points stay infinite)."""
    n = len(vectors)
    if n <= 2:
        return [math.inf] * n
    distance = [0.0] * n
    for name, maximize in objectives:
        order = sorted(range(n), key=lambda i: vectors[i][name])
        distance[order[0]] = math.inf
        distance[order[-1]] = math.inf
        span = vectors[order[-1]][name] - vectors[order[0]][name]
        if span == 0:
            continue
        sign = 1.0 if maximize else -1.0
        for rank in range(1, n - 1):
            gap = vectors[order[rank + 1]][name] - vectors[order[rank - 1]][name]
            distance[order[rank]] += sign * gap / span
    return distance


def hypervolume(
    vectors: Sequence[Mapping[str, float]],
    objectives: Sequence[tuple[str, bool]],
    reference: Mapping[str, float],
) -> float:
    """Exact hypervolume of the normalized dominated region (small fronts)."""
    normalized: list[list[float]] = []
    for vector in vectors:
        point = []
        for name, maximize in objectives:
            value = vector[name]
            ref = reference[name]
            point.append(value - ref if maximize else ref - value)
        if all(v >= 0 for v in point):
            normalized.append(point)
    if not normalized:
        return 0.0
    return _hypervolume_recursive(normalized)


def _hypervolume_recursive(points: list[list[float]]) -> float:
    if not points:
        return 0.0
    dim = len(points[0])
    if dim == 1:
        return max(p[0] for p in points)
    ordered = sorted(points, key=lambda p: p[-1])
    volume = 0.0
    last = 0.0
    for i, point in enumerate(ordered):
        height = point[-1] - last
        if height > 0:
            front = [p[:-1] for p in ordered[i:]]
            volume += height * _hypervolume_recursive(front)
            last = point[-1]
    return volume


class ParetoSelection:
    """Non-dominated sorting with crowding diversity (T24.1.6).

    ``select`` is the scalar protocol view (single-objective fallback);
    ``select_pareto`` is the research-layer extension.
    """

    def select(self, population: list[tuple[object, float]], k: int) -> list[object]:
        ranked = sorted(range(len(population)), key=lambda i: (-population[i][1], i))
        return [population[i][0] for i in ranked[:k]]

    def select_pareto(
        self,
        candidates: Sequence[tuple[CoordinateGenome, dict[str, float]]],
        objectives: Sequence[tuple[str, bool]],
        k: int,
    ) -> list[CoordinateGenome]:
        vectors = [vector for _, vector in candidates]
        fronts = nondominated_sort(vectors, objectives)
        chosen: list[CoordinateGenome] = []
        for front in fronts:
            if len(chosen) + len(front) <= k:
                chosen.extend(candidates[i][0] for i in front)
                continue
            front_vectors = [vectors[i] for i in front]
            distances = crowding_distance(front_vectors, objectives)
            order = sorted(
                range(len(front)),
                key=lambda r: (
                    distances[r] if not math.isinf(distances[r]) else float("inf"),
                    -r,
                ),
                reverse=True,
            )
            slots = k - len(chosen)
            chosen.extend(candidates[front[r]][0] for r in order[:slots])
            break
        return chosen


class ResearchStagnationDetector:
    """Scalar protocol view plus frontier-growth stagnation (T24.1.7)."""

    def __init__(self, patience: int = 2, tol: float = 1e-9) -> None:
        self.patience = patience
        self.tol = tol
        self._best: float | None = None
        self._misses = 0
        self._best_hypervolume: float | None = None
        self._hv_misses = 0

    def update(self, best_fitness: float) -> bool:
        """True when the scalar best has not improved for ``patience``."""
        if self._best is None or best_fitness > self._best + self.tol:
            self._best = best_fitness
            self._misses = 0
            return False
        self._misses += 1
        return self._misses >= self.patience

    def update_hypervolume(self, value: float) -> bool:
        """True when frontier hypervolume has not grown for ``patience``."""
        if self._best_hypervolume is None or value > self._best_hypervolume + self.tol:
            self._best_hypervolume = value
            self._hv_misses = 0
            return False
        self._hv_misses += 1
        return self._hv_misses >= self.patience

    def exhausted(self, used_campaigns: int, cap: int) -> bool:
        return used_campaigns >= cap
