"""Shared utilities for ontology layers.

Consolidates common functions used across credit, dynamics, update, and geometry
modules to eliminate duplication.
"""

from __future__ import annotations

import zlib
from collections.abc import Callable
from typing import TYPE_CHECKING

import torch
from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.ontology.geometry import Geometry, TileBlockGeometry


# ============================================================
# Activation/State Utilities
# ============================================================


def _acts_list(activations: list[Tensor] | Tensor | None) -> list[Tensor]:
    """Normalize activations to a list of layer tensors."""
    if activations is None:
        return []
    if isinstance(activations, list):
        return activations
    return [activations]


def _block_transition_acts(
    acts: list[Tensor], geometry: Geometry
) -> TileBlockGeometry | None:
    """The geometry when it declares a block transition table and the settled
    acts align with it (tile meshes, R11.1.4); else None.

    Returning the narrowed geometry rather than a bool is what lets the block
    paths call ``assemble_blocks`` / ``scatter_block_grads`` under the type
    checker instead of behind a repeated ``getattr``.
    """
    from computronium.ontology.geometry import is_tile_block_geometry

    if is_tile_block_geometry(geometry) and len(acts) == geometry.block_act_count:
        return geometry
    return None


# ============================================================
# Weight/Parameter Utilities
# ============================================================


def _propagate_targets(
    acts: list[Tensor],
    y: Tensor,
    weight_names: list[str],
    geometry: Geometry,
) -> list[Tensor | None]:
    """Transpose-feedback target propagation: t_L = one-hot(y), t_l = t_{l+1} @ W_{l+1}."""
    out_dim = acts[-1].shape[-1]
    targets: list[Tensor | None] = [None] * len(acts)
    targets[-1] = torch.nn.functional.one_hot(y, num_classes=out_dim).float()
    for l in range(min(len(weight_names), len(acts) - 1) - 1, -1, -1):  # ruff: ignore[ambiguous-variable-name]
        nxt = targets[l + 1]
        if nxt is None:
            break
        w = geometry.params[weight_names[l]]
        if nxt.shape[-1] != w.shape[0]:
            # Ragged weight (e.g. tile meshes): the transition contract
            # does not hold — stop propagating rather than crash.
            break
        targets[l] = nxt @ w
    return targets


def _weight_acts(
    weight_names: list[str], acts: list[Tensor], geometry: Geometry
) -> list[tuple[Tensor, Tensor] | None]:
    """(pre, post) activation pair each learnable weight consumes.

    Positional over act transitions: weight i maps acts[i] -> acts[i+1].
    Surplus weights (recurrent self-connections) consume the last hidden
    layer as both pre and post — the correlate the settle kernel itself
    feeds them. Weights whose shape does not match their act-pair widths
    (tile/ragged meshes) map to None — credits emit zeros for them.
    """
    n_trans = len(acts) - 1
    pairs: list[tuple[Tensor, Tensor] | None] = []
    for i, name in enumerate(weight_names):
        w = geometry.params[name]
        if i < n_trans:
            pre, post = acts[i], acts[i + 1]
        elif n_trans >= 1:
            pre = post = acts[n_trans - 1]
        else:
            pairs.append(None)
            continue
        if w.shape[0] == post.shape[-1] and w.shape[1] == pre.shape[-1]:
            pairs.append((pre, post))
        else:
            pairs.append(None)
    return pairs


# ============================================================
# Parameter/Update Utilities
# ============================================================


class UnmatchedWeightNamesError(RuntimeError):
    """No param key satisfied the 'weight'-substring pairing contract."""

    def __init__(self, params: dict[str, Tensor]) -> None:
        super().__init__(
            "apply_pseudo_gradients: no learnable weight names matched "
            "(keys must contain 'weight', ndim 2); a hand-rolled param "
            f"dict like {sorted(params)[:3]} would silently skip every "
            "weight update"
        )


def _learnable_weight_names(params: Mapping[str, Tensor]) -> list[str]:
    """Parameter names that receive pseudo-gradients (2-D weight matrices).

    Credits emit exactly one pseudo-gradient per learnable weight, in this
    order. Biases and other auxiliary parameters never receive gradients
    from the local learning rules.
    """
    return [n for n, p in params.items() if "weight" in n and p.ndim == 2]


def apply_pseudo_gradients(
    params: dict[str, Tensor],
    pseudo_grads: list[Tensor],
    transform: Callable[[str, Tensor, Tensor], Tensor],
    bias_grads: dict[str, Tensor] | None = None,
) -> dict[str, Tensor]:
    """Pair pseudo-gradients with their parameters by learnable-weight order.

    The single choke point for update rules: non-weight parameters pass
    through untouched (fixes the index-pairing crash on bias interleaving),
    surplus gradients are ignored, and gradients are detached — pseudo-
    gradients are consumed as plain values everywhere in this pipeline.

    Args:
        params: Current parameters (name -> tensor).
        pseudo_grads: One pseudo-gradient per learnable weight.
        transform: ``(name, param, grad) -> updated_param`` for matched pairs.
        bias_grads: Optional name-keyed gradients for 1-D bias parameters,
            for credits whose readout trains a bias (LocalContrastive).
            Applied through the same ``transform`` so the update rule's
            lr/momentum/clip semantics cover them; absent means frozen.
    """
    updated = dict(params)
    weight_names = _learnable_weight_names(params)
    if not weight_names and pseudo_grads and any(p.ndim == 2 for p in params.values()):
        raise UnmatchedWeightNamesError(params)
    for name, grad in zip(weight_names, pseudo_grads):
        param = params[name]
        updated[name] = transform(name, param, grad.detach().to(param.device))
    for name, grad in (bias_grads or {}).items():
        param = params[name]
        updated[name] = transform(name, param, grad.detach().to(param.device))
    return updated


# ============================================================
# Deterministic Random Utilities
# ============================================================


def _deterministic_generator(
    name: str, device: torch.device | str = "cpu"
) -> torch.Generator:
    """Create a deterministic generator seeded from a string name."""
    gen = torch.Generator(device=device)
    gen.manual_seed(zlib.crc32(name.encode()))
    return gen


def _fixed_random_matrix(
    name: str,
    rows: int,
    cols: int,
    device: torch.device | str,
    dtype: torch.dtype,
    *,
    orthogonal: bool = False,
    scale: float = 1.0,
) -> Tensor:
    """Create a fixed random matrix deterministically seeded from name."""
    gen = _deterministic_generator(name, device)
    mat = torch.empty(rows, cols, device=device, dtype=torch.float32)
    if orthogonal:
        torch.nn.init.orthogonal_(mat, generator=gen)
    else:
        mat.normal_(generator=gen)
    return mat.to(dtype) * scale


# ============================================================
# Gradient/Update Utilities
# ============================================================


def _clip_grads(grads: list[Tensor], clip: float | None) -> list[Tensor]:
    """Per-parameter gradient clipping."""
    if clip is None or clip <= 0 or not grads:
        return grads
    clipped = []
    for g in grads:
        gn = g.norm()
        if gn > clip:
            g = g * (clip / (gn + 1e-8))
        clipped.append(g)
    return clipped


def _rms_normalize(tensor: Tensor, eps: float = 1e-8) -> Tensor:
    """Normalize tensor to unit RMS."""
    rms = tensor.square().mean().sqrt().add_(eps)
    return tensor / rms


def _spectral_normalize(
    tensor: Tensor, target_norm: float = 1.0, eps: float = 1e-8
) -> Tensor:
    """Normalize tensor to target spectral norm."""
    if tensor.ndim < 2:
        return tensor
    sigma = torch.linalg.matrix_norm(tensor.float(), ord=2)
    if sigma > 0:
        return (tensor.float() * (target_norm / (sigma + eps))).to(tensor.dtype)
    return tensor


# ============================================================
# Normalization Utilities
# ============================================================


def apply_norm(
    grads: list[Tensor],
    mode: str,
    refs: list[Tensor] | None = None,
) -> list[Tensor]:
    """Per-layer normalization of gradient-like tensors.

    Args:
        grads: List of gradient tensors to normalize
        mode: Normalization mode -- "none", "relative", "rms", "beta_adaptive", "spectral"
        refs: Optional reference tensors for relative/beta_adaptive modes

    Returns:
        Normalized gradients (same list structure, zeros stay zeros)
    """
    if mode == "none":
        return grads
    out: list[Tensor] = []
    for i, g in enumerate(grads):
        if not torch.isfinite(g).all():
            # Diverged gradient: pass through untouched (RiemannianOrthogonalUpdate precedent)
            out.append(g)
            continue
        if mode == "spectral":
            if g.ndim < 2:
                out.append(g)
                continue
            radius = torch.linalg.matrix_norm(g, ord=2)
            out.append(g / (radius + 1e-8) if radius > 0 else g)
        elif mode == "rms":
            rms = g.square().mean().sqrt()
            out.append(g / (rms + 1e-8) if rms > 0 else g)
        else:  # "relative" | "beta_adaptive"
            ref = refs[i] if refs is not None and i < len(refs) else None
            if ref is None:
                out.append(g)
                continue
            mag = ref.norm() if mode == "relative" else ref.square().mean().sqrt()
            out.append(g / (mag + 1e-8) if mag > 0 else g)
    return out


# ============================================================
# EMA Utilities
# ============================================================


class _EMANormalizer:
    """Exponential Moving Average normalizer for pseudo-gradients."""

    def __init__(self, beta: float = 0.99) -> None:
        self.beta = beta
        self._ema: dict[str, Tensor] = {}

    def normalize(self, name: str, grad: Tensor) -> Tensor:
        """Update EMA and return normalized gradient."""
        g2 = grad.detach().float() ** 2
        if name not in self._ema:
            self._ema[name] = g2
        else:
            self._ema[name].mul_(self.beta).add_(g2, alpha=1 - self.beta)
        ema_sqrt = self._ema[name].sqrt().add_(1e-8)
        return (grad.float() / ema_sqrt).to(grad.dtype)


# ============================================================
# Configuration Base Class
# ============================================================


class ConfigFactory:
    """Base class for configuration factories with hyperparameter support.

    Provides a standard pattern for:
    - Factory classmethods (e.g., Config.digital(), Config.feedforward())
    - Hyperparameter declaration for sweep/optuna integration
    """

    @classmethod
    def hyperparameters(cls, _primitive_name: str = "") -> dict[str, object]:
        """Hyperparameter ranges owned by this config axis.

        Args:
            primitive_name: The specific primitive name for availability predicates.

        Returns:
            Dictionary mapping parameter name to domain specification.
            Domain spec: {"domain": (min, max, "scale"), "availability": expr, ...}
        """
        raise NotImplementedError


__all__ = [
    "ConfigFactory",
    "_EMANormalizer",
    "_acts_list",
    "_block_transition_acts",
    "_clip_grads",
    "_deterministic_generator",
    "_fixed_random_matrix",
    "_learnable_weight_names",
    "_propagate_targets",
    "_rms_normalize",
    "_spectral_normalize",
    "_weight_acts",
]
