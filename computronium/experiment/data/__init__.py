"""Dataset management (Phase E6)."""

from __future__ import annotations

from .dataset_registry import (
    DatasetRegistration,
    DatasetRegistry,
    DatasetSplit,
    DatasetVersion,
    create_dataset_manifest,
    get_git_sha,
)

__all__ = [
    "DatasetRegistration",
    "DatasetRegistry",
    "DatasetSplit",
    "DatasetVersion",
    "create_dataset_manifest",
    "get_git_sha",
]
