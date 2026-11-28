"""EP vs BPTT parity probe for the tile EP rule (TODO108 W53).

Measures per-parameter and aggregate direction agreement between the
contrastive (hard-clamp) tile update and the BPTT descent direction on the
same parameters. Supports the boundary recorded in
``tests/property/biology/test_biology_axioms.py``.
"""

import torch

from computronium.core.local_learning.builder import TileAlgorithm, TileAlgorithmConfig


def fixture():
    torch.manual_seed(42)
    input_dim, hidden_dim, output_dim = 8, 8, 4
    x = torch.randn(32, input_dim)
    y = torch.randint(0, output_dim, (32,))
    for c in range(output_dim):
        mask = y == c
        if mask.any():
            d = torch.randn(input_dim)
            d = d / d.norm() * 1.5
            x[mask] += d * 0.5
    return x, y, input_dim, hidden_dim, output_dim


def model_for(task):
    _, _, i, h, o = task
    cfg = TileAlgorithmConfig(
        input_dim=i,
        output_dim=o,
        neurons_per_tile=h,
        tiles_per_layer=1,
        num_hidden_layers=1,
        algorithm="ep",
        mode="ep",
        free_steps=20,
        nudged_steps=20,
        learning_rate=0.01,
        beta=0.5,
        step_size=0.1,
    )
    m = TileAlgorithm(cfg)
    m.convergence_threshold = 1e-4
    m.convergence_start = 5
    return m


task = fixture()
x, y = task[0][:16], task[1][:16]
m = model_for(task)
before = {n: p.detach().clone() for n, p in m.named_parameters()}
m.train()
m.local_update(x, y)
delta = {n: p.detach() - before[n] for n, p in m.named_parameters()}
m.zero_grad()
torch.nn.functional.cross_entropy(m(x), y).backward()
bptt = {n: -p.grad.detach() for n, p in m.named_parameters() if p.grad is not None}
shared = [n for n in delta if n in bptt and delta[n].norm() > 0]
cos = {
    n: (
        (delta[n].flatten() @ bptt[n].flatten()) / (delta[n].norm() * bptt[n].norm())
    ).item()
    for n in shared
}
agg = torch.cat([delta[n].flatten() for n in shared]) @ torch.cat([
    bptt[n].flatten() for n in shared
])
agg /= (
    torch.cat([delta[n].flatten() for n in shared]).norm()
    * torch.cat([bptt[n].flatten() for n in shared]).norm()
)
print("shared:", shared)
print("per-param:", {k: round(v, 3) for k, v in cos.items()})
print(
    "aggregate:",
    round(agg.item(), 4),
    "max:",
    round(max(cos.values()), 4),
    "min:",
    round(min(cos.values()), 4),
)
