"""Plugin protocols for structural typing."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ObjectivePlugin(ABC):
    """Protocol for custom objective functions."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        ...

    @abstractmethod
    def compute(self, payload: dict[str, Any], **kwargs: Any) -> float:
        """Compute objective value from run payload metrics."""
        ...

    @abstractmethod
    def requires(self) -> list[str]:
        """Return list of metric keys required from payload."""
        ...


class SubstratePlugin(ABC):
    """Protocol for custom substrate implementations."""

    @property
    @abstractmethod
    def substrate_type(self) -> str:
        """Substrate type identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        ...

    @abstractmethod
    def create_config(self, **kwargs: Any) -> Any:
        """Create substrate configuration from kwargs."""
        ...

    @abstractmethod
    def create_substrate(self, config: Any) -> Any:
        """Instantiate substrate from config."""
        ...


class DynamicsPlugin(ABC):
    """Protocol for custom dynamics/settling implementations."""

    @property
    @abstractmethod
    def dynamics_type(self) -> str:
        """Dynamics type identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        ...

    @abstractmethod
    def create_config(self, **kwargs: Any) -> Any:
        """Create dynamics configuration from kwargs."""
        ...

    @abstractmethod
    def create_dynamics(self, config: Any) -> Any:
        """Instantiate dynamics from config."""
        ...


class GeometryPlugin(ABC):
    """Protocol for custom geometry implementations."""

    @property
    @abstractmethod
    def topology_type(self) -> str:
        """Topology type identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        ...

    @abstractmethod
    def create_config(self, **kwargs: Any) -> Any:
        """Create geometry configuration from kwargs."""
        ...

    @abstractmethod
    def create_geometry(self, config: Any) -> Any:
        """Instantiate geometry from config."""
        ...


class CreditPlugin(ABC):
    """Protocol for custom credit assignment implementations."""

    @property
    @abstractmethod
    def credit_type(self) -> str:
        """Credit type identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        ...

    @abstractmethod
    def create_config(self, **kwargs: Any) -> Any:
        """Create credit configuration from kwargs."""
        ...

    @abstractmethod
    def create_credit(self, config: Any) -> Any:
        """Instantiate credit from config."""
        ...


class UpdatePlugin(ABC):
    """Protocol for custom parameter update implementations."""

    @property
    @abstractmethod
    def update_type(self) -> str:
        """Update type identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        ...

    @abstractmethod
    def create_config(self, **kwargs: Any) -> Any:
        """Create update configuration from kwargs."""
        ...

    @abstractmethod
    def create_update(self, config: Any) -> Any:
        """Instantiate update from config."""
        ...


class PlasticityPlugin(ABC):
    """Protocol for custom plasticity implementations."""

    @property
    @abstractmethod
    def plasticity_type(self) -> str:
        """Plasticity type identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        ...

    @abstractmethod
    def create_config(self, **kwargs: Any) -> Any:
        """Create plasticity configuration from kwargs."""
        ...

    @abstractmethod
    def create_plasticity(self, config: Any) -> Any:
        """Instantiate plasticity from config."""
        ...


# Union type for all plugins
type PluginProtocol = (
    ObjectivePlugin
    | SubstratePlugin
    | DynamicsPlugin
    | GeometryPlugin
    | CreditPlugin
    | UpdatePlugin
    | PlasticityPlugin
)
