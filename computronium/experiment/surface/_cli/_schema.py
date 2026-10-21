"""The surface CLI's schema dump."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.core.logging import get_logger
from computronium.experiment.schema.run_spec import (
    AxisSelection,
    RunSpec,
)

if TYPE_CHECKING:
    import argparse

logger = get_logger()


def _cmd_schema(args: argparse.Namespace) -> int:
    """Dump JSON schemas for experiment models."""

    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    # Import models

    schemas = {}

    if args.model in {"runspec", "all"}:
        schemas["RunSpec"] = RunSpec.model_json_schema()
        schemas["AxisSelection"] = AxisSelection.model_json_schema()
        schemas["Fidelity"] = {"type": "string", "enum": ["L0", "L1", "L2"]}

    if args.model in {"coordinate", "all"}:
        schemas["Coordinate"] = _dataclass_to_schema(Coordinate)
        schemas["Schedule"] = _dataclass_to_schema(Schedule)

    if args.model in {"objectives", "all"}:
        # Build objectives schema from registry
        objectives_schema = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }
        for name, spec in OBJECTIVES_REGISTRY.items():
            obj_schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "const": name},
                    "metric_key": {"type": ["string", "null"]},
                    "description": {"type": "string"},
                    "axis_tag": {"type": ["string", "null"]},
                    "direction": {"type": "string", "enum": ["maximize", "minimize"]},
                    "measured": {"type": "boolean"},
                },
                "required": [
                    "name",
                    "metric_key",
                    "description",
                    "axis_tag",
                    "direction",
                    "measured",
                ],
            }
            objectives_schema["properties"][name] = obj_schema
        schemas["Objectives"] = objectives_schema

    if args.model == "all" and not schemas:
        schemas = {"RunSpec": RunSpec.model_json_schema()}

    # Output
    if args.format == "json":
        output = json.dumps(schemas, indent=2)
    else:
        import yaml

        output = yaml.dump(schemas, sort_keys=False)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        logger.info(f"Schema written to {args.output}")
    else:
        print(output)
    return 0


def _dataclass_to_schema(cls) -> dict:
    """Convert a frozen dataclass to JSON schema."""
    import dataclasses
    from typing import get_type_hints

    hints = get_type_hints(cls)
    properties = {}
    required = []

    for field in dataclasses.fields(cls):
        if field.name.startswith("_"):
            continue
        field_type = hints.get(field.name, Any)
        properties[field.name] = _type_to_schema(field_type)
        if (
            field.default == dataclasses.MISSING
            and field.default_factory == dataclasses.MISSING
        ):
            required.append(field.name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def _type_to_schema(typ) -> dict:  # ruff: ignore[complex-structure, too-many-branches, too-many-return-statements]
    """Convert a Python type to JSON schema."""
    import typing
    from typing import Union, get_args, get_origin

    origin = get_origin(typ)
    args = get_args(typ)

    if typ is str:
        return {"type": "string"}
    elif typ is int:
        return {"type": "integer"}
    elif typ is float:
        return {"type": "number"}
    elif typ is bool:
        return {"type": "boolean"}
    elif typ is None or (origin is type(None)):
        return {"type": "null"}
    elif origin is list or origin is list:
        return {"type": "array", "items": _type_to_schema(args[0]) if args else {}}
    elif origin is dict or origin is dict:
        return {
            "type": "object",
            "additionalProperties": _type_to_schema(args[1]) if len(args) > 1 else {},
        }
    elif origin is tuple or origin is tuple:
        if args and args[-1] is Ellipsis:
            return {"type": "array", "items": _type_to_schema(args[0])}
        return {"type": "array", "prefixItems": [_type_to_schema(a) for a in args]}
    elif origin is Union or origin is typing.Union or typing.get_origin(typ) == Union:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1 and type(None) in args:
            schema = _type_to_schema(non_none[0])
            schema["nullable"] = True
            return schema
        return {"anyOf": [_type_to_schema(a) for a in non_none]}
    elif hasattr(typ, "__pydantic_model__"):
        return typ.__pydantic_model__.model_json_schema()
    elif hasattr(typ, "__dataclass_fields__"):
        return _dataclass_to_schema(typ)
    else:
        return {"type": "object", "description": str(typ)}
