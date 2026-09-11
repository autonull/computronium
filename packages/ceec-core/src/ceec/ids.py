"""Stable, unique ID policy for the CEEC ledger."""

from __future__ import annotations

from typing import Literal

IDPrefix = Literal[
    "A", "E", "D", "B", "G", "X", "DEC", "GO", "SC", "CAL", "BR", "GR", "IR"
]

PREFIX_BY_KIND: dict[str, str] = {
    "artifact": "A",
    "evidence": "E",
    "derived": "D",
    "belief": "B",
    "goal": "G",
    "experiment": "X",
    "decision": "DEC",
    "gate_outcome": "GO",
    "status_change": "SC",
    "calibration_record": "CAL",
    "belief_revision": "BR",
    "goal_revision": "GR",
    "instrument_note": "IR",
}

_ID_ERROR = "id must match '<prefix>-<suffix>' with declared prefix"


def validate_id(id_: str, prefix: str, *alt_prefixes: str) -> str:
    prefixes = (prefix, *alt_prefixes)
    if not any(id_.startswith(f"{p}-") for p in prefixes):
        raise ValueError(f"{_ID_ERROR}: {id_!r} (expected prefixes {prefixes})")
    if not any(len(id_) > len(p) + 1 for p in prefixes):
        raise ValueError(f"{_ID_ERROR}: {id_!r}")
    return id_


def prefix_for(kind: str) -> str:
    return PREFIX_BY_KIND[kind]
