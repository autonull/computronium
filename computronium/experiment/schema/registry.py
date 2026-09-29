"""Generic registry for experiment specifications."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import TypeVar

SpecT = TypeVar("SpecT")


@dataclass(frozen=True, slots=True)
class RegistryDiff:
    """Difference between two registry states."""

    added: frozenset[str]
    removed: frozenset[str]
    changed: frozenset[str]


class Registry[SpecT]:
    """Thread-safe generic registry for specifications.

    Specs must be frozen dataclasses with a `name` field (str) as the key.
    """

    def __init__(self) -> None:
        self._specs: dict[str, SpecT] = {}
        self._lock = threading.RLock()

    def register(self, spec: SpecT) -> None:
        """Register a specification. Raises if name already exists."""
        name = getattr(spec, "name", None)
        if not isinstance(name, str):
            raise TypeError(f"Spec {type(spec).__name__} must have a 'name: str' field")
        with self._lock:
            if name in self._specs:
                raise ValueError(f"Duplicate registration: {name}")
            self._specs[name] = spec

    def unregister(self, name: str) -> None:
        """Unregister a specification by name."""
        with self._lock:
            if name not in self._specs:
                raise KeyError(f"Not registered: {name}")
            del self._specs[name]

    def get(self, name: str) -> SpecT | None:
        """Get a specification by name."""
        with self._lock:
            return self._specs.get(name)

    def __getitem__(self, name: str) -> SpecT:
        with self._lock:
            return self._specs[name]

    def __contains__(self, name: str) -> bool:
        with self._lock:
            return name in self._specs

    def __iter__(self):
        with self._lock:
            return iter(self._specs.values())

    def keys(self) -> frozenset[str]:
        with self._lock:
            return frozenset(self._specs.keys())

    def values(self) -> tuple[SpecT, ...]:
        with self._lock:
            return tuple(self._specs.values())

    def items(self) -> tuple[tuple[str, SpecT], ...]:
        with self._lock:
            return tuple(self._specs.items())

    def diff(self, other: Registry[SpecT]) -> RegistryDiff:
        """Compute difference between this registry and another."""
        with self._lock:
            self_keys = set(self._specs.keys())
        with other._lock:
            other_keys = set(other._specs.keys())

        added = frozenset(other_keys - self_keys)
        removed = frozenset(self_keys - other_keys)

        changed: set[str] = set()
        for key in self_keys & other_keys:
            with self._lock:
                self_spec = self._specs[key]
            with other._lock:
                other_spec = other._specs[key]
            if self_spec != other_spec:
                changed.add(key)
        changed_frozen = frozenset(changed)

        return RegistryDiff(added=added, removed=removed, changed=changed_frozen)

    def integrity_check(self) -> list[str]:
        """Validate registry integrity. Returns list of issues (empty if OK)."""
        issues = []
        with self._lock:
            for name, spec in self._specs.items():
                spec_name = getattr(spec, "name", None)
                if spec_name != name:
                    issues.append(f"Name mismatch: key={name}, spec.name={spec_name}")
                if not hasattr(spec, "__dataclass_fields__"):
                    issues.append(f"Spec {name} is not a dataclass")
        return issues

    def clear(self) -> None:
        """Clear all registrations (for testing)."""
        with self._lock:
            self._specs.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._specs)

    def __repr__(self) -> str:
        with self._lock:
            return f"Registry({len(self._specs)} specs: {sorted(self._specs.keys())})"
