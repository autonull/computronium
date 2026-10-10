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
    # Protocols
    "PluginProtocol",
    "ObjectivePlugin",
    "SubstratePlugin",
    "DynamicsPlugin",
    "GeometryPlugin",
    "CreditPlugin",
    "UpdatePlugin",
    "PlasticityPlugin",
    # Registry
    "registry",
    "PluginMetadata",
    "PLUGIN_ENTRY_POINT_GROUP",
    # Hot-reload
    "HotReloader",
    # Base classes
    "BaseObjectivePlugin",
    "BaseSubstratePlugin",
    "BaseDynamicsPlugin",
    "BaseGeometryPlugin",
    "BaseCreditPlugin",
    "BaseUpdatePlugin",
    "BasePlasticityPlugin",
    # Examples
    "ExampleObjectivePlugin",
]

# Convenience: expose CLI main
from computronium.plugins.cli import main as plugin_cli_main

main = plugin_cli_main  # noqa: PLR0401 (expose CLI entry point)
