#!/usr/bin/env python3
"""Progress preview utilities for experiment_shallow.sh.

This module replaces the inline bash preview logic with a clean Python
implementation that shares constants with the pipeline.
"""

from __future__ import annotations

from ._budget_constants import format_preview


def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("Usage: preview.py <hours>", file=sys.stderr)
        sys.exit(1)

    try:
        hours = float(sys.argv[1])
    except ValueError:
        print(f"Invalid hours value: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)

    print(format_preview(hours))


if __name__ == "__main__":
    main()
