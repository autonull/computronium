"""Plugin metadata and registry."""

from __future__ import annotations

import importlib.metadata
import warnings
from dataclasses import dataclass, field
from typing import Any, ClassVar

from computronium.plugins.core.protocols import PluginProtocol

PLUGIN_ENTRY_POINT_GROUP = "computronium.plugins"


@dataclass(frozen=True, slots=True)
class PluginMetadata:
    """Metadata for a registered plugin."""

    name: str
    version: str
    plugin_type: str
    entry_point_name: str
    module_name: str
    class_name: str
    description: str
    author: str | None = None
    license: str | None = None
    dependencies: list[str] = field(default_factory=list)
    hooks: dict[str, str] = field(default_factory=dict)


class PluginRegistry:
    """Registry for discovered and loaded plugins."""

    _instance: ClassVar[PluginRegistry | None] = None

    def __new__(cls) -> PluginRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._plugins: dict[str, PluginProtocol] = {}
            self._metadata: dict[str, PluginMetadata] = {}
            self._load_plugins()
            self._initialized = True

    def _load_plugins(self) -> None:
        """Discover and load plugins from entry points."""
        try:
            eps = importlib.metadata.entry_points(group=PLUGIN_ENTRY_POINT_GROUP)
        except Exception:
            eps = []

        for ep in eps:
            self._load_entry_point(ep)

    def _load_entry_point(self, ep: importlib.metadata.EntryPoint) -> None:
        """Load a single entry point."""
        try:
            plugin_class = ep.load()
            plugin_instance = plugin_class()
            plugin_type = self._detect_plugin_type(plugin_instance)
            if plugin_type:
                key = f"{plugin_type}:{self._get_plugin_key_name(plugin_instance, plugin_type)}"
                self._plugins[key] = plugin_instance
                self._metadata[key] = PluginMetadata(
                    name=self._get_plugin_key_name(plugin_instance, plugin_type),
                    version=getattr(plugin_class, "__version__", "0.1.0"),
                    plugin_type=plugin_type,
                    entry_point_name=ep.name,
                    module_name=ep.module,
                    class_name=plugin_class.__name__,
                    description=plugin_instance.description,
                    author=getattr(plugin_class, "__author__", None),
                    license=getattr(plugin_class, "__license__", None),
                    dependencies=list(getattr(plugin_class, "__dependencies__", [])),
                )
        except Exception as e:
            warnings.warn(f"Failed to load plugin {ep.name}: {e}", RuntimeWarning)

    def _detect_plugin_type(self, plugin: Any) -> str | None:
        """Detect which protocol a plugin implements."""
        if hasattr(plugin, "requires") and callable(getattr(plugin, "requires", None)):
            return "objective"
        if hasattr(plugin, "substrate_type"):
            return "substrate"
        if hasattr(plugin, "dynamics_type"):
            return "dynamics"
        if hasattr(plugin, "topology_type"):
            return "geometry"
        if hasattr(plugin, "credit_type"):
            return "credit"
        if hasattr(plugin, "update_type"):
            return "update"
        if hasattr(plugin, "plasticity_type"):
            return "plasticity"
        return None

    _TYPE_ATTR_MAP: dict[str, str] = {
        "objective": "name",
        "substrate": "substrate_type",
        "dynamics": "dynamics_type",
        "geometry": "topology_type",
        "credit": "credit_type",
        "update": "update_type",
        "plasticity": "plasticity_type",
    }

    def _get_plugin_key_name(self, plugin: Any, plugin_type: str) -> str:
        """Get the name to use for the plugin key."""
        attr = self._TYPE_ATTR_MAP.get(plugin_type)
        if attr and hasattr(plugin, attr):
            return getattr(plugin, attr)
        return "unknown"

    def get_display_name(self, plugin: PluginProtocol) -> str:
        """Get the display name for a plugin."""
        plugin_type = self._detect_plugin_type(plugin)
        if plugin_type:
            return self._get_plugin_key_name(plugin, plugin_type)
        return "unknown"

    def register(self, plugin: PluginProtocol) -> None:
        """Manually register a plugin instance (for hot-reload)."""
        plugin_type = self._detect_plugin_type(plugin)
        if plugin_type:
            key = f"{plugin_type}:{self._get_plugin_key_name(plugin, plugin_type)}"
            self._plugins[key] = plugin

    def unregister(self, plugin_type: str, name: str) -> None:
        """Unregister a plugin."""
        key = f"{plugin_type}:{name}"
        self._plugins.pop(key, None)
        self._metadata.pop(key, None)

    def get(self, plugin_type: str, name: str) -> PluginProtocol | None:
        """Get a plugin by type and name."""
        return self._plugins.get(f"{plugin_type}:{name}")

    def list(self, plugin_type: str | None = None) -> dict[str, PluginProtocol]:
        """List all plugins, optionally filtered by type."""
        if plugin_type:
            return {
                k: v
                for k, v in self._plugins.items()
                if k.startswith(f"{plugin_type}:")
            }
        return dict(self._plugins)

    def metadata(self, plugin_type: str, name: str) -> PluginMetadata | None:
        """Get plugin metadata."""
        return self._metadata.get(f"{plugin_type}:{name}")

    def all_metadata(self, plugin_type: str | None = None) -> dict[str, PluginMetadata]:
        """Get all plugin metadata."""
        if plugin_type:
            return {
                k: v
                for k, v in self._metadata.items()
                if k.startswith(f"{plugin_type}:")
            }
        return dict(self._metadata)

    def reload(self) -> None:
        """Reload all plugins from entry points (hot-reload)."""
        self._plugins.clear()
        self._metadata.clear()
        self._load_plugins()


# Global registry instance
registry = PluginRegistry()
