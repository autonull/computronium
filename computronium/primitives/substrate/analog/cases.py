"""Deterministic test cases for Analog Substrate.

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
    """Create a deterministic test case for the analog substrate."""
    spec = SubstrateSpec(
        execution_model=ExecutionModel.NATIVE,
        device_model=DeviceModel.ANALOG,
        numeric_representation=NumericRepresentation.REAL,
        noise_model=NoiseConfig(kind="none", level=0.0),
        structural_constraints=ConstraintConfig(
            weight_bounds=(-1.0, 1.0), sparsity=0.0
        ),
        cost_model=CostConfig(joules_per_mac=1e-14, fab_cost_ratio=1.1),
        substrate_type=None,
    )
    config = {
        "noise_level": 0.0,
        "weight_bounds": (-1.0, 1.0),
        "device": device,
        "seed": seed,
    }
    return Case(spec=spec, config=config)
