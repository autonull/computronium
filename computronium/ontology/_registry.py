"""Generic Implementation Registry.

Unifies the decorator-based registration pattern used across ontology layers:
- geometry_backend (geometry.py)
- dynamics_backend (dynamics/_registry.py)
- update_backend (update/__init__.py)
- credit_backend (planned)
- substrate_backend (planned)

Provides a single source of truth for registration, discovery, and dispatch.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterable

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class BackendEntry[T]:
    """A registered implementation backend."""

    cls: type[T]
    build: Callable[[object], T]
    aliases: tuple[str, ...]


class ImplementationRegistry[T]:
    """Generic registry for implementation backends.

    Usage:
        registry = ImplementationRegistry[MyProtocol]("my_protocol")

        @registry.register("alias1", "alias2")
        class MyImpl:
            ...

        impl = registry.get("alias1")  # Returns MyImpl
        instance = registry.build("alias1", config)
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._backends: dict[str, BackendEntry[T]] = {}
        self._discovered: bool = False
        self._discovery_packages: list[str] = []

    def register(
        self,
        *aliases: str,
        build: Callable[[object], T] | None = None,
    ) -> Callable[[type[T]], type[T]]:
        """Register an implementation under the given aliases.

        Args:
            aliases: One or more string keys this implementation answers to.
            build: Optional custom builder (config -> instance). Defaults to cls(config).
        """

        def decorator(cls: type[T]) -> type[T]:
            entry = BackendEntry(
                cls=cls,
                build=build if build is not None else cls,
                aliases=aliases,
            )
            for alias in aliases:
                if alias in self._backends:
                    existing = self._backends[alias]
                    if existing.cls is not cls:
                        raise ValueError(
                            f"{self.name}: backend '{alias}' already registered to "
                            f"{existing.cls.__name__}, cannot register {cls.__name__}"
                        )
                self._backends[alias] = entry
            return cls

        return decorator

    def get(self, alias: str) -> type[T]:
        """Get the implementation class for an alias."""
        entry = self._backends.get(alias)
        if entry is None:
            self._discover()
            entry = self._backends.get(alias)
        if entry is None:
            raise KeyError(
                f"{self.name}: no backend registered for '{alias}'. "
                f"Available: {sorted(self._backends.keys())}"
            )
        return entry.cls

    def build(self, alias: str, config: object) -> T:
        """Instantiate the backend for an alias with a config."""
        entry = self._backends.get(alias)
        if entry is None:
            self._discover()
            entry = self._backends.get(alias)
        if entry is None:
            raise KeyError(
                f"{self.name}: no backend registered for '{alias}'. "
                f"Available: {sorted(self._backends.keys())}"
            )
        return entry.build(config)

    def all(self) -> dict[str, BackendEntry[T]]:
        """Get all registered backends."""
        self._discover()
        return dict(self._backends)

    def aliases(self) -> tuple[str, ...]:
        """Get all registered aliases."""
        self._discover()
        return tuple(self._backends.keys())

    def group_by_attribute(self, attr: str) -> dict[str, list[str]]:
        """Group registered aliases by a class attribute value.

        Args:
            attr: The class attribute to group by (e.g., "kind", "axis").

        Returns:
            Dictionary mapping attribute value to list of aliases.
        """
        self._discover()
        groups: dict[str, list[str]] = defaultdict(list)
        for alias, entry in self._backends.items():
            value = getattr(entry.cls, attr, None)
            if value is not None:
                groups[str(value)].append(alias)
        return dict(groups)

    def add_discovery_package(self, package: str) -> None:
        """Add a package to discover implementations from."""
        if package not in self._discovery_packages:
            self._discovery_packages.append(package)

    def _discover(self) -> None:
        """Discover and register implementations from packages."""
        if self._discovered:
            return

        for package_name in self._discovery_packages:
            package = importlib.import_module(package_name)
            package_path = getattr(package, "__path__", None)
            package_name_attr = getattr(package, "__name__", None)
            if package_path is None or package_name_attr is None:
                continue

            for _, module_name, _ in pkgutil.walk_packages(
                package_path, package_name_attr + "."
            ):
                module = importlib.import_module(module_name)
                # Check for SPEC attribute (primitives/algorithms pattern)
                if hasattr(module, "SPEC"):
                    # The module should have registered itself via the decorator
                    pass

        self._discovered = True

    def clear(self) -> None:
        """Clear all registrations (mainly for testing)."""
        self._backends.clear()
        self._discovered = False


def create_registry[T](name: str) -> ImplementationRegistry[T]:
    """Factory function to create a typed registry."""
    return ImplementationRegistry[T](name)
