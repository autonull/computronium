"""Implementation Matrix Generator.

Prints a table of all registered implementations from the registry.
"""

from computronium.acceleration.registry import all_specs


def main():
    specs = all_specs()

    if not specs:
        print("No implementations registered.")
        return

    # Header
    print(f"{'ID':<55} {'KIND':<10} {'AXIS':<20} {'BACKENDS':<20} {'STATUS'}")
    print("-" * 130)

    for spec in specs:
        axis = spec.axis or ""
        backends = ",".join(spec.supported_backends)
        print(f"{spec.id:<55} {spec.kind:<10} {axis:<20} {backends:<20} {spec.status}")


if __name__ == "__main__":
    main()
