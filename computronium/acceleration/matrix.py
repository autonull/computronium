"""Implementation Matrix Generator.

Prints a table of all registered implementations from the registry.
"""

import argparse
import json
import sys

from computronium.acceleration.registry import all_specs


def _match_axis(spec, value: str) -> bool:
    return spec.axis == value


def _match_kind(spec, value: str) -> bool:
    return spec.kind == value


def _match_status(spec, value: str) -> bool:
    return spec.status == value


def _match_id(spec, value: str) -> bool:
    return value in spec.id


def _match_name(spec, value: str) -> bool:
    return value.lower() in spec.name.lower()


_FILTER_FUNCS = {
    "axis": _match_axis,
    "kind": _match_kind,
    "status": _match_status,
    "id": _match_id,
    "name": _match_name,
}


def _matches_filter(spec, filters: dict[str, str]) -> bool:
    """Check if a spec matches all given filters."""
    for key, value in filters.items():
        func = _FILTER_FUNCS.get(key)
        if func is None:
            print(f"Warning: unknown filter key '{key}', ignoring", file=sys.stderr)
            continue
        if not func(spec, value):
            return False
    return True


def _print_table(specs) -> None:
    """Print default table format."""
    print(
        f"{'ID':<55} {'KIND':<10} {'AXIS':<20} {'BACKENDS':<20} {'STATUS':<18} {'KERNEL TECH':<15}"
    )
    print("-" * 150)
    for spec in specs:
        axis = spec.axis or ""
        backends = ",".join(spec.supported_backends)
        kernel_tech = spec.kernel_technology or ""
        print(
            f"{spec.id:<55} {spec.kind:<10} {axis:<20} {backends:<20} {spec.status:<18} {kernel_tech:<15}"
        )


def _print_markdown(specs) -> None:
    """Print GitHub-flavored markdown format."""
    print("| ID | KIND | AXIS | BACKENDS | STATUS | KERNEL TECH | SUMMARY |")
    print("|----|------|------|----------|--------|-------------|---------|")
    for spec in specs:
        axis = spec.axis or ""
        backends = ",".join(spec.supported_backends)
        kernel_tech = spec.kernel_technology or ""
        summary = (spec.summary or "")[:60]
        print(
            f"| {spec.id} | {spec.kind} | {axis} | {backends} | {spec.status} | {kernel_tech} | {summary} |"
        )


def _print_json(specs) -> None:
    """Print JSON format."""
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


def _parse_filters(filter_list: list[str]) -> dict[str, str]:
    """Parse filter arguments into a dictionary.

    Supports both comma-separated (--filter "axis=state_dynamics,kind=primitive")
    and repeated flags (--filter axis=state_dynamics --filter kind=primitive).
    """
    filters = {}
    for f in filter_list:
        # Split on comma first, then on equals
        parts = f.split(",")
        for part in parts:
            if "=" not in part:
                print(
                    f"Invalid filter format: {part} (expected key=value)",
                    file=sys.stderr,
                )
                continue
            key, value = part.split("=", 1)
            filters[key.strip()] = value.strip()
    return filters


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate implementation matrix")
    parser.add_argument(
        "--format",
        choices={"table", "json", "markdown", "github-markdown"},
        default="table",
    )
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="Filter specs: axis=state_dynamics, kind=primitive, status=kernel_unverified, id=partial_id, name=partial_name",
    )
    args = parser.parse_args()

    specs = all_specs()
    filters = _parse_filters(args.filter)

    if filters:
        specs = tuple(s for s in specs if _matches_filter(s, filters))

    if not specs:
        if args.format == "json":
            print(json.dumps([]))
        else:
            print("No implementations registered matching filters.")
        return

    if args.format in {"markdown", "github-markdown"}:
        _print_markdown(specs)
    elif args.format == "json":
        _print_json(specs)
    else:
        _print_table(specs)


if __name__ == "__main__":
    main()
