#!/usr/bin/env python
"""Scaffold a kernel implementation for an existing primitive.

Usage:
    uv run python scripts/scaffold_kernel.py \
        --primitive primitive.credit_assignment.random_projections \
        --technology compile

This generates a kernel.py that promotes through the ladder:
    reference -> torch.compile -> Triton

Each rung requires parity + microbench evidence before promotion.
"""

import argparse
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from computronium.acceleration.registry import get


TEMPLATE_DIR = Path(__file__).parent / "templates" / "kernel"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a kernel implementation for a primitive")
    parser.add_argument(
        "--primitive",
        required=True,
        help="Primitive registry ID (e.g., primitive.credit_assignment.random_projections)",
    )
    parser.add_argument(
        "--technology",
        required=True,
        choices=["compile", "triton"],
        help="Kernel technology: 'compile' for torch.compile rung, 'triton' for Triton rung",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print generated kernel without writing"
    )
    parser.add_argument(
        "--output",
        help="Output path (default: overwrites existing kernel.py in primitive package)",
    )

    args = parser.parse_args()

    # Load the primitive spec
    spec = get(args.primitive)

    if spec.kind != "primitive":
        print(f"Error: {args.primitive} is not a primitive (kind={spec.kind})", file=sys.stderr)
        return 1

    if spec.axis in ("geometry", "substrate"):
        print(f"Error: {spec.axis} primitives have different kernel interface", file=sys.stderr)
        return 1

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Derive from reference_entrypoint
        module_path = spec.reference_entrypoint.rsplit(".", 1)[0]
        parts = module_path.split(".")
        # computronium.primitives.credit_assignment.random_projections.reference
        # -> computronium/primitives/credit_assignment/random_projections/kernel.py
        primitive_dir = Path(*parts[:-1])  # drop 'reference'
        output_path = primitive_dir / "kernel.py"

    # Prepare template context
    class_name = "".join(word.capitalize() for word in spec.name.split("_"))
    kernel_tech = args.technology

    context = {
        "spec": spec,
        "spec_id": spec.id,
        "spec_name": spec.name,
        "class_name": class_name,
        "axis": spec.axis,
        "kernel_tech": kernel_tech,
        "reference_entrypoint": spec.reference_entrypoint,
        "parity": spec.parity,
    }

    # Load template
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=select_autoescape(),
    )

    template_name = f"kernel_{kernel_tech}.py.j2"
    try:
        template = env.get_template(template_name)
    except Exception as e:
        print(f"Error: Template {template_name} not found: {e}", file=sys.stderr)
        return 1

    content = template.render(**context)

    if args.dry_run:
        print(f"=== {output_path} ===")
        print(content)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        print(f"Created: {output_path}")
        print(f"\nNext steps:")
        print(f"  1. Review and customize the generated kernel")
        print(f"  2. Run parity test: uv run pytest tests/primitives/{spec.axis}/{spec.name}/test_kernel_parity.py -q")
        print(f"  3. Run microbench: uv run python -m computronium.acceleration.microbench --id {spec.id} --backend kernel")
        print(f"  4. Update spec status to 'kernel_unverified' then 'kernel_verified' after parity passes")

    return 0


if __name__ == "__main__":
    sys.exit(main())