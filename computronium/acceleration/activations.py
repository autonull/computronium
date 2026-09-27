"""The activation table and its derivative, in one place.

Three modules in this package each carried their own copy of the same four-row
table — `fa_kernels._apply_activation_derivative`, `mep_kernels._activation_deriv`
and `backprop_kernels._activation_deriv` — and the copies had drifted. The
tanh branch of the backprop copy reads `1 - h**2`, which is only right if `h`
is the layer's *output*; the other two read `1 - tanh(x)**2`, which requires the
*input*. Both spellings produce a plausible number, which is how §4.5's fourth
defect (`1 - mu**2` for `1 - tanh(mu)**2`) survived in a torch module where no
finite difference was ever taken.

So the table lives here, its argument is the pre-activation, and the three
callers share one answer. `tests/acceleration/test_defect_class_audit.py` locks
that they still do.
"""

from __future__ import annotations

import math

import torch
from torch import Tensor, nn

__all__ = [
    "ACTIVATIONS",
    "activation_derivative",
    "activation_from_name",
    "activation_name",
]

ACTIVATIONS: dict[str, nn.Module] = {
    "relu": nn.ReLU(),
    "silu": nn.SiLU(),
    "tanh": nn.Tanh(),
    "gelu": nn.GELU(),
}

_BY_TYPE: dict[type[nn.Module], str] = {
    nn.ReLU: "relu",
    nn.SiLU: "silu",
    nn.Tanh: "tanh",
    nn.GELU: "gelu",
    nn.Identity: "relu",
}


def activation_from_name(name: str) -> nn.Module:
    return ACTIVATIONS.get(name.lower(), nn.ReLU())


def activation_name(activation: nn.Module | str) -> str:
    """The table key for a module or a name; relu is the default."""
    if isinstance(activation, str):
        return activation.lower() if activation.lower() in ACTIVATIONS else "relu"
    return _BY_TYPE.get(type(activation), "relu")


def activation_derivative(x: Tensor, activation: nn.Module | str) -> Tensor:
    """``f'(x)`` for the **pre**-activation ``x``.

    Every branch is a function of the value that went *into* the activation.
    Substituting the output is a different number for every activation except
    tanh, whose `1 - h**2` form is the reason the two conventions look alike.
    """
    match activation_name(activation):
        case "silu":
            sig = torch.sigmoid(x)
            return sig * (1 + x * (1 - sig))
        case "tanh":
            return 1 - torch.tanh(x) ** 2
        case "gelu":
            cdf = 0.5 * (1 + torch.erf(x / math.sqrt(2)))
            pdf = torch.exp(-(x**2) / 2) / math.sqrt(2 * math.pi)
            return cdf + x * pdf
        case _:
            return (x > 0).to(x.dtype)
