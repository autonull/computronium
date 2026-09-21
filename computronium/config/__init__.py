"""
Configuration schemas and defaults for Bioplausible experiments.

Unified ExperimentConfig (Sprint 7) is the single source of truth.
"""

from computronium.config.defaults import (
    DEFAULT_CONFIGS,
    get_named_config,
    list_named_configs,
    register_default_config,
)
from computronium.config.experiment import (
    DataConfig,
    ExperimentConfig,
    HardwareConfig,
    ModelConfig,
    SystemConfig,
    TrainingConfig,
    from_omegaconf,
    to_deployment_config,
    to_omegaconf,
    to_system_trainer_config,
    to_tile_algorithm_config,
    to_trainer_config,
)
from computronium.config.unified import (
    BaseConfig,
    BaseStructuredConfig,
)

__all__ = [
    "DEFAULT_CONFIGS",
    "BaseConfig",
    "BaseStructuredConfig",
    "DataConfig",
    "ExperimentConfig",
    "HardwareConfig",
    "ModelConfig",
    "SystemConfig",
    "TrainingConfig",
    "from_omegaconf",
    "get_named_config",
    "list_named_configs",
    "register_default_config",
    "to_deployment_config",
    "to_omegaconf",
    "to_system_trainer_config",
    "to_tile_algorithm_config",
    "to_trainer_config",
]
