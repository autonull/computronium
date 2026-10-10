"""Environment capture and snapshots (Phase E7)."""

from __future__ import annotations

from .snapshots import (
    ContainerEnvironment,
    ContainerManager,
    EnvironmentCapture,
    EnvironmentSnapshot,
    GitEnvironment,
    PythonEnvironment,
    SystemEnvironment,
    create_environment_snapshot,
    verify_environment,
)

__all__ = [
    "ContainerEnvironment",
    "ContainerManager",
    "EnvironmentCapture",
    "EnvironmentSnapshot",
    "GitEnvironment",
    "PythonEnvironment",
    "SystemEnvironment",
    "create_environment_snapshot",
    "verify_environment",
]
