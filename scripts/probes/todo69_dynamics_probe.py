#!/usr/bin/env python3
"""The demo cell's dynamics, measured (TODO69 Phase 5, the dynamics family).

Question: can the dashboard show the *dynamics* of a cell the demo run
measured — the settling trajectory, the Lyapunov spectrum, the energy
landscape — from the record alone, and in how long?

The demo campaign's cells are feedforward with instantaneous dynamics, so
the first thing to know is whether the composed system's transition is
anything but a constant. This probe composes the demo's leading cell from
the demo profile's own coordinate, builds the transition the stability
analysis builds, and measures what the dashboard would draw.

Regime: CPU, digits task, quick mode, the demo profile's coordinate
(digital / feedforward / instantaneous / null / gradient / adam,
geometry.hidden_dim=32), param budget 10_000. Untrained weights: the
record does not carry the trained cell, and this probe asks first whether
the *architecture's* transition is worth drawing at all.

Run:
    uv run python scripts/probes/todo69_dynamics_probe.py
"""

from __future__ import annotations

import time

import torch


def build_transition(system, device: str):
    """The transition the stability analysis builds (computronium surface CLI)."""
    from stability.state import CompositeState

    from computronium.core.pipeline import forward_pass
    from computronium.ontology import SystemState

    def transition_fn(state, context):
        with torch.no_grad():
            forward_pass(system.substrate, system.geometry, state.activity["x"])
            settled = system.dynamics.settle(
                SystemState(x=state.activity["x"], y=None),
                system.geometry,
                system.substrate,
                target=None,
            )
            activity = settled.activations
            if isinstance(activity, list):
                activity = activity[0] if activity else state.activity["x"]
            elif activity is None:
                activity = state.activity["x"]
            return CompositeState(activity={"x": activity}, plastic={}, substrate={})

    return transition_fn


def main() -> int:
    from computronium.domains.factory import create_task
    from computronium.experiment.kernel.compose import compose_cell_system
    from computronium.experiment.kernel.evaluate import task_shape
    from computronium.experiment.schema.coordinate import Coordinate

    device = "cpu"
    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={"geometry.hidden_dim": 32},
    )

    started = time.perf_counter()
    task = create_task("digits", device=device, quick_mode=True, num_workers=0)
    task.setup()
    print(f"task setup: {time.perf_counter() - started:.2f}s")

    started = time.perf_counter()
    shape = task_shape("digits", device)
    cell = compose_cell_system(
        coordinate=coordinate,
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=10_000,
    )
    system = cell.system.to(device)
    print(f"compose: {time.perf_counter() - started:.2f}s")
    print(f"params: {cell.param_count}")

    sample_x, _ = next(iter(task.get_dataloader("train")))
    flat = sample_x.to(device).reshape(sample_x.shape[0], -1)
    from stability.state import CompositeState

    init_state = CompositeState(activity={"x": flat}, plastic={}, substrate={})
    transition_fn = build_transition(system, device)

    # 1. The trajectory: the norms of the state over the steps.
    from computronium.stability import measure_settling_time

    started = time.perf_counter()
    steps, norms = measure_settling_time(transition_fn, init_state, None, max_steps=40)
    print(f"settling: {time.perf_counter() - started:.2f}s steps={steps}")
    print(f"  norms[:8]={[round(n, 5) for n in norms[:8]]}")
    print(f"  norms[-4:]={[round(n, 5) for n in norms[-4:]]}")
    print(f"  distinct norms: {len({round(n, 8) for n in norms})}")

    # 2. The Lyapunov spectrum of the transition.
    from computronium.stability import estimate_lyapunov_spectrum

    started = time.perf_counter()
    try:
        spectrum = estimate_lyapunov_spectrum(
            transition_fn, init_state, None, num_vectors=3, num_steps=20
        )
        print(f"lyapunov: {time.perf_counter() - started:.2f}s")
        print(f"  spectrum={[round(value, 5) for value in spectrum]}")
    except Exception as exc:  # ruff: ignore[blind-except] - a probe reports
        print(f"lyapunov failed: {exc}")

    # 3. The energy landscape over the state's PCA slice.
    started = time.perf_counter()
    try:
        energies, attractors = landscape(transition_fn, init_state)
        print(f"landscape: {time.perf_counter() - started:.2f}s")
        print(
            f"  energy min={energies.min():.5f} max={energies.max():.5f} "
            f"span={energies.max() - energies.min():.5f}"
        )
        print(f"  attractors: {attractors[:4]}")
    except Exception as exc:  # ruff: ignore[blind-except] - a probe reports
        print(f"landscape failed: {exc}")

    return 0


def landscape(transition_fn, init_state):
    """The energy over the state's PCA slice, as the analysis computes it."""
    import numpy as np

    from computronium.experiment.analysis import (
        EnergyLandscapeConfig,
        compute_energy_landscape_2d,
    )

    result = compute_energy_landscape_2d(
        transition_fn,
        None,
        init_state,
        config=EnergyLandscapeConfig(grid_resolution=12),
        num_trajectories=4,
        trajectory_length=10,
    )
    return np.asarray(result.energy_values), result.attractor_points


if __name__ == "__main__":
    raise SystemExit(main())
