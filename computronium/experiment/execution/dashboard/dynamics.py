"""The cell's own dynamics, measured for the dashboard (TODO69).

Every other view on the stage draws the *bookkeeping* of a run: what was
measured, what was refused, what it cost. This one draws the system being
measured — where its state goes, whether it settles, how wide the set of
states that come back to it is, and what its energy looks like over the
slice its own trajectory crosses.

Two rules make the pictures worth reading.

**The map is the system's own.** The transition is the relaxation the cell's
own settle performs, one step at a time, over the cell's own activity
(``computronium.experiment.analysis.transition``). A map borrowed from
another dynamics measures a system that does not exist, and the first
version of this measured the identity and reported a spectrum of zeros.

**The cell says what it is.** The run's own cells are usually feedforward
with an instantaneous pass, and a cell like that has no state that moves.
Rather than draw a picture of nothing, the server repairs the run's
coordinate — swapping the dynamics for one that relaxes, and the geometry
for a recurrent one when the basin needs it — and says in the payload
exactly which axes it swapped. A picture of a cell the run never measured
is worth having only if the picture says so.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium.experiment.schema.coordinate import Coordinate

logger = logging.getLogger(__name__)

# How many relaxation steps the trajectory is drawn over.
TRAJECTORY_STEPS = 120

# How many steps the Lyapunov spectrum is measured over, and how many
# directions it carries.
SPECTRUM_STEPS = 40
SPECTRUM_VECTORS = 8

# How many starts each radius of the basin is measured from, and how many
# strays' paths the basin draws.
BASIN_SAMPLES = 6
BASIN_PATHS = 2

# How far the basin is asked, and how many steps each radius gets.
BASIN_RADII = (0.1, 0.5, 1.0)
BASIN_STEPS = 60

# The landscape's grid: how many points on each side.
LANDSCAPE_RESOLUTION = 21
LANDSCAPE_RANGE = 3.0

# The dynamics that relax a state, and so have one to show.
ITERATIVE_DYNAMICS = (
    "energy_minimization",
    "predictive_settling",
    "error_predictive_coding",
    "pc_alm",
    "spike_integration",
    "diffusion",
    "lazy",
)

# The credits a relaxing dynamics accepts.
LOCAL_CREDITS = ("thermodynamic_contrast", "local_goodness", "forward_only")

# The geometries that hold a state, and so can have a basin. The command
# that measures a basin refuses a cell without one, and the dashboard reads
# the same rule from the server rather than deciding for itself.
RECURRENT_GEOMETRIES = ("recurrent", "tile_mesh", "nca", "ntm")


def _coordinate_of(record: Any) -> dict[str, str]:
    """The coordinate of a record, as the dashboard knows it."""
    return {
        "substrate": record.substrate,
        "geometry": record.geometry,
        "dynamics": record.dynamics,
        "plasticity": record.plasticity,
        "credit": record.credit,
        "update": record.update,
    }


def _as_coordinate(values: dict[str, str]) -> Coordinate:
    """The coordinate the system composes from."""
    from computronium.experiment.schema.coordinate import Coordinate

    return Coordinate(
        substrate=values["substrate"],
        geometry=values["geometry"],
        dynamics=values["dynamics"],
        plasticity=values["plasticity"],
        credit=values["credit"],
        update=values["update"],
        params={},
    )


def _composes(values: dict[str, str], shape: Any, budget: int) -> Any:
    """The composed cell, or ``None`` when the system refuses the coordinate."""
    from computronium.experiment.kernel.compose import compose_cell_system

    try:
        cell = compose_cell_system(
            coordinate=_as_coordinate(values),
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=budget,
        )
    except Exception as exc:  # ruff: ignore[blind-except] - the system refuses
        logger.debug("the cell %s was refused: %s", values, exc)
        return None
    return cell


def _axis_values(axis: str) -> list[str]:
    """The values an axis takes, in registry order."""
    from computronium.experiment.schema.axis import AXES_REGISTRIES
    from computronium.experiment.schema.harvest import AXIS_KIND_ORDER

    kind = next(candidate for candidate in AXIS_KIND_ORDER if candidate.value == axis)
    return [spec.name for spec in AXES_REGISTRIES[kind].values() if spec.available]


def candidate_cells(values: dict[str, str]) -> list[tuple[dict[str, str], list[str]]]:
    """The cells worth measuring, nearest the run's own first.

    The run's own cell is tried first. When it has no state that moves, the
    dynamics is swapped for one that relaxes, and the credit for one that
    dynamics accepts; the geometry is swapped for a recurrent one so that
    the basin has something to be.

    Returns:
        Each candidate coordinate, and the axes it was repaired on.
    """
    dynamics_values = _axis_values("dynamics")
    credit_values = _axis_values("credit")

    geometries = (
        [values["geometry"]]
        if values["geometry"] in RECURRENT_GEOMETRIES
        else ["recurrent", values["geometry"]]
    )
    candidates: list[tuple[dict[str, str], list[str]]] = [(dict(values), [])]
    for geometry in geometries:
        for dynamics in dynamics_values:
            if dynamics not in ITERATIVE_DYNAMICS:
                continue
            for credit in (values["credit"], *LOCAL_CREDITS):
                if credit not in credit_values:
                    continue
                candidate = dict(values)
                candidate["geometry"] = geometry
                candidate["dynamics"] = dynamics
                candidate["credit"] = credit
                repairs = [
                    name
                    for name, before, after in (
                        ("geometry", values["geometry"], geometry),
                        ("dynamics", values["dynamics"], dynamics),
                        ("credit", values["credit"], credit),
                    )
                    if before != after
                ]
                if (candidate, repairs) not in candidates:
                    candidates.append((candidate, repairs))
    return candidates


def _state_energy(system: Any, acts: Sequence[Any]) -> float:
    """The cell's own energy of a state, in the cell's own units.

    The energy is the one the cell's own dynamics compute — the Hopfield
    energy of an energy-based cell, the prediction energy of a predictive
    one — so a landscape drawn over it is a picture of that cell and not of
    a proxy. A dynamics that cannot say is asked for its prediction error
    instead, which every layered cell agrees on.
    """
    from computronium.ontology import SystemState

    try:
        settled = SystemState(x=acts[0], y=None, activations=list(acts))
        return float(system.dynamics.compute_energy(settled, system.geometry).item())
    except Exception:  # ruff: ignore[blind-except] - the cell may not say
        return _prediction_error(system, acts)


def _prediction_error(system: Any, acts: Sequence[Any]) -> float:
    """The cell's own prediction error: the error its relaxation drives down.

    This is the free energy a predictive cell relaxes, and the quantity
    every cell's own layers agree on. It is a function of the state, which
    is what a landscape needs: the same number at every point of the slice.
    """
    import torch

    from computronium.ontology._settle_kernel import extract_layered_params

    params = extract_layered_params(system.geometry)
    if params is None:
        return 0.0
    op = system.substrate.get_forward_operator()
    total = torch.zeros((), device=acts[0].device, dtype=acts[0].dtype)
    for index, weight in enumerate(params.weights):
        if index + 1 >= len(acts):
            break
        prediction = op(acts[index + 1], weight.T)
        total = total + (acts[index] - prediction).pow(2).sum()  # ruff: ignore[non-augmented-assignment]
    return float(total.item())


def _trajectory(
    transition: Any, system: Any
) -> tuple[list[Any], list[float], list[float], Any]:
    """The cell's own path, and what happened to it on the way.

    Returns:
        The mean state at each step, the state's size, the prediction error
        the relaxation was driving down, and the state it ended in.
    """
    state = transition.initial
    points: list[Any] = []
    norms: list[float] = []
    errors: list[float] = []
    for _ in range(TRAJECTORY_STEPS):
        state = transition.step(state, None)
        packed = state.activity["x"]
        points.append(packed.mean(dim=0).cpu().numpy().copy())
        norms.append(float(packed.norm(dim=-1).mean()))
        errors.append(
            _state_energy(system, [transition.clamped, *transition.layers(state)])
        )
    return points, norms, errors, state


def _directions(points: list[Any]) -> tuple[Any, Any, Any, float, list[list[float]]]:
    """The two directions the state moved in, and where it started from.

    The first is the direction the trajectory itself took; the second is
    across it, so the landscape has a floor to stand on rather than a
    line.
    """
    import numpy as np

    array = np.asarray(points)
    centred = array - array.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(centred, full_matrices=False)
    first = vt[0]
    second = vt[1] if len(vt) > 1 else np.zeros_like(first)
    second = second - float(np.dot(second, first)) * first  # ruff: ignore[non-augmented-assignment]
    length = float(np.linalg.norm(second))
    if length > 1e-12:
        second = second / length  # ruff: ignore[non-augmented-assignment]
    origin = array[-1]
    scale = float(np.linalg.norm(array[0] - origin)) or 1.0
    axis_one = first * scale
    axis_two = second * scale
    offsets = array - origin
    path = np.stack([offsets @ axis_one, offsets @ axis_two], axis=1).tolist()
    return origin, axis_one, axis_two, scale, path


def _landscape(
    system: Any,
    transition: Any,
    origin: Any,
    axis_one: Any,
    axis_two: Any,
    scale: float,
) -> dict[str, Any]:
    """The cell's own prediction error over the slice the trajectory crosses.

    The slice is the trajectory's own two directions, through the state the
    trajectory ended in, so the picture is of the neighbourhood the cell
    actually visited.
    """
    import torch

    widths = list(transition.widths)
    span = LANDSCAPE_RANGE * scale
    grid: list[list[float]] = []
    xs: list[float] = []
    ys: list[float] = []
    for i in range(LANDSCAPE_RESOLUTION):
        a = -span + (2 * span) * i / (LANDSCAPE_RESOLUTION - 1)
        row: list[float] = []
        for j in range(LANDSCAPE_RESOLUTION):
            b = -span + (2 * span) * j / (LANDSCAPE_RESOLUTION - 1)
            probe = torch.as_tensor(
                origin + a * axis_one + b * axis_two, dtype=torch.float32
            ).reshape(1, -1)
            layers = list(torch.split(probe, widths, dim=-1))
            row.append(_state_energy(system, [transition.clamped[:1], *layers]))
        grid.append(row)
        xs.append(float(a))
    for j in range(LANDSCAPE_RESOLUTION):
        ys.append(float(-span + (2 * span) * j / (LANDSCAPE_RESOLUTION - 1)))
    return {"grid": grid, "x": xs, "y": ys, "span": float(span)}


def _basin(
    transition: Any, attractor: Any
) -> tuple[dict[float, float], list[dict[str, Any]]]:
    """How much of the neighbourhood comes back, and how the strays went.

    The fraction is the stability package's own: the share of perturbed
    states that return to the attractor. The paths are drawn as well,
    because a picture of three empty bars says less than a picture of the
    states that did not come back.

    Returns:
        The fraction that returns, per radius, and the path each stray took.
    """
    import torch
    from stability.state import CompositeState

    from computronium.stability import estimate_basin_stability

    fractions: dict[float, float] = {}
    paths: list[dict[str, Any]] = []
    generator = torch.Generator().manual_seed(7)
    for radius in BASIN_RADII:
        fractions[radius] = estimate_basin_stability(
            transition.step,
            attractor,
            None,
            num_samples=BASIN_SAMPLES,
            perturbation_radius=radius,
            max_steps=BASIN_STEPS,
        )
        for sample in range(BASIN_PATHS):
            direction = torch.randn(attractor.activity["x"].shape, generator=generator)
            direction = direction / (direction.norm(dim=-1, keepdim=True) + 1e-8)  # ruff: ignore[non-augmented-assignment]
            start = attractor.activity["x"] + direction * radius
            state = CompositeState(activity={"x": start}, plastic={}, substrate={})
            distances: list[float] = []
            for _ in range(BASIN_STEPS):
                state = transition.step(state, None)
                distances.append(
                    float(
                        (state.activity["x"] - attractor.activity["x"])
                        .norm(dim=-1)
                        .mean()
                    )
                )
            paths.append({
                "radius": radius,
                "sample": sample,
                "distances": distances,
                "returned": distances[-1] < 1e-3,
            })
    return fractions, paths


def _verdict(settles: bool, largest: float, widest: float) -> str:
    """What the three measurements say together, in one sentence.

    The spectrum samples a handful of directions out of a state that has
    hundreds, so a spectrum that contracts everywhere is not on its own
    enough to say the state settles: the basin is the other half of the
    answer, and a state whose neighbourhood never comes back has not
    settled whatever the sampled directions do.
    """
    if settles and widest > 0:
        return (
            f"The state settles: its fastest direction still contracts "
            f"({largest:.4f}), and {widest:.0%} of the states near it come back."
        )
    if settles:
        return (
            f"The directions sampled contract ({largest:.4f}), but nothing "
            f"comes back: the state does not settle in the neighbourhood "
            f"around it."
        )
    return (
        f"The state does not settle: one direction grows "
        f"({largest:.4f} per step), and only {widest:.0%} of the states near "
        f"it come back."
    )


def _kinematics(system: Any, transition: Any) -> dict[str, Any]:
    """The four measurements, and the state they were measured from."""
    from computronium.stability import estimate_lyapunov_spectrum

    points, norms, errors, final = _trajectory(transition, system)
    origin, axis_one, axis_two, scale, path = _directions(points)
    spectrum = estimate_lyapunov_spectrum(
        transition.step,
        transition.initial,
        None,
        num_vectors=SPECTRUM_VECTORS,
        num_steps=SPECTRUM_STEPS,
    )
    basin, paths = _basin(transition, final)
    landscape = _landscape(system, transition, origin, axis_one, axis_two, scale)
    return {
        "path": path,
        "norm": norms,
        "error": errors,
        "span": float(LANDSCAPE_RANGE * scale),
        "spectrum": spectrum,
        "basin": basin,
        "paths": paths,
        "landscape": landscape,
    }


def _measure(system: Any, transition: Any) -> dict[str, Any]:
    """The cell's own dynamics, measured.

    Returns:
        The trajectory, the spectrum, the basin and the landscape, and the
        plain sentence that says what they mean together.
    """
    found = _kinematics(system, transition)
    spectrum = found["spectrum"]
    basin = found["basin"]
    largest = max(spectrum) if spectrum else 0.0
    widest = max(basin.values()) if basin else 0.0
    settles = largest < 0.0

    return {
        "trajectory": {
            "steps": TRAJECTORY_STEPS,
            "path": found["path"],
            "norm": found["norm"],
            "error": found["error"],
            "span": found["span"],
            "axes": ["the direction the state moved", "the direction across it"],
        },
        "spectrum": spectrum,
        "basin": {
            "radii": list(BASIN_RADII),
            "stability": [basin.get(radius, 0.0) for radius in BASIN_RADII],
            "paths": found["paths"],
        },
        "landscape": found["landscape"],
        "settles": settles,
        "largest_exponent": largest,
        "widest_basin": widest,
        "verdict": _verdict(settles, largest, widest),
    }


def measure_cell(
    values: dict[str, str],
    task_id: str,
    *,
    budget: int = 10_000,
    device: str = "cpu",
) -> dict[str, Any]:
    """One cell's own dynamics, measured.

    Args:
        values: The coordinate, axis by axis.
        task_id: The task the cell would be measured on.
        budget: The parameter ceiling the cell is composed under.
        device: Where the cell is composed.

    Returns:
        The payload the browser draws: the cell, the measurements, and the
        plain reason when the cell has no dynamics to show.
    """
    from computronium.domains.factory import create_task
    from computronium.experiment.analysis.transition import build_transition
    from computronium.experiment.kernel.evaluate import task_shape

    started = time.perf_counter()
    task = create_task(task_id, device=device, quick_mode=True, num_workers=0)
    task.setup()
    shape = task_shape(task_id, device)
    cell = _composes(values, shape, budget)
    if cell is None:
        return {
            "cell": {"coordinate": values},
            "stateful": False,
            "reason": "The system refuses this cell: it does not compose.",
            "verdict": "This cell does not compose, so it has no dynamics to show.",
        }
    system = cell.system.to(device)

    from computronium.domains.base import TaskSplit

    sample_x, _ = next(iter(task.get_dataloader(TaskSplit.TRAIN)))
    flat = sample_x.to(device).reshape(sample_x.shape[0], -1)
    transition = build_transition(system, flat)
    if not transition.stateful:
        return {
            "cell": {"coordinate": values},
            "stateful": False,
            "reason": transition.reason,
            "verdict": "This cell has no state that moves, so it has no dynamics to show.",
        }

    measured = _measure(system, transition)
    measured.update({
        "cell": {
            "coordinate": values,
            "params": int(cell.param_count),
        },
        "stateful": True,
        "reason": transition.reason,
        "trained": False,
        "task": task_id,
        "elapsed_s": round(time.perf_counter() - started, 2),
    })
    return measured


def _train_and_measure_cell(
    values: dict[str, str],
    task_id: str,
    *,
    budget: int = 10_000,
    device: str = "cpu",
    epochs: int = 10,
) -> dict[str, Any]:
    """Train a cell, then measure its dynamics.

    Args:
        values: The coordinate, axis by axis.
        task_id: The task the cell is trained and measured on.
        budget: The parameter ceiling the cell is composed under.
        device: Where the cell is composed and trained.
        epochs: Number of training epochs.

    Returns:
        The payload the browser draws: the cell, the measurements, and the
        plain reason when the cell has no dynamics to show.
    """
    from computronium.domains.factory import create_task
    from computronium.experiment.analysis.transition import build_transition
    from computronium.experiment.kernel.evaluate import (
        SystemTrainer,
        SystemTrainerConfig,
        _resolve_device,
        task_shape,
    )

    started = time.perf_counter()
    task = create_task(task_id, device=device, quick_mode=True, num_workers=0)
    task.setup()
    shape = task_shape(task_id, device)
    cell = _composes(values, shape, budget)
    if cell is None:
        return {
            "cell": {"coordinate": values},
            "stateful": False,
            "reason": "The system refuses this cell: it does not compose.",
            "verdict": "This cell does not compose, so it has no dynamics to show.",
        }
    system = cell.system.to(device)

    from computronium.domains.base import TaskSplit

    sample_x, _ = next(iter(task.get_dataloader(TaskSplit.TRAIN)))
    flat = sample_x.to(device).reshape(sample_x.shape[0], -1)
    transition = build_transition(system, flat)
    if not transition.stateful:
        return {
            "cell": {"coordinate": values},
            "stateful": False,
            "reason": transition.reason,
            "verdict": "This cell has no state that moves, so it has no dynamics to show.",
        }

    # Train the cell
    resolved_device = _resolve_device(device)
    config = SystemTrainerConfig(
        max_epochs=epochs,
        device=resolved_device,
        seed=42,
        limit_train_batches=None,
        limit_val_batches=None,
        track_flops=False,
        track_memory=False,
        deterministic=False,
        precision="fp32",
        checkpoint_every_n=0,
    )
    trainer = SystemTrainer(
        system=system,
        config=config,
        train_data=task.get_dataloader(TaskSplit.TRAIN),
        val_data=task.get_dataloader(TaskSplit.VAL),
    )
    trainer.fit()
    # The system is now trained; measure its dynamics
    measured = _measure(system, transition)
    trainer.close()
    measured.update({
        "cell": {
            "coordinate": values,
            "params": int(cell.param_count),
        },
        "stateful": True,
        "reason": transition.reason,
        "trained": True,
        "task": task_id,
        "epochs": epochs,
        "elapsed_s": round(time.perf_counter() - started, 2),
    })
    return measured


def run_trained_dynamics(
    store: Any,
    run_id: str,
    *,
    budget: int = 10_000,
    device: str = "cpu",
    epochs: int = 10,
) -> dict[str, Any]:
    """The run's cell, trained first, then its dynamics measured.

    The run's first measured cell is the starting point. When that cell has
    no state that moves, the nearest cell that does is trained and measured
    instead, and the payload names the axes that were swapped.

    The training is expensive, so the result is cached by the caller.
    """
    records = list(store.query_records(run_id=run_id))
    if not records:
        return {
            "run_id": run_id,
            "stateful": False,
            "reason": "This run measured nothing, so it has no cell to show.",
            "verdict": "This run measured nothing, so it has no dynamics to show.",
        }
    record = records[0]
    values = _coordinate_of(record)
    task_id = record.schedule.task_id or "digits"

    from computronium.domains.factory import create_task
    from computronium.experiment.kernel.evaluate import task_shape

    task = create_task(task_id, device=device, quick_mode=True, num_workers=0)
    task.setup()
    shape = task_shape(task_id, device)

    refused: list[str] = []
    still: list[str] = []
    for candidate, repairs in candidate_cells(values):
        cell = _composes(candidate, shape, budget)
        if cell is None:
            refused.append(f"{candidate['geometry']}/{candidate['dynamics']}")
            continue
        payload = _train_and_measure_cell(candidate, task_id, budget=budget, device=device, epochs=epochs)
        if not payload.get("stateful"):
            # The cell composes but has no state that moves: the next
            # candidate is the one worth measuring.
            still.append(f"{candidate['geometry']}/{candidate['dynamics']}")
            continue
        payload["run_id"] = run_id
        payload["cell"] = {
            **(payload.get("cell") or {}),
            "coordinate": candidate,
            "repairs": repairs,
            "measured_by_run": not repairs,
            "run_cell": values,
        }
        if refused:
            payload["refused"] = refused
        if still:
            payload["without_state"] = still
        return payload

    return {
        "run_id": run_id,
        "stateful": False,
        "reason": "No cell of this run's space has a state that moves.",
        "verdict": "No cell of this run's space has a state that moves.",
        "refused": refused,
    }


def run_dynamics(
    store: Any,
    run_id: str,
    *,
    budget: int = 10_000,
    device: str = "cpu",
) -> dict[str, Any]:
    """The run's own cell, and the dynamics it does or does not have.

    The run's first measured cell is the starting point. When that cell has
    no state that moves, the nearest cell that does is measured instead,
    and the payload names the axes that were swapped.
    """
    records = list(store.query_records(run_id=run_id))
    if not records:
        return {
            "run_id": run_id,
            "stateful": False,
            "reason": "This run measured nothing, so it has no cell to show.",
            "verdict": "This run measured nothing, so it has no dynamics to show.",
        }
    record = records[0]
    values = _coordinate_of(record)
    task_id = record.schedule.task_id or "digits"

    from computronium.domains.factory import create_task
    from computronium.experiment.kernel.evaluate import task_shape

    task = create_task(task_id, device=device, quick_mode=True, num_workers=0)
    task.setup()
    shape = task_shape(task_id, device)

    refused: list[str] = []
    still: list[str] = []
    for candidate, repairs in candidate_cells(values):
        cell = _composes(candidate, shape, budget)
        if cell is None:
            refused.append(f"{candidate['geometry']}/{candidate['dynamics']}")
            continue
        payload = measure_cell(candidate, task_id, budget=budget, device=device)
        if not payload.get("stateful"):
            # The cell composes but has no state that moves: the next
            # candidate is the one worth measuring.
            still.append(f"{candidate['geometry']}/{candidate['dynamics']}")
            continue
        payload["run_id"] = run_id
        payload["cell"] = {
            **(payload.get("cell") or {}),
            "coordinate": candidate,
            "repairs": repairs,
            "measured_by_run": not repairs,
            "run_cell": values,
        }
        if refused:
            payload["refused"] = refused
        if still:
            payload["without_state"] = still
        return payload

    return {
        "run_id": run_id,
        "stateful": False,
        "reason": "No cell of this run's space has a state that moves.",
        "verdict": "No cell of this run's space has a state that moves.",
        "refused": refused,
    }


__all__ = [
    "BASIN_RADII",
    "ITERATIVE_DYNAMICS",
    "LOCAL_CREDITS",
    "candidate_cells",
    "measure_cell",
    "run_dynamics",
    "run_trained_dynamics",
]
