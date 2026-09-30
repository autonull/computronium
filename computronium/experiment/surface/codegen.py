"""Code generation from registries (WP11.2 / abc3 §2.5).

Generates:
- docs/generated/ listings (capabilities, objectives, axes, constraints, priors, policies, stages)
- Compatibility matrix from CONSTRAINTS (R63)
- JSON-Schema validators per AxisSpec (R5 runtime discovery)
- Conformance stubs per CapabilitySpec
- CLI flag tables
"""

from __future__ import annotations

import json
from dataclasses import fields
from datetime import datetime
from pathlib import Path
from typing import Any

from computronium.experiment.schema.axis import (
    AXES_REGISTRIES,
    AxisSpec,
    Domain,
    HyperparameterSpec,
    StructuralAxis,
)
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CONSTRAINTS_REGISTRY,
    OBJECTIVES_REGISTRY,
    POLICIES_REGISTRY,
    PRIORS_REGISTRY,
    STAGES_REGISTRY,
)

__all__ = [
    "generate_all",
    "generate_axes_listing",
    "generate_capabilities_listing",
    "generate_cli_flag_tables",
    "generate_compatibility_matrix",
    "generate_conformance_stubs",
    "generate_constraints_listing",
    "generate_json_schema_validators",
    "generate_objectives_listing",
    "generate_policies_listing",
    "generate_priors_listing",
    "generate_stages_listing",
    "write_generated_docs",
]


def _dataclass_to_dict(obj: Any) -> dict[str, Any]:
    """Convert dataclass to dict, handling enums and special types."""
    result = {}
    for field in fields(obj):
        value = getattr(obj, field.name)
        if hasattr(value, "value"):  # Enum
            result[field.name] = value.value
        elif hasattr(value, "__dict__"):  # Nested dataclass or object
            result[field.name] = (
                _dataclass_to_dict(value)
                if hasattr(value, "__dataclass_fields__")
                else str(value)
            )
        elif isinstance(value, list | tuple | set):
            result[field.name] = list(value)
        elif value is None:
            result[field.name] = None
        else:
            result[field.name] = value
    return result


def generate_capabilities_listing() -> list[dict[str, Any]]:
    """Generate capabilities listing for docs/generated/capabilities.md."""
    capabilities = []
    for cap_id, spec in sorted(CAPABILITIES_REGISTRY.items()):
        capabilities.append({
            "capability_id": spec.capability_id,
            "name": spec.name,
            "kind": spec.kind.value,
            "display_name": spec.display_name,
            "description": spec.description,
            "required": spec.required,
            "gated_by": spec.gated_by,
            "stage": spec.stage,
            "owner": spec.owner,
            "verifying_test": spec.verifying_test,
            "flags": list(spec.flags),
            "status": spec.status.value,
            "retirement_record": spec.retirement_record,
        })
    return capabilities


def generate_objectives_listing() -> list[dict[str, Any]]:
    """Generate objectives listing for docs/generated/objectives.md."""
    objectives = []
    for obj_id, spec in sorted(OBJECTIVES_REGISTRY.items()):
        objectives.append(_dataclass_to_dict(spec))
    return objectives


def generate_axes_listing() -> list[dict[str, Any]]:
    """Generate axes listing for docs/generated/axes.md.

    Iterates all structural axis registries.
    """
    axes = []
    for axis_kind, registry in AXES_REGISTRIES.items():
        for axis_id, spec in sorted(registry.items()):
            axes.append(_axis_spec_to_dict(spec, axis_kind))
    return axes


def _axis_spec_to_dict(spec: AxisSpec, axis_kind: StructuralAxis) -> dict[str, Any]:
    """Convert AxisSpec to dict with structural axis info."""
    return {
        "name": spec.name,
        "structural_axis": axis_kind.value,
        "description": spec.description,
        "available": spec.available,
        "axis_kind": spec.axis_kind.value,
        "availability_predicate": str(spec.availability_predicate)
        if spec.availability_predicate
        else None,
        "prior": spec.prior,
        "override_scope": spec.override_scope,
        "topology_params": [
            {
                "name": hp.name,
                "domain": _domain_to_dict(hp.domain),
                "axis_kind": hp.axis_kind.value,
                "axis_name": hp.axis_name,
                "availability": str(hp.availability) if hp.availability else None,
                "prior": hp.prior,
                "override_scope": hp.override_scope,
            }
            for hp in spec.topology_params
        ],
    }


def _domain_to_dict(domain: Domain) -> dict[str, Any]:
    """Convert Domain to dict."""
    if domain.members is not None:
        return {"type": "enumerated", "members": list(domain.members)}
    else:
        return {
            "type": "range",
            "lo": domain.lo,
            "hi": domain.hi,
            "scale": domain.scale.value,
        }


def generate_constraints_listing() -> list[dict[str, Any]]:
    """Generate constraints listing for docs/generated/constraints.md."""
    constraints = []
    for constr_id, spec in sorted(CONSTRAINTS_REGISTRY.items()):
        d = _dataclass_to_dict(spec)
        # Convert Expr predicate to string representation
        if spec.predicate is not None:
            d["predicate"] = str(spec.predicate)
        constraints.append(d)
    return constraints


def generate_priors_listing() -> list[dict[str, Any]]:
    """Generate priors listing for docs/generated/priors.md."""
    priors = []
    for prior_id, spec in sorted(PRIORS_REGISTRY.items()):
        priors.append(_dataclass_to_dict(spec))
    return priors


def generate_policies_listing() -> list[dict[str, Any]]:
    """Generate policies listing for docs/generated/policies.md."""
    policies = []
    for policy_id, spec in sorted(POLICIES_REGISTRY.items()):
        policies.append(_dataclass_to_dict(spec))
    return policies


def generate_stages_listing() -> list[dict[str, Any]]:
    """Generate stages listing for docs/generated/stages.md."""
    stages = []
    for stage_id, spec in sorted(STAGES_REGISTRY.items()):
        stages.append(_dataclass_to_dict(spec))
    return stages


def generate_compatibility_matrix() -> dict[str, Any]:
    """Generate compatibility matrix from CONSTRAINTS (R63).

    Returns a matrix showing which axis combinations are compatible/void.
    """
    # Build matrix from void constraints
    void_constraints = [
        spec for spec in CONSTRAINTS_REGISTRY.values() if spec.kind.value == "void"
    ]

    matrix = {
        "void_constraints": [],
        "axis_pairs": {},
    }

    for constraint in void_constraints:
        matrix["void_constraints"].append({
            "name": constraint.name,
            "description": constraint.description,
            "predicate": str(constraint.predicate) if constraint.predicate else None,
            "proof_kind": constraint.proof_kind.value
            if constraint.proof_kind
            else None,
        })

    # Extract axis pairs from predicates (simplified)
    # This would be expanded with actual parsing
    structural_axes = [a.value for a in StructuralAxis]
    for i, a1 in enumerate(structural_axes):
        for a2 in structural_axes[i + 1 :]:
            matrix["axis_pairs"][f"{a1}×{a2}"] = {
                "compatible": True,  # Default; void constraints override
                "void_reasons": [],
            }

    return matrix


def _axis_spec_to_json_schema(spec: AxisSpec) -> dict[str, Any]:
    """Convert AxisSpec to JSON Schema for runtime validation (R5)."""
    # For structural axes, generate schema for topology_params
    schema: dict[str, Any] = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": f"AxisSpec: {spec.name}",
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    # Add topology_params as properties
    for hp in spec.topology_params:
        prop = _hyperparameter_to_json_schema(hp)
        schema["properties"][hp.name] = prop
        # All topology params are required
        schema["required"].append(hp.name)

    # Add availability as conditional (simplified)
    if spec.availability_predicate:
        schema["properties"]["available_when"] = {
            "type": "string",
            "description": str(spec.availability_predicate),
        }

    return schema


def _hyperparameter_to_json_schema(hp: HyperparameterSpec) -> dict[str, Any]:
    """Convert HyperparameterSpec to JSON Schema property."""
    domain = hp.domain
    if domain.members is not None:
        return {
            "type": "string",
            "enum": domain.members,
            "description": f"Axis kind: {hp.axis_kind.value}, Availability: {hp.availability}",
        }
    else:
        prop: dict[str, Any] = {"type": "number"}
        if domain.lo is not None:
            prop["minimum"] = domain.lo
        if domain.hi is not None:
            prop["maximum"] = domain.hi
        prop["description"] = (
            f"Axis kind: {hp.axis_kind.value}, Availability: {hp.availability}"
        )
        return prop


def generate_json_schema_validators() -> dict[str, dict[str, Any]]:
    """Generate JSON Schema validators per AxisSpec (R5 runtime discovery)."""
    validators = {}
    for axis_kind, registry in AXES_REGISTRIES.items():
        for axis_id, spec in sorted(registry.items()):
            validators[f"{axis_kind.value}.{axis_id}"] = _axis_spec_to_json_schema(spec)
    return validators


def generate_conformance_stubs() -> dict[str, str]:
    """Generate conformance test stubs per CapabilitySpec."""
    stubs = {}
    for cap_id, spec in sorted(CAPABILITIES_REGISTRY.items()):
        if not spec.required:
            continue

        if spec.verifying_test:
            # Generate a test that runs the verifying test
            stub = f'''"""Conformance test for {spec.capability_id}: {spec.display_name}"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_{spec.capability_id.lower()}() -> None:
    """Verify {spec.capability_id} capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "{spec.verifying_test}",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {{output}}"
'''
        else:
            # Generate a stub that checks for evidence in store
            stub = f'''"""Conformance test stub for {spec.capability_id}: {spec.display_name}"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.
# TODO: Implement evidence-based check for {spec.capability_id}

import pytest


def test_conformance_{spec.capability_id.lower()}_stub() -> None:
    """Stub for {spec.capability_id} - no verifying_test defined."""
    pytest.skip(f"No verifying_test defined for {spec.capability_id}")
'''

        stubs[f"test_conformance_{spec.capability_id.lower()}.py"] = stub

    return stubs


def generate_cli_flag_tables() -> dict[str, list[dict[str, Any]]]:
    """Generate CLI flag tables from registries."""
    tables = {}

    # Capability flags table
    capability_flags = []
    for cap_id, spec in sorted(CAPABILITIES_REGISTRY.items()):
        for flag in spec.flags:
            capability_flags.append({
                "flag": flag,
                "capability_id": spec.capability_id,
                "display_name": spec.display_name,
                "kind": spec.kind.value,
            })
    tables["capability_flags"] = capability_flags

    # Objective flags (axis_tag as pseudo-flag)
    objective_flags = []
    for obj_id, spec in sorted(OBJECTIVES_REGISTRY.items()):
        if spec.axis_tag:
            objective_flags.append({
                "axis_tag": spec.axis_tag,
                "objective_name": spec.name,
                "direction": spec.direction,
            })
    tables["objective_axis_tags"] = objective_flags

    # Constraint kinds as flags
    constraint_flags = []
    for constr_id, spec in sorted(CONSTRAINTS_REGISTRY.items()):
        constraint_flags.append({
            "kind": spec.kind.value,
            "constraint_name": spec.name,
            "origin": spec.origin,
            "proof_kind": spec.proof_kind.value if spec.proof_kind else None,
        })
    tables["constraint_kinds"] = constraint_flags

    return tables


def write_generated_docs(output_dir: str | Path = "docs/generated") -> None:
    """Write all generated documentation to output directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Write listings as JSON
    (output_path / "capabilities.json").write_text(
        json.dumps(generate_capabilities_listing(), indent=2)
    )
    (output_path / "objectives.json").write_text(
        json.dumps(generate_objectives_listing(), indent=2)
    )
    (output_path / "axes.json").write_text(
        json.dumps(generate_axes_listing(), indent=2)
    )
    (output_path / "constraints.json").write_text(
        json.dumps(generate_constraints_listing(), indent=2)
    )
    (output_path / "priors.json").write_text(
        json.dumps(generate_priors_listing(), indent=2)
    )
    (output_path / "policies.json").write_text(
        json.dumps(generate_policies_listing(), indent=2)
    )
    (output_path / "stages.json").write_text(
        json.dumps(generate_stages_listing(), indent=2)
    )

    # Write compatibility matrix
    (output_path / "compatibility_matrix.json").write_text(
        json.dumps(generate_compatibility_matrix(), indent=2)
    )

    # Write JSON Schema validators
    (output_path / "json_schema_validators.json").write_text(
        json.dumps(generate_json_schema_validators(), indent=2)
    )

    # Write CLI flag tables
    (output_path / "cli_flag_tables.json").write_text(
        json.dumps(generate_cli_flag_tables(), indent=2)
    )

    # Write conformance stubs as individual files
    stubs_dir = output_path / "conformance_stubs"
    stubs_dir.mkdir(exist_ok=True)
    for filename, content in generate_conformance_stubs().items():
        (stubs_dir / filename).write_text(content)

    # Write markdown summaries
    _write_capabilities_md(output_path / "capabilities.md")
    _write_objectives_md(output_path / "objectives.md")
    _write_axes_md(output_path / "axes.md")
    _write_stages_md(output_path / "stages.md")


def _write_capabilities_md(path: Path) -> None:
    """Write capabilities as markdown table."""
    capabilities = generate_capabilities_listing()
    lines = [
        "# Capabilities Registry",
        "",
        f"Generated: {datetime.now().isoformat()}",
        f"Total: {len(capabilities)} capabilities",
        "",
        "| ID | Name | Kind | Required | Stage | Owner | Verifying Test | Flags | Status |",
        "|----|------|------|----------|-------|-------|----------------|-------|--------|",
    ]
    for cap in capabilities:
        flags_str = ", ".join(cap["flags"])
        lines.append(
            f"| {cap['capability_id']} | {cap['display_name']} | {cap['kind']} | "
            f"{'✓' if cap['required'] else '✗'} | {cap['stage'] or '-'} | "
            f"{cap['owner'] or '-'} | {cap['verifying_test'] or '-'} | "
            f"{flags_str} | {cap['status']} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_objectives_md(path: Path) -> None:
    """Write objectives as markdown table."""
    objectives = generate_objectives_listing()
    lines = [
        "# Objectives Registry",
        "",
        f"Generated: {datetime.now().isoformat()}",
        f"Total: {len(objectives)} objectives",
        "",
        "| Name | Direction | Weight | Normalizer | Axis Tag |",
        "|------|-----------|--------|------------|----------|",
    ]
    for obj in objectives:
        lines.append(
            f"| {obj['name']} | {obj['direction']} | {obj['weight']} | "
            f"{obj['normalizer'] or '-'} | {obj['axis_tag'] or '-'} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_axes_md(path: Path) -> None:
    """Write axes as markdown table."""
    axes = generate_axes_listing()
    lines = [
        "# Axes Registry",
        "",
        f"Generated: {datetime.now().isoformat()}",
        f"Total: {len(axes)} axes",
        "",
        "| Structural Axis | Name | Axis Kind | Available | Prior | Override Scope | Topology Params |",
        "|-----------------|------|-----------|-----------|-------|----------------|-----------------|",
    ]
    for axis in axes:
        topo_params = ", ".join(hp["name"] for hp in axis.get("topology_params", []))
        avail_str = str(axis.get("availability_predicate") or "always")
        if len(avail_str) > 30:
            avail_str = avail_str[:27] + "..."
        lines.append(
            f"| {axis.get('structural_axis', '-')} | {axis.get('name', '-')} | "
            f"{axis.get('axis_kind', '-')} | {avail_str} | {axis.get('prior', '-')} | "
            f"{axis.get('override_scope', '-')} | {topo_params or '-'} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_stages_md(path: Path) -> None:
    """Write stages as markdown table."""
    stages = generate_stages_listing()
    lines = [
        "# Pipeline Stages",
        "",
        f"Generated: {datetime.now().isoformat()}",
        f"Total: {len(stages)} stages",
        "",
        "| Stage ID | Name | Display Name | Required Fidelity | Min Seeds | Gate |",
        "|----------|------|--------------|-------------------|-----------|------|",
    ]
    for stage in stages:
        lines.append(
            f"| {stage['stage_id']} | {stage['name']} | {stage['display_name']} | "
            f"{stage['required_fidelity']} | {stage['min_n_seeds']} | {stage['gate']} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_all(output_dir: str | Path = "docs/generated") -> dict[str, Any]:
    """Generate all codegen artifacts and return summary."""
    write_generated_docs(output_dir)

    total_axes = sum(len(r) for r in AXES_REGISTRIES.values())

    return {
        "capabilities": len(CAPABILITIES_REGISTRY),
        "objectives": len(OBJECTIVES_REGISTRY),
        "axes": total_axes,
        "constraints": len(CONSTRAINTS_REGISTRY),
        "priors": len(PRIORS_REGISTRY),
        "policies": len(POLICIES_REGISTRY),
        "stages": len(STAGES_REGISTRY),
        "output_dir": str(output_dir),
        "generated_at": datetime.now().isoformat(),
    }
