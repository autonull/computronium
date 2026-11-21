"""Probe: the capability rung at the row's priced cell (TODO97 S5j).

The 1-epoch / 64-batch rung failed eight rows. This probe runs the same rows at
their map box's ``epochs`` and ``batch_limit`` to separate a budget failure
from a primitive failure. It informs the S5j close and the defects it files.

Run:
    uv run python scripts/probes/s5j_capability_price.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.train_task import train_on_task
from computronium.domains.base import DomainType
from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.sec_loop import _is_legal, screen_coordinate
from computronium.primitives.registry import list_primitives

CASES = (
    ("primitive.credit_assignment.forward_tangent", "vision", "mnist"),
    ("primitive.credit_assignment.temporal_trace", "sequence", "char_ngram"),
    ("primitive.geometry.ntm", "sequence", "char_ngram"),
    ("primitive.parameter_update.bayesian_online", "sequence", "char_ngram"),
    ("primitive.parameter_update.quantized_adam", "neuromorphic", "spiking_mnist"),
    ("primitive.plasticity.temporal_psi", "sequence", "char_ngram"),
    ("primitive.state_dynamics.diffusion", "sequence", "char_ngram"),
    ("primitive.geometry.recurrent", "sequence", "char_ngram"),
)


def _map(family: str) -> Path:
    return (
        Path("results/sec/map.json")
        if family == "vision"
        else Path(f"results/sec_{family}/map.json")
    )


def _input_shape(task) -> tuple[int, ...]:
    declared = task.input_dim
    return tuple(declared) if isinstance(declared, (tuple, list)) else (1, declared)


def run(primitive: str, family: str, task_id: str) -> dict:
    spec = next(spec for spec in list_primitives() if spec.id == primitive)
    row = json.loads(_map(family).read_text())["primitives"][primitive]
    box = row["box"]
    coord = screen_coordinate(
        box, spec.axis, str(box.get(spec.axis) or primitive.rsplit(".", 1)[-1])
    )
    legal, refusal = _is_legal(coord, task_id)
    if not legal:
        return {"primitive": primitive, "legal": False, "reason": refusal}

    task = create_task(task_id, quick_mode=True, batch_size=box["batch_size"])
    task.setup()
    cell = compose_cell_system(
        coordinate=coord,
        geometry={},
        input_shape=_input_shape(task),
        output_dim=task.output_dim,
        task=task,
    )
    config = SystemTrainerConfig(
        max_epochs=box["epochs"],
        batch_size=box["batch_size"],
        device="cpu",
        track_energy=False,
        track_flops=False,
        track_memory=False,
        log_every_n_epochs=box["epochs"],
    )
    started = time.time()
    if task.domain_type == DomainType.GRAPH:
        from computronium.core.system_trainer import GraphSystemTrainer

        GraphSystemTrainer(cell.system, config, task, val_data=task).fit()
    else:
        train_on_task(
            lambda *_, **__: cell.system,
            task,
            config,
            batches_per_epoch=box["batch_limit"] or None,
        )
    metrics = task.evaluate(cell.system)
    return {
        "primitive": primitive,
        "legal": True,
        "epochs": box["epochs"],
        "batch_limit": box["batch_limit"],
        "batch_size": box["batch_size"],
        "walltime_s": round(time.time() - started, 1),
        "accuracy": metrics.accuracy,
        "perplexity": metrics.perplexity,
        "chance": 1.0 / task.output_dim,
    }


for case in CASES:
    print(json.dumps(run(*case), default=str))
