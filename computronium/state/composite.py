"""CompositeState: Joint intra-episode state z_t = (activity, plastic, substrate)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import torch
from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Mapping

type ActivityValue = Tensor | list[Tensor] | float | dict[str, float]


@dataclass(frozen=False, slots=True)
class CompositeState:
    """Joint intra-episode state: z_t = (activity, plastic, substrate).

    Fields are declared as ``Mapping`` (covariant in the value type) so
    callers may pass ``dict[str, Tensor]`` etc.; ``__post_init__``
    converts to mutable dicts for in-place stepping.

    Attributes:
        activity: x_t — neural activations at time t (includes persistent θ refs)
        plastic: ψ_t — fast plastic variables (e.g., eligibility traces, fast weights)
        substrate: σ_t — substrate-owned state (e.g., memristor conductance, analog noise)
    """

    activity: Mapping[str, ActivityValue]
    plastic: Mapping[str, Tensor]
    substrate: Mapping[str, Tensor]

    def _act_mut(self) -> dict[str, ActivityValue]:
        """The post-init-converted mutable activity dict."""
        return cast("dict[str, ActivityValue]", self.activity)

    def set_activity(self, key: str, value: ActivityValue | None) -> None:
        """Set an activity entry; ``None`` removes it."""
        if value is None:
            self._act_mut().pop(key, None)
        else:
            self._act_mut()[key] = value

    # For compatibility with StateDynamics.settle which expects state.x
    @property
    def x(self) -> Tensor | None:
        val = self.activity.get("x")
        return val if isinstance(val, Tensor) else None

    @x.setter
    def x(self, value: Tensor | None) -> None:
        self.set_activity("x", value)

    @property
    def y(self) -> Tensor | None:
        val = self.activity.get("y")
        return val if isinstance(val, Tensor) else None

    @y.setter
    def y(self, value: Tensor | None) -> None:
        self.set_activity("y", value)

    @property
    def activations(self) -> list[Tensor] | Tensor | None:
        """Get all layer activations (for backward compat)."""
        val = self.activity.get("activations")
        if isinstance(val, (list, Tensor)):
            return val
        return None

    @activations.setter
    def activations(self, value: list[Tensor] | Tensor | None) -> None:
        if value is None:
            self._act_mut().pop("activations", None)
        else:
            self.set_activity("activations", value)

    @property
    def free_state(self) -> list[Tensor] | Tensor | None:
        val = self.activity.get("free_state")
        if isinstance(val, (list, Tensor)):
            return val
        return None

    @free_state.setter
    def free_state(self, value: list[Tensor] | Tensor | None) -> None:
        if value is None:
            self._act_mut().pop("free_state", None)
        else:
            self.set_activity("free_state", value)

    @property
    def nudged_state(self) -> list[Tensor] | Tensor | None:
        val = self.activity.get("nudged_state")
        if isinstance(val, (list, Tensor)):
            return val
        return None

    @nudged_state.setter
    def nudged_state(self, value: list[Tensor] | Tensor | None) -> None:
        if value is None:
            self._act_mut().pop("nudged_state", None)
        else:
            self.set_activity("nudged_state", value)

    @property
    def loss(self) -> Tensor | float | None:
        val = self.activity.get("loss")
        if isinstance(val, (Tensor, float, int)):
            return val
        return None

    @loss.setter
    def loss(self, value: Tensor | float | None) -> None:
        if value is None:
            self._act_mut().pop("loss", None)
        else:
            self.set_activity("loss", value)

    @property
    def metrics(self) -> dict[str, float] | None:
        val = self.activity.get("metrics")
        if isinstance(val, dict):
            return val
        return None

    @metrics.setter
    def metrics(self, value: dict[str, float] | None) -> None:
        if value is None:
            self._act_mut().pop("metrics", None)
        else:
            self.set_activity("metrics", value)

    def __post_init__(self) -> None:
        # Ensure mappings are mutable dicts for in-place updates during stepping
        if not isinstance(self.activity, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            object.__setattr__(self, "activity", dict(self.activity))
        if not isinstance(self.plastic, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            object.__setattr__(self, "plastic", dict(self.plastic))
        if not isinstance(self.substrate, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            object.__setattr__(self, "substrate", dict(self.substrate))

    @classmethod
    def empty(cls) -> CompositeState:
        """Create an empty joint state."""
        return cls(activity={}, plastic={}, substrate={})

    def clone(self) -> CompositeState:
        """Create a deep copy with cloned tensors (detached from graph)."""
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

    def detach_(self) -> CompositeState:
        """Detach all tensors in-place (for stopping gradient flow)."""
        for v in self.activity.values():
            if isinstance(v, Tensor):
                v.detach_()
            elif isinstance(v, list):
                for t in v:
                    t.detach_()
        for v in self.plastic.values():
            v.detach_()
        for v in self.substrate.values():
            v.detach_()
        return self

    def to(self, device: torch.device | str) -> CompositeState:
        """Move all tensors to device."""
        new_activity: dict[str, ActivityValue] = {}
        for k, v in self.activity.items():
            if isinstance(v, Tensor):
                new_activity[k] = v.to(device)
            elif isinstance(v, list):
                new_activity[k] = [t.to(device) for t in v]
            else:
                new_activity[k] = v
        return CompositeState(
            activity=new_activity,
            plastic={k: v.to(device) for k, v in self.plastic.items()},
            substrate={k: v.to(device) for k, v in self.substrate.items()},
        )
