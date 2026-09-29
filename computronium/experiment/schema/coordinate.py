"""Coordinate specification for the 6-axis experiment ontology."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "fidelity": self.fidelity,
            "seed": self.seed,
            "n_seeds": self.n_seeds,
            "epochs": self.epochs,
            "batch_limit": self.batch_limit,
            "budget_id": self.budget_id,
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
        )


@dataclass(frozen=True, slots=True)
class Provenance:
    """Provenance metadata for an experiment record."""

    env: dict[str, str]
    dataset: str
    dataset_version: str
    code_sha: str
    policy: str
    links: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "env": self.env,
            "dataset": self.dataset,
            "dataset_version": self.dataset_version,
            "code_sha": self.code_sha,
            "policy": self.policy,
            "links": self.links,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Provenance:
        return cls(
            env=data["env"],
            dataset=data["dataset"],
            dataset_version=data["dataset_version"],
            code_sha=data["code_sha"],
            policy=data["policy"],
            links=data.get("links", {}),
        )


__all__ = ["Coordinate", "Provenance", "Schedule", "_canonical_json"]
