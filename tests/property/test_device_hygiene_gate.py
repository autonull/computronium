"""Device-transition hygiene gate (TODO28 session-3 defect class).

Every device bug of 2026-09-15 (ntm state, FA feedback matrices, local-
contrastive EMA, tile zero-grad) was invisible to the suite: the tests
run on CPU with synthetic input, while the bugs lived in the CPU→GPU
transition — lazy per-weight state initialized during a CPU dry-run/
probe, then used against CUDA weights at train time. This gate encodes
the runtime contract so the *class* is caught by pytest:

for every viable (dynamics × credit × update) cell:
    1. compose on CPU
    2. one train_step on CPU (forces every lazy init that a dry-run or
       instrument probe would trigger)
    3. move geometry to the accelerator
    4. one train_step there — any device mismatch raises and fails
"""

from __future__ import annotations

import pytest
import torch

from computronium.autoscientist.compose import compose_cell_system
from computronium.autoscientist.proposer import GRID_CREDITS, GRID_UPDATES
from computronium.ontology import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    ParameterUpdateConfig,
    StateDynamicsConfig,
)
from computronium.ontology.system import SystemConfig

pytestmark = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="device-transition gate needs CUDA"
)

_DYNAMICS = (
    "energy_minimization",
    "predictive_settling",
    "error_predictive_coding",
    "spike_integration",
    "instantaneous",
    "diffusion",
    "lazy",
)

_GEOMETRY = {"topology_type": "feedforward", "depth": 2, "hidden_dim": 16}


def _viable_cells() -> list[tuple[str, str, str]]:
    substrate = DigitalSubstrate().config
    cells: list[tuple[str, str, str]] = []
    from computronium.autoscientist.compose import build_geometry_config

    geometry = build_geometry_config(
        _GEOMETRY, input_dim=64, output_dim=10
    )
    for dynamics in _DYNAMICS:
        dcfg = getattr(StateDynamicsConfig, dynamics)()
        for credit in GRID_CREDITS:
            ccfg = getattr(CreditAssignmentConfig, credit)()
            for update in GRID_UPDATES:
                try:
                    ucfg = getattr(ParameterUpdateConfig, update)()
                except TypeError:
                    continue
                try:
                    SystemConfig(
                        substrate=substrate,
                        geometry=geometry,
                        dynamics=dcfg,
                        credit=ccfg,
                        update=ucfg,
                    ).validate()
                except ValueError:
                    continue
                cells.append((dynamics, credit, update))
    return cells


def _id(cell: tuple[str, str, str]) -> str:
    return "|".join(cell)


@pytest.mark.parametrize("cell", _viable_cells(), ids=_id)
def test_cell_survives_cpu_to_cuda_transition(cell: tuple[str, str, str]) -> None:
    dynamics, credit, update = cell
    system = compose_cell_system(
        dynamics=dynamics,
        credit=credit,
        update=update,
        geometry=dict(_GEOMETRY),
        input_dim=64,
        output_dim=10,
    )
    x_cpu = torch.randn(4, 64)
    y_cpu = torch.randint(0, 10, (4,))

    # CPU phase: compose-time probes (dry-run gate, instrument reads)
    # execute here — any lazy per-weight state initializes now.
    system.train_step(x_cpu, y_cpu)

    if not torch.cuda.is_available():
        pytest.skip("CUDA vanished mid-gate")
    system.geometry.to("cuda")
    x = x_cpu.to("cuda")
    y = y_cpu.to("cuda")

    # Accelerator phase: the first real training step. Device-stranded
    # caches raise here — exactly the failure mode that corrupted the
    # 2026-09-15 pilot before this gate existed.
    metrics = system.train_step(x, y)
    loss = metrics["loss"]
    assert loss == loss  # noqa: PLR0124 — NaN means silent numeric break
