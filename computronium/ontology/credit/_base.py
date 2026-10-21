"""Shared base classes and utilities for CreditAssignment implementations."""

from __future__ import annotations

import zlib
from typing import TYPE_CHECKING, Protocol

import torch
from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.ontology.credit import CreditAssignmentConfig
    from computronium.ontology.geometry import Geometry, TileBlockGeometry


class StatefulCredit(Protocol):
    """A CreditAssignment that can be replayed without consuming state."""

    def get_state(self) -> dict[str, dict[str, Tensor]]: ...

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None: ...


class FeedbackMatrixMixin:
    """Mixin providing lazy-initialized fixed feedback matrices with device sync.

    Handles the common pattern where credit rules need fixed random projection
    matrices that must follow the geometry's device when the model moves
    from CPU (composition/probing) to accelerator (training).
    """

    _feedback_weights: dict[str, Tensor]
    config: CreditAssignmentConfig

    def _init_feedback_weights(
        self,
        geometry: Geometry,
        device: torch.device | None = None,
        key_fn: Callable[[str], str] | None = None,
    ) -> None:
        """Initialize fixed random feedback matrices for each learnable weight.

        Args:
            geometry: Network geometry providing parameter shapes
            device: Target device (defaults to first weight's device)
            key_fn: Optional function to customize the dict key (default: weight name)
        """
        if self._feedback_weights:
            return  # Already initialized

        from computronium.ontology.utils import _learnable_weight_names

        if device is None:
            weight_names = _learnable_weight_names(geometry.params)
            if weight_names:
                device = geometry.params[weight_names[0]].device
            else:
                device = torch.device("cpu")

        for name in _learnable_weight_names(geometry.params):
            param = geometry.params[name]
            key = key_fn(name) if key_fn else name
            if key in self._feedback_weights:
                continue
            gen = torch.Generator(device=device)
            gen.manual_seed(zlib.crc32(key.encode()))
            fb = torch.randn_like(param, generator=gen) * self.config.feedback_scale
            if self.config.orthogonal_init and param.ndim == 2:
                torch.nn.init.orthogonal_(fb, generator=gen)
                fb.mul_(self.config.feedback_scale)
            self._feedback_weights[key] = fb.to(device)

    def _sync_feedback_device(self, geometry: Geometry) -> None:
        """Re-home cached feedback matrices onto the weights' device.

        The cell is composed (and dry-run probed) on CPU before the
        trainer moves geometry to the accelerator; matrices initialized
        in that phase must follow the weights, not stay stranded.
        """
        from computronium.ontology.utils import _learnable_weight_names

        weight_names = _learnable_weight_names(geometry.params)
        if not weight_names or not self._feedback_weights:
            return
        target = geometry.params[weight_names[0]].device
        for key, fb in self._feedback_weights.items():
            if fb.device != target:
                self._feedback_weights[key] = fb.to(target)

    def _get_feedback_weight(self, name: str) -> Tensor:
        """Get feedback weight by name, assuming it exists."""
        return self._feedback_weights[name]


class TileFeedbackMixin:
    """Mixin for tile-mesh block feedback assembly (R11.1.4)."""

    _feedback_weights: dict[str, Tensor]

    def _assemble_tile_feedback(self, geometry: TileBlockGeometry) -> list[Tensor]:
        """Assemble per-transition feedback blocks from per-weight matrices."""
        return geometry.assemble_blocks(self._feedback_weights)


class InertZerosMixin:
    """Mixin providing the inert-zeros failure mode for FA contracts.

    When the layered FA contract cannot chain (detached settle graph
    or feedback/act width mismatch), returning all-zeros is
    indistinguishable from a trained failure. Raising makes it visible
    to the campaign's dry-run gate.
    """

    def _inert_zeros(self, geometry: Geometry, weight_names: list[str]) -> list[Tensor]:
        """All-zeros pseudo-gradient — raise so dry-run gate catches no-op runs."""
        raise RuntimeError(
            f"{type(self).__name__}: layered FA contract would return "
            f"all-zero pseudo-gradient for {len(weight_names)} weights "
            "(detached settle graph or feedback/act width mismatch). "
            "This coordinate cannot train — rejected at dry-run."
        )


class LearnedFeedbackMixin:
    """Mixin providing learned feedback matrices with ridge-regression updates.

    Implements the transport-free reconstruction update from RESEARCH4 Fix 1a:
    each B_i is regressed (closed-form ridge, autograd-free) to map the
    broadcast output error e₁ back into the post-synaptic activity space
    of its weight. EMA-blended at ``feedback_lr`` every
    ``feedback_update_every`` steps.
    """

    _learned: dict[tuple, Tensor]
    _feedback_step: int
    config: CreditAssignmentConfig

    def _learned_projection(
        self,
        name: str,
        width: int,
        out_dim: int,
        device: str,
        dtype: torch.dtype,
    ) -> Tensor:
        """Credit-internal learned B: (out_dim, width), same deterministic
        init as the fixed projection until the first reconstruction update."""
        key = (name, (out_dim, width), device, str(dtype))
        if key not in self._learned:
            self._learned[key] = self._inverse_projection(
                name, width, out_dim, device, dtype
            ).clone()
        return self._learned[key]

    def _update_learned_feedback(
        self,
        free_acts: list[Tensor],
        e1: Tensor,
        weight_names: list[str],
        n_trans: int,
    ) -> None:
        """Transport-free reconstruction update of the learned B matrices.

        Objective: B_i maps the broadcast output error e₁ back into weight i's
        post-synaptic activity space. Ridge solution: B_i = Cᵀ where
        post @ C ≈ e₁ — autograd-free, reads only settled activations.
        """
        self._feedback_step += 1
        if (self._feedback_step - 1) % max(1, self.config.feedback_update_every):
            return
        for k, name in enumerate(weight_names):
            if k >= n_trans:
                continue
            post = free_acts[k + 1].detach()
            width = post.shape[-1]
            key = (name, (e1.shape[-1], width), str(post.device), str(e1.dtype))
            if key not in self._learned:
                continue
            if not (torch.isfinite(post).all() and torch.isfinite(e1).all()):
                continue  # diverged settle: skip, don't poison B
            a = post.float()
            g = a.T @ a
            lam = 1e-3 * g.diagonal().mean().clamp_min(1e-12)
            c = torch.linalg.solve(
                g + lam * torch.eye(g.shape[0], device=g.device), a.T @ e1.float()
            )
            b_new = (c.T * self.config.feedback_scale).to(e1.dtype)
            if not torch.isfinite(b_new).all():
                continue
            cur = self._learned[key]
            lr = self.config.feedback_lr
            self._learned[key] = ((1.0 - lr) * cur.float() + lr * b_new.float()).to(
                cur.dtype
            )

    def _snapshot_learned_feedback(self) -> dict[str, dict[str, Tensor]]:
        """Snapshot protocol for learned feedback state."""
        if not self._learned:
            return {}
        return {
            "learned_feedback": {
                f"{name}|{shape[0]}x{shape[1]}|{device}|{dtype}": t.detach().clone()
                for (name, shape, device, dtype), t in self._learned.items()
            },
            "step": {"counter": torch.tensor(self._feedback_step)},
        }

    def _restore_learned_feedback(self, state: dict[str, dict[str, Tensor]]) -> None:
        """Restore learned feedback state from snapshot."""
        step_group = state.get("step", {})
        step = step_group.get("counter") if isinstance(step_group, dict) else None
        if not isinstance(step, Tensor):
            msg = "learned-feedback credit state is missing the step counter"
            raise TypeError(msg)
        self._feedback_step = int(step.item())
        for key, tensor in state.get("learned_feedback", {}).items():
            name, shape_s, device, dtype = key.split("|", 3)
            rows, cols = (int(s) for s in shape_s.split("x"))
            t_key = (name, (rows, cols), device, dtype)
            cached = self._learned.get(t_key)
            if cached is not None and cached.shape != tensor.shape:
                msg = (
                    f"learned-feedback state shape mismatch for {name!r}: "
                    f"state {tuple(tensor.shape)} vs cache {tuple(cached.shape)} "
                    "(system-scoped state cannot be re-targeted)"
                )
                raise TypeError(msg)
            self._learned[t_key] = tensor.detach().clone()


# Re-export for backward compatibility
__all__ = [
    "FeedbackMatrixMixin",
    "InertZerosMixin",
    "LearnedFeedbackMixin",
    "StatefulCredit",
    "TileFeedbackMixin",
]
