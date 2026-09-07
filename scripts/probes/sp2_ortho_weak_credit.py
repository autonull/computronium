"""SP2 preview (TODO13b W1 interstitial): does OrthoAdam make weak credit strong?

Pre-registered question (TODO13 §6 SP2): run weak credits (ff, pepita)
under OrthoAdam vs Euclid on MNIST-quick. If weak×OrthoAdam ≈ bp×OrthoAdam,
the finding is "the optimizer is doing the learning; credit only needs a
good-enough direction."

Pre-registered predictions (before any run):
- P1: ff/ortho_adam > ff/euclid by a clear margin (OrthoAdam repairs the
  optimizer axis for weak credit, as it did for bp on 3/4 geometries).
- P2: pepita/ortho_adam > pepita/euclid similarly.
- P3 (the profound branch): ff/ortho_adam ≥ 0.9 × bp/ortho_adam —
  credit strength stops mattering under the right optimizer.

Cell design: hunt_cells.py harness pattern verbatim (mnist quick, 150
batches, 1 epoch, feedforward 784-64-64-10, CPU). Single seed 0 for the
first signal; seeds 1-2 only on the cells that decide P3.

step_semantics discipline: ortho_lr on OrthoAdam's OWN axis (1e-3, the
measured plateau 5e-4–1e-3; 3e-3 the D16 mlp calibration — rung checked
at 1e-3 first, never a borrowed muon grid).
"""

from itertools import islice
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable

import torch

from computronium import (
    AdamUpdate,
    BackpropCredit,
    CreditAssignmentConfig,
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalGoodnessCredit,
    OrthoAdamUpdate,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    compose_system,
)
from computronium.domains.base import DomainTask, TaskSplit
from computronium.domains.factory import create_task
from computronium.ontology.geometry import (
    AttentionGeometry,
    SpatialLattice3DGeometry,
)
from computronium.ontology.update import EuclideanUpdate
from computronium.state import CompositeState

BATCH_CAP = 150
SEEDS = (0, 1, 2)
MLP_DIMS = (784, 10)


def _geometries() -> dict:
    return {
        "attention": lambda: AttentionGeometry(
            GeometryConfig.attention(
                input_dim=784, output_dim=10, hidden_dim=32, num_layers=2, num_heads=4
            )
        ),
        "lattice3d": lambda: SpatialLattice3DGeometry(
            GeometryConfig.spatial_lattice(
                input_dim=784,
                output_dim=10,
                lattice_dims=(4, 3, 3),
                hidden_dims=(2,),
                connectivity_radius=1,
            )
        ),
    }


CELLS: list[tuple[str, str]] = [
    ("ff", "euclid.2"),
    ("ff", "ortho.1e3"),
    ("pepita", "euclid.2"),
    ("pepita", "ortho.1e3"),
    ("bp", "adam1e3"),
    ("bp", "ortho.1e3"),
]


def _credit(name: str):
    if name == "bp":
        return BackpropCredit()
    objective = "ff" if name == "ff" else "pepita"
    return LocalGoodnessCredit(
        CreditAssignmentConfig.local_goodness(
            feedback_scale=0.01, local_objective=objective
        )
    )


def _updates() -> dict[str, Callable]:
    return {
        "euclid.2": lambda: EuclideanUpdate(
            ParameterUpdateConfig.euclidean(step_size=0.2)
        ),
        "ortho.1e3": lambda: OrthoAdamUpdate(
            ParameterUpdateConfig.ortho_adam(step_size=1e-3, ortho_lr=1e-3)
        ),
        "adam1e3": lambda: AdamUpdate(ParameterUpdateConfig.adam(step_size=1e-3)),
    }


def _run(
    credit: str,
    update: str,
    seed: int,
    train_data,
    test_batches,
    geometry_fn=None,
) -> float:
    torch.manual_seed(seed)
    if geometry_fn is None:
        geometry_fn = lambda: FeedforwardGeometry(  # noqa: E731 — small probe default
            GeometryConfig.feedforward(
                input_dim=784, output_dim=10, hidden_dims=(64, 64)
            )
        )
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=geometry_fn(),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=_credit(credit),
        update=_updates()[update](),
    )
    SystemTrainer(
        system=system,
        config=SystemTrainerConfig(max_epochs=1, device="cpu", seed=42),
        train_data=train_data,
    ).fit()
    ok = tot = 0
    with torch.no_grad():
        for batch_x, batch_y in test_batches:
            state = system.dynamics.settle(
                CompositeState(activity={"x": batch_x}, plastic={}, substrate={}),
                system.geometry,
                system.substrate,
                None,
            )
            acts = state.activations
            out = acts[-1] if isinstance(acts, list) else acts
            if out is None:
                raise RuntimeError(  # noqa: TRY003 — probe-local invariant
                    "settle produced no activations"
                )
            ok += (out.argmax(1) == batch_y).sum().item()
            tot += batch_y.size(0)
    return ok / tot


def main() -> int:
    task = cast("DomainTask", create_task("mnist", device="cpu", quick_mode=True))
    task.setup()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap)
    train_data = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in islice(task.get_dataloader(TaskSplit.TRAIN), BATCH_CAP)
    ]
    test_batches = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in task.get_dataloader(TaskSplit.TEST)
        if xb.size(0) == 32
    ]
    print(
        "=== SP2 preview: weak credit x {Euclid, OrthoAdam}, MNIST-quick, 1 epoch ==="
    )
    accs = {}
    for credit, update in CELLS:
        vals = [_run(credit, update, seed, train_data, test_batches) for seed in SEEDS]
        accs[credit, update] = sum(vals) / len(vals)
        per_seed = ", ".join(f"{v:.3f}" for v in vals)
        print(
            f"  {credit:>6} x {update:<10} test acc {accs[credit, update]:.3f}"
            f"  ({per_seed})",
            flush=True,
        )
    ff_gap = accs["ff", "ortho.1e3"] / max(accs["bp", "ortho.1e3"], 1e-9)
    print(
        f"\nP3 ratio mlp ff/ortho ÷ bp/ortho = {ff_gap:.2f} "
        f"(≥0.90 → 'optimizer does the learning')"
    )
    for geom, geometry_fn in _geometries().items():
        print(f"--- {geom} ---")
        for credit, update in (("ff", "ortho.1e3"), ("bp", "ortho.1e3")):
            vals = [
                _run(credit, update, seed, train_data, test_batches, geometry_fn)
                for seed in SEEDS
            ]
            accs[credit, update] = sum(vals) / len(vals)
            per_seed = ", ".join(f"{v:.3f}" for v in vals)
            print(
                f"  {credit:>6} x {update:<10} test acc {accs[credit, update]:.3f}"
                f"  ({per_seed})",
                flush=True,
            )
        gap = accs["ff", "ortho.1e3"] / max(accs["bp", "ortho.1e3"], 1e-9)
        print(f"  P3 ratio ff/ortho ÷ bp/ortho = {gap:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
