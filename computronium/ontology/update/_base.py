"""Shared base classes and utilities for ParameterUpdate implementations."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

import torch
from torch import Tensor

if TYPE_CHECKING:
    from computronium.ontology.geometry import Geometry
    from computronium.ontology.update import ParameterUpdateConfig


class StatefulUpdate(Protocol):
    """A ``ParameterUpdate`` that can be replayed without consuming state."""

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry | None,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]: ...

    def get_state(self) -> dict[str, dict[str, Tensor]]: ...

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None: ...


def _fresh_buffer(
    store: dict[str, Tensor], name: str, param: Tensor, buf: Tensor | None
) -> Tensor:
    """Cache-hit validity check: re-init when shape OR device diverged.

    A system composed (or probed) on CPU before the trainer moves the
    geometry strands cached momentum buffers off the weights' device —
    same lazy-init poisoning class as credit feedback matrices. Momentum
    state is zero-warm-started, so re-init on device change is lossless.
    """
    if buf is None or buf.shape != param.shape or buf.device != param.device:
        return torch.zeros_like(param)
    return buf


class BufferManager:
    """Mixin providing validated buffer access for optimizer state.

    Ensures buffers match parameter shape and device, failing loudly on
    geometry reuse (optimizer state is system-scoped).
    """

    def _get_buffer(
        self,
        store: dict[str, Tensor],
        name: str,
        param: Tensor,
        error_prefix: str,
    ) -> Tensor:
        buf = store.get(name)
        if buf is not None and buf.shape != param.shape:
            msg = (
                f"{error_prefix} for {name!r} has shape "
                f"{tuple(buf.shape)} but parameter has "
                f"{tuple(param.shape)} — the update instance is "
                "being reused across different geometries; create "
                "one update per system (optimizer state is "
                "system-scoped)"
            )
            raise RuntimeError(msg)
        buf = _fresh_buffer(store, name, param, buf)
        store[name] = buf
        return buf


class ClippingMixin:
    """Mixin providing global-norm gradient clipping."""

    def _clip(self, grads: list[Tensor], clip_value: float) -> list[Tensor]:
        """Global-norm clip (clip_grad_norm_ semantics): keeps relative
        per-parameter magnitudes intact so updates shrink naturally near
        equilibrium. Per-tensor rescaling would erase that signal and turn
        every step into a fixed-norm jump."""
        if clip_value is None or clip_value <= 0 or not grads:
            return grads
        stacked_norms = torch.stack([g.norm() for g in grads])
        total_norm = torch.linalg.vector_norm(stacked_norms)
        if total_norm > clip_value:
            scale = clip_value / (total_norm + 1e-8)
            grads = [g * scale for g in grads]
        return grads


class StateSnapshotMixin:
    """Mixin providing standard get_state/load_state for momentum-like buffers."""

    _momentum_buffers: dict[str, Tensor]

    def _snapshot_momentum(self) -> dict[str, dict[str, Tensor]]:
        return {
            "momentum": {
                k: v.detach().clone() for k, v in self._momentum_buffers.items()
            }
        }

    def _restore_momentum(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._momentum_buffers = {
            k: v.clone() for k, v in state.get("momentum", {}).items()
        }


class AdamStateMixin:
    """Mixin providing get_state/load_state for Adam-style (m, v, t) state."""

    _m: dict[str, Tensor]
    _v: dict[str, Tensor]
    _t: int

    def _snapshot_adam(self) -> dict[str, dict[str, Tensor]]:
        def group(store: dict[str, Tensor]) -> dict[str, Tensor]:
            return {k: v.detach().clone() for k, v in store.items()}

        return {
            "m": group(self._m),
            "v": group(self._v),
            "counters": {"t": torch.tensor(self._t)},
        }

    def _restore_adam(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._m = {k: v.clone() for k, v in state.get("m", {}).items()}
        self._v = {k: v.clone() for k, v in state.get("v", {}).items()}
        t = state.get("counters", {}).get("t")
        self._t = int(t.item()) if t is not None else 0


class LionStateMixin:
    """Mixin providing get_state/load_state for Lion (m-only) state."""

    _m: dict[str, Tensor]
    _t: int

    def _snapshot_lion(self) -> dict[str, dict[str, Tensor]]:
        return {
            "m": {k: v.detach().clone() for k, v in self._m.items()},
            "counters": {"t": torch.tensor(self._t)},
        }

    def _restore_lion(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._m = {k: v.clone() for k, v in state.get("m", {}).items()}
        t = state.get("counters", {}).get("t")
        self._t = int(t.item()) if t is not None else 0


class BaseParameterUpdate:
    """Abstract base class for ParameterUpdate implementations.

    Provides common infrastructure:
    - Config storage
    - apply_pseudo_gradients delegation
    - Standard state snapshot protocol (override in subclasses)
    """

    config: ParameterUpdateConfig

    @abstractmethod
    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]: ...

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        """Snapshot protocol: named groups of state tensors (clones)."""
        raise NotImplementedError

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        raise NotImplementedError


# Re-export for backward compatibility
__all__ = [
    "AdamStateMixin",
    "BaseParameterUpdate",
    "BufferManager",
    "ClippingMixin",
    "LionStateMixin",
    "StateSnapshotMixin",
    "StatefulUpdate",
    "_fresh_buffer",
]
