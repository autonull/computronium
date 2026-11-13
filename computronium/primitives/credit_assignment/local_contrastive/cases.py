"""Deterministic test cases for Local Contrastive Credit.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

import torch

from computronium.harness import seeded_rng
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.primitives._common import PrimitiveCase

FEATURE_DIM = 8
LABEL_DIM = 4
BATCH = 2


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> PrimitiveCase:
    """Build a label-augmented case: the credit reads its target from ``x``."""
    generator = torch.Generator(device=device).manual_seed(seed)

    target = torch.randint(0, LABEL_DIM, (BATCH,), device=device, generator=generator)
    data = torch.randn(
        BATCH, FEATURE_DIM, device=device, dtype=dtype, generator=generator
    )
    onehot = torch.nn.functional.one_hot(target, LABEL_DIM).to(dtype)
    x = torch.cat((data, onehot), dim=-1)

    with seeded_rng(seed):
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=FEATURE_DIM + LABEL_DIM,
                output_dim=LABEL_DIM,
                hidden_dims=(16,),
            )
        )

    activations = [x]
    for layer in geometry._layers:  # type: ignore[attr-defined]
        activations.append(layer(activations[-1]))

    config = {
        "label_dim": LABEL_DIM,
        "ema_beta": 0.0,
        "stream_norm": True,
        "contrast_threshold": 2.0,
        "contrast_objective": "gate",
        "readout_scale": 1.0,
        "sequential_lr": 0.0,
        "target": target,
        "seed": seed,
    }

    return PrimitiveCase(
        weights=[
            layer.weight.data.clone()
            for layer in geometry._layers  # type: ignore[attr-defined]
            if isinstance(layer, torch.nn.Linear)
        ],
        free_activations=activations,
        nudged_activations=list(activations),
        config=config,
        geometry=geometry,
    )
