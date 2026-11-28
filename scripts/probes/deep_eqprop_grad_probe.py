"""Deep-settle EqProp parameter deltas (TODO108 W53).

The composed EqProp system's credit applies a parameter delta through the
update step; it never populates autograd ``.grad``. This probe measures the
first-layer delta at depths 10/50/100 and supports the tracked quantity in
``tests/property/test_scaling_invariants.py``.
"""

import torch

from computronium.models.native.eqprop_native import create_native_eqprop_mlp

for depth in (10, 50, 100):
    torch.manual_seed(0)
    model = create_native_eqprop_mlp(
        input_dim=64, hidden_dim=64, output_dim=10, beta=0.5, settle_steps=depth
    )
    x = torch.randn(4, 64)
    y = torch.randint(0, 10, (4,))
    before = {name: p.detach().clone() for name, p in model.geometry.params.items()}
    model.train()
    model.train_step(x, y)
    print(f"depth={depth}")
    for name, param in model.geometry.params.items():
        delta = (param.detach() - before[name]).abs().mean().item()
        print(f"  {name:20s} delta={delta:.3e}")
