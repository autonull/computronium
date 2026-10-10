"""Hot-reload support for plugin development."""

from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)


class HotReloader:
    """Hot-reload support for plugin development."""

    def __init__(self, watch_paths: Iterable[Path] | None = None) -> None:
        self.watch_paths = list(watch_paths) if watch_paths else []
        self._watched_modules: dict[str, float] = {}

    def add_watch_path(self, path: Path) -> None:
        """Add a path to watch for changes."""
        if path not in self.watch_paths:
            self.watch_paths.append(path)

    def check_and_reload(self) -> list[str]:
        """Check for changes and reload plugins. Returns list of reloaded plugins."""
        reloaded = []

        for watch_path in self.watch_paths:
            for py_file in watch_path.rglob("*.py"):
                self._check_file(py_file, reloaded)

        if reloaded:
            from computronium.plugins.core.registry import registry

            registry.reload()

        return reloaded

    def _check_file(self, py_file: Path, reloaded: list[str]) -> None:
        try:
            mtime = py_file.stat().st_mtime
        except OSError:
            return

        key = str(py_file)
        if self._watched_modules.get(key) != mtime:
            self._watched_modules[key] = mtime
            module_name = self._path_to_module(py_file)
            if module_name:
                reloaded.extend(self._reload_module(module_name))

    def _path_to_module(self, path: Path) -> str | None:
        """Convert file path to module name."""
        try:
            for sp in sys.path:
                sp_path = Path(sp).resolve()
                if path.is_relative_to(sp_path):
                    rel = path.relative_to(sp_path)
                    return ".".join(rel.with_suffix("").parts)
        except ValueError, OSError:
            pass
        return None

    def _reload_module(self, module_name: str) -> list[str]:
        """Reload a module and re-register any plugin classes."""
        reloaded = []
        module = self._get_or_reload_module(module_name)
        if module is None:
            return reloaded

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr not in _BASE_PLUGIN_CLASSES:
                self._try_register_plugin(attr, reloaded)

        return reloaded

    def _get_or_reload_module(self, module_name: str) -> object | None:
        """Get or reload a module."""
        try:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                importlib.import_module(module_name)
            return sys.modules[module_name]
        except Exception as e:  # ruff: ignore[blind-except]
            logger.debug("Failed to reload module %s: %s", module_name, e)
            return None

    def _try_register_plugin(self, attr: type, reloaded: list[str]) -> None:
        try:
            instance = attr()
            self._register_plugin_instance(instance, reloaded)
        except Exception as e:  # ruff: ignore[blind-except]
            logger.debug("Failed to register plugin %s: %s", attr.__name__, e)

    def _register_plugin_instance(self, instance: object, reloaded: list[str]) -> None:
        from computronium.plugins.core.registry import registry

        plugin_type = registry._detect_plugin_type(instance)
        if plugin_type:
            registry.register(instance)  # type: ignore[arg-type]
            reloaded.append(f"{plugin_type}:{instance.name}")  # type: ignore[attr-defined]


# Lazy import to avoid circular imports
_BASE_PLUGIN_CLASSES: tuple[type, ...] = ()


def _get_base_plugin_classes() -> tuple[type, ...]:
    """Get base plugin classes (lazy initialization)."""
    global _BASE_PLUGIN_CLASSES  # ruff: ignore[global-statement]
    if not _BASE_PLUGIN_CLASSES:
        from computronium.plugins.core.protocols import (
            CreditPlugin,
            DynamicsPlugin,
            GeometryPlugin,
            ObjectivePlugin,
            PlasticityPlugin,
            SubstratePlugin,
            UpdatePlugin,
        )

        _BASE_PLUGIN_CLASSES = (
            ObjectivePlugin,
            SubstratePlugin,
            DynamicsPlugin,
            GeometryPlugin,
            CreditPlugin,
            UpdatePlugin,
            PlasticityPlugin,
        )
    return _BASE_PLUGIN_CLASSES


# Initialize base classes on import
_get_base_plugin_classes()
