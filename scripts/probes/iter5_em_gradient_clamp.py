import sys

import torch

import computronium.ontology.update as U
from computronium.autoscientist.compose import compose_cell_system
from computronium.core.system_trainer.train_task import flat_input_dim
from computronium.domains.factory import create_task
from computronium.utils import seed_everything

BATCHES = int(sys.argv[1]) if len(sys.argv) > 1 else 200
MULTIPLIERS = [float(m) for m in sys.argv[2].split(",")] if len(sys.argv) > 2 else [
    0.5,
    0.05,
]

t = create_task("mnist", device="cpu", batch_size=64, quick_mode=True)
t.setup()
IN = flat_input_dim(t.input_dim, "mnist")
base = dict(U._STEP_SIZE_OVERRIDES)

for mult in MULTIPLIERS:
    U._STEP_SIZE_OVERRIDES[("energy_minimization", "gradient")] = mult
    seed_everything(42)
    s = compose_cell_system(
        dynamics="energy_minimization", credit="gradient", update="riemannian_orthogonal",
        geometry={"topology_type": "feedforward", "depth": 4, "hidden_dim": 20},
        input_dim=IN, output_dim=t.output_dim,
    )
    losses, accs, energies = [], [], []
    for i, (x, y) in enumerate(t.train_dataloader):
        m = s.train_step(x.reshape(x.size(0), -1), y)
        losses.append(float(m["loss"]))
        accs.append(float(m.get("free_accuracy", 0.0)))
        energies.append(float(m.get("energy", 0.0)))
        if not torch.isfinite(torch.tensor(losses[-1])) or i >= BATCHES - 1:
            break
    clamps = getattr(s.dynamics, "_energy_clamp_count", 0)
    print(
        f"mult={mult:<6} clamps={clamps:<6} min_loss={min(losses):.4g} "
        f"last_loss={losses[-1]:.4g} last_acc={accs[-1]:.3f} "
        f"min_energy={min(energies):.4g} max_energy={max(energies):.4g}",
        flush=True,
    )

U._STEP_SIZE_OVERRIDES.clear()
U._STEP_SIZE_OVERRIDES.update(base)
