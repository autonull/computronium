"""Deterministic test cases for Quantum Substrate.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.ontology.substrate.spec import (
    ConstraintConfig,
    CostConfig,
    DeviceModel,
    ExecutionModel,
    NoiseConfig,
    NumericRepresentation,
    SubstrateSpec,
)


@dataclass(frozen=True, slots=True)
class Case:
    spec: SubstrateSpec
    config: dict[str, Any]


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    """Create a deterministic test case for quantum substrate."""

    # Create a fixed substrate spec for deterministic testing
    spec = SubstrateSpec(
        execution_model=ExecutionModel.NATIVE,
        device_model=DeviceModel.QUANTUM,
        numeric_representation=NumericRepresentation.COMPLEX,
        noise_model=NoiseConfig(kind="none", level=0.0),
        structural_constraints=ConstraintConfig(weight_bounds=None, sparsity=0.0),
        cost_model=CostConfig(joules_per_mac=0.0, fab_cost_ratio=1.0),
        substrate_type=None,
    )

    config = {
        "precision": "complex64",
        "noise_level": 0.0,
        "weight_bounds": None,
        "sparsity": 0.0,
        "device": device,
        "seed": seed,
    }

    return Case(
        spec=spec,
        config=config,
    )


def make_case_noisy(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    noise_level: float = 0.1,
) -> Case:
    """Create a deterministic test case for noisy quantum substrate."""
    spec = SubstrateSpec(
        execution_model=ExecutionModel.NATIVE,
        device_model=DeviceModel.QUANTUM,
        numeric_representation=NumericRepresentation.COMPLEX,
        noise_model=NoiseConfig(kind="additive_gaussian", level=noise_level),
        structural_constraints=ConstraintConfig(weight_bounds=None, sparsity=0.0),
        cost_model=CostConfig(joules_per_mac=0.0, fab_cost_ratio=1.0),
        substrate_type=None,
    )

    config = {
        "precision": "complex64",
        "noise_level": noise_level,
        "weight_bounds": None,
        "sparsity": 0.0,
        "device": device,
        "seed": seed,
    }

    return Case(
        spec=spec,
        config=config,
    )
