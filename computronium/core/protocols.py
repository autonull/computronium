"""Structural protocols shared across the core layer."""

from __future__ import annotations

from collections.abc import Iterable  # ruff: ignore[typing-only-standard-library-import] — runtime Protocol member
from typing import TYPE_CHECKING, Protocol, Self, runtime_checkable

if TYPE_CHECKING:
    import torch


@runtime_checkable
class TrainableModel(Protocol):
    """Structural nn.Module-compatible training surface.

    Satisfied by ``nn.Module`` and by composed ``System`` objects; lets
    training helpers accept both without nominal coupling.
    """

    @property
    def training(self) -> bool: ...

    def parameters(self) -> Iterable[torch.Tensor]: ...

    def train(self, mode: bool = True) -> Self: ...

    def eval(self) -> Self: ...

    def zero_grad(self, set_to_none: bool = True) -> None: ...

    def __call__(self, x: torch.Tensor) -> torch.Tensor: ...


__all__ = ["TrainableModel"]
