"""The states a map row may carry (TODO97 §0), in one declaration.

The screen writes a row state and the audit reads it. They used to hold two
vocabularies -- the map wrote ``defect`` and the gate compared ``defective`` --
so the gate's lock predicates could never fire. This module is the one source:
the writer, the audit, and the tests import the same members.

A state owes evidence. ``measured`` carries its number and ruler; ``refused``
is a box statement (the declared families or the declared shape exclude the
cell); the other three owe a test, listed in :data:`ROW_LOCKS`. Only a
``refused`` row is quiet, and it is quiet because its trigger names the rule.
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


class RowStatus(StrEnum):
    """The state of one ``(primitive, family, box)`` row."""

    MEASURED = "measured"
    UNMEASURED = "unmeasured"
    #: No box composes: the families, the shape, or the cost cap exclude it.
    REFUSED = "refused"
    #: Cannot compose by math, shape, or API; owes a refusal and a necessity test.
    IMPOSSIBLE = "impossible"
    #: The primitive, feature, box, or budget does not exist yet.
    UNIMPLEMENTED = "unimplemented"
    #: It exists and should work, but does not.
    DEFECTIVE = "defective"


#: The evidence a row of that state owes the audit.
ROW_LOCKS: Mapping[RowStatus, tuple[str, ...]] = MappingProxyType({
    RowStatus.IMPOSSIBLE: ("refusal_test", "necessity_test"),
    RowStatus.UNIMPLEMENTED: ("failing_test",),
    RowStatus.DEFECTIVE: ("failing_test",),
})

#: The evaluator's cell statuses, in row states. One mapping, both directions
#: of the contract: the writer maps a cell, the audit reads the same member.
CELL_STATUS: Mapping[str, RowStatus] = MappingProxyType({
    "MEASURED": RowStatus.MEASURED,
    "DEFECT": RowStatus.DEFECTIVE,
    "UNAVAILABLE": RowStatus.REFUSED,
})


def row_state(row: Mapping[str, object]) -> RowStatus | None:
    """The row's state, or ``None`` when its status is not a declared one."""
    try:
        return RowStatus(str(row.get("status")))
    except ValueError:
        return None


def missing_locks(row: Mapping[str, object]) -> list[str]:
    """The evidence keys this row's state owes and does not carry.

    Args:
        row: One map row, with its ``status`` and its lock keys.

    Returns:
        The missing keys, in declaration order; empty for a quiet row and for
        an undeclared status, which the caller reports as its own finding.
    """
    status = row_state(row)
    if status is None:
        return []
    return [key for key in ROW_LOCKS.get(status, ()) if not row.get(key)]
