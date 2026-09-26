"""Learning rules as systems, keyed by the name callers already use.

``"ep"``, ``"fa"``, ``"pc"``, ``"backprop"`` are how experiments, benchmarks
and probes have always named the rule under test, and they are how six
documented entry points named a model registry that Sprint 7.6.10 deleted --
which is why none of them could be imported. The rule is the variable and the
geometry is held constant, so an arm is an MLP over the task's flattened
input whose credit assignment is the named rule.

One table, because the zoo's factories already differ in exactly one axis and
five copies of the mapping is how the callers drifted apart in the first
place.
"""

from __future__ import annotations

import inspect
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

from computronium.core.presets import (
    create_backprop_mlp,
    create_eqprop_mlp,
    create_fa_mlp,
    create_hebbian_mlp,
    create_pc_mlp,
    create_pepita_mlp,
    create_snn_mlp,
    create_tp_mlp,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from computronium.core.system_trainer.protocol import JointSystem
    from computronium.ontology import System

__all__ = [
    "MODEL_NAME_RULES",
    "RULES",
    "consumable_config_keys",
    "routing_system",
    "rule_for",
    "rule_for_name",
    "rule_system",
    "rule_system_from_config",
]

RULE_SYSTEMS: Final[Mapping[str, Callable[..., System]]] = MappingProxyType({
    "backprop": create_backprop_mlp,
    "ep": create_eqprop_mlp,
    "fa": create_fa_mlp,
    "hebbian": create_hebbian_mlp,
    "pc": create_pc_mlp,
    "pepita": create_pepita_mlp,
    "snn": create_snn_mlp,
    "tp": create_tp_mlp,
})

RULES: Final[tuple[str, ...]] = tuple(RULE_SYSTEMS)


# The zoo's model names, as benchmarks and probes still spell them, mapped to
# the rule they name. A name that is not here has no rule, and the caller is
# told so rather than silently trained with backprop.
MODEL_NAME_RULES: Final[Mapping[str, str]] = MappingProxyType({
    "backprop": "backprop",
    "backprop_mlp": "backprop",
    "direct_ep": "ep",
    "ep": "ep",
    "eqprop": "ep",
    "eqprop_mlp": "ep",
    "fa": "fa",
    "fa_mlp": "fa",
    "feedback_alignment": "fa",
    "contrastive_hebbian_learning": "hebbian",
    "hebbian": "hebbian",
    "hebbian_mlp": "hebbian",
    "pc": "pc",
    "pc_mlp": "pc",
    "pepita": "pepita",
    "snn": "snn",
    "tile_mlp": "backprop",
    "target_prop": "tp",
    "tp": "tp",
    "tp_mlp": "tp",
})


def rule_for(model_name: str) -> str:
    """The learning rule a zoo model name refers to.

    Raises:
        KeyError: The name is not a rule-bearing model, with the names that
            are listed in the message.
    """
    try:
        return MODEL_NAME_RULES[model_name]
    except KeyError:
        known = ", ".join(sorted(MODEL_NAME_RULES))
        raise KeyError(f"no learning rule for model {model_name!r}; known: {known}")


def routing_system(
    rule: str,
    input_dim: int,
    output_dim: int,
    *,
    top_k: int | None = None,
    temperature: float = 1.0,
    gate_dim: int = 64,
    hidden_dims: tuple[int, ...] = (256, 256),
    lr: float = 1e-3,
    device: str = "cpu",
) -> JointSystem:
    """A learning rule with state-dependent pathway routing on top.

    The rule's own substrate, geometry, dynamics, credit and update are
    reused, so the arms of a routing ablation differ in routing and nothing
    else. ``temperature`` is the knob for *how* gates select: the ontology
    routes with Gumbel-Softmax, so a high temperature is uniform (random)
    gating and 1.0 is the learned hard top-k of :attr:`top_k`.
    """
    from computronium.core.plasticity.routing import RoutingPlasticity
    from computronium.core.system_trainer.joint import compose_joint_system

    base = rule_system(
        rule, input_dim, output_dim, hidden_dims=hidden_dims, lr=lr, device=device
    )
    return compose_joint_system(
        base.substrate,
        base.geometry,
        base.dynamics,
        RoutingPlasticity(gate_dim=gate_dim, temperature=temperature, top_k=top_k),
        base.credit,
        base.update,
    )


def rule_system(
    rule: str,
    input_dim: int,
    output_dim: int,
    *,
    hidden_dims: tuple[int, ...] = (256, 256),
    lr: float = 1e-3,
    device: str = "cpu",
) -> System:
    """Build the system for one learning rule, sized to a task.

    Raises:
        KeyError: The rule is not one of :data:`RULES`, with the known names
            in the message -- an unregistered arm used to be a silent
            fall-through to backprop.
    """
    try:
        factory = RULE_SYSTEMS[rule]
    except KeyError:
        known = ", ".join(RULES)
        raise KeyError(f"no learning-rule system for {rule!r}; known rules: {known}")
    return factory(input_dim, hidden_dims, output_dim, lr=lr, device=device)


def rule_for_name(name: str) -> str:
    """The learning rule a caller means, whether it named a rule or a model.

    Sweeps and probes reach for rules under three vocabularies -- the rule
    name (``"ep"``), the zoo model name (``"eqprop_mlp"``) and the
    propagator name a family is written with (``"feedback_alignment"``) --
    and all three are in :data:`MODEL_NAME_RULES`. Accepting any of them is
    what lets one probe path serve a rule, a zoo arm and a family.

    Raises:
        KeyError: The name is neither, with both sets of known names in the
            message. A probe that cannot name a rule must fail here rather
            than train with a rule nobody asked for.
    """
    if name in RULES:
        return name
    return rule_for(name)


# A probe config's key names a factory parameter by the same name, except for
# the depth/width pair, which the factories take as one ``hidden_dims`` tuple.
_CONFIG_ALIASES: Final[Mapping[str, str]] = MappingProxyType({
    "hidden_dim": "hidden_dims",
    "num_layers": "hidden_dims",
    "learning_rate": "lr",
})

_SIZED: Final[frozenset[str]] = frozenset({
    "input_dim",
    "hidden_dims",
    "output_dim",
    "device",
})


def _factory(rule: str) -> Callable[..., System]:
    try:
        return RULE_SYSTEMS[rule]
    except KeyError:
        raise KeyError(
            f"no learning-rule system for {rule!r}; known rules: {', '.join(RULES)}"
        ) from None


def consumable_config_keys(rule: str) -> frozenset[str]:
    """The probe-config keys ``rule``'s factory can actually be handed.

    Derived from the factory's signature rather than a written list, so a
    parameter added to a preset is deliverable the day it is added. An earlier
    version of this module named three keys by hand and consequently reported
    ``beta`` and ``inference_steps`` as phantom knobs for the eqprop arm --
    two knobs its factory has always taken.
    """
    params = inspect.signature(_factory(rule)).parameters
    return frozenset(
        key for key, target in _CONFIG_ALIASES.items() if target in params
    ) | frozenset(p for p in params if p not in _SIZED)


def rule_system_from_config(
    rule: str,
    input_dim: int,
    output_dim: int,
    config: Mapping[str, object],
    *,
    device: str = "cpu",
    default_hidden_dim: int = 256,
    default_layers: int = 2,
) -> tuple[System, list[str]]:
    """Build ``rule``'s system from a probe config, and report what it missed.

    Every sampled key naming a parameter of the rule's factory is delivered to
    it; the rest come back as phantom keys, because a sweep that samples a knob
    nothing reads should say so rather than discard it.

    Args:
        rule: A name :func:`rule_for_name` accepts.
        input_dim: Flattened input width of the task.
        output_dim: Task output width.
        config: A sampled probe config.
        device: Device the system is built on.
        default_hidden_dim: Width used when the config names none.
        default_layers: Depth used when the config names none.

    Returns:
        ``(system, phantom_keys)`` -- the composed system, and the sorted
        sampled keys it could not consume.

    Raises:
        KeyError: ``rule`` is not one of :data:`RULES`.
    """
    factory = _factory(rule)
    params = inspect.signature(factory).parameters
    width = int(config.get("hidden_dim", default_hidden_dim))
    depth = max(1, int(config.get("num_layers", default_layers)))

    knobs: dict[str, object] = {}
    for key, value in config.items():
        target = _CONFIG_ALIASES.get(key, key)
        if target in params and target not in _SIZED:
            knobs[target] = value

    system = factory(input_dim, (width,) * depth, output_dim, **knobs, device=device)
    phantom = sorted(key for key in config if key not in consumable_config_keys(rule))
    return system, phantom
