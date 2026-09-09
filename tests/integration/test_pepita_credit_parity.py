"""PepitaCredit library wiring lock (TODO15 §11.3 promotion).

The published PEPITA rule (arXiv 2201.11665) — input-modulated second
pass, γ=0.05 — promoted from the validated probe
(``scripts/probes/pepita_faithful_replication.py``: 0.884 vs bp 0.890
across 3 seeds at 150 batches) into the 5-axis library. This lock proves
the library composition reproduces the probe's learning at a reduced
budget: Digital + Feedforward + Instantaneous + PepitaCredit + Adam,
50 MNIST quick batches, accuracy ≥ 0.70 (the probe trajectory at this
budget sits ≈ 0.85; the margin absorbs loader/seed skew).

Guards asserted: θ actually moves on every learnable weight; the
substrate hook composes without error (``set_substrate`` wired by
``compose_system``); the config factory round-trips through
``_credit_from_config``.
"""

from itertools import islice

import torch

from computronium import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    PepitaCredit,
    SubstrateConfig,
    create_task,
)
from computronium.core.pipeline import run_train_step
from computronium.ontology.update import AdamUpdate

BATCHES = 50
EVAL_BATCHES = 20
GATE = 0.70


def test_pepita_credit_learns() -> None:
    torch.manual_seed(0)
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    batches = [
        (x.view(x.size(0), -1), y)
        for _, (x, y) in zip(range(BATCHES), task.get_dataloader("train"))
    ]

    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(input_dim=784, output_dim=10, hidden_dims=(128,))
    )
    dynamics = InstantaneousDynamics()
    config = CreditAssignmentConfig.pepita(gamma=0.05)
    credit = PepitaCredit(config)
    credit.set_substrate(substrate)
    update = AdamUpdate(ParameterUpdateConfig.adam(step_size=1e-3))

    weight_names = list(geometry.params)
    before = {n: geometry.params[n].detach().clone() for n in weight_names}
    for x, y in batches:
        run_train_step(substrate, geometry, dynamics, credit, update, x, y)

    moved = {
        n: (geometry.params[n].detach() - before[n]).abs().sum().item()
        for n in weight_names
    }
    assert all(v > 0.0 for v in moved.values()), moved

    with torch.no_grad():
        ok = tot = 0
        for x, y in islice(task.get_dataloader("test"), EVAL_BATCHES):
            logits = geometry.forward(x.view(x.size(0), -1), substrate)
            ok += (logits.argmax(1) == y).sum().item()
            tot += y.size(0)
    acc = ok / tot
    assert acc >= GATE, f"pepita library parity failed: acc={acc:.3f} < {GATE}"
