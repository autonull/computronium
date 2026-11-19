"""Acceptance: a stranger adds a credit and holds a map row (TODO95 P5).

The recipe in ``docs/sec/map.md`` is this test end to end: build the census,
write the map, then ``comp verify`` the new row in its slice family. A row that
was never screened holds as ``unmeasured``; a row from another family, a
measured row without its replay hash and a missing row are refused with the
reason named. The run must stay inside the 60 s acceptance budget.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from computronium.cli.__main__ import main
from computronium.experiment.sec_census import PrimitiveCensusEntry, build_census
from computronium.experiment.sec_extension import verify_row
from computronium.experiment.sec_loop import update_map

if TYPE_CHECKING:
    from pathlib import Path


def _stranger() -> PrimitiveCensusEntry:
    """A credit a stranger adds: a spec-only row, no screen yet."""
    return PrimitiveCensusEntry(
        id="primitive.credit_assignment.stranger_probe",
        axis="credit",
        name="stranger_probe",
        task_families=("vision",),
        available=True,
        capability_card="a credit the recipe adds",
        status="implemented",
        reference_entrypoint="",
        kernel_entrypoint=None,
        supported_backends=(),
    )


def _map(tmp: Path, extra: PrimitiveCensusEntry | None = None) -> Path:
    entries = [*build_census(), *([extra] if extra else [])]
    update_map(tmp, entries, None, report=False)
    return tmp / "map.json"


def test_a_stranger_holds_a_map_row_end_to_end(tmp_path: Path) -> None:
    path = _map(tmp_path, _stranger())
    verdict = verify_row(json.loads(path.read_text()), _stranger().id, "vision")
    assert verdict.held, verdict.problems
    assert verdict.status == "unmeasured"
    assert verdict.measurement is None

    code = main(["verify", "--primitive", _stranger().id, "--map", str(path)])
    assert code == 0


def test_the_scanner_names_why_a_row_is_refused(tmp_path: Path) -> None:
    path = _map(tmp_path, _stranger())
    data = json.loads(path.read_text())

    data["primitives"][_stranger().id]["status"] = "measured"
    data["primitives"][_stranger().id]["measurement"] = {"val_acc": 0.5}
    verdict = verify_row(data, _stranger().id, "vision")
    assert not verdict.held
    assert any("no box" in problem for problem in verdict.problems)
    assert any("no replay hash" in problem for problem in verdict.problems)

    path.write_text(json.dumps(data))
    assert main(["verify", "--primitive", _stranger().id, "--map", str(path)]) == 1
    assert main(["verify", "--primitive", "primitive.absent", "--map", str(path)]) == 1


def test_a_row_screened_elsewhere_is_not_this_slice(tmp_path: Path) -> None:
    path = _map(tmp_path)
    data = json.loads(path.read_text())
    row = data["primitives"][next(iter(data["primitives"]))]
    row |= {
        "status": "measured",
        "task": "iris",
        "ruler": "val_acc on iris",
        "rule": "base box",
        "box": {"task": "iris"},
        "control": {"val_acc": 0.73},
        "measurement": {"val_acc": 0.74},
        "replay_hash": "0" * 64,
    }
    verdict = verify_row(data, row["primitive"], "vision")
    assert not verdict.held
    assert any("not vision" in problem for problem in verdict.problems)


def test_a_slice_without_a_base_box_is_refused(tmp_path: Path) -> None:
    path = _map(tmp_path, _stranger())
    verdict = verify_row(json.loads(path.read_text()), _stranger().id, "rl")
    assert not verdict.held
    assert any("declares no base box" in problem for problem in verdict.problems)


@pytest.mark.parametrize("version", ["SEC-v2", "SEC-v4"])
def test_another_record_version_is_refused(tmp_path: Path, version: str) -> None:
    path = _map(tmp_path, _stranger())
    data = json.loads(path.read_text())
    data["version"] = version
    verdict = verify_row(data, _stranger().id, "vision")
    assert not verdict.held
    assert any("is not SEC-v3" in problem for problem in verdict.problems)
