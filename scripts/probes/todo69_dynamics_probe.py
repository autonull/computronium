#!/usr/bin/env python3
"""The demo cell's dynamics, measured (TODO69 Phase 5, the dynamics family).

Question: can the dashboard show the *dynamics* of a cell — the settling
trajectory, the Lyapunov spectrum, the energy landscape — from the record
alone, and in how long?

The first answer was no, and the reason is the point of this probe: the
transition the stability analysis built was the identity. The forward pass
was computed and thrown away, and the settle was handed the activity the
state already had, so a feedforward cell's "dynamics" was the identity map
and its spectrum was a row of zeros. The transition is now the system's own
relaxation, one step at a time
(``computronium.experiment.analysis.transition``), and this probe measures
what it gives.

The demo campaign's own cells are feedforward with instantaneous dynamics, so
they have no state to relax: the dashboard measures the nearest cell of the
space that has one, and says which axes it swapped. This probe measures that
cell directly.

Regime: CPU, digits task, quick mode, the demo profile's coordinate
(digital / feedforward / instantaneous / null / gradient / adam,
geometry.hidden_dim=32) for the "no state" case, and digital / recurrent /
energy_minimization / null / gradient / adam for the cell that has one.
Untrained weights: the record does not carry the trained cell, and the
store does not carry it either — the dashboard's payload says so.

Run:
    uv run python scripts/probes/todo69_dynamics_probe.py
"""

from __future__ import annotations

import time

# The demo's own cell: feedforward with an instantaneous pass.
DEMO_COORDINATE = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}

# The nearest cell of the space with a state that moves.
STATEFUL_COORDINATE = {
    "substrate": "digital",
    "geometry": "recurrent",
    "dynamics": "energy_minimization",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}


def compose(coordinate: dict[str, str], shape, device: str):
    """The cell, composed under the demo's parameter budget."""
    from computronium.experiment.kernel.compose import compose_cell_system
    from computronium.experiment.schema.coordinate import Coordinate

    cell = compose_cell_system(
        coordinate=Coordinate(**coordinate, params={}),
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=10_000,
    )
    return cell, cell.system.to(device)


def main() -> int:
    from computronium.domains.factory import create_task
    from computronium.experiment.analysis.transition import build_transition
    from computronium.experiment.kernel.evaluate import task_shape

    device = "cpu"
    task = create_task("digits", device=device, quick_mode=True, num_workers=0)
    task.setup()
    shape = task_shape("digits", device)
    sample_x, _ = next(iter(task.get_dataloader("train")))
    flat = sample_x.to(device).reshape(sample_x.shape[0], -1)

    from computronium.stability import estimate_lyapunov_spectrum

    for name, coordinate in (
        ("the demo's own cell", DEMO_COORDINATE),
        ("the nearest cell with a state", STATEFUL_COORDINATE),
    ):
        started = time.perf_counter()
        _cell, system = compose(coordinate, shape, device)
        transition = build_transition(system, flat)
        print(f"\n{name}: {coordinate['geometry']} · {coordinate['dynamics']}")
        print(f"  composed in {time.perf_counter() - started:.2f}s")
        print(f"  stateful: {transition.stateful}")
        print(f"  {transition.reason}")
        if not transition.stateful:
            continue

        state = transition.initial
        norms = []
        started = time.perf_counter()
        for _ in range(40):
            state = transition.step(state, None)
            norms.append(float(state.activity["x"].norm(dim=-1).mean()))
        print(f"  40 relaxation steps in {time.perf_counter() - started:.2f}s")
        print(f"  the state's size: {norms[0]:.4f} -> {norms[-1]:.4f}")
        print(f"  distinct sizes: {len({round(n, 8) for n in norms})}")

        started = time.perf_counter()
        spectrum = estimate_lyapunov_spectrum(
            transition.step, transition.initial, None, num_vectors=6, num_steps=20
        )
        print(f"  spectrum in {time.perf_counter() - started:.2f}s")
        print(f"  {[round(value, 5) for value in spectrum]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
