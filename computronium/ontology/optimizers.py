"""Standard PyTorch optimizers as PARAM_UPDATE registry components.

First-class ontology-side registrations so standard optimizers are available
without the deprecated zoo package.
"""

from torch.optim import (
    SGD as TorchSGD,  # noqa: N811
)
from torch.optim import Adam as TorchAdam
from torch.optim import AdamW as TorchAdamW
from torch.optim import RMSprop as TorchRMSprop

__all__ = ["SGD", "Adam", "AdamW", "RMSprop"]


class SGD(TorchSGD):
    """SGD optimizer wrapper."""


class Adam(TorchAdam):
    """Adam optimizer wrapper."""


class AdamW(TorchAdamW):
    """AdamW optimizer wrapper."""


class RMSprop(TorchRMSprop):
    """RMSprop optimizer wrapper."""
