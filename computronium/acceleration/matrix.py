"""Implementation Matrix Generator.

Prints a table of all registered implementations from the registry.
"""

import argparse
import json

from computronium.acceleration.registry import all_specs


def main():
    parser = argparse.ArgumentParser(description="Generate implementation matrix")
    parser.add_argument(
        "--format", choices=["table", "json", "markdown"], default="table"
    )
    args = parser.parse_args()

    specs = all_specs()

    if not specs:
        if args.format == "json":
            print(json.dumps([]))
        else:
            print("No implementations registered.")
        return

    if args.format == "json":
        data = []
        for spec in specs:
            data.append({
                "id": spec.id,
                "kind": spec.kind,
                "name": spec.name,
                "axis": spec.axis,
                "supported_backends": list(spec.supported_backends),
                "status": spec.status,
                "kernel_technology": spec.kernel_technology,
                "summary": spec.summary,
            })
        print(json.dumps(data, indent=2))
        return

    if args.format == "markdown":
        print("| ID | KIND | AXIS | BACKENDS | STATUS |")
        print("|----|------|------|----------|--------|")
        for spec in specs:
            axis = spec.axis or ""
            backends = ",".join(spec.supported_backends)
            print(f"| {spec.id} | {spec.kind} | {axis} | {backends} | {spec.status} |")
        return

    # Default table format
    print(f"{'ID':<55} {'KIND':<10} {'AXIS':<20} {'BACKENDS':<20} {'STATUS'}")
    print("-" * 130)

    for spec in specs:
        axis = spec.axis or ""
        backends = ",".join(spec.supported_backends)
        print(f"{spec.id:<55} {spec.kind:<10} {axis:<20} {backends:<20} {spec.status}")


if __name__ == "__main__":
    main()
