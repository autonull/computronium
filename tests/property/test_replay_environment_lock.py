"""Lock: the cell ceiling travels with the run, and the replay runs it.

The ceiling is part of the environment a run measured in, but it lived only in
the CLI, so a replay fell back to the host default and compared two
environments (TODO107 W33). The locks: the declaration validates the ceiling,
the run row records the one its cells trained under, a replay keeps it, and
``comp repro`` cannot name another one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.execution.limits import ExecutionLimits
from computronium.experiment.schema import RunSpec, seed_all_registries
from computronium.experiment.surface import cli as surface_cli
from computronium.experiment.surface._cli._repro import _replay_spec

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def _seed() -> None:
    seed_all_registries()


def _spec(**overrides: object) -> RunSpec:
    return RunSpec.model_validate({"task": "digits", **overrides})


def test_a_zero_ceiling_is_rejected_at_the_declaration() -> None:
    with pytest.raises(ValidationError, match="cell_workers"):
        _spec(cell_workers=0)


def test_the_run_row_records_the_ceiling_its_cells_trained_under(
    tmp_path: Path,
) -> None:
    limits = ExecutionLimits.from_cli(cell_workers=2)
    with RecordStore(StoreConfig(path=tmp_path / "ceiling.duckdb")) as store:
        run_id = store.create_run(spec=limits.declare(_spec()))
        info = store.query_run(run_id)
    assert info is not None
    assert info.spec is not None
    assert info.spec.cell_workers == 2


def test_a_replay_keeps_the_recorded_ceiling() -> None:
    recorded = _spec(cell_workers=1)
    replay = _replay_spec(recorded, seeds=None, device="cpu")
    assert replay.cell_workers == 1
    assert replay.deterministic
    assert replay.device == "cpu"


def test_a_run_that_declares_no_ceiling_still_replays() -> None:
    """A pre-W33 row is replayable; the deviation is the CLI's warning."""
    assert _spec().cell_workers is None
    assert _replay_spec(_spec(), seeds=None, device="auto").cell_workers is None


def test_repro_takes_no_cell_ceiling_flag() -> None:
    parser = surface_cli._build_parser()  # ruff: ignore[private-member-access]
    with pytest.raises(SystemExit):
        parser.parse_args(["repro", "--run-id", "run-1", "--max-workers", "1"])
