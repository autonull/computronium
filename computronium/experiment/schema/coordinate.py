"""Coordinate specification for the 6-axis experiment ontology."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields, replace
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record

from computronium.experiment.schema.registries import validate_rate_value


def _canonical_json(obj: Any) -> str:
    """Serialize to canonical JSON for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True, slots=True)
class Coordinate:
    """A 6-axis coordinate specifying a complete experiment configuration.

    The coordinate is the primary key for experiment identity and deduplication.
    """

    substrate: str
    geometry: str
    dynamics: str
    plasticity: str
    credit: str
    update: str
    params: dict[str, Any]

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name != "params" and not isinstance(value, str):
                raise TypeError(
                    f"Coordinate.{field.name} must be str, got {type(value)}"
                )
            if field.name == "params" and not isinstance(value, dict):
                raise TypeError("Coordinate.params must be dict")
        if isinstance(self.params, dict):
            for name, value in self.params.items():
                validate_rate_value(name, value)

    def cell_key(self) -> str:
        """Compute the cell key: SHA256 of structural axes only (no schedule)."""
        structural = {
            "substrate": self.substrate,
            "geometry": self.geometry,
            "dynamics": self.dynamics,
            "plasticity": self.plasticity,
            "credit": self.credit,
            "update": self.update,
            "params": self.params,
        }
        return hashlib.sha256(_canonical_json(structural).encode()).hexdigest()

    def measurement_key(self, schedule: Schedule) -> str:
        """Compute the measurement key: SHA256 of coordinate + schedule."""
        combined = {
            "coordinate": {
                "substrate": self.substrate,
                "geometry": self.geometry,
                "dynamics": self.dynamics,
                "plasticity": self.plasticity,
                "credit": self.credit,
                "update": self.update,
                "params": self.params,
            },
            "schedule": {
                "fidelity": schedule.fidelity,
                "seed": schedule.seed,
                "n_seeds": schedule.n_seeds,
                "epochs": schedule.epochs,
                "batch_limit": schedule.batch_limit,
                "budget_id": schedule.budget_id,
                "task_id": schedule.task_id,
                "param_budget": schedule.param_budget,
                "device": schedule.device,
                "deterministic": schedule.deterministic,
                "num_workers": schedule.num_workers,
                "precision": schedule.precision,
                "checkpoint_every_n": schedule.checkpoint_every_n,
            },
        }
        return hashlib.sha256(_canonical_json(combined).encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "substrate": self.substrate,
            "geometry": self.geometry,
            "dynamics": self.dynamics,
            "plasticity": self.plasticity,
            "credit": self.credit,
            "update": self.update,
            "params": self.params,
        }

    @classmethod
    def from_record(cls, record: Record) -> Coordinate:
        """The coordinate a record was measured at.

        Records store the six axes flat; reconstructing the coordinate from
        those fields is done here so no consumer assembles it a second way.
        """
        return cls(
            substrate=record.substrate,
            geometry=record.geometry,
            dynamics=record.dynamics,
            plasticity=record.plasticity,
            credit=record.credit,
            update=record.update,
            params=dict(record.params),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Coordinate:
        """Create Coordinate from dictionary."""
        return cls(
            substrate=data["substrate"],
            geometry=data["geometry"],
            dynamics=data["dynamics"],
            plasticity=data["plasticity"],
            credit=data["credit"],
            update=data["update"],
            params=data.get("params", {}),
        )

    def __hash__(self) -> int:
        return hash(self.cell_key())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coordinate):
            return NotImplemented
        return self.cell_key() == other.cell_key()


@dataclass(frozen=True, slots=True)
class Schedule:
    """Execution schedule for an experiment cell."""

    fidelity: str  # L0, L1, L2
    seed: int
    n_seeds: int
    epochs: int
    batch_limit: int
    budget_id: str
    task_id: str = ""  # L17: Task identity for cross-task uniqueness
    # A parameter ceiling changes what is trained, so it is part of the
    # measurement: two cells differing only by ceiling must not share a
    # measurement_key. 0 means unconstrained.
    param_budget: int = 0
    # Device for training: "cpu", "cuda", or "auto". "auto" prefers CUDA when available.
    device: str = "auto"
    # Use deterministic algorithms (sets torch.use_deterministic_algorithms)
    deterministic: bool = False
    # DataLoader num_workers (0 for single-threaded determinism)
    num_workers: int = 0
    # Numerical precision: "fp32", "fp16", "bf16"
    precision: Literal["fp32", "fp16", "bf16"] = "fp32"
    # Save checkpoint every N epochs (0 = disabled)
    checkpoint_every_n: int = 0
    # Distributed training (Phase E1)
    distributed_backend: Literal["none", "ddp", "fsdp"] = "none"
    ddp_backend: str = "nccl"  # nccl, gloo, mpi
    fsdp_sharding_strategy: str = "FULL_SHARD"  # FULL_SHARD, SHARD_GRAD_OP, NO_SHARD
    fsdp_min_params: int = 1_000_000  # Minimum params to shard
    fsdp_cpu_offload: bool = False
    fsdp_mixed_precision: bool = True

    def __post_init__(self) -> None:
        if self.fidelity not in {"L0", "L1", "L2"}:
            raise ValueError(f"Invalid fidelity: {self.fidelity}")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        if self.n_seeds <= 0:
            raise ValueError("n_seeds must be positive")
        if self.epochs <= 0:
            raise ValueError("epochs must be positive")
        if self.batch_limit < 0:
            raise ValueError("batch_limit must be non-negative")
        if self.param_budget < 0:
            raise ValueError("param_budget must be non-negative")
        if self.device not in {"cpu", "cuda", "auto"}:
            raise ValueError(
                f"Invalid device: {self.device}; expected 'cpu', 'cuda', or 'auto'"
            )
        if self.num_workers < 0:
            raise ValueError("num_workers must be non-negative")
        if self.precision not in {"fp32", "fp16", "bf16"}:
            raise ValueError(
                f"Invalid precision: {self.precision}; expected 'fp32', 'fp16', or 'bf16'"
            )
        if self.checkpoint_every_n < 0:
            raise ValueError("checkpoint_every_n must be non-negative")
        if self.distributed_backend not in {"none", "ddp", "fsdp"}:
            raise ValueError(
                f"Invalid distributed_backend: {self.distributed_backend}; expected 'none', 'ddp', or 'fsdp'"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "fidelity": self.fidelity,
            "seed": self.seed,
            "n_seeds": self.n_seeds,
            "epochs": self.epochs,
            "batch_limit": self.batch_limit,
            "budget_id": self.budget_id,
            "task_id": self.task_id,
            "param_budget": self.param_budget,
            "device": self.device,
            "deterministic": self.deterministic,
            "num_workers": self.num_workers,
            "precision": self.precision,
            "checkpoint_every_n": self.checkpoint_every_n,
            "distributed_backend": self.distributed_backend,
            "ddp_backend": self.ddp_backend,
            "fsdp_sharding_strategy": self.fsdp_sharding_strategy,
            "fsdp_min_params": self.fsdp_min_params,
            "fsdp_cpu_offload": self.fsdp_cpu_offload,
            "fsdp_mixed_precision": self.fsdp_mixed_precision,
        }

    @property
    def seed_plan(self) -> tuple[Schedule, ...]:
        """One single-seed schedule per seed this cell replicates over.

        A record's identity is its own single-seed schedule, so this spells a
        cell's replication plan in the terms the store holds: comparing a
        stored record against a ``n_seeds=5`` schedule compares two things the
        store never wrote, which is how a re-measurement goes unnoticed.
        """
        return tuple(
            replace(self, seed=self.seed + offset, n_seeds=1)
            for offset in range(self.n_seeds)
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Schedule:
        return cls(
            fidelity=data["fidelity"],
            seed=data["seed"],
            n_seeds=data["n_seeds"],
            epochs=data["epochs"],
            batch_limit=data["batch_limit"],
            budget_id=data["budget_id"],
            task_id=data.get("task_id", ""),
            param_budget=data.get("param_budget", 0),
            device=data.get("device", "auto"),
            deterministic=data.get("deterministic", False),
            num_workers=data.get("num_workers", 0),
            precision=data.get("precision", "fp32"),
            checkpoint_every_n=data.get("checkpoint_every_n", 0),
            distributed_backend=data.get("distributed_backend", "none"),
            ddp_backend=data.get("ddp_backend", "nccl"),
            fsdp_sharding_strategy=data.get("fsdp_sharding_strategy", "FULL_SHARD"),
            fsdp_min_params=data.get("fsdp_min_params", 1_000_000),
            fsdp_cpu_offload=data.get("fsdp_cpu_offload", False),
            fsdp_mixed_precision=data.get("fsdp_mixed_precision", True),
        )


class DataOrigin(StrEnum):
    """Origin of the data record for I(C,U) leakage protocol and contrast design."""

    EXPLORATION = "exploration"  # Policy-independent exploration
    POLICY_SELECTED = "policy_selected"  # Policy-dependent selection (I(C,U) split)
    CALIBRATION = "calibration"  # Frozen, never used for policy tuning
    TEST = "test"  # Held-out tasks, policy-independent
    CONTROL = "control"  # Control group for contrast design
    CONTRAST = "contrast"  # Contrast group for DOE (OFAT/fractional-factorial)


class TransferMode(StrEnum):
    """Transfer learning mode."""

    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot"
    FULL = "full"


@dataclass(frozen=True, slots=True)
class Provenance:
    """Provenance metadata for an experiment record."""

    env: dict[str, str]
    dataset: str
    dataset_version: str
    code_sha: str
    policy: str
    links: dict[str, str]
    data_origin: DataOrigin = DataOrigin.EXPLORATION
    training_tasks: tuple[str, ...] = ()
    transfer_source_ids: tuple[str, ...] = ()
    transfer_cutoff: str | None = None
    target_task: str | None = None
    transfer_mode: TransferMode | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "env": self.env,
            "dataset": self.dataset,
            "dataset_version": self.dataset_version,
            "code_sha": self.code_sha,
            "policy": self.policy,
            "links": self.links,
            "data_origin": self.data_origin.value,
            "training_tasks": list(self.training_tasks),
            "transfer_source_ids": list(self.transfer_source_ids),
            "transfer_cutoff": self.transfer_cutoff,
            "target_task": self.target_task,
            "transfer_mode": self.transfer_mode.value if self.transfer_mode else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Provenance:
        data_origin = DataOrigin(data.get("data_origin", "exploration"))
        transfer_mode = data.get("transfer_mode")
        return cls(
            env=data["env"],
            dataset=data["dataset"],
            dataset_version=data["dataset_version"],
            code_sha=data["code_sha"],
            policy=data["policy"],
            links=data.get("links", {}),
            data_origin=data_origin,
            training_tasks=tuple(data.get("training_tasks", ())),
            transfer_source_ids=tuple(data.get("transfer_source_ids", ())),
            transfer_cutoff=data.get("transfer_cutoff"),
            target_task=data.get("target_task"),
            transfer_mode=TransferMode(transfer_mode) if transfer_mode else None,
        )


__all__ = [
    "Coordinate",
    "DataOrigin",
    "Provenance",
    "Schedule",
    "TransferMode",
    "_canonical_json",
]
