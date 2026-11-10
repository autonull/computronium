"""Probe: which credit rules train the transformer (vision) geometry?

The transformer pools ``[B, T, d] -> [B, d]`` before its head, so the
readout's error lives in sample space while every hidden act lives in
sequence space (``B*T``). This probe reports, per credit, whether a single
MNIST training step completes and what it does to the weights.

Run: uv run python scripts/probes/t87_transformer_credit_matrix.py
"""

from __future__ import annotations

import traceback

from computronium.experiment.kernel.evaluate import evaluate_cell
from computronium.experiment.schema.coordinate import Coordinate, Schedule

GEOMETRY = {
    "patch_size": 4,
    "patch_embed_dim": 0,
    "image_hw": [28, 28],
    "in_channels": 1,
    "num_layers": 2,
    "hidden_dim": 32,
    "num_heads": 4,
}

CREDITS = (
    "gradient",
    "backprop",
    "random_projections",
    "homeostatic",
    "target_inversion",
    "temporal_trace",
    "pc_alm",
    "local_goodness",
    "pepita",
)


def _schedule() -> Schedule:
    return Schedule(
        task_id="mnist",
        epochs=1,
        seed=42,
        n_seeds=1,
        batch_limit=4,
        budget_id="t87-probe",
        fidelity="L0",
        device="cpu",
    )


def _coordinate(credit: str) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="causal_transformer",
        dynamics="instantaneous",
        plasticity="null",
        credit=credit,
        update="euclidean",
        params={},
    )


def main() -> None:
    for credit in CREDITS:
        print(f"\n=== credit={credit} ===", flush=True)
        try:
            result = evaluate_cell(
                coordinate=_coordinate(credit),
                schedule=_schedule(),
                geometry=GEOMETRY,
            )
            print(
                f"OK val_acc={result.metrics.get('val_acc')} "
                f"train_loss={result.metrics.get('train_loss')}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {type(exc).__name__}: {str(exc)[:220]}")
            traceback.print_exc(limit=3)


if __name__ == "__main__":
    main()
