"""Deterministic test cases for NTM Geometry.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.ontology.geometry import GeometryConfig, NtmGeometry


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    config: dict[str, Any]
    geometry: NtmGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Input: batch of 2, sequence length 4, input_dim 8 (one-hot encoded)
    input_dim = 8
    output_dim = 4
    seq_len = 4
    batch_size = 2

    # Create token IDs
    token_ids = torch.randint(
        0,
        input_dim,
        (batch_size, seq_len),
        device=device,
        dtype=torch.long,
        generator=generator,
    )
    # One-hot encode: (B, T, input_dim)
    state = torch.nn.functional.one_hot(token_ids, num_classes=input_dim).to(dtype)

    # Create a fixed NTM geometry for deterministic testing
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        geometry = NtmGeometry(
            GeometryConfig.ntm(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden=16,
                mem_slots=4,
                mem_width=8,
                beta_init=10.0,
            )
        )
    finally:
        torch.set_rng_state(rng_state)

    config = {
        "input_dim": input_dim,
        "output_dim": output_dim,
        "hidden": 16,
        "mem_slots": 4,
        "mem_width": 8,
        "beta_init": 10.0,
        "seed": seed,
    }

    return Case(
        state=state,
        config=config,
        geometry=geometry,
    )
