"""Base classes for plugin development."""

from __future__ import annotations

from typing import Any, ClassVar


class BaseObjectivePlugin:
    """Base class for objective plugins."""

    name: ClassVar[str]
    description: ClassVar[str] = ""

    def compute(self, payload: dict[str, Any], **kwargs: Any) -> float:
        raise NotImplementedError

    def requires(self) -> list[str]:
        raise NotImplementedError


class BaseSubstratePlugin:
    """Base class for substrate plugins."""

    substrate_type: ClassVar[str]
    description: ClassVar[str] = ""

    def create_config(self, **kwargs: Any) -> Any:
        raise NotImplementedError

    def create_substrate(self, config: Any) -> Any:
        raise NotImplementedError


class BaseDynamicsPlugin:
    """Base class for dynamics plugins."""

    dynamics_type: ClassVar[str]
    description: ClassVar[str] = ""

    def create_config(self, **kwargs: Any) -> Any:
        raise NotImplementedError

    def create_dynamics(self, config: Any) -> Any:
        raise NotImplementedError


class BaseGeometryPlugin:
    """Base class for geometry plugins."""

    topology_type: ClassVar[str]
    description: ClassVar[str] = ""

    def create_config(self, **kwargs: Any) -> Any:
        raise NotImplementedError

    def create_geometry(self, config: Any) -> Any:
        raise NotImplementedError


class BaseCreditPlugin:
    """Base class for credit plugins."""

    credit_type: ClassVar[str]
    description: ClassVar[str] = ""

    def create_config(self, **kwargs: Any) -> Any:
        raise NotImplementedError

    def create_credit(self, config: Any) -> Any:
        raise NotImplementedError


class BaseUpdatePlugin:
    """Base class for update plugins."""

    update_type: ClassVar[str]
    description: ClassVar[str] = ""

    def create_config(self, **kwargs: Any) -> Any:
        raise NotImplementedError

    def create_update(self, config: Any) -> Any:
        raise NotImplementedError


class BasePlasticityPlugin:
    """Base class for plasticity plugins."""

    plasticity_type: ClassVar[str]
    description: ClassVar[str] = ""

    def create_config(self, **kwargs: Any) -> Any:
        raise NotImplementedError

    def create_plasticity(self, config: Any) -> Any:
        raise NotImplementedError
