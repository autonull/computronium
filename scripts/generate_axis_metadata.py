#!/usr/bin/env python3
"""Generate axis metadata JSON from Python registries for frontend consumption.

Single source of truth for structural axis definitions, primitives, and metadata.
"""

from __future__ import annotations

import json

# Import the registries from the Python codebase
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from computronium.ontology.credit import (
    GradientCredit,
    HomeostaticCredit,
    LemmaCredit,
    LocalContrastiveCredit,
    LocalGoodnessCredit,
    PCALMCredit,
    PepitaCredit,
    RandomProjectionsCredit,
    TargetInversionCredit,
    TemporalTraceCredit,
)
from computronium.ontology.dynamics._registry import DYNAMICS_REGISTRY
from computronium.ontology.geometry import _GEOMETRY_BACKENDS
from computronium.ontology.plasticity import (
    ClosedFormRidgePlasticity,
    ConflictAdaptivePsiPlasticity,
    FastWeightPlasticity,
    NullPlasticity,
    RoutingPlasticity,
    RuleStatePlasticity,
    SubstrateCoupledPlasticity,
    TemporalPsiPlasticity,
)
from computronium.ontology.substrate import (
    AnalogSubstrate,
    ComplexSubstrate,
    DigitalSubstrate,
    MemristiveSubstrate,
    NeuromorphicSubstrate,
    NoisySubstrate,
    OpticalSubstrate,
    QuantizedSubstrate,
    QuantumSubstrate,
    SparseSubstrate,
    TernarySubstrate,
)
from computronium.ontology.update import _UPDATE_BACKENDS


def primitive_to_dict(name: str, cls: type) -> dict:
    """Convert a primitive class to a metadata dict."""
    doc = cls.__doc__ or ""
    summary = doc.strip().split("\n")[0] if doc else ""
    return {
        "name": name,
        "summary": summary,
        "class_name": cls.__name__,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_path = (
        root
        / "computronium"
        / "experiment"
        / "execution"
        / "dashboard"
        / "src"
        / "axis-metadata.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Substrate primitives
    substrate_classes = {
        "digital": DigitalSubstrate,
        "memristive": MemristiveSubstrate,
        "neuromorphic": NeuromorphicSubstrate,
        "photonic": OpticalSubstrate,
        "complex": ComplexSubstrate,
        "analog": AnalogSubstrate,
        "quantum": QuantumSubstrate,
        "sparse": SparseSubstrate,
        "noisy": NoisySubstrate,
        "quantized": QuantizedSubstrate,
        "ternary": TernarySubstrate,
    }

    # Credit primitives (from credit.py)
    credit_classes = {
        "gradient": GradientCredit,
        "pepita": PepitaCredit,
        "random_projections": RandomProjectionsCredit,
        "local_goodness": LocalGoodnessCredit,
        "local_contrastive": LocalContrastiveCredit,
        "target_inversion": TargetInversionCredit,
        "temporal_trace": TemporalTraceCredit,
        "homeostatic": HomeostaticCredit,
        "pca_lm": PCALMCredit,
        "lemma": LemmaCredit,
    }

    # Geometry primitives (from registry)
    geometry_classes = {k: v.cls for k, v in _GEOMETRY_BACKENDS.items()}

    # Dynamics primitives (from registry)
    dynamics_classes = DYNAMICS_REGISTRY

    # Plasticity primitives
    plasticity_classes = {
        "null": NullPlasticity,
        "routing": RoutingPlasticity,
        "fast_weights": FastWeightPlasticity,
        "substrate_coupled": SubstrateCoupledPlasticity,
        "hebbian_plasticity": ClosedFormRidgePlasticity,
        "stdp": TemporalPsiPlasticity,
        "conflict_adaptive_psi": ConflictAdaptivePsiPlasticity,
        "rule_state": RuleStatePlasticity,
    }

    # Update primitives (from registry)
    update_classes = _UPDATE_BACKENDS

    axes = {
        "credit": {
            "display_name": "Credit Assignment",
            "description": "How learning signals are assigned to parameters",
            "primitives": [
                primitive_to_dict(name, cls) for name, cls in credit_classes.items()
            ],
        },
        "substrate": {
            "display_name": "Substrate",
            "description": "Physical/computational substrate for computation",
            "primitives": [
                primitive_to_dict(name, cls) for name, cls in substrate_classes.items()
            ],
        },
        "geometry": {
            "display_name": "Geometry",
            "description": "Network architecture and connectivity pattern",
            "primitives": [
                primitive_to_dict(name, cls) for name, cls in geometry_classes.items()
            ],
        },
        "dynamics": {
            "display_name": "Dynamics",
            "description": "State evolution and settling dynamics",
            "primitives": [
                primitive_to_dict(name, cls) for name, cls in dynamics_classes.items()
            ],
        },
        "plasticity": {
            "display_name": "Plasticity",
            "description": "Local learning and adaptation mechanisms",
            "primitives": [
                primitive_to_dict(name, cls) for name, cls in plasticity_classes.items()
            ],
        },
        "update": {
            "display_name": "Update Rule",
            "description": "Parameter update optimization algorithm",
            "primitives": [
                primitive_to_dict(name, cls) for name, cls in update_classes.items()
            ],
        },
    }

    axis_order = ["credit", "geometry", "dynamics", "substrate", "plasticity", "update"]

    metadata = {
        "axes": axes,
        "axis_order": axis_order,
    }

    out_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"✓ Generated {out_path}")


if __name__ == "__main__":
    main()
