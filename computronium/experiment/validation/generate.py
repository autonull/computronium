"""Validation code generation from registries (B10).

Generates:
- Substrate-dynamics compatibility matrix (Python/TypeScript)
- Geometry-dynamics compatibility matrix
- Credit-update compatibility matrix
- Void constraint declarations
- Availability predicate expressions

Run: python -m computronium.experiment.validation.generate
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from computronium.experiment.schema.registries import (
    CONSTRAINTS_REGISTRY,
    ConstraintKind,
)
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.schema.axis import (
    StructuralAxis,
    AXES_REGISTRIES,
    get_axis_spec,
)
from computronium.experiment.schema.axis import StructuralAxis


def generate_substrate_dynamics_matrix() -> dict[str, dict[str, bool]]:
    """Generate substrate × dynamics compatibility matrix from void constraints."""
    seed_all_registries()

    substrates = list(AXES_REGISTRIES[StructuralAxis.SUBSTRATE].keys())
    dynamics = list(AXES_REGISTRIES[StructuralAxis.DYNAMICS].keys())

    # Default: all compatible
    matrix = {s: {d: True for d in dynamics} for s in substrates}

    # Apply void constraints
    for constraint in CONSTRAINTS_REGISTRY.values():
        if constraint.kind != ConstraintKind.VOID:
            continue

        # Parse void constraint to extract incompatible pairs
        # Constraints are logical expressions - we need to evaluate them
        # For now, use the hardcoded known incompatibilities
        pass

    # Known void constraints (from CONSTRAINTS_REGISTRY and search_space.py)
    void_pairs = {
        # Neuromorphic substrate requires temporal dynamics
        ("neuromorphic", "instantaneous"): False,
        ("neuromorphic", "lazy"): False,
        ("neuromorphic", "predictive_settling"): False,
        ("neuromorphic", "error_predictive_coding"): False,
        ("neuromorphic", "pc_alm"): False,
        ("neuromorphic", "diffusion"): True,  # Actually allowed

        # Quantum substrate
        ("quantum", "spike_integration"): False,
        ("quantum", "lazy"): False,
        ("quantum", "predictive_settling"): False,
        ("quantum", "error_predictive_coding"): False,
        ("quantum", "pc_alm"): False,

        # Ternary substrate incompatible with pc_alm
        ("ternary", "pc_alm"): False,

        # Neuromorphic allowed dynamics
        ("neuromorphic", "spike_integration"): True,
        ("neuromorphic", "energy_minimization"): True,
        ("neuromorphic", "diffusion"): True,
    }

    for (sub, dyn), compat in void_pairs.items():
        if sub in matrix and dyn in matrix[sub]:
            matrix[sub][dyn] = compat

    return matrix


def generate_geometry_dynamics_matrix() -> dict[str, dict[str, bool]]:
    """Generate geometry × dynamics compatibility matrix from void constraints."""
    seed_all_registries()

    geometries = list(AXES_REGISTRIES[StructuralAxis.GEOMETRY].keys())
    dynamics = list(AXES_REGISTRIES[StructuralAxis.DYNAMICS].keys())

    matrix = {g: {d: True for d in dynamics} for g in geometries}

    # Recurrent geometries require settling dynamics
    recurrent_geoms = {"recurrent", "recurrent_attractor"}
    settling_dynamics = {
        "energy_minimization", "predictive_settling", "error_predictive_coding",
        "pc_alm", "diffusion", "instantaneous"
    }

    for geom in recurrent_geoms:
        if geom in matrix:
            for dyn in dynamics:
                if dyn not in settling_dynamics:
                    matrix[geom][dyn] = False

    # Non-layered geometries require instantaneous dynamics
    non_layered = {
        "attention", "spatial_lattice", "graph", "conv", "nca",
        "ntm", "causal_transformer"
    }

    for geom in non_layered:
        if geom in matrix:
            for dyn in dynamics:
                if dyn != "instantaneous":
                    matrix[geom][dyn] = False

    return matrix


def generate_credit_update_matrix() -> dict[str, dict[str, bool]]:
    """Generate credit × update compatibility from known issues."""
    seed_all_registries()

    credits = list(AXES_REGISTRIES[StructuralAxis.CREDIT].keys())
    updates = list(AXES_REGISTRIES[StructuralAxis.UPDATE].keys())

    matrix = {c: {u: True for u in updates} for c in credits}

    # Known problematic combinations (from gate calibration analysis)
    # homeostatic + euclidean on digital -> BFloat16 mismatch
    matrix["homeostatic"]["euclidean"] = "conditional"  # substrate-dependent
    matrix["target_inversion"]["muon"] = "conditional"  # BFloat16 mismatch
    matrix["homeostatic"]["natural_gradient"] = "conditional"  # Bool tensor issue
    matrix["pc_alm"]["euclidean"] = "conditional"  # Bool tensor issue

    return matrix


def generate_availability_predicates() -> dict[str, str]:
    """Generate availability predicate expressions from axis specs."""
    seed_all_registries()

    predicates = {}
    for axis in StructuralAxis:
        registry = AXES_REGISTRIES[axis]
        for name, spec in registry.items():
            if spec.availability_predicate is not None:
                predicates[f"{axis.value}.{name}"] = str(spec.availability_predicate)

    return predicates


def generate_void_constraints() -> list[dict[str, Any]]:
    """Extract void constraints from registry."""
    seed_all_registries()

    void_constraints = []
    for name, constraint in CONSTRAINTS_REGISTRY.items():
        if constraint.kind == ConstraintKind.VOID:
            void_constraints.append({
                "name": name,
                "expression": str(constraint.predicate) if constraint.predicate else "",
                "description": constraint.description,
            })

    return void_constraints


def write_outputs(output_dir: Path = Path("docs/generated")) -> None:
    """Write all generated validation artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Substrate × Dynamics
    sub_dyn = generate_substrate_dynamics_matrix()
    (output_dir / "substrate_dynamics_compat.json").write_text(json.dumps(sub_dyn, indent=2))

    # Geometry × Dynamics
    geom_dyn = generate_geometry_dynamics_matrix()
    (output_dir / "geometry_dynamics_compat.json").write_text(json.dumps(geom_dyn, indent=2))

    # Credit × Update
    cred_upd = generate_credit_update_matrix()
    (output_dir / "credit_update_compat.json").write_text(json.dumps(cred_upd, indent=2))

    # Availability predicates
    preds = generate_availability_predicates()
    (output_dir / "availability_predicates.json").write_text(json.dumps(preds, indent=2))

    # Void constraints
    voids = generate_void_constraints()
    (output_dir / "void_constraints.json").write_text(json.dumps(voids, indent=2))

    # TypeScript types for frontend
    ts_output = generate_typescript_types(sub_dyn, geom_dyn, cred_upd)
    (output_dir / "validation_types.ts").write_text(ts_output)

    print(f"Generated validation artifacts in {output_dir}")


def generate_typescript_types(
    sub_dyn: dict,
    geom_dyn: dict,
    cred_upd: dict,
) -> str:
    """Generate TypeScript types for frontend validation."""
    return f"""// Auto-generated validation types - DO NOT EDIT
// Generated by: python -m computronium.experiment.validation.generate

export interface SubstrateDynamicsCompat {{
  [substrate: string]: {{
    [dynamics: string]: boolean;
  }};
}}

export interface GeometryDynamicsCompat {{
  [geometry: string]: {{
    [dynamics: string]: boolean;
  }};
}}

export interface CreditUpdateCompat {{
  [credit: string]: {{
    [update: string]: boolean | "conditional";
  }};
}}

export const SUBSTRATE_DYNAMICS_COMPAT: SubstrateDynamicsCompat = {json.dumps(sub_dyn, indent=2)};

export const GEOMETRY_DYNAMICS_COMPAT: GeometryDynamicsCompat = {json.dumps(geom_dyn, indent=2)};

export const CREDIT_UPDATE_COMPAT: CreditUpdateCompat = {json.dumps(cred_upd, indent=2)};

export function isSubstrateDynamicsCompatible(substrate: string, dynamics: string): boolean {{
  return SUBSTRATE_DYNAMICS_COMPAT[substrate]?.[dynamics] ?? true;
}}

export function isGeometryDynamicsCompatible(geometry: string, dynamics: string): boolean {{
  return GEOMETRY_DYNAMICS_COMPAT[geometry]?.[dynamics] ?? true;
}}

export function isCreditUpdateCompatible(credit: string, update: string): boolean | "conditional" {{
  return CREDIT_UPDATE_COMPAT[credit]?.[update] ?? true;
}}
"""


if __name__ == "__main__":
    write_outputs()