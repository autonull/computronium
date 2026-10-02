"""Coordinate specification for the 6-axis experiment ontology."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
from enum import StrEnum
from typing import Any


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
        }

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
