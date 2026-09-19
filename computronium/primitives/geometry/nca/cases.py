"""Deterministic test cases for NCA Geometry.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.ontology.geometry import GeometryConfig, NcaGeometry


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    config: dict[str, Any]
    geometry: NcaGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # State grid: batch of 1, channels 4, 8x8 grid
    channels = 4
    grid_h, grid_w = 8, 8
    batch_size = 1
    state = torch.randn(
        batch_size,
        channels,
        grid_h,
        grid_w,
        device=device,
        dtype=dtype,
        generator=generator,
    )

    # Create a fixed NCA geometry for deterministic testing
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        geometry = NcaGeometry(
            GeometryConfig.nca(
                channels=channels,
                hidden=16,
                grid_hw=(grid_h, grid_w),
                delta_scale=0.5,
                mask_prob=0.5,
                label_channels=0,
                init_scale=0.1,
            )
        )
    finally:
        torch.set_rng_state(rng_state)

    config = {
        "channels": channels,
        "hidden": 16,
        "grid_hw": (grid_h, grid_w),
        "delta_scale": 0.5,
        "mask_prob": 0.5,
        "label_channels": 0,
        "init_scale": 0.1,
        "seed": seed,
    }

    return Case(
        state=state,
        config=config,
        geometry=geometry,
    )
