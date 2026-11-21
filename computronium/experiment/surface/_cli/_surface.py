"""The declared test surface command: ``comp test --surface``.

Prints what TODO98 tests: 75 laws joined with their axis declarations, the
six protocol seams, and the rule tables. Exits 0 when the surface agrees with
the registry; a disagreement is a wiring defect, not a documentation gap.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

    from computronium.primitives.surface import Surface

__all__ = ["_cmd_test"]


def _render(declared: Surface) -> None:
    """Print the surface's three units as tables."""
    independent, dependent, availability = declared.tables
    print(
        f"The declared test surface: {len(declared.laws)} laws, "
        f"{len(declared.seams)} seams, {len(declared.rules)} rules "
        f"({independent} task-independent, {dependent} task-dependent, "
        f"{availability} availability)"
    )
    print()
    print(f"{'law':54} {'axis':10} {'family':12} state")
    for law in declared.laws:
        state = (law.refusal and f"refused: {law.refusal}") or ""
        state = state or (law.gap and "gap: no mechanism") or "declared"
        print(f"{law.id:54} {law.axis:10} {law.family:12} {state}")
    print()
    print(f"{'seam':18} {'axis':10} {'task':18} exchange")
    for seam in declared.seams:
        print(f"{seam.name:18} {seam.axis:10} {seam.task_id:18} {seam.exchange}")
    print()
    print(f"{'rule':40} table")
    for rule in declared.rules:
        print(f"{rule.name:40} {rule.table}")


def _cmd_test(args: Namespace) -> int:
    """List the declared surface, or name the flag that asks for it."""
    if not args.surface:
        print(
            "comp test: pass --surface to list the declared test surface",
            file=sys.stderr,
        )
        return 2
    from computronium.primitives.surface import surface, validate

    declared = surface()
    problems = validate(declared)
    _render(declared)
    for problem in problems:
        print(f"surface: {problem}", file=sys.stderr)
    return 1 if problems else 0
