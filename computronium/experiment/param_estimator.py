"""Per-model parameter counting, built on the single construction layer.

The heavy lifting — reflection-driven knob routing, ``ModelConfig`` building,
and the canonical :func:`construct_model` — lives in
:mod:`computronium.core.construction`. This module keeps the stable public
parameter-estimation API that the campaign runner, scheduler and parity CLI
depend on, and re-exports the construction primitives so callers have one import
surface.

Do not add construction logic here: new construction behavior goes in
``core/construction.py`` so the trainer, the estimator, the finders and the
probe all share one path and can never disagree about a model's parameters or
knobs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, cast

from computronium.core.construction import (
    KNOBS,
)
from computronium.core.construction import (
    construct_model as _construct_model,
)
from computronium.core.construction import (
    model_kwargs as _model_kwargs,
)
from computronium.core.construction import (
    phantom_knobs as _phantom_knobs,
)
from computronium.models.native import (
    create_native_backprop_mlp,
    create_native_diffusion_eqprop,
    create_native_directed_ep,
    create_native_eqprop_mlp,
    create_native_fa_mlp,
    create_native_finite_nudge_ep,
    create_native_holomorphic_ep,
    create_native_lemma_mlp,
    create_native_momentum_eqprop,
    create_native_sparse_eqprop,
    create_native_ternary_eqprop,
    create_native_tile_ep,
    create_native_tile_fa,
    create_native_tile_gnn,
    create_native_tile_hebbian,
    create_native_tile_pc,
    create_native_tile_snn,
    create_native_tile_tp,
)
from computronium.utils import count_parameters

if TYPE_CHECKING:
    from collections.abc import Callable

    import torch

__all__ = [
    "KNOBS",
    "MODEL_REGISTRY",
    "NATIVE_MODEL_NAMES",
    "InstantiateEstimator",
    "ParamEstimateError",
    "ParamEstimator",
    "bound_estimator",
    "build_model_kwargs",
    "estimate_param_count",
    "has_model",
    "phantom_knobs",
    "resolve_native_model",
]


class ParamEstimateError(RuntimeError):
    """Raised when a model cannot be constructed for parameter counting."""


class ModuleFactory(Protocol):
    """A registered model constructor: builds an ``nn.Module`` from kwargs."""

    def __call__(self, **kwargs: object) -> torch.nn.Module: ...


type NativeModelFactory = Callable[..., object]


@dataclass(frozen=True, slots=True)
class ModelSpec:
    """Single source of truth for a native model.

    Attributes:
        canonical_name: The authoritative zoo name (one per factory).
        factory: The construction callable.
        fragments: Substrings that resolve to this factory (for alias support).
                   First fragment is the primary; order matters for overlapping matches.
    """

    canonical_name: str
    factory: NativeModelFactory
    fragments: tuple[str, ...]


#: Single source of truth: one row per native factory.
#: Canonical names are unique; fragments enable alias resolution (e.g. "pepita" -> lemma_mlp).
#: Order matters: more specific fragments must come before generic substrings (e.g. "feedback_alignment" before "eqprop",
#: "momentum_eqprop" before "eqprop", "diffusion_eqprop" before "eqprop").
MODEL_REGISTRY: tuple[ModelSpec, ...] = (
    ModelSpec("backprop_mlp", create_native_backprop_mlp, ("backprop",)),
    ModelSpec("lemma_mlp", create_native_lemma_mlp, ("lemma", "pepita")),
    ModelSpec("fa_mlp", create_native_fa_mlp, ("feedback_alignment", "fa")),
    ModelSpec(
        "diffusion_eqprop", create_native_diffusion_eqprop, ("diffusion_eqprop",)
    ),
    ModelSpec("directed_ep", create_native_directed_ep, ("directed_ep",)),
    ModelSpec("momentum_eqprop", create_native_momentum_eqprop, ("momentum_eqprop",)),
    ModelSpec("sparse_eqprop", create_native_sparse_eqprop, ("sparse_eqprop",)),
    ModelSpec("ternary_eqprop", create_native_ternary_eqprop, ("ternary_eqprop",)),
    ModelSpec("finite_nudge_ep", create_native_finite_nudge_ep, ("finite_nudge",)),
    ModelSpec("holomorphic_ep", create_native_holomorphic_ep, ("holomorphic",)),
    ModelSpec("eqprop_mlp", create_native_eqprop_mlp, ("eqprop",)),
    ModelSpec("tile_ep", create_native_tile_ep, ("tile_ep",)),
    ModelSpec("tile_fa", create_native_tile_fa, ("tile_fa",)),
    ModelSpec("tile_gnn", create_native_tile_gnn, ("tile_gnn",)),
    ModelSpec("tile_hebbian", create_native_tile_hebbian, ("tile_hebbian", "hebbian")),
    ModelSpec("tile_pc", create_native_tile_pc, ("tile_pc",)),
    ModelSpec("tile_snn", create_native_tile_snn, ("tile_snn",)),
    ModelSpec("tile_tp", create_native_tile_tp, ("tile_tp",)),
)


#: Canonical zoo names — exactly one per factory. Derived from MODEL_REGISTRY.
NATIVE_MODEL_NAMES: tuple[str, ...] = tuple(
    spec.canonical_name for spec in MODEL_REGISTRY
)


#: Fragment-to-factory mapping for resolution — derived from MODEL_REGISTRY.
#: Order preserves priority: longer fragments first so "tile_fa" matches before "fa".
_NATIVE_MODEL_FACTORIES: tuple[tuple[str, NativeModelFactory], ...] = tuple(
    (fragment, spec.factory) for spec in MODEL_REGISTRY for fragment in spec.fragments
)


def has_model(name: str) -> bool:
    """Whether ``name`` names a model this registry can build.

    The membership predicate `resolve_native_model` used to lack: asking "is this
    a known model?" had no answer, so every caller either guessed or caught the
    wrong exception (TODO36 §4.8). Matching is by fragment, exactly as
    :func:`resolve_native_model` matches, so the two cannot disagree.
    """
    key = name.lower()
    return any(fragment in key for fragment, _ in _NATIVE_MODEL_FACTORIES)


def resolve_native_model(name: str) -> NativeModelFactory:
    """Resolve a model name to its native 5-D composition factory.

    An unknown name still falls back to the EqProp composition, which is a silent
    substitution in the one place that must not make one. The registry now covers
    every factory ``models.native`` exports. Use :func:`has_model` before calling
    if the fallback is not desired.
    """
    key = name.lower()
    for fragment, factory in _NATIVE_MODEL_FACTORIES:
        if fragment in key:
            return factory
    return create_native_eqprop_mlp


class ParamEstimator(Protocol):
    """Static parameter-count protocol used by the campaign runner."""

    def estimate(
        self,
        model_name: str,
        config: dict[str, object],
        *,
        input_dim: int,
        output_dim: int,
    ) -> int: ...


#: Public alias: ``model_kwargs`` returns plain serializable scalars (the
#: ``TrainerConfig``/OmegaConf-safe view). ``construct_model`` turns them into a
#: live model with knobs applied.
build_model_kwargs = _model_kwargs
phantom_knobs = _phantom_knobs


class InstantiateEstimator:
    """Count parameters by constructing the model (exact, no training)."""

    @staticmethod
    def estimate(
        model_name: str,
        config: dict[str, object],
        *,
        input_dim: int,
        output_dim: int,
    ) -> int:
        model_cls = cast("ModuleFactory", resolve_native_model(model_name))
        try:
            # Build via the canonical construction layer so the counted model is
            # bit-for-bit the one the trainer builds (same knob routing).
            model = _construct_model(
                model_cls,
                config,
                input_dim=input_dim,
                output_dim=output_dim,
                model_name=model_name,
            )
        except (TypeError, ValueError, RuntimeError) as exc:
            raise ParamEstimateError(  # descriptive message is the public API
                f"Could not construct {model_name!r} for param counting: {exc}"
            ) from exc
        return count_parameters(model, trainable_only=False)  # type: ignore[arg-type]


def estimate_param_count(
    model_name: str,
    config: dict[str, object],
    *,
    input_dim: int,
    output_dim: int,
) -> int:
    """Estimate the parameter count for ``model_name`` under ``config``.

    This is a pure static analysis: the model is built via
    :func:`construct_model <computronium.core.construction.construct_model>`
    and its named parameters are summed. Used for the pre-training ``max_params``
    budget filter (§5.3) and for constraint expressions.
    """

    key = (model_name, input_dim, output_dim, _freeze_config(config))
    cached = _PARAM_COUNT_CACHE.get(key)
    if cached is not None:
        return cached
    # An exception here (ParamEstimateError) naturally returns before the cache
    # write below, so a failed construction is never cached and a transient
    # failure can recover on retry.
    count = InstantiateEstimator.estimate(
        model_name,
        config,
        input_dim=input_dim,
        output_dim=output_dim,
    )
    _PARAM_COUNT_CACHE[key] = count
    return count


def _freeze_config(
    config: dict[str, object],
) -> tuple[tuple[str, object], ...]:
    """Turn a config dict into a hashable, order-independent key fragment.

    Values are ``repr``-it if unhashable (e.g. a list choice); the original
    ``config`` is still passed to the estimator, so the cache is keyed by a
    faithful serialisation without ever mutating the caller's data.
    """
    frozen: list[tuple[str, object]] = []
    for key, value in config.items():
        try:
            hash(value)
        except TypeError:
            frozen.append((key, repr(value)))
        else:
            frozen.append((key, value))
    return tuple(sorted(frozen))


#: ``(model, dims, config) -> param count`` memo. Bounded by the number of
#: distinct (model, config, dims) triples a single process schedules, so it is
#: safely small for a campaign run.
_PARAM_COUNT_CACHE: dict[tuple[object, ...], int] = {}


def bound_estimator(
    model_name: str, input_dim: int, output_dim: int
) -> Callable[[dict[str, object]], int]:
    """Bind a model + dims into ``estimate(config) -> int``.

    The returned callable is the shape consumed by constraint expressions and
    :meth:`SearchSpace.sample_feasible`.
    """

    def _estimate(config: dict[str, object]) -> int:
        return estimate_param_count(
            model_name, config, input_dim=input_dim, output_dim=output_dim
        )

    return _estimate
