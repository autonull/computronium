#!/usr/bin/env python
"""Scaffold a new primitive package with all required files.

Usage:
    uv run python scripts/scaffold_primitive.py \
        --axis state_dynamics \
        --name energy_minimization \
        --ontology-class EnergyMinimizationDynamics \
        --ontology-module computronium.ontology.dynamics \
        --config-class StateDynamicsConfig.energy_minimization

This generates a complete primitive package under
computronium/primitives/<axis>/<name>/ with:
- __init__.py
- spec.py
- reference.py
- kernel.py
- cases.py

And corresponding test files under tests/primitives/<axis>/<name>/:
- test_reference.py
- test_kernel_parity.py
- test_cases.py
"""

import argparse
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).parent / "templates" / "primitive"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a new primitive package")
    parser.add_argument(
        "--axis",
        required=True,
        choices=[
            "state_dynamics",
            "credit_assignment",
            "parameter_update",
            "plasticity",
            "geometry",
            "substrate",
        ],
        help="Primitive axis",
    )
    parser.add_argument("--name", required=True, help="Primitive name (snake_case)")
    parser.add_argument("--ontology-class", required=True, help="Ontology class name")
    parser.add_argument("--ontology-module", required=True, help="Ontology module path")
    parser.add_argument(
        "--config-class",
        required=True,
        help="Config classmethod (e.g., StateDynamicsConfig.energy_minimization)",
    )
    parser.add_argument("--kernel-tech", default="triton", help="Kernel technology")
    parser.add_argument("--summary", default="", help="Short summary for spec")
    parser.add_argument("--equations", default="", help="Equations for spec")
    parser.add_argument(
        "--invariants", default="", help="Comma-separated invariants for spec"
    )
    parser.add_argument("--notes", default="", help="Notes for spec")
    parser.add_argument("--tags", default="", help="Comma-separated tags for spec")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print files without writing"
    )

    args = parser.parse_args()

    # Prepare template context
    class_name = "".join(word.capitalize() for word in args.name.split("_"))
    invariants_list = [i.strip() for i in args.invariants.split(",") if i.strip()]
    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    context = {
        "axis": args.axis,
        "name": args.name,
        "class_name": class_name,
        "ontology_class": args.ontology_class,
        "ontology_module": args.ontology_module,
        "config_class": args.config_class,
        "kernel_tech": args.kernel_tech,
        "spec_id": f"primitive.{args.axis}.{args.name}",
        "spec_name": " ".join(word.capitalize() for word in args.name.split("_")),
        "summary": args.summary or f"{class_name} primitive.",
        "equations": args.equations,
        "invariants": invariants_list
        or [
            "deterministic under fixed seed",
            "state remains finite",
        ],
        "notes": args.notes or "Reference implementation delegates to ontology class.",
        "tags": tags_list or (args.axis.split("_"),),
    }

    # Load templates
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=select_autoescape(),
    )

    # Define output paths
    primitive_dir = Path(f"computronium/primitives/{args.axis}/{args.name}")
    test_dir = Path(f"tests/primitives/{args.axis}/{args.name}")

    files_to_create = [
        (primitive_dir / "__init__.py", env.get_template("init.py.j2")),
        (primitive_dir / "spec.py", env.get_template("spec.py.j2")),
        (primitive_dir / "reference.py", env.get_template("reference.py.j2")),
        (primitive_dir / "kernel.py", env.get_template("kernel.py.j2")),
        (primitive_dir / "cases.py", env.get_template("cases.py.j2")),
        (test_dir / "test_reference.py", env.get_template("test_reference.py.j2")),
        (
            test_dir / "test_kernel_parity.py",
            env.get_template("test_kernel_parity.py.j2"),
        ),
        (test_dir / "test_cases.py", env.get_template("test_cases.py.j2")),
    ]

    for path, template in files_to_create:
        content = template.render(**context)
        if args.dry_run:
            print(f"=== {path} ===")
            print(content)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print(f"Created: {path}")

    if not args.dry_run:
        print(f"\nPrimitive '{args.name}' scaffolded successfully!")
        print(f"  Primitive: {primitive_dir}")
        print(f"  Tests:     {test_dir}")
        print("\nNext steps:")
        print("  1. Review and customize the generated files")
        print(f"  2. Run tests: uv run pytest {test_dir} -q")
        print("  3. Update ontology imports if needed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
