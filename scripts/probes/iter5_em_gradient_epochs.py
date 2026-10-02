import sys

import torch
from computronium.autoscientist.compose import compose_cell_system

import computronium.ontology.update as U
from computronium.core.system_trainer.train_task import flat_input_dim
from computronium.domains.factory import create_task
from computronium.utils import seed_everything

EPOCHS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
MULT = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
DYN = sys.argv[3] if len(sys.argv) > 3 else "energy_minimization"
CRED = sys.argv[4] if len(sys.argv) > 4 else "gradient"
UPD = sys.argv[5] if len(sys.argv) > 5 else "riemannian_orthogonal"
LR = float(sys.argv[6]) if len(sys.argv) > 6 else 1e-3

t = create_task("mnist", device="cpu", batch_size=64, quick_mode=True)
t.setup()
IN = flat_input_dim(t.input_dim, "mnist")
U._STEP_SIZE_OVERRIDES[DYN, CRED] = MULT
seed_everything(42)
s = compose_cell_system(
    dynamics=DYN,
    credit=CRED,
    update=UPD,
    lr=LR,
    geometry={"topology_type": "feedforward", "depth": 4, "hidden_dim": 20},
    input_shape=(IN,),
    output_dim=t.output_dim,
)
loader = t.train_dataloader
for epoch in range(EPOCHS):
    losses, accs, energies = [], [], []
    prev = getattr(s.dynamics, "_energy_clamp_count", 0)
    for i, (x, y) in enumerate(loader):
        m = s.train_step(x.reshape(x.size(0), -1), y)
        losses.append(float(m["loss"]))
        accs.append(float(m.get("free_accuracy", 0.0)))
        energies.append(float(m.get("energy", 0.0)))
        if not torch.isfinite(torch.tensor(losses[-1])):
            break
    clamps = getattr(s.dynamics, "_energy_clamp_count", 0) - prev
    print(
        f"{DYN}|{CRED}|{UPD}|lr={LR} mult={MULT} epoch={epoch} batches={len(losses)} "
        f"clamps={clamps} last_loss={losses[-1]:.4g} last_acc={accs[-1]:.3f} "
        f"min_energy={min(energies):.4g}",
        flush=True,
    )
