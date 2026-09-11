"""Minimal joint-state types for framework-agnostic stability probing.

``CompositeState`` is the structural core of a joint state (activity /
plastic / substrate mappings). Host frameworks may pass their own richer
state objects — anything with the same three mappings (plus ``clone`` when
trajectory recording is used) is duck-compatible.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from torch import Tensor

type ActivityValue = Tensor | list[Tensor] | float | dict[str, float]


@dataclass(slots=True)
class CompositeState:
    """Joint intra-episode state: z_t = (activity, plastic, substrate)."""

    activity: dict[str, ActivityValue]
    plastic: dict[str, Tensor]
    substrate: dict[str, Tensor]

    def clone(self) -> CompositeState:
        """Deep copy with cloned tensors (detached from graph)."""
        new_activity: dict[str, ActivityValue] = {}
        for k, v in self.activity.items():
            if isinstance(v, Tensor):
                new_activity[k] = v.detach().clone()
            elif isinstance(v, list):
                new_activity[k] = [t.detach().clone() for t in v]
            else:
                new_activity[k] = v
        return CompositeState(
            activity=new_activity,
            plastic={k: v.detach().clone() for k, v in self.plastic.items()},
            substrate={k: v.detach().clone() for k, v in self.substrate.items()},
        )


@runtime_checkable
class SystemContext(Protocol):
    """Opaque fixed-parameter context passed through to transition functions.

    Intentionally empty: the stability estimators never read context fields;
    they only forward it to the caller's transition function.
    """


__all__ = ["ActivityValue", "CompositeState", "SystemContext"]
