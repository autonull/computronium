"""Schema versioning and evolution for experiment records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from computronium.experiment.schema.record import Record


class SchemaReader(Protocol):
    """Protocol for schema version readers."""

    def read(self, data: dict[str, Any]) -> Record:
        """Read a record from versioned data."""
        ...


@dataclass(frozen=True, slots=True)
class UnknownField:
    """Preserved unknown field from a newer schema version."""

    name: str
    value: Any


@dataclass(frozen=True, slots=True)
class SchemaVersion:
    """Schema version metadata."""

    version: int
    reader: SchemaReader
    description: str = ""


class SchemaRegistry:
    """Registry of schema readers for forward-compatible reads.

    New schema versions are appended; readers for old versions are never
    removed (append-only). Unknown fields are preserved as UnknownField
    objects for round-trip fidelity (R79).
    """

    def __init__(self) -> None:
        self._readers: dict[int, SchemaReader] = {}
        self._unknown_fields: dict[int, list[UnknownField]] = {}

    def register(
        self, version: int, reader: SchemaReader, description: str = ""
    ) -> None:
        """Register a reader for a schema version."""
        if version in self._readers:
            raise ValueError(f"Reader for version {version} already registered")
        self._readers[version] = reader

    def get_reader(self, version: int) -> SchemaReader | None:
        """Get the reader for a specific version."""
        return self._readers.get(version)

    def get_latest_version(self) -> int:
        """Get the latest registered schema version."""
        return max(self._readers.keys()) if self._readers else 1

    def read_record(self, data: dict[str, Any]) -> Record:
        """Read a record using the appropriate versioned reader."""
        version = data.get("schema_version", 1)
        reader = self.get_reader(version)
        if reader is None:
            # Fall back to latest reader for forward compatibility
            reader = self.get_reader(self.get_latest_version())
            if reader is None:
                raise ValueError(f"No reader available for schema version {version}")

        # Preserve unknown fields
        known_fields = set(Record.__dataclass_fields__.keys())
        unknown = {k: v for k, v in data.items() if k not in known_fields}
        if unknown:
            self._unknown_fields.setdefault(version, []).extend(
                UnknownField(name=k, value=v) for k, v in unknown.items()
            )

        return reader.read(data)

    def get_unknown_fields(self, version: int) -> tuple[UnknownField, ...]:
        """Get preserved unknown fields for a version."""
        return tuple(self._unknown_fields.get(version, ()))


# Global schema registry
SCHEMA_REGISTRY = SchemaRegistry()


class V1Reader:
    """Reader for schema version 1 (current)."""

    def read(self, data: dict[str, Any]) -> Record:
        return Record.from_dict(data)


# Register version 1 reader
SCHEMA_REGISTRY.register(1, V1Reader(), "Initial schema")


def get_schema_registry() -> SchemaRegistry:
    """Get the global schema registry."""
    return SCHEMA_REGISTRY


def current_schema_version() -> int:
    """Get the current schema version."""
    return SCHEMA_REGISTRY.get_latest_version()


__all__ = [
    "SCHEMA_REGISTRY",
    "SchemaReader",
    "SchemaRegistry",
    "SchemaVersion",
    "UnknownField",
    "current_schema_version",
    "get_schema_registry",
]
