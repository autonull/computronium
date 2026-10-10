"""Plugin API — Extensibility for custom objectives, substrates, dynamics.

Provides entry point registration, protocol-based extension points,
and hot-reload support for development.

Public API:
    - Protocols: ObjectivePlugin, SubstratePlugin, DynamicsPlugin, GeometryPlugin,
      CreditPlugin, UpdatePlugin, PlasticityPlugin
    - Base classes: BaseObjectivePlugin, BaseSubstratePlugin, BaseDynamicsPlugin,
      BaseGeometryPlugin, BaseCreditPlugin, BaseUpdatePlugin, BasePlasticityPlugin
    - Registry: registry, PluginMetadata
    - Hot-reload: HotReloader
    - CLI: comp plugin
"""

from __future__ import annotations

from computronium.plugins.cli import main as plugin_cli_main
from computronium.plugins.core.base import (
    BaseCreditPlugin,
    BaseDynamicsPlugin,
    BaseGeometryPlugin,
    BaseObjectivePlugin,
    BasePlasticityPlugin,
    BaseSubstratePlugin,
    BaseUpdatePlugin,
)
from computronium.plugins.core.hotreload import HotReloader
from computronium.plugins.core.protocols import (
    CreditPlugin,
    DynamicsPlugin,
    GeometryPlugin,
    ObjectivePlugin,
    PlasticityPlugin,
    PluginProtocol,
    SubstratePlugin,
    UpdatePlugin,
)
from computronium.plugins.core.registry import (
    PLUGIN_ENTRY_POINT_GROUP,
    PluginMetadata,
    registry,
)
from computronium.plugins.examples import ExampleObjectivePlugin

__all__ = [
    "PLUGIN_ENTRY_POINT_GROUP",
    "BaseCreditPlugin",
    "BaseDynamicsPlugin",
    "BaseGeometryPlugin",
    "BaseObjectivePlugin",
    "BasePlasticityPlugin",
    "BaseSubstratePlugin",
    "BaseUpdatePlugin",
    "CreditPlugin",
    "DynamicsPlugin",
    "ExampleObjectivePlugin",
    "GeometryPlugin",
    "HotReloader",
    "ObjectivePlugin",
    "PlasticityPlugin",
    "PluginMetadata",
    "PluginProtocol",
    "SubstratePlugin",
    "UpdatePlugin",
    "registry",
]

# Convenience: expose CLI main
main = plugin_cli_main  # ruff: ignore[non-empty-init-module]
