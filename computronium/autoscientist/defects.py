"""Runtime defect ledger (TODO29 Phase 2) — crashes as data.

A runtime defect is *not* a structural void: voids are ontology boundaries
caught by the dry-run gate before any budget is spent (``structural_voids.jsonl``,
never ledgered); defects are implementation failures that passed the gate and
crashed at runtime (``runtime_defects.jsonl``, CEEC-failed, cell quarantined
until the code changes). Neither is a scientific measurement.

The stream is append-only JSONL; state is replay-derived, exactly like the
voids ledger — no KB mutation, no schema change.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger("defects")

type DefectId = str  # sha256[:12]

TRACEBACK_TAIL_LINES = 15
MESSAGE_HEAD_CHARS = 500

# ID stability: addresses and tmp paths are noise; tensor shapes and layer
# names are preserved (they discriminate shape-mismatch bugs).
_ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]+")
_TMP_RE = re.compile(r"/tmp/[\w./-]+")  # ruff: ignore[hardcoded-temp-file] (message pattern, not file I/O)


@dataclass(frozen=True, slots=True)
class DefectRecord:
    """One append-only row of ``runtime_defects.jsonl``."""

    defect_id: DefectId
    timestamp: float
    task: str
    cell: str  # cell_key(dynamics, credit, update, topology)
    error_class: str
    message: str
    traceback_tail: str  # last ~TRACEBACK_TAIL_LINES lines
    status: Literal["open", "resolved"]


def defect_id(error_class: str, message: str) -> DefectId:
    """Content hash of ``error_class + message`` with addresses/tmp paths
    normalized away — same bug → same ID across runs and hosts."""
    head = message[:MESSAGE_HEAD_CHARS]
    normalized = _TMP_RE.sub("<tmp>", _ADDRESS_RE.sub("0xADDR", head))
    digest = hashlib.sha256(f"{error_class}|{normalized}".encode())
    return digest.hexdigest()[:12]


def append_defect(path: Path, record: DefectRecord) -> None:
    """Append one defect row to the stream (creates parent dirs)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(record)) + "\n")


def read_defects(path: Path) -> list[DefectRecord]:
    """All defect rows in file order (timestamp ordering is implied by the
    append-only stream)."""
    if not path.exists():
        return []
    rows: list[DefectRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError:
            logger.warning("Skipping malformed defect line in %s", path)
            continue
        if not isinstance(payload, dict):
            logger.warning("Skipping non-object defect line in %s", path)
            continue
        rows.append(DefectRecord(**payload))
    return rows


def quarantined_cells(records: list[DefectRecord]) -> frozenset[str]:
    """Replay the stream: a cell is quarantined while the latest status of
    any defect it emitted is ``open``. Every cell that emitted a defect is
    tracked per defect_id, so one bug failing 45 cells quarantines all 45,
    and one ``resolved`` row releases them together."""
    status: dict[DefectId, str] = {}
    cells: dict[DefectId, set[str]] = {}
    for row in records:
        status[row.defect_id] = row.status
        cells.setdefault(row.defect_id, set()).add(row.cell)
    return frozenset(
        cell
        for defect, is_open in status.items()
        if is_open == "open"
        for cell in cells[defect]
    )


def resolve_defect(path: Path, defect_id_: DefectId) -> int:
    """Append a ``resolved`` row for ``defect_id_``; next burst re-injects
    the affected cells. Returns the number of rows appended (0 for an
    unknown or already-resolved defect)."""
    known = [r for r in read_defects(path) if r.defect_id == defect_id_]
    if not known or known[-1].status == "resolved":
        return 0
    last = known[-1]
    append_defect(
        path,
        DefectRecord(
            defect_id=last.defect_id,
            timestamp=time.time(),
            task=last.task,
            cell=last.cell,
            error_class=last.error_class,
            message=last.message,
            traceback_tail="",
            status="resolved",
        ),
    )
    logger.info("Defect %s resolved: %s", defect_id_, last.cell)
    return 1
